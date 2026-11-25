# Connectors

## Overview

Plugin files reference the CPZAI MCP server (key `cpzai` in `.mcp.json`). Claude Code names a plugin's bundled MCP tools `mcp__plugin_<plugin>_<server>__<tool>`, so the CPZAI tools surface as `mcp__plugin_cpzai_cpzai__<tool_name>` (for example `mcp__plugin_cpzai_cpzai__place_order`). A standalone server you add yourself under the name `cpzai` surfaces as `mcp__cpzai__<tool_name>`; the hooks match both. The placeholder `~~cpzai` is used in skill and command prose as a reminder that the tools require the CPZAI MCP server to be connected: without valid credentials, every call returns `401 Unauthorized`.

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
        "X-CPZ-Client": "claude-plugin/2.1.0"
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

The CPZAI MCP server's main tools are below; `tools/list` has the full current catalog. Every tool carries a safety annotation per the [Model Context Protocol specification](https://modelcontextprotocol.io/specification/server/tools).

| Category | Tool | Annotation | Description |
|----------|------|------------|-------------|
| Strategies | `list_strategies` | `readOnlyHint` | Filter by status, type, title; pagination via `limit`/`offset` |
| Strategies | `get_strategy` | `readOnlyHint` | Fetch one strategy by UUID |
| Strategies | `create_strategy` | write | Create a new strategy with optional Python code |
| Strategies | `update_strategy` | write | Patch any field on an existing strategy |
| Backtesting | `get_backtest_results` | `readOnlyHint` | List saved backtest runs, optionally filtered by strategy. Does not start a run |
| Backtesting | `get_backtest_result` | `readOnlyHint` | One saved run: configuration, result, code. Does not start a run |
| Trading | `list_orders` | `readOnlyHint` | Filter by status, symbol, side, strategy |
| Trading | `list_positions` | `readOnlyHint` | Filter by account or symbol |
| Trading | `list_accounts` | `readOnlyHint` | Connected accounts: broker, environment (paper/live), tradable. No balances |
| Trading | `cash_summary` | `readOnlyHint` | Cash, buying power and equity per account as last synced, with `as_of` and `stale` |
| Trading | `export_transactions` | `readOnlyHint` | Fills by fill time, for statements |
| Trading | `place_order` | **`destructiveHint`** | Place an order through a connected broker |
| Trading | `sync_portfolio` | write | Force-sync positions, balances, and orders across brokers |
| Market Data | `get_market_data` | `readOnlyHint` | Real-time quotes (price, change, bid/ask, volume) for stocks, ETFs and crypto. Not option contracts |
| Market Data | `get_bars` | `readOnlyHint` | Historical OHLCV bars (intraday, daily, weekly, monthly) over a date range |
| Risk | `list_risk_snapshots` | `readOnlyHint` | Historical risk snapshots for trend analysis |
| Risk | `compute_risk` | write | Compute a fresh portfolio risk snapshot (VaR/Sharpe/drawdown/exposures) |
| Execution | `execute_strategy` | **`destructiveHint`** | Run a strategy's code. It can submit orders. It is not a backtest |
| Webhooks | `list_webhooks` | `readOnlyHint` | View configured webhook subscriptions |
| Webhooks | `create_webhook` | write | Subscribe to platform events; signing secret returned once |
| Webhooks | `delete_webhook` | **`destructiveHint`** | Remove a webhook subscription |
| User | `get_profile` | `readOnlyHint` | Authenticated user profile and subscription tier |

## What the Tools Return (and What They Do Not)

Commands, skills and agents use only figures a tool returns. Where a template asks for something no tool provides, write **not available from CPZAI** in its place. Never fill it from memory or general knowledge; if the user supplies a figure, label it as user-supplied.

| Figure | Where it comes from |
|--------|--------------------|
| Holdings: quantity, average cost, market value, unrealized P&L | `list_positions` (page until a short page; read `account_errors`) |
| Sector of a holding | `list_positions` `sector`, when recorded. Often null: then "sector not recorded", never a guess |
| Equity, cash, buying power per account | `cash_summary` (last sync; say when `stale` is true) |
| Which accounts exist, paper or live, tradable | `list_accounts` (it holds no balances) |
| Current price, day change, bid/ask, today's volume | `get_market_data` |
| 52-week range, moving averages, RSI, relative volume, average daily volume, realized volatility, per-holding beta, correlations, covariance | Computed from `get_bars` daily bars (a year for 52-week figures, SPY bars for beta) |
| Portfolio VaR, Sharpe, Sortino, max drawdown, beta, alpha, concentration, holdings correlation | `compute_risk`. These are today's holdings at today's weights replayed over `return_window`; quote its `method_note`, never call them the account's track record |
| Saved backtest metrics | `get_backtest_results`, `get_backtest_result` |
| Fills for statements | `export_transactions` |

