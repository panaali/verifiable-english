import VE.EnglishGrammar.Actions
import VE.Route.Gate
import VE.Route.Wire
import VE.Core.Bridge
import VE.Norms.Plain
import VE.Risk.Wire

/-! The wire form of a reading, the typed check of a document, and the environment decoder of the
English instance (docs/spec/english-lean-s2.md 2.3, 2.10 and 2.15).

`EFormula.encode` is Python's `_to_data` (`ve/ast.py`): a predicate of one argument is `unary`, of two
`binary`, of any other number `atom`. `typedDocument` is `check_document`'s verdict, decided by the
decoders the standalone typing service runs (`VE.Service.Standalone.decodeTyped` for `ve.core@0.2`,
`legacyTyped` for the frozen `ve.core@0` and `ve.core@0.1` envelopes): the same functions, called on the
environment JSON the request carried (`Env.source`) and on the encoded formulas. An `atom` node and a
`reach` node outside `closure@0` do not decode, so a formula Python's checker refuses with
`UnsupportedProfile` is refused here too (spec 4.2).

`Env.decode` reads the lexical view and the signatures from the environment and applies an English
vocabulary overlay as Python's `display_environment` does: a sort's noun, a predicate's wording (with
its negative, which never survives a changed positive) and a constant's display form.

S3 (docs/spec/english-lean-s3.md 2.3): `Env.decode` also reads a predicate's `functional` and `total` flags and
description, the `alternatives` block (present exactly when `alternatives@0` is named), and adds what the
profile blocks generate, as Python's display environment does: the four `alternatives@0` words and their forms
and aliases, the severity sort, its classes and the five risk predicates with their forms and negatives, and
under `norms@0` the modal form of each predicate regulated as a permission or an obligation, read from the
canonical act of `Norms.Wire` (F6). The typed check reads the typing view of the environment (2.3, part 2):
under `risk@0` the risk declarations removed as `Risk.Wire.riskNormsView` removes them and the generated risk
symbols declared (`riskView`), under `alternatives@0` the block removed and its four words declared
(`alternativesView`), under `norms@0` the `regulated` extension checked and removed. `riskView` and
`alternativesView` are `VE.Service.Standalone.riskReduced` and `alternativesReduced`, which this layer may not
import; `VE.EnglishGrammar.Run` proves each equal to its original (`riskView_eq`, `alternativesView_eq`).
-/

namespace VE.EnglishGrammar
open Lean VE.Grammar

def ETerm.encode : ETerm → Json
  | .var i => .arr #[.str "var", toJson i]
  | .const c => .arr #[.str "const", .str c]
  | .num v => .arr #[.str "num", .str (toString v)]
  | .add a b => .arr #[.str "add", a.encode, b.encode]
  | .scale k t => .arr #[.str "scale", .str (toString k), t.encode]

/-- The reach kind of the wire: `star` is zero or more steps, `plus` one or more. -/
def reachKind (reflexive : Bool) : Json := .str (if reflexive then "star" else "plus")

def EFormula.encode : EFormula → Json
  | .top => .arr #[.str "top"]
  | .bottom => .arr #[.str "bottom"]
  | .pred p [t] => .arr #[.str "unary", .str p, t.encode]
  | .pred p [t, u] => .arr #[.str "binary", .str p, t.encode, u.encode]
  | .pred p ts => .arr #[.str "atom", .str p, .arr (ts.map ETerm.encode).toArray]
  | .eq t u => .arr #[.str "eq", t.encode, u.encode]
  | .lt t u => .arr #[.str "lt", t.encode, u.encode]
  | .le t u => .arr #[.str "le", t.encode, u.encode]
  | .not a => .arr #[.str "not", a.encode]
  | .and a b => .arr #[.str "and", a.encode, b.encode]
  | .or a b => .arr #[.str "or", a.encode, b.encode]
  | .implies a b => .arr #[.str "implies", a.encode, b.encode]
  | .all s a => .arr #[.str "forall", .str s, a.encode]
  | .ex s a => .arr #[.str "exists", .str s, a.encode]
  | .reachNamed k r t u => .arr #[.str "reach", reachKind k, .arr #[.str "named", .str r], t.encode, u.encode]
  | .reachBody k s a t u =>
    .arr #[.str "reach", reachKind k, .arr #[.str "body", .str s, a.encode], t.encode, u.encode]

