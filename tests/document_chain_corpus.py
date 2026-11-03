"""PC-2a's parity corpus (F2.3, docs/spec/profile-composition.md 5.2): every document of `tests/data` listing
soft-norms@0 with norm-defaults@0, as written and without `readings@1`, the forms `tests/test_rd9_docroute.py` loads,
and the constitution fixtures of `tests/data/composition/pc2a/chain.json`. `answers` runs the `ve document` commands on
one document; `docs/profile-composition/pc-2a/record_base.py` saved their answers on the base."""
from __future__ import annotations

from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
import json
from pathlib import Path

from conformance.p0 import LANGUAGE, SPEC_REVISION
from ve.document.cli import main

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tests/data"
CHAIN = json.loads((DATA / "composition/pc2a/chain.json").read_text())
SAVED = DATA / "composition/pc2a/parity-base.json"
LISTED = {"soft-norms@0", "norm-defaults@0"}
TOP = ["top"]
# F2.2's question: no Claude instance may directly deny that it is Claude.
NEVER = ["forall", "claude_instance", ["not", ["unary", "deny_being_claude_permitted", ["var", 0]]]]


def text(front, body: bytes) -> bytes:
    return b"---\n" + json.dumps(front).encode() + b"\n---\n" + body


def split(raw: bytes):
    head, body = raw[4:].split(b"\n---\n", 1)
    return json.loads(head), body


def chain_front(uid: str, *, profiles=None, **members):
    """One constitution unit's document: its rule as a soft norm under the chain's profiles."""
    unit = CHAIN["units"][uid]
    return {"format": "ve-document@1",
            "environment": {"language": LANGUAGE, "profiles": list(CHAIN["profiles"] if profiles is None else profiles),
                            "spec_revision": SPEC_REVISION,
                            "vocabulary": {"sorts": {"claude_instance": {"description": "Claude"}}, "constants": {},
                                           "predicates": deepcopy(unit["predicates"])}},
            "units": [{"id": uid, "span": [0, len(unit["body"])], "kind": "norm", "meaning": "specified",
                       "support": "assumption", "content": {"norm": deepcopy(unit["rule"])}}], **members}


def chain_document(uid: str, **members) -> bytes:
    return text(chain_front(uid, **members), CHAIN["units"][uid]["body"].encode())


def listing_documents():
    """Every document under `tests/data` whose environment lists soft-norms@0 and norm-defaults@0, by path."""
    found = {}
    for path in sorted(DATA.rglob("*")):
        if not path.is_file() or not path.name.endswith((".ve.md", ".ve.txt")):
            continue
        raw = path.read_bytes()
        try:
            profiles = split(raw)[0]["environment"]["profiles"]
        except (ValueError, KeyError, TypeError):
            continue
        if LISTED <= set(profiles):
            found[path.relative_to(ROOT).as_posix()] = raw
    return found


def _lowered(raw: bytes) -> bytes:
    front, body = split(raw)
    front["environment"]["profiles"].remove("readings@1")
    return text(front, body)


def _mixed(raw: bytes) -> bytes:
    """Its units as the parts of one `MIXED` container."""
    front, body = split(raw)
    parts = [{**unit, "status": "CHECKED"} for unit in front["units"]]
    front["units"] = [{"id": "parent", "span": [0, len(body)], "status": "MIXED", "parts": parts}]
    return text(front, body)


def _with_held_norm(uid: str) -> bytes:
    """The unit's norm under an open reading set of one assertion: no rule of the free document. The `meaning_id` is
    `["top"]`'s in the soft route's extended environment of `u0125.s04.p2`, as `ve.identity.meaning_id` gave it on the base."""
    sets = [{"id": "rs", "unit": uid, "version": 1, "status": "open",
             "readings": [{"id": "c", "kind": "asserted", "content": ["top"], "meaning_id": "f3d42b96f7a76a47c1dbaff19f17073660360daa79e02dbb501f1ec87c47936f",
                           "admission": {"who": "a", "why": "a", "distinguishing_models": {}}}]}]
    return chain_document(uid, reading_sets=sets)


def _edited(uid: str, edit, **members) -> bytes:
    """The unit's document with `edit` applied to its front matter."""
    front = chain_front(uid, **members)
    edit(front)
    return text(front, CHAIN["units"][uid]["body"].encode())


def _set_unit(field, value):
    return lambda front: front["units"][0].__setitem__(field, value)


