"""14 CFR 61.23 (eCFR 2026-11-10, source.txt sha256 84fe940e...b71f2d6f): the VE translation, written from the source text
ONLY, before the encoder's question file was opened (statute corpus law 4, SAME-FAMILY, Opus 5.5 author).

Shape (as law 1 PAWHP): formulas over a declared vocabulary; one person per case ("pilot"); the person's medical
certificates and applications are records quantified over (ISOLATION.md D1); dates are int constants of unit "day" and
every date that needs arithmetic (age on the examination date, the 60th birthday, the end of the last day of the Nth month
after the month of examination, the 24/48 calendar-month windows, which of two dates is later) comes from the tested bridge
script (bridge/bridges.py), never from these rules (ISOLATION.md D5). The rules only compare dates.

Reading choices (each is listed in RESULT.md; "refuse when in doubt"):
 T1 (a)'s lead-in "Except as provided in (b) and (c)": (b) and (c) win over (a); (c)(1)(vi) wins over (b)(1), (b)(2), (b)(6)
    ("Notwithstanding"); where (b) and (c) both reach a person otherwise, NO answer is derived (ISOLATION.md D3).
 T2 (a)'s three classes are a floor ("at least"): the highest (a) item that applies is the requirement.
 T3 No (a), (b) or (c) item applies: no requirement is derived (refused), never "none" by default.
 T4 (d): "your medical certificate" is the most recent one (the table ties the age to "your most recent medical
    certificate"); a suspended or revoked most recent certificate is not held (encoder fact). No (d) row for the operation
    and the class held -> no expiry (refused); two rows with different periods -> no expiry (refused).
 T5 (c)(2) binds when sport pilot certificate privileges are exercised ((c)(1)(ii), (vi)); it does not bind when none of
    (c)(1)(i)-(iv) or sport privileges are in play; for (c)(1)(i), (iii), (iv) without sport privileges whether it binds is
    left open (no derivation). (c)(3) binds exactly under 61.113(i).
 T6 (b)(6)(ii) "a flight instructor certificate with a glider category rating": instructing in a glider.
 T7 Q3 (the last day) under the medical route is the (d) expiry; under (c)(3) it is the earlier of the two window ends;
    with both routes met, the later of the two; a route with no time limit in the text ((c)(2) alone, (b)) -> NONE.
    A part 121 required pilot crew member whose 60th birthday falls on or before the expiry changes requirement before
    it: no Q3 derived (ISOLATION.md D2 fallback).
"""
from __future__ import annotations

CERTS = ("cert1", "cert2", "cert3", "cert4")   # certificate constants a case may name
APPS = ("app1", "app2", "app3", "app4")        # application constants a case may name
DAY = {"scale": "1", "display": {"kind": "iso_date"}}
CERT_INTS = ("exam", "end6", "end12", "end24", "end60")

INTS = {
    "flight_day": "the date D of the operation",
    "sixtieth": "the pilot's 60th birthday",
    "course_day": "the day the pilot completed the 68.3 medical education course",
    "course_end24": "the last day of the 24th calendar month after the month of the 68.3 course",
    "basic_exam_day": "the day of the pilot's comprehensive medical examination (part 68)",
    "basic_exam_end48": "the last day of the 48th calendar month after the month of the comprehensive examination",
    "expiry": "the last day the pilot's most recent medical certificate serves the operation under (d)",
    "dl_last": "the last day the 61.113(i) windows of (c)(3)(i)(C)-(D) are both met",
    "last_day": "the last day the pilot meets 61.23 for the operation (Q3)",
}
for _c in CERTS:
    INTS[f"{_c}_exam"] = f"the date of examination of {_c}"
    for _n in (6, 12, 24, 60):
        INTS[f"{_c}_end{_n}"] = f"the end of the last day of the {_n}th month after the month of examination of {_c}"

