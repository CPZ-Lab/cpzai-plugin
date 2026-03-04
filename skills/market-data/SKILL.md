---
name: market-data
description: Market data sourcing, technical analysis, fundamental context, and data quality. Use when the user is fetching quotes, analyzing charts, discussing indicators, or working with financial data.
---

# Market Data

How to source, validate, and analyze financial market data for systematic trading.

## Data Types

### Price Data (OHLCV)

The foundation of most strategies. For each bar:
- **Open:** first trade price of the period
- **High:** highest trade price during the period
- **Low:** lowest trade price during the period
- **Close:** last trade price of the period (most commonly used for signals)
- **Volume:** number of shares/contracts traded

**Frequencies:** tick, 1-minute, 5-minute, 15-minute, hourly, daily, weekly, monthly.

For most systematic strategies, daily bars are sufficient. Use intraday only when the strategy requires it.

### Quote Data (Bid/Ask)

Real-time best bid and ask prices. The spread (ask - bid) is a direct trading cost.

- **Tight spread:** liquid instruments, easy to trade
- **Wide spread:** illiquid, costly to enter/exit

### Fundamental Data

Financial statement data (revenue, earnings, margins, balance sheet items). Available quarterly or annually.

- **Point-in-time:** use the data as it was available on each date (avoids look-ahead bias)
- **Restatements:** historical financials can change — point-in-time databases handle this

### Alternative Data

Non-traditional data sources: satellite imagery, credit card spending, web traffic, social sentiment, patent filings, SEC filings.

Useful for alpha research but harder to backtest reliably due to shorter histories and survivorship in the data vendors themselves.

## Technical Indicators

### Trend Indicators

**Moving Averages:**
- Simple (SMA): equal-weight of last N closes
- Exponential (EMA): more weight on recent prices
- Common periods: 10, 20, 50, 100, 200 days
- Signal: price above MA = uptrend; fast MA above slow MA = bullish crossover

**MACD (Moving Average Convergence Divergence):**
- MACD line = EMA(12) - EMA(26)
- Signal line = EMA(9) of MACD line
- Histogram = MACD - Signal
- Bullish when MACD crosses above signal line

### Momentum Indicators

**RSI (Relative Strength Index):**
- Range: 0-100
- RSI < 30: oversold (potential buy)
- RSI > 70: overbought (potential sell)
- Default period: 14 days

**Rate of Change (ROC):**
- ROC = (Price - Price_n) / Price_n × 100
- Positive = upward momentum, negative = downward

### Volatility Indicators

**ATR (Average True Range):**
- True Range = max(H-L, |H-Prev_C|, |L-Prev_C|)
- ATR = SMA or EMA of True Range over N periods
- Used for position sizing and stop placement

**Bollinger Bands:**
- Middle = SMA(20)
- Upper = SMA(20) + 2 × StdDev(20)
- Lower = SMA(20) - 2 × StdDev(20)
- Price at bands = potential reversal zone

### Volume Indicators

**VWAP (Volume-Weighted Average Price):**
- VWAP = Σ(Price × Volume) / Σ(Volume) for the session
- Institutional benchmark — buying below VWAP is considered good execution

**On-Balance Volume (OBV):**
- Cumulative sum of volume (add on up days, subtract on down days)
- Divergence between OBV and price can signal trend changes

## Data Quality

### Common Issues

| Issue | Description | Fix |
|-------|------------|-----|
| Missing data | Gaps in price history | Forward-fill or exclude; never interpolate |
| Corporate actions | Splits, dividends, mergers change price levels | Use adjusted prices for return calculations |
| Survivorship bias | Only current stocks in the dataset | Use point-in-time universe data |
| Stale quotes | After-hours or pre-market prices leaking in | Filter to regular trading hours |
| Duplicates | Same bar appearing twice | Deduplicate by timestamp |
| Timezone issues | Data in different timezones mixed | Normalize to a single timezone (UTC or ET) |

### Adjusted vs Unadjusted Prices

- **Adjusted prices:** retroactively modified for splits and dividends. Use for return calculations and backtesting.
- **Unadjusted prices:** the actual traded price on that day. Use for order execution and current trading.

Never mix adjusted and unadjusted in the same calculation.

### Data Validation Checks

Before using any dataset:
1. Check for gaps in timestamps
2. Verify OHLC relationship: Low ≤ Open, Close ≤ High
3. Check for zero or negative prices
4. Look for extreme returns (>50% daily) and verify they're real (splits, news)
5. Compare to a known source as a sanity check

## Data Sources on CPZAI

CPZAI integrates with multiple data providers:
- **Alpaca Markets** — real-time and historical US equities
- **Yahoo Finance** — broad coverage, free, good for research
- **FRED** — Federal Reserve economic data (rates, macro)
- **Databento** — institutional-grade tick data
- **CoinGecko** — cryptocurrency data
- **SEC EDGAR** — filings, 13F institutional holdings

### CPZAI MCP Tool

- `get_market_data` — fetch real-time quotes (price, bid/ask, volume) for any symbol
