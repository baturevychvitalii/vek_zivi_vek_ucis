# Leak 6 Migration — Interesting Facts Field

## Status
- [x] `Interesting Facts` field added to Production note type (appended after Hint)
- [x] Back template updated — collapsible block renders when field is non-empty:
  `{{#Interesting Facts}}<details><summary>▶ interesting facts</summary><div class="interesting-facts">{{Interesting Facts}}</div></details>{{/Interesting Facts}}`
- [x] Cards migrated (phase 2) ✓ complete

## What to migrate

Move content from `Back` → `Interesting Facts` when the back contains **anything after the Spanish form** that is:
- Etymology or word-origin notes
- Grammar explanations ("In Spanish, X works by...")
- Regional/register notes ("In Argentina...", "In Spain...")
- Cultural context
- Long secondary example sentences that aren't the core form

**Keep in `Back`:** the Spanish form (line 1) + one tight example sentence max.

**Rule of thumb:** if the Back has a `<br>` and the content after it is explanatory rather than the form itself, it belongs in Interesting Facts.

## How to run phase 2 (batches of 20)

1. Take the next 20 note IDs from the pending list below
2. Call `notes_info(note_ids=[...20 ids...])`
3. For each note: inspect `Back` — if it has `<br>` with explanatory content after it, split:
   - `Back` = form + tight example only
   - `Interesting Facts` = everything else (preserve HTML formatting)
4. Call `update_note_fields` for each changed note
5. Cross off the processed IDs, update progress below

## Progress

Batches done: 13 / 13  ✓ complete

| Batch | Notes split | Notes clean |
|---|---|---|
| 1 (1–20) | 3 | 17 |
| 2 (21–40) | 8 | 12 |
| 3 (41–60) | 9 | 11 |
| 4 (61–80) | 3 | 17 |
| 5 (81–100) | 1 | 19 |
| 6 (101–120) | 2 | 18 |
| 7 (121–140) | 4 | 16 |
| 8 (141–160) | 7 | 13 |
| 9 (161–180) | 14 | 6 |
| 10 (181–200) | 12 | 8 |
| 11 (201–220) | 20 | 0 |
| 12 (221–240) | 13 | 7 |
| 13 (241–244) | 0 | 4 |

## All notes processed ✓

~~Batches 10–13~~ ✓ done