/-! ## The typing view (S3 spec 2.3, part 2) -/

/-- `VE.Service.Standalone.alternativesReduced`, word for word (`Run.alternativesView_eq`). -/
def alternativesView (environment : Json) : Except String Json := do
  let block ← environment.getObjVal? "alternatives"
  let chooser ← VE.Bridge.stringField block "chooser"
  let action ← VE.Bridge.stringField block "action"
  let harm ← VE.Bridge.stringField block "harm"
  let word := fun (args : List String) => Json.mkObj [("arguments", toJson args),
    ("description", .str "alternatives@0 profile word")]
  let vocabulary ← environment.getObjVal? "vocabulary"
  let predicates ← VE.Bridge.fields (← vocabulary.getObjVal? "predicates")
  let words := [("avoidable", word [harm, chooser]), ("unavoidable", word [harm, chooser]),
    ("allows", word [action, harm]), ("prevents", word [action, harm])]
  let profiles := (← VE.Route.Gate.profilesOf environment).erase "alternatives@0"
  let fields := (← VE.Bridge.fields environment).filter (·.1 != "alternatives")
  pure (((Json.mkObj fields).setObjVal! "profiles" (toJson profiles)).setObjVal! "vocabulary"
    (vocabulary.setObjVal! "predicates" (Json.mkObj (predicates ++ words))))

/-- `VE.Service.Standalone.riskReduced`, word for word (`Run.riskView_eq`). -/
def riskView (environment : Json) : Except String Json := do
  let ps ← VE.Route.Gate.profilesOf environment
  let block ← environment.getObjVal? "alternatives"
  let severity ← (← environment.getObjVal? "risk").getObjVal? "severity"
  let sort ← VE.Bridge.stringField severity "sort"
  let classes ← VE.Bridge.strings (← severity.getObjVal? "classes")
  let action ← VE.Bridge.stringField block "action"
  let harm ← VE.Bridge.stringField block "harm"
  let view ← VE.Risk.Wire.riskNormsView environment ps
  let view := (view.setObjVal! "alternatives" block).setObjVal! "profiles" (toJson (ps.erase "risk@0"))
  let vocabulary ← view.getObjVal? "vocabulary"
  let sorts ← VE.Bridge.fields (← vocabulary.getObjVal? "sorts")
  let constants ← VE.Bridge.fields (← vocabulary.getObjVal? "constants")
  let predicates ← VE.Bridge.fields (← vocabulary.getObjVal? "predicates")
  let word := fun (args : List String) => Json.mkObj [("arguments", toJson args),
    ("description", .str "risk@0 generated word")]
  let words := [("risk__might_lead_to", word [action, harm]), ("risk__class", word [harm, sort]),
    ("risk__more_severe", word [sort, sort]), ("risk__or_worse", word [harm, sort]),
    ("risk__less_worst", word [action, action])]
  let severityClasses := classes.map fun c => (c, Json.mkObj [("sort", .str sort),
    ("description", .str "risk severity class")])
  pure (view.setObjVal! "vocabulary" (((vocabulary.setObjVal! "sorts"
    (Json.mkObj (sorts ++ [(sort, Json.mkObj [("description", .str "risk severity")])]))).setObjVal! "constants"
    (Json.mkObj (constants ++ severityClasses))).setObjVal! "predicates" (Json.mkObj (predicates ++ words))))

/-- The `regulated` extension checked as `Standalone.validated` checks it, then removed. -/
def regulatedView (environment : Json) : Except String Json := do
  let vocabulary ← environment.getObjVal? "vocabulary"
  let predicates ← VE.Bridge.fields (← vocabulary.getObjVal? "predicates")
  if predicates.any (fun (_, entry) => (entry.getObjVal? "regulated").isOk) then
    let _ ← VE.Norms.Plain.decodeRegulatedAll predicates
    let stripped := predicates.map fun (p, entry) => (p, VE.Risk.Wire.dropField "regulated" entry)
    pure (environment.setObjVal! "vocabulary" (vocabulary.setObjVal! "predicates" (Json.mkObj stripped)))
  else pure environment

