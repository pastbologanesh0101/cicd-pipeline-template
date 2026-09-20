# CI/CD Pipeline Template

[![CI/CD Pipeline](https://github.com/pastbologanesh0101/cicd-pipeline-template/actions/workflows/ci.yml/badge.svg)](https://github.com/pastbologanesh0101/cicd-pipeline-template/actions/workflows/ci.yml)

A small, genuinely working Flask REST API used as the subject of a
**multi-stage GitHub Actions pipeline** — lint, test (with coverage,
matrixed across Python versions), security scan, and a Docker build.
Everything runs on GitHub Actions' free hosted runners; no cloud
account or credentials are required.

The point of this repo isn't the app (a calculator + todo API) — it's
the pipeline structure around it: staged jobs with real dependencies,
a reusable composite action, and a clear seam for where a real deploy
stage would plug in.

## Contents

- [The app](#the-app)
- [Pipeline architecture](#pipeline-architecture) — lint, test,
  security scan, Docker lint, build, and how to add a real deploy stage
- [Reusable composite action](#reusable-composite-action)
- [Project layout](#project-layout)
- [Running everything locally](#running-everything-locally)
- [Troubleshooting / FAQ](#troubleshooting--faq)
- [License](#license)

## The app

`app/` contains:

- `calculator.py` — arithmetic (`add`/`subtract`/`multiply`/`divide`),
  `percentage`, `is_prime`, `factorial`, and an operation dispatcher.
- `todo_store.py` — an in-memory `TodoStore` with validation
  (rejects empty/oversized titles), get/update/toggle/delete, and
  proper `TodoNotFoundError`/`TodoValidationError` exceptions.
- `main.py` — a Flask app (application factory pattern) exposing:
  - `GET /health`
  - `POST /calculate` `{operation, a, b}`
  - `GET /calculate/is-prime/<n>`, `GET /calculate/factorial/<n>`
  - `GET/POST /todos`, `GET/PUT/DELETE /todos/<id>`, `PATCH /todos/<id>/toggle`

`tests/` has 48 tests: unit tests for the calculator and todo store,
plus integration tests hitting every API endpoint through Flask's
test client (`tests/test_calculator.py`, `tests/test_todo_store.py`,
`tests/test_api.py`).

## Pipeline architecture

The workflow (`.github/workflows/ci.yml`) has five jobs, staged with
`needs:` so later, more expensive stages only run once earlier,
cheaper ones pass:

```
lint ──────────┐
test ──────────┤
security-scan ─┼──► build
docker-lint ───┘   (needs: lint, test, security-scan, docker-lint)
```

`lint`, `test`, `security-scan`, and `docker-lint` run in parallel
(nothing depends on them running in a particular order relative to
each other — only `build` waits on all four). This gets fast,
independent feedback and still guarantees nothing gets built from
code (or a Dockerfile) that fails a check.

### 1. Lint — `ruff check .` + `black --check .`

Catches style issues, unused imports, obvious bugs (`ruff`), and
formatting drift (`black --check`, which fails the build rather than
silently reformatting). This is the cheapest, fastest stage, so it
runs first and fails fast before spending CI minutes on anything else.

Run locally:

```bash
pip install -r requirements-dev.txt
ruff check .
black --check .          # or `black .` to auto-fix
```

### 2. Test — `pytest --cov` across a Python version matrix

Runs the full test suite with coverage reporting, matrixed across
Python 3.11 and 3.12 (`strategy.matrix.python-version`) so a change
that only breaks on one interpreter version is caught. Coverage XML
is uploaded as a build artifact per Python version.

Matters because: this is the actual correctness gate — it's what
tells you the calculator and todo logic still behave the way the
tests specify, on every version you claim to support.

Run locally:

```bash
pytest --cov=app --cov-report=term-missing
```

### 3. Security scan — `pip-audit` + `bandit`

- `pip-audit -r requirements.txt` checks every pinned dependency
  against known-vulnerability databases (this is how the initial
  `Flask==3.0.3` pin was caught and bumped to `3.1.3` before this
  repo was even pushed).
- `bandit -r app` statically scans the application code itself for
  common security antipatterns (hardcoded binds, `eval`, weak crypto,
  etc.).

Matters because: lint and tests check "does it work as written";
this stage checks "does it work safely," which neither of the others
covers.

Run locally:

```bash
pip-audit -r requirements.txt
bandit -r app -q
```

### 4. Docker lint — `hadolint`

Lints the `Dockerfile` itself against best-practice rules (pinned
base image tags, sane layer ordering, avoiding unnecessary root
usage, etc.) via `hadolint/hadolint-action@v3.1.0`. This is a
different kind of check than the others: `ruff`/`black` only look at
Python source, and `bandit` only looks at application code — neither
touches the container definition, so a bad `Dockerfile` could
otherwise reach `build` unchecked.

Run locally (requires [hadolint](https://github.com/hadolint/hadolint)
installed, e.g. via `brew install hadolint` or its Docker image):

```bash
hadolint Dockerfile
```

### 5. Build — `docker build` (build-only)

Builds the app's Docker image (`Dockerfile`) to prove it containerizes
cleanly, using `docker/build-push-action` with `push: false`. It
deliberately does **not** push to a registry or deploy anywhere —
that would require cloud credentials this template intentionally
avoids, since the goal is demonstrating pipeline *structure*, not
standing up infrastructure.

Run locally:

```bash
docker build -t cicd-pipeline-template:local .
docker run --rm -p 8000:8000 cicd-pipeline-template:local
```

### Adding a real deploy stage

`ci.yml`'s `build` job has the exact next steps sketched in comments.
In short, a production version of this pipeline would add, after the
build-only step:

1. **Registry login** — `docker/login-action` against `ghcr.io` (or
   ECR/GCR/Docker Hub), authenticated with a repo secret or, for
   GHCR, the built-in `GITHUB_TOKEN`.
2. **Build and push** — swap `push: false` for `push: true` and tag
   the image with `${{ github.sha }}` (and `:latest` on `main`).
3. **Deploy** — a final job, gated with `needs: build` and an
   `environment:` (so GitHub Environments can require manual approval
   for production), that pulls the pushed tag and rolls it out —
   `kubectl set image ...`, `aws ecs update-service`, a Fly.io/Render
   deploy hook, etc., depending on where it's hosted. Cloud
   credentials for that step belong in encrypted repo/environment
   secrets, never committed.

## Reusable composite action

`.github/actions/setup-python-env/action.yml` is a composite action
that installs a given Python version, enables pip caching, and
installs `requirements-dev.txt`. The three jobs that need a Python
environment — `lint`, `test`, and `security-scan` — all call it
(`uses: ./.github/actions/setup-python-env`) instead of repeating the
same three steps three times (`build` and `docker-lint` don't need
it, since neither one runs Python) — a small demonstration of DRY
pipeline design that scales to real multi-job workflows.

## Project layout

```
app/                      Flask app + calculator/todo business logic
tests/                    pytest suite (unit + integration)
.github/workflows/ci.yml  the multi-stage pipeline
.github/actions/          reusable composite action
Dockerfile                build-only container image for the app
requirements.txt          runtime dependency (Flask)
requirements-dev.txt      + pytest, ruff, black, bandit, pip-audit
```

## Running everything locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

ruff check .
black --check .
bandit -r app -q
pip-audit -r requirements.txt
pytest --cov=app --cov-report=term-missing

hadolint Dockerfile   # requires hadolint installed separately, e.g. `brew install hadolint`
docker build -t cicd-pipeline-template:local .
```

## Troubleshooting / FAQ

**`python -m app.main` runs, but I can't reach the API from another
container, VM, or device on my network.** `app/main.py`'s `__main__`
block binds to `127.0.0.1` by default (safe default for local dev —
bandit would also flag a hardcoded `0.0.0.0` bind as B104). Pass
`--host 0.0.0.0` (and `--port` if you don't want 5000) to override it:
`python -m app.main --host 0.0.0.0 --port 8000`. Equivalently, run it
the way the Dockerfile does: `flask --app app.main run
--host=0.0.0.0 --port=8000`, or just use `docker run -p 8000:8000
...`, which already binds all interfaces inside the container.

**`PUT /todos/<id>` with `{"completed": "false"}` returns 400
("completed must be a boolean").** This is intentional, not a bug —
`"false"` is a non-empty *string*, and `bool("false")` is `True` in
Python, so accepting it would have silently marked the todo complete
instead of incomplete. Send a real JSON boolean (`"completed": false`,
no quotes) instead of the string.

**`pip-audit -r requirements.txt` fails locally on a dependency that
passed in CI yesterday.** `pip-audit` checks against a live
vulnerability database, so a previously-clean pin can start failing
without any change to this repo if a new CVE is published for it.
Re-run it to see which package and advisory triggered it, then bump
that pin in `requirements.txt` (this is exactly how the initial
`Flask==3.0.3` pin was caught and bumped to `3.1.3`, per the security
scan section above) — it's not a false positive to silence.

## License

MIT — see [LICENSE](LICENSE).
