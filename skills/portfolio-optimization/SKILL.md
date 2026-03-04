---
name: portfolio-optimization
description: Portfolio construction and optimization — mean-variance, Black-Litterman, hierarchical risk parity, efficient frontier, and constrained optimization. Use when the user is allocating capital across assets, building optimal portfolios, setting target weights, or discussing diversification.
---

# Portfolio Optimization

Systematic approaches to determining how much capital to allocate to each asset, from classical mean-variance to modern machine-learning-aware methods.

## The Optimization Problem

Portfolio optimization answers: given N assets, what weights minimize risk for a target return (or maximize return for a given risk budget)?

```
minimize    w' Σ w                (portfolio variance)
subject to  w' μ ≥ r_target      (return constraint)
            Σ w_i = 1            (fully invested)
            w_i ≥ 0              (long-only, if applicable)
```

Where `w` = weight vector, `Σ` = covariance matrix, `μ` = expected return vector.

## Mean-Variance Optimization (Markowitz)

### The Efficient Frontier

The set of portfolios that offer the highest expected return for each level of risk. Any portfolio below the frontier is suboptimal — you can get more return for the same risk, or less risk for the same return.

**Analytical solution (unconstrained):**
```
w* = (1/λ) Σ⁻¹ μ
```
Where λ = risk aversion parameter. Higher λ → more conservative allocation.

**With constraints:** Use quadratic programming (e.g. `scipy.optimize.minimize` with `method='SLSQP'`).

### Why Raw Mean-Variance Fails in Practice

Markowitz optimization is notoriously unstable:

1. **Estimation error amplification** — Small errors in expected returns produce wild swings in optimal weights. The optimizer loves to exploit estimation errors.
2. **Concentrated portfolios** — Without constraints, the optimizer often puts 80%+ into 1-2 assets.
3. **Unstable over time** — Weights change dramatically month-to-month, generating huge turnover.
4. **Garbage in, garbage out** — Expected returns are nearly impossible to estimate accurately. A 1% error in expected return can flip the optimal portfolio.

**Rule of thumb:** Never use raw mean-variance without shrinkage, constraints, or both.

### Fixes for Mean-Variance Instability

**Shrinkage estimators (Ledoit-Wolf):**
Shrink the sample covariance matrix toward a structured target (e.g. constant correlation, single-factor model). Reduces estimation error dramatically.

```
Σ_shrunk = δ F + (1-δ) S
```
Where F = structured target, S = sample covariance, δ = shrinkage intensity (estimated from data). Use `sklearn.covariance.LedoitWolf`.

**Resampled efficient frontier (Michaud):**
1. Bootstrap many samples from the return distribution
2. Compute the efficient frontier for each sample
3. Average the weights across all samples
Produces more stable, diversified portfolios.

**Regularization:**
Add a penalty term for weight magnitude: `minimize w'Σw + λ||w||₂²`. Prevents extreme concentrations.

## Black-Litterman Model

Combines market equilibrium (what the market implies) with investor views (what you believe).

### Why It's Better Than Raw Mean-Variance

Instead of estimating expected returns from scratch (which is nearly impossible), Black-Litterman starts with the market's implied returns and adjusts them based on your views. This produces:
- More intuitive portfolios
- Stable weights even with small view changes
- Sensible starting point (market portfolio)

### Step-by-Step

**1. Extract implied equilibrium returns:**
```
π = δ Σ w_mkt
```
Where δ = risk aversion (typically 2.5), Σ = covariance matrix, w_mkt = market-cap weights.

These are the returns that, if everyone agreed on them, would make the market portfolio optimal.

**2. Express views:**

Views are statements like "I believe AAPL will outperform MSFT by 2% over the next year" or "I believe the tech sector will return 15%."

Express as: `P μ = Q + ε` where:
- P = pick matrix (which assets the view is about)
- Q = expected return of the view
- ε ~ N(0, Ω) = uncertainty of the view

**3. Combine prior and views:**
```
μ_BL = [(τΣ)⁻¹ + P'Ω⁻¹P]⁻¹ [(τΣ)⁻¹π + P'Ω⁻¹Q]
```

Where τ = scaling factor (typically 0.025-0.05), reflecting uncertainty in the equilibrium returns.

**4. Optimize with the blended returns:**
Use μ_BL as the expected return input to a standard mean-variance optimizer. The result tilts away from market-cap weights toward your views, proportional to your confidence.

### Calibrating View Confidence (Ω)

