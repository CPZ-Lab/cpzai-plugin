---
description: Preview upcoming earnings — expectations, key metrics to watch, historical patterns, and positioning ideas
argument-hint: " <ticker | watchlist | portfolio>"
---

# Earnings Preview

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

**Important**: Earnings previews are based on consensus estimates and historical patterns. Actual results may differ materially. This is not investment advice.

Generate a comprehensive earnings preview — consensus expectations, key metrics to watch, historical beat/miss patterns, and how to think about positioning.

## Usage

```
/cpzai:earnings-preview <target>
```

### Arguments

- `target` — What to preview:
  - A ticker: `AAPL`, `NVDA`, `TSLA`
  - `watchlist` — Preview earnings for all watchlist names with upcoming reports
  - `portfolio` — Preview earnings for current holdings with upcoming reports
  - A group: `mag7`, `faang`, `banks`, `semis`

## Workflow

### 1. Identify Upcoming Earnings

If ~~cpzai is connected:
- Call `list_positions` and `get_market_data` to check which holdings have upcoming earnings
- Use available data to ground the preview

For the target ticker(s), establish:

```
EARNINGS PREVIEW — [TICKER] ([Company Name])
══════════════════════════════════════════════
Report Date:     [Date] ([Before Market / After Market])
Fiscal Quarter:  Q[X] FY[YYYY]
```

### 2. Consensus Expectations

Present the key estimates:

| Metric | Consensus | Range (Low-High) | Year-Ago | YoY Change |
|--------|-----------|-------------------|----------|------------|
| EPS | $X.XX | $X.XX - $X.XX | $X.XX | +XX% |
| Revenue | $X.XXB | $X.XXB - $X.XXB | $X.XXB | +XX% |
| Gross Margin | XX.X% | — | XX.X% | +X.Xpp |
| Operating Margin | XX.X% | — | XX.X% | +X.Xpp |

Note recent estimate revisions:
- How many analysts revised up vs down in the last 30/60/90 days
- Direction and magnitude of the revision trend

### 3. Key Metrics to Watch

Beyond headline EPS and revenue, identify 3-5 company-specific KPIs:

For example (varies by company):
- **Apple**: iPhone units, Services revenue, China revenue, gross margin guidance
- **NVDA**: Data Center revenue, gaming mix, China export impact, guidance
- **TSLA**: Deliveries, automotive gross margin ex-credits, energy storage, FSD progress
- **Banks**: Net interest income, provision for credit losses, trading revenue

Explain why each metric matters more than headline numbers.

### 4. Historical Earnings Patterns

| Quarter | EPS Est. | EPS Actual | Surprise | Stock Move (1d) |
|---------|----------|-----------|----------|----------------|
| Q[X-1] | $X.XX | $X.XX | +X.X% | +X.X% |
| Q[X-2] | $X.XX | $X.XX | +X.X% | -X.X% |
| Q[X-3] | $X.XX | $X.XX | +X.X% | +X.X% |
| Q[X-4] | $X.XX | $X.XX | -X.X% | -X.X% |

Summarize:
- **Beat rate** — how often does this company beat consensus?
- **Typical surprise magnitude** — what's the average beat/miss in %?
- **Post-earnings drift** — does the stock tend to trend after earnings or mean-revert?
- **Options-implied move** — what is the straddle pricing in? How does it compare to actual historical moves?

### 5. Positioning Considerations

Discuss how different traders might approach this earnings event:

**If bullish:**
- Pre-earnings drift play (buy days before, sell before report)
- Holding through with defined risk (protective put, call spread)

**If bearish:**
- Put spread for defined-risk downside bet
- Short call spread if IV is elevated

**If neutral / vol play:**
- Straddle/strangle if implied move looks too cheap
- Iron condor if implied move looks too expensive
- Calendar spread to sell near-term IV, buy longer-dated

**IV context:**
- Current IV percentile heading into earnings
- Is premium rich or cheap relative to historical earnings moves?

### 6. Sector & Peer Context

- How have peers in the same sector reported so far this season?
- Any read-through from suppliers, customers, or competitors?
- Sector-level trends (spending environment, regulatory backdrop)

### 7. Catalyst Calendar

Note other events around the earnings date:
- Fed meetings, CPI/jobs reports near the date
- Other major earnings in the same week
- Ex-dividend dates, index rebalancing

### 8. Next Steps

- "Run `/cpzai:equity-research` for a full fundamental deep dive"
- "Run `/cpzai:options-analysis` to structure an earnings trade"
- "Run `/cpzai:risk-report` to see earnings exposure across your portfolio"
