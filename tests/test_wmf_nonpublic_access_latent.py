"""WMF Access to Nonpublic Personal Data Policy (usecases/wmf_nonpublic_access): two latent departures behind correct
answers, fixed in the rule (rows statute-latent-wmf-nonpublic-access-U6, -U27; manage-agents fidelity check
LATENT-DEPARTURES.md, addendum 2026-11-26, items 13 and 14).

The frozen build (af4991e018) answered every question of its set on these units correctly, but:
* U6: unit 5 makes a known domicile in a blocking jurisdiction a bar to being GRANTED ("would otherwise be unable to be
  granted"); it is not one of Sections (a)-(c). The frozen rule folded it into req ("the minimum requirements of Sections
  (a)-(c) are met") for every test, so the (e) compliance check of unit 23 ("must meet the requirements of Sections (a) -
  (c) ... within ninety (90) calendar days") gave a holder with a blocked domicile who met (a)-(c) in time a definite "no".
  req is now (a)-(c) only; the bar sits in ok of grant and candidacy tests only.
* U27: unit 27 "must destroy all Nonpublic Personal Data that they have as a result of that tool"; the frozen rule made
  ANY data from a revoked tool "must destroy". The duty now needs the data stated to be Nonpublic Personal Data (npd);
  stated not to be (npdst without npd): no; not stated: refused.
Each departure test fails on af4991e018's translation by behaviour (the U6 guards pass there; the U27 guards pass on the
frozen rules once the two new facts npd, npdst exist, and fail before only on that vocabulary); M13 and M14 (the frozen
rules) are killed here. The answers come from the use case's staged prover (run.py run_case; the question-set run
replays every certificate in Lean).
"""
import copy
import sys
from pathlib import Path

import pytest

from tests.usecase_scope import usecase_scope

UC = Path(__file__).resolve().parents[1] / "usecases" / "wmf_nonpublic_access"
REQ = ["cert", "sub", "subvalid", "link", "linkvalid", "cs"]


@pytest.fixture(scope="module")
def uc():
    with usecase_scope(UC):
        sys.path.insert(0, str(UC / "bridge"))
        import cases as K
        import encode as E
        import run as R
        import translation as T
        import wmf_bridge as WB
        yield K, E, R, T, WB
    sys.modules.pop("wmf_bridge", None)


def staged(uc, case, bridge=None, mutant=None):
    """(answers by qid, the Staged object) for a made-up case; bridge {item: bridge input row} replaces bridges.jsonl."""
    _, E, R, _, WB = uc
    real = E.bridges
    if bridge is not None:
        br = {(case["id"], x): WB.row(r) for x, r in bridge.items()}
        E.bridges = lambda: br
    try:
        answers, _, st, *_ = R.run_case(case, mutant)
    finally:
        E.bridges = real
    return {q: a["answer"] for q, a in answers.items()}, st


def truth(uc, st, pred, item):
    v = st.truth(uc[3].U(pred, item))
    return "OPEN" if v is None else ("yes" if v else "no")


# --- U6 ---------------------------------------------------------------------------------------------------------

AGE = {"kind": "age", "dob": "1990-01-01"}


def e_check(cid="L6", a_facts=(), csd="2026-05-01"):
    """A CheckUser holder granted 1 Feb 2026, the Policy effective 1 Mar 2026 (deadline 30 May 2026); the (e) compliance
    check a1 (ctx.atdl: its day is the deadline, a Lean step); every (a)-(c) act on 1 May 2026; known domicile in a
    jurisdiction that blocks access to Wikimedia projects, no exemption."""
    acts = {"certd_a1": "2026-05-01", "subd_a1": "2026-05-01", "linkd_a1": "2026-05-01", "csd_a1": csd}
    return {"id": cid, "facts": {"m": ["granted", "tool"], "a1": REQ + ["blocked"] + list(a_facts)},
            "ints": {"eff_m": "2026-03-01", "gd_m": "2026-02-01", **acts}, "tests": ["a1"], "atdl": ["a1"],
            "questions": [{"qid": f"{cid}-1", "item": "m", "form": "dl"}, {"qid": f"{cid}-2", "item": "a1", "form": "ok"}]}


def grant_test(cid, a_facts):
    """A Suppression grant tested on 1 Jun 2026 (every (a)-(c) act on 1 May), known blocked domicile."""
    acts = {"certd_a1": "2026-05-01", "subd_a1": "2026-05-01", "linkd_a1": "2026-05-01", "csd_a1": "2026-05-01"}
    return {"id": cid, "facts": {"m": ["granted"], "a1": REQ + ["blocked"] + list(a_facts)},
            "ints": {"at_a1": "2026-06-01", **acts}, "tests": ["a1"],
            "questions": [{"qid": f"{cid}-1", "item": "a1", "form": "ok"}]}


def test_e_check_blocked_domicile_meets_a_to_c_req_and_ok_yes(uc):
    """The row's test: the (e) check of a blocked-domicile holder who met (a)-(c) before the deadline: req yes, ok yes
    (af4991e018: both "no")."""
    got, st = staged(uc, e_check(), {"a1": AGE})
    assert got == {"L6-1": "2026-05-30", "L6-2": "yes"}
    assert truth(uc, st, "req", "a1") == "yes"


