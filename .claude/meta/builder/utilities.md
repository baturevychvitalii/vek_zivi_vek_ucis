# Utilities Awareness

Before writing any helper or shared code, check whether `.claude/utils/` already covers it.

**How:** Scan `.claude/utils/README.md` (one table, ~10 seconds). If a module looks relevant, open the source — files are short. Only write new helper code when nothing fits.

**Scope:** Logging, LLM invocation, transcript access — covered. Anything else is fair to implement, but add it to `utils/` if it's likely to be reused across hooks or skills.
