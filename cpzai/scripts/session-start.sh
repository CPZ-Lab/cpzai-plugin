#!/usr/bin/env bash
# CPZAI plugin — SessionStart hook
# Prints a concise plugin status banner so the user knows the trading
# context every session.
set -euo pipefail

PLUGIN_VERSION="2.1.0"
MCP_URL="${CPZAI_MCP_URL:-https://mcp.cpz-lab.com/mcp}"
ENV="${CLAUDE_PLUGIN_OPTION_DEFAULT_ENVIRONMENT:-paper}"
HAS_KEY="$([ -n "${CLAUDE_PLUGIN_OPTION_CPZ_API_KEY:-}" ] && echo "configured" || echo "OAuth/unset")"
# The same reading of the option as scripts/pre_trade_guard.py: only false/0/no/off turn it off.
RAW_CONFIRM="$(printf '%s' "${CLAUDE_PLUGIN_OPTION_REQUIRE_TRADE_CONFIRMATION:-true}" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')"
case "$RAW_CONFIRM" in
  false|0|no|off) CONFIRM="false" ;;
  *) CONFIRM="true" ;;
esac
# The guard and the audit log are Python. `command -v` is not enough: a Mac without the
# developer tools has a /usr/bin/python3 stub that exists but cannot run a script. So
# python3 is run, and only one that answers counts. Without it the guard cannot start;
# hooks.json has it block (onFailure) rather than let an order through, and nothing is logged.
if command -v python3 >/dev/null 2>&1 && [ "$(python3 -c 'import json, re, sys; print("ok")' 2>/dev/null)" = "ok" ]; then
  GUARD="on"
else
  GUARD="OFF (no working python3: CPZAI orders and strategy runs are blocked and nothing is logged)"
  CONFIRM="false"
fi

cat <<EOF
[cpzai v${PLUGIN_VERSION}] MCP=${MCP_URL}  env=${ENV}  auth=${HAS_KEY}  confirm=${CONFIRM}  guard=${GUARD}
EOF
