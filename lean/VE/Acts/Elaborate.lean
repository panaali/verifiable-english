import VE.Acts.Table
import VE.Acts.Syntax
import VE.NormDefaults.Tree

/-! Elaboration: joined acts become rules on simple acts (docs/spec/act-phrases.md 6.3, 6.5, 6.6; plan 2.3).

A predicate whose act's one reading by the table is two or more atoms is split: part `p__i` keeps `p`'s declaration
with atom i's act, and each rule `N` on `p` becomes `N-ai` on part i. `SplitMap` names every generated predicate and
rule with its source and index (SYNTHESIS 2.6). `elaborateMap` checks in the spec's order: the readings, the
references to a split predicate, the generated names, the parts' acts, `validate` on the result, and the backstop.
The author limits of the result (6.3 step 6) come with `authorLimits` (ap-3d).
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

/-- The atoms `p` splits into: its act's one reading (`readingOf`), when that reading is two or more atoms (the
    table's readings are all atoms, or one whole act). -/
def splitAtoms (D : ActsDoc) (p : String) : Option (List Atom) := do
  let R ← (D.acts.lookup p).bind fun A => (readingOf D p A).toOption
  let atoms := R.filterMap fun x => match x with | .atom a => some a | .whole _ => none
  if 2 ≤ atoms.length then some atoms else none

/-- The parts of `p`, each atom with its index from 1; `[]` when `p` does not split. -/
def partsOf (D : ActsDoc) (p : String) : List (Atom × Nat) := ((splitAtoms D p).getD []).zipIdx 1

def splitMap (D : ActsDoc) : SplitMap :=
  { preds := D.U.D.T.regulated.flatMap fun r => (partsOf D r.name).map fun x => (partPred r.name x.2, r.name, x.2)
    rules := D.U.D.T.nodes.flatMap fun N => (partsOf D N.pred).map fun x => (partRule N.name x.2, N.name, x.2) }

/-- The names a source predicate stands for after elaboration: its parts, or itself. -/
def partNames (D : ActsDoc) (p : String) : List String :=
  match (splitMap D).preds.filter (·.2.1 == p) with
  | [] => [p]
  | xs => xs.map (·.1)

/-- Part i of `r`: atom i's act (*to* exactly when plain), the dual's part i (6.5). -/
def splitReg (D : ActsDoc) (r : Regulated) : List Regulated :=
  match partsOf D r.name with
  | [] => [r]
  | xs => xs.map fun x => { r with name := partPred r.name x.2, act := some (partAct D.fixed r.role x.1),
                                   permission := r.permission.map (partPred · x.2) }

/-- Rule `N` on part i, its `over` mapped to part i. -/
def splitNode (D : ActsDoc) (N : Node) : List Node :=
  match partsOf D N.pred with
  | [] => [N]
  | xs => xs.map fun x => { N with name := partRule N.name x.2, pred := partPred N.pred x.2,
                                   over := N.over.map (partRule · x.2) }

/-- Each part declared with its source's sorts; a split source undeclared. -/
def splitEnv (D : ActsDoc) : VE.Environment :=
  let M := splitMap D
  { D.U.D.E with predicates := fun q => match M.preds.find? (·.1 == q) with
      | some x => D.U.D.E.predicates x.2.1
      | none => if M.preds.any (·.2.1 == q) then none else D.U.D.E.predicates q }

def splitDoc (D : ActsDoc) : UDoc :=
  { D := { E := splitEnv D, lits := D.U.D.lits,
           T := { D.U.D.T with regulated := D.U.D.T.regulated.flatMap (splitReg D),
                               nodes := D.U.D.T.nodes.flatMap (splitNode D) } },
    unspec := D.U.unspec.flatMap (partNames D) }

/-- Step 2 (D-25): no guard, exception or definition names a split predicate. -/
def refsOk (D : ActsDoc) : Except String Unit :=
  let split := fun φ => (preds φ).any (fun q => (splitAtoms D q).isSome)
  match D.U.D.T.nodes.find? (fun N => (N.guard :: N.carveOuts).any split) with
  | some N => .error s!"InvalidInput: rule {N.name} names a predicate that is split into parts; name one of its parts"
  | none => match D.U.D.T.definitions.find? (fun d => split d.body) with
    | some d =>
      .error s!"InvalidInput: definition {d.name} names a predicate that is split into parts; name one of its parts"
    | none => .ok ()

