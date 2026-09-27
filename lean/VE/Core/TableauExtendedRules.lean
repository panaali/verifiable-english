import VE.Core.TableauExtendedClosure
import VE.Core.Congruence

namespace VE.Core.Tableau

def edgeCheck (E : Environment) (s : String) : Edge → Bool
  | .named p => decide (E.predicates p = some [s,s])
  | .body q _ => decide (q = s)

def unfoldAt (E : Environment) (b : Branch) (bs : List Token)
    (k : Kind) (e : Edge) (t r : Term) : Option Formula := do
  let x ← termToken bs t
  let y ← termToken bs r
  let s ← x.sortOf E b
  if y.sortOf E b = some s ∧ edgeCheck E s e = true then some (unfold k e s t r) else none

theorem unfoldAt_sound {E : Environment} {S : Structure} (hS : S.Admissible E)
    (b : Branch) (ρ : Assignment S) (hρ : Assignment.Typed S b ρ)
    (bs : List Token) (hb : ∀ t ∈ bs, ∃ v, t.denote S ρ = some v)
    (k : Kind) (e : Edge) (t r : Term) (f : Formula)
    (hf : unfoldAt E b bs k e t r = some f) :
    f.denote S (bindingsValue S ρ bs) ↔
      (Formula.reach k e t r).denote S (bindingsValue S ρ bs) := by
  simp only [unfoldAt, bind, Option.bind] at hf
  split at hf <;> try contradiction
  rename_i x ht
  dsimp only at hf
  split at hf <;> try contradiction
  rename_i y hr
  dsimp only at hf
  split at hf <;> try contradiction
  rename_i s hs
  dsimp only at hf
  split at hf <;> try contradiction
  rename_i he
  cases hf
  obtain ⟨vx,hx,hdx⟩ := token_defined hS hρ hs
  obtain ⟨vy,hy,hdy⟩ := token_defined hS hρ he.1
  have het : e.Typed E s := by cases e <;> simpa [edgeCheck, Edge.Typed] using he.2
  apply unfold_denote hS _ k e s t r het vx vy
  · exact (termToken_denote S ρ bs hb t x ht).trans hx
  · exact (termToken_denote S ρ bs hb r y hr).trans hy
  · exact hdx
  · exact hdy

theorem known_bindings {E : Environment} {S : Structure} (hS : S.Admissible E)
    (b : Branch) (ρ : Assignment S) (hρ : Assignment.Typed S b ρ)
    (hk : b.known E = true) (a : Signed) (ha : a ∈ b.formulas) :
    ∀ t ∈ a.bindings, ∃ v, t.denote S ρ = some v := by
  intro t ht
  have hi := List.all_eq_true.mp (List.all_eq_true.mp hk a ha) t ht
  cases hs : t.sortOf E b with
  | none => simp [hs] at hi
  | some s => obtain ⟨v,hv,_⟩ := token_defined hS hρ hs; exact ⟨v,hv⟩

theorem closure_holds {E : Environment} {S : Structure} (hS : S.Admissible E)
    (b : Branch) (ρ : Assignment S) (hρ : Assignment.Typed S b ρ)
    (a : Signed) (hb : ∀ t ∈ a.bindings, ∃ v, t.denote S ρ = some v)
    (k : Kind) (e : Edge) (t r : Term) (f : Formula)
    (hr : a.rule = .closure k e t r) (ha : a.Holds S ρ)
    (hf : unfoldAt E b a.bindings k e t r = some f) :
    (Signed.mk f a.positive a.bindings).Holds S ρ := by
  have he := unfoldAt_sound hS b ρ hρ a.bindings hb k e t r f hf
  have hae : a.formula = Formula.reach k e t r := by
    cases a with
    | mk f p bs => cases f <;> cases p <;> simp_all [Signed.rule, Formula.reach] <;> grind
  simpa only [Signed.Holds, he, ← hae] using ha

def groundMatch (edges : List (Token × Token)) (bs cs : List Token) (t r : Term) : Bool :=
  match termToken bs t, termToken cs r with
  | some x, some y => equivalent edges x y
  | _, _ => false

def isReach : Formula → Bool
  | .reachNamed .. | .reachBody .. => true
  | _ => false

def reachClosed (b : Branch) : Bool :=
  let edges := equalities (literals b)
  b.formulas.any fun p => p.positive && isReach p.formula && b.formulas.any fun n =>
    !n.positive && p.formula.matches (groundMatch edges p.bindings n.bindings) n.formula

theorem reachClosed_sound {E : Environment} {S : Structure} (hS : S.Admissible E)
    (b : Branch) (ρ : Assignment S) (hρ : Assignment.Typed S b ρ)
    (hk : b.known E = true) (hh : b.Holds S ρ) (hc : reachClosed b = true) : False := by
  obtain ⟨p,hp,hc⟩ := List.any_eq_true.mp hc
  obtain ⟨hp',hc⟩ := Bool.and_eq_true_iff.mp hc
  obtain ⟨n,hn,hc⟩ := List.any_eq_true.mp hc
  obtain ⟨hn',hm⟩ := Bool.and_eq_true_iff.mp hc
  have hpos := (Bool.and_eq_true_iff.mp hp').1
  have hneg : n.positive = false := by cases he : n.positive <;> simp_all
  have he := formula_matches_sound S p.formula n.formula
    (bindingsValue S ρ p.bindings) (bindingsValue S ρ n.bindings) _ (by
      intro t r htr
      cases ht : termToken p.bindings t <;> cases hr : termToken n.bindings r <;>
        simp only [groundMatch, ht, hr] at htr
      all_goals try contradiction
      rw [termToken_denote S ρ p.bindings (known_bindings hS b ρ hρ hk p hp) _ _ ht,
        termToken_denote S ρ n.bindings (known_bindings hS b ρ hρ hk n hn) _ _ hr]
      exact equivalent_sound S ρ (literals b) (literals_hold hS b ρ hρ hk hh) _ _ htr) hm
  have hph := hh p hp
  have hnh := hh n hn
  simp only [Signed.Holds, hpos, hneg, if_true, Bool.false_eq_true, if_false] at hph hnh
  exact hnh (he.mp hph)

end VE.Core.Tableau
