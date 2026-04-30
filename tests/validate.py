#!/usr/bin/env python3
"""CPZAI plugin structure validator.

Validates:
  - .claude-plugin/marketplace.json schema (kebab-case names, required fields)
  - cpzai/.claude-plugin/plugin.json schema (kebab-case, required + recommended fields)
  - cpzai/.mcp.json structure
  - cpzai/hooks/hooks.json structure
  - All command frontmatter (description, optional argument-hint, optional allowed-tools)
  - All skill frontmatter (name, description)
  - All agent frontmatter (name, description)
  - All scripts are executable
  - All MCP tool references resolve to known live tools

Exits 0 on success, 1 on any failure. Run via:
    python3 tests/validate.py
"""
from __future__ import annotations

import json
import os
import re
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "cpzai"

# Live tool list as of plugin v2.0.0. Update when the MCP server adds tools.
LIVE_TOOLS = {
    "list_strategies",
    "get_strategy",
    "create_strategy",
    "update_strategy",
    "get_backtest_results",
    "list_orders",
    "place_order",
    "list_positions",
    "sync_portfolio",
    "list_accounts",
    "get_market_data",
    "compute_risk",
    "list_risk_snapshots",
    "execute_strategy",
    "list_webhooks",
    "create_webhook",
    "delete_webhook",
    "get_profile",
}

# Built-in Claude Code tools that may appear in allowed-tools.
BUILTIN_TOOLS = {
    "Read", "Write", "Edit", "Bash", "Glob", "Grep", "WebFetch", "WebSearch",
    "Task", "TodoWrite", "NotebookEdit", "AskUserQuestion", "Skill",
}

KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TOOL_REF = re.compile(r"^mcp__([a-z0-9_]+)__([a-z0-9_]+)$")

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def parse_frontmatter(path: Path) -> tuple[dict, str] | tuple[None, str]:
    text = path.read_text()
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    fm_text = text[4:end]
    body = text[end + 4:]
    parsed: dict = {}
    cur_key: str | None = None
    cur_list: list | None = None
    for line in fm_text.splitlines():
        if not line.strip():
            cur_key = None
            cur_list = None
            continue
        m = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
        if m and not line.startswith(" ") and not line.startswith("\t"):
            cur_key = m.group(1)
            val = m.group(2).strip()
            if val == "":
                # likely a list follows
                cur_list = []
                parsed[cur_key] = cur_list
            else:
                parsed[cur_key] = val
                cur_list = None
        else:
            # list item under last key
            mm = re.match(r"^\s*-\s*(.+)$", line)
            if mm and cur_list is not None:
                cur_list.append(mm.group(1).strip())
    return parsed, body


def validate_marketplace() -> None:
    path = ROOT / ".claude-plugin" / "marketplace.json"
    if not path.exists():
        err(f"missing {path}")
        return
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        err(f"{path}: invalid JSON: {e}")
        return
    if "name" not in data:
        err(f"{path}: missing 'name'")
    elif not KEBAB.match(data["name"]):
        err(f"{path}: name '{data['name']}' is not kebab-case")
    if "owner" not in data or "name" not in data.get("owner", {}):
        err(f"{path}: missing owner.name")
    if "plugins" not in data or not isinstance(data["plugins"], list):
        err(f"{path}: missing plugins[] array")
        return
    for p in data["plugins"]:
        if "name" not in p:
            err(f"{path}: plugin entry missing 'name'")
        elif not KEBAB.match(p["name"]):
            err(f"{path}: plugin name '{p['name']}' is not kebab-case")
        if "source" not in p:
            err(f"{path}: plugin {p.get('name', '?')} missing 'source'")


def validate_plugin_manifest() -> None:
    path = PLUGIN / ".claude-plugin" / "plugin.json"
    if not path.exists():
        err(f"missing {path}")
        return
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        err(f"{path}: invalid JSON: {e}")
        return
    if "name" not in data:
        err(f"{path}: missing 'name'")
    elif not KEBAB.match(data["name"]):
        err(f"{path}: name '{data['name']}' is not kebab-case")
    for required in ("version", "description"):
        if required not in data:
            warn(f"{path}: missing recommended '{required}'")
    if "version" in data and not re.match(r"^\d+\.\d+\.\d+", data["version"]):
        err(f"{path}: version '{data['version']}' is not semver")
    if "license" not in data:
        warn(f"{path}: missing recommended 'license'")
    # userConfig sanity
    uc = data.get("userConfig", {})
    for k, v in uc.items():
        if "type" not in v:
            err(f"{path}: userConfig.{k} missing 'type'")
        if "title" not in v:
            err(f"{path}: userConfig.{k} missing 'title'")
        if "description" not in v:
            err(f"{path}: userConfig.{k} missing 'description'")


def validate_mcp_config() -> None:
    path = PLUGIN / ".mcp.json"
    if not path.exists():
        err(f"missing {path}")
        return
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        err(f"{path}: invalid JSON: {e}")
        return
    if "mcpServers" not in data or not data["mcpServers"]:
        err(f"{path}: missing mcpServers")
        return
    for name, cfg in data["mcpServers"].items():
        if cfg.get("type") not in ("http", "stdio", "sse", "websocket"):
            warn(f"{path}: server {name} has unknown type {cfg.get('type')}")
        if cfg.get("type") == "http" and "url" not in cfg:
            err(f"{path}: http server {name} missing 'url'")


