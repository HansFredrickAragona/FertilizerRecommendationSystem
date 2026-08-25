---
description: Run the full quality gate (compile, ruff, tests, JSON validation) and report results.
---

Run the full validation gate from AGENTS.md and report pass/fail for each step,
plus anything that was NOT exercised:

```powershell
python -m compileall -q .
ruff check .
ruff format --check .
python -m unittest discover -s tests -v
Get-ChildItem *.json | ForEach-Object { Get-Content $_ -Raw | ConvertFrom-Json | Out-Null }
```

$ARGUMENTS
