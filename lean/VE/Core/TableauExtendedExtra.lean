import VE.Core.TableauExtendedRules
import VE.Core.PathRules

namespace VE.Core.Tableau

theorem rule_closure_formula (a : Signed) (k : Kind) (e : Edge) (t r : Term)
    (hr : a.rule = .closure k e t r) : a.formula = Formula.reach k e t r := by
  cases a with
  | mk f p bs => cases f <;> cases p <;> simp_all [Signed.rule, Formula.reach] <;> grind

def edgeStep (E : Environment) (a : Signed) : Option Signed :=
  match a.formula, a.positive with
  | .binary p t r, true =>
    match E.predicates p with
    | some [s,q] => if s = q then some ⟨.reachNamed .plus p t r,true,a.bindings⟩ else none
    | _ => none
  | _, _ => none

theorem edgeStep_sound (E : Environment) (S : Structure) (ρ : Assignment S) (a x : Signed)
    (ha : a.Holds S ρ) (hx : edgeStep E a = some x) : x.Holds S ρ := by
  cases a with
  | mk f p bs =>
    cases f <;> cases p <;> simp only [edgeStep, reduceCtorEq] at hx
    all_goals try contradiction
    split at hx <;> try contradiction
    split at hx <;> try contradiction
    cases hx
    exact edge_inclusion S _ _ _ _ ha

def composeStep (a d : Signed) : Option Signed :=
  match a.rule, d.rule with
  | .closure k e t r, .closure l f u v =>
    if a.positive && d.positive && decide (a.bindings = d.bindings ∧ e = f ∧ r = u) then
      some ⟨.reach (composeKind k l) e t v,true,a.bindings⟩ else none
  | _, _ => none

theorem composeStep_sound (S : Structure) (ρ : Assignment S) (a d x : Signed)
    (ha : a.Holds S ρ) (hd : d.Holds S ρ) (hx : composeStep a d = some x) : x.Holds S ρ := by
  cases hr : a.rule <;> cases hs : d.rule <;> simp only [composeStep,hr,hs] at hx
  all_goals try contradiction
  split at hx <;> try contradiction
  rename_i k e t r l f u v h
  have h' : (a.positive = true ∧ d.positive = true) ∧
      (a.bindings = d.bindings ∧ e = f ∧ r = u) := by simpa using h
  obtain ⟨⟨hp,hq⟩,⟨hb,rfl,rfl⟩⟩ := h'
  cases hx
  have hae := rule_closure_formula a k e t r hr
  have hde := rule_closure_formula d l e r v hs
  simp only [Signed.Holds, hp, hq, if_true, hae, hde, ← hb] at ha hd ⊢
  exact reach_compose S _ e k l t r v ha hd

def endStep (E : Environment) (b : Branch) (a : Signed) (last : Bool) : Option Signed := do
  match a.rule with
  | .closure .plus e t r =>
    if !a.positive then none else
      let x ← termToken a.bindings t
      let s ← x.sortOf E b
      if edgeCheck E s e then some ⟨endEdge last e s t r,true,a.bindings⟩ else none
  | _ => none

theorem endStep_sound {E : Environment} {S : Structure} (hS : S.Admissible E)
    (b : Branch) (ρ : Assignment S) (a x : Signed) (last : Bool)
    (ha : a.Holds S ρ) (hx : endStep E b a last = some x) : x.Holds S ρ := by
  cases hr : a.rule <;> simp only [endStep,hr] at hx
  all_goals try contradiction
  rename_i k e t r
  cases k <;> simp only at hx
  case star => contradiction
  split at hx <;> try contradiction
  rename_i hp
  have hp : a.positive = true := by simpa using hp
  simp only [bind,Option.bind] at hx
  split at hx <;> try contradiction
  dsimp only at hx
  split at hx <;> try contradiction
  rename_i z hz s hs
  dsimp only at hx
  split at hx <;> try contradiction
  rename_i he
  cases hx
  have het : e.Typed E s := by cases e <;> simpa [edgeCheck, Edge.Typed] using he
  have hae := rule_closure_formula a .plus e t r hr
  simp only [Signed.Holds,hp,if_true,hae] at ha ⊢
  exact endEdge_sound hS _ last e s t r het ha

