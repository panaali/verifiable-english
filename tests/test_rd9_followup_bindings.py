"""fu-rd9-checks: the two answer fields rd-9's rechecks left unchecked (rd-9-c141730 looprecheck1, FOLLOW-UP).

1. Binding-audit row 38: the rights report shows a rights-conflict answer's status line. Its Lean shape
   (`rights.json#/$defs/packages`) makes an UNKNOWN answer's line the UNKNOWN line, its `detail` a certificate failure
   and its `conditional_on` empty, and a CONFLICT-FREE answer's line the CONFLICT-FREE line. The relay binds the target
   an UNKNOWN line names to the request's targets, and the line to its detail (R8 (b)).
2. The `report_id` of a soft-norms or rights admission answer is not a name the relay can bind: it is an identity hash,
   a derived value that ADR 0001 (D1) leaves to Lean and forbids Python to recompute. Lean already guarantees it:
   `VE.SoftNorms.Run.runAdmission_sound` and `VE.Rights.Run.runAdmission_sound` prove every admission answer's
   `report_id` is the digest of the canonical environment id, the document sent and the report
   (`BindingsMatchSourceAndRegeneration`, `RightsAdmissionAnswer`). The regressions below pin that guarantee: the
   theorems stay stated and audited, and Lean's genuine answers meet them.
"""
from __future__ import annotations

import copy
from pathlib import Path

import pytest

from ve import rights_route, soft_route
from ve.backends.service_schema import Invalid, check_row
from ve.errors import CheckerUnavailable

ROW_38 = "CONFLICT-FREE among rules on the same act, conditional on 9 coherence premises and 0 limitation premises"
CONFLICT_UNBOUND = "CheckerUnavailable: Lean rights conflict is not bound to the request: unbound conflict status text"


@pytest.fixture(scope="module", autouse=True)
def _service():
    from tests.test_soft_norms_lean import SERVICE
    if not SERVICE.exists():
        pytest.skip("the Lean service has not been built")


def _gamma():
    from tests.test_relay_binding_inventory import _rights_sources
    from ve.rights import RightsEnvironment
    raw, units = _rights_sources()["gamma"]
    return RightsEnvironment(raw), units


def _conflict(monkeypatch, mutation):
    """The rights report, as a call, with Lean's package answer to `rights-conflict` mutated; the call records the
    mutant and its case in the returned dict."""
    real, seen = rights_route.decide_once, {}

    def forged(mode, case):
        row = copy.deepcopy(real(mode, case))
        if case["kind"] == "rights-conflict" and "witness" not in case:
            mutation(row)
            seen.update(row=row, case=case)
        return row

    monkeypatch.setattr(rights_route, "decide_once", forged)
    environment, units = _gamma()
    return lambda: rights_route.report_rights(environment, units), seen


def test_the_genuine_conflict_answer_is_unknown_and_shown():
    """The forgeries below start from this answer: no package is sent, so the one target's certificate is missing."""
    environment, units = _gamma()
    conflict = rights_route.report_rights(environment, units)["conflict"]
    assert conflict == {"verdict": "UNKNOWN", "targets": ["arrest_permitted"], "conditional_on": [],
                        "status_text": "UNKNOWN: missing certificate for arrest_permitted, budget 10000"}


def _set(**fields):
    def mutation(row):
        row.update(fields)
    return mutation


def _drop_detail(**fields):
    def mutation(row):
        row.pop("detail")
        row.update(fields)
    return mutation


@pytest.mark.parametrize("mutation", [
    # Row 38 as the audit wrote it: a CONFLICT-FREE line, with its counts, on an UNKNOWN verdict.
    pytest.param(_set(status_text=ROW_38, conditional_on=[]), id="row 38"),
    pytest.param(_set(status_text="ghost"), id="UNKNOWN line renamed"),
    pytest.param(_set(detail="ghost", status_text="UNKNOWN: ghost, budget 10000"), id="detail not a certificate"),
    pytest.param(_set(conditional_on=["soft:coherence:a,b"]), id="UNKNOWN conditional on a premise"),
    pytest.param(_drop_detail(verdict="CONFLICT-FREE"), id="CONFLICT-FREE with the UNKNOWN line"),
])
def test_a_status_line_of_the_wrong_verdict_does_not_fit_the_lean_shape(monkeypatch, mutation):
    call, seen = _conflict(monkeypatch, lambda row: None)
    call()
    check_row("rights", seen["row"], seen["case"], 0)
    forged = copy.deepcopy(seen["row"])
    mutation(forged)
    with pytest.raises(Invalid):
        check_row("rights", forged, seen["case"], 0)


