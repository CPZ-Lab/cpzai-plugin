#!/usr/bin/env bash
# CPZAI plugin — PreToolUse hook for destructive MCP tools.
#
# Reads the hook event JSON from stdin, decides whether to allow the
# tool call to proceed, and either:
#   - exit 0 with no output → allow
#   - exit 0 with JSON {"decision":"block","reason":"..."} → block
#   - exit 2 → block with a default reason
#
# Behaviour:
#   - If require_trade_confirmation=false → allow (user opted out)
#   - For place_order / execute_strategy → block with structured reason
#     so the agent must summarize and re-confirm via AskUserQuestion.
#   - delete_webhook is default-deny.
set -euo pipefail

EVENT_FILE="$(mktemp)"
trap 'rm -f "$EVENT_FILE"' EXIT
cat > "$EVENT_FILE"

TOOL="$(EVENT_FILE="$EVENT_FILE" python3 - <<'PY'
import json, os, sys
try:
    with open(os.environ["EVENT_FILE"]) as f:
        d = json.load(f)
    print(d.get("tool_name") or d.get("toolName") or "")
except Exception:
    print("")
PY
)"

CONFIRM="${CLAUDE_PLUGIN_OPTION_REQUIRE_TRADE_CONFIRMATION:-true}"
ENV="${CLAUDE_PLUGIN_OPTION_DEFAULT_ENVIRONMENT:-paper}"

if [ "$CONFIRM" != "true" ]; then
  exit 0
fi

if [ "$TOOL" = "mcp__cpzai__delete_webhook" ]; then
  cat <<JSON
{"decision":"block","reason":"delete_webhook is destructive. Confirm explicitly with the user (the webhook id and signing secret cannot be recovered) and re-issue the call inside the same turn after acknowledgement."}
JSON
  exit 0
fi

if [ "$TOOL" = "mcp__cpzai__place_order" ] || [ "$TOOL" = "mcp__cpzai__execute_strategy" ]; then
  cat <<JSON
{"decision":"block","reason":"CPZAI safety guard: tool=${TOOL} env=${ENV}. Before executing, summarize the order/run for the user (account, symbol, side, qty, price, environment) and obtain explicit confirmation via AskUserQuestion. Then re-issue this exact tool call. Set userConfig.require_trade_confirmation=false to opt out of this guard."}
JSON
  exit 0
fi

# Mutating strategy/webhook/connection/portfolio tools also require confirmation
if [ "$TOOL" = "mcp__cpzai__create_strategy" ] || [ "$TOOL" = "mcp__cpzai__update_strategy" ] || [ "$TOOL" = "mcp__cpzai__create_webhook" ] || [ "$TOOL" = "mcp__cpzai__sync_portfolio" ] || [ "$TOOL" = "mcp__cpzai__create_connection" ]; then
  cat <<JSON
{"decision":"block","reason":"CPZAI safety guard: tool=${TOOL} env=${ENV}. This is a mutating tool. Summarize what will change and obtain explicit confirmation via AskUserQuestion before re-issuing. Set require_trade_confirmation=false to opt out."}
JSON
  exit 0
fi

exit 0
