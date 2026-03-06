---
description: View recent orders — open, filled, cancelled — with status and fill details
argument-hint: " [status] [symbol]"
---

# Orders

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Pull your recent order history and present status, fills, and execution details.

## Usage

```
/cpzai:orders [status] [symbol]
```

### Arguments

- `status` (optional) — Filter by order status:
  - `open` — pending/working orders only
  - `filled` — completed orders only
  - `cancelled` — cancelled orders only
  - No filter shows all recent orders (default)
- `symbol` (optional) — Filter to a specific ticker: `AAPL`, `SPY`

## Workflow

### 1. Fetch Orders

If ~~cpzai is connected:
- Call `list_orders` with any status/symbol filters
- Call `list_accounts` to identify which broker account(s) are active

If no connection:
> Connect your CPZAI account to pull order history. Go to **Settings → Connected Apps** to link your broker.

### 2. Open Orders (if any)

```
OPEN ORDERS — [Count]
═════════════════════
```

| Order ID | Symbol | Side | Type | Qty | Price | Submitted | Status |
|----------|--------|------|------|-----|-------|-----------|--------|
| ... | AAPL | BUY | Limit | 10 | $180.00 | 2h ago | Working |
| ... | ... | ... | ... | ... | ... | ... | ... |

### 3. Recent Fills

| Order ID | Symbol | Side | Type | Qty | Fill Price | Filled At | Total |
|----------|--------|------|------|-----|-----------|-----------|-------|
| ... | MSFT | BUY | Market | 20 | $392.50 | Today 10:32 | $7,850 |
| ... | AAPL | SELL | Limit | 10 | $186.00 | Yesterday | $1,860 |
| ... | ... | ... | ... | ... | ... | ... | ... |

### 4. Summary Stats

```
Last 7 Days:  XX orders (XX filled, XX cancelled, XX open)
Total Volume: $XX,XXX
```

### 5. Actions

For open orders, offer quick actions:
- "Want to cancel any open orders?"
- "Want to modify the AAPL limit to a different price?"