@pytest.mark.parametrize("mutation", [
    pytest.param(_set(status_text="UNKNOWN: missing certificate for ghost, budget 10000"), id="line names ghost"),
    pytest.param(_set(detail="missing certificate for ghost",
                      status_text="UNKNOWN: missing certificate for ghost, budget 10000"), id="detail names ghost"),
    pytest.param(_set(status_text="UNKNOWN: invalid certificate for arrest_permitted, budget 10000"),
                 id="line and detail differ"),
    pytest.param(_set(status_text="UNKNOWN: missing certificate for arrest_permitted, budget 9999"),
                 id="budget shifted"),
    pytest.param(_set(detail="missing certificate for ", status_text="UNKNOWN: missing certificate for , budget 10000"),
                 id="no target"),
])
def test_an_unknown_line_naming_what_the_request_lacks_is_unavailable(monkeypatch, mutation):
    """Each forgery fits the shape, so only the relay's binding can refuse it."""
    call, seen = _conflict(monkeypatch, mutation)
    with pytest.raises(CheckerUnavailable) as raised:
        call()
    assert str(raised.value) == CONFLICT_UNBOUND
    check_row("rights", seen["row"], seen["case"], 0)


# ---------------------------------------------------------------------------------------------------
# report_id

ROOT = Path(__file__).resolve().parents[1]
REPORT_ID_THEOREMS = {
    "VE.SoftNorms.Run.runAdmission_sound": ("VE.SoftNorms.Run.SoftAdmissionAnswer@VE.SoftNorms.Run",
                                            "VE.SoftNorms.Run.runAdmission@VE.SoftNorms.Run"),
    "VE.Rights.Run.runAdmission_sound": ("VE.Rights.Run.RightsAdmissionAnswer@VE.Rights.Run",
                                         "VE.Rights.Run.runAdmission@VE.Rights.Run"),
}


def _statements():
    """lean/statements.txt as {theorem: its `-- uses` constants} (tools/lean_statements.py writes one block per
    theorem: `theorem <name>`, the statement, `  -- uses <constants>`)."""
    blocks, name = {}, None
    for line in (ROOT / "lean/statements.txt").read_text().splitlines():
        if line.startswith("theorem "):
            name = line.removeprefix("theorem ")
        elif name is not None and line.startswith("  -- uses "):
            blocks[name] = set(line.removeprefix("  -- uses ").split())
    return blocks


def test_the_report_id_guarantee_is_a_stated_audited_theorem():
    statements = _statements()
    audited = (ROOT / "lean/VE/Audit.lean").read_text().splitlines()
    for theorem, uses in REPORT_ID_THEOREMS.items():
        assert set(uses) <= statements.get(theorem, set()), theorem
        assert f"#print axioms {theorem}" in audited, theorem


SOURCES = {"rights": ("gamma", "carve-out", "bar"), "soft": ("holistic", "open pair", "witness")}


def _admissions(family):
    """(environment, case sent, Lean's answer) of each source's genuine admission."""
    from tests import test_relay_binding_inventory as inventory
    seen = []

    def spy(module, attr):
        real = getattr(module, attr)

        def recording(*args):
            rows = real(*args)
            listed = type(rows) is list
            for case, row in zip(args[1] if listed else [args[-1]], rows if listed else [rows]):
                if case["kind"] == "admission":
                    seen.append((case, copy.deepcopy(row)))
            return rows
        return recording

    out = []
    with pytest.MonkeyPatch.context() as patch:
        for name in SOURCES[family]:
            if family == "rights":
                from ve.rights import RightsEnvironment
                raw, units = inventory._rights_sources()[name]
                environment = RightsEnvironment(raw)
                patch.setattr(rights_route, "decide", spy(rights_route, "decide"))
                inventory._rights_calls(name, environment, units)["rights-admission"]()
            else:
                from ve.softnorms import SoftEnvironment, SoftNormDocument
                raw, norms = inventory._soft_sources()[name]
                document = SoftNormDocument(SoftEnvironment(raw), norms)
                environment = document.env
                patch.setattr(soft_route, "_run", spy(soft_route, "_run"))
                inventory._soft_calls(name, document, raw, norms)["soft-admission"]()
            out.append((environment, *seen.pop()))
    return out


@pytest.mark.parametrize("family", ["soft", "rights"])
def test_lean_admission_report_ids_are_the_identity_the_theorem_states(family):
    """What `runAdmission_sound` proves, on Lean's genuine answers: `report_id` is the digest, under the report domain,
    of the environment id, the document as sent and the report. Distinct sources get distinct ids."""
    from ve.wire import digest
    ids = []
    for environment, case, row in _admissions(family):
        assert row["report_id"] == digest(f"ve-report-{environment.identity_version}\n", {
            "environment_id": environment.environment_id, "document": case["document"], "report": row["report"]})
        ids.append(row["report_id"])
    assert len(set(ids)) == len(SOURCES[family])
