import VE.Acts.Table
import VE.Acts.Syntax
import VE.NormDefaults.Wire

/-! Elaboration: joined acts become rules on simple acts (docs/spec/act-phrases.md 6.3, 6.5, 6.6; plan 2.3).

A predicate whose act's one reading by the table is two or more atoms is split: part `p__i` keeps `p`'s declaration
with atom i's act, and each rule `N` on `p` becomes `N-ai` on part i. `SplitMap` names every generated predicate and
rule with its source and index (SYNTHESIS 2.6). `elaborateMap` checks in the spec's order: the readings, the
references to a split predicate, the generated names, the parts' acts, `validate` and the author limits on the
result, and the backstop. Each predicate's split is read once per document, from step 1's readings (`sa`); every
later step looks it up. `splitMap_exact` and `elaborate_parts` come with ap-3cb.
-/

namespace VE.Acts
open VE.Norms VE.NormDefaults

structure ActsDoc where
  U : VE.NormDefaults.UDoc
  V : Vocab
  fixed : List String
  /-- each joined act's predicate and its one meaning (from `read`) -/
  acts : List (String × Act)
  /-- the environment's declared predicates, as `checkAuthorN` counts them (SR7) -/
  declared : Nat

structure SplitMap where
  /-- generated `p__i`, its source predicate, i -/
  preds : List (String × String × Nat)
  /-- generated `<rule>-a<i>`, its source rule, i -/
  rules : List (String × String × Nat)
  deriving DecidableEq, Repr

def partPred (p : String) (i : Nat) : String := p ++ "__" ++ toString i
def partRule (n : String) (i : Nat) : String := n ++ "-a" ++ toString i

/-- An obligation's permission dual, or the obligation a permission is the dual of. -/
def dualOf (T : Tree) (p : String) : Option String :=
  match T.regulated.find? (·.name == p) with
  | some r => match r.role, r.permission with
    | .obligation, some m => some m
    | .permission, _ => (T.regulated.find? (fun o => o.role == .obligation && o.permission == some p)).map (·.name)
    | _, _ => none
  | none => none

/-- The one reading of a joined act by rule `N`'s op: D-21, D-22, D-23 (with the paraphrases of 2.2, form unknown). -/
def ruleReading (D : ActsDoc) (A : Act) (N : Node) : Except String (List Simple) :=
  match (D.U.D.T.regulated.find? (·.name == N.pred)).bind (opOf · N.sign) with
  | none => .error s!"InvalidInput: rule {N.name} has no modal word for a joined act"
  | some op => match table op A with
    | [] => .error s!"InvalidInput: rule {N.name} has no reading of its act; rewrite it"
    | [R] => .ok R
    | Rs => paraphrases D.fixed op none s!"rule {N.name}" Rs >>= fun ps =>
      .error (s!"InvalidInput: rule {N.name} has more than one reading: " ++ numbered ps)

/-- The one reading of a predicate's act: `[[atom a]]` for `one a`; for a join, every rule on `p` and on its dual has
    exactly one reading by the table, and all are equal (D-20 to D-24). -/
def readingOf (D : ActsDoc) (p : String) : Act → Except String (List Simple)
  | .one a => .ok [.atom a]
  | A => do
    let d := dualOf D.U.D.T p
    let Rs ← (D.U.D.T.nodes.filter (fun N => N.pred == p || some N.pred == d)).mapM (ruleReading D A)
    match Rs with
    | [] => .error s!"InvalidInput: the joined act of {p} has no rule to read it by"
    | R :: rest =>
      if rest.all (· == R) then .ok R
      else .error s!"InvalidInput: the rules on {p} and its dual read its act differently; write the parts as separate predicates"

