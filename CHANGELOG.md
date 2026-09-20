# Changelog

All notable changes to this project are documented here. Format is
loosely based on [Keep a Changelog](https://keepachangelog.com/).

## [0.1.0] - 2026-09-18

Initial release: a sample Flask app plus the multi-stage CI pipeline
built around it.

### Added

- **App** (`app/`): a small Flask REST API (application factory in
  `main.py`) covering two independent pieces of business logic:
  - `calculator.py` — `add`/`subtract`/`multiply`/`divide`,
    `percentage`, `is_prime`, `factorial`, and a `calculate()`
    operation dispatcher, all raising `CalculatorError` on bad input
    (e.g. division by zero, non-integer `factorial`/`is_prime` input,
    unknown operation names).
  - `todo_store.py` — an in-memory `TodoStore` (add/list/get/update/
    toggle/delete) with title validation (non-empty, ≤200 chars) and
    dedicated `TodoNotFoundError`/`TodoValidationError` exceptions.
  - HTTP routes: `GET /health`, `POST /calculate`, `GET
    /calculate/is-prime/<n>`, `GET /calculate/factorial/<n>`, and full
    CRUD + toggle on `/todos`.
- **Tests** (`tests/`): 48 pytest tests spanning unit tests for the
  calculator and todo store plus integration tests hitting every
  route through Flask's test client, with coverage configured via
  `pyproject.toml` (`pytest --cov=app`).
- **CI pipeline** (`.github/workflows/ci.yml`): four staged jobs —
  `lint` (ruff + black), `test` (pytest, matrixed across Python 3.11
  and 3.12), `security-scan` (pip-audit + bandit), and `build`
  (build-only `docker build`, gated with `needs:` on the first three
  so nothing builds from code that fails a check).
- **Reusable composite action**
  (`.github/actions/setup-python-env/action.yml`): sets up Python +
  pip caching + `requirements-dev.txt`, used by all four CI jobs
  instead of duplicating the same three steps.
- **Dockerfile**: build-only container image (non-root user, layer
  ordering so dependency installs cache independently of app code)
  proving the app containerizes cleanly; no registry push or deploy
  step, by design.
- **Dependency pins**: `requirements.txt` pins `Flask==3.1.3` (bumped
  up from an initially-audited `3.0.3` after `pip-audit` flagged it
  before the repo was pushed); `requirements-dev.txt` adds pytest,
  pytest-cov, ruff, black, bandit, and pip-audit.
- `README.md` documenting the pipeline architecture and how to run
  every stage locally, `LICENSE` (MIT).

[0.1.0]: https://github.com/pastbologanesh0101/cicd-pipeline-template/commit/ad534240f961ca388ffd1c7f12a5354c955fa38b
