"""Check batch 16d's committed measurements without consulting live git state."""
from __future__ import annotations

from collections import Counter
import gzip
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "docs/lean-first/b16d"
EVIDENCE = HERE / "evidence"


def saved(name):
    path = EVIDENCE / name
    return json.loads(gzip.decompress(path.read_bytes()) if name.endswith(".gz") else path.read_text())


def report():
    spec = importlib.util.spec_from_file_location("b16d_report", HERE / "report.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_every_residue_and_count_comes_from_saved_ledger():
    cases = saved("cases.json.gz")
    share = saved("share.json")
    old = json.loads(gzip.decompress((ROOT / "docs/lean-first/b16c/evidence/residues.json.gz").read_bytes()))
    assert len(cases) == 1010 + 904 + 339
    assert len({(r["corpus"], r["case"]) for r in cases}) == len(cases)
    assert all(set(r) == {"corpus", "case", "source_sha256", "decision"} |
               ({"cause", "prior_error"} if r["decision"] == "retained" else set()) for r in cases)
    assert all(len(r["source_sha256"]) == 64 for r in cases)
    for name in share:
        rows = [r for r in cases if r["corpus"] == name]
        assert share[name] == {"documents": len(rows), **dict(Counter(r["decision"] for r in rows))}
    assert share["norm_defaults"] == {"documents": 1010, "ok": 1000, "error": 10}
    assert share["pilots"] == {"documents": 339, "ok": 339}
    assert share["document"]["documents"] == 904
    assert all(r["prior_error"]["code"] not in ("CheckerUnavailable", "ResourceLimit") and
               r["cause"].startswith("CheckerUnavailable:") for r in cases if r["decision"] == "retained")
    wanted = {(r["corpus"], r["case"]): r["source_sha256"] for r in old if
              r["corpus"] == "norm_defaults" or
              r["corpus"] in ("pilots", "document") and r["cause"] ==
              "retained: document checks under norm-defaults@0 need its Lean profile route"}
    assert {(r["corpus"], r["case"]): r["source_sha256"] for r in cases} == wanted


def test_scope_mutants_and_gate_are_saved():
    mutants = saved("mutants.json")
    assert len(mutants) >= 3 and len({m["bug"] for m in mutants}) == len(mutants)
    assert all(m["exit_code"] != 0 and "1 failed" in m["failure_excerpt"] for m in mutants)
    if not (EVIDENCE / "scope.json").exists():
        return  # The code-commit gate precedes its captured scope.
    scope = saved("scope.json")
    assert len(scope["base"]) == len(scope["head"]) == 40 and scope["base"] != scope["head"]
    assert scope["command"] == "git log main..HEAD --no-merges"
    assert scope["commits"] and scope["commits"][0]["hash"] == scope["head"]
    assert len({c["hash"] for c in scope["commits"]}) == len(scope["commits"])
    assert all(set(c) == {"hash", "subject"} and len(c["hash"]) == 40 and c["subject"]
               for c in scope["commits"])
    assert scope["changes"]
    assert all(set(c) == {"added", "deleted", "path"} and c["path"] and
               (all(n.isdecimal() for n in (c["added"], c["deleted"])) or
                (c["added"], c["deleted"]) == ("-", "-")) for c in scope["changes"])
    if not (EVIDENCE / "gate.json").exists():
        return  # The code-commit gate precedes its own captured result.
    gate = saved("gate.json")
    assert gate["commit_sha"] == scope["head"] and gate["dirty"] is False
    assert gate["status"] == "passed" and gate["failures"] == []
    counts = gate["counts"]
    assert counts["passed"] + counts["skipped"] + counts["failed"] == counts["selected"]
    assert counts["selected"] + counts["deselected"] == counts["collected"]


def test_nine_corpus_comparison_and_report_are_saved():
    ab = saved("ab.json")
    assert set(ab["records"]) == {f"{name}/{a}" for name in
        ("probe", "conformance", "quantity") for a in ("python", "lean")} | {
        f"{name}/default" for name in ("pilots", "readings", "discourse", "rights", "norm_defaults", "document")}
    assert ab["unlisted"] == 0
    assert sum(ab["totals"].values()) == sum(ab["records"].values())
    assert len(ab["differences"]) == sum(v for k, v in ab["totals"].items() if k != "same")
    assert all(r["listed"] for r in ab["differences"])
    for row in ab["differences"]:
        if row["corpus"] in ("norm_defaults", "document"):
            assert "raised" in row["base"] and "raised" in row["head"]
        else:
            assert row["corpus"] == "pilots" and row["class"] == "wording"
            assert all("Cannot read sense pack" in str(row[side]) for side in ("base", "head"))
    if not (EVIDENCE / "gate.json").exists():
        return  # The report is generated after the code-commit gate finishes.
    delta = (HERE / "DELTA.md").read_text()
    generated = delta.split("<!-- BEGIN GENERATED B16D METRICS -->\n", 1)[1].split(
        "\n<!-- END GENERATED B16D METRICS -->", 1)[0]
    assert generated == report().metrics()
