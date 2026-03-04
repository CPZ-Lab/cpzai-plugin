---
name: risk-management
description: Portfolio and position risk management — VaR, drawdown controls, position sizing limits, correlation analysis, and hedging. Use when the user is analyzing risk, setting stops, sizing positions, or discussing portfolio protection.
---

# Risk Management

Frameworks for measuring, monitoring, and controlling risk in systematic trading portfolios.

## Core Risk Metrics

### Value at Risk (VaR)

The maximum expected loss over a given time horizon at a given confidence level.

**Parametric VaR (variance-covariance):**
```
VaR(95%, 1-day) = Portfolio Value × z_0.95 × σ_daily
                = Portfolio Value × 1.645 × σ_daily
```
Where σ_daily is the portfolio's daily standard deviation.

**Historical VaR:**
Sort historical daily P&L, take the 5th percentile (for 95% VaR). More robust to non-normal distributions.

**Monte Carlo VaR:**
Simulate thousands of return paths using fitted distributions, take the 5th percentile of simulated P&L.

**Interpretation:**
- VaR(95%, 1-day) = $10,000 means: on 19 out of 20 days, you expect to lose less than $10,000
- VaR does NOT tell you how bad the worst day can be — that's what CVaR addresses

### Conditional VaR (Expected Shortfall)

The average loss in the worst (1-α)% of scenarios. Always worse than VaR.

```
CVaR(95%) = E[Loss | Loss > VaR(95%)]
```

More useful than VaR because it captures tail risk. Regulators and risk managers increasingly prefer CVaR.

### Maximum Drawdown

The largest peak-to-trough decline in portfolio value.

```
Drawdown(t) = (Peak(t) - Value(t)) / Peak(t)
Max Drawdown = max(Drawdown(t)) for all t
```

**Recovery time:** how long from the trough back to the previous peak. Long recovery times can be psychologically and financially damaging.

**Rules of thumb:**
- Max drawdown of 2-3x the annualized standard deviation is typical
- If max drawdown exceeds 3x vol, something unusual happened (or the strategy has fat tails)
- Strategies with max drawdown > 30% are difficult for most investors to hold through

### Sharpe Ratio

Risk-adjusted return: `Sharpe = (R_p - R_f) / σ_p`

| Sharpe | Interpretation |
|--------|----------------|
| < 0.5 | Poor — not compensating for risk |
| 0.5-1.0 | Acceptable for long-only |
| 1.0-2.0 | Good — typical target for systematic strategies |
| 2.0-3.0 | Very good — strong edge |
| > 3.0 | Suspicious in backtest — likely overfit |

### Sortino Ratio

Like Sharpe but only penalizes downside deviation: `Sortino = (R_p - R_f) / σ_downside`

Better for strategies with asymmetric returns (e.g. options, trend following).

### Beta

Sensitivity of portfolio returns to the market: `β = Cov(R_p, R_m) / Var(R_m)`

- β = 1.0: moves with the market
- β = 0: market-neutral
- β < 0: inverse to market (rare for long portfolios)

## Position-Level Risk Controls

### Position Size Limits

- **Max single position:** 5-15% of portfolio (depending on strategy type)
- **Max sector exposure:** 25-35% of portfolio
- **Max correlated cluster:** no more than 3-5 highly correlated positions (r > 0.7)

### Stop-Loss Types

**Fixed percentage:** exit when position is down X% from entry. Simple, predictable.

**Volatility-based:** stop at entry - N × ATR. Adapts to the instrument's normal range.

**Trailing:** stop moves up with price but never down. Locks in gains. Distance can be fixed or ATR-based.

**Time-based:** exit after N days regardless of P&L. Useful for event-driven or catalyst strategies.

**Portfolio-level:** if total portfolio drawdown hits X%, reduce all positions by Y% or go flat.

### When Stops Get Hit

1. Execute immediately — do not "give it more room" after the fact
2. Log the reason and outcome for later analysis
3. If stops are hitting too frequently, the entry signal may need adjustment — don't just widen stops

## Portfolio-Level Risk Controls

### Exposure Limits

| Metric | Conservative | Moderate | Aggressive |
|--------|-------------|----------|------------|
| Gross exposure | 100% | 150% | 200% |
| Net exposure | 50-100% | 0-100% | -50% to 150% |
| Max single name | 5% | 10% | 15% |
| Max sector | 20% | 30% | 40% |
| Max drawdown trigger | 10% | 15% | 25% |

### Correlation Management

Diversification only works when correlations are low. Monitor:

- **Pairwise correlations** between positions (correlation matrix)
- **Correlation to market** (portfolio beta)
- **Correlation regime** — correlations spike during crises ("correlation goes to 1 in a crash")
- **Effective number of bets** = 1 / Σ(w_i²) adjusted for correlations

### Drawdown Response Protocol

1. **Warning level (50% of max tolerance):** Review positions, tighten stops, reduce new entries
2. **Caution level (75% of max tolerance):** Cut position sizes by 50%, no new positions
3. **Stop level (max tolerance hit):** Flatten portfolio, pause trading, review strategy
4. **Recovery:** Restart at reduced size, scale back up gradually over 1-2 weeks

## Stress Testing

### Historical Scenarios

Test portfolio against known market events:
- 2008 Financial Crisis (Sep-Nov 2008)
- 2020 COVID Crash (Feb-Mar 2020)
- 2022 Rate Shock (Jan-Oct 2022)
- Flash crashes (May 2010, Aug 2015)
- Sector-specific events (oil crash 2014-2016, tech wreck 2000-2002)

### Custom Scenarios

Construct hypothetical shocks:
- What if SPY drops 10% in a week?
- What if VIX doubles?
- What if the 10Y yield moves 100bps?
- What if your largest position gaps down 20%?

Apply betas and correlations to estimate portfolio impact under each scenario.

## CPZAI Risk Tools

The CPZAI MCP server provides:
- `compute_risk` — fresh risk snapshot (VaR, Sharpe, drawdown, beta, risk score)
- `list_risk_snapshots` — historical risk data for trend analysis
- `list_positions` — current portfolio for position-level analysis
