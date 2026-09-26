import VE.Route.Background
import VE.Data.Background
import VE.CertificateWire
import VE.Order.Wire
import VE.Order.ModelCheck
import VE.Closure.Bridge

/-! Wire decoding for the `route` subcommand (`ve.core@0.2`). The envelope is
decoded by `Gate.decodeEnvelope`; the vocabulary by the family's decoder, which
on every family additionally admits the built-in sort `$string` for declared
literal constants (at most 64; the description is optional, PLAN-EXPAND2 W5).
Stage 1 is equality only: `$string` is never a predicate argument and never a
quantifiable sort (it is not in the environment's `sorts`, so `Formula.check`
rejects `∀`/`∃` over it). Background is regenerated from the
decoded literals; the wire never supplies it. Identity uses the domain
`ve-<kind>-v0.2:<sorted profiles>` (PLAN-EXPAND2 rule 3). -/
namespace VE.Route.Wire
open Lean
open VE.Bridge (exactFields fields stringField strings identifier reserved generatedName)

/-- A decoded FOL/closure vocabulary and its declared `$string` literals. -/
structure RouteVocabulary where
  vocabulary : VE.Bridge.Vocabulary
  literals : List String
  nodup : literals.Nodup
  flags : List VE.Data.Background.Flag := []

def RouteVocabulary.environment (rv : RouteVocabulary) : VE.Environment :=
  let E := rv.vocabulary.environment
  { E with sorts := E.sorts ++
      (if rv.flags.any (fun f => f.source == Background.stringSort ||
                                   f.target == Background.stringSort) then [Background.stringSort] else []) }

/-- The model tables list `$string` as a domain whenever a literal is declared
(Python `Environment.model_sorts`). -/
def RouteVocabulary.modelVocabulary (rv : RouteVocabulary) : VE.Bridge.Vocabulary :=
  { rv.vocabulary with
    sorts := rv.vocabulary.sorts ++
      (if rv.literals.isEmpty && !(rv.vocabulary.predicates.any (fun p =>
          p.2.contains Background.stringSort))
       then [] else [Background.stringSort]) }

/-- A declared `$string` literal: the sort is required and the description is
optional (and nonempty when present). -/
def literalEntry (entry : Json) : Except String Unit := do
  VE.Bridge.displayFields entry ["sort"] ["description"]
  if let .ok _ := entry.getObjVal? "description" then VE.Bridge.description entry

def isLiteralEntry (entry : Json) : Bool :=
  entry.getObjValD "sort" == .str Background.stringSort

