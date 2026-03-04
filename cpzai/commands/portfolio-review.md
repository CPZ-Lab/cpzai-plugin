---
description: Full portfolio health check — positions, performance, diversification, and actionable insights
argument-hint: ""
---

# Portfolio Review

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

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
- Call `list_accounts` for account summaries (equity, buying power, margin)
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
Margin Used:         $XX,XXX

Today's P&L:         $X,XXX (X.X%)
Week P&L:            $X,XXX (X.X%)
Month P&L:           $X,XXX (X.X%)
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

**Sector Exposure:**
| Sector | Weight | # Positions |
|--------|--------|-------------|
| ... | ... | ... |

**Key Observations:**
- Sector over/under-weights vs a benchmark (e.g. S&P 500)
- Single-stock concentration risk (any position > 15%)
- Cash level relative to market conditions
- Long/short balance (if applicable)

### 6. Risk Summary

Pull from the `compute_risk` results:
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
