#!/usr/bin/env python3
"""Build the run's documents from the previous run's translation plus spec.py.

Writes translation.ve.md (main document: unresolved force readings recorded as reading sets) and the two
companion documents readings/all-strict.ve.md and readings/all-default.ve.md (each resolves every force
reading one way, so the elaborated norm of each reading is checked end to end). The source bytes and every
unit not listed in spec.py are copied from the previous run unchanged.
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
from ve.model import FiniteModel  # noqa: E402
from ve.softnorms import SoftEnvironment, SoftNormDocument  # noqa: E402

SOURCE = (ROOT / "usecases/claude-constitution-pilot/source/claude-constitution.md").read_bytes()


def load_previous():
    data = (RUN / "prev/translation.ve.md").read_bytes()
    assert data.startswith(b"---\n")
    end = data.index(b"\n---\n", 4)
    return json.loads(data[4:end]), data[end + 5:]


def excepted_name(rule):
    return "soft__excepted__" + rule.replace("-", "_")


def norm_block(item, mode):
    block = {"name": item["rule"], "predicate": item["predicate"], "sign": item["sign"],
             "guard": item["guard"], "unless": item["unless"], "over": []}
    if mode == "default":
        block.update({"mode": "default",
                      "exception": {"decided_by": "unstated", "sufficient": [], "necessary": [], "factors": []}})
    elif item.get("hard_if_narrowed"):
        block["hard"] = True
    return {"norm": block}


def environment(prev_env):
    env = copy.deepcopy(prev_env)
    env["profiles"] = sorted(set(env["profiles"]) | {"soft-norms@0"})
    vocab = env["vocabulary"]
    vocab["sorts"].update(copy.deepcopy(spec.SORTS))
    predicates = vocab["predicates"]
    predicates.pop(spec.OLD_PREDICATE_REMOVED)
    for hard in spec.HARD:
        _, _, predicate, term, act, words = hard
        predicates[predicate] = spec._reg(
            "obligation", act, [spec.CLAUDE, spec.SITUATION],
            f"Claude is required to avoid the act in a situation that is a case of {words}. The act phrase only points at "
            f"the case; the source's own words for it are the case atom {term}, an open term.")
        predicates[term] = spec._base(
            [spec.SITUATION], "{0} is a case of " + words,
            f"The situation is a case of {words}; which situations these are is the open term {term}.")
    predicates.update(copy.deepcopy(spec.PREDICATES))
    return env


def open_terms(prev_terms):
    terms = copy.deepcopy(prev_terms)
    have = {t["name"] for t in terms}
    for name, factors in spec.OPEN_TERM_FACTORS.items():
        if name in have:
            continue
        terms.append({"name": name, "arguments": spec.OPEN_TERM_ARGS[name], "decided_by": "unresolved_decider",
                      "necessary": [], "sufficient": [], "factors": factors, "precedents": [],
                      "jurisdiction": "claude_constitution", "version": 1})
    return terms


def split(text, pieces):
    out, cursor = [], 0
    for piece in pieces:
        s = piece[0]
        assert text[cursor:cursor + len(s)] == s, (text, s)
        out.append((cursor, cursor + len(s.encode("utf-8")) if False else None))
        cursor += len(s)
    assert cursor == len(text), (cursor, len(text), text)


def build_units(prev_units, variant):
    by_old = {u["old"]: u for u in spec.UNITS}
    units, reading_sets, narrowings, soft_contents = [], [], [], []
    for unit in prev_units:
        item = by_old.get(unit["id"])
        if item is None:
            units.append(unit)
            continue
        assert "status" not in unit or unit["status"] != "MIXED"
        a, b = unit["span"]
        text = SOURCE[a:b].decode("utf-8")
        if "pieces" not in item:
            units.append(norm_unit(unit["id"], [a, b], item, variant, reading_sets, narrowings, soft_contents))
            continue
        parts, cursor = [], a
        joined = ""
        for index, (s, status, feature, note) in enumerate(item["pieces"], 1):
            width = len(s.encode("utf-8"))
            assert SOURCE[cursor:cursor + width].decode("utf-8") == s, (unit["id"], s)
            span = [cursor, cursor + width]
            cursor += width
            pid = f"{unit['id']}.p{index}"
            if status == "norm":
                part = norm_unit(pid, span, item, variant, reading_sets, narrowings, soft_contents)
            else:
                part = {"id": pid, "span": span, "support": "none",
                        "kind": ["unformalised", feature.replace(":", ".")],
                        "meaning": {"unformalised": feature.replace(":", ".")}}
            parts.append(part)
        assert cursor == b, (unit["id"], cursor, b)
        # Flat units, not a MIXED parent: the document loader collects soft norms from top-level units only.
        units.extend(parts)
    return units, reading_sets, narrowings, soft_contents


def norm_unit(uid, span, item, variant, reading_sets, narrowings, soft_contents, part=False):
    terms = list(item["open_terms"])
    forced = item["kind"] == "norm-force"
    unit = {"id": uid, "span": span, "kind": "norm", "support": "assumption"}
    if forced and variant == "main":
        unit["meaning"] = {"open": terms} if terms else "specified"
        if part:
            unit["status"] = "OPEN"
        reading_sets.append(reading_set(uid, item))
        if item.get("cites"):
            narrowings.append({"id": f"narrow-{uid.replace('.', '-')}", "set": f"force-{uid.replace('.', '-')}",
                               "version": 1, "keeps": ["strict"], "by": "translator", "reason_spans": item["cites"]})
        return unit
    mode = "strict" if forced and variant == "strict" else "default"
    content = norm_block(item, mode)
    soft_contents.append(content)
    names = terms + ([excepted_name(item["rule"])] if mode == "default" else [])
    unit["meaning"] = {"open": names} if names else "specified"
    unit["content"] = content
    if part:
        unit["status"] = "OPEN" if names else "CHECKED"
    return unit


PLACEHOLDER = (" The stored model is a placeholder (an empty situation): a candidate norm carries no content, so this document "
               "cannot check that it separates the readings. The separating situation is computed in finish.py "
               "(readings/separating-situations.json).")


def reading_set(uid, item):
    key = uid.replace(".", "-")
    admission = lambda other: {"who": "translator", "why": item["readings_note"] + PLACEHOLDER, "distinguishing_models": {other: "@MODEL"}}
    return {"id": f"force-{key}", "unit": uid, "version": 1, "status": "open", "models": {},
            "readings": [
                {"id": "strict", "kind": "norm", "meaning_id": f"pending-strict-{key}", "content": None,
                 "admission": admission("default")},
                {"id": "default", "kind": "norm", "meaning_id": f"pending-default-{key}", "content": None,
                 "admission": admission("strict")}]}


def all_models(env_dict, soft_contents):
    env = SoftEnvironment(env_dict)
    ext = SoftNormDocument(env, soft_contents).extended_env
    domains = {s: [s + "0"] for s in ext.sorts}
    data = {"complete": True, "domains": domains,
            "constants": {c: env_dict["vocabulary"]["constants"][c]["sort"] + "0"
                          for c in env_dict["vocabulary"]["constants"]},
            "relations": {p: [] for p in ext.predicates}}
    return FiniteModel.from_dict(ext, data).model_id, data


def write(path, meta, rest):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                     + b"\n---\n" + rest)


def main():
    prev_meta, rest = load_previous()
    env = environment(prev_meta["environment"])
    terms = open_terms(prev_meta.get("open_terms", []))
    out = {}
    for variant, path in (("main", RUN / "translation.ve.md"),
                          ("strict", RUN / "readings/all-strict.ve.md"),
                          ("default", RUN / "readings/all-default.ve.md")):
        units, reading_sets, narrowings, soft = build_units(prev_meta["units"], variant)
        meta = {k: v for k, v in prev_meta.items() if k not in ("environment", "units", "open_terms")}
        meta.update({"environment": env, "units": units, "open_terms": terms})
        if reading_sets:
            model_id, model = all_models(env, soft)
            for rs in reading_sets:
                rs["models"] = {model_id: model}
                for reading in rs["readings"]:
                    for other in reading["admission"]["distinguishing_models"]:
                        reading["admission"]["distinguishing_models"][other] = model_id
            meta["reading_sets"] = reading_sets
            meta["narrowings"] = narrowings
        meta = {k: meta[k] for k in sorted(meta)} if False else meta
        write(path, meta, rest)
        out[variant] = str(path.relative_to(ROOT))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