/-- The norm-defaults profile affects defaults, not formula typing. The modal form reads the
same placeholder as the source decoder, while the submitted environment remains the identity. -/
def normDefaultsView (environment : Json) : Except String Json := do
  let vocabulary ← environment.getObjVal? "vocabulary"
  let predicates ← VE.Bridge.fields (← vocabulary.getObjVal? "predicates")
  let predicates := predicates.map fun (p, entry) =>
    let entry := match entry.getObjVal? "regulated" with
      | .ok r => if r.getObjValD "default" == .str "unspecified" then
          entry.setObjVal! "regulated" (r.setObjVal! "default" (.str "deny")) else entry
      | .error _ => entry
    (p, entry)
  let profiles := (← VE.Route.Gate.profilesOf environment).erase "norm-defaults@0"
  pure ((environment.setObjVal! "profiles" (toJson profiles)).setObjVal! "vocabulary"
    (vocabulary.setObjVal! "predicates" (Json.mkObj predicates)))

/-- Soft declarations carry ranks and instruction links, not argument sorts. -/
def softNormsView (environment : Json) : Except String Json := do
  let vocabulary ← environment.getObjVal? "vocabulary"
  let predicates ← VE.Bridge.fields (← vocabulary.getObjVal? "predicates")
  let predicates := predicates.map fun (p, entry) =>
    (p, VE.Risk.Wire.dropField "instruction_of" entry)
  let vocabulary := (VE.Risk.Wire.dropField "soft" vocabulary).setObjVal! "predicates" (Json.mkObj predicates)
  let profiles := (← VE.Route.Gate.profilesOf environment).erase "soft-norms@0"
  pure ((environment.setObjVal! "profiles" (toJson profiles)).setObjVal! "vocabulary" vocabulary)

/-- W6 annotations are checked on the submitted environment and absent from the formula typing view. -/
def unitsView (environment : Json) : Except String Json := do
  let vocabulary ← environment.getObjVal? "vocabulary"
  let predicates := VE.Risk.Wire.mapEntries (VE.Risk.Wire.dropField "argument_units")
    (vocabulary.getObjValD "predicates")
  let constants := VE.Risk.Wire.mapEntries (fun e => VE.Risk.Wire.dropField "unit"
    (VE.Risk.Wire.dropField "verbalisation" e)) (vocabulary.getObjValD "constants")
  let vocabulary := (vocabulary.setObjVal! "predicates" predicates).setObjVal! "constants" constants
  let environment := VE.Risk.Wire.dropField "units" (VE.Risk.Wire.dropField "unit_schema" environment)
  pure (environment.setObjVal! "vocabulary" vocabulary)

/-- The typing view of an environment (S3 spec 2.3, part 2): `riskView` under `risk@0`, then
`alternativesView` under `alternatives@0`, then `regulatedView` under `norms@0`. An environment without these
profiles is its own view. -/
def typingView (environment : Json) : Except String Json := do
  let ps := (VE.Route.Gate.profilesOf environment).toOption.getD []
  let env ← if ps.contains "risk@0" then riskView environment else pure environment
  let env ← if ps.contains "alternatives@0" then alternativesView env else pure env
  let env ← if ps.contains "soft-norms@0" then softNormsView env else pure env
  let env ← if ps.contains "norm-defaults@0" then normDefaultsView env else pure env
  let env ← if (environment.getObjVal? "units").isOk && !ps.contains "risk@0" then unitsView env else pure env
  let env ← if ps.contains "norms@0" then regulatedView env else pure env
  let env ← if ps.contains "reports@0" then do
    let vocabulary ← env.getObjVal? "vocabulary"
    let constants ← (← VE.Bridge.fields (← vocabulary.getObjVal? "constants")).mapM fun (c, entry) => do
      pure (c, Json.mkObj ((← VE.Bridge.fields entry).filter (·.1 != "verbalisation")))
    let fields := (← VE.Bridge.fields vocabulary).filter (·.1 != "reports")
    let reduced := env.setObjVal! "profiles"
      (toJson (((VE.Route.Gate.profilesOf env).toOption.getD []).erase "reports@0"))
    pure (reduced.setObjVal! "vocabulary"
      ((Json.mkObj fields).setObjVal! "constants" (Json.mkObj constants)))
    else pure env
  let env := if ps.contains "readings@1" then
    env.setObjVal! "profiles" (toJson (((VE.Route.Gate.profilesOf env).toOption.getD []).erase "readings@1"))
    else env
  if ps.contains "speech-acts@0" then
    let fields := (← VE.Bridge.fields env).filter (·.1 != "speech_acts")
    pure ((Json.mkObj fields).setObjVal! "profiles"
      (toJson (((VE.Route.Gate.profilesOf env).toOption.getD []).erase "speech-acts@0")))
  else pure env