/-- The atoms of a reading, when it has two or more (the table's readings are all atoms, or one whole act). -/
def atomsOf (R : List Simple) : Option (List Atom) :=
  let atoms := R.filterMap fun x => match x with | .atom a => some a | .whole _ => none
  if 2 ≤ atoms.length then some atoms else none

/-- The atoms `p` splits into: its act's one reading (`readingOf`), when that reading is two or more atoms. -/
def splitAtoms (D : ActsDoc) (p : String) : Option (List Atom) :=
  ((D.acts.lookup p).bind fun A => (readingOf D p A).toOption).bind atomsOf

/-- The parts of `p` under the splits `sa`, each atom with its index from 1; `[]` when `p` does not split. -/
def partsOf (sa : String → Option (List Atom)) (p : String) : List (Atom × Nat) := ((sa p).getD []).zipIdx 1

def splitMap (D : ActsDoc) (sa : String → Option (List Atom)) : SplitMap :=
  { preds := D.U.D.T.regulated.flatMap fun r => (partsOf sa r.name).map fun x => (partPred r.name x.2, r.name, x.2)
    rules := D.U.D.T.nodes.flatMap fun N => (partsOf sa N.pred).map fun x => (partRule N.name x.2, N.name, x.2) }

/-- The names `p` stands for under the map `M`: its parts, or itself. -/
def partNamesIn (M : SplitMap) (p : String) : List String :=
  match M.preds.filter (·.2.1 == p) with
  | [] => [p]
  | xs => xs.map (·.1)

/-- The names a source predicate stands for after elaboration: its parts, or itself. -/
def partNames (D : ActsDoc) (p : String) : List String := partNamesIn (splitMap D (splitAtoms D)) p

/-- Part i of `r`: atom i's act (*to* exactly when plain), the dual's part i (6.5). -/
def splitReg (D : ActsDoc) (sa : String → Option (List Atom)) (r : Regulated) : List Regulated :=
  match partsOf sa r.name with
  | [] => [r]
  | xs => xs.map fun x => { r with name := partPred r.name x.2, act := some (partAct D.fixed r.role x.1),
                                   permission := r.permission.map (partPred · x.2) }

/-- Rule `N` on part i, its `over` mapped to part i. -/
def splitNode (sa : String → Option (List Atom)) (N : Node) : List Node :=
  match partsOf sa N.pred with
  | [] => [N]
  | xs => xs.map fun x => { N with name := partRule N.name x.2, pred := partPred N.pred x.2,
                                   over := N.over.map (partRule · x.2) }

/-- Each part declared with its source's sorts; a split source undeclared. -/
def splitEnv (D : ActsDoc) (M : SplitMap) : VE.Environment :=
  { D.U.D.E with predicates := fun q => match M.preds.find? (·.1 == q) with
      | some x => D.U.D.E.predicates x.2.1
      | none => if M.preds.any (·.2.1 == q) then none else D.U.D.E.predicates q }

def splitDoc (D : ActsDoc) (sa : String → Option (List Atom)) (M : SplitMap) : UDoc :=
  { D := { E := splitEnv D M, lits := D.U.D.lits,
           T := { D.U.D.T with regulated := D.U.D.T.regulated.flatMap (splitReg D sa),
                               nodes := D.U.D.T.nodes.flatMap (splitNode sa) } },
    unspec := D.U.unspec.flatMap (partNamesIn M) }

/-- Step 2 (D-25): no guard, exception or definition names a split predicate. -/
def refsOk (D : ActsDoc) (sa : String → Option (List Atom)) : Except String Unit :=
  let split := fun φ => (preds φ).any (fun q => (sa q).isSome)
  match D.U.D.T.nodes.find? (fun N => (N.guard :: N.carveOuts).any split) with
  | some N => .error s!"InvalidInput: rule {N.name} names a predicate that is split into parts; name one of its parts"
  | none => match D.U.D.T.definitions.find? (fun d => split d.body) with
    | some d =>
      .error s!"InvalidInput: definition {d.name} names a predicate that is split into parts; name one of its parts"
    | none => .ok ()

/-- Step 3 (D-26): a part name is not declared in the source (environment, regulated, unspecified) or by another
    part, and has at most 64 bytes; a part rule name is not a source rule's or another part's, and is a rule name. -/
def namesOk (D : ActsDoc) (M : SplitMap) : Except String Unit :=
  let qs := M.preds.map (·.1)
  let ns := M.rules.map (·.1)
  let declared := fun q => (D.U.D.E.predicates q).isSome || D.U.D.T.regulated.any (·.name == q) ||
    D.U.unspec.contains q || qs.count q > 1
  let used := fun n => D.U.D.T.nodes.any (·.name == n) || ns.count n > 1
  match qs.find? (fun q => declared q || q.utf8ByteSize > VE.Limits.maxIdentifierBytes),
      ns.find? (fun n => used n || !ruleName n) with
  | some q, _ => .error (if declared q then s!"InvalidInput: the part name {q} is already declared"
      else s!"ResourceLimit: the part name {q} is over 64 bytes")
  | none, some n => .error (if used n then s!"InvalidInput: the part rule name {n} is already used"
      else s!"ResourceLimit: the part rule name {n} is not a rule name of at most 64 bytes")
  | none, none => .ok ()

/-- Step 4 (D-27): two parts of one predicate never have equal acts, for every role. -/
def partsDistinct (D : ActsDoc) (sa : String → Option (List Atom)) : Except String Unit :=
  match D.U.D.T.regulated.find? (fun r => !decide ((partsOf sa r.name).map (partAct D.fixed r.role ·.1)).Nodup) with
  | some r => .error s!"InvalidInput: two parts of {r.name} are the same act"
  | none => .ok ()

/-- Step 6's vocabulary: the environment's declared predicates, less the split ones, plus their parts. -/
def declaredAfter (D : ActsDoc) (sa : String → Option (List Atom)) (M : SplitMap) : Nat :=
  D.declared - (D.U.D.T.regulated.filter fun r => (sa r.name).isSome).length + M.preds.length

/-- The splits read off step 1's readings `Rs` of `D.acts`: each predicate's first entry, as `splitAtoms` reads it. -/
def splitsOf (acts : List (String × Act)) (Rs : List (List Simple)) : List (String × Option (List Atom)) :=
  (acts.zip Rs).map fun (x, R) => (x.1, atomsOf R)

/-- AP-3: split every predicate whose reading has two or more atoms; refuse a formula naming a split predicate;
    check the generated names and parts; re-run the route limits on the result (`validate`, then `authorLimits` with
    the vocabulary `D.declared − s + k`: `s` split predicates, `k` parts); backstop: the result is `WellFormedU`, and
    no split rule keeps its name (a source with two rules of one name). Each act is read once (step 1). -/
def elaborateMap (D : ActsDoc) : Except String (VE.NormDefaults.UDoc × SplitMap) := do
  let Rs ← D.acts.mapM fun x => readingOf D x.1 x.2
  let S := splitsOf D.acts Rs
  let sa := fun p => (S.lookup p).join
  refsOk D sa
  let M := splitMap D sa
  namesOk D M
  partsDistinct D sa
  let U' := splitDoc D sa M
  VE.Norms.validate U'.D
  VE.NormDefaults.Wire.authorLimits (declaredAfter D sa M) U'
  unless WellFormedU U' && M.rules.all (fun x => !U'.D.T.nodes.any (·.name == x.2.1)) do
    throw "InvalidInput: the elaborated document is not well formed"
  pure (U', M)

def elaborate (D : ActsDoc) : Except String VE.NormDefaults.UDoc := (elaborateMap D).map (·.1)

/-! ### Theorems (6.6) -/

theorem mapM_ok {α β ε : Type} {f : α → Except ε β} :
    ∀ {l : List α} {ys : List β}, l.mapM f = .ok ys → ∀ x ∈ l, ∃ y ∈ ys, f x = .ok y
  | [], _, _, x, hx => absurd hx List.not_mem_nil
  | a :: l, ys, h, x, hx => by
    rw [List.mapM_cons] at h
    cases ha : f a with
    | error e => simp [ha, bind, Except.bind] at h
    | ok y =>
      cases hl : l.mapM f with
      | error e => simp [ha, hl, bind, Except.bind] at h
      | ok ys' =>
        simp [ha, hl, bind, Except.bind, pure, Except.pure] at h
        subst h
        rcases List.mem_cons.mp hx with rfl | hx
        · exact ⟨y, List.mem_cons_self, ha⟩
        · obtain ⟨y', hy', e⟩ := mapM_ok hl x hx
          exact ⟨y', List.mem_cons_of_mem _ hy', e⟩

/-- Step 1's splits are `splitAtoms`'s: each predicate's first entry, read once. -/
theorem lookup_splitsOf (D : ActsDoc) : ∀ {l : List (String × Act)} {Rs : List (List Simple)},
    l.mapM (fun x => readingOf D x.1 x.2) = .ok Rs → ∀ p,
      ((splitsOf l Rs).lookup p).join = ((l.lookup p).bind fun A => (readingOf D p A).toOption).bind atomsOf
  | [], Rs, h, p => by cases h; rfl
  | (q, A) :: l, Rs, h, p => by
    rw [List.mapM_cons] at h
    cases hq : readingOf D q A with
    | error e => simp [hq, bind, Except.bind] at h
    | ok R =>
      cases hl : l.mapM (fun x => readingOf D x.1 x.2) with
      | error e => simp [hq, hl, bind, Except.bind] at h
      | ok Rs' =>
        simp only [hq, hl, bind, Except.bind, pure, Except.pure, Except.ok.injEq] at h
        subst h
        by_cases hp : p = q
        · subst hp; simp [splitsOf, List.lookup, hq, Except.toOption]
        · have := lookup_splitsOf D hl p
          simp only [splitsOf] at this ⊢
          have hb : (p == q) = false := beq_eq_false_iff_ne.mpr hp
          simp only [List.zip_cons_cons, List.map_cons, List.lookup, hb]
          exact this

theorem splits_eq {D : ActsDoc} {Rs : List (List Simple)} (h : D.acts.mapM (fun x => readingOf D x.1 x.2) = .ok Rs) :
    (fun p => ((splitsOf D.acts Rs).lookup p).join) = splitAtoms D :=
  funext fun p => lookup_splitsOf D h p

theorem elaborateMap_ok {D : ActsDoc} {U' : UDoc} {M : SplitMap} (h : elaborateMap D = .ok (U', M)) :
    (∃ Rs, D.acts.mapM (fun x => readingOf D x.1 x.2) = .ok Rs) ∧ namesOk D (splitMap D (splitAtoms D)) = .ok () ∧
    U' = splitDoc D (splitAtoms D) (splitMap D (splitAtoms D)) ∧ M = splitMap D (splitAtoms D) ∧
    WellFormedU U' = true ∧ (M.rules.all fun x => !U'.D.T.nodes.any (·.name == x.2.1)) = true := by
  unfold elaborateMap at h
  cases h1 : D.acts.mapM (fun x => readingOf D x.1 x.2) with
  | error e => simp only [h1, bind, Except.bind] at h; cases h
  | ok Rs =>
  simp only [h1, bind, Except.bind] at h
  rw [splits_eq h1] at h
  cases h2 : refsOk D (splitAtoms D) <;> simp only [h2] at h
  · cases h
  cases h3 : namesOk D (splitMap D (splitAtoms D)) <;> simp only [h3] at h
  · cases h
  cases h4 : partsDistinct D (splitAtoms D) <;> simp only [h4] at h
  · cases h
  cases h5 : validate (splitDoc D (splitAtoms D) (splitMap D (splitAtoms D))).D <;> simp only [h5] at h
  · cases h
  split at h
  · cases h
  split at h
  next hb =>
    simp only [pure, Except.pure, Except.ok.injEq, Prod.mk.injEq] at h
    obtain ⟨rfl, rfl⟩ := h
    rw [Bool.and_eq_true] at hb
    exact ⟨⟨_, rfl⟩, rfl, rfl, rfl, hb.1, hb.2⟩
  next => cases h

