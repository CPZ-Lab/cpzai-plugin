---
description: List, view, and manage your trading strategies — status, last backtest, and quick actions
argument-hint: " [strategy name | list | status]"
---

# Strategies

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

View and manage your strategy library — list all strategies, check status, view code, or take quick actions.

## Usage

```
/cpzai:strategies [action]
```

### Arguments

- No argument or `list` — List all strategies with status summary
- `<strategy name>` — View details and code for a specific strategy
- `active` / `draft` / `paused` — Filter by status
- `create <description>` — Shortcut to `/cpzai:strategy-builder`

## Workflow

### 1. Fetch Strategies

If ~~cpzai is connected:
- Call `list_strategies` to get all strategies with status, type, and dates
- Call `get_backtest_results` for recent backtest performance

If no connection:
> Connect your CPZAI account to manage strategies. Go to **Settings → API Keys** to generate credentials.

### 2. Strategy Library

```
YOUR STRATEGIES — [Count] total
════════════════════════════════
```

| # | Title | Status | Type | Last Backtest | Last Updated |
|---|-------|--------|------|---------------|-------------|
| 1 | Momentum SPY | Active | Momentum | 3 days ago | Mar 1 |
| 2 | Mean Rev Pairs | Draft | Mean Reversion | Never | Feb 28 |
| 3 | Vol Harvester | Paused | Volatility | 2 weeks ago | Feb 15 |
| ... | ... | ... | ... | ... | ... |

### 3. Strategy Detail (if specific strategy requested)

When viewing a single strategy:

```
STRATEGY: [Title]
═════════════════
ID:          [uuid]
Status:      [Active / Draft / Paused]
Type:        [Momentum / Mean Reversion / ...]
Created:     [Date]
Last Updated: [Date]
Last Backtest: [Date] — Sharpe: X.XX, Return: XX.X%, Max DD: XX.X%
```

Show the strategy code (from `get_strategy`):
- Key parameters and their current values
- Signal logic summary
- Position sizing approach

### 4. Needs Attention

Flag strategies that may need action:
- Not backtested in 30+ days
- Draft status for 2+ weeks (stale drafts)
- Active strategies with no recent execution
- Strategies with poor last backtest results (Sharpe < 0.5)

### 5. Quick Actions

Suggest next steps based on context:
- "Run `/cpzai:backtest Momentum SPY` to refresh the backtest"
- "Run `/cpzai:strategy-builder` to create a new strategy"
- "Want me to update any parameters on [strategy name]?"
