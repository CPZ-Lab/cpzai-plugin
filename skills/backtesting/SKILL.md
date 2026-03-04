---
name: backtesting
description: Backtesting methodology — historical simulation, performance metrics, overfitting avoidance, and walk-forward validation. Use when the user is running backtests, analyzing historical performance, or evaluating strategy robustness.
---

# Backtesting

Rigorous approaches to testing trading strategies on historical data without fooling yourself.

## Core Principles

1. **A backtest is a hypothesis test, not a proof.** Good backtest results mean the strategy *might* work. They don't guarantee anything.
2. **The more you test, the more likely you are to find something that looks good by chance.** Multiple testing bias is the #1 enemy.
3. **Out-of-sample performance is the only performance that matters.** In-sample results tell you how well you curve-fit.
4. **Transaction costs, slippage, and market impact are not optional.** A strategy that ignores these is fiction.

## Performance Metrics

### Return Metrics

| Metric | Formula | What it tells you |
|--------|---------|-------------------|
| Total return | (End - Start) / Start | Raw performance |
| Annualized return | (1 + Total)^(252/days) - 1 | Comparable across periods |
| Alpha | Strategy return - Beta × Market return | Return above market exposure |
| Information ratio | Alpha / Tracking error | Alpha per unit of active risk |

### Risk-Adjusted Metrics

| Metric | Formula | Good value |
|--------|---------|------------|
| Sharpe ratio | (Return - Rf) / Volatility | > 1.0 |
| Sortino ratio | (Return - Rf) / Downside vol | > 1.5 |
| Calmar ratio | Ann. return / Max drawdown | > 1.0 |
| Profit factor | Gross profits / Gross losses | > 1.5 |

### Trade-Level Metrics

| Metric | What it tells you |
|--------|-------------------|
| Win rate | % of trades that are profitable |
| Avg win / Avg loss | Payoff ratio — how much you make vs lose per trade |
| Max consecutive losses | Worst streak — tests psychological endurance |
| Avg holding period | How long positions are held |
| Turnover | How much of the portfolio is traded per period |

### The Metrics That Matter Most

For most systematic strategies, focus on:
1. **Sharpe ratio** — is the risk-adjusted return attractive?
2. **Max drawdown** — can you survive the worst period?
3. **Number of trades** — is there enough data for statistical significance?
4. **Profit factor** — is the strategy actually making more than it loses?
5. **Stability** — does it work across different time periods?

## Common Biases and How to Avoid Them

### Survivorship Bias

**Problem:** Testing on only stocks that exist today. Stocks that went bankrupt, got delisted, or were acquired are excluded — making results look better.

**Fix:** Use point-in-time constituent data. If testing an S&P 500 strategy, use the actual S&P 500 members as of each date, not today's members.

### Look-Ahead Bias

**Problem:** Using information in the backtest that wasn't available at the time. Common examples: using today's earnings data for last year's signal, using the full-sample mean for normalization.

**Fix:** Ensure every data point is strictly available before the signal date. Use expanding or rolling windows, never the full sample.

### Selection Bias (Data Snooping)

**Problem:** Testing 100 strategies and reporting the one that worked. With enough tests, something will look good by pure chance.

**Fix:**
- Limit the number of strategies you test
- Use Bonferroni or Holm correction for multiple comparisons
- Reserve an out-of-sample period that you never touch until final validation
- Report all strategies tested, not just the winners

### Overfitting

**Problem:** The strategy is optimized to match historical noise rather than genuine patterns. Telltale signs: Sharpe > 3 in backtest, too many parameters, performance only in one market regime.

**Fix:**
- Fewer parameters (ideally 2-5)
- Large sample size (>100 trades)
- Walk-forward validation
- Penalize complexity (would you bet your own money on this?)

## Walk-Forward Validation

The gold standard for robustness testing.

### Method

1. **Split data** into in-sample (IS) and out-of-sample (OOS) segments
2. **Optimize** on IS period
3. **Test** on OOS period (no changes allowed)
4. **Roll forward** — move the window and repeat

```
|------- IS1 -------|--- OOS1 ---|
          |------- IS2 -------|--- OOS2 ---|
                    |------- IS3 -------|--- OOS3 ---|
```

### Walk-Forward Efficiency

```
WFE = OOS Performance / IS Performance
```

