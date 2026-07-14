#!/bin/sh
set -eu

PET_ID="frieren-pixel"
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SOURCE_DIR="$SCRIPT_DIR/pet/$PET_ID"
CODEX_HOME=${CODEX_HOME:-"$HOME/.codex"}
PET_ROOT="$CODEX_HOME/pets"
TARGET_DIR="$PET_ROOT/$PET_ID"
CONFIG_FILE="$CODEX_HOME/config.toml"
SELECTED_ID="custom:$PET_ID"

if [ ! -f "$SOURCE_DIR/pet.json" ] || [ ! -f "$SOURCE_DIR/spritesheet.webp" ]; then
  echo "Pet package is incomplete: $SOURCE_DIR" >&2
  exit 1
fi

mkdir -p "$PET_ROOT"
mkdir -p "$TARGET_DIR"

# Keep one stable custom-pet directory. Stage each file beside its destination
# and rename it into place so updates never create another scan-visible pet.
TMP_PET_JSON="$TARGET_DIR/.pet.json.tmp.$$"
TMP_SPRITESHEET="$TARGET_DIR/.spritesheet.webp.tmp.$$"
trap 'rm -f "$TMP_PET_JSON" "$TMP_SPRITESHEET"' EXIT HUP INT TERM
cp "$SOURCE_DIR/pet.json" "$TMP_PET_JSON"
cp "$SOURCE_DIR/spritesheet.webp" "$TMP_SPRITESHEET"
mv "$TMP_SPRITESHEET" "$TARGET_DIR/spritesheet.webp"
mv "$TMP_PET_JSON" "$TARGET_DIR/pet.json"
trap - EXIT HUP INT TERM

# Older installers moved the active directory to frieren-pixel.backup-*, and
# Codex treated every one as another pet because each still contained pet.json.
# The repository is the version history now, so remove those obsolete copies.
LEGACY_COUNT=0
for LEGACY_DIR in "$PET_ROOT/$PET_ID".backup-*; do
  if [ -d "$LEGACY_DIR" ]; then
    rm -rf "$LEGACY_DIR"
    LEGACY_COUNT=$((LEGACY_COUNT + 1))
  fi
done

mkdir -p "$CODEX_HOME"
if [ ! -f "$CONFIG_FILE" ]; then
  : > "$CONFIG_FILE"
fi

TMP_CONFIG="$CONFIG_FILE.tmp.$$"
awk -v selected="$SELECTED_ID" '
BEGIN {
  in_desktop = 0
  saw_desktop = 0
  wrote_selected = 0
}
/^\[[^]]+\][[:space:]]*$/ {
  if (in_desktop && !wrote_selected) {
    print "selected-avatar-id = \"" selected "\""
    wrote_selected = 1
  }
  in_desktop = ($0 == "[desktop]")
  if (in_desktop) saw_desktop = 1
  print
  next
}
in_desktop && /^[[:space:]]*selected-avatar-id[[:space:]]*=/ {
  print "selected-avatar-id = \"" selected "\""
  wrote_selected = 1
  next
}
{ print }
END {
  if (in_desktop && !wrote_selected) {
    print "selected-avatar-id = \"" selected "\""
    wrote_selected = 1
  }
  if (!saw_desktop) {
    print ""
    print "[desktop]"
    print "selected-avatar-id = \"" selected "\""
  }
}
' "$CONFIG_FILE" > "$TMP_CONFIG"
mv "$TMP_CONFIG" "$CONFIG_FILE"

echo "Installed Frieren Pixel to $TARGET_DIR"
if [ "$LEGACY_COUNT" -gt 0 ]; then
  echo "Removed $LEGACY_COUNT obsolete Frieren Pixel backup directories."
fi
echo "Selected $SELECTED_ID in $CONFIG_FILE"
echo "Restart Codex to load the pet."
