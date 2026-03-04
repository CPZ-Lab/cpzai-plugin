---
description: Build a trading strategy from a natural language idea — generates Python code and creates it on the platform
argument-hint: " <strategy description>"
---

# Strategy Builder

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

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

Write a complete Python strategy following standard systematic trading conventions:

Requirements:
- Clean, readable Python with clear parameter definitions and defaults
- Signal logic separated from execution logic
- Position sizing with configurable method (equal-weight, vol-scaled, or signal-weighted)
- Risk checks built in (max position size, exposure limits, stop-loss levels)
- Use standard libraries (numpy, pandas) for calculations
- Keep it simple — no over-engineering for a first version; fewer parameters = less overfitting

### 3. Explain the Logic

Provide a brief summary covering:
- What the strategy does in 2-3 sentences
- Key parameters and what they control
- Expected behavior (when it buys, when it sells, when it's flat)
- Known limitations or assumptions

### 4. Create on the Platform

If ~~cpzai is connected:
- Call `create_strategy` with the generated code
- Set strategy type, title, and description
- Report the created strategy ID back to the user
- Suggest next step: "Run `/cpzai:backtest` to test this strategy"

If no connection:
> Connect your CPZAI account to create the strategy automatically. For now, here's the code — you can paste it into the Strategy Lab at [ai.cpz-lab.com](https://ai.cpz-lab.com).

### 5. Suggest Improvements

After creating, briefly mention 1-2 ways to iterate:
- Parameter values to experiment with
- Additional filters or confirmation signals
- Risk management enhancements
- Complementary strategies for diversification
