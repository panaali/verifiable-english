"""Fresh vocabularies for E1. Nothing here is taken from a public dataset.

A *binding* fills the abstract roles used by the templates:

    sorts   A, B
    unary   P, Q, X, Y on A;  S on B
    binary  R : (B, A);  T : (A, A)

Each predicate has an identifier (used in every formal view), a positive and a negative English
phrase (used only in the requirement prose), and a description (shown in the vocabulary list).
Predicates inside one binding are chosen to be logically independent in ordinary usage, so that a
judge cannot settle an item from world knowledge.
"""

from __future__ import annotations

from dataclasses import dataclass

SPEC_REVISION = "ve-v0-draft-2026-09-20"


@dataclass(frozen=True)
class Pred:
    id: str
    pos: str  # "is deployed" / "maintains"
    neg: str  # "is not deployed" / "does not maintain"
    desc: str


@dataclass(frozen=True)
class Binding:
    family: str
    name: str
    A: tuple[str, str]  # (sort id, description)
    B: tuple[str, str]
    P: Pred
    Q: Pred
    X: Pred
    Y: Pred
    S: Pred
    R: Pred
    T: Pred

    def verbalisation(self) -> dict:
        """Verbalisation templates for an ACE-style natural view ({0}, {1} are argument slots). They
        live beside the environment because the v0 environment schema rejects unknown fields."""
        preds = {getattr(self, r).id: _verbalise(getattr(self, r), 1) for r in "PQXYS"}
        preds[self.R.id] = _verbalise(self.R, 2)
        preds[self.T.id] = _verbalise(self.T, 2)
        sorts = {s[0]: {"singular": s[0], "plural": s[0] + "s"} for s in (self.A, self.B)}
        return {"sorts": sorts, "predicates": preds}

    def environment(self) -> dict:
        a, b = self.A[0], self.B[0]
        preds = {}
        for role in "PQXY":
            p = getattr(self, role)
            preds[p.id] = {"arguments": [a], "description": p.desc}
        preds[self.S.id] = {"arguments": [b], "description": self.S.desc}
        preds[self.R.id] = {"arguments": [b, a], "description": self.R.desc}
        preds[self.T.id] = {"arguments": [a, a], "description": self.T.desc}
        return {
            "language": "ve.core@0",
            "profile": "relational-fol@0",
            "spec_revision": SPEC_REVISION,
            "vocabulary": {
                "sorts": {a: {"description": self.A[1]}, b: {"description": self.B[1]}},
                "predicates": preds,
                "constants": {},
            },
        }


def _verbalise(p: Pred, arity: int) -> dict:
    if arity == 1:
        return {"positive": "{0} " + p.pos, "negative": "{0} " + p.neg}
    return {"positive": "{0} " + p.pos + " {1}", "negative": "{0} " + p.neg + " {1}"}


def _u(id: str, adj: str, desc: str) -> Pred:
    return Pred(id, f"is {adj}", f"is not {adj}", desc)


def _v(id: str, verb3: str, base: str, desc: str) -> Pred:
    return Pred(id, verb3, f"does not {base}", desc)


