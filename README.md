<div align="center">

<a href="https://ai.cpz-lab.com">
  <img src="https://drive.google.com/uc?id=1PXRTr7fd7ONFUblpuXZsvl457wWTwjzb" alt="CPZAI" width="150">
</a>

# CPZAI — Systematic Trading Plugin

**AI-Native Systematic and Quantitative Trading for Claude**

[![Claude Cowork](https://img.shields.io/badge/Claude-Cowork-000000?logo=anthropic&logoColor=white)](https://claude.com/product/cowork)
[![Claude Code](https://img.shields.io/badge/Claude-Code-000000?logo=anthropic&logoColor=white)](https://claude.com/product/claude-code)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue)](cpzai/LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0.0-blue)]()
[![Skills](https://img.shields.io/badge/Skills-10-green)]()
[![Commands](https://img.shields.io/badge/Commands-17-green)]()
[![Agents](https://img.shields.io/badge/Agents-3-green)]()
[![MCP Tools](https://img.shields.io/badge/MCP_Tools-18-green)]()

</div>

A plugin that turns Claude into a systematic trading specialist. Built for [Cowork](https://claude.com/product/cowork), also fully compatible with [Claude Code](https://claude.com/product/claude-code).

Build quantitative strategies, backtest them against historical data, monitor risk in real time, and execute trades — all through natural conversation with Claude, powered by [CPZAI](https://ai.cpz-lab.com).

> **Important**: This plugin assists with trading and investment workflows but does not provide financial advice. All trading decisions carry risk of loss and should be made by qualified individuals. Past performance does not guarantee future results.

---

## What's New in 2.0

- **Specialized subagents** — `quant-researcher`, `risk-auditor`, and `execution-reviewer` invoke automatically for the right task with the right model and tool scope.
- **Pre-trade safety hooks** — every `place_order` and `execute_strategy` call is intercepted for explicit confirmation; `delete_webhook` is default-deny.
- **Audit trail** — every state-mutating call writes a single-line JSON record to a persistent log.
- **Configure via UI, not JSON** — API key, secret, default environment, and confirmation policy are prompted via the Claude `/plugin` interface and stored in your system keychain.
- **Least-privilege tool scoping** — every command lists exactly the tools it needs.
- **New compliance skill** — covers SEC Rule 17a-4, MiFID II, FINRA, model governance, and audit trails.
- **CI-validated** — every change runs through structure validation and a live MCP smoke test.

See [CHANGELOG.md](CHANGELOG.md) for the full list.

---

## Prerequisites

You need a CPZAI account with API credentials. The plugin connects to the CPZAI MCP server — without valid credentials, no tools are accessible.

1. Sign up at [ai.cpz-lab.com](https://ai.cpz-lab.com)
2. Go to **Settings → API Keys** and generate a key pair
3. Install the plugin (see below)

## Installation

### Cowork

Install from [claude.com/plugins](https://claude.com/plugins/). When prompted, paste your CPZ API key and secret — they're stored in your system keychain.

### Claude Code

```bash
# Add the marketplace
claude plugin marketplace add CPZ-Lab/cpzai-plugin

# Install the plugin
claude plugin install cpzai@cpzai-plugin
```

Claude Code prompts for your CPZ API key and secret on first use. To re-configure later: `claude /plugin` → select `cpzai` → **Configure**.

---

## Commands

17 slash commands covering the systematic trading lifecycle.

| Command | Description |
|---------|-------------|
| `/cpzai:strategy-builder` | Guided strategy creation — describe a trading idea and Claude writes the code |
| `/cpzai:backtest` | Run a strategy backtest, analyze metrics, and identify improvements |
| `/cpzai:risk-report` | Generate a risk report — VaR, Sharpe, drawdown, with recommendations |
| `/cpzai:portfolio-review` | Full portfolio health check — positions, diversification, attribution |
| `/cpzai:market-scan` | Scan sectors or themes with real-time quotes and context |
| `/cpzai:trade` | Place a trade — buy or sell through your connected broker |
| `/cpzai:trade-idea` | Generate a structured trade idea with entry, exit, sizing, and risk |
| `/cpzai:optimize` | Optimize portfolio allocation — mean-variance, Black-Litterman, risk parity, HRP |
| `/cpzai:options-analysis` | Analyze options strategies, Greeks, and vol surface for a ticker |
| `/cpzai:equity-research` | Generate a comprehensive equity research report |
| `/cpzai:earnings-preview` | Preview upcoming earnings — expectations, patterns, and positioning |
| `/cpzai:factor-screen` | Screen stocks by quantitative factors — value, momentum, quality, etc. |
| `/cpzai:price` | Get real-time quotes — price, change, volume, bid/ask |
| `/cpzai:positions` | View current portfolio positions — holdings, P&L, weights |
| `/cpzai:orders` | View recent orders — open, filled, cancelled, with fill details |
| `/cpzai:strategies` | List, view, and manage your trading strategies |
| `/cpzai:sync` | Sync your portfolio from all connected brokers |

Every command declares its `allowed-tools` set so Claude can only call the MCP tools it actually needs.

## Agents

3 specialized subagents that activate when Claude detects the right context. Each has a deliberately chosen model and effort level, and explicitly lists tools it must not touch.

| Agent | Model | When it fires |
|-------|-------|---------------|
| `quant-researcher` | opus / high | Designing experiments, IC analysis, walk-forward validation, factor combination, ML model selection |
| `risk-auditor` | sonnet / medium | Pre-trade risk audits, weekly reviews, concentration / correlation / drawdown checks |
| `execution-reviewer` | sonnet / medium | The 7-point pre-trade compliance check — runs automatically before any destructive trade tool |

Read-only by design: `risk-auditor` and `execution-reviewer` cannot place orders. `quant-researcher` cannot place orders or modify webhooks.

## Skills

10 skills that auto-activate based on conversational context. Skills are reference material — Claude loads them when relevant.

| Skill | When it fires |
|-------|---------------|
| `strategy-development` | Designing trading strategies, signal generation, factor models |
| `risk-management` | Analyzing risk, position sizing, drawdown limits, hedging |
| `backtesting` | Running historical tests, avoiding overfitting, walk-forward validation |
| `order-execution` | Placing trades, order types, execution quality, slippage |
| `market-data` | Fetching quotes, technical analysis, corporate actions, data quality |
| `portfolio-analytics` | Performance measurement, attribution, benchmarking, rebalancing |
| `portfolio-optimization` | Mean-variance, Black-Litterman, HRP, efficient frontier, constraints |
| `volatility-and-derivatives` | Greeks, GARCH, vol surface, skew, options strategies, VIX |
| `alpha-research` | IC/IR analysis, feature engineering, ML cross-validation, signal decay |
| `compliance-and-recordkeeping` | Audit trails, model governance, SEC 17a-4, MiFID II, recordkeeping |

## MCP Tools

The CPZAI MCP server provides 18 tools across 8 categories. Every tool carries a safety annotation (`readOnlyHint`, or `destructiveHint`) per the MCP specification.

| Category | Read-Only | Write | Destructive |
|----------|-----------|-------|-------------|
| Strategies | `list_strategies`, `get_strategy` | `create_strategy`, `update_strategy` | — |
| Backtesting | `get_backtest_results` | — | — |
| Trading | `list_orders`, `list_positions`, `list_accounts` | `sync_portfolio` | `place_order` |
| Market Data | `get_market_data` | — | — |
| Risk | `list_risk_snapshots` | `compute_risk` | — |
| Execution | — | — | `execute_strategy` |
| Webhooks | `list_webhooks` | `create_webhook` | `delete_webhook` |
| User | `get_profile` | — | — |

Destructive tools (`place_order`, `execute_strategy`, `delete_webhook`) are intercepted by the plugin's `PreToolUse` safety hook and require explicit confirmation. See [cpzai/CONNECTORS.md](cpzai/CONNECTORS.md) for the full schema reference.

## Safety Architecture

Three layers of defense protect every state-mutating operation:

1. **Command-level scoping** — each command's `allowed-tools` lists only the tools it can call.
2. **Pre-trade hook** — `place_order` and `execute_strategy` are blocked at `PreToolUse` until the agent re-summarizes and confirms; `delete_webhook` is default-deny.
3. **Audit log** — every successful state-mutating call appends a JSON line to `${CLAUDE_PLUGIN_DATA}/audit.log` with timestamp, tool, and a 240-char input preview. The log persists across plugin updates.

To opt out of the trade-confirmation hook (not recommended): set `userConfig.require_trade_confirmation = false` via `/plugin` configuration.

---

## Example Workflows

### Build a mean-reversion strategy from scratch

```
/cpzai:strategy-builder pairs mean-reversion on AAPL/MSFT using z-score entry at 2.0 std
```

Claude writes the Python strategy code, explains the logic, and creates it on your CPZAI account — ready to backtest. The `quant-researcher` agent may activate for parameter design.

### Morning risk check

```
/cpzai:risk-report
```

The `risk-auditor` agent pulls live positions, computes current VaR/Sharpe/drawdown, flags concentration risk, and produces a prioritized remediation memo. It cannot place orders — it hands you the trade list.

### Backtest and iterate

```
/cpzai:backtest my momentum strategy from 2020-01 to 2024-12 with weekly rebalance
```

Runs the backtest, analyzes results (Sharpe, max drawdown, win rate), checks robustness across sub-periods, and suggests parameter improvements grounded in the `backtesting` skill.

### Place a guarded order

```
/cpzai:trade buy 10 AAPL limit 185.00
```

The `execution-reviewer` agent runs the 7-point pre-trade check (account, buying power, existing exposure, market quality, sizing, risk impact, order semantics). Only when all checks pass does the safety hook ask you to confirm before the order is placed.

---

## Configuration

The plugin authenticates via your MCP client's server configuration. Two paths:

### OAuth 2.0 (recommended for Cowork / Claude Desktop)

Click **Connect** in the plugin UI. Claude redirects you to the CPZAI authorization page; you enter your key and secret once; Claude manages the access token. The OAuth metadata is published at `https://mcp.cpz-lab.com/.well-known/oauth-authorization-server`.

### Direct API headers (Claude Code / custom MCP clients)

The `cpzai/.mcp.json` config wires `userConfig` values into HTTP headers automatically:

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

Provide the key/secret via `/plugin` UI on first use; they're stored in your system keychain (never written to disk in plaintext).

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `401 Unauthorized` from any tool call | Missing or invalid API credentials | `claude /plugin` → `cpzai` → **Configure** → re-enter key + secret |
| Plugin not loading | Manifest schema error | `python3 tests/validate.py` to see exactly which file fails |
| Slash commands not appearing | Plugin disabled | `claude plugin enable cpzai@cpzai-plugin` |
| `place_order` blocked with "CPZAI safety guard" message | Pre-trade hook (working as intended) | Have the agent summarize the order and confirm; or set `require_trade_confirmation=false` |
| `tools/list` empty | MCP server unreachable | `bash tests/smoke-mcp.sh` to confirm endpoint health |
| Audit log missing | Hook script not executable | `chmod +x cpzai/scripts/*.sh` |

For platform issues, file an issue at [github.com/CPZ-Lab/cpzai-plugin/issues](https://github.com/CPZ-Lab/cpzai-plugin/issues).

---

## Development

```bash
git clone git@github.com:CPZ-Lab/cpzai-plugin.git
cd cpzai-plugin

# Structure validation (offline, no network)
python3 tests/validate.py

# Full test suite (validation + live MCP smoke test)
bash tests/run-all.sh
```

CI runs both on every PR. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full development guide.

## License

Apache 2.0 — see [cpzai/LICENSE](cpzai/LICENSE).

---

<div align="center">

Built by [CPZ Lab](https://www.cpz-lab.com/) — [CPZAI](https://ai.cpz-lab.com)

</div>
