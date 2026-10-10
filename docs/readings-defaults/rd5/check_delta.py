"""Check RD-5's DELTA.md against its saved evidence (DRI-RULINGS R11, D4: checked at the gate and the merge).

    uv run --frozen python docs/readings-defaults/rd5/check_delta.py

Every figure the DELTA states is recomputed from the saved files (the pilot's `metrics.json` and `unmigrated.json`,
and `evidence/scope.json`, `mutants.json`, `ab-summary.json` and, once the gate has run, `gate.json`) and must appear
in the DELTA as written. Exit 1 lists each figure that does not.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = ROOT / "usecases/udhr-pilot/run-20261010T1400Z"
EVIDENCE = HERE / "evidence"


def load(path):
    return json.loads(Path(path).read_text())


def expected():
    m, u = load(RUN / "metrics.json"), load(RUN / "unmigrated.json")
    scope, mutants, ab = load(EVIDENCE / "scope.json"), load(EVIDENCE / "mutants.json"), load(EVIDENCE / "ab-summary.json")
    after, before, w, c = m["after"]["share"], m["before"]["share"], m["witnesses"], m["components"]
    sets = u["sets"]
    out = [
        f"{sets} reading sets", f"Lean admitted {len(u['migrated'])}",
        f"({m['migration']['situations_recorded']} situations, {len(m['migration']['unseparated_pairs'])} unseparated",
        f"Lean's split refused {len(u['not_migrated'])}",
        f"CONFLICT-FREE over {c['count']} components" if m["after"]["conflict"] == "CONFLICT-FREE" else "?",
        f"{w['in_components_same']} of {w['in_components_total']} status witnesses",
        f"All {w['companions_alone']} companions re-checked alone",
        f"{w['alone_same']} of {w['alone_total']} of their witnesses",
        f"from {before['decided_bytes']} bytes ({before['decided_share_percent']}%) to {after['decided_bytes']:,} of "
        f"{after['source_bytes']:,} bytes ({after['decided_share_percent']}%) in {len(after['decided_units'])} units",
        f"{after['decided_bytes_checked_outside']:,} of those bytes",
        f"holds {c['max_rules_in_one_choice_document']} rules ({c['max_author_rules_in_one_choice_document']} written",
    ]
    q = {x["name"]: x["verdict"] for x in m["queries"]}
    out.append(f"`rs_u029` {q['u029-recognise']}; `rs_u081` {q['u081-secure']}, then {q['u081-secure-under-2']} under "
               f"`--under rs_u081:2`; `rs_u081` {q['u081-none']}")
    report = load(RUN / "reports/after.check.json")["readings"]
    pairs = [p["wording"] for s in report["sets"] for p in s["pairs"]]
    out.append(f"{pairs.count('E24')} of the migrated UDHR's {len(pairs)} pair sentences are E24")
    pc = ab["probe_conformance"]
    out.append(f"{sum(pc['records'].values()):,} records (probe {pc['records']['probe/python']:,} per authority, "
               f"conformance {pc['records']['conformance/python']:,} per authority), all")
    out.append(f"{pc['unlisted']} unlisted")
    total = sum(ab["records"].values())
    t = ab["totals"]
    out.append(f"{total:,} records ({ab['records']['pilots/default']} pilot documents, "
               f"{ab['records']['readings/default']:,} readings cases). {t['same']:,} same. The "
               f"{len(ab['differences'])} differences")
    out.append(f"are {t['availability']} availability, {t['unavailable']} unavailable on both sides and "
               f"{t['wording']} wording")
    first = sum(d["rerun"] == "ab-rerun.json.gz" and d["rerun_equal"] for d in ab["differences"])
    last = sum(d["rerun"] == "ab-rerun-rust600.json.gz" and d["rerun_equal"] for d in ab["differences"])
    out.append(f"{first} are equal")
    out.append(f"the last {last} are equal with the Rust checker's limit raised")
    if all(d["rerun_equal"] for d in ab["differences"]):
        out.append(f"All {len(ab['differences'])} are equal")
    rows = mutants["mutants"]
    if all(r["failed"] and r["sha256_before"] == r["sha256_restored"] for r in rows):
        out += [f"| `{r['name']}` | `{r['file']}` | `{r['test']}` |" for r in rows]
    out.append(f"**{len(scope['commits'])} commits**")
    out.append(f"{scope['files_changed']} files, **{scope['insertions']:,} lines added**, **{scope['deletions']} deleted**")
    out.append(", ".join(f"`{c[:8]}`" for c in scope["commits"]))
    gate = EVIDENCE / "gate.json"
    if gate.exists():
        g = load(gate)
        out.append(f"`{g['commit_sha'][:8]}`")
        out.append(f"**{g['counts']['passed']:,} Python passed**")
    return out


def main():
    text = (HERE / "DELTA.md").read_text()
    text = " ".join(text.split())
    missing = [e for e in expected() if " ".join(e.split()) not in text]
    for e in missing:
        print("not in DELTA.md:", e)
    print("DELTA.md matches the saved evidence" if not missing else f"{len(missing)} figures differ")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
