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
                  "1. Base translation minus its norm declaration and norm unit, plus the discourse block, with the clause u0248 still a "
                  "fenced English block: (20260930T1800Z, ve-green-risk) the Lean route abstained (NotImplemented: fenced English or "
                  "strict content). Not re-run at ve-green-risk-c5: docs/spec/discourse.md 11 still lists fenced content as a limitation.",
                  "2. Fence removed: (20260930T1800Z) the route abstained (a document without a claim graph); a discourse document must "
                  "keep a claim graph. Same status at ve-green-risk-c5 (spec 11).",
                  "3. u0248 written as JSON content ({\"ast\": ...}) with its graph node, the name's U+2019 unit kept whole: (20260930T1800Z) "
                  "InvalidInput: discourse wording of u0214.s02.p1. Superseded by the c5 spec amendment (a location binding needs no "
                  "discourse wording), but the probe below still cuts the clause in two because a unit holding a location binding must "
                  "have no meaning and the rest of the sentence is a substantive claim that must not be labelled content-free.",
                  "4. Naming clause cut before the name (two LABELLED fragments p1, p1b, which the translation would not otherwise do; "
                  "the rest, \", and\" and \"it helps define what we mean by broad safety\", stay UNFORMALISED): (20260930T1800Z) "
                  "MentionNotSlot: m-this-pattern. At ve-green-risk-c5 this attempt is ACCEPTED at document-check level: both mentions "
                  "are location bindings (status navigation) to the unit u0214.s01 under the content name \u201cClaude\u2019s principal "
                  "hierarchy\u201d. This is the one change in the language that touches the constitution, and it labels two fragments "
                  "of one clause; it formalises nothing."]}
    if proc.returncode == 0:
        report = json.loads(proc.stdout)
        result.update({k: report[k] for k in ("coverage", "premises") if k in report})
        result["references"] = report.get("references")
    else:
        result["error"] = (proc.stderr.strip().splitlines() or [proc.stdout[-300:]])[-1]
    # Attempt 5: the same block on the real translation (norms, soft norms, fenced clause kept), to see whether the
    # upgrade can reach the translation itself.
    raw = (RUN / "translation.ve.md").read_bytes()
    full_end = raw.index(b"\n---\n", 4)
    full = json.loads(raw[4:full_end])
    full_tail = raw[full_end + 5:]
    probe_meta = json.loads(out.read_bytes()[4:out.read_bytes().index(b"\n---\n", 4)])
    full["discourse"] = probe_meta["discourse"]
    full["units"] = [u for u in full["units"] if not u["id"].startswith(UNIT)] + [u for u in probe_meta["units"] if u["id"].startswith(UNIT)]
    full["units"].sort(key=lambda u: u["span"][0])
    full["environment"]["profiles"] = sorted(set(full["environment"]["profiles"]) | {"ve.discourse@1"})
    full["format"] = "ve-document@2"
    out5 = RUN / "probes/discourse-in-translation-probe.ve.md"
    out5.write_bytes(b"---\n" + json.dumps(full, ensure_ascii=False, separators=(",", ":")).encode() + b"\n---\n" + full_tail)
    p5 = subprocess.run([sys.executable, "-m", "ve", "document", "check", str(out5.relative_to(ROOT))], cwd=ROOT,
                        capture_output=True, text=True)
    lines = [l for l in (p5.stdout + "\n" + p5.stderr).splitlines() if l.strip()]
    msg = lines[-1].strip() if lines else ""
    # Run 20261005T0600Z: since lean-first b4 Lean answers alone and its first rejection is the front matter; the same document with
    # its reading sets removed is rejected for the profile, which is the limit the spec states (docs/spec/discourse.md 11).
    import tempfile
    stripped = json.loads(json.dumps(full))
    stripped.pop("reading_sets", None)
    with tempfile.NamedTemporaryFile("wb", suffix=".ve.md", delete=False) as handle:
        handle.write(b"---\n" + json.dumps(stripped, ensure_ascii=False, separators=(",", ":")).encode() + b"\n---\n" + full_tail)
    p6 = subprocess.run([sys.executable, "-m", "ve", "document", "check", handle.name], cwd=ROOT, capture_output=True, text=True)
    Path(handle.name).unlink()
    lines6 = [l for l in (p6.stdout + "\n" + p6.stderr).splitlines() if l.strip()]
    result["in_the_translation_itself"] = {"returncode": p5.returncode, "message": msg,
        "same_document_without_its_reading_sets": {"returncode": p6.returncode, "message": lines6[-1].strip() if lines6 else ""},
        "previous_run_message": "ve.errors.VEError: UnrecordedSlot: u0123.s02.p1: [76303, 76305)",
        "meaning": "The translation has norm and soft-norm units and one fenced clause. The discourse route is Lean's alone since "
                   "lean-first b4 and its first rejection of this document is its front matter (what in the reading sets it cannot decode "
                   "was not isolated: removing the reading sets changes the message); with them removed it names the profile (norm-defaults@0 is not supported "
                   "beside ve.discourse@1), which is the limit the spec states (docs/spec/discourse.md 11: norm and soft-norm "
                   "composition is not implemented). The earlier run's message named an unrecorded slot; the verdict is the same: the "
                   "upgrade cannot enter the main document, u0214.s02 stays UNFORMALISED (other:discourse) there, and only the "
                   "norms-free companion probe is admitted."}
    result["attempts_in_order"].append("5. The same discourse block and fragments added to the real translation (with its norms, soft norms and "
                                       "fence): returncode %d, see in_the_translation_itself." % p5.returncode)
    (RUN / "probes/discourse-probe.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result, indent=1, ensure_ascii=False)[:3500])


if __name__ == "__main__":
    main()
