#!/usr/bin/env zsh
# Run the full unit test suite and a quick linter check
# Usage: ./run_all_tests.sh

set -euo pipefail

echo "Running quick lint (ruff) if available..."
if command -v ruff >/dev/null 2>&1; then
  echo "-> ruff found: running ruff check (selected rules)..."
  # quick check; adjust as needed
  ruff check . --select E,F,W || true
else
  echo "-> ruff not found; skipping lint step (install with: pip install ruff)"
fi

echo "\nRunning unit tests..."
python -m unittest discover tests -v

echo "\nAll done. If tests passed above, the suite is green."
