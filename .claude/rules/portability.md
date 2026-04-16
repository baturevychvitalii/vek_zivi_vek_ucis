# Portability: Bash Path Format

Always use project-root-relative paths in bash commands — never absolute paths.

**Wrong:**
```bash
python3 /home/papa/Documents/ideas/vek_zivi_vek_ucis/.claude/anki.py '...'
```

**Right:**
```bash
python3 .claude/anki.py '...'
```

**Why:** The permission system matches the literal command string. An absolute path
will never match a whitelist entry written with a relative path — causing an unexpected
user prompt. Relative paths also keep skills portable across machines and users.

**At execution time:** When running a command taken from a skill spec, use it verbatim.
Do not expand, resolve, or rewrite paths.
