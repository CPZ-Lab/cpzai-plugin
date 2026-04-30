# Contributing to the CPZAI plugin

Thank you for considering a contribution. The CPZAI plugin is the surface that turns Claude into a systematic trading specialist — quality and safety here directly affect whether real capital moves correctly.

## Ground Rules

1. **Safety first.** Anything that touches `place_order`, `execute_strategy`, or `delete_webhook` must preserve the human-in-the-loop guarantee. Do not bypass `hooks/hooks.json` or remove the `require_trade_confirmation` userConfig.
2. **Spec compliance.** All names are kebab-case. All manifests validate. Every `mcp__cpzai__*` reference points to a real tool on the production server.
3. **No secrets in code.** API keys live in `userConfig` (sensitive flag) and flow through MCP headers via `${user_config.*}` substitution. Never hardcode credentials, even in tests.

## Repository Layout

```
.
├── .claude-plugin/
│   └── marketplace.json          # Marketplace catalog entry
├── .github/workflows/
│   └── validate.yml              # CI: structure validation + smoke MCP test
├── cpzai/                        # The plugin itself
│   ├── .claude-plugin/
│   │   └── plugin.json           # Plugin manifest + userConfig
│   ├── .mcp.json                 # MCP server config (HTTP transport)
│   ├── CONNECTORS.md             # Authoritative tool reference
│   ├── LICENSE                   # Apache-2.0
│   ├── agents/                   # 3 specialized subagents
│   ├── commands/                 # 17 slash commands
│   ├── hooks/                    # Lifecycle hooks (Session/PreTool/PostTool)
│   ├── scripts/                  # Bash helpers invoked by hooks
│   └── skills/                   # 10 skills (auto-activate by context)
├── tests/                        # validate.py + smoke-mcp.sh + run-all.sh
├── CHANGELOG.md
├── CONTRIBUTING.md
└── README.md
```

## Development Loop

```bash
# 1. Make a change.
$EDITOR cpzai/commands/some-command.md

# 2. Validate locally (offline — no network).
bash tests/run-all.sh --offline

# 3. Run the live smoke test (requires internet).
bash tests/run-all.sh
```

Both pass before you commit. CI runs the same scripts.

## Adding a Command

1. Create `cpzai/commands/<name>.md` (kebab-case).
2. Add frontmatter:
   ```yaml
   ---
   description: One-line purpose
   argument-hint: "<args>"           # optional
   allowed-tools:                    # required if you call MCP tools
     - mcp__cpzai__<tool>
   ---
   ```
3. Body: explain workflow steps, reference relevant skills, give next-step suggestions. Use `~~cpzai` as the placeholder for the MCP server in prose.
4. Add an entry to the README's command table.
5. Run `bash tests/run-all.sh --offline`.

## Adding a Skill

1. Create `cpzai/skills/<name>/SKILL.md` (kebab-case directory).
2. Frontmatter must include `name` and `description`. The `description` should clearly state when the skill activates.
3. Body: comprehensive reference material. Skills are loaded into Claude's context when invoked, so keep them rich but focused. End with a "CPZAI Tool Chaining" section that maps the skill's workflow to specific MCP tool calls.
4. Add an entry to the README's skill table.

## Adding an Agent

Plugin-shipped agents support `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`. They do **not** support `hooks`, `mcpServers`, or `permissionMode`.

Pick a model deliberately:
- `opus` + `effort: high` for deep research / planning
- `sonnet` + `effort: medium` for procedural / review tasks
- `haiku` for fast triage

Always set `disallowedTools` to gate destructive actions an agent should never take (e.g. `mcp__cpzai__place_order` for read-only research agents).

## Adding a Hook

1. Edit `cpzai/hooks/hooks.json`.
2. Hook scripts live in `cpzai/scripts/` and must be executable (`chmod +x`).
3. Reference scripts via `${CLAUDE_PLUGIN_ROOT}/scripts/<name>.sh`.
4. Hooks that block tool calls must emit JSON `{"decision":"block","reason":"..."}` — see `pre-trade-guard.sh` for the canonical pattern.

## Versioning

We follow [SemVer](https://semver.org/):
- **MAJOR** — breaking changes (manifest schema change, removed command/tool, hook behavior change).
- **MINOR** — new commands, skills, agents, hooks; new userConfig keys with safe defaults.
- **PATCH** — fixes, doc updates, internal refactors.

Bump `cpzai/.claude-plugin/plugin.json` `version` and add a `CHANGELOG.md` entry in the same commit. Tag the release: `git tag v<version> && git push --tags`.

## Pull Request Checklist

- [ ] `bash tests/run-all.sh --offline` passes.
- [ ] `bash tests/run-all.sh` (live smoke) passes.
- [ ] CHANGELOG updated under the appropriate `## [Unreleased]` or version header.
- [ ] README updated if you added or changed a command, skill, or agent.
- [ ] CONNECTORS.md updated if you wired a new MCP tool.
- [ ] No secrets in the diff.
- [ ] Conventional commit message (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).

## License

By contributing you agree your contributions are licensed under the project's [Apache-2.0](cpzai/LICENSE) license.
