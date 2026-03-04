# Connectors

## How tool references work

Plugin files use `~~cpzai` as a placeholder for the CPZAI MCP server. All tools require a valid CPZ API key and secret — the plugin does not grant platform access.

## Authentication

Every MCP call requires two headers:

| Header | Description |
|--------|-------------|
| `X-CPZ-Key` | Your CPZ API key (found in Settings → API Keys) |
| `X-CPZ-Secret` | Your CPZ API secret |

Without valid credentials, all tools return `401 Unauthorized`.

## Available Tools

The CPZAI MCP server exposes 18 tools across six categories:

| Category | Tools | Description |
|----------|-------|-------------|
| Strategies | `list_strategies`, `get_strategy`, `create_strategy`, `update_strategy` | CRUD for trading strategies |
| Backtesting | `get_backtest_results` | Retrieve historical backtest runs and metrics |
| Trading | `list_orders`, `place_order`, `list_positions`, `sync_portfolio`, `list_accounts` | Order management and portfolio tracking |
| Market Data | `get_market_data` | Real-time quotes (price, bid/ask, volume) |
| Risk Analytics | `compute_risk`, `list_risk_snapshots` | VaR, Sharpe, drawdown, beta, risk scoring |
| Execution | `execute_strategy` | Run a strategy on the compute backend |
| Webhooks | `list_webhooks`, `create_webhook`, `delete_webhook` | Subscribe to platform events |
| User | `get_profile` | Current user info and subscription tier |

## Getting an API Key

1. Sign up at [ai.cpz-lab.com](https://ai.cpz-lab.com)
2. Go to **Settings → API Keys**
3. Generate a new key pair
4. Add the key and secret to your MCP client configuration
