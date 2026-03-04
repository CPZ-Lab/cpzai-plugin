---
name: alpha-research
description: Alpha signal research — information coefficient, feature engineering, machine learning for finance, alpha combination, signal decay, and research workflow. Use when the user is researching new signals, evaluating alpha, combining factors, applying ML to trading, or analyzing signal quality.
---

# Alpha Research

The systematic process of discovering, validating, and combining predictive signals for financial returns.

## What Alpha Is (and Isn't)

**Alpha** is the component of returns not explained by systematic risk factors. In practice, it's the edge your signal has after accounting for market exposure, known factors, and transaction costs.

```
R_strategy = α + β₁F₁ + β₂F₂ + ... + ε
```

If α is statistically significant and survives transaction costs, you have a tradeable signal. If it's explained by known factors (market, value, momentum, etc.), you have factor exposure, not alpha.

**Alpha decay:** All alpha signals degrade over time as:
- Other participants discover the same signal
- Market structure changes
- The economic driver behind the signal weakens
- Capacity gets saturated

Typical half-life: 1-5 years for fundamental signals, months for technical signals, minutes to hours for microstructure signals.

## Information Coefficient (IC)

The core metric for evaluating predictive signals.

### Definition

```
IC = rank_correlation(signal_t, forward_return_{t+1})
```

The Spearman rank correlation between your signal values today and the subsequent asset returns. Computed cross-sectionally (across all assets at each time point).

### Interpreting IC

| IC | Interpretation | Typical Source |
|----|---------------|----------------|
| 0.00-0.02 | Noise | Random signal |
| 0.02-0.05 | Weak but potentially tradeable | Most real alpha signals |
| 0.05-0.10 | Strong | Exceptional signal or short horizon |
| 0.10+ | Suspiciously strong | Check for look-ahead bias or data errors |

**Important:** An IC of 0.03 sounds pathetically small, but it's actually a legitimate trading signal. The Fundamental Law of Active Management explains why:

```
IR ≈ IC × √BR
```

Where IR = information ratio, BR = breadth (number of independent bets per year). With IC = 0.03 and BR = 500 (trading 500 stocks daily), IR ≈ 0.03 × √500 ≈ 0.67 — a respectable risk-adjusted return.

### IC Analysis Best Practices

**Time-series IC:** Compute IC at each time point, then analyze the distribution:
- Mean IC (average predictive power)
- IC standard deviation (stability)
- IC information ratio = Mean IC / Std IC (reward-to-variability of the signal)
- Percent of periods with positive IC (consistency)

**Decay profile:** Compute IC at different forward horizons (1d, 5d, 21d, 63d). The shape reveals optimal holding period:
- IC peaks at 1d → intraday/short-term signal
- IC peaks at 21d → monthly rebalancing signal
- IC monotonically increasing → momentum-like signal
- IC peaks then reverses → mean-reversion signal with specific horizon

### Turnover-Adjusted IC

Raw IC ignores the cost of acting on the signal. Adjust for turnover:

```
IC_net = IC - λ × turnover
```

Where λ scales transaction costs. A high-IC signal with 200% daily turnover may be worse than a low-IC signal with 20% monthly turnover after costs.

## Feature Engineering for Finance

### Transformations That Matter

**Cross-sectional standardization (z-scoring):**
```
z_i,t = (x_i,t - mean(x_t)) / std(x_t)
```
Rank assets relative to each other at each point in time. Removes the time-series level, isolates cross-sectional ranking.

**Winsorization:**
Clip extreme values to the 1st/99th (or 5th/95th) percentile. Financial data has fat tails; extreme outliers dominate z-scores and distort signals.

**Sector/industry neutralization:**
```
z_neutral_i,t = z_i,t - mean(z_{sector(i),t})
```
Removes sector effects so the signal predicts stock-specific returns, not sector rotation.

**Rate of change vs level:**
- Level signals: current P/E, current RSI
- Change signals: ΔP/E over 3 months, ΔRSI over 5 days
- Acceleration: Δ(ΔP/E) — second derivative
Often the change carries more information than the level.

### Feature Categories

**Price-based:**
- Returns over various horizons (1d, 5d, 21d, 63d, 252d)
- Volatility (realized, range-based)
- Volume profiles (relative volume, volume-price trend)
- Technical patterns (MA crossovers, breakouts, RSI extremes)

**Fundamental:**
- Valuation ratios (P/E, P/B, EV/EBITDA) — cross-sectional rank
- Quality metrics (ROE, gross margin stability, accruals)
- Growth (revenue growth, earnings revision, analyst estimate changes)
- Earnings surprises (SUE — standardized unexpected earnings)

**Alternative:**
- Sentiment (news sentiment scores, social media volume)
- Short interest (days to cover, utilization rate)
- Insider transactions (net buying/selling)
- Options flow (put/call ratio, unusual volume)
- Fund flows (ETF creation/redemption, 13F changes)

**Macro:**
- Yield curve slope (10Y-2Y spread)
- Credit spreads (high yield - investment grade)
- VIX level and term structure
- Dollar index (DXY)
- Commodity prices (oil, copper as growth proxies)

### Feature Pitfalls

- **Snooping:** building features after seeing the forward returns. All feature design must be motivated by economic logic, then validated out-of-sample.
- **Stale data:** fundamental data arrives quarterly; using it as if it's available daily is look-ahead bias.
- **Multicollinearity:** many financial features are highly correlated (P/E and EV/EBITDA, different momentum lookbacks). Use PCA or careful feature selection.

## Machine Learning for Finance

### Why ML in Finance Is Different

