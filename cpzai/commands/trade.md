---
description: Place a trade — buy or sell stocks, ETFs, or crypto through your connected broker
argument-hint: "<buy|sell> <quantity> <symbol> [order type] [limit price]"
allowed-tools:
  - mcp__plugin_cpzai_cpzai__list_accounts
  - mcp__plugin_cpzai_cpzai__cash_summary
  - mcp__plugin_cpzai_cpzai__list_positions
  - mcp__plugin_cpzai_cpzai__get_market_data
  - mcp__plugin_cpzai_cpzai__place_order
  - mcp__plugin_cpzai_cpzai__list_orders
  - AskUserQuestion
---

# Trade

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).
>
> Use only figures a CPZAI tool returns. Anything a template below asks for that no tool provides (see [What the Tools Return](../CONNECTORS.md#what-the-tools-return-and-what-they-do-not)) is written "not available from CPZAI", never filled from memory.

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
- Call `list_accounts` to pick the account: it must be `tradable`, and its `environment` must be the one intended. If the account is live and the plugin's default environment is paper, stop and ask the user to confirm a live trade explicitly
- Call `cash_summary` for that account's buying power (last sync: if `stale` is true or it has no balance source, say the buying power is not known; never assume it is sufficient)
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

If this session's `[cpzai v...]` banner shows `confirm=true`, the plugin's guard runs: call `place_order` with the validated parameters, and Claude Code shows the user this order and places it only after they approve it there. That approval is the confirmation, so do not ask a second time in chat.

If there is no banner (the client does not run plugin hooks) or it shows `confirm=false`, nothing else will ask: ask in chat first and call `place_order` only after an explicit yes:
> "Ready to place this order. Confirm? (yes/no)"

After the call:
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
