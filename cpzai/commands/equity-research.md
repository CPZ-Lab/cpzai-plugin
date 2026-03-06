---
description: Generate a comprehensive equity research report on any publicly traded company
argument-hint: " <ticker | company name>"
---

# Equity Research

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

**Important**: Equity research reports are for informational purposes only. They do not constitute investment advice or buy/sell recommendations. All investment decisions should be made independently.

Generate a professional-grade equity research report with real-time data, analyst consensus, financials, and risk analysis — similar to institutional sell-side coverage.

## Usage

```
/cpzai:equity-research <target>
```

### Arguments

- `target` — What to research:
  - A ticker symbol: `AAPL`, `TSLA`, `NVDA`
  - A company name: `Apple`, `Tesla`, `Roblox` (resolved to the correct ticker automatically)

## Workflow

### 1. Resolve the Ticker

If the user provides a company name, resolve it to the correct ticker:
- Obvious mappings (e.g. "Tesla" → TSLA, "Apple" → AAPL, "Roblox" → RBLX) — proceed immediately
- Ambiguous names — confirm with the user before proceeding

### 2. Gather Data

If ~~cpzai is connected:
- Call `get_market_data` for the ticker to get current price, volume, change
- Use available market data to ground the report in real-time numbers

Supplement with research knowledge covering:
- Company overview and business segments
- Financial performance (revenue, EPS, margins, growth rates)
- Valuation multiples (P/E, EV/EBITDA, P/S, PEG)
- Recent developments and catalysts
- Analyst consensus ratings and price targets
- SEC filings and insider activity
- Competitive landscape and risk factors

### 3. Executive Summary

Lead with a concise thesis:

```
[COMPANY] ([TICKER]) — Equity Research Report
Date: [Today] | Sector: [Sector] | Exchange: [Exchange]
Last Close: ~$XX.XX | Market Cap: ~$X.XXB

1. Executive Summary
[2-3 paragraph overview with key thesis, recent quarter highlights,
and forward outlook]
```

### 4. Financial Performance

Present key financials in a structured table:

| Key Metric | Value |
|------------|-------|
| Consensus Rating | ... |
| Average Price Target | ... |
| Price Target Range | ... |
| Implied Upside | ... |
| FY EPS Estimate | ... |
| Revenue (TTM) | ... |
| Net Income (TTM) | ... |

### 5. Valuation Analysis

Compare valuation multiples against:
- Historical averages (3-year, 5-year)
- Sector/industry peers
- Growth-adjusted metrics (PEG ratio)

### 6. Recent Developments & Catalysts

Highlight 3-5 recent events that could impact the stock:
- Earnings results and guidance
- Product launches or strategic shifts
- Regulatory developments
- M&A activity
- Management changes

### 7. Risk Factors

Identify key risks:
- Company-specific risks (execution, competition, concentration)
- Industry/sector risks (cyclicality, regulation)
- Macro risks (rates, FX, trade policy)

### 8. Investment Conclusion

Summarize the bull and bear cases:
- **Bull case** — what goes right, upside price target
- **Bear case** — what goes wrong, downside price target
- **Base case** — most likely outcome

### 9. Disclaimer

Always include: "This report is AI-generated for informational purposes only. It does not constitute investment advice. Past performance does not guarantee future results. Consult a qualified financial advisor before making investment decisions."

### 10. Next Steps

Suggest follow-up actions:
- "Run `/cpzai:backtest` to test a strategy based on this thesis"
- "Run `/cpzai:market-scan` to compare against sector peers"
- "Run `/cpzai:risk-report` to see how this fits in your portfolio"
