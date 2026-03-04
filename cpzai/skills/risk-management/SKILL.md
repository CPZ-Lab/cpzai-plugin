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

## Factor Risk Models

Decompose portfolio risk into systematic (factor) and idiosyncratic (specific) components.

### Systematic vs Specific Risk

```
Total Risk² = Systematic Risk² + Specific Risk²
σ²_portfolio = w' B F B' w + w' D w
```

Where B = factor exposure matrix, F = factor covariance matrix, D = diagonal matrix of specific variances.

**Systematic risk** comes from exposure to common factors (market, sector, style). It's diversifiable across strategies but not within a single factor exposure.

**Specific risk** is unique to each security. It diversifies away with more positions. A well-diversified portfolio of 50+ stocks has specific risk that is small relative to factor risk.

### Common Factor Taxonomies

**Statistical factors (PCA-based):**
Extract principal components from the return covariance matrix. Factors are purely statistical — no economic interpretation. PC1 is usually the market, PC2 often captures a size or sector rotation.

**Fundamental factors:**
- Market (beta)
- Size (log market cap)
- Value (book-to-price, earnings yield)
- Momentum (12-1 month return)
- Volatility (realized vol)
- Quality (ROE, leverage, earnings stability)
- Growth (revenue growth, earnings growth)
- Liquidity (turnover, bid-ask spread)
- Sector (GICS classification dummies)

**Factor exposure estimation:**
Cross-sectional regression at each time period:
```
R_i,t = Σ_k β_i,k × f_k,t + ε_i,t
```
Where β_i,k = asset i's exposure to factor k, f_k,t = factor return at time t.

### Risk Budgeting

Allocate risk (not capital) across factors or strategies.

**Marginal contribution to risk (MCTR):**
```
MCTR_i = w_i × (Σw)_i / σ_portfolio
```

The change in portfolio risk from a small increase in position i. Useful for identifying which positions are driving total risk.

**Component risk:**
```
CR_i = w_i × MCTR_i
Σ CR_i = σ²_portfolio
```

Each position's share of total portfolio variance. If one position contributes 40% of risk but only 10% of weight, it's dominating the portfolio's risk profile.

**Risk budget target:** set desired risk contribution per position/factor/strategy, then optimize weights to match the budget.

### Liquidity Risk

Risk that positions cannot be exited at expected prices, especially during stress.

**Liquidity metrics:**
- **Days to liquidate:** Position value / (ADV × participation rate). Participation rate = 10-20% of volume is typical.
- **Liquidation cost:** estimated slippage if the full position is sold. Increases non-linearly with position size.
- **Liquidity-adjusted VaR:** standard VaR + liquidation cost. More realistic for less liquid portfolios.

**Liquidity rules of thumb:**
- No single position should be more than 1 day's ADV
- Total portfolio should be liquidatable in 3-5 trading days at <2% cost
- During crises, assume ADV drops 50-70%

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

## CPZAI Tool Chaining for Risk Analysis

When ~~cpzai is connected, execute this workflow:

1. **`list_positions`** — get all open positions with market values and entry prices
2. **`list_accounts`** — get account equity, buying power, margin usage
3. **`get_market_data`** — fetch current prices for all held symbols (for real-time P&L)
4. **`compute_risk`** — trigger a fresh risk computation (VaR, Sharpe, drawdown, beta, risk score)
5. **`list_risk_snapshots`** — pull historical risk data (last 30 snapshots) for trend analysis
6. **Synthesize:** combine position data with risk metrics to identify concentration, correlation clusters, and exposure limit violations. Compare current risk score to the 30-day trend. Flag deterioration.

If risk flags are identified:
7. **`place_order`** — execute risk-reduction trades (trim oversized positions, add hedges)
8. **`compute_risk`** — recompute to verify improvement after adjustments
