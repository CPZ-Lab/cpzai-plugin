---
description: Generate a structured trade idea with entry, exit, sizing, and risk management — based on your portfolio context
argument-hint: " <ticker | theme | setup>"
---

# Trade Idea

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

**Important**: Trade ideas are generated for research and educational purposes only. They are not recommendations to buy or sell any security. All trading involves risk of loss. Make decisions independently and consider your own financial situation.

Generate a structured, institutional-quality trade idea with clear thesis, entry/exit levels, position sizing, risk management, and monitoring triggers.

## Usage

```
/cpzai:trade-idea <input>
```

### Arguments

- `input` — Starting point for the trade idea:
  - A ticker: `AAPL`, `NVDA`, `SPY` — analyze and generate a directional or neutral idea
  - A theme: `"AI infrastructure"`, `"rate cuts"`, `"oil supply shock"`
  - A setup: `"mean reversion on TSLA"`, `"momentum breakout in semis"`, `"pairs trade GOOGL vs META"`
  - A macro view: `"long duration"`, `"short vol"`, `"steepener"`

## Workflow

### 1. Portfolio Context

If ~~cpzai is connected:
- Call `list_positions` to understand current exposure
- Call `compute_risk` for portfolio-level risk metrics
- Call `list_accounts` for available capital and buying power
- Call `get_market_data` for current prices

Frame the idea relative to the user's existing portfolio — don't suggest buying something they're already overweight.

### 2. Thesis

State the trade thesis clearly and concisely:

```
TRADE IDEA — [TICKER or DESCRIPTION]
══════════════════════════════════════
Direction:  LONG | SHORT | NEUTRAL
Timeframe:  [Days/Weeks/Months]
Conviction: HIGH | MEDIUM | LOW
Thesis:     [2-3 sentence explanation of WHY this trade works]
```

The thesis must be grounded in at least one of:
- **Technical** — breakout, support/resistance, momentum, mean-reversion
- **Fundamental** — valuation gap, earnings catalyst, growth inflection
- **Quantitative** — factor exposure, statistical anomaly, relative value
- **Macro** — rates, FX, policy, cycle positioning
- **Event-driven** — earnings, M&A, index inclusion, regulatory

### 3. Trade Structure

Detail the exact trade setup:

```
ENTRY
═════
Instrument:   [Stock / ETF / Options structure]
Entry Price:   $XX.XX (current) or $XX.XX (limit, on pullback to [level])
Entry Trigger: [What needs to happen to enter]

TARGETS
═══════
Target 1:      $XX.XX (+X.X%) — [rationale: prior resistance, measured move, etc.]
Target 2:      $XX.XX (+XX.X%) — [rationale]

STOP LOSS
═════════
Stop:          $XX.XX (-X.X%) — [rationale: below support, below entry candle, etc.]
Invalidation:  [What kills the thesis entirely]
```

### 4. Position Sizing

Calculate sizing based on portfolio context:

```
SIZING
══════
Portfolio Value:    $XX,XXX
Risk per Trade:     X.X% of portfolio ($XXX)
Position Size:      XX shares ($X,XXX)
Stop Distance:      X.X%
Risk/Reward:        1:X.X (X.X R)
Kelly Fraction:     X.X% (half-Kelly recommended)
```

Sizing methods:
- **Fixed fractional** — risk 1-2% of portfolio per trade (default)
- **Volatility-scaled** — adjust for the ticker's volatility (ATR-based)
- **Kelly criterion** — optimal geometric growth (use half-Kelly for safety)

### 5. Risk/Reward Analysis

| Scenario | Price | P&L | Probability Est. |
|----------|-------|-----|-----------------|
| Bull (Target 2) | $XX.XX | +$XXX (+XX.X%) | ~XX% |
| Base (Target 1) | $XX.XX | +$XXX (+X.X%) | ~XX% |
| Stop Out | $XX.XX | -$XXX (-X.X%) | ~XX% |
| Worst Case | $XX.XX | -$XXX (-XX.X%) | ~X% |

**Expected value:** (P_bull × R_bull) + (P_base × R_base) + (P_stop × R_stop) = +X.X%

### 6. Correlation & Portfolio Impact

Assess how this trade interacts with existing positions:
- Correlation with current holdings
- Factor exposure overlap (are you doubling down on momentum, beta, etc.?)
- Sector concentration after adding this trade
- Impact on portfolio-level VaR

### 7. Monitoring Plan

Define what to watch after entry:

| Trigger | Action |
|---------|--------|
| Hits Target 1 | Take partial profit (50%), trail stop to breakeven |
| Breaks above $XX | Add to position (scale in) |
| Volume drops below average | Reduce conviction, tighten stop |
| Thesis invalidated by [event] | Exit immediately regardless of P&L |
| 30 days with no movement | Re-evaluate — time stop |

### 8. What Could Go Wrong

Explicitly state the bear case:
- What macro scenario kills this trade?
- What company-specific risk are you underestimating?
- What if the timing is wrong (right idea, wrong entry)?
- Where are the crowded exits if everyone is in the same trade?

### 9. Next Steps

- "Run `/cpzai:backtest` to test this setup historically"
- "Run `/cpzai:options-analysis` to structure this with defined risk"
- "Run `/cpzai:risk-report` to check portfolio impact before entering"
- "Run `/cpzai:equity-research` for deeper fundamental analysis"
