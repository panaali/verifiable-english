import VE.Rights.Route

/-! The layers of a chain document computed once (lean-first plan F5d), for the readings route.

A readings request validates `free D` and every candidate's `one D s i` and evaluates every pair's completions.
Each of those rebuilt, for every formula it typed or expanded, the layer order of `soften (correlate X)` (a
topological sort of its stratum DAG), the layered environment `envAt` and the outcome expansion table `expTable`.
The functions here compute them once per document. Each is declared in the namespace of the function it replaces,
with a lemma that the two are equal, so every theorem about the original holds of the run. This module is
imported only by the readings route, so no other executable changes. -/

namespace VE.Norms

/-! ## The expansion table built once

`expTable T i` answers a lookup by computing the layer order (`syms T`, a topological sort) at each of the `i`
levels and the meaning of the symbol it finds afresh, recursively; nothing is kept between lookups. `expEntries T`
holds one entry per layer symbol, newest first, each symbol's base formula built when first read and then kept
(a `Thunk`), and `expAt` reads the table of any prefix from it. `expAt_expEntries` says it is `expTable`. -/

/-- The table of an entry list kept newest first: a name's newest entry. -/
def entryTable (es : List (String × Thunk VE.Formula)) : Table := fun n => (es.find? (·.1 == n)).map (·.2.get)

/-- The entries with the next layer symbol added: its meaning under the entries before it. -/
def expStep (T : Tree) (es : List (String × Thunk VE.Formula)) (q : Sym) : List (String × Thunk VE.Formula) :=
  (q.name, Thunk.mk (fun _ => substWith (entryTable es) (q.meaning T))) :: es

/-- One entry per layer symbol of `T`, newest first. -/
def expEntries (T : Tree) : List (String × Thunk VE.Formula) := (syms T).foldl (expStep T) []

/-- The table of the first `i` layer symbols, read from the entries of all of them. -/
def expAt (es : List (String × Thunk VE.Formula)) (i : Nat) : Table := entryTable (es.drop (es.length - i))

theorem expStep_foldl_length (T : Tree) : ∀ (l : List Sym) (es : List (String × Thunk VE.Formula)),
    (l.foldl (expStep T) es).length = es.length + l.length
  | [], _ => rfl
  | q :: l, es => by
    rw [List.foldl_cons, expStep_foldl_length T l, expStep, List.length_cons, List.length_cons]
    omega

theorem expStep_foldl_drop (T : Tree) : ∀ (l : List Sym) (es : List (String × Thunk VE.Formula)),
    (l.foldl (expStep T) es).drop l.length = es
  | [], _ => rfl
  | q :: l, es => by
    rw [List.foldl_cons, List.length_cons, ← List.drop_drop, expStep_foldl_drop T l, expStep, List.drop_one,
      List.tail_cons]

theorem entryTable_take (T : Tree) : ∀ k : Nat, entryTable (((syms T).take k).foldl (expStep T) []) = expTable T k
  | 0 => by funext n; simp [entryTable, expTable]
  | k + 1 => by
    funext n
    cases hq : (syms T)[k]? with
    | some q =>
      have hk : (syms T).take (k + 1) = (syms T).take k ++ [q] := by rw [List.take_succ, hq]; rfl
      have ih := entryTable_take T k
      rw [hk, List.foldl_append, List.foldl_cons, List.foldl_nil, expStep]
      simp only [expTable, hq, ← ih]
      by_cases h : q.name = n
      · simp [entryTable, h, Thunk.get]
      · simp [entryTable, h, Ne.symm h]
    | none =>
      have hk : (syms T).take (k + 1) = (syms T).take k := by rw [List.take_succ, hq]; simp
      rw [hk, entryTable_take T k]
      simp only [expTable, hq]

theorem expAt_expEntries (T : Tree) (i : Nat) : expAt (expEntries T) i = expTable T i := by
  have hs : syms T = (syms T).take i ++ (syms T).drop i := (List.take_append_drop i (syms T)).symm
  have hl : (expEntries T).length - i = ((syms T).drop i).length := by
    rw [expEntries, expStep_foldl_length, List.length_drop]
    simp
  unfold expAt
  rw [hl, expEntries, hs, List.foldl_append, ← hs, expStep_foldl_drop, entryTable_take]

