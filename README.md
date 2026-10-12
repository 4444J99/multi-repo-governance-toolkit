# multi-repo-governance-toolkit

[![CI](https://github.com/4444J99/multi-repo-governance-toolkit/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/4444J99/multi-repo-governance-toolkit/actions/workflows/ci.yml)

When one owner runs dozens of separate GitHub repos, the registry, community-health files and metadata drift apart, and personal details leak into public code. This toolkit keeps them consistent with scripts that validate the registry, generate GitHub config, report PR status and lint every file for names, emails and home paths.

## Quick start

```console
$ python scripts/identity-lint.py .
identity-lint: notice: IDENTITY_SALT/IDENTITY_DENYLIST not set; skipping denylist and domain-hash checks (plain-pattern checks still run)
identity-lint: 0 denylist hashes, 4 allowlist entries, 0 finding(s)
```

That output is from a local run without the CI secrets. In CI, the same command loads the salted denylist.

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
