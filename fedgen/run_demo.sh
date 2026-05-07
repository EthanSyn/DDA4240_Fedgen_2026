#!/bin/bash
#
# FedGen Demo - Sovereign Dataspace for Decentralized AI Training
#
# Prerequisites:
#   1. MVD deployed: cd MinimumViableDataspace/deployment && terraform apply
#   2. Data backend:  cd fedgen/deployment && terraform apply
#   3. Seed complete: bash fedgen/scripts/seed_mvd.sh
#
# Usage:
#   bash run_demo.sh          # Run all scenarios
#   bash run_demo.sh --seed   # Seed + Run all scenarios
#

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "************************************************************"
echo "  FedGen - Sovereign Dataspace for AI Training Corpora"
echo "************************************************************"

# Optional: run seed first
if [ "$1" = "--seed" ]; then
  echo ""
  echo "=== Running MVD Seed ==="
  bash "$SCRIPT_DIR/scripts/seed_mvd.sh"
  echo ""
fi

# Run the comprehensive demo
cd "$SCRIPT_DIR"
python3 scripts/fedgen_demo.py
