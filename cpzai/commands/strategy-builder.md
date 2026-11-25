---
description: Build a trading strategy from a natural language idea — generates Python code and creates it on the platform
argument-hint: "<strategy description>"
allowed-tools:
  - mcp__plugin_cpzai_cpzai__list_strategies
  - mcp__plugin_cpzai_cpzai__get_strategy
  - mcp__plugin_cpzai_cpzai__create_strategy
  - mcp__plugin_cpzai_cpzai__update_strategy
  - mcp__plugin_cpzai_cpzai__get_market_data
---

# Strategy Builder

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).
>
> Use only figures a CPZAI tool returns. Anything a template below asks for that no tool provides (see [What the Tools Return](../CONNECTORS.md#what-the-tools-return-and-what-they-do-not)) is written "not available from CPZAI", never filled from memory.

**Important**: This command generates strategy code to assist development. All strategies should be thoroughly backtested and reviewed before live deployment. Trading carries risk of loss.

Take a natural language description of a trading idea and produce a complete, deployable Python strategy — then create it on the user's CPZAI account.

## Usage

```
/cpzai:strategy-builder <description>
```

### Arguments

- `description` — A plain-English description of the strategy idea. Can include:
  - Strategy type (momentum, mean-reversion, pairs, breakout, factor, statistical arbitrage)
  - Target instruments (specific tickers, sectors, asset classes)
  - Entry/exit signals (z-score, moving average crossover, RSI, volume spikes)
  - Position sizing approach (equal-weight, volatility-scaled, Kelly)
  - Rebalance frequency (daily, weekly, monthly)
  - Risk constraints (max drawdown, position limits, sector caps)

## Workflow

### 1. Clarify the Idea

Parse the user's description and identify:
- **Strategy archetype** — which family does this belong to?
- **Universe** — what instruments are in scope?
- **Signal** — what triggers entry and exit?
- **Sizing** — how much capital per position?
- **Risk rules** — stops, limits, exposure caps?

If any critical element is missing, ask one focused follow-up question. Don't ask more than two questions before generating.

### 2. Generate the Strategy Code

Write `strategy.py` in the format CPZAI's Strategy Lab backtests. Code in any other shape (a class, a script, a function under another name) fails before its first bar with "No strategy interface function is available".

The format:
- A flat module of imports, constants and functions. No class wrapping the signal, no code that runs at import time beyond definitions
- `SYMBOLS = ["AAPL", "MSFT", ...]`: a literal list of every ticker the code reads, including a benchmark or filter symbol such as SPY. Never a function call, comprehension or screener result
- Exactly one module-level signal function:
  - `def generate_signals(data, state, **kwargs)` (preferred) or `def generate_signal(data, state)`: `data` holds point-in-time history per symbol (polars DataFrames with `timestamp, open, high, low, close, volume`); return a dict of symbol to target weight
  - or `def on_bar(context, data)`, which calls `context.target_weights(weights)`
- Weights, not share quantities or orders: an empty dict means no rebalance, an explicit 0 closes a position. The backtest fills at the next bar's open
- Use only the supplied history: no broker orders, live data, API clients or screeners inside the signal or at import
- numpy and polars are available; for pandas, build the frame with `pd.DataFrame(df.to_dict(as_series=False))` (`to_pandas()` needs pyarrow, which the runner does not have)

Within that format:
- Clear parameters with defaults as module constants
- Position sizing in the returned weights (equal-weight, vol-scaled, or signal-weighted), with caps on single-name weight and gross exposure
- Keep it simple: fewer parameters means less overfitting

### 3. Explain the Logic

Provide a brief summary covering:
- What the strategy does in 2-3 sentences
- Key parameters and what they control
- Expected behavior (when it buys, when it sells, when it's flat)
- Known limitations or assumptions

### 4. Create on the Platform

If ~~cpzai is connected:
- Call `create_strategy` with the generated code as `python_code`
- Set strategy type, title, and description
- Report the created strategy ID back to the user
- Suggest next step: "Backtest it in CPZAI Strategy Lab, then run `/cpzai:backtest` to analyze the run"

If no connection:
> Connect your CPZAI account to create the strategy automatically. For now, here's the code — you can paste it into the Strategy Lab at [ai.cpz-lab.com](https://ai.cpz-lab.com).

### 5. Suggest Improvements

After creating, briefly mention 1-2 ways to iterate:
- Parameter values to experiment with
- Additional filters or confirmation signals
- Risk management enhancements
- Complementary strategies for diversification
