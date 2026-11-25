---
description: Sync your portfolio — pull latest positions, balances, and orders from all connected brokers
allowed-tools:
  - mcp__plugin_cpzai_cpzai__sync_portfolio
  - mcp__plugin_cpzai_cpzai__list_accounts
  - mcp__plugin_cpzai_cpzai__cash_summary
  - mcp__plugin_cpzai_cpzai__list_positions
---

# Sync

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).
>
> Use only figures a CPZAI tool returns. Anything a template below asks for that no tool provides (see [What the Tools Return](../CONNECTORS.md#what-the-tools-return-and-what-they-do-not)) is written "not available from CPZAI", never filled from memory.

Trigger a portfolio sync across all connected broker accounts to pull the latest positions, balances, and order status.

## Usage

```
/cpzai:sync
```

No arguments needed — syncs all connected accounts.

## Workflow

### 1. Trigger Sync

If ~~cpzai is connected:
- Call `sync_portfolio` to initiate a sync across all connected brokers
- Call `list_accounts` to show which accounts are being synced

If no connection:
> Connect your CPZAI account to sync your portfolio. Go to **Settings → Connected Apps** to link your broker.

### 2. Sync Status

```
PORTFOLIO SYNC
══════════════
Accounts synced:  [Count]
Broker(s):        [Alpaca, IBKR, ...]
Status:           ✓ Complete
Last sync:        [Timestamp]
```

### 3. Updated Summary

After sync completes, show the refreshed state:
- Total equity across all accounts (`cash_summary` totals; say which accounts have no balance)
- Position count
- Any changes since last sync (new fills, position changes)

### 4. Next Steps

- "Run `/cpzai:positions` to view your updated holdings"
- "Run `/cpzai:risk-report` to check your current risk profile"
