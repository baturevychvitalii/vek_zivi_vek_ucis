# Cross-Tool Portability: Claude Code ↔ opencode

Notes on sharing tooling (skills, MCP servers, agents, hooks) between **Claude Code**
and **opencode** from one source of truth. Captured 2026-07-09.

**Goal:** one source of truth consumable by both tools — not just persisting Claude Code
config, and without scattering git submodules into every needed location.

---

## TL;DR

- **The counterintuitive crux:** wrapping skills in the **Claude Code plugin format is
  exactly what breaks opencode sharing.** opencode reads `.claude/skills/<name>/SKILL.md`
  natively, but it *cannot* see a skill bundled inside a Claude plugin (those live at
  `plugins/<name>/skills/` or, once installed, `~/.claude/plugins/cache/…` — none of which
  are in opencode's scan paths). opencode also can't load Claude plugins at all.
- **Two buckets:**
  1. **MCP server (`anki-mcp`): keep standalone.** Portable on its own merits — both tools
     speak MCP. One repo/submodule, referenced by each tool's own config. This part of the
     current migration is *sound*.
  2. **Skills: plain files in `.claude/skills/`** — no plugin wrapper, no submodule. Both
     tools read the path in place. This dissolves the "submodules everywhere" pain.
- Both tools implement the [agentskills.io](https://agentskills.io) open `SKILL.md`
  standard — **that standard IS the portability layer.** Don't hide it inside a proprietary
  wrapper.

---

## Shareability matrix

| Thing | Shared? | Why / what to do |
|---|---|---|
| **MCP servers** | ✅ | Both speak MCP; one repo, two config pointers |
| **Skills (`SKILL.md`)** | ✅ | Both read `.claude/skills/` natively (open standard) |
| **Agents** | ⚠️ partial | Both use md+frontmatter, but different schemas (opencode: `mode: subagent`, `permission:`) and locations (`.claude/agents/` vs `.opencode/agents/`) — needs per-tool copies |
| **Hooks** | ❌ | Claude = shell commands in settings.json; opencode = JS/TS event plugins. The mem-bank/debug hooks are Claude-only |
| **Pipelines / orchestration** | ❌ mostly | Command bodies port as skills, but pipeline wiring is tool-specific |

---

## Skill discovery paths (the key evidence)

**opencode** scans (walks up from CWD to the git worktree root):
- `.claude/skills/<name>/SKILL.md`      ← Claude-compatible (project)
- `~/.claude/skills/<name>/SKILL.md`    ← Claude-compatible (global)
- `.agents/skills/<name>/SKILL.md`      ← tool-neutral
- `.opencode/skills/<name>/SKILL.md`    ← opencode-native

**Claude Code** scans:
- `~/.claude/skills/<name>/SKILL.md`    ← personal (all projects)
- `.claude/skills/<name>/SKILL.md`      ← project (plus parent dirs up to repo root, plus
  nested dirs on demand — monorepo support)
- enterprise location
- `.claude/skills/` inside any `--add-dir` directory
- **Does NOT read `.agents/skills/`**

➡️ **Intersection = `.claude/skills/`.** That's the shared, tool-neutral-enough home both
tools read in place. (`.agents/skills/` would be *more* neutral but Claude Code doesn't
read it yet.)

Notes:
- Claude Code follows **symlinks** inside `.claude/skills/` (reads `SKILL.md` from the
  symlink target) — useful for the fallback below.
- Adding `.claude-plugin/plugin.json` to a skill folder makes it load as a plugin named
  `<name>@skills-dir` (can then bundle agents/hooks/MCP), but that reintroduces the
  Claude-only wrapper opencode can't see.

---

## MCP server config (same binary, two pointers)

```jsonc
// Claude Code — .mcp.json
{ "mcpServers": {
    "anki": { "command": "plugins/anki-mcp/.venv/bin/python3",
              "args": ["…"] } } }
```

```jsonc
// opencode — opencode.json / opencode.jsonc
{ "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "anki": { "type": "local",
              "command": ["plugins/anki-mcp/.venv/bin/python3", "…"],
              "enabled": true,
              "environment": { } } } }
```

opencode MCP: `type` is `"local"` (command array) or `"remote"` (url + headers), with
optional `enabled` / `environment`.

---

## Recommendations

- **`anki-mcp`**: keep as the standalone MCP submodule. ✅ Right call — leave it.
- **Skills currently being plugin-migrated**: move (or symlink) them back to plain
  `.claude/skills/<name>/`. Single source of truth for both tools.
- **Fallback** (only if a Claude *plugin* earns its keep for distribution AND you still want
  opencode visibility): symlink `.claude/skills/<name>` → the plugin's skill dir. Claude
  follows the symlink; opencode sees the `.claude/skills/` entry. Plain files are cleaner.
- **Hooks / agents**: accept thin per-tool adapters — no shared format to unify them.

Net: the MCP-as-submodule instinct is the right half of the elegant solution. The other
half is the *opposite* of plugin-wrapping — keep skills as bare files in `.claude/skills/`,
where the open standard does the cross-tool work for free.

---

## Open follow-ups (for next time)

- [ ] Inventory which current `plugins/*/skills/…` should return to `.claude/skills/`.
- [ ] Fill the two MCP config snippets with real `anki-mcp` launch args.
- [ ] Decide on per-tool agent adapters (Claude `.claude/agents/` vs opencode
      `.opencode/agents/` frontmatter differences).
- [ ] Hooks: what (if anything) to reimplement as opencode JS/TS plugins vs leave
      Claude-only (mem-bank small/big bank, debug loggers).
- [ ] Re-check whether Claude Code has added `.agents/skills/` support since 2026-07-09 —
      if so, `.agents/skills/` becomes the cleaner neutral home.

---

## Sources

- Claude Code — Skills: https://code.claude.com/docs/en/skills
- Claude Code — Plugins: https://code.claude.com/docs/en/plugins
- Claude Code — Settings: https://code.claude.com/docs/en/settings
- opencode — Skills: https://opencode.ai/docs/skills/
- opencode — Plugins: https://opencode.ai/docs/plugins/
- opencode — Agents: https://opencode.ai/docs/agents/
- opencode — MCP servers: https://opencode.ai/docs/mcp-servers/
- Open standard: https://agentskills.io
