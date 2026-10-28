import VE.Cardinality.Syntax

/-! Regions of the counted sorts (docs/spec/quantities.md 3.5).

The counted sorts come from counts only (count atoms, proportions and count operands of a ratio); a recognised
universal statement over a counted sort adds its predicates on that sort, so it can be bridged (`bridgePremises`). For
each counted sort a region is one truth value per predicate of `predsOn`, and each region gets one fresh dimensionless
integer constant. -/
namespace VE.Cardinality
open VE.Time (QEnv QTerm QFormula)

def firstUse {β : Type} [BEq β] (xs : List β) : List β :=
  xs.foldl (fun acc x => if acc.contains x then acc else acc ++ [x]) []

def Body.atoms : Body → List String
  | .atom p => [p]
  | .any => []
  | .not b => b.atoms
  | .and a b => a.atoms ++ b.atoms
  | .or a b => a.atoms ++ b.atoms

/-- A W6a formula on the counted variable (de Bruijn 0) built from unary atoms, read as a body. -/
def bodyOfQ? : QFormula → Option Body
  | .unary p (.var 0) => some (.atom p)
  | .top => some .any
  | .bottom => some (.not .any)
  | .not a => (bodyOfQ? a).map Body.not
  | .and a b => match bodyOfQ? a, bodyOfQ? b with
    | some x, some y => some (.and x y)
    | _, _ => none
  | .or a b => match bodyOfQ? a, bodyOfQ? b with
    | some x, some y => some (.or x y)
    | _, _ => none
  | .implies a b => match bodyOfQ? a, bodyOfQ? b with
    | some x, some y => some (.or (.not x) y)
    | _, _ => none
  | _ => none

/-- The recognised universal statements `∀x:s. b(x)` anywhere in a W6a formula, each with its own text. -/
def universalsOf : QFormula → List (String × Body × QFormula)
  | .all s a => (match bodyOfQ? a with
      | some b => [(s, b, QFormula.all s a)]
      | none => []) ++ universalsOf a
  | .ex _ a => universalsOf a
  | .not a => universalsOf a
  | .and a b => universalsOf a ++ universalsOf b
  | .or a b => universalsOf a ++ universalsOf b
  | .implies a b => universalsOf a ++ universalsOf b
  | _ => []

def CFormula.universalsC (E : CEnv) : CFormula → List (String × Body × QFormula)
  | .quantity a => (universalsOf a).filter (fun x => E.finite.contains x.1)
  | .not a => a.universalsC E
  | .and a b => a.universalsC E ++ b.universalsC E
  | .or a b => a.universalsC E ++ b.universalsC E
  | .implies a b => a.universalsC E ++ b.universalsC E
  | _ => []

def CTerm.countBodies : CTerm → List (String × Body)
  | .quantity _ => []
  | .count s b => [(s, b)]

/-- The counted sorts and bodies: count atoms, proportions and count operands (not universal statements). -/
def CFormula.countBodies : CFormula → List (String × Body)
  | .quantity _ => []
  | .count c => c.terms.map (fun kb => (c.sort, kb.2))
  | .proportion p => [(p.sort, p.whole), (p.sort, p.part)]
  | .roundsTo _ n d _ _ => n.countBodies ++ d.countBodies
  | .percentOf p w _ _ => p.countBodies ++ w.countBodies
  | .percentRoundsTo _ p w _ _ => p.countBodies ++ w.countBodies
  | .not a => a.countBodies
  | .and a b => a.countBodies ++ b.countBodies
  | .or a b => a.countBodies ++ b.countBodies
  | .implies a b => a.countBodies ++ b.countBodies

def countedSorts (fs : List CFormula) : List String :=
  firstUse ((fs.flatMap (·.countBodies)).map (·.1))

/-- The universal statements of `us` over a sort of `sorts`, each once. -/
def countedAmong (sorts : List String) (us : List (String × Body × QFormula)) : List (String × Body × QFormula) :=
  firstUse (us.filter (fun x => sorts.contains x.1))

/-- Recognised universal statements over a counted sort, each once. -/
def countedUniversals (E : CEnv) (fs : List CFormula) : List (String × Body × QFormula) :=
  countedAmong (countedSorts fs) (fs.flatMap (·.universalsC E))

/-- The predicates on sort `s` of the count bodies `bodies` and the counted universal statements `us`, in first-use
order: count bodies first, then counted universal statements. -/
def predsAmong (bodies : List (String × Body)) (us : List (String × Body × QFormula)) (s : String) : List String :=
  firstUse (((bodies.filter (·.1 == s)).flatMap (·.2.atoms)) ++ ((us.filter (·.1 == s)).flatMap (·.2.1.atoms)))

/-- The predicates on sort `s`, in first-use order: count bodies first, then counted universal statements. -/
def predsOn (E : CEnv) (fs : List CFormula) (s : String) : List String :=
  predsAmong (fs.flatMap (·.countBodies)) (countedUniversals E fs) s

/-- A region: one truth value per predicate of `predsOn`; `regions n` lists all `2 ^ n`, first predicate most
significant. -/
abbrev Region := List Bool

def regions : Nat → List Region
  | 0 => [[]]
  | n + 1 => (regions n).map (false :: ·) ++ (regions n).map (true :: ·)

