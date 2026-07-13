#!/bin/sh
set -eu

PET_ID="frieren-pixel"
CODEX_HOME=${CODEX_HOME:-"$HOME/.codex"}
TARGET_DIR="$CODEX_HOME/pets/$PET_ID"
CONFIG_FILE="$CODEX_HOME/config.toml"

rm -rf "$TARGET_DIR"

if [ -f "$CONFIG_FILE" ]; then
  TMP_CONFIG="$CONFIG_FILE.tmp.$$"
  awk '
  BEGIN { in_desktop = 0 }
  /^\[[^]]+\][[:space:]]*$/ {
    in_desktop = ($0 == "[desktop]")
    print
    next
  }
  in_desktop && /^[[:space:]]*selected-avatar-id[[:space:]]*=[[:space:]]*"custom:frieren-pixel"[[:space:]]*$/ { next }
  { print }
  ' "$CONFIG_FILE" > "$TMP_CONFIG"
  mv "$TMP_CONFIG" "$CONFIG_FILE"
fi

echo "Removed Frieren Pixel. Restart Codex to return to the default pet."
