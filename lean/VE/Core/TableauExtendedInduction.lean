import VE.Core.TableauExtendedExtra
import VE.Core.Induction

namespace VE.Core.Tableau

/-- Three ordinary subproofs discharge base, preservation, and continuation.
The supplied unary formula is checked under the path's captured bindings. -/
def induct (E : Environment) (b : Branch) (index : Nat) (s : String) (P : Formula) :
    Option (List Branch) := do
  let a ← b.formulas[index]?
  match a.rule with
  | .closure _ e t r =>
    let context ← a.bindings.mapM (Token.sortOf E b)
    if a.positive && edgeCheck E s e && P.check E (s :: context) then
      some [b.add [⟨invariantAt P t,false,a.bindings⟩],
        b.add [⟨inductionStep s e P,false,a.bindings⟩],
        b.add [⟨invariantAt P r,true,a.bindings⟩]]
    else none
  | _ => none

theorem induct_sound {E : Environment} {S : Structure} (hS : S.Admissible E)
    (b : Branch) (ρ : Assignment S) (hρ : Assignment.Typed S b ρ)
    (hh : b.Holds S ρ) (index : Nat) (s : String) (P : Formula)
    (bs : List Branch) (hn : induct E b index s P = some bs) :
    ∃ child ∈ bs, ∃ σ, Assignment.Typed S child σ ∧ child.Holds S σ := by
  classical
  cases hi : b.formulas[index]? with
  | none => simp [induct,hi] at hn
  | some a =>
    have ha := hh a (List.mem_of_getElem? hi)
    cases hr : a.rule <;> simp only [induct,hi,hr,bind,Option.bind] at hn
    all_goals try contradiction
    rename_i k e t r
    split at hn <;> try contradiction
    dsimp only at hn
    split at hn <;> try contradiction
    rename_i context hc hcheck
    have hc' : (a.positive = true ∧ edgeCheck E s e = true) ∧
        P.check E (s :: context) = true := by simpa using hcheck
    have he : e.Typed E s := by cases e <;> simpa [edgeCheck, Edge.Typed] using hc'.1.2
    have hae := rule_closure_formula a k e t r hr
    simp only [Signed.Holds,hc'.1.1,if_true,hae] at ha
    cases hn
    by_cases hb : (invariantAt P t).denote S (bindingsValue S ρ a.bindings)
    · by_cases hs : (inductionStep s e P).denote S (bindingsValue S ρ a.bindings)
      · refine ⟨b.add [⟨invariantAt P r,true,a.bindings⟩],by simp,ρ,hρ,add_holds S ρ b _ hh ?_⟩
        simpa [Signed.Holds] using closure_induction hS _ k s e P t r he hb hs ha
      · refine ⟨b.add [⟨inductionStep s e P,false,a.bindings⟩],by simp,ρ,hρ,add_holds S ρ b _ hh ?_⟩
        simpa [Signed.Holds] using hs
    · refine ⟨b.add [⟨invariantAt P t,false,a.bindings⟩],by simp,ρ,hρ,add_holds S ρ b _ hh ?_⟩
      simpa [Signed.Holds] using hb

end VE.Core.Tableau
