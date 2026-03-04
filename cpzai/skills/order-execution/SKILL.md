---
name: order-execution
description: Order execution — order types, execution quality, slippage management, and broker connectivity. Use when the user is placing trades, discussing order types, analyzing fills, or managing execution.
---

# Order Execution

How to get from signal to fill efficiently, minimizing execution costs and errors.

## Order Types

### Market Order

Executes immediately at the best available price. Use when speed matters more than price.

- **Pros:** guaranteed fill (in liquid markets), no management needed
- **Cons:** price uncertainty, slippage in fast markets or illiquid names
- **When to use:** urgent exits, highly liquid instruments, small orders

### Limit Order

Sets the maximum buy price or minimum sell price. Only fills at your price or better.

- **Pros:** price control, no slippage
- **Cons:** may not fill, partial fills, opportunity cost of missing the trade
- **When to use:** entries without urgency, scaling into positions, illiquid instruments

### Stop Order (Stop-Loss)

Becomes a market order when the stop price is reached. Used for risk management.

- **Stop-market:** triggers a market order at stop price — guaranteed exit but price may gap through
- **Stop-limit:** triggers a limit order at stop price — price control but may not fill in fast markets

### Trailing Stop

Stop price moves with the market in your favor but never moves against you.

- **Fixed trailing:** stop trails by a fixed dollar or percentage amount
- **ATR trailing:** stop trails by N × ATR — adapts to volatility

### Bracket Order (OCO)

Combines a take-profit limit and a stop-loss. When one fills, the other cancels. Useful for "set and forget" position management.

## Execution Quality

### Slippage

The difference between expected price and actual fill price.

**Causes:**
- Market movement between signal and execution
- Spread crossing (limit → market)
- Order size relative to available liquidity
- Latency

**Measurement:**
```
Slippage = Fill Price - Decision Price (for buys)
Slippage = Decision Price - Fill Price (for sells)
```

**Reducing slippage:**
- Use limit orders for non-urgent entries
- Split large orders into smaller pieces
- Avoid trading at market open (first 15 min) — spreads are widest
- Avoid trading during low-volume periods

### Fill Analysis

After each trade, evaluate:
- Did the fill price match expectations?
- What was the spread at time of execution?
- How much of the order filled? (partial fills)
- How long did the order take to fill?

### Implementation Shortfall

The total cost of implementing a trading decision, decomposed into:

```
IS = Delay Cost + Trading Cost + Opportunity Cost

Delay Cost     = (Arrival Price - Decision Price) × Shares Executed
Trading Cost   = (Execution Price - Arrival Price) × Shares Executed
Opportunity    = (Close Price - Decision Price) × Shares NOT Executed
```

Track IS over time to evaluate execution quality. Compare to benchmarks (VWAP, arrival price) and across brokers.

## Market Impact Models

### Square-Root Law

The most widely used market impact model. Temporary impact scales with the square root of trade size relative to volume:

```
Impact (bps) = σ_daily × η × √(Q / ADV)
```

Where Q = shares traded, ADV = average daily volume, η = market impact coefficient (typically 0.1-0.5 depending on the market), σ_daily = daily volatility in bps.

**Implication:** doubling your order size increases impact by ~40%, not 100%. But impact still grows — large orders in illiquid names are expensive.

### Almgren-Chriss Framework

Optimal execution that minimizes the sum of market impact and timing risk:

- **Trade too fast:** high market impact (you push the price against yourself)
- **Trade too slow:** high timing risk (the market moves while you wait)
- **Optimal:** balance the two based on risk aversion

The solution is a trajectory — how many shares to trade at each interval. For a risk-neutral trader, this is a constant rate (TWAP). For risk-averse traders, front-load the execution.

### Permanent vs Temporary Impact

- **Temporary impact:** price displacement that reverts after your order finishes. Caused by liquidity consumption.
- **Permanent impact:** price shift that persists. Caused by information leakage (the market learns from your trading).
- Total cost = temporary + permanent. For small retail orders, both are negligible. For institutional size, they dominate.

## Execution Algorithms

### TWAP (Time-Weighted Average Price)

