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
STAMP=$(date +%Y%m%d-%H%M%S)

if [ ! -f "$SOURCE_DIR/pet.json" ] || [ ! -f "$SOURCE_DIR/spritesheet.webp" ]; then
  echo "Pet package is incomplete: $SOURCE_DIR" >&2
  exit 1
fi

mkdir -p "$PET_ROOT"
if [ -d "$TARGET_DIR" ]; then
  mv "$TARGET_DIR" "$TARGET_DIR.backup-$STAMP"
fi
mkdir -p "$TARGET_DIR"
cp "$SOURCE_DIR/pet.json" "$TARGET_DIR/pet.json"
cp "$SOURCE_DIR/spritesheet.webp" "$TARGET_DIR/spritesheet.webp"

mkdir -p "$CODEX_HOME"
if [ -f "$CONFIG_FILE" ]; then
  cp "$CONFIG_FILE" "$CONFIG_FILE.backup-$STAMP"
else
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
echo "Selected $SELECTED_ID in $CONFIG_FILE"
echo "Restart Codex to load the pet."