/-- `subst` read from the entries. -/
theorem subst_expAt (T : Tree) (i : Nat) (φ : VE.Formula) : substWith (expAt (expEntries T) i) φ = subst T i φ := by
  rw [expAt_expEntries]
  rfl

/-- What every formula of a document reads from its layers, computed once per document: the layer symbols in
order, their names, and the expansion table's entries. -/
structure Layers where
  syms : List Sym
  names : List String
  entries : List (String × Thunk VE.Formula)

def layersOf (D : Doc) : Layers :=
  let ss := syms D.T
  ⟨ss, ss.map Sym.name, ss.foldl (expStep D.T) []⟩

theorem layersOf_syms (D : Doc) : (layersOf D).syms = syms D.T := rfl
theorem layersOf_names (D : Doc) : (layersOf D).names = layerNames D.T := rfl
theorem layersOf_entries (D : Doc) : (layersOf D).entries = expEntries D.T := rfl

/-- `subst D.T i` from a document's layers. -/
def substIn (L : Layers) (i : Nat) (φ : VE.Formula) : VE.Formula := substWith (expAt L.entries i) φ

theorem substIn_eq (D : Doc) (i : Nat) (φ : VE.Formula) : substIn (layersOf D) i φ = subst D.T i φ :=
  subst_expAt D.T i φ

/-- `conflict`, `outcomeBase` and `pairConflict` from the document's layers, computed once (plan F5d). -/
def conflictIn (D : Doc) (L : Layers) (r : Regulated) : VE.Formula :=
  let i := L.names.idxOf r.name
  .and (substIn L i (pos D.T r.name)) (substIn L i (neg D.T r.name))

def outcomeBaseIn (D : Doc) (L : Layers) (n : String) : VE.Formula :=
  match D.T.regulated.find? (·.name == n) with
  | some r => substIn L (L.names.idxOf n) (outcome D.T r)
  | none => .bottom

def pairConflictIn (D : Doc) (L : Layers) (pr : Pair) : VE.Formula :=
  .and (outcomeBaseIn D L pr.req) (.not (outcomeBaseIn D L pr.perm))

theorem conflictIn_eq (D : Doc) (r : Regulated) : conflictIn D (layersOf D) r = conflict D r := by
  simp only [conflictIn, conflict, substIn_eq, layersOf_names, before]

theorem outcomeBaseIn_eq (D : Doc) (n : String) : outcomeBaseIn D (layersOf D) n = outcomeBase D n := by
  simp only [outcomeBaseIn, outcomeBase, substIn_eq, layersOf_names, before]
  all_goals rfl

theorem pairConflictIn_eq (D : Doc) (pr : Pair) : pairConflictIn D (layersOf D) pr = pairConflict D pr := by
  simp only [pairConflictIn, pairConflict, outcomeBaseIn_eq]

/-- `targets` from the document's layers, computed once (plan F5d). -/
def targetsIn (D : Doc) (L : Layers) : List (String × List String × VE.Formula) :=
  L.syms.filterMap (fun | .reg r => some (r.name, r.sorts, conflictIn D L r) | .defn _ => none) ++
    (pairs D.T).map (fun pr => (pr.req ++ "->" ++ pr.perm, pr.sorts, pairConflictIn D L pr))

theorem targetsIn_eq (D : Doc) : targetsIn D (layersOf D) = targets D := by
  simp only [targetsIn, targets, layersOf_syms, conflictIn_eq, pairConflictIn_eq]
  all_goals rfl

end VE.Norms

namespace VE.SoftNorms
open VE.Norms

/-! ## Soft-norm checks with the layers computed once

`softSemanticCheck` computes `envAt (soften D) _` (a topological sort of the stratum DAG) for every formula it
types, and `checkSoft`'s conflict targets rebuild the layer order at every level of the expansion table. The
functions below compute `soften D`, its layered environments and its expansion table once; each is equal to the
function it replaces (`checkSoftOnce_eq`, `softSemanticCheckOnce_eq`, `validateSoftOnce_eq`). -/

/-- `selects′_N` with `soften D` given. -/
def selectsOn (S : Doc) (D : SoftDoc) (N : SoftNode) : VE.Formula :=
  VE.Norms.selects S.T (VE.Norms.fuel S.T) (primeNode D N)

theorem selectsOn_soften (D : SoftDoc) : selectsOn (soften D) D = selects' D := rfl

