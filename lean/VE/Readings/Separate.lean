import VE.Readings.Doc
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
/-- The criterion of 1.7 with i the strict twin: the default twin's exception key. -/
def decisionOnly (D : Doc) (s : String) (i j : Nat) : Option GenKey :=
  match (candidate D s i).bind (·.content), (candidate D s j).bind (·.content) with
  | some ci, some cj =>
    match forceTwins ci cj with
    | some (_, Nd) =>
      let C := correlate (one D s j).1
      if (Nd.exception.all (·.sufficient.isEmpty)) &&
          C.T.nodes.any (fun M => M.name == Nd.name && M.pred == Nd.pred) &&
          C.T.nodes.all (fun M => VE.SoftNorms.act C M != VE.SoftNorms.act C Nd || M.name == Nd.name)
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
        obtain ⟨⟨he, _⟩, hn⟩ := hc
        refine ⟨ci, cj, Ns, Nd, hi, hj, hf, rfl, fun e hx => he e hx, fun M hM ha => ?_⟩
        rcases hn M hM with h' | h'
        · exact absurd ha h'
        · exact h'
      · cases h
    · cases h
  · cases h

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
end VE.Readings