1. **Signal-to-noise ratio is extremely low.** Financial returns are dominated by noise. Models that work well in vision or NLP (where SNR is high) overfit aggressively on financial data.
2. **Non-stationarity.** The data-generating process changes over time (regime changes, policy shifts, market structure evolution). A model trained on 2010-2020 may fail in 2021+.
3. **Limited data.** 20 years of daily data = ~5,000 observations. With 100 features, you're in a severely overparameterized regime.
4. **Adversarial dynamics.** Other participants are adapting. Profitable signals attract capital, eroding the edge.

### Cross-Validation for Financial Time Series

**Never use random k-fold CV.** Financial data is autocorrelated; random folds create look-ahead bias.

**Correct approaches:**

**Walk-forward (expanding window):**
```
Train: [2010-2015] → Test: [2016]
Train: [2010-2016] → Test: [2017]
Train: [2010-2017] → Test: [2018]
...
```

**Rolling window:**
```
Train: [2010-2015] → Test: [2016]
Train: [2011-2016] → Test: [2017]
Train: [2012-2017] → Test: [2018]
...
```

**Purged and embargoed CV (Marcos Lopez de Prado):**
Remove observations near the train/test boundary to prevent information leakage from overlapping labels. Embargo period = label horizon + 1.

### Model Selection

| Model | Strengths | Weaknesses | Best for |
|-------|-----------|------------|----------|
| Linear regression (OLS/Ridge/Lasso) | Interpretable, stable, fast | Can't capture non-linear relationships | Baseline, factor combination |
| Random forest | Handles non-linearity, feature interactions | Overfits with many features, can't extrapolate | Feature importance, interaction discovery |
| Gradient boosting (XGBoost/LightGBM) | State-of-the-art for tabular data | Easy to overfit; requires careful regularization | Primary prediction model |
| Neural networks | Flexible, can model complex patterns | Data hungry, black box, unstable in finance | Very large datasets, alternative data |
| Ensemble (stacking) | Combines model strengths | Complexity, risk of overfitting the meta-learner | Final production models |

**For most quant applications, gradient boosting with strong regularization is the practical sweet spot.** Use early stopping on a validation set, limit tree depth (3-6), and use L1/L2 regularization.

### Regularization for Finance

- **Feature selection:** Start with 10-20 economically motivated features, not 500 data-mined ones
- **Tree constraints:** max_depth=4-6, min_samples_leaf=50+, max_features=0.3-0.5
- **Early stopping:** monitor OOS loss; stop when validation performance degrades
- **Temporal stability:** test that feature importances are stable across different training windows
- **Ensemble diversity:** combine models with different training windows, feature subsets, or model types

## Alpha Combination

### Why Combine

Individual signals are weak. Combining multiple orthogonal signals improves the signal-to-noise ratio:

```
IC_combined ≈ √(Σ IC²_i)     (if signals are uncorrelated)
```

Three signals with IC = 0.03 each → combined IC ≈ 0.05 (if orthogonal).

### Combination Methods

**Equal weight:**
Simple average of z-scored signals. Robust, no estimation error, often hard to beat.

**IC-weighted:**
Weight each signal by its recent IC. Adapts to signal strength over time, but introduces estimation error.

**Regression-weighted:**
Regress forward returns on all signals. Coefficients = optimal weights. Requires careful regularization to avoid overfitting.

**Conditional combination:**
Vary signal weights based on regime (e.g. momentum works better in trending markets, mean-reversion in ranging markets). Attractive in theory, dangerous in practice (regime classification is itself a hard problem).

### Orthogonalization

Before combining, neutralize each signal against the others:
```
signal_i_orthogonal = residual(signal_i regressed on signal_1, ..., signal_{i-1})
```

This reveals the unique information each signal contributes. If a signal has zero IC after orthogonalization, it's redundant.

## Research Workflow

### The Virtuous Cycle

```
1. Hypothesis → "Earnings surprises predict drift for 60 days"
2. Feature engineering → Compute SUE, standardize cross-sectionally
3. IC analysis → Compute IC at 1d, 5d, 21d, 63d horizons
4. Backtest → Build long-short portfolio, compute Sharpe after costs
5. Robustness → Walk-forward, sub-period stability, parameter sensitivity
6. Deployment → Paper trade, monitor live IC, compare to backtest
7. Monitoring → Track IC decay, model staleness, regime changes
```

### Research Anti-Patterns

- **Data mining without theory:** testing 1000 random features and reporting the 5 that work. These will fail out-of-sample.
- **In-sample hero:** optimizing until the backtest Sharpe is 5.0. This is curve-fitting, not alpha.
- **Ignoring costs:** a signal that generates 3bps of alpha but costs 10bps to trade is a loss generator.
- **Single-metric fixation:** only looking at Sharpe. Check IC stability, drawdown, turnover, capacity.
- **No decay monitoring:** deploying a signal and never checking if it's still working. Set up automated IC tracking.

### When to Kill a Signal

- IC has been negative for 3+ consecutive months
- Live performance is less than 50% of backtest performance for 6+ months
- The economic rationale no longer holds (regulatory change, market structure shift)
- Costs exceed gross alpha (signal is being arbitraged away)

## CPZAI Tool Chaining for Alpha Research

1. **`get_market_data`** — fetch current and historical prices for signal computation
2. **`list_strategies`** / **`get_strategy`** — review existing strategies and their signal logic
3. **`execute_strategy`** — run a backtest with the new signal
4. **`get_backtest_results`** — pull performance metrics (Sharpe, turnover, drawdown)
5. **`compute_risk`** — check factor exposures of the signal-driven portfolio
6. **`create_strategy`** — deploy the validated signal as a new strategy