def defaultDecidesOn (S : Doc) (D : SoftDoc) (p : String) (sign : Bool) : VE.Formula :=
  anyF ((((rulesOn D p).filter (·.mode == .default)).filter (·.sign == sign)).map (selectsOn S D))

/-- The coherence premise from `soften D` and its layers. -/
def cohPremiseIn (D : SoftDoc) (S : Doc) (L : Layers) (M N : SoftNode) : VE.Formula :=
  bindAll (actSorts D M) (.not (.and (substIn L L.syms.length (selectsOn S D M))
                                     (substIn L L.syms.length (selectsOn S D N))))

def softPremisesIn (D : SoftDoc) (S : Doc) (L : Layers) : List VE.Formula :=
  excPremises D ++ (collidingPairs D).map (fun (M, N) => cohPremiseIn D S L M N)

theorem softPremisesIn_eq (D : SoftDoc) : softPremisesIn D (soften D) (layersOf (soften D)) = softPremises D := by
  simp only [softPremisesIn, softPremises, cohPremises, cohPremiseIn, cohPremise, substIn_eq, layersOf_syms,
    selectsOn_soften, size]

/-- `checkSoft` with the conflict targets and the soft premises built from the layers of `soften D`. -/
def checkSoftOnce (D : SoftDoc) : Except String Unit := do
  let env := D.soft
  checkSoftEnv D
  for (p, _) in D.T.regulated.map (fun r => (r.name, r.sorts)) do
    if containsDunder p then throw s!"InvalidInput: invalid soft name {p}"
  for p in D.T.definitions.map (·.name) do
    if reservedPredicate p then throw s!"InvalidInput: invalid soft name {p}"
  checkW1 D.base
  for N in D.T.nodes do
    checkSoftRule D N
  for N in D.T.nodes do
    if N.mode = .default then
      for m in N.over do
        match D.T.nodes.find? (·.name == m) with
        | some M => if M.mode = .strict then throw s!"SoftOverHard: rule {N.name} over {M.name}"
        | none => pure ()
  match checkSoft.dependencyOrderOf env with
  | .error e => throw e
  | .ok _ => pure ()
  for (a, b) in env.ties do
    if outranksPlus env a b || outranksPlus env b a then throw s!"TieAgainstOrder: {a}, {b}"
  if (env.ties.map (fun (a, b) => if a ≤ b then (a, b) else (b, a))).eraseDups.length != env.ties.length then
    throw "DuplicateDeclaration: tie"
  for (N, s) in D.T.nodes.zip (derivedSizes D) do
    if N.carveOuts.length + (if hasDerived N then 1 else 0) > 8 || (hasDerived N && !fits s) then
      throw s!"ResourceLimit: derived carve-out of rule {N.name}"
  for N in D.T.nodes do
    unless (derivedList D N).all withinLimits do
      throw s!"ResourceLimit: derived carve-out of rule {N.name}"
  validateW1 (soften D)
  let sizes := generatedSizes D
  for s in sizes.soft do
    unless fits s do throw "ResourceLimit: generated soft premise"
  for φ in softPremisesIn D (soften D) (layersOf (soften D)) do
    unless withinLimits φ do throw "ResourceLimit: generated soft premise"
  for (p, s) in sizes.layers do
    unless fits s do throw s!"ResourceLimit: generated norm layer layer:norms:{p}"
  for s in syms (soften D).T do
    if let .reg r := s then
      unless withinLimits (elabPremise (soften D).T r) do
        throw s!"ResourceLimit: generated norm layer layer:norms:{r.name}"
  for (t, s) in sizes.targets do
    unless fits s do throw s!"ResourceLimit: generated conflict target {t}"
  for t in targetsIn (soften D) (layersOf (soften D)) do
    unless withinLimits (targetConclusion t) do throw s!"ResourceLimit: generated conflict target {t.1}"
  unless fitsTogether ((VE.Norms.background (soften D)).map (fsize noSubst) ++ sizes.soft) do
    throw "ResourceLimit: generated background"
  unless fitsTogether (sizes.layers.map (·.2) ++ [fsize noSubst .top]) do
    throw "ResourceLimit: generated norm layers"

