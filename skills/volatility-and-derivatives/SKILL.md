---
name: volatility-and-derivatives
description: Volatility modeling, options Greeks, volatility surface analysis, and derivatives strategies. Use when the user is analyzing volatility, pricing options, discussing Greeks, building vol strategies, or working with VIX/variance products.
---

# Volatility and Derivatives

Frameworks for understanding, modeling, and trading volatility — from basic Greeks to volatility surface dynamics and systematic vol strategies.

## Volatility Fundamentals

### Realized Volatility

Historical volatility computed from observed price changes.

**Close-to-close (standard):**
```
σ_realized = std(ln(P_t / P_{t-1})) × √252
```

**Yang-Zhang estimator (more efficient):**
Uses open, high, low, close to extract more information per bar. Reduces the estimation window needed by ~5x vs close-to-close. Preferred for short lookback windows.

**Parkinson estimator (range-based):**
```
σ² = (1/4n ln2) × Σ(ln(H_i/L_i))²
```
Uses high-low range only. More efficient than close-to-close but biased downward when markets gap.

### Implied Volatility

The volatility that equates the Black-Scholes option price to the observed market price. It encodes the market's expectation of future realized volatility, plus a risk premium.

**Key relationship:**
```
Implied Vol ≈ Expected Future Realized Vol + Variance Risk Premium
```

The variance risk premium (VRP) is typically positive — implied vol usually exceeds subsequent realized vol. This is why systematic option selling has historically been profitable (and why it blows up in tail events).

### Volatility Term Structure

Implied vol varies by expiration:

| Shape | Meaning | When it occurs |
|-------|---------|---------------|
| Contango (upward sloping) | Near-term calm, uncertainty further out | Normal markets |
| Backwardation (inverted) | Near-term fear exceeds long-term | Crisis, event risk |
| Flat | Uniform vol expectations | Transitional periods |

**VIX term structure** is the canonical example. VIX futures typically trade above spot VIX (contango). When the curve inverts, it signals severe stress.

### Volatility Skew and Smile

Implied vol varies by strike price:

**Equity skew:** OTM puts have higher implied vol than ATM or OTM calls. Reflects demand for downside protection and the empirical fact that equities crash more than they spike.

**Skew metrics:**
- **25-delta risk reversal:** IV(25d put) - IV(25d call). Measures skew direction. Negative for equities (puts more expensive).
- **25-delta butterfly:** (IV(25d put) + IV(25d call))/2 - IV(ATM). Measures smile curvature (wing richness).

**What skew tells you:**
- Steepening skew → market pricing more crash risk
- Flattening skew → complacency or positioning unwind
- Abnormally flat skew → potential opportunity to buy downside protection cheaply

## Options Greeks

### Delta (Δ)

Rate of change of option price with respect to underlying price.

```
Call delta: 0 to +1 (ATM ≈ 0.50)
Put delta:  -1 to 0 (ATM ≈ -0.50)
```

**Uses:**
- Hedge ratio (to delta-hedge, hold -Δ shares per option)
- Probability proxy (|Δ| ≈ probability of finishing ITM, roughly)
- Position sizing in delta-equivalent terms

### Gamma (Γ)

Rate of change of delta with respect to underlying price. Highest at ATM, near expiration.

```
Γ = ∂Δ/∂S = ∂²V/∂S²
```

**Why it matters:**
- Long gamma = profitable when the underlying moves (in either direction)
- Short gamma = profitable when the underlying doesn't move, but catastrophic in large moves
- Gamma risk concentrates near expiration for ATM options ("gamma risk at pin")

### Vega (ν)

Sensitivity to implied volatility. Typically quoted as dollar P&L per 1% move in vol.

```
Vega = ∂V/∂σ
```

**Characteristics:**
- Highest for ATM options
- Increases with time to expiration (longer-dated options have more vega)
- A "long vega" position profits when vol rises

### Theta (Θ)

Time decay — how much value the option loses per day, all else equal.

```
Θ = ∂V/∂t
```

**Key dynamics:**
- Theta accelerates as expiration approaches (especially for ATM)
- Theta is the "cost" of being long gamma
- Short options collect theta but bear gamma and tail risk
- Relationship: Θ + ½σ²S²Γ + rSΔ = rV (Black-Scholes PDE)

### Rho (ρ)

Sensitivity to interest rates. Usually small for short-dated options, matters for LEAPS and in high-rate environments.

### Greeks Interaction

The Greeks are not independent:

```
Gamma-Theta tradeoff: Long gamma → negative theta (you pay time decay for convexity)
Vega-Gamma relationship: Long-dated → high vega, low gamma; Short-dated → low vega, high gamma
Delta-Gamma: Δ changes as underlying moves; Γ tells you how fast
```

