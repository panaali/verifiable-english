"""kb-2a-b (6): the acceptance document tests/data/kb2a/rsp-mixed.ve.md (DESIGN section 3), cut from the pinned RSP
3.4 text and the D1 translation (usecases/anthropic-rsp/), as the stage-0 part documents are (`safetyfw_common.
part_document`, probes P1, P2 and P8).

    uv run python docs/kernel/kb-2a-b/build_rsp_mixed.py [--source PATH] [--check]

Each translated unit keeps its D1 bytes, kind, meaning and content, and is preceded by a `meta` unit, its header: a
Markdown heading that quotes the FULL source sentence the unit's bytes come from. What differs from D1, and why (the
REPORT lists the same):

* profiles: D1's (`norms@0`, `relational-fol@0`, `soft-norms@0`) with `documents@1`, `judgments@0` and `readings@1`
  (probe P8's input, with the reading set below);
* s36-full-review (ii): under `judgments@0` a judgment term is a predicate of the vocabulary, so OT5 and OT4 are
  declared on the two open predicates the rule reads (`highly_capable`, `significantly_redacted`), with D1's deciders
  (the re-expression fsf-r2 probe JT-c makes); D1's tokens would be refused `JudgmentUnbound` (probe P8);
* s35-aim (i): D1 gives it the set RS12minimize (default: the soft rule f13-minimize-default; intent: no rule); here
  its content is the default reading's rule, the one soft rule with an exception of the translation (the collapse
  fsf-r2 probe DF-b makes); no D1 unit has a soft rule as its own content;
* t1-plan (iii): D1's set RS1 (rs1_t1) with its readings' rules as content (cond: rows-cond, uncond: rows-uncond;
  ov: no rule, pending), one rule name for both (the twins of `safety-framework/build_document.content_set`), and OT1
  declared on the predicate the rules read (`crossed`; D1's OT13 names no predicate of the rules, so it is not
  listed). RS3o, the first candidate, cannot be lowered: its reading `iff` is two rules, and a reading carries one
  content. RS8 (strict or default force, two one-rule readings) cannot either: a reading's rule is lowered as a
  strict W1 rule only (`CoreDocument.lowerCandidate`; `Document.setCandidates` reads it with the W1 decoder), so a
  default reading is refused. W2 calls a set `authored` only with one signed reading (Loader.lean `authored reading
  needs one signed choice`), so this set is `open`.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "tests/data/kb2a/rsp-mixed.ve.md"
sys.path.insert(0, str(ROOT / "usecases/anthropic-rsp"))
sys.path.insert(0, str(ROOT / "usecases"))

# (unit id, the role DESIGN section 3 gives it)
UNITS = [("intro-aspire", "v"), ("t1-plan", "iii"), ("t4-name", "iv"), ("s35-aim", "i"),
         ("s35-disclose", "rule"), ("s36-full-review", "ii")]
PROFILES = ["documents@1", "judgments@0", "norms@0", "readings@1", "relational-fol@0", "soft-norms@0"]
JUDGED = {"crossed": "ot1_crossed", "highly_capable": "ot5_highly_capable",
          "significantly_redacted": "ot4_significantly_redacted"}
# Reading set RS1 on t1-plan (D1's rs1_t1): each reading's rule in rules.d1.ve, or none (`ov`).
RS1 = (("cond", "rows-cond"), ("uncond", "rows-uncond"), ("ov", None))


def sentence(source: bytes, a: int, b: int) -> str:
    """The full sentence around the bytes [a, b): from the end of the sentence before (". " or a line start) to the
    first sentence end (". " or ": " followed by a bullet or a line end) at or after the unit's last word."""
    text = source.decode("utf-8")
    start_char = len(source[:a].decode("utf-8"))
    stop_char = len(source[:b].decode("utf-8").rstrip())
    begin = max(text.rfind(". ", 0, start_char) + 2, text.rfind("\n", 0, start_char) + 1, 0)
    ends = [i for i in (text.find(". ", stop_char - 1), text.find(".\n", stop_char - 1),
                        text.find(": ", stop_char - 1)) if i >= 0]
    end = min(ends) + 1
    return " ".join(text[begin:end].split())


