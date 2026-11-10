import VE.Presupposition.Admit
import VE.Discourse.Joint

/-! # Coupling of equal goals (docs/spec/presupposition.md 1.9 and 4.8; PS-3)

A pick chooses one emitted candidate per unresolved obligation (never in place, R-3). A group is two or more
unresolved obligations with equal goals and equal cells, root carriers only. Its representative sets every member
to assumed if one chose assumed, else asserted if one chose asserted, else conditioned. A group is couplable when
every pick of the existing constrained joint set `J` (lf-14d's enumeration) has its representative in `J`; only
couplable groups are coupled, by generated `requires` constraints in lf-14d's `Constraint` type
(`couplingConstraints`, `couplings_spec`). Picks are compared under the document's own semantics (R-9): W1's
elaboration without a norm-defaults block, the unspecified completion with one; the placeholder `deny` never applies.

The source-identity choice "assume `pre` once" for a closed `pre` that several unresolved rule acts take for granted
is one extra, labelled choice (`sourceChoices`), offered beside the per-rule candidates and never imposed: it enters
neither a group nor the joint set. Its entailment is `source_identity_entails` (Rules.lean). -/
namespace VE.Presupposition
universe u

/-- One candidate per unresolved obligation, by obligation id. -/
abbrev Pick := List (String × Candidate)

def pickOf (ch : Pick) (o : String) : Option Candidate := (ch.find? (fun x => x.1 == o)).map (·.2)

structure Group where
  members : List String
  goal    : VE.Formula
  cands   : List Candidate
  deriving DecidableEq, Repr

/-- Unresolved obligations with equal goals and equal cells, at least two, root carriers only. -/
def groups (t : CandidateTable) (R : Report) : List Group :=
  let opens := R.checked.filter (fun c => c.ob.carrier == .unresolved)
  let step : List Group → Checked → List Group := fun gs c =>
    let cs := t c.ob.row c.pos
    if gs.any (fun g => g.goal == c.goal && g.cands == cs) then
      gs.map (fun g => if g.goal == c.goal && g.cands == cs then { g with members := g.members ++ [c.ob.id] } else g)
    else gs ++ [({ members := [c.ob.id], goal := c.goal, cands := cs } : Group)]
  (opens.foldl step []).filter (fun g => decide (2 ≤ g.members.length) && g.cands.all Candidate.core)

def repCandidate (g : Group) (ch : Pick) : Candidate :=
  if g.members.any (fun o => pickOf ch o == some .assumed) then .assumed
  else if g.members.any (fun o => pickOf ch o == some .asserted) then .asserted
  else .conditioned

def rep (g : Group) (ch : Pick) : Pick :=
  ch.map (fun x => if g.members.contains x.1 then (x.1, repCandidate g ch) else x)

def Uniform (g : Group) (ch : Pick) : Prop := ∀ o ∈ g.members, ∀ o' ∈ g.members, pickOf ch o = pickOf ch o'

def uniformB (g : Group) (ch : Pick) : Bool :=
  g.members.all (fun o => g.members.all (fun o' => pickOf ch o == pickOf ch o'))

/-- The check over the existing constrained joint set `J`: every admissible choice's representative is admissible. -/
def couplable (J : List Pick) (g : Group) : Bool :=
  g.cands.all Candidate.core && J.all (fun ch => J.contains (rep g ch))

def coupledSet (J : List Pick) (gs : List Group) : List Pick := J.filter (fun ch => gs.all (fun g => uniformB g ch))

/-- The picked reading of unit `u`, found by its canonical candidate; aliases never enter (R-3). -/
def readingFor (R : Report) (ch : Pick) (u : String) (rs : List RReading) : Option RReading :=
  (R.checked.find? (fun c => c.ob.unit == u && c.ob.carrier == .unresolved)).bind (fun c =>
    (pickOf ch c.ob.id).bind (fun k => rs.find? (fun r => r.cand == k)))

/-- What one unit contributes to the document's formulas under a pick. -/
def unitFormulas (R : Report) (ch : Pick) (x : DocUnit) : List VE.Formula :=
  match x.content, (match x.content with | .readings rs => readingFor R ch x.id rs | _ => none) with
  | .claim a, _ => if x.asserted then [a] else []
  | .readings _, some ⟨_, _, .claim a, p⟩ => a :: p.toList
  | .readings _, some ⟨_, _, .rule _, p⟩ => p.toList
  | _, _ => []

/-- Background, claims, picked readings. -/
def formulasUnder (D : PDoc) (R : Report) (ch : Pick) : List VE.Formula :=
  D.background ++ D.units.flatMap (unitFormulas R ch)

/-- The rule an open rule unit contributes under a pick. -/
def unitRule (R : Report) (ch : Pick) (x : DocUnit) : Option VE.Norms.Node :=
  match (match x.content with | .readings rs => readingFor R ch x.id rs | _ => none) with
  | some ⟨_, _, .rule N, _⟩ => some N
  | _ => none

/-- Fixed rules and picked open rules. -/
def treeUnder (D : PDoc) (R : Report) (ch : Pick) : VE.Norms.Tree :=
  { D.norms with nodes := D.norms.nodes ++ D.units.filterMap (unitRule R ch) }

/-- The picked readings' premises. -/
def assumptionsUnder (D : PDoc) (R : Report) (ch : Pick) : List VE.Formula :=
  D.units.flatMap (fun x => match x.content with
    | .readings rs => ((readingFor R ch x.id rs).bind (·.premise)).toList
    | _ => [])

/-- R-3: a pick names emitted readings only, never in place. -/
def PickFits (t : CandidateTable) (R : Report) (ch : Pick) : Prop :=
  (ch.map (·.1)).Nodup ∧
  (∀ x ∈ ch, ∃ c ∈ R.checked, c.ob.id = x.1 ∧ c.ob.carrier = .unresolved ∧ x.2 ∈ emitted t c) ∧
  ∀ c ∈ R.checked, c.ob.carrier = .unresolved → (pickOf ch c.ob.id).isSome

instance (t : CandidateTable) (R : Report) (ch : Pick) : Decidable (PickFits t R ch) := by
  unfold PickFits; infer_instance

/-- R-9: the picked document as norm-defaults' `UDoc`. -/
def pickedU (D : PDoc) (R : Report) (ch : Pick) : VE.NormDefaults.UDoc :=
  ⟨⟨D.E, D.lits, treeUnder D R ch⟩, D.unspec⟩

/-- R-9: a model of the picked document under the document's own semantics: W1's elaboration without a
    norm-defaults block; with one, the unspecified completion. The placeholder `deny` is never applied. -/
def SatUnder (D : PDoc) (R : Report) (ch : Pick) (S : VE.Structure.{u}) : Prop :=
  if D.defaults then
    VE.Norms.Sat S (formulasUnder D R ch) ∧
      ∀ r ∈ D.norms.regulated, VE.NormDefaults.IntendedAt3 (pickedU D R ch) r S
  else VE.Norms.Sat S (formulasUnder D R ch ++ VE.Norms.elaborate (treeUnder D R ch))

/-- R-9: with a norm-defaults block, the picked document passes norm-defaults' check. -/
def PickedWF (D : PDoc) (R : Report) (ch : Pick) : Prop :=
  D.defaults = true → VE.NormDefaults.WellFormedU (pickedU D R ch) = true

def SameModels (D : PDoc) (R : Report) (ch ch' : Pick) : Prop :=
  PickedWF D R ch ∧ PickedWF D R ch' ∧
  ∀ S : VE.Structure.{u}, S.Admissible D.E → (SatUnder D R ch S ↔ SatUnder D R ch' S)

def SameDecides (D : PDoc) (R : Report) (ch ch' : Pick) : Prop :=
  ∀ S : VE.Structure.{u}, S.Admissible D.E → SatUnder D R ch S →
    ∀ r ∈ D.norms.regulated, ∀ vs, VE.TupleTyped S r.sorts vs → ∀ sign : Bool,
      ((VE.Norms.decides (treeUnder D R ch) r.name sign).denote S (VE.Norms.tupleVal vs) ↔
        (VE.Norms.decides (treeUnder D R ch') r.name sign).denote S (VE.Norms.tupleVal vs))

/-! ## The generated `requires` constraints (lf-14d's API, called, never edited)

A presupposition reading set is named by its obligation (spec 1.9: a unit's only open set is its obligation's own),
at version `ver o`; reading `i` is the `i`-th emitted candidate of the obligation's cell. A couplable group
contributes, for every ordered pair of members and every reading index of the shared cell, `requires (o, i) (o', i)`. -/

/-- The reading index of candidate `k` in obligation `o`'s reading set. -/
def pickIndex (t : CandidateTable) (R : Report) (o : String) (k : Candidate) : Option Nat :=
  (R.checked.find? (fun c => c.ob.id == o)).map (fun c => (emitted t c).idxOf k)

/-- A pick as lf-14d's choice vector. -/
def choiceOf (t : CandidateTable) (R : Report) (ver : String → Nat) (ch : Pick) : VE.Discourse.Choice :=
  ch.filterMap (fun x => (pickIndex t R x.1 x.2).map (fun i => (x.1, ver x.1, i)))

def groupConstraints (ver : String → Nat) (g : Group) : List VE.Discourse.Constraint :=
  g.members.flatMap (fun o => g.members.flatMap (fun o' => (List.range g.cands.length).map (fun i =>
    ⟨.requires, (o, ver o, i), (o', ver o', i)⟩)))

/-- The constraints PS-3 adds to the manifest: one block per couplable group; an uncouplable group adds none. -/
def couplingConstraints (ver : String → Nat) (J : List Pick) (gs : List Group) : List VE.Discourse.Constraint :=
  (gs.filter (couplable J)).flatMap (groupConstraints ver)

/-! ## The source-identity choice (offered, never imposed) -/

/-- The label of the source-identity choice (spec 1.6: "assume `pre` once"). -/
def sourceLabel : String := "assume once"

/-- One extra, labelled choice: assume the closed `pre` once for the listed unresolved rule acts. -/
structure SourceChoice where
  label   : String
  pre     : VE.Formula
  members : List String
  deriving DecidableEq, Repr

/-- Every closed `pre` that two or more unresolved rule acts take for granted, once, in block order. -/
def sourceChoices (E : VE.Environment) (R : Report) : List SourceChoice :=
  let acts := R.checked.filter (fun c => c.ob.carrier == .unresolved && c.pos == .ruleAct && c.pre.check E [])
  ((acts.map (·.pre)).eraseDups.map (fun p => ⟨sourceLabel, p, (acts.filter (·.pre == p)).map (·.ob.id)⟩)).filter
    (fun s => decide (2 ≤ s.members.length))

end VE.Presupposition
