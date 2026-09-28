import VE.SoftNorms.Soften

/-! Rights documents (docs/spec/rights.md sections 1, 3 and 9.1): the environment
`rights` block, rights and their incident lines, limitations with named conditions,
the Art. 30 bar, line instances in instance order and the generated vocabulary
`E″ = E + lim + cond + aimed` (1.5, 1.6).

A `RightsDoc` is a soft document (`soft`: the author's `E`, literals, soft block and the
norm units outside rights) plus the rights block, the rights, the limitations and at
most one bar. The `right_lines` units of 3.2 are already appended to their right's
`lines` by the decoder, at the unit's own position, so `lines` is the right's complete
line list in document order. `outsideCites` carries the `cites` of the norm units
outside rights (rule name ↦ key ↦ cited units, 3.2), the only rights-relevant field
those units have beyond their soft norm object.

Nothing here refers to the elaboration: `correlate`, `limPremises` and
`WellFormedRights` are in `Correlate.lean`. -/
namespace VE.Rights
open VE.Norms (Regulated Role)
open VE.SoftNorms (SoftNode SoftDoc)

/-- Source kind, as authored; a limitation's `kinds` matches it. -/
inductive Kind | claim | liberty | immunity | power
  deriving DecidableEq, Repr

/-- Instance kind, what `linesOf` produces (1.2). -/
inductive IKind | claim | liberty | immunity | powerLiberty | powerRecognition
  deriving DecidableEq, Repr

inductive Reading | rule | query
  deriving DecidableEq, Repr

structure Condition where
  name : String
  /-- `false` = sufficient. -/
  necessary : Bool
  verbalisation : String
  decidedBy : Option String
  deriving DecidableEq, Repr

structure Limitation where
  name : String
  /-- `none` = all. -/
  scope : Option (List String)
  /-- `none` = all. -/
  kinds : Option (List Kind)
  decidedBy : Option String
  conditions : List Condition
  factors : List String
  deriving DecidableEq, Repr

structure Bar where
  name : String
  reading : Reading
  decidedBy : Option String
  deriving DecidableEq, Repr

/-- A line as authored (3.2). -/
structure SourceLine where
  kind : Kind
  /-- claim, liberty, immunity; its predicate is ignored when `fanOut ≠ []`. -/
  norm : Option SoftNode
  /-- power only -/
  liberty : Option SoftNode
  /-- power only -/
  recognition : Option SoftNode
  /-- bearer sort ↦ predicate, empty when not a fan-out -/
  fanOut : List (String × String)
  holderSlot : Option Nat
  cites : List (String × List String)
  deriving DecidableEq, Repr

/-- A line instance (1.2): what every projection, audit and theorem ranges over. -/
structure Line where
  right : String
  source : SourceLine
  /-- `= source.kind`; `inScope` matches it. -/
  kind : Kind
  ikind : IKind
  /-- The instance's rule as written: the norm; a fan-out instance on its bearer sort's
  predicate, named `rights-fan-<k>`; a power's liberty or recognition unit. -/
  node : SoftNode
  /-- The bearer sort of a fan-out instance. -/
  bearer : Option String
  deriving DecidableEq, Repr

structure Right where
  name : String
  holder : String
  /-- Typed in the context `[holder]`. -/
  guard : VE.Formula
  lines : List SourceLine
  deriving DecidableEq, Repr

/-- An `alters` entry (1.1). -/
structure AltersEntry where
  actKey : String
  /-- The affected holder's argument index. -/
  holderSlot : Nat
  status : String
  recognition : Option String
  deriving DecidableEq, Repr

structure RightsEnv where
  holders : List String
  bearers : List String
  «protected» : List String
  alters : List AltersEntry
  deriving DecidableEq, Repr

structure RightsDoc where
  /-- `E`, literals, the soft block and the norm units outside rights (`T`). -/
  soft : SoftDoc
  rights : RightsEnv
  rs : List Right
  limits : List Limitation
  /-- length ≤ 1 -/
  bars : List Bar
  /-- The `cites` of the norm units outside rights, by rule name. -/
  outsideCites : List (String × List (String × List String))

/-! ## Generated names (1.6) -/

def fanName (k : Nat) : String := s!"rights-fan-{k}"
def barRuleName (k : Nat) : String := s!"rights-bar-{k}"
def limName (k : Nat) : String := s!"rights__lim__{k}"
def condName (k : Nat) : String := s!"rights__cond__{k}"
def aimedName (k : Nat) : String := s!"rights__bar__{k}"

/-! ## Line instances in instance order (1.2, 1.6) -/

/-- The instance kind of a claim, liberty or immunity line. -/
def ikindOf : Kind → IKind
  | .claim => .claim
  | .liberty => .liberty
  | .immunity => .immunity
  | .power => .powerLiberty

