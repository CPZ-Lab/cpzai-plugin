#!/usr/bin/env bash
# CPZAI plugin — live MCP smoke test.
# Verifies the production MCP endpoint is reachable, performs the
# initialize handshake, lists tools, and asserts that every tool
# referenced by the plugin's commands and agents is present on the
# server.
set -euo pipefail

MCP_URL="${CPZAI_MCP_URL:-https://mcp.cpz-lab.com/mcp}"
# Strip trailing /mcp (or any path) to derive the origin for OAuth metadata.
MCP_ORIGIN="$(printf '%s' "$MCP_URL" | python3 -c 'import sys,urllib.parse as u; p=u.urlparse(sys.stdin.read().strip()); print(f"{p.scheme}://{p.netloc}")')"
OAUTH_URL="${MCP_ORIGIN}/.well-known/oauth-authorization-server"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

ok=0
fail=0
note() { printf "  • %s\n" "$1"; }
pass() { printf "  ✓ %s\n" "$1"; ok=$((ok+1)); }
flag() { printf "  ✗ %s\n" "$1"; fail=$((fail+1)); }

echo "Smoke test: $MCP_URL"

# 1. OAuth metadata
status=$(curl -sS -o "$TMP/oauth.json" -w "%{http_code}" "$OAUTH_URL")
if [ "$status" = "200" ]; then
  pass "OAuth metadata: HTTP 200"
else
  flag "OAuth metadata: HTTP $status (expected 200)"
fi

# 2. MCP initialize
curl -sS -o "$TMP/init.txt" -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"cpzai-smoke","version":"2.0.0"}}}' \
  "$MCP_URL"

if grep -q '"protocolVersion"' "$TMP/init.txt"; then
  pass "initialize handshake succeeded"
else
  flag "initialize handshake failed (no protocolVersion in response)"
  cat "$TMP/init.txt"
  exit 1
fi

# 3. tools/list
curl -sS -o "$TMP/tools.txt" -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
  "$MCP_URL"

# Extract tool names. The response is SSE-framed (event: message\ndata: {...}).
python3 - <<PY > "$TMP/tools.json"
import re, json, sys
text = open("$TMP/tools.txt").read()
m = re.search(r"data:\s*(\{.*\})", text, re.S)
if not m:
    print("[]")
    sys.exit(0)
try:
    payload = json.loads(m.group(1))
    tools = [t["name"] for t in payload.get("result", {}).get("tools", [])]
    print(json.dumps(tools))
except Exception as e:
    print("[]")
    sys.exit(0)
PY

count=$(python3 -c "import json; print(len(json.load(open('$TMP/tools.json'))))")
if [ "$count" -ge 18 ]; then
  pass "tools/list returned $count tools (>=18 expected)"
else
  flag "tools/list returned $count tools (expected >=18)"
fi

# 4. Cross-check referenced tools exist
python3 <<PY
import json, re, sys, os
root = os.environ.get("ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
live = set(json.load(open("$TMP/tools.json")))
ref = set()
for d in (os.path.join(root, "cpzai", "commands"), os.path.join(root, "cpzai", "agents")):
    if not os.path.isdir(d):
        continue
    for f in os.listdir(d):
        if not f.endswith(".md"):
            continue
        text = open(os.path.join(d, f)).read()
        for m in re.finditer(r"mcp__cpzai__([a-z0-9_]+)", text):
            ref.add(m.group(1))
missing = ref - live
extra = live - ref
print(f"  referenced tools: {len(ref)}")
print(f"  live tools:       {len(live)}")
if missing:
    print(f"  ✗ MISSING ON SERVER: {sorted(missing)}")
    sys.exit(1)
print("  ✓ all referenced tools exist on the server")
if extra:
    print(f"  (info) live tools not referenced anywhere: {sorted(extra)}")
PY

echo
echo "passed: $ok   failed: $fail"
exit $fail
