Execute the add-cards pipeline.

Usage: `/pipe:anki-add-cards <deck> [input]`

Read `.claude/pipeline-specifications/add-cards.md`. Execute each step in the defined order,
passing `<deck>` and `[input]` through to the relevant steps. Follow the
mandatory/optional and error handling rules defined in the pipeline file exactly.
