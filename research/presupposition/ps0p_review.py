#!/usr/bin/env python3
"""PS-0p post-review checks (review of 0fbf57d8, findings 1 and 2); NEVER counted toward any check or bar.

  R1 (finding 2) Each class A unit alone: the pinned translation + only that unit's own predicate (the plan's
     wording) + the constant `anthropic` when its formula names it + that one unit converted. The product's loader's
     refusal is that unit's own reason, not another unit's.
  R2 (finding 1) The sort `entity`'s English noun is a field of the document (environment.vocabulary.sorts.entity
     .verbalisation). For the pinned noun ("entity", reserved) and for "thing"/"things": which candidate wordings the
     vocabulary lint admits, whether `human` keeps "{0} is human", and which plain sentences parse to which formula.
  R3 (finding 1) What the reviewer did not run: a full `ve document check`, with the separating situations
     regenerated (ps0p_explore.resituate), for (a) the noun change alone and (b) the noun change + `open_problem`
     worded "{0} is unsolved" + u0286 converted to "Some thing is unsolved."; the same readings and probe comparison
     as F3-F6.

Writes docs/research/evidence/presupposition/review.json. Run as ps0p_dryrun.py (memory limit, VE_RUST_TIMEOUT).
"""
from __future__ import annotations

import copy
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


d = _load("ps0p_dryrun")
x = _load("ps0p_explore")

from ve.ast import formula_from_data, formula_to_data  # noqa: E402
from ve.english import EnglishVocabulary, parse_english, render_english  # noqa: E402
from ve.environment import Environment  # noqa: E402

NOUNS = {"entity": {"singular": "entity", "plural": "entities"}, "thing": {"singular": "thing", "plural": "things"}}
UNIT_PREDICATE = {"u0013.presupposition": "core_value_of", "u0095.presupposition": "guideline_of",
                  "u0286.presupposition": "open_problem", "u0002.presupposition": "mission_of",
                  "u0235.presupposition": "nature_of"}
# (predicate, arity, wording, constant its existence formula names or None, uniqueness?). The plan's wordings, the
# reviewer's relational-noun attempts, owner-first "has" forms, and two unary wordings for "open problem".
CANDIDATES = [
    ("core_value_of", 2, "{0} is a core value of {1}", "claude", False),
    ("core_value_of", 2, "{0} belongs to the core values of {1}", "claude", False),
    ("core_value_of", 2, "{0} counts among the core values of {1}", "claude", False),
    ("core_value_of", 2, "{0} ranks among the core values of {1}", "claude", False),
    ("core_value_of", 2, "{0} serves as a core value for {1}", "claude", False),
    ("core_value_of", 2, "{0} is valued by {1}", "claude", False),
    ("has_core_value", 2, "{0} has core value {1}", "claude", False),
    ("guideline_of", 2, "{0} is a guideline of {1}", "anthropic", False),
    ("has_guideline", 2, "{0} has guideline {1}", "anthropic", False),
    ("mission_of", 2, "{0} is a mission of {1}", "anthropic", True),
    ("has_mission", 2, "{0} has mission {1}", "anthropic", True),
    ("nature_of", 2, "{0} is a nature of {1}", "claude", True),
    ("has_nature", 2, "{0} has nature {1}", "claude", True),
    ("open_problem", 1, "{0} is an open problem", None, False),
    ("open_problem", 1, "{0} is unsolved", None, False),
]
U0286 = "u0286.presupposition"
U0286_FENCE = "Some thing is unsolved."


def with_noun(meta: dict, noun: str) -> dict:
    meta = copy.deepcopy(meta)
    meta["environment"]["vocabulary"]["sorts"]["entity"]["verbalisation"] = dict(NOUNS[noun])
    return meta


def with_predicate(meta: dict, name: str, arity: int, wording: str | None, anthropic: bool) -> dict:
    meta = copy.deepcopy(meta)
    voc = meta["environment"]["vocabulary"]
    voc["predicates"][name] = {"arguments": ["entity"] * arity, "description": f"Recorded as {name} (PS-0p review).",
                               **({"verbalisation": wording} if wording else {})}
    if anthropic:
        voc["constants"][d.CONSTANT[0]] = d.CONSTANT[1]
    return meta


