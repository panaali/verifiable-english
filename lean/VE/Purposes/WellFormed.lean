import VE.Purposes.Decl
import VE.Route.Inert

/-! Well-formedness of a `purposes` block (purpose-explanation plan 2.3, spec 4): the input is the checked units
and parts after the status fold (4.1); `check` refuses in spec 7.2's fault order (4.3); `check_ok_iff` says what
it decides (4.4). Purposes compiles nothing. -/

namespace VE.Purposes
open VE.Route.Admission (Kind)
open VE.Route.Gate (require)

structure Part where
  id         : String
  span       : Nat × Nat
  kind       : Kind
  status     : String          -- the W2 status name: CHECKED, OPEN, LABELLED or UNFORMALISED
  parent     : Option String   -- the MIXED unit a part belongs to
  formula    : Option VE.Formula
  candidates : List Kind       -- the kinds of the candidates of an active reading set on it; [] when none
  readings   : List String := []  -- PE-R8: those candidates' names, in the same order
  deriving Repr

structure Units where
  source : String
  parts  : List Part
  packSources : List String := []  -- PE-R11: the unit and part ids the list's pack premises in `X` are sourced to
  deriving Repr

def Units.find? (U : Units) (i : String) : Option Part := U.parts.find? (·.id == i)
def Units.kind? (U : Units) (i : String) : Option Kind := (U.find? i).map (·.kind)

def Ref.partId? : Ref → Option String
  | .part i => some i
  | .mention _ => none

def Link.partIds (L : Link) : List String := L.marker :: (L.reason ++ L.target).filterMap Ref.partId?

/-- Plan D3: the sides in W2's slot order, `causal r c e`. -/
def Link.slots (L : Link) : List Ref × List Ref :=
  match L.relation with
  | .because => (L.reason, L.target)
  | .inOrderTo => (L.target, L.reason)

def sideOfKind (U : Units) (s : List Ref) (k : Kind) : Bool :=
  !s.isEmpty && s.all fun r => match r.partId? with
    | some i => U.kind? i == some k
    | none => true

def markerAgrees (U : Units) (L : Link) : Bool :=
  match U.kind? L.marker with
  | some (.causal r c e) => r == L.relation.wire && sideOfKind U L.slots.1 c && sideOfKind U L.slots.2 e
  | _ => false

/-- PE-1: the marker and every side are distinct parts of one MIXED unit. PE-4 replaces it (A3). -/
def sameUnit (U : Units) (L : Link) : Bool :=
  (L.reason ++ L.target).all (·.partId?.isSome) && decide L.partIds.Nodup &&
  match (U.find? L.marker).bind (·.parent) with
  | some p => L.partIds.all fun i => (U.find? i).bind (·.parent) == some p
  | none => false

/-- SR 6: each side's parts are in source order and each part starts where the previous one ends. A mention fails
    it; PE-4 replaces it on resolved sides, as it replaces `sameUnit` (A3). -/
def sideAdjacent (U : Units) (s : List Ref) : Bool :=
  match s.mapM fun r => r.partId? >>= U.find? with
  | some ps => ps.all (fun p => p.span.1 ≤ p.span.2) && (ps.zip ps.tail).all fun (a, b) => a.span.2 == b.span.1
  | none => false

def sidesAdjacent (U : Units) (L : Link) : Bool := sideAdjacent U L.reason && sideAdjacent U L.target

/-- Other affirmed links with the same relation and target and a *different* reason list (A4). -/
def rivals (B : Block) (L : Link) : List Link :=
  B.links.filter fun M => M.id != L.id && M.polarity == .affirmed && M.relation == L.relation &&
    M.target == L.target && M.reason != L.reason

/-- A4 and SR 5 (E-d): `sole` is refused against a rival, and against any other affirmed link with the same relation
    and target whose share is `partly` or `notSole` ("only because B" with "not only because B"). -/
def shareOk (B : Block) (L : Link) : Bool :=
  match L.share with
  | .sole => (rivals B L).isEmpty && B.links.all fun M => M.id == L.id || M.polarity != .affirmed ||
      M.relation != L.relation || M.target != L.target || M.share == .plain || M.share == .sole
  | _ => true

/-- Under `purposes@0` every part of kind `causal because|in order to _ _` marks some link. -/
def markersLinked (U : Units) (B : Block) : Bool :=
  U.parts.all fun p => match p.kind with
    | .causal r _ _ => r == "prevents" || B.links.any (·.marker == p.id)
    | _ => true