def Body.inRegion (ps : List String) (r : Region) : Body → Bool
  | .atom p => match ps.findIdx? (· == p) with
    | some i => r.getD i false
    | none => false
  | .any => true
  | .not b => !(b.inRegion ps r)
  | .and a b => a.inRegion ps r && b.inRegion ps r
  | .or a b => a.inRegion ps r || b.inRegion ps r

def bitString (r : Region) : String := String.mk (r.map (fun b => if b then '1' else '0'))

/-- `cardinality__<sort>__<bits>`. Bits are only `0` and `1`, so two different (sort, region) pairs never share a
name. -/
def regionConst (s : String) (r : Region) : String := regionPrefix ++ s ++ "__" ++ bitString r

/-- Every region constant of the sorts `sorts`, with its sort and region, the predicates on each sort read from `P`. -/
def tableOf (sorts : List String) (P : String → List String) : List (String × String × Region) :=
  sorts.flatMap fun s => (regions (P s).length).map fun r => (regionConst s r, s, r)

def regionTable (E : CEnv) (fs : List CFormula) : List (String × String × Region) :=
  tableOf (countedSorts fs) (predsOn E fs)

def dl : String := VE.Time.dimensionless

/-- `E.q` plus one dimensionless integer constant per region constant of `table`. -/
def CEnv.elabBy (E : CEnv) (table : List (String × String × Region)) : QEnv :=
  { E.q with constants := fun c => if table.any (·.1 == c) then some (.qty dl) else E.q.constants c }

/-- `E.q` plus one dimensionless integer constant per region of every counted sort; the region table is computed once,
not at every read of a constant. -/
def CEnv.elab (E : CEnv) (fs : List CFormula) : QEnv := E.elabBy (regionTable E fs)

/-- The region's own body: each predicate of `ps` or its negation, as the region's bits say. -/
def regionBody (ps : List String) (r : Region) : Body :=
  (ps.zip r).foldr (fun pv acc => .and (if pv.2 then .atom pv.1 else .not (.atom pv.1)) acc) .any

/-! ## Problem limits (spec 4.2, P1 and P2; P3 is W6a's aggregate limit on the erased problem, QT-A3) -/

def maxCountedSorts : Nat := 8
def maxPredicates : Nat := 6

/-- P1: at most 8 counted sorts. -/
def sortLimit (sorts : List String) : Except String Unit :=
  if sorts.length > maxCountedSorts then throw s!"ResourceLimit: At most {maxCountedSorts} counted sorts" else pure ()

/-- P2: at most 6 predicates (64 regions) on each counted sort, in first-use order, read from `P`. -/
def predicateLimit (sorts : List String) (P : String → List String) : Except String Unit := do
  for s in sorts do
    if (P s).length > maxPredicates then
      throw s!"ResourceLimit: At most {maxPredicates} predicates on counted sort {s} ({2 ^ maxPredicates} regions)"

/-- At most 8 counted sorts, then at most 6 predicates (64 regions) on each, in first-use order; so a problem has at
most 512 region constants. -/
def problemLimits (E : CEnv) (fs : List CFormula) : Except String Unit := do
  let sorts := countedSorts fs
  sortLimit sorts
  predicateLimit sorts (predsOn E fs)

/-! ## The region structure, computed once per problem (`regionData_predsOn`) -/

/-- A problem's counted sorts, the predicates on each and its counted universal statements, each computed once;
`regionData` builds it after P1 (`sortLimit`), so the predicates are listed for at most 8 sorts. -/
structure RegionData where
  sorts : List String
  preds : List (String × List String)
  universals : List (String × Body × QFormula)

/-- The predicates on `s`: its row of `preds`, none on a sort that is not counted (as `predsOn`). -/
def RegionData.predsOn (R : RegionData) (s : String) : List String :=
  match R.preds.find? (·.1 == s) with
  | some e => e.2
  | none => []

/-- The region table, each sort's predicates read from its row. -/
def RegionData.table (R : RegionData) : List (String × String × Region) := tableOf R.sorts R.predsOn

/-- The region structure of the counted sorts `sorts` with the count bodies `bodies` and the universal statements
`us`: one scan of the problem for each sort's predicates. -/
def regionDataOf (sorts : List String) (bodies : List (String × Body)) (us : List (String × Body × QFormula)) :
    RegionData :=
  let counted := countedAmong sorts us
  ⟨sorts, sorts.map fun s => (s, predsAmong bodies counted s), counted⟩

def regionData (E : CEnv) (fs : List CFormula) : RegionData :=
  regionDataOf (countedSorts fs) (fs.flatMap (·.countBodies)) (fs.flatMap (·.universalsC E))

/-- P1, the region structure, then P2 on it: `problemLimits` and then `regionData`, each part computed once. -/
def checkedRegions (E : CEnv) (fs : List CFormula) : Except String RegionData := do
  let sorts := countedSorts fs
  sortLimit sorts
  let R := regionDataOf sorts (fs.flatMap (·.countBodies)) (fs.flatMap (·.universalsC E))
  predicateLimit sorts R.predsOn
  pure R

end VE.Cardinality
