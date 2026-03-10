# Connectors

## How tool references work

Plugin files use `~~cpzai` as a placeholder for the CPZAI MCP server. All tools require a valid CPZ API key and secret — the plugin does not grant platform access.

## Authentication

The CPZAI MCP connector supports two authentication methods:

### OAuth 2.0 (recommended for Claude.ai / Desktop)

When connecting via the Claude Connectors directory, authentication is handled automatically through OAuth 2.0:

1. Claude redirects you to the CPZAI authorization page
2. Enter your API key and secret
3. Claude receives an access token and manages it for you

The OAuth server metadata is published at `https://mcp.cpz-lab.com/.well-known/oauth-authorization-server`.

### Direct API headers (Claude Code / custom clients)

For direct MCP connections, pass credentials in HTTP headers:

| Header | Description |
|--------|-------------|
| `X-CPZ-Key` | Your CPZ API key (found in Settings → API Keys) |
| `X-CPZ-Secret` | Your CPZ API secret |

Without valid credentials, all tools return `401 Unauthorized`.

## Available Tools

The CPZAI MCP server exposes 18 tools across eight categories. Each tool includes safety annotations (`readOnlyHint` or `destructiveHint`) per the MCP specification.

| Category | Tools | Access | Description |
|----------|-------|--------|-------------|
| Strategies | `list_strategies`, `get_strategy` | read-only | Query trading strategies |
| Strategies | `create_strategy`, `update_strategy` | write | Create and modify strategies |
| Backtesting | `get_backtest_results` | read-only | Retrieve historical backtest runs and metrics |
| Trading | `list_orders`, `list_positions`, `list_accounts` | read-only | View orders, positions, and accounts |
| Trading | `place_order`, `sync_portfolio` | write | Place trades and sync portfolio |
| Market Data | `get_market_data` | read-only | Real-time quotes (price, bid/ask, volume) |
| Risk Analytics | `list_risk_snapshots` | read-only | View historical risk snapshots |
| Risk Analytics | `compute_risk` | write | Compute fresh risk snapshot |
| Execution | `execute_strategy` | destructive | Run a strategy on the compute backend |
| Webhooks | `list_webhooks` | read-only | View webhook subscriptions |
| Webhooks | `create_webhook` | write | Subscribe to platform events |
| Webhooks | `delete_webhook` | destructive | Remove a webhook subscription |
| User | `get_profile` | read-only | Current user info and subscription tier |

## Privacy Policy

See our privacy policy at [mcp.cpz-lab.com/privacy](https://mcp.cpz-lab.com/privacy).

## Getting an API Key

1. Sign up at [ai.cpz-lab.com](https://ai.cpz-lab.com)
2. Go to **Settings → API Keys**
3. Generate a new key pair
4. Add the key and secret to your MCP client configuration
