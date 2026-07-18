# Fork task — score CVUT subjects for outreach relevance

You are one worker in a parallel batch. You score CVUT (Czech Technical University)
subjects for how well their **guarantor** (the professor who owns the course) fits
as an outreach target for the project below. Work autonomously; write results to a
file; reply with only a thin summary.

## The project you are scoring relevance TO

An AI-assisted **learning conductor**: a context-engineered directory architecture with
deep **spaced-repetition (Anki)** integration that helps humans learn and boosts research.
Knowledge lives in per-domain "groves" that generate flashcards; the system finds learning
materials matched to skill level and aims at adaptive learning infrastructure.

The outreach pitch offers the project as a base for concrete university work:

- **Applied ML & context-engineering track** — improving the project architecture; making it
  cross-platform & LLM-provider-agnostic; packaging it into a single end-user deliverable.
- **Marketing & community track** — onboarding and tailoring the project to specific use
  cases: other faculties, other universities, and organizations with long/complex onboarding
  (e.g. banks, large legacy institutions).
- **Student daily use** — students using it directly in their studies; ed-tech at scale.

So a subject is a good target when its guarantor plausibly **cares about, would supervise a
thesis/team-project on, collaborates on, or would adopt** any of the above.

## Rubric — assign exactly one verdict per subject

- **relevant** — clear topical fit with a track above. Strong signals: team/semester
  **software projects**; **software & platform architecture**; **scalability / distributed
  systems**; **applied ML / context engineering / LLM / NLP**; software engineering broadly;
  **packaging / distribution / DevOps / deployment**; **databases & information systems**
  (data & knowledge representation); **HCI / ed-tech / e-learning / teaching of informatics**;
  **marketing / community / adoption / knowledge management & organizational onboarding**.
- **borderline** — a genuine but thin topical adjacency; note the uncertainty in one line.
- **irrelevant** — no topical fit. Includes: **pure mathematics (incl. linear algebra) even
  when the guarantor has an ML-leaning background** — topical fit must come from the *subject*,
  not the person; company **economics / finance**; low-level **hardware / circuits / control**;
  **embedded crypto / security hardware**; **language / PE** courses; and administrative or
  **fictional placeholder** "subjects" (e.g. a course named *Fiktivní předmět …*).

Calibration (from a validated pilot): `NI-DSP` (databases in practice) → relevant;
`NI-PIS` (enterprise information systems) → relevant; `BI-LA2` (linear algebra) → irrelevant;
`BIE-EPP` (company economics) → irrelevant; `AKCE` (fictional placeholder) → irrelevant.

## Procedure

Read your assigned batch JSON file (an array of subjects; path given in your spawn prompt).
For **each** subject:

1. `WebFetch` its `detail_url` (a `bilakniha.cvut.cz/cs/predmet…` page) and extract a 1–2
   sentence description (the *Anotace* / *Náplň*). If no usable description exists, note
   "no description available" and judge from the name + department.
2. Apply the rubric; write a one-line reason.

## Output

Write a **JSON Lines** file (one object per line, UTF-8) to the exact output path given in
your spawn prompt. Emit a line for **every** subject in the batch (all three verdicts) so the
result is auditable. Each line:

```json
{"code":"…","name":"…","department":"…","guarantor":"…","guarantor_profile":"…","detail_url":"…","verdict":"relevant|borderline|irrelevant","reason":"one line","description":"1–2 sentences you fetched"}
```

## Reply (keep it short — never paste descriptions or the file)

Only: total processed, count per verdict, and the codes marked relevant/borderline with their
one-line reason.
