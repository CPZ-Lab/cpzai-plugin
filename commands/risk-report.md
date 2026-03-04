---
description: Generate a comprehensive risk report for your portfolio or a specific strategy
argument-hint: " [portfolio | strategy <name>]"
---

# Risk Report

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

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
- Call `list_positions` to get all open positions with market values
- Call `list_accounts` to get account-level info (buying power, equity)
- Call `get_market_data` for current prices on all held symbols
- Call `compute_risk` to get a fresh risk snapshot

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

Flag positions that:
- Exceed 20% portfolio weight (concentration risk)
- Have annualized volatility > 50%
- Are highly correlated with other positions (correlation > 0.8)
- Are at or near stop-loss levels

### 4. Concentration Analysis

Assess diversification across:
- **Single-name concentration** — largest position as % of portfolio
- **Sector concentration** — exposure by GICS sector
- **Factor concentration** — beta, momentum, value tilts
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
