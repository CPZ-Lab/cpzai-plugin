---
description: Analyze a strategy's saved backtest runs and suggest improvements (runs start in CPZAI Strategy Lab)
argument-hint: "<strategy> [date range] [parameters]"
allowed-tools:
  - mcp__plugin_cpzai_cpzai__list_strategies
  - mcp__plugin_cpzai_cpzai__get_strategy
  - mcp__plugin_cpzai_cpzai__update_strategy
  - mcp__plugin_cpzai_cpzai__get_backtest_results
  - mcp__plugin_cpzai_cpzai__get_backtest_result
---

# Backtest

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).
>
> Use only figures a CPZAI tool returns. Anything a template below asks for that no tool provides (see [What the Tools Return](../CONNECTORS.md#what-the-tools-return-and-what-they-do-not)) is written "not available from CPZAI", never filled from memory.

**Important**: Backtest results reflect historical performance and do not guarantee future returns. Be aware of common pitfalls like overfitting, survivorship bias, and look-ahead bias.

Read a strategy's saved backtest runs and provide a thorough analysis with improvement suggestions.

**No CPZAI tool starts a backtest.** Runs are started in CPZAI Strategy Lab. Never call `execute_strategy` for a backtest: it runs the strategy's code and can submit orders, and it takes no date range or backtest settings.

## Usage

```
/cpzai:backtest <strategy> [date range] [parameters]
```

### Arguments

- `strategy`: Strategy name or ID whose runs to analyze
- `date range` (optional): The run to pick, by its backtest period, e.g. `2020-01 to 2024-12`
- `parameters` (optional): The run to pick, by its parameters, e.g. `lookback=20 threshold=2.0`

## Workflow

### 1. Identify the Strategy

If ~~cpzai is connected:
- Call `list_strategies` to find the strategy by name or ID
- Call `get_strategy` to retrieve its code and current parameters
- Confirm with the user which strategy and which saved run to analyze

If no connection:
> Connect your CPZAI account to read your saved backtest runs. To analyze results from elsewhere, provide the performance metrics.

### 2. Find the Saved Run

- Call `get_backtest_results` with the strategy ID to list its saved runs (newest first)
- Pick the run matching the requested period and parameters, and call `get_backtest_result` for its configuration and result
- If no saved run matches, say so and stop: ask the user to run it in CPZAI Strategy Lab, then run this command again. Do not start a run any other way

Report only metrics the saved run contains; any line of the templates below that the run does not hold is "not available from CPZAI".

### 3. Performance Summary

Present results in a structured format:

```
BACKTEST RESULTS — [Strategy Name]
Period: [Start] to [End]
═══════════════════════════════════

Return:              XX.X% (total) | XX.X% (annualized)
Benchmark (SPY):     XX.X% (total) | XX.X% (annualized)
Alpha:               XX.X% (annualized)

Sharpe Ratio:        X.XX
Sortino Ratio:       X.XX
Calmar Ratio:        X.XX

Max Drawdown:        XX.X% ([date] to [date])
Avg Drawdown:        X.X%
Recovery Time:       XX days (longest)

Win Rate:            XX.X%
Profit Factor:       X.XX
Avg Win / Avg Loss:  X.XX

Total Trades:        XXX
Avg Holding Period:  XX days
Turnover:            XX.X% (annualized)
```

### 4. Regime Analysis

Break performance into market regimes:

| Regime | Period | Strategy Return | Benchmark Return | Sharpe |
|--------|--------|----------------|-----------------|--------|
| Bull | ... | ... | ... | ... |
| Bear | ... | ... | ... | ... |
| Sideways | ... | ... | ... | ... |
| High Vol | ... | ... | ... | ... |

Highlight:
- Does the strategy protect in drawdowns?
- Does it capture upside in rallies?
- How does it behave in low-vol grind-up markets?

### 5. Robustness Checks

Assess whether results are likely to hold out-of-sample:

- **Parameter sensitivity** — How much do results change with ±20% parameter shifts?
- **Time stability** — Is performance consistent across sub-periods (halves, thirds)?
- **Trade count**: 30+ trades is directional only; a meaningful Sharpe needs 100+, robust inference 250+ (backtesting skill)
- **Overfitting indicators** — Sharpe > 3.0 in backtest is suspicious; very high win rates with few trades; performance only in one regime

### 6. Improvement Suggestions

Based on the results, suggest 2-3 specific improvements:

- Parameter adjustments (with reasoning)
- Additional filters to reduce false signals
- Risk management additions (trailing stops, time-based exits)
- Universe changes (add/remove instruments)
- Combine with other signals for confirmation

### 7. Next Steps

Recommend the logical next action:
- If results are strong: "Consider paper trading — use `/cpzai:risk-report` after a few days to monitor"
- If results need work: "Try adjusting [parameter]. I can update the strategy code; run the new version in Strategy Lab and I will analyze it"
- If results are poor: "This signal may not have edge. Consider a fundamentally different approach like [suggestion]"
