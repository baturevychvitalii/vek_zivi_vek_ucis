# Pipeline: add-cards

## Steps

1. compile-deck-context <deck> [mandatory] — fire as background fork
   Why: no dependency on sync or backup; starts immediately so compilation
   overlaps with the I/O-bound steps below
   On failure: stop — cannot generate without compiled context

2. anki-sync [mandatory]
   Why: ensure local Anki state is current before modifying it
   On failure: stop — do not proceed with stale local state

3. anki-backup-deck <deck> [mandatory]
   Why: snapshot before any writes; provides rollback point
   On failure: stop — do not proceed without a backup

4. await compile-deck-context result [mandatory]
   Why: compiled context must be ready before generation begins
   On failure: stop — report error from the background fork

5. anki-add-cards <deck> <input> [mandatory]
   Why: the actual card generation (isolated subprocess) and injection
   On failure: stop and report

6. anki-sync [mandatory]
   Why: push changes to anki
   On failure: stop and report

## Error handling rules
- mandatory step fails → notify user with the step name and error, stop immediately
- optional step fails → notify user with the step name and error, ask whether to continue
- never silently swallow failures
