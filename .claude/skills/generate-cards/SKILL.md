---
name: generate-cards
description: Generate Anki cards from a compiled deck context and user input. Internal skill — invoked by the anki-add-cards pipeline step only.
context: fork
disable-model-invocation: false
user-invocable: false
---

!`cat $(printf '%s' '$ARGUMENTS' | head -1)`

$ARGUMENTS

The first line above is the context file path (already loaded). The Available Note Types section and card input follow it.

Output ONLY the cards in the exact format specified. No preamble, no commentary, no explanation.