def validate_hooks() -> None:
    path = PLUGIN / "hooks" / "hooks.json"
    if not path.exists():
        warn(f"missing {path} (hooks are optional)")
        return
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        err(f"{path}: invalid JSON: {e}")
        return
    if "hooks" not in data:
        err(f"{path}: missing top-level 'hooks' key")
        return
    for event, entries in data["hooks"].items():
        for entry in entries:
            for hk in entry.get("hooks", []):
                if hk.get("type") == "command":
                    cmd = hk.get("command", "")
                    # Variable substitution check
                    if "${CLAUDE_PLUGIN_ROOT}" in cmd:
                        rel = cmd.replace("${CLAUDE_PLUGIN_ROOT}/", "")
                        rel = rel.split()[0]
                        target = PLUGIN / rel
                        if not target.exists():
                            err(f"{path}: command references non-existent {target}")
                        elif not (target.stat().st_mode & stat.S_IXUSR):
                            err(f"{target}: not executable (chmod +x required)")


def validate_command(path: Path) -> None:
    fm, _ = parse_frontmatter(path)
    rel = path.relative_to(ROOT)
    if fm is None:
        err(f"{rel}: missing YAML frontmatter")
        return
    if "description" not in fm:
        err(f"{rel}: missing 'description' in frontmatter")
    if "argument-hint" in fm:
        ah = fm["argument-hint"]
        if isinstance(ah, str) and ah.startswith('" '):
            err(f"{rel}: argument-hint starts with leading whitespace inside the quoted value")
    if "allowed-tools" in fm:
        tools = fm["allowed-tools"]
        if not isinstance(tools, list):
            err(f"{rel}: allowed-tools must be a list")
        else:
            for t in tools:
                m = TOOL_REF.match(t)
                if m:
                    server, tool = m.group(1), m.group(2)
                    if server == "cpzai" and tool not in LIVE_TOOLS:
                        err(f"{rel}: allowed-tools references unknown CPZAI tool '{tool}'")
                elif t not in BUILTIN_TOOLS and not t.startswith("Bash("):
                    warn(f"{rel}: allowed-tools entry '{t}' is not a known built-in or mcp__server__tool reference")


def validate_skill(path: Path) -> None:
    fm, _ = parse_frontmatter(path)
    rel = path.relative_to(ROOT)
    if fm is None:
        err(f"{rel}: missing YAML frontmatter")
        return
    for required in ("name", "description"):
        if required not in fm:
            err(f"{rel}: missing '{required}' in frontmatter")
    if "name" in fm and not KEBAB.match(fm["name"]):
        err(f"{rel}: skill name '{fm['name']}' is not kebab-case")
    # Check directory matches name when set
    if "name" in fm and path.parent.name != fm["name"]:
        warn(f"{rel}: directory '{path.parent.name}' differs from frontmatter name '{fm['name']}'")


def validate_agent(path: Path) -> None:
    fm, _ = parse_frontmatter(path)
    rel = path.relative_to(ROOT)
    if fm is None:
        err(f"{rel}: missing YAML frontmatter")
        return
    for required in ("name", "description"):
        if required not in fm:
            err(f"{rel}: missing '{required}' in frontmatter")
    if "name" in fm and not KEBAB.match(fm["name"]):
        err(f"{rel}: agent name '{fm['name']}' is not kebab-case")
    if "tools" in fm and isinstance(fm["tools"], list):
        for t in fm["tools"]:
            m = TOOL_REF.match(t)
            if m and m.group(1) == "cpzai" and m.group(2) not in LIVE_TOOLS:
                err(f"{rel}: tools references unknown CPZAI tool '{m.group(2)}'")


def main() -> int:
    print(f"Validating plugin at {PLUGIN}")
    validate_marketplace()
    validate_plugin_manifest()
    validate_mcp_config()
    validate_hooks()

    cmd_dir = PLUGIN / "commands"
    cmds = sorted(cmd_dir.glob("*.md")) if cmd_dir.exists() else []
    print(f"  commands: {len(cmds)}")
    for c in cmds:
        validate_command(c)

    skills_dir = PLUGIN / "skills"
    skills = sorted(skills_dir.glob("*/SKILL.md")) if skills_dir.exists() else []
    print(f"  skills:   {len(skills)}")
    for s in skills:
        validate_skill(s)

    agents_dir = PLUGIN / "agents"
    agents = sorted(agents_dir.glob("*.md")) if agents_dir.exists() else []
    print(f"  agents:   {len(agents)}")
    for a in agents:
        validate_agent(a)

    scripts_dir = PLUGIN / "scripts"
    scripts = sorted(scripts_dir.glob("*.sh")) if scripts_dir.exists() else []
    print(f"  scripts:  {len(scripts)}")
    for sc in scripts:
        if not (sc.stat().st_mode & stat.S_IXUSR):
            err(f"{sc.relative_to(ROOT)}: not executable")

    print()
    if warnings:
        print(f"warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  ! {w}")
    if errors:
        print(f"errors ({len(errors)}):")
        for e in errors:
            print(f"  x {e}")
        return 1
    print("OK — no errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
