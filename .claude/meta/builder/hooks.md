# Hook Authoring Guide

Read this before creating or modifying any hook in `.claude/hooks/`.

## Log Output Format

All log lines must be tab-delimited:

```
{timestamp}\t{operation}\t{detail}\n
```

Fields are separated by literal `\t` (tab characters), not spaces. One line per event.

Example from existing hooks:

```
2026-04-16T13:54:57.627875	REQUEST	architect mode on
2026-04-16T13:55:01.526927	[notify-meta-read]	architect/context.md
```