/-- Step 3 (D-26): a part name is not declared in the source (environment, regulated, unspecified) or by another
    part, and has at most 64 bytes; a part rule name is not a source rule's or another part's, and is a rule name. -/
def namesOk (D : ActsDoc) : Except String Unit :=
  let qs := (splitMap D).preds.map (·.1)
  let ns := (splitMap D).rules.map (·.1)
  let declared := fun q => (D.U.D.E.predicates q).isSome || D.U.D.T.regulated.any (·.name == q) ||
    D.U.unspec.contains q || qs.count q > 1
  let used := fun n => D.U.D.T.nodes.any (·.name == n) || ns.count n > 1
  match qs.find? (fun q => declared q || q.utf8ByteSize > 64), ns.find? (fun n => used n || !ruleName n) with
  | some q, _ => .error (if declared q then s!"InvalidInput: the part name {q} is already declared"
      else s!"ResourceLimit: the part name {q} is over 64 bytes")
  | none, some n => .error (if used n then s!"InvalidInput: the part rule name {n} is already used"
      else s!"ResourceLimit: the part rule name {n} is not a rule name of at most 64 bytes")
  | none, none => .ok ()

/-- Step 4 (D-27): two parts of one predicate never have equal acts, for every role. -/
def partsDistinct (D : ActsDoc) : Except String Unit :=
  match D.U.D.T.regulated.find? (fun r => !decide ((partsOf D r.name).map (partAct D.fixed r.role ·.1)).Nodup) with
  | some r => .error s!"InvalidInput: two parts of {r.name} are the same act"
  | none => .ok ()

/-- AP-3: split every predicate whose reading has two or more atoms; refuse a formula naming a split predicate;
    check the generated names and parts; re-run the route limits on the result; backstop: the result is
    `WellFormedU`, and no split rule keeps its name (a source with two rules of one name). -/
def elaborateMap (D : ActsDoc) : Except String (VE.NormDefaults.UDoc × SplitMap) := do
  let _ ← D.acts.mapM fun x => readingOf D x.1 x.2
  refsOk D
  namesOk D
  partsDistinct D
  let U' := splitDoc D
  let M := splitMap D
  VE.Norms.validate U'.D
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

theorem inj_of_nodup_map {α β : Type} {f : α → β} :
    ∀ {l : List α}, (l.map f).Nodup → ∀ {x y}, x ∈ l → y ∈ l → f x = f y → x = y
  | [], _, _, _, hx, _, _ => absurd hx List.not_mem_nil
  | a :: l, h, x, y, hx, hy, e => by
    rw [List.map_cons, List.nodup_cons] at h
    simp only [List.mem_cons] at hx hy
    rcases hx with rfl | hx <;> rcases hy with rfl | hy
    · rfl
    · exact absurd (e ▸ List.mem_map_of_mem hy) h.1
    · exact absurd (e.symm ▸ List.mem_map_of_mem hx) h.1
    · exact inj_of_nodup_map h.2 hx hy e

theorem elaborateMap_ok {D : ActsDoc} {U' : UDoc} {M : SplitMap} (h : elaborateMap D = .ok (U', M)) :
    (∃ Rs, D.acts.mapM (fun x => readingOf D x.1 x.2) = .ok Rs) ∧ namesOk D = .ok () ∧ U' = splitDoc D ∧
    M = splitMap D ∧ WellFormedU U' = true ∧ (M.rules.all fun x => !U'.D.T.nodes.any (·.name == x.2.1)) = true := by
  unfold elaborateMap at h
  cases h1 : D.acts.mapM (fun x => readingOf D x.1 x.2) <;> simp only [h1, bind, Except.bind] at h
  · cases h
  cases h2 : refsOk D <;> simp only [h2] at h
  · cases h
  cases h3 : namesOk D <;> simp only [h3] at h
  · cases h
  cases h4 : partsDistinct D <;> simp only [h4] at h
  · cases h
  cases h5 : validate (splitDoc D).D <;> simp only [h5] at h
  · cases h
  split at h
  next hb =>
    simp only [pure, Except.pure, Except.ok.injEq, Prod.mk.injEq] at h
    obtain ⟨rfl, rfl⟩ := h
    rw [Bool.and_eq_true] at hb
    exact ⟨⟨_, rfl⟩, rfl, rfl, rfl, hb.1, hb.2⟩
  next => cases h

