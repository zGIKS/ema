#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v uv >/dev/null 2>&1; then
  echo "[ERR] 'uv' not found. Install uv first: https://docs.astral.sh/uv/"
  exit 1
fi

echo "[BOOT] Creating venv (.venv) ..."
uv venv

echo "[BOOT] Installing dependencies ..."
uv pip install -r requirements.txt

echo
echo "[OK] Environment ready."
echo "Run:"
echo "  uv run python -m src.main"
echo
echo "Optional (NixOS):"
echo "  nix-shell --run \"uv run python -m src.main\""

