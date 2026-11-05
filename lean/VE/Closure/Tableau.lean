import VE.Core.Conservativity
import VE.Core.TableauExtendedChecker

/-! Closure's tableau certificates, checked by Core's replay (consolidation step 3b).

A closure certificate has Core's shape over the closure language, which has no n-ary `atom`:
its induction invariants are closure formulas. That is the atom-free gate in front of Core.
Closure's own decoder (`VE.CertificateWire.decodeClosureTrace`) refuses an `atom` invariant
with its own message, and `embedCert` maps what it accepts into Core's syntax, where
`checkCertificate` runs Core's `replay` behind closure's own version gate: `@0` and `@1`, with
the induction rule only at `@1`. `VE.Closure.CoreEquiv.checkCertificate_eq_core_replay` is its
defining equation. -/
namespace VE.Closure.Tableau
universe u

inductive Trace where
  | close
  | expand (rule : String) (index : Nat) (parameter : Option String) (children : List Trace)
  | induct (index : Nat) (sort : String) (invariant : Formula) (children : List Trace)
  deriving Repr

/-- The five fields shared by ve-tableau-checker@1 and @2. Hash bindings are checked by the
wire adapter; semantic replay always uses the actual supplied ASTs and E. -/
structure Certificate where
  checker_version : String
  environment_id : String
  premise_meaning_ids : List String
  conclusion_meaning_id : String
  trace : Trace
  deriving Repr

/-- The closure rules beyond expansion that a trace may name: Core's. -/
abbrev extraRule (rule : String) : Bool := VE.Core.Tableau.extraRule rule

end VE.Closure.Tableau

namespace VE.Closure.CoreEquiv

open VE.Core (embedClosure)

mutual
def embedTrace : Tableau.Trace → Core.Tableau.Trace
  | .close => .close
  | .expand rule index parameter children => .expand rule index parameter (embedTraces children)
  | .induct index sort P children => .induct index sort (embedClosure P) (embedTraces children)
def embedTraces : List Tableau.Trace → List Core.Tableau.Trace
  | [] => []
  | t :: ts => embedTrace t :: embedTraces ts
end

def embedCert (c : Tableau.Certificate) : Core.Tableau.Certificate :=
  ⟨c.checker_version, c.environment_id, c.premise_meaning_ids, c.conclusion_meaning_id,
    embedTrace c.trace⟩

end VE.Closure.CoreEquiv

namespace VE.Closure.Tableau

open VE.Core (embedClosure)
open VE.Closure.CoreEquiv (embedCert)

/-- The logical checker uses exact AST inputs; wire identity validation is an
additional gate. Closure's version gate, then Core's replay of the embedded certificate:
the induction rule is on only for `@1`, so `@0` certificates keep their verdicts. -/
def checkCertificate (E : Environment) (premises : List Formula) (conclusion : Formula)
    (c : Certificate) : Bool :=
  (c.checker_version == "ve-tableau-closure-checker@0" ||
      c.checker_version == "ve-tableau-closure-checker@1") &&
    (premises.map embedClosure).all (fun f => f.check E []) &&
    (embedClosure conclusion).check E [] &&
    Core.Tableau.replay E true (c.checker_version == "ve-tableau-closure-checker@1") 125
      (Core.Tableau.initial (premises.map embedClosure) (embedClosure conclusion)) (embedCert c).trace

/-- Sound over every admissible structure at every universe, including empty
sorts and an empty common carrier. There is no certificate-soundness premise: Core's
replay is sound for both flags, and closure consequence is Core consequence of the
embedding (`VE.Core.entails_closure`). -/
theorem checkCertificate_sound (E : Environment) (premises : List Formula)
    (conclusion : Formula) (c : Certificate) (hc : checkCertificate E premises conclusion c = true) :
    Entails.{u} E premises conclusion := by
  classical
  apply VE.Core.entails_closure
  intro S hS hp
  apply Classical.byContradiction
  intro hn
  have hr : Core.Tableau.replay E true (c.checker_version == "ve-tableau-closure-checker@1") 125
      (Core.Tableau.initial (premises.map embedClosure) (embedClosure conclusion))
      (embedCert c).trace = true :=
    (Bool.and_eq_true_iff.mp hc).2
  apply Core.Tableau.replay_sound hS _ _ _ _ (fun _ => none) _ _ _ hr
  · intro i s hi
    simp [Core.Tableau.initial] at hi
  · intro a ha
    rcases List.mem_append.mp ha with ha | ha
    · obtain ⟨f, hm, rfl⟩ := List.mem_map.mp ha
      exact hp f hm
    · have he : a = ⟨embedClosure conclusion, false, []⟩ := by simpa using ha
      subst a
      exact hn

/-- The extended soundness theorem specializes to the unchanged v0 consequence
relation through the proved denotation conservativity theorem. -/
theorem checkCertificate_sound_v0 (E : Environment) (premises : List VE.Formula)
    (conclusion : VE.Formula) (c : Certificate)
    (hc : checkCertificate E (premises.map embed) (embed conclusion) c = true) :
    VE.Entails.{u} E premises conclusion := by
  intro S hS hp
  apply (conservativity S [] conclusion).mp
  apply checkCertificate_sound E (premises.map embed) (embed conclusion) c hc S hS
  intro a ha
  obtain ⟨f,hf,rfl⟩ := List.mem_map.mp ha
  exact (conservativity S [] f).mpr (hp f hf)

end VE.Closure.Tableau
