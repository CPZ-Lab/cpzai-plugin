---
description: View your current portfolio positions — holdings, P&L, weights, and today's movers
argument-hint: ""
---

# Positions

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Pull your live portfolio positions and present a clean summary with P&L, weights, and today's activity.

## Usage

```
/cpzai:positions
```

No arguments needed — pulls all open positions from connected accounts.

## Workflow

### 1. Fetch Positions

If ~~cpzai is connected:
- Call `list_positions` to get all open positions
- Call `list_accounts` for account-level info (equity, buying power)
- Call `get_market_data` for current prices on all held symbols

If no connection:
> Connect your CPZAI account to pull live positions. Go to **Settings → Connected Apps** to link your broker.

### 2. Account Summary

```
PORTFOLIO — [Date]
══════════════════
Total Equity:     $XX,XXX.XX
Buying Power:     $XX,XXX.XX
Positions:        XX open
Today's P&L:      +$XXX.XX (+X.XX%)
```

### 3. Holdings Table

| Symbol | Shares | Avg Cost | Current | P&L ($) | P&L (%) | Weight |
|--------|--------|----------|---------|---------|---------|--------|
| AAPL | 50 | $175.00 | $185.00 | +$500 | +5.7% | 15.2% |
| MSFT | 30 | $380.00 | $395.00 | +$450 | +3.9% | 19.5% |
| ... | ... | ... | ... | ... | ... | ... |
| **Total** | | | | **+$X,XXX** | **+X.X%** | **100%** |

Sort by weight (largest first).

### 4. Today's Movers

Highlight the biggest daily movers:

**Top Gainers:**
- AAPL: +X.X% ($+X.XX)
- MSFT: +X.X% ($+X.XX)

**Top Losers:**
- TSLA: -X.X% ($-X.XX)

### 5. Quick Flags

Note anything that stands out:
- Positions over 20% weight (concentration risk)
- Large unrealized losses (>10%)
- Any positions with unusual volume today