def covered (U : Units) (s : List Ref) : Bool :=
  s.all fun r => match r.partId? >>= U.find? with
    | some p => p.status == "CHECKED" || p.status == "OPEN"
    | none => false

/-- The side the text does not state: a purpose, or the reason of a denied link (plan D8a). -/
def unstated (L : Link) : List Ref :=
  if L.relation == .inOrderTo || L.polarity == .denied then L.reason else []

/-- D8a, positively: every part on the unstated side, and every candidate of an active reading set on it, is inert.
    A mention there is refused until PE-4 resolves it. -/
def nonfactive (U : Units) (L : Link) : Bool :=
  (unstated L).all fun r => match r.partId? >>= U.find? with
    | some p => p.kind.inert && p.candidates.all Kind.inert
    | none => false

/-- Plan D4: a LABELLED marker marks a link whose two sides are CHECKED or OPEN. -/
def markerHonest (U : Units) (B : Block) : Bool :=
  U.parts.all fun p => p.status != "LABELLED" || !(B.links.any (·.marker == p.id)) ||
    B.links.any fun L => L.marker == p.id && covered U L.reason && covered U L.target

/-- PE-R11 (plan D8a): no pack premise is sourced to a part on the unstated side, or to that part's unit, which
    holds its bytes. -/
def packsInert (U : Units) (L : Link) : Bool :=
  (unstated L).all fun r => match r.partId? >>= U.find? with
    | some p => !(U.packSources.contains p.id) && !(p.parent.any U.packSources.contains)
    | none => false

/-- PE-R8: the kind the marker's slot gives the target (`slots`: the second slot for `because`, the first for
    `in order to`). -/
def targetKind (U : Units) (L : Link) : Option Kind :=
  match U.kind? L.marker with
  | some (.causal _ c e) => some (if L.relation == .because then e else c)
  | _ => none

/-- PE-R8: a candidate of a target part's active set holds the target when its kind is that kind. -/
def holdsTarget (U : Units) (L : Link) (k : Kind) : Bool := targetKind U L == some k

/-- PE-R8: for each target part with an active set, the names of the candidates that hold the target. -/
def shownUnder (U : Units) (L : Link) : List (String × List String) :=
  (L.target.filterMap fun r => r.partId? >>= U.find?).filterMap fun p =>
    if p.candidates.isEmpty then none
    else some (p.id, ((p.readings.zip p.candidates).filter (holdsTarget U L ·.2)).map (·.1))

/-- PE-R8: the parts of the marker's unit that no link of the block names and whose kind is not inert, in view
    order: a scope the link's quotes may leave out. -/
def unlinkedActive (U : Units) (B : Block) (L : Link) : List String :=
  match (U.find? L.marker).bind (·.parent) with
  | some u => (U.parts.filter fun p => p.parent == some u && !p.kind.inert &&
      !(B.links.any fun M => M.partIds.contains p.id)).map (·.id)
  | none => []

/-- Spec 4.3, in spec 7.2's fault order; each step is one `require` (`VE.Route.Gate.require`). -/
def check (U : Units) (B : Block) : Except String Unit := do
  require (decide (B.links.length ≤ maxLinks)) s!"ResourceLimit: purposes links exceed {maxLinks}"
  require (decide (B.links.map (·.id)).Nodup) "InvalidPurposes: two links have the same id"
  B.links.forM fun L => do
    L.partIds.forM fun i =>
      require (U.find? i).isSome s!"InvalidPurposes: link {L.id} names unknown unit {i}"
    require (sameUnit U L) s!"InvalidPurposes: link {L.id} must join distinct parts of one unit"
    require (sidesAdjacent U L)
      s!"InvalidPurposes: link {L.id} has a side whose parts are not adjacent and in order"
    require (markerAgrees U L)
      s!"InvalidPurposes: unit {L.marker} is not marked as this link's reason or purpose"
    require (nonfactive U L)
      s!"InvalidPurposes: link {L.id} would make a purpose or a denied reason a premise or a rule"
    require (packsInert U L)  -- fault 6a, PE-R11
      s!"InvalidPurposes: link {L.id} has a side the text does not state, and a pack takes a premise from it"
    require (!(L.polarity == .denied && L.share != .plain))
      s!"InvalidPurposes: link {L.id} denies a reason and also says how much of the reason it is"
    require (shareOk B L)
      s!"InvalidPurposes: link {L.id} says this is the only reason, and the text gives another"
  require (markersLinked U B) "InvalidPurposes: a unit marked as a reason or purpose has no link"
  require (markerHonest U B)
    "InvalidPurposes: link words are counted as covered, but what they link is not formalised"

