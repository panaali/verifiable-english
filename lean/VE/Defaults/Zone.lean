import VE.Weighing.Zone
import VE.Defaults.Premises

/-!
# DF-5: the zone at one situation, with observations (spec 7.5, plan 3.6)

A default completion of a finite situation is an admissible completion (weighing's `AdmissibleCompletion` over the
whole `X` and `Fill_T`, the switches off unless the record says otherwise) that agrees with the observations and is
minimal in its decision atoms; the unsaid tables vary (D15). `defaultZoneOf` computes the zone of an outcome by
nd-atoms' enumeration (`subsets`, valued by `coneAtomVX` and Kleene evaluation) over every typed open atom of the
situation (`openAtomsAll`), never the query's cone (D10: `cone_minimal_iff` is not proved, so cone pruning is off).
`zoneCharge` counts the record, the open atoms (`openAtomsCount`, equal to `openAtomsAll`'s length) and the typed
atoms arithmetically before any atom, tuple or assignment is listed; past a bound the zone is `unknown` at once. Within
the bounds each value the enumeration reads (the atoms, the record, the premises, the observed outcomes) is let-bound
once per function.
-/

namespace VE.Defaults
open VE.Weighing (AdmissibleCompletion OutcomeIn decisionAtoms openNames SettledZ ZoneUnknown)
open VE.SoftNorms (SoftDoc decisionNames offDecisions outweighsTriples)
open VE.NormDefaults (UDoc)
open VE.NormDefaults.Wire (LayeredU)

/-- `R₁` holds no decision atom of the situation that `R₂` lacks. Only decision atoms are compared; the unsaid atoms
    of the two completions are free to differ (D15, as `DefaultBase`). -/
def DecLe {α : Type} (D : SoftDoc) (M : VE.FiniteModel α) (R₁ R₂ : String → List α → Prop) : Prop :=
  ∀ a ∈ decisionAtoms D M, R₁ a.1 a.2 → R₂ a.1 a.2

/-- Each observed outcome has its observed value. -/
def Observed {α : Type} (U : UDoc) (M : VE.FiniteModel α) (obs : List ((VE.Norms.Regulated × List α) × Bool))
    (R : String → List α → Prop) : Prop :=
  ∀ o ∈ obs, (OutcomeIn U M R o.1.1 o.1.2 ↔ o.2 = true)

/-- Switches off, except where the record says otherwise. -/
def switchesOffRecord {α : Type} [DecidableEq α] (D : SoftDoc) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) : List ((String × List α) × Bool) :=
  (offDecisions D).flatMap (fun (n, ss) => (VE.NormDefaults.allTuples M ss).filterMap (fun vs =>
    if record.any (fun r => r.1 == (n, vs)) then none else some ((n, vs), false)))

/-- A default completion: admissible with the record and the switches off, agreeing with the observations, and minimal
    in decisions among such completions. `R'` ranges over every admissible completion, whose open atoms are the decision
    and the unsaid atoms (`openNames`), so its unsaid tables vary; the facts and the domain are `M`'s, fixed by
    `AdmissibleCompletion`. This is `DefaultBase`'s comparison at one situation. -/
def DefaultCompletion {α : Type} [DecidableEq α] (L : LayeredU) (X : List VE.Formula) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) (obs : List ((VE.Norms.Regulated × List α) × Bool))
    (R : String → List α → Prop) : Prop :=
  let rec' := record ++ switchesOffRecord L.D M record
  AdmissibleCompletion L.U X M (openNames L) rec' R ∧ Observed L.U M obs R ∧
  ∀ R', AdmissibleCompletion L.U X M (openNames L) rec' R' → Observed L.U M obs R' → DecLe L.D M R' R →
    DecLe L.D M R R'

/-- By default `b`: every default completion gives `b`, and at least one exists. -/
def ByDefaultZ {α : Type} [DecidableEq α] (L : LayeredU) (X : List VE.Formula) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) (obs : List ((VE.Norms.Regulated × List α) × Bool))
    (r : VE.Norms.Regulated) (vs : List α) (b : Bool) : Prop :=
  (∃ R, DefaultCompletion L X M record obs R) ∧
  ∀ R, DefaultCompletion L X M record obs R → (OutcomeIn L.U M R r vs ↔ b = true)

/-- Left to a decider: two default completions with the same unsaid tables differ on the outcome. -/
def ByDefaultLeftTo {α : Type} [DecidableEq α] (L : LayeredU) (X : List VE.Formula) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) (obs : List ((VE.Norms.Regulated × List α) × Bool))
    (r : VE.Norms.Regulated) (vs : List α) : Prop :=
  ∃ R₁ R₂, DefaultCompletion L X M record obs R₁ ∧ DefaultCompletion L X M record obs R₂ ∧
    (∀ n ∈ VE.NormDefaults.unsaidNames L.U, ∀ ws, R₁ n ws ↔ R₂ n ws) ∧
    OutcomeIn L.U M R₁ r vs ∧ ¬ OutcomeIn L.U M R₂ r vs

/-- The zone of an outcome at a tuple; each witness is an assignment of the enumerated atoms. -/
inductive DefaultZone (α : Type)
  | byDefault (b : Bool) (witness : List ((String × List α) × Bool))
  | leftTo (differ : List (String × List α)) (w₁ w₂ : List ((String × List α) × Bool))
  | notSaid (w₁ w₂ : List ((String × List α) × Bool))
  | noCompletion (labels : List String)
  | unknown (reason : ZoneUnknown α)

/-- The bound on the open atoms enumerated: every typed open atom of the situation not fixed by the record. -/
def maxDefaultAtoms : Nat := 12

/-- Every typed open atom of `M` not fixed by the record: the decision atoms, and the unsaid atoms under
    `norm-defaults@0`. Not a cone: the question's atoms, the observations' atoms and every atom a premise of X or
    `Fill_T` names are all in it. -/
def openAtomsAll {α : Type} [DecidableEq α] (L : LayeredU) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) : List (String × List α) :=
  (decisionAtoms L.D M ++ L.U.unspec.flatMap (fun p =>
      (VE.NormDefaults.allTuples M (VE.NormDefaults.sortsOf L.U.D p)).map (fun vs => (VE.NormDefaults.unsaidName p, vs)))).filter
    (fun a => !record.any (fun r => r.1 == a))

/-- One assignment `A` of the enumerated atoms `C` (true exactly on `A`; the record's atoms at their values, nd-atoms'
    `coneAtomVX`), checked by Kleene evaluation: `.error l` when the check labelled `l` refutes it (an atom of `A`
    that is not a declared typed atom, a premise of `P`, an observation), `.ok true` when every premise holds and every
    observation has its value, `.ok false` when a value stays unknown. -/
def zoneRow {α : Type} [DecidableEq α] (M : VE.FiniteModel α) (opens : List String)
    (record : List ((String × List α) × Bool)) (C ok : List (String × List α)) (P : List (String × VE.Formula))
    (obs : List ((VE.Formula × List α) × Bool)) (A : List (String × List α)) : Except String Bool :=
  if A.all (ok.contains ·) then
    let V := VE.NormDefaults.coneAtomVX M opens record C A
    let pv := P.map (fun e => (e.1, VE.NormDefaults.kleene M V [] e.2))
    let ov := obs.map (fun o => (VE.NormDefaults.kleene M V o.1.2 o.1.1, o.2))
    match pv.find? (fun e => e.2 == some false) with
    | some e => .error e.1
    | none =>
      if ov.any (fun o => o.1 == some (!o.2)) then .error "observed"
      else .ok (pv.all (fun e => e.2 == some true) && ov.all (fun o => o.1 == some o.2))
  else .error "typing"

/-- `A`'s true decision atoms (those in `dec`) are among `B`'s. -/
def decSub {α : Type} [DecidableEq α] (dec A B : List (String × List α)) : Bool :=
  A.all (fun a => !dec.contains a || B.contains a)

/-- The atoms `defaultZoneOf` enumerates: `openAtomsAll` without the atoms the switches-off record fixes. -/
def zoneAtoms {α : Type} [DecidableEq α] (L : LayeredU) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) : List (String × List α) :=
  let off := switchesOffRecord L.D M record
  (openAtomsAll L M record).filter (fun a => !off.any (fun e => e.1 == a))

/-- An atom of the situation is a declared predicate of the filled base environment at a typed tuple. -/
def zoneDeclOk {α : Type} [DecidableEq α] (L : LayeredU) (M : VE.FiniteModel α) (a : String × List α) : Bool :=
  match (VE.Norms.envAt (VE.NormDefaults.fill L.U) 0).predicates a.1 with
  | some ss => VE.NormDefaults.tupleTypedB M ss a.2
  | none => false

/-- The record can be met: each entry is the first entry for its atom, agrees with `M` off the open names, and is a
    declared typed atom when true. -/
def zoneRecordOk {α : Type} [DecidableEq α] (L : LayeredU) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) : Bool :=
  record.all (fun e => (record.find? (fun e' => decide (e'.1 = e.1))).map (·.2) == some e.2 &&
    (decide (e.1.1 ∈ openNames L) || (decide (e.1.2 ∈ M.relations e.1.1) == e.2)) &&
    (!e.2 || zoneDeclOk L M e.1))

/-! ## The charge: sizes counted before anything is listed -/

/-- The number of tuples `allTuples M ss` lists (`length_allTuples`), counted without listing them. -/
def tupleCount {α : Type} (M : VE.FiniteModel α) : List String → Nat
  | [] => 1
  | s :: ss => (M.domains s).length * tupleCount M ss

/-- How often `allTuples M ss` lists `vs` (`count_allTuples`), counted without listing it. -/
def tupleMult {α : Type} [DecidableEq α] (M : VE.FiniteModel α) : List String → List α → Nat
  | [], [] => 1
  | s :: ss, v :: vs => (M.domains s).count v * tupleMult M ss vs
  | _, _ => 0

/-- How many entries of `allTuples M ss` are not in `S` (`tuplesOutside_eq`), counted without listing them. -/
def tuplesOutside {α : Type} [DecidableEq α] (M : VE.FiniteModel α) (ss : List String) : List (List α) → Nat
  | [] => tupleCount M ss
  | vs :: S => tuplesOutside M ss S - (if S.contains vs then 0 else tupleMult M ss vs)

/-- The predicates `openAtomsAll` lists atoms of, each with its sorts: the decisions, then the unsaid predicates. -/
def zoneGens (L : LayeredU) : List (String × List String) :=
  VE.SoftNorms.decisions L.D ++
    L.U.unspec.map (fun p => (VE.NormDefaults.unsaidName p, VE.NormDefaults.sortsOf L.U.D p))

/-- The tuples the record fixes at predicate `p`. -/
def recTuples {α : Type} (record : List ((String × List α) × Bool)) (p : String) : List (List α) :=
  record.filterMap (fun e => if e.1.1 == p then some e.1.2 else none)

