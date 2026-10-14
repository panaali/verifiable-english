#!/usr/bin/env python3
"""PS-0p dry run (presupposition-PLAN 6, PS-0p steps 3 and 6; checks F1-F6 of docs/research/presupposition-phase1.md 1.4).

The pinned translation is copied, never edited. Scratch documents are written under a work directory (default
/tmp/ps0p); the evidence this script keeps is written to docs/research/evidence/presupposition/dryrun.json, with
the scratch translation's front matter delta and fences in dryrun-scratch-delta.json.

Run under the memory limit, from the repository root (`ve` runs as a child and inherits it):

    VE_RUST_TIMEOUT=600 prlimit --as=6442450944 uv run python research/presupposition/ps0p_dryrun.py

VE_RUST_TIMEOUT: the Rust accelerator times out at its 5 s default on the pinned translation itself
(CheckerUnavailable); the raised limit is bounded by the 6 GiB address-space limit (see the results doc, 2.3).
"""
from __future__ import annotations

import copy
import json
import os
import re
import resource
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ve.document import load_document  # noqa: E402

RUN = Path("/home/seyran/code/manage-agents/pilots/claude-constitution/run-20261012T1800Z")
WORK = Path(os.environ.get("PS0P_WORK", "/tmp/ps0p"))
OUT = ROOT / "docs/research/evidence/presupposition"

PREDICATES = {
    "core_value_of": (["entity", "entity"], "{0} is a core value of {1}", "The first entity is a core value of the second."),
    "guideline_of": (["entity", "entity"], "{0} is a guideline of {1}", "The first entity is a guideline of the second."),
    "open_problem": (["entity"], "{0} is an open problem", "The entity is an open problem."),
    "mission_of": (["entity", "entity"], "{0} is a mission of {1}", "The first entity is a mission of the second."),
    "nature_of": (["entity", "entity"], "{0} is a nature of {1}", "The first entity is a nature of the second."),
}
CONSTANT = ("anthropic", {"sort": "entity", "description": "Anthropic in the source."})

V0 = ["var", 0]


def b(p, c):
    return ["binary", p, ["var", 0], ["const", c]]


def unique(d_x, d_y):
    return ["exists", "entity", ["and", d_x, ["forall", "entity", ["implies", d_y, ["eq", ["var", 0], ["var", 1]]]]]]


# Class A (plan PS-0p step 3): unit, fence, the exact formula of 1.3's "exactly the existence" check.
CLASS_A = {
    "u0013.presupposition": ("Some entity is a core value of Claude.", ["exists", "entity", b("core_value_of", "claude")]),
    "u0095.presupposition": ("Some entity is a guideline of Anthropic.", ["exists", "entity", b("guideline_of", "anthropic")]),
    "u0286.presupposition": ("Some entity is an open problem.", ["exists", "entity", ["unary", "open_problem", V0]]),
    "u0002.presupposition": ("Some entity is a mission of Anthropic, and every entity that is a mission of Anthropic is that entity.",
                             unique(b("mission_of", "anthropic"), b("mission_of", "anthropic"))),
    "u0235.presupposition": ("Some entity is a nature of Claude, and every entity that is a nature of Claude is that entity.",
                             unique(b("nature_of", "claude"), b("nature_of", "claude"))),
}
EXPLORATORY = ("u0002.presupposition", "Exactly one entity is a mission of Anthropic.")
FORBIDDEN = re.compile(r"\b(?:desired|relevant|must|should)\b", re.I)
ID_KEY = re.compile(r"(?:^|_)(?:id|hash)$")
HEX64 = re.compile(r"\b[0-9a-f]{64}\b")
AS_CAP = 6442450944  # prlimit --as, bytes (6 GiB); every `ve` child inherits it


def require_cap() -> None:
    soft, _hard = resource.getrlimit(resource.RLIMIT_AS)
    if soft == resource.RLIM_INFINITY or soft > AS_CAP:
        sys.exit(f"refused: run under prlimit --as={AS_CAP} (RLIMIT_AS soft limit is {soft})")