/-- The fan-out map in bearer-sort order. -/
def sortFan (l : List (String × String)) : List (String × String) :=
  VE.Norms.sortBy (fun a b => decide (a.1 < b.1)) l

/-- The instances of one source line of right `R`, given the number `k` of fan-out
instances before it: one per bearer sort for a fan-out line (`rights-fan-<k+i+1>`), a
power's liberty then its recognition unit, else the line itself. -/
def instancesOf (R : String) (S : SourceLine) (k : Nat) : List Line :=
  match S.kind with
  | .power =>
    match S.liberty, S.recognition with
    | some l, some r => [⟨R, S, .power, .powerLiberty, l, none⟩, ⟨R, S, .power, .powerRecognition, r, none⟩]
    | _, _ => []
  | kd =>
    match S.norm with
    | none => []
    | some n =>
      if S.fanOut = [] then [⟨R, S, kd, ikindOf kd, n, none⟩]
      else (sortFan S.fanOut).mapIdx (fun i bp =>
        ⟨R, S, kd, ikindOf kd, { n with name := fanName (k + i + 1), pred := bp.2 }, some bp.1⟩)

/-- The number of fan-out instances of one source line. -/
def fanCount (S : SourceLine) : Nat :=
  match S.kind with
  | .power => 0
  | _ => if S.norm.isSome then (sortFan S.fanOut).length else 0

def linesAux : List (String × SourceLine) → Nat → List (String × Line)
  | [], _ => []
  | (R, S) :: rest, k => (instancesOf R S k).map (R, ·) ++ linesAux rest (k + fanCount S)

/-- `(right, source line)` in document order. -/
def sourceLines (D : RightsDoc) : List (String × SourceLine) :=
  D.rs.flatMap (fun R => R.lines.map (R.name, ·))

/-- `(right name, line instance)` in instance order (1.6). -/
def linesOf (D : RightsDoc) : List (String × Line) := linesAux (sourceLines D) 0

def dutyKind (N : Line) : Bool :=
  match N.ikind with | .claim | .immunity | .powerRecognition => true | _ => false

def libertyKind (N : Line) : Bool :=
  match N.ikind with | .liberty | .powerLiberty => true | _ => false

def rightOf (D : RightsDoc) (R : String) : Option Right := D.rs.find? (·.name == R)

/-- The argument sorts of the instance's predicate. -/
def sortsOf (D : RightsDoc) (N : Line) : List String := VE.SoftNorms.sortsOf D.soft N.node.pred

/-- 1.2: the subject slot for a liberty half, else the named `holder_slot`, else the first
object slot of the holder sort. -/
def holderSlot (D : RightsDoc) (N : Line) : Nat :=
  match N.ikind with
  | .liberty | .powerLiberty => 0
  | _ =>
    match N.source.holderSlot with
    | some k => k
    | none =>
      match rightOf D N.right with
      | some R => ((sortsOf D N).drop 1).idxOf R.holder + 1
      | none => 1

/-- The permission predicates of the liberty and powerLiberty instances. -/
def permPreds (D : RightsDoc) : List String :=
  (linesOf D).filterMap (fun RN => if libertyKind RN.2 then some RN.2.node.pred else none)

/-- `p` is the predicate of some line instance. -/
def rightDerived (D : RightsDoc) (p : String) : Bool := (linesOf D).any (fun RN => RN.2.node.pred == p)

/-- `m` is the predicate of some liberty or powerLiberty instance. -/
def rightPermission (D : RightsDoc) (m : String) : Bool := (permPreds D).contains m

def ruleReading (D : RightsDoc) : Bool := D.bars.any (fun b => b.reading == .rule)

/-- `R ∈ scope(L) ∧ kind(N) ∈ kinds(L)`, the source kind (4.2). -/
def inScope (_D : RightsDoc) (L : Limitation) (R : String) (N : Line) : Bool :=
  (match L.scope with | none => true | some rs => rs.contains R) &&
    (match L.kinds with | none => true | some ks => ks.contains N.kind)

/-! ## Canonical orders and indices (1.6) -/

/-- The act key of an instance (1.3). -/
def lineAct (D : RightsDoc) (N : Line) : String := VE.SoftNorms.actKey D.soft N.node.pred

/-- The act keys of the instances in scope of `L`, first occurrence kept. -/
def limActs (D : RightsDoc) (L : Limitation) : List String :=
  VE.SoftNorms.dedup ((linesOf D).filterMap (fun RN => if inScope D L RN.1 RN.2 then some (lineAct D RN.2) else none))

def pairLex (x y : String × String) : Bool := decide (x.1 < y.1) || (x.1 == y.1 && decide (x.2 < y.2))

