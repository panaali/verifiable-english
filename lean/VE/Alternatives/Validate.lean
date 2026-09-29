import VE.Alternatives.Followable

/-! Finite validation and scenario evaluation (docs/spec/alternatives.md 3.3, 4.2,
4.6, 4.7, 6 and 7.1).

`validateAlternatives` checks a supplied finite base model and its signed rows:
the Background (`backgroundValidAlt`: literals and the four slot premises), the
rows (`RowsConsistent`), the existence facts E1–E3 and every `Γ_base` formula,
all by evaluation, reporting the texts of 6 on failure. The Boolean gate
`altModelChecks` decides success; the failure text is computed separately and
is not part of any claim. `M.Valid` (structural admissibility) is established by
the Bridge decoder, as for W1's witnesses: a `FiniteModel`'s relation table is a
function and cannot be enumerated here, so `validate_sound` takes it as a
hypothesis.

`scenarioConflict` evaluates the regenerated conflict formulas on the model
first (4.7); `diagnose` is the untrusted 4.6 procedure. -/
namespace VE.Alternatives
open VE.Norms
universe u

/-- How an entity of a finite model is named in diagnostics. -/
class EntityName (α : Type u) where
  name : α → String

instance : EntityName VE.Bridge.Entity := ⟨fun e => e.2⟩
instance : EntityName String := ⟨id⟩

def modelError (text : String) : String := s!"InvalidModel(alternatives): {text}"

section Model
variable {α : Type u} [DecidableEq α]

