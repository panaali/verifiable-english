import VE.Bridge
import VE.Order.Wire

/-! Model decoding for the `route` and `quantity` runners.

The frozen decoders (`VE.Bridge.decodeModelData`, `VE.Order.Wire.decodeModel`)
find duplicates with `eraseDups`, quadratic in a domain or table, and check the
domain and tuple limits only after that work. These decoders return the same
`ModelData` with the same diagnostics, but first check the model's static
limits on the submitted JSON (`modelLimits`, as Python `_model_limits` and Rust
`model_limits`: every domain at most 1,000 entities, then at most 100,000
supplied tuples in all) and find duplicates with hash sets. Nothing here is
trusted: the runners re-check every decoded model with the proved admissibility
gates (`ModelData.valid`, `validModel?`) and Background. -/
namespace VE.Route.Decode
open Lean
open VE.Bridge (exactFields stringField strings identifier)

def domainLimit : String := "ResourceLimit: domain size"
def tupleLimit : String := "ResourceLimit: tuple count"

/-- The static limits of a submitted model, after its shape (fields, `complete`,
declared names) and before any entity is read: each domain has at most 1,000
entries, then all supplied tables at most 100,000 rows together. Entries that
are not arrays are left to the decoder's diagnostics. -/
def modelLimits (sorts : List String) (ds rs : Json) : Except String Unit := do
  for s in sorts do
    if let .ok (.arr xs) := ds.getObjVal? s then
      if xs.size > 1000 then throw domainLimit
  let rows := match rs with
    | .obj kvs => kvs.foldl (fun n _ v => match v with | .arr xs => n + xs.size | _ => n) 0
    | _ => 0
  if rows > 100000 then throw tupleLimit

/-- Whether a list has no repeated element, in one pass with a hash set. -/
def distinct {β : Type} [BEq β] [Hashable β] (xs : List β) : Bool :=
  (xs.foldlM (fun (seen : Std.HashSet β) x =>
    if seen.contains x then none else some (seen.insert x)) {}).isSome

def localIds (j : Json) : Except String (List String) := do
  let xs ← strings j
  unless xs.all identifier do throw "invalid local identifier"
  pure xs

/-- Each domain as a hash set, for membership while tables are decoded. -/
def domainSets (domains : List (String × List String)) : Std.HashMap String (Std.HashSet String) :=
  domains.foldr (fun (s, xs) m => m.insert s (Std.HashSet.ofList xs)) {}

def inDomain (sets : Std.HashMap String (Std.HashSet String)) (s x : String) : Bool :=
  match sets[s]? with
  | some xs => xs.contains x
  | none => false


/-! ## The admissibility gates, with hash-set domains

`ModelData.valid` and `validModel?` search a domain list for every cell of
every row. These give the same Boolean with a hash set per domain
(`validFast_eq`, `validOrderFast_eq`), so the proofs about the gates apply. -/

/-- A hash set per key, the first binding winning as in `lookup`. -/
def assocIndex {β : Type} [BEq β] [Hashable β] (xs : List (String × List β)) :
    Std.HashMap String (Std.HashSet β) :=
  xs.foldr (fun (k, ys) m => m.insert k (Std.HashSet.ofList ys)) {}