theorem namesOk_ok {D : ActsDoc} (h : namesOk D = .ok ()) :
    (∀ q ∈ (splitMap D).preds.map (·.1), (∀ r ∈ D.U.D.T.regulated, r.name ≠ q) ∧ q ∉ D.U.unspec) ∧
    ((splitMap D).preds.map (·.1)).Nodup ∧
    (∀ n ∈ (splitMap D).rules.map (·.1), ∀ N ∈ D.U.D.T.nodes, N.name ≠ n) ∧ ((splitMap D).rules.map (·.1)).Nodup := by
  unfold namesOk at h
  dsimp only at h
  split at h
  · cases h
  · cases h
  next hq hn =>
    have hq := List.find?_eq_none.mp hq
    have hn := List.find?_eq_none.mp hn
    refine ⟨fun q m => ?_, List.nodup_iff_count.mpr fun q => ?_, fun n m N hN e => ?_,
      List.nodup_iff_count.mpr fun n => ?_⟩
    · have := hq q m
      simp only [Bool.or_eq_true, decide_eq_true_eq, List.any_eq_true, beq_iff_eq, List.contains_iff_mem,
        not_or] at this
      exact ⟨fun r hr e => this.1.1.1.2 ⟨r, hr, e⟩, this.1.1.2⟩
    · by_cases m : q ∈ (splitMap D).preds.map (·.1)
      · have := hq q m
        simp only [Bool.or_eq_true, decide_eq_true_eq, not_or] at this
        exact Nat.le_of_not_gt this.1.2
      · rw [List.count_eq_zero_of_not_mem m]; exact Nat.zero_le _
    · have := hn n m
      simp only [Bool.or_eq_true, List.any_eq_true, beq_iff_eq, not_or] at this
      exact this.1.1 ⟨N, hN, e⟩
    · by_cases m : n ∈ (splitMap D).rules.map (·.1)
      · have := hn n m
        simp only [Bool.or_eq_true, decide_eq_true_eq, not_or] at this
        exact Nat.le_of_not_gt this.1.2
      · rw [List.count_eq_zero_of_not_mem m]; exact Nat.zero_le _

theorem mem_partsOf {D : ActsDoc} {p : String} {x : Atom × Nat} (h : x ∈ partsOf D p) :
    ∃ atoms, splitAtoms D p = some atoms ∧ 1 ≤ x.2 ∧ atoms[x.2 - 1]? = some x.1 := by
  unfold partsOf at h
  cases hs : splitAtoms D p with
  | none => simp [hs] at h
  | some atoms =>
    rw [hs, Option.getD_some, List.mem_zipIdx_iff_le_and_getElem?_sub] at h
    exact ⟨atoms, rfl, h⟩

theorem mem_preds {D : ActsDoc} {x : String × String × Nat} : x ∈ (splitMap D).preds ↔
    ∃ r ∈ D.U.D.T.regulated, ∃ y ∈ partsOf D r.name, x = (partPred r.name y.2, r.name, y.2) := by
  simp only [splitMap, List.mem_flatMap, List.mem_map]
  exact ⟨fun ⟨r, hr, y, hy, e⟩ => ⟨r, hr, y, hy, e.symm⟩, fun ⟨r, hr, y, hy, e⟩ => ⟨r, hr, y, hy, e.symm⟩⟩

theorem mem_rules {D : ActsDoc} {x : String × String × Nat} : x ∈ (splitMap D).rules ↔
    ∃ N ∈ D.U.D.T.nodes, ∃ y ∈ partsOf D N.pred, x = (partRule N.name y.2, N.name, y.2) := by
  simp only [splitMap, List.mem_flatMap, List.mem_map]
  exact ⟨fun ⟨N, hN, y, hy, e⟩ => ⟨N, hN, y, hy, e.symm⟩, fun ⟨N, hN, y, hy, e⟩ => ⟨N, hN, y, hy, e.symm⟩⟩

