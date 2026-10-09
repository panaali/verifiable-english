import VE.NormDefaults.Report
import VE.NormDefaults.Semantics

/-! What the English of a CONFLICT witness, a status and a reached default needs, decided
here so that Python only formats Lean's answer (docs/spec/norm-defaults.md 3.1, 3.2, 4.2 and 8).

* **Conflict kind** (3.1): a CONFLICT witness is `settled` when the target is Kleene-true
  with no unsaid atom known (true under every filling, `settled_every_filling`), else
  `latent`.
* **Deciding assignment** (`under`, 4.2's "contradict each other if …"): the unsaid atoms of
  the witness, with their values, under which the target is Kleene-true whatever the other
  unsaid atoms are (`underOf_sufficient`). The atoms come from one evaluation that records the
  atoms supporting its value (`supportEval`, untrusted), shrunk one atom at a time while the
  Kleene check still passes; the result is used only when that check passes. The work is
  polynomial in the situation: no assignment is enumerated.
* **Deciding rules**: the author rules on a predicate whose selection formula on `fill U`,
  expanded to the base, is true at the tuple of a filled model (`selectedRules_sound`).
* **Completed value** of a reached default (3.2): no author rule decides there, so the
  value is the completion's (`value3_gap`). -/
namespace VE.NormDefaults.Wire
open Lean
open VE.Norms VE.Route
open VE.Bridge (Entity)

/-! ## Kleene evaluation with some unsaid atoms known -/

/-- An atom's value when the unsaid atoms `K` are read from `M` and the other unsaid
atoms are unknown; a base atom is `M`'s. -/
def keptV (U : UDoc) (M : VE.FiniteModel Entity) (K : List (String × List Entity)) (p : String)
    (vs : List Entity) : Option Bool :=
  if p ∈ unsaidNames U then (if (p, vs) ∈ K then some (decide (vs ∈ M.relations p)) else none)
  else some (decide (vs ∈ M.relations p))

/-- A Kleene-true formula with the atoms `K` known is true in every structure over `M` that
agrees with `M` on `K` and on every base atom. -/
theorem kept_sound (U : UDoc) (M : VE.FiniteModel Entity) (K : List (String × List Entity))
    (R : String → List Entity → Prop) (hK : ∀ a ∈ K, (R a.1 a.2 ↔ a.2 ∈ M.relations a.1))
    (hbase : ∀ p vs, p ∉ unsaidNames U → (R p vs ↔ vs ∈ M.relations p)) (φ : VE.Formula)
    (ρ : List Entity) (h : kleene M (keptV U M K) ρ φ = some true) :
    φ.denote { M.asStructure with relation := R } ρ := by
  have hs := kleene_sound M (keptV U M K) R (fun p vs b hb => by
    unfold keptV at hb
    split at hb
    · split at hb
      · rename_i hmem
        simp only [Option.some.injEq] at hb
        subst hb
        rw [hK (p, vs) hmem]
        simp
      · cases hb
    · rename_i hp
      simp only [Option.some.injEq] at hb
      subst hb
      rw [hbase p vs hp]
      simp) φ ρ true h
  exact hs.mpr rfl

/-! ## The conflict kind -/

/-- `settled` (3.1): the target is Kleene-true with no unsaid atom known. -/
def settledConflict (U : UDoc) (M : VE.FiniteModel Entity) (ρ : List Entity) (φ : VE.Formula) : Bool :=
  kleene M (keptV U M []) ρ φ == some true

/-- `settled_every_filling`: a settled target is true whatever the unsaid tables are. -/
theorem settled_every_filling (U : UDoc) (M : VE.FiniteModel Entity) (ρ : List Entity) (φ : VE.Formula)
    (h : settledConflict U M ρ φ = true) (R : String → List Entity → Prop)
    (hbase : ∀ p vs, p ∉ unsaidNames U → (R p vs ↔ vs ∈ M.relations p)) :
    φ.denote { M.asStructure with relation := R } ρ :=
  kept_sound U M [] R (fun _ h => by cases h) hbase φ ρ (by simpa [settledConflict] using h)

/-! ## The deciding assignment -/

def supportAtom (U : UDoc) (M : VE.FiniteModel Entity) (p : String) (vs : List Entity) :
    Bool × List (String × List Entity) :=
  (decide (vs ∈ M.relations p), if p ∈ unsaidNames U then [(p, vs)] else [])

/-- A binary junction: `stop` is the value that decides it (true for `or`). -/
def supportJoin {β : Type} (stop : Bool) (x y : Bool × List β) : Bool × List β :=
  if x.1 == stop then (stop, x.2) else if y.1 == stop then (stop, y.2) else (!stop, x.2 ++ y.2)

/-- A finite quantifier: `stop` is the value that decides it (true for `ex`). -/
def supportList {β : Type} (stop : Bool) (l : List (Bool × List β)) : Bool × List β :=
  match l.find? (·.1 == stop) with
  | some x => (stop, x.2)
  | none => (!stop, l.flatMap (·.2))

/-- The value of a formula in `M` with the unsaid atoms it was read from: one deciding
operand of a decided junction or quantifier, every operand otherwise. Untrusted:
`underOf` keeps the atoms only when the Kleene check passes. -/
def supportEval (U : UDoc) (M : VE.FiniteModel Entity) (ρ : List Entity) :
    VE.Formula → Bool × List (String × List Entity)
  | .top => (true, [])
  | .bottom => (false, [])
  | .unary p t => match t.denote M.asStructure ρ with
      | some v => supportAtom U M p [v]
      | none => (false, [])
  | .binary p t w => match t.denote M.asStructure ρ, w.denote M.asStructure ρ with
      | some v, some v' => supportAtom U M p [v, v']
      | _, _ => (false, [])
  | .eq t w => match t.denote M.asStructure ρ, w.denote M.asStructure ρ with
      | some v, some v' => (@decide (v = v') (instDecidableEqProd v v'), [])
      | _, _ => (false, [])
  | .not a => let x := supportEval U M ρ a; (!x.1, x.2)
  | .and a b => supportJoin false (supportEval U M ρ a) (supportEval U M ρ b)
  | .or a b => supportJoin true (supportEval U M ρ a) (supportEval U M ρ b)
  | .implies a b => let x := supportEval U M ρ a; supportJoin true (!x.1, x.2) (supportEval U M ρ b)
  | .all s a => supportList false ((M.domains s).map (fun v => supportEval U M (v :: ρ) a))
  | .ex s a => supportList true ((M.domains s).map (fun v => supportEval U M (v :: ρ) a))

/-- Drop each atom in turn while `ok` still holds without it. -/
def shrink {β : Type} (ok : List β → Bool) : List β → List β → List β
  | kept, [] => kept
  | kept, a :: rest => if ok (kept ++ rest) then shrink ok kept rest else shrink ok (kept ++ [a]) rest

/-- The deciding assignment of a true target: the supporting unsaid atoms, in Python's atom
order, shrunk while the target stays Kleene-true; `none` if the check fails. -/
def underOf (U : UDoc) (M : VE.FiniteModel Entity) (ρ : List Entity) (φ : VE.Formula) :
    Option (List (String × List Entity)) :=
  let ok := fun K => kleene M (keptV U M K) ρ φ == some true
  let K := shrink ok [] (sortAtoms (supportEval U M ρ φ).2.eraseDups)
  if ok K then some K else none

/-- `underOf_sufficient`: the target is true in every structure over `M` that agrees with `M`
on the deciding assignment and on every base atom, whatever the other unsaid atoms are. -/
theorem underOf_sufficient (U : UDoc) (M : VE.FiniteModel Entity) (ρ : List Entity) (φ : VE.Formula)
    (K : List (String × List Entity)) (h : underOf U M ρ φ = some K) (R : String → List Entity → Prop)
    (hK : ∀ a ∈ K, (R a.1 a.2 ↔ a.2 ∈ M.relations a.1))
    (hbase : ∀ p vs, p ∉ unsaidNames U → (R p vs ↔ vs ∈ M.relations p)) :
    φ.denote { M.asStructure with relation := R } ρ := by
  unfold underOf at h
  simp only at h
  split at h
  · rename_i hok
    simp only [Option.some.injEq] at h
    subst h
    exact kept_sound U M _ R hK hbase φ ρ (by simpa using hok)
  · cases h

/-- The regulated predicate of an unsaid name. -/
def unsaidPredicate (U : UDoc) (n : String) : String :=
  (U.unspec.find? (fun p => unsaidName p == n)).getD n

/-- The deciding assignment as rows: predicate, tuple ids and the witness's answer. -/
def underJson (U : UDoc) (M : VE.FiniteModel Entity) (K : List (String × List Entity)) : Json :=
  Json.arr (K.map (fun a => Json.mkObj [("predicate", .str (unsaidPredicate U a.1)),
    ("tuple", toJson (a.2.map (·.2))), ("value", .bool (decide (a.2 ∈ M.relations a.1)))])).toArray

/-! ## The deciding rules -/

/-- "Author rule `N` decides" on `fill U`, expanded to the base (Python's `selection`). -/
def selectionBase (U : UDoc) (N : Node) : VE.Formula :=
  subst (fill U).T (before (fill U) N.pred) (selects (fill U).T (fuel (fill U).T) N)

/-- The author rules on `p`, in rule order, that decide at `ρ` in the filled model `M`. -/
def selectedRules (U : UDoc) (M : VE.FiniteModel Entity) (ρ : List Entity) (p : String) : List String :=
  ((U.D.T.nodes.map (fillRoot U)).filter (fun N => N.pred == p && (selectionBase U N).eval M ρ)).map (·.name)

theorem selectedRules_sound (U : UDoc) (M : VE.FiniteModel Entity) (ρ : List Entity) (p n : String)
    (h : n ∈ selectedRules U M ρ p) :
    ∃ N ∈ U.D.T.nodes.map (fillRoot U), N.name = n ∧ N.pred = p ∧
      (selectionBase U N).denote M.asStructure ρ := by
  unfold selectedRules at h
  obtain ⟨N, hm, rfl⟩ := List.mem_map.mp h
  obtain ⟨hN, hf⟩ := List.mem_filter.mp hm
  simp only [Bool.and_eq_true, beq_iff_eq] at hf
  obtain ⟨hp, he⟩ := hf
  exact ⟨N, hN, rfl, hp, (VE.eval_iff_denote M ρ _).mp he⟩

/-- The other members of `p`'s declared pairs. -/
def pairPartners (U : UDoc) (p : String) : List String :=
  (pairs U.D.T).filterMap (fun pr => if pr.req == p then some pr.perm else if pr.perm == p then some pr.req
    else none)

/-! ## The fields of a CONFLICT witness -/

/-- The kind, the deciding assignment (empty when settled; empty and refused by the renderer
when the check fails) and the rules of the target's predicates that decide at the tuple. -/
def conflictFields (U : UDoc) (M : VE.FiniteModel Entity) (target : String) (φ : VE.Formula)
    (tuple : List Entity) : List (String × Json) :=
  let ρ := tupleVal tuple
  let settled := settledConflict U M ρ φ
  [("tuple", toJson (tuple.map (·.2))),
   ("kind", .str (if settled then "settled" else "latent")),
   ("under", underJson U M (if settled then [] else (underOf U M ρ φ).getD [])),
   ("rules", toJson ((target.splitOn "->").flatMap (selectedRules U M ρ)))]

/-! ## The fields of a status -/

/-- The unsaid atoms on which two fillings differ, in Python's atom order. -/
def fillingsDiffer (U : UDoc) (F₁ F₂ : FiniteFill U Entity) : List (String × List Entity) :=
  sortAtoms (U.unspec.flatMap (fun p =>
    let n := unsaidName p
    ((F₁ n).filter (fun r => r ∉ F₂ n) ++ (F₂ n).filter (fun r => r ∉ F₁ n)).map (fun r => (p, r))))

def atomsJson (A : List (String × List Entity)) : Json :=
  Json.arr (A.map (fun a => Json.mkObj [("predicate", .str a.1), ("tuple", toJson (a.2.map (·.2)))])).toArray

/-- The deciding rules of a status: on a SETTLED point, the rules on `p` and on its pair
partners that decide under the canonical filling; on an UNDECIDED point, the rules on `p`
that decide under either supplied filling, and the atoms where the fillings differ. -/
def statusFields (U : UDoc) (M : VE.FiniteModel Entity) (p : String) (tuple : List Entity)
    (settled : Bool) (fillings : Option (FiniteFill U Entity × FiniteFill U Entity)) : List (String × Json) :=
  let ρ := tupleVal tuple
  let rules := match fillings with
    | some (F₁, F₂) => (selectedRules U (M.withFill F₁) ρ p ++ selectedRules U (M.withFill F₂) ρ p).eraseDups
    | none => if settled then (p :: pairPartners U p).flatMap (selectedRules U (M.withFill (canonicalFinite U M)) ρ)
      else []
  let differs := match fillings with
    | some (F₁, F₂) => fillingsDiffer U F₁ F₂
    | none => []
  [("tuple", toJson (tuple.map (·.2))), ("rules", toJson rules), ("differs", atomsJson differs)]

/-! ## The completed value of a reached default -/

def outcomeLabel : Outcome3 → String
  | .yes => "yes"
  | .no => "no"
  | .unsaid => "unsaid"
  | .conflict => "conflict"

/-- `value3_gap`: where no author rule decides, the value is the completion's (the `value`
of a reachable report line, `completedLabel`). -/
theorem value3_gap (P N : Prop) (c : Completion) (hP : ¬ P) (hN : ¬ N) :
    outcomeLabel (value3 P N c) = completedLabel c := by
  classical
  unfold value3
  cases c <;> simp [hP, hN, outcomeLabel, completedLabel]

end VE.NormDefaults.Wire
