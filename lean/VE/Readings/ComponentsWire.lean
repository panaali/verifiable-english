import VE.Readings.Components
import VE.Readings.VerdictsWire
import VE.Readings.Companions

/-! `readings-verdicts` over a document's components (docs/spec/readings-defaults.md 1.9, 1.10, 2.4, 3, 4.5, 5 rows
16 to 18; plan RD-4b).

A document with companion sets is split (`Wire.splitCase`); asked `readings-verdicts` without naming a `component`,
Lean answers for the document: each case is replayed by itself under the completion as RD-3 replays a case
(`replayND`, its own question, its own evidence, `component`-tagged in the request), and the product fold
(`productConflict`, `productPremises`, `productQuery`) reads the cases' rows. A query is typed in exactly one case
(`--sentence` picks it when the terms fit several), `--under` names sets of that case only, and every other case is
asked the premises question, whose rows carry its conflict and premise rows.

What each answer says is `Components.lean`'s: `readings_wire_product_conflict_free`, `..._conflict`, `..._model`,
`..._all`, `..._none` and `..._some` read a replay (`ProductReplay`) as `foldK_*` and `foldK_*_under` do. The answer's
`decided_units` are 1.10's rule (`partDecided`: `fixedDecided`, `setDecided` on the case's own rows).

The main case is checked under the completion like the companion cases. When it has no content-bearing set, its
checked part is its fixed units (`fixedPart`): the sets left on W2 carry no content, add nothing to any choice's
document and stay visible, unchecked, with W2's UNKNOWN (`unchecked`); a main case with a pending reading, or a case
outside the completion, is refused (`productProfileText`, `productPendingText`). -/

namespace VE.Readings
open VE.NormDefaults (EntailsU)
universe u

/-! ## The product fold over the cases' rows (4.5) -/

/-- Every case other than `k` is CONFLICT-FREE. -/
def othersFree (rows : List ComponentRows) (k : Nat) : Bool :=
  rows.zipIdx.all (fun x => x.2 == k || foldConflict x.1.conflicts == .free)
/-- Every case other than `k` has a model under every compatible choice. -/
def othersEvery (rows : List ComponentRows) (k : Nat) : Bool :=
  rows.zipIdx.all (fun x => x.2 == k || x.1.premises.all (·.2 == .model))
/-- Every case other than `k` has a model under some compatible choice. -/
def othersSome (rows : List ComponentRows) (k : Nat) : Bool :=
  rows.zipIdx.all (fun x => x.2 == k || foldPremises x.1.premises == .model)

def productConflict (rows : List ComponentRows) : ChoiceResult :=
  if rows.all (fun r => foldConflict r.conflicts == .free) then .free
  else if rows.any (fun r => foldConflict r.conflicts == .conflict) then .conflict else .unknown
def productPremises (rows : List ComponentRows) : ChoiceResult :=
  if rows.all (fun r => foldPremises r.premises == .model) then .model else .unknown
/-- A query typed in case `k` (`cs`, `r`: its conflict rows and query rows): its own fold, gated on every other case
    being CONFLICT-FREE; NONE needs every other case's model under every choice, SOME under some choice. -/
def productQuery (rows : List ComponentRows) (k : Nat) (cs r : List (Choice × ChoiceResult)) : ReadingVerdict :=
  if !othersFree rows k then .unknown
  else match foldEntailment cs r with
    | .all => .all
    | .none => if othersEvery rows k then .none else .unknown
    | .some => if othersSome rows k then .some else .unknown
    | .unknown => .unknown