def situation_id(written_env: dict, entry: dict) -> str:
    """The id the readings route gives `entry` over the document's written environment (`situation_id.lean`): Python
    reads no environment that lists `judgments@0`, so Lean computes it."""
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as scratch:
        env_path, entry_path = Path(scratch) / "environment.json", Path(scratch) / "entry.json"
        env_path.write_text(json.dumps(written_env))
        entry_path.write_text(json.dumps(entry))
        out = subprocess.run(["lake", "env", "lean", "--run", str(HERE / "situation_id.lean"), str(env_path),
                              str(entry_path)], cwd=ROOT / "lean", capture_output=True, text=True, check=True)
    return out.stdout.strip()


def situations(raw_env: dict, written_env: dict, unit: dict, reading_set: dict) -> dict:
    """The set with the situations Python's search finds for its pair of readings, recorded as
    `safety-framework/build_document.record_situations` records them (no hint),
    each keyed by its id over the written environment."""
    from ve.readings_route import document_wire
    from ve.readings_s1 import record_situations, search
    env = {**raw_env, "profiles": sorted({*raw_env["profiles"], "readings@1"})}
    wire = document_wire([{"id": unit["id"], "kind": unit["kind"], "content": unit.get("content")}], [reading_set])
    found = {k: v for k, v in search(env, wire, reading_set["id"]).items() if v is not None}
    found = {pair: (situation_id(written_env, entry), entry) for pair, (_, entry) in found.items()}
    return record_situations(reading_set, found)


def build(source: bytes) -> bytes:
    import build_document as B
    from ve.readings import s1_content_meaning_id
    from ve.softnorms import SoftEnvironment
    document, _ = B.build(source)
    front = json.loads(document[4:document.index(b"\n---\n")])
    by_id = {u["id"]: u for u in front["units"]}
    env = {**front["environment"], "profiles": PROFILES}
    predicates = env["vocabulary"]["predicates"]
    declared = {t["name"]: t for t in B.open_term_declarations()}
    open_terms = [{**declared[token], "name": name, "arguments": list(predicates[name]["arguments"])}
                  for name, token in JUDGED.items()]
    units, body, sets = [], b"", []

    def add(unit, data):
        nonlocal body
        units.append({**unit, "span": [len(body), len(body) + len(data)]})
        body += data

    for uid, role in UNITS:
        u = {k: v for k, v in by_id[uid].items() if k != "span"}
        a, b = by_id[uid]["span"]
        header = f"## {uid} ({role}): “{sentence(source, a, b)}”\n".encode()
        add({"id": f"{uid}-source", "kind": "meta", "meaning": "specified", "support": "none"}, header)
        if uid == "s36-full-review":
            u["meaning"] = {"open": ["highly_capable", "significantly_redacted"]}
        if uid == "t1-plan":
            u["meaning"] = {"open": ["crossed"]}
        if uid == "s35-aim":
            u["content"] = {"norm": json.loads(B.T.parsed_rule("f13-minimize-default"))}
        if uid == "t1-plan":
            readings = []
            for choice, rule_id in RS1:
                if rule_id is None:
                    readings.append({"id": choice, "kind": "norm", "meaning_id": "pending", "content": None,
                                     "admission": {"who": "translator", "why": f"RS1 = {choice}: no rule",
                                                   "distinguishing_models": {}}})
                    continue
                reading = {"id": choice, "kind": "norm",
                           "content": {"norm": {**json.loads(B.T.parsed_rule(rule_id)), "name": "rs1-t1"}}}
                readings.append({**reading, "meaning_id": s1_content_meaning_id(SoftEnvironment(front["environment"]),
                                                                                  "rs1-t1", reading),
                                 "admission": {"who": "translator", "why": f"RS1 = {choice}: rule {rule_id} of rules.d1.ve",
                                               "distinguishing_models": {}}})
            sets.append(situations(front["environment"], env, u, {"id": "rs1-t1", "unit": uid, "version": 1,
                                                                   "status": "open", "readings": readings}))
        add(u, source[a:b] + (b"" if source[a:b].endswith(b"\n") else b"\n"))
    front_out = {"format": "ve-document@1", "environment": env, "units": units, "open_terms": open_terms,
                 "reading_sets": sets}
    return b"---\n" + json.dumps(front_out, indent=1, ensure_ascii=False).encode() + b"\n---\n" + body


def main(argv=None) -> int:
    import build_document as B
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=B.DEFAULT_SOURCE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    data = build(args.source.read_bytes())
    if args.check:
        return 0 if OUT.read_bytes() == data else 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
