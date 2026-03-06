---
description: Get real-time quotes — price, change, volume, bid/ask — for one or more symbols
argument-hint: " <symbols>"
---

# Price

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Fetch real-time market data for one or more symbols and present a clean quote summary.

## Usage

```
/cpzai:price <symbols>
```

### Arguments

- `symbols` — One or more ticker symbols, space-separated:
  - Single: `AAPL`
  - Multiple: `AAPL MSFT GOOGL NVDA`
  - Crypto: `BTC/USD ETH/USD`
  - Index ETFs: `SPY QQQ IWM DIA`

## Workflow

### 1. Fetch Quotes

If ~~cpzai is connected:
- Call `get_market_data` with the requested symbols

If no connection:
> Connect your CPZAI account to pull real-time quotes. Go to **Settings → API Keys** to generate credentials.

### 2. Present Results

For a single symbol:

```
AAPL — Apple Inc.
$XXX.XX  ▲ $X.XX (+X.XX%)
Volume: XX.XM  |  Bid: $XXX.XX  |  Ask: $XXX.XX  |  Spread: $0.XX
```

For multiple symbols:

| Symbol | Price | Change | % Change | Volume | Bid | Ask |
|--------|-------|--------|----------|--------|-----|-----|
| AAPL | $XXX.XX | +$X.XX | +X.XX% | XX.XM | $XXX.XX | $XXX.XX |
| MSFT | $XXX.XX | -$X.XX | -X.XX% | XX.XM | $XXX.XX | $XXX.XX |
| ... | ... | ... | ... | ... | ... | ... |

### 3. Quick Context (if single symbol)

For a single ticker, add a one-line note on:
- Where price sits relative to 52-week range
- Unusual volume (if >1.5x average)
- Proximity to round numbers or key levels
