# spec-kit-catalog

Private [Spec Kit](https://github.com/github/spec-kit) catalog for Benjamin Kuebler's
extended SDD setup. It hosts two separate catalog types plus the workflow definition:

- **`catalog.json`** — extension catalog (the allow-list of extensions that may be installed)
- **`workflow-catalog.json`** — workflow catalog (points to the workflow YAML below)
- **`workflows/extended-sdd.yml`** — the extended SDD workflow definition

The extensions themselves are **not** stored here — this repo is a directory only.
Each `download_url` in `catalog.json` points to the release archive of the
extension's own repository.

## Layout

```
catalog.json                             Extension catalog (allow-list)
workflow-catalog.json                    Workflow catalog
workflows/extended-sdd.yml               Extended SDD workflow definition
scripts/validate_catalog.py              Structure + URL validator (stdlib only)
.github/workflows/validate-catalog.yml   CI: runs the validator on every push
```

## Extension catalog contents

| id | version | effect | purpose |
|---|---|---|---|
| discovery | 0.2.0 | read-write | Pre-spec discovery: problem, concept, ADR, decomposition |
| red-team | 1.0.2 | read-write | Adversarial spec review before `/speckit.plan` |
| security-review | 1.6.1 | read-write | DevSecOps security audits (plan / tasks / branch / PR) |
| qa | 1.0.0 | read-only | Acceptance-criteria testing |
| agent-assign | 1.1.0 | read-write | Assign and run Claude Code agents per task |
| bugfix | 1.1.0 | read-write | Structured bugfix workflow (maintenance) |
| context-budget | 0.1.0 | read-write | Budget-aware memory loader + token tracking + learning |

Versions are pinned to tested releases (newer than the community catalog for
several entries). All `download_url`s use `archive/refs/tags/v<version>.zip`.

## Register the catalogs

Extension catalog:

```bash
export SPECKIT_CATALOG_URL="https://raw.githubusercontent.com/bkuebler/spec-kit-catalog/main/catalog.json"
# or additive (keeps the community catalog alongside):
specify extension catalog add "$SPECKIT_CATALOG_URL" --name bkuebler --priority 5 --install-allowed
```

Workflow catalog (a **separate** catalog type from the extension catalog):

```bash
export SPECKIT_WORKFLOW_CATALOG_URL="https://raw.githubusercontent.com/bkuebler/spec-kit-catalog/main/workflow-catalog.json"
# or additive:
specify workflow catalog add "$SPECKIT_WORKFLOW_CATALOG_URL" --name bkuebler
```

## Use in a new repo

With the catalogs registered (once per machine):

```bash
specify bundle install extended-sdd-stack      # installs all 7 extensions (+ the workflow)
specify workflow run extended-sdd -i spec="…"  # runs the extended step sequence
```

After install, disable the overlapping auto-hooks in `.specify/extensions.yml`
(`security-review` after_*, `qa` after_implement, `red-team` before_plan) so the
workflow drives those commands explicitly as steps. Keep `context-budget`'s hooks
enabled — it is a cross-cutting context loader, not a workflow step.

## Validation

`scripts/validate_catalog.py` checks both catalogs for required fields,
id/key consistency, and reachable URLs (HEAD, expecting 200/302). CI runs it on
every push to the catalog files.

```bash
python scripts/validate_catalog.py             # full (structure + URLs)
python scripts/validate_catalog.py --skip-urls # structure only
```

## License

MIT — see [LICENSE](LICENSE).