**Not available from any CPZAI tool:** option chains, implied volatility, IV rank or percentile, Greeks, put/call ratio, skew and term structure; company fundamentals (P/E, ROE, margins, revenue, EPS, estimates, market cap, dividends, earnings dates); factor exposures or tilts; margin used; week or month account P&L; per-position contribution to VaR (compute it from `get_bars` covariance if needed and say so); starting a backtest.

**Backtests:** no CPZAI tool starts one. Run it in CPZAI Strategy Lab (ai.cpz-lab.com), then read it with `get_backtest_results`. Never call `execute_strategy` to backtest: it runs the strategy's code and can submit orders.

## Plugin-Side Safety Layers

Three safety layers wrap destructive tools — they apply automatically when the plugin is enabled.

### 1. Command-level least privilege

Every command in `cpzai/commands/` declares `allowed-tools` listing only the MCP tools it actually needs. A command without an MCP entry cannot call MCP. Example:

```yaml
allowed-tools:
  - mcp__plugin_cpzai_cpzai__list_accounts
  - mcp__plugin_cpzai_cpzai__cash_summary
  - mcp__plugin_cpzai_cpzai__list_positions
  - mcp__plugin_cpzai_cpzai__get_market_data
  - mcp__plugin_cpzai_cpzai__place_order
  - mcp__plugin_cpzai_cpzai__list_orders
```

### 2. PreToolUse safety hook

`cpzai/hooks/hooks.json` registers a `PreToolUse` hook for every state-changing CPZAI tool (`place_order`, `execute_strategy`, `create_strategy`, `update_strategy`, `configure_overlay`, `create_webhook`, `delete_webhook`, `sync_portfolio`, `create_connection`), under both tool spellings. The hook script (`cpzai/scripts/pre_trade_guard.py`) answers `permissionDecision: "ask"`: Claude Code shows you the call with a summary (for an order: side, quantity, symbol, type, price, account, and your default environment) and runs it once you approve. You are asked once per call, and an approved call goes through; there is no block-and-retry loop. The guard fails closed: an event it cannot read, a tool name it does not recognise, or an error inside it is asked about, never let through. It needs a working `python3`; the session banner runs it and shows `guard=OFF` when it does not answer (for example the `/usr/bin/python3` stub on a Mac without the developer tools). The hook entry has `"onFailure": "block"` (Claude Code 2.1.295 and later): a guard that cannot start, exits with an error or times out blocks the call instead of letting it through.

`add_to_watchlist` and `remove_from_watchlist` are not guarded: they change a list of at most 10 symbols to watch, move no money, place nothing and are undone by the opposite call, and asking on each would train you to approve without reading.

The default environment is a reminder, not an account check: the order input carries the account id, not its environment, so the hook cannot see whether the account is paper or live. `/cpzai:trade` and the execution-reviewer agent check the account's `environment` with `list_accounts` before an order.

To opt out (not recommended): set `userConfig.require_trade_confirmation = false` via the `/plugin` UI.

### 3. Audit log

`cpzai/scripts/audit_log.py` runs after every state-changing CPZAI tool call, on `PostToolUse` and on `PostToolUseFailure` (a call that failed outright), and appends one JSON line to `${CLAUDE_PLUGIN_DATA}/audit.log` (typically `~/.claude/plugins/data/cpzai-cpzai-plugin/audit.log`). Record shape:

```json
{"ts":"2026-11-25T13:00:13Z","event":"PostToolUse","tool":"mcp__plugin_cpzai_cpzai__place_order","ok":true,"input":{"account_id":"PA3...","broker_credential_id":"...","symbol":"AAPL","side":"buy","order_type":"limit","quantity":10,"price":200.5},"order_id":"alp-123","status":"accepted"}
```

`ok` is false when the call failed or the tool answered an error or a refusal (with `error` holding the reason), true when it answered without one, and null when the answer says neither; it is never assumed true. `order_id` and `status` come from the tool's answer. The input is recorded whole, with any field named like a key, secret, token or password replaced by `[redacted]`. The log persists across plugin updates.

## Privacy Policy

See our privacy policy at [mcp.cpz-lab.com/privacy](https://mcp.cpz-lab.com/privacy).

## Getting an API Key

1. Sign up at [ai.cpz-lab.com](https://ai.cpz-lab.com)
2. Go to **Settings → API Keys**
3. Generate a new key pair
4. On first plugin use, paste the key and secret when Claude prompts. They are stored in your system keychain.