def _second_unit(uid: str, unit, **members) -> bytes:
    """A second unit over `CLAIM`."""
    start = len(CHAIN["units"][uid]["body"])
    front = chain_front(uid, **members)
    front["units"].append({"id": "u2", "span": [start, start + len(CLAIM)], "meaning": "specified",
                           "support": "assumption", **unit})
    return text(front, CHAIN["units"][uid]["body"].encode() + CLAIM)


# That one Claude instance may deny: it contradicts F2.2's strict rule.
DENIABLE = ["exists", "claude_instance", ["unary", "deny_being_claude_permitted", ["var", 0]]]
CLAIM = b" This follows."


def _extras():
    uid, strict = "u0073.s05", "u0125.s04.p2"
    claim = {"kind": "asserted", "content": {"ast": NEVER}}
    record = {"name": "t", "arguments": ["claude_instance"], "decided_by": "unstated", "necessary": [],
              "sufficient": [], "factors": [], "precedents": [], "jurisdiction": "document", "version": 1}
    rule = {**CHAIN["units"][strict]["rule"], "name": "quoted-rule"}
    return {f"{uid}#unknown-predicate": _edited(uid, lambda f: f["units"][0]["content"]["norm"].update(predicate="absent")),
            f"{uid}#wrong-meaning-id": _edited(uid, _set_unit("meaning_id", "0" * 64)),
            f"{uid}#status-contradiction": _edited(uid, _set_unit("status", "OPEN")),
            f"{strict}#unformalised": _second_unit(strict, {"kind": ["unformalised", "prose"],
                                                            "meaning": {"unformalised": "prose"}}),
            f"{strict}#contextual": _second_unit(strict, {"kind": "example", "meaning": {"contextual": "a heading"}}),
            f"{strict}#open-term": _edited(strict, _set_unit("meaning", {"open": ["t"]}), open_terms=[record]),
            f"{strict}#graph": _second_unit(strict, claim, graph={"nodes": [{"ast": NEVER, "name": "claim", "unit": "u2"}],
                                                                  "root": "claim"}),
            f"{strict}#inconsistent": _second_unit(strict, {**claim, "content": {"ast": DENIABLE}}, graph={
                "nodes": [{"ast": DENIABLE, "name": "claim", "unit": "u2"}], "root": "claim"}),
            f"{strict}#attributed": _second_unit(strict, {"kind": ["attributed", "constitution", "says", "norm"],
                                                          "content": {"norm": rule}})}


def corpus():
    """Name to document, for F2.3: the first group is what the chain's document mode now answers, the rest stays
    with the retained path until PC-2b (`readings@1`)."""
    written = listing_documents()
    lowered = {f"{path}#lower": _lowered(raw) for path, raw in written.items()}
    route = lowered["tests/data/rd9-docroute.ve.md#lower"]
    uids = list(CHAIN["units"])
    answered = {**lowered, "rd9-docroute#mixed": _mixed(route),
                **{uid: chain_document(uid) for uid in uids},
                "u0073.s05#mixed": _mixed(chain_document("u0073.s05")),
                "u0073.s05#completions": chain_document(
                    "u0073.s05", completions={"comply_permitted": {"cites": ["u0073.s05"], "reason": "the rule"}}),
                "u0125.s04.p2#held": _with_held_norm("u0125.s04.p2"), **_extras()}
    return answered, written


def _run(argv):
    out = StringIO()
    try:
        with redirect_stdout(out):
            main(argv)
    except Exception as error:  # noqa: BLE001 - a refusal is the answer being compared
        return {"refused": type(error).__name__, "text": str(error)}
    return {"output": out.getvalue()}


def answers(raw: bytes, directory: Path, conclusions=(TOP,)):
    """Every `ve document` command's answer on one document, in `directory`."""
    path = directory / "document.ve.md"
    path.write_bytes(raw)
    found = {command: _run([command, str(path)]) for command in ("check", "coverage", "render", "readings")}
    for index, conclusion in enumerate(conclusions):
        asked = directory / f"conclusion{index}.json"
        asked.write_text(json.dumps(conclusion))
        found[f"readings --conclusion {json.dumps(conclusion)}"] = _run(["readings", str(path), "--conclusion", str(asked)])
        found[f"readings --assume-no-exception {json.dumps(conclusion)}"] = _run(
            ["readings", str(path), "--conclusion", str(asked), "--assume-no-exception"])
    return found


def conclusions_of(name: str):
    return (TOP, NEVER) if name.startswith("u0125") else (TOP,)
