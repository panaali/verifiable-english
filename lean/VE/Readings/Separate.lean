import VE.Readings.Doc
import VE.Readings.Layers
import VE.NormDefaults.Dag

/-! Separating situations (docs/spec/composition-s1.md 1.5 to 1.7, 4.5, 4.6, 4.9, 8.3).

The generated base predicates of a document are named by their **source keys** (`GenKey`), never by their
positional names; `genKeys` lists them in the order of the generated vocabulary (`genKeys_names`). A key is
**owned** by a candidate when its rule or limitation name is one the candidate declares, and shared otherwise.

`Achieves D s i B F q v` is the semantic statement: `B` is admissible over the author's base vocabulary and some
completion of candidate `i` over `B`, with the shared tables `F` and tables of its own for the keys it owns, gives
the probe `q` the value `v`, read in the expansion of the completion. `separates` is the executable check of 4.5:
step 1's conditions on keys, tables and the probe (`situationWF`), the witness's completion, and every assignment
of the other candidate's owned tables over the base. `separates_sound` says that, on a base valid over the
author's vocabulary, a `true` answer proves the witness achieves the recorded value on the shown base and shared
tables and the other candidate does not.

Typing of tables is checked per generated name, against the generated name's declaration in the elaborated
base vocabulary (`declaredTyped`), so the checks need no fact about how keys and names correspond beyond the
one table a name reads. -/
namespace VE.Readings
open VE.Norms (Regulated Sat tupleVal envAt size conflict outcomeBase)
open VE.SoftNorms (SoftNode SoftDoc soften WellFormedSoft ValueSoft SelectsSoftD canon circ selects' exceptedF)
open VE.Rights (RightsDoc correlate BaseAdmissibleR backgroundValidR linesOf nodeOf)
open VE.Compose (Content)
universe u

/-! ## Source keys (1.5) -/

inductive GenKey
  | excepted (rule : String) (bearer : Option String)
  | off (rule : String) (bearer : Option String) (party : String)
  | outweighs (act lower higher : String)
  | lim (limitation act : String)
  | cond (limitation act condition : String)
  | aimed (pred : String)
  deriving DecidableEq, Repr

/-- The author rule name of a line instance: the source norm's name for a fan-out instance, else the instance's
    own rule name. -/
def ruleOf (N : VE.Rights.Line) : String :=
  if N.bearer.isSome then (N.source.norm.map (·.name)).getD N.node.name else N.node.name
/-- The nodes of `correlate X` in order, each with its rule's source name and bearer. -/
def keyedNodes (X : RightsDoc) : List (SoftNode × String × Option String) :=
  (linesOf X).map (fun RN => (nodeOf X RN.2, ruleOf RN.2, RN.2.bearer)) ++
    X.soft.T.nodes.map (fun N => (N, N.name, none)) ++ (VE.Rights.barNodes X).map (fun N => (N, N.name, none))
/-- The generated base predicates of X's elaboration: source key, name in X, argument sorts, in the order
    `VE.SoftNorms.decisions (correlate X) ++ VE.Rights.genDecls X`. -/
def genKeys (X : RightsDoc) : List (GenKey × String × List String) :=
  ((keyedNodes X).filter (fun e => e.1.mode == .default)).map (fun e =>
      (GenKey.excepted e.2.1 e.2.2, VE.SoftNorms.exceptedName e.1, VE.SoftNorms.sortsOf (correlate X) e.1.pred)) ++
  (keyedNodes X).flatMap (fun e => e.1.alterable.map (fun π =>
      (GenKey.off e.2.1 e.2.2 π, VE.SoftNorms.offName e.1 π, VE.SoftNorms.sortsOf (correlate X) e.1.pred))) ++
  (VE.SoftNorms.outweighsTriples (correlate X)).map (fun x =>
      (GenKey.outweighs x.1 x.2.1 x.2.2, VE.SoftNorms.outweighsName x.1 x.2.1 x.2.2,
        VE.SoftNorms.actSortsOf (correlate X) x.1)) ++
  (VE.Rights.limKeys X).map (fun k =>
      (GenKey.lim k.1 k.2, VE.Rights.limName ((VE.Rights.limKeys X).idxOf k + 1), VE.SoftNorms.sortsOf X.soft k.2)) ++
  (VE.Rights.condKeys X).map (fun k =>
      (GenKey.cond k.1 k.2.1 k.2.2, VE.Rights.condName ((VE.Rights.condKeys X).idxOf k + 1),
        VE.SoftNorms.sortsOf X.soft k.2.1)) ++
  (if X.bars = [] then [] else (VE.Rights.barPreds X).map (fun m =>
      (GenKey.aimed m, VE.Rights.aimedName (VE.Rights.barIndex X m), VE.SoftNorms.sortsOf X.soft m)))

theorem keyedNodes_nodes (X : RightsDoc) : (keyedNodes X).map (·.1) = (correlate X).T.nodes := by
  simp [keyedNodes, correlate, List.map_append, List.map_map, Function.comp_def]

theorem genKeys_names (X : RightsDoc) :
  (genKeys X).map (fun g => (g.2.1, g.2.2)) = VE.SoftNorms.decisions (correlate X) ++ VE.Rights.genDecls X := by
  have hn := keyedNodes_nodes X
  simp only [genKeys, VE.SoftNorms.decisions, VE.SoftNorms.exceptedDecisions, VE.SoftNorms.offDecisions,
    VE.SoftNorms.outweighsDecisions, VE.Rights.genDecls, VE.Rights.limDecls, VE.Rights.condDecls,
    VE.Rights.aimedDecls, ← hn, List.map_append, List.map_map, List.filter_map, List.flatMap_map,
    List.map_flatMap, Function.comp_def, List.append_assoc]
  split <;> simp

/-- The rule or limitation name a key carries; `none` for a key over environment names only. -/
def GenKey.source : GenKey → Option (String × String)
  | .excepted r _ => some ("rule", r)
  | .off r _ _ => some ("rule", r)
  | .lim L _ => some ("limitation", L)
  | .cond L _ _ => some ("limitation", L)
  | .outweighs _ _ _ => none
  | .aimed _ => none
def owned (D : Doc) (s : String) (i : Nat) (k : GenKey) : Bool :=
  match (candidate D s i).bind (·.content), k.source with
  | some c, some n => c.declared.contains n
  | _, _ => false
def ownedKeys (D : Doc) (s : String) (i : Nat) : List GenKey :=
  ((genKeys (one D s i).1).map (·.1)).filter (owned D s i)

/-! ## Completions and probes (1.6) -/

abbrev Tables (α : Type u) := GenKey → List α → Prop
/-- B with every generated predicate of X read from its key's table. -/
def withTables (X : RightsDoc) (B : VE.Structure.{u}) (G : Tables B.Carrier) : VE.Structure.{u} :=
  { B with relation := fun p vs => match (genKeys X).find? (·.2.1 == p) with
      | some g => G g.1 vs
      | none => B.relation p vs }
/-- Every regulated and defined predicate at its meaning over the base. -/
def expand (X : RightsDoc) (B : VE.Structure.{u}) : VE.Structure.{u} := canon (soften (correlate X)) B

inductive Probe (α : Type u)
  | outcome (p : String) (vs : List α)
  | selects (kind p : String) (vs : List α)
  | holds
  deriving DecidableEq
def kindWord : VE.Rights.IKind → String
  | .claim => "claim" | .liberty => "liberty" | .immunity => "immunity"
  | .powerLiberty => "powerLiberty" | .powerRecognition => "powerRecognition"
/-- The nodes of the kind on p, as they sit in `correlate X`. A probe never names a rule. -/
def selectable (X : RightsDoc) (kind p : String) : List SoftNode :=
  if kind == "norm" then X.soft.T.nodes.filter (·.pred == p)
  else ((linesOf X).filter (fun RN => kindWord RN.2.ikind == kind && RN.2.node.pred == p)).map
    (fun RN => nodeOf X RN.2)

/-- Probe q has value v in the expansion of B, for the document X with assertions A. -/
def Observes (X : RightsDoc) (A : List VE.Formula) (B : VE.Structure.{u}) : Probe B.Carrier → Bool → Prop
  | .outcome p vs, v => ∃ r ∈ (correlate X).T.regulated, r.name = p ∧ VE.TupleTyped B r.sorts vs ∧
      ValueSoft (correlate X) r (expand X B) vs = some v
  | .selects k p vs, v => VE.TupleTyped B (VE.SoftNorms.sortsOf (correlate X) p) vs ∧
      ((∃ N ∈ selectable X k p,
          SelectsSoftD (correlate X) (expand X B) (tupleVal vs) (VE.SoftNorms.fuel (correlate X)) N) ↔ v = true)
  | .holds, v => ((∀ a ∈ A, a.denote (expand X B) []) ↔ v = true)

/-- The author's base vocabulary. -/
def authorEnv (D : Doc) : VE.Environment := envAt D.frame.soft.base 0
/-- B is admissible over the author's base vocabulary, and some completion of candidate i over B and shared
    tables F gives q the value v. Tables of keys the candidate does not own are F's and are not reassigned.
    Without the first conjunct a base could carry a true tuple on a predicate that one reading's document
    generates and the other's does not declare (K2b). -/
def Achieves (D : Doc) (s : String) (i : Nat) (B : VE.Structure.{u}) (F : Tables B.Carrier)
    (q : Probe B.Carrier) (v : Bool) : Prop :=
  B.Admissible (authorEnv D) ∧
  ∃ G : Tables B.Carrier, (∀ k, owned D s i k = false → ∀ vs, G k vs ↔ F k vs) ∧
    BaseAdmissibleR (one D s i).1 (withTables (one D s i).1 B G) ∧
    Observes (one D s i).1 (one D s i).2 (withTables (one D s i).1 B G) q v
def Separated (D : Doc) (s : String) (i j : Nat) : Prop :=
  ∃ (B : VE.Structure.{u}) (F : Tables B.Carrier) (q : Probe B.Carrier) (v : Bool),
    (Achieves D s i B F q v ∧ ¬ Achieves D s j B F q v) ∨ (Achieves D s j B F q v ∧ ¬ Achieves D s i B F q v)

/-! ## The executable check (4.5) -/

structure Situation (α : Type u) where
  base : VE.FiniteModel α
  fixed : List (GenKey × List (List α))
  decisions : List (GenKey × List (List α))
  probe : Probe α
  value : Bool

/-- The table of key k in T, `[]` when absent. -/
def tableOf {α : Type u} (T : List (GenKey × List (List α))) (k : GenKey) : List (List α) :=
  ((T.find? (·.1 == k)).map (·.2)).getD []
/-- M with, for every generated predicate of X, the table of its key in T (`[]` when absent). -/
def tablesModel {α : Type u} (X : RightsDoc) (M : VE.FiniteModel α) (T : List (GenKey × List (List α))) :
    VE.FiniteModel α :=
  { M with relations := fun p => match (genKeys X).find? (·.2.1 == p) with
      | some g => tableOf T g.1
      | none => M.relations p }
/-- A tuple of M's domains, by sorts. -/
def typedTuple {α : Type u} [DecidableEq α] (M : VE.FiniteModel α) : List String → List α → Bool
  | [], [] => true
  | s :: ss, v :: vs => decide (v ∈ M.domains s) && typedTuple M ss vs
  | _, _ => false
/-- The key the generated predicate `p` of X reads. -/
def keyOfName (X : RightsDoc) (p : String) : Option GenKey := ((genKeys X).find? (·.2.1 == p)).map (·.1)
/-- `vs` is typed over M's domains by the declaration of `p` in X's elaborated base vocabulary. -/
def declaredTyped {α : Type u} [DecidableEq α] (X : RightsDoc) (M : VE.FiniteModel α) (p : String)
    (vs : List α) : Bool :=
  match (envAt (soften (correlate X)) 0).predicates p with
  | some ss => typedTuple M ss vs
  | none => false
/-- Every table of T is on a key of X and holds tuples typed over M's domains by the key's sorts: the declared
    sorts of every generated predicate that reads the key. -/
def tablesTyped {α : Type u} [DecidableEq α] (X : RightsDoc) (M : VE.FiniteModel α)
    (T : List (GenKey × List (List α))) : Bool :=
  T.all (fun t => (genKeys X).any (·.1 == t.1) &&
    t.2.all (fun vs => (genKeys X).all (fun g => keyOfName X g.2.1 != some t.1 || declaredTyped X M g.2.1 vs)))
/-- The six probe kinds of 1.6. -/
def probeKinds : List String := ["claim", "liberty", "immunity", "powerLiberty", "powerRecognition", "norm"]
/-- The probe names a regulated predicate, a kind of 1.6 and a tuple typed over M's domains. -/
def probeTyped {α : Type u} [DecidableEq α] (X : RightsDoc) (M : VE.FiniteModel α) : Probe α → Bool
  | .outcome p vs => X.soft.T.regulated.any (·.name == p) &&
      typedTuple M (VE.SoftNorms.sortsIn X.soft.T.regulated p) vs
  | .selects k p vs => probeKinds.contains k && X.soft.T.regulated.any (·.name == p) &&
      typedTuple M (VE.SoftNorms.sortsIn X.soft.T.regulated p) vs
  | .holds => true

def observe {α : Type u} [DecidableEq α] (X : RightsDoc) (A : List VE.Formula) (M : VE.FiniteModel α) :
    Probe α → Option Bool
  | .outcome p vs =>
    match (correlate X).T.regulated.find? (·.name == p) with
    | some r => if (conflict (soften (correlate X)) r).eval M (tupleVal vs) then none
                else some ((outcomeBase (soften (correlate X)) p).eval M (tupleVal vs))
    | none => none
  | .selects k p vs => some ((selectable X k p).any (fun N =>
      (circ (correlate X) (selects' (correlate X) N)).eval M (tupleVal vs)))
  | .holds => some (A.all (fun a => (circ (correlate X) a).eval M []))

def sideValid {α : Type u} [DecidableEq α] (D : Doc) (s : String) (i : Nat) (M : VE.FiniteModel α)
    (T : List (GenKey × List (List α))) : Bool :=
  tablesTyped (one D s i).1 M T && backgroundValidR (one D s i).1 (tablesModel (one D s i).1 M T)
def sideValue {α : Type u} [DecidableEq α] (D : Doc) (s : String) (i : Nat) (M : VE.FiniteModel α)
    (T : List (GenKey × List (List α))) (q : Probe α) : Option Bool :=
  observe (one D s i).1 (one D s i).2 (tablesModel (one D s i).1 M T) q
/-- Every typed tuple over M's domains. -/
def tuplesOf {α : Type u} (M : VE.FiniteModel α) : List String → List (List α)
  | [] => [[]]
  | s :: ss => (M.domains s).flatMap (fun v => (tuplesOf M ss).map (v :: ·))
/-- The list without repeats, last occurrences kept. -/
def uniq {β : Type u} [BEq β] : List β → List β
  | [] => []
  | x :: xs => if (uniq xs).contains x then uniq xs else x :: uniq xs
/-- The typed tuples of key k over M: those of every generated predicate of X that reads k. -/
def keyTuples {α : Type u} [DecidableEq α] (X : RightsDoc) (M : VE.FiniteModel α) (k : GenKey) : List (List α) :=
  uniq ((genKeys X).flatMap (fun g =>
    if keyOfName X g.2.1 == some k then
      match (envAt (soften (correlate X)) 0).predicates g.2.1 with
      | some ss => tuplesOf M ss
      | none => []
    else []))
/-- The cells of candidate j's owned tables over M: per owned key, the number of typed tuples. -/
def cells {α : Type u} [DecidableEq α] (D : Doc) (s : String) (j : Nat) (M : VE.FiniteModel α) : Nat :=
  ((ownedKeys D s j).map (fun k => (keyTuples (one D s j).1 M k).length)).sum
/-- Every sublist of a list, keeping order. -/
def subsets {β : Type u} : List β → List (List β)
  | [] => [[]]
  | x :: xs => (subsets xs).map (x :: ·) ++ subsets xs
/-- Every assignment of tables to candidate j's owned keys over M's typed tuples: `2 ^ cells` of them. -/
def assignments {α : Type u} [DecidableEq α] (D : Doc) (s : String) (j : Nat) (M : VE.FiniteModel α) :
    List (List (GenKey × List (List α))) :=
  (ownedKeys D s j).foldr (fun k acc =>
    (subsets (keyTuples (one D s j).1 M k)).flatMap (fun tbl => acc.map ((k, tbl) :: ·))) [[]]
def maxCells : Nat := 12
/-- The tables of T on keys that candidate i's document generates: a reading reads no other. -/
def tablesFor {α : Type u} (D : Doc) (s : String) (i : Nat) (T : List (GenKey × List (List α))) :
    List (GenKey × List (List α)) :=
  T.filter (fun t => (genKeys (one D s i).1).any (·.1 == t.1))
/-- The tables of T as relations: the table of key k, empty when T has none. -/
def tablesOf {α : Type u} (T : List (GenKey × List (List α))) : Tables α :=
  fun k vs => ∃ t ∈ T, t.1 = k ∧ vs ∈ t.2
/-- 4.5 step 1 without the id and without the base's validity over the author's vocabulary (the hypothesis
    `valid` of `separates_sound`), i the witness: no key listed twice; every shared key owned by neither reading
    and generated in i's or in j's document; every decision key owned by i and generated in i's document; the
    tables each reading reads typed over the base; the probe typed. -/
def situationWF {α : Type u} [DecidableEq α] (D : Doc) (s : String) (i j : Nat) (σ : Situation α) : Bool :=
  decide (((σ.fixed ++ σ.decisions).map (·.1)).Nodup) &&
  σ.fixed.all (fun t => !owned D s i t.1 && !owned D s j t.1 &&
    ((genKeys (one D s i).1).any (·.1 == t.1) || (genKeys (one D s j).1).any (·.1 == t.1))) &&
  σ.decisions.all (fun t => owned D s i t.1 && (genKeys (one D s i).1).any (·.1 == t.1)) &&
  tablesTyped (one D s i).1 σ.base (tablesFor D s i (σ.fixed ++ σ.decisions)) &&
  tablesTyped (one D s j).1 σ.base (tablesFor D s j σ.fixed) &&
  probeTyped (one D s i).1 σ.base σ.probe

/-- i is the witness. False on a situation that fails `situationWF`, and when the bound is exceeded. It does not
    test whether the base is valid over the author's vocabulary: `separates_sound` takes that as `valid`. -/
def separates {α : Type u} [DecidableEq α] (D : Doc) (s : String) (i j : Nat) (σ : Situation α) : Bool :=
  situationWF D s i j σ &&
  sideValid D s i σ.base (tablesFor D s i (σ.fixed ++ σ.decisions)) &&
  sideValue D s i σ.base (tablesFor D s i (σ.fixed ++ σ.decisions)) σ.probe == some σ.value &&
  decide (cells D s j σ.base ≤ maxCells) &&
  (assignments D s j σ.base).all (fun G =>
    !(sideValid D s j σ.base (tablesFor D s j σ.fixed ++ G) &&
      sideValue D s j σ.base (tablesFor D s j σ.fixed ++ G) σ.probe == some σ.value))

/-! ## A candidate's completions with its layers computed once (lean-first plan F5d)

`observe` builds `soften (correlate X)`, the layer order and the expansion table again for every formula it
evaluates, and `tablesTyped` the base environment for every tuple. `sideOf D s i` computes them once per candidate,
and `sideValidOn` and `sideValueOn` read them; each is equal to the function it replaces (`sideValidOn_sideOf`,
`sideValueOn_sideOf`). -/

/-- Candidate `i`'s document, assertions and generated keys, `soften (correlate X)`, its layers and its base
    environment. -/
structure Side where
  X : RightsDoc
  A : List VE.Formula
  keys : List (GenKey × String × List String)
  S : VE.Norms.Doc
  L : VE.Norms.Layers
  E0 : VE.Environment

def sideOf (D : Doc) (s : String) (i : Nat) : Side :=
  let X := one D s i
  let S := soften (correlate X.1)
  let L := VE.Norms.layersOf S
  ⟨X.1, X.2, genKeys X.1, S, L, VE.Norms.hide S.E L.names⟩

def tablesModelOn {α : Type u} (P : Side) (M : VE.FiniteModel α) (T : List (GenKey × List (List α))) :
    VE.FiniteModel α :=
  { M with relations := fun p => match P.keys.find? (·.2.1 == p) with
      | some g => tableOf T g.1
      | none => M.relations p }

def declaredTypedOn {α : Type u} [DecidableEq α] (P : Side) (M : VE.FiniteModel α) (p : String) (vs : List α) :
    Bool :=
  match P.E0.predicates p with
  | some ss => typedTuple M ss vs
  | none => false

def tablesTypedOn {α : Type u} [DecidableEq α] (P : Side) (M : VE.FiniteModel α)
    (T : List (GenKey × List (List α))) : Bool :=
  T.all (fun t => P.keys.any (·.1 == t.1) &&
    t.2.all (fun vs => P.keys.all (fun g =>
      ((P.keys.find? (·.2.1 == g.2.1)).map (·.1)) != some t.1 || declaredTypedOn P M g.2.1 vs)))

def backgroundValidOn {α : Type u} [DecidableEq α] (P : Side) (M : VE.FiniteModel α) : Bool :=
  (VE.Norms.backgroundValid P.S M &&
    (VE.SoftNorms.softPremisesIn (correlate P.X) P.S P.L).all (fun a => a.eval M [])) &&
  (VE.Rights.limPremises P.X).all (fun a => a.eval M [])

def observeOn {α : Type u} [DecidableEq α] (P : Side) (M : VE.FiniteModel α) : Probe α → Option Bool
  | .outcome p vs =>
    match (correlate P.X).T.regulated.find? (·.name == p) with
    | some r => if (VE.Norms.conflictIn P.S P.L r).eval M (tupleVal vs) then none
                else some ((VE.Norms.outcomeBaseIn P.S P.L p).eval M (tupleVal vs))
    | none => none
  | .selects k p vs => some ((selectable P.X k p).any (fun N =>
      (VE.Norms.substIn P.L P.L.syms.length (VE.SoftNorms.selectsOn P.S (correlate P.X) N)).eval M (tupleVal vs)))
  | .holds => some (P.A.all (fun a => (VE.Norms.substIn P.L P.L.syms.length a).eval M []))

def sideValidOn {α : Type u} [DecidableEq α] (P : Side) (M : VE.FiniteModel α)
    (T : List (GenKey × List (List α))) : Bool :=
  tablesTypedOn P M T && backgroundValidOn P (tablesModelOn P M T)

def sideValueOn {α : Type u} [DecidableEq α] (P : Side) (M : VE.FiniteModel α)
    (T : List (GenKey × List (List α))) (q : Probe α) : Option Bool :=
  observeOn P (tablesModelOn P M T) q

def keyTuplesOn {α : Type u} [DecidableEq α] (P : Side) (M : VE.FiniteModel α) (k : GenKey) : List (List α) :=
  uniq (P.keys.flatMap (fun g =>
    if ((P.keys.find? (·.2.1 == g.2.1)).map (·.1)) == some k then
      match P.E0.predicates g.2.1 with
      | some ss => tuplesOf M ss
      | none => []
    else []))

def ownedKeysOn (D : Doc) (s : String) (j : Nat) (P : Side) : List GenKey :=
  (P.keys.map (·.1)).filter (owned D s j)

def cellsOn {α : Type u} [DecidableEq α] (D : Doc) (s : String) (j : Nat) (P : Side) (M : VE.FiniteModel α) : Nat :=
  ((ownedKeysOn D s j P).map (fun k => (keyTuplesOn P M k).length)).sum

def assignmentsOn {α : Type u} [DecidableEq α] (D : Doc) (s : String) (j : Nat) (P : Side) (M : VE.FiniteModel α) :
    List (List (GenKey × List (List α))) :=
  (ownedKeysOn D s j P).foldr (fun k acc =>
    (subsets (keyTuplesOn P M k)).flatMap (fun tbl => acc.map ((k, tbl) :: ·))) [[]]

theorem ownedKeysOn_sideOf (D : Doc) (s : String) (j : Nat) : ownedKeysOn D s j (sideOf D s j) = ownedKeys D s j := rfl

theorem cellsOn_sideOf {α : Type u} [DecidableEq α] (D : Doc) (s : String) (j : Nat) (M : VE.FiniteModel α) :
    cellsOn D s j (sideOf D s j) M = cells D s j M := rfl

theorem assignmentsOn_sideOf {α : Type u} [DecidableEq α] (D : Doc) (s : String) (j : Nat) (M : VE.FiniteModel α) :
    assignmentsOn D s j (sideOf D s j) M = assignments D s j M := rfl

theorem tablesModelOn_sideOf {α : Type u} (D : Doc) (s : String) (i : Nat) (M : VE.FiniteModel α)
    (T : List (GenKey × List (List α))) : tablesModelOn (sideOf D s i) M T = tablesModel (one D s i).1 M T := rfl

theorem sideValidOn_sideOf {α : Type u} [DecidableEq α] (D : Doc) (s : String) (i : Nat) (M : VE.FiniteModel α)
    (T : List (GenKey × List (List α))) : sideValidOn (sideOf D s i) M T = sideValid D s i M T := by
  simp only [sideValidOn, sideValid, backgroundValidOn, backgroundValidR,
    VE.SoftNorms.backgroundValid', sideOf, VE.SoftNorms.softPremisesIn_eq]
  rfl

theorem sideValueOn_sideOf {α : Type u} [DecidableEq α] (D : Doc) (s : String) (i : Nat) (M : VE.FiniteModel α)
    (T : List (GenKey × List (List α))) (q : Probe α) :
    sideValueOn (sideOf D s i) M T q = sideValue D s i M T q := by
  simp only [sideValueOn, sideValue, tablesModelOn_sideOf]
  cases q with
  | outcome p vs => simp only [observeOn, observe, sideOf, VE.Norms.conflictIn_eq, VE.Norms.outcomeBaseIn_eq]
  | selects k p vs =>
    simp only [observeOn, observe, sideOf, circ, VE.Norms.size, VE.Norms.substIn_eq, VE.Norms.layersOf_syms,
      VE.SoftNorms.selectsOn_soften]
  | holds => simp only [observeOn, observe, sideOf, circ, VE.Norms.size, VE.Norms.substIn_eq, VE.Norms.layersOf_syms]

/-! ## Conservativity (4.9) -/

/-- Every outcome probe and every selects probe on M: regulated predicates of the frame, the six kinds, typed
    tuples, in canonical order. -/
def probesOf {α : Type u} (D : Doc) (M : VE.FiniteModel α) : List (Probe α) :=
  let regs := D.frame.soft.T.regulated
  let names := VE.SoftNorms.dedup (regs.map (·.name))
  names.flatMap (fun p => (tuplesOf M (VE.SoftNorms.sortsIn regs p)).map (Probe.outcome p)) ++
  probeKinds.flatMap (fun k => names.flatMap (fun p =>
    (tuplesOf M (VE.SoftNorms.sortsIn regs p)).map (Probe.selects k p)))
def observeAll {α : Type u} [DecidableEq α] (D : Doc) (s : String) (i : Nat) (M : VE.FiniteModel α)
    (F : List (GenKey × List (List α))) : List (Option Bool) :=
  (probesOf D M).map (sideValue D s i M (tablesFor D s i F))

/-! ## Force (1.7) -/

def strictOf (N : SoftNode) : SoftNode := { N with mode := .strict, exception := none }
def strictTwin (X : SoftDoc) (N : SoftNode) : SoftDoc :=
  { X with T := { X.T with nodes := X.T.nodes.map (fun M => if M.name == N.name then strictOf M else M) } }

/-- `Ns` strict and `Nd` default, equal in every other field (mode, exception and hard apart). -/
def twinNodes (Ns Nd : SoftNode) : Bool :=
  Ns.mode == .strict && Nd.mode == .default &&
    { Ns with mode := .default, exception := Nd.exception, hard := Nd.hard } == Nd
/-- Two lines equal except in their `norm`, which are twins; `none` otherwise. A fan-out line is no force twin. -/
def twinLines (S S' : VE.Rights.SourceLine) : Option (SoftNode × SoftNode) :=
  match S.norm, S'.norm with
  | some Ns, some Nd =>
    if twinNodes Ns Nd && S.fanOut.isEmpty && { S with norm := some Nd } == S' then some (Ns, Nd) else none
  | _, _ => none
/-- Two line lists equal except at one position, where the lines are twins. -/
def twinLineLists : List VE.Rights.SourceLine → List VE.Rights.SourceLine → Option (SoftNode × SoftNode)
  | S :: ls, S' :: ls' =>
    if S == S' then twinLineLists ls ls'
    else match twinLines S S' with
      | some p => if ls == ls' then some p else none
      | none => none
  | _, _ => none
/-- The strict and the default rule of a pair of force twins (1.7), strict first; `none` otherwise. -/
def forceTwins (c c' : Content) : Option (SoftNode × SoftNode) :=
  match c, c' with
  | .norm Ns, .norm Nd => if twinNodes Ns Nd then some (Ns, Nd) else none
  | .right R, .right R' =>
    if R.name == R'.name && R.holder == R'.holder && R.guard == R'.guard then twinLineLists R.lines R'.lines
    else none
  | .rightLines r ls, .rightLines r' ls' => if r == r' then twinLineLists ls ls' else none
  | _, _ => none
/-- A node of the strict reading's elaboration with the default twin's mode, exception and `hard` when it carries
    the twin's name; any other node unchanged. -/
def relaxTo (Nd M : SoftNode) : SoftNode :=
  if M.name == Nd.name then { M with mode := .default, exception := Nd.exception, hard := Nd.hard } else M
/-- The default reading's document is the strict reading's with only the twin's mode changed, read on what the
    semantics uses: both contents declare the same names, the twin's among them; the two readings assert the same
    formulas and generate the same rights vocabulary and `Lim_D`; the elaborated rules of the default reading are
    the strict reading's through `relaxTo`, where the twin's name is strict; the generated keys differ by the
    twin's exception key only, which is the one key named by the twin's exception predicate; the selectable rules
    correspond through `relaxTo`; and no definition takes the exception predicate's name. -/
def twinDocs (D : Doc) (s : String) (i j : Nat) (ci cj : Content) (Nd : SoftNode) : Bool :=
  let Xs := one D s i
  let Xd := one D s j
  let k₀ := GenKey.excepted Nd.name none
  decide (ci.declared = cj.declared) && cj.declared.contains ("rule", Nd.name) && decide (Xs.2 = Xd.2) &&
  decide (VE.Rights.genDecls Xs.1 = VE.Rights.genDecls Xd.1) &&
  decide (VE.Rights.limPremises Xs.1 = VE.Rights.limPremises Xd.1) &&
  decide ((correlate Xd.1).T.nodes = (correlate Xs.1).T.nodes.map (relaxTo Nd)) &&
  (correlate Xs.1).T.nodes.all (fun M => M.name != Nd.name || M.mode == .strict) &&
  decide (genKeys Xs.1 = (genKeys Xd.1).filter (·.1 != k₀)) &&
  (genKeys Xd.1).all (fun g => (g.1 == k₀) == (g.2.1 == VE.SoftNorms.exceptedName Nd)) &&
  decide (Xd.1.soft.T.nodes = Xs.1.soft.T.nodes.map (relaxTo Nd)) &&
  decide ((linesOf Xd.1).map (fun RN => (RN.2.ikind, RN.2.node.pred, nodeOf Xd.1 RN.2)) =
    (linesOf Xs.1).map (fun RN => (RN.2.ikind, RN.2.node.pred, relaxTo Nd (nodeOf Xs.1 RN.2)))) &&
  (correlate Xd.1).T.definitions.all (·.name != VE.SoftNorms.exceptedName Nd)
/-- The criterion of 1.7 with i the strict twin: the default twin's exception key. -/
def decisionOnly (D : Doc) (s : String) (i j : Nat) : Option GenKey :=
  match (candidate D s i).bind (·.content), (candidate D s j).bind (·.content) with
  | some ci, some cj =>
    match forceTwins ci cj with
    | some (_, Nd) =>
      let C := correlate (one D s j).1
      if (Nd.exception.all (·.sufficient.isEmpty)) &&
          C.T.nodes.any (fun M => M.name == Nd.name && M.pred == Nd.pred) &&
          C.T.nodes.all (fun M => VE.SoftNorms.act C M != VE.SoftNorms.act C Nd || M.name == Nd.name) &&
          twinDocs D s i j ci cj Nd
      then some (.excepted Nd.name none) else none
    | none => none
  | _, _ => none
theorem decisionOnly_spec (D : Doc) (s : String) (i j : Nat) (k : GenKey) (h : decisionOnly D s i j = some k) :
  ∃ ci cj Ns Nd, (candidate D s i).bind (·.content) = some ci ∧ (candidate D s j).bind (·.content) = some cj ∧
    forceTwins ci cj = some (Ns, Nd) ∧ k = .excepted Nd.name none ∧
    (∀ e, Nd.exception = some e → e.sufficient = []) ∧
    ∀ M ∈ (correlate (one D s j).1).T.nodes,
      VE.SoftNorms.act (correlate (one D s j).1) M = VE.SoftNorms.act (correlate (one D s j).1) Nd → M.name = Nd.name := by
  unfold decisionOnly at h
  dsimp only at h
  split at h
  · rename_i ci cj hi hj
    split at h
    · rename_i Ns Nd hf
      split at h
      · rename_i hc
        cases h
        simp only [Bool.and_eq_true, Option.all_eq_true, List.isEmpty_iff, List.all_eq_true, List.any_eq_true,
          Bool.or_eq_true, bne_iff_ne, ne_eq, beq_iff_eq] at hc
        obtain ⟨⟨⟨he, _⟩, hn⟩, _⟩ := hc
        refine ⟨ci, cj, Ns, Nd, hi, hj, hf, rfl, fun e hx => he e hx, fun M hM ha => ?_⟩
        rcases hn M hM with h' | h'
        · exact absurd ha h'
        · exact h'
      · cases h
    · cases h
  · cases h

/-- Achieves, with the table of k₀ empty. -/
def AchievesQuiet (D : Doc) (s : String) (j : Nat) (k₀ : GenKey) (B : VE.Structure.{u}) (F : Tables B.Carrier)
    (q : Probe B.Carrier) (v : Bool) : Prop :=
  B.Admissible (authorEnv D) ∧
  ∃ G : Tables B.Carrier, (∀ k, owned D s j k = false → ∀ vs, G k vs ↔ F k vs) ∧ (∀ vs, ¬ G k₀ vs) ∧
    BaseAdmissibleR (one D s j).1 (withTables (one D s j).1 B G) ∧
    Observes (one D s j).1 (one D s j).2 (withTables (one D s j).1 B G) q v

/-- The acts a content regulates in a document, first occurrence kept. -/
def contentActs (C : SoftDoc) (c : Content) : List String :=
  let linePreds := fun (S : VE.Rights.SourceLine) =>
    if S.fanOut.isEmpty then (S.norm.toList ++ S.liberty.toList ++ S.recognition.toList).map (·.pred)
    else S.fanOut.map (·.2) ++ (S.liberty.toList ++ S.recognition.toList).map (·.pred)
  let ps := match c with
    | .norm N => [N.pred]
    | .right R => R.lines.flatMap linePreds
    | .rightLines _ ls => ls.flatMap linePreds
    | _ => []
  VE.SoftNorms.dedup (ps.map (VE.SoftNorms.actKey C))
/-- The two act keys of 1.7's `SeparatedByActOnly`; `none` otherwise. -/
def actOnly (D : Doc) (s : String) (i j : Nat) : Option (String × String) :=
  match (candidate D s i).bind (·.content), (candidate D s j).bind (·.content) with
  | some ci, some cj =>
    match contentActs (correlate (one D s i).1) ci, contentActs (correlate (one D s j).1) cj with
    | [a], [b] => if a == b then none else some (a, b)
    | _, _ => none
  | _, _ => none

/-! ## Proofs: the finite evaluation -/

theorem typedTuple_iff {α : Type u} [DecidableEq α] (M : VE.FiniteModel α) :
    ∀ (ss : List String) (vs : List α), typedTuple M ss vs = true ↔ VE.TupleTyped M.asStructure ss vs
  | [], [] => by simp [typedTuple, VE.TupleTyped]
  | [], _ :: _ => by simp [typedTuple, VE.TupleTyped]
  | _ :: _, [] => by simp [typedTuple, VE.TupleTyped]
  | s :: ss, v :: vs => by
    simp only [typedTuple, Bool.and_eq_true, decide_eq_true_eq, VE.TupleTyped, typedTuple_iff M ss vs]
    rfl

theorem mem_tuplesOf {α : Type u} (M : VE.FiniteModel α) :
    ∀ (ss : List String) (vs : List α), vs ∈ tuplesOf M ss ↔ VE.TupleTyped M.asStructure ss vs
  | [], [] => by simp [tuplesOf, VE.TupleTyped]
  | [], _ :: _ => by simp [tuplesOf, VE.TupleTyped]
  | s :: ss, [] => by simp [tuplesOf, VE.TupleTyped]
  | s :: ss, v :: vs => by
    simp only [tuplesOf, List.mem_flatMap, List.mem_map, VE.TupleTyped, List.cons.injEq]
    constructor
    · rintro ⟨w, hw, us, hus, rfl, rfl⟩
      exact ⟨hw, (mem_tuplesOf M ss us).mp hus⟩
    · rintro ⟨hv, hvs⟩
      exact ⟨v, hv, vs, (mem_tuplesOf M ss vs).mpr hvs, rfl, rfl⟩

theorem selectable_mem {X : RightsDoc} {k p : String} {N : SoftNode} (h : N ∈ selectable X k p) :
    N ∈ (correlate X).T.nodes ∧ N.pred = p := by
  unfold selectable at h
  split at h
  · obtain ⟨hN, hp⟩ := List.mem_filter.mp h
    refine ⟨?_, by simpa using hp⟩
    simp only [correlate, List.mem_append]
    exact Or.inl (Or.inr hN)
  · obtain ⟨RN, hRN, rfl⟩ := List.mem_map.mp h
    obtain ⟨hRN, hk⟩ := List.mem_filter.mp hRN
    simp only [Bool.and_eq_true, beq_iff_eq] at hk
    refine ⟨?_, hk.2⟩
    simp only [correlate, List.mem_append, List.mem_map]
    exact Or.inl (Or.inl ⟨RN, hRN, rfl⟩)

theorem catalaValue_eq (P N : Prop) (d v : Bool) :
    VE.Norms.catalaValue P N d = some v ↔ ¬ (P ∧ N) ∧ ((if d then ¬ N else P) ↔ v = true) := by
  classical
  unfold VE.Norms.catalaValue
  by_cases hP : P <;> by_cases hN : N <;> cases d <;> cases v <;> simp [hP, hN]

/-- The finite evaluation is the semantics, on an admissible side and a typed probe. -/
theorem observe_sound {α : Type u} [DecidableEq α] (c : Chain) (X : RightsDoc) (A : List VE.Formula)
    (h : chainWF c X = true)
    (hA : ∀ a ∈ A, a.WellFormed (envAt (soften (correlate X)) (size (soften (correlate X)))) [])
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (soften (correlate X)) 0))
    (hb : backgroundValidR X M = true) (q : Probe α) (hq : probeTyped X M q = true) (v : Bool) :
  observe X A M q = some v ↔ Observes X A M.asStructure q v := by
  have hw := chain_soft c X h
  have hv := VE.SoftNorms.softValid_of_wellFormed _ hw
  have hB : VE.Norms.BaseAdmissible (soften (correlate X)) M.asStructure :=
    (VE.Rights.baseAdmissibleR_of_valid X M valid hb).1.1
  cases q with
  | outcome p vs =>
    simp only [probeTyped, Bool.and_eq_true, List.any_eq_true, beq_iff_eq] at hq
    obtain ⟨⟨r, hr, rfl⟩, ht⟩ := hq
    have hr' : r ∈ (correlate X).T.regulated := hr
    have hfind : (correlate X).T.regulated.find? (·.name == r.name) = some r :=
      VE.SoftNorms.find_key Regulated.name _ hv.regNames r hr'
    have hs : VE.SoftNorms.sortsIn X.soft.T.regulated r.name = r.sorts := VE.SoftNorms.sortsOf_reg hv hr'
    rw [hs, typedTuple_iff] at ht
    have hc := VE.SoftNorms.conflict_canon hv _ hB hr' vs ht
    have ho := VE.SoftNorms.outcome_canon hv _ hB hr' vs ht
    rw [← VE.eval_iff_denote] at hc ho
    simp only [observe, hfind]
    constructor
    · intro hobs
      refine ⟨r, hr', rfl, ht, ?_⟩
      unfold ValueSoft
      rw [catalaValue_eq]
      split at hobs
      · cases hobs
      · rename_i hcf
        cases hobs
        exact ⟨fun hpn => hcf (hc.mpr hpn), ho.symm⟩
    · rintro ⟨r', hr'', hn, _, hval⟩
      have : r' = r := by
        have := VE.SoftNorms.find_key Regulated.name _ hv.regNames r' hr''
        rw [hn, hfind] at this
        exact (Option.some.inj this).symm
      subst this
      unfold ValueSoft at hval
      rw [catalaValue_eq] at hval
      rw [if_neg (fun hcf => hval.1 (hc.mp hcf))]
      congr 1
      have h2 := hval.2
      cases hov : (outcomeBase (soften (correlate X)) r'.name).eval M (tupleVal vs) <;> cases v
      · rfl
      · exact absurd (ho.mpr (h2.mpr rfl)) (by simp [hov])
      · exact absurd (h2.mp (ho.mp hov)) (by simp)
      · rfl
  | selects k p vs =>
    simp only [probeTyped, Bool.and_eq_true] at hq
    obtain ⟨_, ht⟩ := hq
    rw [typedTuple_iff] at ht
    have hsel : ∀ N ∈ selectable X k p,
        (circ (correlate X) (selects' (correlate X) N)).eval M (tupleVal vs) = true ↔
          SelectsSoftD (correlate X) (expand X M.asStructure) (tupleVal vs) (VE.SoftNorms.fuel (correlate X)) N := by
      intro N hN
      obtain ⟨hN', hp⟩ := selectable_mem hN
      have ht' : VE.TupleTyped M.asStructure (VE.SoftNorms.sortsOf (correlate X) N.pred) vs := by
        rw [hp]; exact ht
      rw [VE.eval_iff_denote]
      unfold circ
      rw [VE.SoftNorms.circ_canon hv _ hB _ _ (hv.selTyped N hN') _ (VE.Norms.tupleVal_typed _ _ vs ht')]
      exact VE.SoftNorms.selectsPrime_denote _ _ _ N
    simp only [observe, Observes, Option.some.injEq]
    constructor
    · rintro rfl
      refine ⟨ht, ?_⟩
      rw [List.any_eq_true]
      exact ⟨fun ⟨N, hN, hs⟩ => ⟨N, hN, (hsel N hN).mpr hs⟩, fun ⟨N, hN, hs⟩ => ⟨N, hN, (hsel N hN).mp hs⟩⟩
    · rintro ⟨_, hiff⟩
      cases hany : (selectable X k p).any (fun N =>
          (circ (correlate X) (selects' (correlate X) N)).eval M (tupleVal vs))
      · cases v
        · rfl
        · exfalso
          obtain ⟨N, hN, hs⟩ := hiff.mpr rfl
          have := (hsel N hN).mpr hs
          rw [List.any_eq_false] at hany
          exact hany N hN (by simp [this])
      · rw [List.any_eq_true] at hany
        obtain ⟨N, hN, hs⟩ := hany
        exact (hiff.mp ⟨N, hN, (hsel N hN).mp hs⟩).symm
  | holds =>
    have hh : ∀ a ∈ A, (circ (correlate X) a).eval M [] = true ↔ a.denote (expand X M.asStructure) [] := by
      intro a ha
      rw [VE.eval_iff_denote]
      exact VE.SoftNorms.circ_canon hv _ hB a [] (hA a ha) [] (VE.typed_empty _)
    simp only [observe, Observes, Option.some.injEq]
    constructor
    · rintro rfl
      rw [List.all_eq_true]
      exact ⟨fun h a ha => (hh a ha).mpr (h a ha), fun h a ha => (hh a ha).mp (h a ha)⟩
    · intro hiff
      cases hall : A.all (fun a => (circ (correlate X) a).eval M [])
      · cases v
        · rfl
        · exfalso
          have h' := hiff.mpr rfl
          rw [List.all_eq_false] at hall
          obtain ⟨a, ha, hf⟩ := hall
          exact hf ((hh a ha).mpr (h' a ha))
      · rw [List.all_eq_true] at hall
        exact (hiff.mp (fun a ha => (hh a ha).mp (hall a ha))).symm

/-! ## Proofs: the candidate's document keeps the frame -/

theorem buildStep_soft (keep : String → Bool) (pick : ReadingSet → Option Candidate)
    (acc : RightsDoc × List VE.Formula) (it : Item) :
    ∃ extra, (buildStep keep pick acc it).1.soft =
      { acc.1.soft with T := { acc.1.soft.T with nodes := acc.1.soft.T.nodes ++ extra } } := by
  have hp : ∀ (X : RightsDoc) c cs, ∃ extra, (place X c cs).soft =
      { X.soft with T := { X.soft.T with nodes := X.soft.T.nodes ++ extra } } := by
    intro X c cs
    cases c with
    | norm N => exact ⟨[N], rfl⟩
    | _ => exact ⟨[], by simp [place]⟩
  cases it with
  | fixed u c cs =>
    simp only [buildStep]
    split
    · exact hp _ c cs
    · exact ⟨[], by simp⟩
  | bar u b =>
    simp only [buildStep]
    split
    · exact ⟨[], by simp⟩
    · exact ⟨[], by simp⟩
  | set R =>
    simp only [buildStep]
    split
    · exact hp _ _ _
    · exact ⟨[], by simp⟩

theorem build_soft (D : Doc) (keep : String → Bool) (pick : ReadingSet → Option Candidate) :
    ∃ extra, (build D keep pick).1.soft =
      { D.frame.soft with T := { D.frame.soft.T with nodes := D.frame.soft.T.nodes ++ extra } } := by
  rw [build_eq]
  suffices ∀ (l : List Item) (acc : RightsDoc × List VE.Formula), ∃ extra,
      (l.foldl (buildStep keep pick) acc).1.soft =
        { acc.1.soft with T := { acc.1.soft.T with nodes := acc.1.soft.T.nodes ++ extra } } from this _ _
  intro l
  induction l with
  | nil => intro acc; exact ⟨[], by simp⟩
  | cons it l ih =>
    intro acc
    obtain ⟨e1, h1⟩ := buildStep_soft keep pick acc it
    obtain ⟨e2, h2⟩ := ih (buildStep keep pick acc it)
    refine ⟨e1 ++ e2, ?_⟩
    simp only [List.foldl_cons, h2, h1, List.append_assoc]

/-- The facts of the frame a candidate's document keeps. -/
structure KeepsFrame (D : Doc) (X : RightsDoc) : Prop where
  E : X.soft.E = D.frame.soft.E
  regulated : X.soft.T.regulated = D.frame.soft.T.regulated
  definitions : X.soft.T.definitions = D.frame.soft.T.definitions
  nodes : ∀ N ∈ D.frame.soft.T.nodes, N ∈ X.soft.T.nodes

theorem keepsFrame_build (D : Doc) (keep : String → Bool) (pick : ReadingSet → Option Candidate) :
    KeepsFrame D (build D keep pick).1 := by
  obtain ⟨e, h⟩ := build_soft D keep pick
  refine ⟨by rw [h], by rw [h], by rw [h], fun N hN => ?_⟩
  rw [h]
  exact List.mem_append_left _ hN

theorem keepsFrame_one (D : Doc) (s : String) (i : Nat) : KeepsFrame D (one D s i).1 := keepsFrame_build _ _ _

/-! ## Proofs: the layer symbols of a candidate's document are hidden in the author's vocabulary -/

theorem names_nodup_of_order {ns : List VE.Route.DepNode} {o : List String}
    (h : VE.Route.dependencyOrder ns = .ok o) : (VE.Route.nodeNames ns).Nodup := by
  unfold VE.Route.dependencyOrder at h
  split at h
  · cases h
  · rename_i hf
    rw [List.find?_eq_none] at hf
    rw [List.nodup_iff_count]
    intro a
    by_cases ha : a ∈ VE.Route.nodeNames ns
    · have := hf a ha; simp at this; omega
    · have : List.count a (VE.Route.nodeNames ns) = 0 := List.count_eq_zero.mpr ha
      omega

theorem lookupSym_name {T : VE.Norms.Tree} {n : String} {q : VE.Norms.Sym} (h : VE.Norms.lookupSym T n = some q) :
    q.name = n := by
  unfold VE.Norms.lookupSym at h
  split at h
  · rename_i r hf
    cases h
    simpa [VE.Norms.Sym.name] using List.find?_some hf
  · obtain ⟨d, hd, rfl⟩ := Option.map_eq_some_iff.mp h
    simpa [VE.Norms.Sym.name] using List.find?_some hd

theorem nodeNames_stratum (T : VE.Norms.Tree) :
    VE.Route.nodeNames (VE.Norms.stratumNodes T) = T.regulated.map (·.name) ++ T.definitions.map (·.name) := by
  simp [VE.Route.nodeNames, VE.Norms.stratumNodes, Function.comp_def]

theorem lookupSym_some {T : VE.Norms.Tree} {x : String}
    (h : x ∈ T.regulated.map (·.name) ++ T.definitions.map (·.name)) : ∃ q, VE.Norms.lookupSym T x = some q := by
  unfold VE.Norms.lookupSym
  split
  · exact ⟨_, rfl⟩
  · rename_i hn
    rcases List.mem_append.mp h with h | h
    · obtain ⟨r, hr, rfl⟩ := List.mem_map.mp h
      exact absurd (List.find?_eq_none.mp hn r hr) (by simp)
    · obtain ⟨d, hd, rfl⟩ := List.mem_map.mp h
      cases hf : T.definitions.find? (·.name == d.name) with
      | none => exact absurd (List.find?_eq_none.mp hf d hd) (by simp)
      | some d' => exact ⟨_, rfl⟩

theorem layer_sub (Tf T' : VE.Norms.Tree) (hr : Tf.regulated = T'.regulated) (hd : Tf.definitions = T'.definitions)
    (hm : ∀ N ∈ Tf.nodes, ∃ N' ∈ T'.nodes, N'.pred = N.pred ∧ ∀ φ ∈ N.guard :: N.carveOuts, φ ∈ N'.guard :: N'.carveOuts) :
    ∀ x ∈ VE.Norms.layerNames T', x ∈ VE.Norms.layerNames Tf := by
  intro x hx
  obtain ⟨q, hq, rfl⟩ := List.mem_map.mp hx
  obtain ⟨y, hy, hl⟩ := List.mem_filterMap.mp hq
  have hqy := lookupSym_name hl
  unfold VE.Norms.order at hy
  split at hy
  · rename_i o' ho'
    obtain ⟨_, hmem', _, hac'⟩ := VE.Route.dag_acyclic _ _ ho'
    have hyn : y ∈ VE.Route.nodeNames (VE.Norms.stratumNodes T') := (hmem' y).mp hy
    have hnames : VE.Route.nodeNames (VE.Norms.stratumNodes Tf) = VE.Route.nodeNames (VE.Norms.stratumNodes T') := by
      rw [nodeNames_stratum, nodeNames_stratum, hr, hd]
    -- every edge of the frame's stratum graph is an edge of the elaborated one
    have hedge : ∀ a b, VE.Route.DepEdge (VE.Norms.stratumNodes Tf) a b →
        VE.Route.DepEdge (VE.Norms.stratumNodes T') a b := by
      rintro a b ⟨n, hn, rfl, hb⟩
      simp only [VE.Route.deps, List.mem_filter, hnames] at hb
      obtain ⟨hbm, hbc⟩ := hb
      simp only [VE.Norms.stratumNodes, List.mem_append, List.mem_map] at hn
      rcases hn with ⟨r, hrm, rfl⟩ | ⟨d, hdm, rfl⟩
      · refine ⟨⟨r.name, ((VE.Norms.Sym.reg r).formulas T').flatMap VE.Norms.preds⟩,
          by simp only [VE.Norms.stratumNodes, List.mem_append, List.mem_map]; exact Or.inl ⟨r, hr ▸ hrm, rfl⟩,
          rfl, ?_⟩
        simp only [VE.Route.deps, List.mem_filter, hbc, and_true]
        simp only [VE.Norms.Sym.formulas, List.mem_flatMap, VE.Norms.rulesOn, List.mem_filter, beq_iff_eq] at hbm ⊢
        obtain ⟨φ, ⟨N, ⟨hN, hp⟩, hφ⟩, hq⟩ := hbm
        obtain ⟨N', hN', hp', hφ'⟩ := hm N hN
        exact ⟨φ, ⟨N', ⟨hN', hp'.trans hp⟩, hφ' φ hφ⟩, hq⟩
      · refine ⟨⟨d.name, VE.Norms.preds d.body⟩,
          by simp only [VE.Norms.stratumNodes, List.mem_append, List.mem_map]; exact Or.inr ⟨d, hd ▸ hdm, rfl⟩,
          rfl, ?_⟩
        simp only [VE.Route.deps, List.mem_filter, hbc, and_true]
        exact hbm
    have hpath : ∀ a b, VE.Route.DepPath (VE.Norms.stratumNodes Tf) a b →
        VE.Route.DepPath (VE.Norms.stratumNodes T') a b := by
      intro a b h
      induction h with
      | edge he => exact .edge (hedge _ _ he)
      | trans _ _ ih₁ ih₂ => exact .trans ih₁ ih₂
    have hnd : (VE.Route.nodeNames (VE.Norms.stratumNodes Tf)).Nodup := hnames ▸ names_nodup_of_order ho'
    obtain ⟨of, hof⟩ := VE.NormDefaults.dependencyOrder_ok _ hnd (fun a h => hac' a (hpath a a h))
    obtain ⟨_, hmemf, _, _⟩ := VE.Route.dag_acyclic _ _ hof
    have hyf : y ∈ VE.Route.nodeNames (VE.Norms.stratumNodes Tf) := hnames ▸ hyn
    obtain ⟨q', hq'⟩ := lookupSym_some (by rw [← nodeNames_stratum]; exact hyf)
    refine List.mem_map.mpr ⟨q', List.mem_filterMap.mpr ⟨y, ?_, hq'⟩, ?_⟩
    · unfold VE.Norms.order; rw [hof]; exact (hmemf y).mpr hyf
    · rw [lookupSym_name hq', hqy]
  · cases hy

/-- The layer symbols of a candidate's elaborated document are hidden in the author's base vocabulary. -/
theorem layerNames_hidden (D : Doc) (X : RightsDoc) (hX : KeepsFrame D X) :
    ∀ x ∈ VE.Norms.layerNames (soften (correlate X)).T, x ∈ VE.Norms.layerNames D.frame.soft.base.T := by
  apply layer_sub
  · show D.frame.soft.T.regulated = X.soft.T.regulated; rw [hX.regulated]
  · show D.frame.soft.T.definitions = X.soft.T.definitions; rw [hX.definitions]
  · intro N hN
    obtain ⟨F, hF, rfl⟩ := List.mem_map.mp hN
    refine ⟨VE.SoftNorms.primeNode (correlate X) F, ?_, rfl, ?_⟩
    · show _ ∈ (correlate X).T.nodes.map (VE.SoftNorms.primeNode (correlate X))
      apply List.mem_map_of_mem
      simp only [correlate, List.mem_append]
      exact Or.inl (Or.inr (hX.nodes F hF))
    · intro φ hφ
      simp only [VE.SoftNorms.primeNode, List.mem_cons, List.mem_append] at hφ ⊢
      rcases hφ with h | h
      · exact Or.inl h
      · exact Or.inr (Or.inl h)

/-! ## Proofs: tables -/

theorem tableOf_cons {α : Type u} (t : GenKey × List (List α)) (T : List (GenKey × List (List α))) (k : GenKey) :
    tableOf (t :: T) k = if t.1 = k then t.2 else tableOf T k := by
  by_cases h : t.1 = k <;> simp [tableOf, h]

theorem tableOf_nil {α : Type u} (k : GenKey) : tableOf ([] : List (GenKey × List (List α))) k = [] := rfl

theorem mem_tableOf {α : Type u} : ∀ {T : List (GenKey × List (List α))} {k : GenKey} {vs : List α},
    vs ∈ tableOf T k → tablesOf T k vs
  | [], _, _, h => by simp [tableOf_nil] at h
  | t :: T, k, vs, h => by
    rw [tableOf_cons] at h
    split at h
    · exact ⟨t, List.mem_cons_self, by assumption, h⟩
    · obtain ⟨t', ht', he, hv⟩ := mem_tableOf h
      exact ⟨t', List.mem_cons_of_mem _ ht', he, hv⟩

theorem mem_tableOf_iff {α : Type u} : ∀ {T : List (GenKey × List (List α))}, (T.map (·.1)).Nodup →
    ∀ (k : GenKey) (vs : List α), vs ∈ tableOf T k ↔ tablesOf T k vs
  | [], _, k, vs => by simp [tableOf_nil, tablesOf]
  | t :: T, hn, k, vs => by
    refine ⟨mem_tableOf, ?_⟩
    rintro ⟨t', ht', he, hv⟩
    rw [List.map_cons, List.nodup_cons] at hn
    rw [tableOf_cons]
    rcases List.mem_cons.mp ht' with rfl | ht'
    · rw [if_pos he]; exact hv
    · by_cases h : t.1 = k
      · exfalso; exact hn.1 (h ▸ he ▸ List.mem_map_of_mem ht')
      · rw [if_neg h]; exact (mem_tableOf_iff hn.2 k vs).mpr ⟨t', ht', he, hv⟩

theorem tableOf_filter {α : Type u} (P : GenKey × List (List α) → Bool) (k : GenKey)
    (hP : ∀ t : GenKey × List (List α), t.1 = k → P t = true) :
    ∀ T : List (GenKey × List (List α)), tableOf (T.filter P) k = tableOf T k
  | [] => rfl
  | t :: T => by
    by_cases h : t.1 = k
    · rw [List.filter_cons_of_pos (hP t h), tableOf_cons, tableOf_cons, if_pos h, if_pos h]
    · rw [tableOf_cons, if_neg h]
      by_cases hp : P t = true
      · rw [List.filter_cons_of_pos hp, tableOf_cons, if_neg h, tableOf_filter P k hP T]
      · rw [List.filter_cons_of_neg hp, tableOf_filter P k hP T]

theorem tableOf_append_of_not {α : Type u} (k : GenKey) :
    ∀ (A B : List (GenKey × List (List α))), (∀ t ∈ A, t.1 ≠ k) → tableOf (A ++ B) k = tableOf B k
  | [], _, _ => rfl
  | t :: A, B, h => by
    rw [List.cons_append, tableOf_cons, if_neg (h t List.mem_cons_self)]
    exact tableOf_append_of_not k A B (fun t' ht' => h t' (List.mem_cons_of_mem _ ht'))

theorem tableOf_none {α : Type u} (k : GenKey) :
    ∀ (A : List (GenKey × List (List α))), (∀ t ∈ A, t.1 ≠ k) → tableOf A k = []
  | A, h => by simpa using tableOf_append_of_not k A [] h

theorem tablesFor_generated {α : Type u} (D : Doc) (s : String) (i : Nat) (T : List (GenKey × List (List α)))
    (k : GenKey) (hk : (genKeys (one D s i).1).any (·.1 == k) = true) :
    tableOf (tablesFor D s i T) k = tableOf T k :=
  tableOf_filter _ k (fun t ht => by rw [ht]; exact hk) T

theorem find_name {X : RightsDoc} {p : String} {g : GenKey × String × List String}
    (h : (genKeys X).find? (·.2.1 == p) = some g) : g ∈ genKeys X ∧ g.2.1 = p :=
  ⟨List.mem_of_find?_eq_some h, by simpa using List.find?_some h⟩

theorem keyOfName_of_find {X : RightsDoc} {p : String} {g : GenKey × String × List String}
    (h : (genKeys X).find? (·.2.1 == p) = some g) : keyOfName X p = some g.1 := by
  simp [keyOfName, h]

/-- The finite model of a side is the completion: the relations agree name by name. -/
theorem tablesModel_eq {α : Type u} (X : RightsDoc) (M : VE.FiniteModel α) (T : List (GenKey × List (List α)))
    (G : Tables α) (hG : ∀ g ∈ genKeys X, ∀ vs, vs ∈ tableOf T g.1 ↔ G g.1 vs) :
    (tablesModel X M T).asStructure = withTables X M.asStructure G := by
  simp only [VE.FiniteModel.asStructure, tablesModel, withTables]
  congr
  funext p vs
  split
  · rename_i g hg
    exact propext (hG g (find_name hg).1 vs)
  · rfl

theorem observes_rel {X : RightsDoc} {A : List VE.Formula} {α : Type u} {d : String → α → Prop}
    {c : String → Option α} {R1 R2 : String → List α → Prop} (h : R1 = R2) (q : Probe α) (v : Bool)
    (ho : Observes X A ⟨α, d, c, R1⟩ q v) : Observes X A ⟨α, d, c, R2⟩ q v := by
  subst h; exact ho

theorem genKeys_find_none {X : RightsDoc} {p : String} (h : (genKeys X).find? (·.2.1 == p) = none) :
    (∀ d ∈ VE.SoftNorms.decisions (correlate X), d.1 ≠ p) ∧ (∀ d ∈ VE.Rights.genDecls X, d.1 ≠ p) := by
  have hn := genKeys_names X
  have hall : ∀ d ∈ VE.SoftNorms.decisions (correlate X) ++ VE.Rights.genDecls X, d.1 ≠ p := by
    intro d hd
    rw [← hn] at hd
    obtain ⟨g, hg, rfl⟩ := List.mem_map.mp hd
    have := List.find?_eq_none.mp h g hg
    simpa using this
  exact ⟨fun d hd => hall d (List.mem_append_left _ hd), fun d hd => hall d (List.mem_append_right _ hd)⟩

/-- Outside the generated names, the elaborated base vocabulary of a candidate's document is the author's. -/
theorem envAt_author (D : Doc) (X : RightsDoc) (hX : KeepsFrame D X) {p : String} {ss : List String}
    (hg : (genKeys X).find? (·.2.1 == p) = none) (ha : (authorEnv D).predicates p = some ss) :
    (envAt (soften (correlate X)) 0).predicates p = some ss := by
  obtain ⟨hd, hr⟩ := genKeys_find_none hg
  simp only [authorEnv, envAt, VE.Norms.hide, List.drop_zero] at ha ⊢
  split at ha
  · cases ha
  · rename_i hnl
    rw [if_neg (fun hl => hnl (layerNames_hidden D X hX p hl))]
    show (VE.SoftNorms.envPrime (correlate X)).predicates p = some ss
    simp only [VE.SoftNorms.envPrime]
    rw [List.find?_eq_none.mpr (fun d hd' => by simpa using hd d hd')]
    show (VE.Rights.envR X).predicates p = some ss
    simp only [VE.Rights.envR]
    rw [List.find?_eq_none.mpr (fun d hd' => by simpa using hr d hd'), hX.E]
    exact ha

theorem envAt_constants (D : Doc) (X : RightsDoc) (hX : KeepsFrame D X) :
    (envAt (soften (correlate X)) 0).constants = (authorEnv D).constants := by
  show X.soft.E.constants = D.frame.soft.E.constants
  rw [hX.E]

theorem typedTuple_domains {α : Type u} [DecidableEq α] {M M' : VE.FiniteModel α} (h : M.domains = M'.domains) :
    ∀ (ss : List String) (vs : List α), typedTuple M ss vs = typedTuple M' ss vs
  | [], [] => rfl
  | [], _ :: _ => rfl
  | _ :: _, [] => rfl
  | s :: ss, v :: vs => by simp only [typedTuple, h, typedTuple_domains h ss vs]

theorem tupleTyped_tablesModel {α : Type u} [DecidableEq α] (X : RightsDoc) (M : VE.FiniteModel α)
    (T : List (GenKey × List (List α))) (ss : List String) (vs : List α) :
    VE.TupleTyped (tablesModel X M T).asStructure ss vs ↔ VE.TupleTyped M.asStructure ss vs := by
  rw [← typedTuple_iff, ← typedTuple_iff, typedTuple_domains (M := tablesModel X M T) (M' := M) rfl]

/-- A side's finite model is valid over its elaborated base vocabulary: the base is valid over the author's,
    and the tables are typed. -/
theorem valid_tablesModel {α : Type u} [DecidableEq α] (D : Doc) (X : RightsDoc) (hX : KeepsFrame D X)
    (M : VE.FiniteModel α) (valid : M.Valid (authorEnv D)) (T : List (GenKey × List (List α)))
    (ht : tablesTyped X M T = true) : (tablesModel X M T).Valid (envAt (soften (correlate X)) 0) := by
  refine ⟨fun c s hc => ?_, fun p vs hvs => ?_⟩
  · rw [envAt_constants D X hX] at hc
    exact valid.1 c s hc
  · change vs ∈ (tablesModel X M T).relations p at hvs
    simp only [tablesModel] at hvs
    split at hvs
    · rename_i g hg
      obtain ⟨hgm, hgp⟩ := find_name hg
      obtain ⟨t, htT, htk, hvt⟩ := mem_tableOf hvs
      simp only [tablesTyped, List.all_eq_true, Bool.and_eq_true, Bool.or_eq_true, bne_iff_ne, ne_eq] at ht
      have := (ht t htT).2 vs hvt g hgm
      rw [hgp, keyOfName_of_find hg, htk] at this
      simp only [not_true_eq_false, false_or] at this
      unfold declaredTyped at this
      split at this
      · rename_i ss hss
        exact ⟨ss, hss, (tupleTyped_tablesModel X M T ss vs).mpr ((typedTuple_iff M ss vs).mp this)⟩
      · cases this
    · rename_i hg
      obtain ⟨ss, hss, hty⟩ := valid.2 p vs hvs
      exact ⟨ss, envAt_author D X hX hg hss, (tupleTyped_tablesModel X M T ss vs).mpr hty⟩

/-! ## Proofs: `separates_sound` -/

theorem mem_uniq {β : Type u} [BEq β] [LawfulBEq β] {x : β} : ∀ {l : List β}, x ∈ uniq l ↔ x ∈ l
  | [] => by simp [uniq]
  | y :: ys => by
    simp only [uniq]
    split
    · rename_i h
      rw [mem_uniq, List.mem_cons]
      refine ⟨Or.inr, ?_⟩
      rintro (rfl | h')
      · exact mem_uniq.mp (List.contains_iff_mem.mp h)
      · exact h'
    · simp only [List.mem_cons, mem_uniq]

theorem filter_mem_subsets {β : Type u} (P : β → Bool) : ∀ (L : List β), L.filter P ∈ subsets L
  | [] => by simp [subsets]
  | x :: xs => by
    simp only [subsets, List.mem_append, List.mem_map]
    by_cases h : P x = true
    · rw [List.filter_cons_of_pos h]; exact Or.inl ⟨_, filter_mem_subsets P xs, rfl⟩
    · rw [List.filter_cons_of_neg h]; exact Or.inr (filter_mem_subsets P xs)

theorem mem_assignments_foldr {α : Type u} (f : GenKey → List (List α)) (P : GenKey → List α → Bool) :
    ∀ ks : List GenKey, ks.map (fun k => (k, (f k).filter (P k))) ∈
      ks.foldr (fun k acc => (subsets (f k)).flatMap (fun tbl => acc.map ((k, tbl) :: ·))) [[]]
  | [] => by simp
  | k :: ks => by
    simp only [List.map_cons, List.foldr_cons, List.mem_flatMap, List.mem_map]
    exact ⟨_, filter_mem_subsets (P k) (f k), _, mem_assignments_foldr f P ks, rfl⟩

theorem tableOf_map_keys {α : Type u} (f : GenKey → List (List α)) (k : GenKey) :
    ∀ ks : List GenKey, tableOf (ks.map (fun k' => (k', f k'))) k = if k ∈ ks then f k else []
  | [] => by simp [tableOf_nil]
  | k' :: ks => by
    rw [List.map_cons, tableOf_cons, tableOf_map_keys f k ks]
    by_cases h : k' = k
    · subst h; simp
    · simp only [if_neg h, List.mem_cons]
      by_cases hk : k ∈ ks
      · simp [hk]
      · simp [hk, Ne.symm h]

theorem tableOf_append_right_not {α : Type u} (k : GenKey) :
    ∀ (A B : List (GenKey × List (List α))), (∀ t ∈ B, t.1 ≠ k) → tableOf (A ++ B) k = tableOf A k
  | [], B, h => by rw [List.nil_append, tableOf_none k B h, tableOf_nil]
  | t :: A, B, h => by
    rw [List.cons_append, tableOf_cons, tableOf_cons, tableOf_append_right_not k A B h]

theorem withTables_domain {X : RightsDoc} {S : VE.Structure.{u}} {G : Tables S.Carrier} :
    (withTables X S G).domain = S.domain := rfl

theorem tupleTyped_withTables {X : RightsDoc} {S : VE.Structure.{u}} {G : Tables S.Carrier} :
    ∀ (ss : List String) (vs : List S.Carrier), VE.TupleTyped (withTables X S G) ss vs ↔ VE.TupleTyped S ss vs
  | [], [] => by simp only [VE.TupleTyped]
  | [], _ :: _ => by simp only [VE.TupleTyped]
  | _ :: _, [] => by simp only [VE.TupleTyped]
  | s :: ss, v :: vs => by
    simp only [VE.TupleTyped]
    exact and_congr (by rw [withTables_domain]) (tupleTyped_withTables ss vs)

theorem backgroundValidR_of_admissible {α : Type u} [DecidableEq α] (X : RightsDoc) (M : VE.FiniteModel α)
    (h : BaseAdmissibleR X M.asStructure) : backgroundValidR X M = true := by
  obtain ⟨⟨⟨_, hbb⟩, hsoft⟩, hlim⟩ := h
  simp only [backgroundValidR, VE.SoftNorms.backgroundValid', VE.Norms.backgroundValid, Bool.and_eq_true,
    List.all_eq_true]
  exact ⟨⟨fun a ha => (VE.eval_iff_denote M [] a).mpr (hbb a ha), fun a ha => (VE.eval_iff_denote M [] a).mpr
    (hsoft a ha)⟩, fun a ha => (VE.eval_iff_denote M [] a).mpr (hlim a ha)⟩

theorem probeTyped_congr {α : Type u} [DecidableEq α] {X Y : RightsDoc} {M M' : VE.FiniteModel α}
    (hr : X.soft.T.regulated = Y.soft.T.regulated) (hd : M.domains = M'.domains) (q : Probe α) :
    probeTyped X M q = probeTyped Y M' q := by
  cases q <;> simp only [probeTyped, hr, typedTuple_domains hd]

theorem sideWF_one (D : Doc) (hD : WellFormedDoc D = true) {s : String} {i : Nat}
    (hi : (candidate D s i).bind (·.content) ≠ none) : sideWF D (one D s i) = true := by
  unfold candidate at hi
  cases hR : D.sets.find? (·.id == s) with
  | none => rw [hR] at hi; exact absurd rfl hi
  | some R =>
    rw [hR] at hi
    have hRm := List.mem_of_find?_eq_some hR
    have hRs : R.id = s := by simpa using List.find?_some hR
    simp only [Option.bind_some] at hi
    cases ha : R.candidates[i]? with
    | none => rw [ha] at hi; exact absurd rfl hi
    | some a =>
      rw [ha] at hi
      have hlt : i < R.candidates.length := (List.getElem?_eq_some_iff.mp ha).1
      simp only [WellFormedDoc, Bool.and_eq_true, List.all_eq_true, List.mem_range, Bool.or_eq_true] at hD
      rcases hD.2 R hRm i hlt with h | h
      · rw [ha] at h
        simp only [Option.bind_some, Option.isNone_iff_eq_none] at h
        exact absurd h hi
      · rw [← hRs]; exact h

/-- The relations of a side's finite model are those of its completion. -/
theorem tablesModel_rel {α : Type u} (X : RightsDoc) (M : VE.FiniteModel α) (T : List (GenKey × List (List α)))
    (G : Tables α)
    (hG : ∀ p g, (genKeys X).find? (·.2.1 == p) = some g → ∀ vs, vs ∈ tableOf T g.1 ↔ G g.1 vs) :
    (fun p vs => vs ∈ (tablesModel X M T).relations p) =
      (fun p vs => match (genKeys X).find? (·.2.1 == p) with
        | some g => G g.1 vs
        | none => vs ∈ M.relations p) := by
  funext p vs
  simp only [tablesModel]
  split
  · rename_i g hg
    exact propext (hG p g hg vs)
  · rfl

/-- The witness side of `separates_sound`. -/
theorem separates_witness {α : Type u} [DecidableEq α] (D : Doc) (hD : WellFormedDoc D = true) (s : String)
    (i : Nat) (hi : (candidate D s i).bind (·.content) ≠ none) (σ : Situation α) (valid : σ.base.Valid (authorEnv D))
    (hnd : ((σ.fixed ++ σ.decisions).map (·.1)).Nodup)
    (hdec : ∀ t ∈ σ.decisions, owned D s i t.1 = true)
    (hpt : probeTyped (one D s i).1 σ.base σ.probe = true)
    (hsvi : sideValid D s i σ.base (tablesFor D s i (σ.fixed ++ σ.decisions)) = true)
    (hvi : sideValue D s i σ.base (tablesFor D s i (σ.fixed ++ σ.decisions)) σ.probe = some σ.value) :
    Achieves D s i σ.base.asStructure (tablesOf σ.fixed) σ.probe σ.value := by
  have hwi := sideWF_one D hD hi
  simp only [sideWF, Bool.and_eq_true, List.all_eq_true] at hwi
  have hAi : ∀ a ∈ (one D s i).2, a.WellFormed (envAt (soften (correlate (one D s i).1))
      (size (soften (correlate (one D s i).1)))) [] :=
    fun a ha => (VE.check_iff_wellFormed _ _ _).mp (hwi.2 a ha)
  simp only [sideValid, Bool.and_eq_true] at hsvi
  obtain ⟨httT, hbgi⟩ := hsvi
  have hvalT := valid_tablesModel D (one D s i).1 (keepsFrame_one D s i) σ.base valid _ httT
  have hGi : ∀ p g, (genKeys (one D s i).1).find? (·.2.1 == p) = some g → ∀ vs,
      vs ∈ tableOf (tablesFor D s i (σ.fixed ++ σ.decisions)) g.1 ↔ tablesOf (σ.fixed ++ σ.decisions) g.1 vs := by
    intro p g hg vs
    have hk : (genKeys (one D s i).1).any (·.1 == g.1) = true := List.any_eq_true.mpr ⟨g, (find_name hg).1, by simp⟩
    rw [tablesFor_generated D s i _ g.1 hk]
    exact mem_tableOf_iff hnd g.1 vs
  have hreli := tablesModel_rel (one D s i).1 σ.base _ _ hGi
  have hBi := VE.Rights.baseAdmissibleR_of_valid (one D s i).1 _ hvalT hbgi
  have hpti : probeTyped (one D s i).1 (tablesModel (one D s i).1 σ.base
      (tablesFor D s i (σ.fixed ++ σ.decisions))) σ.probe = true := by
    exact (probeTyped_congr (X := (one D s i).1) (Y := (one D s i).1)
      (M := tablesModel (one D s i).1 σ.base (tablesFor D s i (σ.fixed ++ σ.decisions))) (M' := σ.base)
      rfl rfl σ.probe).trans hpt
  have hobsi := (observe_sound D.chain (one D s i).1 (one D s i).2 hwi.1 hAi _ hvalT hbgi σ.probe hpti
    σ.value).mp hvi
  refine ⟨valid, tablesOf (σ.fixed ++ σ.decisions), ?_, ?_, observes_rel hreli σ.probe σ.value hobsi⟩
  · intro k hk vs
    simp only [tablesOf, List.mem_append]
    constructor
    · rintro ⟨t, ht | ht, rfl, hv⟩
      · exact ⟨t, ht, rfl, hv⟩
      · rw [hdec t ht] at hk; cases hk
    · rintro ⟨t, ht, rfl, hv⟩; exact ⟨t, Or.inl ht, rfl, hv⟩
  · have e : (tablesModel (one D s i).1 σ.base (tablesFor D s i (σ.fixed ++ σ.decisions))).asStructure =
        withTables (one D s i).1 σ.base.asStructure (tablesOf (σ.fixed ++ σ.decisions)) := by
      simp only [VE.FiniteModel.asStructure, withTables]
      congr 1
    rw [← e]; exact hBi

/-- The other side of `separates_sound`: a completion of `j` with the recorded value is one of the enumerated
    assignments. -/
theorem separates_other {α : Type u} [DecidableEq α] (D : Doc) (hD : WellFormedDoc D = true) (s : String)
    (i j : Nat) (hj : (candidate D s j).bind (·.content) ≠ none) (σ : Situation α)
    (hndf : (σ.fixed.map (·.1)).Nodup)
    (hfx : ∀ t ∈ σ.fixed, owned D s j t.1 = false)
    (htyj : tablesTyped (one D s j).1 σ.base (tablesFor D s j σ.fixed) = true)
    (hpt : probeTyped (one D s i).1 σ.base σ.probe = true)
    (hall : ∀ G ∈ assignments D s j σ.base, (sideValid D s j σ.base (tablesFor D s j σ.fixed ++ G) &&
          sideValue D s j σ.base (tablesFor D s j σ.fixed ++ G) σ.probe == some σ.value) = false) :
    ¬ Achieves D s j σ.base.asStructure (tablesOf σ.fixed) σ.probe σ.value := by
  classical
  rintro ⟨_, G, hagree, hBA, hObs⟩
  have hadm : (withTables (one D s j).1 σ.base.asStructure G).Admissible
      (envAt (soften (correlate (one D s j).1)) 0) := hBA.1.1.1
  have htyp : ∀ p g, (genKeys (one D s j).1).find? (·.2.1 == p) = some g → ∀ vs, G g.1 vs →
      ∃ ss, (envAt (soften (correlate (one D s j).1)) 0).predicates p = some ss ∧
        VE.TupleTyped σ.base.asStructure ss vs := by
    intro p g hg vs hv
    have hrel : (withTables (one D s j).1 σ.base.asStructure G).relation p vs := by
      simp only [withTables, hg]; exact hv
    obtain ⟨ss, hss, ht⟩ := hadm.2 p vs hrel
    exact ⟨ss, hss, (tupleTyped_withTables ss vs).mp ht⟩
  let G' : List (GenKey × List (List α)) := (ownedKeys D s j).map (fun k =>
    (k, (keyTuples (one D s j).1 σ.base k).filter (fun vs => decide (G k vs))))
  have hG'mem : G' ∈ assignments D s j σ.base := mem_assignments_foldr _ _ _
  have hGj : ∀ p g, (genKeys (one D s j).1).find? (·.2.1 == p) = some g → ∀ vs,
      vs ∈ tableOf (tablesFor D s j σ.fixed ++ G') g.1 ↔ G g.1 vs := by
    intro p g hg vs
    have hgm := find_name hg
    have hk : (genKeys (one D s j).1).any (·.1 == g.1) = true := List.any_eq_true.mpr ⟨g, hgm.1, by simp⟩
    by_cases ho : owned D s j g.1 = true
    · rw [tableOf_append_of_not g.1 _ _ (fun t ht e => by
          have := hfx t (List.mem_filter.mp ht).1; rw [e, ho] at this; cases this)]
      show vs ∈ tableOf ((ownedKeys D s j).map (fun k =>
        (k, (keyTuples (one D s j).1 σ.base k).filter (fun vs => decide (G k vs))))) g.1 ↔ G g.1 vs
      rw [tableOf_map_keys (fun k => (keyTuples (one D s j).1 σ.base k).filter (fun vs => decide (G k vs))) g.1]
      have hmem : g.1 ∈ ownedKeys D s j := List.mem_filter.mpr ⟨List.mem_map_of_mem hgm.1, ho⟩
      rw [if_pos hmem, List.mem_filter, decide_eq_true_eq]
      refine ⟨fun h => h.2, fun hv => ⟨?_, hv⟩⟩
      obtain ⟨ss, hss, ht⟩ := htyp p g hg vs hv
      rw [keyTuples, mem_uniq, List.mem_flatMap]
      refine ⟨g, hgm.1, ?_⟩
      rw [hgm.2, keyOfName_of_find hg]
      simp only [beq_self_eq_true, if_true, hss]
      exact (mem_tuplesOf σ.base ss vs).mpr ht
    · have ho' : owned D s j g.1 = false := by simpa using ho
      rw [tableOf_append_right_not g.1 _ _ (fun t ht e => by
          obtain ⟨k, hk', rfl⟩ := List.mem_map.mp ht
          have := (List.mem_filter.mp hk').2
          simp only at e; rw [e, ho'] at this; cases this),
        tablesFor_generated D s j _ g.1 hk, mem_tableOf_iff hndf]
      exact (hagree g.1 ho' vs).symm
  have hrelj := tablesModel_rel (one D s j).1 σ.base _ _ hGj
  have heq : (tablesModel (one D s j).1 σ.base (tablesFor D s j σ.fixed ++ G')).asStructure =
      withTables (one D s j).1 σ.base.asStructure G := by
    simp only [VE.FiniteModel.asStructure, withTables]
    congr 1
  have hBA' : BaseAdmissibleR (one D s j).1
      (tablesModel (one D s j).1 σ.base (tablesFor D s j σ.fixed ++ G')).asStructure := by
    rw [heq]; exact hBA
  have hvalj : (tablesModel (one D s j).1 σ.base (tablesFor D s j σ.fixed ++ G')).Valid
      (envAt (soften (correlate (one D s j).1)) 0) := hBA'.1.1.1
  have hbgj := backgroundValidR_of_admissible _ _ hBA'
  have htyG' : tablesTyped (one D s j).1 σ.base G' = true := by
    simp only [tablesTyped, List.all_eq_true, Bool.and_eq_true, Bool.or_eq_true, bne_iff_ne, ne_eq]
    intro t ht
    obtain ⟨k, hk, rfl⟩ := List.mem_map.mp ht
    obtain ⟨hk1, _⟩ := List.mem_filter.mp hk
    obtain ⟨g0, hg0, hg0k⟩ := List.mem_map.mp hk1
    refine ⟨List.any_eq_true.mpr ⟨g0, hg0, by simp [hg0k]⟩, fun vs hvs g'' _ => ?_⟩
    obtain ⟨_, hv⟩ := List.mem_filter.mp hvs
    rw [decide_eq_true_eq] at hv
    by_cases hkn : keyOfName (one D s j).1 g''.2.1 = some k
    · right
      simp only [keyOfName, Option.map_eq_some_iff] at hkn
      obtain ⟨g3, hg3, hg3k⟩ := hkn
      obtain ⟨ss, hss, ht⟩ := htyp g''.2.1 g3 hg3 vs (hg3k ▸ hv)
      simp only [declaredTyped, hss]
      exact (typedTuple_iff σ.base ss vs).mpr ht
    · exact Or.inl hkn
  have htyT' : tablesTyped (one D s j).1 σ.base (tablesFor D s j σ.fixed ++ G') = true := by
    simp only [tablesTyped, List.all_append, Bool.and_eq_true] at htyj htyG' ⊢
    exact ⟨htyj, htyG'⟩
  have hsvj : sideValid D s j σ.base (tablesFor D s j σ.fixed ++ G') = true := by
    simp only [sideValid, Bool.and_eq_true]
    exact ⟨htyT', hbgj⟩
  have hwj := sideWF_one D hD hj
  simp only [sideWF, Bool.and_eq_true, List.all_eq_true] at hwj
  have hAj : ∀ a ∈ (one D s j).2, a.WellFormed (envAt (soften (correlate (one D s j).1))
      (size (soften (correlate (one D s j).1)))) [] :=
    fun a ha => (VE.check_iff_wellFormed _ _ _).mp (hwj.2 a ha)
  have hptj : probeTyped (one D s j).1 (tablesModel (one D s j).1 σ.base (tablesFor D s j σ.fixed ++ G'))
      σ.probe = true := by
    refine (probeTyped_congr (X := (one D s j).1) (Y := (one D s i).1)
      (M := tablesModel (one D s j).1 σ.base (tablesFor D s j σ.fixed ++ G')) (M' := σ.base)
      ?_ rfl σ.probe).trans hpt
    rw [(keepsFrame_one D s j).regulated, (keepsFrame_one D s i).regulated]
  have hobsj := observes_rel hrelj.symm σ.probe σ.value hObs
  have hsvalj := (observe_sound D.chain (one D s j).1 (one D s j).2 hwj.1 hAj _ hvalj hbgj σ.probe hptj
    σ.value).mpr hobsj
  have := hall G' hG'mem
  simp only [sideValue] at this
  rw [hsvj, hsvalj] at this
  simp at this

theorem separates_sound {α : Type u} [DecidableEq α] (D : Doc) (hD : WellFormedDoc D = true) (s : String)
    (i j : Nat) (hi : (candidate D s i).bind (·.content) ≠ none) (hj : (candidate D s j).bind (·.content) ≠ none)
    (σ : Situation α) (valid : σ.base.Valid (authorEnv D)) (h : separates D s i j σ = true) :
  Achieves D s i σ.base.asStructure (tablesOf σ.fixed) σ.probe σ.value ∧
    ¬ Achieves D s j σ.base.asStructure (tablesOf σ.fixed) σ.probe σ.value := by
  simp only [separates, situationWF, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, beq_iff_eq,
    Bool.not_eq_true', Bool.or_eq_true] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨hnd, hfx⟩, hdec⟩, htyi⟩, htyj⟩, hpt⟩, hsvi⟩, hvi⟩, _⟩, hall⟩ := h
  have hndf : (σ.fixed.map (·.1)).Nodup := by
    rw [List.map_append] at hnd; exact (List.nodup_append.mp hnd).1
  refine ⟨separates_witness D hD s i hi σ valid hnd (fun t ht => (hdec t ht).1) hpt hsvi hvi,
    separates_other D hD s i j hj σ hndf (fun t ht => (hfx t ht).1.2) htyj hpt (fun G hG => ?_)⟩
  have := hall G hG
  simpa using this

/-- The corollary: a checked separation proves `Separated`. -/
theorem separates_separated {α : Type u} [DecidableEq α] (D : Doc) (hD : WellFormedDoc D = true) (s : String)
    (i j : Nat) (hi : (candidate D s i).bind (·.content) ≠ none) (hj : (candidate D s j).bind (·.content) ≠ none)
    (σ : Situation α) (valid : σ.base.Valid (authorEnv D)) (h : separates D s i j σ = true) :
  Separated.{u} D s i j :=
  ⟨σ.base.asStructure, tablesOf σ.fixed, σ.probe, σ.value,
    Or.inl (separates_sound D hD s i j hi hj σ valid h)⟩

/-! ## Proofs: conservativity -/

theorem probesOf_typed {α : Type u} [DecidableEq α] (D : Doc) (s : String) (i : Nat) (M : VE.FiniteModel α)
    (q : Probe α) (hq : q ∈ probesOf D M) : probeTyped (one D s i).1 M q = true := by
  have hr := (keepsFrame_one D s i).regulated
  simp only [probesOf, List.mem_append, List.mem_flatMap, List.mem_map] at hq
  rcases hq with ⟨p, hp, vs, hvs, rfl⟩ | ⟨k, hk, p, hp, vs, hvs, rfl⟩
  · simp only [probeTyped, hr, Bool.and_eq_true, List.any_eq_true, beq_iff_eq]
    rw [VE.SoftNorms.mem_dedup] at hp
    obtain ⟨r, hr', rfl⟩ := List.mem_map.mp hp
    exact ⟨⟨r, hr', rfl⟩, (typedTuple_iff M _ vs).mpr ((mem_tuplesOf M _ vs).mp hvs)⟩
  · simp only [probeTyped, hr, Bool.and_eq_true, List.any_eq_true, beq_iff_eq, List.contains_iff_mem]
    rw [VE.SoftNorms.mem_dedup] at hp
    obtain ⟨r, hr', rfl⟩ := List.mem_map.mp hp
    exact ⟨⟨hk, r, hr', rfl⟩, (typedTuple_iff M _ vs).mpr ((mem_tuplesOf M _ vs).mp hvs)⟩

theorem cells_nil {α : Type u} [DecidableEq α] {D : Doc} {s : String} {j : Nat} (M : VE.FiniteModel α)
    (h : ownedKeys D s j = []) : cells D s j M = 0 := by
  simp [cells, h]

theorem assignments_nil {α : Type u} [DecidableEq α] {D : Doc} {s : String} {j : Nat} (M : VE.FiniteModel α)
    (h : ownedKeys D s j = []) : assignments D s j M = [[]] := by
  simp [assignments, h]

theorem separates_noKeys {α : Type u} [DecidableEq α] (D : Doc) (s : String) (i j : Nat)
    (M : VE.FiniteModel α) (F : List (GenKey × List (List α))) (q : Probe α) (v : Bool)
    (hj : ownedKeys D s j = [])
    (hF : ∀ t ∈ F, owned D s i t.1 = false ∧ owned D s j t.1 = false ∧
      ((genKeys (one D s i).1).any (·.1 == t.1) || (genKeys (one D s j).1).any (·.1 == t.1)) = true)
    (hu : (F.map (·.1)).Nodup) (hq : q ∈ probesOf D M)
    (hvi : sideValid D s i M (tablesFor D s i F) = true) (hvj : sideValid D s j M (tablesFor D s j F) = true) :
    separates D s i j ⟨M, F, [], q, v⟩ = true ↔
      sideValue D s i M (tablesFor D s i F) q = some v ∧ sideValue D s j M (tablesFor D s j F) q ≠ some v := by
  have hti : tablesTyped (one D s i).1 M (tablesFor D s i F) = true := by
    simp only [sideValid, Bool.and_eq_true] at hvi; exact hvi.1
  have htj : tablesTyped (one D s j).1 M (tablesFor D s j F) = true := by
    simp only [sideValid, Bool.and_eq_true] at hvj; exact hvj.1
  have hwf : situationWF D s i j ⟨M, F, [], q, v⟩ = true := by
    simp only [situationWF, List.append_nil, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true,
      List.not_mem_nil, false_implies, implies_true, and_true, Bool.not_eq_true']
    refine ⟨⟨⟨⟨hu, fun t ht => ⟨⟨(hF t ht).1, (hF t ht).2.1⟩, by simpa using (hF t ht).2.2⟩⟩, hti⟩, htj⟩,
      probesOf_typed D s i M q hq⟩
  simp only [separates, hwf, List.append_nil, hvi, hvj, cells_nil M hj, assignments_nil M hj, Bool.true_and,
    List.all_cons, List.all_nil, Bool.and_true, beq_iff_eq, Bool.and_eq_true, decide_eq_true_eq, Bool.not_eq_true']
  simp [maxCells]

theorem separation_conservative {α : Type u} [DecidableEq α] (D : Doc) (s : String) (i j : Nat)
    (M : VE.FiniteModel α) (F : List (GenKey × List (List α)))
    (hi : ownedKeys D s i = []) (hj : ownedKeys D s j = [])
    (hF : ∀ t ∈ F, owned D s i t.1 = false ∧ owned D s j t.1 = false ∧
      ((genKeys (one D s i).1).any (·.1 == t.1) || (genKeys (one D s j).1).any (·.1 == t.1)) = true)
    (hu : (F.map (·.1)).Nodup)
    (hvi : sideValid D s i M (tablesFor D s i F) = true) (hvj : sideValid D s j M (tablesFor D s j F) = true) :
  (∃ q ∈ probesOf D M, ∃ v, separates D s i j ⟨M, F, [], q, v⟩ = true ∨ separates D s j i ⟨M, F, [], q, v⟩ = true) ↔
    observeAll D s i M F ≠ observeAll D s j M F := by
  have hF' : ∀ t ∈ F, owned D s j t.1 = false ∧ owned D s i t.1 = false ∧
      ((genKeys (one D s j).1).any (·.1 == t.1) || (genKeys (one D s i).1).any (·.1 == t.1)) = true := by
    intro t ht
    obtain ⟨h1, h2, h3⟩ := hF t ht
    exact ⟨h2, h1, by rw [Bool.or_comm]; exact h3⟩
  simp only [observeAll, ne_eq, List.map_inj_left]
  constructor
  · rintro ⟨q, hq, v, h | h⟩ hall
    · rw [separates_noKeys D s i j M F q v hj hF hu hq hvi hvj] at h
      exact h.2 (hall q hq ▸ h.1)
    · rw [separates_noKeys D s j i M F q v hi hF' hu hq hvj hvi] at h
      exact h.2 ((hall q hq).symm ▸ h.1)
  · intro hn
    obtain ⟨q, hq, hne⟩ : ∃ q ∈ probesOf D M,
        sideValue D s i M (tablesFor D s i F) q ≠ sideValue D s j M (tablesFor D s j F) q :=
      Classical.byContradiction fun hc => hn (fun q hq => Classical.byContradiction fun hne => hc ⟨q, hq, hne⟩)
    cases hoi : sideValue D s i M (tablesFor D s i F) q with
    | some v =>
      refine ⟨q, hq, v, Or.inl ?_⟩
      rw [separates_noKeys D s i j M F q v hj hF hu hq hvi hvj]
      exact ⟨hoi, fun e => hne (hoi.trans e.symm)⟩
    | none =>
      cases hoj : sideValue D s j M (tablesFor D s j F) q with
      | none => exact absurd (hoi.trans hoj.symm) hne
      | some v =>
        refine ⟨q, hq, v, Or.inr ?_⟩
        rw [separates_noKeys D s j i M F q v hi hF' hu hq hvj hvi]
        exact ⟨hoj, by rw [hoi]; simp⟩

/-! ## Proofs: force -/


theorem strictTwin_nodes (X : SoftDoc) (N : SoftNode) (hN : X.T.nodes = [N]) : (strictTwin X N).T.nodes = [strictOf N] := by
  simp [strictTwin, hN]

theorem switch_false (N : SoftNode) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (ha : N.alterable = []) (Y : SoftDoc) : ¬ (VE.SoftNorms.switchF Y N).denote S ρ := by
  simp [VE.SoftNorms.switchF, VE.SoftNorms.switchIn, ha, VE.Norms.anyF_denote]

theorem strictDecides_alone (X : SoftDoc) (N : SoftNode) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (hN : X.T.nodes = [N]) (hd : N.mode = .default) (p : String) (sign : Bool) :
    ¬ VE.SoftNorms.StrictDecidesD X S ρ p sign := by
  rintro ⟨M, hM, _, hs, _⟩
  obtain ⟨hM, _⟩ := VE.SoftNorms.mem_rulesOn.mp hM
  rw [hN, List.mem_singleton] at hM
  subst hM
  rw [hd] at hs; cases hs

theorem eff_alone (X : SoftDoc) (N : SoftNode) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (hN : X.T.nodes = [N]) (hd : N.mode = .default) :
    ∀ g, VE.SoftNorms.EffD X S ρ g N ↔ VE.SoftNorms.EligibleD X S ρ N
  | 0 => Iff.rfl
  | g + 1 => by
    simp only [VE.SoftNorms.EffD]
    refine ⟨fun h => h.1, fun h => ⟨h, ?_⟩⟩
    rintro ⟨M, hM, hi, _⟩
    rw [hN, List.mem_singleton] at hM
    subst hM
    simp [VE.SoftNorms.Incompatible] at hi

theorem applies_alone (X : SoftDoc) (N : SoftNode) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (hN : X.T.nodes = [N]) (hd : N.mode = .default) (ha : N.alterable = [])
    (he : ¬ (exceptedF X N).denote S ρ) :
    VE.SoftNorms.AppliesSoftD X S ρ N ↔ VE.SoftNorms.AppliesSoftD (strictTwin X N) S ρ (strictOf N) := by
  simp only [VE.SoftNorms.AppliesSoftD, hd, strictOf]
  rw [eff_alone X N S ρ hN hd]
  simp only [VE.SoftNorms.EligibleD, VE.SoftNorms.LiveD, VE.SoftNorms.BlockedD]
  have hs1 := switch_false N S ρ ha X
  have hs2 := switch_false { N with mode := .strict, exception := none } S ρ ha (strictTwin X N)
  have hb := strictDecides_alone X N S ρ hN hd
  constructor
  · rintro ⟨_, ⟨hg, hc, _, _⟩, _⟩
    exact ⟨hg, hc, hs2, fun h => by cases h⟩
  · rintro ⟨hg, hc, _, _⟩
    refine ⟨hd, ⟨hg, hc, hs1, fun _ => he⟩, ?_⟩
    rintro (h | h | ⟨_, _, _, h⟩ | ⟨_, _, _, h⟩) <;> exact hb _ _ h

theorem yields_alone (X : SoftDoc) (N : SoftNode) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (hN : X.T.nodes = [N]) (hd : N.mode = .default) (ha : N.alterable = [])
    (he : ¬ (exceptedF X N).denote S ρ) :
    ∀ f, VE.SoftNorms.YieldsSoftD X S ρ f N ↔ VE.SoftNorms.YieldsSoftD (strictTwin X N) S ρ f (strictOf N)
  | 0 => applies_alone X N S ρ hN hd ha he
  | f + 1 => by
    simp only [VE.SoftNorms.YieldsSoftD, VE.SoftNorms.children, VE.SoftNorms.mem_childrenIn_iff,
      strictTwin_nodes X N hN, hN, List.mem_singleton]
    rw [applies_alone X N S ρ hN hd ha he]
    apply or_congr Iff.rfl
    constructor
    · rintro ⟨C, ⟨hC, _, ho⟩, hy⟩
      rw [hC] at hy ho
      exact ⟨strictOf N, ⟨rfl, rfl, ho⟩, (yields_alone X N S ρ hN hd ha he f).mp hy⟩
    · rintro ⟨C, ⟨hC, _, ho⟩, hy⟩
      rw [hC] at hy ho
      exact ⟨N, ⟨rfl, rfl, ho⟩, (yields_alone X N S ρ hN hd ha he f).mpr hy⟩

theorem decides_alone (X : SoftDoc) (N : SoftNode) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (hN : X.T.nodes = [N]) (hd : N.mode = .default) (ha : N.alterable = [])
    (he : ¬ (exceptedF X N).denote S ρ) (p : String) (sign : Bool) :
    VE.SoftNorms.DecidesSoftD X S ρ p sign ↔ VE.SoftNorms.DecidesSoftD (strictTwin X N) S ρ p sign := by
  have hf : VE.SoftNorms.fuel (strictTwin X N) = VE.SoftNorms.fuel X := by
    simp [VE.SoftNorms.fuel, strictTwin_nodes X N hN, hN]
  simp only [VE.SoftNorms.DecidesSoftD, VE.SoftNorms.SelectsSoftD, VE.SoftNorms.mem_rulesOn, hf,
    strictTwin_nodes X N hN, hN, List.mem_singleton, VE.SoftNorms.children, VE.SoftNorms.mem_childrenIn_iff]
  constructor
  · rintro ⟨M, ⟨hM, hp⟩, hs, hap, hn⟩
    rw [hM] at hp hs hap hn
    refine ⟨strictOf N, ⟨rfl, hp⟩, hs, (applies_alone X N S ρ hN hd ha he).mp hap, ?_⟩
    rintro ⟨C, ⟨hC, _, ho⟩, hy⟩
    rw [hC] at hy ho
    exact hn ⟨N, ⟨rfl, rfl, ho⟩, (yields_alone X N S ρ hN hd ha he _).mpr hy⟩
  · rintro ⟨M, ⟨hM, hp⟩, hs, hap, hn⟩
    rw [hM] at hp hs hap hn
    refine ⟨N, ⟨rfl, hp⟩, hs, (applies_alone X N S ρ hN hd ha he).mpr hap, ?_⟩
    rintro ⟨C, ⟨hC, _, ho⟩, hy⟩
    rw [hC] at hy ho
    exact hn ⟨strictOf N, ⟨rfl, rfl, ho⟩, (yields_alone X N S ρ hN hd ha he _).mp hy⟩


/-- The force axis is real exactly where the exception can apply: a default rule alone and its strict twin agree
    wherever the rule's exception does not hold. -/
theorem force_agrees_off_exception (X : SoftDoc) (h : WellFormedSoft X = true) (N : SoftNode)
    (hN : X.T.nodes = [N]) (hd : N.mode = .default) (ha : N.alterable = []) (r : Regulated)
    (hr : r ∈ X.T.regulated) (S : VE.Structure.{u}) (vs : List S.Carrier)
    (he : ¬ (exceptedF X N).denote S (tupleVal vs)) :
  ValueSoft X r S vs = ValueSoft (strictTwin X N) r S vs := by
  unfold ValueSoft
  rw [propext (decides_alone X N S _ hN hd ha he r.name true),
    propext (decides_alone X N S _ hN hd ha he r.name false)]

end VE.Readings
