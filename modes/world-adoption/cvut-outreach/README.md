# CVUT per-subject outreach — data collection

Deterministic pipeline that turns the CVUT *bílá kniha* (bilakniha.cvut.cz)
faculty subject listing into a CSV roster, so a later session can go through
subjects in batches, judge relatedness to the project, and reach out to the
people behind the related ones.

Two phases, by design:

- **Phase 1 (this folder): the roster.** Code, name, **detail-page link**,
  guarantor + their usermap profile, co-teachers, department. No descriptions.
- **Phase 2 (a separate session): descriptions, relatedness, emails.** Fetch
  each `detail_url` for the subject description, score relatedness in batches,
  resolve the guarantor's email from their usermap profile, run the outreach loop.

## Scope

FIT (faculty **F8**) only — 846 subjects. Chosen deliberately: the flat page
`f8-predmety.html` is a **complete superset** of all six department pages *and*
the faculty electives page (verified 2026-07-17: 0 codes in `katedra18101…18106`
or `f8-volitelne` that aren't already in the flat page). So one page + one parser
covers the whole faculty; the fancier two-semester department/elective layouts
are redundant and are not parsed.

The school-wide electives page `volitelnepredmety.html` (~6,700 subjects across
all CVUT faculties) was **excluded** — it is ~9× the batch-review load. To
include it or extend to another faculty, the crawler is parameterized by
`--faculty` / `--page`; add the source and re-dedup.

## Run

```bash
python3 modes/world-adoption/cvut-outreach/scrape_subjects.py \
    --faculty FIT --page f8-predmety.html \
    -o modes/world-adoption/cvut-outreach/subjects.csv
```

Add `--from-file <cached.html>` to parse a local snapshot instead of fetching
(fully offline / reproducible).

## Uniqueness

Dedup is done **in Python**, keyed on the subject **code** (first-seen wins,
then sorted by code) — a plain `sort -u` on the CSV cannot dedup rows that
differ only in a `faculty`/`source` column, so the authoritative dedup lives in
the crawler. Verify the guarantee any time with:

```bash
tail -n +2 modes/world-adoption/cvut-outreach/subjects.csv | cut -d, -f1 | sort | uniq -d
```

Empty output = every code appears once. (Currently 846 rows, all unique.)

## Columns

`code, name, detail_url, guarantor, guarantor_profile, teachers, department,
faculty, language, completion, credits`

- `detail_url` — absolute link to the subject page (`…/predmetNNN.html`). The
  Phase-2 entry point for descriptions. **Mandatory column.**
- `guarantor` / `guarantor_profile` — the person marked Ⓖ (*garant*) and their
  usermap profile URL. Primary contact for outreach; distinct from co-teachers.
- `teachers` — all listed instructors, `; `-separated (includes the guarantor).