/-- The actions available to `r` (in the order of the relation's tuples). -/
def availOf (M : VE.FiniteModel α) (p : String) (r : α) : List α :=
  (M.relations p).filterMap (fun t => match t with
    | [a, r'] => if r' = r then some a else none
    | _ => none)

/-- The choosers to which `a` is available. -/
def ownersOf (M : VE.FiniteModel α) (p : String) (a : α) : List α :=
  (M.relations p).filterMap (fun t => match t with
    | [a', r] => if a' = a then some r else none
    | _ => none)

theorem mem_availOf {M : VE.FiniteModel α} {p : String} {r a : α} :
    a ∈ availOf M p r ↔ [a, r] ∈ M.relations p := by
  simp only [availOf, List.mem_filterMap]
  constructor
  · rintro ⟨t, ht, he⟩
    match t, he with
    | [a', r'], he =>
      by_cases hr : r' = r
      · simp only [hr, if_true, Option.some.injEq] at he
        subst he; subst hr; exact ht
      · simp [hr] at he
  · intro h
    exact ⟨[a, r], h, by simp⟩

theorem mem_ownersOf {M : VE.FiniteModel α} {p : String} {a r : α} :
    r ∈ ownersOf M p a ↔ [a, r] ∈ M.relations p := by
  simp only [ownersOf, List.mem_filterMap]
  constructor
  · rintro ⟨t, ht, he⟩
    match t, he with
    | [a', r'], he =>
      by_cases ha : a' = a
      · simp only [ha, if_true, Option.some.injEq] at he
        subst he; subst ha; exact ht
      · simp [ha] at he
  · intro h
    exact ⟨[a, r], h, by simp⟩

/-- The pair a row names, as denoted in `M`. -/
def rowPair (M : VE.FiniteModel α) (row : Row) : Option α × Option α :=
  (M.constants row.action, M.constants row.harm)

def rowDenotes (M : VE.FiniteModel α) (row : Row) (a h : α) : Bool :=
  M.constants row.action == some a && M.constants row.harm == some h

/-- 3.3: every row is typed, no two rows name one pair, and the positive rows are exactly the
`leads_to` table. -/
def RowsConsistent (A : AltDoc) (M : VE.FiniteModel α) (rows : List Row) : Prop :=
  (∀ row ∈ rows, ∃ a h, M.constants row.action = some a ∧ M.constants row.harm = some h ∧
    a ∈ M.domains A.alt.action ∧ h ∈ M.domains A.alt.harm) ∧
  (rows.map (rowPair M)).Nodup ∧
  (∀ a h, [a, h] ∈ M.relations A.alt.leadsTo ↔
    ∃ row ∈ rows, row.leadsTo = true ∧ M.constants row.action = some a ∧ M.constants row.harm = some h)

/-- E1: every action of the action domain is available to some chooser. -/
def E1 (A : AltDoc) (M : VE.FiniteModel α) : Prop :=
  ∀ a ∈ M.domains A.alt.action, ∃ r, [a, r] ∈ M.relations A.alt.available

/-- E2: when `inaction` is declared, every chooser with an alternative has an inaction among them. -/
def E2 (A : AltDoc) (M : VE.FiniteModel α) : Prop :=
  ∀ p, A.alt.inaction = some p → ∀ r ∈ M.domains A.alt.chooser,
    (∃ a, [a, r] ∈ M.relations A.alt.available) → ∃ a, [a, r] ∈ M.relations A.alt.available ∧ [a] ∈ M.relations p

/-- E3: under `signed`, every (available action, harm) pair has a row. -/
def E3 (A : AltDoc) (M : VE.FiniteModel α) (rows : List Row) : Prop :=
  A.alt.outcomes = .signed → ∀ a r h, [a, r] ∈ M.relations A.alt.available → h ∈ M.domains A.alt.harm →
    ∃ row ∈ rows, M.constants row.action = some a ∧ M.constants row.harm = some h

def ExistenceFacts (A : AltDoc) (M : VE.FiniteModel α) (rows : List Row) : Prop :=
  RowsConsistent A M rows ∧ E1 A M ∧ E2 A M ∧ E3 A M rows

/-! ### The Boolean checks -/

def rowsTypedB (A : AltDoc) (M : VE.FiniteModel α) (rows : List Row) : Bool :=
  rows.all fun row => match M.constants row.action, M.constants row.harm with
    | some a, some h => (M.domains A.alt.action).contains a && (M.domains A.alt.harm).contains h
    | _, _ => false

def rowsAgreeB (A : AltDoc) (M : VE.FiniteModel α) (rows : List Row) : Bool :=
  (M.relations A.alt.leadsTo).all (fun t => match t with
    | [a, h] => rows.any (fun row => row.leadsTo && rowDenotes M row a h)
    | _ => false) &&
  rows.all (fun row => !row.leadsTo || match M.constants row.action, M.constants row.harm with
    | some a, some h => (M.relations A.alt.leadsTo).contains [a, h]
    | _, _ => false)

def rowsB (A : AltDoc) (M : VE.FiniteModel α) (rows : List Row) : Bool :=
  rowsTypedB A M rows && decide (rows.map (rowPair M)).Nodup && rowsAgreeB A M rows

def e1B (A : AltDoc) (M : VE.FiniteModel α) : Bool :=
  (M.domains A.alt.action).all (fun a => !(ownersOf M A.alt.available a).isEmpty)

def e2B (A : AltDoc) (M : VE.FiniteModel α) : Bool :=
  match A.alt.inaction with
  | none => true
  | some p => (M.domains A.alt.chooser).all (fun r => (availOf M A.alt.available r).isEmpty ||
      (availOf M A.alt.available r).any (fun a => (M.relations p).contains [a]))

def e3B (A : AltDoc) (M : VE.FiniteModel α) (rows : List Row) : Bool :=
  match A.alt.outcomes with
  | .completeBy _ => true
  | .signed => (M.relations A.alt.available).all (fun t => match t with
      | [a, _] => (M.domains A.alt.harm).all (fun h => rows.any (fun row => rowDenotes M row a h))
      | _ => true)

/-- Everything `validateAlternatives` decides. -/
def altModelChecks (A : AltDoc) (M : VE.FiniteModel α) (rows : List Row) : Bool :=
  backgroundValidAlt A M && rowsB A M rows && e1B A M && e2B A M && e3B A M rows &&
    A.Γ.all (fun p => p.eval M [])

/-! ### Soundness of the checks -/

theorem rowDenotes_true {M : VE.FiniteModel α} {row : Row} {a h : α} (hr : rowDenotes M row a h = true) :
    M.constants row.action = some a ∧ M.constants row.harm = some h := by
  simpa [rowDenotes] using hr

theorem rowsB_sound {A : AltDoc} {M : VE.FiniteModel α} {rows : List Row} (hb : rowsB A M rows = true) :
    RowsConsistent A M rows := by
  simp only [rowsB, Bool.and_eq_true, decide_eq_true_eq] at hb
  obtain ⟨⟨ht, hd⟩, ha⟩ := hb
  refine ⟨fun row hrow => ?_, hd, fun a h => ?_⟩
  · have := List.all_eq_true.mp ht row hrow
    revert this
    cases hca : M.constants row.action <;> cases hch : M.constants row.harm <;> simp
  · simp only [rowsAgreeB, Bool.and_eq_true, List.all_eq_true] at ha
    obtain ⟨h1, h2⟩ := ha
    constructor
    · intro hm
      have := h1 _ hm
      simp only [List.any_eq_true, Bool.and_eq_true] at this
      obtain ⟨row, hrow, hpos, hden⟩ := this
      exact ⟨row, hrow, hpos, rowDenotes_true hden⟩
    · rintro ⟨row, hrow, hpos, hca, hch⟩
      have := h2 row hrow
      simp only [hpos, Bool.not_true, Bool.false_or, hca, hch, List.contains_iff_mem] at this
      exact this

theorem e1B_sound {A : AltDoc} {M : VE.FiniteModel α} (hb : e1B A M = true) : E1 A M := by
  intro a ha
  have := List.all_eq_true.mp hb a ha
  simp only [Bool.not_eq_eq_eq_not, Bool.not_true, List.isEmpty_eq_false_iff_exists_mem] at this
  obtain ⟨r, hr⟩ := this
  exact ⟨r, mem_ownersOf.mp hr⟩

theorem e2B_sound {A : AltDoc} {M : VE.FiniteModel α} (hb : e2B A M = true) : E2 A M := by
  intro p hp r hr ⟨a, ha⟩
  simp only [e2B, hp] at hb
  have := List.all_eq_true.mp hb r hr
  simp only [Bool.or_eq_true, List.isEmpty_iff, List.any_eq_true, List.contains_iff_mem] at this
  rcases this with he | ⟨a', ha', hi⟩
  · rw [List.eq_nil_iff_forall_not_mem] at he
    exact absurd (mem_availOf.mpr ha) (he a)
  · exact ⟨a', mem_availOf.mp ha', hi⟩

theorem e3B_sound {A : AltDoc} {M : VE.FiniteModel α} {rows : List Row} (hb : e3B A M rows = true) :
    E3 A M rows := by
  intro hs a r h har hh
  simp only [e3B, hs] at hb
  have := List.all_eq_true.mp hb _ har
  simp only [List.all_eq_true, List.any_eq_true] at this
  obtain ⟨row, hrow, hden⟩ := this h hh
  exact ⟨row, hrow, rowDenotes_true hden⟩

/-! ### Failure texts (untrusted: they only render a failed check) -/

variable [EntityName α]

def nm (v : α) : String := EntityName.name v

def ownFailure (A : AltDoc) (M : VE.FiniteModel α) : Option String :=
  (M.relations A.alt.available).findSome? fun t => match t with
    | [a, r] => (ownersOf M A.alt.available a).find? (· ≠ r) |>.map fun r' =>
        s!"action {nm a} is available to two choosers: {nm r}, {nm r'}"
    | _ => none

def oneFailure (A : AltDoc) (M : VE.FiniteModel α) (p what : String) : Option String :=
  (M.domains A.alt.chooser).findSome? fun r =>
    match ((availOf M A.alt.available r).filter (fun a => (M.relations p).contains [a])) with
    | a :: a' :: _ => some s!"{nm r} has two {what}: {nm a}, {nm a'}"
    | _ => none

def proximateFailure (A : AltDoc) (M : VE.FiniteModel α) (p : String) : Option String :=
  (M.relations p).findSome? fun t => match t with
    | [a, h] => if (M.relations A.alt.leadsTo).contains [a, h] then none
        else some s!"{nm a} causes {nm h} but does not lead to it"
    | _ => none

def rowsFailure (A : AltDoc) (M : VE.FiniteModel α) (rows : List Row) : Option String :=
  let label (row : Row) := s!"{row.action}/{row.harm}"
  (rows.findSome? fun row => match M.constants row.action, M.constants row.harm with
    | some a, some h => if (M.domains A.alt.action).contains a && (M.domains A.alt.harm).contains h then none
        else some s!"row {label row} untyped"
    | _, _ => some s!"row {label row} untyped") <|>
  ((List.range rows.length).findSome? fun i => match rows[i]? with
    | some row => if (rows.take i).any (fun r' => rowPair M r' == rowPair M row) then some s!"row {label row} repeated"
        else none
    | none => none) <|>
  (rows.findSome? fun row => match M.constants row.action, M.constants row.harm with
    | some a, some h => if row.leadsTo != (M.relations A.alt.leadsTo).contains [a, h] then
        some s!"row {label row} disagrees with leads_to" else none
    | _, _ => none) <|>
  ((M.relations A.alt.leadsTo).findSome? fun t => match t with
    | [a, h] => if rows.any (fun row => row.leadsTo && rowDenotes M row a h) then none
        else some s!"row {nm a}/{nm h} disagrees with leads_to"
    | _ => some "leads_to has a malformed tuple")

def existenceFailure (A : AltDoc) (M : VE.FiniteModel α) (rows : List Row) : Option String :=
  ((M.domains A.alt.action).findSome? fun a =>
    if (ownersOf M A.alt.available a).isEmpty then some s!"action {nm a} belongs to no chooser" else none) <|>
  (match A.alt.inaction with
    | none => none
    | some p => (M.domains A.alt.chooser).findSome? fun r =>
        if !(availOf M A.alt.available r).isEmpty &&
            !(availOf M A.alt.available r).any (fun a => (M.relations p).contains [a])
        then some s!"{nm r} has no inaction" else none) <|>
  (match A.alt.outcomes with
    | .completeBy _ => none
    | .signed => (M.relations A.alt.available).findSome? fun t => match t with
        | [a, _] => (M.domains A.alt.harm).findSome? fun h =>
            if rows.any (fun row => rowDenotes M row a h) then none
            else some s!"outcome of {nm a} for {nm h} unstated"
        | _ => none)

/-- The first failed check's text, in the order of 4.2 (literals, the four premises, the rows,
E1–E3, `Γ_base`). `labels` names the `Γ_base` formulas; an unlabelled one is `premise <n>`. -/
def failureText (labels : List String) (A : AltDoc) (M : VE.FiniteModel α) (rows : List Row) : String :=
  if !backgroundValid (inlineTree A) M then VE.Route.Wire.invalidModel "literals" else
  let premise := ownFailure A M <|>
    (A.alt.taken.bind fun p => oneFailure A M p "taken actions") <|>
    (A.alt.inaction.bind fun p => oneFailure A M p "inactions") <|>
    (A.alt.proximate.bind fun p => proximateFailure A M p)
  let gamma := (List.range A.Γ.length).findSome? fun i => match A.Γ[i]? with
    | some p => if p.eval M [] then none
        else some s!"premise {(labels[i]?).getD s!"{i + 1}"} fails"
    | none => none
  modelError ((premise <|> rowsFailure A M rows <|> existenceFailure A M rows <|> gamma).getD
    "the model violates an alternatives premise")

def validateAlternativesWith (labels : List String) (A : AltDoc) (M : VE.FiniteModel α) (rows : List Row) :
    Except String Unit :=
  if altModelChecks A M rows then .ok () else .error (failureText labels A M rows)

/-- 4.2 finite validation (the texts of 6 on failure). -/
def validateAlternatives (A : AltDoc) (M : VE.FiniteModel α) (rows : List Row) : Except String Unit :=
  validateAlternativesWith [] A M rows

theorem validateAlternativesWith_ok {labels : List String} {A : AltDoc} {M : VE.FiniteModel α}
    {rows : List Row} : validateAlternativesWith labels A M rows = .ok () ↔ altModelChecks A M rows = true := by
  unfold validateAlternativesWith
  split <;> simp_all

theorem validateAlternatives_labels (labels : List String) (A : AltDoc) (M : VE.FiniteModel α) (rows : List Row) :
    validateAlternativesWith labels A M rows = .ok () ↔ validateAlternatives A M rows = .ok () := by
  unfold validateAlternatives
  rw [validateAlternativesWith_ok, validateAlternativesWith_ok]

end Model

/-- 4.2: successful validation gives every hypothesis `dilemma_witness_sound` needs, plus the rows
and existence facts. `M.Valid` comes from the Bridge decoder (see the module comment). -/
theorem validate_sound {α : Type u} [DecidableEq α] [EntityName α] (A : AltDoc) (M : VE.FiniteModel α)
    (rows : List Row) (valid : M.Valid (envAt (inlineTree A) 0))
    (hv : validateAlternatives A M rows = .ok ()) :
    M.Valid (envAt (inlineTree A) 0) ∧ backgroundValidAlt A M = true ∧ A.Γ.all (fun p => p.eval M []) = true ∧
      BaseAdmissibleAlt A M.asStructure ∧ ExistenceFacts A M rows := by
  have hc := validateAlternativesWith_ok.mp hv
  simp only [altModelChecks, Bool.and_eq_true] at hc
  obtain ⟨⟨⟨⟨⟨hb, hr⟩, h1⟩, h2⟩, h3⟩, hΓ⟩ := hc
  exact ⟨valid, hb, hΓ, baseAdmissibleAlt_of_valid A M valid hb,
    rowsB_sound hr, e1B_sound h1, e2B_sound h2, e3B_sound h3⟩

/-! ## Scenario conflict (4.7) -/

/-- Every tuple of the listed domains, in argument order. -/
def tuples {α : Type u} (M : VE.FiniteModel α) : List String → List (List α)
  | [] => [[]]
  | s :: ss => (M.domains s).flatMap (fun v => (tuples M ss).map (v :: ·))

theorem tuples_typed {α : Type u} (M : VE.FiniteModel α) :
    ∀ (ss : List String) (vs : List α), vs ∈ tuples M ss → VE.TupleTyped M.asStructure ss vs
  | [], vs, h => by simp [tuples] at h; subst h; trivial
  | s :: ss, vs, h => by
    simp only [tuples, List.mem_flatMap, List.mem_map] at h
    obtain ⟨v, hv, ws, hws, rfl⟩ := h
    exact ⟨hv, tuples_typed M ss ws hws⟩

/-- The first regenerated conflict formula of the inlined document true at a typed tuple. -/
def scenarioConflict {α : Type u} [DecidableEq α] (A : AltDoc) (M : VE.FiniteModel α) :
    Option ((String × List String × VE.Formula) × List α) :=
  (targets (inlineTree A)).findSome? fun t =>
    ((tuples M t.2.1).find? (fun vs => t.2.2.eval M (tupleVal vs))).map (t, ·)

/-- 4.7: a scenario answer is rendered only where no regenerated conflict formula holds on the model. -/
theorem scenarioConflict_sound {α : Type u} [DecidableEq α] (A : AltDoc) (h : WellFormedAlt A = true)
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (inlineTree A) 0)) (hb : backgroundValidAlt A M = true)
    (t : String × List String × VE.Formula) (vs : List α) (hc : scenarioConflict A M = some (t, vs)) :
    ¬ ConflictFree (inlineTree A) M.asStructure ∧ ¬ AltConflictFree.{u} A := by
  unfold scenarioConflict at hc
  obtain ⟨t', ht', hf⟩ := List.exists_of_findSome?_eq_some hc
  simp only [Option.map_eq_some_iff, Prod.mk.injEq] at hf
  obtain ⟨vs', hfind, rfl, rfl⟩ := hf
  have hmem := List.mem_of_find?_eq_some hfind
  have heval := List.find?_some hfind
  obtain ⟨h1, _, h3⟩ := alt_conflict_witness_sound A h t' ht' M valid hb vs'
    (tuples_typed M _ vs' hmem) heval
  exact ⟨h1, h3⟩

/-! ## Diagnosis (4.6; untrusted) -/

inductive Diagnosis (α : Type u)
  | noAlternatives
  | nonePermitted
  | overRequired (req : List α)
  | undischargeable (duty : String × List α)
  | jointlyUndischargeable (duties : List (String × List α))
  | clear (actions : List α)

section Diagnose
variable {α : Type u} [DecidableEq α]

def permittedAt (A : AltDoc) (M : VE.FiniteModel α) (a : α) : Bool :=
  match A.alt.performed with
  | some (m, _) => (oBase A m).eval M [a]
  | none => true

def requiredAt (A : AltDoc) (M : VE.FiniteModel α) (a : α) : Bool :=
  match A.alt.performed with
  | some (_, q) => (oBase A q).eval M [a]
  | none => false

/-- The mapped duties on `r`: `(o, x̄)` with `O_o°(r, x̄)`. -/
def duties (A : AltDoc) (M : VE.FiniteModel α) (r : α) : List (Fulfilment × List α) :=
  A.alt.fulfilments.flatMap fun f =>
    ((tuples M (restSorts A f)).filter fun xs => (oBase A f.obligation).eval M (tupleVal (r :: xs))).map (f, ·)

def discharges (M : VE.FiniteModel α) (a : α) (d : Fulfilment × List α) : Bool :=
  d.1.body.eval M (tupleVal (a :: d.2))

/-- Shrink a set of duties with no common discharger in `P` to a minimal one (greedy). -/
def minimalJoint (M : VE.FiniteModel α) (P : List α) : List (Fulfilment × List α) → List (Fulfilment × List α)
  | [] => []
  | d :: ds =>
    let rest := minimalJoint M P ds
    if P.any (fun a => rest.all (discharges M a)) then d :: rest else rest

/-- The 4.6 procedure at a chooser: the classification of a failed `followable°`, or the clear
alternatives. -/
def diagnose (A : AltDoc) (M : VE.FiniteModel α) (r : α) : Diagnosis α :=
  let alts := availOf M A.alt.available r
  let perm := alts.filter (permittedAt A M)
  let req := alts.filter (requiredAt A M)
  if alts.isEmpty then .noAlternatives
  else if perm.isEmpty then .nonePermitted
  else if req.length ≥ 2 then .overRequired req
  else
    let P := perm.filter (fun a => req.all (· == a))
    let ds := duties A M r
    let clear := P.filter (fun a => ds.all (discharges M a))
    match ds.find? (fun d => !P.any (fun a => discharges M a d)) with
    | some d => .undischargeable (d.1.obligation, d.2)
    | none => if clear.isEmpty then
        .jointlyUndischargeable ((minimalJoint M P ds).map (fun d => (d.1.obligation, d.2)))
      else .clear clear

end Diagnose

end VE.Alternatives
