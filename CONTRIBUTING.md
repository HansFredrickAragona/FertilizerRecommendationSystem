# Contributing

## Before you change anything

Read `AGENTS.md` and `docs/ARCHITECTURE.md`. This project makes agricultural
recommendations, so rule-data accuracy matters as much as code correctness.

## Setup

Python **3.12** is the supported version. Create and activate a virtual
environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

Dependency installation requires repository-owner approval. After approval:

```powershell
pip install -r requirements.txt
```

Note: the existing UI imports Streamlit, but Streamlit is not currently listed
in `requirements.txt`. Treat correcting that dependency declaration as a
separate, approval-required change.

## Development workflow

1. Identify whether the request affects the engine, API, UI, frontend, or
   protected rule data.
2. For engine changes, start with a failing or updated test in `tests/`.
3. Keep the response produced by `build_recommendation` backward-compatible
   unless an API contract change is explicitly requested.
4. Do not edit JSON rules without explicit approval and a cited agronomic source.
5. Follow the MVC layer boundaries in `docs/ARCHITECTURE.md`: no calculation logic
   in views or controllers.
6. Follow the memory-discipline rule in `AGENTS.md`: no task is complete
   until `agent-memory/status.md` (and `docs/STATUS.md` if user-visible)
   reflects the change.
7. Run the quality gate below and report what was and was not exercised.

## Code style (Ruff)

This project uses [Ruff](https://docs.astral.sh/ruff/) as its single linter
and formatter. Configuration lives in `ruff.toml`. After installing Ruff:

```powershell
ruff check .          # lint
ruff format .         # format files you changed
```

CI enforces `ruff check .` and `ruff format --check .`.

## Quality gate

```powershell
python -m compileall -q .
ruff check .
ruff format --check .
python -m unittest discover -s tests -v
Get-ChildItem rules/*.json | ForEach-Object { Get-Content $_ -Raw | ConvertFrom-Json | Out-Null }
```

For API changes, additionally exercise the endpoint after approved dependencies
are installed. For UI changes, run the Streamlit app or the Next.js frontend
and check the relevant user flow manually.

## Git workflow

- Single branch: all work happens on `main`.
- Commits, pushes, and PRs require explicit owner approval.
- Use conventional commit messages (e.g. `feat(frontend): ...`,
  `fix(engine): ...`).

## Pull-request expectations

- Explain the user-visible behavior change.
- Include tests for engine or API behavior changes.
- State whether any protected agronomic file changed and cite its approval.
- Include the validation commands and their results.
- Do not commit, push, or alter Git history without the repository owner's
  explicit authorization.
