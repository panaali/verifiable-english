#!/usr/bin/env python3
"""arch-decoder-measure: write MEASURE.json from tools/trust_map.py and the saved evidence.

Measurement only (no product change). Reads:

* tools/trust_map.py `walk` on the pinned main (`extract_rev`, the commit's own `lean/` and side
  table) and on this checkout: every declaration's class, tie and line range;
* evidence/deps.json: the compiled environment's reach of `decodeClosureTrace` and the part of it
  nothing else uses (deps.lean);
* evidence/kernel-cut.json: tools/kernel_closure.py's kernel total with the decoder cut (kernel_cut.py);
* switch.lean: the switch written out (not in the tree); its declarations are counted here by the
  trust map's line rule (a declaration runs from its docstring to the line before the next one).

    uv run python docs/arch/arch-decoder-measure/measure.py           # write MEASURE.json
    uv run python docs/arch/arch-decoder-measure/measure.py --check   # exit 1 unless MEASURE.json is what it writes
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import trust_map  # noqa: E402

PINNED = "f97dd2d0c03689334abab42b0a6b5a3211b890db"
OUT = HERE / "MEASURE.json"
EVIDENCE = HERE / "evidence"
ROOT_DECL = "VE.CertificateWire.decodeClosureTrace"

# Declarations a switch touches or reads; their class and size are reported for context.
CONTEXT = [
    ROOT_DECL,
    "VE.CertificateWire.decodeClosureCertificate",
    "VE.Closure.Bridge.decodeFormula",
    "VE.Closure.Bridge.formulaNodes",
    "VE.Closure.Bridge.decodeKind",
    "VE.Closure.Tableau.extraRule",
    "VE.Core.Bridge.decodeFormula",
    "VE.Core.Bridge.formulaNodes",
    "VE.Core.Wire.decodeTrace",
    "VE.Core.Wire.decodeCertificate",
    "VE.Closure.CoreEquiv.embedTrace",
    "VE.Closure.CoreEquiv.embedTraces",
    "VE.Closure.CoreEquiv.decodeTrace_ne_embed",
]

BOUNDARY = re.compile(r"^(?:/--|/-!|def |theorem |abbrev |mutual\b|end\b|#guard|example\b|section\b|open\b|namespace\b)")
NAMED = re.compile(r"^(?:def|theorem|abbrev) ([A-Za-z_][A-Za-z_0-9.]*)")

# Part B of switch.lean: what the tree would hold after a switch, and what each piece replaces.
SWITCH_CODE = {
    "decodeFormulaWith": {"replaces": "VE.Core.Bridge.decodeFormula", "file": "VE/Core/Bridge.lean"},
    "decodeTraceWith": {"replaces": "VE.Core.Wire.decodeTrace", "file": "VE/Core/Wire.lean"},
    "unembedFormula": {"replaces": None, "file": "VE/CertificateWire.lean"},
    "unembedTrace": {"replaces": None, "file": "VE/CertificateWire.lean"},
    "unembedTraces": {"replaces": None, "file": "VE/CertificateWire.lean"},
    "decodeClosureTraceViaCore": {"replaces": ROOT_DECL, "file": "VE/CertificateWire.lean"},
}
TRUSTED_STATEMENTS = ["switch_eq", "core_unchanged_formula", "core_unchanged_trace"]
OBLIGATIONS = ["decodeFormulaWith_false", "formulaNodes_embed", "decodeTraceWith_false",
               "unembedFormula_embed", "unembedTrace_embed", "unembedTraces_embed"]
# Proof lines not written (the proof is `sorry` in switch.lean): an ESTIMATE, low and high.
PROOF_ESTIMATE = {
    "decodeFormulaWith_false": [60, 120],
    "decodeTraceWith_false": [50, 100],
    "switch_eq": [5, 15],
    "core_unchanged_formula": [0, 2],
    "core_unchanged_trace": [0, 2],
}


def classified(root: Path, table: Path | None = None, statements: Path | None = None) -> dict:
    decls, _, problems = (trust_map.walk(root) if table is None else trust_map.walk(root, table, statements))
    if problems:
        raise SystemExit(f"trust_map problems at {root}: {problems[:3]}")
    return {d.decl.name: d for d in decls}


def row(d) -> dict:
    return {"file": d.module, "start": d.decl.start, "end": d.decl.end, "lines": d.decl.lines, "class": d.cls,
            "tied": d.tied, "trusted": d.trusted}


def by_class(rows: list[dict]) -> dict:
    """Per file: lines by the task's classes D, S, V (untied verdict-bearing D or G), K, and trusted."""
    out: dict[str, dict[str, int]] = {}
    for r in rows:
        c = out.setdefault(r["file"], {"K": 0, "S": 0, "D": 0, "V": 0, "trusted": 0, "untrusted": 0})
        cls = r["class"]
        if cls in ("K", "S"):
            c[cls] += r["lines"]
        if cls.startswith("D"):
            c["D"] += r["lines"]
        if cls in ("D[V]", "G[V]") and not r["tied"]:
            c["V"] += r["lines"]
        c["trusted" if r["trusted"] else "untrusted"] += r["lines"]
    return out