- **High confidence:** small Ω → weights move strongly toward your view
- **Low confidence:** large Ω → weights stay close to market equilibrium
- **Rule of thumb:** set Ω = diag(P (τΣ) P') × confidence_scalar, where confidence_scalar ranges from 0.1 (very confident) to 10 (low confidence)

## Hierarchical Risk Parity (HRP)

A machine-learning-inspired approach that doesn't require expected return estimates at all. Uses only the covariance matrix.

### Why HRP Exists

Mean-variance requires inverting the covariance matrix, which is unstable when assets are correlated. HRP avoids matrix inversion entirely.

### Algorithm

**1. Tree clustering:**
Compute a distance matrix from correlations: `d(i,j) = √(0.5(1-ρ_ij))`. Apply hierarchical clustering (single-linkage or Ward's method) to build a dendrogram.

**2. Quasi-diagonalization:**
Reorder the covariance matrix so that correlated assets are adjacent. This creates a block-diagonal-like structure.

**3. Recursive bisection:**
Split the sorted assets into two halves. Allocate capital between the halves inversely proportional to their variance. Recurse on each half until you reach individual assets.

### Properties

- No expected return input needed (avoids the hardest estimation problem)
- No matrix inversion (numerically stable)
- Respects correlation structure (clusters correlated assets together)
- Out-of-sample performance consistently competitive with or better than mean-variance
- Produces diversified portfolios by construction

### When to Use HRP vs Mean-Variance

| Scenario | Recommendation |
|----------|---------------|
| No strong return views | HRP (avoids return estimation entirely) |
| Strong directional views | Black-Litterman + mean-variance |
| Many assets, short history | HRP (more stable with limited data) |
| Few assets, long history | Mean-variance with shrinkage |
| Risk-parity mandate | HRP or inverse-volatility |

## Risk Parity

Allocate so each asset contributes equally to portfolio risk.

### Equal Risk Contribution (ERC)

Find weights such that: `w_i × (Σw)_i / (w'Σw) = 1/N` for all i.

This means each asset's marginal contribution to portfolio volatility is identical. Solved numerically (no closed-form).

### Inverse Volatility (Simple Approximation)

```
w_i = (1/σ_i) / Σ(1/σ_j)
```

Quick approximation that ignores correlations. Works well when correlations are roughly uniform.

### Leveraged Risk Parity

Risk parity portfolios tend to have low expected returns (because bonds get high weight). The Bridgewater approach: lever the risk-parity portfolio to match equity-like returns.

Key risk: leverage amplifies tail events. The 2013 "taper tantrum" and 2020 COVID crash both hit leveraged risk parity hard.

## Practical Constraints

Real portfolios need constraints beyond just "minimize variance":

### Common Constraints

| Constraint | Formula | Purpose |
|-----------|---------|---------|
| Long-only | w_i ≥ 0 | No short selling |
| Max position | w_i ≤ w_max | Concentration limits |
| Sector caps | Σ w_i (in sector) ≤ s_max | Sector diversification |
| Turnover | Σ \|w_new - w_old\| ≤ τ | Transaction cost control |
| Tracking error | √((w-w_b)'Σ(w-w_b)) ≤ TE_max | Benchmark deviation |
| Min holdings | count(w_i > 0) ≥ N_min | Diversification floor |
| Leverage | Σ \|w_i\| ≤ L_max | Gross exposure cap |

### Turnover Control

Reoptimizing every period without turnover constraints generates excessive trading. Approaches:

1. **Turnover constraint:** hard cap on total weight changes
2. **Transaction cost penalty:** add `λ_tc × Σ|w_new - w_old|` to the objective
3. **Rebalance bands:** only trade when weights drift beyond ±X% of target

### Tax-Aware Optimization

Add tax costs as asymmetric transaction costs:
- Selling winners: cost = gain × tax_rate
- Selling losers: benefit = loss × tax_rate (tax-loss harvesting)
- Short-term vs long-term rates differ

## CPZAI Tool Chaining for Portfolio Optimization

1. **`list_positions`** — get current portfolio weights and values
2. **`get_market_data`** — fetch prices for universe + current holdings
3. **`compute_risk`** — get current risk metrics (covariance inputs)
4. **Run optimization** — apply chosen method (HRP, mean-variance, risk parity) using the data above
5. **`place_order`** — execute the rebalancing trades
6. **`list_risk_snapshots`** — monitor risk before and after rebalancing
