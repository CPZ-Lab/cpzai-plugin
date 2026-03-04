---
description: Scan markets by sector, theme, or custom criteria with real-time data
argument-hint: " <sector | theme | symbols>"
---

# Market Scan

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

**Important**: Market scans provide information for research purposes only. They do not constitute buy/sell recommendations. All investment decisions should be made independently.

Scan a group of instruments using real-time market data and provide structured analysis.

## Usage

```
/cpzai:market-scan <target>
```

### Arguments

- `target` — What to scan:
  - A sector: `technology`, `healthcare`, `energy`, `financials`, etc.
  - A theme: `AI stocks`, `dividend aristocrats`, `small-cap value`, `EV supply chain`
  - A list of symbols: `AAPL MSFT GOOGL AMZN META`
  - A comparison: `AAPL vs MSFT`

## Workflow

### 1. Determine the Universe

Map the user's input to a concrete list of symbols:
- For sectors: use well-known constituents (top 10-20 by market cap)
- For themes: identify relevant tickers and explain the selection
- For explicit symbols: use as-is

### 2. Fetch Real-Time Data

If ~~cpzai is connected:
- Call `get_market_data` for all symbols in the universe
- Collect: price, change, volume, bid/ask spread

If no connection:
> Connect your CPZAI account to pull real-time quotes. I can still provide analysis frameworks and discuss the sector/theme qualitatively.

### 3. Market Overview Table

Present the scan results:

| Symbol | Price | Change | % Change | Volume | Rel. Volume | Spread |
|--------|-------|--------|----------|--------|-------------|--------|
| ... | ... | ... | ... | ... | ... | ... |

Sort by the most relevant column (% change for momentum scans, volume for activity scans).

### 4. Technical Context

For each symbol or the group overall, note:
- **Trend** — above/below key moving averages (50d, 200d)
- **Momentum** — RSI range, recent breakouts or breakdowns
- **Volume** — unusual activity relative to average
- **Volatility** — recent realized vol vs historical

### 5. Standouts

Highlight 2-4 notable observations:
- Biggest mover and possible catalyst
- Unusual volume (>2x average)
- Technical breakout/breakdown candidates
- Divergences within the group (one stock moving against the sector)

### 6. Ideas

Based on the scan, suggest research directions:
- Pairs that look interesting for mean-reversion
- Momentum names with confirmation signals
- Relative value opportunities within the sector
- Risk considerations for the group as a whole

Remind the user these are starting points for research, not recommendations.
