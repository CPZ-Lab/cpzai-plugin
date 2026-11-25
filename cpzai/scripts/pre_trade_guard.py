#!/usr/bin/env python3
"""CPZAI plugin: PreToolUse guard for state-changing CPZAI tools.

Claude Code names a tool from a plugin's bundled MCP server
mcp__plugin_<plugin>_<server>__<tool>, so this plugin's tools are
mcp__plugin_cpzai_cpzai__place_order and so on. The guard used to match
mcp__cpzai__place_order only, so it never ran (cpzai#2908). Both spellings
are accepted here (the short one is what a standalone `cpzai` MCP server is
called), and hooks.json matches both.

It used to answer {"decision":"block"} and tell Claude to ask the user and
re-issue the call. It kept no record of a confirmation, so the re-issued
call was blocked again, every time. Now it answers permissionDecision "ask":
Claude Code itself shows the user this call with the reason below, once,
and runs it when the user approves. The approval is the user's, in Claude
Code's own prompt, never the model's say-so.

Stdin: the PreToolUse event JSON. Stdout: nothing (the normal permission
flow applies) or one JSON object. A call this guard cannot read is asked
about, never let through silently.
"""
from __future__ import annotations

import json
import os
import re
import sys

TOOL_NAME = re.compile(r"^mcp__(?:plugin_cpzai_)?cpzai__([a-z0-9_]+)$")

# Tools that move money or run code that can.
TRADING = {"place_order", "execute_strategy"}
# Tools that change platform state.
MUTATING = {
    "create_strategy",
    "update_strategy",
    "configure_overlay",
    "create_webhook",
    "delete_webhook",
    "sync_portfolio",
    "create_connection",
}
GUARDED = TRADING | MUTATING


def option(name: str, default: str) -> str:
    return os.environ.get(f"CLAUDE_PLUGIN_OPTION_{name}", default).strip()


def confirmation_required() -> bool:
    return option("REQUIRE_TRADE_CONFIRMATION", "true").lower() not in ("false", "0", "no", "off")


def ask(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        }
    }))


def field(inp: dict, key: str) -> str:
    v = inp.get(key)
    return "?" if v is None or v == "" else str(v)


def describe(tool: str, inp: dict, default_env: str) -> str:
    if tool == "place_order":
        price = ""
        if inp.get("price") is not None:
            price += f" limit {inp['price']}"
        if inp.get("stop_price") is not None:
            price += f" stop {inp['stop_price']}"
        env_note = (
            "Your default trading environment is paper: approve only if this account is a paper account. "
            "A live account trades real money."
            if default_env.lower() == "paper"
            else f"Your default trading environment is {default_env}. A live account trades real money."
        )
        return (
            f"CPZAI order: {field(inp, 'side').upper()} {field(inp, 'quantity')} {field(inp, 'symbol')} "
            f"{field(inp, 'order_type')}{price}, account {field(inp, 'account_id')} "
            f"(credential {field(inp, 'broker_credential_id')}). {env_note} Approve to place it once."
        )
    if tool == "execute_strategy":
        override = " with a code override" if inp.get("code") else ""
        return (
            f"CPZAI strategy run: strategy {field(inp, 'strategy_id')}{override}. "
            "A strategy run executes the strategy's code and can submit orders; it is not a backtest. "
            f"Default trading environment: {default_env}. Approve to run it once."
        )
    if tool == "delete_webhook":
        return (
            f"CPZAI: delete webhook {field(inp, 'id')}. Its signing secret cannot be recovered. "
            "Approve to delete it."
        )
    return f"CPZAI: {tool} changes your CPZAI account. Approve to run it once."


UNREADABLE = "CPZAI safety guard could not read this tool call. Review it before approving."


def decide(raw: str) -> str | None:
    """The reason to ask the user about this call, or None to leave the normal permission flow.

    This hook only runs for the CPZAI tools hooks.json matches, so anything it
    cannot read, or a name it does not recognise, is asked about: the guard
    fails closed, never open.
    """
    try:
        event = json.loads(raw) if raw.strip() else None
    except (json.JSONDecodeError, ValueError):
        event = None
    if not isinstance(event, dict):
        return UNREADABLE
    name = event.get("tool_name") or event.get("toolName")
    if not isinstance(name, str) or not name:
        return UNREADABLE
    m = TOOL_NAME.match(name)
    if not m or m.group(1) not in GUARDED:
        return f"CPZAI safety guard does not recognise the tool {name[:80]}. Review it before approving."
    # The user's own opt-out (userConfig.require_trade_confirmation = false).
    if not confirmation_required():
        return None
    inp = event.get("tool_input") if "tool_input" in event else event.get("toolInput")
    if not isinstance(inp, dict):
        inp = {}
    return describe(m.group(1), inp, option("DEFAULT_ENVIRONMENT", "paper") or "paper")


def main() -> int:
    try:
        reason = decide(sys.stdin.read())
    except Exception as e:  # Fail closed: an error here must never let the call through unasked.
        reason = f"{UNREADABLE} ({type(e).__name__})"
    if reason is not None:
        ask(reason)
    return 0


if __name__ == "__main__":
    sys.exit(main())
