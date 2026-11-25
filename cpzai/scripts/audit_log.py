#!/usr/bin/env python3
"""CPZAI plugin: PostToolUse and PostToolUseFailure audit log.

Appends one JSON line per state-changing CPZAI tool call to
${CLAUDE_PLUGIN_DATA}/audit.log, the file the compliance skill calls the
primary audit source (cpzai#3024). Each record has:

  ts, event, tool          when, PostToolUse or PostToolUseFailure, which tool
  ok                       false when the call failed or the tool answered an
                           error or a refusal, true when it answered without
                           one, null when the answer says neither
  input                    the full tool input, with any credential field
                           (key, secret, token, password) replaced by
                           "[redacted]"; never cut short
  order_id, status         from the tool's answer when it carries them
                           (place_order: the broker's order id and status)
  error                    the tool's error text, when there is one

A record that cannot be built is still written, with the reason, so a call is
never silently missing from the log.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import sys
from pathlib import Path

SENSITIVE = re.compile(r"(key|secret|token|password|passphrase)", re.I)


def redact(value):
    if isinstance(value, dict):
        return {k: ("[redacted]" if SENSITIVE.search(str(k)) else redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value


def answer_body(resp):
    """The tool's JSON answer: structuredContent, or the first text block that parses."""
    if isinstance(resp, dict):
        sc = resp.get("structuredContent")
        if isinstance(sc, dict):
            return sc
        content = resp.get("content")
    elif isinstance(resp, list):
        content = resp
    else:
        content = None
    if isinstance(resp, str):
        content = [{"type": "text", "text": resp}]
    for block in content or []:
        if isinstance(block, dict) and block.get("type") == "text":
            try:
                parsed = json.loads(block.get("text") or "")
            except (TypeError, ValueError):
                continue
            if isinstance(parsed, dict):
                return parsed
    return resp if isinstance(resp, dict) else None


def pick(body, *keys):
    if not isinstance(body, dict):
        return None
    for scope in (body, body.get("data") if isinstance(body.get("data"), dict) else None, body.get("order") if isinstance(body.get("order"), dict) else None):
        if not isinstance(scope, dict):
            continue
        for k in keys:
            v = scope.get(k)
            if v not in (None, ""):
                return v
    return None


def record(event: dict) -> dict:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    name = event.get("hook_event_name") or event.get("hookEventName") or "PostToolUse"
    tool = event.get("tool_name") or event.get("toolName") or ""
    inp = event.get("tool_input") if "tool_input" in event else event.get("toolInput")
    rec = {"ts": ts, "event": name, "tool": tool, "ok": None, "input": redact(inp)}

    if name == "PostToolUseFailure":
        rec["ok"] = False
        err = event.get("error") or event.get("tool_error") or "the tool call failed"
        rec["error"] = err if isinstance(err, str) else json.dumps(err)
        return rec

    resp = event.get("tool_response") if "tool_response" in event else event.get("toolResponse")
    body = answer_body(resp)
    is_error = resp.get("isError") if isinstance(resp, dict) else None
    error = pick(body, "error", "message") if isinstance(body, dict) and ("error" in body or is_error) else None
    refused = isinstance(body, dict) and (body.get("success") is False or body.get("ok") is False or "error" in body)
    if is_error is True or refused:
        rec["ok"] = False
    elif is_error is False or (isinstance(body, dict) and body):
        rec["ok"] = True
    rec["order_id"] = pick(body, "order_id", "broker_order_id", "id")
    rec["status"] = pick(body, "status")
    if error is not None:
        rec["error"] = error if isinstance(error, str) else json.dumps(error)
    return rec


def main() -> int:
    data_dir = Path(os.environ.get("CLAUDE_PLUGIN_DATA") or Path.home() / ".claude" / "plugins" / "data" / "cpzai")
    data_dir.mkdir(parents=True, exist_ok=True)
    raw = sys.stdin.read()
    try:
        event = json.loads(raw) if raw.strip() else {}
        rec = record(event if isinstance(event, dict) else {})
    except Exception as e:  # The call happened: log that it did, and why the record is thin.
        rec = {
            "ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "event": "unreadable",
            "ok": None,
            "error": f"audit record could not be built: {type(e).__name__}: {e}",
            # Not the raw event: it can hold a credential (create_connection).
            "raw_length": len(raw),
        }
    with open(data_dir / "audit.log", "a") as f:
        f.write(json.dumps(rec, separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
