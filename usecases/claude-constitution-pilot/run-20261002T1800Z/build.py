#!/usr/bin/env python3
"""Build the run's documents from the base translation plus spec.py and spec_nd.py.

Three documents (all cover the whole 184,893-byte source):

* translation.ve.md (main): profiles documents@1, norms@0, norm-defaults@0, relational-fol@0. The seven hard constraints and
  the operator/user permission units carry their one strict reading as content, with the completion `unspecified`.
  Units whose force or scope is open are reading sets (candidate norms carry no content).
* readings/all-strict.ve.md: the same environment; every force-ambiguous unit and the scope-ambiguous u0123.s03 resolved
  to the strict (narrow) reading, so those rules are elaborated and checked.
* readings/all-default.ve.md: soft-norms@0, which norm-defaults@0 cannot join in one document
  (`UnsupportedProfile: norm-defaults@0 documents on the soft and rights routes await the Lean route`). The
  force-ambiguous units and u0073.s05 resolved to the defeasible reading, with the previous run's completions. The hard
  constraints and the operator units are not elaborated here (the defeasible reading is not admissible for the hard
  constraints, and the operator rules do not depend on force).

The source bytes and every unit not listed in spec.py / spec_nd.py are copied from the base translation unchanged.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))

import spec  # noqa: E402
import spec_nd as nd  # noqa: E402
from ve.document import _environment  # noqa: E402
from ve.model import FiniteModel  # noqa: E402

SOURCE = (ROOT / "usecases/claude-constitution-pilot/source/claude-constitution.md").read_bytes()
HARD_UNITS = [h[0] for h in nd.HARD]
FORCE_UNITS = [u["old"] for u in spec.UNITS if u["kind"] == "norm-force" and u["old"] not in HARD_UNITS]
SOFT_ONE = [u["old"] for u in spec.UNITS if u["kind"] == "norm-one"]
OLD_ITEM = {u["old"]: u for u in spec.UNITS}
NEW_ITEM = {u["old"]: u for u in nd.OPS_ALL}


def load_previous():
    data = (RUN / "prev/translation.ve.md").read_bytes()
    assert data.startswith(b"---\n")
    end = data.index(b"\n---\n", 4)
    return json.loads(data[4:end]), data[end + 5:]


# ------------------------------------------------------------------ environments and open terms
def environment(prev_env, variant):
    env = copy.deepcopy(prev_env)
    vocab = env["vocabulary"]
    vocab["predicates"].pop(spec.OLD_PREDICATE_REMOVED)
    if variant == "soft":
        env["profiles"] = sorted(set(env["profiles"]) | {"soft-norms@0"})
        vocab["sorts"].update(copy.deepcopy(spec.SORTS))
        vocab["predicates"].update(copy.deepcopy(spec.PREDICATES))
    else:
        env["profiles"] = sorted(set(env["profiles"]) | {"norm-defaults@0"})
        vocab["sorts"].update(copy.deepcopy(nd.SORTS))
        vocab["predicates"].update(copy.deepcopy(nd.PREDICATES))
    return env


def open_terms(prev_terms, variant):
    terms = copy.deepcopy(prev_terms)
    have = {t["name"] for t in terms}
    if variant == "soft":
        factors, args = spec.OPEN_TERM_FACTORS, spec.OPEN_TERM_ARGS
        factors = {k: v for k, v in factors.items() if k not in HARD_TERMS}
    else:
        factors, args = nd.OPEN_TERM_FACTORS, nd.OPEN_TERM_ARGS
    for name, f in factors.items():
        if name in have:
            continue
        terms.append({"name": name, "arguments": args[name], "decided_by": "unresolved_decider",
                      "necessary": [], "sufficient": [], "factors": f, "precedents": [],
                      "jurisdiction": "claude_constitution", "version": 1})
    return terms


HARD_TERMS = {h[3] for h in nd.HARD}


# ------------------------------------------------------------------ norm blocks
def soft_block(item):
    block = {"name": item["rule"], "predicate": item["predicate"], "sign": item["sign"], "guard": item["guard"],
             "unless": item["unless"], "over": [],
             "mode": "default", "exception": {"decided_by": "unstated", "sufficient": [], "necessary": [], "factors": []}}
    return {"norm": block}


def nd_block(r):
    return {"norm": {"name": r["rule"], "predicate": r["predicate"], "sign": r["sign"], "guard": r["guard"],
                     "unless": r["unless"], "over": []}}


def excepted_name(rule):
    return "soft__excepted__" + rule.replace("-", "_")


def norm_part(uid, span, content, terms):
    unit = {"id": uid, "span": span, "kind": "norm", "support": "assumption",
            "meaning": {"open": terms} if terms else "specified"}
    if content is not None:
        unit["content"] = content
    return unit


def unformalised(uid, span, feature):
    f = feature.replace(":", ".")
    return {"id": uid, "span": span, "support": "none", "kind": ["unformalised", f], "meaning": {"unformalised": f}}


# ------------------------------------------------------------------ reading sets
PLACEHOLDER = (" The stored model is a placeholder (an empty situation): a candidate norm carries no content, so this document "
               "cannot check that it separates the readings. The separating situation is computed in finish.py "
               "(readings/separating-situations.json).")


def force_set(uid, item):
    key = uid.replace(".", "-")
    admission = lambda other: {"who": "translator", "why": item["readings_note"] + PLACEHOLDER,
                               "distinguishing_models": {other: "@MODEL"}}
    return {"id": f"force-{key}", "unit": uid, "version": 1, "status": "open", "models": {},
            "readings": [
                {"id": "strict", "kind": "norm", "meaning_id": f"pending-strict-{key}", "content": None,
                 "admission": admission("default")},
                {"id": "default", "kind": "norm", "meaning_id": f"pending-default-{key}", "content": None,
                 "admission": admission("strict")}]}


def single_set(uid, item):
    key = uid.replace(".", "-")
    return {"id": f"force-{key}", "unit": uid, "version": 1, "status": "open", "models": {},
            "readings": [{"id": "default", "kind": "norm", "meaning_id": f"pending-default-{key}", "content": None,
                          "admission": {"who": "translator", "why": item["readings_note"] + " One reading: the source says "
                                        "“generally”, a defeasible duty (soft-norms 2.2). The rule is elaborated in "
                                        "readings/all-default.ve.md because norm-defaults@0 and soft-norms@0 cannot share a "
                                        "document; a candidate norm carries no content.",
                                        "distinguishing_models": {}}}]}


def modal_set(uid, item):
    key = uid.replace(".", "-")
    cands = item["candidates"]
    set_id = item["set_id"] if uid == item["old"] else f"{item['set_id']}-{uid.rsplit('.', 1)[1]}"
    admission = lambda cid, text: {"who": "translator", "why": text + " " + item["note"] + PLACEHOLDER,
                                   "distinguishing_models": {c: "@MODEL" for c, _, _ in cands if c != cid}}
    return {"id": set_id, "unit": uid, "version": 1, "status": "open", "models": {},
            "readings": [{"id": cid, "kind": kind, "meaning_id": f"pending-{cid}-{key}", "content": None,
                          "admission": admission(cid, text)} for cid, kind, text in cands]}


# ------------------------------------------------------------------ units
def fact_unit(uid, span, terms):
    """A checked English statement (a fence), not a norm: the unit's content is bound to the fence of the same id."""
    return {"id": uid, "span": span, "kind": "asserted", "support": "assumption",
            "meaning": {"open": list(terms)} if terms else "specified",
            "content": {"fence": uid}, "surface": "english"}


