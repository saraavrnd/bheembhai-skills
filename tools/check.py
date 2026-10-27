#!/usr/bin/env python3
"""Tier-1 static checks for the BheemBhai skills catalog (ADR-032 §2). No LLM, no network.

  python tools/check.py            exit 1 on any error not listed in tools/known-issues.txt

Checks: skill folder/name/verify.yaml agreement, on_fail and Outcomes words against
verdicts_used, referenced skill files exist, workflow routing and skill references, policy
gates, catalog.yaml, and the bheembhai-verify pin. Shared-note copies are checked by
`tools/build.py sync --check`.
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
CONFIG = ROOT / "config"
KNOWN = ROOT / "tools" / "known-issues.txt"
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
FILE_REF = re.compile(r"`((?:templates|references|examples|schemas|scripts)/[^`\s]+)`")
OUTCOME_WORD = re.compile(r"^\s*-\s*\*\*(\w+)\*\*:", re.M)

errors = []


def err(msg):
    errors.append(msg)


def frontmatter(text):
    if not text.startswith("---"):
        return None
    try:
        return yaml.safe_load(text.split("---", 2)[1]) or {}
    except yaml.YAMLError:
        return None


def check_skills():
    names = set()
    for d in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        n = d.name
        names.add(n)
        if not n.startswith("sdlc-"):
            err(f"skills/{n}: folder name must start with sdlc-")
        md_path = d / "SKILL.md"
        if not md_path.is_file():
            err(f"skills/{n}: SKILL.md missing")
            continue
        md = md_path.read_text()
        fm = frontmatter(md)
        if fm is None:
            err(f"skills/{n}: SKILL.md frontmatter missing or invalid")
        elif fm.get("name") != n:
            err(f"skills/{n}: SKILL.md name '{fm.get('name')}' does not match folder")

        for ref in FILE_REF.findall(md):
            if any(c in ref for c in "<*{") or ref.endswith("/"):
                continue
            if not (d / ref).exists():
                err(f"skills/{n}: SKILL.md references {ref}, which does not exist")

        v_path = d / "verify.yaml"
        if not v_path.is_file():
            continue
        try:
            v = yaml.safe_load(v_path.read_text()) or {}
        except yaml.YAMLError as e:
            err(f"skills/{n}: verify.yaml does not parse: {e}")
            continue
        if v.get("skill") != n:
            err(f"skills/{n}: verify.yaml skill '{v.get('skill')}' does not match folder")
        used = set(v.get("verdicts_used") or [])
        on_fails = {c.get("on_fail") for k in ("preconditions", "checks") for c in (v.get(k) or [])}
        on_fails |= {c.get("on_fail") for c in ((v.get("judge") or {}).get("criteria") or [])}
        on_fails -= {None, "advisory"}
        for word in sorted(on_fails - used):
            err(f"skills/{n}: verify.yaml uses on_fail '{word}' not listed in verdicts_used")
        outcomes = re.search(r"^## Outcomes\n(.*?)(?=^## |\Z)", md, re.S | re.M)
        if outcomes:
            for word in sorted(set(OUTCOME_WORD.findall(outcomes.group(1))) - used - {"completed"}):
                err(f"skills/{n}: Outcomes names '{word}', which verify.yaml never returns (verdicts_used)")
    return names


def load_dir(prefix, key):
    out = {}
    for f in sorted(CONFIG.glob(f"{prefix}*.yaml")):
        try:
            doc = yaml.safe_load(f.read_text()) or {}
        except yaml.YAMLError as e:
            err(f"config/{f.name}: does not parse: {e}")
            continue
        name = doc.get(key)
        if name != f.stem:
            err(f"config/{f.name}: {key} '{name}' does not match file name")
        out[name] = doc
    return out


def check_config(skill_names):
    workflows = load_dir("sdlc-wf-", "workflow")
    policies = load_dir("sdlc-policy-", "policy")
    for name, w in workflows.items():
        steps = {s.get("id"): s for s in w.get("steps") or []}
        if w.get("start") not in steps:
            err(f"{name}: start '{w.get('start')}' is not a step")
        for sid, s in steps.items():
            if "skill" in s:
                if s["skill"] not in skill_names:
                    err(f"{name}: step {sid} uses skill '{s['skill']}', which is not in skills/")
                if sid != s["skill"]:
                    err(f"{name}: step id '{sid}' must equal its skill '{s['skill']}'")
            fe = s.get("foreach")
            if fe:
                if fe.get("run") not in workflows:
                    err(f"{name}: step {sid} fans out to unknown workflow '{fe.get('run')}'")
                if fe.get("policy") and fe["policy"] not in policies:
                    err(f"{name}: step {sid} names unknown policy '{fe['policy']}'")
            for word, target in (s.get("on") or {}).items():
                if target != "DONE" and target not in steps:
                    err(f"{name}: step {sid} routes {word} to unknown step '{target}'")
    for name, p in policies.items():
        w = workflows.get(p.get("applies_to"))
        if not w:
            err(f"{name}: applies_to unknown workflow '{p.get('applies_to')}'")
            continue
        steps = {s.get("id"): s for s in w.get("steps") or []}
        for gate, conf in (p.get("gates") or {}).items():
            if gate not in steps:
                err(f"{name}: gates unknown step '{gate}'")
                continue
            for status in (conf or {}).get("on_status") or []:
                if status not in (steps[gate].get("on") or {}):
                    err(f"{name}: gate {gate} gates '{status}', which the workflow does not route")


def version_tuple(v):
    return tuple(int(x) for x in v.split("."))


def satisfies(version, spec):
    """Minimal >=, >, <=, <, == range check over comma-separated clauses (X.Y or X.Y.Z)."""
    for clause in [c.strip() for c in spec.split(",") if c.strip()]:
        m = re.match(r"(>=|<=|==|>|<)\s*([\d.]+)$", clause)
        if not m:
            return None
        op, bound = m.groups()
        a, b = version_tuple(version), version_tuple(bound)
        b = b + (0,) * (len(a) - len(b))
        if not {">=": a >= b, "<=": a <= b, "==": a == b, ">": a > b, "<": a < b}[op]:
            return False
    return True


def check_catalog():
    path = ROOT / "catalog.yaml"
    if not path.is_file():
        err("catalog.yaml missing")
        return
    c = yaml.safe_load(path.read_text()) or {}
    if not SEMVER.match(str(c.get("version", ""))):
        err(f"catalog.yaml: version '{c.get('version')}' is not MAJOR.MINOR.PATCH")
    for key in ("requires_platform", "requires_verify"):
        if not c.get(key):
            err(f"catalog.yaml: {key} missing")
    # Optional, but a non-string (YAML reads a bare 1.3 as a float) makes the
    # platform refuse the release at parse time instead of showing it.
    if "verify_tested" in c and not isinstance(c["verify_tested"], str):
        err(f"catalog.yaml: verify_tested '{c['verify_tested']}' must be a quoted string, e.g. \"1.3.0\"")
    pin = None
    req = ROOT / "requirements-verify.txt"
    if req.is_file():
        for line in req.read_text().splitlines():
            m = re.match(r"\s*bheembhai-verify\s*==\s*([\d.]+)", line)
            if m:
                pin = m.group(1)
    if pin is None:
        print("note: requirements-verify.txt has no active bheembhai-verify pin yet; tier 2 is skipped")
    elif c.get("requires_verify") and satisfies(pin, c["requires_verify"]) is False:
        err(f"requirements-verify.txt pins bheembhai-verify {pin}, outside catalog.yaml requires_verify '{c['requires_verify']}'")


def main():
    check_config(check_skills())
    check_catalog()
    known = set()
    if KNOWN.is_file():
        known = {l.strip() for l in KNOWN.read_text().splitlines() if l.strip() and not l.startswith("#")}
    new = [e for e in errors if e not in known]
    for e in errors:
        print(("known: " if e in known else "ERROR: ") + e)
    for k in sorted(known - set(errors)):
        print(f"fixed: '{k}' no longer occurs; remove it from tools/known-issues.txt")
    print(f"{len(new)} error(s), {len(errors) - len(new)} known issue(s)")
    return 1 if new else 0


if __name__ == "__main__":
    sys.exit(main())