def test_e_check_blocked_domicile_late_agreement_still_no(uc):
    """Guard (both builds): the Confidentiality Agreement certified after the deadline -> (c) not met -> no."""
    got, st = staged(uc, e_check("L6b", csd="2026-06-01"), {"a1": AGE})
    assert got == {"L6b-1": "2026-05-30", "L6b-2": "no"}
    assert truth(uc, st, "req", "a1") == "no"


def test_grant_blocked_domicile_still_barred(uc):
    """Guard (both builds): unit 5's bar stands at a grant: blocked domicile, no exemption -> ok no."""
    got, _ = staged(uc, grant_test("L6c", ()), {"a1": AGE})
    assert got == {"L6c-1": "no"}


def test_grant_blocked_domicile_req_is_a_to_c_only(uc):
    """req names Sections (a)-(c) only: at the same grant it is met (af4991e018: "no", the bar read into it)."""
    _, st = staged(uc, grant_test("L6d", ()), {"a1": AGE})
    assert truth(uc, st, "req", "a1") == "yes"
    assert truth(uc, st, "domok", "a1") == "no"


def test_grant_blocked_domicile_legal_exemption_ok(uc):
    """Guard (both builds): a Legal-reviewed domicile exemption removes the bar -> ok yes (as W007)."""
    got, _ = staged(uc, grant_test("L6e", ("exm_dom",)), {"a1": AGE})
    assert got == {"L6e-1": "yes"}


def test_m13_frozen_domicile_killed(uc):
    """M13 restores the frozen unit 6: the row's case answers "no" again."""
    assert "M13" in uc[3].MUTANTS
    got, st = staged(uc, e_check("L6m"), {"a1": AGE}, mutant="M13")
    assert got["L6m-2"] == "no"
    assert truth(uc, st, "req", "a1") == "no"


# --- U27 --------------------------------------------------------------------------------------------------------

def destroy_case(cid, dat_facts, revoked=True, xask="2026-08-02"):
    """Hana's Suppression access (t1) revoked on 1 Aug 2026; a data item dat1 she has as a result of it, asked 2 Aug."""
    facts = {"m": ["granted", "supp", "tool"], "dat1": list(dat_facts)}
    ints = {"xask_dat1": xask}
    if revoked:
        facts["t1"] = ["rev"]
        ints["revd_t1"] = "2026-08-01"
    return {"id": cid, "facts": facts, "ints": ints, "tools": ["t1"], "datas": ["dat1"], "from": [("dat1", "t1")],
            "questions": [{"qid": f"{cid}-1", "item": "dat1", "form": "destroy"}]}


def test_revoked_tool_data_not_npd_no_destroy(uc):
    """The row's test: a suppressed revision's text stated to hold no personal data (npdst, not npd), from a tool revoked
    before the day asked: destroy "no" (af4991e018: "yes")."""
    got, _ = staged(uc, destroy_case("L27", ["npdst"]))
    assert got == {"L27-1": "no"}


def test_revoked_tool_data_npd_unstated_refused(uc):
    """Whether the data is Nonpublic Personal Data not stated: refused, never "no duty" (af4991e018: "yes")."""
    got, _ = staged(uc, destroy_case("L27b", []))
    assert got == {"L27b-1": "OPEN"}


def test_revoked_tool_npd_destroy_yes(uc):
    """Guard (both builds): Nonpublic Personal Data from the revoked tool -> must destroy."""
    got, _ = staged(uc, destroy_case("L27c", ["npd", "npdst"]))
    assert got == {"L27c-1": "yes"}


def test_not_revoked_or_before_revocation_no_destroy(uc):
    """Guard (both builds): tool not revoked (npd not stated), or asked before the revocation day (npd) -> no."""
    got, _ = staged(uc, destroy_case("L27d", [], revoked=False))
    assert got == {"L27d-1": "no"}
    got, _ = staged(uc, destroy_case("L27e", ["npd", "npdst"], xask="2026-07-31"))
    assert got == {"L27e-1": "no"}


def test_m14_frozen_destroy_killed(uc):
    """M14 restores the frozen unit 27: the row's case answers "yes" again."""
    assert "M14" in uc[3].MUTANTS
    got, _ = staged(uc, destroy_case("L27m", ["npdst"]), mutant="M14")
    assert got == {"L27m-1": "yes"}


@pytest.mark.parametrize("cid", ["W017", "W018", "W020", "W023"])
def test_question_set_destroy_answers_kept(uc, cid):
    """Guard: the set's destroy questions keep their frozen answers on the re-encoded cases (W023 dat1: a nonpublic email
    address and a private real name, npd; W023 dat2 and the others: npd not stated, their tools never revoked)."""
    K = uc[0]
    case = copy.deepcopy(next(c for c in K.CASES if c["id"] == cid))
    want = {"W017": {"W017-3": "no"}, "W018": {"W018-3": "no"}, "W020": {"W020-3": "no"},
            "W023": {"W023-2": "yes", "W023-3": "no"}}[cid]
    case["questions"] = [q for q in case["questions"] if q["qid"] in want]
    got, _ = staged(uc, case)
    assert got == want