/-- The v0 vocabulary rules plus `$string` as the sort of declared literal
constants. -/
def decodeVocabulary (profiles : List String) (v : Json) : Except String RouteVocabulary := do
  exactFields v ["sorts", "predicates", "constants"]
  let sorts ← fields (← v.getObjVal? "sorts")
  let predicates ← fields (← v.getObjVal? "predicates")
  let constants ← fields (← v.getObjVal? "constants")
  let names := (sorts ++ predicates ++ constants).map Prod.fst
  unless names.eraseDups.length == names.length do throw "duplicate declaration"
  for name in names do
    unless identifier name && !reserved.contains name && !generatedName name do
      throw s!"invalid or reserved declaration: {name}"
  if sorts.length > 32 || predicates.length > 256 then
    throw "ResourceLimit: vocabulary size"
  for (_, entry) in sorts do
    VE.Bridge.displayFields entry ["description"] ["verbalisation"]
    VE.Bridge.description entry
    if let .ok words := entry.getObjVal? "verbalisation" then
      exactFields words ["singular", "plural"]
      VE.Bridge.displayString (← words.getObjVal? "singular")
      VE.Bridge.displayString (← words.getObjVal? "plural")
  let sortNames := sorts.map Prod.fst
  let allowed := fun (s : String) => sortNames.contains s || s == Background.stringSort
  let flagged := profiles.contains "data@0"
  let psAndFlags ← predicates.mapM fun (p, entry) => do
    if (entry.getObjVal? "defined" |>.isOk) &&
        ((entry.getObjVal? "functional" |>.isOk) || (entry.getObjVal? "total" |>.isOk)) then
      throw "UnsupportedProfile: Defined predicates cannot carry functional or total flags"
    VE.Bridge.displayFields entry ["arguments", "description"]
      (["verbalisation", "negative_verbalisation"] ++
        (if flagged then ["functional", "total"] else []))
    VE.Bridge.description entry
    for key in ["verbalisation", "negative_verbalisation"] do
      if let .ok words := entry.getObjVal? key then
        VE.Bridge.displayString words
    let ss ← strings (← entry.getObjVal? "arguments")
    unless (ss.length == 1 || ss.length == 2) &&
      ss.all (fun s => sortNames.contains s || (flagged && s == Background.stringSort)) do
      throw s!"invalid signature: {p}"
    let functional ← match entry.getObjVal? "functional" with
      | .ok b => b.getBool?
      | .error _ => pure false
    let total ← match entry.getObjVal? "total" with
      | .ok b => b.getBool?
      | .error _ => pure false
    if (entry.getObjVal? "functional" |>.isOk) || (entry.getObjVal? "total" |>.isOk) then
      unless ss.length == 2 do throw "flags require a binary predicate"
    let flag : Option VE.Data.Background.Flag :=
      if functional || total then some ⟨p, ss[0]!, ss[1]!, functional, total⟩ else none
    pure ((p, ss), flag)
  let ps := psAndFlags.map Prod.fst
  let flags := psAndFlags.filterMap Prod.snd
  let cs ← constants.mapM fun (c, entry) => do
    if isLiteralEntry entry then literalEntry entry
    else
      exactFields entry ["sort", "description"]
      VE.Bridge.description entry
    let s ← stringField entry "sort"
    unless allowed s do throw s!"unknown constant sort: {c}"
    pure (c, s)
  let literals := (cs.filter (fun c => c.2 == Background.stringSort)).map Prod.fst
  if literals.length > 64 then throw "ResourceLimit: At most 64 declared $string literals"
  let result : VE.Bridge.Vocabulary := ⟨sortNames, ps, cs⟩
  unless result.namesValid do throw "invalid declaration names"
  if h : literals.Nodup then pure ⟨result, literals, h, flags⟩ else throw "duplicate declaration"

/-- A decoded order vocabulary and its declared `$string` literals. -/
structure RouteOrderVocabulary where
  vocabulary : VE.Order.Vocabulary
  literals : List String
  nodup : literals.Nodup

/-- Model tables list `$string` as a domain whenever a literal is declared. -/
def RouteOrderVocabulary.modelVocabulary (rv : RouteOrderVocabulary) : VE.Order.Vocabulary :=
  { rv.vocabulary with
    sorts := rv.vocabulary.sorts ++ (if rv.literals.isEmpty then [] else [Background.stringSort]) }

/-- The order vocabulary: the numbers2 order decoder, unchanged, applied to the
vocabulary without its `$string` literals; each literal is then declared as a
constant of the user sort `$string`, which is not in `sorts` (so never
quantified over) and is never a predicate argument. -/
def decodeOrderVocabulary (v : Json) : Except String RouteOrderVocabulary := do
  exactFields v ["sorts", "predicates", "constants"]
  let constants ← fields (← v.getObjVal? "constants")
  let literalDecls := constants.filter (fun c => isLiteralEntry c.2)
  for (_, entry) in literalDecls do literalEntry entry
  let literals := literalDecls.map Prod.fst
  if literals.length > 64 then throw "ResourceLimit: At most 64 declared $string literals"
  let others := constants.filter (fun c => !isLiteralEntry c.2)
  let base ← VE.Order.Wire.decodeEnvironment (Json.mkObj [
    ("language", .str VE.Order.Wire.orderLanguage),
    ("profiles", toJson VE.Order.Wire.orderProfiles),
    ("spec_revision", .str VE.Order.Wire.orderRevision),
    ("vocabulary", Json.mkObj [("sorts", v.getObjValD "sorts"),
      ("predicates", v.getObjValD "predicates"), ("constants", Json.mkObj others)])])
  let declared := base.sorts ++ base.predicates.map Prod.fst ++ base.constants.map Prod.fst
  for name in literals do
    unless identifier name && !reserved.contains name && !generatedName name do
      throw s!"invalid or reserved declaration: {name}"
    if declared.contains name then throw "duplicate declaration"
  let vocabulary : VE.Order.Vocabulary := { base with
    constants := base.constants ++ literals.map (fun c => (c, .user Background.stringSort)) }
  if h : literals.Nodup then pure ⟨vocabulary, literals, h⟩ else throw "duplicate declaration"