FENCES: list = []  # (unit id, English text) of the statements written as fences at the end of the document


def build_units(prev_units, variant):
    units, sets = [], []
    for unit in prev_units:
        uid = unit["id"]
        a, b = unit["span"]
        text = SOURCE[a:b].decode("utf-8")
        if uid in HARD_UNITS:
            r = nd.ND_RULES[uid]
            if variant == "default":
                units.append(unformalised(uid, [a, b], "norms"))
            else:
                units.append(norm_part(uid, [a, b], nd_block(r), r["open_terms"]))
        elif uid in FORCE_UNITS or uid in SOFT_ONE:
            item = OLD_ITEM[uid]
            pieces = item.get("pieces") or [(text, "norm", None, None)]
            cursor = a
            for index, (s, status, feature, note) in enumerate(pieces, 1):
                width = len(s.encode("utf-8"))
                assert SOURCE[cursor:cursor + width].decode("utf-8") == s, (uid, s)
                span = [cursor, cursor + width]
                cursor += width
                pid = uid if "pieces" not in item else f"{uid}.p{index}"
                if status != "norm":
                    units.append(unformalised(pid, span, feature))
                    continue
                if variant == "default":
                    names = list(item["open_terms"]) + [excepted_name(item["rule"])]
                    units.append(norm_part(pid, span, soft_block(item), names))
                elif uid in SOFT_ONE and variant == "strict":
                    # its only reading is defeasible; it is elaborated in readings/all-default.ve.md
                    units.append(unformalised(pid, span, "norms"))
                elif uid in SOFT_ONE or variant == "main":
                    terms = list(item["open_terms"])
                    units.append(norm_part(pid, span, None, terms))
                    sets.append(single_set(pid, item) if uid in SOFT_ONE else
                                force_set(pid, {**item, "readings_note": nd.NOTE_OVERRIDE.get(uid, item["readings_note"])}))
                else:  # strict
                    r = nd.ND_RULES[uid]
                    units.append(norm_part(pid, span, nd_block(r), r["open_terms"]))
            assert cursor == b, uid
        elif uid in NEW_ITEM and NEW_ITEM[uid]["kind"] == "ops-fact":
            item = NEW_ITEM[uid]
            if variant == "default":
                units.append(unformalised(uid, [a, b], "norms"))
            else:
                cursor = a
                for index, seg in enumerate(item["main"], 1):
                    width = len(seg[1].encode("utf-8"))
                    assert SOURCE[cursor:cursor + width].decode("utf-8") == seg[1], (uid, seg[1])
                    span = [cursor, cursor + width]
                    cursor += width
                    pid = f"{uid}.p{index}"
                    if seg[0] == "unf":
                        units.append(unformalised(pid, span, seg[2]))
                    else:
                        units.append(fact_unit(pid, span, seg[2]))
                        FENCES.append((pid, seg[3]))
                assert cursor == b, uid
        elif uid in NEW_ITEM:
            item = NEW_ITEM[uid]
            if variant == "default":
                units.append(unformalised(uid, [a, b], "norms"))
            elif variant == "main":
                cursor, norm_cursor = a, 0
                strict_norms = [seg for seg in item["strict"]]
                for index, seg in enumerate(item["main"], 1):
                    width = len(seg[1].encode("utf-8"))
                    assert SOURCE[cursor:cursor + width].decode("utf-8") == seg[1], (uid, seg[1])
                    span = [cursor, cursor + width]
                    cursor += width
                    pid = uid if len(item["main"]) == 1 else f"{uid}.p{index}"
                    if seg[0] == "unf":
                        units.append(unformalised(pid, span, seg[2]))
                        norm_cursor = advance(strict_norms, norm_cursor, seg[1])
                        continue
                    terms, norm_cursor = group_terms(strict_norms, norm_cursor, seg[1])
                    terms = terms + [t for t in item.get("extra_terms", []) if t not in terms]
                    units.append(norm_part(pid, span, None, terms))
                    sets.append(modal_set(pid, item))
                assert cursor == b, uid
            else:  # strict: the permission reading, one rule per list item
                cursor = a
                for j, seg in enumerate(item["strict"], 1):
                    width = len(seg[1].encode("utf-8"))
                    assert SOURCE[cursor:cursor + width].decode("utf-8") == seg[1], (uid, seg[1])
                    span = [cursor, cursor + width]
                    cursor += width
                    pid = f"{uid}.r{j}"
                    if seg[0] == "norm":
                        r = seg[2]
                        units.append(norm_part(pid, span, nd_block(r), r["open_terms"]))
                    else:
                        units.append(unformalised(pid, span, seg[2]))
                assert cursor == b, uid
        else:
            units.append(unit)
    return units, sets


