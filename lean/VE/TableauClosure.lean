import VE.Tableau

namespace VE.Tableau
universe u

inductive Atom where
  | top | bottom
  | unary (predicate : String) (term : Token)
  | binary (predicate : String) (left right : Token)
  | eq (left right : Token)
  deriving DecidableEq, Repr

structure Literal where
  atom : Atom
  positive : Bool
  deriving Repr

def termToken (bs : List Token) : Term → Option Token
  | .const c => some (.constant c)
  | .var i => bs[i]?

def ground (bs : List Token) : Formula → Option Atom
  | .top => some .top
  | .bottom => some .bottom
  | .unary p t => return .unary p (← termToken bs t)
  | .binary p t r => return .binary p (← termToken bs t) (← termToken bs r)
  | .eq t r => return .eq (← termToken bs t) (← termToken bs r)
  | _ => none

def Atom.denote (S : Structure) (ρ : Assignment S) : Atom → Prop
  | .top => True
  | .bottom => False
  | .unary p t => ∃ v, t.denote S ρ = some v ∧ S.relation p [v]
  | .binary p t r => ∃ v w, t.denote S ρ = some v ∧
      r.denote S ρ = some w ∧ S.relation p [v, w]
  | .eq t r => ∃ v, t.denote S ρ = some v ∧ r.denote S ρ = some v

def Literal.Holds (S : Structure) (ρ : Assignment S) (l : Literal) : Prop :=
  if l.positive then l.atom.denote S ρ else ¬ l.atom.denote S ρ

def Branch.known (E : Environment) (b : Branch) : Bool :=
  b.formulas.all fun a => a.bindings.all fun t => (t.sortOf E b).isSome

def literals (b : Branch) : List Literal :=
  b.formulas.filterMap fun a => (ground a.bindings a.formula).map (⟨·, a.positive⟩)

theorem bindings_get (S : Structure) (ρ : Assignment S) (bs : List Token)
    (hb : ∀ t ∈ bs, ∃ v, t.denote S ρ = some v) (i : Nat) :
    (bindingsValue S ρ bs)[i]? = (bs[i]?).bind (Token.denote S ρ) := by
  induction bs generalizing i with
  | nil => simp [bindingsValue]
  | cons t ts ih =>
    obtain ⟨v, hv⟩ := hb t (by simp)
    have hh := ih (fun t ht => hb t (by simp [ht]))
    cases i with
    | zero => simp [bindingsValue, hv]
    | succ i => simpa [bindingsValue, hv] using hh i

theorem termToken_denote (S : Structure) (ρ : Assignment S) (bs : List Token)
    (hb : ∀ t ∈ bs, ∃ v, t.denote S ρ = some v) (t : Term) (x : Token)
    (ht : termToken bs t = some x) :
    t.denote S (bindingsValue S ρ bs) = x.denote S ρ := by
  cases t with
  | const c => cases ht; rfl
  | var i =>
    rw [Term.denote, bindings_get S ρ bs hb, show bs[i]? = some x from ht]
    rfl

theorem ground_denote (S : Structure) (ρ : Assignment S) (bs : List Token)
    (hb : ∀ t ∈ bs, ∃ v, t.denote S ρ = some v) (f : Formula) (a : Atom)
    (hg : ground bs f = some a) :
    f.denote S (bindingsValue S ρ bs) ↔ a.denote S ρ := by
  cases f <;> simp only [ground, reduceCtorEq] at hg
  all_goals first | cases hg; rfl | skip
  all_goals
    simp only [bind, Option.bind, Option.pure_def] at hg
    split at hg <;> try contradiction
    rename_i ht
    first
    | cases hg; simp only [Formula.denote, Atom.denote, termToken_denote S ρ bs hb _ _ ht]
    | skip
  all_goals
    dsimp only at hg
    split at hg <;> try contradiction
    rename_i hu
    cases hg
    simp only [Formula.denote, Atom.denote,
      termToken_denote S ρ bs hb _ _ ht, termToken_denote S ρ bs hb _ _ hu]

