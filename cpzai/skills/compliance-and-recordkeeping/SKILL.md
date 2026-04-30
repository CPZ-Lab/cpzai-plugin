---
name: compliance-and-recordkeeping
description: Trading compliance, audit trails, recordkeeping, and the regulatory baseline every systematic operator must maintain — order audit logs, best-execution evidence, model governance documentation, books-and-records under SEC Rule 17a-4, and FINRA/CFTC/MiFID II considerations. Use when the user is setting up a new account, building a model governance process, designing an audit trail, preparing for examiner questions, or asking what records they need to keep.
---

# Compliance and Recordkeeping

Quantitative trading is a regulated activity in every major jurisdiction. The strategies in this plugin are tools — what makes them safe and defensible is the operating discipline around them. This skill covers the minimum viable compliance and recordkeeping practices that every systematic operator should adopt, whether they are a single-account retail user or a registered investment adviser.

This is not legal advice. Consult counsel and your compliance officer for jurisdiction-specific requirements.

## The Three Pillars

Every systematic trading operation needs three durable, immutable records:

1. **Order audit trail** — every order intent, every parent/child relationship, every fill, every cancel.
2. **Decision audit trail** — the model, parameters, and inputs that produced each order.
3. **Risk audit trail** — pre-trade and post-trade risk snapshots, exposure breaches, and remediations.

The CPZAI plugin's PostToolUse audit hook writes a single-line JSON record for every state-mutating tool call to `${CLAUDE_PLUGIN_DATA}/audit.log`. Treat that file as your primary local audit source and back it up regularly.

## Order Audit Trail

For every order, capture and retain at minimum:

| Field | Why it matters |
|-------|---------------|
| Receipt timestamp (millisecond precision) | Reconstruct event sequence under examination |
| Intended account | Distinguish paper vs live, allocation correctness |
| Symbol, side, quantity, order type, price, time-in-force | Order intent |
| Strategy ID / signal hash | Link order back to its decision source |
| User confirmation (if applicable) | Evidence of human-in-the-loop |
| Broker order ID | Link to broker-side records |
| Fill events (price, qty, venue, timestamp) | Best-execution evidence |
| Cancellation events (reason, timestamp) | Demonstrate intent and process |

**Retention:** SEC Rule 17a-4 requires registered broker-dealers to keep order records for 6 years (first 2 readily accessible). Retail traders are not subject to 17a-4 directly, but the best practice is still 7 years on tax-deductible activities and indefinitely on long-term investing decisions.

## Decision Audit Trail

For every algorithmic decision, capture:

- **Strategy version hash** — the SHA of the exact code that ran
- **Parameter set** — every numeric input the strategy used
- **Input data fingerprint** — the dataset version, vendor, and snapshot timestamp
- **Output signal** — the score/rank/decision the strategy produced
- **Translation to order** — how the signal became a specific order (sizing rule, rounding, etc.)

**Why:** when (not if) a regulator, auditor, or counterparty asks "why did you place that order on Tuesday at 9:32?", you need to be able to reproduce the decision deterministically.

CPZAI strategies are stored with their Python source, so the strategy version is recoverable via `get_strategy(id)`. The parameter set must be captured separately if you mutate it across runs.

## Risk Audit Trail

For every trading day, capture at minimum a daily risk snapshot. The CPZAI `compute_risk` and `list_risk_snapshots` tools provide this. For each snapshot, the auditable fields are:

- VaR (95%, 1d) — both parametric and historical if available
- Sharpe and Sortino, trailing 30-day and YTD
- Maximum drawdown — current and historical
- Beta to chosen benchmark
- Largest position weight, sector concentration
- Risk score (composite) and the 30-day baseline

When a risk metric breaches a documented limit, capture:
- The breach event (time, metric, value, limit)
- The decision (continue, reduce, hedge, halt)
- The action taken
- The post-action measurement that confirms remediation

## Best Execution Evidence

If you trade on behalf of others (or want to defend your own execution choices), retain:

- The bid/ask spread at the moment of the decision
- The arrival price (mid at decision time)
- The fill price(s) and timestamps
- Implementation shortfall = (Fill - Arrival) × shares signed for buys/sells
- Comparison to a benchmark (VWAP for the day, arrival, close)

