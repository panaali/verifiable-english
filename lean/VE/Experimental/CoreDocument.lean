-- ve-layer: 4 (the document mode's lowering over its decoded units; experimental, unreachable from the service)
import VE.Service.Document

/-! The lowering of a document to its core documents (kb-2a step A; docs/spec/kernel-boundary.md 4.1 and 4.2;
the architect seat's design for kb-2a, section 2.1).

Expires: 2026-12-07

`lower` takes what the document mode's `check` has decoded before its status folds (the environment `Env`, the
judgment records and unit views, the units with their `UnitContent`, the active reading sets with their candidates)
and answers, for each compatible choice of readings, one core document: the environment and norm objects the soft
route's `decodeSoftSource` reads, the premises `P` of the slot, and every statement with its origin. It decodes no
document text again, calls no kernel, and has no flag, status or verdict of its own: its only answers are core
documents or a refusal (`UnsupportedLowering`, `ReadingsCollapsed`, `UnknownPart`, `ResourceLimit`, or the judgment
refusals of `Judgments.admit` and `Judgments.status`, reused unchanged).

Tier: experimental (spec section 5); nothing the service imports reaches this module. Step B promotes it to the
shell and calls it from the document mode. -/

namespace VE.Experimental.CoreDocument
open Lean
open VE.Service.Document
open VE.Discourse (FrontSet)

/-! ## Types -/

/-- Where a statement comes from: its unit, the feature that lowered it and, for a reading, the set id and the index
of the reading in that set. -/
structure Origin where
  unit : String
  feature : String
  reading : Option (String × Nat) := none
  deriving DecidableEq, Repr

/-- What a statement says, without its origin. -/
inductive Body
  /-- A soft rule: one norm object of the soft route's source, as `decodeSoftSource` reads it. -/
  | soft (rule : Json)
  /-- A premise of the slot `P` (`Compose.SlotWellFormed`). -/
  | premise (φ : VE.Formula)
  /-- A judgment term: a base predicate with its decider (`Judgments.admit`); it contributes no premise. -/
  | judgment (term : VE.Judgments.Judgment)

/-- A body as text, one per body: the readings' distinctness is decided on these. -/
def Body.key : Body → String
  | .soft r => "soft " ++ r.compress
  | .premise φ => "premise " ++ (VE.Route.Wire.encodeFormula φ).compress
  | .judgment j => "judgment " ++ reprStr j

def Body.rule? : Body → Option Json
  | .soft r => some r
  | _ => none

def Body.premise? : Body → Option VE.Formula
  | .premise φ => some φ
  | _ => none

structure Statement where
  body : Body
  origin : Origin

/-- One core document: the environment and the norm objects the soft route's `decodeSoftSource` reads for `X`, the
premises `P`, and every statement with its origin, in the document order of their units. -/
structure CoreDoc where
  environment : Json
  norms : Json
  premises : List VE.Formula
  statements : List Statement

/-- The core document of a statement list: its norm objects and premises are its statements' soft rules and premises,
in order. -/
def CoreDoc.of (environment : Json) (statements : List Statement) : CoreDoc :=
  ⟨environment, Json.arr (statements.filterMap (·.body.rule?)).toArray, statements.filterMap (·.body.premise?),
    statements⟩

/-- For each active reading set, by its id, the index of the reading chosen; in the order of the sets. -/
abbrev Choice := List (String × Nat)

/-- An active reading set and its candidates (`setCandidates`: a formula, a W1 rule, or `none` for a pending
reading), one per reading. -/
abbrev ActiveSet := FrontSet × List (Option VE.Judgments.Content)

/-- A coupling of reading sets on one axis: each coupled set's id and each of its readings' label on that axis. A
choice is compatible when the readings it chooses in the coupled sets have one label. -/
structure Coupling where
  id : String
  members : List (String × List String)

/-! ## The table, row by row -/

def unsupported (unit feature why : String) : String :=
  s!"UnsupportedLowering: unit {unit} feature {feature}: {why}"

/-- The profiles a row of the table lowers (with the base); a document listing any other is refused. -/
def rowProfiles : List String :=
  ["data@0", "documents@1", "judgments@0", "norms@0", "readings@1", "relational-fol@0", "soft-norms@0"]

/-- A feature of the whole document that no row lowers: a profile outside the rows (rights, cardinality,
norm-defaults, alternatives, risk, scope, events, ...), senses, a composed block, or W3 definitions. -/
def documentFeature (E : Env) (senses : Bool) : Option String :=
  match E.profiles.find? (!rowProfiles.contains ·) with
  | some p => some p
  | none =>
    if senses then some "senses"
    else if E.block != .none then some "alternatives or risk block"
    else if E.events.isSome then some "events@0"
    else if E.cardinality.isSome then some "cardinality@0"
    else if !E.rv.definitions.isEmpty then some "definitions"
    else none

/-- A JSON value as the soft relay sends it: `wireJson` with the fuel of the document mode's soft requests
(`DocumentChain.requestOf`, `softContentOf`). -/
def wire (j : Json) : Json := wireJson 257 j

/-- The soft rule a strict W1 norm lowers to: its encoding, when the soft route's decoder, over the core document's
environment, reads it as the strict rule with the same name, predicate, sign, guard, carve-outs and precedence, and no
exception, rank, alterable party, hardness or split. Otherwise there is no embedding, and the reason. -/
def strictRule (environment : Json) (n : VE.Norms.Node) : Except String Json := do
  let rule := wire (VE.Alternatives.Wire.encodeNode n)
  let src ← (VE.SoftNorms.Wire.decodeSoftSource environment (Json.arr #[])).mapError
    (s!"the soft route's decoder refuses the core environment: {·}")
  let N ← (VE.SoftNorms.Wire.decodeSoftNorm src.se rule).mapError (s!"the soft route's decoder refuses the rule: {·}")
  unless N == { toNode := n, mode := .strict, rank := none, alterable := [], exception := none, hard := false } do
    throw "the soft route's decoder reads it as another rule"
  pure rule

/-- A formula unit's premise; a formula over a regulated predicate is a claim about the rules, not a premise. -/
def premise (E : Env) (unit : String) (φ : VE.Formula) : Except String Body := do
  if let some p := (VE.Norms.preds φ).find? E.regulated.contains then
    throw (unsupported unit "facts" s!"a formula over the regulated predicate {p} is a claim about the rules, not a premise")
  pure (.premise φ)

/-- A unit's own content, lowered: at most one body, with the feature that lowered it. -/
def lowerContent (E : Env) (environment : Json) (unit : String) :
    Option UnitContent → Except String (Option (String × Body))
  | none => pure none
  | some (.formula φ) => return some ("facts", ← premise E unit φ)
  | some (.soft r) => pure (some ("soft-norms@0", .soft (wire r)))
  | some (.norm n) => do
    let r ← (strictRule environment n).mapError (unsupported unit "norms@0" s!"a strict norm has no soft rule: {·}")
    pure (some ("norms@0", .soft r))
  | some (.rights _) => throw (unsupported unit "rights@0" "a rights block has no row")
  | some (.cardinality _) => throw (unsupported unit "cardinality@0" "a cardinality statement has no row")

/-- A reading's candidate, lowered as the same content of its unit would be; a pending reading lowers to nothing. -/
def lowerCandidate (E : Env) (environment : Json) (unit : String) :
    Option VE.Judgments.Content → Except String (Option (String × Body))
  | none => pure none
  | some (.formula φ) => lowerContent E environment unit (some (.formula φ))
  | some (.rule n) => lowerContent E environment unit (some (.norm n))

/-- The judgment terms a unit's `open` meaning lists, in its order: each one a declaration, never a premise. -/
def declarations (J : List VE.Judgments.Judgment) (u : SourceUnit) : List (String × Body) :=
  (listedOf u.meaning).filterMap (fun (t : String) =>
    Option.map (fun j => ("judgments@0", Body.judgment j)) (J.find? (·.name == t)))

/-! ## References -/

def setFault (unitIds : List String) (x : ActiveSet) : Option String :=
  if !unitIds.contains x.1.unit then
    some s!"UnknownPart: reading set {x.1.id} names unit {x.1.unit}, which the document does not have"
  else if x.2.length != x.1.readings.length then
    some s!"UnknownPart: reading set {x.1.id} has {x.2.length} candidates for {x.1.readings.length} readings"
  else none

def setsFault (unitIds : List String) (sets : List ActiveSet) : Option String :=
  (sets.findSome? (setFault unitIds)).orElse fun _ =>
    if (sets.map (·.1.id)).Nodup && (sets.map (·.1.unit)).Nodup then none
    else some "UnknownPart: two active reading sets have one id or one unit"

def couplingFault (sets : List ActiveSet) (c : Coupling) : Option String :=
  c.members.findSome? fun (s, labels) => match sets.find? (·.1.id == s) with
    | none => some s!"UnknownPart: coupling {c.id} names reading set {s}, which is not an active reading set"
    | some x => if labels.length == x.1.readings.length then none
      else some s!"UnknownPart: coupling {c.id} labels {labels.length} readings of set {s}, which has {x.1.readings.length}"

def declared (E : Env) (p : String) : Bool := (E.rv.environment.predicates p).isSome

/-- Whether the reading a statement's origin names, if any, is an active set of the statement's unit and an index
inside it. -/
def readingNamed (sets : List ActiveSet) (s : Statement) : Bool :=
  match s.origin.reading with
  | some (r, i) => sets.any fun x => x.1.id == r && x.1.unit == s.origin.unit && decide (i < x.1.readings.length)
  | none => true

/-- A predicate of a premise, or a judgment term, that the vocabulary does not declare. -/
def bodyFault (E : Env) (s : Statement) : Option String :=
  match s.body with
  | .premise φ => ((VE.Norms.preds φ).find? (!declared E ·)).map fun p =>
    s!"UnknownPart: a premise of unit {s.origin.unit} names predicate {p}, which the vocabulary does not declare"
  | .judgment j => if declared E j.name then none else
    some s!"UnknownPart: judgment term {j.name} of unit {s.origin.unit} is not a predicate of the vocabulary"
  | .soft _ => none

/-- The first reference of a statement that the document does not have: its unit, its reading, a predicate of its
premise or its judgment term. -/
def statementFault (E : Env) (unitIds : List String) (sets : List ActiveSet) (s : Statement) : Option String :=
  if !unitIds.contains s.origin.unit then
    some s!"UnknownPart: a statement's origin names unit {s.origin.unit}, which the document does not have"
  else if !readingNamed sets s then
    some s!"UnknownPart: a statement of unit {s.origin.unit} names a reading no active set of the unit has"
  else bodyFault E s

/-! ## Readings and choices -/

/-- Each reading's statements (its unit's body under that reading, if any), in the order of the readings. -/
abbrev Options := List (Option (String × Body))

def readingOptions (E : Env) (environment : Json) (x : ActiveSet) : Except String Options :=
  x.2.mapM (lowerCandidate E environment x.1.unit)

def optionKeys (opts : Options) : List (Option String) := opts.map (Option.map (·.2.key))

/-- The first two readings, `(i, j)` with `i < j`, that lower to the same statements. -/
def collapsed (keys : List (Option String)) : Option (Nat × Nat) :=
  (List.range keys.length).findSome? fun j =>
    (List.range j).findSome? fun i => if keys[i]? == keys[j]? then some (i, j) else none

/-- Two readings of the set that lower to the same statements are refused. -/
def distinct (x : ActiveSet) (opts : Options) : Except String Unit :=
  if (optionKeys opts).Nodup then .ok () else
    let (i, j) := (collapsed (optionKeys opts)).getD (0, 0)
    .error s!"ReadingsCollapsed: reading set {x.1.id} readings {i} and {j} lower to the same statements"

def readingsOf (E : Env) (environment : Json) (x : ActiveSet) : Except String (ActiveSet × Options) := do
  let opts ← readingOptions E environment x
  distinct x opts
  pure (x, opts)

/-- A choice is compatible when, for each coupling, the readings it chooses in the coupled sets have at most one
label on that axis. -/
def compatible (couplings : List Coupling) (c : Choice) : Bool :=
  couplings.all (fun (cp : Coupling) =>
    let labels := c.filterMap (fun (p : String × Nat) =>
      (cp.members.lookup p.1).bind (fun (ls : List String) => ls[p.2]?))
    labels.eraseDups.length ≤ 1)

/-- Every choice of one reading index per set, in the order of the sets. -/
def allChoices : List (String × Nat) → List Choice
  | [] => [[]]
  | (s, n) :: rest => (List.range n).flatMap fun i => (allChoices rest).map ((s, i) :: ·)

/-- The compatible choices of the active sets. -/
def compatibleChoices (couplings : List Coupling) (sets : List ActiveSet) : List Choice :=
  (allChoices (sets.map fun x => (x.1.id, x.1.readings.length))).filter (compatible couplings)

def maxChoices : Nat := 64
/-- The combinations enumerated before couplings are read: a work bound; a larger product is refused. -/
def maxCombinations : Nat := 4096

/-- The unit of the first active set, which a refusal of the sets names. -/
def firstUnit : List ActiveSet → String
  | x :: _ => x.1.unit
  | [] => ""

def choicesOf (couplings : List Coupling) (sets : List ActiveSet) : Except String (List Choice) := do
  let combinations := (sets.map (·.1.readings.length)).foldl (· * ·) 1
  if combinations > maxCombinations then
    throw s!"ResourceLimit: {combinations} combinations of readings, more than {maxCombinations} to enumerate"
  match compatibleChoices couplings sets with
  | [] => throw (unsupported (firstUnit sets) "readings@1" "the couplings leave no compatible choice")
  | cs =>
    if cs.length > maxChoices then throw s!"ResourceLimit: {cs.length} compatible choices, more than {maxChoices}"
    pure cs

/-! ## The lowering -/

/-- A unit's lowering before a choice: its judgment declarations, then its statements under each reading of its
active set (`set`), or, with no active set, its own content's (`set = none`, one option). -/
structure UnitPlan where
  unit : String
  declarations : List (String × Body)
  set : Option String
  options : Options

/-- A unit's statements under a choice: its declarations, then the body of the reading chosen in its set (that
reading's origin), or of its own content. -/
def UnitPlan.statements (c : Choice) (p : UnitPlan) : List Statement :=
  let reading := p.set.bind fun s => Option.map (s, ·) (c.lookup s)
  p.declarations.map (fun (f, b) => ⟨b, ⟨p.unit, f, none⟩⟩) ++
    match (p.options[(Option.map Prod.snd reading).getD 0]?).join with
    | some (f, b) => [⟨b, ⟨p.unit, f, reading⟩⟩]
    | none => []

def planOf (E : Env) (environment : Json) (J : List VE.Judgments.Judgment) (rd : List (ActiveSet × Options))
    (u : SourceUnit) : Except String UnitPlan :=
  match rd.find? (fun (r : ActiveSet × Options) => r.1.1.unit == u.id) with
  | some (x, opts) => pure ⟨u.id, declarations J u, some x.1.id, opts⟩
  | none => do return ⟨u.id, declarations J u, none, [← lowerContent E environment u.id u.content]⟩

/-- A feature of the document that no row lowers, refused at the document's first unit. -/
def featureRefusal (E : Env) (senses : Bool) (units : List SourceUnit) : Except String Unit :=
  match documentFeature E senses with
  | some f => throw (unsupported ((units.head?.map (·.id)).getD "") f "the table has no row for it")
  | none => pure ()

/-- Under `judgments@0`: the records' admission (`Judgments.admit`) and each unit's judgment refusals
(`Judgments.status`, whose value is not used), unchanged. The judgments `Judgments.admit` answers. -/
def judgments (E : Env) (records : List VE.Judgments.Rec) (views : List VE.Judgments.UnitView)
    (units : List SourceUnit) : Except String (List VE.Judgments.Judgment) := do
  if !E.profiles.contains "judgments@0" then return []
  let J ← VE.Judgments.admit E.rv.environment E.rv.definitions E.regulated records
  unless views.map (fun (v : VE.Judgments.UnitView) => v.id) == units.map (fun (u : SourceUnit) => u.id) do
    throw "UnknownPart: the unit views are not the document's units"
  for v in views do
    let _ ← VE.Judgments.status E.rv.definitions (VE.Judgments.names J) v
  pure J

/-- The reading sets' and couplings' references. -/
def references (unitIds : List String) (sets : List ActiveSet) (couplings : List Coupling) : Except String Unit :=
  match setsFault unitIds sets, couplings.findSome? (couplingFault sets) with
  | some m, _ => .error m
  | none, some m => .error m
  | none, none => .ok ()

/-- The refusals before any unit is lowered, in order; the judgments `Judgments.admit` answers. -/
def preliminaries (E : Env) (senses : Bool) (records : List VE.Judgments.Rec) (views : List VE.Judgments.UnitView)
    (units : List SourceUnit) (sets : List ActiveSet) (couplings : List Coupling) :
    Except String (List VE.Judgments.Judgment) := do
  featureRefusal E senses units
  let J ← judgments E records views units
  references (units.map (·.id)) sets couplings
  pure J

def finish (E : Env) (unitIds : List String) (sets : List ActiveSet) (docs : List (Choice × CoreDoc)) :
    Except String (List (Choice × CoreDoc)) :=
  match docs.findSome? fun d => d.2.statements.findSome? (statementFault E unitIds sets) with
  | some m => .error m
  | none => .ok docs

/-- The lowering: one core document per compatible choice of the active reading sets, its statements in the
document order of their units. -/
def lower (E : Env) (senses : Bool) (records : List VE.Judgments.Rec) (views : List VE.Judgments.UnitView)
    (units : List SourceUnit) (sets : List ActiveSet) (couplings : List Coupling) :
    Except String (List (Choice × CoreDoc)) := do
  let J ← preliminaries E senses records views units sets couplings
  let rd ← sets.mapM (readingsOf E (wire E.lower))
  let plans ← units.mapM (planOf E (wire E.lower) J rd)
  let choices ← choicesOf couplings sets
  finish E (units.map (·.id)) sets
    (choices.map fun c => (c, CoreDoc.of (wire E.lower) (plans.flatMap (·.statements c))))

/-! ## Theorems, for every input the lowering answers -/

open VE.Kit.Except (bind_ok)

theorem finish_ok {E : Env} {unitIds : List String} {sets : List ActiveSet} {docs cs : List (Choice × CoreDoc)}
    (h : finish E unitIds sets docs = .ok cs) :
    cs = docs ∧ ∀ d ∈ docs, ∀ st ∈ d.2.statements, statementFault E unitIds sets st = none := by
  unfold finish at h
  split at h
  · cases h
  · rename_i hn
    cases h
    refine ⟨rfl, fun d hd st hst => ?_⟩
    have := List.findSome?_eq_none_iff.mp hn d hd
    exact List.findSome?_eq_none_iff.mp this st hst

theorem statementFault_none {E : Env} {unitIds : List String} {sets : List ActiveSet} {s : Statement}
    (h : statementFault E unitIds sets s = none) :
    s.origin.unit ∈ unitIds ∧
    (∀ r i, s.origin.reading = some (r, i) →
      ∃ x ∈ sets, x.1.id = r ∧ x.1.unit = s.origin.unit ∧ i < x.1.readings.length) ∧
    (∀ φ, s.body = .premise φ → ∀ p ∈ VE.Norms.preds φ, declared E p = true) ∧
    (∀ j, s.body = .judgment j → declared E j.name = true) := by
  unfold statementFault at h
  by_cases hu : unitIds.contains s.origin.unit = true
  · by_cases hr : readingNamed sets s = true
    · simp only [hu, hr, Bool.not_true, Bool.false_eq_true, ↓reduceIte] at h
      refine ⟨List.contains_iff_mem.mp hu, fun r i hri => ?_, fun φ hφ p hp => ?_, fun j hj => ?_⟩
      · unfold readingNamed at hr
        rw [hri] at hr
        simp only [List.any_eq_true, Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq] at hr
        obtain ⟨x, hx, ⟨h1, h2⟩, h3⟩ := hr
        exact ⟨x, hx, h1, h2, h3⟩
      · unfold bodyFault at h
        rw [hφ] at h
        simp only [Option.map_eq_none_iff, List.find?_eq_none, Bool.not_eq_true', Bool.not_eq_false] at h
        simpa using h p hp
      · unfold bodyFault at h
        rw [hj] at h
        simp only at h
        split at h
        · assumption
        · cases h
    · simp only [hu, Bool.not_true, Bool.false_eq_true, ↓reduceIte, Bool.not_eq_true'] at h
      simp only [Bool.not_eq_true] at hr
      simp [hr] at h
  · have hu : s.origin.unit ∉ unitIds := by simpa using hu
    simp [hu] at h

theorem allChoices_nodup : ∀ L : List (String × Nat), (allChoices L).Nodup
  | [] => by simp [allChoices]
  | (s, n) :: rest => by
    simp only [allChoices, List.Nodup]
    rw [List.pairwise_flatMap]
    refine ⟨fun i _ => ?_, ?_⟩
    · rw [List.pairwise_map]
      exact (allChoices_nodup rest).imp fun hne heq => hne (List.cons.inj heq).2
    · exact (List.nodup_range).imp fun hij x hx y hy heq => by
        obtain ⟨x', _, rfl⟩ := List.mem_map.mp hx
        obtain ⟨y', _, rfl⟩ := List.mem_map.mp hy
        exact hij (Prod.mk.inj (List.cons.inj heq).1).2

theorem allChoices_mem : ∀ (L : List (String × Nat)) (c : Choice), c ∈ allChoices L →
    ∀ p ∈ c, ∃ q ∈ L, q.1 = p.1 ∧ p.2 < q.2
  | [], c, hc, p, hp => by simp [allChoices] at hc; subst hc; cases hp
  | (s, n) :: rest, c, hc, p, hp => by
    simp only [allChoices, List.mem_flatMap, List.mem_range, List.mem_map] at hc
    obtain ⟨i, hi, c', hc', rfl⟩ := hc
    cases hp with
    | head => exact ⟨(s, n), List.mem_cons_self, rfl, hi⟩
    | tail _ hp =>
      obtain ⟨q, hq, h1, h2⟩ := allChoices_mem rest c' hc' p hp
      exact ⟨q, List.mem_cons_of_mem _ hq, h1, h2⟩

theorem choicesOf_ok {couplings : List Coupling} {sets : List ActiveSet} {cs : List Choice}
    (h : choicesOf couplings sets = .ok cs) : cs = compatibleChoices couplings sets ∧ cs.length ≤ maxChoices := by
  unfold choicesOf at h
  simp only at h
  split at h
  · cases h
  generalize hc : compatibleChoices couplings sets = l at h
  cases l with
  | nil => cases h
  | cons c rest =>
    dsimp only at h
    split at h
    · cases h
    · rename_i hle
      cases h
      exact ⟨rfl, Nat.le_of_not_gt hle⟩

theorem preliminaries_sets {E : Env} {senses : Bool} {records : List VE.Judgments.Rec}
    {views : List VE.Judgments.UnitView} {units : List SourceUnit} {sets : List ActiveSet}
    {couplings : List Coupling} {J : List VE.Judgments.Judgment}
    (h : preliminaries E senses records views units sets couplings = .ok J) :
    ∀ x ∈ sets, x.1.unit ∈ units.map (·.id) := by
  unfold preliminaries at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, hs, _⟩ := bind_ok h
  intro x hx
  unfold references at hs
  split at hs
  · cases hs
  · cases hs
  rename_i hn _
  unfold setsFault at hn
  cases hf : sets.findSome? (setFault (units.map (·.id))) with
  | some m => rw [hf] at hn; cases hn
  | none =>
    have := List.findSome?_eq_none_iff.mp hf x hx
    unfold setFault at this
    split at this
    · cases this
    · rename_i hu
      simpa using hu

/-- The parts of a lowered document. -/
theorem lower_ok {E : Env} {senses : Bool} {records : List VE.Judgments.Rec} {views : List VE.Judgments.UnitView}
    {units : List SourceUnit} {sets : List ActiveSet} {couplings : List Coupling} {cs : List (Choice × CoreDoc)}
    (h : lower E senses records views units sets couplings = .ok cs) :
    (∃ J, preliminaries E senses records views units sets couplings = .ok J) ∧
    (∃ rd, sets.mapM (readingsOf E (wire E.lower)) = .ok rd) ∧
    (∃ plans : List UnitPlan, cs = (compatibleChoices couplings sets).map
      fun c => (c, CoreDoc.of (wire E.lower) (plans.flatMap (UnitPlan.statements c)))) ∧
    (compatibleChoices couplings sets).length ≤ maxChoices ∧
    ∀ d ∈ cs, ∀ st ∈ d.2.statements, statementFault E (units.map (·.id)) sets st = none := by
  unfold lower at h
  obtain ⟨J, hJ, h⟩ := bind_ok h
  obtain ⟨rd, hrd, h⟩ := bind_ok h
  obtain ⟨plans, _, h⟩ := bind_ok h
  obtain ⟨choices, hc, h⟩ := bind_ok h
  obtain ⟨rfl, hf⟩ := finish_ok h
  obtain ⟨rfl, hle⟩ := choicesOf_ok hc
  exact ⟨⟨J, hJ⟩, ⟨rd, hrd⟩, ⟨plans, rfl⟩, hle, hf⟩

/-- (a) Every statement's origin is a unit of the document, and an origin that names a reading names an active set
of that unit and an index inside it; every set a choice names is an active set of a unit of the document, and the
index chosen is inside it. -/
theorem lower_origin_units {E : Env} {senses : Bool} {records : List VE.Judgments.Rec}
    {views : List VE.Judgments.UnitView} {units : List SourceUnit} {sets : List ActiveSet}
    {couplings : List Coupling} {cs : List (Choice × CoreDoc)}
    (h : lower E senses records views units sets couplings = .ok cs) :
    ∀ d ∈ cs,
      (∀ st ∈ d.2.statements, st.origin.unit ∈ units.map (·.id) ∧
        ∀ r i, st.origin.reading = some (r, i) →
          ∃ x ∈ sets, x.1.id = r ∧ x.1.unit = st.origin.unit ∧ i < x.1.readings.length) ∧
      ∀ p ∈ d.1, ∃ x ∈ sets, x.1.id = p.1 ∧ x.1.unit ∈ units.map (·.id) ∧ p.2 < x.1.readings.length := by
  obtain ⟨⟨J, hJ⟩, _, ⟨plans, rfl⟩, _, hf⟩ := lower_ok h
  intro d hd
  refine ⟨fun st hst => ?_, fun p hp => ?_⟩
  · have := statementFault_none (hf d hd st hst)
    exact ⟨this.1, this.2.1⟩
  · obtain ⟨c, hc, rfl⟩ := List.mem_map.mp hd
    have hc := (List.mem_filter.mp hc).1
    obtain ⟨q, hq, h1, h2⟩ := allChoices_mem _ c hc p hp
    obtain ⟨x, hx, rfl⟩ := List.mem_map.mp hq
    exact ⟨x, hx, h1, preliminaries_sets hJ x hx, h2⟩

/-- (b) For every active set, the statement lists of two different readings are different. -/
theorem lower_readings_distinct {E : Env} {senses : Bool} {records : List VE.Judgments.Rec}
    {views : List VE.Judgments.UnitView} {units : List SourceUnit} {sets : List ActiveSet}
    {couplings : List Coupling} {cs : List (Choice × CoreDoc)}
    (h : lower E senses records views units sets couplings = .ok cs) :
    ∀ x ∈ sets, ∃ opts, readingOptions E (wire E.lower) x = .ok opts ∧
      (opts.map (·.map Prod.snd)).Nodup := by
  obtain ⟨_, ⟨rd, hrd⟩, _⟩ := lower_ok h
  intro x hx
  obtain ⟨y, _, hy⟩ := VE.Acts.mapM_ok hrd x hx
  unfold readingsOf at hy
  obtain ⟨opts, ho, hy⟩ := bind_ok hy
  obtain ⟨_, hu, _⟩ := bind_ok hy
  refine ⟨opts, ho, ?_⟩
  unfold distinct at hu
  split at hu
  · rename_i hn
    unfold optionKeys List.Nodup at hn
    rw [List.pairwise_map] at hn
    unfold List.Nodup
    rw [List.pairwise_map]
    have hk : ∀ o : Option (String × Body), o.map (·.2.key) = (o.map Prod.snd).map Body.key := fun o => by
      cases o <;> rfl
    exact hn.imp fun hne heq => hne (by rw [hk, hk, heq])
  · cases hu

/-- (c) One core document per compatible choice, at most 64, no choice twice. -/
theorem lower_choices {E : Env} {senses : Bool} {records : List VE.Judgments.Rec}
    {views : List VE.Judgments.UnitView} {units : List SourceUnit} {sets : List ActiveSet}
    {couplings : List Coupling} {cs : List (Choice × CoreDoc)}
    (h : lower E senses records views units sets couplings = .ok cs) :
    cs.map Prod.fst = compatibleChoices couplings sets ∧
    cs.length = (compatibleChoices couplings sets).length ∧ cs.length ≤ 64 ∧ (cs.map Prod.fst).Nodup := by
  obtain ⟨_, _, ⟨plans, rfl⟩, hle, _⟩ := lower_ok h
  have hm : ((compatibleChoices couplings sets).map fun c =>
      (c, CoreDoc.of (wire E.lower) (plans.flatMap (UnitPlan.statements c)))).map Prod.fst =
      compatibleChoices couplings sets := by
    rw [List.map_map]
    exact List.map_id' _ ▸ rfl
  refine ⟨hm, by simp, by simpa using hle, ?_⟩
  rw [hm]
  exact (allChoices_nodup _).filter _

/-- (d) Every predicate a premise mentions and every term a judgment declaration names is declared in the core
document's vocabulary (`Env.rv`, decoded from the environment the core document carries). -/
theorem lower_names_bound {E : Env} {senses : Bool} {records : List VE.Judgments.Rec}
    {views : List VE.Judgments.UnitView} {units : List SourceUnit} {sets : List ActiveSet}
    {couplings : List Coupling} {cs : List (Choice × CoreDoc)}
    (h : lower E senses records views units sets couplings = .ok cs) :
    ∀ d ∈ cs,
      (∀ φ ∈ d.2.premises, ∀ p ∈ VE.Norms.preds φ, (E.rv.environment.predicates p).isSome) ∧
      ∀ st ∈ d.2.statements, ∀ j, st.body = .judgment j → (E.rv.environment.predicates j.name).isSome := by
  obtain ⟨_, _, ⟨plans, rfl⟩, _, hf⟩ := lower_ok h
  intro d hd
  refine ⟨fun φ hφ p hp => ?_, fun st hst j hj => (statementFault_none (hf d hd st hst)).2.2.2 j hj⟩
  obtain ⟨c, _, rfl⟩ := List.mem_map.mp hd
  obtain ⟨st, hst, hb⟩ := List.mem_filterMap.mp hφ
  have hb : st.body = .premise φ := by
    revert hb; cases st.body <;> simp [Body.premise?]
  exact (statementFault_none (hf _ hd st hst)).2.2.1 φ hb p hp

/-- The core document's norm objects and premises are its statements' soft rules and premises, in order. -/
theorem lower_parts {E : Env} {senses : Bool} {records : List VE.Judgments.Rec}
    {views : List VE.Judgments.UnitView} {units : List SourceUnit} {sets : List ActiveSet}
    {couplings : List Coupling} {cs : List (Choice × CoreDoc)}
    (h : lower E senses records views units sets couplings = .ok cs) :
    ∀ d ∈ cs, d.2 = CoreDoc.of (wire E.lower) d.2.statements := by
  obtain ⟨_, _, ⟨plans, rfl⟩, _, _⟩ := lower_ok h
  intro d hd
  obtain ⟨c, _, rfl⟩ := List.mem_map.mp hd
  rfl

end VE.Experimental.CoreDocument