def text_declarations(path: Path) -> dict[str, dict]:
    """Declarations of a Lean text by the trust map's line rule; theorems split at `:= by`."""
    lines = path.read_text().splitlines()
    starts = []
    for i, line in enumerate(lines):
        if BOUNDARY.match(line):
            starts.append(i)
    out = {}
    for k, i in enumerate(starts):
        m = NAMED.match(lines[i])
        if not m:
            continue
        begin = starts[k - 1] if k > 0 and lines[starts[k - 1]].startswith("/--") else i
        nxt = next((s for s in starts[k + 1:]), len(lines))
        body = lines[begin:nxt]
        rec = {"start": begin + 1, "end": nxt, "lines": nxt - begin,
               "nonblank": sum(1 for x in body if x.strip())}
        if lines[i].startswith("theorem "):
            stop = next(j for j in range(i, nxt) if lines[j].rstrip().endswith((":= by", ":="))
                        or lines[j + 1].startswith("  |"))
            rec["statement_lines"] = stop - begin + 1
            proof = [x for x in lines[stop + 1:nxt] if x.strip()]
            rec["proof_lines"] = len(proof)
            rec["proved"] = proof != ["  sorry"]
        out[m.group(1)] = rec
    return out


def build() -> dict:
    with tempfile.TemporaryDirectory() as scratch:
        tree = Path(scratch)
        problem = trust_map.extract_rev(PINNED, tree, ROOT)
        if problem:
            raise SystemExit(problem)
        pinned = classified(tree, *trust_map.rev_paths(tree))
        pinned_files, _ = trust_map.measure(tree, *trust_map.rev_paths(tree))
    head = classified(ROOT)
    head_files, _ = trust_map.measure(ROOT)

    deps = json.loads((EVIDENCE / "deps.json").read_text())
    exclusive = [e["name"] for e in deps["exclusive"]]
    removable = [row(pinned[n]) | {"name": n} for n in exclusive if n in pinned]
    same_at_head = all(row(pinned[n]) == row(head[n]) for n in CONTEXT)

    text = text_declarations(HERE / "switch.lean")
    code = {}
    for name, meta in SWITCH_CODE.items():
        t = text[name]
        old = pinned[meta["replaces"]].decl.lines if meta["replaces"] else 0
        code[name] = {**meta, "lines": t["lines"], "nonblank": t["nonblank"], "old_lines": old,
                      "added": t["lines"] - old}
    added_code = sum(c["added"] for c in code.values())
    statements = {n: {k: text[n][k] for k in ("statement_lines", "proof_lines", "proved")}
                  for n in TRUSTED_STATEMENTS}
    obligations = {n: {k: text[n][k] for k in ("statement_lines", "proof_lines", "proved")} for n in OBLIGATIONS}
    measured_proof = sum(v["proof_lines"] for v in obligations.values() if v["proved"])
    estimate = [sum(v[0] for v in PROOF_ESTIMATE.values()), sum(v[1] for v in PROOF_ESTIMATE.values())]

    cut = json.loads((EVIDENCE / "kernel-cut.json").read_text())
    kernel_new = {n: text[n]["nonblank"] for n in ("unembedFormula", "unembedTrace", "unembedTraces",
                                                    "decodeClosureTraceViaCore")}
    kernel_core_growth = sum(max(code[n]["added"], 0) for n in ("decodeFormulaWith", "decodeTraceWith"))
    kernel_added = sum(kernel_new.values()) + kernel_core_growth

    return {
        "comment": "arch-decoder-measure (measurement only). Generated by measure.py; see REPORT.md.",
        "pinned": PINNED,
        "decls_identical_at_head": same_at_head,
        "trust_budget": {"pinned": trust_map.budget(trust_map.totals(pinned_files)),
                         "head": trust_map.budget(trust_map.totals(head_files))},
        "context": {n: row(pinned[n]) for n in CONTEXT},
        "removable": {"declarations": removable, "by_file": by_class(removable),
                      "reach": len(deps["reach"]), "kept_by_other_users": len(deps["kept_by_outside_users"]),
                      "root_users": [e["name"] for e in deps["root_users"]]},
        "switch": {
            "code": code,
            "trusted_code_delta_text": added_code,
            "trusted_statements": statements,
            "trusted_statement_lines": sum(v["statement_lines"] for v in statements.values()),
            "obligations": obligations,
            "audited_proof_lines_measured": measured_proof,
            "audited_proof_lines_ESTIMATE": {"per_statement": PROOF_ESTIMATE, "total": estimate},
        },
        "kernel": {
            "before": cut["before"]["kernel_lines"],
            "decoder_cut_MEASURED": cut["kernel_delta"],
            "path_deltas_MEASURED": cut["path_deltas"],
            "kernel_paths_reaching_decoder": sorted(n for n in cut["path_deltas"]
                                                    if cut["before"]["paths"][n]["tier"] == "kernel"),
            "switch_additions_ESTIMATE": {"new": kernel_new, "core_growth": kernel_core_growth,
                                          "total": kernel_added},
            "switch_net_ESTIMATE": cut["kernel_delta"] + kernel_added,
        },
    }


def render(data: dict) -> str:
    return json.dumps(data, indent=1, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    text = render(build())
    if "--check" in argv:
        if OUT.read_text() != text:
            print("MEASURE.json is not what measure.py writes now")
            return 1
        print("MEASURE.json is current")
        return 0
    OUT.write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
