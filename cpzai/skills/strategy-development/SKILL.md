---
name: strategy-development
description: Quantitative strategy design — signal generation, factor models, universe construction, and strategy architecture. Use when the user is designing, writing, or discussing trading strategies, alpha signals, or systematic investment approaches.
---

# Strategy Development

Systematic approaches to building trading strategies that are testable, robust, and deployable.

## Strategy Archetypes

### Momentum / Trend Following

Buys assets that have been rising, sells assets that have been falling. Works across equities, futures, and FX.

**Signal types:**
- Time-series momentum: compare asset return over lookback to zero
- Cross-sectional momentum: rank assets by return, go long top decile, short bottom decile
- Moving average crossover: fast MA crosses above slow MA → long
- Breakout: price exceeds N-day high/low

**Key parameters:**
- Lookback period (typically 1-12 months; 1 month and 12 months most documented)
- Holding period (weekly to monthly rebalance)
- Volatility scaling (normalize position sizes by realized vol)

**Known risks:**
- Crash risk — momentum portfolios can reverse violently in regime changes
- Crowding — popular signals degrade as more capital chases them
- Transaction costs — high turnover erodes returns

### Mean Reversion

Bets that deviations from equilibrium will revert. Works best at shorter horizons (intraday to weekly).

**Signal types:**
- Z-score of price relative to moving average: enter when |z| > threshold, exit at z ≈ 0
- Pairs/cointegration: find cointegrated pairs, trade the spread
- RSI extremes: RSI < 30 → buy, RSI > 70 → sell (with confirmation)
- Bollinger Band reversion: enter at band touch, exit at midline

**Key parameters:**
- Lookback for mean calculation (20-60 days typical)
- Entry threshold (1.5-2.5 standard deviations)
- Exit threshold (0-0.5 standard deviations)
- Stop-loss distance (critical — mean reversion without stops can blow up)

**Known risks:**
- Regime change — the "mean" can shift permanently
- Gap risk — mean reversion during earnings/news can face large adverse moves
- Requires tight risk management

### Factor / Smart Beta

Builds portfolios tilted toward empirically documented return factors.

**Common factors:**
- Value: low P/E, P/B, EV/EBITDA relative to sector
- Size: small-cap premium (long small, short large)
- Quality: high ROE, low leverage, stable earnings
- Low volatility: low-beta or low-vol stocks outperform on risk-adjusted basis
- Momentum: covered above, but also used as a factor tilt

**Construction:**
1. Score each stock on the factor(s)
2. Rank and form portfolios (quintiles or deciles)
3. Go long top quintile, optionally short bottom quintile
4. Rebalance monthly or quarterly
5. Neutralize sector and market exposure if desired

### Statistical Arbitrage

Market-neutral strategies that exploit statistical mispricings across many instruments.

**Approaches:**
- Pairs trading with cointegration tests (Engle-Granger, Johansen)
- PCA-based: decompose returns into factors, trade residuals
- Event-driven: systematic response to earnings, splits, index changes
- Cross-asset: exploit lead-lag relationships between related instruments

### Multi-Asset / Cross-Asset

Strategies that trade across asset classes (equities, bonds, commodities, currencies).

**Approaches:**
- Risk parity across asset classes (equalize risk contribution from each)
- Carry strategies (harvest yield differentials — bond carry, FX carry, dividend yield)
- Trend following across futures (managed futures / CTA style)
- Macro factor timing (overweight equities when yield curve steep, credit spreads tight)

**Cross-asset considerations:**
- Different trading hours and settlement conventions
- Currency hedging for international positions
- Varying liquidity profiles across asset classes
- Correlation instability between asset classes (equity-bond correlation can flip sign)

## Capacity and Crowding

### Estimating Strategy Capacity

**Capacity** is the maximum AUM a strategy can manage before market impact erodes returns to zero.

```
Capacity ≈ (Gross Alpha - Fixed Costs) / (Impact Coefficient × Turnover)
```

**Rules of thumb:**
- High-frequency strategies: $10M-$100M capacity
- Daily systematic equity (500-stock universe): $100M-$1B
- Monthly factor strategies (large-cap): $1B-$10B+
- Lower liquidity = lower capacity

### Measuring Crowding

Crowding occurs when many participants hold the same positions, creating correlated exit risk.

**Crowding indicators:**
- **Short interest concentration:** many funds short the same names
- **13F overlap:** high ownership overlap across hedge funds
- **Factor valuation:** when value spreads compress, the value factor is crowded
- **Momentum crash risk:** when momentum portfolios have extreme sector or factor tilts
- **Correlation of returns among similar strategies:** rising correlation = rising crowding

**Impact of crowding:**
- Reduces forward alpha (the edge is shared among more participants)
- Increases tail risk (when crowded positions unwind, they unwind together)
- Creates gap risk (liquidity disappears when everyone wants to exit simultaneously)

## Signal Design Principles

1. **Economic rationale** — Every signal should have a plausible reason to work. Pure data-mined patterns are fragile.
2. **Simplicity** — Fewer parameters = less overfitting. If you need 10 parameters to make it work, it probably doesn't.
3. **Decay awareness** — Signals degrade over time as markets adapt. Build in monitoring.
4. **Transaction cost awareness** — A signal that generates 2bps of alpha but costs 5bps to trade is worthless.
5. **Capacity** — How much capital can the strategy absorb before moving markets? Matters for scaling.

## Universe Construction

Choosing which instruments to trade is as important as the signal itself.

**Filters:**
- Liquidity: minimum average daily volume (e.g. >$1M ADV)
- Price: avoid penny stocks (>$5 minimum)
- Market cap: define the tier (large, mid, small, micro)
- Listing: exclude ADRs, REITs, SPACs if they don't fit the model
- Data quality: require N days of clean history

**Universe size tradeoffs:**
- Narrow (20-50 stocks): easier to monitor, higher concentration risk
- Broad (200-500 stocks): better diversification, harder to analyze individually
- Full market (1000+): requires fully automated pipeline, statistical edge only

## Position Sizing

### Equal Weight
Every position gets 1/N of the portfolio. Simple, transparent, avoids concentration.

### Volatility Parity (Risk Parity)
Weight inversely proportional to volatility: `w_i = (1/σ_i) / Σ(1/σ_j)`. Equalizes risk contribution.

### Kelly Criterion
Optimal sizing: `f = (p * b - q) / b` where p = win probability, b = win/loss ratio, q = 1-p. In practice, use fractional Kelly (0.25-0.5x) to reduce variance.

### Signal-Weighted
Size proportional to signal strength. Stronger signals get larger positions. Requires well-calibrated signal magnitudes.

## CPZAI MCP Tools for Strategy Development

When ~~cpzai is connected, use these tools in sequence:

1. **`list_strategies`** — browse existing strategies for inspiration or iteration
2. **`get_strategy`** — inspect a specific strategy's configuration and parameters
3. **`create_strategy`** — create a new strategy from generated Python code
4. **`update_strategy`** — modify parameters or code of an existing strategy
5. **`execute_strategy`** — run the strategy on the compute backend (backtest or live)
6. **`get_backtest_results`** — pull performance metrics after execution

**Workflow:** Design the signal logic using the frameworks above, then call `create_strategy` to deploy it. Follow up with `execute_strategy` to backtest, and `get_backtest_results` to evaluate. Iterate by calling `update_strategy` with refined parameters.
