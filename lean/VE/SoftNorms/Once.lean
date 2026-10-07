import VE.SoftNorms.Coherence
import VE.Norms.LayersOnce

/-! The layers of a soft document computed once (lean-first plan F5d).

Validating a soft document (`checkSoft`, `softSemanticCheck`) rebuilt, for every formula it typed or expanded, the
layer order of `soften D` (a topological sort of its stratum DAG), the layered environment `envAt` and the outcome
expansion table `expTable` (`VE.Norms.LayersOnce`): work quartic in the regulated predicates of the environment.
The functions here compute them once per document. Each is declared in the namespace of the function it replaces,
with a lemma that the two are equal, so every theorem about the original holds of the run. The `@[csimp]` lemmas at
the end make the compiler run the hoisted function wherever compiled code calls the original, so every route that
decodes a soft or rights source (soft-norms, rights, readings, admission, the wire-contract hooks) runs it, not only
the readings route (lean-first batch 7 review B1). -/

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

theorem cohPremiseIn_eq (D : SoftDoc) (M N : SoftNode) :
    cohPremiseIn D (soften D) (layersOf (soften D)) M N = cohPremise D M N := by
  simp only [cohPremiseIn, cohPremise, substIn_eq, layersOf_syms, selectsOn_soften, size]

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

/-- `softSemanticCheck` with `soften D`, its two layered environments and its layers computed once. Each is built
    when a conjunct first reads it (a `Thunk`), so a document that fails an earlier conjunct builds none of them, as
    in `softSemanticCheck` (batch 3d review B: a hoisted value keeps the short-circuit of the code it replaces). -/
def softSemanticCheckOnce (D : SoftDoc) : Bool :=
  let S := soften D
  let L := Thunk.mk (fun _ => layersOf S)
  let E0 := Thunk.mk (fun _ => envAt S 0)
  let En := Thunk.mk (fun _ => envAt S L.get.syms.length)
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
  (softPremisesIn D S L.get).all (fun φ => φ.check E0.get []) &&
  D.T.nodes.all (fun N => (selectsOn S D N).check En.get (sortsOf D N.pred).reverse) &&
  (collidingPairs D).all (fun x => sortsOf D x.1.pred == sortsOf D x.2.pred) &&
  D.T.regulated.all (fun r => (D.E.predicates r.name).isSome) &&
  D.T.regulated.all (fun r =>
    [strictPos D r.name, strictNeg D r.name, defaultDecidesOn S D r.name true, defaultDecidesOn S D r.name false].all
      (fun φ => φ.check En.get r.sorts.reverse))

theorem softSemanticCheckOnce_eq (D : SoftDoc) : softSemanticCheckOnce D = softSemanticCheck D := by
  simp only [softSemanticCheckOnce, softSemanticCheck, Thunk.get, softPremisesIn_eq, layersOf_syms, defaultDecidesOn,
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

namespace VE.SoftNorms

/-- `WellFormedSoft` over `validateSoftOnce`. -/
def WellFormedSoftOnce (D : SoftDoc) : Bool :=
  match validateSoftOnce D with
  | .ok () => true
  | .error _ => false

theorem WellFormedSoftOnce_eq (D : SoftDoc) : WellFormedSoftOnce D = WellFormedSoft D := by
  unfold WellFormedSoftOnce WellFormedSoft
  rw [validateSoftOnce_eq]
  all_goals rfl

/-! ## The compiled code runs the hoisted functions

Each lemma below replaces, in code compiled by a module that imports this one, a call of the original by a call of
the hoisted function equal to it. -/

@[csimp] theorem checkSoft_eq_once : @checkSoft = @checkSoftOnce :=
  funext fun D => (checkSoftOnce_eq D).symm

@[csimp] theorem softSemanticCheck_eq_once : @softSemanticCheck = @softSemanticCheckOnce :=
  funext fun D => (softSemanticCheckOnce_eq D).symm

@[csimp] theorem validateSoft_eq_once : @validateSoft = @validateSoftOnce :=
  funext fun D => (validateSoftOnce_eq D).symm

@[csimp] theorem wellFormedSoft_eq_once : @WellFormedSoft = @WellFormedSoftOnce :=
  funext fun D => (WellFormedSoftOnce_eq D).symm

/-- `InFragment` with `soften D` and its layers computed once. -/
def InFragmentOnce (D : SoftDoc) : Bool :=
  let S := soften D
  let L := VE.Norms.layersOf S
  VE.Norms.InFragmentIn S L && (softPremisesIn D S L).all universalQF

theorem InFragmentOnce_eq (D : SoftDoc) : InFragmentOnce D = InFragment D := by
  simp only [InFragmentOnce, InFragment, VE.Norms.InFragmentIn_eq, softPremisesIn_eq]

@[csimp] theorem inFragment_eq_once : @InFragment = @InFragmentOnce :=
  funext fun D => (InFragmentOnce_eq D).symm

end VE.SoftNorms
