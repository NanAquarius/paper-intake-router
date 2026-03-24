#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"
REQ_FILE="${REQ_FILE:-requirements-minimal.txt}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[paper-intake-router] Python not found: $PYTHON_BIN" >&2
  exit 1
fi

"$PYTHON_BIN" -m venv "$VENV_DIR"
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip

if [ -f "$REQ_FILE" ]; then
  pip install -r "$REQ_FILE"
fi

echo
printf '[paper-intake-router] environment ready\n'
printf 'activate with: source %s/bin/activate\n' "$VENV_DIR"