FACTS = {  # unary facts about the pilot and the operation P on date D (the encoder states each, true or false)
    "atp": "exercises the privileges of an airline transport pilot certificate",
    "commercial": "exercises the privileges of a commercial pilot certificate",
    "private": "exercises the privileges of a private pilot certificate",
    "recreational": "exercises the privileges of a recreational pilot certificate",
    "student": "exercises the privileges of a student pilot certificate",
    "sport": "exercises the privileges of a sport pilot certificate",
    "flight_instructor": "exercises the privileges of a flight instructor certificate",
    "ground_instructor": "exercises the privileges of a ground instructor certificate",
    "flight_engineer": "the operation requires a flight engineer certificate",
    "atc_tower": "the operation requires an air traffic control tower operator certificate",
    "acting_pic": "acts as pilot in command",
    "serving_sic": "exercises second-in-command privileges",
    "required_crew": "serves as a required (pilot) flightcrew member",
    "part121": "the operation is conducted under part 121",
    "flag_supp_3plus": "the operation is a flag or supplemental operation in part 121 that requires three or more pilots",
    "in_glider": "the aircraft is a glider",
    "in_balloon": "the aircraft is a balloon",
    "glider_rating": "holds a pilot certificate with a glider category rating",
    "balloon_rating": "the certificate exercised has a balloon class rating",
    "fi_sport_rating": "the flight instructor certificate exercised has a sport pilot rating",
    "fi_glider_rating": "the flight instructor certificate exercised has a glider category rating",
    "comp_hire": "the flight is for compensation or hire",
    "training_61_133": "provides flight training in accordance with 61.133(a)(2)(ii)",
    "conducting_training": "conducts flight training",
    "taking_test_aircraft": "takes a practical test in an aircraft for a recreational, private, commercial, airline transport "
                            "pilot or flight instructor certificate",
    "examiner_aircraft": "performs the duties of an Examiner in an aircraft administering a practical test or proficiency check",
    "examiner_gbsf": "serves as an Examiner or check airman administering a practical test or proficiency check conducted in "
                     "a glider, balloon, flight simulator or flight training device",
    "taking_test_gbsf": "takes a practical test or proficiency check conducted in a glider, balloon, flight simulator or "
                        "flight training device",
    "examiner_sport_test": "serves as an Examiner administering a practical test for the issuance of a sport pilot certificate",
    "examiner_admin": "serves as an Examiner administering a practical test or proficiency check",
    "seeking_sport_gb": "a student pilot seeking a sport pilot certificate with glider or balloon privileges",
    "seeking_gb_rating": "a student pilot seeking a pilot certificate with a glider category or balloon class rating",
    "seeking_sport": "a student pilot seeking sport pilot privileges",
    "meets_316": "the aircraft meets the performance limits and design requirements of 61.316",
    "under_113i": "the flight is conducted under the conditions and limitations of 61.113(i)",
    "night": "the flight is at night",
    "military_evidence": "is a military pilot of the U.S. Armed Forces who can show evidence of an up-to-date medical "
                         "examination authorizing pilot flight status",
    "domestic_us": "the flight is a domestic flight operation within U.S. airspace",
    "special_med_test": "acts on a special medical flight test authorized under part 67",
    "holds_dl": "holds (and possesses) a U.S. driver's license",
    "dl_complied": "complies with each restriction and limitation of the driver's license and any judicial or administrative "
                   "order applying to the operation of a motor vehicle",
    "dl_med_complied": "complies with all medical requirements or restrictions associated with the driver's license",
    "knows_condition": "knows or has reason to know of a medical condition that would make the person unable to operate such "
                       "an aircraft in a safe manner (stated judgement)",
    "diagnosed_impact": "has been diagnosed with a medical condition that may impact the ability to fly (stated judgement)",
    "physician_care": "is under the care and treatment of a State-licensed physician",
    "course_done": "completed the 68.3 medical education course and retains the certification of completion",
    "basic_exam_done": "received a comprehensive medical examination from a State-licensed physician under part 68",
    "last_si_withdrawn": "the most recently issued Authorization for a Special Issuance has been withdrawn",
}
DERIVED = {  # unary derived atoms about the pilot
    "reached_60": "has reached the 60th birthday on D",
    "a11": "61.23(a)(1)(i)", "a12": "61.23(a)(1)(ii)", "a13": "61.23(a)(1)(iii)",
    "a21": "61.23(a)(2)(i)", "a22": "61.23(a)(2)(ii)", "a23": "61.23(a)(2)(iii)",
    "a31": "61.23(a)(3)(i)", "a32": "61.23(a)(3)(ii)", "a33": "61.23(a)(3)(iii)", "a34": "61.23(a)(3)(iv)",
    "a1": "an item of (a)(1) applies", "a2": "an item of (a)(2) applies", "a3": "an item of (a)(3) applies",
    **{f"b{i}": f"61.23(b)({i})" for i in range(1, 13)},
    **{f"c1{r}": f"61.23(c)(1)({r})" for r in ("i", "ii", "iii", "iv", "v", "vi", "vii", "viii")},
    "b_eff": "an item of (b) applies and is not overridden by (c)(1)(vi)",
    "c_any": "an item of (c)(1) applies",
    "needs_first": "the operation requires a first-class medical certificate",
    "needs_second": "the operation requires at least a second-class medical certificate",
    "needs_third": "the operation requires at least a third-class medical certificate",
    "needs_none": "no medical certificate is required",
    "needs_cert_or_dl": "a medical certificate or a U.S. driver's license is required",
    "d_row1": "the operation requires an ATP certificate for PIC privileges or SIC privileges in a flag or supplemental "
              "part 121 operation requiring three or more pilots ((d)(1)(i)-(ii))",
    "d_row1_60": "the operation is a part 121 pilot flightcrew member who has reached the 60th birthday ((d)(1)(ii))",
    "d_atp_sic": "the operation requires an ATP certificate for SIC privileges other than (d)(1) operations ((d)(2)(i))",
    "d_comm": "the operation requires a commercial pilot certificate (not a balloon rating when conducting flight training), "
              "a flight engineer or an air traffic control tower operator certificate",
    "d_priv": "the operation requires a recreational, private, student or sport pilot certificate or a flight instructor "
              "certificate when acting as PIC or required pilot crew outside gliders and balloons",
    "mr_any": "has a most recent medical certificate", "mr_first": "the most recent medical certificate is first class",
    "mr_second": "the most recent medical certificate is second class",
    "mr_suspended": "the most recent medical certificate has been suspended or revoked",
    "valid_med": "D is on or before the expiry of the most recent medical certificate for the operation",
    "med_ok": "meets the requirement with a medical certificate",
    "c2_applies": "(c)(2) binds the driver's license route", "c3_applies": "(c)(3) binds the driver's license route",
    "c2ii": "61.23(c)(2)(ii)", "c2iii": "61.23(c)(2)(iii)", "c2_ok": "meets (c)(2)",
    "c3ib": "61.23(c)(3)(i)(B)", "c3ic": "61.23(c)(3)(i)(C)", "c3id": "61.23(c)(3)(i)(D)", "c3iv": "61.23(c)(3)(iv)",
    "c3_ok": "meets (c)(3)",
    "dl_ok": "meets the requirement with a U.S. driver's license",
    "meets": "meets the requirement of 61.23 for the operation on D (Q2)",
    "crossing": "a part 121 required pilot crew member whose 60th birthday falls after D and on or before the expiry",
    "no_last_day": "61.23 sets no last day (Q3 NONE)",
}
CERT_PREDS = {
    "first_class": "is a first-class medical certificate", "second_class": "is a second-class medical certificate",
    "third_class": "is a third-class medical certificate",
    "suspended_or_revoked": "has been suspended or revoked",
    "under40_exam": "the pilot was under age 40 on its date of examination (bridge)",
    "after_2006": "its date of examination is after July 14, 2006 (bridge)",
    "held_by_d": "its date of examination is on or before D",
    "most_recent": "is the pilot's most recent medical certificate on D",
}
APP_PREDS = {
    "app_eligible": "the person was found eligible for at least a third-class certificate on this application",
    "app_denied": "this application was completed and denied",
    "most_recent_app": "is the pilot's most recent application for an airman medical certificate",
}


