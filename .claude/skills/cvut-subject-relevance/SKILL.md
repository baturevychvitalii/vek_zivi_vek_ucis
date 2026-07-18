---
name: cvut-subject-relevance
description: Score CVUT subjects for outreach relevance in parallel Haiku forks, each with clean context, and merge the shortlist. Phase 2 of the CVUT per-subject outreach.
disable-model-invocation: false
---

Score a large CVUT subject roster for outreach relevance without loading the subjects into
the orchestrator's context. Work is fanned out to **cold-start Haiku subagents**, one per
batch of ~10 subjects; each fetches descriptions, applies the shared rubric in
`fork-task.md`, and writes its own output file. The orchestrator only splits, spawns, and
merges — it never ingests the descriptions.

## Inputs and layout

- Roster: `modes/world-adoption/cvut-outreach/subjects_with_people.csv` (rows that have a person).
- Fork inputs: `modes/world-adoption/cvut-outreach/phase2/batches/batch_NN.json`
- Fork outputs: `modes/world-adoption/cvut-outreach/phase2/out/batch_NN.jsonl`
- Deliverables: `modes/world-adoption/cvut-outreach/phase2/{all_scored,relevant_subjects}.csv`

## Design invariants (do not violate)

- **Clean context per fork** — spawn `subagent_type: general-purpose` with **`model: haiku`**.
  Never use `subagent_type: fork` (it inherits the parent's context and model — the opposite
  of what we want).
- **Thin orchestrator** — forks read their batch file and write their output file themselves.
  Do NOT inline subject rows or read fork outputs back into your context. Relay only the thin
  summaries. This is what keeps the run affordable and the context clean.
- **Unique per-batch filenames** — never a shared fixed-name file (parallel-safe, resumable).

## Generate batches

```bash
python3 .claude/skills/cvut-subject-relevance/make_batches.py --input modes/world-adoption/cvut-outreach/subjects_with_people.csv --batch-dir modes/world-adoption/cvut-outreach/phase2/batches --out-dir modes/world-adoption/cvut-outreach/phase2/out
```

It prints the total batch count and the **pending** batch numbers (those without a complete
output). Spawn forks only for pending batches — this is the resume mechanism across sessions.

## Spawn a wave

For each pending batch NN, spawn one background agent. Keep the spawn prompt tiny — the
context lives in `fork-task.md`, not in your prompt:

> Read and follow `.claude/skills/cvut-subject-relevance/fork-task.md`. Your batch is
> `modes/world-adoption/cvut-outreach/phase2/batches/batch_NN.json`. Write your JSONL output
> to `modes/world-adoption/cvut-outreach/phase2/out/batch_NN.jsonl`. Reply with only the thin
> summary that file describes.

Run waves of a handful of batches at a time (not all at once). When a fork finishes, note its
thin summary only. Re-running `make_batches.py` reprints what is still pending.

## Merge

Once pending is empty (or whenever you want a partial roll-up):

```bash
python3 .claude/skills/cvut-subject-relevance/merge.py --out-dir modes/world-adoption/cvut-outreach/phase2/out --batch-dir modes/world-adoption/cvut-outreach/phase2/batches --dest modes/world-adoption/cvut-outreach/phase2
```

`relevant_subjects.csv` (verdict relevant + borderline) is the outreach shortlist handed to
later phases (email lookup via the guarantor's usermap profile, drafting under the outbound
contract). `all_scored.csv` keeps the full audit trail.
