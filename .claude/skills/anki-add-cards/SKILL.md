---
name: anki-add-cards
description: Generate Anki cards for a deck and push to Anki
disable-model-invocation: false
---

Generate Anki cards for any deck and push them to Anki.

Card generation runs in an isolated subprocess with only compiled context — no CLAUDE.md, no memory, no rules.

## Resolve Deck

Parse `$ARGUMENTS`: the first word is the deck name, everything after is the card input.

Locate the deck directory by searching `decks/` for a subdirectory named `<deck>` at any depth. If not found or no deck name given: report "Deck '<deck>' not found. Available decks: [list all leaf deck dirs]" and stop.

The compiled context file is `<deck-dir>/<deck>.compiled.md`.


## Get Input

If input (the part after the deck name) is non-empty, use it as the card input.
If input is already in a form of generated cards - jump to the Preview step.
If empty, ask: "What would you like to turn into cards?"

## Build Generation Context

Fetch the live model registry from Anki:
1. Call `mcp__anki__model_names` to get all note type names.
2. For each model name, call `mcp__anki__model_field_names` to get its fields.
3. For each model name, call `mcp__anki__model_templates` to get its Front/Back HTML.

From each template, derive a one-line **render gloss** for any field whose role is
not obvious from its name — the generator routes content correctly only if it knows
how a field renders. In particular, a field wrapped in a `<details>` collapsible block
is optional, progressive-disclosure content:
- wrapped on the **Front** → a reveal-on-demand scaffold (a hint), shown before the answer
- wrapped on the **Back** (after `<hr id=answer>`) → post-recall context, read after flipping

Build an **Available Note Types** section. List each model's fields, then any render
glosses indented beneath:

```
## Available Note Types

Use one of these existing models when creating cards. If none fits well, you may propose
a new model — provide a name and field list and the orchestrator will handle creation.

- **Basic**: Front, Back
- **Cloze**: Text, Back Extra
- **<model n>**: Front, Back, Hint, Interesting Facts
    <field 1> → collapsible reveal-on-demand scaffold on the front (shown before the answer)
    <field 2> → collapsible post-recall context on the back (read after flipping)
    <field n> → metadata, not visible
- **<other model>**: <field1>, <field2>, ...
```

The glosses are derived from the live template, not hard-coded — a deck with a
different collapsible-field layout gets glosses describing *its* template.

Read `<deck-dir>/<deck>.compiled.md`. Invoke the `/generate-cards` skill with all content inlined as arguments:
- The compiled context file content
- Blank line
- The Available Note Types section (markdown, built above)
- Blank line
- The card input

Capture the skill output. If empty or failed: report the error and stop.

## Preview

Display the generated cards to the user using the numbered format as compiled context specifies.

Before displaying, scan the generated batch and attach an inline `⚠` flag next to any
card matching a known quality leak. These are signals for the human to catch — never
auto-rejections; the user still decides:
- a production card and a cloze card hide the **same** form (redundant pair)
- one card stacks more than one new difficulty, or has no plausible conversational anchor
- an idiom/expression front is written in Spanish rather than a situational L1 cue
- Spain-register lexicon appears as the target form (e.g. *vale*, *coger* for transport, *patatas*)
- a `Back` runs long with the form not on its first line

## User Confirmation

Ask the user: **"Apply these N change(s)? [yes / no]"**

If the user says no or wants to skip individual cards, respect that.

## Push to Anki

Parse each card block from the generator output. Each block has this format:

```
[model: <ModelName>] card
<FieldName>: <value>
<FieldName>: <value>
Tags: <tag1> <tag2> <tag3>
```

For each unique model name referenced:
- Check whether it exists in the registry fetched in Build Generation Context.
- If it does not exist:
  - Collect the field names declared in the cards using that model.
  - Check whether any field value contains `{{c1::}}` syntax — if so, pass `is_cloze=True`.
  - Show the user: **"New note type needed: '<ModelName>' with fields [<f1>, <f2>, ...]. Create it? [yes / no]"**
  - On yes: call `mcp__anki__create_model` with the model name, fields, and `is_cloze`.
  - On no: skip all cards using that model, report them as skipped.

Call `mcp__anki__add_notes` with the notes list.

### Idiom-batch auto-suspend

Idioms generated ahead of real exposure are low-ROI and interfere with each other in
review. Cap how many enter the active queue at once:

- Among the just-added notes, identify idiom cards — those whose `Tags` include
  `vocab::idiom` or `vocab::expression`.
- If **more than 3** idiom cards were added in this batch: keep the first 3 (input
  order) active, and suspend the rest. Resolve their card IDs via
  `mcp__anki__notes_info` (the `cards` field) and call `mcp__anki__suspend_cards`.
- Never suspend non-idiom cards.

The surplus is preserved, not discarded — unsuspend each one reactively as you meet it
in real context.

## Report

```
Added X card(s) to <deck>.
  ✓ [first-field snippet]
  ⚠ [first-field snippet] — skipped (duplicate / user skipped / model creation declined)
  ⏸ [first-field snippet] — suspended (idiom batch > 3; unsuspend as you meet it in context)
```
