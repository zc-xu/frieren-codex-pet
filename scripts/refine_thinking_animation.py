#!/usr/bin/env python3
"""Build a calm six-frame thinking loop for the Codex v2 pet atlas."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


CELL_WIDTH = 192
CELL_HEIGHT = 208
ATLAS_COLUMNS = 8
ATLAS_ROWS = 11
THINKING_ROW = 7
THINKING_FRAMES = 6
FRAME_DURATIONS_MS = [120, 120, 120, 120, 120, 220]

# Keep one readable thinking silhouette throughout. The tiny one-pixel lift is
# slow enough to read as breathing, while the identical first/last frames make
# the loop boundary invisible.
VERTICAL_OFFSETS = [0, 0, -1, -1, 0, 0]
BASE_FRAME = (7, 1)
BLINK_SOURCE_FRAME = (0, 2)
BLINK_FRAME_INDEX = 3
BLINK_PATCH_BOX = (68, 63, 124, 83)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--preview", type=Path)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def crop_cell(atlas: Image.Image, row: int, column: int) -> Image.Image:
    left = column * CELL_WIDTH
    top = row * CELL_HEIGHT
    return atlas.crop((left, top, left + CELL_WIDTH, top + CELL_HEIGHT))


def shifted(frame: Image.Image, dy: int) -> Image.Image:
    result = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    result.alpha_composite(frame, (0, dy))
    return result


def make_blink(base: Image.Image, blink_source: Image.Image) -> Image.Image:
    result = base.copy()
    result.paste(blink_source.crop(BLINK_PATCH_BOX), BLINK_PATCH_BOX[:2])
    return result


def row_digest(atlas: Image.Image, row: int) -> str:
    band = atlas.crop((0, row * CELL_HEIGHT, atlas.width, (row + 1) * CELL_HEIGHT))
    return hashlib.sha256(band.tobytes()).hexdigest()


def render_preview(frames: list[Image.Image], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered: list[Image.Image] = []
    for frame in frames:
        background = Image.new("RGBA", frame.size, (16, 16, 18, 255))
        background.alpha_composite(frame)
        rendered.append(
            background.convert("RGB").resize(
                (CELL_WIDTH * 4, CELL_HEIGHT * 4), Image.Resampling.NEAREST
            )
        )
    rendered[0].save(
        path,
        save_all=True,
        append_images=rendered[1:],
        duration=FRAME_DURATIONS_MS,
        loop=0,
        optimize=False,
    )


def main() -> None:
    args = parse_args()
    source = Image.open(args.input).convert("RGBA")
    expected_size = (CELL_WIDTH * ATLAS_COLUMNS, CELL_HEIGHT * ATLAS_ROWS)
    if source.size != expected_size:
        raise SystemExit(f"Expected atlas size {expected_size}, got {source.size}")

    before_digests = [row_digest(source, row) for row in range(ATLAS_ROWS)]
    base = crop_cell(source, *BASE_FRAME)
    blink_source = crop_cell(source, *BLINK_SOURCE_FRAME)
    blink = make_blink(base, blink_source)

    frames = []
    for index, dy in enumerate(VERTICAL_OFFSETS):
        frame = blink if index == BLINK_FRAME_INDEX else base
        frames.append(shifted(frame, dy))

    output = source.copy()
    clear_row = Image.new("RGBA", (output.width, CELL_HEIGHT), (0, 0, 0, 0))
    output.paste(clear_row, (0, THINKING_ROW * CELL_HEIGHT))
    for column, frame in enumerate(frames):
        output.alpha_composite(frame, (column * CELL_WIDTH, THINKING_ROW * CELL_HEIGHT))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.save(args.output, "WEBP", lossless=True, method=6, exact=True)

    if args.preview:
        render_preview(frames, args.preview)

    after_digests = [row_digest(output, row) for row in range(ATLAS_ROWS)]
    changed_rows = [
        row for row in range(ATLAS_ROWS) if before_digests[row] != after_digests[row]
    ]
    unchanged_rows = [
        row for row in range(ATLAS_ROWS) if before_digests[row] == after_digests[row]
    ]
    report = {
        "ok": changed_rows in ([], [THINKING_ROW]),
        "state": "running",
        "row": THINKING_ROW,
        "frameCount": THINKING_FRAMES,
        "frameDurationsMs": FRAME_DURATIONS_MS,
        "baseFrame": {"row": BASE_FRAME[0], "column": BASE_FRAME[1]},
        "blinkSourceFrame": {
            "row": BLINK_SOURCE_FRAME[0],
            "column": BLINK_SOURCE_FRAME[1],
        },
        "blinkFrameIndex": BLINK_FRAME_INDEX,
        "blinkPatchBox": list(BLINK_PATCH_BOX),
        "verticalOffsets": VERTICAL_OFFSETS,
        "loopBoundaryExact": frames[0].tobytes() == frames[-1].tobytes(),
        "changedRows": changed_rows,
        "unchangedRows": unchanged_rows,
        "transparentUnusedCells": all(
            crop_cell(output, THINKING_ROW, column).getchannel("A").getbbox() is None
            for column in range(THINKING_FRAMES, ATLAS_COLUMNS)
        ),
    }
    if not report["ok"]:
        raise SystemExit(f"Unexpected atlas row changes: {changed_rows}")

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