/-- The typed check of a document of encoded formulas against an environment JSON, by the standalone
typing service's decoders, family by family, over the environment's typing view (S3 spec 2.3). -/
def typedCheck (environment ast : Json) : Except String Unit := do
  let language ← VE.Bridge.stringField environment "language"
  if language == "ve.core@0" then
    let v ← VE.Bridge.decodeEnvironment environment
    let _ ← VE.Bridge.decodeDocument v.environment ast
    pure ()
  else if language == "ve.core@0.1" then
    if environment.getObjValD "profiles" == toJson ["order@0", "relational-fol@0"] then
      let v ← VE.Order.Wire.decodeEnvironment environment
      let _ ← VE.Order.Wire.decodeFormulas v.environment ast
      pure ()
    else
      let v ← VE.Closure.Bridge.decodeEnvironment environment
      let _ ← VE.Closure.Bridge.decodeFormulas v.environment ast
      pure ()
  else
    let e ← VE.Route.Gate.decodeEnvelope (← typingView environment)
    VE.Route.AstLimit.check (← ast.getArr?).toList
    match e.family with
    | .fol =>
      let rv ← VE.Route.Wire.decodeVocabulary e.profiles e.vocabulary
      unless rv.definitions.isEmpty || e.profiles.contains "definitions@0" do
        throw "defined declarations require the definitions@0 profile"
      let _ ← VE.Route.Wire.decodeFormulas rv.environment ast (e.profiles.contains "data@0")
      pure ()
    | .closure =>
      let rv ← VE.Route.Wire.decodeVocabulary e.profiles e.vocabulary
      let _ ← VE.Closure.Bridge.decodeFormulas rv.environment ast
      pure ()
    | .closureNary =>
      let v ← VE.Core.Bridge.decodeEnvironment environment
      let _ ← VE.Core.Bridge.decodeFormulas v.environment ast
      pure ()
    | .order =>
      let v ← VE.Route.Wire.decodeOrderVocabulary e.vocabulary
      let _ ← VE.Order.Wire.decodeFormulas v.vocabulary.environment ast
      pure ()

/-- Whether the formulas of a document are well typed under the environment (spec 2.3). -/
def typedDocument (E : Env) (As : List EFormula) : Bool :=
  match typedCheck E.source (.arr (As.map EFormula.encode).toArray) with
  | .ok () => true
  | .error _ => false

/-- An optional string field. -/
def optString (j : Json) (name : String) : Option String :=
  match j.getObjVal? name with
  | .ok (.str s) => some s
  | _ => none

/-- The entries of an optional object field. -/
def optFields (j : Json) (name : String) : Except String (List (String × Json)) :=
  match j.getObjVal? name with
  | .ok o => VE.Bridge.fields o
  | .error _ => pure []

/-- An optional Boolean field, `false` when absent. -/
def optBool (j : Json) (name : String) : Except String Bool :=
  match j.getObjVal? name with
  | .ok b => b.getBool?
  | .error _ => pure false

/-- The `alternatives@0` block of an environment (S3 spec 2.3): present exactly when the profile is named. -/
def decodeAltBlock (environment : Json) (profiles : List String) : Except String (Option AltBlock) := do
  match environment.getObjVal? "alternatives", profiles.contains "alternatives@0" with
  | .ok b, true =>
    let action ← VE.Bridge.stringField b "action"
    let chooser ← VE.Bridge.stringField b "chooser"
    let harm ← VE.Bridge.stringField b "harm"
    let available ← VE.Bridge.stringField b "available"
    let leadsTo ← VE.Bridge.stringField b "leads_to"
    let optional := ["inaction", "taken", "proximate"].filterMap (optString b)
    pure (some { action, chooser, harm, available, leadsTo, optional })
  | .error _, false => pure none
  | _, true => throw "InvalidInput: alternatives@0 is named without its block"
  | _, false => throw "UnsupportedProfile: an alternatives block requires alternatives@0"