def formula(name: str, arity: int, const: str | None, unique: bool):
    body = ["unary", name, d.V0] if arity == 1 else (
        ["binary", name, d.V0, ["const", const]] if not name.startswith("has_") else ["binary", name, ["const", const], d.V0])
    if not unique:
        return ["exists", "entity", body]
    return d.unique(body, body)  # under the inner binder var 0 is the second variable, as in ps0p_dryrun.CLASS_A


def parse(env, sentence: str) -> dict:
    try:
        parsed = parse_english(env, sentence)
        return {"formulas": [formula_to_data(env, f) for f in parsed.formulas]}
    except Exception as e:  # the parser's refusal is the measurement
        return {"error": f"{type(e).__name__}: {e}"}


def plain_sentences(noun: str, name: str, arity: int, wording: str, const: str | None, unique: bool) -> list[str]:
    """Hand-written plain sentences for the formula: the plan's shapes with this noun."""
    a = "an" if noun[0] in "aeiou" else "a"
    if arity == 1:
        phrase = wording.removeprefix("{0} ")
        out = [f"Some {noun} {phrase}.", f"There is {a} {noun} that {phrase}.", f"Exactly one {noun} {phrase}."]
        if unique:
            out.append(f"Some {noun} {phrase}, and every {noun} that {phrase} is that {noun}.")
        return out
    owner = "Claude" if const == "claude" else "Anthropic"
    if name.startswith("has_"):
        phrase = wording.removeprefix("{0} ").removesuffix(" {1}")
        return [f"{owner} {phrase} some {noun}.", f"There is {a} {noun} such that {owner} {phrase} it."]
    phrase = wording.removeprefix("{0} ").removesuffix(" {1}")
    out = [f"Some {noun} {phrase} {owner}.", f"There is {a} {noun} that {phrase} {owner}."]
    if unique:
        out.append(f"Some {noun} {phrase} {owner}, and every {noun} that {phrase} {owner} is that {noun}.")
        out.append(f"Exactly one {noun} {phrase} {owner}.")
    return out


def check_and_probe(meta: dict, body: str, label: str, pinned: Path, pc: dict) -> dict:
    meta = x.resituate(meta)
    doc = d.write_doc(d.WORK / f"review-{label}.ve.md", meta, body)
    sc = d.ve("document", "check", doc, out=d.WORK / f"review-{label}-check.json")
    out = {"returncode": sc["returncode"], "stderr": sc["stderr"][-600:]}
    if sc["returncode"] == 0:
        s = json.loads(sc["stdout"])
        p_b, s_b = d.status_bytes(pc), d.status_bytes(s)
        out["admitted"] = s.get("admission", {}).get("admitted")
        out["status_delta"] = {k: s_b.get(k, 0) - p_b.get(k, 0) for k in sorted(set(p_b) | set(s_b))
                               if s_b.get(k, 0) != p_b.get(k, 0)}
        out["readings"] = {"pinned": d.readings_summary(pc), "scratch": d.readings_summary(s)}
        out["residual"] = {"pinned": pc["coverage"]["residual"], "scratch": s["coverage"]["residual"]}
        out["differences_after_normalising"] = sorted(k for k in set(pc) | set(s)
                                                      if d.normalise(pc.get(k)) != d.normalise(s.get(k)))
    probes = {}
    for name in ("conclusion-no-denial.json", "conclusion-no-claim-human.json"):
        q = d.RUN / "probes/nd" / name
        a = d.ve("document", "readings", pinned, "--conclusion", q)
        z = d.ve("document", "readings", doc, "--conclusion", q)
        try:
            same = d.normalise(json.loads(a["stdout"])) == d.normalise(json.loads(z["stdout"]))
        except json.JSONDecodeError:
            same = False
        probes[name] = {"pinned_returncode": a["returncode"], "scratch_returncode": z["returncode"],
                        "identical_normalised": same, "byte_identical_raw": a["stdout"] == z["stdout"]}
    out["probes"] = probes
    return out


