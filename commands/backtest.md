---
description: Run a strategy backtest, analyze performance metrics, and suggest improvements
argument-hint: " <strategy> [date range] [parameters]"
---

# Backtest

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

**Important**: Backtest results reflect historical performance and do not guarantee future returns. Be aware of common pitfalls like overfitting, survivorship bias, and look-ahead bias.

Run a strategy backtest, pull results, and provide a thorough analysis with improvement suggestions.

## Usage

```
/cpzai:backtest <strategy> [date range] [parameters]
```

### Arguments

- `strategy` — Strategy name or ID to backtest
- `date range` (optional) — Start and end dates, e.g. `2020-01 to 2024-12`
- `parameters` (optional) — Override default parameters, e.g. `lookback=20 threshold=2.0`

## Workflow

### 1. Identify the Strategy

If ~~cpzai is connected:
- Call `list_strategies` to find the strategy by name or ID
- Call `get_strategy` to retrieve its code and current parameters
- Confirm with the user which strategy and parameters to test

If no connection:
> Connect your CPZAI account to run backtests directly. To analyze existing results, provide the performance metrics.

### 2. Execute the Backtest

- Call `execute_strategy` with the strategy ID and backtest parameters
- Wait for completion (poll if needed)
- Call `get_backtest_results` to retrieve the output

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
- **Trade count** — Are there enough trades for statistical significance (>30)?
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
- If results need work: "Try adjusting [parameter] — I can update the strategy code for you"
- If results are poor: "This signal may not have edge. Consider a fundamentally different approach like [suggestion]"