/-- The modal form of a regulated predicate (S3 spec 2.3, F6): the canonical act with `{0} ` replaced once by
`{0} may ` or `{0} must `; none for a predicate that is not a permission or an obligation. -/
def modalForm (name : String) (args : List String) (entry : Json) : Except String (Option String) := do
  match entry.getObjVal? "regulated" with
  | .error _ => pure none
  | .ok raw =>
    let r ← VE.Norms.Wire.decodeRegulated name args raw
    match r.role, r.act with
    | .permission, some act => pure (some (replaceFirst act "{0} " "{0} may "))
    | .obligation, some act => pure (some (replaceFirst act "{0} " "{0} must "))
    | _, _ => pure none

/-- The modal reader's placeholder for an unspecified norm default. -/
def placeholderEntry (entry : Json) : Json :=
  match entry.getObjVal? "regulated" with
  | .ok r => if r.getObjValD "default" == .str "unspecified" then
      entry.setObjVal! "regulated" (r.setObjVal! "default" (.str "deny")) else entry
  | .error _ => entry

/-- What the profile blocks generate (S3 spec 2.3; `ve/environment.py:658–680`, `english.py:393–468`): the
sorts, predicates and constants, and the forms they fix. `roles` are the block's role predicates with their
decoded wordings. -/
def blockSymbols (environment : Json) (block : Option AltBlock) (risk : Bool)
    (roles : List (String × String)) :
    Except String (List SortDecl × List PredDecl × List ConstDecl × ProfileForms) := do
  match block with
  | none => pure ([], [], [], {})
  | some B =>
    let gen := fun (name : String) (args : List String) =>
      ({ name, arity := args.length, args, generated := true } : PredDecl)
    let altPreds := [gen "avoidable" [B.harm, B.chooser], gen "unavoidable" [B.harm, B.chooser],
      gen "allows" [B.action, B.harm], gen "prevents" [B.action, B.harm]]
    let altForms : ProfileForms := {
      wordings := roles ++ [("avoidable", "{0} is avoidable by {1}"), ("unavoidable", "{0} is unavoidable by {1}"),
        ("allows", "{0} allows {1} to happen"),
        ("prevents", if risk then "{0} might prevent {1}" else "{0} prevents {1}")],
      aliases := [("avoidable", "{0} is preventable by {1}", false), ("allows", "{0} lets {1} happen", false)] ++
        (if risk then [] else [(B.leadsTo, "{0} does not lead to {1}", true)]) }
    if !risk then pure ([], altPreds, [], altForms)
    else
      let severity ← (← environment.getObjVal? "risk").getObjVal? "severity"
      let sort ← VE.Bridge.stringField severity "sort"
      let classes ← VE.Bridge.strings (← severity.getObjVal? "classes")
      let riskPreds := [gen "risk__might_lead_to" [B.action, B.harm], gen "risk__class" [B.harm, sort],
        gen "risk__more_severe" [sort, sort], gen "risk__or_worse" [B.harm, sort],
        gen "risk__less_worst" [B.action, B.action]]
      pure ([{ name := sort, generated := true }], altPreds ++ riskPreds,
        classes.map fun c => ({ name := c, sort, generated := true } : ConstDecl),
        { altForms with
          wordings := altForms.wordings ++ [("risk__might_lead_to", "{0} might lead to {1}"),
            ("risk__class", "{0} is {1}"), ("risk__or_worse", "{0} is {1} or worse"),
            ("risk__less_worst", "{0} has a less severe worst case than {1}"),
            ("risk__more_severe", "{0} is more severe than {1}")],
          negatives := [(B.leadsTo, "{0} might not lead to {1}"), ("risk__might_lead_to", "{0} cannot lead to {1}")],
          nouns := [(sort, "severity")] })