theorem ruleReading_ok {D : ActsDoc} {A : Act} {N : Node} {R : List Simple} (h : ruleReading D A N = .ok R) :
    ∃ r op, D.U.D.T.regulated.find? (·.name == N.pred) = some r ∧ opOf r N.sign = some op ∧ table op A = [R] := by
  unfold ruleReading at h
  cases hf : D.U.D.T.regulated.find? (·.name == N.pred) with
  | none => simp [hf] at h
  | some r =>
    cases ho : opOf r N.sign with
    | none => simp [hf, ho] at h
    | some op =>
      simp only [hf, ho, Option.bind_some] at h
      refine ⟨r, op, rfl, ho, ?_⟩
      split at h
      · cases h
      next R' heq => cases h; exact heq
      · simp only [bind, Except.bind] at h
        split at h <;> cases h

theorem elaborateMap_fst (D : ActsDoc) : (elaborateMap D).map (·.1) = elaborate D := rfl

theorem elaborate_ok {D : ActsDoc} {U' : VE.NormDefaults.UDoc} (h : elaborate D = .ok U') :
    ∃ M, elaborateMap D = .ok (U', M) := by
  unfold elaborate at h
  cases he : elaborateMap D with
  | error e => simp [he, Except.map] at h
  | ok x => simp [he, Except.map] at h; exact ⟨x.2, by rw [← h]⟩

theorem elaborate_wellFormed (D : ActsDoc) {U' : VE.NormDefaults.UDoc} (h : elaborate D = .ok U') :
    VE.NormDefaults.WellFormedU U' = true := by
  obtain ⟨M, hM⟩ := elaborate_ok h
  exact (elaborateMap_ok hM).2.2.2.2.1

theorem elaborate_one_reading (D : ActsDoc) {U' : VE.NormDefaults.UDoc} (h : elaborate D = .ok U') :
    ∀ p A, (p, A) ∈ D.acts → (∃ a, A = .one a) ∨ ∃ R, readingOf D p A = .ok R ∧
      ∀ N ∈ D.U.D.T.nodes, (N.pred = p ∨ some N.pred = dualOf D.U.D.T p) →
        ∃ r op, D.U.D.T.regulated.find? (·.name == N.pred) = some r ∧ opOf r N.sign = some op ∧ table op A = [R] := by
  intro p A hpA
  obtain ⟨M, hM⟩ := elaborate_ok h
  obtain ⟨⟨Rs, hRs⟩, _⟩ := elaborateMap_ok hM
  obtain ⟨R, _, hR⟩ := mapM_ok hRs (p, A) hpA
  cases A with
  | one a => exact .inl ⟨a, rfl⟩
  | all s sp ps | any s sp ps =>
    refine .inr ⟨R, hR, fun N hN hc => ruleReading_ok ?_⟩
    simp only [readingOf, bind, Except.bind] at hR
    split at hR
    · cases hR
    next Rs' hRs' =>
      have hNf : N ∈ D.U.D.T.nodes.filter (fun N => N.pred == p || some N.pred == dualOf D.U.D.T p) :=
        List.mem_filter.mpr ⟨hN, by rcases hc with hc | hc <;> simp [hc]⟩
      obtain ⟨y, hy, hNy⟩ := mapM_ok hRs' N hNf
      split at hR
      · cases hR
      next R0 rest =>
        split at hR
        next hall =>
          cases hR
          rcases List.mem_cons.mp hy with rfl | hy
          · exact hNy
          · have := List.all_eq_true.mp hall y hy
            simp only [beq_iff_eq] at this
            exact this ▸ hNy
        · cases hR

theorem elaborate_unspec (D : ActsDoc) {U' : VE.NormDefaults.UDoc} (h : elaborate D = .ok U') :
    U'.unspec = D.U.unspec.flatMap (partNames D) := by
  obtain ⟨M, hM⟩ := elaborate_ok h
  obtain ⟨_, _, rfl, _⟩ := elaborateMap_ok hM
  rfl

/-- No act splits: every check passes on the source itself, and the result is the source. -/
theorem splitDoc_none (D : ActsDoc) : splitDoc D (fun _ => none) (splitMap D (fun _ => none)) = D.U := by
  have hM : splitMap D (fun _ => none) = ⟨[], []⟩ := by simp [splitMap, partsOf]
  have hr : splitReg D (fun _ => none) = fun r => [r] := funext fun _ => rfl
  have hn : splitNode (fun _ => none) = fun N => [N] := funext fun _ => rfl
  have hu : partNamesIn ⟨[], []⟩ = fun p => [p] := funext fun _ => rfl
  rw [hM]
  simp only [splitDoc, hr, hn, hu, List.flatMap_singleton', splitEnv, List.find?_nil, List.any_nil,
    Bool.false_eq_true, if_false]

theorem lookup_mem {α β : Type} [BEq α] [LawfulBEq α] {p : α} {b : β} :
    ∀ {l : List (α × β)}, l.lookup p = some b → (p, b) ∈ l
  | [], h => by cases h
  | (q, c) :: l, h => by
    by_cases hp : p = q
    · subst hp; simp only [List.lookup, beq_self_eq_true, Option.some.injEq] at h; subst h; exact List.mem_cons_self ..
    · simp only [List.lookup, beq_eq_false_iff_ne.mpr hp] at h; exact List.mem_cons_of_mem _ (lookup_mem h)

/-- The source document is its own elaboration when no act splits (6.6). -/
theorem elaborate_identity (D : ActsDoc) (h : ∀ p A, (p, A) ∈ D.acts → ∃ a, A = .one a)
    (h0 : VE.NormDefaults.WellFormedU D.U = true) (hv : VE.Norms.validate D.U.D = .ok ())
    (hl : VE.NormDefaults.Wire.authorLimits D.declared D.U = .ok ()) : elaborate D = .ok D.U := by
  have hR : D.acts.mapM (fun x => readingOf D x.1 x.2) = .ok (D.acts.map fun x => (readingOf D x.1 x.2).toOption.getD []) := by
    suffices ∀ l : List (String × Act), (∀ p A, (p, A) ∈ l → ∃ a, A = .one a) →
        l.mapM (fun x => readingOf D x.1 x.2) = .ok (l.map fun x => (readingOf D x.1 x.2).toOption.getD []) from
      this _ h
    intro l hl'
    induction l with
    | nil => rfl
    | cons x l ih =>
      obtain ⟨p, A⟩ := x
      obtain ⟨a, rfl⟩ := hl' p A (List.mem_cons_self ..)
      rw [List.mapM_cons, ih (fun p A hm => hl' p A (List.mem_cons_of_mem _ hm))]
      rfl
  have hs : splitAtoms D = fun _ => none := by
    funext p
    unfold splitAtoms
    cases hp : D.acts.lookup p with
    | none => rfl
    | some A =>
      obtain ⟨a, rfl⟩ := h p A (lookup_mem hp)
      simp [readingOf, Except.toOption, atomsOf]
  unfold elaborate elaborateMap
  simp only [hR, bind, Except.bind]
  rw [splits_eq hR, hs, splitDoc_none]
  have hM : splitMap D (fun _ => none) = ⟨[], []⟩ := by simp [splitMap, partsOf]
  have hf : ∀ {α : Type} (l : List α), l.any (fun _ => false) = false := fun l => by induction l <;> simp_all
  have hn : ∀ {α : Type} (l : List α), l.find? (fun _ => false) = none := fun l => by induction l <;> simp_all
  have h2 : refsOk D (fun _ => none) = .ok () := by
    simp only [refsOk, Option.isSome_none, hf, hn]
  have h4 : partsDistinct D (fun _ => none) = .ok () := by
    have : ∀ r : Regulated, (!decide (((partsOf (fun _ => none) r.name).map
        (partAct D.fixed r.role ·.1)).Nodup)) = false := fun _ => by simp [partsOf]
    simp only [partsDistinct, this, hn]
  have h6 : declaredAfter D (fun _ => none) ⟨[], []⟩ = D.declared := by
    have : ∀ l : List Regulated, (l.filter fun _ => false) = [] := fun l => by induction l <;> simp_all
    simp [declaredAfter, Option.isSome_none, this]
  rw [hM, h2, h4, h6]
  simp [namesOk, hv, hl, h0, Except.map, pure, Except.pure]

end VE.Acts
