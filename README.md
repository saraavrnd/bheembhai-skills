# bheembhai-skills

The BheemBhai skills catalog: every SDLC skill, workflow and policy the platform runs. This repo
is the only place they are edited (ADR-032). The platform imports tagged releases from its admin
Catalog page.

## Layout

| Path | What it holds |
|---|---|
| `skills/<name>/` | One skill: `SKILL.md`, `verify.yaml`, `templates/`, `references/`, `examples/` |
| `shared/` | Shared notes. **The only editable copy.** `shared-map.yaml` lists which skills get a copy in `references/` |
| `config/` | Workflows (`sdlc-wf-*.yaml`) and policies (`sdlc-policy-*.yaml`) |
| `catalog.yaml` | Catalog `version`, `requires_platform`, `requires_verify` |
| `requirements-verify.txt` | Exact pin of the shared verifier `bheembhai-verify` (ADR-032 §2a) |
| `tools/` | `check.py` (tier-1 checks), `build.py` (sync shared notes, pack a release), `known-issues.txt` |
| `docs/skill-chain.md` | How the skills chain into workflows |

## Changing a skill

1. Branch, edit the skill (or `shared/`, then run `python tools/build.py sync`).
2. Run `python tools/build.py sync --check` and `python tools/check.py` locally (`pip install -r requirements-tools.txt`).
3. Open a PR. CI runs the same checks.

Naming: skills `sdlc-<phase>-<object>-<action>`, workflows `sdlc-wf-*`, policies `sdlc-policy-*`;
a workflow step's id equals its skill name.

## Releasing

1. Bump `version` in `catalog.yaml` (and `requires_platform` / `requires_verify` if the skills need
   newer platform features or checks). Merge.
2. Tag the merge commit `v<version>` and push the tag. The release workflow checks, packs and
   publishes `catalog.tgz`, its `.sha256` and `manifest.json` as a GitHub Release.
3. In the platform, open **Admin → Catalog**, pick the release, review the preview, deploy.

The archive is deterministic: packing the same commit twice gives the same sha256.