/-! ## Identity -/

def identityVersion (profiles : List String) : String := "v0.2:" ++ ",".intercalate profiles

def environmentId (profiles : List String) (environment : Json) : Except String String :=
  VE.CertificateWire.digest s!"ve-environment-{identityVersion profiles}\n" environment

def meaningId (profiles : List String) (environmentId : String) (ast : Json) : Except String String :=
  VE.CertificateWire.digest s!"ve-meaning-{identityVersion profiles}\n"
    (Json.mkObj [("environment_id", .str environmentId), ("ast", ast)])

/-! ## Formula encoding (Background ASTs are generated, then bound by meaning id) -/

def encodeTerm : VE.Term → Json
  | .var i => Json.arr #[.str "var", toJson i]
  | .const c => Json.arr #[.str "const", .str c]

def encodeFormula : VE.Formula → Json
  | .top => Json.arr #[.str "top"]
  | .bottom => Json.arr #[.str "bottom"]
  | .unary p t => Json.arr #[.str "unary", .str p, encodeTerm t]
  | .binary p t u => Json.arr #[.str "binary", .str p, encodeTerm t, encodeTerm u]
  | .eq t u => Json.arr #[.str "eq", encodeTerm t, encodeTerm u]
  | .not a => Json.arr #[.str "not", encodeFormula a]
  | .and a b => Json.arr #[.str "and", encodeFormula a, encodeFormula b]
  | .or a b => Json.arr #[.str "or", encodeFormula a, encodeFormula b]
  | .implies a b => Json.arr #[.str "implies", encodeFormula a, encodeFormula b]
  | .all s a => Json.arr #[.str "forall", .str s, encodeFormula a]
  | .ex s a => Json.arr #[.str "exists", .str s, encodeFormula a]

/-! ## Models: structural admissibility, then Background validity -/

/-- The first Background premise the model violates, with its generator. -/
def backgroundViolation {α : Type} [DecidableEq α] (M : VE.FiniteModel α) (lits : List String) :
    Option String :=
  ((Background.background lits).find? (fun p => !p.1.eval M [])).map Prod.snd

def invalidModel (generator : String) : String :=
  s!"InvalidModel({generator}): the model violates a background premise"

/-- Decode finite tables, check structural admissibility, then Background: a
model aliasing two declared literals is `InvalidModel(literals)`, never a truth
value. -/
def decodeModel (rv : RouteVocabulary) (j : Json) : Except String (VE.FiniteModel VE.Bridge.Entity) := do
  let data ← VE.Bridge.decodeModelData rv.modelVocabulary j
  Gate.require (data.valid rv.modelVocabulary) "model is not semantically admissible"
  let M := data.toModel
  match backgroundViolation M rv.literals with
  | some g => throw (invalidModel g)
  | none => pure M

theorem backgroundViolation_none {α : Type} [DecidableEq α] (M : VE.FiniteModel α)
    (lits : List String) (h : backgroundViolation M lits = none) : Background.literalsValid M lits = true := by
  unfold backgroundViolation at h
  apply List.all_eq_true.mpr
  intro a ha
  have hn := List.find?_eq_none.mp (Option.map_eq_none_iff.mp h) (a, "literals")
    (List.mem_map.mpr ⟨a, ha, rfl⟩)
  simpa using hn

open VE.Order.ProfileGate in
/-- A decoded model is admissible for the environment and satisfies the
stage-1 meaning of strings: it is a string-admissible structure. -/
theorem decodeModel_valid (rv : RouteVocabulary) (j : Json) (M : VE.FiniteModel VE.Bridge.Entity)
    (h : decodeModel rv j = .ok M) :
    Background.StringAdmissible rv.environment rv.literals M.asStructure := by
  unfold decodeModel at h
  obtain ⟨data, _, h⟩ := bind_ok h
  obtain ⟨_, hv, h⟩ := bind_ok h
  have hvalid : data.valid rv.modelVocabulary = true := Gate.require_ok hv
  dsimp only at h
  split at h
  · cases h
  · rename_i hn
    cases h
    exact ⟨VE.Bridge.modelData_valid data rv.modelVocabulary hvalid,
      Background.literalsValid_sound _ rv.literals rv.nodup (backgroundViolation_none _ _ hn)⟩