/-- The environment of the English reader, from the environment JSON and an English vocabulary overlay
(an object with `sorts`, `predicates` and `constants`, or `{}` for none). -/
def Env.decode (environment overlay : Json) : Except String Env := do
  let vocabulary ← environment.getObjVal? "vocabulary"
  let profiles ← match environment.getObjVal? "profiles" with
    | .ok ps => VE.Bridge.strings ps
    | .error _ => do pure [← VE.Bridge.stringField environment "profile"]
  let oSorts ← optFields overlay "sorts"
  let oPreds ← optFields overlay "predicates"
  let oConsts ← optFields overlay "constants"
  let sorts ← (← VE.Bridge.fields (← vocabulary.getObjVal? "sorts")).mapM fun (name, entry) => do
    let selected := match VE.Bridge.lookup oSorts name with
      | some o => o
      | none => entry
    let noun := match VE.Bridge.lookup oSorts name with
      | some o => (o.getObjValD "verbalisation").getObjValD "singular" |>.getStr?.toOption
      | none => (entry.getObjValD "verbalisation").getObjValD "singular" |>.getStr?.toOption
    let plural := optString (selected.getObjValD "verbalisation") "plural"
    pure ({ name, noun, plural } : SortDecl)
  let decoded ← (← VE.Bridge.fields (← vocabulary.getObjVal? "predicates")).mapM fun (name, entry) => do
    let args ← VE.Bridge.strings (← entry.getObjVal? "arguments")
    let (wording, negative) := match VE.Bridge.lookup oPreds name with
      | some o => (optString o "verbalisation", optString o "negative_verbalisation")
      | none => (optString entry "verbalisation", optString entry "negative_verbalisation")
    let modal ← if profiles.contains "norms@0" then
      modalForm name args (if profiles.contains "norm-defaults@0" then placeholderEntry entry else entry)
      else pure none
    pure (({ name, arity := args.length, wording, negative, args, functional := ← optBool entry "functional",
             total := ← optBool entry "total", modal := modal.isSome,
             description := (optString entry "description").getD "",
             suggested := (VE.Bridge.lookup oPreds name).isSome &&
               ((VE.Bridge.lookup oPreds name).map (fun o => (o.getObjValD "suggested") == .bool true)).getD false
             } : PredDecl), modal)
  let predicates := decoded.map (·.1)
  let modalForms := decoded.filterMap fun (d, m) => m.map (d.name, ·)
  let alternatives ← decodeAltBlock environment profiles
  let roles := match alternatives with
    | some _ => (["available", "leads_to", "inaction", "taken", "proximate"].filterMap fun r =>
        optString (environment.getObjValD "alternatives") r).filterMap fun p =>
          ((predicates.find? (·.name == p)).bind (·.wording)).map (p, ·)
    | none => []
  let (gSorts, gPreds, gConsts, forms) ← blockSymbols environment alternatives (profiles.contains "risk@0") roles
  let gConsts := gConsts.map fun c =>
    { c with display := (VE.Bridge.lookup oConsts c.name).bind (optString · "verbalisation") }
  let constants ← (← VE.Bridge.fields (← vocabulary.getObjVal? "constants")).mapM fun (name, entry) => do
    let sort ← VE.Bridge.stringField entry "sort"
    let display := (VE.Bridge.lookup oConsts name).bind (optString · "verbalisation")
    pure ({ name, display, sort } : ConstDecl)
  pure { sorts := sorts ++ gSorts, predicates := predicates ++ gPreds, constants := constants ++ gConsts, profiles,
         forms := { forms with wordings := modalForms ++ forms.wordings }, source := environment, alternatives }

/-- Python's display environment for identity binding: overlay sort and predicate fields replace the
submitted declaration fields; `suggested` is transport metadata, and an old negative is removed. -/
def displayJson (environment overlay : Json) : Json := Id.run do
  let vocabulary := environment.getObjValD "vocabulary"
  let merge (category : String) (dropNegative : Bool) (vocabulary : Json) : Json := Id.run do
    let entries := (VE.Bridge.fields (vocabulary.getObjValD category)).toOption.getD []
    let replacements := (VE.Bridge.fields (overlay.getObjValD category)).toOption.getD []
    let entries := entries.map fun (name, entry) =>
      match VE.Bridge.lookup replacements name with
      | none => (name, entry)
      | some replacement =>
        let base := (VE.Bridge.fields entry).toOption.getD []
        let base := base.filter fun (key, _) => !(dropNegative && key == "negative_verbalisation")
        let changed := ((VE.Bridge.fields replacement).toOption.getD []).filter (·.1 != "suggested")
        (name, Json.mkObj (base.filter (fun (key, _) => !(changed.any (·.1 == key))) ++ changed))
    return vocabulary.setObjVal! category (Json.mkObj entries)
  let vocabulary := merge "sorts" false vocabulary
  let vocabulary := merge "predicates" true vocabulary
  return environment.setObjVal! "vocabulary" vocabulary

