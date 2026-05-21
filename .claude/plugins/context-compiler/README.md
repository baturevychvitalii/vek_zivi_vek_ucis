# context-compiler plugin

General-purpose preprocessor for resolving `#include` directives in markdown files, plus skills for compiling layered context into a single flat document.

## Subsystem files

| File | Role |
|---|---|
| `preprocess.py` | CLI preprocessor — resolves `#include` chains |
| `skills/compile/` | LLM merge step — collapses depolymorphized layers into one readable doc |
| `skills/compile-deck-context/` | Orchestrator — freshness check → preprocess → compile |

## `#include` directive

```
#include <path>
```

- Must be the entire line, no leading whitespace.
- Path resolves relative to the **including file** when it starts with `.` or `..`; otherwise relative to the **project root**.

**Always put `#include` at the top of the file** — this preserves general → specific order in the output, which the compile merge step depends on.

## Deduplication and cycle detection

Each file is included at most once (keyed by canonical resolved path). Circular includes are an error.

## CLI

```bash
# Write to file
python3 .claude/plugins/context-compiler/preprocess.py <entry-file> <output-file>

# Print to stdout
python3 .claude/plugins/context-compiler/preprocess.py <entry-file>
```

## Skills

| Command | What it does |
|---|---|
| `/context-compiler:compile <depolymorphized.md>` | LLM merge into `compiled.md` (fork context) |
| `/context-compiler:compile-deck-context <deck>` | Full pipeline: preprocess → compile |

## Notes

`scripts/compiled-is-fresh.py` still uses folder-hierarchy traversal for the freshness check. Works for all current use cases where includes stay within ancestor directories. Update it if cross-directory includes are ever introduced.
