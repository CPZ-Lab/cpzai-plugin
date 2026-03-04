# CPZAI — Systematic Trading Plugin

A plugin that turns Claude into a systematic trading specialist. Built for [Cowork](https://claude.com/product/cowork), also compatible with [Claude Code](https://claude.com/product/claude-code).

Build quantitative strategies, backtest them against historical data, monitor risk in real time, and execute trades — all through natural conversation with Claude, powered by [CPZAI Quant Studio](https://ai.cpz-lab.com).

> **Important**: This plugin assists with trading and investment workflows but does not provide financial advice. All trading decisions carry risk of loss and should be made by qualified individuals. Past performance does not guarantee future results.

## Prerequisites

You need a CPZAI Quant Studio account with API credentials. The plugin connects to the CPZAI MCP server — without valid credentials, no tools are accessible.

1. Sign up at [ai.cpz-lab.com](https://ai.cpz-lab.com)
2. Go to **Settings → API Keys** and generate a key pair
3. Install the plugin (see below)

## Installation

### Cowork

Install from [claude.com/plugins](https://claude.com/plugins/).

### Claude Code

```bash
# Add the marketplace
claude plugin marketplace add cpz-lab/cpzai-plugin

# Install the plugin
claude plugin install cpzai@cpzai-plugin
```

## Commands

| Command | Description |
|---------|-------------|
| `/cpzai:strategy-builder` | Guided strategy creation — describe a trading idea and Claude writes the code, creates the strategy on the platform |
| `/cpzai:risk-report` | Generate a risk report — VaR, Sharpe, drawdown, correlation, with actionable recommendations |
| `/cpzai:backtest` | Run a strategy backtest, analyze metrics, and identify improvements |
| `/cpzai:market-scan` | Scan sectors or themes with real-time quotes and technical/fundamental context |
| `/cpzai:portfolio-review` | Full portfolio health check — positions, diversification, performance attribution |

## Skills

Skills activate automatically when Claude detects relevant context:

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

## MCP Tools

The CPZAI MCP server provides 18 tools:

- **Strategies** — create, list, update, and manage algorithmic trading strategies
- **Backtesting** — retrieve backtest results with performance metrics
- **Trading** — place orders, list positions, sync portfolios across broker accounts
- **Market Data** — real-time quotes for any symbol
- **Risk** — compute VaR, Sharpe, drawdown, beta; track risk history
- **Execution** — run strategies on the compute backend
- **Webhooks** — subscribe to platform events (fills, alerts)

Each skill includes **tool chaining workflows** that specify the exact sequence of MCP tool calls for common tasks (e.g. "risk check" = `list_positions` -> `get_market_data` -> `compute_risk` -> synthesize).

See [CONNECTORS.md](CONNECTORS.md) for the full tool reference.

## Example Workflows

### Build a mean-reversion strategy from scratch

```
/cpzai:strategy-builder pairs mean-reversion on AAPL/MSFT using z-score entry at 2.0 std
```

Claude will write the Python strategy code, explain the logic, and create it on your CPZAI account — ready to backtest.

### Morning risk check

```
/cpzai:risk-report
```

Pulls your live positions, computes current VaR/Sharpe/drawdown, flags concentration risk, and suggests hedges.

### Backtest and iterate

```
/cpzai:backtest my momentum strategy from 2020-01 to 2024-12 with weekly rebalance
```

Runs the backtest, analyzes results (Sharpe, max drawdown, win rate), and suggests parameter improvements.

## Configuration

The plugin authenticates via your MCP client's server configuration. Add your credentials:

```json
{
  "mcpServers": {
    "cpzai": {
      "type": "http",
      "url": "https://mcp.cpz-lab.com/mcp",
      "headers": {
        "X-CPZ-Key": "YOUR_KEY",
        "X-CPZ-Secret": "YOUR_SECRET"
      }
    }
  }
}
```

## License

Apache 2.0 — see [LICENSE](LICENSE).