def Overlay.decode (overlay : Json) : Except String Overlay := do
  let sorts ← (← optFields overlay "sorts").mapM fun (s, e) => do
    pure (s, ← VE.Bridge.stringField (← e.getObjVal? "verbalisation") "singular")
  let predicates ← (← optFields overlay "predicates").mapM fun (p, e) => do
    pure (p, ← VE.Bridge.stringField e "verbalisation", optString e "negative_verbalisation")
  let constants ← (← optFields overlay "constants").mapM fun (c, e) => do
    pure (c, ← VE.Bridge.stringField e "verbalisation")
  pure { sorts, predicates, constants }

def overlayText : Failure → String
  | ("O1", _, n) => s!"The vocabulary overlay gives {n} a wording that another symbol already has. No text was read."
  | ("O2", _, n) => s!"The vocabulary overlay gives {n} a wording that risk@0 reserves. No text was read."
  | (_, _, n) => s!"The vocabulary overlay entry for {n} cannot be used as written. No text was read."

def ETerm.decode : Json → Option ETerm
  | .arr #[.str "var", i] => (i.getNat?.toOption).map ETerm.var
  | .arr #[.str "const", .str x] => some (.const x)
  | .arr #[.str "num", .str v] => v.toInt?.map ETerm.num
  | .arr #[.str "add", a, b] => do pure (.add (← ETerm.decode a) (← ETerm.decode b))
  | .arr #[.str "scale", .str k, t] => do pure (.scale (← k.toInt?) (← ETerm.decode t))
  | _ => none

def reachRefl : Json → Option Bool
  | .str "star" => some true
  | .str "plus" => some false
  | _ => none

def EFormula.decode : Json → Option EFormula
  | .arr #[.str "top"] => some .top
  | .arr #[.str "bottom"] => some .bottom
  | .arr #[.str "unary", .str p, t] => do pure (.pred p [← ETerm.decode t])
  | .arr #[.str "binary", .str p, t, u] => do pure (.pred p [← ETerm.decode t, ← ETerm.decode u])
  | .arr #[.str "atom", .str p, .arr ts] => do pure (.pred p (← ts.toList.mapM ETerm.decode))
  | .arr #[.str "eq", t, u] => do pure (.eq (← ETerm.decode t) (← ETerm.decode u))
  | .arr #[.str "lt", t, u] => do pure (.lt (← ETerm.decode t) (← ETerm.decode u))
  | .arr #[.str "le", t, u] => do pure (.le (← ETerm.decode t) (← ETerm.decode u))
  | .arr #[.str "not", a] => do pure (.not (← EFormula.decode a))
  | .arr #[.str "and", a, b] => do pure (.and (← EFormula.decode a) (← EFormula.decode b))
  | .arr #[.str "or", a, b] => do pure (.or (← EFormula.decode a) (← EFormula.decode b))
  | .arr #[.str "implies", a, b] => do pure (.implies (← EFormula.decode a) (← EFormula.decode b))
  | .arr #[.str "forall", .str s, a] => do pure (.all s (← EFormula.decode a))
  | .arr #[.str "exists", .str s, a] => do pure (.ex s (← EFormula.decode a))
  | .arr #[.str "reach", k, .arr #[.str "named", .str r], t, u] => do
      pure (.reachNamed (← reachRefl k) r (← ETerm.decode t) (← ETerm.decode u))
  | .arr #[.str "reach", k, .arr #[.str "body", .str s, a], t, u] => do
      pure (.reachBody (← reachRefl k) s (← EFormula.decode a) (← ETerm.decode t) (← ETerm.decode u))
  | _ => none


end VE.EnglishGrammar
