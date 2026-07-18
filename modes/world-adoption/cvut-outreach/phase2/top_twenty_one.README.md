# top_twenty_one.csv — how this list was made

**21 distinct people to reach out to**, each anchored to the single best subject
to reach them through. One row per person, ranked. Names live only in the
untracked local `top_twenty_one.csv` — this doc describes the method, not the
individuals.

## Method (interim — this is the lossy step)

This is a **manual pass over 112 distinct guarantors** in `relevant_subjects.csv`,
and it is exactly the loss-prone big-data step that **diotima#14** exists to
replace with a batched LLM-comparator ranking helper. Read the order as a
considered human judgement, not a measured ranking — correct it freely.

Selection rules applied:

1. **Dedup by person, not by subject.** You email a person once (outbound
   contract: one mail, one owner, one angle). Many people guarantee several
   shortlisted subjects — the top two guarantors own 8 and 15 rows respectively.
   Each person appears once here, at their strongest door.
2. **Anchor = the single best subject** to open with, chosen for outreach angle,
   not for the subject's own score.
3. **Ranked by adoption strategy, not raw topical relevance** — following
   `../../drafts/cvut-per-subject-outreach.md`. Lead with the smallest ask
   (the #1 target / team project), then strongest research cards, then track
   coverage.
4. **Guarantor ≠ research supervisor.** A guarantor owns a syllabus; they may
   have neither capacity nor research interest. The #1 target is the exception —
   sourcing student projects *is* their job, which is why they lead.

## Consistency check against the draft

All six targets named in the outreach draft appear here (ranks #1, #2, #3, #4,
#9, and #21 — the last deliberately last, the draft calls it the weakest fit).
The rest fill track coverage, including on-mission signals the draft predates:
LLM / Transformers, personalized ML for education, and didactics of informatics.

## Before sending

- **Only the top three (#1–#3) were verified against live pages** in the draft.
  The others came from phase-2 scoring — reconfirm name + role on the
  `detail_url` before any envelope goes out (the draft warns phase-2 summaries
  have invented URLs before).
- Emails still need resolving from each `guarantor_profile` (usermap) — that is
  the phase-2 email-resolution step, not done here.

## Columns

`rank, guarantor, anchor_code, anchor_name, department, track, angle, verdict,
guarantor_profile, detail_url`