Split the order evenly across time intervals. Simple, predictable, minimizes information leakage.

**When to use:** no urgency, low market impact tolerance, desire for predictable execution.

### VWAP (Volume-Weighted Average Price)

Trade proportionally to historical volume profile. More shares during high-volume periods (typically open and close), fewer during midday.

**When to use:** want to match the market's natural rhythm, benchmark is VWAP.

### Implementation Shortfall (IS) Algo

Front-loads execution to minimize risk of adverse price movement. Trades more aggressively early, tapers off.

**When to use:** time-sensitive signals where alpha decays quickly, willing to accept more market impact for reduced timing risk.

### Participation / POV (Percentage of Volume)

Trade at a fixed percentage of real-time volume (e.g. 10% of volume). Adapts to market conditions automatically.

**When to use:** want to be invisible in the order flow, limit market impact, no urgency.

### Pre-Trade Cost Estimation

Before executing, estimate expected cost:

| Component | Estimate |
|-----------|----------|
| Half-spread | bid-ask / 2 |
| Market impact | σ × η × √(Q/ADV) |
| Timing risk | σ × √(T) × α |
| Commission | broker fee schedule |
| **Total expected cost** | **sum of above** |

If total expected cost exceeds the signal's expected alpha, the trade is negative expected value — do not execute.

## Paper vs Live Trading

### Paper Trading

Simulated execution using real market data but no real money.

**Use paper trading to:**
- Validate strategy behavior in live market conditions
- Test order management and fill handling
- Build confidence before deploying capital
- Debug edge cases (market opens, halts, corporate actions)

**Paper trading limitations:**
- Fills are instant and at mid-price — real fills are worse
- No market impact — your orders don't move prices in paper
- No emotional pressure — live trading feels different

### Going Live

Recommended progression:
1. **Backtest** → validates the signal on historical data
2. **Paper trade** (2-4 weeks) → validates execution and infrastructure
3. **Live, small size** (1-2 months) → validates with real money at reduced risk
4. **Live, full size** → scale up after confirming live matches backtest

At each stage, compare actual performance to expected performance. If live Sharpe is less than half of backtest Sharpe, investigate before scaling.

## Broker Considerations

### Alpaca

CPZAI's primary broker integration. Supports:
- Stocks and ETFs (US markets)
- Market, limit, stop, stop-limit, trailing stop orders
- Paper and live accounts
- Real-time order status via WebSocket
- Fractional shares

### Interactive Brokers

Available for users who need:
- Options, futures, forex
- International markets
- Advanced order types (algorithmic orders, conditional)
- Lower commissions at scale

### Order Routing Best Practices

1. Always specify `time_in_force` (day, GTC, IOC, FOK)
2. Use `extended_hours: false` unless you specifically want pre/post-market fills
3. For strategies, prefer limit orders with a small buffer above/below current price
4. Monitor order status — don't assume fills; handle rejections and partial fills

## CPZAI Tool Chaining for Order Execution

When ~~cpzai is connected, execute this workflow:

**Pre-trade:**
1. **`list_accounts`** — verify which broker accounts are connected and check buying power
2. **`list_positions`** — check current holdings to avoid duplicates or unintended concentration
3. **`get_market_data`** — get current price, bid/ask spread, and volume for the target symbol
4. **`compute_risk`** — evaluate current portfolio risk before adding new exposure

**Execution:**
5. **`place_order`** — submit the order (market, limit, or stop) through the connected broker. For limit orders, reference the current bid/ask from step 3.

**Post-trade:**
6. **`list_orders`** — verify fill status (filled, partial, rejected). If partially filled, decide whether to chase or cancel remainder.
7. **`sync_portfolio`** — force-sync to reconcile positions across accounts
8. **`compute_risk`** — recompute risk metrics to verify the new position hasn't pushed the portfolio outside risk limits

**For strategy-driven execution:**
1. **`execute_strategy`** — run the strategy to generate signals
2. **`list_positions`** — compare current holdings to target portfolio
3. **`place_order`** (multiple) — execute the rebalancing trades
4. **`sync_portfolio`** — reconcile after all orders fill
