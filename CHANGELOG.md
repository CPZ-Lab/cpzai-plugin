# Changelog

All notable changes to the CPZAI plugin are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] — 2026-04-30

State-of-the-art upgrade aligning the plugin with the current Claude Code / Cowork plugin specification.

### Added
- `userConfig` block in `plugin.json` so the API key, secret, default environment, and trade-confirmation policy are prompted via the Claude `/plugin` UI and stored in the system keychain (no JSON editing required).
- HTTP header substitution in `.mcp.json` — credentials flow from `userConfig` into the MCP server via `X-CPZ-Key`/`X-CPZ-Secret` headers, plus a `X-CPZ-Client` identifier.
- `allowed-tools` frontmatter on every command — least-privilege scoping that maps each command to the minimal set of `mcp__cpzai__*` tools it needs.
- New `agents/` directory with three specialized subagents:
  - `quant-researcher` (opus, high effort) — deep alpha research with TodoWrite-backed experimental design.
  - `risk-auditor` (sonnet) — structured 6-dimension portfolio risk audit with prioritized remediation.
  - `execution-reviewer` (sonnet) — 7-point pre-trade compliance check; never places orders itself.
- New `hooks/hooks.json` with three lifecycle hooks:
  - `SessionStart` — prints a status banner (version, MCP URL, environment, auth state, confirmation policy).
  - `PreToolUse` — guards `place_order`, `execute_strategy`, and `delete_webhook` behind explicit confirmation.
  - `PostToolUse` — appends a single-line JSON audit record for every state-mutating tool call to `${CLAUDE_PLUGIN_DATA}/audit.log`.
- New `scripts/` directory with the three shell scripts above (executable, plain bash + python3).
- New 10th skill: `compliance-and-recordkeeping` — covers SEC Rule 17a-4, MiFID II, FINRA, model governance, audit trails, and a practical setup checklist.
- New `tests/` directory:
  - `tests/validate.py` — structure validator (manifests, frontmatter, kebab-case names, MCP tool reference resolution, executable scripts).
  - `tests/smoke-mcp.sh` — live MCP smoke test (OAuth metadata, initialize handshake, tools/list, cross-check that every referenced tool exists on the server).
  - `tests/run-all.sh` — orchestrator with `--offline` mode.
- New `.github/workflows/validate.yml` CI workflow — runs structure validation on every PR, smoke test on push to main.
- `CONTRIBUTING.md` with the development loop, validation steps, release process.
- `CHANGELOG.md` (this file).

### Changed
- Plugin name changed from `CPZAI` to `cpzai` in both manifests — kebab-case is required by the Claude Code spec and is the convention used by every plugin in the official Anthropic marketplace.
- Plugin `version` bumped to `2.0.0`.
- `plugin.json` enriched with `$schema`, `repository`, `homepage`, `license` (`Apache-2.0`), `keywords`, and `author.url`.
- `marketplace.json` enriched with `$schema`, `owner.url`, `metadata.description`, and `category: productivity`.
- `argument-hint` strings stripped of leading whitespace across all commands.
- README install instructions point to the correct GitHub handle (`CPZ-Lab/cpzai-plugin`); CONNECTORS link points to `cpzai/CONNECTORS.md`.
- `.gitignore` expanded to cover IDE/env artifacts.

### Removed
- Three stray `.DS_Store` files removed from the working tree.

### Security
- Pre-trade safety: every `place_order` and `execute_strategy` call is intercepted by the `PreToolUse` hook and requires the calling agent to summarize and re-confirm the action.
- `delete_webhook` is default-deny — the hook blocks the call and requires explicit acknowledgement.
- API key and secret are stored in the system keychain via the `sensitive: true` `userConfig` flag.
- Audit trail: every state-mutating call is logged with timestamp, tool name, and a 240-char input preview to `${CLAUDE_PLUGIN_DATA}/audit.log`.

## [1.0.0] — 2026-04-21

Initial public release.

- 17 commands covering strategy creation, backtesting, risk reporting, portfolio review, market scanning, trading, options analysis, equity research, earnings preview, factor screening, and more.
- 9 skills covering strategy development, risk management, backtesting, order execution, market data, portfolio analytics, portfolio optimization, volatility-and-derivatives, and alpha research.
- 18 MCP tools across Strategies, Backtesting, Trading, Market Data, Risk Analytics, Execution, Webhooks, and User categories.
- OAuth 2.0 + direct-header authentication.
- Cowork marketplace discovery via `marketplace.json`.

[2.0.0]: https://github.com/CPZ-Lab/cpzai-plugin/releases/tag/v2.0.0
[1.0.0]: https://github.com/CPZ-Lab/cpzai-plugin/releases/tag/v1.0.0