The `get_market_data` and `list_orders` tools provide the inputs; you must capture them at the right moment and store them paired with the order.

## Model Governance

For any strategy that places real orders, maintain a brief but explicit governance dossier:

1. **Hypothesis** — the economic rationale, in plain English, in 2-5 sentences
2. **Data sources** — vendors, fields, frequency, snapshot policy
3. **Method** — feature engineering, model class, training procedure, validation scheme
4. **Backtest results** — IC distribution, Sharpe, drawdown, sub-period stability, parameter sensitivity
5. **Risks** — known failure modes, regimes where it underperforms, decay expectation
6. **Live performance** — rolling comparison of live to backtest expectations
7. **Change log** — every parameter change, code change, universe change, with date and rationale
8. **Decommission criteria** — pre-defined conditions under which the strategy is paused or killed

When changes happen, append to the change log; do not edit prior entries.

## Jurisdiction-Specific Notes

### United States

- **SEC Rule 17a-4** (broker-dealers): 6-year order record retention, write-once media or equivalent, designated third-party access in case of failure.
- **FINRA Rule 4511 / 4512**: customer account records, supervisory procedures.
- **Reg SHO**: short sale recordkeeping; locate and close-out requirements.
- **Reg ATS / Reg NMS**: order routing disclosure for those who route.
- **Wash sale (IRS §1091)**: 30-day window before and after; tax-loss harvesting must respect it across related accounts.

### European Union

- **MiFID II / MiFIR**: transaction reporting (RTS 22), best-execution reporting (RTS 27/28), record retention 5-7 years, 5-year tape recording for client communications related to trades.
- **EMIR**: derivative reporting to a trade repository.
- **GDPR**: any client data must respect data-subject rights even within the audit trail.

### United Kingdom

- **FCA SYSC** (Senior Management Arrangements, Systems and Controls): governance and recordkeeping in line with MiFID II equivalents.
- **MAR** (Market Abuse Regulation): no insider dealing, no market manipulation; for systematic operators this applies to any signal sourced from material non-public information.

### Algorithmic / Automated Trading

- **MiFID II RTS 6**: algorithmic trading systems must be tested, monitored, and have kill switches.
- **CFTC Reg AT (proposed/withdrawn but principles still relevant for futures algo)**: pre-trade risk controls, source code repository.
- **SEC 15c3-5 (Market Access Rule)**: pre-trade risk controls on broker-provided market access.

The minimum behavioral compliance for any user of this plugin: do not place orders driven by inside information; do not place orders intended to manipulate markets (spoofing, layering, marking-the-close); ensure every algorithmic order has a documented kill switch (which, in this stack, is your ability to call `update_strategy(status='paused')` or `delete_webhook` to stop event-driven flows).

## Practical Setup Checklist

For a new operator using this plugin:

- [ ] Decide your retention policy (recommend ≥7 years).
- [ ] Configure the plugin's userConfig with `require_trade_confirmation=true` until you have a documented exception process.
- [ ] Back up `${CLAUDE_PLUGIN_DATA}/audit.log` to durable storage daily.
- [ ] Snapshot strategies (via `list_strategies` + `get_strategy`) on a schedule and version the JSON in a private repo.
- [ ] Capture daily risk snapshots via `compute_risk`; archive `list_risk_snapshots` weekly.
- [ ] Maintain a written governance dossier (1-3 pages per strategy).
- [ ] Keep a single change log file for all production parameter changes.
- [ ] Have a written kill-switch procedure: who can pause what, how, and how it is verified.
- [ ] Periodically (quarterly recommended) replay a random sample of trades from the audit log to verify reproducibility.

## When Asked "Show Me Your Records"

A good answer is:

> "Every order is logged at `audit.log` with timestamp, account, symbol, side, qty, type, price, and broker order ID. The strategy that produced each order is identified by its UUID and the SHA of its Python source at the time. Daily risk snapshots are stored in CPZAI and exported weekly to private storage. Model change history is in `governance/CHANGELOG.md` with one commit per parameter change, signed by the operator."

If you cannot give that answer today, this skill is your roadmap to being able to give it tomorrow.
