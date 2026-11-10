import VE.Closure.Tableau
import VE.Route.Steps
import VE.Core.Wire

/-! Closure's tableau checker is Core's on the embedding (consolidation steps 3a and 3b).

Closure's certificate checker (`VE.Closure.Tableau.checkCertificate`) is its own version gate,
then Core's `replay` of the embedded certificate (`embedCert`, with `VE.Core.embedClosure` on
formulas); `checkCertificate_eq_core_replay` is its defining equation. The step counts agree on
the embedding. The trace decoders do not: Core's decodes an n-ary `atom` invariant that
closure's refuses. -/
namespace VE.Closure.CoreEquiv

open VE.Core (embedClosure embedKind)

theorem embedKind_inj (k l : Kind) : embedKind k = embedKind l ↔ k = l := by
  cases k <;> cases l <;> decide

theorem embedClosure_inj (a b : Formula) : embedClosure a = embedClosure b ↔ a = b := by
  induction a generalizing b <;> cases b <;>
    simp_all [embedClosure, Formula.toCore]

def embedEdge : Edge → Core.Edge
  | .named p => .named p
  | .body s a => .body s (embedClosure a)

theorem embedEdge_inj (e f : Edge) : embedEdge e = embedEdge f ↔ e = f := by
  cases e <;> cases f <;> simp [embedEdge, embedClosure_inj]

theorem reach_embed (k : Kind) (e : Edge) (t u : Term) :
    Core.Formula.reach (embedKind k) (embedEdge e) t u = embedClosure (Formula.reach k e t u) := by
  cases e <;> cases k <;> rfl

theorem extraRule_eq (rule : String) : Core.Tableau.extraRule rule = Tableau.extraRule rule := rfl

mutual
/-- A closure trace and its embedding count the same replay steps. -/
theorem steps_embed (t : Tableau.Trace) :
    VE.Route.Steps.core (embedTrace t) = VE.Route.Steps.closure t :=
  match t with
  | .close => rfl
  | .expand _ _ _ cs => by
    simp only [embedTrace, VE.Route.Steps.core, VE.Route.Steps.closure,
      VE.CertificateWire.closureSteps, stepsList_embed cs]
  | .induct _ _ _ cs => by
    simp only [embedTrace, VE.Route.Steps.core, VE.Route.Steps.closure,
      VE.CertificateWire.closureSteps, stepsList_embed cs]

theorem stepsList_embed (ts : List Tableau.Trace) :
    VE.Route.Steps.coreList (embedTraces ts) = VE.CertificateWire.closureStepsList ts :=
  match ts with
  | [] => rfl
  | t :: ts => by
    simp only [embedTraces, VE.Route.Steps.coreList, VE.CertificateWire.closureStepsList,
      steps_embed t, stepsList_embed ts]
end

/-- Closure's certificate checker is its own version gate and well-formedness checks, then
Core's replay of the embedded certificate with closure's flag choice (`version == @1`): the
checker's defining equation. -/
theorem checkCertificate_eq_core_replay (E : Environment) (premises : List Formula)
    (conclusion : Formula) (c : Tableau.Certificate) :
    Tableau.checkCertificate E premises conclusion c =
      ((c.checker_version == "ve-tableau-closure-checker@0" ||
          c.checker_version == "ve-tableau-closure-checker@1") &&
        (premises.map embedClosure).all (fun f => f.check E []) &&
        (embedClosure conclusion).check E [] &&
        Core.Tableau.replay E true (c.checker_version == "ve-tableau-closure-checker@1") 125
          (Core.Tableau.initial (premises.map embedClosure) (embedClosure conclusion))
          (embedCert c).trace) := rfl

/-- An `@0` certificate: Core's replay with the induction flag off. -/
theorem checkCertificate_v0 (E : Environment) (premises : List Formula)
    (conclusion : Formula) (c : Tableau.Certificate)
    (hv : c.checker_version = "ve-tableau-closure-checker@0") :
    Tableau.checkCertificate E premises conclusion c =
      ((premises.map embedClosure).all (fun f => f.check E []) &&
        (embedClosure conclusion).check E [] &&
        Core.Tableau.replay E true false 125
          (Core.Tableau.initial (premises.map embedClosure) (embedClosure conclusion))
          (embedCert c).trace) := by
  rw [checkCertificate_eq_core_replay, hv]
  simp

/-- An `@1` certificate: Core's replay with both flags on, as Core's own checker runs it. -/
theorem checkCertificate_v1 (E : Environment) (premises : List Formula)
    (conclusion : Formula) (c : Tableau.Certificate)
    (hv : c.checker_version = "ve-tableau-closure-checker@1") :
    Tableau.checkCertificate E premises conclusion c =
      ((premises.map embedClosure).all (fun f => f.check E []) &&
        (embedClosure conclusion).check E [] &&
        Core.Tableau.replay E true true 125
          (Core.Tableau.initial (premises.map embedClosure) (embedClosure conclusion))
          (embedCert c).trace) := by
  rw [checkCertificate_eq_core_replay, hv]
  simp

/-- Any other version is rejected. -/
theorem checkCertificate_other_version (E : Environment) (premises : List Formula)
    (conclusion : Formula) (c : Tableau.Certificate)
    (h0 : c.checker_version ≠ "ve-tableau-closure-checker@0")
    (h1 : c.checker_version ≠ "ve-tableau-closure-checker@1") :
    Tableau.checkCertificate E premises conclusion c = false := by
  simp [Tableau.checkCertificate, h0, h1]

/-- The trace decoders are not equal on the embedding: a `closure-induct@1` node whose
invariant is a ternary `atom` decodes in Core and is refused by closure. -/
theorem decodeTrace_ne_embed :
    ∃ fuel j, Core.Wire.decodeTrace fuel j ≠
      (VE.CertificateWire.decodeClosureTrace fuel j).map embedTrace := by
  let c : Lean.Json := .arr #[.str "const", .str "a"]
  refine ⟨125, Lean.Json.mkObj [("rule", .str "closure-induct@1"), ("at", (0 : Nat)),
    ("sort", .str "s"), ("invariant", .arr #[.str "atom", .str "p", .arr #[c, c, c]]),
    ("children", .arr #[])], fun h => ?_⟩
  have h' := congrArg Except.toBool h
  revert h'
  decide

end VE.Closure.CoreEquiv
