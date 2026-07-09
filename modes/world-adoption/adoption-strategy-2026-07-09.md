# Adoption strategy — assessment (2026-07-09)

Context: user is time-poor, considering a cold email to CVUT FIT (`cvut_mail.txt`).
Question: is the university email the right move, or reach out elsewhere — what's the strategy?

## Verdict

Sending the email is nearly free, so it's not a bad idea — but as the *primary* adoption
strategy it's weak, and as a general letter to the faculty it will most likely die in an
inbox. The moves that fit the "no time" constraint are distribution moves, not partnership
moves.

## Why the CVUT email, as a strategy, underdelivers

Inception research (2026-05-22) already called this: the university path is the one "most
likely to produce a paper 12 people read." Three structural reasons:

1. **Universities don't adopt projects; individual supervisors adopt thesis topics.**
   A letter addressed to the institution has no owner. FIT's actual intake channel for
   outside topics is formal: external proposers submit a topic annotation, it gets assigned
   to a guaranteeing department, and it's posted through the thesis system
   (ProjectsFIT / is.fit.cvut.cz) where students pick it. A "would you consider my project
   for future opportunities" email fits none of these slots.
2. **The timeline is wrong for adoption.** Topics get picked at semester boundaries;
   results land in 1–2 years; the student graduates and leaves. It temporarily rents
   development capacity but produces zero popularization.
3. **It skips the prerequisite.** Both repos are public on GitHub but invisible — zero
   stars, main repo has no description or positioning. Anyone who gets curious lands on
   something they can't evaluate in five minutes. Every outreach channel converts at ~zero
   because of this, regardless of who is emailed.

## Strategy ranked by adoption-per-hour-of-your-time

1. **Make the repo legible (one-time, a few evenings — highest leverage).** README leading
   with the "learning conductor" idea, a 2–3 minute demo GIF/video of a real session, one
   copy-pasteable install path. Basic Anki+LLM card generation is saturated; the README
   must sell the conductor/context-garden architecture and the deep Anki-state feedback
   loop, not "another Anki MCP."
2. **Register where seekers already look (hours, permanent payoff).** MCP registries
   (official registry, PulseMCP, mcp.so, Smithery), Claude Code plugin ecosystem, Anki
   community tool lists. Free, passive distribution.
3. **One-shot announcements (one day, done once).** Show HN, r/Anki, Anki Forums,
   r/ClaudeAI, r/languagelearning. Co-maintainers emerge from users who got value, almost
   never from cold institutional outreach.
4. **CVUT — yes, but through the right door and reshaped.** After steps 1–2, send 2–3
   concretely scoped thesis topic annotations (the format their process consumes), via the
   cooperation channel or directly to a named supervisor whose group fits (SW engineering /
   HCI / applied ML). The draft's bullets ("provider-agnostic migration", "single-deliverable
   packaging") are the right raw material — as individual topic annotations, not bullets in
   a letter. Strongest card: motivation/plateau detection from Anki review-history data —
   a real research question that exists commercially but not in open source; supervisors
   pick topics because they're interesting, not as favors to alumni.
5. **Skip for now:** EU grants (Erasmus+/Horizon) — proposal-writing is exactly the time
   you don't have; tool partnerships (Obsidian, Readwise…) — premature with zero external
   users.

## Bottom line

Not "email CVUT" vs "other organizations" — the right axis is **artifact before outreach**:
one focused push to make the public repo self-explaining, then near-free listings and
announcements, then targeted university outreach in the form their system actually accepts.
The co-maintainer conversation happens on its own once a motivated user or student appears.

## Sources

- [Témata závěrečných prací — FIT ČVUT](https://courses.fit.cvut.cz/SZZ/prace/topics.html)
- [Možnosti pro firmy — FIT ČVUT](https://fit.cvut.cz/cs/spoluprace/pro-prumysl/moznosti-pro-firmy)
- [Závěrečná práce — SZZ FIT ČVUT](https://courses.fit.cvut.cz/SZZ/prace/index.html)
