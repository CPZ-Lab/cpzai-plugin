---
name: portfolio-analytics
description: Portfolio performance measurement — attribution, benchmarking, Sharpe decomposition, rebalancing, and reporting. Use when the user is reviewing portfolio performance, comparing to benchmarks, rebalancing, or generating reports.
---

# Portfolio Analytics

Measuring, attributing, and communicating portfolio performance.

## Performance Measurement

### Return Calculation

**Simple return:**
```
R = (V_end - V_start) / V_start
```
Use for single-period returns.

**Time-weighted return (TWR):**
```
TWR = Π(1 + R_i) - 1
```
Chains sub-period returns. Eliminates the effect of cash flows (deposits/withdrawals). This is the standard for comparing portfolio managers.

**Money-weighted return (IRR):**
Accounts for the timing and size of cash flows. Shows the investor's actual experience, including the impact of adding/removing capital.

**Use TWR for comparing strategies; use IRR for evaluating personal returns.**

### Annualization

```
Annualized Return = (1 + Total Return)^(252/trading_days) - 1
Annualized Volatility = Daily Volatility × √252
```

252 trading days per year is the standard convention for US equities.

### Benchmark Selection

Choose a benchmark that matches the strategy's investment universe and style:

| Strategy Type | Common Benchmark |
|--------------|-----------------|
| US large-cap long-only | S&P 500 (SPY) |
| US broad market | Russell 3000 (IWV) |
| US small-cap | Russell 2000 (IWM) |
| Market-neutral | 0% (absolute return) or T-bills |
| Global equity | MSCI ACWI |
| Fixed income | Bloomberg Aggregate (AGG) |
| 60/40 balanced | 60% SPY + 40% AGG |

A benchmark should be:
- Investable (you could buy it as an ETF)
- Representative of the opportunity set
- Known in advance (not selected after seeing results)

## Performance Attribution

### Brinson Attribution (Top-Down)

Decomposes excess return into allocation and selection effects.

**Allocation effect:** Did you overweight the right sectors?
```
Allocation_i = (w_portfolio_i - w_benchmark_i) × (R_benchmark_i - R_benchmark_total)
```

**Selection effect:** Did you pick the right stocks within each sector?
```
Selection_i = w_benchmark_i × (R_portfolio_i - R_benchmark_i)
```

**Interaction effect:**
```
Interaction_i = (w_portfolio_i - w_benchmark_i) × (R_portfolio_i - R_benchmark_i)
```

### Factor Attribution

Decomposes returns into factor exposures:

```
R_portfolio = α + β_market × R_market + β_size × R_size + β_value × R_value + ... + ε
```

Common factor models:
- **CAPM:** single factor (market)
- **Fama-French 3-factor:** market, size, value
- **Fama-French 5-factor:** + profitability, investment
- **Carhart 4-factor:** market, size, value, momentum

Alpha (α) is the return not explained by factor exposures — the strategy's genuine edge.

## Portfolio Statistics

### Risk-Return Profile

| Metric | Calculation | Purpose |
|--------|-------------|---------|
| Return (ann.) | Annualized TWR | How much you made |
| Volatility (ann.) | σ × √252 | How much it moved |
| Sharpe | (R - Rf) / σ | Return per unit of risk |
| Sortino | (R - Rf) / σ_down | Return per unit of downside risk |
| Max drawdown | Largest peak-to-trough | Worst-case loss |
| Calmar | R_ann / MaxDD | Return per unit of drawdown |
| Beta | Cov(R_p, R_m) / Var(R_m) | Market sensitivity |
| Alpha | R_p - β × R_m | Excess return above market exposure |
| R² | Correlation² with benchmark | How much is explained by benchmark |

### Drawdown Analysis

Track all drawdown episodes:

| # | Start | Trough | Recovery | Depth | Duration | Recovery Time |
|---|-------|--------|----------|-------|----------|--------------|
| 1 | ... | ... | ... | -XX% | XX days | XX days |
| 2 | ... | ... | ... | -XX% | XX days | XX days |

Key insights:
- Are drawdowns getting deeper over time? (deteriorating strategy)
- How long does recovery take? (test investor patience)
- Do drawdowns coincide with market drawdowns? (systematic risk)

## Rebalancing

### When to Rebalance

**Calendar-based:** fixed schedule (daily, weekly, monthly, quarterly). Simple, predictable, lower turnover.

**Threshold-based:** rebalance when any position drifts more than X% from target weight. More responsive, but can increase turnover in volatile markets.

**Signal-based:** rebalance when the strategy signal changes. Most responsive, highest turnover.

### Rebalancing Costs

Every rebalance incurs:
- Transaction costs (commissions + spread + slippage)
- Tax consequences (realizing gains/losses)
- Market impact (large rebalances move prices)

Optimal rebalancing frequency balances tracking error against transaction costs. For most systematic strategies, weekly or monthly rebalancing is sufficient.

### Tax-Aware Rebalancing

- Harvest losses when possible (sell losers, buy correlated replacement)
- Prefer selling short-term losses over long-term losses (higher tax benefit)
- Avoid wash sales (don't repurchase substantially identical security within 30 days)
- Consider holding period — long-term gains taxed at lower rate

## Reporting

### Daily Summary

```
Date: [Date]
Portfolio Value: $XX,XXX
Daily P&L: $X,XXX (X.X%)
MTD Return: X.X%
YTD Return: X.X%
Benchmark (SPY): X.X% (daily) / X.X% (YTD)
Active Return: X.X% (YTD)
```

### Monthly Report

Include:
1. Return summary (gross, net, benchmark, alpha)
2. Risk metrics (Sharpe, vol, drawdown, VaR)
3. Attribution (what drove returns — sectors, factors, specific positions)
4. Top/bottom contributors
5. Portfolio changes (new positions, exits)
6. Outlook / plan for next month

## CPZAI Portfolio Tools

- `list_positions` — current holdings with P&L
- `list_accounts` — account summaries (equity, buying power)
- `compute_risk` — risk metrics (VaR, Sharpe, drawdown, beta)
- `list_risk_snapshots` — historical risk data for trending
- `get_market_data` — real-time prices for performance calculation
- `sync_portfolio` — force-sync across connected brokers
