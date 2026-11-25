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


class Formulas(unittest.TestCase):
    """cpzai#3012, #3022, #3023: formulas and rules the skills give Claude."""

    def test_risk_contributions_add_up_to_100_percent(self):
        body = text("skills/risk-management/SKILL.md")
        self.assertIn("MCTR_i = ∂σ_p / ∂w_i = (Σw)_i / σ_p", body)
        self.assertIn("Σ PCR_i = 100%", body)
        self.assertNotIn("Σ CR_i = σ²_portfolio", body)
        self.assertNotIn("MCTR_i = w_i × (Σw)_i / σ_portfolio", body)
        # Reference: a 4-asset book. The derivative of σ_p equals (Σw)_i/σ_p, and the
        # percent contributions w_i(Σw)_i/(w'Σw) add up to 1; the old CR_i = w_i²(Σw)_i/σ_p did not add up to σ².
        vol = [0.30, 0.20, 0.25, 0.05]
        corr = [[1, .5, .6, 0], [.5, 1, .4, .1], [.6, .4, 1, 0], [0, .1, 0, 1]]
        cov = [[vol[i] * vol[j] * corr[i][j] for j in range(4)] for i in range(4)]
        w = [.4, .25, .25, .1]
        sw = [sum(cov[i][j] * w[j] for j in range(4)) for i in range(4)]
        var = sum(w[i] * sw[i] for i in range(4))
        sp = var ** 0.5
        for i in range(4):
            h = 1e-7
            w2 = [w[j] + (h if j == i else 0) for j in range(4)]
            sp2 = sum(w2[a] * cov[a][b] * w2[b] for a in range(4) for b in range(4)) ** 0.5
            self.assertAlmostEqual((sp2 - sp) / h, sw[i] / sp, places=5)
        self.assertAlmostEqual(sum(w[i] * sw[i] / var for i in range(4)), 1.0, places=12)
        old_cr = [w[i] * (w[i] * sw[i] / sp) for i in range(4)]
        self.assertNotAlmostEqual(sum(old_cr), var, places=3)

    def test_risk_parity_is_described_as_equal_total_contribution(self):
        po = text("skills/portfolio-optimization/SKILL.md")
        self.assertNotIn("each asset's marginal contribution to portfolio volatility is identical", po)
        self.assertIn("the minimum-variance one", po)
        self.assertNotIn("`w_i = (1/σ_i) / Σ(1/σ_j)`. Equalizes risk contribution.", text("skills/strategy-development/SKILL.md"))

    def test_six_rules_from_3022(self):
        self.assertIn("IV(25d call) - IV(25d put)", text("skills/volatility-and-derivatives/SKILL.md"))
        self.assertNotIn("BR of ~125,000", text("skills/alpha-research/SKILL.md"))
        po = text("skills/portfolio-optimization/SKILL.md")
        self.assertIn("5,000 + 55 + 500 = 5,555", po)
        self.assertIn("scaled identity", po)
        self.assertNotIn("statistical significance (>30)", text("commands/backtest.md"))
        self.assertIn("(P_worst × R_worst)", text("commands/trade-idea.md"))

    def test_17a4_retention(self):
        body = text("skills/compliance-and-recordkeeping/SKILL.md")
        self.assertNotIn("order records for 6 years", body)
        self.assertNotIn("6-year order record retention", body)
        self.assertIn("order memoranda (Rule 17a-3(a)(6)) for 3 years", body)


class Orders(unittest.TestCase):
    """cpzai#3014, #3034: /trade matches place_order's fields and never resends blindly."""

    def test_trade_takes_a_stop_price_and_shares_only(self):
        body = text("commands/trade.md")
        self.assertIn("[stop price]", body)
        self.assertNotIn("`$500` for notional", body)
        self.assertNotIn("buy $1000 SPY", body)
        self.assertIn("Stop:       $XXX.XX", body)
        self.assertIn("`time_in_force: day` only", body)
        self.assertNotIn("(day, GTC, IOC, FOK)", text("skills/order-execution/SKILL.md"))

    def test_trade_never_resends_after_a_timeout(self):
        body = text("commands/trade.md")
        self.assertIn("Do not call `place_order` again", body)
        self.assertIn("not** guaranteed to be deduplicated", body)


class StrategyFormat(unittest.TestCase):
    """cpzai#3013: /strategy-builder writes the format Strategy Lab backtests."""

    def test_names_symbols_and_the_signal_interface(self):
        body = text("commands/strategy-builder.md")
        for part in ("SYMBOLS = [", "def generate_signals(data, state, **kwargs)", "def on_bar(context, data)", "No strategy interface function is available"):
            self.assertIn(part, body)


class Paging(unittest.TestCase):
    """cpzai#3037: a page of positions or orders is not the whole book."""

    def test_book_commands_page_until_a_short_page(self):
        for rel in ("commands/positions.md", "commands/portfolio-review.md", "commands/risk-report.md", "commands/orders.md"):
            self.assertIn("until a page comes back shorter than the limit", text(rel), rel)


if __name__ == "__main__":
    unittest.main(verbosity=2)
