"""AR-6 evidence and report numbers.

`python docs/arch/AR-6/report.py --collect` saves the census (`tools/identity_lint.py` at HEAD), the Lean files that
compute each allowlisted domain, and the batch's commits (`main..HEAD --no-merges`). `metrics()` renders REPORT.md's
generated block from the saved files only, so the report stays true after syncs with `main` and after the merge.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "docs/arch/AR-6"
EVIDENCE = HERE / "evidence"
PLAN_BASE = "c24aeab2"


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def stem(domain: str) -> str:
    """The domain as Lean source writes it, up to its first computed part."""
    return domain.split("{", 1)[0].replace("\n", "\\n")


def collect() -> None:
    sys.path.insert(0, str(ROOT))
    from tools import identity_lint
    found = identity_lint.tree_sites()
    entries = json.loads(identity_lint.ALLOWLIST.read_text())
    assert identity_lint.problems(found, entries) == []
    head = _git("rev-parse", "HEAD").strip()
    census = {"commit": head, **identity_lint.census(found, entries), "entries": entries,
              "lines": [[site.path, site.line, site.scope, site.domain] for site in found]}
    lean = {}
    for domain in sorted({e["domain"] for e in entries}):
        listed = subprocess.run(["git", "grep", "-l", "-F", stem(domain), head, "--", "lean/VE"], cwd=ROOT,
                                capture_output=True, text=True)
        lean[domain] = sorted(line.split(":", 1)[1] for line in listed.stdout.splitlines())
    base = _git("merge-base", "HEAD", "main").strip()
    commits = [dict(zip(("hash", "subject"), line.split(" ", 1)))
               for line in _git("log", "--no-merges", "--format=%H %s", f"{base}..HEAD").splitlines()]
    files = sorted(_git("diff", "--name-only", f"{base}..HEAD").split())
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / "census.json").write_text(json.dumps(census, indent=1, ensure_ascii=False) + "\n")
    (EVIDENCE / "lean-domains.json").write_text(json.dumps({"commit": head, "domains": lean}, indent=1) + "\n")
    (EVIDENCE / "scope.json").write_text(json.dumps({"base": base, "plan_base": PLAN_BASE, "head": head,
                                                     "commits": commits, "files": files}, indent=1) + "\n")


def metrics() -> str:
    """REPORT.md's generated block, from the saved evidence."""
    census = json.loads((EVIDENCE / "census.json").read_text())
    lean = json.loads((EVIDENCE / "lean-domains.json").read_text())["domains"]
    scope = json.loads((EVIDENCE / "scope.json").read_text())
    mutants = json.loads((EVIDENCE / "mutants.json").read_text())
    rows = ["| Owner | Removed by or record | Sites |", "|---|---|---:|"]
    rows += [f"| Lean | {k} | {v} |" for k, v in census["by_remover"].items()]
    rows += [f"| Python | {k} | {v} |" for k, v in census["by_record"].items()]
    owners = {}
    for e in census["entries"]:
        owners.setdefault(e["domain"], set()).add(e["owner"])
    domains = ["| Domain | Sites | Owner | Lean files whose source holds the domain text |", "|---|---:|---|---|"]
    for domain, n in census["by_domain"].items():
        files = lean[domain]
        shown = ", ".join(f"`{f}`" for f in files[:2]) + (f" and {len(files) - 2} more" if len(files) > 2 else "")
        domains.append(f"| `{domain.encode('unicode_escape').decode()}` | {n} | {'/'.join(sorted(owners[domain]))} "
                       f"| {shown or 'none'} |")
    no_lean = sorted(d for d in lean if not lean[d] and owners[d] == {"lean"})
    return "\n".join([
        f"Census at `{census['commit'][:8]}` (`tools/identity_lint.py --json`): **{census['sites']} identity sites in "
        f"{census['modules']} modules**, every one allowlisted; **{census['lean_owned']} Lean-owned** in "
        f"{census['lean_modules']} modules, {census['python_owned']} Python-owned records; "
        f"{census['relayed_sites']} in relayed modules.",
        "",
        *rows,
        "",
        *domains,
        "",
        "Lean-owned domains that no Lean file holds yet: "
        + (", ".join(f"`{d.encode('unicode_escape').decode()}`" for d in no_lean) or "none") + ".",
        "",
        f"Commits (`main..HEAD --no-merges`, base `{scope['base'][:8]}`): {len(scope['commits'])}; files changed: "
        f"{len(scope['files'])}, none under `ve/` or `lean/`: "
        f"{'yes' if not any(f.startswith(('ve/', 'lean/')) for f in scope['files']) else 'NO'}.",
        f"Seeded faults: {len(mutants)}, each failing its named test: "
        f"{'yes' if all(m['exit_code'] != 0 and '1 failed' in m['failure_excerpt'] for m in mutants) else 'NO'}.",
    ])


def render() -> None:
    """Write `metrics()` into REPORT.md's generated block."""
    path = HERE / "REPORT.md"
    head, rest = path.read_text().split("<!-- BEGIN GENERATED AR-6 METRICS -->\n", 1)
    tail = rest.split("<!-- END GENERATED AR-6 METRICS -->", 1)[1]
    path.write_text(f"{head}<!-- BEGIN GENERATED AR-6 METRICS -->\n{metrics()}\n<!-- END GENERATED AR-6 METRICS -->{tail}")


if __name__ == "__main__":
    if sys.argv[1:] == ["--collect"]:
        collect()
    render()
    print(metrics())
