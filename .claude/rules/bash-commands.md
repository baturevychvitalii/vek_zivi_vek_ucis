# Bash Commands: One Command Per Block

Each bash block must contain exactly one command. Never chain with `&&`, `;`, or `|`.

**Wrong:**
```bash
mkdir -p /tmp/anki && python3 .claude/anki.py '...'
```

**Right:**
```bash
mkdir -p /tmp/anki
```
```bash
python3 .claude/anki.py '...'
```

**Why:** The permission system matches the full command string against whitelist rules.
Chained commands never match individual whitelist entries — they always fall through to
a user prompt, even when each individual command is whitelisted.

**At execution time:** When running commands from a skill spec, run each bash block as a
separate invocation. Do not combine, chain, or rewrite them — even as a convenience.