def namedStep (E : Environment) (a : Signed) : Option Signed := do
  match a.formula with
  | .reachNamed k p t r =>
    match E.predicates p with
    | some [s,q] => if s = q then
        some ⟨.reachBody k s (.binary p (.var 1) (.var 0)) t r,a.positive,a.bindings⟩ else none
    | _ => none
  | _ => none

theorem namedStep_sound {E : Environment} {S : Structure} (hS : S.Admissible E)
    (ρ : Assignment S) (a x : Signed) (ha : a.Holds S ρ)
    (hx : namedStep E a = some x) : x.Holds S ρ := by
  cases a with
  | mk f pos bs =>
    cases f <;> simp only [namedStep] at hx
    all_goals try contradiction
    rename_i k p t r
    split at hx <;> try contradiction
    rename_i s q hp
    split at hx <;> try contradiction
    rename_i he
    subst q
    cases hx
    have he := named_body_denote hS (bindingsValue S ρ bs) k p s t r hp
    simpa only [Signed.Holds, ← he] using ha

def extraRule (rule : String) : Bool :=
  ["closure-edge@0", "closure-compose@0", "closure-first@0", "closure-last@0",
    "closure-named-body@0"].contains rule

def deriveExtra (E : Environment) (b : Branch) (a : Signed) (rule : String)
    (parameter : Option String) : Option Signed :=
  if rule = "closure-compose@0" then do
    let text ← parameter
    let j ← text.toNat?
    let d ← b.formulas[j]?
    composeStep a d
  else if parameter.isSome then none
  else if rule = "closure-edge@0" then edgeStep E a
  else if rule = "closure-first@0" then endStep E b a false
  else if rule = "closure-last@0" then endStep E b a true
  else if rule = "closure-named-body@0" then namedStep E a
  else none

def extra (E : Environment) (b : Branch) (rule : String) (index : Nat)
    (parameter : Option String) : Option (List Branch) := do
  let a ← b.formulas[index]?
  let x ← deriveExtra E b a rule parameter
  some [b.add [x]]

theorem extra_sound {E : Environment} {S : Structure} (hS : S.Admissible E)
    (b : Branch) (ρ : Assignment S) (hρ : Assignment.Typed S b ρ)
    (hh : b.Holds S ρ) (rule : String) (index : Nat) (parameter : Option String)
    (bs : List Branch) (hn : extra E b rule index parameter = some bs) :
    ∃ child ∈ bs, ∃ σ, Assignment.Typed S child σ ∧ child.Holds S σ := by
  cases hi : b.formulas[index]? with
  | none => simp [extra,hi] at hn
  | some a =>
    have ha := hh a (List.mem_of_getElem? hi)
    simp only [extra,hi,bind,Option.bind] at hn
    have hs : ∀ x, (if rule = "closure-compose@0" then do
        let text ← parameter
        let j ← text.toNat?
        let d ← b.formulas[j]?
        composeStep a d
      else if parameter.isSome then none
      else if rule = "closure-edge@0" then edgeStep E a
      else if rule = "closure-first@0" then endStep E b a false
      else if rule = "closure-last@0" then endStep E b a true
      else if rule = "closure-named-body@0" then namedStep E a else none) = some x → x.Holds S ρ := by
      intro x hx
      split at hx
      · cases hp : parameter <;> simp only [hp,bind,Option.bind] at hx
        · contradiction
        · split at hx <;> try contradiction
          dsimp only at hx
          split at hx <;> try contradiction
          rename_i j hj d hd
          dsimp only at hx
          exact composeStep_sound S ρ a d x ha (hh d (List.mem_of_getElem? hd)) hx
      · split at hx <;> try contradiction
        split at hx
        · exact edgeStep_sound E S ρ a x ha hx
        · split at hx
          · exact endStep_sound hS b ρ a x false ha hx
          · split at hx
            · exact endStep_sound hS b ρ a x true ha hx
            · split at hx
              · exact namedStep_sound hS ρ a x ha hx
              · contradiction
    cases hx : deriveExtra E b a rule parameter with
    | none => simp only [hx] at hn; contradiction
    | some x =>
      simp only [hx] at hn
      cases hn
      exact ⟨_,List.mem_cons_self,ρ,hρ,add_holds S ρ b [x] hh (by simpa using hs x hx)⟩

end VE.Core.Tableau