theorem literals_hold {E : Environment} {S : Structure} (hS : S.Admissible E)
    (b : Branch) (ρ : Assignment S) (hρ : Assignment.Typed S b ρ)
    (hk : b.known E = true) (hh : b.Holds S ρ) :
    ∀ l ∈ literals b, l.Holds S ρ := by
  intro l hl
  obtain ⟨a, ha, hg⟩ := List.mem_filterMap.mp hl
  obtain ⟨atom, hground, he⟩ := Option.map_eq_some_iff.mp hg
  subst l
  have hb : ∀ t ∈ a.bindings, ∃ v, t.denote S ρ = some v := by
    intro t ht
    have hi := List.all_eq_true.mp (List.all_eq_true.mp hk a ha) t ht
    cases hs : t.sortOf E b with
    | none => simp [hs] at hi
    | some s =>
      obtain ⟨v, hv, _⟩ := token_defined hS hρ hs
      exact ⟨v, hv⟩
  have hd := ground_denote S ρ a.bindings hb a.formula atom hground
  simpa only [Literal.Holds, Signed.Holds, hd] using hh a ha

/-- Positive equalities are undirected edges. Reachability computes their
reflexive, symmetric, transitive closure, with at most one round per edge. -/
def equalities (ls : List Literal) : List (Token × Token) :=
  ls.filterMap fun l => match l.atom, l.positive with
    | .eq t r, true => some (t, r)
    | _, _ => none

def dedup : List Token → List Token
  | [] => []
  | t :: ts => let rest := dedup ts; if t ∈ rest then rest else t :: rest

theorem mem_dedup (t : Token) (ts : List Token) : t ∈ dedup ts ↔ t ∈ ts := by
  induction ts generalizing t with
  | nil => simp [dedup]
  | cons a ts ih =>
    simp only [dedup]
    split <;> simp_all

def grow (edges : List (Token × Token)) (seen : List Token) : List Token :=
  dedup (seen ++ edges.flatMap (fun (a, b) =>
    (if a ∈ seen then [b] else []) ++ (if b ∈ seen then [a] else [])))

def reachable (edges : List (Token × Token)) : Nat → List Token → List Token
  | 0, seen => seen
  | n + 1, seen => reachable edges n (grow edges seen)

def equivalent (edges : List (Token × Token)) (a b : Token) : Bool :=
  decide (b ∈ reachable edges edges.length [a])

theorem equalities_sound (S : Structure) (ρ : Assignment S) (ls : List Literal)
    (hh : ∀ l ∈ ls, l.Holds S ρ) :
    ∀ e ∈ equalities ls, e.1.denote S ρ = e.2.denote S ρ := by
  intro e he
  obtain ⟨l, hl, he⟩ := List.mem_filterMap.mp he
  have hh := hh l hl
  rcases l with ⟨a, p⟩
  cases a <;> cases p <;> simp only [reduceCtorEq] at he
  all_goals try contradiction
  cases he
  obtain ⟨v, ht, hr⟩ := hh
  exact ht.trans hr.symm

theorem grow_sound {α : Type u} (value : Token → α) (edges : List (Token × Token))
    (he : ∀ e ∈ edges, value e.1 = value e.2) (seen : List Token) (v : α)
    (hs : ∀ t ∈ seen, value t = v) : ∀ t ∈ grow edges seen, value t = v := by
  intro t ht
  simp only [grow, mem_dedup, List.mem_append, List.mem_flatMap] at ht
  rcases ht with ht | ⟨⟨a,b⟩, hm, ht⟩
  · exact hs t ht
  · have hab := he (a,b) hm
    rcases ht with ht | ht
    · split at ht <;> simp_all
    · split at ht <;> simp_all

theorem reachable_sound {α : Type u} (value : Token → α) (edges : List (Token × Token))
    (he : ∀ e ∈ edges, value e.1 = value e.2) (n : Nat) (seen : List Token) (v : α)
    (hs : ∀ t ∈ seen, value t = v) :
    ∀ t ∈ reachable edges n seen, value t = v := by
  induction n generalizing seen with
  | zero => exact hs
  | succ n ih => exact ih (grow edges seen) (grow_sound value edges he seen v hs)