def advance(segments, index, text):
    """Skip the strict segments whose text makes up `text` (an unformalised segment of main)."""
    done = ""
    while done != text:
        done += segments[index][1]
        index += 1
        assert text.startswith(done), (text, done)
    return index


def group_terms(segments, index, text):
    """Open terms of the strict norm segments whose concatenated text is `text`."""
    done, terms = "", []
    while done != text:
        seg = segments[index]
        done += seg[1]
        index += 1
        assert text.startswith(done), (text, done)
        if seg[0] == "norm":
            terms += [t for t in seg[2]["open_terms"] if t not in terms]
    return terms, index


def environment_model(env_dict):
    """The empty situation over the document's own environment (the placeholder model of a reading set)."""
    env = _environment(env_dict)
    domains = {s: [s + "0"] for s in env.sorts}
    data = {"complete": True, "domains": domains,
            "constants": {c: env_dict["vocabulary"]["constants"][c]["sort"] + "0"
                          for c in env_dict["vocabulary"].get("constants", {})},
            "relations": {p: [] for p in env.predicates}}
    return FiniteModel.from_dict(env, data).model_id, data


def write(path, meta, rest):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                     + b"\n---\n" + rest)


def main():
    prev_meta, rest = load_previous()
    out = {}
    for variant, path in (("main", RUN / "translation.ve.md"),
                          ("strict", RUN / "readings/all-strict.ve.md"),
                          ("default", RUN / "readings/all-default.ve.md")):
        kind = "soft" if variant == "default" else "nd"
        env = environment(prev_meta["environment"], kind)
        terms = open_terms(prev_meta.get("open_terms", []), kind)
        del FENCES[:]
        units, sets = build_units(prev_meta["units"], variant)
        meta = {k: v for k, v in prev_meta.items() if k not in ("environment", "units", "open_terms")}
        meta.update({"environment": env, "units": units, "open_terms": terms})
        if sets:
            model_id, model = environment_model(env)
            for rs in sets:
                if any(r["admission"]["distinguishing_models"] for r in rs["readings"]):
                    rs["models"] = {model_id: model}
                for reading in rs["readings"]:
                    for other in reading["admission"]["distinguishing_models"]:
                        reading["admission"]["distinguishing_models"][other] = model_id
            meta["reading_sets"] = sets
            meta["narrowings"] = []
        fences = b"".join(f"```ve {pid}\n{text}\n```\n".encode("utf-8") for pid, text in FENCES)
        write(path, meta, rest + fences)
        out[variant] = str(path.relative_to(ROOT))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