theorem mem_splitReg {D : ActsDoc} {r s : Regulated} : s ∈ splitReg D r ↔ (partsOf D r.name = [] ∧ s = r) ∨
    ∃ x ∈ partsOf D r.name, s = { r with name := partPred r.name x.2, act := some (partAct D.fixed r.role x.1),
                                         permission := r.permission.map (partPred · x.2) } := by
  unfold splitReg
  cases partsOf D r.name with
  | nil => simp
  | cons y ys =>
    simp only [List.mem_map, reduceCtorEq, false_and, false_or]
    constructor <;> rintro ⟨x, hx, e⟩ <;> exact ⟨x, hx, e.symm⟩

theorem mem_splitNode {D : ActsDoc} {N K : Node} : K ∈ splitNode D N ↔ (partsOf D N.pred = [] ∧ K = N) ∨
    ∃ x ∈ partsOf D N.pred, K = { N with name := partRule N.name x.2, pred := partPred N.pred x.2,
                                         over := N.over.map (partRule · x.2) } := by
  unfold splitNode
  cases partsOf D N.pred with
  | nil => simp
  | cons y ys =>
    simp only [List.mem_map, reduceCtorEq, false_and, false_or]
    constructor <;> rintro ⟨x, hx, e⟩ <;> exact ⟨x, hx, e.symm⟩

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

