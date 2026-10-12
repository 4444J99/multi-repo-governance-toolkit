# multi-repo-governance-toolkit

A small toolkit for governing a multi-repository GitHub estate: registry and metadata scripts, reusable repository templates, and a pytest suite.

## What's inside

- `scripts/` — Python utilities for validating, normalizing and reporting on repository registry data, generating per-repo seed files and org-level GitHub configs, and checking publication authorizations.
- `templates/` — reusable ADR, changelog, badge and dependency-manifest templates.
- `.github-template/` — community-health file templates (code of conduct, contributing, security, issue and PR templates) and an org profile template, using `{{PLACEHOLDER}}` values.
- `tests/` — pytest suite.

Scripts that scan a local workspace read its root from the `ORGANVM_WORKSPACE` environment variable (default: current directory).

## Running the tests

```bash
python -m pip install pytest pyyaml
python -m pytest
```

## License

MIT — see [LICENSE](LICENSE).

## Identity lint

`scripts/identity-lint.py` flags emails, home paths and denylisted names. Denylisted
terms are stored only as salted SHA-256 hashes in repository secrets
(`IDENTITY_SALT`, `IDENTITY_DENYLIST`, optional `IDENTITY_OWN_NAMES`); nothing
guessable is committed. Without those secrets (forks, local runs) the hash check is
skipped with a notice and the plain-pattern checks still run. In CI it is warning-only.