/-- The data profile rejects a finite table that violates a generated flag
premise before any evaluation or countermodel verdict. -/
def decodeDataModel (rv : RouteVocabulary) (j : Json) :
    Except String (VE.FiniteModel VE.Bridge.Entity) := do
  let data ← VE.Bridge.decodeModelData rv.modelVocabulary j
  Gate.require (data.valid rv.modelVocabulary) "model is not semantically admissible"
  let M := data.toModel
  unless VE.Data.Background.flagsValid M rv.flags do
    throw (invalidModel "flags")
  match backgroundViolation M rv.literals with
  | some g => throw (invalidModel g)
  | none => pure M

/-- Runtime model admission enforces both parts of the reviewed data meaning:
distinct declared literals and functional/total relation tables. -/
theorem decodeDataModel_valid (rv : RouteVocabulary) (j : Json)
    (M : VE.FiniteModel VE.Bridge.Entity) (h : decodeDataModel rv j = .ok M) :
    Background.StringAdmissible rv.environment rv.literals M.asStructure ∧
      ∀ f ∈ rv.flags, VE.Data.Background.Intended M.asStructure f := by
  unfold decodeDataModel at h
  obtain ⟨data, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, hv, h⟩ := VE.Order.ProfileGate.bind_ok h
  have hvalid : data.valid rv.modelVocabulary = true := Gate.require_ok hv
  dsimp only at h
  split at h
  · rename_i hf
    split at h
    · cases h
    · rename_i hl
      cases h
      refine ⟨⟨VE.Bridge.modelData_valid data rv.modelVocabulary hvalid,
        Background.literalsValid_sound _ rv.literals rv.nodup
          (backgroundViolation_none _ _ hl)⟩, ?_⟩
      exact VE.Data.Background.flags_model_valid _ rv.flags (by simpa using hf)
  · cases h

def usesStringBinder : VE.Formula → Bool
  | .all s a | .ex s a => s == Background.stringSort || usesStringBinder a
  | .not a => usesStringBinder a
  | .and a b | .or a b | .implies a b => usesStringBinder a || usesStringBinder b
  | _ => false

def closureUsesStringBinder : VE.Closure.Formula → Bool
  | .all s a | .ex s a => s == Background.stringSort || closureUsesStringBinder a
  | .not a => closureUsesStringBinder a
  | .and a b | .or a b | .implies a b =>
      closureUsesStringBinder a || closureUsesStringBinder b
  | .reachBody _ s a _ _ => s == Background.stringSort || closureUsesStringBinder a
  | _ => false

/-! ## Formula decoding for the FOL family -/

def decodeFormulas (E : VE.Environment) (j : Json) (data : Bool := false) :
    Except String (List VE.Formula) := do
  let fs ← (← j.getArr?).toList.mapM (VE.Bridge.decodeFormula 64)
  if data && fs.any usesStringBinder then throw "UnsupportedProfile: $string quantification requires data stage 2"
  unless fs.all (fun a => a.check E []) do throw "ill-typed or unbound formula"
  if (fs.map VE.Bridge.formulaNodes).foldl (· + ·) 0 > 10000 then throw "ResourceLimit: AST node count"
  pure fs

def decodeClosed (E : VE.Environment) (j : Json) (data : Bool := false) : Except String VE.Formula := do
  let a ← VE.Bridge.decodeFormula 64 j
  if data && usesStringBinder a then throw "UnsupportedProfile: $string quantification requires data stage 2"
  unless a.check E [] do throw "ill-typed or unbound conclusion"
  pure a

