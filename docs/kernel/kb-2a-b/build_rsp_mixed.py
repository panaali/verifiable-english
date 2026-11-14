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
* s32-strong-attempt (iii): the set RS8attempt with its two readings' rules (f10-attempt-strict, f10-attempt-default)
  as content, one rule name for both (the twins of `safety-framework/build_document.content_set`). RS3o, the first
  candidate, cannot be lowered: its reading `iff` is two rules, and a reading carries one content. W2 calls a set
  `authored` only with one signed reading (Loader.lean `authored reading needs one signed choice`), so this
  two-reading set is `open`.
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
UNITS = [("intro-aspire", "v"), ("t4-name", "iv"), ("s32-strong-attempt", "iii"), ("s35-aim", "i"),
         ("s35-disclose", "rule"), ("s36-full-review", "ii")]
PROFILES = ["documents@1", "judgments@0", "norms@0", "readings@1", "relational-fol@0", "soft-norms@0"]
JUDGED = {"highly_capable": "ot5_highly_capable", "significantly_redacted": "ot4_significantly_redacted"}


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
            u["meaning"] = {"open": list(JUDGED)}
        if uid == "s35-aim":
            u["content"] = {"norm": json.loads(B.T.parsed_rule("f13-minimize-default"))}
        if uid == "s32-strong-attempt":
            readings = []
            for choice, rule_id in (("strict", "f10-attempt-strict"), ("default", "f10-attempt-default")):
                reading = {"id": choice, "kind": "norm",
                           "content": {"norm": {**json.loads(B.T.parsed_rule(rule_id)), "name": "rs8-attempt"}}}
                readings.append({**reading, "meaning_id": s1_content_meaning_id(SoftEnvironment(front["environment"]), "rs8-attempt",
                                                                                  reading),
                                 "admission": {"who": "translator",
                                               "why": f"RS8attempt = {choice}: rule {rule_id} of rules.d1.ve"}})
            sets.append({"id": "rs8-attempt", "unit": uid, "version": 1, "status": "open", "readings": readings})
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