theorem assocIndex_get {β : Type} [BEq β] [Hashable β] [LawfulBEq β]
    (xs : List (String × List β)) (k : String) :
    (assocIndex xs)[k]? = ((xs.find? (fun x => x.1 == k)).map Prod.snd).map Std.HashSet.ofList := by
  induction xs with
  | nil => simp [assocIndex]
  | cons x xs ih =>
    obtain ⟨k', ys⟩ := x
    simp only [assocIndex, List.foldr_cons] at ih ⊢
    rw [Std.HashMap.getElem?_insert, ih]
    by_cases h : k' = k
    · subst h; simp
    · have hb : (k' == k) = false := beq_eq_false_iff_ne.mpr h
      simp [hb]

theorem ofList_contains {β : Type} [BEq β] [Hashable β] [LawfulBEq β] (ys : List β) (y : β) :
    (Std.HashSet.ofList ys).contains y = decide (y ∈ ys) := by
  rw [Std.HashSet.contains_ofList]
  cases h : ys.contains y <;> simp_all

def memFast (idx : Std.HashMap String (Std.HashSet String)) (s : String) (x : VE.Bridge.Entity) : Bool :=
  x.1 == s && match idx[s]? with
    | some xs => xs.contains x.2
    | none => false

theorem memFast_eq (d : VE.Bridge.ModelData) (s : String) (x : VE.Bridge.Entity) :
    memFast (assocIndex d.domains) s x = (d.toModel.domains s).contains x := by
  obtain ⟨x1, x2⟩ := x
  simp only [memFast, assocIndex_get, VE.Bridge.ModelData.toModel, VE.Bridge.lookup]
  cases (d.domains.find? (fun x => x.1 == s)).map Prod.snd with
  | none => simp
  | some ys =>
    simp only [Option.map_some, Option.getD_some, ofList_contains]
    by_cases h : x1 = s
    · subst h; simp
    · have hb : (x1 == s) = false := beq_eq_false_iff_ne.mpr h
      simp only [hb, Bool.false_and]
      symm
      simp only [List.contains_iff_mem, List.mem_map, Prod.mk.injEq, not_exists, not_and,
        Bool.eq_false_iff, ne_eq]
      intro _ _ he
      exact (h he.symm).elim

def tupleCheckFast (idx : Std.HashMap String (Std.HashSet String)) :
    List String → List VE.Bridge.Entity → Bool
  | [], [] => true
  | s :: ss, x :: xs => memFast idx s x && tupleCheckFast idx ss xs
  | _, _ => false

theorem tupleCheckFast_eq (d : VE.Bridge.ModelData) :
    ∀ (ss : List String) (xs : List VE.Bridge.Entity),
      tupleCheckFast (assocIndex d.domains) ss xs = VE.Bridge.tupleCheck d.toModel ss xs
  | [], [] => rfl
  | s :: ss, x :: xs => by
    simp only [tupleCheckFast, VE.Bridge.tupleCheck, memFast_eq, tupleCheckFast_eq d ss xs]
  | [], _ :: _ | _ :: _, [] => rfl

/-- `ModelData.valid` with hash-set domains. -/
def validFast (d : VE.Bridge.ModelData) (v : VE.Bridge.Vocabulary) : Bool :=
  let idx := assocIndex d.domains
  v.constants.all (fun (c, s) => match d.toModel.constants c with
    | some x => memFast idx s x
    | none => false) &&
  d.relations.all (fun (p, rows) => match v.environment.predicates p with
    | some ss => rows.all (tupleCheckFast idx ss)
    | none => false)

theorem validFast_eq (d : VE.Bridge.ModelData) (v : VE.Bridge.Vocabulary) :
    validFast d v = d.valid v := by
  have ht : tupleCheckFast (assocIndex d.domains) = VE.Bridge.tupleCheck d.toModel :=
    funext fun ss => funext fun xs => tupleCheckFast_eq d ss xs
  simp only [validFast, VE.Bridge.ModelData.valid, memFast_eq, ht]
  rfl

def domainCheckFast (idx : Std.HashMap String (Std.HashSet VE.Order.Wire.Entity)) :
    VE.Order.SortName → VE.Order.Value VE.Order.Wire.Entity → Bool
  | .user s, .inl x => match idx[s]? with
    | some xs => xs.contains x
    | none => false
  | .int, .inr _ => true
  | _, _ => false

theorem domainCheckFast_eq (d : VE.Order.ModelData VE.Order.Wire.Entity) (s : VE.Order.SortName)
    (x : VE.Order.Value VE.Order.Wire.Entity) :
    domainCheckFast (assocIndex d.domains) s x = VE.Order.domainCheck d.toModel s x := by
  cases s <;> cases x <;> simp only [domainCheckFast, VE.Order.domainCheck]
  rename_i s x
  apply Bool.eq_iff_iff.mpr
  simp only [decide_eq_true_eq]
  rw [assocIndex_get]
  simp only [VE.Order.ModelData.toModel, VE.Order.lookup]
  cases List.find? (fun x => x.fst == s) d.domains with
  | none => simp
  | some p => simp

def tupleCheckOrderFast (idx : Std.HashMap String (Std.HashSet VE.Order.Wire.Entity)) :
    List VE.Order.SortName → List (VE.Order.Value VE.Order.Wire.Entity) → Bool
  | [], [] => true
  | s :: ss, x :: xs => domainCheckFast idx s x && tupleCheckOrderFast idx ss xs
  | _, _ => false

theorem tupleCheckOrderFast_eq (d : VE.Order.ModelData VE.Order.Wire.Entity) :
    ∀ (ss : List VE.Order.SortName) (xs : List (VE.Order.Value VE.Order.Wire.Entity)),
      tupleCheckOrderFast (assocIndex d.domains) ss xs = VE.Order.tupleCheck d.toModel ss xs
  | [], [] => rfl
  | s :: ss, x :: xs => by
    simp only [tupleCheckOrderFast, VE.Order.tupleCheck, domainCheckFast_eq,
      tupleCheckOrderFast_eq d ss xs]
  | [], _ :: _ | _ :: _, [] => rfl

/-- `validModel?` with hash-set domains. -/
def validOrderFast (v : VE.Order.Vocabulary) (d : VE.Order.ModelData VE.Order.Wire.Entity) : Bool :=
  let idx := assocIndex d.domains
  v.constants.all (fun (c, _) =>
    match v.environment.constants c, d.toModel.constants c with
    | some s, some x => domainCheckFast idx s x
    | _, _ => false) &&
  d.relations.all (fun (p, _) => (d.toModel.relations p).all (fun xs =>
    match v.environment.predicates p with
    | some ss => tupleCheckOrderFast idx ss xs
    | none => false))

theorem validOrderFast_eq (v : VE.Order.Vocabulary) (d : VE.Order.ModelData VE.Order.Wire.Entity) :
    validOrderFast v d = VE.Order.validModel? v d := by
  have ht : tupleCheckOrderFast (assocIndex d.domains) = VE.Order.tupleCheck d.toModel :=
    funext fun ss => funext fun xs => tupleCheckOrderFast_eq d ss xs
  simp only [validOrderFast, VE.Order.validModel?, domainCheckFast_eq, ht]
  congr 1
  congr 1
  funext x
  split <;> simp_all

/-- `VE.Bridge.decodeModelData` with the static limits first and linear
duplicate checks. -/
def decodeModelData (v : VE.Bridge.Vocabulary) (j : Json) : Except String VE.Bridge.ModelData := do
  exactFields j ["complete", "domains", "constants", "relations"]
  unless (← (← j.getObjVal? "complete").getBool?) do throw "complete must be true"
  let ds ← j.getObjVal? "domains"
  let cs ← j.getObjVal? "constants"
  let rs ← j.getObjVal? "relations"
  exactFields ds v.sorts
  exactFields cs (v.constants.map Prod.fst)
  exactFields rs (v.predicates.map Prod.fst)
  modelLimits v.sorts ds rs
  let domains ← v.sorts.mapM fun s => do
    let xs ← localIds (← ds.getObjVal? s)
    unless distinct xs do throw "duplicate domain entity"
    if xs.length > 1000 then throw domainLimit
    pure (s, xs)
  let sets := domainSets domains
  let constants ← v.constants.mapM fun (c, s) => do
    let x ← stringField cs c
    unless inDomain sets s x do throw "dangling constant"
    pure (c, (s, x))
  let relations ← v.predicates.mapM fun (p, ss) => do
    let rows ← (← (← rs.getObjVal? p).getArr?).toList.mapM localIds
    unless distinct rows do throw "duplicate relation tuple"
    let tuples ← rows.mapM fun row => do
      unless row.length == ss.length do throw "wrong relation arity"
      let tuple := ss.zip row
      for (s, x) in tuple do
        unless inDomain sets s x do throw "dangling or wrong-sort tuple"
      pure tuple
    pure (p, tuples)
  if (relations.map (fun p => p.2.length)).foldl (· + ·) 0 > 100000 then throw tupleLimit
  pure ⟨domains, constants, relations⟩

/-- `VE.Order.Wire.decodeValue` against hash-set domains. -/
def decodeValue (sets : Std.HashMap String (Std.HashSet String)) (s : VE.Order.SortName) (j : Json) :
    Except String (VE.Order.Value VE.Order.Wire.Entity) := do
  let text ← j.getStr?
  match s with
  | .int => return .inr (← VE.Order.Wire.decodeInt text)
  | .user sort =>
    unless inDomain sets sort text do throw "dangling or wrong-sort value"
    return .inl (sort, text)

/-- A hashable spelling of an order cell (no user sort is named `$int`). -/
def cellKey : VE.Order.Value VE.Order.Wire.Entity → String × String
  | .inl e => e
  | .inr z => ("$int", toString z)

/-- `VE.Order.Wire.decodeValidModel` with the static limits first and linear
duplicate checks; admissibility is the `validModel?` gate (`validOrderFast_eq`). -/
def decodeOrderModel (v : VE.Order.Vocabulary) (j : Json) :
    Except String (VE.Order.ModelData VE.Order.Wire.Entity) := do
  exactFields j ["complete", "domains", "constants", "relations"]
  unless (← (← j.getObjVal? "complete").getBool?) do throw "complete must be true"
  let ds ← j.getObjVal? "domains"
  let cs ← j.getObjVal? "constants"
  let rs ← j.getObjVal? "relations"
  exactFields ds v.sorts
  exactFields cs (v.constants.map Prod.fst)
  exactFields rs (v.predicates.map Prod.fst)
  modelLimits v.sorts ds rs
  let domains ← v.sorts.mapM fun s => do
    let xs ← strings (← ds.getObjVal? s)
    unless xs.all identifier do throw "invalid local identifier"
    unless distinct xs do throw "duplicate domain entity"
    if xs.length > 1000 then throw domainLimit
    pure (s, xs)
  let sets := domainSets domains
  let constants ← v.constants.mapM fun (c, s) => do
    pure (c, ← decodeValue sets s (← cs.getObjVal? c))
  let relations ← v.predicates.mapM fun (p, ss) => do
    let rows ← (← (← rs.getObjVal? p).getArr?).toList.mapM fun row => do
      let cells := (← row.getArr?).toList
      unless cells.length == ss.length do throw "wrong relation arity"
      (ss.zip cells).mapM fun (s, cell) => decodeValue sets s cell
    unless distinct (rows.map (·.map cellKey)) do throw "duplicate relation tuple"
    pure (p, rows)
  if (relations.map (fun p => p.2.length)).foldl (· + ·) 0 > 100000 then throw tupleLimit
  let d : VE.Order.ModelData VE.Order.Wire.Entity :=
    ⟨domains.map (fun (s, xs) => (s, xs.map (s, ·))), constants, relations⟩
  unless validOrderFast v d do throw "model is not semantically admissible"
  pure d

end VE.Route.Decode