BINDINGS: list[Binding] = [
    Binding("deployment", "services",
        ("service", "A software service in the inventory."), ("engineer", "An engineer on the staff list."),
        _u("deployed", "deployed", "The service is recorded as deployed."),
        _u("reviewed", "reviewed", "The service is recorded as reviewed."),
        _u("deprecated", "deprecated", "The service is recorded as deprecated."),
        _u("internal", "internal", "The service is recorded as internal-only."),
        _u("on_call", "on call", "The engineer is recorded as on call."),
        _v("maintains", "maintains", "maintain", "The engineer (first) is recorded as a maintainer of the service (second)."),
        _v("depends_on", "depends on", "depend on", "The first service is recorded as depending on the second service.")),
    Binding("deployment", "pipelines",
        ("pipeline", "A build pipeline in the registry."), ("operator", "An operator on the roster."),
        _u("active", "active", "The pipeline is recorded as active."),
        _u("audited", "audited", "The pipeline is recorded as audited."),
        _u("experimental", "experimental", "The pipeline is recorded as experimental."),
        _u("sandboxed", "sandboxed", "The pipeline is recorded as sandboxed."),
        _u("certified", "certified", "The operator is recorded as certified."),
        _v("monitors", "monitors", "monitor", "The operator (first) is recorded as monitoring the pipeline (second)."),
        _v("triggers", "triggers", "trigger", "The first pipeline is recorded as triggering the second pipeline.")),
    Binding("access", "accounts",
        ("account", "A user account in the directory."), ("administrator", "An administrator in the directory."),
        _u("privileged", "privileged", "The account is recorded as privileged."),
        _u("enrolled", "enrolled", "The account is recorded as enrolled in multi-factor authentication."),
        _u("suspended", "suspended", "The account is recorded as suspended."),
        _u("shared", "shared", "The account is recorded as shared by several people."),
        _u("vetted", "vetted", "The administrator is recorded as vetted."),
        _v("sponsors", "sponsors", "sponsor", "The administrator (first) is recorded as sponsor of the account (second)."),
        _v("delegates_to", "delegates to", "delegate to", "The first account is recorded as delegating its rights to the second account.")),
    Binding("access", "documents",
        ("document", "A document in the repository."), ("curator", "A curator of the repository."),
        _u("confidential", "confidential", "The document is recorded as confidential."),
        _u("encrypted", "encrypted", "The document is recorded as encrypted."),
        _u("archived", "archived", "The document is recorded as archived."),
        _u("redacted", "redacted", "The document is recorded as redacted."),
        _u("cleared", "cleared", "The curator is recorded as security-cleared."),
        _v("curates", "curates", "curate", "The curator (first) is recorded as curating the document (second)."),
        _v("references", "references", "reference", "The first document is recorded as referencing the second document.")),
    Binding("lab", "samples",
        ("sample", "A sample in the laboratory log."), ("technician", "A technician in the laboratory log."),
        _u("hazardous", "hazardous", "The sample is recorded as hazardous."),
        _u("sealed", "sealed", "The sample is recorded as sealed."),
        _u("quarantined", "quarantined", "The sample is recorded as quarantined."),
        _u("labelled", "labelled", "The sample is recorded as labelled."),
        _u("trained", "trained", "The technician is recorded as safety-trained."),
        _v("handles", "handles", "handle", "The technician (first) is recorded as handling the sample (second)."),
        _v("stored_with", "is stored with", "get stored with", "The first sample is recorded as stored in the same container as the second sample.")),
    Binding("lab", "instruments",
        ("instrument", "An instrument in the equipment register."), ("inspector", "An inspector in the equipment register."),
        _u("pressurized", "pressurized", "The instrument is recorded as pressurized."),
        _u("calibrated", "calibrated", "The instrument is recorded as calibrated."),
        _u("decommissioned", "decommissioned", "The instrument is recorded as decommissioned."),
        _u("portable", "portable", "The instrument is recorded as portable."),
        _u("accredited", "accredited", "The inspector is recorded as accredited."),
        _v("inspects", "inspects", "inspect", "The inspector (first) is recorded as inspecting the instrument (second)."),
        _v("feeds", "feeds", "feed", "The first instrument is recorded as feeding its output to the second instrument.")),
    Binding("finance", "payments",
        ("payment", "A payment in the ledger."), ("approver", "An approver in the finance team list."),
        _u("international", "international", "The payment is recorded as international."),
        _u("screened", "screened", "The payment is recorded as sanctions-screened."),
        _u("reversed", "reversed", "The payment is recorded as reversed."),
        _u("recurring", "recurring", "The payment is recorded as recurring."),
        _u("senior", "senior", "The approver is recorded as senior."),
        _v("authorizes", "authorizes", "authorize", "The approver (first) is recorded as authorizing the payment (second)."),
        _v("offsets", "offsets", "offset", "The first payment is recorded as offsetting the second payment.")),
    Binding("finance", "ledgers",
        ("ledger", "A ledger in the accounting system."), ("auditor", "An auditor on the engagement list."),
        _u("consolidated", "consolidated", "The ledger is recorded as consolidated."),
        _u("reconciled", "reconciled", "The ledger is recorded as reconciled."),
        _u("frozen", "frozen", "The ledger is recorded as frozen."),
        _u("provisional", "provisional", "The ledger is recorded as provisional."),
        _u("independent", "independent", "The auditor is recorded as independent."),
        _v("certifies", "certifies", "certify", "The auditor (first) is recorded as certifying the ledger (second)."),
        _v("rolls_into", "rolls into", "roll into", "The first ledger is recorded as rolling up into the second ledger.")),
    Binding("clinical", "participants",
        ("participant", "A participant in the trial database."), ("clinician", "A clinician in the trial database."),
        _u("randomized", "randomized", "The participant is recorded as randomized."),
        _u("consented", "consented", "The participant is recorded as having given consent."),
        _u("withdrawn", "withdrawn", "The participant is recorded as withdrawn."),
        _u("pediatric", "pediatric", "The participant is recorded as pediatric."),
        _u("blinded", "blinded", "The clinician is recorded as blinded to treatment arm."),
        _v("examines", "examines", "examine", "The clinician (first) is recorded as examining the participant (second)."),
        _v("matched_with", "is matched with", "get matched with", "The first participant is recorded as the matched control of the second participant.")),
    Binding("clinical", "doses",
        ("dose", "A dose in the dispensing record."), ("pharmacist", "A pharmacist in the dispensing record."),
        _u("scheduled", "scheduled", "The dose is recorded as scheduled."),
        _u("verified", "verified", "The dose is recorded as verified."),
        _u("cancelled", "cancelled", "The dose is recorded as cancelled."),
        _u("compounded", "compounded", "The dose is recorded as compounded on site."),
        _u("licensed", "licensed", "The pharmacist is recorded as licensed."),
        _v("dispenses", "dispenses", "dispense", "The pharmacist (first) is recorded as dispensing the dose (second)."),
        _v("replaces", "replaces", "replace", "The first dose is recorded as replacing the second dose.")),
    Binding("warehouse", "robots",
        ("robot", "A robot in the fleet register."), ("supervisor", "A supervisor on the shift list."),
        _u("autonomous", "autonomous", "The robot is recorded as operating autonomously."),
        _u("inspected", "inspected", "The robot is recorded as inspected."),
        _u("docked", "docked", "The robot is recorded as docked."),
        _u("legacy", "legacy", "The robot is recorded as a legacy model."),
        _u("present", "present", "The supervisor is recorded as present on site."),
        _v("oversees", "oversees", "oversee", "The supervisor (first) is recorded as overseeing the robot (second)."),
        _v("follows", "follows", "follow", "The first robot is recorded as following the second robot.")),
    Binding("warehouse", "pallets",
        ("pallet", "A pallet in the stock register."), ("handler", "A handler on the shift list."),
        _u("fragile", "fragile", "The pallet is recorded as fragile."),
        _u("wrapped", "wrapped", "The pallet is recorded as wrapped."),
        _u("empty", "empty", "The pallet is recorded as empty."),
        _u("oversized", "oversized", "The pallet is recorded as oversized."),
        _u("equipped", "equipped", "The handler is recorded as equipped with protective gear."),
        _v("lifts", "lifts", "lift", "The handler (first) is recorded as lifting the pallet (second)."),
        _v("rests_on", "rests on", "rest on", "The first pallet is recorded as resting on the second pallet.")),
]  # fmt: skip

DEV_FAMILIES = ("access", "warehouse")
SCORED_FAMILIES = ("deployment", "lab", "finance", "clinical")
