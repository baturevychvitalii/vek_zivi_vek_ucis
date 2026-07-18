# Creative Usages — AI × Anki

Ideas for what becomes possible when an AI can reason over a full deck.
Organized by theme. Rough, unordered — to be refined over time.

---

## Vocabulary & Knowledge Mapping

- **"What is my vocabulary?"** — AI reasons on mature/young/new card breakdown to give an estimated word count and sample
- **Projected vocabulary** — given current learning rate, estimate vocabulary in 6 months / 1 year
- **Frequency-band gaps** — map your cards against a word frequency list (top 5000 Spanish) and show which bands have coverage gaps
- **Grammar structure audit** — "Do I have enough cards covering the subjunctive?" — AI analyzes grammatical structures present across the deck
- **Phoneme coverage** — check whether key sounds (e.g. rioplatense aspiration, yeísmo rehilado) appear across enough cards to be reinforced
- **Semantic duplicate detection** — find cards that teach the same concept in different words (not exact duplicates, but semantically equivalent)

---

## Difficulty Evolution & Card Lifecycle

- **Flip easy fronts** — on A1/A2-tagged cards with high interval, replace the English front with a Spanish prompt (monolingual progression)
- **Auto-promote tags** — a card tagged A2 that has been reviewed 50+ times with high ease → auto-retag B1
- **Switch to monolingual definitions** — as intervals grow past a threshold, replace English gloss with a Spanish-only definition
- **Retire deeply learned cards** — move cards with 180-day+ intervals to a "burial" deck to reduce daily load
- **Cloze upgrade** — auto-convert Basic cards to Cloze format based on content analysis

---

## Media Enrichment

- **Add animal images** — for all cards with animal names, fetch an image from Wikipedia and embed it
- **Add phonetic audio** — generate TTS audio in the target dialect (Rioplatense, Castilian) for cards missing audio
- **Add IPA transcription** — for any card without a phonetic field, compute and add IPA
- **Add example sentences** — pull a corpus example sentence and append to the back field
- **Add cultural context** — flag and annotate words with strong regional or cultural meaning
- **Add pronunciation comparison** — for words that differ between Rioplatense and Castilian, add a note

---

## Targeted Batch Operations

- **Add audio for specific phonological criteria** — "add audio to all cards with rioplatense yeísmo rehilado" — AI filters by phonological property, then TTS generates
- **Tag inference** — given card content, suggest or auto-apply missing tags (grammar category, frequency band, topic cluster)
- **False cognate warnings** — add a warning note to cards where the Spanish word is a false friend with English
- **Idiom detection** — flag phrases that should be treated as idioms, not literal translations, and add a note
- **Grammar cluster analysis** — find all cards sharing a pattern you're struggling with (e.g., ser vs estar), then generate a linking "meta-card"

---

## Study Intelligence & Recommendations

- **Study session warm-up** — before reviewing, surface the 5 cards you historically struggle with most in this deck
- **Time-boxed plan** — "I have 20 minutes" → prioritize overdue, then new cards from weakest tag cluster
- **Post-session insight** — which tags had worst retention today → generate a targeted review suggestion
- **Identify redesign candidates** — cards answered wrong disproportionately often → flag for content rework, not just more review
- **Knowledge gap inference** — recurring wrong answers on a card → check whether prerequisite cards exist, suggest creating them
- **Retention-based study order** — reorder a custom study session by predicted forgetting probability

---

## Cross-Domain & Integrations

- **E-reader → cards** — parse a Kindle/Kobo highlight export, find unknown words, create cards for them
- **"Generate a paragraph I can read"** — compose a passage using only words at or below your current interval threshold
- **Simulate a conversation** — produce a dialogue using only your known vocabulary
- **Cross-language transfer** — when a Spanish card is mastered, offer to clone it into a Portuguese deck
- **Reading level checker** — paste in a text, get an estimate of what % of the vocabulary you currently know

---

## Maintenance & Hygiene

- **Find broken cards** — detect cards with missing media, broken HTML, or empty fields
- **Consistency audit** — "all verb cards should have infinitive on front" — flag violations
- **Orphaned tag cleanup** — already possible with `clear_unused_tags`, but AI can also suggest tag consolidations
- **Near-duplicate review** — semantic similarity sweep across the whole deck to find overlapping cards
