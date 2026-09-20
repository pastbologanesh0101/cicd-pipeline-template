## What does this change do?

<!-- One or two sentences. If it touches app/, note which route(s) or
     module(s) are affected. -->

## Why?

<!-- What breaks or is missing without this change? -->

## Checklist

- [ ] Added/updated tests in `tests/` for any behavior change in `app/`
      (see [CONTRIBUTING.md](../CONTRIBUTING.md))
- [ ] `pytest` passes locally
- [ ] `ruff check .` and `black --check .` pass locally
- [ ] If this touches `app/`, `bandit -r app -q` still passes
- [ ] If this changes dependencies, `pip-audit -r requirements.txt` still passes
- [ ] If this changes the `Dockerfile`, `hadolint Dockerfile` still passes
- [ ] This PR is scoped to one logical change (see CONTRIBUTING.md)

<!-- CI (lint, test matrix, security scan, docker-lint, build) will
     re-run these automatically, but running them locally first saves
     a round trip. -->
