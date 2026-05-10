# Health Agent Memory Index

- [Hooks create analysis friction](pattern_hooks_create_analysis_friction.md) — subagent analysis requires permission prompts for transcript parsing
- [Health hooks should exclude infrastructure edits](pattern_hooks_in_health_findings.md) — findings report hook file edits as friction; filter them out
- [anki-sync skill is clean](anki_sync_skill_runs_cleanly.md) — anki-sync executes without friction; issues are in hook infrastructure
- [add-cards pipeline clean run](add_cards_pipeline_clean_run.md) — full pipeline execution with background compilation, user approval, and sync; no errors
- [Debug sessions tend toward bash chaining](pattern_debug_bash_chaining.md) — troubleshooting often produces &&, ||, | violations; common in 1-2 minute clusters