def limits() -> dict:
    """The address-space limit this process (and so every `ve` child) runs under, the Rust time limit, and the
    largest resident set of any waited-for descendant so far (Linux ru_maxrss of RUSAGE_CHILDREN, KiB)."""
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    return {"rlimit_as_soft": soft, "rlimit_as_hard": hard, "VE_RUST_TIMEOUT": os.environ.get("VE_RUST_TIMEOUT"),
            "children_peak_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            "self_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


def split(path: Path):
    lines = path.read_text().split("\n")
    assert lines[0] == "---" and lines[2] == "---", "unexpected front matter layout"
    return json.loads(lines[1]), "\n".join(lines[3:])


def write_doc(path: Path, meta: dict, body: str) -> Path:
    path.write_text("---\n" + json.dumps(meta, ensure_ascii=False) + "\n---\n" + body)
    return path


def with_vocabulary(meta: dict) -> dict:
    meta = copy.deepcopy(meta)
    voc = meta["environment"]["vocabulary"]
    for name, (args, verb, desc) in PREDICATES.items():
        assert name not in voc["predicates"]
        voc["predicates"][name] = {"arguments": args, "description": desc, "verbalisation": verb}
    assert CONSTANT[0] not in voc["constants"]
    voc["constants"][CONSTANT[0]] = CONSTANT[1]
    return meta


def convert(meta: dict, body: str, fences: dict[str, str]):
    """The scratch form of step 3: each unit in `fences` becomes u0248's form, its fence appended after the last."""
    meta = copy.deepcopy(meta)
    for i, u in enumerate(meta["units"]):
        if u["id"] in fences:
            meta["units"][i] = {"id": u["id"], "span": u["span"], "support": "assumption", "kind": "asserted",
                                "meaning": "specified", "content": {"fence": u["id"]}, "surface": "english"}
    assert sum(u["id"] in fences for u in meta["units"]) == len(fences)
    tail = "".join(f"```ve {uid}\n{text}\n```\n" for uid, text in fences.items())
    body = body if body.endswith("\n") else body + "\n"
    return meta, body + tail


def ve(*args, out: Path | None = None) -> dict:
    p = subprocess.run([sys.executable, "-m", "ve", *map(str, args)], cwd=ROOT, capture_output=True, text=True)
    if out is not None:
        out.write_text(p.stdout)
    return {"returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr[-2000:]}


def load_units(path: Path, ids) -> dict:
    """The product's own reading of the scratch document (`ve.document.load_document`): each unit's
    status, content and meaning id, or the loader's error."""
    try:
        doc = load_document(path)
    except Exception as e:  # the loader's refusal is the measurement
        return {"error": f"{type(e).__name__}: {e}"}
    by_id = {u["id"]: u for u in doc["units"]}
    return {i: {k: by_id[i].get(k) for k in ("status", "kind", "support", "content", "meaning_id")} for i in ids}


def normalise(value):
    """Identity values a new unit or predicate necessarily changes (1.3, probe comparison)."""
    if isinstance(value, dict):
        return {k: ("<id>" if ID_KEY.search(k) and isinstance(v, str) else normalise(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [normalise(v) for v in value]
    if isinstance(value, str):
        return HEX64.sub("<hex>", value)
    return value


def status_bytes(check: dict) -> dict:
    return check["coverage"]["bytes_by_status"]


def readings_summary(check: dict) -> dict:
    r = check["readings"]
    return {"choice_count": r["choice_count"], "choices_checked": r["choices_checked"],
            "conflict_status": r["conflict"]["status"],
            "choices_conflict_free": sum(1 for c in r["conflict"].get("choices", [])
                                         if c.get("status", r["conflict"]["status"]) == "CONFLICT-FREE"),
            "status": r["status"]}


def rendered_reading(render_text: str, sentence_source: str) -> str | None:
    """The "Checked reading:" line that `ve document render` writes under a unit's source text."""
    lines = render_text.split("\n")
    for i, line in enumerate(lines):
        if line.strip() == sentence_source.strip():
            for nxt in lines[i + 1:i + 4]:
                if nxt.startswith("Checked reading: "):
                    return nxt[len("Checked reading: "):].strip()
    return None


def main() -> int:
    require_cap()
    WORK.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    pinned = WORK / "pinned.ve.md"
    pinned.write_bytes((RUN / "translation.ve.md").read_bytes())
    meta, body = split(pinned)
    result = {"run": "20261012T1800Z", "definitions": "docs/research/presupposition-phase1.md 1.3-1.4",
              "rust_timeout": os.environ.get("VE_RUST_TIMEOUT"), "limits_at_start": limits(), "checks": []}

    # Pinned, under this binary: the control.
    pc = ve("document", "check", pinned, out=WORK / "pinned-check.json")
    pinned_check = json.loads(pc["stdout"])
    result["pinned_check"] = {"returncode": pc["returncode"],
                              "identical_to_pinned_record": pc["stdout"] == (RUN / "check.json").read_text(),
                              "bytes_by_status": status_bytes(pinned_check), "readings": readings_summary(pinned_check)}

    # Per unit (F1, F2): the product's loader on vocabulary + one converted unit.
    vmeta = with_vocabulary(meta)
    per_unit = {}
    for uid, (fence, expected) in CLASS_A.items():
        m, bd = convert(vmeta, body, {uid: fence})
        got = load_units(write_doc(WORK / f"unit-{uid}.ve.md", m, bd), [uid])
        row = {"fence": fence, "expected_formula": expected, "loader": got}
        if "error" not in got:
            u = got[uid]
            row["exact"] = u["content"] == expected
            row["forbidden_words"] = FORBIDDEN.findall(fence)
            row["status"] = u["status"]
        per_unit[uid] = row
    result["per_unit"] = per_unit
    if "error" in per_unit[EXPLORATORY[0]]["loader"] or not per_unit[EXPLORATORY[0]].get("exact"):
        uid, fence = EXPLORATORY
        m, bd = convert(vmeta, body, {uid: fence})
        result["exploratory_u0002"] = {"fence": fence, "never_counted": True,
                                       "loader": load_units(write_doc(WORK / "exploratory-u0002.ve.md", m, bd), [uid])}

    admitted = {u: CLASS_A[u][0] for u, r in per_unit.items()
                if "error" not in r["loader"] and r.get("exact") and not r.get("forbidden_words")}

    # Vocabulary only (control for F3/F4/F6), and the full scratch translation.
    v0 = write_doc(WORK / "vocabulary-only.ve.md", vmeta, body)
    v0c = ve("document", "check", v0, out=WORK / "vocabulary-only-check.json")
    sm, sb = convert(vmeta, body, admitted)
    scratch = write_doc(WORK / "scratch.ve.md", sm, sb)
    sc = ve("document", "check", scratch, out=WORK / "scratch-check.json")
    result["vocabulary_only_check"] = {"returncode": v0c["returncode"], "stderr": v0c["stderr"]}
    result["scratch_check"] = {"returncode": sc["returncode"], "stderr": sc["stderr"], "converted": sorted(admitted)}
    try:
        v0_check, scratch_check = json.loads(v0c["stdout"]), json.loads(sc["stdout"])
    except json.JSONDecodeError:
        v0_check = scratch_check = None

    # Round trip: render the scratch translation, refit each new fence with its rendering, and reload.
    rd = ve("document", "render", scratch, out=WORK / "scratch-render.md")
    trip = {}
    source =(RUN.parent / "source/claude-constitution.md").read_bytes()
    for uid in admitted:
        a, z = next(u["span"] for u in meta["units"] if u["id"] == uid)
        words = source[a:z].decode("utf-8")
        trip[uid] = {"source_words": words, "rendered": rendered_reading(rd["stdout"], words)}
    if all(t["rendered"] for t in trip.values()) and admitted:
        rm, rb = convert(vmeta, body, {u: t["rendered"] for u, t in trip.items()})
        again = load_units(write_doc(WORK / "roundtrip.ve.md", rm, rb), list(admitted))
        first = load_units(scratch, list(admitted))
        for uid in admitted:
            trip[uid]["same_formula"] = ("error" not in again and "error" not in first
                                         and again[uid]["content"] == first[uid]["content"])
        if "error" in again:
            result["roundtrip_error"] = again["error"]
    result["roundtrip"] = trip

    # F1, F2.
    def f_ok(ids):
        return {u: bool(per_unit[u].get("exact") and not per_unit[u].get("forbidden_words")
                        and trip.get(u, {}).get("same_formula")) for u in ids}
    f1 = f_ok(["u0013.presupposition", "u0095.presupposition", "u0286.presupposition"])
    f2 = f_ok(["u0002.presupposition", "u0235.presupposition"])
    result["checks"].append({"id": "F1", "expected": "all three", "measured": f1, "pass": all(f1.values())})
    result["checks"].append({"id": "F2", "expected": "open (decides P4)", "measured": f2, "pass": all(f2.values())})

    # F3-F5.
    if scratch_check is not None and "coverage" in scratch_check:
        f3 = {"pinned_returncode": pc["returncode"], "scratch_returncode": sc["returncode"],
              "admitted": scratch_check.get("admission", {}).get("admitted")}
        result["checks"].append({"id": "F3", "expected": "same exit code, admitted", "measured": f3,
                                 "pass": sc["returncode"] == pc["returncode"] and f3["admitted"] is True})
        p_b, s_b = status_bytes(pinned_check), status_bytes(scratch_check)
        delta = {k: s_b.get(k, 0) - p_b.get(k, 0) for k in sorted(set(p_b) | set(s_b)) if s_b.get(k, 0) != p_b.get(k, 0)}
        expected_gain = 145 if all(f2.values()) else 89
        claimed = sum(next(u["span"][1] - u["span"][0] for u in meta["units"] if u["id"] == x) for x in admitted)
        result["checks"].append({"id": "F4", "expected": {"CHECKED": expected_gain, "UNFORMALISED": -expected_gain},
                                 "measured": delta, "converted_bytes": claimed,
                                 "pass": delta == {"CHECKED": expected_gain, "UNFORMALISED": -expected_gain}})
        pr, sr = readings_summary(pinned_check), readings_summary(scratch_check)
        result["checks"].append({"id": "F5", "expected": "8 of 8 conflict-free, pinned and scratch",
                                 "measured": {"pinned": pr, "scratch": sr},
                                 "pass": all(r["choice_count"] == 8 and r["choices_checked"] == 8
                                             and r["conflict_status"] == "CONFLICT-FREE" for r in (pr, sr))})
        result["vocabulary_only_identical_after_normalising"] = normalise(v0_check) == normalise(pinned_check)
        result["scratch_vs_pinned_differences"] = sorted(
            k for k in set(pinned_check) | set(scratch_check)
            if normalise(pinned_check.get(k)) != normalise(scratch_check.get(k)))
    else:
        result["checks"].append({"id": "F3", "expected": "same exit code, admitted",
                                 "measured": {"scratch_returncode": sc["returncode"], "stdout": sc["stdout"][:2000]},
                                 "pass": False})

    # F6: the two conclusion probes on pinned and scratch.
    probes = {}
    for name in ("conclusion-no-denial.json", "conclusion-no-claim-human.json"):
        q = RUN / "probes/nd" / name
        a = ve("document", "readings", pinned, "--conclusion", q, out=WORK / f"pinned-{name}")
        z = ve("document", "readings", scratch, "--conclusion", q, out=WORK / f"scratch-{name}")
        try:
            same = normalise(json.loads(a["stdout"])) == normalise(json.loads(z["stdout"]))
        except json.JSONDecodeError:
            same = False
        probes[name] = {"pinned_returncode": a["returncode"], "scratch_returncode": z["returncode"],
                        "identical_normalised": same, "byte_identical_raw": a["stdout"] == z["stdout"],
                        "pinned_verdict": (json.loads(a["stdout"]).get("verdict") if a["stdout"].startswith("{") else None),
                        "scratch_verdict": (json.loads(z["stdout"]).get("verdict") if z["stdout"].startswith("{") else None)}
    result["checks"].append({"id": "F6", "expected": "identical after normalising", "measured": probes,
                             "pass": all(p["identical_normalised"] for p in probes.values())})

    result["limits_at_end"] = limits()
    (OUT / "dryrun.json").write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n")
    delta = {"vocabulary_added": {k: {"arguments": a, "verbalisation": v} for k, (a, v, _) in PREDICATES.items()},
             "constant_added": dict([CONSTANT]), "units_converted": {u: CLASS_A[u][0] for u in admitted}}
    (OUT / "dryrun-scratch-delta.json").write_text(json.dumps(delta, ensure_ascii=False, indent=1) + "\n")
    for c in result["checks"]:
        print(c["id"], "PASS" if c["pass"] else "FAIL", json.dumps(c["measured"], ensure_ascii=False)[:600])
    return 0


if __name__ == "__main__":
    sys.exit(main())
