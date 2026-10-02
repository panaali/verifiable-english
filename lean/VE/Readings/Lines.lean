import VE.Readings.Separate
import VE.NormDefaults.Check

/-! The line order of a candidate's document and the uniqueness of source keys (docs/spec/composition-s1.md 4.4,
8.3; DRI ruling 1 of 2026-10-02).

`genKeys_nodup` as first approved is false: `WellFormedRights` accepts a rights document whose line order
(`sourceOrder`) lists one default fan-out line twice, and two pairs of the generated keys then repeat
(`Examples.lean`, `twiceListed`). It is also false when the order lists a line that is not a line of its right:
the rights checks read the rights' own lines and the order is not compared with them (`Examples.lean`,
`orderOnly`). The rights decoder never builds either order (`VE.Rights.Wire.addUnit` appends each unit's lines
once, and refuses `right_lines` before its right), but `place` does when a `right_lines` unit precedes its right.

So S1 admission checks the line order of every candidate's document and of `free D` (`lineOrderText`, before the
chain's own checks, 4.4): an entry that is no line of its right is the rights decoder's `UnknownRight: <r>`, and an
entry listed twice is `InvalidInput: line order lists a line of right <r> twice`. `linesOnce` is that check as a
Boolean (`linesOnce_of_text`), and `genKeys_nodup` takes it as its hypothesis. The frozen rights code is unchanged:
the facts the proof reads from `checkRights` come from a restatement of it that is equal to it by `rfl`
(`checkRights_steps`). -/
namespace VE.Readings
open VE.Rights (RightsDoc SourceLine Line Limitation sourceLines linesOf linesAux instancesOf correlate authorNodes
  checkRights checkBlock checkSourceLine)
open VE.SoftNorms (SoftNode)
open VE.NormDefaults (ebind_ok ethrow_ok forIn_each)

/-! ## The check -/

/-- The entry is a line of a right of the document with the entry's right name. -/
def lineOwned (X : RightsDoc) (e : String × SourceLine) : Bool :=
  X.rs.any (fun R => R.name == e.1 && R.lines.contains e.2)

/-- The line order lists each entry once, and only lines of its right. -/
def linesOnce (X : RightsDoc) : Bool :=
  decide (sourceLines X).Nodup && (sourceLines X).all (lineOwned X)

/-- The first entry of the line order that is no line of its right, or that an earlier entry repeats. -/
def lineOrderText (X : RightsDoc) : Option String := go [] (sourceLines X)
where
  go (seen : List (String × SourceLine)) : List (String × SourceLine) → Option String
    | [] => none
    | e :: rest =>
      if !lineOwned X e then some s!"UnknownRight: {e.1}"
      else if seen.contains e then some s!"InvalidInput: line order lists a line of right {e.1} twice"
      else go (e :: seen) rest

