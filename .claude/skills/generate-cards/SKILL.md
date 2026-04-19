---
name: generate-cards
description: Generate Anki cards from a compiled deck context and user input. Internal skill — invoked by the anki-add-cards pipeline step only.
context: fork
disable-model-invocation: true
user-invocable: false
---

!`cat /tmp/card-generation-context.md`

$ARGUMENTS

Output ONLY the cards in the exact format specified. No preamble, no commentary, no explanation.
