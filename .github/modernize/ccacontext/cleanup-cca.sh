#!/bin/bash
# Removes CCA-copied skill directories listed in .ccaskills
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$(cd "$SCRIPT_DIR/../../skills" && pwd)"
CCASKILLS="$SCRIPT_DIR/.ccaskills"

if [ ! -f "$CCASKILLS" ]; then
    echo "No .ccaskills file found, nothing to clean."
    exit 0
fi

while IFS= read -r skill; do
    [ -z "$skill" ] && continue
    target="$SKILLS_DIR/$skill"
    if [ -d "$target" ]; then
        rm -rf "$target"
        echo "Removed: $skill"
    fi
done < "$CCASKILLS"

rm -f "$CCASKILLS"
echo "Cleanup complete."
