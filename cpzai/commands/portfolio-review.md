---
description: Full portfolio health check — positions, performance, diversification, and actionable insights
allowed-tools:
  - mcp__plugin_cpzai_cpzai__list_positions
  - mcp__plugin_cpzai_cpzai__list_accounts
  - mcp__plugin_cpzai_cpzai__cash_summary
  - mcp__plugin_cpzai_cpzai__get_market_data
  - mcp__plugin_cpzai_cpzai__get_bars
  - mcp__plugin_cpzai_cpzai__compute_risk
  - mcp__plugin_cpzai_cpzai__list_orders
  - mcp__plugin_cpzai_cpzai__list_risk_snapshots
---

# Portfolio Review

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).
>
> Use only figures a CPZAI tool returns. Anything a template below asks for that no tool provides (see [What the Tools Return](../CONNECTORS.md#what-the-tools-return-and-what-they-do-not)) is written "not available from CPZAI", never filled from memory.

**Important**: Portfolio reviews are informational and do not constitute investment advice. Consult a qualified financial advisor before making portfolio changes.

Conduct a comprehensive review of the user's live portfolio — positions, performance, diversification, risk, and improvement opportunities.

## Usage

```
/cpzai:portfolio-review
```

No arguments needed — pulls the full portfolio from connected accounts.

## Workflow

### 1. Gather Portfolio Data

If ~~cpzai is connected:
- Call `list_positions` for all open positions
- Call `cash_summary` for equity, cash and buying power per account (last sync; note `stale`)
- Call `list_accounts` for each account's broker and environment; it holds no balances
- Call `get_market_data` for current prices on all holdings
- Call `compute_risk` for the latest risk snapshot
- Call `list_orders` with status `filled` for recent trade history

If no connection:
> Connect your CPZAI account to pull your live portfolio. To review manually, provide your current holdings (symbol, shares, entry price).

### 2. Portfolio Overview

```
PORTFOLIO REVIEW — [Date]
═════════════════════════

Total Equity:        $XX,XXX
Cash / Buying Power: $XX,XXX (XX% of portfolio)
Positions:           XX open positions

Today's P&L:         $X,XXX (X.X%)   (from `get_market_data` day change x quantity)
```

### 3. Holdings Breakdown

| Symbol | Shares | Avg Cost | Current | P&L ($) | P&L (%) | Weight |
|--------|--------|----------|---------|---------|---------|--------|
| ... | ... | ... | ... | ... | ... | ... |
| **Total** | | | | **$X,XXX** | **X.X%** | **100%** |

Sort by weight (largest first).

### 4. Winners and Losers

**Top 3 Winners:**
| Symbol | P&L | Return | Holding Period |
|--------|-----|--------|---------------|
| ... | ... | ... | ... |

**Top 3 Losers:**
| Symbol | P&L | Return | Holding Period |
|--------|-----|--------|---------------|
| ... | ... | ... | ... |

### 5. Diversification Assessment

**Sector Exposure** (from each position's `sector` in `list_positions`; a position with no sector recorded is listed as "sector not recorded", never assigned one from memory):
| Sector | Weight | # Positions |
|--------|--------|-------------|
| ... | ... | ... |

**Key Observations:**
- Single-stock concentration risk (any position > 15%)
- Cash level relative to market conditions
- Long/short balance (if applicable)

### 6. Risk Summary

Pull from the `compute_risk` results. They are today's holdings replayed over `return_window`; quote its `method_note` and never present them as the account's own track record:
- VaR (95%, 1-day)
- Max drawdown (current and from peak)
- Sharpe and Sortino
- Portfolio beta
- Correlation concentration

### 7. Actionable Insights

Provide 3-5 specific observations, prioritized:

1. **Immediate** — Risks that should be addressed now (over-concentrated, stop-loss breached, margin risk)
2. **This week** — Rebalancing opportunities, harvesting winners/losers
3. **Strategic** — Longer-term adjustments (sector rotation, adding hedges, diversification)

### 8. Recent Activity Context

If recent orders are available:
- Summarize last 5-10 trades
- Note any patterns (buying dips, chasing momentum, averaging down)
- Flag if recent trades are increasing or decreasing concentration
