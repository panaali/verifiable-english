#!/usr/bin/env python3
"""PS-0p exploration, run after the pre-registered dry run failed; NEVER counted toward any check or bar.

Question: with no product code, can the pilot carry class A's formulas at all, and in what English?
  V1 = the pinned translation + the five predicates declared WITHOUT a verbalisation + the constant `anthropic`.
  For each class A formula (ps0p_dryrun.CLASS_A), VE's own renderer (`ve.english.render_english`) writes the sentence
  (plus the final period the fence parser requires); VE's English parser must read back exactly that formula, and
  render it to the same sentence. The units that do are converted together; the reading sets' separating situations
  are regenerated as the pilot's `nd.py` does after any vocabulary change (`resituate`); and the scratch translation
  gets the same check, readings and probe comparison as F3-F6.

Writes docs/research/evidence/presupposition/explore.json. Run as ps0p_dryrun.py (memory limit, VE_RUST_TIMEOUT).
"""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ps0p_dryrun", HERE / "ps0p_dryrun.py")
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

from ve.ast import formula_from_data, formula_to_data  # noqa: E402
from ve.english import EnglishVocabulary, parse_english, render_english  # noqa: E402
from ve.environment import Environment  # noqa: E402

_pspec = importlib.util.spec_from_file_location("readings_s1_pilot", d.ROOT / "tools/readings_s1_pilot.py")
_pilot = importlib.util.module_from_spec(_pspec)
_pspec.loader.exec_module(_pilot)


def bare_vocabulary(meta: dict) -> dict:
    meta = copy.deepcopy(meta)
    voc = meta["environment"]["vocabulary"]
    for name, (args, _verb, desc) in d.PREDICATES.items():
        voc["predicates"][name] = {"arguments": args, "description": desc}
    voc["constants"][d.CONSTANT[0]] = d.CONSTANT[1]
    return meta


def resituate(meta: dict) -> dict:
    """The pilot's own regeneration of separating situations after a vocabulary change: a transcription of
    `find_situations` in manage-agents/pilots/claude-constitution/run-20261012T1800Z/nd.py (pilot code, not
    product code), which a pilot run executes in its `nd.py all` step. It fails loudly where nd.py would."""
    from ve.errors import VEError
    from ve.readings_route import document_wire, run_lean
    from ve.readings_s1 import Decoded, guard_base, record_situations, search
    units = [{"id": u["id"], "kind": u["kind"], "content": u.get("content")} for u in _pilot._flat(meta["units"])]
    document = document_wire(units, meta["reading_sets"])
    [row] = run_lean([{"id": "e", "kind": "readings-elaborate", "environment": meta["environment"],
                       "document": document}])
    if row.get("status") != "ok" or "filled" not in row:
        raise VEError("elaborate refused: " + json.dumps(row)[:600])
    decoded = Decoded(meta["environment"], document, row["filled"], row.get("fill_premises"))
    sets = []
    for item in meta["reading_sets"]:
        R = decoded.doc.set_by_id(item["id"])
        if R is None or not Decoded.content_bearing(R):
            sets.append(item)
            continue
        with_content = [i for i, a in enumerate(R.candidates) if a.content is not None]
        if len(with_content) < 2:
            sets.append(item)
            continue
        hints = [guard_base(decoded, item["id"], i) for i in with_content]
        found = search(meta["environment"], document, item["id"], max_size=1, hints=hints, decoded=decoded, filled=row)
        sets.append(record_situations(item, {k: v for k, v in found.items() if v is not None}))
    return {**meta, "reading_sets": sets}


