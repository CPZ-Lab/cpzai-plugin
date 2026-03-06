---
description: Place a trade — buy or sell stocks, ETFs, or crypto through your connected broker
argument-hint: " <buy|sell> <quantity> <symbol> [order type] [limit price]"
---

# Trade

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

**Important**: This command places real orders through your connected broker. Orders are irreversible once filled. Double-check all details before confirming. Trading carries risk of loss.

Place a buy or sell order through your connected brokerage account.

## Usage

```
/cpzai:trade <side> <quantity> <symbol> [order type] [limit price]
```

### Arguments

- `side` — `buy` or `sell`
- `quantity` — Number of shares (or `$500` for notional amount)
- `symbol` — Ticker symbol (e.g. `AAPL`, `SPY`, `BTC/USD`)
- `order type` (optional) — `market` (default), `limit`, `stop`, `stop-limit`
- `limit price` (optional) — Required for limit and stop-limit orders

### Examples

```
/cpzai:trade buy 10 AAPL
/cpzai:trade sell 50 MSFT limit 420.00
/cpzai:trade buy $1000 SPY
/cpzai:trade buy 5 NVDA stop-limit 850.00
```

## Workflow

### 1. Validate the Order

Parse the user's input and confirm all required fields:
- Side (buy/sell)
- Quantity (shares or notional)
- Symbol (validate it's a real ticker)
- Order type and price (if applicable)

### 2. Pre-Trade Check

If ~~cpzai is connected:
- Call `list_accounts` to verify the user has a connected broker and sufficient buying power
- Call `list_positions` to check existing exposure to this symbol
- Call `get_market_data` to get the current price

Present a confirmation:

```
ORDER CONFIRMATION
══════════════════
Action:     BUY 10 AAPL
Order Type: Market
Est. Price: ~$XXX.XX
Est. Total: ~$X,XXX.XX
Account:    [Broker Name] ([Paper/Live])
Buying Power: $XX,XXX.XX

Current Position: [None | XX shares @ $XXX.XX avg]
```

### 3. Confirm and Execute

Ask for explicit confirmation before placing:
> "Ready to place this order. Confirm? (yes/no)"

On confirmation:
- Call `place_order` with the validated parameters
- Report the order ID and status back to the user

```
ORDER PLACED ✓
══════════════
Order ID:   [ID]
Status:     [Submitted / Filled / Partially Filled]
Fill Price: $XXX.XX (if filled)
```

### 4. Post-Trade Context

After placing:
- Show updated position (if filled)
- Note impact on portfolio concentration
- Suggest: "Run `/cpzai:risk-report` to check how this affects your portfolio risk"

### 5. Error Handling

If the order fails:
- Insufficient buying power → show available balance and suggest reducing size
- Market closed → note market hours and suggest a limit order for next open
- Invalid symbol → suggest corrections
- Broker not connected → guide to Settings → Connected Apps