/-- The certificate binds the environment, every checked premise (Background
first, then the case's premises) and the conclusion by meaning id. -/
def bindingOk (profiles : List String) (environment : Json) (premises : List Json)
    (conclusion : Json) (environmentIdField : String) (premiseIds : List String)
    (conclusionId : String) : Except String Unit := do
  let envId ← environmentId profiles environment
  let ps ← premises.mapM (meaningId profiles envId)
  let c ← meaningId profiles envId conclusion
  unless environmentIdField == envId && premiseIds == ps && conclusionId == c do
    throw "certificate is stale or bound to different inputs"

def ok (id : String) (fields : List (String × Json)) : Json :=
  Json.mkObj ([("id", .str id), ("status", .str "ok")] ++ fields)

/-- FOL family: evaluate, countermodel and certificate cases. -/
def runFol (profiles : List String) (environment : Json) (rv : RouteVocabulary) (id kind : String)
    (j : Json) : Except String Json := do
  let E := rv.environment
  if kind == "background" then
    let flagPremises := VE.Data.Background.generate rv.flags
    let literalPremises := Background.literals rv.literals
    return ok id [("premises", toJson ((flagPremises ++ literalPremises).map encodeFormula)),
      ("generators", toJson ((List.replicate flagPremises.length "flags") ++
        (List.replicate literalPremises.length "literals")))]
  if kind == "evaluate" then
    let M ← decodeDataModel rv (← j.getObjVal? "model")
    let fs ← decodeFormulas E (← j.getObjVal? "ast") (profiles.contains "data@0")
    if fs.isEmpty then throw "empty document"
    return ok id [("values", toJson (fs.map (fun a => a.eval M [])))]
  let premisesJson ← j.getObjVal? "premises"
  let ps ← decodeFormulas E premisesJson (profiles.contains "data@0")
  let c ← decodeClosed E (← j.getObjVal? "conclusion") (profiles.contains "data@0")
  if kind == "countermodel" then
    let M ← decodeDataModel rv (← j.getObjVal? "model")
    return ok id [("refutes", .bool (VE.countermodelCheck M ps c))]
  unless kind == "certificate" do throw "unknown case kind"
  let certificate ← VE.CertificateWire.decodeCertificate (← j.getObjVal? "certificate")
  let background := VE.Data.Background.generate rv.flags ++ Background.literals rv.literals
  bindingOk profiles environment (background.map encodeFormula ++ (← premisesJson.getArr?).toList)
    (← j.getObjVal? "conclusion") certificate.environment_id certificate.premise_meaning_ids
    certificate.conclusion_meaning_id
  return ok id [("valid", .bool (VE.Tableau.checkCertificate E (background ++ ps) c certificate)),
    ("background", toJson background.length)]

/-- Closure family: the same cases over closure formulas; Background embedded. -/
def runClosure (profiles : List String) (environment : Json) (rv : RouteVocabulary) (id kind : String)
    (j : Json) : Except String Json := do
  let E := rv.environment
  if kind == "background" then
    let flagPremises := VE.Data.Background.generate rv.flags
    let literalPremises := Background.literals rv.literals
    return ok id [("premises", toJson ((flagPremises ++ literalPremises).map encodeFormula)),
      ("generators", toJson ((List.replicate flagPremises.length "flags") ++
        (List.replicate literalPremises.length "literals")))]
  if kind == "evaluate" then
    let M ← decodeDataModel rv (← j.getObjVal? "model")
    let fs ← VE.Closure.Bridge.decodeFormulas E (← j.getObjVal? "ast")
    if profiles.contains "data@0" && fs.any closureUsesStringBinder then
      throw "$string quantification requires data stage 2"
    if fs.isEmpty then throw "empty document"
    return ok id [("values", toJson (fs.map (fun a => a.eval M [])))]
  let premisesJson ← j.getObjVal? "premises"
  let ps ← VE.Closure.Bridge.decodeFormulas E premisesJson
  if profiles.contains "data@0" && ps.any closureUsesStringBinder then
    throw "$string quantification requires data stage 2"
  let c ← VE.Closure.Bridge.decodeFormula 64 (← j.getObjVal? "conclusion")
  if profiles.contains "data@0" && closureUsesStringBinder c then
    throw "$string quantification requires data stage 2"
  unless c.check E [] do throw "ill-typed or unbound conclusion"
  if ((c :: ps).map VE.Closure.Bridge.formulaNodes).foldl (· + ·) 0 > 10000 then
    throw "ResourceLimit: AST node count"
  if kind == "countermodel" then
    let M ← decodeDataModel rv (← j.getObjVal? "model")
    return ok id [("refutes", .bool (VE.Closure.countermodelCheck M ps c))]
  unless kind == "certificate" do throw "unknown case kind"
  let certificate ← VE.CertificateWire.decodeClosureCertificate (← j.getObjVal? "certificate")
  let background := VE.Data.Background.generate rv.flags ++ Background.literals rv.literals
  bindingOk profiles environment (background.map encodeFormula ++ (← premisesJson.getArr?).toList)
    (← j.getObjVal? "conclusion") certificate.environment_id certificate.premise_meaning_ids
    certificate.conclusion_meaning_id
  return ok id [("valid", .bool (VE.Closure.Tableau.checkCertificate E
      (background.map VE.Closure.embed ++ ps) c certificate)),
    ("background", toJson background.length)]

/-- An order model: decoded, structurally admissible, then Background
(`InvalidModel(literals)` on aliasing literals, never a truth value). -/
def decodeOrderModel (rv : RouteOrderVocabulary) (j : Json) :
    Except String (VE.Order.ModelData VE.Order.Wire.Entity) := do
  let d ← VE.Order.Wire.decodeValidModel rv.modelVocabulary j
  unless Background.orderLiteralsValid d.toModel rv.literals do throw (invalidModel "literals")
  pure d

open VE.Order.ProfileGate in
/-- Every decoded order model satisfies the regenerated string premises. -/
theorem decodeOrderModel_valid (rv : RouteOrderVocabulary) (j : Json)
    (d : VE.Order.ModelData VE.Order.Wire.Entity) (h : decodeOrderModel rv j = .ok d) :
    Background.orderLiteralsValid d.toModel rv.literals = true := by
  unfold decodeOrderModel at h
  obtain ⟨decoded, _, h⟩ := bind_ok h
  dsimp only at h
  split at h
  · rename_i hv
    cases h
    simpa using hv
  · cases h

/-- Order family: the numbers2 order decoders; Background is the order form of
`literals`, regenerated from the declared literals and bound like the others. -/
def runOrder (profiles : List String) (environment : Json) (rv : RouteOrderVocabulary) (id kind : String)
    (j : Json) : Except String Json := do
  let E := rv.vocabulary.environment
  if kind == "evaluate" then
    let d ← decodeOrderModel rv (← j.getObjVal? "model")
    let fs ← VE.Order.Wire.decodeFormulas E (← j.getObjVal? "ast")
    if fs.isEmpty then throw "empty document"
    return ok id [("values", toJson (fs.map (fun a => a.eval d.toModel [])))]
  let premisesJson ← j.getObjVal? "premises"
  let ps ← VE.Order.Wire.decodeFormulas E premisesJson
  let c ← VE.Order.Wire.decodeFormula 64 (← j.getObjVal? "conclusion")
  unless c.check E [] do throw "ill-typed or unbound conclusion"
  if ((c :: ps).map VE.Order.Wire.formulaNodes).foldl (· + ·) 0 > 10000 then
    throw "ResourceLimit: AST node count"
  if kind == "countermodel" then
    let d ← decodeOrderModel rv (← j.getObjVal? "model")
    return ok id [("refutes", .bool (VE.Order.checkCountermodel rv.vocabulary d ps c))]
  unless kind == "certificate" do throw "unknown case kind"
  let certificate ← VE.Order.Wire.decodeCertificate (← j.getObjVal? "certificate")
  let background := Background.orderLiterals rv.literals
  bindingOk profiles environment
    ((Background.literals rv.literals).map encodeFormula ++ (← premisesJson.getArr?).toList)
    (← j.getObjVal? "conclusion") certificate.environment_id certificate.premise_meaning_ids
    certificate.conclusion_meaning_id
  return ok id [("valid", .bool (VE.Order.Tableau.checkCertificate E (background ++ ps) c certificate)),
    ("background", toJson background.length)]

/-- The dependency-order case: nodes `{"name", "mentions"}`; the result is the
route order or the shared cycle diagnostic. -/
def decodeNodes (j : Json) : Except String (List DepNode) := do
  let items := (← j.getArr?).toList
  if items.length > 256 then throw "ResourceLimit: dependency graph size"
  items.mapM fun item => do
    exactFields item ["name", "mentions"]
    pure ⟨← stringField item "name", ← strings (← item.getObjVal? "mentions")⟩

def runDependencyOrder (id : String) (j : Json) : Except String Json := do
  let nodes ← decodeNodes (← j.getObjVal? "nodes")
  let order ← dependencyOrder nodes
  pure (ok id [("order", toJson order)])

end VE.Route.Wire