theorem lineOrderText_go (X : RightsDoc) : ∀ (seen l : List (String × SourceLine)),
    lineOrderText.go X seen l = none → (∀ e ∈ l, lineOwned X e = true) ∧ l.Nodup ∧ ∀ e ∈ l, e ∉ seen
  | _, [], _ => ⟨by simp, List.nodup_nil, by simp⟩
  | seen, e :: rest, h => by
    simp only [lineOrderText.go] at h
    split at h
    · cases h
    split at h
    · cases h
    rename_i ho hs
    simp only [Bool.not_eq_true', Bool.not_eq_false] at ho
    have hs' : e ∉ seen := fun hm => hs (List.contains_iff_mem.mpr hm)
    obtain ⟨h1, h2, h3⟩ := lineOrderText_go X (e :: seen) rest h
    refine ⟨fun x hx => ?_, List.nodup_cons.mpr ⟨fun hm => h3 e hm (List.mem_cons_self ..), h2⟩, fun x hx => ?_⟩
    · rcases List.mem_cons.mp hx with rfl | hx
      · exact ho
      · exact h1 x hx
    · rcases List.mem_cons.mp hx with rfl | hx
      · exact hs'
      · exact fun hm => h3 x hx (List.mem_cons_of_mem _ hm)

/-- The admission check passes exactly on a document whose line order `linesOnce` accepts. -/
theorem linesOnce_of_text (X : RightsDoc) (h : lineOrderText X = none) : linesOnce X = true := by
  obtain ⟨h1, h2, _⟩ := lineOrderText_go X [] (sourceLines X) h
  simp only [linesOnce, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true]
  exact ⟨h2, h1⟩

/-! ## What `checkRights` guarantees about names

`checkRights` restated in four steps, each named after what follows it, equal to it by `rfl`. -/

def limBody (D : RightsDoc) (L : Limitation) : Except String (ForInStep PUnit) := do
  match L.scope with
  | none => pure ()
  | some rs =>
    if rs.isEmpty then throw s!"InvalidInput: invalid scope of limitation {L.name}"
    for r in rs do
      unless (D.rs.map (·.name)).contains r do throw s!"UnknownRight: {r}"
  if L.kinds == some [] then throw s!"InvalidInput: invalid kinds of limitation {L.name}"
  if L.conditions.length > 8 then throw "ResourceLimit: conditions"
  for c in L.conditions do
    unless VE.Rights.identifier c.name do throw s!"InvalidInput: invalid condition {c.name}"
    unless VE.Rights.validDecider c.decidedBy do throw s!"InvalidInput: invalid decider for condition {c.name}"
  if let some c := VE.SoftNorms.dupOf (L.conditions.map (·.name)) then
    throw s!"DuplicateDeclaration: condition {c}"
  unless VE.Rights.validDecider L.decidedBy do throw s!"InvalidInput: invalid decider for limitation {L.name}"
  if L.decidedBy.isNone then throw s!"MissingExceptionDecider: limitation {L.name}"
  pure (ForInStep.yield PUnit.unit)

def stepsBars (D : RightsDoc) : Except String Unit := do
  if D.bars.length > 1 then throw "DuplicateDeclaration: bar"
  for b in D.bars do
    unless VE.Rights.validDecider b.decidedBy do throw s!"InvalidInput: invalid decider for bar {b.name}"
  for cs in D.rs.flatMap (fun R => R.lines.map (·.cites)) ++ D.outsideCites.map (·.2) do
    for kv in cs do
      for u in kv.2 do
        unless D.sourceUnits.contains u do throw s!"UnknownSymbol: unit {u}"

def stepsLimits (D : RightsDoc) : Except String Unit := do
  forIn D.limits PUnit.unit (fun L _ => limBody D L)
  stepsBars D

def stepsLines (D : RightsDoc) : Except String Unit := do
  for RN in linesOf D do
    match VE.Rights.rightOf D RN.1 with
    | none => throw s!"UnknownRight: {RN.1}"
    | some R =>
      VE.Rights.checkShape D R RN.2
      if RN.2.node.carveOuts.length > 6 then throw s!"ResourceLimit: carve-outs of rule {RN.2.node.name}"
  for R in D.rs do
    unless (linesOf D).any (·.1 == R.name) do throw s!"RightWithoutIncident: {R.name}"
  stepsLimits D

def stepsRights (D : RightsDoc) : Except String Unit := do
  for R in D.rs do
    unless D.rights.holders.contains R.holder do throw s!"UnknownSymbol: sort {R.holder}"
    VE.Norms.typeDiagnostic D.soft.E [R.holder] R.guard
    unless R.guard.check D.soft.E [R.holder] do throw s!"InvalidInput: ill-typed right {R.name}"
    for S in R.lines do
      checkSourceLine D R S
  stepsLines D

def stepsPreds (D : RightsDoc) : Except String Unit := do
  for p in D.soft.T.regulated.map (·.name) ++ D.soft.T.definitions.map (·.name) do
    if VE.Rights.beginsRightsPred p then throw s!"InvalidInput: author predicate {p} begins with rights__"
  for d in VE.Rights.genDecls D do
    if (D.soft.E.predicates d.1).isSome then throw s!"InvalidInput: author predicate {d.1} begins with rights__"
  for M in D.rs.flatMap (fun R => R.lines.flatMap authorNodes) ++ D.soft.T.nodes do
    for m in M.over do
      if VE.Rights.beginsRightsRule m then throw s!"UnknownSymbol: rule {m}"
  stepsRights D

def stepsHead (D : RightsDoc) : Except String Unit := do
  checkBlock D
  if D.rs.length > 128 then throw "ResourceLimit: rights"
  if D.limits.length > 16 then throw "ResourceLimit: limitations"
  let names := D.rs.map (·.name) ++ D.limits.map (·.name) ++ D.bars.map (·.name)
  let ruleNames := (D.rs.flatMap (fun R => R.lines.flatMap authorNodes)).map (·.name) ++ D.soft.T.nodes.map (·.name)
  for n in names ++ ruleNames do
    if VE.Rights.beginsRightsRule n then throw s!"InvalidInput: name {n} begins with rights-"
  if let some n := VE.SoftNorms.dupOf (names ++ ruleNames) then
    if (D.rs.map (·.name)).contains n then throw s!"DuplicateDeclaration: right {n}"
    else if (D.limits.map (·.name)).contains n then throw s!"DuplicateDeclaration: limitation {n}"
    else if (D.bars.map (·.name)).contains n then throw "DuplicateDeclaration: bar"
    else throw s!"DuplicateDeclaration: rule {n}"
  stepsPreds D

theorem checkRights_steps (D : RightsDoc) : checkRights D = stepsHead D := rfl

theorem bind_ok_right {α β : Type} {x : Except String α} {f : α → Except String β} {b : β}
    (h : (x >>= f) = .ok b) : ∃ a, f a = .ok b := by
  obtain ⟨a, _, h⟩ := (ebind_ok x f b).mp h; exact ⟨a, h⟩

theorem throw_bind_ok {α β : Type} {e : String} {f : α → Except String β} {b : β}
    (h : ((throw e : Except String α) >>= f) = .ok b) : False := by
  obtain ⟨_, h, _⟩ := (ebind_ok _ f b).mp h; exact (ethrow_ok e _).mp h

theorem nodup_of_count : ∀ {l : List String}, (∀ a ∈ l, l.count a ≤ 1) → l.Nodup
  | [], _ => List.nodup_nil
  | x :: t, h => by
    refine List.nodup_cons.mpr ⟨fun hx => ?_, nodup_of_count (fun a ha => ?_)⟩
    · have := h x (List.mem_cons_self ..)
      rw [List.count_cons_self] at this
      have := List.count_pos_iff.mpr hx
      omega
    · exact Nat.le_trans (List.Sublist.count_le _ (List.sublist_cons_self x t)) (h a (List.mem_cons_of_mem _ ha))

theorem dupOf_nodup {l : List String} (h : VE.SoftNorms.dupOf l = none) : l.Nodup := by
  refine nodup_of_count (fun a ha => ?_)
  have := List.find?_eq_none.mp h a ha
  simp only [gt_iff_lt, decide_eq_true_eq, Nat.not_lt] at this
  exact this

theorem stepsHead_dup {D : RightsDoc} (h : stepsHead D = .ok ()) :
    VE.SoftNorms.dupOf ((D.rs.map (·.name) ++ D.limits.map (·.name) ++ D.bars.map (·.name)) ++
      ((D.rs.flatMap (fun R => R.lines.flatMap authorNodes)).map (·.name) ++ D.soft.T.nodes.map (·.name))) = none ∧
    stepsPreds D = .ok () := by
  unfold stepsHead at h
  obtain ⟨_, h⟩ := bind_ok_right h
  dsimp only at h
  split at h
  · exact (throw_bind_ok h).elim
  obtain ⟨_, h⟩ := bind_ok_right h
  split at h
  · exact (throw_bind_ok h).elim
  obtain ⟨_, h⟩ := bind_ok_right h
  obtain ⟨_, h⟩ := bind_ok_right h
  split at h
  · rename_i n hn
    split at h
    · exact (throw_bind_ok h).elim
    split at h
    · exact (throw_bind_ok h).elim
    split at h
    · exact (throw_bind_ok h).elim
    exact (throw_bind_ok h).elim
  · rename_i hn
    refine ⟨?_, ?_⟩
    · cases hd : VE.SoftNorms.dupOf _ with
      | none => rfl
      | some n => exact (hn n hd).elim
    · obtain ⟨_, h⟩ := (ebind_ok _ _ _).mp h
      exact h.2

theorem stepsPreds_rights {D : RightsDoc} (h : stepsPreds D = .ok ()) : stepsRights D = .ok () := by
  unfold stepsPreds at h
  obtain ⟨_, h⟩ := bind_ok_right h
  obtain ⟨_, h⟩ := bind_ok_right h
  obtain ⟨_, h⟩ := bind_ok_right h
  exact h

theorem stepsRights_lines {D : RightsDoc} (h : stepsRights D = .ok ()) :
    (∀ R ∈ D.rs, ∀ S ∈ R.lines, checkSourceLine D R S = .ok ()) ∧ stepsLines D = .ok () := by
  unfold stepsRights at h
  obtain ⟨u, hl, h⟩ := (ebind_ok _ _ _).mp h
  refine ⟨fun R hR S hS => ?_, h⟩
  have hb := forIn_each _ (fun x t r hr => ?_) _ _ _ hl R hR
  · obtain ⟨t, t', hR'⟩ := hb
    cases t
    simp only at hR'
    split at hR'
    · obtain ⟨_, hR'⟩ := bind_ok_right hR'
      obtain ⟨_, hR'⟩ := bind_ok_right hR'
      split at hR'
      · obtain ⟨_, hR'⟩ := bind_ok_right hR'
        obtain ⟨_, hS', _⟩ := (ebind_ok _ _ _).mp hR'
        have := forIn_each _ (fun x t r hr => ?_) _ _ _ hS' S hS
        · obtain ⟨_, _, hc⟩ := this
          obtain ⟨_, hc, hy⟩ := (ebind_ok _ _ _).mp hc
          cases ‹Unit›
          exact hc
        · obtain ⟨_, _, hr⟩ := (ebind_ok _ _ _).mp hr
          cases hr
          exact ⟨_, rfl⟩
      · exact (throw_bind_ok hR').elim
    · exact (throw_bind_ok hR').elim
  · cases t
    simp only at hr
    split at hr
    · obtain ⟨_, hr⟩ := bind_ok_right hr
      obtain ⟨_, hr⟩ := bind_ok_right hr
      split at hr
      · obtain ⟨_, hr⟩ := bind_ok_right hr
        obtain ⟨_, _, hr⟩ := (ebind_ok _ _ _).mp hr
        obtain ⟨_, _, hr⟩ := (ebind_ok _ _ _).mp hr
        cases hr
        exact ⟨_, rfl⟩
      · exact (throw_bind_ok hr).elim
    · exact (throw_bind_ok hr).elim

theorem stepsLines_limits {D : RightsDoc} (h : stepsLines D = .ok ()) : stepsLimits D = .ok () := by
  unfold stepsLines at h
  obtain ⟨_, h⟩ := bind_ok_right h
  obtain ⟨_, h⟩ := bind_ok_right h
  exact h

theorem limBody_ok {D : RightsDoc} {L : Limitation} {r : ForInStep PUnit} (h : limBody D L = .ok r) :
    VE.SoftNorms.dupOf (L.conditions.map (·.name)) = none ∧ ∃ t, r = .yield t := by
  unfold limBody at h
  dsimp only at h
  split at h
  · obtain ⟨_, h⟩ := bind_ok_right h
    split at h <;> try exact (throw_bind_ok h).elim
    obtain ⟨_, h⟩ := bind_ok_right h
    split at h <;> try exact (throw_bind_ok h).elim
    obtain ⟨_, h⟩ := bind_ok_right h
    obtain ⟨_, h⟩ := bind_ok_right h
    split at h <;> try exact (throw_bind_ok h).elim
    rename_i hn
    refine ⟨?_, ?_⟩
    · cases hd : VE.SoftNorms.dupOf _ with
      | none => rfl
      | some c => exact (hn c hd).elim
    · obtain ⟨_, h⟩ := bind_ok_right h
      split at h <;> try exact (throw_bind_ok h).elim
      obtain ⟨_, h⟩ := bind_ok_right h
      split at h <;> try exact (throw_bind_ok h).elim
      obtain ⟨_, h⟩ := bind_ok_right h
      cases h
      exact ⟨_, rfl⟩
  · split at h <;> try exact (throw_bind_ok h).elim
    obtain ⟨_, h⟩ := bind_ok_right h
    obtain ⟨_, h⟩ := bind_ok_right h
    obtain ⟨_, h⟩ := bind_ok_right h
    split at h <;> try exact (throw_bind_ok h).elim
    obtain ⟨_, h⟩ := bind_ok_right h
    split at h <;> try exact (throw_bind_ok h).elim
    obtain ⟨_, h⟩ := bind_ok_right h
    obtain ⟨_, h⟩ := bind_ok_right h
    split at h <;> try exact (throw_bind_ok h).elim
    rename_i hn
    refine ⟨?_, ?_⟩
    · cases hd : VE.SoftNorms.dupOf _ with
      | none => rfl
      | some c => exact (hn c hd).elim
    · obtain ⟨_, h⟩ := bind_ok_right h
      split at h <;> try exact (throw_bind_ok h).elim
      obtain ⟨_, h⟩ := bind_ok_right h
      split at h <;> try exact (throw_bind_ok h).elim
      obtain ⟨_, h⟩ := bind_ok_right h
      cases h
      exact ⟨_, rfl⟩

theorem stepsLimits_conds {D : RightsDoc} (h : stepsLimits D = .ok ()) :
    ∀ L ∈ D.limits, VE.SoftNorms.dupOf (L.conditions.map (·.name)) = none := by
  unfold stepsLimits at h
  obtain ⟨_, hl, _⟩ := (ebind_ok _ _ _).mp h
  intro L hL
  obtain ⟨_, _, hb⟩ := forIn_each _ (fun x t r hr => (limBody_ok hr).2) _ _ _ hl L hL
  exact (limBody_ok hb).1

theorem throw_ok {α : Type} {e : String} {a : α} (h : (throw e : Except String α) = .ok a) : False :=
  (ethrow_ok e a).mp h

-- `walk_ok` walks a hypothesis `h : <do block> = .ok _` through binds, `if`s and `match`es, dropping every
-- branch that throws.
set_option hygiene false in
macro "walk_ok" : tactic => `(tactic| repeat' (first
  | exact (throw_bind_ok h).elim
  | exact (throw_ok h).elim
  | (obtain ⟨_, h⟩ := bind_ok_right h)
  | (split at h)))

theorem checkSourceLine_fan {D : RightsDoc} {R : VE.Rights.Right} {S : SourceLine}
    (h : checkSourceLine D R S = .ok ()) : (S.fanOut.map (·.1)).Nodup := by
  unfold checkSourceLine at h
  dsimp only at h
  walk_ok
  · rename_i he; simp only [List.isEmpty_iff] at he; simp [he]
  · by_cases hc : (S.liberty.isSome || S.recognition.isSome) = true
    · rw [if_pos hc] at h
      walk_ok
    rw [if_neg hc] at h
    by_cases he : S.fanOut.isEmpty = true
    · simp only [List.isEmpty_iff] at he; simp [he]
    rw [if_neg he] at h
    by_cases hl : (S.kind == .liberty) = true
    · rw [if_pos hl] at h
      walk_ok
    rw [if_neg hl] at h
    obtain ⟨_, h⟩ := bind_ok_right h
    obtain ⟨_, h⟩ := bind_ok_right h
    cases hd : VE.SoftNorms.dupOf (S.fanOut.map (·.1)) with
    | none => exact dupOf_nodup hd
    | some b =>
      rw [hd] at h
      walk_ok

/-- The facts about names that `checkRights` guarantees and `genKeys_nodup` reads. -/
structure RightsNames (X : RightsDoc) : Prop where
  rules : ((X.rs.flatMap (fun R => R.lines.flatMap authorNodes)).map (·.name)).Nodup
  limits : (X.limits.map (·.name)).Nodup
  conds : ∀ L ∈ X.limits, (L.conditions.map (·.name)).Nodup
  fan : ∀ R ∈ X.rs, ∀ S ∈ R.lines, (S.fanOut.map (·.1)).Nodup

theorem rightsNames_of_check {X : RightsDoc} (h : checkRights X = .ok ()) : RightsNames X := by
  rw [checkRights_steps] at h
  obtain ⟨hd, hp⟩ := stepsHead_dup h
  obtain ⟨hs, hl⟩ := stepsRights_lines (stepsPreds_rights hp)
  have hc := stepsLimits_conds (stepsLines_limits hl)
  obtain ⟨hnames, hrules, _⟩ := List.nodup_append.mp (dupOf_nodup hd)
  obtain ⟨hrl, _, _⟩ := List.nodup_append.mp hnames
  exact ⟨(List.nodup_append.mp hrules).1, (List.nodup_append.mp hrl).2.1,
    fun L hL => dupOf_nodup (hc L hL), fun R hR S hS => checkSourceLine_fan (hs R hR S hS)⟩

theorem rightsNames_of_chainWF (c : Chain) (X : RightsDoc) (h : chainWF c X = true) : RightsNames X := by
  cases c with
  | rights =>
    simp only [chainWF, VE.Rights.WellFormedRights, VE.Rights.validateRights] at h
    cases hc : checkRights X with
    | error e => rw [hc] at h; cases h
    | ok u => cases u; exact rightsNames_of_check hc
  | soft | norms =>
    have hnr : noRights X = true := by
      simp only [chainWF, Bool.and_eq_true] at h
      first | exact h.1 | exact h.1.1
    simp only [noRights, Bool.and_eq_true, List.isEmpty_iff] at hnr
    have hr : X.rs = [] := hnr.1.1.1
    have hl : X.limits = [] := hnr.1.1.2
    exact ⟨by simp [hr], by simp [hl], by simp [hl], by simp [hr]⟩

/-! ## Lists -/

theorem nodup_of_map {α β : Type} {f : α → β} {l : List α} (h : (l.map f).Nodup) : l.Nodup :=
  (List.pairwise_map.mp h).imp (fun hne he => hne (congrArg f he))

theorem nodup_map_of_inj {α β : Type} {f : α → β} {l : List α} (inj : ∀ a b, f a = f b → a = b)
    (h : l.Nodup) : (l.map f).Nodup :=
  List.pairwise_map.mpr (h.imp (fun hne he => hne (inj _ _ he)))

theorem nodup_flatMap_iff {α β : Type} (f : α → List β) : ∀ (l : List α),
    (l.flatMap f).Nodup ↔ (∀ x ∈ l, (f x).Nodup) ∧ l.Pairwise (fun a b => ∀ y ∈ f a, y ∉ f b)
  | [] => by simp
  | x :: t => by
    rw [List.flatMap_cons, List.nodup_append, nodup_flatMap_iff f t, List.pairwise_cons]
    constructor
    · rintro ⟨hx, ⟨ht, hp⟩, hd⟩
      refine ⟨fun z hz => ?_, ⟨fun b hb y hy hy' => hd y hy y (List.mem_flatMap.mpr ⟨b, hb, hy'⟩) rfl, hp⟩⟩
      rcases List.mem_cons.mp hz with rfl | hz
      · exact hx
      · exact ht z hz
    · rintro ⟨hall, hb, hp⟩
      refine ⟨hall x (List.mem_cons_self ..), ⟨fun z hz => hall z (List.mem_cons_of_mem _ hz), hp⟩, ?_⟩
      intro a ha b hb' hab
      subst hab
      obtain ⟨c, hc, hbc⟩ := List.mem_flatMap.mp hb'
      exact hb c hc a ha hbc

/-- In a list pairwise related by a symmetric relation, two different members are related. -/
theorem pairwise_of_ne {α : Type} {R : α → α → Prop} (hs : ∀ a b, R a b → R b a) :
    ∀ {l : List α}, l.Pairwise R → ∀ a ∈ l, ∀ b ∈ l, a ≠ b → R a b
  | [], _, a, ha, _, _, _ => absurd ha List.not_mem_nil
  | x :: t, h, a, ha, b, hb, hab => by
    obtain ⟨hx, ht⟩ := List.pairwise_cons.mp h
    rcases List.mem_cons.mp ha with ha' | ha' <;> rcases List.mem_cons.mp hb with hb' | hb'
    · exact absurd (ha'.trans hb'.symm) hab
    · rw [ha']; exact hx b hb'
    · rw [hb']; exact hs _ _ (hx a ha')
    · exact pairwise_of_ne hs ht a ha' b hb' hab

theorem insertBy_perm {α : Type} (lt : α → α → Bool) (x : α) : ∀ l : List α, (VE.Norms.insertBy lt x l).Perm (x :: l)
  | [] => List.Perm.refl _
  | y :: ys => by
    simp only [VE.Norms.insertBy]
    split
    · exact List.Perm.refl _
    · exact ((List.perm_cons y).mpr (insertBy_perm lt x ys)).trans (List.Perm.swap x y ys)

theorem sortBy_perm {α : Type} (lt : α → α → Bool) : ∀ l : List α, (VE.Norms.sortBy lt l).Perm l
  | [] => List.Perm.refl _
  | x :: xs => (insertBy_perm lt x _).trans ((List.perm_cons x).mpr (sortBy_perm lt xs))

theorem dedup_nodup {α : Type} [BEq α] [LawfulBEq α] : ∀ l : List α, (VE.SoftNorms.dedup l).Nodup
  | [] => List.nodup_nil
  | x :: xs => by
    simp only [VE.SoftNorms.dedup]
    split
    · exact dedup_nodup xs
    · rename_i hc
      exact List.nodup_cons.mpr ⟨fun hm => hc (List.contains_iff_mem.mpr hm), dedup_nodup xs⟩

/-! ## The keys of the rules -/

theorem nodeOf_name (X : RightsDoc) (N : Line) : (VE.Rights.nodeOf X N).name = N.node.name := rfl

/-- An entry of `keyedNodes` without a bearer carries its node's name. -/
theorem keyedNodes_bearerless (X : RightsDoc) : ∀ e ∈ keyedNodes X, e.2.2 = none → e.2.1 = e.1.name := by
  intro e he hb
  simp only [keyedNodes, List.mem_append, List.mem_map] at he
  rcases he with (⟨RN, _, rfl⟩ | ⟨N, _, rfl⟩) | ⟨N, _, rfl⟩
  · simp only at hb ⊢
    simp [ruleOf, hb, nodeOf_name]
  · rfl
  · rfl

/-- A line instance with a bearer is a fan-out instance of its source line's norm, and carries its name. -/
theorem instancesOf_fan {R : String} {S : SourceLine} {k : Nat} {N : Line} (h : N ∈ instancesOf R S k)
    (hb : N.bearer.isSome = true) : ∃ n, S.norm = some n ∧ ruleOf N = n.name := by
  unfold instancesOf at h
  split at h
  · split at h
    · simp only [List.mem_cons, List.not_mem_nil, or_false] at h
      rcases h with rfl | rfl <;> simp at hb
    · simp at h
  · split at h
    · simp at h
    · rename_i n hn
      split at h
      · simp only [List.mem_cons, List.not_mem_nil, or_false] at h
        subst h; simp at hb
      · obtain ⟨i, hi, rfl⟩ := List.mem_mapIdx.mp h
        exact ⟨n, hn, by simp [ruleOf, hn]⟩

theorem mapIdx_bearers (l : List (String × String)) (f : Nat → String × String → Line)
    (hf : ∀ i bp, (f i bp).bearer = some bp.1) (hnd : (l.map (·.1)).Nodup) :
    (l.mapIdx f).Pairwise (fun a b => a.bearer.isSome = true → b.bearer.isSome = true → a.bearer ≠ b.bearer) := by
  have hmap : (l.mapIdx f).map (·.bearer) = (l.map (·.1)).map some := by
    apply List.ext_getElem
    · simp
    · intro i h1 h2
      simp [List.getElem_mapIdx, hf]
  have := nodup_map_of_inj (f := some) (fun a b h => Option.some.inj h) hnd
  rw [← hmap] at this
  exact (List.pairwise_map.mp this).imp (fun hne _ _ => hne)

/-- The instances of one source line have distinct bearers. -/
theorem instancesOf_bearers {R : String} {S : SourceLine} {k : Nat} (hf : (S.fanOut.map (·.1)).Nodup) :
    (instancesOf R S k).Pairwise (fun a b => a.bearer.isSome = true → b.bearer.isSome = true →
      a.bearer ≠ b.bearer) := by
  unfold instancesOf
  split
  · split
    · simp
    · simp
  · split
    · simp
    · split
      · simp
      · have hperm : ((VE.Rights.sortFan S.fanOut).map (·.1)).Perm (S.fanOut.map (·.1)) :=
          (sortBy_perm _ _).map _
        exact mapIdx_bearers _ _ (fun _ _ => rfl) (hperm.nodup_iff.mpr hf)

theorem mem_linesAux : ∀ {L : List (String × SourceLine)} {k : Nat} {x : String × Line}, x ∈ linesAux L k →
    ∃ e ∈ L, ∃ k', x.2 ∈ instancesOf e.1 e.2 k'
  | [], _, _, h => by simp [linesAux] at h
  | (R, S) :: rest, k, x, h => by
    simp only [linesAux, List.mem_append, List.mem_map] at h
    rcases h with ⟨N, hN, rfl⟩ | h
    · exact ⟨(R, S), List.mem_cons_self .., k, hN⟩
    · obtain ⟨e, he, k', hx⟩ := mem_linesAux h
      exact ⟨e, List.mem_cons_of_mem _ he, k', hx⟩

/-- Fan-out instances of different source lines, or of one line on different bearers, have different keys. -/
theorem linesAux_pairwise : ∀ (L : List (String × SourceLine)) (k : Nat), L.Nodup →
    (∀ e ∈ L, (e.2.fanOut.map (·.1)).Nodup) →
    (∀ e ∈ L, ∀ e' ∈ L, e ≠ e' → ∀ n ∈ authorNodes e.2, ∀ n' ∈ authorNodes e'.2, n.name ≠ n'.name) →
    (linesAux L k).Pairwise (fun a b => a.2.bearer.isSome = true → b.2.bearer.isSome = true →
      (ruleOf a.2, a.2.bearer) ≠ (ruleOf b.2, b.2.bearer))
  | [], _, _, _, _ => by simp [linesAux]
  | (R, S) :: rest, k, hnd, hf, hn => by
    obtain ⟨hnot, hrest⟩ := List.nodup_cons.mp hnd
    simp only [linesAux]
    refine List.pairwise_append.mpr ⟨?_, ?_, ?_⟩
    · refine List.pairwise_map.mpr ((instancesOf_bearers (hf _ (List.mem_cons_self ..))).imp ?_)
      intro a b hab ha hb he
      exact hab ha hb (congrArg Prod.snd he)
    · exact linesAux_pairwise rest _ hrest (fun e he => hf e (List.mem_cons_of_mem _ he))
        (fun e he e' he' => hn e (List.mem_cons_of_mem _ he) e' (List.mem_cons_of_mem _ he'))
    · intro a ha b hb hab hbb he
      obtain ⟨N, hN, rfl⟩ := List.mem_map.mp ha
      obtain ⟨e', he', k', hb'⟩ := mem_linesAux hb
      obtain ⟨n, hns, hrn⟩ := instancesOf_fan hN hab
      obtain ⟨n', hns', hrn'⟩ := instancesOf_fan hb' hbb
      have hne : (R, S) ≠ e' := fun h => hnot (h ▸ he')
      have := hn (R, S) (List.mem_cons_self ..) e' (List.mem_cons_of_mem _ he') hne n
        (by simp [authorNodes, hns]) n' (by simp [authorNodes, hns'])
      simp only at he
      exact this (by rw [← hrn, ← hrn']; exact congrArg Prod.fst he)

/-- The rights' lines, each with its right's name. -/
def rsLines (X : RightsDoc) : List (String × SourceLine) := X.rs.flatMap (fun R => R.lines.map (R.name, ·))

theorem rules_eq : ∀ (rs : List VE.Rights.Right),
    (rs.flatMap (fun R => R.lines.flatMap authorNodes)).map (·.name) =
      (rs.flatMap (fun R => R.lines.map (R.name, ·))).flatMap (fun e => (authorNodes e.2).map (·.name))
  | [] => rfl
  | R :: rs => by
    simp only [List.flatMap_cons, List.map_append, List.flatMap_append, rules_eq rs]
    congr 1
    induction R.lines with
    | nil => rfl
    | cons S l ih => simp [List.flatMap_cons, ih]

/-- Two different lines of the rights declare no rule name in common. -/
theorem distinct_lines {X : RightsDoc} (hn : RightsNames X) : ∀ e ∈ rsLines X, ∀ e' ∈ rsLines X, e ≠ e' →
    ∀ n ∈ authorNodes e.2, ∀ n' ∈ authorNodes e'.2, n.name ≠ n'.name := by
  have h := hn.rules
  rw [rules_eq] at h
  obtain ⟨_, hp⟩ := (nodup_flatMap_iff _ _).mp h
  intro e he e' he' hne n hn' n' hn'' heq
  have := pairwise_of_ne (R := fun a b => ∀ y ∈ (authorNodes a.2).map (·.name), y ∉ (authorNodes b.2).map (·.name))
    (fun a b hab y hy hy' => hab y hy' hy) hp e he e' he' hne
  exact this n.name (List.mem_map_of_mem hn') (heq ▸ List.mem_map_of_mem hn'')

theorem owned_mem {X : RightsDoc} {e : String × SourceLine} (h : lineOwned X e = true) :
    ∃ R ∈ X.rs, R.name = e.1 ∧ e.2 ∈ R.lines ∧ e ∈ rsLines X := by
  simp only [lineOwned, List.any_eq_true, Bool.and_eq_true, beq_iff_eq, List.contains_iff_mem] at h
  obtain ⟨R, hR, hn, hS⟩ := h
  exact ⟨R, hR, hn, hS, List.mem_flatMap.mpr ⟨R, hR, List.mem_map.mpr ⟨e.2, hS, by rw [hn]⟩⟩⟩

theorem owned_rsLines {X : RightsDoc} {e : String × SourceLine} (h : lineOwned X e = true) :
    e ∈ rsLines X := by
  obtain ⟨_, _, _, _, hm⟩ := owned_mem h
  exact hm

theorem pairwise_all {α : Type} {R : α → α → Prop} : ∀ {l : List α}, (∀ a ∈ l, ∀ b ∈ l, R a b) → l.Pairwise R
  | [], _ => List.Pairwise.nil
  | x :: _, h => List.pairwise_cons.mpr ⟨fun b hb => h x (List.mem_cons_self ..) b (List.mem_cons_of_mem _ hb),
      pairwise_all (fun a ha b hb => h a (List.mem_cons_of_mem _ ha) b (List.mem_cons_of_mem _ hb))⟩

/-- The source key of a rule's entry: its rule name and bearer. -/
def keyPair (e : SoftNode × String × Option String) : String × Option String := (e.2.1, e.2.2)

/-- No two rules of the elaboration carry one source rule name and bearer. -/
theorem keyedNodes_pairwise (c : Chain) (X : RightsDoc) (h : chainWF c X = true) (hl : linesOnce X = true) :
    (keyedNodes X).Pairwise (fun a b => keyPair a ≠ keyPair b) := by
  have hs := VE.SoftNorms.softValid_of_wellFormed _ (chain_soft c X h)
  have hn := rightsNames_of_chainWF c X h
  simp only [linesOnce, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true] at hl
  obtain ⟨hnd, hown⟩ := hl
  have hnames : (keyedNodes X).Pairwise (fun a b => a.1.name ≠ b.1.name) := by
    have := hs.names
    rw [← keyedNodes_nodes, List.map_map] at this
    exact List.pairwise_map.mp this
  have hlines := linesAux_pairwise (sourceLines X) 0 hnd
    (fun e he => by
      obtain ⟨R, hR, _, hS, _⟩ := owned_mem (hown e he)
      exact hn.fan R hR e.2 hS)
    (fun e he e' he' hne => distinct_lines hn e (owned_rsLines (hown e he)) e' (owned_rsLines (hown e' he')) hne)
  have hfan : (keyedNodes X).Pairwise
      (fun a b => a.2.2.isSome = true → b.2.2.isSome = true → keyPair a ≠ keyPair b) := by
    simp only [keyedNodes]
    refine List.pairwise_append.mpr ⟨List.pairwise_append.mpr ⟨?_, ?_, ?_⟩, ?_, ?_⟩
    · exact List.pairwise_map.mpr (hlines.imp (fun h ha hb => h ha hb))
    · exact pairwise_all (fun a ha b hb _ hsb => by
        obtain ⟨N, _, rfl⟩ := List.mem_map.mp hb; simp at hsb)
    · intro a _ b hb _ hsb
      obtain ⟨N, _, rfl⟩ := List.mem_map.mp hb; simp at hsb
    · exact pairwise_all (fun a ha b hb _ hsb => by
        obtain ⟨N, _, rfl⟩ := List.mem_map.mp hb; simp at hsb)
    · intro a _ b hb _ hsb
      obtain ⟨N, _, rfl⟩ := List.mem_map.mp hb; simp at hsb
  refine (hnames.and hfan).imp_of_mem (fun {a b} ha hb hab => ?_)
  obtain ⟨hne, hf⟩ := hab
  cases hxa : a.2.2 <;> cases hxb : b.2.2
  · intro he
    have h1 := congrArg Prod.fst he
    simp only [keyPair] at h1
    rw [keyedNodes_bearerless X a ha hxa, keyedNodes_bearerless X b hb hxb] at h1
    exact hne h1
  · intro he; have := congrArg Prod.snd he; simp [keyPair, hxa, hxb] at this
  · intro he; have := congrArg Prod.snd he; simp [keyPair, hxa, hxb] at this
  · exact hf (by simp [hxa]) (by simp [hxb])

/-! ## `genKeys_nodup` -/

def GenKey.tag : GenKey → Nat
  | .excepted _ _ => 0
  | .off _ _ _ => 1
  | .outweighs _ _ _ => 2
  | .lim _ _ => 3
  | .cond _ _ _ => 4
  | .aimed _ => 5

theorem nodup_append_tag {l1 l2 : List GenKey} {n : Nat} (h1 : l1.Nodup) (h2 : l2.Nodup)
    (t1 : ∀ k ∈ l1, k.tag < n) (t2 : ∀ k ∈ l2, k.tag = n) : (l1 ++ l2).Nodup :=
  List.nodup_append.mpr ⟨h1, h2, fun a ha b hb hab => by
    have := t1 a ha
    rw [hab, t2 b hb] at this
    exact Nat.lt_irrefl _ this⟩

theorem genKeys_keys (X : RightsDoc) : (genKeys X).map (·.1) =
    ((keyedNodes X).filter (fun e => e.1.mode == .default)).map (fun e => GenKey.excepted e.2.1 e.2.2) ++
    (keyedNodes X).flatMap (fun e => e.1.alterable.map (fun π => GenKey.off e.2.1 e.2.2 π)) ++
    (VE.SoftNorms.outweighsTriples (correlate X)).map (fun x => GenKey.outweighs x.1 x.2.1 x.2.2) ++
    (VE.Rights.limKeys X).map (fun k => GenKey.lim k.1 k.2) ++
    (VE.Rights.condKeys X).map (fun k => GenKey.cond k.1 k.2.1 k.2.2) ++
    (if X.bars = [] then [] else (VE.Rights.barPreds X).map GenKey.aimed) := by
  simp only [genKeys, List.map_append, List.map_map, List.map_flatMap, Function.comp_def]
  split <;> simp

/-- Every generated base predicate of a well-formed document has its own source key, when the line order lists
    each line of each right once (DRI ruling 1 of 2026-10-02; the hypothesis is the admission check of 4.4). -/
theorem genKeys_nodup (c : Chain) (X : RightsDoc) (h : chainWF c X = true) (hl : linesOnce X = true) :
    ((genKeys X).map (·.1)).Nodup := by
  have hs := VE.SoftNorms.softValid_of_wellFormed _ (chain_soft c X h)
  have hn := rightsNames_of_chainWF c X h
  have hk := keyedNodes_pairwise c X h hl
  have hdec := hs.decNodup
  simp only [VE.SoftNorms.decisionNames, VE.SoftNorms.decisions, List.map_append] at hdec
  obtain ⟨hdec1, hdecW, _⟩ := List.nodup_append.mp hdec
  obtain ⟨_, hdecO, _⟩ := List.nodup_append.mp hdec1
  rw [genKeys_keys]
  -- excepted
  have hE : (((keyedNodes X).filter (fun e => e.1.mode == .default)).map
      (fun e => GenKey.excepted e.2.1 e.2.2)).Nodup := by
    refine List.pairwise_map.mpr ((hk.filter _).imp ?_)
    intro a b hab he
    injection he with h1 h2
    exact hab (Prod.ext h1 h2)
  -- off
  have halt : ∀ e ∈ keyedNodes X, e.1.alterable.Nodup := by
    intro e he
    have hN : e.1 ∈ (correlate X).T.nodes := by
      rw [← keyedNodes_nodes]; exact List.mem_map_of_mem he
    simp only [VE.SoftNorms.offDecisions, List.map_flatMap, List.map_map] at hdecO
    exact nodup_of_map (((nodup_flatMap_iff _ _).mp hdecO).1 _ hN)
  have hO : ((keyedNodes X).flatMap (fun e => e.1.alterable.map (fun π => GenKey.off e.2.1 e.2.2 π))).Nodup := by
    refine (nodup_flatMap_iff _ _).mpr ⟨fun e he => nodup_map_of_inj (fun a b h => by injection h) (halt e he),
      hk.imp ?_⟩
    intro a b hab y hy hy'
    obtain ⟨π, _, rfl⟩ := List.mem_map.mp hy
    obtain ⟨π', _, h'⟩ := List.mem_map.mp hy'
    injection h' with h1 h2 h3
    exact hab (Prod.ext h1.symm h2.symm)
  -- outweighs
  have hW : ((VE.SoftNorms.outweighsTriples (correlate X)).map
      (fun x => GenKey.outweighs x.1 x.2.1 x.2.2)).Nodup := by
    simp only [VE.SoftNorms.outweighsDecisions, List.map_map] at hdecW
    refine nodup_map_of_inj (fun a b h => ?_) (nodup_of_map hdecW)
    injection h with h1 h2 h3
    exact Prod.ext h1 (Prod.ext h2 h3)
  -- limitations
  have hnamesL := List.pairwise_map.mp hn.limits
  have hL : ((VE.Rights.limKeys X).map (fun k => GenKey.lim k.1 k.2)).Nodup := by
    refine nodup_map_of_inj (fun a b h => ?_) ?_
    · injection h with h1 h2; exact Prod.ext h1 h2
    refine (sortBy_perm _ _).nodup_iff.mpr ((nodup_flatMap_iff _ _).mpr ⟨fun L _ => ?_, hnamesL.imp ?_⟩)
    · exact nodup_map_of_inj (fun a b h => by injection h) (dedup_nodup _)
    · intro L L' hne y hy hy'
      obtain ⟨a, _, rfl⟩ := List.mem_map.mp hy
      obtain ⟨a', _, h'⟩ := List.mem_map.mp hy'
      exact hne (congrArg Prod.fst h').symm
  have hC : ((VE.Rights.condKeys X).map (fun k => GenKey.cond k.1 k.2.1 k.2.2)).Nodup := by
    refine nodup_map_of_inj (fun a b h => ?_) ?_
    · injection h with h1 h2 h3; exact Prod.ext h1 (Prod.ext h2 h3)
    refine (sortBy_perm _ _).nodup_iff.mpr ((nodup_flatMap_iff _ _).mpr ⟨fun L hL => ?_, hnamesL.imp ?_⟩)
    · refine (nodup_flatMap_iff _ _).mpr ⟨fun a _ => ?_, (dedup_nodup _).imp ?_⟩
      · have := hn.conds L hL
        rw [show L.conditions.map (fun c => (L.name, a, c.name)) =
          (L.conditions.map (·.name)).map (fun n => (L.name, a, n)) by simp [List.map_map]]
        exact nodup_map_of_inj (fun x y h => by injection h with _ h2; injection h2) this
      · intro a a' hne y hy hy'
        obtain ⟨c, _, rfl⟩ := List.mem_map.mp hy
        obtain ⟨c', _, h'⟩ := List.mem_map.mp hy'
        exact hne (congrArg (fun t => t.2.1) h').symm
    · intro L L' hne y hy hy'
      obtain ⟨a, _, hy⟩ := List.mem_flatMap.mp hy
      obtain ⟨c, _, rfl⟩ := List.mem_map.mp hy
      obtain ⟨a', _, hy'⟩ := List.mem_flatMap.mp hy'
      obtain ⟨c', _, h'⟩ := List.mem_map.mp hy'
      exact hne (congrArg Prod.fst h').symm
  -- bars
  have hA : (if X.bars = [] then [] else (VE.Rights.barPreds X).map GenKey.aimed).Nodup := by
    split
    · exact List.nodup_nil
    · exact nodup_map_of_inj (fun a b h => by injection h)
        ((List.mergeSort_perm _ _).nodup_iff.mpr (dedup_nodup _))
  refine nodup_append_tag (n := 5) (nodup_append_tag (n := 4) (nodup_append_tag (n := 3)
    (nodup_append_tag (n := 2) (nodup_append_tag (n := 1) hE hO ?_ ?_) hW ?_ ?_) hL ?_ ?_) hC ?_ ?_) hA ?_ ?_
  all_goals try simp only [List.forall_mem_append]
  all_goals repeat' apply And.intro
  all_goals intro k hk
  all_goals first
    | (obtain ⟨_, _, rfl⟩ := List.mem_map.mp hk; simp [GenKey.tag])
    | (obtain ⟨_, _, hk⟩ := List.mem_flatMap.mp hk; obtain ⟨_, _, rfl⟩ := List.mem_map.mp hk; simp [GenKey.tag])
    | (split at hk
       · simp at hk
       · obtain ⟨_, _, rfl⟩ := List.mem_map.mp hk; simp [GenKey.tag])

end VE.Readings