def main() -> int:
    d.require_cap()
    d.WORK.mkdir(parents=True, exist_ok=True)
    meta, body = d.split(d.RUN / "translation.ve.md")
    pinned = d.WORK / "pinned.ve.md"
    pinned.write_bytes((d.RUN / "translation.ve.md").read_bytes())
    out = {"never_counted": True, "review_of": "0fbf57d8", "limits_at_start": d.limits()}

    # R1: each class A unit with only its own predicate declared.
    plan = {name: (args, verb) for name, (args, verb, _desc) in d.PREDICATES.items()}
    r1 = {}
    for uid, (fence, _expected) in d.CLASS_A.items():
        name = UNIT_PREDICATE[uid]
        args, verb = plan[name]
        m = with_predicate(meta, name, len(args), verb, "anthropic" in fence.lower())
        m, bd = d.convert(m, body, {uid: fence})
        r1[uid] = {"declared": {name: verb}, "fence": fence,
                   "loader": d.load_units(d.write_doc(d.WORK / f"review-alone-{uid}.ve.md", m, bd), [uid])}
    out["R1_unit_alone"] = r1

    # R2: wordings and sentences, pinned noun and "thing".
    fences = re.findall(r"```ve [^\n]*\n(.*?)```", body, re.S)
    out["pinned_fences"] = {"count": len(fences),
                            "using_entity_or_thing": sum(bool(re.search(r"\b(entit(y|ies)|things?)\b", f, re.I))
                                                         for f in fences)}
    r2 = {}
    for noun in NOUNS:
        rows = []
        for name, arity, wording, const, unique in CANDIDATES:
            m = with_predicate(with_noun(meta, noun), name, arity, wording, const == "anthropic")
            env = Environment.from_dict(m["environment"])
            v = EnglishVocabulary(env)
            row = {"predicate": name, "wording": wording, "selected": v.predicates[name],
                   "accepted": v.predicates[name] == wording, "human": v.predicates["human"],
                   "sort_noun": v.sorts["entity"],
                   "lint": sorted({i.code for i in v.issues if f"/predicates/{name}/" in i.path})}
            target = formula(name, arity, const, False)
            target_unique = formula(name, arity, const, True) if unique else None
            sentences = plain_sentences(noun, name, arity, wording, const, unique)
            rendered = [render_english(formula_from_data(env, f), env) + "." for f in (target, target_unique) if f]
            row["sentences"] = {}
            for s in dict.fromkeys(sentences + rendered):
                p = parse(env, s)
                if "formulas" in p:
                    p["is_existence"] = p["formulas"] == [target]
                    p["is_existence_and_uniqueness"] = target_unique is not None and p["formulas"] == [target_unique]
                    p["plain"] = '"' not in s and "(a)" not in s
                p["rendered_by_ve"] = s in rendered
                row["sentences"][s] = p
            rows.append(row)
        r2[noun] = rows
    out["R2_wordings"] = r2

    # R3: full checks, situations regenerated.
    pc = json.loads(d.ve("document", "check", pinned)["stdout"])
    noun_only = with_noun(meta, "thing")
    out["R3_noun_only"] = check_and_probe(noun_only, body, "noun-only", pinned, pc)
    m = with_predicate(noun_only, "open_problem", 1, "{0} is unsolved", False)
    m, bd = d.convert(m, body, {U0286: U0286_FENCE})
    out["R3_u0286_unsolved"] = {"fence": U0286_FENCE,
                                "loader": d.load_units(d.write_doc(d.WORK / "review-u0286-load.ve.md", m, bd), [U0286]),
                                "unit_bytes": next(u["span"][1] - u["span"][0] for u in meta["units"] if u["id"] == U0286),
                                **check_and_probe(m, bd, "u0286-unsolved", pinned, pc)}
    out["limits_at_end"] = d.limits()
    (d.OUT / "review.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(r1, ensure_ascii=False)[:1500])
    for noun, rows in r2.items():
        for r in rows:
            ok = [s for s, p in r["sentences"].items() if p.get("is_existence") or p.get("is_existence_and_uniqueness")]
            print(noun, r["wording"], "accepted" if r["accepted"] else r["lint"], "human ok" if r["human"] == "{0} is human" else "HUMAN BROKEN", ok)
    print(json.dumps({k: out[k] for k in ("pinned_fences", "R3_noun_only", "R3_u0286_unsolved")}, ensure_ascii=False)[:3000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