/-- `(openAtomsAll L M record).length` (`openAtomsCount_eq`), counted from the sorts' sizes and the record without
    listing an atom or a tuple. With the empty record it counts every typed decision and unsaid atom. -/
def openAtomsCount {α : Type} [DecidableEq α] (L : LayeredU) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) : Nat :=
  ((zoneGens L).map (fun g => tuplesOutside M g.2 (recTuples record g.1))).sum

/-- The bound on the record's entries; with `maxDefaultAtoms`, the bound on the typed atoms listed. -/
def maxZoneRecord : Nat := 1024

/-- The charge, before any atom, tuple or record entry is listed (the evaluator rule: never a long run or a large
    allocation). `unknown (branch [] "record size")` for a record of more than `maxZoneRecord` entries;
    `unknown (budget n maxDefaultAtoms)` when more than `maxDefaultAtoms` atoms are open (`n` counted by
    `openAtomsCount`); `unknown (branch [] "size")` when the situation has more than `maxZoneRecord + maxDefaultAtoms`
    typed decision and unsaid atoms (with at most `maxDefaultAtoms` open, only a domain or a predicate listed twice
    gets there). `none` when every list `zoneMin` and `zoneForm` build is within these bounds. -/
def zoneCharge {α : Type} [DecidableEq α] (L : LayeredU) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) : Option (DefaultZone α) :=
  if maxZoneRecord < record.length then some (.unknown (.branch [] "record size")) else
  let n := openAtomsCount L M record
  if maxDefaultAtoms < n then some (.unknown (.budget n maxDefaultAtoms)) else
  if maxZoneRecord + maxDefaultAtoms < openAtomsCount L M [] then some (.unknown (.branch [] "size")) else none

/-- The enumeration and the minimality filter: `.error` with the zone when it ends early (`zoneCharge`, a record or
    background no completion meets, an assignment left unknown, no assignment left), otherwise `.ok` with the
    decision-minimal assignments that pass every check. Nothing is listed before `zoneCharge` passes. -/
def zoneMin {α : Type} [DecidableEq α] (L : LayeredU) (X : List (String × VE.Formula)) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) (obs : List ((VE.Norms.Regulated × List α) × Bool)) :
    Except (DefaultZone α) (List (List (String × List α))) :=
  match zoneCharge L M record with
  | some z => .error z
  | none =>
  let rec' := record ++ switchesOffRecord L.D M record
  if !zoneRecordOk L M rec' then .error (.noCompletion ["record"]) else
  if !(VE.Norms.backgroundBase (VE.NormDefaults.fill L.U)).all (·.eval M []) then
    .error (.noCompletion ["background"]) else
  let C := zoneAtoms L M record
  let ok := C.filter (zoneDeclOk L M)
  let P := X ++ (VE.NormDefaults.fillPremises L.U).map (fun ψ => ("fill", ψ))
  let obsF := obs.map (fun o =>
    ((VE.Norms.outcomeBase (VE.NormDefaults.fill L.U) o.1.1.name, VE.Norms.tupleVal o.1.2), o.2))
  let opens := openNames L
  let rows := (VE.NormDefaults.subsets C).map (fun A => (A, zoneRow M opens rec' C ok P obsF A))
  match rows.find? (fun x => x.2.toOption == some false) with
  | some x => .error (.unknown (.branch (C.map (fun a => (a, x.1.contains a))) "none checked"))
  | none =>
    let S := (rows.filter (fun x => x.2.toOption == some true)).map (·.1)
    if S.isEmpty then
      .error (.noCompletion (rows.filterMap (fun x => match x.2 with | .error l => some l | .ok _ => none)).eraseDups)
    else
      let dec := decisionAtoms L.D M
      .ok (S.filter (fun A => S.all (fun B => !decSub dec B A || decSub dec A B)))

/-- The zone of the outcome `r` at `vs` from `zoneMin`'s minimal assignments `Min` (`defaultZoneOf`'s answer after a
    complete enumeration; `defaultZoneOf_eq`): the wire reads `zoneMin` once and gives its result here and to
    `forcedOfMin` (DRI 2026-11-04, df-5 item 2). -/
def zoneOfMin {α : Type} [DecidableEq α] (L : LayeredU) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) (r : VE.Norms.Regulated) (vs : List α)
    (Min : List (List (String × List α))) : DefaultZone α :=
    let rec' := record ++ switchesOffRecord L.D M record
    let C := zoneAtoms L M record
    let φ := VE.Norms.outcomeBase (VE.NormDefaults.fill L.U) r.name
    let opens := openNames L
    let wit := fun (A : List (String × List α)) => C.map (fun a => (a, A.contains a))
    let qv := Min.map (fun A => (A, VE.NormDefaults.kleene M (VE.NormDefaults.coneAtomVX M opens rec' C A)
      (VE.Norms.tupleVal vs) φ))
    match qv.find? (fun x => x.2 == none) with
    | some x => .unknown (.branch (wit x.1) "none checked")
    | none =>
      let vals := qv.filterMap (fun x => x.2.map (x.1, ·))
      match vals with
      | [] => .unknown (.branch [] "none checked")
      | (A, b) :: _ =>
        if vals.all (·.2 == b) then .byDefault b (wit A) else
        let un := VE.NormDefaults.unsaidNames L.U
        let dec := decisionAtoms L.D M
        let pairs := vals.flatMap (fun x => vals.map (x, ·))
        match pairs.find? (fun p => p.1.2 && !p.2.2 &&
            C.all (fun a => !un.contains a.1 || (p.1.1.contains a == p.2.1.contains a))) with
        | some p => .leftTo (C.filter (fun a => dec.contains a && (p.1.1.contains a != p.2.1.contains a)))
            (wit p.1.1) (wit p.2.1)
        | none =>
          match pairs.find? (fun p => p.1.2 && !p.2.2) with
          | some p => .notSaid (wit p.1.1) (wit p.2.1)
          | none => .unknown (.branch [] "none checked")

/-- nd-atoms' bounded enumeration over `openAtomsAll` (C10) (the atom list given, no cone pruning; `zoneCharge` first,
    so `unknown (budget)` beyond `maxDefaultAtoms` is counted, never listed), then the full assignments that satisfy X
    and `Fill_T` (each premise evaluated on the finite situation) and agree with the observations, then the minimality
    filter over their decision parts. The record and the atom list are built once in `zoneMin` and once here, both
    after the charge. -/
def defaultZoneOf {α : Type} [DecidableEq α] (L : LayeredU) (X : List (String × VE.Formula)) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) (obs : List ((VE.Norms.Regulated × List α) × Bool))
    (r : VE.Norms.Regulated) (vs : List α) (proposed : List (List ((String × List α) × Bool))) : DefaultZone α :=
  have _ := proposed
  match zoneMin L X M record obs with
  | .error z => z
  | .ok Min => zoneOfMin L M record r vs Min

/-- DE10's first form ("no exceptions here …", `short`) only when every decision atom the record leaves open is an
    exception; otherwise the second ("no assumptions here …", `long`). -/
def zoneForm {α : Type} [DecidableEq α] (L : LayeredU) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) : Form :=
  if (openAtomsAll L M (record ++ switchesOffRecord L.D M record)).all (fun a =>
      !(decisionNames L.D).contains a.1 || (VE.SoftNorms.exceptedDecisions L.D).any (·.1 == a.1))
  then .short else .long

/-- `zoneForm` behind `zoneCharge`: `none` when the charge stops, so the form never lists the atoms of a situation
    `defaultZoneOf` does not enumerate. The entry a renderer calls. -/
def zoneFormOf {α : Type} [DecidableEq α] (L : LayeredU) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) : Option Form :=
  match zoneCharge L M record with
  | some _ => none
  | none => some (zoneForm L M record)

/-- Weighing's record "assuming no exception applies": every `excepted` atom of the situation set to false. -/
def noExceptionRecord {α : Type} (D : SoftDoc) (M : VE.FiniteModel α) : List ((String × List α) × Bool) :=
  (VE.SoftNorms.exceptedDecisions D).flatMap (fun (n, ss) =>
    (VE.NormDefaults.allTuples M ss).map (fun vs => ((n, vs), false)))

/-- `forcedAllOf`'s list from `zoneMin`'s minimal assignments `Min` (`forcedAllOf_eq`); `none` when `Min` is empty. -/
def forcedOfMin {α : Type} [DecidableEq α] (L : LayeredU) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) (Min : List (List (String × List α))) :
    Option (List (String × List α)) :=
    if Min.isEmpty then none else
    let C := zoneAtoms L M record
    let V₀ := VE.NormDefaults.coneAtomVX M (openNames L) (record ++ switchesOffRecord L.D M record) C []
    some (((noExceptionRecord L.D M).map (·.1)).filter (fun a =>
      if C.contains a then Min.all (·.contains a) else V₀ a.1 a.2 == some true)).eraseDups

/-- The exception atoms true in every default completion, from the same complete enumeration as `defaultZoneOf`;
    `none` when that enumeration is not complete (the budget, or a branch left unknown) or finds no default
    completion. "The facts here force <e>" is rendered only from a `some` list. An atom the enumeration varies is
    forced when every minimal assignment holds it; any other atom has one value in every assignment (the record's, or
    `M`'s), read once from the empty one. Each atom is listed once. -/
def forcedAllOf {α : Type} [DecidableEq α] (L : LayeredU) (X : List (String × VE.Formula)) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) (obs : List ((VE.Norms.Regulated × List α) × Bool))
    (proposed : List (List ((String × List α) × Bool))) : Option (List (String × List α)) :=
  have _ := proposed
  match zoneMin L X M record obs with
  | .error _ => none
  | .ok Min => forcedOfMin L M record Min

/-! ## Proofs -/