def environment():
    consts = {"pilot": {"sort": "person", "description": "The pilot.", "verbalisation": "the pilot"}}
    for c in CERTS:
        consts[c] = {"sort": "certificate", "description": f"A medical certificate the case names ({c}).",
                     "verbalisation": f"the case's {c}"}
    for a in APPS:
        consts[a] = {"sort": "application", "description": f"A medical certificate application the case names ({a}).",
                     "verbalisation": f"the case's {a}"}
    for n, w in INTS.items():
        consts[n] = {"sort": "$int", "unit": "day", "description": w[0].upper() + w[1:] + ".", "verbalisation": w}
    preds = {n: {"arguments": ["person"], "description": d[0].upper() + d[1:] + "."} for n, d in {**FACTS, **DERIVED}.items()}
    preds.update({n: {"arguments": ["certificate"], "description": d[0].upper() + d[1:] + "."} for n, d in CERT_PREDS.items()})
    preds.update({n: {"arguments": ["application"], "description": d[0].upper() + d[1:] + "."} for n, d in APP_PREDS.items()})
    preds["later"] = {"arguments": ["certificate", "certificate"],
                      "description": "The first certificate's date of examination is later than the second's (bridge)."}
    preds["app_later"] = {"arguments": ["application", "application"],
                          "description": "The first application is later than the second (bridge)."}
    sorts = {s: {"description": f"A {s}."} for s in ("person", "certificate", "application")}
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": sorts, "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1", "units": {"day": DAY}}


