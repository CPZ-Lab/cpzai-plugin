#!/usr/bin/env python3
"""Tests for the plugin's hooks (cpzai#2908).

The pre-trade guard named the CPZAI tools mcp__cpzai__*, while Claude Code
lists a plugin's bundled MCP tools as mcp__plugin_cpzai_cpzai__*, so the
guard and the audit log never ran. And the guard blocked every call with
"ask the user and re-issue", keeping no record of the answer, so a fixed
name alone would have blocked a confirmed order forever.

Run: python3 tests/test_hooks.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "cpzai"
GUARD = PLUGIN / "scripts" / "pre_trade_guard.py"
AUDIT = PLUGIN / "scripts" / "audit_log.py"
HOOKS = json.loads((PLUGIN / "hooks" / "hooks.json").read_text())

PLUGIN_NAME = "mcp__plugin_cpzai_cpzai__{}"


def run_guard(event: dict | str, **env: str) -> dict | None:
    full_env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE_PLUGIN_OPTION_")}
    full_env.update(env)
    raw = event if isinstance(event, str) else json.dumps(event)
    out = subprocess.run([str(GUARD)], input=raw, capture_output=True, text=True, env=full_env, check=True)
    return json.loads(out.stdout) if out.stdout.strip() else None


def matcher(event: str) -> re.Pattern:
    entries = HOOKS["hooks"][event]
    return re.compile(entries[0]["matcher"])


ORDER = {
    "account_id": "PA3VZ41G5INS",
    "broker_credential_id": "6f1c2e2a-1111-4222-8333-944455556666",
    "symbol": "AAPL",
    "side": "buy",
    "order_type": "limit",
    "quantity": 10,
    "price": 200.5,
}


class HookMatchers(unittest.TestCase):
    def test_pre_and_post_hooks_match_the_names_claude_code_gives_plugin_tools(self):
        for event in ("PreToolUse", "PostToolUse", "PostToolUseFailure"):
            m = matcher(event)
            for tool in ("place_order", "execute_strategy", "delete_webhook", "create_strategy", "configure_overlay"):
                self.assertTrue(m.search(PLUGIN_NAME.format(tool)), f"{event} misses {tool}")
                self.assertTrue(m.search(f"mcp__cpzai__{tool}"), f"{event} misses standalone {tool}")

    def test_reads_are_not_matched(self):
        for event in ("PreToolUse", "PostToolUse"):
            m = matcher(event)
            for tool in ("list_positions", "list_orders", "cash_summary", "get_market_data"):
                self.assertIsNone(m.search(PLUGIN_NAME.format(tool)))
            # Another server's tool of the same name is not CPZAI's.
            self.assertIsNone(m.search("mcp__other__place_order"))

    def test_every_hook_command_exists_and_is_executable(self):
        for entries in HOOKS["hooks"].values():
            for entry in entries:
                for hk in entry["hooks"]:
                    path = PLUGIN / hk["command"].replace("${CLAUDE_PLUGIN_ROOT}/", "").split()[0]
                    self.assertTrue(path.exists(), path)
                    self.assertTrue(os.access(path, os.X_OK), path)


class PreTradeGuard(unittest.TestCase):
    def test_an_order_is_asked_about_once_in_claude_codes_own_prompt_never_blocked(self):
        out = run_guard({"tool_name": PLUGIN_NAME.format("place_order"), "tool_input": ORDER})
        self.assertIsNotNone(out)
        spec = out["hookSpecificOutput"]
        self.assertEqual(spec["hookEventName"], "PreToolUse")
        # "ask": the user approves in Claude Code's prompt and the call runs. Never "deny" or block.
        self.assertEqual(spec["permissionDecision"], "ask")
        self.assertNotIn("decision", out)
        reason = spec["permissionDecisionReason"]
        for part in ("BUY 10 AAPL", "limit 200.5", "PA3VZ41G5INS", "paper"):
            self.assertIn(part, reason)
        self.assertNotIn("re-issue", reason)

    def test_a_confirmed_call_is_not_blocked_again(self):
        # The same call twice: each answer is an ask the user can approve; nothing is ever a block.
        for _ in range(2):
            out = run_guard({"tool_name": PLUGIN_NAME.format("place_order"), "tool_input": ORDER})
            self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "ask")

    def test_strategy_runs_and_webhook_deletes_are_asked_about(self):
        run = run_guard({"tool_name": PLUGIN_NAME.format("execute_strategy"), "tool_input": {"strategy_id": "s-1"}})
        self.assertIn("can submit orders", run["hookSpecificOutput"]["permissionDecisionReason"])
        self.assertIn("not a backtest", run["hookSpecificOutput"]["permissionDecisionReason"])
        delete = run_guard({"tool_name": PLUGIN_NAME.format("delete_webhook"), "tool_input": {"id": "w-1"}})
        self.assertIn("w-1", delete["hookSpecificOutput"]["permissionDecisionReason"])

    def test_live_default_environment_is_named(self):
        out = run_guard({"tool_name": PLUGIN_NAME.format("place_order"), "tool_input": ORDER},
                        CLAUDE_PLUGIN_OPTION_DEFAULT_ENVIRONMENT="live")
        self.assertIn("default trading environment is live", out["hookSpecificOutput"]["permissionDecisionReason"])

    def test_opt_out_leaves_the_normal_permission_flow(self):
        self.assertIsNone(run_guard({"tool_name": PLUGIN_NAME.format("place_order"), "tool_input": ORDER},
                                    CLAUDE_PLUGIN_OPTION_REQUIRE_TRADE_CONFIRMATION="false"))

    # Review of plugin #1: the guard failed open on malformed events.
    def test_a_name_the_guard_does_not_recognise_is_asked_about(self):
        for name in (PLUGIN_NAME.format("list_positions"), "mcp__other__place_order"):
            out = run_guard({"tool_name": name, "tool_input": {}})
            self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "ask", name)

    def test_an_unreadable_event_is_asked_about_not_let_through(self):
        for raw in ("not json", "", "{}", "[]", '{"tool_input": {}}', '{"tool_name": 5}', '{"tool_name": null}', '{"tool_name": ["x"]}'):
            out = run_guard(raw)
            self.assertIsNotNone(out, raw)
            self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "ask", raw)

    def test_a_non_object_tool_input_still_asks(self):
        out = run_guard({"tool_name": PLUGIN_NAME.format("place_order"), "tool_input": "AAPL"})
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "ask")


class SessionBanner(unittest.TestCase):
    SCRIPT = PLUGIN / "scripts" / "session-start.sh"

    def banner(self, path: str | None = None, **env: str) -> str:
        full = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE_PLUGIN_OPTION_")}
        full.update(env)
        if path is not None:
            full["PATH"] = path
        return subprocess.run(["/bin/bash", str(self.SCRIPT)], capture_output=True, text=True, env=full, check=True).stdout

    def test_confirm_is_read_the_way_the_guard_reads_it(self):
        self.assertIn("confirm=true", self.banner())
        self.assertIn("confirm=true", self.banner(CLAUDE_PLUGIN_OPTION_REQUIRE_TRADE_CONFIRMATION="yes please"))
        for off in ("false", "FALSE", " off ", "0", "no"):
            self.assertIn("confirm=false", self.banner(CLAUDE_PLUGIN_OPTION_REQUIRE_TRADE_CONFIRMATION=off), off)

    def test_says_when_python3_is_missing(self):
        self.assertIn("guard=on", self.banner())
        with tempfile.TemporaryDirectory() as d:
            # The tools the banner uses, and no python3.
            for tool in ("tr", "cat"):
                os.symlink(shutil.which(tool), os.path.join(d, tool))
            out = self.banner(path=d)
        self.assertIn("guard=OFF (no working python3", out)
        self.assertIn("confirm=false", out)

    # Re-review of plugin #1: the /usr/bin/python3 stub on a Mac without the developer
    # tools passes `command -v` but cannot run anything; the banner said guard=on.
    def test_says_when_python3_exists_but_does_not_run(self):
        with tempfile.TemporaryDirectory() as d:
            for tool in ("tr", "cat"):
                os.symlink(shutil.which(tool), os.path.join(d, tool))
            stub = os.path.join(d, "python3")
            with open(stub, "w") as f:
                f.write("#!/bin/sh\necho 'xcode-select: note: No developer tools were found' >&2\nexit 1\n")
            os.chmod(stub, 0o755)
            out = self.banner(path=d)
        self.assertIn("guard=OFF (no working python3", out)
        self.assertIn("confirm=false", out)


class GuardFailure(unittest.TestCase):
    def test_a_guard_that_cannot_run_blocks_the_call(self):
        entry = HOOKS["hooks"]["PreToolUse"][0]["hooks"][0]
        self.assertTrue(entry["command"].endswith("pre_trade_guard.py"))
        self.assertEqual(entry.get("onFailure"), "block")


class AuditLog(unittest.TestCase):
    def run_audit(self, event: dict) -> dict:
        with tempfile.TemporaryDirectory() as d:
            env = {**os.environ, "CLAUDE_PLUGIN_DATA": d}
            subprocess.run([str(AUDIT)], input=json.dumps(event), text=True, env=env, check=True)
            lines = (Path(d) / "audit.log").read_text().splitlines()
            self.assertEqual(len(lines), 1)
            return json.loads(lines[0])

    def test_records_the_outcome_from_the_tool_response_never_assumes_ok(self):
        name = PLUGIN_NAME.format("place_order")
        self.assertIs(self.run_audit({"tool_name": name, "tool_input": ORDER, "tool_response": {"isError": True}})["ok"], False)
        self.assertIs(self.run_audit({"tool_name": name, "tool_input": ORDER, "tool_response": {"isError": False}})["ok"], True)
        rec = self.run_audit({"tool_name": name, "tool_input": ORDER})
        self.assertIsNone(rec["ok"])
        self.assertEqual(rec["tool"], name)

    # cpzai#3024: a refused order was logged ok, with no broker reply.
    def test_a_refused_order_is_logged_as_refused_with_the_reason(self):
        refusal = {"error": "Insufficient buying power", "code": "insufficient_buying_power"}
        rec = self.run_audit({
            "hook_event_name": "PostToolUse", "tool_name": PLUGIN_NAME.format("place_order"), "tool_input": ORDER,
            "tool_response": {"isError": True, "content": [{"type": "text", "text": json.dumps(refusal)}]},
        })
        self.assertIs(rec["ok"], False)
        self.assertEqual(rec["error"], "Insufficient buying power")

    def test_an_accepted_order_is_logged_with_the_broker_order_id_and_status(self):
        answer = {"data": {"id": "row-1", "order_id": "alp-123", "status": "accepted", "symbol": "AAPL"}}
        rec = self.run_audit({
            "hook_event_name": "PostToolUse", "tool_name": PLUGIN_NAME.format("place_order"), "tool_input": ORDER,
            "tool_response": {"content": [{"type": "text", "text": json.dumps(answer)}]},
        })
        self.assertIs(rec["ok"], True)
        self.assertEqual((rec["order_id"], rec["status"]), ("alp-123", "accepted"))

    # Re-review: a timed-out order may have been placed, so its outcome is unknown, not false.
    def test_a_trading_call_that_failed_without_an_answer_is_logged_as_unknown(self):
        rec = self.run_audit({"hook_event_name": "PostToolUseFailure", "tool_name": PLUGIN_NAME.format("place_order"),
                              "tool_input": ORDER, "error": "MCP request timed out", "is_interrupt": False, "duration_ms": 60012})
        self.assertIsNone(rec["ok"])
        self.assertEqual(rec["outcome"], "unknown: reconcile with list_orders before any resubmission")
        self.assertEqual(rec["error"], "MCP request timed out")
        self.assertEqual((rec["is_interrupt"], rec["duration_ms"]), (False, 60012))

    def test_other_state_changing_failures_are_unknown_too(self):
        rec = self.run_audit({"hook_event_name": "PostToolUseFailure", "tool_name": PLUGIN_NAME.format("create_strategy"),
                              "tool_input": {"title": "x"}, "error": "socket hang up", "is_interrupt": True, "duration_ms": 5})
        self.assertIsNone(rec["ok"])
        self.assertEqual(rec["outcome"], "unknown: check the resource before retrying")
        self.assertIs(rec["is_interrupt"], True)

    def test_redaction_covers_credential_like_fields_but_keeps_identifiers(self):
        rec = self.run_audit({"tool_name": PLUGIN_NAME.format("place_order"), "tool_response": {"isError": False},
                              "tool_input": {**ORDER, "Authorization": "Bearer abc", "x_bearer": "abc", "cookie": "c=1",
                                             "pass": "p", "pwd": "p", "pin": "1234", "private_key_pem": "k", "signature": "s",
                                             "credential": "c", "nested": {"auth_header": "h", "note": "fine"}}})
        inp = rec["input"]
        for k in ("Authorization", "x_bearer", "cookie", "pass", "pwd", "pin", "private_key_pem", "signature", "credential"):
            self.assertEqual(inp[k], "[redacted]", k)
        self.assertEqual(inp["nested"], {"auth_header": "[redacted]", "note": "fine"})
        # Which account the order went to stays on record.
        self.assertEqual(inp["broker_credential_id"], ORDER["broker_credential_id"])
        self.assertEqual(inp["account_id"], ORDER["account_id"])

    def test_a_connection_configuration_is_logged_as_key_names_only(self):
        rec = self.run_audit({"tool_name": PLUGIN_NAME.format("create_connection"), "tool_response": {"isError": False},
                              "tool_input": {"connection_type": "vipe", "configuration": {"base_url": "https://x", "login": "me@example.com"}}})
        self.assertEqual(rec["input"]["configuration"], {"fields": ["base_url", "login"]})
        self.assertNotIn("me@example.com", json.dumps(rec))

    def test_the_log_is_owner_only(self):
        with tempfile.TemporaryDirectory() as d:
            env = {**os.environ, "CLAUDE_PLUGIN_DATA": d}
            subprocess.run([str(AUDIT)], input=json.dumps({"tool_name": PLUGIN_NAME.format("place_order")}), text=True, env=env, check=True)
            self.assertEqual(os.stat(Path(d) / "audit.log").st_mode & 0o777, 0o600)

    def test_the_whole_order_is_kept_and_credentials_are_not(self):
        long_order = {**ORDER, "order_type": "stop_limit", "stop_price": 199.5, "client_order_id": "c" * 50}
        rec = self.run_audit({"tool_name": PLUGIN_NAME.format("place_order"), "tool_input": long_order, "tool_response": {"isError": False}})
        self.assertEqual(rec["input"], long_order)
        conn = self.run_audit({"tool_name": PLUGIN_NAME.format("create_connection"),
                               "tool_input": {"connection_type": "polygon", "api_key": "abc123", "secret_token": "s3cr3t"},
                               "tool_response": {"isError": False}})
        self.assertEqual(conn["input"], {"connection_type": "polygon", "api_key": "[redacted]", "secret_token": "[redacted]"})
        self.assertNotIn("abc123", json.dumps(conn))


if __name__ == "__main__":
    unittest.main(verbosity=2)