section Proofs
variable {α : Type} [DecidableEq α]
open VE.NormDefaults (coneAtomVX coneAtomVO kleene subsets)
variable {M : VE.FiniteModel α} {opens : List String} {rec' : List ((String × List α) × Bool)}
  {C ok A : List (String × List α)} {P : List (String × VE.Formula)} {ob : List ((VE.Formula × List α) × Bool)}

/-! ### The charge counts exactly what `openAtomsAll` lists -/

theorem sum_replicate_zone (n c : Nat) : (List.replicate n c).sum = n * c := by
  induction n with
  | zero => simp
  | succ n ih => simp [List.replicate_succ, ih, Nat.succ_mul, Nat.add_comm]

theorem count_map_cons (v v' : α) (vs : List α) :
    ∀ L : List (List α), (L.map (v' :: ·)).count (v :: vs) = if v' = v then L.count vs else 0
  | [] => by simp
  | w :: L => by
    have ih := count_map_cons v v' vs L
    simp only [List.map_cons, List.count_cons, ih, List.cons.injEq, beq_iff_eq]
    by_cases h : v' = v <;> simp [h]

theorem sum_ite_count (v : α) (c : Nat) :
    ∀ D : List α, (D.map (fun v' => if v' = v then c else 0)).sum = D.count v * c
  | [] => by simp
  | w :: D => by
    have ih := sum_ite_count v c D
    simp only [List.map_cons, List.sum_cons, ih, List.count_cons, beq_iff_eq]
    by_cases h : w = v <;> simp [h, Nat.add_mul, Nat.add_comm]

omit [DecidableEq α] in
theorem length_allTuples (M : VE.FiniteModel α) :
    ∀ ss, (VE.NormDefaults.allTuples M ss).length = tupleCount M ss
  | [] => by simp [VE.NormDefaults.allTuples, tupleCount]
  | s :: ss => by
    simp only [VE.NormDefaults.allTuples, tupleCount, List.length_flatMap, List.length_map, length_allTuples M ss,
      List.map_const', sum_replicate_zone]

theorem count_allTuples (M : VE.FiniteModel α) :
    ∀ ss vs, (VE.NormDefaults.allTuples M ss).count vs = tupleMult M ss vs
  | [], [] => by simp [VE.NormDefaults.allTuples, tupleMult]
  | [], _ :: _ => by simp [VE.NormDefaults.allTuples, tupleMult]
  | s :: ss, [] => by
    simp only [VE.NormDefaults.allTuples, tupleMult, List.count_eq_zero, List.mem_flatMap, List.mem_map]
    rintro ⟨_, _, _, _, h⟩
    cases h
  | s :: ss, v :: vs => by
    simp only [VE.NormDefaults.allTuples, tupleMult, List.count_flatMap, Function.comp_def, count_map_cons,
      count_allTuples M ss vs, sum_ite_count]

theorem length_filter_ne {β : Type} [BEq β] [LawfulBEq β] (p : β → Bool) (x : β) :
    ∀ l : List β, (l.filter (fun v => !(v == x) && p v)).length + (if p x then l.count x else 0) =
      (l.filter p).length
  | [] => by simp
  | y :: l => by
    have ih := length_filter_ne p x l
    rw [List.filter_cons, List.filter_cons, List.count_cons]
    by_cases hy : y = x
    · subst hy
      cases hp : p y <;> simp only [hp, beq_self_eq_true, Bool.not_true, Bool.false_and, Bool.false_eq_true,
        ↓reduceIte, List.length_cons] at ih ⊢ <;> omega
    · have hb : (y == x) = false := by simpa [beq_iff_eq] using hy
      cases hp : p y <;> cases hpx : p x <;> simp only [hp, hpx, hb, Bool.not_false, Bool.true_and,
        Bool.false_eq_true, ↓reduceIte, List.length_cons, Nat.add_zero] at ih ⊢ <;> omega

theorem tuplesOutside_eq (M : VE.FiniteModel α) (ss : List String) :
    ∀ S, tuplesOutside M ss S = ((VE.NormDefaults.allTuples M ss).filter (fun vs => !S.contains vs)).length
  | [] => by
    rw [tuplesOutside, ← length_allTuples]
    congr 1
    exact (List.filter_eq_self.mpr (by simp)).symm
  | x :: S => by
    have h := length_filter_ne (fun v => !S.contains v) x (VE.NormDefaults.allTuples M ss)
    have e : (fun v => !(x :: S).contains v) = (fun v => !(v == x) && !S.contains v) := by
      funext v; rw [List.contains_cons, Bool.not_or]
    rw [count_allTuples] at h
    rw [tuplesOutside, tuplesOutside_eq M ss S, e]
    cases hx : S.contains x <;> simp only [hx, Bool.not_false, Bool.not_true, ↓reduceIte, Bool.false_eq_true] at h ⊢
      <;> omega

theorem any_eq_recTuples (record : List ((String × List α) × Bool)) (p : String) (vs : List α) :
    record.any (fun r => r.1 == (p, vs)) = (recTuples record p).contains vs := by
  induction record with
  | nil => simp [recTuples]
  | cons e record ih =>
    rcases e with ⟨⟨q, ws⟩, b⟩
    simp only [recTuples] at ih ⊢
    rw [List.any_cons, List.filterMap_cons, ih]
    by_cases h : q = p
    · subst h
      simp only [beq_self_eq_true, ↓reduceIte, List.contains_cons]
      congr 1
      rw [Bool.eq_iff_iff, beq_iff_eq, beq_iff_eq]
      exact ⟨fun h => ((Prod.mk.inj h).2).symm, fun h => h ▸ rfl⟩
    · have h' : (q == p) = false := by simpa using h
      simp only [h', Bool.false_eq_true, ↓reduceIte]
      simp [h]

/-- The charge's count is `openAtomsAll`'s length, so `unknown (budget n _)` names the exact number of open atoms
    without listing them. -/
theorem openAtomsCount_eq (L : LayeredU) (M : VE.FiniteModel α) (record : List ((String × List α) × Bool)) :
    openAtomsCount L M record = (openAtomsAll L M record).length := by
  have hL : decisionAtoms L.D M ++ L.U.unspec.flatMap (fun p =>
      (VE.NormDefaults.allTuples M (VE.NormDefaults.sortsOf L.U.D p)).map
        (fun vs => (VE.NormDefaults.unsaidName p, vs))) =
      (zoneGens L).flatMap (fun g => (VE.NormDefaults.allTuples M g.2).map (g.1, ·)) := by
    simp only [decisionAtoms, zoneGens, List.flatMap_append, List.flatMap_map]
  unfold openAtomsAll openAtomsCount
  rw [hL, List.filter_flatMap, List.length_flatMap]
  congr 1
  apply List.map_congr_left
  intro g _
  rw [List.filter_map, List.length_map, tuplesOutside_eq]
  congr 1
  apply List.filter_congr
  intro vs _
  simp only [Function.comp_def, any_eq_recTuples]

/-- What the charge answers: the exact budget, or a branch left unknown; never a zone with a completion. -/
theorem zoneCharge_some {L : LayeredU} {record : List ((String × List α) × Bool)} {z : DefaultZone α}
    (h : zoneCharge L M record = some z) :
    (z = .unknown (.budget (openAtomsAll L M record).length maxDefaultAtoms) ∧
      maxDefaultAtoms < (openAtomsAll L M record).length) ∨ ∃ w y, z = .unknown (.branch w y) := by
  unfold zoneCharge at h
  rw [← openAtomsCount_eq]
  split at h
  · cases h; exact Or.inr ⟨_, _, rfl⟩
  simp only at h
  split at h
  · rename_i hn; cases h; exact Or.inl ⟨rfl, hn⟩
  split at h
  · cases h; exact Or.inr ⟨_, _, rfl⟩
  · cases h

/-- The form behind the charge is `zoneForm`'s, and it is given exactly when the charge passes. -/
theorem zoneFormOf_eq {L : LayeredU} {record : List ((String × List α) × Bool)} :
    zoneFormOf L M record = (if (zoneCharge L M record).isSome then none else some (zoneForm L M record)) := by
  unfold zoneFormOf
  split <;> rename_i h <;> simp [h]

theorem mem_of_mem_subsets {β : Type} : ∀ {C A : List β}, A ∈ subsets C → ∀ a ∈ A, a ∈ C
  | [], A, h => by simp only [subsets, List.mem_singleton] at h; subst h; simp
  | x :: xs, A, h => by
    simp only [subsets, List.mem_append, List.mem_map] at h
    rcases h with h | ⟨B, hB, rfl⟩
    · exact fun a ha => List.mem_cons_of_mem _ (mem_of_mem_subsets h a ha)
    · intro a ha
      rcases List.mem_cons.mp ha with rfl | ha
      · exact List.mem_cons_self
      · exact List.mem_cons_of_mem _ (mem_of_mem_subsets hB a ha)

theorem zoneRow_true (h : zoneRow M opens rec' C ok P ob A = .ok true) :
    (∀ a ∈ A, a ∈ ok) ∧ (∀ e ∈ P, kleene M (coneAtomVX M opens rec' C A) [] e.2 = some true) ∧
      ∀ o ∈ ob, kleene M (coneAtomVX M opens rec' C A) o.1.2 o.1.1 = some o.2 := by
  unfold zoneRow at h
  split at h
  · rename_i hA
    simp only at h
    split at h <;> try (cases h; done)
    · split at h
      · cases h
      · simp only [Except.ok.injEq, Bool.and_eq_true, List.all_map, List.all_eq_true, Function.comp_def,
          beq_iff_eq] at h
        exact ⟨fun a ha => by simpa using List.all_eq_true.mp hA a ha, h.1, h.2⟩
  · cases h

theorem zoneRow_ok (hA : ∀ a ∈ A, a ∈ ok)
    (hP : ∀ e ∈ P, kleene M (coneAtomVX M opens rec' C A) [] e.2 ≠ some false)
    (hO : ∀ o ∈ ob, kleene M (coneAtomVX M opens rec' C A) o.1.2 o.1.1 ≠ some (!o.2)) :
    ∃ t, zoneRow M opens rec' C ok P ob A = .ok t := by
  unfold zoneRow
  rw [if_pos (List.all_eq_true.mpr fun a ha => by simpa using hA a ha)]
  simp only
  rw [List.find?_eq_none.mpr (fun e he => by obtain ⟨x, hx, rfl⟩ := List.mem_map.mp he; simpa using hP x hx)]
  rw [if_neg (by
    simp only [List.any_eq_true, not_exists, not_and]
    intro o ho
    obtain ⟨x, hx, rfl⟩ := List.mem_map.mp ho
    simpa using hO x hx)]
  exact ⟨_, rfl⟩

/-- A completion that agrees with `M` off `opens`, with the record, and with `A` on `C` is consistent with
    `coneAtomVX`'s valuation of `A`. -/
theorem consistent_atomV {R : String → List α → Prop}
    (hoff : ∀ n vs, n ∉ opens → (R n vs ↔ vs ∈ M.relations n))
    (hrec : ∀ a b, (a, b) ∈ rec' → (R a.1 a.2 ↔ b = true)) (hA : ∀ a ∈ C, (R a.1 a.2 ↔ a ∈ A)) :
    ∀ p vs c, coneAtomVX M opens rec' C A p vs = some c → (R p vs ↔ c = true) := by
  intro p vs c hc
  unfold coneAtomVX at hc
  split at hc
  · rename_i e he
    simp only [Option.some.injEq] at hc
    subst hc
    have hp : e.1 = (p, vs) := by simpa using List.find?_some he
    have := hrec e.1 e.2 (by simpa using List.mem_of_find?_eq_some he)
    rwa [hp] at this
  unfold coneAtomVO at hc
  split at hc
  · split at hc
    · rename_i hC
      simp only [Option.some.injEq] at hc
      subst hc
      simpa using hA _ hC
    · cases hc
  · rename_i hun
    simp only [Option.some.injEq] at hc
    subst hc
    simpa using hoff p vs hun

theorem zoneDeclOk_iff (L : LayeredU) (M : VE.FiniteModel α) (a : String × List α) :
    zoneDeclOk L M a = true ↔ ∃ ss, (VE.Norms.envAt (VE.NormDefaults.fill L.U) 0).predicates a.1 = some ss ∧
      VE.TupleTyped M.asStructure ss a.2 := by
  unfold zoneDeclOk
  split
  · rename_i ss h
    simp only [h, Option.some.injEq, exists_eq_left']
    exact VE.NormDefaults.tupleTypedB_iff M ss a.2
  · rename_i h
    simp [h]

/-- The completion an assignment `A` stands for: true exactly where `coneAtomVX` gives `true`. -/
theorem realized_off (hoffrec : ∀ e ∈ rec', e.1.1 ∉ opens → (e.1.2 ∈ M.relations e.1.1 ↔ e.2 = true))
    (n : String) (vs : List α) (hn : n ∉ opens) :
    coneAtomVX M opens rec' C A n vs = some true ↔ vs ∈ M.relations n := by
  unfold coneAtomVX
  split
  · rename_i e he
    have hp : e.1 = (n, vs) := by simpa using List.find?_some he
    have := hoffrec e (List.mem_of_find?_eq_some he)
    rw [hp] at this
    simpa using (this hn).symm
  · simp [coneAtomVO, hn]

theorem realized_rec (hfirst : ∀ e ∈ rec', (rec'.find? (fun e' => decide (e'.1 = e.1))).map (·.2) = some e.2)
    (a : String × List α) (b : Bool) (h : (a, b) ∈ rec') :
    coneAtomVX M opens rec' C A a.1 a.2 = some true ↔ b = true := by
  have hf := hfirst _ h
  unfold coneAtomVX
  obtain ⟨e, he, hb⟩ := Option.map_eq_some_iff.mp hf
  simp only at hb
  rw [show (rec'.find? fun e => decide (e.1 = (a.1, a.2))) = some e from he]
  simp [hb]

theorem realized_C (a : String × List α) (hC : a ∈ C) (ho : a.1 ∈ opens)
    (hr : ∀ b, (a, b) ∉ rec') :
    coneAtomVX M opens rec' C A a.1 a.2 = some true ↔ a ∈ A := by
  unfold coneAtomVX
  rw [List.find?_eq_none.mpr (fun e he hd => hr e.2 (by
    have : e.1 = a := by simpa using hd
    rw [← this]; exact he))]
  simp [coneAtomVO, ho, hC]

theorem decLe_iff {D : SoftDoc} {M : VE.FiniteModel α} {rec' : List ((String × List α) × Bool)}
    {C A₁ A₂ : List (String × List α)} {R₁ R₂ : String → List α → Prop}
    (hdec : ∀ a ∈ decisionAtoms D M, (∃ b, (a, b) ∈ rec') ∨ a ∈ C)
    (h₁ : ∀ a b, (a, b) ∈ rec' → (R₁ a.1 a.2 ↔ b = true)) (h₂ : ∀ a b, (a, b) ∈ rec' → (R₂ a.1 a.2 ↔ b = true))
    (hA₁ : ∀ a ∈ C, (R₁ a.1 a.2 ↔ a ∈ A₁)) (hA₂ : ∀ a ∈ C, (R₂ a.1 a.2 ↔ a ∈ A₂)) (hsub : ∀ a ∈ A₁, a ∈ C) :
    DecLe D M R₁ R₂ ↔ decSub (decisionAtoms D M) A₁ A₂ = true := by
  unfold DecLe decSub
  simp only [List.all_eq_true, Bool.or_eq_true, Bool.not_eq_true', Bool.eq_false_iff, ne_eq,
    List.contains_iff_mem]
  constructor
  · intro h a ha
    by_cases hd : a ∈ decisionAtoms D M
    · exact Or.inr ((hA₂ a (hsub a ha)).mp (h a hd ((hA₁ a (hsub a ha)).mpr ha)))
    · exact Or.inl (by simpa using hd)
  · intro h a hd hr
    rcases hdec a hd with ⟨b, hb⟩ | hC
    · exact (h₂ a b hb).mpr ((h₁ a b hb).mp hr)
    · rcases h a ((hA₁ a hC).mp hr) with h' | h'
      · exact absurd hd (by simpa using h')
      · exact (hA₂ a hC).mpr h'

theorem toOption_eq_some {x : Except String Bool} {b : Bool} : x.toOption = some b ↔ x = .ok b := by
  cases x <;> simp [Except.toOption]

/-- The row `zoneMin` computes for an assignment. -/
abbrev zRow (L : LayeredU) (X : List (String × VE.Formula)) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) (obs : List ((VE.Norms.Regulated × List α) × Bool))
    (A : List (String × List α)) : Except String Bool :=
  zoneRow M (openNames L) (record ++ switchesOffRecord L.D M record) (zoneAtoms L M record)
    ((zoneAtoms L M record).filter (zoneDeclOk L M)) (X ++ (VE.NormDefaults.fillPremises L.U).map (fun ψ => ("fill", ψ)))
    (obs.map (fun o => ((VE.Norms.outcomeBase (VE.NormDefaults.fill L.U) o.1.1.name, VE.Norms.tupleVal o.1.2), o.2))) A

/-- The valuation of an assignment. -/
abbrev zV (L : LayeredU) (M : VE.FiniteModel α) (record : List ((String × List α) × Bool))
    (A : List (String × List α)) : String → List α → Option Bool :=
  coneAtomVX M (openNames L) (record ++ switchesOffRecord L.D M record) (zoneAtoms L M record) A

/-- The completion an assignment stands for. -/
abbrev zReal (L : LayeredU) (M : VE.FiniteModel α) (record : List ((String × List α) × Bool))
    (A : List (String × List α)) : String → List α → Prop :=
  fun p vs => zV L M record A p vs = some true

/-- The assignment a completion takes on the enumerated atoms. -/
noncomputable abbrev zA (L : LayeredU) (M : VE.FiniteModel α) (record : List ((String × List α) × Bool))
    (R : String → List α → Prop) : List (String × List α) :=
  (zoneAtoms L M record).filter (fun a => @decide (R a.1 a.2) (Classical.propDecidable _))

section Zone
variable {L : LayeredU} {X : List (String × VE.Formula)} {record : List ((String × List α) × Bool)}
  {obs : List ((VE.Norms.Regulated × List α) × Bool)}

theorem zoneMin_ok {Min : List (List (String × List α))} (h : zoneMin L X M record obs = .ok Min) :
    zoneRecordOk L M (record ++ switchesOffRecord L.D M record) = true ∧
    (VE.Norms.backgroundBase (VE.NormDefaults.fill L.U)).all (·.eval M []) = true ∧
    (∀ A ∈ subsets (zoneAtoms L M record), zRow L X M record obs A ≠ .ok false) ∧
    ∀ A, A ∈ Min ↔ (A ∈ subsets (zoneAtoms L M record) ∧ zRow L X M record obs A = .ok true) ∧
      ∀ B ∈ subsets (zoneAtoms L M record), zRow L X M record obs B = .ok true →
        decSub (decisionAtoms L.D M) B A = true → decSub (decisionAtoms L.D M) A B = true := by
  unfold zoneMin at h
  simp only at h
  split at h <;> try (cases h; done)
  split at h <;> try (cases h; done)
  rename_i hrec
  split at h <;> try (cases h; done)
  rename_i hbg
  split at h <;> try (cases h; done)
  rename_i hnone
  split at h <;> try (cases h; done)
  simp only [Except.ok.injEq] at h
  subst h
  simp only [Bool.not_eq_true', Bool.not_eq_false] at hrec hbg
  refine ⟨hrec, hbg, fun A hA hf => ?_, fun A => ?_⟩
  · have := List.find?_eq_none.mp hnone (A, zRow L X M record obs A) (List.mem_map.mpr ⟨A, hA, rfl⟩)
    simp [hf, Except.toOption] at this
  · have hS : ∀ B, B ∈ ((List.map (fun A => (A, zRow L X M record obs A)) (subsets (zoneAtoms L M record))).filter
        (fun x => x.2.toOption == some true)).map (·.1) ↔
        B ∈ subsets (zoneAtoms L M record) ∧ zRow L X M record obs B = .ok true := by
      intro B
      simp only [List.mem_map, List.mem_filter, beq_iff_eq, toOption_eq_some]
      constructor
      · rintro ⟨_, ⟨⟨B', hB', rfl⟩, hk⟩, rfl⟩
        exact ⟨hB', hk⟩
      · rintro ⟨hB, hk⟩
        exact ⟨_, ⟨⟨B, hB, rfl⟩, hk⟩, rfl⟩
    simp only [List.mem_filter, List.all_eq_true, Bool.or_eq_true, Bool.not_eq_true', Bool.eq_false_iff, ne_eq]
    rw [hS]
    constructor
    · rintro ⟨hA, hall⟩
      refine ⟨hA, fun B hB hk hd => ?_⟩
      rcases hall B ((hS B).mpr ⟨hB, hk⟩) with h' | h'
      · exact absurd hd h'
      · exact h'
    · rintro ⟨hA, hall⟩
      refine ⟨hA, fun B hB => ?_⟩
      obtain ⟨hB, hk⟩ := (hS B).mp hB
      by_cases hd : decSub (decisionAtoms L.D M) B A = true
      · exact Or.inr (hall B hB hk hd)
      · exact Or.inl hd

theorem zoneAtoms_facts (L : LayeredU) (M : VE.FiniteModel α) (record : List ((String × List α) × Bool)) :
    (∀ a ∈ zoneAtoms L M record, a.1 ∈ openNames L ∧ ∀ b, (a, b) ∉ record ++ switchesOffRecord L.D M record) ∧
    ∀ a ∈ decisionAtoms L.D M, (∃ b, (a, b) ∈ record ++ switchesOffRecord L.D M record) ∨
      a ∈ zoneAtoms L M record := by
  constructor
  · intro a ha
    simp only [zoneAtoms, openAtomsAll, List.mem_filter, List.mem_append, List.mem_flatMap, List.mem_map,
      Bool.not_eq_true', List.any_eq_false, beq_iff_eq] at ha
    obtain ⟨⟨hm, hr⟩, hs⟩ := ha
    refine ⟨?_, fun b hb => ?_⟩
    · unfold openNames VE.NormDefaults.unsaidNames
      rcases hm with hd | ⟨p, hp, vs, _, rfl⟩
      · unfold decisionAtoms at hd
        obtain ⟨⟨n, ss⟩, hn, hv⟩ := List.mem_flatMap.mp hd
        obtain ⟨vs, _, rfl⟩ := List.mem_map.mp hv
        exact List.mem_append_left _ (List.mem_map.mpr ⟨_, hn, rfl⟩)
      · exact List.mem_append_right _ (List.mem_map.mpr ⟨p, hp, rfl⟩)
    · rcases List.mem_append.mp hb with hb | hb
      · exact hr _ hb rfl
      · exact hs _ hb rfl
  · intro a ha
    by_cases h : ∃ b, (a, b) ∈ record ++ switchesOffRecord L.D M record
    · exact Or.inl h
    · refine Or.inr ?_
      simp only [zoneAtoms, openAtomsAll, List.mem_filter, List.mem_append, Bool.not_eq_true', List.any_eq_false,
        beq_iff_eq]
      refine ⟨⟨Or.inl ha, fun e he hea => h ⟨e.2, ?_⟩⟩, fun e he hea => h ⟨e.2, ?_⟩⟩
      · rw [← hea]; exact List.mem_append_left _ he
      · rw [← hea]; exact List.mem_append_right _ he

theorem zoneRecordOk_facts {L : LayeredU} (h : zoneRecordOk L M rec' = true) :
    (∀ e ∈ rec', (rec'.find? (fun e' => decide (e'.1 = e.1))).map (·.2) = some e.2) ∧
    (∀ e ∈ rec', e.1.1 ∉ openNames L → (e.1.2 ∈ M.relations e.1.1 ↔ e.2 = true)) ∧
    ∀ e ∈ rec', e.2 = true → zoneDeclOk L M e.1 = true := by
  unfold zoneRecordOk at h
  refine ⟨fun e he => ?_, fun e he hn => ?_, fun e he ht => ?_⟩ <;>
    have h' := List.all_eq_true.mp h e he <;> simp only [Bool.and_eq_true, beq_iff_eq] at h'
  · exact h'.1.1
  · have := h'.1.2
    simp only [hn, decide_false, Bool.false_or, beq_iff_eq] at this
    rw [← this]; simp
  · simpa [ht] using h'.2

/-- The completion of a passing assignment is admissible and agrees with the observations. -/
theorem realized_admissible (valid : M.Valid (VE.Norms.envAt L.U.D 0)) {A : List (String × List α)}
    (hrec : zoneRecordOk L M (record ++ switchesOffRecord L.D M record) = true)
    (hbg : (VE.Norms.backgroundBase (VE.NormDefaults.fill L.U)).all (·.eval M []) = true)
    (hrow : zRow L X M record obs A = .ok true) :
    AdmissibleCompletion L.U (X.map (·.2)) M (openNames L) (record ++ switchesOffRecord L.D M record)
      (zReal L M record A) ∧ Observed L.U M obs (zReal L M record A) := by
  obtain ⟨hfirst, hoffrec, htrue⟩ := zoneRecordOk_facts hrec
  obtain ⟨hok, hP, hO⟩ := zoneRow_true hrow
  have hK := VE.NormDefaults.kleene_sound M (zV L M record A) (zReal L M record A)
    (fun p vs c h => by simp only [zReal, h, Option.some.injEq])
  have hu := VE.NormDefaults.uvalid L.wfU
  refine ⟨⟨fun n vs hn => realized_off hoffrec n vs hn, fun a b h => realized_rec hfirst a b h,
    ⟨⟨⟨⟨fun c s hc => valid.1 c s hc, fun p vs hp => ?_⟩, ?_⟩, fun ψ hψ => ?_⟩, fun ψ hψ => ?_⟩⟩, fun o ho => ?_⟩
  · -- every true atom is declared and typed
    have hd : zoneDeclOk L M (p, vs) = true := by
      simp only [zReal, zV, coneAtomVX] at hp
      split at hp
      · rename_i e he
        have hpe : e.1 = (p, vs) := by simpa using List.find?_some he
        simp only [Option.some.injEq] at hp
        have := htrue e (List.mem_of_find?_eq_some he) hp
        rwa [hpe] at this
      · simp only [coneAtomVO] at hp
        split at hp
        · split at hp
          · simp only [Option.some.injEq, decide_eq_true_eq] at hp
            have := hok _ hp
            simp only [List.mem_filter] at this
            exact this.2
          · cases hp
        · rename_i hn
          simp only [Option.some.injEq, decide_eq_true_eq] at hp
          obtain ⟨ss, hss, ht⟩ := valid.2 p vs hp
          exact (zoneDeclOk_iff L M (p, vs)).mpr ⟨ss, VE.NormDefaults.envAt_fill_mono hu 0 p ss hss, ht⟩
    obtain ⟨ss, hss, ht⟩ := (zoneDeclOk_iff L M (p, vs)).mp hd
    exact ⟨ss, hss, (VE.Norms.tupleTyped_relation M.asStructure (zReal L M record A) ss vs).mpr ht⟩
  · exact (VE.NormDefaults.sat_literals_relation _ M.asStructure _).mpr fun a ha =>
      (VE.eval_iff_denote M [] a).mp (List.all_eq_true.mp hbg a ha)
  · exact (hK ψ [] true (hP ("fill", ψ) (List.mem_append_right _ (List.mem_map.mpr ⟨ψ, hψ, rfl⟩)))).mpr rfl
  · obtain ⟨e, he, rfl⟩ := List.mem_map.mp hψ
    exact (hK e.2 [] true (hP e (List.mem_append_left _ he))).mpr rfl
  · exact hK _ _ o.2 (hO _ (List.mem_map.mpr ⟨o, ho, rfl⟩))

/-- An admissible completion that agrees with the observations takes an assignment no check refutes. -/
theorem row_of_completion {R : String → List α → Prop}
    (hR : AdmissibleCompletion L.U (X.map (·.2)) M (openNames L) (record ++ switchesOffRecord L.D M record) R)
    (ho : Observed L.U M obs R) :
    zA L M record R ∈ subsets (zoneAtoms L M record) ∧
    (∀ p vs c, zV L M record (zA L M record R) p vs = some c → (R p vs ↔ c = true)) ∧
    ∃ t, zRow L X M record obs (zA L M record R) = .ok t := by
  obtain ⟨hoff, hrec, ⟨⟨⟨hadm, _⟩, hfill⟩, hX⟩⟩ := hR
  have hA : ∀ a ∈ zoneAtoms L M record, (R a.1 a.2 ↔ a ∈ zA L M record R) := by
    intro a ha; simp [zA, ha]
  have hc := consistent_atomV hoff hrec hA
  have hK := VE.NormDefaults.kleene_sound M _ R hc
  refine ⟨VE.NormDefaults.filter_mem_subsets _ _, hc, zoneRow_ok (fun a ha => ?_) (fun e he hk => ?_)
    (fun o ho' hk => ?_)⟩
  · simp only [zA, List.mem_filter, decide_eq_true_eq] at ha
    obtain ⟨ss, hss, ht⟩ := hadm.2 a.1 a.2 ha.2
    exact List.mem_filter.mpr ⟨ha.1, (zoneDeclOk_iff L M a).mpr ⟨ss, hss, (VE.Norms.tupleTyped_relation M.asStructure R ss a.2).mp ht⟩⟩
  · rcases List.mem_append.mp he with he | he
    · exact absurd ((hK _ _ _ hk).mp (hX _ (List.mem_map.mpr ⟨e, he, rfl⟩))) (by simp)
    · obtain ⟨ψ, hψ, rfl⟩ := List.mem_map.mp he
      exact absurd ((hK _ _ _ hk).mp (hfill ψ hψ)) (by simp)
  · obtain ⟨o, hmem, rfl⟩ := List.mem_map.mp ho'
    have h1 := hK _ _ _ hk
    have h2 := ho o hmem
    unfold OutcomeIn at h2
    cases hb : o.2 <;> simp_all

theorem dc_of_min (valid : M.Valid (VE.Norms.envAt L.U.D 0)) {Min : List (List (String × List α))}
    (hm : zoneMin L X M record obs = .ok Min) {A : List (String × List α)} (hA : A ∈ Min) :
    DefaultCompletion L (X.map (·.2)) M record obs (zReal L M record A) := by
  obtain ⟨hrec, hbg, hnone, hmin⟩ := zoneMin_ok hm
  obtain ⟨⟨hsA, hrow⟩, hall⟩ := (hmin A).mp hA
  obtain ⟨hadm, hobs⟩ := realized_admissible valid hrec hbg hrow
  obtain ⟨hC, hdec⟩ := zoneAtoms_facts L M record
  have hAA : ∀ a ∈ zoneAtoms L M record, (zReal L M record A a.1 a.2 ↔ a ∈ A) :=
    fun a ha => realized_C a ha (hC a ha).1 (hC a ha).2
  refine ⟨hadm, hobs, fun R' hR' ho' hle => ?_⟩
  obtain ⟨hsub', _, t, ht⟩ := row_of_completion (X := X) hR' ho'
  cases t
  · exact absurd ht (hnone _ hsub')
  have hA' : ∀ a ∈ zoneAtoms L M record, (R' a.1 a.2 ↔ a ∈ zA L M record R') := by intro a ha; simp [zA, ha]
  have hd := (decLe_iff hdec hR'.2.1 hadm.2.1 hA' hAA (mem_of_mem_subsets hsub')).mp hle
  exact (decLe_iff hdec hadm.2.1 hR'.2.1 hAA hA' (mem_of_mem_subsets hsA)).mpr (hall _ hsub' ht hd)

theorem min_of_dc (valid : M.Valid (VE.Norms.envAt L.U.D 0)) {Min : List (List (String × List α))}
    (hm : zoneMin L X M record obs = .ok Min) {R : String → List α → Prop}
    (hdc : DefaultCompletion L (X.map (·.2)) M record obs R) : zA L M record R ∈ Min := by
  obtain ⟨hrec, hbg, hnone, hmin⟩ := zoneMin_ok hm
  obtain ⟨hR, ho, hm'⟩ := hdc
  obtain ⟨hsub, _, t, ht⟩ := row_of_completion (X := X) hR ho
  cases t
  · exact absurd ht (hnone _ hsub)
  obtain ⟨hC, hdec⟩ := zoneAtoms_facts L M record
  have hA : ∀ a ∈ zoneAtoms L M record, (R a.1 a.2 ↔ a ∈ zA L M record R) := by intro a ha; simp [zA, ha]
  refine (hmin _).mpr ⟨⟨hsub, ht⟩, fun B hB hkB hd => ?_⟩
  obtain ⟨hadm, hobs⟩ := realized_admissible valid hrec hbg hkB
  have hBB : ∀ a ∈ zoneAtoms L M record, (zReal L M record B a.1 a.2 ↔ a ∈ B) :=
    fun a ha => realized_C a ha (hC a ha).1 (hC a ha).2
  have hle := (decLe_iff hdec hadm.2.1 hR.2.1 hBB hA (mem_of_mem_subsets hB)).mpr hd
  exact (decLe_iff hdec hR.2.1 hadm.2.1 hA hBB (mem_of_mem_subsets hsub)).mp (hm' _ hadm hobs hle)

/-- The query values `defaultZoneOf` reads, one per minimal assignment. -/
abbrev zVals (L : LayeredU) (M : VE.FiniteModel α) (record : List ((String × List α) × Bool))
    (r : VE.Norms.Regulated) (vs : List α) (Min : List (List (String × List α))) :
    List (List (String × List α) × Bool) :=
  (Min.map (fun A => (A, kleene M (zV L M record A) (VE.Norms.tupleVal vs)
    (VE.Norms.outcomeBase (VE.NormDefaults.fill L.U) r.name)))).filterMap (fun x => x.2.map (x.1, ·))

theorem mem_zVals {r : VE.Norms.Regulated} {vs : List α} {Min : List (List (String × List α))} {A : List (String × List α)}
    {v : Bool} : (A, v) ∈ zVals L M record r vs Min ↔ A ∈ Min ∧
      kleene M (zV L M record A) (VE.Norms.tupleVal vs) (VE.Norms.outcomeBase (VE.NormDefaults.fill L.U) r.name) =
        some v := by
  simp only [zVals, List.mem_filterMap, List.mem_map, Option.map_eq_some_iff, Prod.mk.injEq]
  constructor
  · rintro ⟨_, ⟨B, hB, rfl⟩, w, hw, rfl, rfl⟩
    exact ⟨hB, hw⟩
  · rintro ⟨hA, hk⟩
    exact ⟨_, ⟨A, hA, rfl⟩, v, hk, rfl, rfl⟩

theorem val_real (valid : M.Valid (VE.Norms.envAt L.U.D 0)) {Min : List (List (String × List α))}
    (hm : zoneMin L X M record obs = .ok Min) {r : VE.Norms.Regulated} {vs : List α} {A : List (String × List α)}
    {v : Bool} (h : (A, v) ∈ zVals L M record r vs Min) :
    DefaultCompletion L (X.map (·.2)) M record obs (zReal L M record A) ∧
      (OutcomeIn L.U M (zReal L M record A) r vs ↔ v = true) := by
  obtain ⟨hA, hk⟩ := mem_zVals.mp h
  exact ⟨dc_of_min valid hm hA, VE.NormDefaults.kleene_sound M _ (zReal L M record A)
    (fun p vs c h => by simp only [zReal, h, Option.some.injEq]) _ _ v hk⟩

theorem val_dc (valid : M.Valid (VE.Norms.envAt L.U.D 0)) {Min : List (List (String × List α))}
    (hm : zoneMin L X M record obs = .ok Min) {r : VE.Norms.Regulated} {vs : List α}
    (hq : ∀ x ∈ Min.map (fun A => (A, kleene M (zV L M record A) (VE.Norms.tupleVal vs)
      (VE.Norms.outcomeBase (VE.NormDefaults.fill L.U) r.name))), ¬ (x.2 == none) = true)
    {R : String → List α → Prop} (hdc : DefaultCompletion L (X.map (·.2)) M record obs R) :
    ∃ v, (zA L M record R, v) ∈ zVals L M record r vs Min ∧ (OutcomeIn L.U M R r vs ↔ v = true) := by
  have hA := min_of_dc valid hm hdc
  have hn := hq _ (List.mem_map.mpr ⟨_, hA, rfl⟩)
  obtain ⟨v, hv⟩ := Option.ne_none_iff_exists'.mp (by simpa using hn)
  obtain ⟨hR, ho, _⟩ := hdc
  obtain ⟨_, hc, _⟩ := row_of_completion (X := X) hR ho
  exact ⟨v, mem_zVals.mpr ⟨hA, hv⟩, VE.NormDefaults.kleene_sound M _ R hc _ _ v hv⟩

theorem zoneMin_error {z : DefaultZone α} (h : zoneMin L X M record obs = .error z) :
    (z = .unknown (.budget (openAtomsAll L M record).length maxDefaultAtoms) ∧
      maxDefaultAtoms < (openAtomsAll L M record).length) ∨ (∃ l, z = .noCompletion l) ∨
      ∃ w y, z = .unknown (.branch w y) := by
  unfold zoneMin at h
  simp only at h
  split at h
  · rename_i hc; cases h
    rcases zoneCharge_some hc with h | h
    · exact Or.inl h
    · exact Or.inr (Or.inr h)
  split at h
  · cases h; exact Or.inr (Or.inl ⟨_, rfl⟩)
  split at h
  · cases h; exact Or.inr (Or.inl ⟨_, rfl⟩)
  split at h
  · cases h; exact Or.inr (Or.inr ⟨_, _, rfl⟩)
  split at h
  · cases h; exact Or.inr (Or.inl ⟨_, rfl⟩)
  · cases h

/-- No admissible completion agreeing with the observations, when `zoneMin` answers `noCompletion`. -/
theorem zoneMin_noCompletion {l : List String} (h : zoneMin L X M record obs = .error (.noCompletion l)) (R : String → List α → Prop)
    (hR : AdmissibleCompletion L.U (X.map (·.2)) M (openNames L) (record ++ switchesOffRecord L.D M record) R)
    (ho : Observed L.U M obs R) : False := by
  obtain ⟨hoff, hrec, ⟨⟨⟨hadm, hbgR⟩, _⟩, _⟩⟩ := hR
  unfold zoneMin at h
  simp only at h
  split at h
  · rename_i hc; cases h
    rcases zoneCharge_some hc with ⟨h, _⟩ | ⟨_, _, h⟩ <;> cases h
  split at h
  · rename_i hk
    have hk' : zoneRecordOk L M (record ++ switchesOffRecord L.D M record) ≠ true := by simpa using hk
    apply hk'
    unfold zoneRecordOk
    refine List.all_eq_true.mpr fun e he => ?_
    have hf : (List.find? (fun e' => decide (e'.1 = e.1)) (record ++ switchesOffRecord L.D M record)).map (·.2) =
        some e.2 := by
      obtain ⟨e', he'⟩ := Option.isSome_iff_exists.mp ((List.find?_isSome (p := fun e' => decide (e'.1 = e.1))).mpr ⟨e, he, by simp⟩)
      have h1 : e'.1 = e.1 := by simpa using List.find?_some he'
      have h2 := hrec e'.1 e'.2 (List.mem_of_find?_eq_some he')
      have h3 := hrec e.1 e.2 he
      rw [h1] at h2
      rw [he']
      simp only [Option.map_some, Option.some.injEq]
      exact Bool.eq_iff_iff.mpr (h2.symm.trans h3)
    simp only [Bool.and_eq_true, beq_iff_eq, Bool.or_eq_true, decide_eq_true_eq]
    refine ⟨⟨hf, ?_⟩, ?_⟩
    · by_cases hn : e.1.1 ∈ openNames L
      · exact Or.inl hn
      · have h1 := hoff e.1.1 e.1.2 hn
        have h2 := hrec e.1 e.2 he
        exact Or.inr (by cases h4 : e.2 <;> simp_all)
    · cases h4 : e.2
      · simp
      · have := (hrec e.1 e.2 he).mpr h4
        obtain ⟨ss, hss, ht⟩ := hadm.2 e.1.1 e.1.2 this
        simpa using (zoneDeclOk_iff L M e.1).mpr ⟨ss, hss, (VE.Norms.tupleTyped_relation M.asStructure R ss _).mp ht⟩
  split at h
  · rename_i hk
    have hk' : (VE.Norms.backgroundBase (VE.NormDefaults.fill L.U)).all (·.eval M []) ≠ true := by simpa using hk
    refine hk' (List.all_eq_true.mpr fun a ha => ?_)
    exact (VE.eval_iff_denote M [] a).mpr ((VE.NormDefaults.sat_literals_relation _ M.asStructure R).mp hbgR a ha)
  split at h <;> try (cases h; done)
  split at h
  · rename_i hnone hS
    obtain ⟨hsub, _, t, ht⟩ := row_of_completion (X := X) ⟨hoff, hrec, ⟨⟨⟨hadm, hbgR⟩, by assumption⟩, by assumption⟩⟩ ho
    cases t
    · have := List.find?_eq_none.mp hnone (_, _) (List.mem_map.mpr ⟨_, hsub, rfl⟩)
      simp [ht, Except.toOption] at this
    · refine absurd hS ?_
      rw [List.isEmpty_iff, List.map_eq_nil_iff, List.filter_eq_nil_iff]
      intro hall
      have := hall _ (List.mem_map.mpr ⟨_, hsub, rfl⟩)
      simp [ht, Except.toOption] at this
  · cases h

theorem defaultZone_byDefault_sound {α : Type} [DecidableEq α] (L : LayeredU) (X : List (String × VE.Formula))
    (M : VE.FiniteModel α) (valid : M.Valid (VE.Norms.envAt L.U.D 0)) (record : List ((String × List α) × Bool))
    (obs : List ((VE.Norms.Regulated × List α) × Bool)) (r : VE.Norms.Regulated) (hr : r ∈ L.U.D.T.regulated)
    (vs : List α) (typed : VE.TupleTyped M.asStructure r.sorts vs)
    (proposed : List (List ((String × List α) × Bool))) (b : Bool) (w : List ((String × List α) × Bool))
    (hz : defaultZoneOf L X M record obs r vs proposed = .byDefault b w) :
    ByDefaultZ L (X.map (·.2)) M record obs r vs b := by
  have _ := hr
  have _ := typed
  unfold defaultZoneOf at hz
  simp only at hz
  split at hz
  · rename_i z hm
    subst hz
    rcases zoneMin_error hm with ⟨h, _⟩ | ⟨_, h⟩ | ⟨_, _, h⟩ <;> cases h
  rename_i Min hm
  dsimp only [zoneOfMin] at hz
  split at hz <;> try (cases hz; done)
  rename_i hq
  split at hz <;> try (cases hz; done)
  rename_i A b' rest hvals
  split at hz
  · rename_i hall
    cases hz
    have hv' : zVals L M record r vs Min = (A, b) :: rest := hvals
    have hmem : (A, b) ∈ zVals L M record r vs Min := by rw [hv']; exact List.mem_cons_self
    obtain ⟨hdc, _⟩ := val_real valid hm hmem
    refine ⟨⟨_, hdc⟩, fun R hR => ?_⟩
    obtain ⟨v, hv, hout⟩ := val_dc valid hm (List.find?_eq_none.mp hq) hR
    have := List.all_eq_true.mp hall _ hv
    simp only [beq_iff_eq] at this
    rwa [← this]
  · split at hz
    · cases hz
    · split at hz <;> cases hz

theorem pair_facts (valid : M.Valid (VE.Norms.envAt L.U.D 0)) {Min : List (List (String × List α))}
    (hm : zoneMin L X M record obs = .ok Min) {r : VE.Norms.Regulated} {vs : List α}
    {p : (List (String × List α) × Bool) × (List (String × List α) × Bool)}
    (hp : p ∈ (zVals L M record r vs Min).flatMap (fun x => (zVals L M record r vs Min).map (x, ·)))
    (h12 : (p.1.2 && !p.2.2) = true) :
    DefaultCompletion L (X.map (·.2)) M record obs (zReal L M record p.1.1) ∧
    DefaultCompletion L (X.map (·.2)) M record obs (zReal L M record p.2.1) ∧
    OutcomeIn L.U M (zReal L M record p.1.1) r vs ∧ ¬ OutcomeIn L.U M (zReal L M record p.2.1) r vs := by
  obtain ⟨x, hx, hy⟩ := List.mem_flatMap.mp hp
  obtain ⟨y, hy', rfl⟩ := List.mem_map.mp hy
  obtain ⟨h1, h2⟩ := val_real valid hm hx
  obtain ⟨h3, h4⟩ := val_real valid hm hy'
  simp only [Bool.and_eq_true, Bool.not_eq_true'] at h12
  exact ⟨h1, h3, h2.mpr h12.1, fun h => by simp [h4.mp h] at h12⟩

theorem defaultZone_leftTo_sound {α : Type} [DecidableEq α] (L : LayeredU) (X : List (String × VE.Formula))
    (M : VE.FiniteModel α) (valid : M.Valid (VE.Norms.envAt L.U.D 0)) (record : List ((String × List α) × Bool))
    (obs : List ((VE.Norms.Regulated × List α) × Bool)) (r : VE.Norms.Regulated) (hr : r ∈ L.U.D.T.regulated)
    (vs : List α) (typed : VE.TupleTyped M.asStructure r.sorts vs)
    (proposed : List (List ((String × List α) × Bool))) (differ : List (String × List α))
    (w₁ w₂ : List ((String × List α) × Bool))
    (hz : defaultZoneOf L X M record obs r vs proposed = .leftTo differ w₁ w₂) :
    ByDefaultLeftTo L (X.map (·.2)) M record obs r vs ∧ ∀ a ∈ differ, a.1 ∈ decisionNames L.D := by
  have _ := hr
  have _ := typed
  unfold defaultZoneOf at hz
  simp only at hz
  split at hz
  · rename_i z hm
    subst hz
    rcases zoneMin_error hm with ⟨h, _⟩ | ⟨_, h⟩ | ⟨_, _, h⟩ <;> cases h
  rename_i Min hm
  dsimp only [zoneOfMin] at hz
  split at hz <;> try (cases hz; done)
  rename_i hq
  split at hz <;> try (cases hz; done)
  rename_i A b' rest hvals
  split at hz <;> try (cases hz; done)
  split at hz
  · rename_i p hp
    cases hz
    have hpm := List.mem_of_find?_eq_some hp
    have hpc := List.find?_some hp
    simp only [Bool.and_eq_true, List.all_eq_true] at hpc
    obtain ⟨h1, h2, h3, h4⟩ := pair_facts valid hm hpm (by simp [hpc.1.1, hpc.1.2])
    obtain ⟨hC, _⟩ := zoneAtoms_facts L M record
    obtain ⟨hfirst, _, _⟩ := zoneRecordOk_facts (zoneMin_ok hm).1
    refine ⟨⟨_, _, h1, h2, fun n hn ws => ?_, h3, h4⟩, fun a ha => ?_⟩
    · simp only [zReal, zV, coneAtomVX]
      split
      · rfl
      · simp only [coneAtomVO]
        split
        · split
          · rename_i hC'
            have := hpc.2 (n, ws) hC'
            simp only [Bool.or_eq_true, Bool.not_eq_true', beq_iff_eq] at this
            rcases this with h | h
            · have h' := List.contains_iff_mem.mpr hn
              rw [h] at h'
              cases h'
            · have h' : (n, ws) ∈ p.1.1 ↔ (n, ws) ∈ p.2.1 := by
                rw [← List.contains_iff_mem, ← List.contains_iff_mem, h]
              simp [h']
          · exact Iff.rfl
        · exact Iff.rfl
    · simp only [List.mem_filter, Bool.and_eq_true, List.contains_iff_mem] at ha
      obtain ⟨⟨n, ss⟩, hn, hv⟩ := List.mem_flatMap.mp ha.2.1
      obtain ⟨_, _, rfl⟩ := List.mem_map.mp hv
      exact List.mem_map.mpr ⟨_, hn, rfl⟩
  · split at hz <;> cases hz

theorem defaultZone_notSaid_sound {α : Type} [DecidableEq α] (L : LayeredU) (X : List (String × VE.Formula))
    (M : VE.FiniteModel α) (valid : M.Valid (VE.Norms.envAt L.U.D 0)) (record : List ((String × List α) × Bool))
    (obs : List ((VE.Norms.Regulated × List α) × Bool)) (r : VE.Norms.Regulated) (hr : r ∈ L.U.D.T.regulated)
    (vs : List α) (typed : VE.TupleTyped M.asStructure r.sorts vs)
    (proposed : List (List ((String × List α) × Bool))) (w₁ w₂ : List ((String × List α) × Bool))
    (hz : defaultZoneOf L X M record obs r vs proposed = .notSaid w₁ w₂) :
    (∃ R₁ R₂, DefaultCompletion L (X.map (·.2)) M record obs R₁ ∧ DefaultCompletion L (X.map (·.2)) M record obs R₂ ∧
      OutcomeIn L.U M R₁ r vs ∧ ¬ OutcomeIn L.U M R₂ r vs) ∧
    ¬ ByDefaultLeftTo L (X.map (·.2)) M record obs r vs := by
  have _ := hr
  have _ := typed
  unfold defaultZoneOf at hz
  simp only at hz
  split at hz
  · rename_i z hm
    subst hz
    rcases zoneMin_error hm with ⟨h, _⟩ | ⟨_, h⟩ | ⟨_, _, h⟩ <;> cases h
  rename_i Min hm
  dsimp only [zoneOfMin] at hz
  split at hz <;> try (cases hz; done)
  rename_i hq
  split at hz <;> try (cases hz; done)
  rename_i A b' rest hvals
  split at hz <;> try (cases hz; done)
  split at hz <;> try (cases hz; done)
  rename_i hnoleft
  split at hz
  · rename_i p hp
    have hpm := List.mem_of_find?_eq_some hp
    obtain ⟨h1, h2, h3, h4⟩ := pair_facts valid hm hpm (by simpa using List.find?_some hp)
    refine ⟨⟨_, _, h1, h2, h3, h4⟩, ?_⟩
    rintro ⟨R₁, R₂, hd₁, hd₂, hun, ho₁, ho₂⟩
    obtain ⟨v₁, hv₁, hout₁⟩ := val_dc valid hm (List.find?_eq_none.mp hq) hd₁
    obtain ⟨v₂, hv₂, hout₂⟩ := val_dc valid hm (List.find?_eq_none.mp hq) hd₂
    refine List.find?_eq_none.mp hnoleft ((zA L M record R₁, v₁), (zA L M record R₂, v₂))
      (List.mem_flatMap.mpr ⟨_, hv₁, List.mem_map.mpr ⟨_, hv₂, rfl⟩⟩) ?_
    have e₁ := hout₁.mp ho₁
    have e₂ : v₂ = false := by cases h : v₂ <;> simp_all
    simp only [e₁, e₂, Bool.not_false, Bool.and_self, Bool.true_and, List.all_eq_true, Bool.or_eq_true,
      Bool.not_eq_true', beq_iff_eq]
    intro a ha
    by_cases hn : a.1 ∈ VE.NormDefaults.unsaidNames L.U
    · refine Or.inr ?_
      have := hun a.1 hn a.2
      rw [Bool.eq_iff_iff, List.contains_iff_mem, List.contains_iff_mem]
      simp only [zA, List.mem_filter, decide_eq_true_eq]
      exact and_congr Iff.rfl this
    · exact Or.inl (by simpa using hn)
  · cases hz

theorem defaultZone_noCompletion_sound {α : Type} [DecidableEq α] (L : LayeredU) (X : List (String × VE.Formula))
    (M : VE.FiniteModel α) (record : List ((String × List α) × Bool))
    (obs : List ((VE.Norms.Regulated × List α) × Bool)) (r : VE.Norms.Regulated) (vs : List α)
    (proposed : List (List ((String × List α) × Bool))) (labels : List String)
    (hz : defaultZoneOf L X M record obs r vs proposed = .noCompletion labels) :
    ¬ ∃ R, DefaultCompletion L (X.map (·.2)) M record obs R := by
  rintro ⟨R, hR, ho, _⟩
  unfold defaultZoneOf at hz
  simp only at hz
  split at hz
  · rename_i z hm
    subst hz
    exact zoneMin_noCompletion hm R hR ho
  dsimp only [zoneOfMin] at hz
  split at hz <;> try (cases hz; done)
  split at hz <;> try (cases hz; done)
  split at hz <;> try (cases hz; done)
  split at hz <;> try (cases hz; done)
  split at hz <;> cases hz

theorem defaultZone_budget {α : Type} [DecidableEq α] (L : LayeredU) (X : List (String × VE.Formula))
    (M : VE.FiniteModel α) (record : List ((String × List α) × Bool))
    (obs : List ((VE.Norms.Regulated × List α) × Bool)) (r : VE.Norms.Regulated) (vs : List α)
    (proposed : List (List ((String × List α) × Bool))) (n k : Nat)
    (hz : defaultZoneOf L X M record obs r vs proposed = .unknown (.budget n k)) :
    n = (openAtomsAll L M record).length ∧ k = maxDefaultAtoms ∧ maxDefaultAtoms < n := by
  unfold defaultZoneOf at hz
  simp only at hz
  split at hz
  · rename_i z hm
    subst hz
    rcases zoneMin_error hm with ⟨h, hlt⟩ | ⟨_, h⟩ | ⟨_, _, h⟩ <;> cases h
    exact ⟨rfl, rfl, hlt⟩
  dsimp only [zoneOfMin] at hz
  split at hz <;> try (cases hz; done)
  split at hz <;> try (cases hz; done)
  split at hz <;> try (cases hz; done)
  split at hz <;> try (cases hz; done)
  split at hz <;> cases hz

/-- With no switch and no `outweighs` decision, the decision atoms are exactly the atoms of weighing's record.
    Proved in the stub (`simp`). -/
theorem decisionAtoms_none {α : Type} (D : SoftDoc) (M : VE.FiniteModel α)
    (hnone : offDecisions D = [] ∧ outweighsTriples D = []) (a : String × List α) :
    a ∈ decisionAtoms D M ↔ a ∈ (noExceptionRecord D M).map (·.1) := by
  simp [decisionAtoms, VE.SoftNorms.decisions, VE.SoftNorms.outweighsDecisions, hnone.1, hnone.2, noExceptionRecord,
    List.map_flatMap]

theorem defaultZone_eq_noException {α : Type} [DecidableEq α] (L : LayeredU) (X : List VE.Formula)
    (M : VE.FiniteModel α) (r : VE.Norms.Regulated) (vs : List α) (b : Bool)
    (hnone : offDecisions L.D = [] ∧ outweighsTriples L.D = [])
    (hadm : ∃ R, AdmissibleCompletion L.U X M (openNames L) (noExceptionRecord L.D M) R) :
    ByDefaultZ L X M [] [] r vs b ↔ SettledZ L.U X M (openNames L) (noExceptionRecord L.D M) r vs b := by
  have hsw : switchesOffRecord L.D M [] = [] := by simp [switchesOffRecord, hnone.1]
  -- a completion meeting weighing's record has no true decision
  have hfalse : ∀ R, AdmissibleCompletion L.U X M (openNames L) (noExceptionRecord L.D M) R →
      ∀ a ∈ decisionAtoms L.D M, ¬ R a.1 a.2 := by
    intro R hR a ha hRa
    obtain ⟨⟨a', c⟩, hm, rfl⟩ := List.mem_map.mp ((decisionAtoms_none L.D M hnone a).mp ha)
    have hc : c = false := by
      simp only [noExceptionRecord, List.mem_flatMap, List.mem_map, Prod.mk.injEq] at hm
      obtain ⟨_, _, _, _, _, h⟩ := hm
      exact h.symm
    simpa [hc] using (hR.2.1 a' c hm).mp hRa
  have key : ∀ R, DefaultCompletion L X M [] [] R ↔
      AdmissibleCompletion L.U X M (openNames L) (noExceptionRecord L.D M) R := by
    intro R
    simp only [DefaultCompletion, hsw, List.append_nil]
    constructor
    · rintro ⟨hR, _, hmin⟩
      obtain ⟨R₀, h₀⟩ := hadm
      have hle := hmin R₀ ⟨h₀.1, by simp, h₀.2.2⟩ (by simp [Observed])
        (fun a ha h => absurd h (hfalse R₀ h₀ a ha))
      refine ⟨hR.1, fun a c hm => ?_, hR.2.2⟩
      have ha := (decisionAtoms_none L.D M hnone a).mpr (List.mem_map.mpr ⟨_, hm, rfl⟩)
      have hc : c = false := by
        simp only [noExceptionRecord, List.mem_flatMap, List.mem_map, Prod.mk.injEq] at hm
        obtain ⟨_, _, _, _, _, h⟩ := hm
        exact h.symm
      simp only [hc, Bool.false_eq_true, iff_false]
      exact fun h => hfalse R₀ h₀ a ha (hle a ha h)
    · intro hR
      exact ⟨⟨hR.1, by simp, hR.2.2⟩, by simp [Observed], fun _ _ _ _ a ha h => absurd h (hfalse R hR a ha)⟩
  unfold ByDefaultZ SettledZ
  simp only [key]

/-! ### `forcedAll`: what every default completion holds -/

theorem mem_of_mem_eraseDups {β : Type} [BEq β] : ∀ (l : List β) (x : β), x ∈ l.eraseDups → x ∈ l
  | [], _, h => by simp at h
  | a :: as, x, h => by
    rw [List.eraseDups_cons] at h
    rcases List.mem_cons.mp h with rfl | h
    · exact List.mem_cons_self
    · exact List.mem_cons_of_mem _ (List.mem_filter.mp (mem_of_mem_eraseDups _ x h)).1
termination_by l => l.length
decreasing_by have := List.length_filter_le (fun b => !b == a) as; simp only [List.length_cons]; omega

/-- Off the enumerated atoms an assignment's valuation does not depend on the assignment. -/
theorem coneAtomVX_off {a : String × List α} (ha : a ∉ C) (A B : List (String × List α)) :
    coneAtomVX M opens rec' C A a.1 a.2 = coneAtomVX M opens rec' C B a.1 a.2 := by
  unfold coneAtomVX
  split <;> simp [coneAtomVO, ha]

theorem forcedAll_sound {α : Type} [DecidableEq α] (L : LayeredU) (X : List (String × VE.Formula))
    (M : VE.FiniteModel α) (valid : M.Valid (VE.Norms.envAt L.U.D 0)) (record : List ((String × List α) × Bool))
    (obs : List ((VE.Norms.Regulated × List α) × Bool)) (proposed : List (List ((String × List α) × Bool)))
    (fs : List (String × List α)) (hf : forcedAllOf L X M record obs proposed = some fs) :
    (∃ R, DefaultCompletion L (X.map (·.2)) M record obs R) ∧
    ∀ a ∈ fs, (∃ ss, (a.1, ss) ∈ VE.SoftNorms.exceptedDecisions L.D ∧ a.2 ∈ VE.NormDefaults.allTuples M ss) ∧
      ∀ R, DefaultCompletion L (X.map (·.2)) M record obs R → R a.1 a.2 := by
  unfold forcedAllOf at hf
  simp only at hf
  split at hf
  · cases hf
  rename_i Min hm
  unfold forcedOfMin at hf
  split at hf
  · cases hf
  rename_i hne
  cases hf
  obtain ⟨A, hA⟩ := List.exists_mem_of_ne_nil Min (by simpa using hne)
  refine ⟨⟨_, dc_of_min valid hm hA⟩, fun a ha => ?_⟩
  obtain ⟨hmem, hp⟩ := List.mem_filter.mp (mem_of_mem_eraseDups _ _ ha)
  refine ⟨?_, fun R hR => ?_⟩
  · simp only [noExceptionRecord, List.mem_map, List.mem_flatMap] at hmem
    obtain ⟨_, ⟨⟨n, ss⟩, hn, vs, hvs, rfl⟩, rfl⟩ := hmem
    exact ⟨ss, hn, hvs⟩
  · have hAR := min_of_dc valid hm hR
    obtain ⟨hRa, hRo, _⟩ := hR
    obtain ⟨_, hc, _⟩ := row_of_completion (X := X) hRa hRo
    refine (hc a.1 a.2 true ?_).mpr rfl
    obtain ⟨hC, _⟩ := zoneAtoms_facts L M record
    by_cases haC : a ∈ zoneAtoms L M record
    · simp only [haC, List.contains_iff_mem, if_true, List.all_eq_true] at hp
      exact (realized_C a haC (hC a haC).1 (hC a haC).2).mpr (hp _ hAR)
    · simp only [haC, List.contains_iff_mem, if_false, beq_iff_eq] at hp
      exact (coneAtomVX_off haC _ []).trans hp

/-- The finite minimal-subcompletion lemma: below every admissible completion that agrees with the observations
    there is a default completion (so it lacks every decision atom the first one lacks). -/
theorem defaultCompletion_below {α : Type} [DecidableEq α] (L : LayeredU) (X : List VE.Formula)
    (M : VE.FiniteModel α) (record : List ((String × List α) × Bool))
    (obs : List ((VE.Norms.Regulated × List α) × Bool)) (R : String → List α → Prop)
    (hR : AdmissibleCompletion L.U X M (openNames L) (record ++ switchesOffRecord L.D M record) R)
    (ho : Observed L.U M obs R) :
    ∃ R', DefaultCompletion L X M record obs R' ∧ DecLe L.D M R' R := by
  -- the number of true decision atoms falls strictly below a completion that is not minimal
  let f : (String → List α → Prop) → Nat := fun R' =>
    (decisionAtoms L.D M).countP (fun a => @decide (R' a.1 a.2) (Classical.propDecidable _))
  suffices h : ∀ n R, f R = n →
      AdmissibleCompletion L.U X M (openNames L) (record ++ switchesOffRecord L.D M record) R →
      Observed L.U M obs R → ∃ R', DefaultCompletion L X M record obs R' ∧ DecLe L.D M R' R from h _ R rfl hR ho
  intro n
  induction n using Nat.strongRecOn with
  | ind n ih =>
  intro R hf hR ho
  by_cases hmin : ∀ R', AdmissibleCompletion L.U X M (openNames L) (record ++ switchesOffRecord L.D M record) R' →
      Observed L.U M obs R' → DecLe L.D M R' R → DecLe L.D M R R'
  · exact ⟨R, ⟨hR, ho, hmin⟩, fun _ _ h => h⟩
  obtain ⟨R'', h1, h2, h3, h4⟩ : ∃ R'',
      AdmissibleCompletion L.U X M (openNames L) (record ++ switchesOffRecord L.D M record) R'' ∧
      Observed L.U M obs R'' ∧ DecLe L.D M R'' R ∧ ¬ DecLe L.D M R R'' :=
    Classical.byContradiction fun hno => hmin fun R' a b c => Classical.byContradiction fun hd => hno ⟨R', a, b, c, hd⟩
  obtain ⟨a, ha, hRa, hna⟩ : ∃ a ∈ decisionAtoms L.D M, R a.1 a.2 ∧ ¬ R'' a.1 a.2 :=
    Classical.byContradiction fun hno => h4 fun a ha hRa => Classical.byContradiction fun hn => hno ⟨a, ha, hRa, hn⟩
  have hlt : f R'' < f R :=
    VE.NormDefaults.countP_lt_of (fun b hb h => by simpa using h3 b hb (by simpa using h))
      ⟨a, ha, by simpa using hRa, by simpa using hna⟩
  obtain ⟨R', hdc, hle⟩ := ih (f R'') (hf ▸ hlt) R'' rfl h1 h2
  exact ⟨R', hdc, fun b hb h => h3 b hb (hle b hb h)⟩

/-- "The facts here force <e>": a decision atom true in every default completion is true in every admissible
    completion that agrees with the record and the observations. Proved in the stub from `defaultCompletion_below`. -/
theorem forced_everywhere {α : Type} [DecidableEq α] (L : LayeredU) (X : List VE.Formula)
    (M : VE.FiniteModel α) (record : List ((String × List α) × Bool))
    (obs : List ((VE.Norms.Regulated × List α) × Bool)) (a : String × List α) (ha : a ∈ decisionAtoms L.D M)
    (hall : ∀ R, DefaultCompletion L X M record obs R → R a.1 a.2) (R : String → List α → Prop)
    (hR : AdmissibleCompletion L.U X M (openNames L) (record ++ switchesOffRecord L.D M record) R)
    (ho : Observed L.U M obs R) : R a.1 a.2 := by
  obtain ⟨R', hdc, hle⟩ := defaultCompletion_below L X M record obs R hR ho
  exact hle a ha (hall R' hdc)

end Zone

/-- `defaultZoneOf` is `zoneOfMin` on `zoneMin`'s result (DRI 2026-11-04, df-5 item 2). -/
theorem defaultZoneOf_eq (L : LayeredU) (X : List (String × VE.Formula)) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) (obs : List ((VE.Norms.Regulated × List α) × Bool))
    (r : VE.Norms.Regulated) (vs : List α) (proposed : List (List ((String × List α) × Bool))) :
    defaultZoneOf L X M record obs r vs proposed =
      match zoneMin L X M record obs with | .error z => z | .ok Min => zoneOfMin L M record r vs Min := rfl

/-- `forcedAllOf` is `forcedOfMin` on `zoneMin`'s result. -/
theorem forcedAllOf_eq (L : LayeredU) (X : List (String × VE.Formula)) (M : VE.FiniteModel α)
    (record : List ((String × List α) × Bool)) (obs : List ((VE.Norms.Regulated × List α) × Bool))
    (proposed : List (List ((String × List α) × Bool))) :
    forcedAllOf L X M record obs proposed =
      match zoneMin L X M record obs with | .error _ => none | .ok Min => forcedOfMin L M record Min := rfl

end Proofs

end VE.Defaults
