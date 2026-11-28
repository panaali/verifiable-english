"""Plain-English explanation of one Winter Fuel Payment profile (release B, checklist item 4).

For each answer (questions 1 to 4) it prints: the answer; the clauses used, each as the
rules.json gloss with the quoted source text it reads (from the four files in source/), and with
--wording each rule's checked English wording under its gloss (ask.py --wording prints it in place of the
gloss: render(..., gloss=False)); the bridges and adopted readings
it rests on, as plain-English assumptions; for questions 3 and 4, the guide's "over £35,000"
section, shown as an assumption (its legal basis is not pinned); and the number of Lean step
certificates behind the answer. An answer that uses a clause of guidance (a source whose BASIS is "guidance": the
GOV.UK guide), not only of law, carries the mark "basis: guidance" (`basis_mark`; ask.py's summary lines carry it too).

A rule's checked English wording is the one run.py's `english_rules` records in results.json
(`english.rule_rows`): generated from the rule by `render_w6_sentence` and read back by
`parse_w6_sentence` to exactly one reading, the rule itself. The data (`explanation`) carries it
for every rule premise; the default printout leaves it out because the wordings still name
benefits by their identifiers ('paid "state_pension"'); yes/no facts read with their plain wordings
(plain_wordings.json, relb F3).

The answers come from the staged route of run.py (one derived fact per step, each step a
certificate, each answer a `documents@1` document Lean admits). An answer whose document Lean
does not admit is OPEN, as in run.py. Nothing here reads a profile's `key`.

Usage: python usecases/eligibility/explain.py <profile id | profile.json> [--no-lean] [--wording]
A profile file holds one case in the cases.json form ({"applicant": {...}, "housemate": ...});
fields it leaves out take the cases.json defaults.

Importable: `explain(profile, *, wording=False) -> str`, `explanation(profile) -> dict` (the same
content as data, wordings included).
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
# What each source is: "law" (an Act or a statutory instrument) or "guidance" (the GOV.UK guide, which states how the
# government reads the law but is not law). An answer's basis is the set of these over the sources of the clauses its
# rules come from (CLAUSES), so a rule moved to another source changes the mark with it.
BASIS = {"S1": "law", "S2": "guidance", "S3": "law", "Sch4": "law"}
BASIS_MARK = "basis: guidance"

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
    "week": "The qualifying week, 21 to 27 September 2026, is worked out in Python from the rule “the week beginning on the third Monday in September” (2026 being the year of the payment); the checker checks only that its last day is 6 days after its first.",
    "ages": "Each person's pensionable-age date is worked out in Python from the birth date by the rules and tables of the Pensions Act 1995, Schedule 4, paragraph 1, read from their text, and the 80th birthday as 80 years on; an age is taken to be reached at the start of the birthday. The checker does not do this arithmetic (its dates start in 1970); tests check it against a separate working of Schedule 4. For this qualifying week the GOV.UK guide's birth-date cut-offs (born on or before 27 June 1960; born before 28 September 1946) must agree with it, or no answer is given. Where the source does not fix one day (a birthday on 29 February in a year without one, or a birth before 6 December 1953, where the rules differ for men and women), only the earliest and latest possible days are used.",
    "statuses": "These legal statuses are taken as stated in the profile, not decided from other circumstances: {}.",
    "one_other": "At most one other person shares the home; “a person” in regulations 3 and 4(2)(a) is read as that one person.",
    "income": "Whether HMRC takes the payment back follows the GOV.UK guide's £35,000 test on the total income the profile gives; the legal basis of the charge and the definition of total income are not pinned down. The guide's section is read as follows:",
    "no_opt_out": "The applicant has not opted out of the payment, so a person over the income limit receives it and HMRC takes it back.",
    "all_or_nothing": "HMRC takes back the whole payment or nothing, so the amount kept is the payment or £0.00.",
    "other_schemes": "The Scotland and Northern Ireland schemes are not modelled; a person not ordinarily resident in England or Wales on any day of the qualifying week gets no payment under these Regulations.",
    "glosses": "Each rule is shown with its clause as a plain gloss next to the source text; the gloss, a hand-written summary not checked against the rule, is taken to describe it. Each rule used here also has a checked English wording: a sentence generated from the rule and read back by the parser to exactly one reading, the rule itself (usecases/eligibility/explain.py --wording prints it under the gloss).",
    "open": "A proof the checker cannot find within its limits gives no answer (OPEN), never a guess.",
    "weeks_as_days": "“52 weeks” and “12 weeks” are taken as 364 and 84 days.",
    "lives_with": "In “lives with”, the words “they are not in residential care” apply only to the person who lives with someone; the other person may be in residential care.",
    "care_stay": "Residential care needs the stay to begin no later than 29 June 2026, and a stay with a last day counts only if that day is no earlier than 27 September 2026.",
    "hospital": "For hospital, “throughout the week” means admitted no later than 20 September 2026 and leaving no earlier than 27 September 2026, and “more than 52 weeks” means admitted no later than 20 September 2025, because a treatment period begins the day after admission.",
    "custody": "Custody under a sentence is “throughout the qualifying week” only if the sentence began before 21 September and release is after 27 September; release on 27 September does not count, and days on remand before the sentence are not under it.",
    "no_claim": "A person the profile does not say was paid without a claim is taken to be paid without one if they get a benefit on the GOV.UK guide's list of people who do not need to claim, and not if they get none and the guide says they must claim; “do not need to claim” is read as a payment under regulation 5(1). A person who gets none of them and for whom neither of the guide's reasons to claim is given gets no answer: the guide does not say they are paid without a claim.",
    "undated_payment": "A payment without a claim with no date given is taken to be made by 31 March 2027, the last day regulation 5(1) allows (the GOV.UK guide: “Most payments are made automatically in November or December”).",
    "excluded_not_entitled": "A person excluded by regulation 4 is not “entitled under regulation 2”, so living with them does not lower the amount.",
    "new_care_resident": "A care-home resident of under 12 weeks is not in residential care and does not “live with” other residents unless a mutual home with a named person is given.",
    "benefit_paid_to": "A relevant benefit is paid to a named person; pension credit is paid to the claimant of a couple.",
    "household": "A listed housemate shares the home on at least one day of the week; an undated shared home or partnership began before the week and continues after it, and a dated one includes a day of the week.",
    "move_order": "Regulation 4(4) applies only if the move to Scotland or Northern Ireland comes on or after a day of the week on which the person lived in England or Wales; a move on that same day counts.",
    "throughout": "For regulation 4(2)(a), the partnership and the shared home each last throughout the week when they begin no later than 21 September and end no earlier than 27 September; a first or last day inside the week counts as a day of it.",
    "common_day": "Regulation 3(3) needs one day of the week on which the person is both the partner of and living with the person aged 80; one shared day is enough.",
}
# The "glosses" assumption when the printout shows the wordings (--wording), and when a rule used has none.
GLOSSES_WORDED = ("Each rule is shown with its clause as a plain gloss and, under it, its checked English wording: a "
                  "sentence generated from the rule and read back by the parser to exactly one reading, the rule itself, "
                  "so the wording states the rule. The gloss, a hand-written summary not checked against the rule, is "
                  "taken to describe it.")
# The "glosses" assumption when the printout shows the wordings in place of the glosses (render(..., gloss=False):
# ask.py --wording, tour stop 6), and when a rule used has no wording there.
GLOSSES_WORDING_ONLY = ("Each rule is shown with its clause by its checked English wording, in place of a hand-written "
                        "gloss: a sentence generated from the rule and read back by the parser to exactly one reading, "
                        "the rule itself, so the wording states the rule as the parser reads it; that a person reads "
                        "the same meaning in it is taken as given. usecases/eligibility/explain.py prints the "
                        "hand-written glosses.")
GLOSSES_WORDING_ONLY_UNWORDED = ("Each rule is shown with its clause by its checked English wording, in place of a "
                                 "hand-written gloss: a sentence generated from the rule and read back by the parser to "
                                 "exactly one reading, the rule itself; that a person reads the same meaning in it is "
                                 "taken as given. Some rules used for these answers have no checked English wording; "
                                 "each of those is shown by its gloss, marked as one, and the gloss, a hand-written "
                                 "summary not checked against the rule, is taken to state the rule.")
GLOSSES_UNWORDED = ("Each rule is shown with its clause as a plain gloss next to the source text. Some rules used for "
                    "these answers have no checked English wording (a sentence generated from the rule and read back by "
                    "the parser to exactly that rule); for those, the gloss is taken to state the rule.")
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


def load_wordings(rules=None):
    """Rule id -> its checked English wording: results.json's `english.rule_rows` (written by run.py's
    `english_rules`), only rows whose wording read back to exactly one reading, the rule (`round_trip`).
    A rule in `rules` whose formula differs from the published rules.json rule of that id gets none:
    its recorded wording is not its wording."""
    rows = json.loads((HERE / "results.json").read_text(encoding="utf-8"))["english"]["rule_rows"]
    worded = {r["rule"]: r["sentence"] for r in rows if r.get("round_trip") is True and r.get("sentence")}
    published = {r["id"]: r["formula"] for r in load_rules()}
    rules = load_rules() if rules is None else rules
    return {r["id"]: worded[r["id"]] for r in rules
            if r["id"] in worded and published.get(r["id"]) == r["formula"]}


def english_count():
    """The sentence the "glosses" assumption ends with: how many of the translation's rules have a checked English
    wording, as results.json records it (`english.rules_round_trip` of `english.rules`)."""
    english = json.loads((HERE / "results.json").read_text(encoding="utf-8"))["english"]
    worded, rules = english["rules_round_trip"], english["rules"]
    return f"In all, {worded} of the published translation's {rules} rules have a checked English wording."


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
    return f"the {role}'s {what} is {({'date_no_later': 'no later than ', 'date_after': 'after '}).get(op, '')}{iso}"


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
    if any(f.get("kind") == "assumption O3" and f["id"].endswith(".paid_without_claim") for f in facts):
        used["no_claim"] = ASSUMPTIONS["no_claim"]
    if any(f.get("kind") == "assumption F8" for f in facts):
        used["undated_payment"] = ASSUMPTIONS["undated_payment"]
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


def basis_mark(entry):
    """" (basis: guidance)" for an answer (an `explanation` entry) that uses a clause of guidance; "" for one whose
    clauses are all law, and for an answer that is no answer (OPEN, or not applicable)."""
    if entry["answer"] in ("OPEN", "N/A") or "guidance" not in entry.get("basis", ()):
        return ""
    return f" ({BASIS_MARK})"


def basis_legend(entries, *, summary=True):
    """What the mark means, naming the guidance the marked answers use and where the printout quotes it; None when no
    answer is marked. The summary's legend (ask.py) also says the mark looks at clauses only; `summary=False` gives
    the line render prints under a marked answer."""
    marked = [e for e in entries if basis_mark(e)]
    titles = list(dict.fromkeys(t for e in marked for t in e["guidance_sources"]))
    if not titles:
        return None
    named = " and ".join(t[0].lower() + t[1:] if t.startswith("The ") else t for t in titles)
    # the guide's income rules are quoted under the assumptions (O6), never under "Clauses used"
    where = " (quoted under the assumptions)" if all(e["guidance_as_assumption"] for e in marked) else ""
    lead = f"({BASIS_MARK}): a marked answer" if summary else f"Basis: guidance: this answer"
    text = f"{lead} uses a clause of {named}{where}, which is guidance on the law, not law."
    if summary:
        text += (" The mark looks at clauses only: an assumption that cites the guide is listed with the assumptions,"
                 " not marked.")
    return text


def wrap(text, indent=""):
    """`text` wrapped as the printout wraps it (ask.py's summary uses it)."""
    return _wrap(text, indent)


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
    wordings = load_wordings(rules)
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

    out, shown_clauses, shown_assumptions, shown_guide = [], set(), {}, set()
    unworded = any(n.startswith("rule:") and n[5:] not in wordings for names in needed.values() for n in names)
    for question in ("Q1", "Q2", "Q3", "Q4"):
        value = answers[question]
        entry = {"question": question, "text": QUESTIONS[question], "answer": value}
        if question in targets:
            names = needed[question]
            steps = [by_name[n] for n in names if n in by_name]
            rule_premises = [by_id[n[5:]] for n in names if n.startswith("rule:")]
            sources = list(dict.fromkeys(CLAUSES[r["rule"]][0] for r in rule_premises))
            entry["basis"] = sorted({BASIS[s] for s in sources})
            entry["guidance_sources"] = [SOURCES[s][1] for s in sources if BASIS[s] == "guidance"]
            entry["guidance_as_assumption"] = all(r["rule"] in GUIDE_RULES for r in rule_premises
                                                  if BASIS[CLAUSES[r["rule"]][0]] == "guidance")
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
            clauses, guide, new_guide = {}, {}, {}
            for r in rule_premises:
                c = _clause(r)
                buckets = [guide, *([new_guide] if r["id"] not in shown_guide else [])] \
                    if r["rule"] in GUIDE_RULES else [clauses]
                for bucket in buckets:
                    group = bucket.setdefault((c["source"], c["heading"]),
                                              {**c, "quotes": [], "glosses": [], "wordings": []})
                    group["quotes"] += [t for t in c["quotes"] if t not in group["quotes"]]  # rules of one clause may quote more lines
                    group["glosses"].append(r["gloss"])
                    group["wordings"].append(wordings.get(r["id"]))  # None: the rule has no checked wording
            entry["wordings"] = {r["id"]: wordings.get(r["id"]) for r in rule_premises}
            entry["clauses"] = list(clauses.values())
            entry["new_clauses"] = [c for k, c in clauses.items() if k not in shown_clauses]
            shown_clauses |= set(clauses)
            assumptions = _assumptions(value, rule_premises, fact_premises)
            if "glosses" in assumptions and unworded:  # decided once per profile, so the answers agree
                assumptions["glosses"] = GLOSSES_UNWORDED
            entry["guide_clauses"] = list(guide.values())
            # The guide rules this answer uses for the first time (question 4's all-or-nothing rule once
            # question 3 showed the income section): printed under the all-or-nothing assumption.
            entry["new_guide_clauses"] = list(new_guide.values())
            shown_guide |= {r["id"] for r in rule_premises if r["rule"] in GUIDE_RULES}
            if "no_opt_out" in assumptions:
                entry["no_opt_out_quote"] = quote("S2", *NO_OPT_OUT_LINE)
        else:
            entry["clauses"] = entry["new_clauses"] = entry["guide_clauses"] = entry["new_guide_clauses"] = []
            entry["basis"], entry["guidance_sources"], entry["guidance_as_assumption"] = [], [], False
            assumptions = {"open": ASSUMPTIONS["open"]} if value == "OPEN" else {}
        entry["assumptions"] = assumptions
        entry["new_assumptions"] = {k: v for k, v in assumptions.items() if shown_assumptions.get(k) != v}
        shown_assumptions.update(assumptions)
        entry["display"] = _display(question, entry["answer"])
        entry["mark"] = basis_mark(entry)
        out.append(entry)
    return {"answers": out, "lean": lean}


def _wrap(text, indent, width=100):
    return textwrap.fill(text, width=width, initial_indent=indent, subsequent_indent=" " * len(indent) + "  ",
                         break_long_words=False, break_on_hyphens=False)


def _readings(c, indent, wording, gloss_shown=True):
    """A clause's "Read as:" lines: each rule's gloss, and with `wording` its checked English wording
    under it (the wording's own line breaks and nesting kept, each line wrapped). Without `gloss_shown`
    each rule's checked wording stands in place of its gloss; a rule with none keeps its gloss, said to be one."""
    out = []
    for gloss, sentence in dict.fromkeys(zip(c["glosses"], c["wordings"])):
        if not gloss_shown:
            if sentence is None:
                out.append(_wrap(f"{gloss} (a hand-written gloss: this rule has no checked English wording)",
                                 indent + "- "))
                continue
            for n, line in enumerate(sentence.split("\n")):
                text = line.lstrip(" ")
                out.append(_wrap(text, indent + "- " if n == 0 else indent + "  " + " " * (len(line) - len(text))))
            continue
        out.append(_wrap(gloss, indent + "- "))
        if not wording:
            continue
        pad = indent + "    "
        if sentence is None:
            out.append(_wrap("Checked English wording: none.", pad))
            continue
        out.append(pad + "Checked English wording:")
        for line in sentence.split("\n"):
            text = line.lstrip(" ")
            out.append(_wrap(text, pad + "  " + " " * (len(line) - len(text))))
    return out


def render(data, wording=False, gloss=True):
    """The printout of `explanation` data. `wording` adds each rule's checked English wording under its gloss;
    with `gloss=False` as well, the wording is shown in place of the gloss (ask.py --wording, tour stop 6)."""
    gloss = gloss or not wording  # without a wording to show, the gloss stays
    read_as = "    Read as:" if gloss else "    Read as (each rule's checked English wording, generated from the rule):"
    lines = ["Winter Fuel Payment, winter 2026 to 2027: the answers for one applicant, with the clauses",
             "and assumptions each answer rests on.", ""]
    for i, e in enumerate(data["answers"]):
        lines += [e["text"], f"Answer: {e['display']}{e.get('mark', '')}"]
        if e.get("mark"):
            lines.append(_wrap(basis_legend([e], summary=False), ""))
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
                lines.append(read_as)
                lines += _readings(c, "      ", wording, gloss)
        lines.append("")
        if e["new_assumptions"]:
            lines.append("Assumptions (taken as given, not checked):" if not i
                         else "Assumptions: those listed above, plus:")
            for name, text in e["new_assumptions"].items():
                if name == "glosses":
                    if wording and not gloss:
                        text = GLOSSES_WORDING_ONLY if text == ASSUMPTIONS["glosses"] else GLOSSES_WORDING_ONLY_UNWORDED
                    elif wording and text == ASSUMPTIONS["glosses"]:
                        text = GLOSSES_WORDED
                    text += " " + english_count()
                lines.append(_wrap(text, "  - "))
                if name == "income":
                    for c in e["guide_clauses"]:
                        lines.append(_wrap(f"{c['source']}, {c['heading']}", "      "))
                        lines += [_wrap(f"“{t}”", "        ") for t in c["quotes"]]
                        lines.append("  " + read_as)
                        lines += _readings(c, "        ", wording, gloss)
                if name == "all_or_nothing" and "income" not in e["new_assumptions"]:
                    for c in e["new_guide_clauses"]:  # the income section above did not show these rules
                        lines.append(_wrap(f"{c['source']}, {c['heading']}", "      "))
                        lines += [_wrap(f"“{t}”", "        ") for t in c["quotes"]]
                        lines.append("  " + read_as)
                        lines += _readings(c, "        ", wording, gloss)
                if name == "no_opt_out":
                    lines.append(_wrap(f"The guide: “{e['no_opt_out_quote']}”", "      "))
        else:
            lines.append("Assumptions: only those listed for the questions above.")
        lines.append("")
        n = e["certificates"]
        if "lean" in e:
            lean = e["lean"]
            verdict = ("the answer was checked by Lean and accepted" if lean["admitted"]
                       else "the answer was NOT accepted by Lean, so it is OPEN")
            lines.append(f"Lean check: this answer rests on {n} proof step{'s' * (n != 1)}; {lean['accepted']} of "
                         f"{lean['checked']} proof step{'s' * (lean['checked'] != 1)} accepted by Lean; {verdict}.")
        else:
            lines.append(f"Lean check: this answer rests on {n} proof step{'s' * (n != 1)}; "
                         "Lean was not run for this printout.")
        lines += ["", ""]
    return "\n".join(lines).rstrip() + "\n"


def explain(profile, *, rules=None, lean=True, wording=False, gloss=True):
    """The plain-English printout for one profile: an id from cases.json, a case dict, or a
    path to a JSON file holding one case. `wording` adds each rule's checked English wording;
    with `gloss=False` as well, in place of the gloss."""
    return render(explanation(profile, rules=rules, lean=lean), wording=wording, gloss=gloss)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("profile", help="a profile id from cases.json, or a JSON file holding one profile")
    parser.add_argument("--no-lean", action="store_true", help="skip the Lean check of the proof steps")
    parser.add_argument("--wording", action="store_true",
                        help="print each rule's checked English wording under its gloss")
    args = parser.parse_args(argv)
    sys.stdout.write(explain(args.profile, lean=not args.no_lean, wording=args.wording))
    return 0


if __name__ == "__main__":
    sys.exit(main())
