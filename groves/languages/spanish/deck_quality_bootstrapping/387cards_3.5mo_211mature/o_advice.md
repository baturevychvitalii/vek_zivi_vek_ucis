# Plan — Bake the deck-quality findings back into generation & population

## Context

A deep audit of the Spanish deck (`analysis.md`, 387 cards, 3.5 mo) found and
fixed **6 efficiency leaks**. Fixing the existing deck is done. The open question:
**why did these leaks get generated in the first place, and what rule change stops
them recurring?** A profound analysis that changes nothing upstream is wasted.

Two upstream surfaces produce and populate cards:

1. **`decks/languages/spanish/rioplatense-anki.compiled.md`** — the *only* context
   the card generator sees. The add-cards skill runs generation "in an isolated
   subprocess with only compiled context — no CLAUDE.md, no memory, no rules."
   → Therefore **every content rule must live here.** This is the leverage point.
2. **`.claude/skills/anki-add-cards/SKILL.md`** — thin orchestration (resolve deck,
   fetch live model registry, invoke generator, preview, confirm, push). It cannot
   shape card *content*, but it owns Preview + Confirmation — the human catch-net.

Mapping each leak to the upstream gap that allowed it:

| Leak | What slipped through | Why the current rules allowed it |
|---|---|---|
| 1 Production+cloze duplication | cloze hiding the same form the production card forces | Cloze section says "don't force cloze" but never says "don't duplicate the production card's forced form"; Input+Design rules actively push "always make a production card" + "as many cards as warranted" |
| 2 Leeches (over-complex / no anchor) | cards stacking tense+pronoun+connector; abstract constructed sentences | No "one difficulty per card" rule; no "prefer conversational anchor"; **`Hint` field exists on the Production model but is documented nowhere** |
| 3 Idiom L2→L2 front | Spanish-paraphrase → Spanish-idiom fronts | Nothing forbids a Spanish front for idioms |
| 4 Idiom concentration | 26-idiom batch, look-alike interference | No guidance on batching / interference / reactive intake |
| 5 European Spanish | vale, coger, patatas, ostras, majo, chulo | Dialect rule is passive ("if Spain differs, add a note") — never says *reject* Spain-register lexicon |
| 6 Back verbosity | key form buried under etymology | No "form on line 1" rule; **`Interesting Facts` field exists but is documented nowhere** |

**Cross-cutting root cause:** the leak-fix work added two fields to the `Production`
note type — `Hint` and `Interesting Facts` — but `compiled.md` documents neither.
The generator is handed field *names* live (skill Step 3) with zero semantics, so it
can't route content into them. Documenting field routing is the single
highest-value change; it directly addresses Leaks 1, 2, and 6 at once.

---

## Part 1 — `rioplatense-anki.compiled.md` (the generator's only input)

> **Execution constraint (avoid self-inflicted Leak 6):** integrate each rule below
> *into the existing terse section* (Cloze, Dialect, Card Design, Quality Check) —
> do **not** append six new prose blocks. The compiled file is the generator's
> entire world; keep signal density high. The text below states intent, not
> verbatim wording to paste.

> **Affirmative levers (the "increase chances of something good" half):** the
> analysis says Anki earns its keep on **collocations / fixed chunks** and **EN→ES
> production priming**. State these as a positive generation *preference*, not only
> as "avoid X" — e.g. prefer carding a high-frequency collocation as one chunk over
> isolated single words. Field routing (1A) is itself the main positive lever:
> richer encoding via `Interesting Facts` without polluting the tested form.

### 1A. Document `Production` field routing  *(Leaks 1, 2, 6 — keystone change)*
Add a field-routing block to the Production card type / Output Format:
- **Front** — L1 (English) cue. For idioms/expressions: a *situational* cue, never a Spanish paraphrase.
- **Back** — **first line = the exact Spanish form to produce.** Then at most one natural example. Nothing else.
- **Hint** — *optional* scaffold for genuinely hard production. **It names the *category* of difficulty, never the form** (e.g. "irregular preterite", "pronoun attaches to infinitive", "voseo", "por vs para" — *not* the stem or answer itself). Use it to **rescue** a would-be leech without recreating Leak 1's give-away-the-answer problem.
- **Interesting Facts** — *optional*, rendered collapsed / post-recall. Etymology, the Spanish definition, related vocab from source, dialect notes. "Read after you flip," never "tested."
- Rule: **never put on Back what belongs in Interesting Facts. The form leads.**

