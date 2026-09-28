import VE.Discourse.Elaborate

/-! # Resolution and acceptance (docs/spec/discourse.md 4.3, 9.2)

`Accepted D u s A` fixes one recorded, typed derivation and assignment and requires every
competitor (any derivation of `s`, any accessible assignment of its slots) whose
elaboration is closed and well typed to equal it: the same tree, the same slots and the
same targets modulo declared aliases. The type check is the only filter on competitors:
recorded targets are the comparison point (`σ m = K.target(m)`), never a filter, and the
recorded readings are a fixed input of the elaboration.

`validate` is the executable validator. It enumerates every derivation (`derivs`, complete
by `mem_derivs`) and every accessible assignment of their slots whose targets can
elaborate, keeps the type-checking competitors, and requires them all to agree with the
recorded assignment. Resource exhaustion is `ResourceLimit: resolution`, never uniqueness. -/
namespace VE.Discourse
open VE.English (Tok)

/-- One recorded, typed (d, σ) first; every type-checking competitor equals it. The type
check is the only filter. -/
def Accepted (D : DDoc) (u : String) (s : List Tok) (A : VE.Formula) : Prop :=
  ∃ d σ, Derives D u s d ∧ (∀ m ∈ d.slots, Acc D m (σ m) ∧ recordedTarget D m = some (σ m)) ∧
    elaborateD D d σ = some A ∧ A.check D.E [] = true ∧
    ∀ d' σ' A', Derives D u s d' → (∀ m ∈ d'.slots, Acc D m (σ' m)) →
      elaborateD D d' σ' = some A' → A'.check D.E [] = true →
      d'.tree = d.tree ∧ d'.slots = d.slots ∧ ∀ m ∈ d.slots, AliasEq D (σ' m) (σ m)

/-- Exactly one accepted formula. -/
theorem accepted_unique (D : DDoc) (u : String) (s : List Tok) (A A' : VE.Formula)
    (h : Accepted D u s A) (h' : Accepted D u s A') : A = A' := by
  obtain ⟨d, σ, hd, _, he, _, hall⟩ := h
  obtain ⟨d', σ', hd', hr', he', hc', _⟩ := h'
  obtain ⟨ht, hsl, hal⟩ := hall d' σ' A' hd' (fun m hm => (hr' m hm).1) he' hc'
  have : elaborateD D d' σ' = elaborateD D d σ := by
    rw [elaborate_alias D d' σ' σ (fun m hm => by
      rw [← hd'.1, hsl] at hm; exact hal m hm)]
    rcases d with ⟨t, sl⟩
    rcases d' with ⟨t', sl'⟩
    simp only at ht hsl
    subst ht hsl
    rfl
  rw [he', he] at this
  exact (Option.some.inj this).symm

/-- The type check is the only filter: a type-checking competitor is the accepted formula. -/
theorem accepted_no_pruning (D : DDoc) (u : String) (s : List Tok) (A : VE.Formula) (h : Accepted D u s A)
    (d' : DTree) (σ' : Assignment) (A' : VE.Formula) (hd : Derives D u s d') (ha : ∀ m ∈ d'.slots, Acc D m (σ' m))
    (he : elaborateD D d' σ' = some A') (hc : A'.check D.E [] = true) : A' = A := by
  obtain ⟨d, σ, _, _, he₀, _, hall⟩ := h
  obtain ⟨ht, hsl, hal⟩ := hall d' σ' A' hd ha he hc
  have : elaborateD D d' σ' = elaborateD D d σ := by
    rw [elaborate_alias D d' σ' σ (fun m hm => by rw [← hd.1, hsl] at hm; exact hal m hm)]
    rcases d with ⟨t, sl⟩
    rcases d' with ⟨t', sl'⟩
    simp only at ht hsl
    subst ht hsl
    rfl
  rw [he, he₀] at this
  exact Option.some.inj this

/-! ## Slot candidates -/

/-- The accessible targets of a slot that can elaborate (entity, predicate, document or claim
targets), by form. -/
def slotCands (D : DDoc) (m : Slot) : List Target :=
  let consts := D.K.names.map Name.constant
  match m.form with
  | .pronoun | .demonstrative | .possessive => consts.map entityTarget
  | .definite => [entityTarget "binder:0"]
  | .plural => (earlierPairs D m).map fun p => listTarget [p.1, p.2]
  | .ordinalPair => (earlierPairs D m).flatMap fun p => [pairTarget p.1 p, pairTarget p.2 p]
  | .such => (earlierProperties D m).map fun p => predTarget p.1
  | .definitionRef => match namedSection D m with
    | some a => a.exports.map predTarget
    | none => []
  | .documentName => D.K.documents.map fun d => namedTarget .document d.name
  | .citation => (lemmaNames D).map (namedTarget .claim)
  | .sectionRef | .navigation => []

def okKind (t : Target) : Bool :=
  t.kind == .entity || t.kind == .predicate || t.kind == .document || t.kind == .claim

theorem slotCands_complete (D : DDoc) (m : Slot) (t : Target) (h : accB D m t = true) (hk : okKind t = true) :
    t ∈ slotCands D m := by
  unfold accB at h
  simp only [Bool.and_eq_true] at h
  obtain ⟨hfit, h⟩ := h
  split at h
  · rename_i c
    split at h
    · simp only [Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq, pronounLike] at h
      obtain ⟨⟨hf, hc⟩, _⟩ := h
      have hmem := constAcc_mem hc
      unfold slotCands
      rcases hf with (hf | hf) | hf <;> simp only [hf] <;> exact List.mem_map.mpr ⟨c, hmem, rfl⟩
    · simp only [Bool.and_eq_true, beq_iff_eq] at h
      obtain ⟨rfl, hf⟩ := h
      unfold slotCands
      simp only [hf]
      exact List.mem_singleton_self _
  · rename_i ms
    simp only [Bool.and_eq_true, List.any_eq_true, beq_iff_eq] at h
    obtain ⟨⟨⟨hf, p, hp, rfl⟩, _⟩, _⟩ := h
    unfold slotCands
    simp only [hf]
    exact List.mem_map.mpr ⟨p, hp, rfl⟩
  · rename_i c p
    simp only [Bool.and_eq_true, List.contains_iff_mem, beq_iff_eq] at h
    obtain ⟨⟨⟨⟨hf, hp⟩, _⟩, _⟩, hk⟩ := h
    unfold slotCands
    simp only [hf]
    refine List.mem_flatMap.mpr ⟨p, hp, ?_⟩
    split at hk
    · simp only [beq_iff_eq] at hk; subst hk; simp [pairTarget]
    · simp only [beq_iff_eq] at hk; subst hk; simp [pairTarget]
    · cases hk
  · rename_i p
    simp only [Bool.and_eq_true, Bool.or_eq_true] at h
    obtain ⟨_, h | h⟩ := h
    · simp only [List.any_eq_true, beq_iff_eq, Bool.and_eq_true] at h
      obtain ⟨hf, x, hx, rfl⟩ := h
      unfold slotCands
      simp only [hf]
      exact List.mem_map.mpr ⟨x, hx, rfl⟩
    · obtain ⟨⟨hf, _⟩, h⟩ := h
      simp only [beq_iff_eq] at hf
      unfold slotCands
      simp only [hf]
      split at h
      · rename_i a ha
        simp only [ha]
        exact List.mem_map.mpr ⟨p, List.contains_iff_mem.mp h, rfl⟩
      · cases h
  · simp [okKind] at hk
  · simp [okKind] at hk
  · simp [okKind] at hk
  · rename_i l
    have hf : m.form = .citation := by
      revert hfit; cases hm : m.form <;> simp [formFits]
    unfold slotCands
    simp only [hf]
    exact List.mem_map.mpr ⟨l, List.contains_iff_mem.mp h, rfl⟩
  · rename_i d
    have hf : m.form = .documentName := by
      revert hfit; cases hm : m.form <;> simp [formFits]
    simp only [List.any_eq_true, Bool.and_eq_true, beq_iff_eq] at h
    obtain ⟨x, hx, rfl, _⟩ := h
    unfold slotCands
    simp only [hf]
    exact List.mem_map.mpr ⟨x, hx, rfl⟩
  · cases h

/-! ## Every target an elaboration reads has an elaborable kind -/

theorem canon_kind (D : DDoc) (t : Target) : (canonTarget D t).kind = t.kind := rfl

theorem okKind_canon (D : DDoc) (t : Target) (h : okKind (canonTarget D t) = true) : okKind t = true := by
  simpa [okKind, canon_kind] using h

theorem termConst_ok (t : Target) (c : String) (h : termConst t = some c) : okKind t = true := by
  unfold termConst at h
  split at h <;> first | rfl | cases h

theorem pluralMembers_ok (t : Target) (ms : List String) (h : pluralMembers t = some ms) : okKind t = true := by
  unfold pluralMembers at h
  split at h <;> first | rfl | cases h

theorem propertyOf_ok (t : Target) (q : String) (h : propertyOf t = some q) : okKind t = true := by
  unfold propertyOf at h
  split at h <;> first | rfl | cases h

theorem isClaim_ok (t : Target) (h : isClaim t = true) : okKind t = true := by
  unfold isClaim at h
  split at h <;> first | rfl | cases h

theorem npConsts_ok (D : DDoc) (σ : Assignment) (np : NP) (cs : List String) (h : npConsts D σ np = some cs) :
    ∀ m ∈ npSlots np, okKind (σ m) = true := by
  cases np with
  | name => simp [npSlots]
  | slot m =>
    intro x hx
    simp only [npSlots, List.mem_singleton] at hx
    subst hx
    simp only [npConsts] at h
    split at h
    · exact okKind_canon D _ (pluralMembers_ok _ cs h)
    · cases hc : termConst (canonTarget D (σ x)) with
      | none => rw [hc] at h; cases h
      | some c => exact okKind_canon D _ (termConst_ok _ c hc)
  | definite => simp [npConsts] at h

theorem predFormula_ok (D : DDoc) (σ : Assignment) (subj : NP) (p : String) (A : VE.Formula)
    (h : predFormula D σ subj p = some A) : ∀ m ∈ npSlots subj, okKind (σ m) = true := by
  cases subj with
  | definite m r =>
    simp only [predFormula, definiteFormula] at h
    split at h
    · rename_i hb
      intro x hx
      have hm : okKind (σ m) = true := okKind_canon D _ (by rw [hb]; simp [okKind, entityTarget])
      cases r with
      | noun q =>
        simp only [npSlots, List.mem_singleton] at hx
        subst hx; exact hm
      | rel q poss =>
        simp only [npSlots, List.mem_cons, List.not_mem_nil, or_false] at hx
        rcases hx with rfl | rfl
        · exact hm
        · cases hr : restrFormula D σ (.rel q x) with
          | none => rw [hr] at h; simp at h
          | some y =>
            simp only [restrFormula] at hr
            split at hr
            · rename_i s _ c _ hc
              exact okKind_canon D _ (termConst_ok _ c hc)
            · cases hr
    · cases h
  | name c k => simp [npSlots]
  | slot m =>
    simp only [predFormula] at h
    cases hc : npConsts D σ (.slot m) with
    | none => rw [hc] at h; cases h
    | some cs => exact npConsts_ok D σ _ cs hc

theorem coreFormula_ok (D : DDoc) (σ : Assignment) (c : Core) (A : VE.Formula) (h : coreFormula D σ c = some A) :
    ∀ m ∈ coreSlots c, okKind (σ m) = true := by
  cases c with
  | pred subj are p => exact predFormula_ok D σ subj p A h
  | coord => simp [coreSlots]
  | rel subj p obj =>
    simp only [coreFormula, relFormula] at h
    split at h
    · rename_i a b ha hb
      intro m hm
      rcases List.mem_append.mp hm with hm | hm
      · exact npConsts_ok D σ subj _ ha m hm
      · exact npConsts_ok D σ obj _ hb m hm
    · cases h
  | every md srt p =>
    simp only [coreFormula] at h
    intro m hm
    cases md with
    | slot x =>
      simp only [coreSlots, modSlots, List.mem_singleton] at hm
      subst hm
      simp only [modPred] at h
      cases hq : propertyOf (canonTarget D (σ m)) with
      | none => rw [hq] at h; cases h
      | some q => exact okKind_canon D _ (propertyOf_ok _ q hq)
    | _ => simp [coreSlots, modSlots] at hm
  | some an md srt p =>
    simp only [coreFormula] at h
    intro m hm
    cases md with
    | slot x =>
      simp only [coreSlots, modSlots, List.mem_singleton] at hm
      subst hm
      simp only [modPred] at h
      cases hq : propertyOf (canonTarget D (σ m)) with
      | none => rw [hq] at h; cases h
      | some q => exact okKind_canon D _ (propertyOf_ok _ q hq)
    | _ => simp [coreSlots, modSlots] at hm
  | everyDef x srt p sec =>
    simp only [coreFormula] at h
    intro m hm
    simp only [coreSlots, List.mem_singleton] at hm
    subst hm
    cases hq : propertyOf (canonTarget D (σ m)) with
    | none => rw [hq] at h; cases h
    | some q => exact okKind_canon D _ (propertyOf_ok _ q hq)

theorem elaborate_ok (D : DDoc) (d : DTree) (σ : Assignment) (A : VE.Formula) (h : elaborateD D d σ = some A) :
    ∀ m ∈ slotsOf d.tree, okKind (σ m) = true := by
  unfold elaborateD at h
  split at h
  · rename_i c hc
    rw [hc]
    exact coreFormula_ok D σ c A h
  · rename_i x c hc
    rw [hc]
    split at h
    · rename_i hcl
      intro m hm
      rcases List.mem_cons.mp hm with rfl | hm
      · exact okKind_canon D _ (isClaim_ok _ hcl)
      · exact coreFormula_ok D σ c A h m hm
    · cases h

/-! ## Assignments as vectors -/

def defaultTarget : Target := ⟨.entity, none, none, [], none, [], none⟩

def assignOf (slots : List Slot) (vec : List Target) : Assignment := fun m =>
  (((slots.zip vec).find? (·.1 == m)).map (·.2)).getD defaultTarget

theorem assignOf_map (σ : Assignment) : ∀ (slots : List Slot) (m : Slot), m ∈ slots →
    assignOf slots (slots.map σ) m = σ m
  | [], m, h => nomatch h
  | x :: xs, m, h => by
    unfold assignOf
    simp only [List.map_cons, List.zip_cons_cons, List.find?_cons]
    by_cases hx : x = m
    · subst hx; simp
    · have hne : (x == m) = false := by simpa using hx
      simp only [hne]
      have hm : m ∈ xs := by
        rcases List.mem_cons.mp h with h | h
        · exact absurd h.symm hx
        · exact h
      exact assignOf_map σ xs m hm

theorem assignOf_cons_self (x : Slot) (t : Target) (xs : List Slot) (vec : List Target) :
    assignOf (x :: xs) (t :: vec) x = t := by
  simp [assignOf]

theorem assignOf_cons_ne (x m : Slot) (t : Target) (xs : List Slot) (vec : List Target) (h : x ≠ m) :
    assignOf (x :: xs) (t :: vec) m = assignOf xs vec m := by
  have hne : (x == m) = false := by simpa using h
  simp [assignOf, hne]

def vectors : List (List Target) → List (List Target)
  | [] => [[]]
  | c :: cs => c.flatMap fun t => (vectors cs).map (t :: ·)

theorem map_mem_vectors (σ : Assignment) (f : Slot → List Target) : ∀ slots : List Slot,
    (∀ m ∈ slots, σ m ∈ f m) → slots.map σ ∈ vectors (slots.map f)
  | [], _ => by simp [vectors]
  | x :: xs, h => by
    simp only [List.map_cons, vectors, List.mem_flatMap, List.mem_map]
    exact ⟨σ x, h x List.mem_cons_self, xs.map σ,
      map_mem_vectors σ f xs (fun m hm => h m (List.mem_cons_of_mem _ hm)), rfl⟩

def recordedVec (D : DDoc) (d : DTree) : Option (List Target) := d.slots.mapM (recordedTarget D)

theorem mapM_recorded (D : DDoc) : ∀ (slots : List Slot) (vec : List Target),
    slots.mapM (recordedTarget D) = some vec →
      vec.length = slots.length ∧ ∀ m ∈ slots, recordedTarget D m = some (assignOf slots vec m)
  | [], vec, h => by
    simp only [List.mapM_nil, pure, Option.some.injEq] at h
    subst h; simp
  | x :: xs, vec, h => by
    simp only [List.mapM_cons, Option.bind_eq_bind] at h
    cases hx : recordedTarget D x with
    | none => rw [hx] at h; simp at h
    | some t =>
      rw [hx] at h
      simp only [Option.bind_some] at h
      cases hxs : xs.mapM (recordedTarget D) with
      | none => rw [hxs] at h; simp at h
      | some ts =>
        rw [hxs] at h
        simp only [Option.bind_some, pure, Option.some.injEq] at h
        subst h
        obtain ⟨hl, hr⟩ := mapM_recorded D xs ts hxs
        refine ⟨by simp [hl], fun m hm => ?_⟩
        by_cases hxm : x = m
        · subst hxm; rw [assignOf_cons_self]; exact hx
        · rw [assignOf_cons_ne x m t xs ts hxm]
          rcases List.mem_cons.mp hm with h | h
          · exact absurd h.symm hxm
          · exact hr m h

theorem mapM_of_recorded (D : DDoc) (σ : Assignment) : ∀ slots : List Slot,
    (∀ m ∈ slots, recordedTarget D m = some (σ m)) → slots.mapM (recordedTarget D) = some (slots.map σ)
  | [], _ => rfl
  | x :: xs, h => by
    simp only [List.mapM_cons, Option.bind_eq_bind, h x List.mem_cons_self, Option.bind_some,
      mapM_of_recorded D σ xs (fun m hm => h m (List.mem_cons_of_mem _ hm)), pure, List.map_cons]

theorem zip_all_assign (P : Slot → Target → Bool) : ∀ (slots : List Slot) (vec : List Target),
    vec.length = slots.length → ((slots.zip vec).all fun x => P x.1 x.2) = true →
      ∀ m ∈ slots, P m (assignOf slots vec m) = true
  | [], _, _, _, m, hm => nomatch hm
  | x :: xs, [], hl, _, _, _ => by simp at hl
  | x :: xs, t :: ts, hl, h, m, hm => by
    simp only [List.zip_cons_cons, List.all_cons, Bool.and_eq_true] at h
    by_cases hxm : x = m
    · subst hxm; rw [assignOf_cons_self]; exact h.1
    · rw [assignOf_cons_ne x m t xs ts hxm]
      rcases List.mem_cons.mp hm with h' | h'
      · exact absurd h'.symm hxm
      · exact zip_all_assign P xs ts (by simpa using hl) h.2 m h'

theorem zip_all_map (P : Slot → Target → Bool) (σ : Assignment) : ∀ slots : List Slot,
    (∀ m ∈ slots, P m (σ m) = true) → ((slots.zip (slots.map σ)).all fun x => P x.1 x.2) = true
  | [], _ => rfl
  | x :: xs, h => by
    simp only [List.map_cons, List.zip_cons_cons, List.all_cons, Bool.and_eq_true]
    exact ⟨h x List.mem_cons_self, zip_all_map P σ xs (fun m hm => h m (List.mem_cons_of_mem _ hm))⟩

/-! ## The validator -/

def mentionLimit : Nat := 4096
def workLimit : Nat := 1000000

def mentionIdAt (D : DDoc) (m : Slot) : String := ((mentionAt D m).map Mention.id).getD "?"

def targetText (t : Target) : String :=
  match t.name with
  | some n => n
  | none => if t.members.isEmpty then ", ".intercalate t.units else ", ".intercalate t.members

def spanText (m : Slot) : String := "[" ++ toString m.span.1 ++ ", " ++ toString m.span.2 ++ ")"

/-- The formula-producing forms: their mentions are slots of the unit's derivation. -/
def formulaForm (f : Form) : Bool :=
  !(f == .sectionRef || f == .navigation)

def slotBefore (a b : Slot) : Bool := a.span.1 < b.span.1 || (a.span.1 == b.span.1 && b.span.2 ≤ a.span.2)

/-- The formula-producing mentions of `u` as slots, source order: an enclosing slot before
its nested slots (4.3). -/
def recordedSlots (D : DDoc) (u : String) : List Slot :=
  ((D.K.mentions.filter fun x => x.unit == u && formulaForm x.form).map
    fun x => (⟨x.unit, x.span, x.form⟩ : Slot)).mergeSort slotBefore

def candCount (D : DDoc) (m : Slot) : Nat := (slotCands D m).length

/-- The number of competitor assignments, computed before any is built. -/
def workOf (D : DDoc) (ds : List DTree) : Nat :=
  ds.foldl (fun acc d => acc + (d.slots.map (candCount D)).foldl (· * ·) 1) 0

/-- The accessible, elaborable candidates of a slot. -/
def accCands (D : DDoc) (m : Slot) : List Target := (slotCands D m).filter (accB D m)

/-- Every type-checking competitor: a derivation, an accessible assignment of its slots, the formula. -/
def typedComps (D : DDoc) (ds : List DTree) : List (DTree × List Target × VE.Formula) :=
  ds.flatMap fun d => (vectors (d.slots.map (accCands D))).filterMap fun vec =>
    match elaborateD D d (assignOf d.slots vec) with
    | some A => if A.check D.E [] then some (d, vec, A) else none
    | none => none

/-- Two competitors agree: same tree, same slots, targets equal modulo aliases. -/
def aligned (D : DDoc) (d d' : DTree) (vec vec' : List Target) : Bool :=
  d'.tree == d.tree && d'.slots == d.slots &&
    d.slots.all fun m => decide (AliasEq D (assignOf d.slots vec' m) (assignOf d.slots vec m))

/-- A derivation all of whose (at least one) slots carry accessible recorded targets whose
elaboration is ill typed. -/
def illTypedOf (D : DDoc) (d : DTree) : Bool :=
  !d.slots.isEmpty && match recordedVec D d with
    | some vec => ((d.slots.zip vec).all fun x => accB D x.1 x.2) && match elaborateD D d (assignOf d.slots vec) with
      | some A => !A.check D.E []
      | none => false
    | none => false

/-! ## Which slot an ill-typed elaboration blames -/

/-- The sort a predicate expects at argument `k`. -/
def argSort (D : DDoc) (p : String) (k : Nat) : Option String := (D.E.predicates p).bind (·[k]?)

def constsFit (D : DDoc) (cs : Option (List String)) (s : Option String) : Bool :=
  match cs, s with
  | some cs, some s => cs.all fun c => D.E.constants c == some s
  | _, _ => false

def propertyFits (D : DDoc) (t : Target) (srt : String) : Bool :=
  match propertyOf (canonTarget D t) with
  | some q => D.E.predicates q == some [srt]
  | none => false

/-- Each slot of a noun phrase with whether its target fits the sort `s` its position
expects: a constant or member list by its declared sorts, a description by its
restriction's sort, a nested possessive by the relation's other argument sort. -/
def npFit (D : DDoc) (σ : Assignment) (np : NP) (s : Option String) : List (Slot × Bool) :=
  match np with
  | .name _ _ => []
  | .slot m => [(m, constsFit D (npConsts D σ (.slot m)) s)]
  | .definite m r =>
    let rs := (restrFormula D σ r).map Prod.fst
    (m, rs.isSome && rs == s) :: match r with
      | .noun _ => []
      | .rel q poss => [(poss, constsFit D ((termConst (canonTarget D (σ poss))).map ([·])) (argSort D q 1))]

def coreFit (D : DDoc) (σ : Assignment) : Core → List (Slot × Bool)
  | .pred subj _ p => npFit D σ subj (argSort D p 0)
  | .coord .. => []
  | .rel subj p obj => npFit D σ subj (argSort D p 0) ++ npFit D σ obj (argSort D p 1)
  | .every (.slot m) srt _ | .some _ (.slot m) srt _ => [(m, propertyFits D (σ m) srt)]
  | .every .. | .some .. => []
  | .everyDef m srt _ _ => [(m, propertyFits D (σ m) srt)]

def treeFit (D : DDoc) (σ : Assignment) : STree → List (Slot × Bool)
  | .core c => coreFit D σ c
  | .cite m c => (m, true) :: coreFit D σ c

/-- The slot an ill-typed elaboration blames (4.3, `IllTypedTarget: <mention>: <target>`):
the first slot, in source order, whose target does not fit the sort its position expects
(for "Her manager is ready." with `Her` → `api`, the possessive, not the description); the
first slot when every slot fits on its own. -/
def culprit (D : DDoc) (d : DTree) (σ : Assignment) : Option Slot :=
  match d.slots.find? (fun m => (treeFit D σ d.tree).any fun x => x.1 == m && !x.2) with
  | some m => some m
  | none => d.slots.head?

theorem culprit_mem (D : DDoc) (d : DTree) (σ : Assignment) (m : Slot) (h : culprit D d σ = some m) :
    m ∈ d.slots := by
  unfold culprit at h
  split at h
  · rename_i x hx
    cases h
    exact List.mem_of_find?_eq_some hx
  · exact List.mem_of_getElem? (by simpa [List.head?_eq_getElem?] using h)

def illTypedText (D : DDoc) (u : String) (d : DTree) : String :=
  match culprit D d (assignOf d.slots ((recordedVec D d).getD [])) with
  | some m => "IllTypedTarget: " ++ mentionIdAt D m ++ ": " ++ (((recordedTarget D m).map targetText).getD "?")
  | none => "IllTypedTarget: " ++ u

def definiteRestrs : STree → List (Slot × Restr)
  | .core (.pred (.definite m r) _ _) | .cite _ (.pred (.definite m r) _ _) => [(m, r)]
  | _ => []

/-- The recorded restriction of every definite equals the regenerated one (1.4). -/
def restrictionMismatch (D : DDoc) (d : DTree) (σ : Assignment) : Option Slot :=
  ((definiteRestrs d.tree).find? fun (m, r) => match (mentionAt D m).bind Mention.restriction with
    | some R => (restrFormula D σ r).map Prod.snd != some R
    | none => false).map Prod.fst

def firstBad (D : DDoc) (d : DTree) (vec : List Target) : String :=
  match (d.slots.zip vec).find? (fun x => !accB D x.1 x.2) with
  | some (m, t) =>
    if formFits m.form t.kind then "InaccessibleTarget: " ++ mentionIdAt D m ++ ": " ++ targetText t
    else "TargetKindMismatch: " ++ mentionIdAt D m
  | none => "UnresolvedReference: " ++ ((d.slots.head?.map (mentionIdAt D)).getD "?")

/-- No type-checking accessible competitor: the unit's first recorded slot is unresolved. -/
def unresolvedText (D : DDoc) (u : String) (s : List Tok) (ds : List DTree) : String :=
  match ds with
  | [] => match (recordedSlots D u).isEmpty, referenceIndex D s with
    | true, some i => "UnrecordedSlot: " ++ u ++ ": [" ++ toString i ++ ", " ++ toString (i + 1) ++ ")"
    | _, _ => "InvalidInput: unit " ++ u ++ " is outside the supported discourse fragment"
  | d :: _ => match d.slots.find? (fun m => (recordedTarget D m).isSome) with
    | some m => "UnresolvedReference: " ++ mentionIdAt D m
    | none => match d.slots.head? with
      | some m => "UnrecordedSlot: " ++ u ++ ": " ++ spanText m
      | none => "UnresolvedReference: " ++ u

def ambiguityText (D : DDoc) (u : String) (d d' : DTree) (vec vec' : List Target) : String :=
  if d'.tree == d.tree && d'.slots == d.slots then
    match d.slots.find? (fun m => !decide (AliasEq D (assignOf d.slots vec' m) (assignOf d.slots vec m))) with
    | some m => "AmbiguousReference: " ++ mentionIdAt D m ++ ": " ++ targetText (assignOf d.slots vec m) ++ ", " ++
        targetText (assignOf d.slots vec' m)
    | none => "AmbiguousReference: " ++ u
  else "AmbiguityError: " ++ u ++ " has more than one derivation"

def slotMismatchText (D : DDoc) (u : String) (d : DTree) : String :=
  match (recordedSlots D u).find? (fun m => !d.slots.contains m) with
  | some m => "MentionNotSlot: " ++ mentionIdAt D m
  | none => match d.slots.find? (fun m => !(recordedSlots D u).contains m) with
    | some m => "UnrecordedSlot: " ++ u ++ ": " ++ spanText m
    | none => "UnrecordedSlot: " ++ u

/-- After uniqueness: the recorded assignment, its accessibility, its agreement with the
unique competitor, slot correspondence, the restrictions, and its typed elaboration. -/
def checkRecorded (D : DDoc) (u : String) (d : DTree) (vec : List Target) : Except String VE.Formula :=
  match recordedVec D d with
  | none => .error ("UnrecordedSlot: " ++ u ++ ": " ++
      (((d.slots.find? fun m => (recordedTarget D m).isNone).map spanText).getD "?"))
  | some rvec =>
    if !((d.slots.zip rvec).all fun x => accB D x.1 x.2) then .error (firstBad D d rvec)
    else if !aligned D d d vec rvec then .error ("ManifestMismatch: mentions." ++
      ((d.slots.find? (fun m => !decide (AliasEq D (assignOf d.slots rvec m) (assignOf d.slots vec m)))).map
        (mentionIdAt D)).getD u ++ ".target")
    else if recordedSlots D u != d.slots then .error (slotMismatchText D u d)
    else match restrictionMismatch D d (assignOf d.slots rvec) with
    | some m => .error ("ManifestMismatch: mentions." ++ mentionIdAt D m ++ ".restriction")
    | none => match elaborateD D d (assignOf d.slots rvec) with
      | some A => if A.check D.E [] then .ok A else .error (illTypedText D u d)
      | none => .error (firstBad D d rvec)

/-- The executable validator (untrusted proposals in, one formula out). -/
def validate (D : DDoc) (unit : String) : Except String VE.Formula :=
  if D.K.mentions.length > mentionLimit then .error "ResourceLimit: resolution" else
  match D.text unit with
  | none => .error ("InvalidInput: unit " ++ unit ++ " has no text")
  | some s =>
    let ds := derivs D unit s
    match ds.find? (illTypedOf D) with
    | some d => .error (illTypedText D unit d)
    | none =>
      if workOf D ds > workLimit then .error "ResourceLimit: resolution" else
      match typedComps D ds with
      | [] => .error (unresolvedText D unit s ds)
      | (d, vec, _) :: rest =>
        match rest.find? (fun x => !aligned D d x.1 vec x.2.1) with
        | some x => .error (ambiguityText D unit d x.1 vec x.2.1)
        | none => checkRecorded D unit d vec

/-- The supported fragment: within the validator's budgets. -/
def Supported (D : DDoc) (u : String) (s : List Tok) : Prop :=
  D.K.mentions.length ≤ mentionLimit ∧ workOf D (derivs D u s) ≤ workLimit

/-! ## Proofs about the validator (9.2) -/

/-- What a successful validation establishes, read off the validator. -/
structure ValidOk (D : DDoc) (u : String) (A : VE.Formula) : Prop where
  budget : D.K.mentions.length ≤ mentionLimit
  spec : ∃ s d vec A₀ rest rvec, D.text u = some s ∧ (derivs D u s).find? (illTypedOf D) = none ∧
    typedComps D (derivs D u s) = (d, vec, A₀) :: rest ∧
    (∀ x ∈ rest, aligned D d x.1 vec x.2.1 = true) ∧
    recordedVec D d = some rvec ∧ ((d.slots.zip rvec).all fun x => accB D x.1 x.2) = true ∧
    aligned D d d vec rvec = true ∧ recordedSlots D u = d.slots ∧
    elaborateD D d (assignOf d.slots rvec) = some A ∧ A.check D.E [] = true

theorem validate_ok (D : DDoc) (u : String) (A : VE.Formula) (h : validate D u = .ok A) : ValidOk D u A := by
  unfold validate at h
  split at h
  · cases h
  · rename_i hb
    refine ⟨Nat.le_of_not_gt hb, ?_⟩
    split at h
    · cases h
    · rename_i s hs
      dsimp only at h
      split at h
      · cases h
      · rename_i hill
        split at h
        · cases h
        · split at h
          · cases h
          · rename_i d vec A₀ rest hc
            split at h
            · cases h
            · rename_i hrest
              have hal : ∀ x ∈ rest, aligned D d x.1 vec x.2.1 = true := by
                intro x hx
                have := List.find?_eq_none.mp hrest x hx
                simpa using this
              unfold checkRecorded at h
              split at h
              · cases h
              · rename_i rvec hr
                split at h
                · cases h
                · rename_i hacc
                  split at h
                  · cases h
                  · rename_i halign
                    split at h
                    · cases h
                    · rename_i hslots
                      split at h
                      · cases h
                      · split at h
                        · rename_i A' hA
                          split at h
                          · rename_i hck
                            cases h
                            exact ⟨s, d, vec, A₀, rest, rvec, hs, hill, hc, hal, hr,
                              by simpa using hacc, by simpa using halign, by simpa using hslots, hA, hck⟩
                          · cases h
                        · cases h

theorem mem_typedComps (D : DDoc) (ds : List DTree) (d : DTree) (vec : List Target) (A : VE.Formula) :
    (d, vec, A) ∈ typedComps D ds ↔ d ∈ ds ∧ vec ∈ vectors (d.slots.map (accCands D)) ∧
      elaborateD D d (assignOf d.slots vec) = some A ∧ A.check D.E [] = true := by
  unfold typedComps
  simp only [List.mem_flatMap, List.mem_filterMap]
  constructor
  · rintro ⟨d', hd', vec', hv', hx⟩
    split at hx
    · rename_i A' hA'
      split at hx
      · rename_i hck
        simp only [Option.some.injEq, Prod.mk.injEq] at hx
        obtain ⟨rfl, rfl, rfl⟩ := hx
        exact ⟨hd', hv', hA', hck⟩
      · cases hx
    · cases hx
  · rintro ⟨hd, hv, hA, hck⟩
    exact ⟨d, hd, vec, hv, by simp [hA, hck]⟩

theorem aligned_spec {D : DDoc} {d d' : DTree} {vec vec' : List Target} (h : aligned D d d' vec vec' = true) :
    d'.tree = d.tree ∧ d'.slots = d.slots ∧
      ∀ m ∈ d.slots, AliasEq D (assignOf d.slots vec' m) (assignOf d.slots vec m) := by
  simp only [aligned, Bool.and_eq_true, beq_iff_eq, List.all_eq_true, decide_eq_true_eq] at h
  exact ⟨h.1.1, h.1.2, h.2⟩

theorem aligned_refl (D : DDoc) (d : DTree) (vec : List Target) : aligned D d d vec vec = true := by
  simp [aligned, AliasEq]

/-- The validator is sound: whatever it returns is the unique accepted resolution of that
unit's text. -/
theorem validate_accepted (D : DDoc) (u : String) (A : VE.Formula) (s : List Tok) (hs : D.text u = some s)
    (hv : validate D u = .ok A) : Accepted D u s A := by
  obtain ⟨_, s', d, vec, A₀, rest, rvec, hs', _, hc, hal, hr, hacc, halign, _, hA, hck⟩ := validate_ok D u A hv
  rw [hs] at hs'
  cases hs'
  have hmem : (d, vec, A₀) ∈ typedComps D (derivs D u s) := by rw [hc]; exact List.mem_cons_self
  obtain ⟨hd, _, _, _⟩ := (mem_typedComps D _ d vec A₀).mp hmem
  obtain ⟨hlen, hrec⟩ := mapM_recorded D d.slots rvec hr
  have hacc' := zip_all_assign (fun m t => accB D m t) d.slots rvec hlen hacc
  refine ⟨d, assignOf d.slots rvec, (mem_derivs D u s d).mp hd, fun m hm => ⟨hacc' m hm, hrec m hm⟩, hA, hck, ?_⟩
  intro d' σ' A' hd' ha' he' hc'
  have hsl : d'.slots = slotsOf d'.tree := hd'.1
  have hok := elaborate_ok D d' σ' A' he'
  have hvec : d'.slots.map σ' ∈ vectors (d'.slots.map (accCands D)) :=
    map_mem_vectors σ' (accCands D) d'.slots fun m hm => List.mem_filter.mpr
      ⟨slotCands_complete D m (σ' m) (ha' m hm) (hok m (by rw [← hsl]; exact hm)), ha' m hm⟩
  have he'' : elaborateD D d' (assignOf d'.slots (d'.slots.map σ')) = some A' := by
    rw [elaborate_congr D d' _ σ' (fun m hm => assignOf_map σ' d'.slots m (by rw [hsl]; exact hm))]
    exact he'
  have hm' : (d', d'.slots.map σ', A') ∈ typedComps D (derivs D u s) :=
    (mem_typedComps D _ _ _ _).mpr ⟨(mem_derivs D u s d').mpr hd', hvec, he'', hc'⟩
  have hal' : aligned D d d' vec (d'.slots.map σ') = true := by
    rw [hc] at hm'
    rcases List.mem_cons.mp hm' with he | he
    · simp only [Prod.mk.injEq] at he
      obtain ⟨rfl, hv, _⟩ := he
      rw [← hv]
      exact aligned_refl D d' _
    · exact hal _ he
  obtain ⟨ht, hsl', hali⟩ := aligned_spec hal'
  obtain ⟨_, _, hali₀⟩ := aligned_spec halign
  refine ⟨ht, hsl', fun m hm => ?_⟩
  have e1 := hali m hm
  have e2 := hali₀ m hm
  have e3 : assignOf d.slots (d'.slots.map σ') m = σ' m := by
    rw [← hsl']; exact assignOf_map σ' d'.slots m (by rw [hsl']; exact hm)
  unfold AliasEq at e1 e2 ⊢
  rw [← e3, e1, e2]


/-- Slot correspondence: the recorded formula-producing mentions of the unit are the accepted
derivation's slots. -/
theorem validate_recorded (D : DDoc) (u : String) (A : VE.Formula) (s : List Tok) (hs : D.text u = some s)
    (hv : validate D u = .ok A) :
    ∃ d σ, Derives D u s d ∧ (∀ m ∈ d.slots, recordedTarget D m = some (σ m)) ∧ elaborateD D d σ = some A ∧
      recordedSlots D u = d.slots := by
  obtain ⟨_, s', d, vec, A₀, rest, rvec, hs', _, hc, _, hr, _, _, hslots, hA, _⟩ := validate_ok D u A hv
  rw [hs] at hs'
  cases hs'
  have hmem : (d, vec, A₀) ∈ typedComps D (derivs D u s) := by rw [hc]; exact List.mem_cons_self
  obtain ⟨hd, _, _, _⟩ := (mem_typedComps D _ d vec A₀).mp hmem
  obtain ⟨_, hrec⟩ := mapM_recorded D d.slots rvec hr
  exact ⟨d, assignOf d.slots rvec, (mem_derivs D u s d).mp hd, hrec, hA, hslots⟩

/-- Closed and typed. -/
theorem validate_closed (D : DDoc) (u : String) (A : VE.Formula) (hv : validate D u = .ok A) :
    A.check D.E [] = true := by
  obtain ⟨_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, hck⟩ := validate_ok D u A hv
  exact hck

/-- Total: the validator never loops; resource exhaustion is the named error, never a formula. -/
theorem validate_total (D : DDoc) (u : String) :
    (∃ A, validate D u = .ok A) ∨ (∃ e, validate D u = .error e) := by
  cases validate D u with
  | ok A => exact Or.inl ⟨A, rfl⟩
  | error e => exact Or.inr ⟨e, rfl⟩

theorem validate_budget (D : DDoc) (u : String) (hover : D.K.mentions.length > mentionLimit) :
    validate D u = .error "ResourceLimit: resolution" := by
  unfold validate
  rw [if_pos hover]

/-- An ill-typed recorded elaboration is found by the validator, which names it. -/
theorem ill_typed_found (D : DDoc) (u : String) (s : List Tok) (hs : D.text u = some s)
    (hlim : D.K.mentions.length ≤ mentionLimit) (d : DTree) (σ : Assignment)
    (hd : Derives D u s d) (hr : ∀ m ∈ d.slots, Acc D m (σ m) ∧ recordedTarget D m = some (σ m))
    (m : Slot) (hm : m ∈ d.slots) (A : VE.Formula) (he : elaborateD D d σ = some A) (hc : A.check D.E [] = false) :
    ∃ d'', d'' ∈ derivs D u s ∧ illTypedOf D d'' = true ∧ validate D u = .error (illTypedText D u d'') := by
  have hill : illTypedOf D d = true := by
    have hne : d.slots.isEmpty = false := by
      cases hsl : d.slots with
      | nil => rw [hsl] at hm; cases hm
      | cons _ _ => rfl
    have hvec : recordedVec D d = some (d.slots.map σ) := mapM_of_recorded D σ d.slots (fun m hm => (hr m hm).2)
    have hel : elaborateD D d (assignOf d.slots (d.slots.map σ)) = some A := by
      rw [elaborate_congr D d _ σ (fun m hm => assignOf_map σ d.slots m (by rw [hd.1]; exact hm))]
      exact he
    simp only [illTypedOf, hne, Bool.not_false, Bool.true_and, hvec, hel, hc, Bool.not_false, Bool.and_true]
    exact zip_all_map (fun m t => accB D m t) σ d.slots (fun m hm => (hr m hm).1)
  have hd' : d ∈ derivs D u s := (mem_derivs D u s d).mpr hd
  unfold validate
  rw [if_neg (Nat.not_lt.mpr hlim), hs]
  dsimp only
  cases hf : (derivs D u s).find? (illTypedOf D) with
  | none => exact absurd (List.find?_eq_none.mp hf d hd') (by simp [hill])
  | some d'' => exact ⟨d'', List.mem_of_find?_eq_some hf, List.find?_some hf, rfl⟩

end VE.Discourse
