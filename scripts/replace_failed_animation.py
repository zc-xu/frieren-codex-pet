#!/usr/bin/env python3
"""Replace only the Codex failed row and render its real three-cycle cadence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops


CELL_WIDTH = 192
CELL_HEIGHT = 208
COLUMNS = 8
ROWS = 11
FAILED_ROW = 5
FRAME_COUNT = 8
FRAME_DURATIONS_MS = [140, 140, 140, 140, 140, 140, 140, 240]
HOST_REPEAT_COUNT = 3
IMAGE_SUFFIXES = {".png", ".webp"}


def digest(image: Image.Image) -> str:
    return hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest()


def load_frames(frames_dir: Path) -> list[Image.Image]:
    paths = sorted(
        path for path in frames_dir.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES
    )
    if len(paths) != FRAME_COUNT:
        raise SystemExit(
            f"failed row needs exactly {FRAME_COUNT} frames; found {len(paths)} in {frames_dir}"
        )

    frames: list[Image.Image] = []
    for path in paths:
        with Image.open(path) as opened:
            frame = opened.convert("RGBA")
        if frame.size != (CELL_WIDTH, CELL_HEIGHT):
            raise SystemExit(
                f"{path} must be {CELL_WIDTH}x{CELL_HEIGHT}; got {frame.width}x{frame.height}"
            )
        if frame.getbbox() is None:
            raise SystemExit(f"{path} is empty")
        frames.append(frame)
    return frames


def changed_rows(before: Image.Image, after: Image.Image) -> list[int]:
    changed: list[int] = []
    for row in range(ROWS):
        top = row * CELL_HEIGHT
        box = (0, top, COLUMNS * CELL_WIDTH, top + CELL_HEIGHT)
        if ImageChops.difference(before.crop(box), after.crop(box)).getbbox() is not None:
            changed.append(row)
    return changed


def save_lossless_webp(image: Image.Image, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="WEBP", lossless=True, quality=100, method=6, exact=True)


def save_preview(frames: list[Image.Image], output: Path) -> None:
    preview_frames = frames * HOST_REPEAT_COUNT
    preview_durations = FRAME_DURATIONS_MS * HOST_REPEAT_COUNT
    output.parent.mkdir(parents=True, exist_ok=True)
    preview_frames[0].save(
        output,
        save_all=True,
        append_images=preview_frames[1:],
        duration=preview_durations,
        loop=0,
        disposal=2,
        optimize=False,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--frames-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--preview", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    frames_dir = Path(args.frames_dir).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    preview_path = Path(args.preview).expanduser().resolve()
    report_path = Path(args.report).expanduser().resolve()

    with Image.open(input_path) as opened:
        before = opened.convert("RGBA")
    expected_size = (COLUMNS * CELL_WIDTH, ROWS * CELL_HEIGHT)
    if before.size != expected_size:
        raise SystemExit(f"input atlas must be {expected_size}; got {before.size}")

    frames = load_frames(frames_dir)
    after = before.copy()
    top = FAILED_ROW * CELL_HEIGHT
    for column, frame in enumerate(frames):
        left = column * CELL_WIDTH
        after.paste((0, 0, 0, 0), (left, top, left + CELL_WIDTH, top + CELL_HEIGHT))
        after.alpha_composite(frame, (left, top))

    rows = changed_rows(before, after)
    unexpected_rows = [row for row in rows if row != FAILED_ROW]
    if unexpected_rows:
        raise SystemExit(
            f"expected only row {FAILED_ROW} to change; changed rows: {rows}"
        )

    save_lossless_webp(after, output_path)
    save_preview(frames, preview_path)

    with Image.open(output_path) as opened:
        saved = opened.convert("RGBA")
    saved_rows = changed_rows(before, saved)
    if saved_rows != rows:
        raise SystemExit(
            "lossless output changed a different set of rows than the in-memory assembly: "
            f"expected {rows}, got {saved_rows}"
        )
    if ImageChops.difference(after, saved).getbbox() is not None:
        raise SystemExit("lossless WebP round trip changed RGBA pixels")

    report = {
        "ok": True,
        "input": str(input_path),
        "output": str(output_path),
        "frames_dir": str(frames_dir),
        "changed_rows_zero_based": rows,
        "saved_changed_rows_zero_based": saved_rows,
        "failed_row_updated": FAILED_ROW in rows,
        "preserved_rows_pixel_identical": [row for row in range(ROWS) if row != FAILED_ROW],
        "frame_durations_ms": FRAME_DURATIONS_MS,
        "host_repeat_count": HOST_REPEAT_COUNT,
        "cycle_duration_ms": sum(FRAME_DURATIONS_MS),
        "host_sequence_duration_ms": sum(FRAME_DURATIONS_MS) * HOST_REPEAT_COUNT,
        "before_rgba_sha256": digest(before),
        "after_rgba_sha256": digest(after),
        "saved_rgba_sha256": digest(saved),
        "frame_rgba_sha256": [digest(frame) for frame in frames],
        "preview": str(preview_path),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
