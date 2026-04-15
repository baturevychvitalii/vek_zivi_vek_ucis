# Pipeline: add-cards

## Steps

1. anki-skill-sync [optional]
   Why: ensure local Anki state is current before modifying it
   On failure: warn user, ask whether to continue

2. anki-skill-backup-deck <deck> [mandatory]
   Why: snapshot before any writes; provides rollback point
   On failure: stop — do not proceed without a backup

3. anki-skill-add-cards <deck> <input> [mandatory]
   Why: the actual card generation and injection
   On failure: stop and report

## Error handling rules
- mandatory step fails → notify user with the step name and error, stop immediately
- optional step fails → notify user with the step name and error, ask whether to continue
- never silently swallow failures
