---
description: Save an opencode session snapshot as its own dated file in opencode-memory/.
---

Create a session snapshot file at `opencode-memory/<today's date>-<time>.md`
(e.g. `2026-08-25-1430.md`) containing:

1. **Session summary** - what was asked and what was done
2. **Decisions made** - with reasons
3. **Files changed** - full list
4. **Validation results** - commands run and outcomes
5. **Incomplete work / next steps**

Then verify `agent-memory/status.md` reflects the latest overall project state
(update it only if this session changed something not yet recorded).

Context from the owner:

$ARGUMENTS

Never store secrets, tokens, or real user/farm data in either location.
