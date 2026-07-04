Based on my analysis of the deck performance, the research on production vs. comprehension, and the existing generation framework, here are my recommendations to improve `spanish/rioplatense-anki.compiled.md` and the `anki-add-cards` skill.

The goal is to formalize the lessons learned from the deck audit, making the card generation process more efficient and less prone to creating ineffective "leech" cards.

---

### **Recommendations for `spanish/rioplatense-anki.compiled.md`**

These changes integrate the key findings from the analysis directly into the card generation logic.

**1. Explicitly Forbid Redundant Cloze Cards**

*   **Insight:** The analysis revealed that paired production and cloze cards for the same item are a major source of inefficiency (`Leak 1`). The cloze card is almost always easier and costs review time for little gain.
*   **Recommendation:** Add the following rule to the `Card Types > Cloze` section:
    > **Crucially, do NOT generate a cloze card if a Production card for the same input already tests the exact same knowledge.** A cloze card is only justified if it isolates a specific grammatical feature not forced by the EN->ES production card (e.g., a preposition, pronoun placement, or a specific irregular form within a longer phrase).

**2. Enforce Atomic, Reality-Grounded Cards**

*   **Insight:** "Leech" cards were often overly complex or based on abstract, "textbook" sentences with no real-world anchor (`Leak 2`).
*   **Recommendation:** Add two new rules to the `Card Design Rules` section:
    > - **Cards must be atomic.** Each card should test only one piece of information. Avoid prompts that require recalling multiple independent concepts at once.
    > - **Cards must be grounded in reality.** Use natural, conversational phrases that one would actually hear or say. Avoid abstract sentences constructed purely to demonstrate a grammar point.

**3. Formalize the Use of the `Interesting Facts` Field**

*   **Insight:** Verbose back content can obscure the primary answer and slow down reviews (`Leak 6`). A new `Interesting Facts` field was created to solve this. The generation rules must enforce its use.
*   **Recommendation:** Add a rule to the `Output Format` section or create a new `Note Type Usage` section:
    > **Use the `Production` note type for EN->ES cards.** The `Back` field must contain *only* the direct Spanish translation. All supplementary information (etymology, grammar notes, detailed examples, dialect comparisons) must go into the `Interesting Facts` field. This keeps recall clean and efficient.

**4. Add a Guideline for "Reactive Intake"**

*   **Insight:** Batch-adding idioms or vocabulary is less effective than adding them as they are encountered in real content (`Leak 4`).
*   **Recommendation:** Add a guiding principle to the `Input Rules` section:
    > **Prioritize reactive intake.** Generate cards from material you have recently consumed (read, heard, or watched). This provides a natural context anchor for each card, making it far more memorable than cards generated from abstract lists.

---

### **Recommendations for the `add-cards` skill (`anki-add-cards/SKILL.md`)**

These are minor process improvements to make the overall workflow smarter and more robust.

**1. Emphasize the Preferred `Production` Note Type**

*   **Insight:** The `Production` note type with its `Interesting Facts` field is now the standard for this deck. The skill should ensure the generation model is aware of this.
*   **Recommendation:** In `Step 3 — Build Generation Context`, amend the instructions to explicitly guide the generator:
    > When invoking `/generate-cards`, the context should highlight that the `Production` model is preferred for EN->ES cards and that verbose, supplementary information should be placed in the `Interesting Facts` field.

**2. Add Deck-Level Dialect Metadata**

*   **Insight:** Dialect coherence is critical (`Leak 5`). While the compiled context specifies it, the system could be made more robust for future decks.
*   **Recommendation:** In `Step 1 — Resolve Deck`, enhance the process:
    > After finding the deck directory, look for a metadata file (e.g., `deck.json`). If it exists and specifies a primary dialect (e.g., `"dialect": "es-AR"`), pass this information as an explicit parameter to the `/generate-cards` skill to ensure strict adherence. This makes the system more scalable and reduces ambiguity.
