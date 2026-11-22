"""Plain-English explanation of one Winter Fuel Payment profile (release B, checklist item 4).

For each answer (questions 1 to 4) it prints: the answer; the clauses used, each as the
rules.json gloss with the quoted source text it reads (from the four files in source/); the
bridges and adopted readings it rests on, as plain-English assumptions; for questions 3 and 4,
the guide's "over £35,000" section, shown as an assumption (its legal basis is not pinned);
and the number of Lean step certificates behind the answer.

The answers come from the staged route of run.py (one derived fact per step, each step a
certificate, each answer a `documents@1` document Lean admits). An answer whose document Lean
does not admit is OPEN, as in run.py. Nothing here reads a profile's `key`.

Usage: python usecases/eligibility/explain.py <profile id | profile.json> [--no-lean]
A profile file holds one case in the cases.json form ({"applicant": {...}, "housemate": ...});
fields it leaves out take the cases.json defaults.

Importable: `explain(profile) -> str`, `explanation(profile) -> dict` (the same content as data).
"""
from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for _path in (str(ROOT), str(HERE)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import run as R  # noqa: E402
import translation as T  # noqa: E402
from ve.environment import Environment  # noqa: E402

SOURCES = {  # the four source files: name -> (file, title)
    "S1": ("uksi-2025-969-made.txt", "The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969)"),
    "S2": ("wfp-print.txt", "The GOV.UK guide “Winter Fuel Payment”"),
    "S3": ("uksi-2005-3360-reg2.txt", "The Social Security (Hospital In-Patients) Regulations 2005 (SI 2005/3360)"),
    "Sch4": ("ukpga-1995-26-sch4.txt", "The Pensions Act 1995, Schedule 4"),
}

# Rule (its `rule` field in rules.json) -> (source, the clause it reads, [(line, opening words)]).
# Each quote is the whole source line; the words given are checked to be on it, so a
# changed source file fails loudly instead of quoting the wrong text.
_REG2 = (60, "2. Subject to regulation 4")
_REG4_2 = (84, "(2) This paragraph applies where, throughout")
CLAUSES = {
    "R2": ("S1", "regulation 2(a)", [_REG2, (61, "(a)in or before the qualifying week")]),
    "R3": ("S1", "regulation 2(b)", [_REG2, (62, "(b)in respect of any day")]),
    "R80": ("S1", "regulation 3 (the age of 80 in or before the qualifying week)",
            [(73, "(4) Subject to paragraphs (5) and (6)")]),
    "R4": ("S1", "regulation 1(3), “relevant benefit”",
           [(41, "“relevant benefit” means"), (42, "(a)"), (43, "income support"), (44, "(b)"),
            (45, "an income-based jobseeker"), (46, "(c)"), (47, "state pension credit"), (48, "(d)"),
            (49, "an income-related employment"), (50, "(e)"), (51, "universal credit")]),
    "R5a": ("S1", "regulation 1(4)(a), “residential care”",
            [(52, "(4) In these Regulations, a person"), (53, "(a)is in residential care"), (54, "(i)a care home"),
             (55, "(ii)an independent hospital"), (56, "(iii)accommodation provided"), (57, "throughout the qualifying week")]),
    "R6": ("S1", "regulation 1(4)(b), “lives with”", [(52, "(4) In these Regulations, a person"), (58, "(b)lives with a person")]),
    "R7": ("S1", "regulation 4(2)(a)", [_REG4_2, (85, "(a)a partner of and living with")]),
    "R8a": ("S3", "regulation 2(5)", [(13, "(5) For the purposes of paragraph (4)")]),
    "R8b": ("S1", "regulation 4(2)(b)", [_REG4_2, (86, "(b)receiving free in-patient treatment")]),
    "R9": ("S1", "regulation 4(2)(c)", [_REG4_2, (87, "(c)detained in custody")]),
    "R10": ("S1", "regulation 4(3)", [(88, "(3) This paragraph applies where P is in residential care")]),
    "R11": ("S1", "regulation 4(4)", [(89, "(4) This paragraph applies where, having been")]),
    "R12": ("S1", "regulations 4(5) and (6) and 5(1)",
            [(90, "(5) Subject to paragraph (6)"), (91, "(6) Paragraph (5) does not apply"), (92, "(a)a winter fuel payment has been made"),
             (93, "(b)regulation 5(2) applies"), (95, "5.—(1) The Secretary of State may")]),
    "R13a": ("S1", "regulation 4(1)", [(83, "4.—(1) Regulation 2 does not apply")]),
    "R13b": ("S1", "regulation 2, read with regulation 4(1)", [_REG2, (83, "4.—(1) Regulation 2 does not apply")]),
    "R14.1": ("S1", "regulation 3(1)", [(64, "3.—(1) Subject to paragraphs (2) and (3)")]),
    "R14.2": ("S1", "regulation 3(2)",
              [(65, "(2) Where P has not reached the age of 80"), (66, "(a)a relevant benefit has not been"), (67, "(b)P is"),
               (68, "(i)in that week, living with"), (69, "(ii)in residential care")]),
    "R14.3": ("S1", "regulation 3(3)",
              [(70, "(3) Where P has not reached the age of 80"), (71, "(a)a relevant benefit has been"), (72, "(b)in that week, P is the partner")]),
    "R15.4": ("S1", "regulation 3(4)", [(73, "(4) Subject to paragraphs (5) and (6)")]),
    "R15.5": ("S1", "regulation 3(5)",
              [(74, "(5) Subject to paragraph (6)"), (75, "(a)a relevant benefit has not been"), (76, "(b)in that week, P is living with")]),
    "R15.6": ("S1", "regulation 3(6)",
              [(77, "(6) Where P has reached the age of 80"), (78, "(a)a relevant benefit has not been"), (79, "(b)P is"),
               (80, "(i)in that week, living with"), (81, "(ii)in residential care")]),
    # The guide's section 7: shown as an assumption, never as a clause of the Regulations (O6).
    "R16a": ("S2", "section 7, “If your income is over £35,000”",
             [(138, "7. If your income is over £35,000"), (139, "If your total income is over £35,000"),
              (140, "Your partner’s income does not count")]),
    "R16c": ("S2", "section 7, “If your income is over £35,000”", [(139, "If your total income is over £35,000")]),
    "B1": ("S1", "regulation 1(3), “qualifying week”", [(40, "“qualifying week” means")]),
}
CLAUSES["R5b"] = CLAUSES["R5a"]
CLAUSES["R7a"] = CLAUSES["R7b"] = (*CLAUSES["R7"][:2], [_REG4_2])
CLAUSES["R8c"] = CLAUSES["R8b"]
CLAUSES["R14a"] = CLAUSES["R14.3"]
CLAUSES["R16b"] = CLAUSES["R16a"]
for _rid, (_unit, _line, _sentence) in T.GUIDE_SENTENCES.items():
    CLAUSES[_rid] = ("S2", "the guide", [(_line, _sentence[:30])])
GUIDE_RULES = {"R16a", "R16b", "R16c"}  # read from the guide; shown as the income assumption (O6)
NO_OPT_OUT_LINE = (166, "If you do not opt out and your total income")

QUESTIONS = {
    "Q1": "Question 1. Is the applicant entitled to a Winter Fuel Payment for winter 2026 to 2027?",
    "Q2": "Question 2. How much is the payment?",
    "Q3": "Question 3. Does HMRC take the payment back because the applicant's total income is over £35,000?",
    "Q4": "Question 4. How much does the applicant keep after that?",
}

# Assumptions: reviews/relb/SCOPE.md section (c), in plain English (no ids, no file references).
# Name -> text; `_assumptions` decides which ones an answer uses.
ASSUMPTIONS = {
    "week": "The qualifying week is taken as 21 to 27 September 2026. The rule “the week beginning on the third Monday in September” is not worked out; only the 6-day span of the week is checked.",
    "ages": "Each person's pensionable-age date and 80th birthday are worked out by hand from the birth date (Pensions Act 1995, Schedule 4, paragraph 1, plus 80 years) and given as dates; the age arithmetic itself is not checked. The hand working takes a person to reach an age at the start of the birthday, and a birth date of 29 February 1960 as giving pensionable age no later than 1 March 2026.",
    "statuses": "These legal statuses are taken as stated in the profile, not decided from other circumstances: {}.",
    "one_other": "At most one other person shares the home; “a person” in regulations 3 and 4(2)(a) is read as that one person.",
    "income": "Whether HMRC takes the payment back follows the GOV.UK guide's £35,000 test on the total income the profile gives; the legal basis of the charge and the definition of total income are not pinned down. The guide's section is read as follows:",
    "no_opt_out": "The applicant has not opted out of the payment, so a person over the income limit receives it and HMRC takes it back.",
    "all_or_nothing": "HMRC takes back the whole payment or nothing, so the amount kept is the payment or £0.00.",
    "other_schemes": "The Scotland and Northern Ireland schemes are not modelled; a person not ordinarily resident in England or Wales on any day of the qualifying week gets no payment under these Regulations.",
    "glosses": "The rules have no checked English wording; each is shown above as a plain gloss next to its source text, and the gloss is taken to state the rule.",
    "open": "A proof the checker cannot find within its limits gives no answer (OPEN), never a guess.",
    "weeks_as_days": "“52 weeks” and “12 weeks” are taken as 364 and 84 days.",
    "lives_with": "In “lives with”, the words “they are not in residential care” apply only to the person who lives with someone; the other person may be in residential care.",
    "care_stay": "Residential care needs the stay to begin no later than 29 June 2026, and a stay with a last day counts only if that day is no earlier than 27 September 2026.",
    "hospital": "For hospital, “throughout the week” means admitted no later than 20 September 2026 and leaving no earlier than 27 September 2026, and “more than 52 weeks” means admitted no later than 20 September 2025, because a treatment period begins the day after admission.",
    "custody": "Custody is “throughout the qualifying week” only if it began before 21 September and release is after 27 September; release on 27 September does not count.",
    "excluded_not_entitled": "A person excluded by regulation 4 is not “entitled under regulation 2”, so living with them does not lower the amount.",
    "new_care_resident": "A care-home resident of under 12 weeks is not in residential care and does not “live with” other residents unless a mutual home with a named person is given.",
    "benefit_paid_to": "A relevant benefit is paid to a named person; pension credit is paid to the claimant of a couple.",
    "household": "A listed housemate shares the home on at least one day of the week; an undated shared home or partnership began before the week and continues after it, and a dated one includes a day of the week.",
    "move_order": "Regulation 4(4) applies only if the move to Scotland or Northern Ireland comes on or after a day of the week on which the person lived in England or Wales; a move on that same day counts.",
    "throughout": "For regulation 4(2)(a), the partnership and the shared home each last throughout the week when they begin no later than 21 September and end no earlier than 27 September; a first or last day inside the week counts as a day of it.",
    "common_day": "Regulation 3(3) needs one day of the week on which the person is both the partner of and living with the person aged 80; one shared day is enough.",
}
# Base predicates of a profile fact -> the legal status the profile states (the "statuses" assumption).
STATUS_WORDS = {
    "ever_resident_ew": "ordinarily resident in England or Wales, and from when",
    "remains_resident_ew": "ordinarily resident in England or Wales, and from when",
    "moved_to_scotland_or_ni": "ordinarily resident in Scotland or Northern Ireland, and from when",
    "partner_of": "a partner (a member of a couple)",
    "partnership_start_dated": "a partner (a member of a couple)",
    "partnership_ended": "a partner (a member of a couple)",
    "shares_home": "sharing a mutual home",
    "home_start_dated": "sharing a mutual home",
    "home_ended": "sharing a mutual home",
    "in_care_setting": "living in a care home or independent hospital",
    "care_ended": "living in a care home or independent hospital",
    "inpatient": "receiving free in-patient treatment",
    "detained_in_custody": "detained in custody",
    "under_sentence": "under a sentence imposed by a court",
    "paid_for_week": "who a benefit is paid to for the qualifying week",
    "paid_without_claim": "paid without a claim",
    "claimed": "the date of a claim",
}


class MissingGloss(ValueError):
    """A rule premise of a step has no gloss, so the printout could not say what it reads."""


class SourceMismatch(ValueError):
    """A cited source line does not start with the words the cite table expects."""


def _source_lines(name):
    return (HERE / "source" / SOURCES[name][0]).read_text(encoding="utf-8").splitlines()


def quote(source, line, opening):
    """The whole source line `line` (1-based) of `source`, checked to hold the expected words."""
    text = _source_lines(source)[line - 1].strip()
    if opening not in text:
        raise SourceMismatch(f"{SOURCES[source][0]}:{line} does not contain {opening!r}: {text[:60]!r}")
    return text


def check_cites(rules):
    """Every rule has a cite whose quoted lines match the source files. Returns the rule ids."""
    missing = sorted({r["rule"] for r in rules} - set(CLAUSES))
    if missing:
        raise SourceMismatch(f"rules with no source cite: {missing}")
    for source, _, lines in CLAUSES.values():
        for line, opening in lines:
            quote(source, line, opening)
    return sorted({r["rule"] for r in rules})


def load_rules():
    """The rule premises as published in rules.json (the glosses printed are these)."""
    return json.loads((HERE / "rules.json").read_text(encoding="utf-8"))["rules"]


def load_profile(profile):
    """A profile id from cases.json, a case dict, or a path to a JSON file with one case.
    The `key` field, if any, is dropped before anything else reads the case."""
    data = T.load_cases()
    if isinstance(profile, (str, Path)) and Path(profile).suffix == ".json" and Path(profile).is_file():
        profile = json.loads(Path(profile).read_text(encoding="utf-8"))
    if isinstance(profile, str):
        found = [c for c in data["cases"] if c["id"] == profile]
        if not found:
            raise ValueError(f"no profile {profile!r} in cases.json")
        profile = found[0]
    case = {k: v for k, v in profile.items() if k != "key"}
    case.setdefault("housemate", None)
    if "applicant" not in case:
        raise ValueError("a profile needs an 'applicant'")
    return case, data["defaults"]


def _contains(formula, part):
    if formula == part:
        return True
    return type(formula) is list and any(_contains(x, part) for x in formula[1:])


def _fact_predicates(formula, out):
    if type(formula) is not list or not formula:
        return
    if formula[0] in ("unary", "binary"):
        out.add(formula[1])
        return
    for x in formula[1:]:
        _fact_predicates(x, out)


def _date_words(fact):
    op, (_, _, name), (_, iso) = fact["formula"]
    role, _, suffix = name.partition("_")
    what = T.ROLE_INTEGERS[suffix][1]
    return f"the {role}'s {what} is {'no later than ' if op == 'date_no_later' else ''}{iso}"


def _assumptions(answer, rules, facts):
    """The assumption names (and per-answer text) an answer rests on, in ASSUMPTIONS order."""
    ids = {r["rule"] for r in rules}
    fact_preds = set()
    for f in facts:
        _fact_predicates(f["formula"], fact_preds)
    used = {}
    if any(_contains(r["formula"], T.day(d)) for r in rules for d in (T.QW0, T.QW1)):
        used["week"] = ASSUMPTIONS["week"]
    bridges = [f for f in facts if f.get("kind", "").startswith("bridge")]
    if bridges:
        used["ages"] = ASSUMPTIONS["ages"] + " Dates used here: " + "; ".join(_date_words(f) for f in bridges) + "."
    statuses = list(dict.fromkeys(STATUS_WORDS[p] for p in sorted(fact_preds, key=list(STATUS_WORDS).index)
                                  if p in STATUS_WORDS))
    if statuses:
        used["statuses"] = ASSUMPTIONS["statuses"].format("; ".join(statuses))
    if "shares_home" in fact_preds:
        used["one_other"] = ASSUMPTIONS["one_other"]
    if ids & {"R16a", "R16b"}:
        used["income"] = ASSUMPTIONS["income"]
        used["no_opt_out"] = ASSUMPTIONS["no_opt_out"]
    if "R16c" in ids:
        used["all_or_nothing"] = ASSUMPTIONS["all_or_nothing"]
    if ids & {"R3", "R11"}:
        used["other_schemes"] = ASSUMPTIONS["other_schemes"]
    if rules:
        used["glosses"] = ASSUMPTIONS["glosses"]
    if answer == "OPEN":
        used["open"] = ASSUMPTIONS["open"]
    if ids & {"R5b", "R8c"}:
        used["weeks_as_days"] = ASSUMPTIONS["weeks_as_days"]
    for rid, name in (("R6", "lives_with"), ("R5b", "care_stay"), ("R8c", "hospital"), ("R9", "custody")):
        if rid in ids:
            used[name] = ASSUMPTIONS[name]
    if any(_contains(r["formula"], T.U("entitled", "housemate")) for r in rules if r["rule"] not in ("R13b",)):
        used["excluded_not_entitled"] = ASSUMPTIONS["excluded_not_entitled"]
    if "R5b" in ids and "in_care_setting" in fact_preds and any(
            f["formula"][0] == "unary" and f["formula"][1] == "in_care_setting" for f in facts):
        used["new_care_resident"] = ASSUMPTIONS["new_care_resident"]
    if "R4" in ids:
        used["benefit_paid_to"] = ASSUMPTIONS["benefit_paid_to"]
    if ids & {"R7a", "R7b", "R14a"} or fact_preds & {"home_start_dated", "home_ended", "partnership_start_dated",
                                                       "partnership_ended"}:
        used["household"] = ASSUMPTIONS["household"]
    if "R11" in ids:
        used["move_order"] = ASSUMPTIONS["move_order"]
    if ids & {"R7a", "R7b"}:
        used["throughout"] = ASSUMPTIONS["throughout"]
    if ids & {"R14a", "R14.3"}:
        used["common_day"] = ASSUMPTIONS["common_day"]
    order = list(ASSUMPTIONS)
    return dict(sorted(used.items(), key=lambda item: order.index(item[0])))


def _clause(rule):
    source, heading, lines = CLAUSES[rule["rule"]]
    return {"source": SOURCES[source][1], "heading": heading,
            "quotes": [quote(source, line, opening) for line, opening in lines]}


def _display(question, value):
    if value in ("YES", "NO", "OPEN"):
        return value
    if value == "N/A":
        return "Not applicable: the applicant is not entitled."
    return f"£{value}"


def explanation(profile, *, rules=None, lean=True):
    """The explanation of one profile as data: one entry per question (see `explain`)."""
    rules = load_rules() if rules is None else rules
    check_cites(rules)
    by_id = {r["id"]: r for r in rules}
    case, defaults = load_profile(profile)
    raw_env = T.environment()
    env = Environment(raw_env)
    facts = T.profile_facts(case, defaults)
    fact_by_id = {f["id"]: f for f in facts}
    staged = R.Staged(R.Prover(env), rules, facts)
    answers = staged.run()
    targets = R.answer_targets(answers)
    by_name = staged.step_by_name

    documents, needed = {}, {}
    for question, target in targets.items():
        documents[question] = staged.document(target)
        needed[question] = [n["name"] for n in documents[question]["graph"]["nodes"]]
        for name in needed[question]:  # every rule premise of a step must carry a gloss
            if name in by_name:
                for premise in by_name[name]["premises"]:
                    if premise.startswith("rule:") and not (by_id[premise[5:]].get("gloss") or "").strip():
                        raise MissingGloss(f"premise {premise} of step {name} has no gloss")

    lean_rows = {}
    if lean and targets:
        cases = []
        for step in staged.steps.values():
            if any(step["name"] in names for names in needed.values()):
                cases.append({"id": f"cert/{step['name']}", "kind": "certificate", "environment": raw_env,
                              "premises": [R.q(staged.formula(n)) for n in step["premises"]],
                              "conclusion": R.q(step["formula"]), "certificate": step["certificate"]})
        cases += [{"id": f"doc/{question}", "kind": "document", "environment": raw_env, "document": doc}
                  for question, doc in documents.items()]
        lean_rows = {row["id"]: row for row in R.lean(cases)}

    out, shown_clauses, shown_assumptions = [], set(), {}
    for question in ("Q1", "Q2", "Q3", "Q4"):
        value = answers[question]
        entry = {"question": question, "text": QUESTIONS[question], "answer": value}
        if question in targets:
            names = needed[question]
            steps = [by_name[n] for n in names if n in by_name]
            rule_premises = [by_id[n[5:]] for n in names if n.startswith("rule:")]
            fact_premises = [fact_by_id[n[5:]] for n in names if n.startswith("fact:")]
            entry["certificates"] = len(steps)
            if lean:
                certs = [lean_rows[f"cert/{s['name']}"] for s in steps]
                doc = lean_rows[f"doc/{question}"]
                entry["lean"] = {"checked": len(certs),
                                 "accepted": sum(r.get("status") == "ok" and r.get("valid") is True for r in certs),
                                 "admitted": doc.get("status") == "ok" and doc.get("assurance") == "lean-admitted"}
                if not entry["lean"]["admitted"]:
                    entry["answer"] = value = "OPEN"  # as run.py: an answer counts only if Lean admits it
            clauses, guide = {}, {}
            for r in rule_premises:
                c = _clause(r)
                bucket = guide if r["rule"] in GUIDE_RULES else clauses
                group = bucket.setdefault((c["source"], c["heading"]), {**c, "quotes": [], "glosses": []})
                group["quotes"] += [t for t in c["quotes"] if t not in group["quotes"]]  # rules of one clause may quote more lines
                group["glosses"].append(r["gloss"])
            entry["clauses"] = list(clauses.values())
            entry["new_clauses"] = [c for k, c in clauses.items() if k not in shown_clauses]
            shown_clauses |= set(clauses)
            assumptions = _assumptions(value, rule_premises, fact_premises)
            entry["guide_clauses"] = list(guide.values())
            if "no_opt_out" in assumptions:
                entry["no_opt_out_quote"] = quote("S2", *NO_OPT_OUT_LINE)
        else:
            entry["clauses"] = entry["new_clauses"] = entry["guide_clauses"] = []
            assumptions = {"open": ASSUMPTIONS["open"]} if value == "OPEN" else {}
        entry["assumptions"] = assumptions
        entry["new_assumptions"] = {k: v for k, v in assumptions.items() if shown_assumptions.get(k) != v}
        shown_assumptions.update(assumptions)
        entry["display"] = _display(question, entry["answer"])
        out.append(entry)
    return {"answers": out, "lean": lean}


def _wrap(text, indent, width=100):
    return textwrap.fill(text, width=width, initial_indent=indent, subsequent_indent=" " * len(indent) + "  ",
                         break_long_words=False, break_on_hyphens=False)


def render(data):
    lines = ["Winter Fuel Payment, winter 2026 to 2027: the answers for one applicant, with the clauses",
             "and assumptions each answer rests on.", ""]
    for i, e in enumerate(data["answers"]):
        lines += [e["text"], f"Answer: {e['display']}"]
        if "certificates" not in e:
            lines += ["", ""] if e["answer"] == "N/A" else [""]
            if e["new_assumptions"]:
                lines.append("Assumptions:")
                lines += [_wrap(t, "  - ") for t in e["new_assumptions"].values()]
                lines.append("")
            continue
        lines.append("")
        if i and not e["new_clauses"]:
            lines.append("Clauses used: only those listed for the questions above.")
        else:
            lines.append("Clauses used:" if not i else "Clauses used: those listed above, plus:")
            for c in e["new_clauses"]:
                lines.append(_wrap(f"{c['source']}, {c['heading']}", "  "))
                lines.append("    Source text:")
                lines += [_wrap(f"“{t}”", "      ") for t in c["quotes"]]
                lines.append("    Read as:")
                lines += [_wrap(g, "      - ") for g in dict.fromkeys(c["glosses"])]
        lines.append("")
        if e["new_assumptions"]:
            lines.append("Assumptions (taken as given, not checked):" if not i
                         else "Assumptions: those listed above, plus:")
            for name, text in e["new_assumptions"].items():
                lines.append(_wrap(text, "  - "))
                if name == "income":
                    for c in e["guide_clauses"]:
                        lines.append(_wrap(f"{c['source']}, {c['heading']}", "      "))
                        lines += [_wrap(f"“{t}”", "        ") for t in c["quotes"]]
                        lines.append("      Read as:")
                        lines += [_wrap(g, "        - ") for g in dict.fromkeys(c["glosses"])]
                if name == "no_opt_out":
                    lines.append(_wrap(f"The guide: “{e['no_opt_out_quote']}”", "      "))
        else:
            lines.append("Assumptions: only those listed for the questions above.")
        lines.append("")
        n = e["certificates"]
        if "lean" in e:
            lean = e["lean"]
            verdict = "admitted" if lean["admitted"] else "NOT admitted, so the answer is OPEN"
            lines.append(f"Lean check: this answer rests on {n} proof step{'s' * (n != 1)}; Lean checked "
                         f"{lean['checked']} certificate{'s' * (lean['checked'] != 1)}, {lean['accepted']} accepted; "
                         f"the answer document was {verdict}.")
        else:
            lines.append(f"Lean check: this answer rests on {n} proof step certificate{'s' * (n != 1)}; "
                         "Lean was not run for this printout.")
        lines += ["", ""]
    return "\n".join(lines).rstrip() + "\n"


def explain(profile, *, rules=None, lean=True):
    """The plain-English printout for one profile: an id from cases.json, a case dict, or a
    path to a JSON file holding one case."""
    return render(explanation(profile, rules=rules, lean=lean))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("profile", help="a profile id from cases.json, or a JSON file holding one profile")
    parser.add_argument("--no-lean", action="store_true", help="skip the Lean check of the certificates")
    args = parser.parse_args(argv)
    sys.stdout.write(explain(args.profile, lean=not args.no_lean))
    return 0


if __name__ == "__main__":
    sys.exit(main())
