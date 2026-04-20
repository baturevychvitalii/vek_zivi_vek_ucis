# Pipeline: add-cards

## Steps

1. anki-sync [mandatory]
   Why: ensure local Anki state is current before modifying it
   On failure: stop — do not proceed with stale local state

2. anki-backup-deck <deck> [mandatory]
   Why: snapshot before any writes; provides rollback point
   On failure: stop — do not proceed without a backup

3. compile-deck-context <deck> [mandatory]
   Why: flatten the context-inheritance chain into a single compiled file before generation
   On failure: stop — cannot generate without compiled context

4. anki-add-cards <deck> <input> [mandatory]
   Why: the actual card generation (isolated subprocess) and injection
   On failure: stop and report

5. /anki-sync [mandatory]
   Why: push changes to anki
   On failure: stop and report

## Error handling rules
- mandatory step fails → notify user with the step name and error, stop immediately
- optional step fails → notify user with the step name and error, ask whether to continue
- never silently swallow failures
