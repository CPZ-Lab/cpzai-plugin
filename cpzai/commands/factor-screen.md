---
description: Screen stocks by quantitative factors — value, momentum, quality, volatility, size, and custom signals
argument-hint: " <factor | theme> [universe]"
---

# Factor Screen

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

**Important**: Factor screens are quantitative filters for research purposes only. They do not constitute buy/sell recommendations. Factor performance is cyclical and past factor returns do not predict future results.

Screen a universe of stocks by quantitative factors — value, momentum, quality, low volatility, size, or custom composite signals.

## Usage

```
/cpzai:factor-screen <factor> [universe]
```

### Arguments

- `factor` — Which factor(s) to screen by:
  - Single factor: `value`, `momentum`, `quality`, `low-vol`, `size`, `growth`, `dividend`, `reversal`
  - Multi-factor: `value+quality`, `momentum+quality`, `value+momentum`
  - Custom: `"high ROE, low P/E, positive earnings revision"` (natural language)
- `universe` (optional) — Which stocks to screen:
  - `sp500`, `nasdaq100`, `russell2000`, `all` (default: S&P 500)
  - A sector: `technology`, `healthcare`, `financials`
  - A custom list: `AAPL MSFT GOOGL AMZN META NVDA TSLA`

## Workflow

### 1. Define the Factor Model

Map the user's request to specific quantitative metrics:

| Factor | Primary Metrics | Secondary Metrics |
|--------|----------------|-------------------|
| Value | P/E, P/B, EV/EBITDA | FCF yield, dividend yield, earnings yield |
| Momentum | 12-1 month return, 6-month return | 52-week high proximity, RS rating |
| Quality | ROE, gross margin stability, low accruals | Debt/equity, interest coverage, Piotroski F-score |
| Low Volatility | 1-year realized vol, beta | Max drawdown, downside deviation |
| Size | Market cap (small = factor exposure) | Revenue, enterprise value |
| Growth | Revenue growth, EPS growth, estimate revisions | Sales acceleration, margin expansion |
| Dividend | Dividend yield, payout ratio, growth streak | FCF coverage, dividend growth rate |
| Reversal | 1-month return (lowest = strongest) | RSI extremes, mean-reversion z-score |

### 2. Fetch Data

If ~~cpzai is connected:
- Call `get_market_data` for the universe to get current prices and volume
- Call `list_positions` to flag which screened stocks the user already owns

### 3. Screen Results

Present the top-ranked stocks:

```
FACTOR SCREEN — [Factor Name]
Universe: [Universe] | Stocks Screened: XXX
Date: [Today]
══════════════════════════════════════
```

| Rank | Symbol | Name | Factor Score | P/E | Momentum (12-1M) | ROE | Vol (1Y) |
|------|--------|------|-------------|-----|-------------------|-----|----------|
| 1 | ... | ... | ... | ... | ... | ... | ... |
| 2 | ... | ... | ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... | ... | ... |

Show top 15-20 results. Highlight any stocks the user currently holds.

### 4. Factor Commentary

Explain the current factor environment:
- **Factor regime** — which factors are working now (momentum, value, etc.)?
- **Crowding risk** — are popular factor portfolios getting overcrowded?
- **Macro context** — how do rate expectations, growth outlook affect factor performance?
- **Historical context** — where is this factor's recent performance vs its long-run average?

Reference the Fundamental Law of Active Management:
```
IR ≈ IC × √BR
```
Explain how factor breadth (number of stocks) affects expected performance.

### 5. Factor Correlations

Show how the selected factor interacts with others:

| Factor Pair | Correlation | Implication |
|-------------|-------------|-------------|
| Value × Momentum | -0.XX | Historically negative — combining improves diversification |
| Value × Quality | +0.XX | Moderate positive — quality-value is a natural pairing |
| Momentum × Low Vol | X.XX | ... |

### 6. Portfolio Construction Ideas

Suggest how to use the screen results:
- **Long-only tilt** — overweight top quintile, underweight bottom quintile
- **Long-short** — top decile long, bottom decile short (for sophisticates)
- **Multi-factor composite** — combine 2-3 orthogonal factors for higher IC
- **Sector-neutral** — neutralize sector bets to isolate stock-level alpha

### 7. Next Steps

- "Run `/cpzai:equity-research` on any of these names for a deep dive"
- "Run `/cpzai:strategy-builder` to build a systematic factor strategy"
- "Run `/cpzai:backtest` to test this factor's historical performance"
- "Run `/cpzai:risk-report` to check how factor exposure affects your portfolio"
