---
description: Analyze options strategies, Greeks, volatility surface, and derivatives positioning for a ticker
argument-hint: " <ticker> [strategy type]"
---

# Options Analysis

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

**Important**: Options involve significant risk and are not suitable for all investors. This analysis is for educational and research purposes only. All options trading decisions should be made independently with full understanding of the risks.

Analyze the options landscape for a given ticker — implied volatility, Greeks, strategy construction, and risk/reward profiles.

## Usage

```
/cpzai:options-analysis <ticker> [strategy type]
```

### Arguments

- `ticker` — The underlying asset to analyze (e.g. `AAPL`, `SPY`, `TSLA`)
- `strategy type` (optional) — Focus on a specific strategy:
  - `covered-call`, `protective-put`, `straddle`, `strangle`
  - `iron-condor`, `butterfly`, `vertical-spread`, `calendar-spread`
  - `collar`, `ratio-spread`
  - If omitted, provides a general volatility and options landscape overview

## Workflow

### 1. Current Market Context

If ~~cpzai is connected:
- Call `get_market_data` for the ticker (price, volume, recent move)
- Call `compute_risk` if the user holds the underlying (portfolio context)

Establish the setup:

```
OPTIONS ANALYSIS — [TICKER]
══════════════════════════
Underlying:     $XX.XX (X.X% today)
IV Rank:        XX/100 (percentile vs 52-week range)
IV Percentile:  XX%
HV (30d):       XX.X%
IV-HV Spread:   XX.X% (IV premium/discount to realized)
Put/Call Ratio:  X.XX
```

### 2. Volatility Assessment

Analyze the implied volatility environment:
- **IV Rank** — where current IV sits relative to its 52-week range
- **IV vs HV** — is implied vol rich or cheap relative to realized?
- **Term structure** — is the vol curve in contango (normal) or backwardation (fear)?
- **Skew** — how steep is the put skew? (risk reversal, 25-delta skew)
- **Earnings/events** — is elevated IV justified by upcoming catalysts?

### 3. Strategy Recommendation

Based on the volatility environment, recommend appropriate strategies:

| IV Environment | Direction View | Suggested Strategies |
|---------------|---------------|---------------------|
| High IV | Neutral | Iron condor, short strangle, butterfly |
| High IV | Directional | Vertical spread (sell premium side) |
| Low IV | Directional | Long calls/puts, debit spreads |
| Low IV | Neutral | Calendar spread, diagonal |
| Pre-earnings | Any | Straddle/strangle (long or short based on IV rank) |

### 4. Strategy Construction

For the selected or recommended strategy, detail:

```
STRATEGY: [Name]
═════════════════
Leg 1: [BUY/SELL] [Qty] [TICKER] [Expiry] [Strike] [Call/Put] @ $X.XX
Leg 2: [BUY/SELL] [Qty] [TICKER] [Expiry] [Strike] [Call/Put] @ $X.XX
...

Net Debit/Credit:  $X.XX per spread
Max Profit:        $X.XX (at $XX underlying)
Max Loss:          $X.XX (at $XX underlying)
Breakeven(s):      $XX.XX [, $XX.XX]
Probability of Profit: ~XX%
```

### 5. Greeks Profile

Present the position Greeks:

| Greek | Value | Interpretation |
|-------|-------|---------------|
| Delta | X.XX | Directional exposure |
| Gamma | X.XX | Rate of delta change |
| Theta | -$X.XX/day | Time decay (earning or paying) |
| Vega | $X.XX/1% IV | Volatility sensitivity |
| Rho | X.XX | Interest rate sensitivity |

Explain what each Greek means for this specific position.

### 6. Scenario Analysis

Show P&L at expiration across a range of underlying prices:

| Underlying Price | P&L | Notes |
|-----------------|-----|-------|
| $XX (-10%) | -$XXX | Max loss zone |
| $XX (-5%) | -$XX | ... |
| $XX (current) | +$XX | ... |
| $XX (+5%) | +$XXX | ... |
| $XX (+10%) | +$XXX | Max profit zone |

### 7. Risk Considerations

Flag key risks for the strategy:
- Assignment risk (for short options)
- Early exercise (American-style options)
- Pin risk near expiration
- Liquidity (bid-ask spread, open interest)
- Gap risk over weekends/earnings
- Margin requirements

### 8. Next Steps

- "Run `/cpzai:equity-research` for fundamental context on the underlying"
- "Run `/cpzai:risk-report` to see how this options position affects portfolio risk"
- "Run `/cpzai:backtest` to test a systematic options strategy"
