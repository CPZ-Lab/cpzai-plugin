---
description: Optimize portfolio allocation using quantitative methods — mean-variance, Black-Litterman, risk parity, or HRP
argument-hint: "[method] [constraints]"
allowed-tools:
  - mcp__plugin_cpzai_cpzai__list_positions
  - mcp__plugin_cpzai_cpzai__cash_summary
  - mcp__plugin_cpzai_cpzai__get_market_data
  - mcp__plugin_cpzai_cpzai__get_bars
  - mcp__plugin_cpzai_cpzai__compute_risk
  - mcp__plugin_cpzai_cpzai__list_risk_snapshots
---

# Optimize

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).
>
> Use only figures a CPZAI tool returns. Anything a template below asks for that no tool provides (see [What the Tools Return](../CONNECTORS.md#what-the-tools-return-and-what-they-do-not)) is written "not available from CPZAI", never filled from memory.

**Important**: Portfolio optimization outputs are model-dependent and sensitive to input assumptions. They should be treated as a starting point for analysis, not as definitive allocations. All portfolio decisions should be reviewed by qualified professionals.

Run portfolio optimization on your current holdings or a proposed portfolio — using mean-variance, Black-Litterman, risk parity, HRP, or minimum variance approaches.

## Usage

```
/cpzai:optimize [method] [constraints]
```

### Arguments

- `method` (optional) — Optimization approach:
  - `mean-variance` or `mv` — Classic Markowitz (default)
  - `black-litterman` or `bl` — Bayesian with market-implied priors
  - `risk-parity` or `rp` — Equal risk contribution
  - `hrp` — Hierarchical Risk Parity (Lopez de Prado)
  - `min-variance` or `minvol` — Minimum volatility portfolio
  - `max-sharpe` — Maximum Sharpe ratio portfolio
- `constraints` (optional) — Natural language constraints:
  - `"max 10% per position"`, `"long only"`, `"sector cap 30%"`
  - `"no more than 5% in any single name"`, `"target vol 12%"`

## Workflow

### 1. Gather Portfolio Data

If ~~cpzai is connected:
- Call `list_positions` to get current holdings and weights
- Call `get_market_data` for current prices
- Call `get_bars` for daily bars of every holding (and any candidate), one to three years: expected returns and the covariance matrix are estimated from these
- Call `compute_risk` for the current risk profile (it returns summary figures, not covariance inputs)
- Call `cash_summary` for total equity and cash

If no connection:
> Connect your CPZAI account to optimize your live portfolio. Alternatively, provide a list of holdings (symbol, weight or dollar amount).

### 2. Current Portfolio Assessment

Show what the user currently has:

```
CURRENT PORTFOLIO
═════════════════
Total Value:     $XX,XXX
Positions:       XX
Expected Return: XX.X% (annualized)
Volatility:      XX.X% (annualized)
Sharpe Ratio:    X.XX
Max Drawdown:    XX.X% (current holdings replayed over the bars used)
```

| Symbol | Current Weight | Return Contrib. | Risk Contrib. |
|--------|---------------|----------------|---------------|
| ... | XX.X% | XX.X% | XX.X% |

Risk Contrib. is each position's percent contribution `w_i (Σw)_i / (w'Σw)` from the `get_bars` covariance; the column adds up to 100%. Flag imbalances: positions where risk contribution far exceeds weight.

### 3. Run Optimization

Execute the selected optimization method:

**Mean-Variance:**
- Estimate expected returns (historical, CAPM, or shrinkage)
- Estimate covariance matrix (Ledoit-Wolf shrinkage recommended)
- Solve for optimal weights subject to constraints

**Black-Litterman:**
- Start with market-implied equilibrium returns
- Incorporate user views (if provided): "I think AAPL will outperform by 5%"
- Blend views with equilibrium using the BL formula

**Risk Parity:**
- Each asset contributes equally to total portfolio risk: `w_i (Σw)_i / (w'Σw) = 1/N`, solved numerically (inverse volatility is exact only when all correlations are equal)
- No return assumptions needed — purely risk-based

**HRP (Hierarchical Risk Parity):**
- Cluster assets by correlation
- Allocate within clusters using inverse variance
- No matrix inversion — more robust with many assets

### 4. Optimized Portfolio

Present the recommended allocation:

```
OPTIMIZED PORTFOLIO — [Method]
══════════════════════════════
Expected Return: XX.X% (annualized)
Volatility:      XX.X% (annualized)
Sharpe Ratio:    X.XX
Diversification Ratio: X.XX
```

| Symbol | Current Wt. | Optimal Wt. | Change | Action |
|--------|------------|------------|--------|--------|
| AAPL | 25.0% | 12.0% | -13.0% | Reduce |
| MSFT | 10.0% | 15.0% | +5.0% | Add |
| ... | ... | ... | ... | ... |
| *Cash* | 5.0% | 8.0% | +3.0% | Hold |

### 5. Efficient Frontier Context

Show where the current and optimized portfolios sit:

```
Risk-Return Tradeoff:
                    Return
                      |       * Max Sharpe
                      |     /
                      |   * Optimized
                      |  /
                      | * Current
                      |/
                      +------------ Volatility
                    Min Vol *
```

Present 3-4 points on the efficient frontier:
- Minimum variance portfolio
- Current portfolio
- Optimized portfolio
- Maximum Sharpe portfolio

### 6. Rebalancing Trade List

If the user wants to implement:

| Trade | Symbol | Side | Shares | Est. Value | Purpose |
|-------|--------|------|--------|-----------|---------|
| 1 | AAPL | SELL | 50 | $XX,XXX | Reduce concentration |
| 2 | MSFT | BUY | 30 | $XX,XXX | Increase allocation |
| ... | ... | ... | ... | ... | ... |

Estimate transaction costs and tax implications.

### 7. Sensitivity Analysis

Show how results change with different assumptions:
- **Return estimation method** — does the optimal portfolio change significantly?
- **Lookback period** — 1Y vs 3Y vs 5Y covariance
- **Constraint sensitivity** — how binding are the constraints?
- **Rebalancing frequency** — monthly vs quarterly vs annually

### 8. Next Steps

- "Run `/cpzai:risk-report` to validate the optimized portfolio's risk profile"
- "Run `/cpzai:backtest` to test the optimized allocation historically"
- "Run `/cpzai:factor-screen` to check factor exposures of the optimized portfolio"