theorem checkSoftOnce_eq (D : SoftDoc) : checkSoftOnce D = checkSoft D := by
  unfold checkSoftOnce checkSoft
  rw [softPremisesIn_eq, targetsIn_eq]
  all_goals rfl

/-- `softSemanticCheck` with `soften D`, its two layered environments and its layers computed once. -/
def softSemanticCheckOnce (D : SoftDoc) : Bool :=
  let S := soften D
  let L := layersOf S
  let E0 := envAt S 0
  let En := envAt S L.syms.length
  VE.Norms.WellFormed S &&
  decide (D.T.nodes.map (·.name)).Nodup &&
  decide (D.T.regulated.map (·.name)).Nodup &&
  decide ((pairs D.base.T).map (·.req)).Nodup &&
  decide ((pairs D.base.T).map (·.perm)).Nodup &&
  (pairs D.base.T).all (fun pr => !((pairs D.base.T).map (·.req)).contains pr.perm) &&
  D.T.nodes.all (fun N => (D.T.regulated.map (·.name)).contains N.pred) &&
  D.soft.outranks.all (fun e => D.soft.ranks.contains e.1 && D.soft.ranks.contains e.2) &&
  (VE.Route.dependencyOrder (rankNodes D.soft)).isOk &&
  decide (D.soft.below = closureOf D.soft.ranks D.soft.outranks) &&
  D.T.nodes.all (fun N => N.mode != .default ||
    N.over.all (fun m => (D.T.nodes.find? (·.name == m)).all (·.mode == .default))) &&
  decide (decisionNames D).Nodup &&
  (decisionNames D).all (fun n => (D.E.predicates n).isNone) &&
  D.T.nodes.all (fun N => (N.guard :: N.carveOuts).all (fun φ => φ.check D.E (sortsOf D N.pred).reverse)) &&
  (softPremisesIn D S L).all (fun φ => φ.check E0 []) &&
  D.T.nodes.all (fun N => (selectsOn S D N).check En (sortsOf D N.pred).reverse) &&
  (collidingPairs D).all (fun x => sortsOf D x.1.pred == sortsOf D x.2.pred) &&
  D.T.regulated.all (fun r => (D.E.predicates r.name).isSome) &&
  D.T.regulated.all (fun r =>
    [strictPos D r.name, strictNeg D r.name, defaultDecidesOn S D r.name true, defaultDecidesOn S D r.name false].all
      (fun φ => φ.check En r.sorts.reverse))

theorem softSemanticCheckOnce_eq (D : SoftDoc) : softSemanticCheckOnce D = softSemanticCheck D := by
  simp only [softSemanticCheckOnce, softSemanticCheck, softPremisesIn_eq, layersOf_syms, defaultDecidesOn,
    defaultPos, defaultNeg, defaultDecidesF, selectsOn_soften, size]

def validateSoftOnce (D : SoftDoc) : Except String Unit :=
  match checkSoftOnce D with
  | .error e => .error e
  | .ok () => if softSemanticCheckOnce D then .ok () else .error "InvalidInput: soft norm document is not stratified"

theorem validateSoftOnce_eq (D : SoftDoc) : validateSoftOnce D = validateSoft D := by
  unfold validateSoftOnce validateSoft
  rw [checkSoftOnce_eq, softSemanticCheckOnce_eq]
  all_goals rfl

end VE.SoftNorms

namespace VE.Rights
open VE.Norms (envAt size)
open VE.SoftNorms (soften)

/-- `validateRights` with soft well-formedness checked by `validateSoftOnce` (lean-first plan F5d). -/
def validateRightsOnce (D : RightsDoc) : Except String Unit :=
  match checkRights D with
  | .error e => .error e
  | .ok () =>
    match VE.SoftNorms.validateSoftOnce (correlate D) with
    | .error e => .error e
    | .ok () =>
      match (VE.SoftNorms.decisionNames (correlate D)).find? (fun n => n.utf8ByteSize > 64) with
      | some n => .error s!"ResourceLimit: identifier {n} exceeds 64 bytes"
      | none => if rightsSemanticCheck D then .ok () else .error "InvalidInput: rights document is not stratified"

theorem validateRightsOnce_eq (D : RightsDoc) : validateRightsOnce D = validateRights D := by
  unfold validateRightsOnce validateRights
  rw [VE.SoftNorms.validateSoftOnce_eq]
  all_goals rfl

end VE.Rights