def WellFormed (U : Units) (B : Block) : Prop :=
  B.links.length ≤ maxLinks ∧ (B.links.map (·.id)).Nodup ∧
  (∀ L ∈ B.links, (∀ i ∈ L.partIds, (U.find? i).isSome = true) ∧ sameUnit U L = true ∧
    sidesAdjacent U L = true ∧ markerAgrees U L = true ∧ nonfactive U L = true ∧ packsInert U L = true ∧
    (L.polarity = .denied → L.share = .plain) ∧ shareOk B L = true) ∧
  markersLinked U B = true ∧ markerHonest U B = true

theorem require_iff {b : Bool} {m : String} : require b m = .ok () ↔ b = true := by
  cases b <;> simp [require]

theorem unit_bind {α : Type} {x : Except String PUnit} {f : PUnit → Except String α} {y : α} :
    (x >>= f) = .ok y ↔ x = .ok () ∧ f () = .ok y := by
  cases x with
  | error e => simp [bind, Except.bind]
  | ok a => simp [bind, Except.bind]

theorem forM_iff {α : Type} (f : α → Except String PUnit) : ∀ l : List α,
    l.forM f = .ok () ↔ ∀ a ∈ l, f a = .ok ()
  | [] => by simp; rfl
  | a :: l => by simp only [List.forM, unit_bind, forM_iff f l]; simp

/-- The characterization; its right side has SR 6's conjunct `sidesAdjacent` and (PE-R11) `packsInert`. -/
theorem check_ok_iff (U : Units) (B : Block) : check U B = .ok () ↔ WellFormed U B := by
  simp only [check, WellFormed, unit_bind, require_iff, forM_iff, decide_eq_true_eq]
  simp [Bool.not_and, Bool.or_eq_true, Decidable.imp_iff_not_or]

theorem sameUnit_parent (U : Units) (L : Link) (h : sameUnit U L = true) :
    (∀ r ∈ L.reason ++ L.target, ∃ i, r = .part i) ∧ L.partIds.Nodup ∧
      ∃ p, ∀ i ∈ L.partIds, ∃ x, U.find? i = some x ∧ x.parent = some p := by
  unfold sameUnit at h
  simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨hs, hn⟩, hp⟩ := h
  refine ⟨fun r hr => ?_, hn, ?_⟩
  · have := hs r hr
    cases r with
    | part i => exact ⟨i, rfl⟩
    | mention i => simp [Ref.partId?] at this
  · split at hp
    · rename_i p _
      refine ⟨p, fun i hi => ?_⟩
      have := List.all_eq_true.mp hp i hi
      cases hx : U.find? i with
      | none => simp [hx] at this
      | some x => exact ⟨x, rfl, by simpa [hx] using this⟩
    · cases hp

theorem adjacent_iff : ∀ ps : List Part,
    ((ps.zip ps.tail).all fun (a, b) => a.span.2 == b.span.1) = true ↔
      ∀ (i : Nat) (h : i + 1 < ps.length), ps[i].span.2 = ps[i + 1].span.1
  | [] => by simp
  | [_] => by simp
  | a :: b :: ps => by
    have ih := adjacent_iff (b :: ps)
    simp only [List.tail_cons, List.zip_cons_cons, List.all_cons, Bool.and_eq_true, beq_iff_eq] at ih ⊢
    rw [ih]
    constructor
    · rintro ⟨h0, h⟩ i hi
      cases i with
      | zero => exact h0
      | succ i => simpa using h i (by simp at hi ⊢; omega)
    · intro h
      exact ⟨h 0 (by simp), fun i hi => by simpa using h (i + 1) (by simp at hi ⊢; omega)⟩

/-- SR 6: a side passes exactly when its refs are parts of the view, each part's span is ordered, and each part
    starts where the previous one ends. -/
theorem sideAdjacent_iff (U : Units) (s : List Ref) :
    sideAdjacent U s = true ↔ ∃ ps, (s.mapM fun r => r.partId? >>= U.find?) = some ps ∧
      (∀ p ∈ ps, p.span.1 ≤ p.span.2) ∧ ∀ (i : Nat) (h : i + 1 < ps.length), ps[i].span.2 = ps[i + 1].span.1 := by
  unfold sideAdjacent
  cases hm : s.mapM fun r => r.partId? >>= U.find? with
  | none => simp
  | some ps => simp [adjacent_iff ps]

/-- A4 and SR 5: only `sole` constrains other links. It is refused against an affirmed link with the same relation
    and target and a different reason list, or with the same reason list and the share `partly` or `notSole`;
    `plain`, `partly` and `notSole` need no other link. -/
