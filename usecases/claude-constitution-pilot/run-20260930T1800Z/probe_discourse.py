#!/usr/bin/env python3
"""Probe (not part of the counted translation): what ve.discourse@1 can say about u0214.s02.

    "We call this broad pattern of treatment and trust Claude's principal hierarchy, and it helps define what we
     mean by broad safety."

The discourse route admits first-order documents only (no norm, no soft norm), so the probe document is the base
translation without its norm declaration and unit; everything else is that translation's unit, byte for byte.
The naming clause registers a content name over a unit target (docs/spec/discourse.md 2.5); the rest of the
sentence keeps its own UNFORMALISED span. Writes probes/discourse-probe.ve.md and probes/discourse-probe.json."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
SOURCE = (ROOT / "usecases/claude-constitution-pilot/source/claude-constitution.md").read_bytes()
UNIT = "u0214.s02"
NAMING = "We call this broad pattern of treatment and trust Claude’s principal hierarchy"
NAME = "Claude’s principal hierarchy"


def unformalised(uid, span, feature):
    return {"id": uid, "span": span, "support": "none", "kind": ["unformalised", feature], "meaning": {"unformalised": feature}}


def main():
    data = (RUN / "prev/translation.ve.md").read_bytes()
    end = data.index(b"\n---\n", 4)
    meta, tail = json.loads(data[4:end]), data[end + 5:]
    env = meta["environment"]
    env["profiles"] = sorted((set(env["profiles"]) - {"norms@0"}) | {"ve.discourse@1"})
    env["vocabulary"]["predicates"].pop("csam_generation_permitted")
    meta["format"] = "ve-document@2"
    # The route abstains on fenced English ("NotImplemented: fenced English or strict content"), so the probe writes
    # the one checked clause (u0248) as JSON content instead of a fence; the counted translation keeps the fence.
    tail = tail[:len(SOURCE)]
    assert tail == SOURCE
    units = []
    for unit in meta["units"]:
        if unit["id"] == "u0165.s07":
            unit = unformalised(unit["id"], unit["span"], "norms")  # a norm unit cannot share a discourse document
        if unit["id"] == "u0248":
            unit = {**unit, "content": {"ast": meta["graph"]["nodes"][0]["ast"]}}
        if unit["id"] == UNIT:
            a, b = unit["span"]
            text = SOURCE[a:b].decode("utf-8")
            assert text.startswith(NAMING + ", and it helps define what we mean by broad safety.")
            n = len(NAMING.encode("utf-8"))
            lead = len("We call this broad pattern of treatment and trust ")
            # The unit holding the mention must be printable ASCII (discourse wording, 4.1(4)); the name has a curly
            # apostrophe, so the naming clause is cut before it: two labelled fragments of one clause.
            units += [{"id": UNIT + ".p1", "span": [a, a + lead], "support": "none", "kind": "meta", "meaning": "specified"},
                      {"id": UNIT + ".p1b", "span": [a + lead, a + n], "support": "none", "kind": "meta", "meaning": "specified"},
                      unformalised(UNIT + ".p2", [a + n, a + n + len(", and ")], "other.discourse"),
                      unformalised(UNIT + ".p3", [a + n + len(", and "), b], "attribution")]
            continue
        units.append(unit)
    meta["units"] = units
    meta["open_terms"] = [t for t in meta["open_terms"] if t["name"] != "child_sexual_abuse_material"]
    a = SOURCE.index(b"this broad pattern of treatment and trust", 133749)
    it = SOURCE.index(b"it helps define", a)
    meta["discourse"] = {
        "version": "ve.discourse@1",
        "anchors": [{"id": "doc", "kind": "document", "label": "Claude’s constitution", "span": [0, len(SOURCE)]}],
        "content_names": [{"name": NAME, "units": ["u0214.s01"], "scope": "doc"}],
        "mentions": [
            {"id": "m-this-pattern", "unit": UNIT + ".p1", "span": [a, a + len("this broad pattern of treatment and trust")],
             "form": "demonstrative", "target": {"kind": "unit", "units": ["u0214.s01"], "content_name": NAME}},
            {"id": "m-it", "unit": UNIT + ".p3", "span": [it, it + 2], "form": "pronoun",
             "target": {"kind": "unit", "units": ["u0214.s01"], "content_name": NAME}}]}
    out = RUN / "probes/discourse-probe.ve.md"
    out.write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False, separators=(",", ":")).encode() + b"\n---\n" + tail)
    proc = subprocess.run([sys.executable, "-m", "ve", "document", "check", str(out.relative_to(ROOT))], cwd=ROOT,
                          capture_output=True, text=True)
    result = {"unit": UNIT, "returncode": proc.returncode, "target_of_this_broad_pattern": ["u0214.s01"],
              "attempts_in_order": [
                  "1. Base translation minus its norm declaration and norm unit, plus the discourse block: the Lean route abstains "
                  "(NotImplemented: fenced English or strict content) because the one checked clause u0248 is a fenced English block.",
                  "2. Fence removed: the route abstains (NotImplemented: a document without a claim graph); a discourse document "
                  "must keep a claim graph.",
                  "3. u0248 written as JSON content ({\"ast\": ...}) with its graph node: InvalidInput: discourse wording of "
                  "u0214.s02.p1. The unit holding a recorded mention must be printable ASCII (docs/spec/discourse.md 4.1(4)); the "
                  "name has U+2019 (Claude\u2019s).",
                  "4. Naming clause cut before the name (two labelled fragments, which the translation would not otherwise do): "
                  "MentionNotSlot: m-this-pattern. A demonstrative that targets a unit is recorded as a location in the spec "
                  "(1.4) but this tag treats every demonstrative as a slot of a bound formula, and a naming clause has none. "
                  "This is the last attempt and the one in `error` below."]}
    if proc.returncode == 0:
        report = json.loads(proc.stdout)
        result.update({k: report[k] for k in ("coverage", "premises") if k in report})
        result["references"] = report.get("references")
    else:
        result["error"] = proc.stderr.strip().splitlines()[-1]
    (RUN / "probes/discourse-probe.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result, indent=1, ensure_ascii=False)[:3500])


if __name__ == "__main__":
    main()
