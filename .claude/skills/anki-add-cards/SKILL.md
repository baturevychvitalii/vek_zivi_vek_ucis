---
name: anki-add-cards
description: Generate Anki cards for a deck and push to Anki
disable-model-invocation: true
---

Generate Anki cards for any deck and push them to Anki.

Card generation runs in an isolated subprocess with only compiled context — no CLAUDE.md, no memory, no rules.

## Step 1 — Resolve Deck

Parse `$ARGUMENTS`: the first word is the deck name, everything after is the card input.

If no deck name given: list subdirectories of `decks/` and ask the user which deck to use.

Read `decks/<deck>/compiled.md`. Extract from the **Deck Config** block: `deckName`.

If the directory `decks/<deck>/` does not exist: report "Deck '<deck>' not found. Available decks: [list]" and stop.

## Step 2 — Get Input

If input (the part after the deck name) is non-empty, use it as the card input.
If input is already in a form of generated cards - jump to ## Preview step.
If empty, ask: "What would you like to turn into cards?"

## Step 3 — Build Generation Context

Fetch the live model registry from Anki:
1. Call `mcp__anki__model_names` to get all note type names.
2. For each model name, call `mcp__anki__model_field_names` to get its fields.

Build an **Available Note Types** section:

```
## Available Note Types

Use one of these existing models when creating cards. If none fits well, you may propose
a new model — provide a name and field list and the orchestrator will handle creation.

- **Basic**: Front, Back
- **Cloze**: Text, Back Extra
- **<other model>**: <field1>, <field2>, ...
```

Read `decks/<deck>/compiled.md`. Read `/tmp/card-generation-context.md` (ignore contents — satisfies read-first constraint). Write the compiled context followed by the Available Note Types section to `/tmp/card-generation-context.md`.

## Step 4 — Generate Cards (isolated subagent)

Invoke the `/generate-cards` skill with the card input as its arguments.

The skill runs in a forked subagent with no conversation history. It reads `/tmp/card-generation-context.md` as its system context and receives the card input as its prompt.

Capture the skill output — this is the generated card output.

If the skill fails or returns empty output: report the error and stop.

## Step 5 — Preview

Display the generated cards to the user using the numbered format as compiled context specifies.

## Step 6 — User Confirmation

Ask the user: **"Apply these N change(s)? [yes / no]"**

If the user says no or wants to skip individual cards, respect that.

## Step 7 — Push to Anki

Parse each card block from the generator output. Each block has this format:

```
[model: <ModelName>] card
<FieldName>: <value>
<FieldName>: <value>
Tags: <tag1> <tag2> <tag3>
```

For each unique model name referenced:
- Check whether it exists in the registry fetched in Step 3.
- If it does not exist:
  - Collect the field names declared in the cards using that model.
  - Check whether any field value contains `{{c1::}}` syntax — if so, pass `is_cloze=True`.
  - Show the user: **"New note type needed: '<ModelName>' with fields [<f1>, <f2>, ...]. Create it? [yes / no]"**
  - On yes: call `mcp__anki__create_model` with the model name, fields, and `is_cloze`.
  - On no: skip all cards using that model, report them as skipped.

Call `mcp__anki__add_notes` with the notes list.

## Step 8 — Report

```
Added X card(s) to <deckName>.
  ✓ [first-field snippet]
  ⚠ [first-field snippet] — skipped (duplicate / user skipped / model creation declined)
```