- WFE > 0.5: good — strategy retains most of its edge out-of-sample
- WFE 0.3-0.5: acceptable — some degradation but still profitable
- WFE < 0.3: poor — strategy is likely overfit

### Anchored vs Rolling

- **Anchored:** IS always starts from the beginning. More data, but includes stale regimes.
- **Rolling:** Fixed IS window that slides forward. Adapts to regime changes, but less data.

## Statistical Significance

### Minimum Trade Count

A strategy needs enough trades for results to be meaningful.

| Confidence Level | Minimum Trades (rough) |
|-----------------|----------------------|
| Directional only | 30+ |
| Meaningful Sharpe | 100+ |
| Robust inference | 250+ |

With 20 trades, even a 70% win rate is not statistically significant. Don't trust small samples.

### Bootstrapping

Resample trades with replacement to estimate confidence intervals around key metrics. If the 5th percentile of bootstrapped Sharpe is still > 0, the strategy likely has genuine edge.

## Transaction Cost Modeling

### Components

| Cost | Typical Range | Impact |
|------|--------------|--------|
| Commission | $0-0.005/share | Negligible for most retail |
| Spread | 1-10 bps | Significant for frequent trading |
| Slippage | 2-20 bps | Depends on order size vs volume |
| Market impact | 5-100+ bps | Matters for larger orders |

### Rules of Thumb

- Assume 5-10 bps round-trip for liquid large-cap equities
- Assume 20-50 bps round-trip for small-cap or less liquid names
- If your strategy's gross Sharpe drops below 1.0 after costs, reconsider

## Production Monitoring and Model Governance

### Live Performance Tracking

Once a strategy is deployed, continuously compare live performance to backtest expectations:

| Metric | Backtest | Live | Ratio |
|--------|----------|------|-------|
| Sharpe | ... | ... | Live/BT |
| Max drawdown | ... | ... | ... |
| Win rate | ... | ... | ... |
| Avg trade P&L | ... | ... | ... |
| Turnover | ... | ... | ... |

**Acceptable degradation:** live Sharpe = 50-80% of backtest Sharpe is normal. Below 50% warrants investigation. Below 0 for 3+ months → pause and review.

### Automated Monitoring Alerts

Set alerts for:
- **IC degradation:** trailing 30-day IC drops below 0 for 5+ consecutive days
- **Drawdown breach:** live drawdown exceeds 1.5x backtest max drawdown
- **Turnover spike:** turnover exceeds 2x expected (signal may be oscillating)
- **Tracking error:** live returns diverge from paper/backtest by more than expected
- **Regime change:** correlation between strategy and market shifts significantly

### Model Review Cadence

| Frequency | Review |
|-----------|--------|
| Daily | P&L, fills, slippage, errors |
| Weekly | IC, risk metrics, exposure drift |
| Monthly | Performance vs benchmark, attribution, factor exposures |
| Quarterly | Full model review — is the thesis still valid? Parameter stability? |
| Annually | Deep review — competitive landscape, capacity, signal decay |

### When to Decommission a Strategy

1. Live Sharpe < 0.3 for 6+ months (after accounting for market regime)
2. The economic thesis is no longer valid (regulatory change, structural shift)
3. Signal IC has been persistently near zero for 3+ months
4. Capacity has been reached and impact is eating all alpha
5. A strictly better replacement strategy has been validated

Document the reason for decommission. Dead strategies are valuable post-mortems.

## CPZAI Tool Chaining for Backtesting

When ~~cpzai is connected, execute this workflow:

1. **`list_strategies`** — find the strategy to test (filter by name, type, or status)
2. **`get_strategy`** — inspect the strategy's code, parameters, and configuration
3. **`execute_strategy`** — run the backtest with specified date range and parameters
4. **`get_backtest_results`** — pull the full results (returns, Sharpe, drawdown, trade log)
5. **Analyze:** apply the metrics framework and robustness checks from this skill. Identify overfitting risks, regime sensitivity, and transaction cost impact.
6. **`update_strategy`** — adjust parameters based on findings
7. **Iterate:** repeat steps 3-5 with modified parameters. Compare results across runs to assess parameter sensitivity.

**Guardrail:** If testing multiple parameter sets, track all results — not just the best one. Report how many configurations were tested and the distribution of outcomes to avoid selection bias.
