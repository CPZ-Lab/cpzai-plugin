#!/usr/bin/env bash
# CPZAI plugin — PostToolUse hook
#
# Appends a single-line JSON audit record for every state-mutating
# CPZAI MCP tool call. The log lives in the plugin's persistent data
# directory so it survives plugin updates.
set -euo pipefail

DATA_DIR="${CLAUDE_PLUGIN_DATA:-${HOME}/.claude/plugins/data/cpzai}"
mkdir -p "$DATA_DIR"
LOG_FILE="$DATA_DIR/audit.log"

# Cache stdin in a temp file so we can hand it to python without conflicting
# with the heredoc.
EVENT_FILE="$(mktemp)"
trap 'rm -f "$EVENT_FILE"' EXIT
cat > "$EVENT_FILE"

EVENT_FILE="$EVENT_FILE" python3 - >> "$LOG_FILE" <<'PY'
import json, os, datetime
ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
try:
    with open(os.environ["EVENT_FILE"]) as f:
        raw = f.read()
    d = json.loads(raw) if raw.strip() else {}
except Exception:
    d = {}
tool = d.get("tool_name") or d.get("toolName") or ""
ok = d.get("success", True)
inp = d.get("tool_input") or d.get("toolInput") or {}
input_preview = json.dumps(inp, separators=(",", ":"))[:240]
record = {"ts": ts, "tool": tool, "ok": ok, "input_preview": input_preview}
print(json.dumps(record, separators=(",", ":")))
PY