theorem shareOk_iff (B : Block) (L : Link) :
    shareOk B L = true ↔
      (L.share = .sole → ∀ M ∈ B.links, M.id ≠ L.id → M.polarity = .affirmed → M.relation = L.relation →
        M.target = L.target → M.reason = L.reason ∧ (M.share = .plain ∨ M.share = .sole)) := by
  unfold shareOk rivals
  cases hs : L.share with
  | sole =>
    simp only [Bool.and_eq_true, List.isEmpty_iff, List.filter_eq_nil_iff, List.all_eq_true]
    constructor
    · rintro ⟨h1, h2⟩ - M hM hid hpol hrel htg
      have a := h1 M hM
      have b := h2 M hM
      simp_all
    · intro h
      have h := h trivial
      refine ⟨fun M hM => ?_, fun M hM => ?_⟩ <;> by_cases hid : M.id = L.id <;>
        by_cases hpol : M.polarity = .affirmed <;> by_cases hrel : M.relation = L.relation <;>
        by_cases htg : M.target = L.target <;> simp_all
  | _ => simp

theorem side_kind {U : Units} {s : List Ref} {k : Kind} (h : sideOfKind U s k = true) :
    ∀ i ∈ s.filterMap Ref.partId?, U.kind? i = some k := by
  unfold sideOfKind at h
  simp only [Bool.and_eq_true, List.all_eq_true] at h
  intro i hi
  obtain ⟨r, hr, hri⟩ := List.mem_filterMap.mp hi
  have := h.2 r hr
  rw [hri] at this
  simpa using this

theorem markerAgrees_kind (U : Units) (L : Link) (h : markerAgrees U L = true) :
    ∃ c e, U.kind? L.marker = some (.causal L.relation.wire c e) ∧
      (∀ i ∈ L.slots.1.filterMap Ref.partId?, U.kind? i = some c) ∧
      (∀ i ∈ L.slots.2.filterMap Ref.partId?, U.kind? i = some e) := by
  unfold markerAgrees at h
  split at h
  · rename_i r c e hk
    simp only [Bool.and_eq_true, beq_iff_eq] at h
    obtain ⟨⟨hr, h1⟩, h2⟩ := h
    subst hr
    exact ⟨c, e, hk, side_kind h1, side_kind h2⟩
  · cases h

theorem unstated_eq (L : Link) :
    unstated L = if L.relation = .inOrderTo ∨ L.polarity = .denied then L.reason else [] := by
  unfold unstated
  by_cases h1 : L.relation = .inOrderTo <;> by_cases h2 : L.polarity = .denied <;> simp [h1, h2]

/-- D8a exactly: the unstated side is all parts, each inert, each with only inert candidates. -/
theorem nonfactive_iff (U : Units) (L : Link) :
    nonfactive U L = true ↔ ∀ r ∈ unstated L, ∃ i p, r = .part i ∧ U.find? i = some p ∧
      p.kind.inert = true ∧ ∀ k ∈ p.candidates, k.inert = true := by
  unfold nonfactive
  rw [List.all_eq_true]
  refine forall_congr' fun r => imp_congr_right fun _ => ?_
  cases r with
  | mention i => simp [Ref.partId?]
  | part i =>
    cases hp : U.find? i with
    | none => simp [Ref.partId?, hp]
    | some p => simp [Ref.partId?, hp, List.all_eq_true]

theorem markerHonest_labelled (U : Units) (B : Block) (h : markerHonest U B = true) (p : Part)
    (hp : p ∈ U.parts) (hl : p.status = "LABELLED") (hm : ∃ L ∈ B.links, L.marker = p.id) :
    ∃ L ∈ B.links, L.marker = p.id ∧ covered U L.reason = true ∧ covered U L.target = true := by
  unfold markerHonest at h
  have := List.all_eq_true.mp h p hp
  obtain ⟨L, hL, hLm⟩ := hm
  have hany : B.links.any (·.marker == p.id) = true := List.any_eq_true.mpr ⟨L, hL, by simp [hLm]⟩
  simp only [hl, hany, bne_self_eq_false, Bool.not_true, Bool.false_or, List.any_eq_true,
    Bool.and_eq_true, beq_iff_eq] at this
  obtain ⟨M, hM, ⟨hMm, hr⟩, ht⟩ := this
  exact ⟨M, hM, hMm, hr, ht⟩

