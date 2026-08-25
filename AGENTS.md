# Agent Repository Guide

## Project identity

- Official name: **Fertilizer Recommendation System** (engine codename: SoilScanRuleBased).
- Positioning: a **decision-support prototype** for fertilizer guidance, designed for
  CAR (Cordillera Administrative Region) produce and land conditions.
- Audience: farmers, the general public, and recruiters viewing it as a portfolio piece.
- Owner and sole approver of agronomic decisions: **Hans Fredrick Aragona**.
- License: MIT (`Copyright (c) 2026 Hans Fredrick Aragona`).

## Source of truth

- `engine/core.py` is the active recommendation engine (formerly
  `app_final.py`). Its public entry point is `build_recommendation(...)`.
- `api/main.py` exposes that engine through `POST /recommendation` (formerly
  `RuleBasedAPI.py`).
- `ui/streamlit_app.py` is the Streamlit reference UI, maintained alongside
  the Next.js frontend — not replaced by it.
- `engine/prototype_solver.py` is a prototype solver; it is not imported by
  the active engine.

## Protected agronomic data

All JSON rule files under `rules/` are **final domain data**. Never edit,
rename, reformat, regenerate, or delete them without explicit owner approval
in the current task:

- `rules/crop_npk_rules.json` — active crop nutrient targets
- `rules/engine_rules.json` — solver constraints and calculation policy
- `rules/ph_rules.json` — pH thresholds and amendment guidance
- `rules/fertilizers.json` — fertilizer analysis used in recommendations
- `rules/orig_crop_npk.json` — reference data, protected under the same rule

Web research may inform suggestions but must never lead to a JSON-rule change
without explicit approval of that exact change. Do not infer agronomic values.

## Autonomy and approvals

Allowed without asking: read repository files, edit in-scope non-JSON code and
documentation, create tests, create new files/directories when necessary, run
non-destructive local commands (including generated caches/build folders and
virtual environments), use web research, and report findings.

Ask before: installing or upgrading packages; editing `requirements.txt`;
editing any JSON rule file; adding external services, secrets, or paid APIs;
deployment; committing, pushing, opening pull requests; modifying GitHub
Actions workflows; or any Git-history operation.

Never use destructive Git commands (`reset --hard`, force push, history
rewrites). The repository works on a single `main` branch; commits happen only
with explicit owner approval.

## Unattended operation

When running without supervision, agents continue safe, in-scope work:
inspect code, implement approved tasks, write/run tests, update documentation,
and record progress in `agent-memory/`. Stop at every approval boundary above
and leave a clear handoff note instead of proceeding.

## Agent team roles

| Role | Responsibility |
| --- | --- |
| Coordinator | Breaks work into tasks, delegates, reviews all results before integration. |
| Backend developer | FastAPI, engine integration, API contracts. |
| Frontend developer | Next.js dashboard, session behavior, PDF export. |
| Test/QA agent | Unit, API, UI, end-to-end tests and regression checks. |
| UI/UX reviewer | Dashboard usability, accessibility, responsive design. |
| Security reviewer | Dependency, API exposure, secrets, deployment review. |
| Documentation agent | README/architecture/user docs; maintains `agent-memory/`. |
| Research agent | Deployment/library/agronomic references; recommends only, never edits rules. |

## Subagent policy

- Specialists may spawn helper subagents but must inform the coordinator first.
- Helpers may research, inspect code, and run tests — **never edit files**.
- Specialists may edit only the files assigned to them.
- Maximum four agents running simultaneously.
- The coordinator reviews every result before it is integrated.

## Product behavior contracts

1. Two recommendation sets in one response:
   - **Standard set**: raw N/P/K requirement plus combinations from the full
     approved fertilizer catalogue.
   - **Farmer-selected set**: combinations based on preselected fertilizers;
     must include at least one selected item whenever possible, prefer using
     all selected items, and may supplement from the catalogue when needed.
2. pH is assessed independently of N/P/K quantities but returned in the same
   recommendation response.
3. Recommendation history lives only in the active browser session. Warn the
   user before tab close/leave if results are unexported. Export is user-
   triggered PDF download only.
4. The AI assistant (future) is guidance-only: it never alters JSON rules,
   nutrient targets, thresholds, or solver output; it explains deterministic
   engine results; it directs users to qualified professionals; it states the
   tool is designed for CAR produce and does not assure results elsewhere.

## Engineering rules

- Preserve `build_recommendation`'s response shape unless a task explicitly
  authorizes an API contract change.
- Keep rule evaluation deterministic and explainable; no model-generated
  agronomic advice replaces approved rules.
- Keep business logic out of presentation layers; frontends consume the
  FastAPI contract rather than duplicate N/P/K calculations.
- Write or update tests for behavior changes in `engine/core.py`, the API, or
  frontend logic. Target ~80% coverage on tested Python code.
- Run Ruff (`ruff check .` and `ruff format --check .`) on Python changes.

## Required validation

Run from the repository root when relevant:

```powershell
python -m compileall -q .
ruff check .
ruff format --check .
python -m unittest discover -s tests -v
Get-ChildItem rules/*.json | ForEach-Object { Get-Content $_ -Raw | ConvertFrom-Json | Out-Null }
```

CI runs equivalent checks on GitHub. Report what was and was not exercised;
never claim Streamlit/FastAPI were tested unless dependencies were installed
and the service was actually exercised.

## Memory discipline (non-negotiable)

Every work session MUST end with a memory update before reporting completion:

1. Update `agent-memory/status.md` with status, decisions + reasons,
   validation results, risks, next action, and changed files.
2. Sync `docs/STATUS.md` (public mirror) if the change is user-visible.
3. Run `/session-save` (or write the dated snapshot manually in
   `opencode-memory/`) so session history is preserved.
4. Never mark a task complete or hand off without steps 1-3.

An agent that changes code but leaves memory stale has NOT finished its task.

## Agent memory and handoff

Two local-only memory layers (both gitignored, never committed):

- `agent-memory/` — shared state for the agent team: project status,
  decisions with reasons, incomplete tasks, validation results, known
  issues/risks, next recommended action, and changed files. The documentation
  agent keeps `agent-memory/status.md` current after completed work and at
  handoff points.
- `opencode-memory/` — one dated snapshot file per opencode session,
  written via the `/session-save` command when a session ends.

Never store chat transcripts, secrets, tokens, or real user/farm data in
either location.
