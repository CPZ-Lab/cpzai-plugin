#!/usr/bin/env bash
# CPZAI plugin — SessionStart hook
# Prints a concise plugin status banner so the user knows the trading
# context every session.
set -euo pipefail

PLUGIN_VERSION="2.0.0"
MCP_URL="${CPZAI_MCP_URL:-https://mcp.cpz-lab.com/mcp}"
ENV="${CLAUDE_PLUGIN_OPTION_DEFAULT_ENVIRONMENT:-paper}"
HAS_KEY="$([ -n "${CLAUDE_PLUGIN_OPTION_CPZ_API_KEY:-}" ] && echo "configured" || echo "OAuth/unset")"
CONFIRM="${CLAUDE_PLUGIN_OPTION_REQUIRE_TRADE_CONFIRMATION:-true}"

cat <<EOF
[cpzai v${PLUGIN_VERSION}] MCP=${MCP_URL}  env=${ENV}  auth=${HAS_KEY}  confirm=${CONFIRM}
EOF