/-- What the document's UNKNOWN names when another case is not CONFLICT-FREE (4.5): CONFLICT when some other case's
    fold is CONFLICT, else UNKNOWN; the first other case (in `Components.all`'s order) with that status, and its first
    choice with it, as `reasonOf` names a choice. -/
def othersReason (rows : List ComponentRows) (k : Nat) : Option (ChoiceResult × Nat × Choice) :=
  let others := rows.zipIdx.filter (fun x => x.2 != k)
  let pick := fun (s : ChoiceResult) => others.findSome? (fun x =>
    if foldConflict x.1.conflicts == s then
      (x.1.conflicts.find? (fun y => if s == .conflict then y.2 == .conflict else y.2 != .free)).map
        (fun y => (s, x.2, y.1))
    else none)
  match pick .conflict with
  | some x => some x
  | none => pick .unknown

theorem othersFree_spec {rows : List ComponentRows} {k : Nat} (h : othersFree rows k = true) :
    ∀ (j : Nat) (r : ComponentRows), j ≠ k → rows[j]? = some r → foldConflict r.conflicts = .free := by
  intro j r hj hr
  have hm : (r, j) ∈ rows.zipIdx := List.mem_zipIdx_iff_getElem?.mpr hr
  have := List.all_eq_true.mp h _ hm
  simp only [Bool.or_eq_true, beq_iff_eq] at this
  exact this.resolve_left hj

theorem othersSettled_every {rows : List ComponentRows} {k : Nat} (h1 : othersFree rows k = true)
    (h2 : othersEvery rows k = true) : OthersSettled rows k true := by
  intro j r hj hr
  refine ⟨othersFree_spec h1 j r hj hr, ?_⟩
  have hm : (r, j) ∈ rows.zipIdx := List.mem_zipIdx_iff_getElem?.mpr hr
  have := List.all_eq_true.mp h2 _ hm
  simp only [Bool.or_eq_true, beq_iff_eq] at this
  simpa using this.resolve_left hj

theorem othersSettled_some {rows : List ComponentRows} {k : Nat} (h1 : othersFree rows k = true)
    (h2 : othersSome rows k = true) : OthersSettled rows k false := by
  intro j r hj hr
  refine ⟨othersFree_spec h1 j r hj hr, ?_⟩
  have hm : (r, j) ∈ rows.zipIdx := List.mem_zipIdx_iff_getElem?.mpr hr
  have := List.all_eq_true.mp h2 _ hm
  simp only [Bool.or_eq_true, beq_iff_eq] at this
  simpa using this.resolve_left hj

theorem productQuery_all {rows : List ComponentRows} {k : Nat} {cs r : List (Choice × ChoiceResult)}
    (h : productQuery rows k cs r = .all) : othersFree rows k = true ∧ foldEntailment cs r = .all := by
  unfold productQuery at h
  by_cases hf : othersFree rows k = true
  · simp only [hf, Bool.not_true, Bool.false_eq_true, if_false] at h
    refine ⟨hf, ?_⟩
    split at h <;> (try split at h) <;> first | assumption | cases h
  · simp only [hf, Bool.not_false, if_true] at h
    cases h

theorem productQuery_none {rows : List ComponentRows} {k : Nat} {cs r : List (Choice × ChoiceResult)}
    (h : productQuery rows k cs r = .none) :
    othersFree rows k = true ∧ othersEvery rows k = true ∧ foldEntailment cs r = .none := by
  unfold productQuery at h
  by_cases hf : othersFree rows k = true
  · simp only [hf, Bool.not_true, Bool.false_eq_true, if_false] at h
    split at h
    · cases h
    · rename_i he
      split at h
      · rename_i hv
        exact ⟨hf, hv, he⟩
      · cases h
    · split at h <;> cases h
    · cases h
  · simp only [hf, Bool.not_false, if_true] at h
    cases h

theorem productQuery_some {rows : List ComponentRows} {k : Nat} {cs r : List (Choice × ChoiceResult)}
    (h : productQuery rows k cs r = .some) :
    othersFree rows k = true ∧ othersSome rows k = true ∧ foldEntailment cs r = .some := by
  unfold productQuery at h
  by_cases hf : othersFree rows k = true
  · simp only [hf, Bool.not_true, Bool.false_eq_true, if_false] at h
    split at h
    · cases h
    · split at h <;> cases h
    · rename_i he
      split at h
      · rename_i hv
        exact ⟨hf, hv, he⟩
      · cases h
    · cases h
  · simp only [hf, Bool.not_false, if_true] at h
    cases h

theorem productConflict_free {rows : List ComponentRows} (h : productConflict rows = .free) :
    rows.all (fun r => foldConflict r.conflicts == .free) = true := by
  unfold productConflict at h
  split at h
  · assumption
  · split at h <;> cases h

theorem productConflict_conflict {rows : List ComponentRows} (h : productConflict rows = .conflict) :
    rows.any (fun r => foldConflict r.conflicts == .conflict) = true := by
  unfold productConflict at h
  split at h
  · cases h
  · split at h
    · assumption
    · cases h

theorem productPremises_model {rows : List ComponentRows} (h : productPremises rows = .model) :
    rows.all (fun r => foldPremises r.premises == .model) = true := by
  unfold productPremises at h
  split at h
  · assumption
  · cases h

end VE.Readings

namespace VE.Readings.Run
open Lean
open VE.Readings
open VE.Readings.Wire (AdmittedNDFull NDVerdicts admitS2 admitNDFull nd_rowsHold nd_premiseRowsHold
  mem_chosenOf chosenOf fullEnv)
open VE.NormDefaults (EntailsU)
universe u

/-! ## A replayed product (the theorems' object) -/

/-- The cases of a document replayed by themselves, `main` first (`Components.all`'s order); `kq` is the case a
    query is typed in, the only one whose rows may be under `--under`. -/
structure ProductReplay where
  all : List (String × NDVerdicts)
  hne : all ≠ []
  kq : Option Nat
  hA : ∀ (j : Nat) (p : String × NDVerdicts), kq ≠ some j → all[j]? = some p → p.2.A = []
  rowsNe : ∀ p ∈ all, p.2.evs ≠ []

def ProductReplay.K (P : ProductReplay) : Components :=
  ⟨(P.all.head P.hne).2.r.N, P.all.tail.map (fun p => (p.1, p.2.r.N))⟩
def ProductReplay.rows (P : ProductReplay) : List ComponentRows :=
  P.all.map (fun p => ⟨p.2.conflictRows, p.2.premiseRows⟩)

theorem ProductReplay.K_all (P : ProductReplay) : P.K.all = P.all.map (·.2.r.N) := by
  obtain ⟨all, hne, _, _, _⟩ := P
  cases all with
  | nil => exact absurd rfl hne
  | cons p ps => simp [ProductReplay.K, Components.all, List.map_map, Function.comp_def]

theorem ProductReplay.at {P : ProductReplay} {j : Nat} {N : NDoc} {r : ComponentRows} (hN : P.K.all[j]? = some N)
    (hr : P.rows[j]? = some r) :
    ∃ p, P.all[j]? = some p ∧ N = p.2.r.N ∧ r = ⟨p.2.conflictRows, p.2.premiseRows⟩ := by
  rw [P.K_all, List.getElem?_map] at hN
  simp only [ProductReplay.rows, List.getElem?_map] at hr
  cases hp : P.all[j]? with
  | none => rw [hp] at hN; cases hN
  | some p =>
    rw [hp] at hN hr
    simp only [Option.map_some, Option.some.injEq] at hN hr
    exact ⟨p, rfl, hN.symm, hr.symm⟩

theorem ProductReplay.rows_length (P : ProductReplay) : P.rows.length = P.K.all.length := by
  simp [ProductReplay.rows, P.K_all]

/-- The rows of a case asked over all of its compatible choices are sound. -/
theorem part_sound (x : NDVerdicts) (hA : x.A = []) :
    Covers x.r.N [] x.conflictRows ∧ Covers x.r.N [] x.premiseRows ∧
      (∀ y ∈ x.conflictRows, Holds.{u} x.r.N [] .bottom y.1 y.2) ∧ ∀ y ∈ x.premiseRows, Holds.{u} x.r.N [] .bottom y.1 y.2 := by
  obtain ⟨h1, _, h3, _⟩ := nd_rowsHold.{u} x
  obtain ⟨h5, h6⟩ := nd_premiseRowsHold.{u} x
  rw [hA] at h1 h5
  exact ⟨h1, h5, h3, h6⟩

theorem ProductReplay.soundBut (P : ProductReplay) (k : Nat) (hq : P.kq = some k) : RowsSoundBut.{u} P.K P.rows k := by
  refine ⟨P.rows_length, fun j N r hj hN hr => ?_⟩
  obtain ⟨p, hp, rfl, rfl⟩ := P.at hN hr
  exact part_sound p.2 (P.hA j p (by rw [hq]; simpa using Ne.symm hj) hp)

theorem ProductReplay.sound (P : ProductReplay) (hq : P.kq = none) : RowsSound.{u} P.K P.rows := by
  refine ⟨P.rows_length, fun j N r hN hr => ?_⟩
  obtain ⟨p, hp, rfl, rfl⟩ := P.at hN hr
  exact part_sound p.2 (P.hA j p (by rw [hq]; simp) hp)

/-! ### The wire theorems: every verdict a replayed product folds to is its `foldK` theorem's conclusion -/

theorem readings_wire_product_conflict_free (P : ProductReplay) (hq : P.kq = none)
    (h : productConflict P.rows = .free) : ∀ cs, CompatibleK P.K cs → ConflictFreeK.{u} P.K cs :=
  foldK_conflict_free P.K P.rows (P.sound hq) (productConflict_free h)

theorem readings_wire_product_conflict (P : ProductReplay) (hq : P.kq = none)
    (h : productConflict P.rows = .conflict) :
    ∃ cs, CompatibleK P.K cs ∧ ∃ (k : Nat) (N : NDoc) (c : Choice), P.K.all[k]? = some N ∧ cs[k]? = some c ∧
      ¬ VE.NormDefaults.ConflictFreeU.{0} (choiceU N c) := by
  refine foldK_conflict.{0} P.K P.rows (P.sound hq) (fun j N hN => ?_) (productConflict_conflict h)
  rw [P.K_all, List.getElem?_map] at hN
  cases hp : P.all[j]? with
  | none => rw [hp] at hN; cases hN
  | some p =>
    rw [hp] at hN
    simp only [Option.map_some, Option.some.injEq] at hN
    subst hN
    have hne := P.rowsNe p (List.mem_of_getElem? hp)
    obtain ⟨e, he⟩ := List.exists_mem_of_ne_nil _ hne
    have hc : e.1 ∈ chosenOf p.2.r.N.D p.2.A := by
      rw [← p.2.hevs]
      exact List.mem_map.mpr ⟨e, he, rfl⟩
    exact ⟨e.1, ((mem_chosenOf _ p.2.ready p.2.hle _ _).mp hc).1⟩

theorem readings_wire_product_model (P : ProductReplay) (hq : P.kq = none) (h : productPremises P.rows = .model) :
    ∃ cs, CompatibleK P.K cs ∧ ConsistentK P.K cs :=
  foldK_consistent.{0} P.K P.rows (P.sound hq) (productPremises_model h)

theorem ProductReplay.k_at (P : ProductReplay) {k : Nat} {p : String × NDVerdicts} (hp : P.all[k]? = some p) :
    P.K.all[k]? = some p.2.r.N := by
  rw [P.K_all, List.getElem?_map, hp]
  rfl

theorem ProductReplay.rows_at (P : ProductReplay) {k : Nat} {p : String × NDVerdicts} (hp : P.all[k]? = some p) :
    P.rows[k]? = some ⟨p.2.conflictRows, p.2.premiseRows⟩ := by
  simp [ProductReplay.rows, List.getElem?_map, hp]

/-- ALL for the document: the query's case `k` (its rows under its `--under` readings `A`) is ALL and every other
    case is CONFLICT-FREE; every compatible product choice taking `A` at `k` is CONFLICT-FREE and entails the
    conclusion at `k`. -/
theorem readings_wire_product_all (P : ProductReplay) (k : Nat) (hq : P.kq = some k) (p : String × NDVerdicts)
    (hp : P.all[k]? = some p) (h : productQuery P.rows k p.2.conflictRows p.2.queryRows = .all) :
    ∀ cs', CompatibleK P.K cs' → TakesAt cs' k p.2.A → ConflictFreeK.{u} P.K cs' ∧
      ∀ c, cs'[k]? = some c → EntailsU.{u} (choiceU p.2.r.N c) ((choiceDoc p.2.r.N.D c).2 ++ p.2.Γ) p.2.φ := by
  obtain ⟨hf, ha⟩ := productQuery_all h
  exact foldK_all_under P.K k p.2.r.N (P.k_at hp) p.2.A p.2.Γ p.2.φ P.rows (P.soundBut k hq) _ _ (nd_rowsHold p.2) ha
    (othersFree_spec hf)

theorem readings_wire_product_none (P : ProductReplay) (k : Nat) (hq : P.kq = some k) (p : String × NDVerdicts)
    (hp : P.all[k]? = some p) (h : productQuery P.rows k p.2.conflictRows p.2.queryRows = .none) :
    ∀ cs', CompatibleK P.K cs' → TakesAt cs' k p.2.A → ConflictFreeK.{u} P.K cs' ∧
      (∀ (j : Nat) (M : NDoc) (c : Choice), j ≠ k → P.K.all[j]? = some M → cs'[j]? = some c →
        ConsistentU (choiceU M c) (choiceDoc M.D c).2) ∧
      ∀ c, cs'[k]? = some c → CounterU (choiceU p.2.r.N c) ((choiceDoc p.2.r.N.D c).2 ++ p.2.Γ) p.2.φ := by
  obtain ⟨hf, he, hn⟩ := productQuery_none h
  exact foldK_none_under P.K k p.2.r.N (P.k_at hp) p.2.A p.2.Γ p.2.φ P.rows (P.soundBut k hq) _ _ (nd_rowsHold p.2) hn
    (othersSettled_every hf he)

theorem readings_wire_product_some (P : ProductReplay) (k : Nat) (hq : P.kq = some k) (p : String × NDVerdicts)
    (hp : P.all[k]? = some p) (h : productQuery P.rows k p.2.conflictRows p.2.queryRows = .some) :
    (∀ cs', CompatibleK P.K cs' → TakesAt cs' k p.2.A → ConflictFreeK.{u} P.K cs') ∧
    (∃ cs', CompatibleK P.K cs' ∧ TakesAt cs' k p.2.A ∧ ∃ c, cs'[k]? = some c ∧
      EntailsU.{u} (choiceU p.2.r.N c) ((choiceDoc p.2.r.N.D c).2 ++ p.2.Γ) p.2.φ) ∧
    (∃ cs', CompatibleK P.K cs' ∧ TakesAt cs' k p.2.A ∧
      (∀ (j : Nat) (M : NDoc) (c : Choice), j ≠ k → P.K.all[j]? = some M → cs'[j]? = some c →
        ConsistentU (choiceU M c) (choiceDoc M.D c).2) ∧
      ∃ c, cs'[k]? = some c ∧ CounterU (choiceU p.2.r.N c) ((choiceDoc p.2.r.N.D c).2 ++ p.2.Γ) p.2.φ) := by
  obtain ⟨hf, he, hs⟩ := productQuery_some h
  exact foldK_some_under P.K k p.2.r.N (P.k_at hp) p.2.A p.2.Γ p.2.φ P.rows (P.soundBut k hq) _ _ (nd_rowsHold p.2) hs
    (othersSettled_some hf he)

/-! ## Each case of the product: its admission -/

def productProfileText : String :=
  "UnsupportedProfile: a document with readings that carry their own vocabulary is checked as a product of its sentences only under norm-defaults@0 on the norms chain"
def productPendingText (name : String) : String :=
  s!"UnsupportedProfile: component {name} has a reading without content, so its sentences are pending; the product of sentences checked by themselves needs each reading's content"

/-- The main case's checked part when it has no content-bearing set: its fixed units. The sets left on W2 carry no
    content, add nothing to any choice's document, and are reported unchecked (1.9). -/
def fixedPart (document : Json) : Json :=
  VE.Readings.Wire.withArrays document [("couplings", []), ("narrowings", []), ("reading_sets", [])]

/-- One case of the product, admitted under the completion: its name, its admission (of its checked part), its
    route as split, and the sets it leaves on W2, with their units. -/
structure ProductPart where
  name : String
  f : AdmittedNDFull
  route : Route
  unchecked : List (String × String)

def requireCompletion (b : VE.Readings.Wire.Admitted2) : Except String Unit :=
  if b.a.re.lower.contains "norm-defaults@0" && b.a.re.chain == .norms then pure () else throw productProfileText

/-- A case's admission for the product (4.1 on the case, then the completion's): on its checked part. -/
def admitPart (name : String) (environment document : Json) : Except String ProductPart := do
  let b ← admitS2 environment document
  requireCompletion b
  match routeOf true b.D with
  | .enumerated => pure ⟨name, ← admitNDFull b, .enumerated, []⟩
  | .w2 => pure ⟨name, ← admitNDFull (← admitS2 environment (fixedPart document)), .w2,
      b.D.sets.map (fun R => (R.id, R.unit))⟩
  | _ => throw (productPendingText name)

/-- The units of a case's checked document, in source order. -/
def partUnits (p : ProductPart) : List String := p.f.r.N.D.items.map itemUnit

/-- A unit's sentence number: its position among the document's units, from 1. -/
def unitNumber (document : Json) (u : String) : Nat :=
  (((VE.Readings.Wire.arr document "units").findIdx? (fun x => VE.Readings.Wire.strOf (x.getObjValD "id") == u)).map
    (· + 1)).getD 0

/-! ## The query's case (5 rows 16 to 18) -/

/-- The conclusion and premises type in the case's frame (its first compatible choice's filled environment, where
    RD-3's replay reads them). -/
def fitsQuery (j : Json) (p : ProductPart) : Bool :=
  match queryFormulas (fullEnv p.f.r.N ((choices p.f.r.N.D).headD [])) "query" j with
  | .ok _ => true
  | .error _ => false

def dedupNats (l : List Nat) : List Nat := l.foldl (fun acc x => if acc.contains x then acc else acc ++ [x]) []

def fitText (document : Json) (parts : List ProductPart) (ks : List Nat) : String :=
  let ns := dedupNats (ks.flatMap (fun k => ((parts[k]?.map partUnits).getD []).map (unitNumber document)))
  s!"InvalidInput: the conclusion's terms fit sentences {", ".intercalate (ns.map toString)}; name one with --sentence"

def noFitText : String := "InvalidInput: the conclusion uses terms of no sentence checked by itself"

/-- The case a query is about: the one `sentence` names, else the one case its terms fit. -/
def queryPart (document j : Json) (parts : List ProductPart) : Except String Nat := do
  let _ ← j.getObjVal? "conclusion"
  match j.getObjValD "sentence" with
  | .str u =>
    match parts.findIdx? (fun p => (partUnits p).contains u) with
    | none => throw s!"InvalidInput: --sentence names {u}, which is not a sentence of the document"
    | some k =>
      if (parts[k]?.map (fitsQuery j)).getD false then pure k
      else throw s!"InvalidInput: the conclusion's terms do not fit sentence {unitNumber document u}"
  | .null =>
    match (List.range parts.length).filter (fun k => (parts[k]?.map (fitsQuery j)).getD false) with
    | [] => throw noFitText
    | [k] => pure k
    | ks => throw (fitText document parts ks)
  | _ => throw "InvalidInput: --sentence takes a unit id"

/-- 5 row 18: `--under` names sets of the query's case only (A3). -/
def underCheck (p : ProductPart) (A : Choice) : Except String Unit :=
  match A.find? (fun x => !(p.f.r.N.D.sets.any (·.id == x.1))) with
  | some x => throw s!"InvalidInput: --under names {x.1}, which is not a reading set of the sentence the conclusion is about"
  | none => pure ()

/-! ## Each case's own answer -/

/-- The request a case is asked: its question, the evidence and dead certificates tagged with its name, and, for the
    query's case, the conclusion, premises and readings named. -/
def partRequest (j : Json) (name question : String) (query : Bool) : Json :=
  let mine := fun (e : Json) => VE.Readings.Wire.strOf (e.getObjValD "component") == name
  let deadL := match j.getObjValD "dead" with | .arr xs => xs.toList | _ => []
  Json.mkObj ([("question", .str question), ("evidence", Json.arr ((evidenceList j).filter mine).toArray),
    ("dead", Json.arr (deadL.filter mine).toArray)] ++
    (if query then [("premises", j.getObjValD "premises"), ("conclusion", j.getObjValD "conclusion"),
      ("assumed", j.getObjValD "assumed")] else []))

/-- One case after its replay: its part, its question, its replay, the readings it names and the dead certificates
    it was sent. Its answer is RD-3's on it (`PartRun.answer`), and so is its plan. -/
structure PartRun where
  id : String
  part : ProductPart
  question : String
  hq : verdictsQuestions.contains question = true
  x : NDVerdicts
  named : Option Choice
  dead : List Json

def PartRun.infos (r : PartRun) : List RowInfo := ndInfos r.x
def PartRun.rows (r : PartRun) : ComponentRows := ⟨r.x.conflictRows, r.x.premiseRows⟩
def PartRun.answer (r : PartRun) : Json :=
  verdictsAnswer r.id r.question true r.part.f.r.N.D r.x.A r.named (some r.infos) [] r.dead
def PartRun.lines (r : PartRun) : List Line :=
  verdictsPlan r.question true r.part.f.r.N.D r.x.A r.named (some r.infos) [] r.dead

/-- A case replayed by itself (RD-3's replay under the completion). -/
def runPart (id : String) (p : ProductPart) (question : String) (A : Choice) (named : Option Choice) (jp : Json) :
    Except String PartRun :=
  if hq : verdictsQuestions.contains question = true then do
    let D := p.f.r.N.D
    if (choices D).isEmpty then throw (unsatText D)
    let x ← replayND p.f question A jp
    let dead := match jp.getObjValD "dead" with | .arr xs => xs.toList | _ => []
    pure ⟨id, p, question, hq, x, named, dead⟩
  else throw s!"InvalidInput: unknown readings-verdicts question {question}"

/-! ## The answer -/

/-- A reading's premise status (1.10): narrowed, dead, or the fold of the premise rows of the choices taking it. -/
def readingPremise (D : Doc) (infos : List RowInfo) (dead : List (String × Nat)) (R : ReadingSet) (i : Nat) : Premise :=
  if (droppedBy D R i).isSome then .narrowed
  else if dead.contains (R.id, i) then .dead
  else
    let taking := infos.filter (·.choice.contains (R.id, i))
    if taking.isEmpty then .unknown
    else match foldPremises (taking.map (fun t => (t.choice, t.premise))) with
      | .model => .model
      | .inconsistent => .inconsistent
      | _ => .unknown

/-- The case's Lean-decided units (1.10): each fixed unit with content by `fixedDecided` on the case's folds, each
    content-bearing set's unit by `setDecided` on its conflict rows per compatible choice and its readings' premise
    statuses. -/
def partDecided (D : Doc) (infos : List RowInfo) (dead : List (String × Nat)) : List String :=
  let cs := infos.map (fun i => (i.choice, i.conflict))
  let ps := infos.map (fun i => (i.choice, i.premise))
  D.items.filterMap (fun it => match it with
    | .fixed u _ _ => if fixedDecided (foldConflict cs) (foldPremises ps) then some u else none
    | .set R =>
      if VE.Readings.Wire.contentBearing R &&
          setDecided cs ((List.range R.candidates.length).map (readingPremise D infos dead R)) then some R.unit
      else none
    | .bar _ _ => none)

/-- A line of the product's plan with the case it is read in (`null`: the document). -/
def entryJson (component : Option String) (l : Line) : Json :=
  Json.mkObj [("component", match component with | some c => .str c | none => .null), ("line", l.json)]

def entryJsonP (x : Option String × Line) : Json := entryJson x.1 x.2

def e32Line : Line := ⟨"E32", none, [], none, [], none⟩
def e31Line (D : Doc) : Line := ⟨"E31", none, D.sets.map (·.id, 0), none, [], none⟩
/-- E30 replaces E26 for a companion case (2.4 item 1): "sentence n" is the case's one open sentence. -/
def toE30 (D : Doc) (l : Line) : Line :=
  if l.frame == "E26" then { l with frame := "E30", readings := D.sets.map (·.id, 0) } else l

/-- A case's lines in the product's plan: none for a case without an open sentence; a companion case's preceded by
    E31, with E30 for E26. -/
def partLines (companion : Bool) (D : Doc) (lines : List Line) : List Line :=
  if D.sets.isEmpty then []
  else if companion then e31Line D :: lines.map (toE30 D) else lines

def componentJson (r : PartRun) : Json :=
  Json.mkObj [("component", .str r.part.name), ("route", .str r.part.route.text),
    ("units", toJson (partUnits r.part)),
    ("unchecked", Json.arr (r.part.unchecked.map (fun (s, un) =>
      Json.mkObj [("set", .str s), ("unit", .str un), ("status", .str "UNKNOWN")])).toArray),
    ("answer", r.answer)]

def statusRows (runs : List PartRun) (f : ComponentRows → ChoiceResult) : Json :=
  Json.arr (runs.map (fun r => Json.mkObj [("component", .str r.part.name), ("status", .str (word (f r.rows)))])).toArray

/-- The product's result for the question (4.5). -/
def productResult (question : String) (runs : List PartRun) (k : Nat) : Json :=
  let rows := runs.map (·.rows)
  let route : String × Json := ("route", .str "components")
  if question == "conflict" then
    Json.mkObj [("status", .str (word (productConflict rows))), route,
      ("components", statusRows runs (fun r => foldConflict r.conflicts))]
  else if question == "premises" then
    Json.mkObj [("status", .str (word (productPremises rows))), route,
      ("components", statusRows runs (fun r => foldPremises r.premises))]
  else
    let kr := runs[k]?
    let name : String × Json := ("component", .str ((kr.map (·.part.name)).getD ""))
    let cs := (kr.map (·.x.conflictRows)).getD []
    let qs := (kr.map (·.x.queryRows)).getD []
    match productQuery rows k cs qs with
    | .all => Json.mkObj [("verdict", .str "ALL"), route, name]
    | .none => Json.mkObj [("verdict", .str "NONE"), route, name]
    | .some => Json.mkObj [("verdict", .str "SOME"), route, name]
    | .unknown =>
      if !othersFree rows k then
        match othersReason rows k with
        | some (s, j, c) => Json.mkObj [("verdict", .str "UNKNOWN"), route, name,
            ("status", .str s!"UNKNOWN (conflict status: {word s})"), ("conflict_status", .str (word s)),
            ("choice", choiceJson c), ("choice_component", .str ((runs[j]?.map (·.part.name)).getD "")),
            ("choice_text", .str ((runs[j]?.map (fun r => choiceText r.part.f.r.N.D c)).getD ""))]
        | none => Json.mkObj [("verdict", .str "UNKNOWN"), route, name]
      else if foldEntailment cs qs == .none || foldEntailment cs qs == .some then
        Json.mkObj [("verdict", .str "UNKNOWN"), route, name,
          ("reason", .str "another sentence's readings are not all consistent")]
      else Json.mkObj [("verdict", .str "UNKNOWN"), route, name]

/-- The product's English plan (2.4 item 1): E32, then each case's lines in `Components.all`'s order; for a query,
    the query case's lines when the document's verdict is that case's own, else none (the case's own verdict stays
    in its `components` entry). -/
def productPlan (question : String) (runs : List PartRun) (k : Nat) : List (Option String × Line) :=
  let rows := runs.map (·.rows)
  let partEntries := fun (r : PartRun) =>
    (partLines (r.part.name != "main") r.part.f.r.N.D r.lines).map (fun l => (some r.part.name, l))
  if question == "query" then
    match runs[k]? with
    | some r =>
      let own := foldEntailment r.x.conflictRows r.x.queryRows
      if own != .unknown && productQuery rows k r.x.conflictRows r.x.queryRows == own then
        (none, e32Line) :: partEntries r
      else []
    | none => []
  else (none, e32Line) :: runs.flatMap partEntries

/-- The units of `us` in the document's order (its `units`, by id): the order every list of the document's units
    takes on the wire. -/
def documentOrder (document : Json) (us : List String) : List String :=
  ((VE.Readings.Wire.arr document "units").map (fun x => VE.Readings.Wire.strOf (x.getObjValD "id"))).filter us.contains

/-- The decided units of every case asked over all of its compatible choices. -/
def productDecided (runs : List PartRun) : List String :=
  runs.flatMap (fun r =>
    if r.x.A.isEmpty then
      let dead := (deadOf r.part.f.r.N.D r.infos r.dead).1
      partDecided r.part.f.r.N.D r.infos (dead.getD [])
    else [])

def productAnswer (id question : String) (document : Json) (runs : List PartRun) (k : Nat) (sentence : Option String) :
    Json :=
  okWith id [("route", .str "components"), ("question", .str question),
    ("component", if question == "query" then .str (((runs[k]?).map (·.part.name)).getD "") else .null),
    ("sentence", match sentence with | some u => .str u | none => .null),
    ("components", Json.arr (runs.map componentJson).toArray),
    ("result", productResult question runs k),
    ("decided_units", toJson (documentOrder document (productDecided runs))),
    ("english", Json.arr ((productPlan question runs k).map entryJsonP).toArray)]

/-! ## The run -/

def sentenceOf (j : Json) : Option String := match j.getObjValD "sentence" with | .str u => some u | _ => none

def namedOf (j : Json) (A : Choice) : Option Choice :=
  match j.getObjVal? "assumed" with
  | .ok v => if v == .null then none else some A
  | .error _ => none

/-- Each case replayed: the query's case `k` asked the query (under `A`), every other case the premises question
    (its conflict and premise rows); for the conflict and premises questions every case is asked that question. -/
def runParts (id question : String) (j : Json) (parts : List ProductPart) (k : Nat) (A : Choice) :
    Except String (List PartRun) :=
  (List.range parts.length).zip parts |>.mapM (fun (i, p) =>
    let query := question == "query" && i == k
    let q := if question == "query" then (if query then "query" else "premises") else question
    runPart id p q (if query then A else []) (if query then namedOf j A else none) (partRequest j p.name q query))

/-- The replayed product the theorems read, from the runs: one case per run, the query's case `kq`; every other case
    asked over all of its compatible choices, and every case with a compatible choice (checked here, so a replay that
    breaks either is refused rather than folded). -/
def productReplay (runs : List PartRun) (kq : Option Nat) : Except String ProductReplay :=
  let all := runs.map (fun r => (r.part.name, r.x))
  if hne0 : all.isEmpty = false then
    have hne : all ≠ [] := fun h => by simp [h] at hne0
    if hA : (all.zipIdx.all (fun x => kq == some x.2 || x.1.2.A.isEmpty)) = true then
      if hr : all.all (fun p => !p.2.evs.isEmpty) = true then
        .ok ⟨all, hne, kq, fun j p hj hp => by
            have hm : (p, j) ∈ all.zipIdx := List.mem_zipIdx_iff_getElem?.mpr hp
            have := List.all_eq_true.mp hA _ hm
            simp only [Bool.or_eq_true, beq_iff_eq, List.isEmpty_iff] at this
            exact this.resolve_left (fun h => hj h),
          fun p hp => by
            have := List.all_eq_true.mp hr p hp
            simpa using this⟩
      else .error "readings-verdicts: a component has no compatible reading"
    else .error "readings-verdicts: a component other than the query's is asked under named readings"
  else .error "readings-verdicts: no component"

theorem productReplay_rows {runs : List PartRun} {kq : Option Nat} {P : ProductReplay}
    (h : productReplay runs kq = .ok P) : P.rows = runs.map (·.rows) := by
  unfold productReplay at h
  simp only at h
  split at h
  · split at h
    · split at h
      · cases h
        simp [ProductReplay.rows, PartRun.rows, List.map_map, Function.comp_def]
      · cases h
    · cases h
  · cases h

/-- `readings-verdicts` over the cases of the split (4.5): each case admitted for the product in source order, the
    query's case chosen, each case replayed by itself, then the product's answer. -/
def runProduct (j : Json) (id : String) (cases : List (String × Json × Json)) : Except String Json := do
  let question ← VE.Bridge.stringField j "question"
  unless verdictsQuestions.contains question do throw s!"InvalidInput: unknown readings-verdicts question {question}"
  let document ← j.getObjVal? "document"
  let parts ← cases.mapM (fun c => admitPart c.1 c.2.1 c.2.2)
  let A ← VE.Readings.Wire.decodeChoice (j.getObjValD "assumed")
  let k ← if question == "query" then queryPart document j parts else pure 0
  if question == "query" then
    match parts[k]? with
    | some p => underCheck p A
    | none => throw noFitText
  let runs ← runParts id question j parts k A
  let _ ← productReplay runs (if question == "query" then some k else none)
  pure (productAnswer id question document runs k (if question == "query" then sentenceOf j else none))

end VE.Readings.Run