**Net portfolio Greeks:** Sum across all positions. A market-neutral portfolio has net delta ≈ 0, but may still have significant gamma, vega, and theta exposure.

## Volatility Modeling

### GARCH(1,1)

The workhorse volatility model. Captures volatility clustering (large moves follow large moves).

```
σ²_t = ω + α r²_{t-1} + β σ²_{t-1}
```

Where:
- ω = long-run variance weight
- α = reaction to recent returns (news coefficient)
- β = persistence of previous variance
- α + β < 1 for stationarity
- Long-run variance = ω / (1 - α - β)

**Typical equity values:** α ≈ 0.05-0.10, β ≈ 0.85-0.93

**Extensions:**
- **EGARCH:** allows asymmetric response (negative returns → higher vol increase than positive returns of same magnitude; "leverage effect")
- **GJR-GARCH:** adds an indicator for negative returns: σ²_t = ω + (α + γ I_{r<0}) r²_{t-1} + β σ²_{t-1}
- **GARCH-M:** adds volatility as a factor in the return equation (risk-return tradeoff)

### Realized Variance and Variance Swaps

**Realized variance:**
```
RV = (252/N) × Σ r²_i
```
Annualized sum of squared log returns. The payoff of a variance swap.

**Variance swap:**
A forward contract on future realized variance. Payoff = Notional × (RV - K_var). Fair strike K_var ≈ IV² (approximately the ATM implied vol squared, with skew adjustments).

**Variance risk premium:**
```
VRP = IV² - subsequent RV
```
Historically positive ~75% of the time in equities. Systematic variance selling captures this premium but has negative skewness and kurtosis (left-tail blowups).

### Volatility Cones

Compare current implied vol to the historical distribution of realized vol for the same tenor:

| Percentile | 1M RV | 3M RV | 6M RV | 1Y RV |
|-----------|-------|-------|-------|-------|
| 90th | ... | ... | ... | ... |
| 75th | ... | ... | ... | ... |
| 50th | ... | ... | ... | ... |
| 25th | ... | ... | ... | ... |
| 10th | ... | ... | ... | ... |
| Current IV | ... | ... | ... | ... |

If current IV is above the 90th percentile of historical RV, options look expensive. If below the 10th percentile, they look cheap. Context matters — vol can stay elevated for extended periods during regime changes.

## Systematic Volatility Strategies

### Short Volatility (Selling Premium)

**Strategies:**
- Sell OTM puts (cash-secured or spread)
- Sell strangles/straddles (ATM or near-ATM)
- Sell VIX call spreads when VIX > 25
- Sell variance swaps

**Risk profile:** Positive expected value (capture VRP), negative skew (small frequent wins, rare large losses). Blows up in tail events.

**Risk management is everything:**
- Hard stop-losses (close at 2-3x premium collected)
- Position size limits (no more than 2-3% portfolio risk per trade)
- Hedging tails (buy far OTM puts as insurance)
- Avoid selling vol before known events (earnings, FOMC, elections)

### Long Volatility (Buying Convexity)

**Strategies:**
- Buy OTM puts as tail hedges
- Buy straddles before catalysts
- Long VIX calls or call spreads
- Long variance swaps

**Risk profile:** Negative expected value (pay VRP), positive skew (small frequent losses, rare large wins). Portfolio insurance.

**Sizing for tail hedges:** Allocate 0.5-2% of portfolio per year to tail protection. Accept that most hedges expire worthless. The payout in a crash (5-10x on deep OTM puts in 2008, 2020) justifies the ongoing cost.

### Dispersion Trading

Sell index vol, buy single-stock vol (or vice versa). Exploits the difference between implied correlation and realized correlation.

```
Index Vol² ≈ Σ w²_i σ²_i + Σ_i≠j w_i w_j ρ_{ij} σ_i σ_j
```

When implied correlation > realized correlation (common), selling index vol and buying component vol is profitable.

### Volatility Relative Value

Trade volatility across:
- **Term structure:** sell expensive tenor, buy cheap tenor
- **Skew:** sell expensive wing, buy cheap wing
- **Cross-asset:** sell rich vol in one asset, buy cheap vol in a correlated asset

## CPZAI Tool Chaining for Volatility Analysis

1. **`get_market_data`** — fetch current prices and recent history for vol computation
2. **`compute_risk`** — get portfolio-level vol, VaR, and beta
3. **`list_positions`** — identify current exposures for Greeks netting
4. **`list_risk_snapshots`** — track vol regime changes over time
5. **Synthesize:** compare current implied levels to historical realized vol, identify whether vol is rich or cheap, recommend strategies with specific risk parameters