# --- formula helpers (law 1's shapes) -----------------------------------------------------------
def c(n): return ["const", n]
def ci(n): return ["const", "day", n]
def day(iso): return ["date", iso]
def U(p, x="pilot"): return ["unary", p, c(x) if isinstance(x, str) else x]
def B(p, x, y): return ["binary", p, c(x) if isinstance(x, str) else x, c(y) if isinstance(y, str) else y]
def Not(f): return ["not", f]
def V(i): return ["var", i]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def All(sort, f): return ["forall", sort, f]
def Ex(sort, f): return ["exists", sort, f]
def Eq(a, b): return ["eq", a, b]
def no_later(a, b): return ["date_no_later", a, b]
def before(a, b): return ["date_before", a, b]


def And(*fs):
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["and", f, r]
    return r


def Or(*fs):
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["or", f, r]
    return r


u = U
gb = Or(u("in_glider"), u("in_balloon"))
not_gb = And(Not(u("in_glider")), Not(u("in_balloon")))
pic_or_crew = Or(u("acting_pic"), u("required_crew"))


def cert_rules(k):
    """Rules about certificate constant k (written once per certificate the case names: grounding, translation.py)."""
    E = lambda n: ci(f"{k}_{n}")  # noqa: E731
    mr = U("most_recent", k)
    first, second, third, u40 = U("first_class", k), U("second_class", k), U("third_class", k), U("under40_exam", k)
    return [
        ("held_by_d", "d-lead", Iff(U("held_by_d", k), no_later(E("exam"), ci("flight_day")))),
        # (d) table, one rule per row and age; the expiry of the MOST RECENT certificate for the operation (T4)
        ("d1i", "(d)(1)(i)", Implies(And(mr, first, u40, u("d_row1")), Eq(ci("expiry"), E("end12")))),
        ("d1ii", "(d)(1)(ii)", Implies(And(mr, first, Not(u40), Or(u("d_row1"), u("d_row1_60"))), Eq(ci("expiry"), E("end6")))),
        ("d1iii", "(d)(1)(iii)", Implies(And(mr, first, u("d_comm")), Eq(ci("expiry"), E("end12")))),
        ("d1iv", "(d)(1)(iv)", Implies(And(mr, first, u40, u("d_priv")), Eq(ci("expiry"), E("end60")))),
        ("d1v", "(d)(1)(v)", Implies(And(mr, first, Not(u40), u("d_priv")), Eq(ci("expiry"), E("end24")))),
        ("d2i", "(d)(2)(i)", Implies(And(mr, second, Or(u("d_atp_sic"), u("d_comm"))), Eq(ci("expiry"), E("end12")))),
        ("d2ii", "(d)(2)(ii)", Implies(And(mr, second, u40, u("d_priv")), Eq(ci("expiry"), E("end60")))),
        ("d2iii", "(d)(2)(iii)", Implies(And(mr, second, Not(u40), u("d_priv")), Eq(ci("expiry"), E("end24")))),
        ("d3i", "(d)(3)(i)", Implies(And(mr, third, u40, u("d_priv")), Eq(ci("expiry"), E("end60")))),
        ("d3ii", "(d)(3)(ii)", Implies(And(mr, third, Not(u40), u("d_priv")), Eq(ci("expiry"), E("end24")))),
    ]


