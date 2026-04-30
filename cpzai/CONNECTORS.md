# Connectors

## Overview

Plugin files reference the CPZAI MCP server (key `cpzai` in `.mcp.json`). Tools surface to Claude as `mcp__cpzai__<tool_name>`. The placeholder `~~cpzai` is used in skill and command prose as a reminder that the tools require the CPZAI MCP server to be connected — without valid credentials, every call returns `401 Unauthorized`.

## Authentication

The CPZAI MCP connector supports two authentication methods.

### OAuth 2.0 (recommended for Claude.ai / Cowork / Desktop)

Authentication flows through the Claude Connectors directory.

1. Claude redirects the user to the CPZAI authorization page.
2. The user enters their API key and secret (or signs in via SSO if enabled).
3. Claude receives an access token and manages refresh automatically.

OAuth metadata is published at `https://mcp.cpz-lab.com/.well-known/oauth-authorization-server` and supports PKCE (`S256`). Available scopes: `read`, `write`, `trade`.

### Direct API headers (Claude Code / custom MCP clients)

The plugin's `cpzai/.mcp.json` wires `userConfig` values into HTTP headers automatically:

```json
{
  "mcpServers": {
    "cpzai": {
      "type": "http",
      "url": "https://mcp.cpz-lab.com/mcp",
      "headers": {
        "X-CPZ-Key": "${user_config.cpz_api_key}",
        "X-CPZ-Secret": "${user_config.cpz_api_secret}",
        "X-CPZ-Client": "claude-plugin/2.0.0"
      }
    }
  }
}
```

The user supplies the key and secret via the `/plugin` configuration UI. Both fields are flagged `sensitive: true` in the manifest, so they are stored in the system keychain (or `~/.claude/.credentials.json` where keychain is unavailable) — never written to plain `settings.json`.

| Header | Source | Notes |
|--------|--------|-------|
| `X-CPZ-Key` | `userConfig.cpz_api_key` | Substituted at MCP server start |
| `X-CPZ-Secret` | `userConfig.cpz_api_secret` | Substituted at MCP server start |
| `X-CPZ-Client` | Hardcoded plugin version | Allows the server to attribute traffic to plugin builds |

## Available Tools

The CPZAI MCP server exposes 18 tools across 8 categories. Every tool carries a safety annotation per the [Model Context Protocol specification](https://modelcontextprotocol.io/specification/server/tools).

| Category | Tool | Annotation | Description |
|----------|------|------------|-------------|
| Strategies | `list_strategies` | `readOnlyHint` | Filter by status, type, title; pagination via `limit`/`offset` |
| Strategies | `get_strategy` | `readOnlyHint` | Fetch one strategy by UUID |
| Strategies | `create_strategy` | write | Create a new strategy with optional Python code |
| Strategies | `update_strategy` | write | Patch any field on an existing strategy |
| Backtesting | `get_backtest_results` | `readOnlyHint` | List backtest runs, optionally filtered by strategy |
| Trading | `list_orders` | `readOnlyHint` | Filter by status, symbol, side, strategy |
| Trading | `list_positions` | `readOnlyHint` | Filter by account or symbol |
| Trading | `list_accounts` | `readOnlyHint` | Connected broker credentials (sensitive fields masked) |
| Trading | `place_order` | **`destructiveHint`** | Place an order through a connected broker |
| Trading | `sync_portfolio` | write | Force-sync positions, balances, and orders across brokers |
| Market Data | `get_market_data` | `readOnlyHint` | Real-time quotes (price, bid/ask, volume) for a list of symbols |
| Risk | `list_risk_snapshots` | `readOnlyHint` | Historical risk snapshots for trend analysis |
| Risk | `compute_risk` | write | Compute a fresh portfolio risk snapshot (VaR/Sharpe/drawdown/exposures) |
| Execution | `execute_strategy` | **`destructiveHint`** | Run strategy code on the compute backend |
| Webhooks | `list_webhooks` | `readOnlyHint` | View configured webhook subscriptions |
| Webhooks | `create_webhook` | write | Subscribe to platform events; signing secret returned once |
| Webhooks | `delete_webhook` | **`destructiveHint`** | Remove a webhook subscription |
| User | `get_profile` | `readOnlyHint` | Authenticated user profile and subscription tier |

## Plugin-Side Safety Layers

Three safety layers wrap destructive tools — they apply automatically when the plugin is enabled.

### 1. Command-level least privilege

Every command in `cpzai/commands/` declares `allowed-tools` listing only the MCP tools it actually needs. A command without an MCP entry cannot call MCP. Example:

```yaml
allowed-tools:
  - mcp__cpzai__list_accounts
  - mcp__cpzai__list_positions
  - mcp__cpzai__get_market_data
  - mcp__cpzai__place_order
  - mcp__cpzai__list_orders
```

### 2. PreToolUse safety hook

`cpzai/hooks/hooks.json` registers a `PreToolUse` hook that matches `mcp__cpzai__place_order|mcp__cpzai__execute_strategy|mcp__cpzai__delete_webhook`. The hook script (`cpzai/scripts/pre-trade-guard.sh`) blocks the call with a structured `{"decision":"block","reason":"..."}` response, instructing the calling agent to summarize the action and obtain explicit user confirmation via `AskUserQuestion` before re-issuing the tool call.

`delete_webhook` is default-deny — the hook always blocks first time.

To opt out (not recommended): set `userConfig.require_trade_confirmation = false` via the `/plugin` UI.

### 3. PostToolUse audit log

`cpzai/scripts/audit-log.sh` runs after every state-mutating CPZAI tool call and appends a single-line JSON record to `${CLAUDE_PLUGIN_DATA}/audit.log` (typically `~/.claude/plugins/data/cpzai-cpzai-plugin/audit.log`). Record shape:

```json
{"ts":"2026-04-30T13:00:13Z","tool":"mcp__cpzai__place_order","ok":true,"input_preview":"{\"symbol\":\"AAPL\",\"quantity\":10,\"side\":\"buy\",\"order_type\":\"market\"}"}
```

The log persists across plugin updates. Input previews are truncated to 240 characters and never include credentials.

## Privacy Policy

See our privacy policy at [mcp.cpz-lab.com/privacy](https://mcp.cpz-lab.com/privacy).

## Getting an API Key

1. Sign up at [ai.cpz-lab.com](https://ai.cpz-lab.com)
2. Go to **Settings → API Keys**
3. Generate a new key pair
4. On first plugin use, paste the key and secret when Claude prompts. They are stored in your system keychain.