def main() -> int:
    d.require_cap()
    d.WORK.mkdir(parents=True, exist_ok=True)
    meta, body = d.split(d.RUN / "translation.ve.md")
    pinned = d.WORK / "pinned.ve.md"
    pinned.write_bytes((d.RUN / "translation.ve.md").read_bytes())
    out = {"never_counted": True, "question": next(l for l in __doc__.split("\n") if l.startswith("Question")),
           "limits_at_start": d.limits(), "variants": {}}

    # Which wordings each vocabulary gives (pinned, plan's verbalisations, bare).
    for label, m in (("pinned", meta), ("plan_verbalisations", d.with_vocabulary(meta)), ("bare", bare_vocabulary(meta))):
        env = Environment.from_dict(m["environment"])
        v = EnglishVocabulary(env)
        out["variants"][label] = {"sort_entity_noun": v.sorts["entity"], "human": v.predicates["human"],
                                  **{k: v.predicates[k] for k in d.PREDICATES if k in v.predicates},
                                  "lint": sorted({f"{i.path.split('/')[3]}:{i.code}" for i in v.issues
                                                  if i.path.split('/')[3] in (*d.PREDICATES, "human")})}

    bm = bare_vocabulary(meta)
    env = Environment.from_dict(bm["environment"])
    units = {}
    for uid, (_plan_fence, formula) in d.CLASS_A.items():
        # The renderer writes no final period; the fence parser requires one ("End it with a period.").
        sentence = render_english(formula_from_data(env, formula), env) + "."
        row = {"rendered": sentence}
        try:
            parsed = parse_english(env, sentence)
            assert len(parsed.formulas) == 1
            content = formula_to_data(env, parsed.formulas[0])
            row["exact"] = content == formula
            row["rerendered_same"] = render_english(parsed.formulas[0], env) + "." == sentence
        except Exception as e:  # the parser's refusal is the measurement
            row["error"] = f"{type(e).__name__}: {e}"
        units[uid] = row
    out["units"] = units
    ok = {u: r["rendered"] for u, r in units.items() if r.get("exact") and r.get("rerendered_same")}
    out["converted"] = sorted(ok)

    # Control: the transcription of the pilot's situation search reproduces the pinned reading sets.
    out["resituate_pinned_identical"] = resituate(meta)["reading_sets"] == meta["reading_sets"]
    pc = json.loads(d.ve("document", "check", pinned)["stdout"])
    sm, sb = d.convert(bm, body, ok)
    sm = resituate(sm)
    scratch = d.write_doc(d.WORK / "explore-scratch.ve.md", sm, sb)
    sc = d.ve("document", "check", scratch, out=d.WORK / "explore-scratch-check.json")
    x = {"returncode": sc["returncode"], "stderr": sc["stderr"][-600:]}
    if sc["returncode"] == 0:
        s = json.loads(sc["stdout"])
        p_b, s_b = d.status_bytes(pc), d.status_bytes(s)
        x["admitted"] = s.get("admission", {}).get("admitted")
        x["status_delta"] = {k: s_b.get(k, 0) - p_b.get(k, 0) for k in sorted(set(p_b) | set(s_b))
                             if s_b.get(k, 0) != p_b.get(k, 0)}
        x["converted_bytes"] = sum(u["span"][1] - u["span"][0] for u in meta["units"] if u["id"] in ok)
        x["readings"] = {"pinned": d.readings_summary(pc), "scratch": d.readings_summary(s)}
        x["residual"] = {"pinned": pc["coverage"]["residual"], "scratch": s["coverage"]["residual"]}
        x["differences_after_normalising"] = sorted(k for k in set(pc) | set(s)
                                                    if d.normalise(pc.get(k)) != d.normalise(s.get(k)))
        rd = d.ve("document", "render", scratch, out=d.WORK / "explore-scratch-render.md")
        source = (d.RUN.parent / "source/claude-constitution.md").read_bytes()
        x["rendered_lines"] = {}
        for uid in ok:
            a, z = next(u["span"] for u in meta["units"] if u["id"] == uid)
            x["rendered_lines"][uid] = d.rendered_reading(rd["stdout"], source[a:z].decode("utf-8"))
    out["scratch_check"] = x
    probes = {}
    for name in ("conclusion-no-denial.json", "conclusion-no-claim-human.json"):
        q = d.RUN / "probes/nd" / name
        a = d.ve("document", "readings", pinned, "--conclusion", q)
        z = d.ve("document", "readings", scratch, "--conclusion", q)
        try:
            same = d.normalise(json.loads(a["stdout"])) == d.normalise(json.loads(z["stdout"]))
        except json.JSONDecodeError:
            same = False
        probes[name] = {"pinned_returncode": a["returncode"], "scratch_returncode": z["returncode"],
                        "identical_normalised": same, "byte_identical_raw": a["stdout"] == z["stdout"]}
    out["probes"] = probes
    out["limits_at_end"] = d.limits()
    (d.OUT / "explore.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("variants", "converted")}, ensure_ascii=False, indent=1)[:4000])
    print(json.dumps({u: {k: r.get(k) for k in ("rendered", "exact", "rerendered_same")} for u, r in units.items()},
                     ensure_ascii=False, indent=1))
    print(json.dumps(x, ensure_ascii=False)[:2500])
    print(json.dumps(probes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
