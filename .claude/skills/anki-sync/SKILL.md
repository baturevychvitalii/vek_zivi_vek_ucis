---
name: anki-sync
description: Trigger an Anki sync with AnkiWeb via AnkiConnect
disable-model-invocation: true
---

Trigger an Anki sync with AnkiWeb via AnkiConnect.

## Step 1 — Trigger Sync

Run:

```bash
python3 .claude/anki.py '{"action": "sync"}'
```

## Step 2 — Report

Parse the JSON output:
- If `result["error"]` is null: report "Anki sync triggered successfully."
- If `result["error"]` is non-null: report the error and stop.

Note: AnkiConnect's `sync` action fires the sync and returns immediately — it does not wait for sync completion. The actual sync runs in the background inside Anki. This is expected behavior.
