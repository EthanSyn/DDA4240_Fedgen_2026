#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ "$1" = "--seed" ]; then
  bash "$SCRIPT_DIR/scripts/seed_mvd.sh"
fi

cd "$SCRIPT_DIR"
python3 scripts/demo_thirdparty_database.py