theorem equivalent_sound (S : Structure) (ρ : Assignment S) (ls : List Literal)
    (hh : ∀ l ∈ ls, l.Holds S ρ) (a b : Token)
    (he : equivalent (equalities ls) a b = true) : a.denote S ρ = b.denote S ρ := by
  have hm : b ∈ reachable (equalities ls) (equalities ls).length [a] := of_decide_eq_true he
  exact (reachable_sound (Token.denote S ρ) (equalities ls)
    (equalities_sound S ρ ls hh) _ [a] (a.denote S ρ) (by simp) b hm).symm

/-- Congruence on unary/binary relation atoms uses equality of denotations;
there are no function symbols in VE. -/
def atomMatches (edges : List (Token × Token)) : Atom → Atom → Bool
  | .unary p t, .unary q r => decide (p = q) && equivalent edges t r
  | .binary p t u, .binary q r s =>
      decide (p = q) && equivalent edges t r && equivalent edges u s
  | _, _ => false

theorem matches_sound (S : Structure) (ρ : Assignment S) (ls : List Literal)
    (hh : ∀ l ∈ ls, l.Holds S ρ) (a b : Atom)
    (hm : atomMatches (equalities ls) a b = true) : a.denote S ρ ↔ b.denote S ρ := by
  cases a <;> cases b <;> simp only [atomMatches, Bool.and_eq_true, decide_eq_true_eq] at hm
  all_goals try contradiction
  case unary.unary p t q r =>
    obtain ⟨rfl, ht⟩ := hm
    simp only [Atom.denote, equivalent_sound S ρ ls hh t r ht]
  case binary.binary p t u q r s =>
    obtain ⟨⟨rfl, ht⟩, hu⟩ := hm
    simp only [Atom.denote, equivalent_sound S ρ ls hh t r ht,
      equivalent_sound S ρ ls hh u s hu]

def closes (E : Environment) (b : Branch) (ls : List Literal) (l : Literal) : Bool :=
  let edges := equalities ls
  match l.atom, l.positive with
  | .bottom, true | .top, false => true
  | .eq t r, false => (t.sortOf E b).isSome && equivalent edges t r
  | a, false => ls.any fun p => p.positive && atomMatches edges p.atom a
  | _, _ => false

def closed (E : Environment) (b : Branch) : Bool :=
  let ls := literals b
  ls.any (closes E b ls)

theorem closes_sound {E : Environment} {S : Structure} (hS : S.Admissible E)
    (b : Branch) (ρ : Assignment S) (hρ : Assignment.Typed S b ρ)
    (ls : List Literal) (hh : ∀ l ∈ ls, l.Holds S ρ) (l : Literal)
    (hl : l.Holds S ρ) (hc : closes E b ls l = true) : False := by
  rcases l with ⟨a,p⟩
  cases a <;> cases p <;> simp only [closes, Bool.and_eq_true] at hc
  all_goals try contradiction
  all_goals try (exact hl)
  all_goals try (exact hl trivial)
  case eq.false t r =>
    obtain ⟨hk, he⟩ := hc
    cases ht : t.sortOf E b with
    | none => simp [ht] at hk
    | some s =>
      obtain ⟨v, hv, _⟩ := token_defined hS hρ ht
      exact hl ⟨v, hv, (equivalent_sound S ρ ls hh t r he).symm.trans hv⟩
  all_goals
    obtain ⟨l, hm, hp⟩ := List.any_eq_true.mp hc
    obtain ⟨hp, he⟩ := Bool.and_eq_true_iff.mp hp
    have hh := hh l hm
    simp only [Literal.Holds, hp, if_true] at hh
    exact hl ((matches_sound S ρ ls (by assumption) _ _ he).mp hh)

theorem closed_sound {E : Environment} {S : Structure} (hS : S.Admissible E)
    (b : Branch) (ρ : Assignment S) (hρ : Assignment.Typed S b ρ)
    (hk : b.known E = true) (hh : b.Holds S ρ) (hc : closed E b = true) : False := by
  have hl := literals_hold hS b ρ hρ hk hh
  obtain ⟨l, hm, hc⟩ := List.any_eq_true.mp hc
  exact closes_sound hS b ρ hρ (literals b) hl l (hl l hm) hc

end VE.Tableau