### 1B. Anti-duplication test for cloze  *(Leak 1)*
Revise the Cloze section. Add the explicit gate:
> A cloze must isolate a difficulty the production card does **not** already force.
> Before adding a cloze beside a production card for the same item: *does the
> production Back already lead with the exact form this cloze would hide?* If yes →
> redundant, do not generate. Generate the cloze only for a **different** buried
> difficulty (a preposition mid-sentence, a pronoun position, an irregular form
> inside a longer clause).

### 1C. One-difficulty + real-anchor rule  *(Leak 2)*
Add to Card Design Rules:
> One card, one new difficulty. Don't stack unfamiliar elements (new tense + pronoun
> attachment + connector) in one card — split them, or scaffold with `Hint`. Prefer
> sentences that plausibly occur in real Rioplatense conversation over abstract /
> constructed showcase sentences; a card with no situational anchor gets failed and
> only re-learned in real use.

### 1D. Idiom / expression front format  *(Leak 3)*
Add to the Production / idiom guidance:
> Idioms & fixed expressions: the front is a **situational English cue** describing
> when you'd reach for the expression — never a Spanish definition or paraphrase
> (that trains a skill that never fires in speech). Spanish definition, etymology,
> related vocab → `Interesting Facts`. (Basis: `production_vs_comprehension.md`.)

**Precedence:** an explicit user `front | back` directive (take 1:1, don't change)
wins over this auto-format rule — the situational-front rule applies only when the
generator is choosing the front itself.

### 1E. Idiom batching / interference  *(Leak 4)*
Add a note near the idiom guidance:
> Idioms are low-ROI when generated ahead of real exposure — prefer reactive intake
> (card an idiom after it's been heard/read in context). For a batch of similar
> idioms, flag look-alike interference (e.g. *irse de las manos / irse a las manos /
> estar hasta las manos*) and recommend spacing rather than one block.

### 1F. Reject Spain-register lexicon  *(Leak 5)*
Strengthen the Dialect section from passive to active:
> Actively reject Spain-register lexicon as the target form. Replace, don't drill:
> `vale→dale`, `coger`(transport)`→tomar`, `patatas→papas`, `ostras→uy/uh`,
> `majo/chulo/cuqui→` Argentine equivalent (`copado/lindo/che`). If the user's input
> *is* a Spain-register word, make the Rioplatense equivalent the card's answer and
> note the Spain form in `Interesting Facts` — don't drill the Spain form.

Strengthen the Quality Check line to cover lexicon, not just grammar:
> "Would a porteño actually say this — grammar **and** lexicon?"

---

## Part 2 — `anki-add-cards/SKILL.md` (the human catch-net)

The skill can't shape content (generation is isolated). Its leverage is the
preview/confirm gates — a place to catch what still slips through.

### 2A. Preview-time quality gate (Step 4)
Before displaying generated cards, have the orchestrator run a short checklist over
them and surface inline flags next to the preview:
- production+cloze pair hiding the same form (Leak 1)
- card stacking >1 new difficulty, or no conversational anchor (Leak 2)
- idiom front written in Spanish (Leak 3)
- idiom-batch size + look-alike interference (Leak 4)
- Spain-register lexicon (Leak 5)
- Back >~2 lines with the form not on line 1 (Leak 6)

These are *flags for the human*, not auto-rejections — the human stays in the loop.

### 2B. Idiom-batch confirmation nudge (Step 5)
If the batch contains several idiom cards, add a one-line warning at confirmation
suggesting reactive intake / spacing (reinforces 1E at the point of decision).

---

## Division of labour (the honest summary)

- The generator sees **only `compiled.md`** → all *content* rules (1A–1F) must live
  there. This is where ~80% of leak-prevention belongs.
- The skill (2A–2B) is a **human review net** for what the rules miss — it can flag,
  not fix.
- Note: 1A–1D are general L1→L2 production principles that would ideally live in the
  shared `generate-cards` generator skill so every deck benefits. That skill is
  out of scope per the "don't read other skills" constraint — flagged for later.

---

## Verification

1. **Dry-run generation** with deliberately leak-prone input, e.g.
   `/anki-add-cards spanish "I was tired so I went home" "vale" "Hay gato encerrado"`
   and confirm in the preview:
   - no redundant production+cloze pair (1B)
   - `vale` produced as `dale`, Spain form in Interesting Facts (1F)
   - the idiom gets a situational English front, not a Spanish paraphrase (1D)
   - the tired/home sentence is split or carries a Hint, not a single stacked card (1C)
   - the preview shows the new quality-gate flags (2A)
2. **Field routing spot-check**: a generated card puts the exact form on Back line 1
   and pushes etymology to Interesting Facts (1A).
3. No regression: a plain vocabulary input ("the table") still yields one clean
   production card with no spurious cloze or flags.
