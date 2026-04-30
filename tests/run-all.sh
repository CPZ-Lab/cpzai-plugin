#!/usr/bin/env bash
# CPZAI plugin — run all tests.
#
# Usage:
#   tests/run-all.sh           # structure validation + live MCP smoke test
#   tests/run-all.sh --offline # structure validation only (skips network)
set -euo pipefail
cd "$(dirname "$0")/.."

mode="${1:-online}"

echo "=== Structure validation ==="
python3 tests/validate.py

if [ "$mode" != "--offline" ]; then
  echo
  echo "=== Live MCP smoke test ==="
  ROOT="$(pwd)" bash tests/smoke-mcp.sh
fi

echo
echo "All tests passed."