/-- PE-R11: no part on the unstated side, and not its unit, is a pack premise's source. -/
theorem packsInert_iff (U : Units) (L : Link) :
    packsInert U L = true ↔ ∀ r ∈ unstated L, ∃ i p, r = .part i ∧ U.find? i = some p ∧
      p.id ∉ U.packSources ∧ ∀ u, p.parent = some u → u ∉ U.packSources := by
  unfold packsInert
  rw [List.all_eq_true]
  refine forall_congr' fun r => imp_congr_right fun _ => ?_
  cases r with
  | mention i => simp [Ref.partId?]
  | part i =>
    cases hp : U.find? i with
    | none => simp [Ref.partId?, hp]
    | some p => cases hq : p.parent <;> simp [Ref.partId?, hp, hq]

/-- PE-R11: with no pack on the list, the conjunct adds nothing beyond `nonfactive`'s parts. -/
theorem packsInert_nil (U : Units) (L : Link) (h : U.packSources = []) (hn : nonfactive U L = true) :
    packsInert U L = true := by
  rw [packsInert_iff]
  intro r hr
  obtain ⟨i, p, hri, hp, -⟩ := (nonfactive_iff U L).mp hn r hr
  exact ⟨i, p, hri, hp, by simp [h], by simp [h]⟩

/-- PE-R8: exactly the target parts with an active set, each with exactly the names of its candidates whose kind is
    the target's slot kind. The view gives one name per kind (`checkDocSetsView_readings`, 5.1), so no candidate is
    cut by the zip. -/
theorem shownUnder_iff (U : Units) (L : Link) (i : String) (ns : List String) :
    (i, ns) ∈ shownUnder U L ↔ ∃ r ∈ L.target, ∃ p, r = .part i ∧ U.find? i = some p ∧ p.candidates ≠ [] ∧
      ns = ((p.readings.zip p.candidates).filter fun x => targetKind U L = some x.2).map (·.1) := by
  have hf : (fun x : String × Kind => holdsTarget U L x.2) = fun x => decide (targetKind U L = some x.2) := by
    funext x; unfold holdsTarget; by_cases h : targetKind U L = some x.2 <;> simp [h]
  have hid : ∀ {j p}, U.find? j = some p → p.id = j := fun h => by
    simpa using List.find?_some h
  unfold shownUnder
  simp only [List.mem_filterMap, hf]
  constructor
  · rintro ⟨p, ⟨r, hr, hrp⟩, hpi⟩
    cases r with
    | mention m => simp [Ref.partId?] at hrp
    | part j =>
      simp only [Ref.partId?, Option.bind_eq_bind, Option.bind_some] at hrp
      by_cases hc : p.candidates.isEmpty
      · simp [hc] at hpi
      · simp only [hc, Bool.false_eq_true, ↓reduceIte, Option.some.injEq, Prod.mk.injEq] at hpi
        obtain ⟨rfl, rfl⟩ := hpi
        have := hid hrp
        subst this
        exact ⟨.part p.id, hr, p, rfl, hrp, by simpa using hc, rfl⟩
  · rintro ⟨r, hr, p, rfl, hp, hc, rfl⟩
    refine ⟨p, ⟨.part i, hr, by simpa [Ref.partId?] using hp⟩, ?_⟩
    simp [List.isEmpty_iff, hc, hid hp]

/-- PE-R8: a part is listed exactly when it is in the marker's unit, is not inert, and no link names it. -/
theorem unlinkedActive_iff (U : Units) (B : Block) (L : Link) (i : String) :
    i ∈ unlinkedActive U B L ↔ ∃ u p, (U.find? L.marker).bind (·.parent) = some u ∧ p ∈ U.parts ∧ p.id = i ∧
      p.parent = some u ∧ p.kind.inert = false ∧ ∀ M ∈ B.links, i ∉ M.partIds := by
  unfold unlinkedActive
  cases hu : (U.find? L.marker).bind (·.parent) with
  | none => simp
  | some u =>
    simp only [List.mem_map, List.mem_filter, Bool.and_eq_true, beq_iff_eq, Bool.not_eq_true',
      List.any_eq_false, List.contains_iff_mem]
    constructor
    · rintro ⟨p, ⟨hp, ⟨hpu, hk⟩, hl⟩, rfl⟩
      exact ⟨u, p, rfl, hp, rfl, hpu, hk, fun M hM h => hl M hM (by simpa using h)⟩
    · rintro ⟨u', p, hu', hp, rfl, hpu, hk, hl⟩
      cases hu'
      exact ⟨p, ⟨hp, ⟨hpu, hk⟩, fun M hM h => hl M hM (by simpa using h)⟩, rfl⟩

end VE.Purposes