theorem splitMap_exact (D : ActsDoc) {U' : VE.NormDefaults.UDoc} {M : SplitMap} (h : elaborateMap D = .ok (U', M)) :
    (∀ q, (q ∈ U'.D.T.regulated.map (·.name) ∧ q ∉ D.U.D.T.regulated.map (·.name)) ↔ ∃ p i, (q, p, i) ∈ M.preds) ∧
    (∀ n, (n ∈ U'.D.T.nodes.map (·.name) ∧ n ∉ D.U.D.T.nodes.map (·.name)) ↔ ∃ m i, (n, m, i) ∈ M.rules) ∧
    (∀ q p i, (q, p, i) ∈ M.preds →
      q = partPred p i ∧ p ∈ D.U.D.T.regulated.map (·.name) ∧ p ∉ U'.D.T.regulated.map (·.name) ∧ 1 ≤ i) ∧
    (∀ n m i, (n, m, i) ∈ M.rules →
      n = partRule m i ∧ m ∈ D.U.D.T.nodes.map (·.name) ∧ m ∉ U'.D.T.nodes.map (·.name) ∧ 1 ≤ i) ∧
    (∀ q p i j, (q, p, i) ∈ M.preds → 1 ≤ j → j ≤ i → ∃ q', (q', p, j) ∈ M.preds) ∧
    (M.preds.map (·.1)).Nodup ∧ (M.rules.map (·.1)).Nodup := by
  obtain ⟨_, hn, rfl, rfl, _, hb⟩ := elaborateMap_ok h
  obtain ⟨hq, hqd, hr, hrd⟩ := namesOk_ok hn
  simp only [splitDoc, List.mem_map, List.mem_flatMap, not_exists, not_and]
  refine ⟨fun q => ⟨?_, ?_⟩, fun n => ⟨?_, ?_⟩, fun q p i hm => ?_, fun n m i hm => ?_, fun q p i j hm h1 hj => ?_,
    hqd, hrd⟩
  · rintro ⟨⟨s, ⟨r, hr, hs⟩, rfl⟩, hnot⟩
    rcases mem_splitReg.mp hs with ⟨_, rfl⟩ | ⟨x, hx, rfl⟩
    · exact absurd rfl (hnot s hr)
    · exact ⟨r.name, x.2, mem_preds.mpr ⟨r, hr, x, hx, rfl⟩⟩
  · rintro ⟨p, i, hm⟩
    obtain ⟨r, hr', y, hy, e⟩ := mem_preds.mp hm
    simp only [Prod.mk.injEq] at e
    obtain ⟨rfl, rfl, rfl⟩ := e
    exact ⟨⟨_, ⟨r, hr', mem_splitReg.mpr (.inr ⟨y, hy, rfl⟩)⟩, rfl⟩,
      fun r' hr'' => (hq _ (List.mem_map_of_mem hm)).1 r' hr''⟩
  · rintro ⟨⟨K, ⟨N, hN, hK⟩, rfl⟩, hnot⟩
    rcases mem_splitNode.mp hK with ⟨_, rfl⟩ | ⟨x, hx, rfl⟩
    · exact absurd rfl (hnot K hN)
    · exact ⟨N.name, x.2, mem_rules.mpr ⟨N, hN, x, hx, rfl⟩⟩
  · rintro ⟨m, i, hm⟩
    obtain ⟨N, hN, y, hy, e⟩ := mem_rules.mp hm
    simp only [Prod.mk.injEq] at e
    obtain ⟨rfl, rfl, rfl⟩ := e
    exact ⟨⟨_, ⟨N, hN, mem_splitNode.mpr (.inr ⟨y, hy, rfl⟩)⟩, rfl⟩,
      fun N' hN' => hr _ (List.mem_map_of_mem hm) N' hN'⟩
  · obtain ⟨r, hr', y, hy, e⟩ := mem_preds.mp hm
    simp only [Prod.mk.injEq] at e
    obtain ⟨rfl, rfl, rfl⟩ := e
    obtain ⟨_, _, h1, _⟩ := mem_partsOf hy
    refine ⟨rfl, ⟨r, hr', rfl⟩, ?_, h1⟩
    rintro s ⟨r', hr'', hs⟩ e
    rcases mem_splitReg.mp hs with ⟨he, rfl⟩ | ⟨x, hx, rfl⟩
    · rw [e] at he; rw [he] at hy; cases hy
    · exact (hq _ (List.mem_map_of_mem (mem_preds.mpr ⟨r', hr'', x, hx, rfl⟩))).1 r hr' e.symm
  · obtain ⟨N, hN, y, hy, e⟩ := mem_rules.mp hm
    simp only [Prod.mk.injEq] at e
    obtain ⟨rfl, rfl, rfl⟩ := e
    obtain ⟨_, _, h1, _⟩ := mem_partsOf hy
    refine ⟨rfl, ⟨N, hN, rfl⟩, ?_, h1⟩
    rintro K ⟨N', hN', hK⟩ e
    have := List.all_eq_true.mp hb _ hm
    simp only [Bool.not_eq_true', List.any_eq_false, beq_iff_eq] at this
    exact this K (List.mem_flatMap.mpr ⟨N', hN', hK⟩) e
  · obtain ⟨r, hr', y, hy, e⟩ := mem_preds.mp hm
    simp only [Prod.mk.injEq] at e
    obtain ⟨rfl, rfl, rfl⟩ := e
    obtain ⟨atoms, hs, _, ha⟩ := mem_partsOf hy
    have hlt : j - 1 < atoms.length := by
      have := (List.getElem?_eq_some_iff.mp ha).1; omega
    refine ⟨partPred r.name j, mem_preds.mpr ⟨r, hr', (atoms[j - 1], j), ?_, rfl⟩⟩
    rw [partsOf, hs, Option.getD_some, List.mem_zipIdx_iff_le_and_getElem?_sub]
    exact ⟨h1, List.getElem?_eq_getElem hlt⟩

/-- What a part contains (SR9): part i of `p` is `p`'s declaration with atom i's act and the dual's part i, and keeps
    `p`'s sorts, role and completion; part rule i of `N` is `N` on part i with its `over` mapped, every other field
    copied. -/
theorem elaborate_parts (D : ActsDoc) {U' : VE.NormDefaults.UDoc} {M : SplitMap} (h : elaborateMap D = .ok (U', M)) :
    (∀ q p i, (q, p, i) ∈ M.preds → ∃ r ∈ D.U.D.T.regulated, r.name = p ∧ ∃ atoms a, splitAtoms D p = some atoms ∧
       atoms[i - 1]? = some a ∧
       U'.D.T.regulated.find? (·.name == q) =
         some { r with name := q, act := some (partAct D.fixed r.role a),
                       permission := r.permission.map (partPred · i) } ∧
       U'.D.E.predicates q = D.U.D.E.predicates p ∧ (q ∈ U'.unspec ↔ p ∈ D.U.unspec)) ∧
    (∀ n m i, (n, m, i) ∈ M.rules → ∃ N ∈ D.U.D.T.nodes, N.name = m ∧
       U'.D.T.nodes.find? (·.name == n) =
         some { N with name := n, pred := partPred N.pred i, over := N.over.map (partRule · i) }) := by
  obtain ⟨_, hn, rfl, rfl, _, _⟩ := elaborateMap_ok h
  obtain ⟨hq, hqd, hr, hrd⟩ := namesOk_ok hn
  refine ⟨fun q p i hm => ?_, fun n m i hm => ?_⟩
  · have hqm := List.mem_map_of_mem (f := (·.1)) hm
    -- the first regulated predicate of the result named `q` is a part, and its map entry is `(q, p, i)`
    obtain ⟨r0, hr0, y0, hy0, e0⟩ := mem_preds.mp hm
    cases hf : (splitDoc D).D.T.regulated.find? (·.name == q) with
    | none =>
      have := List.find?_eq_none.mp hf _ (List.mem_flatMap.mpr ⟨r0, hr0, mem_splitReg.mpr (.inr ⟨y0, hy0, rfl⟩)⟩)
      simp only [Prod.mk.injEq] at e0
      simp [e0.1] at this
    | some z =>
      have hz := List.mem_flatMap.mp (List.mem_of_find?_eq_some hf)
      have hzq : z.name = q := by simpa using List.find?_some hf
      obtain ⟨r, hr', hzr⟩ := hz
      rcases mem_splitReg.mp hzr with ⟨_, rfl⟩ | ⟨x, hx, rfl⟩
      · exact absurd hzq ((hq q hqm).1 z hr')
      · have hw := mem_preds.mpr ⟨r, hr', x, hx, rfl⟩
        have e := inj_of_nodup_map hqd hw hm hzq
        simp only [Prod.mk.injEq] at e
        obtain ⟨rfl, rfl, rfl⟩ := e
        obtain ⟨atoms, hs, _, ha⟩ := mem_partsOf hx
        refine ⟨r, hr', rfl, atoms, x.1, hs, ha, rfl, ?_, ?_⟩
        · simp only [splitDoc, splitEnv]
          cases hg : (splitMap D).preds.find? (·.1 == partPred r.name x.2) with
          | none => have := List.find?_eq_none.mp hg _ hm; simp at this
          | some w =>
            have hw' : w.1 = partPred r.name x.2 := by simpa using List.find?_some hg
            rw [inj_of_nodup_map hqd (List.mem_of_find?_eq_some hg) hm hw']
        · simp only [splitDoc, List.mem_flatMap]
          constructor
          · rintro ⟨p', hp', hq'⟩
            unfold partNames at hq'
            split at hq'
            · simp only [List.mem_singleton] at hq'
              exact absurd (hq' ▸ hp') (hq _ hqm).2
            · obtain ⟨w, hwf, hw1⟩ := List.mem_map.mp hq'
              obtain ⟨hwm, hwp⟩ := List.mem_filter.mp hwf
              rw [inj_of_nodup_map hqd hwm hm hw1] at hwp
              simp only [beq_iff_eq] at hwp
              exact hwp ▸ hp'
          · intro hp
            refine ⟨r.name, hp, ?_⟩
            unfold partNames
            have hmf : (partPred r.name x.2, r.name, x.2) ∈ (splitMap D).preds.filter (·.2.1 == r.name) :=
              List.mem_filter.mpr ⟨hm, by simp⟩
            split
            next he => rw [he] at hmf; cases hmf
            · exact List.mem_map_of_mem (f := (·.1)) hmf
  · have hnm := List.mem_map_of_mem (f := (·.1)) hm
    obtain ⟨N0, hN0, y0, hy0, e0⟩ := mem_rules.mp hm
    cases hf : (splitDoc D).D.T.nodes.find? (·.name == n) with
    | none =>
      have := List.find?_eq_none.mp hf _ (List.mem_flatMap.mpr ⟨N0, hN0, mem_splitNode.mpr (.inr ⟨y0, hy0, rfl⟩)⟩)
      simp only [Prod.mk.injEq] at e0
      simp [e0.1] at this
    | some z =>
      have hzn : z.name = n := by simpa using List.find?_some hf
      obtain ⟨N, hN, hzN⟩ := List.mem_flatMap.mp (List.mem_of_find?_eq_some hf)
      rcases mem_splitNode.mp hzN with ⟨_, rfl⟩ | ⟨x, hx, rfl⟩
      · exact absurd hzn (hr n hnm z hN)
      · have e := inj_of_nodup_map hrd (mem_rules.mpr ⟨N, hN, x, hx, rfl⟩) hm hzn
        simp only [Prod.mk.injEq] at e
        obtain ⟨rfl, rfl, rfl⟩ := e
        exact ⟨N, hN, rfl, rfl⟩

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

end VE.Acts
