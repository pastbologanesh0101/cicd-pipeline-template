# Contributing

This is a small, dependency-light Flask sample used to demonstrate a
multi-stage CI pipeline (see `README.md` for the pipeline itself).
Changes to the app should stay in that spirit: no database, no extra
runtime dependencies beyond Flask unless there's a strong reason.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Running the test suite

Tests run with `pytest` (config lives in `pyproject.toml`'s
`[tool.pytest.ini_options]`, so plain `pytest` already runs with
coverage):

```bash
pytest
# equivalent to:
pytest --cov=app --cov-report=term-missing --cov-report=xml
```

All 48+ tests must pass before opening a PR. If you add behavior to
`app/calculator.py`, `app/todo_store.py`, or a route in `app/main.py`,
add tests for it in the matching file under `tests/`
(`test_calculator.py`, `test_todo_store.py`, `test_api.py`
respectively) — don't rely on the CI matrix to catch a missing case.

## Code style

- **Formatting**: `black` (line length 100, targets py311/py312).
  Run `black .` to auto-format, or `black --check .` to verify without
  changing anything.
- **Linting**: `ruff check .` (rule set: `E`, `F`, `W`, `I`, `B` — see
  `pyproject.toml`). Fix warnings rather than suppressing them unless
  there's a good reason, and note the reason inline if you do.
- **Type hints**: the codebase uses `from __future__ import
  annotations` plus hints on public functions (see
  `app/calculator.py`). Match that style for new functions.
- **Docstrings**: short one-line docstrings on public functions, with
  a `Raises:` note when a function raises something other than the
  obvious. Follow the existing style in `app/calculator.py` and
  `app/todo_store.py`.
- **Errors**: business-logic errors are domain exceptions
  (`CalculatorError`, `TodoValidationError`, `TodoNotFoundError`), not
  bare `ValueError`/`KeyError` — Flask routes catch these and turn
  them into the right HTTP status + JSON body. New failure modes
  should follow the same pattern rather than raising Flask errors
  directly from `app/calculator.py` or `app/todo_store.py`.

Before committing, run the same checks CI runs:

```bash
ruff check .
black --check .
bandit -r app -q
pip-audit -r requirements.txt
pytest
```

## Submitting changes

1. Fork/branch, make focused commits (one logical change per commit).
2. Make sure `pytest`, `ruff check .`, and `black --check .` all pass
   locally — the `lint` and `test` CI jobs will fail the PR otherwise.
3. Open a PR against `main`. The CI pipeline (lint, test matrix,
   security scan, Docker build) runs automatically; all four jobs
   must be green before merge.
4. Keep PRs scoped to one change — this repo is a teaching example of
   pipeline structure, so small, reviewable diffs matter more than in
   a typical app repo.