def T(certs, apps):
    """All rules for a case naming these certificate and application constants: [(id, cite, formula)].
    Quantifiers over certificates/applications are left in the formula; translation.py grounds them."""
    out = [
        ("reached_60", "(a)(1)(iii)", Iff(u("reached_60"), no_later(ci("sixtieth"), ci("flight_day")))),
        # (a)
        ("a11", "(a)(1)(i)", Iff(u("a11"), And(u("atp"), u("acting_pic")))),
        ("a12", "(a)(1)(ii)", Iff(u("a12"), And(u("atp"), u("serving_sic"), u("part121"), u("flag_supp_3plus")))),
        ("a13", "(a)(1)(iii)", Iff(u("a13"), And(u("part121"), u("required_crew"), u("reached_60")))),
        ("a21", "(a)(2)(i)", Iff(u("a21"), And(u("atp"), u("serving_sic"), u("part121"), Not(u("a12"))))),
        ("a22", "(a)(2)(ii)", Iff(u("a22"), And(u("commercial"), not_gb))),
        ("a23", "(a)(2)(iii)", Iff(u("a23"), And(u("commercial"), u("balloon_rating"), u("comp_hire"), Not(u("b5"))))),
        ("a31", "(a)(3)(i)", Iff(u("a31"), And(Or(u("private"), u("recreational"), u("student")), Not(u("under_113i"))))),
        ("a32", "(a)(3)(ii)", Iff(u("a32"), And(u("flight_instructor"), pic_or_crew, Not(u("under_113i"))))),
        ("a33", "(a)(3)(iii)", Iff(u("a33"), And(u("taking_test_aircraft"), Not(u("under_113i"))))),
        ("a34", "(a)(3)(iv)", Iff(u("a34"), And(u("examiner_aircraft"), Not(u("under_113i"))))),
        ("a1", "(a)(1)", Iff(u("a1"), Or(u("a11"), u("a12"), u("a13")))),
        ("a2", "(a)(2)", Iff(u("a2"), Or(u("a21"), u("a22"), u("a23")))),
        ("a3", "(a)(3)", Iff(u("a3"), Or(u("a31"), u("a32"), u("a33"), u("a34")))),
        # (b)
        ("b1", "(b)(1)", Iff(u("b1"), And(u("student"), Or(u("seeking_sport_gb"), u("seeking_gb_rating"))))),
        ("b2", "(b)(2)", Iff(u("b2"), And(u("sport"), gb))),
        ("b3", "(b)(3)", Iff(u("b3"), And(u("glider_rating"), u("in_glider")))),
        ("b4", "(b)(4)", Iff(u("b4"), And(u("private"), u("balloon_rating"), u("in_balloon")))),
        ("b5", "(b)(5)", Iff(u("b5"), And(u("commercial"), u("balloon_rating"), u("in_balloon"), u("training_61_133")))),
        ("b6", "(b)(6)", Iff(u("b6"), And(u("flight_instructor"), Or(And(u("fi_sport_rating"), gb),
                                                                      And(u("fi_glider_rating"), u("in_glider")))))),
        ("b7", "(b)(7)", Iff(u("b7"), And(u("flight_instructor"), Not(u("acting_pic")), Not(u("required_crew"))))),
        ("b8", "(b)(8)", Iff(u("b8"), u("ground_instructor"))),
        ("b9", "(b)(9)", Iff(u("b9"), u("examiner_gbsf"))),
        ("b10", "(b)(10)", Iff(u("b10"), u("taking_test_gbsf"))),
        ("b11", "(b)(11)", Iff(u("b11"), And(u("military_evidence"), Not(u("a1")), Not(u("a2")), u("domestic_us")))),
        ("b12", "(b)(12)", Iff(u("b12"), And(u("special_med_test"), u("acting_pic")))),
        # (c)(1)
        ("c1i", "(c)(1)(i)", Iff(u("c1i"), And(u("student"), u("seeking_sport"), u("meets_316"), not_gb))),
        ("c1ii", "(c)(1)(ii)", Iff(u("c1ii"), And(u("sport"), u("meets_316"), not_gb))),
        ("c1iii", "(c)(1)(iii)", Iff(u("c1iii"), And(u("flight_instructor"), u("fi_sport_rating"), pic_or_crew,
                                                     u("meets_316"), not_gb))),
        ("c1iv", "(c)(1)(iv)", Iff(u("c1iv"), And(u("examiner_sport_test"), u("meets_316"), not_gb))),
        ("c1v", "(c)(1)(v)", Iff(u("c1v"), And(Or(u("student"), u("recreational"), u("private")), u("under_113i")))),
        ("c1vi", "(c)(1)(vi)", Iff(u("c1vi"), And(u("sport"), u("night"), u("under_113i")))),
        ("c1vii", "(c)(1)(vii)", Iff(u("c1vii"), And(u("flight_instructor"), pic_or_crew, u("under_113i")))),
        ("c1viii", "(c)(1)(viii)", Iff(u("c1viii"), And(u("examiner_admin"), u("under_113i")))),
        # the requirement (T1-T3)
        ("b_eff", "(b), (c)(1)(vi)", Iff(u("b_eff"), Or(And(Or(u("b1"), u("b2"), u("b6")), Not(u("c1vi"))),
                                                        u("b3"), u("b4"), u("b5"), u("b7"), u("b8"), u("b9"), u("b10"),
                                                        u("b11"), u("b12")))),
        ("c_any", "(c)(1)", Iff(u("c_any"), Or(*(u(f"c1{r}") for r in ("i", "ii", "iii", "iv", "v", "vi", "vii", "viii"))))),
        ("needs_none", "(b)", Iff(u("needs_none"), And(u("b_eff"), Not(u("c_any"))))),
        ("needs_cert_or_dl", "(c)(1)", Iff(u("needs_cert_or_dl"), And(u("c_any"), Not(u("b_eff"))))),
        ("needs_first", "(a)(1)", Iff(u("needs_first"), And(u("a1"), Not(u("b_eff")), Not(u("c_any"))))),
        ("needs_second", "(a)(2)", Iff(u("needs_second"), And(u("a2"), Not(u("a1")), Not(u("b_eff")), Not(u("c_any"))))),
        ("needs_third", "(a)(3)", Iff(u("needs_third"), And(u("a3"), Not(u("a1")), Not(u("a2")), Not(u("b_eff")),
                                                            Not(u("c_any"))))),
        # (d): what the operation requires, for the table
        ("d_row1", "(d)(1)(i)-(ii)", Iff(u("d_row1"), Or(u("a11"), u("a12")))),
        ("d_row1_60", "(d)(1)(ii)", Iff(u("d_row1_60"), u("a13"))),
        ("d_atp_sic", "(d)(2)(i)", Iff(u("d_atp_sic"), And(u("atp"), u("serving_sic"), Not(u("d_row1")), Not(u("d_row1_60"))))),
        ("d_comm", "(d)(1)(iii), (d)(2)(i)", Iff(u("d_comm"), Or(And(u("commercial"),
                                                                     Not(And(u("balloon_rating"), u("in_balloon"),
                                                                             u("conducting_training")))),
                                                                 u("flight_engineer"), u("atc_tower")))),
        ("d_priv", "(d)(1)(iv)-(v), (d)(2)(ii)-(iii), (d)(3)", Iff(u("d_priv"), Or(
            u("recreational"), u("private"), And(u("flight_instructor"), pic_or_crew, not_gb), u("student"), u("sport")))),
        # the most recent certificate and application (D1: quantified over the case's records)
        ("most_recent", "(d), (c)(2)(iii), (c)(3)(ii)", All("certificate", Iff(
            ["unary", "most_recent", V(0)],
            And(["unary", "held_by_d", V(0)],
                All("certificate", Implies(And(Not(Eq(V(0), V(1))), ["unary", "held_by_d", V(0)]),
                                           ["binary", "later", V(1), V(0)])))))),
        ("most_recent_app", "(c)(2)(ii), (c)(3)(iv)", All("application", Iff(
            ["unary", "most_recent_app", V(0)],
            All("application", Implies(Not(Eq(V(0), V(1))), ["binary", "app_later", V(1), V(0)]))))),
        ("mr_any", "(d)", Iff(u("mr_any"), Ex("certificate", ["unary", "most_recent", V(0)]))),
        ("mr_first", "(d)", Iff(u("mr_first"), Ex("certificate", And(["unary", "most_recent", V(0)],
                                                                    ["unary", "first_class", V(0)])))),
        ("mr_second", "(d)", Iff(u("mr_second"), Ex("certificate", And(["unary", "most_recent", V(0)],
                                                                      ["unary", "second_class", V(0)])))),
        ("mr_suspended", "(c)(2)(iii), (c)(3)(ii)(C)", Iff(u("mr_suspended"), Ex("certificate", And(
            ["unary", "most_recent", V(0)], ["unary", "suspended_or_revoked", V(0)])))),
        # the medical route
        ("valid_med", "(d)", Iff(u("valid_med"), no_later(ci("flight_day"), ci("expiry")))),
        ("med_ok", "(a), (c)(1), (d)", Iff(u("med_ok"), And(u("mr_any"), Not(u("mr_suspended")), u("valid_med"),
                                                            Implies(u("needs_first"), u("mr_first")),
                                                            Implies(u("needs_second"), Or(u("mr_first"), u("mr_second")))))),
        # the driver's license route (T5)
        ("c2_applies+", "(c)(2)", Implies(u("sport"), u("c2_applies"))),
        ("c2_applies-", "(c)(2)", Implies(And(Not(u("sport")), Not(u("c1i")), Not(u("c1iii")), Not(u("c1iv"))),
                                          Not(u("c2_applies")))),
        ("c3_applies", "(c)(3)", Iff(u("c3_applies"), u("under_113i"))),
        ("c2ii", "(c)(2)(ii)", Iff(u("c2ii"), All("application", Implies(["unary", "most_recent_app", V(0)],
                                                                          ["unary", "app_eligible", V(0)])))),
        ("c2iii", "(c)(2)(iii)", Iff(u("c2iii"), And(Not(u("mr_suspended")), Not(u("last_si_withdrawn"))))),
        ("c2_ok", "(c)(2)", Iff(u("c2_ok"), And(u("dl_complied"), u("c2ii"), u("c2iii"), Not(u("knows_condition"))))),
        ("c3ib", "(c)(3)(i)(B)", Iff(u("c3ib"), Ex("certificate", ["unary", "after_2006", V(0)]))),
        ("c3ic", "(c)(3)(i)(C)", Iff(u("c3ic"), And(u("course_done"), no_later(ci("course_day"), ci("flight_day")),
                                                    no_later(ci("flight_day"), ci("course_end24"))))),
        ("c3id", "(c)(3)(i)(D)", Iff(u("c3id"), And(u("basic_exam_done"), no_later(ci("basic_exam_day"), ci("flight_day")),
                                                    no_later(ci("flight_day"), ci("basic_exam_end48"))))),
        ("c3iv", "(c)(3)(iv)", Iff(u("c3iv"), All("application", Implies(["unary", "most_recent_app", V(0)],
                                                                          Not(["unary", "app_denied", V(0)]))))),
        ("c3_ok", "(c)(3)", Iff(u("c3_ok"), And(u("dl_med_complied"), u("c3ib"), u("c3ic"), u("c3id"),
                                                Implies(u("diagnosed_impact"), u("physician_care")),
                                                Not(u("mr_suspended")), Not(u("last_si_withdrawn")), u("c3iv")))),
        ("dl_ok", "(c)(1)-(3)", Iff(u("dl_ok"), And(u("holds_dl"), Implies(u("c2_applies"), u("c2_ok")),
                                                    Implies(u("c3_applies"), u("c3_ok"))))),
        # Q2
        ("meets", "61.23", Iff(u("meets"), Or(u("needs_none"),
                                              And(Or(u("needs_first"), u("needs_second"), u("needs_third")), u("med_ok")),
                                              And(u("needs_cert_or_dl"), Or(u("med_ok"), u("dl_ok")))))),
        # Q3 (T7)
        ("crossing", "(a)(1)(iii), (d)(1)(ii)", Iff(u("crossing"), And(u("part121"), u("required_crew"), Not(u("reached_60")),
                                                                       Not(u("a11")), Not(u("a12")),
                                                                       no_later(ci("sixtieth"), ci("expiry"))))),
        ("no_last_day", "(b), (c)(2)", Iff(u("no_last_day"), Or(u("needs_none"), And(u("needs_cert_or_dl"), u("dl_ok"),
                                                                                    Not(u("c3_applies")))))),
        ("dl_last1", "(c)(3)(i)(C)-(D)", Implies(no_later(ci("course_end24"), ci("basic_exam_end48")),
                                                 Eq(ci("dl_last"), ci("course_end24")))),
        ("dl_last2", "(c)(3)(i)(C)-(D)", Implies(before(ci("basic_exam_end48"), ci("course_end24")),
                                                 Eq(ci("dl_last"), ci("basic_exam_end48")))),
        ("last_med", "(d)", Implies(And(Or(u("needs_first"), u("needs_second"), u("needs_third")), u("med_ok"),
                                        Not(u("crossing"))), Eq(ci("last_day"), ci("expiry")))),
        ("last_c_med", "(c)(1), (d)", Implies(And(u("needs_cert_or_dl"), u("med_ok"), Not(u("dl_ok"))),
                                              Eq(ci("last_day"), ci("expiry")))),
        ("last_c_dl", "(c)(3)", Implies(And(u("needs_cert_or_dl"), u("dl_ok"), u("c3_applies"), Not(u("med_ok"))),
                                        Eq(ci("last_day"), ci("dl_last")))),
        ("last_c_both1", "(c)(3), (d)", Implies(And(u("needs_cert_or_dl"), u("dl_ok"), u("c3_applies"), u("med_ok"),
                                                    no_later(ci("dl_last"), ci("expiry"))), Eq(ci("last_day"), ci("expiry")))),
        ("last_c_both2", "(c)(3), (d)", Implies(And(u("needs_cert_or_dl"), u("dl_ok"), u("c3_applies"), u("med_ok"),
                                                    before(ci("expiry"), ci("dl_last"))), Eq(ci("last_day"), ci("dl_last")))),
    ]
    for k in certs:
        out += [(f"{k}.{rid}", cite, f) for rid, cite, f in cert_rules(k)]
    return out