def tripleLex (x y : String × String × String) : Bool :=
  decide (x.1 < y.1) || (x.1 == y.1 && pairLex x.2 y.2)

/-- `(limitation name, act key)`, sorted. -/
def limKeys (D : RightsDoc) : List (String × String) :=
  VE.Norms.sortBy pairLex (D.limits.flatMap (fun L => (limActs D L).map (L.name, ·)))

/-- `(limitation name, act key, condition name)`, sorted. -/
def condKeys (D : RightsDoc) : List (String × String × String) :=
  VE.Norms.sortBy tripleLex (D.limits.flatMap (fun L =>
    (limActs D L).flatMap (fun a => L.conditions.map (fun c => (L.name, a, c.name)))))

def limIndex (D : RightsDoc) (L : Limitation) (actKey : String) : Nat := (limKeys D).idxOf (L.name, actKey) + 1

def condIndex (D : RightsDoc) (L : Limitation) (c : Condition) (actKey : String) : Nat :=
  (condKeys D).idxOf (L.name, actKey, c.name) + 1

/-- The right-derived permission predicates, by name. -/
def barPreds (D : RightsDoc) : List String := VE.Route.sortStrings (VE.SoftNorms.dedup (permPreds D))

def barIndex (D : RightsDoc) (m : String) : Nat := (barPreds D).idxOf m + 1

/-- The index of a fan-out instance, read back from its generated name's position. -/
def fanIndex (D : RightsDoc) (N : Line) : Option Nat :=
  if N.bearer.isSome then
    (((linesOf D).map (·.2)).filter (·.bearer.isSome)).idxOf N |> fun i => some (i + 1)
  else none

/-! ## `E″` (1.5) -/

def limDecls (D : RightsDoc) : List (String × List String) :=
  (limKeys D).map (fun k => (limName ((limKeys D).idxOf k + 1), VE.SoftNorms.sortsOf D.soft k.2))

def condDecls (D : RightsDoc) : List (String × List String) :=
  (condKeys D).map (fun k => (condName ((condKeys D).idxOf k + 1), VE.SoftNorms.sortsOf D.soft k.2.1))

/-- `aimed_m` exists under both readings, and only when a bar unit exists. -/
def aimedDecls (D : RightsDoc) : List (String × List String) :=
  if D.bars = [] then [] else (barPreds D).map (fun m => (aimedName (barIndex D m), VE.SoftNorms.sortsOf D.soft m))

/-- Every rights-generated predicate with its argument sorts. -/
def genDecls (D : RightsDoc) : List (String × List String) := limDecls D ++ condDecls D ++ aimedDecls D

/-- `E″ = E + lim + cond + aimed`, the soft input vocabulary of `T″`. -/
def envR (D : RightsDoc) : VE.Environment :=
  { D.soft.E with predicates := fun p => match (genDecls D).find? (·.1 == p) with
      | some d => some d.2
      | none => D.soft.E.predicates p }

theorem envR_of_no_gen (D : RightsDoc) (h : genDecls D = []) : envR D = D.soft.E := by
  unfold envR
  rw [h]
  rfl

theorem limKeys_nil (D : RightsDoc) (h : D.limits = []) : limKeys D = [] := by
  simp [limKeys, h, VE.Norms.sortBy]

theorem condKeys_nil (D : RightsDoc) (h : D.limits = []) : condKeys D = [] := by
  simp [condKeys, h, VE.Norms.sortBy]

theorem genDecls_nil (D : RightsDoc) (hl : D.limits = []) (hb : D.bars = []) : genDecls D = [] := by
  simp [genDecls, limDecls, condDecls, aimedDecls, limKeys_nil D hl, condKeys_nil D hl, hb]

/-! ## Membership lemmas -/

theorem mem_dedup {α : Type} [BEq α] [LawfulBEq α] (x : α) : ∀ l : List α, x ∈ VE.SoftNorms.dedup l ↔ x ∈ l
  | [] => by simp [VE.SoftNorms.dedup]
  | y :: ys => by
    unfold VE.SoftNorms.dedup
    split
    · rename_i hc
      rw [mem_dedup x ys, List.mem_cons]
      constructor
      · exact Or.inr
      · rintro (rfl | h)
        · exact (mem_dedup x ys).mp (List.contains_iff_mem.mp hc)
        · exact h
    · rw [List.mem_cons, List.mem_cons, mem_dedup x ys]

theorem mem_barPreds (D : RightsDoc) (m : String) : m ∈ barPreds D ↔ rightPermission D m = true := by
  simp only [barPreds, VE.Route.sortStrings, List.mem_mergeSort, mem_dedup, rightPermission,
    List.contains_iff_mem]

end VE.Rights
