Graduate the current branch's `active-context.md` into a durable entry under `.claude/meta/architect/why/`.

Run the script:

```bash
python3 .claude/scripts/mem-bank-graduate.py --source .claude/meta/state/active-context.md --archive-dir .claude/meta/architect/why --backup-dir .claude/meta/state/.archived
```

The script reads `active-context.md`, asks Claude (Sonnet) for a topical kebab-case filename and a 4–8-sentence summary, writes a new file under `why/` containing the summary plus the verbatim active-context, copies the original to the backup directory, and deletes the source. On a clean no-op (missing or empty source) it exits 0 without writing anything.
