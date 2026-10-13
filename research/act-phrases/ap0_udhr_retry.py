"""AP-0 item 1: re-try the 11 M1 units as plain entitlements (rule: docs/research/act-phrases-phase1.md 1.2).

    prlimit --as=8589934592 uv run python research/act-phrases/ap0_udhr_retry.py

Writes one companion document per unit, in the pilot's own entitlement form (as readings/u081.entitlement.ve.md of
run 20261012T1800Z), to docs/research/evidence/act-phrases/udhr-retry/, checks and renders each with the ordinary entry
points, applies C1 to C4, and writes docs/research/evidence/act-phrases/udhr-retry.json. Reads the pilot run read-only.
No model call.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ve.document import check_document, render_document  # noqa: E402

RUN = Path("/home/seyran/code/manage-agents/pilots/udhr/run-20261012T1800Z")
OUT = ROOT / "docs/research/evidence/act-phrases"
PROFILES = ["documents@1", "norm-defaults@0", "norms@0", "relational-fol@0"]
STOP = set("a an the of to in and or for by his him himself he its it is be has have had any all every everyone which "
           "that who at from with as on this such shall will".split())
PERSON = {"description": "a human person", "verbalisation": {"plural": "people", "singular": "person"}}


def sort(desc, singular, plural):
    return {"description": desc, "verbalisation": {"plural": plural, "singular": singular}}


def plain(args, desc, verbal):
    return {"arguments": args, "description": desc, "regulated": {"default": "unspecified", "role": "plain"},
            "verbalisation": verbal}


def base(args, desc):
    return {"arguments": args, "description": desc}


def term(name, factor):
    return {"arguments": [], "decided_by": "unstated", "factors": [factor], "jurisdiction": "universal", "name": name,
            "necessary": [], "precedents": [], "sufficient": [], "version": 1}


def var(i):
    return ["var", i]


def un(p, i):
    return ["unary", p, var(i)]


def bi(p, i, j):
    return ["binary", p, var(i), var(j)]


# Per unit: the entitlement predicate (first), other predicates, sorts, open terms, guard; the C4 table of 1.2
# ("carry": phrases; "arity2": the argument the ledger asks for); the hidden-structure list of 1.2.
UNITS = {
    "u039": dict(
        preds={"is_entitled_to_a_fair_hearing_in_full_equality": plain(
                   ["person", "determination"],
                   "The person is entitled in full equality to a fair and public hearing by an independent and "
                   "impartial tribunal in the determination",
                   "{0} is entitled in full equality to a fair and public hearing by an independent and impartial "
                   "tribunal in {1}"),
               "determines_rights_and_obligations_of": base(
                   ["determination", "person"], "The determination is of the rights and obligations of the person"),
               "determines_criminal_charge_against": base(
                   ["determination", "person"], "The determination is of a criminal charge against the person")},
        sorts={"person": PERSON, "determination": sort("a determination by a tribunal", "determination",
                                                       "determinations")},
        terms=[term("fair_and_public_hearing", "what makes a hearing fair and public"),
               term("independent_and_impartial_tribunal", "what makes a tribunal independent and impartial"),
               term("full_equality", "what hearing a person in full equality requires")],
        guard=["or", bi("determines_rights_and_obligations_of", 0, 1), bi("determines_criminal_charge_against", 0, 1)],
        carry=["in full equality", "fair and public hearing by an independent and impartial tribunal",
               "of his rights and obligations", "of any criminal charge against him"],
        arity2=True, hidden=[]),
    "u041": dict(
        preds={"has_the_right_to_be_presumed_innocent": plain(
                   ["person"],
                   "The person has the right to be presumed innocent until proved guilty according to law in a public "
                   "trial at which they have had all the guarantees necessary for their defence",
                   "{0} has the right to be presumed innocent until proved guilty according to law in a public trial "
                   "at which they have had all the guarantees necessary for their defence"),
               "is_charged_with_a_penal_offence": base(["person"], "The person is charged with a penal offence")},
        sorts={"person": PERSON},
        terms=[term("guarantees_necessary_for_defence", "which guarantees are necessary for a defence")],
        guard=un("is_charged_with_a_penal_offence", 0),
        carry=["until proved guilty according to law in a public trial at which he has had all the guarantees "
               "necessary for his defence", "charged with a penal offence"],
        arity2=False, hidden=["time ('until proved guilty'): events-time-causation"]),
    "u076": dict(
        preds={"has_the_right_to_take_part_in_government": plain(
                   ["person"],
                   "The person has the right to take part in the government of their country, directly or through "
                   "freely chosen representatives",
                   "{0} has the right to take part in the government of their country, directly or through freely "
                   "chosen representatives")},
        sorts={"person": PERSON},
        terms=[term("freely_chosen_representatives", "what makes the choice of representatives free")],
        guard=["top"],
        carry=["the government of his country", "directly or through freely chosen representatives"],
        arity2=False, hidden=["two readings of 'directly or through ...' (AP-4)"]),
    "u079b": dict(
        preds={"is_held_by_secret_vote_or_equivalent_free_procedure": plain(
                   ["election"],
                   "The election is held by secret vote or by equivalent free voting procedures",
                   "{0} is held by secret vote or by equivalent free voting procedures")},
        sorts={"election": sort("an election that expresses the will of the people", "election", "elections")},
        terms=[term("equivalent_free_voting_procedures", "which voting procedures are free and equivalent to a "
                                                         "secret vote")],
        guard=["top"],
        carry=["by secret vote or by equivalent free voting procedures", "elections"],
        arity2=False, hidden=["an obligation ('shall') stated as a plain property, with a disjunctive act (AP-3)",
                              "the subject is carried from u079a, which is UNFORMALISED (time)"]),
    "u082": dict(
        preds={"is_entitled_to_realization_of_rights": plain(
                   ["person"],
                   "The person is entitled to realization, through national effort and international co-operation "
                   "and in accordance with the organization and resources of each State, of the economic, social "
                   "and cultural rights indispensable for their dignity and the free development of their personality",
                   "{0} is entitled to realization, through national effort and international co-operation and in "
                   "accordance with the organization and resources of each State, of the economic, social and "
                   "cultural rights indispensable for their dignity and the free development of their personality")},
        sorts={"person": PERSON},
        terms=[term("organization_and_resources_of_each_state", "what the organization and resources of each "
                                                                "State allow"),
               term("indispensable_rights", "which economic, social and cultural rights are indispensable")],
        guard=["top"],
        carry=["through national effort and international co-operation",
               "in accordance with the organization and resources of each State",
               "the economic, social and cultural rights indispensable for his dignity and the free development of "
               "his personality"],
        arity2=False, retry_without_verbalisation=True,
        hidden=["rights as objects (the object ranges over rights)",
                              "the limit is cited by the other Article 22 to 27 units"]),
    "u085": dict(
        preds={"has_the_right_to_equal_pay_for_equal_work": plain(
                   ["person"],
                   "The person, without any discrimination, has the right to equal pay for equal work",
                   "{0}, without any discrimination, has the right to equal pay for equal work")},
        sorts={"person": PERSON},
        terms=[term("equal_pay_for_equal_work", "which work is equal and which pay is equal"),
               term("discrimination", "what counts as discrimination")],
        guard=["top"],
        carry=["equal pay for equal work", "without any discrimination"],
        arity2=False, hidden=[]),
    "u086": dict(
        preds={"has_the_right_to_just_and_favourable_remuneration": plain(
                   ["person"],
                   "The person has the right to just and favourable remuneration ensuring for themselves and their "
                   "family an existence worthy of human dignity, and supplemented, if necessary, by other means of "
                   "social protection",
                   "{0} has the right to just and favourable remuneration ensuring for themselves and their family an "
                   "existence worthy of human dignity, and supplemented, if necessary, by other means of social "
                   "protection"),
               "works": base(["person"], "The person works")},
        sorts={"person": PERSON},
        terms=[term("just_and_favourable_remuneration", "what remuneration is just and favourable"),
               term("existence_worthy_of_human_dignity", "what existence is worthy of human dignity")],
        guard=un("works", 0),
        carry=["ensuring for himself and his family an existence worthy of human dignity",
               "supplemented, if necessary, by other means of social protection", "who works"],
        arity2=False, hidden=["a condition ('if necessary') inside the object (research R4)"]),
    "u091": dict(
        preds={"has_the_right_to_an_adequate_standard_of_living": plain(
                   ["person"],
                   "The person has the right to a standard of living adequate for the health and well-being of "
                   "themselves and of their family, including food, clothing, housing and medical care and necessary "
                   "social services",
                   "{0} has the right to a standard of living adequate for the health and well-being of themselves "
                   "and of their family, including food, clothing, housing and medical care and necessary social "
                   "services")},
        sorts={"person": PERSON},
        terms=[term("adequate_standard_of_living", "what standard of living is adequate for health and "
                                                   "well-being")],
        guard=["top"],
        carry=["adequate for the health and well-being of himself and of his family",
               "including food, clothing, housing and medical care and necessary social services"],
        arity2=False, hidden=[]),
    "u092": dict(
        preds={"has_the_right_to_security_in_lack_of_livelihood": plain(
                   ["person"],
                   "The person has the right to security in the event of unemployment, sickness, disability, "
                   "widowhood, old age or other lack of livelihood in circumstances beyond their control",
                   "{0} has the right to security in the event of unemployment, sickness, disability, widowhood, old "
                   "age or other lack of livelihood in circumstances beyond their control")},
        sorts={"person": PERSON},
        terms=[term("circumstances_beyond_control", "which circumstances are beyond a person's control")],
        guard=["top"],
        carry=["in the event of unemployment, sickness, disability, widowhood, old age or other lack of livelihood",
               "in circumstances beyond his control"],
        arity2=False, hidden=["two readings of 'in circumstances beyond his control' (AP-4)"]),
    "u106": dict(
        preds={"has_the_right_to_protection_of_interests_in": plain(
                   ["person", "production"],
                   "The person has the right to the protection of the moral and material interests resulting from "
                   "the production",
                   "{0} has the right to the protection of the moral and material interests resulting from {1}"),
               "is_author_of": base(["person", "production"], "The person is the author of the production"),
               "is_scientific": base(["production"], "The production is scientific"),
               "is_literary": base(["production"], "The production is literary"),
               "is_artistic": base(["production"], "The production is artistic")},
        sorts={"person": PERSON, "production": sort("a production, a work someone produces", "production",
                                                    "productions")},
        terms=[term("moral_and_material_interests", "which moral and material interests result from a "
                                                    "production")],
        guard=["and", bi("is_author_of", 1, 0),
               ["or", ["or", un("is_scientific", 0), un("is_literary", 0)], un("is_artistic", 0)]],
        carry=["the moral and material interests", "scientific, literary or artistic", "of which he is the author"],
        arity2=True, hidden=[],
        retry=("the kinds as one guard predicate (C4 reads a phrase in one text)",
               {"preds": {"has_the_right_to_protection_of_interests_in": plain(
                              ["person", "production"],
                              "The person has the right to the protection of the moral and material interests "
                              "resulting from the production",
                              "{0} has the right to the protection of the moral and material interests resulting "
                              "from {1}"),
                          "is_author_of": base(["person", "production"], "The person is the author of the production"),
                          "is_scientific_literary_or_artistic": base(
                              ["production"], "The production is scientific, literary or artistic")},
                "guard": ["and", bi("is_author_of", 1, 0), un("is_scientific_literary_or_artistic", 0)]})),
    "u108": dict(
        preds={"is_entitled_to_a_social_and_international_order": plain(
                   ["person"],
                   "The person is entitled to a social and international order in which the rights and freedoms set "
                   "forth in this Declaration can be fully realized",
                   "{0} is entitled to a social and international order in which the rights and freedoms set forth in "
                   "this Declaration can be fully realized")},
        sorts={"person": PERSON},
        terms=[term("fully_realized", "when the rights and freedoms of the Declaration are fully realized")],
        guard=["top"],
        carry=["a social and international order in which the rights and freedoms set forth in this Declaration can "
               "be fully realized"],
        arity2=False, hidden=["modality ('can be fully realized')"]),
}


def words(text):
    out = []
    for w in re.split(r"[^a-z]+", text.lower()):
        if w and w not in STOP:
            out.append(w[:-1] if w.endswith("s") and len(w) > 3 else w)
    return out


def build(uid, spec, source):
    entitlement = next(iter(spec["preds"]))
    meta = {"environment": {"language": "ve.core@0.2", "profiles": PROFILES,
                            "spec_revision": "ve-v0.2-expand2-2026-09-25",
                            "vocabulary": {"constants": {}, "predicates": spec["preds"], "sorts": spec["sorts"]}},
            "format": "ve-document@1", "open_terms": spec["terms"],
            "units": [{"content": {"norm": {"guard": spec["guard"], "name": f"{uid}-entitlement", "over": [],
                                            "predicate": entitlement, "sign": True, "unless": []}},
                       "id": f"{uid}_entitlement", "kind": "norm",
                       "meaning": {"open": [t["name"] for t in spec["terms"]]},
                       "span": [0, len(source.encode())], "support": "none"}]}
    return "---\n" + json.dumps(meta, indent=2, ensure_ascii=False) + "\n---\n" + source, entitlement


def own_texts(spec):
    texts = []
    for p in spec["preds"].values():
        texts += [p["description"], p.get("verbalisation", "")]
    texts += [s["description"] for s in spec["sorts"].values()]
    texts += [s["verbalisation"]["plural"] for s in spec["sorts"].values()]
    for t in spec["terms"]:
        texts += [t["name"].replace("_", " "), *t["factors"]]
    return texts


def variants(spec):
    """The first attempt; then, only for a unit whose first attempt failed and is marked so, a second authoring attempt
    (both are recorded): u106 with its kinds in one guard predicate; u082 without the display-only verbalisation, whose
    256-character limit (lean/VE/Bridge.lean:123) the full wording exceeds, the description still carrying every
    word, which C3 and C4 check."""
    yield dict(spec, variant="full description and verbalisation")
    if "retry" in spec:
        label, overrides = spec["retry"]
        yield dict(spec, **overrides, variant=label)
    if spec.get("retry_without_verbalisation"):
        preds = {k: {f: v for f, v in p.items() if f != "verbalisation"} if k == next(iter(spec["preds"])) else p
                 for k, p in spec["preds"].items()}
        yield dict(spec, preds=preds, variant="no verbalisation on the entitlement (description carries the words)")


def attempt(uid, spec, source, nbytes):
    text, entitlement = build(uid, spec, source)
    path = OUT / "udhr-retry" / f"{uid}.entitlement.ve.md"
    path.write_text(text)
    row = {"unit": uid, "bytes": nbytes, "source": source, "variant": spec["variant"],
           "document": str(path.relative_to(ROOT)), "entitlement": entitlement, "hidden_structure": spec["hidden"]}
    try:
        report = check_document(path)
        row["C1"] = True
        row["check_status"] = (report.get("premises") or {}).get("status")
        cov = report["coverage"]
        row["coverage"] = {k: cov[k] for k in ("coverage_percent", "bytes_by_status", "residual_total")}
        row["C2"] = cov["coverage_percent"] == 100 and "UNFORMALISED" not in cov["bytes_by_status"]
        row["rendered"] = render_document(path)
        row["renders_classified_as"] = "classified as" in row["rendered"]
    except Exception as exc:  # a refusal is the C1 result, recorded verbatim
        row["C1"] = row["C2"] = False
        row["error"] = f"{type(exc).__name__}: {getattr(exc, 'message', None) or exc}"[:800]
    own = set(w for t in own_texts(spec) for w in words(t))
    row["C3_missing"] = sorted(set(words(source)) - own)
    row["C3"] = not row["C3_missing"]
    carried = []
    for phrase in spec["carry"]:
        need = set(words(phrase))
        carried.append({"phrase": phrase, "in_one_text": any(need <= set(words(t)) for t in own_texts(spec))})
    ent = spec["preds"][entitlement]
    # A guard variable counts from the last argument: in a rule over (person, x), var 0 is x and var 1 the person.
    guard = json.dumps(spec["guard"])
    guard_on_both = json.dumps(["var", 0]) in guard and json.dumps(["var", 1]) in guard
    row["C4_carry"] = carried
    row["C4_argument"] = (len(ent["arguments"]) == 2 and guard_on_both) if spec["arity2"] else None
    row["C4"] = all(c["in_one_text"] for c in carried) and row["C4_argument"] is not False
    row["loads_as_opaque_entitlement"] = row["C1"] and row["C2"] and row["C3"] and row["C4"]
    row["expressible_today"] = "yes" if row["loads_as_opaque_entitlement"] and not spec["hidden"] else "no"
    if not row["loads_as_opaque_entitlement"]:
        failed = [c for c in ("C1", "C2", "C3", "C4") if not row[c]]
        row["reason"] = "fails " + ", ".join(failed) + (f": {row['error']}" if "error" in row else "")
    elif spec["hidden"]:
        row["reason"] = "loads as one opaque entitlement only by hiding, in its name: " + "; ".join(spec["hidden"])
    else:
        row["reason"] = ("loads as one opaque entitlement carrying every word and the argument the ledger asks for; "
                         "the act stays one string, as under AP-1; pending the pilot's audit")
    return row


def main():
    units = {u["id"]: u for u in json.loads((RUN / "units.json").read_text())["units"]}
    (OUT / "udhr-retry").mkdir(parents=True, exist_ok=True)
    rows = []
    for uid, first in UNITS.items():
        unit = units[uid]
        source = unit["source"]
        nbytes = unit["span"][1] - unit["span"][0]
        attempts = []
        for spec in variants(first):
            row = attempt(uid, spec, source, nbytes)
            attempts.append(row)
            if row["loads_as_opaque_entitlement"]:
                break
        row = dict(attempts[-1])
        row["attempts"] = [{k: a[k] for k in ("variant", "C1", "C2", "C3", "C4") if k in a} |
                           ({"error": a["error"]} if "error" in a else {}) for a in attempts]
        rows.append(row)
        print(uid, nbytes, row["variant"], row["C1"], row["C2"], row["C3"], row["C4"], row["expressible_today"],
              row.get("check_status"), row.get("error", "")[:200], row["C3_missing"], flush=True)

    def tally(pred):
        sel = [r for r in rows if pred(r)]
        return {"units": [r["unit"] for r in sel], "count": len(sel), "bytes": sum(r["bytes"] for r in sel)}

    result = {"run": str(RUN), "rule": "docs/research/act-phrases-phase1.md 1.2", "profiles": PROFILES,
              "m1_before": {"count": 11, "bytes": 1860},
              "m1_after_primary": tally(lambda r: r["expressible_today"] == "no"),
              "m1_after_loose": tally(lambda r: not r["loads_as_opaque_entitlement"]),
              "credited_to_ap0": tally(lambda r: r["expressible_today"] == "yes"),
              "units": rows}
    (OUT / "udhr-retry.json").write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: result[k] for k in ("m1_after_primary", "m1_after_loose", "credited_to_ap0")}))


if __name__ == "__main__":
    main()
