---
description: Generate a comprehensive risk report for your portfolio or a specific strategy
argument-hint: "[portfolio | strategy <name>]"
allowed-tools:
  - mcp__plugin_cpzai_cpzai__list_positions
  - mcp__plugin_cpzai_cpzai__list_accounts
  - mcp__plugin_cpzai_cpzai__cash_summary
  - mcp__plugin_cpzai_cpzai__get_market_data
  - mcp__plugin_cpzai_cpzai__get_bars
  - mcp__plugin_cpzai_cpzai__compute_risk
  - mcp__plugin_cpzai_cpzai__list_risk_snapshots
---

# Risk Report

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).
>
> Use only figures a CPZAI tool returns. Anything a template below asks for that no tool provides (see [What the Tools Return](../CONNECTORS.md#what-the-tools-return-and-what-they-do-not)) is written "not available from CPZAI", never filled from memory.

**Important**: Risk metrics are estimates based on historical data and models. They do not predict future losses. All risk assessments should be reviewed by qualified professionals.

Pull live positions, compute risk metrics, and produce an actionable risk report with flagged issues and recommendations.

## Usage

```
/cpzai:risk-report [scope]
```

### Arguments

- `scope` (optional) — What to analyze:
  - No argument or `portfolio` — Full portfolio risk report
  - `strategy <name>` — Risk analysis for a specific strategy
  - `positions` — Position-level risk breakdown

## Workflow

### 1. Gather Current State

If ~~cpzai is connected:
- Call `list_positions` and keep paging (`offset` += rows returned) until a page comes back shorter than the limit; `count` is the page size, not the total. Read `account_errors`: an account named there was not read, so totals leave it out and say so
- Call `cash_summary` for equity and buying power per account (last sync; note `stale`)
- Call `get_market_data` for current prices on all held symbols
- Call `compute_risk` to get a fresh risk snapshot. Its figures are today's holdings replayed over `return_window`: quote `method_note` with them
- Call `get_bars` for a year of daily bars of each holding and SPY, for the position-level figures below

If no connection:
> Connect your CPZAI account to pull live portfolio data. To analyze manually, provide your current positions (symbol, quantity, entry price).

### 2. Risk Metrics Summary

Present the core metrics in a dashboard format:

```
RISK DASHBOARD — [Date]
═══════════════════════

Portfolio Value:     $XX,XXX
Daily P&L:          $X,XXX (X.X%)

Value at Risk (95%): $X,XXX (X.X% of portfolio)
Conditional VaR:     $X,XXX
Max Drawdown:        X.X% (from $XX,XXX peak)
Current Drawdown:    X.X%

Sharpe Ratio:        X.XX
Sortino Ratio:       X.XX
Beta (vs SPY):       X.XX
Risk Score:          X/100
```

### 3. Position-Level Analysis

Break down risk by position:

| Symbol | Weight | P&L | Beta | Vol (Ann.) | Contribution to VaR |
|--------|--------|-----|------|------------|---------------------|
| ... | ... | ... | ... | ... | ... |

Weight and P&L come from `list_positions`. Beta (against SPY), annualized volatility and contribution to VaR are computed from the `get_bars` daily returns and the weights; say they were computed here. `compute_risk` returns no per-holding beta or volatility.

Flag positions that:
- Exceed 20% portfolio weight (concentration risk)
- Have annualized volatility > 50%
- Are highly correlated with other positions (correlation > 0.8)
- Are at or near stop-loss levels

### 4. Concentration Analysis

Assess diversification across:
- **Single-name concentration** — largest position as % of portfolio
- **Sector concentration**: from each position's `sector` in `list_positions`; "sector not recorded" where it is null
- **Factor concentration**: not available from CPZAI (no tool returns factor exposures); beta from `get_bars` only
- **Correlation** — average pairwise correlation of positions

### 5. Risk Flags

Identify and prioritize issues:

| Priority | Flag | Detail | Suggested Action |
|----------|------|--------|-----------------|
| HIGH | ... | ... | ... |
| MEDIUM | ... | ... | ... |
| LOW | ... | ... | ... |

Common flags:
- VaR exceeds 5% of portfolio value
- Single position > 25% weight
- Max drawdown approaching historical worst
- Sharpe below 0.5
- High correlation cluster (3+ positions with r > 0.7)

### 6. Recommendations

Provide 2-4 specific, actionable recommendations:
- Position reductions to fix concentration
- Hedge suggestions (sector ETFs, put spreads)
- Stop-loss adjustments
- Rebalancing triggers

### 7. Historical Context

If `list_risk_snapshots` returns history:
- Show risk score trend over the last 30 days
- Highlight any deterioration or improvement
- Note if current risk is above/below the user's historical average
