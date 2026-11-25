#!/usr/bin/env python3
"""Content checks: commands, skills and agents send Claude to tools that
return what they ask for (cpzai#2797, #2886, #2906, #2909).

Run: python3 tests/test_content.py
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "cpzai"
P = "mcp__plugin_cpzai_cpzai__"
FILES = sorted([*PLUGIN.glob("commands/*.md"), *PLUGIN.glob("skills/*/SKILL.md"), *PLUGIN.glob("agents/*.md")])


def text(rel: str) -> str:
    return (PLUGIN / rel).read_text()


def tools(rel: str) -> set[str]:
    """The CPZAI tools a command allows or an agent may use (not its disallowedTools)."""
    fm = text(rel).split("\n---", 1)[0]
    out: set[str] = set()
    key = None
    for line in fm.splitlines():
        m = re.match(r"^([\w-]+):", line)
        if m:
            key = m.group(1)
            continue
        item = re.match(r"^\s*-\s*" + re.escape(P) + r"([a-z_]+)\s*$", line)
        if item and key in ("tools", "allowed-tools"):
            out.add(item.group(1))
    return out


class Backtests(unittest.TestCase):
    """#2797: no CPZAI tool starts a backtest, and execute_strategy can submit orders."""

    def test_nothing_backtests_with_execute_strategy(self):
        old = [
            "Call `execute_strategy` with the strategy ID and backtest parameters",
            "run the backtest with specified date range and parameters",
            "run a backtest with the new signal",
            "Follow up with `execute_strategy` to backtest",
            "run the strategy on the compute backend (backtest or live)",
        ]
        for f in FILES:
            body = f.read_text()
            for phrase in old:
                self.assertNotIn(phrase, body, f.relative_to(ROOT))

    def test_backtest_command_reads_saved_runs_only(self):
        self.assertNotIn("execute_strategy", tools("commands/backtest.md"))
        self.assertTrue({"get_backtest_results", "get_backtest_result"} <= tools("commands/backtest.md"))
        self.assertIn("No CPZAI tool starts a backtest", text("commands/backtest.md"))

    def test_the_research_agent_cannot_run_strategy_code(self):
        self.assertNotIn("execute_strategy", tools("agents/quant-researcher.md"))


class Balances(unittest.TestCase):
    """#2906: list_accounts holds no balances; cash_summary does."""

    def test_no_file_reads_balances_from_list_accounts(self):
        pattern = re.compile(r"`list_accounts`[^\n]*(equity|buying power|margin|capital|portfolio value)", re.I)
        for f in FILES:
            for line in f.read_text().splitlines():
                if pattern.search(line) and "no balances" not in line and "cash_summary" not in line:
                    self.fail(f"{f.relative_to(ROOT)}: {line.strip()}")

    def test_commands_that_show_balances_can_call_cash_summary(self):
        for rel in ("commands/positions.md", "commands/portfolio-review.md", "commands/risk-report.md",
                    "commands/trade.md", "commands/trade-idea.md", "commands/optimize.md", "commands/sync.md",
                    "agents/execution-reviewer.md", "agents/risk-auditor.md"):
            self.assertIn("cash_summary", tools(rel), rel)

    def test_portfolio_review_drops_figures_no_tool_has(self):
        body = text("commands/portfolio-review.md")
        for line in ("Margin Used:", "Week P&L:", "Month P&L:"):
            self.assertNotIn(line, body)


class History(unittest.TestCase):
    """#2909: history-based figures come from get_bars, not the quote or the risk check."""

    def test_commands_that_need_price_history_can_call_get_bars(self):
        for rel in ("commands/price.md", "commands/market-scan.md", "commands/optimize.md", "commands/risk-report.md",
                    "commands/trade-idea.md", "commands/options-analysis.md", "commands/factor-screen.md",
                    "agents/execution-reviewer.md"):
            self.assertIn("get_bars", tools(rel), rel)

    def test_optimize_takes_covariance_from_bars(self):
        self.assertNotIn("get current risk metrics (covariance inputs)", text("skills/portfolio-optimization/SKILL.md"))
        self.assertIn("covariance matrix are estimated from these", text("commands/optimize.md"))


class Unavailable(unittest.TestCase):
    """#2886, #2909: figures no tool returns are said to be unavailable, never filled from memory."""

    def test_every_command_carries_the_rule(self):
        for f in sorted(PLUGIN.glob("commands/*.md")):
            self.assertIn('"not available from CPZAI", never filled from memory', f.read_text(), f.name)

    def test_options_and_fundamentals_are_named_unavailable(self):
        self.assertIn("No CPZAI tool returns option chains, option quotes, implied volatility, IV rank, Greeks",
                      text("commands/options-analysis.md"))
        self.assertIn("No CPZAI tool returns fundamentals", text("commands/factor-screen.md"))
        self.assertIn("**Not available from any CPZAI tool:**", text("CONNECTORS.md"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
