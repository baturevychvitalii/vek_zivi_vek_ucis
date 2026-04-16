---
description: Enforce parent-first context loading for all context.md files
globs:
  - "**/context.md"
---
When reading any `context.md`, first walk up from its directory toward the project root and read every `context.md` found in ancestor directories (root-first, then downward). Only then read the target file. This ensures inherited context is always loaded before specialized context.
