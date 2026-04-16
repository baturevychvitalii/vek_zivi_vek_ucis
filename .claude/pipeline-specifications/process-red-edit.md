# Pipeline: process-red-edit

## Steps

1. skill:anki-sync [mandatory]
   Why: ensure local Anki state is current before reading or modifying any cards
   On failure: stop — do not proceed with stale local state

2. skill:anki-backup-deck <deck> [mandatory]
   Why: snapshot before any writes; provides rollback point
   On failure: stop — do not proceed without a backup

3. skill:anki-process-red-edit <deck> [mandatory]
   Why: the actual red-flag processing and in-place edits
   On failure: stop and report

4. skill:anki-sync [optional]
   Why: push edited cards to AnkiWeb immediately
   On failure: notify user and stop, but edited cards are already saved locally

## Error handling rules
- mandatory step fails → notify user with the step name and error, stop immediately
- optional step fails → notify user with the step name and error, ask whether to continue
- never silently swallow failures
