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

/-- The decimal text of an integer, the text `toString` gives (`E2Examples` checks the two agree): digits, with `-`
before a negative. `toString` joins the sign with `String.Internal.append`, a runtime primitive with no
definition the logic can unfold, so `decode_encode` could not be proved of it; `++` here is `String.append`, which
the logic unfolds. -/
def intText : Int → String
  | .ofNat n => toString n
  | .negSucc n => "-" ++ toString (n + 1)

def ETerm.encode : ETerm → Json
  | .var i => .arr #[.str "var", toJson i]
  | .const c => .arr #[.str "const", .str c]
  | .num v => .arr #[.str "num", .str (intText v)]
  | .add a b => .arr #[.str "add", a.encode, b.encode]
  | .scale k t => .arr #[.str "scale", .str (intText k), t.encode]

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

/-- The text of an overlay refusal; the mode appends what it did not do (`Run.notDone`). -/
def overlayText : Failure → String
  | ("O1", _, n) => s!"The vocabulary overlay gives {n} a wording that another symbol already has."
  | ("O2", _, n) => s!"The vocabulary overlay gives {n} a wording that risk@0 reserves."
  | (_, _, n) => s!"The vocabulary overlay entry for {n} cannot be used as written."

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


/-! ## `decode_encode` (spec 5.5)

Decoding the wire form gives the formula back. The integer text is read back by `String.toInt?`, which works on
byte positions; the lemmas below compute its loops over a character list, and the decimal digits of `toString`. -/

namespace DecodeEncode

theorem go_append (a b : List Char) :
    String.utf8ByteSize.go (a ++ b) = String.utf8ByteSize.go a + String.utf8ByteSize.go b := by
  induction a with
  | nil => simp [String.utf8ByteSize.go]
  | cons c a ih => simp only [List.cons_append, String.utf8ByteSize.go, ih]; omega

theorem go_cons (c : Char) (a : List Char) :
    String.utf8ByteSize.go (c :: a) = String.utf8ByteSize.go a + c.utf8Size := rfl

theorem go_nil : String.utf8ByteSize.go [] = 0 := rfl

theorem pos_add_char (i : Nat) (c : Char) : (String.Pos.mk i + c) = String.Pos.mk (i + c.utf8Size) := rfl

theorem getAux_at (pre rest : List Char) (c : Char) (i : Nat) :
    String.utf8GetAux (pre ++ c :: rest) ⟨i⟩ ⟨i + String.utf8ByteSize.go pre⟩ = c := by
  induction pre generalizing i with
  | nil => simp [String.utf8GetAux, String.utf8ByteSize.go]
  | cons d pre ih =>
    have hp := d.utf8Size_pos
    simp only [List.cons_append, String.utf8GetAux, go_cons]
    rw [if_neg (fun h => by have := congrArg String.Pos.byteIdx h; simp at this; omega)]
    rw [pos_add_char, show i + (String.utf8ByteSize.go pre + d.utf8Size) =
      i + d.utf8Size + String.utf8ByteSize.go pre by omega]
    exact ih _

theorem get_at (pre rest : List Char) (c : Char) :
    String.get ⟨pre ++ c :: rest⟩ ⟨String.utf8ByteSize.go pre⟩ = c := by
  have := getAux_at pre rest c 0
  simpa [String.get] using this

theorem foldlAux_at {α : Type} (f : α → Char → α) (pre rest : List Char) (a : α) :
    String.foldlAux f ⟨pre ++ rest⟩ ⟨String.utf8ByteSize.go (pre ++ rest)⟩ ⟨String.utf8ByteSize.go pre⟩ a =
      rest.foldl f a := by
  induction rest generalizing pre a with
  | nil =>
    rw [String.foldlAux]; simp
  | cons c rest ih =>
    rw [String.foldlAux]
    have hp := c.utf8Size_pos
    rw [dif_pos (by
      show String.utf8ByteSize.go pre < String.utf8ByteSize.go (pre ++ c :: rest)
      simp only [go_append, go_cons]; omega)]
    have hn : String.next ⟨pre ++ c :: rest⟩ ⟨String.utf8ByteSize.go pre⟩ =
        ⟨String.utf8ByteSize.go (pre ++ [c])⟩ := by
      simp only [String.next, get_at, go_append, go_cons, go_nil, Nat.zero_add]; rfl
    simp only [hn, get_at]
    have := ih (pre ++ [c]) (f a c)
    simp only [List.append_assoc, List.singleton_append] at this
    exact this

theorem anyAux_at (p : Char → Bool) (pre rest : List Char) :
    String.anyAux ⟨pre ++ rest⟩ ⟨String.utf8ByteSize.go (pre ++ rest)⟩ p ⟨String.utf8ByteSize.go pre⟩ =
      rest.any p := by
  induction rest generalizing pre with
  | nil => rw [String.anyAux]; simp
  | cons c rest ih =>
    rw [String.anyAux]
    have hp := c.utf8Size_pos
    rw [dif_pos (by
      show String.utf8ByteSize.go pre < String.utf8ByteSize.go (pre ++ c :: rest)
      simp only [go_append, go_cons]; omega)]
    have hn : String.next ⟨pre ++ c :: rest⟩ ⟨String.utf8ByteSize.go pre⟩ =
        ⟨String.utf8ByteSize.go (pre ++ [c])⟩ := by
      simp only [String.next, get_at, go_append, go_cons, go_nil, Nat.zero_add]; rfl
    simp only [hn, get_at]
    have := ih (pre ++ [c])
    simp only [List.append_assoc, List.singleton_append] at this
    rw [this]; simp

theorem digitChar_facts (n : Nat) (h : n < 10) :
    (Nat.digitChar n).isDigit = true ∧ (Nat.digitChar n).toNat - '0'.toNat = n ∧ Nat.digitChar n ≠ '-' := by
  match n with
  | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 => decide
  | n + 10 => omega

theorem toDigitsCore_digits (fuel n : Nat) (ds : List Char) (h : ∀ c ∈ ds, c.isDigit = true ∧ c ≠ '-') :
    ∀ c ∈ Nat.toDigitsCore 10 fuel n ds, c.isDigit = true ∧ c ≠ '-' := by
  induction fuel generalizing n ds with
  | zero => exact h
  | succ fuel ih =>
    have hd := digitChar_facts (n % 10) (Nat.mod_lt _ (by decide))
    simp only [Nat.toDigitsCore]
    split
    · intro c hc
      simp only [List.mem_cons] at hc
      rcases hc with rfl | hc
      · exact ⟨hd.1, hd.2.2⟩
      · exact h c hc
    · apply ih
      intro c hc
      simp only [List.mem_cons] at hc
      rcases hc with rfl | hc
      · exact ⟨hd.1, hd.2.2⟩
      · exact h c hc

theorem toDigitsCore_value (fuel n : Nat) (ds : List Char) (h : n < fuel) :
    (Nat.toDigitsCore 10 fuel n ds).foldl (fun v c => v * 10 + (c.toNat - '0'.toNat)) 0 =
      ds.foldl (fun v c => v * 10 + (c.toNat - '0'.toNat)) n := by
  induction fuel generalizing n ds with
  | zero => omega
  | succ fuel ih =>
    have hd := (digitChar_facts (n % 10) (Nat.mod_lt _ (by decide))).2.1
    simp only [Nat.toDigitsCore]
    split
    next =>
      simp only [List.foldl_cons, Nat.zero_mul, Nat.zero_add, hd]
      have : n % 10 = n := by omega
      rw [this]
    next =>
      rw [ih (n / 10) _ (by omega)]
      simp only [List.foldl_cons, hd]
      congr 1
      omega

theorem toDigitsCore_ne_nil (fuel n : Nat) (ds : List Char) (h : 0 < fuel) :
    Nat.toDigitsCore 10 fuel n ds ≠ [] := by
  induction fuel generalizing n ds with
  | zero => omega
  | succ fuel ih =>
    simp only [Nat.toDigitsCore]
    split
    · simp
    · cases fuel with
      | zero =>
        simp [Nat.toDigitsCore]
      | succ f => exact ih _ _ (by omega)

theorem toString_nat (n : Nat) : toString n = ⟨Nat.toDigits 10 n⟩ := rfl

theorem string_foldl {α : Type} (f : α → Char → α) (a : α) (cs : List Char) :
    String.foldl f a ⟨cs⟩ = cs.foldl f a := by
  have := foldlAux_at f [] cs a
  simpa [String.foldl, String.endPos, String.utf8ByteSize, go_nil] using this

theorem string_any (p : Char → Bool) (cs : List Char) : String.any ⟨cs⟩ p = cs.any p := by
  have := anyAux_at p [] cs
  simpa [String.any, String.endPos, String.utf8ByteSize, go_nil] using this

theorem go_pos (c : Char) (cs : List Char) : String.utf8ByteSize.go (c :: cs) ≠ 0 := by
  have := c.utf8Size_pos; rw [go_cons]; omega

/-- A nonempty run of decimal digits reads as its value. -/
theorem toNatOpt_of_digits (cs : List Char) (hne : cs ≠ []) (hd : ∀ c ∈ cs, c.isDigit = true) :
    String.toNat? ⟨cs⟩ = some (cs.foldl (fun n c => n * 10 + (c.toNat - '0'.toNat)) 0) := by
  have hall : cs.any (fun c => !c.isDigit) = false := by
    rw [List.any_eq_false]; intro c hc; simp [hd c hc]
  have hemp : String.isEmpty ⟨cs⟩ = false := by
    cases cs with
    | nil => exact absurd rfl hne
    | cons c cs =>
      simp only [String.isEmpty, String.endPos, String.utf8ByteSize, beq_eq_false_iff_ne, ne_eq]
      intro h; exact go_pos c cs (congrArg String.Pos.byteIdx h)
  simp only [String.toNat?, String.isNat, String.all, string_any, hall, hemp, string_foldl]
  rfl

theorem toNatOpt_toString (n : Nat) : (toString n).toNat? = some n := by
  rw [toString_nat]; unfold Nat.toDigits; rw [toNatOpt_of_digits _ (toDigitsCore_ne_nil (n + 1) n [] (by omega))
    (fun c hc => (toDigitsCore_digits (n + 1) n [] (by simp) c hc).1)]
  have hval := toDigitsCore_value (n + 1) n [] (by omega)
  simp only [List.foldl_nil] at hval
  exact congrArg some hval

theorem digits_props (n : Nat) :
    Nat.toDigits 10 n ≠ [] ∧ (∀ c ∈ Nat.toDigits 10 n, c.isDigit = true ∧ c ≠ '-') ∧
      (Nat.toDigits 10 n).foldl (fun v c => v * 10 + (c.toNat - '0'.toNat)) 0 = n := by
  unfold Nat.toDigits
  refine ⟨toDigitsCore_ne_nil (n + 1) n [] (by omega), toDigitsCore_digits (n + 1) n [] (by simp), ?_⟩
  have hval := toDigitsCore_value (n + 1) n [] (by omega)
  simpa using hval

theorem intText_toIntOpt (v : Int) : (intText v).toInt? = some v := by
  cases v with
  | ofNat n =>
    obtain ⟨hne, hd, _⟩ := digits_props n
    have hget : (toString n).get 0 ≠ '-' := by
      rw [toString_nat]
      revert hne hd
      cases Nat.toDigits 10 n with
      | nil => intro h; exact absurd rfl h
      | cons c cs =>
        intro _ hd
        have := get_at [] cs c
        simp only [List.nil_append, go_nil] at this
        rw [show (0 : String.Pos) = ⟨0⟩ from rfl, this]
        exact (hd c (by simp)).2
    simp only [intText, String.toInt?, hget, if_false, toNatOpt_toString]
    rfl
  | negSucc n =>
    obtain ⟨hne, hd, hval⟩ := digits_props (n + 1)
    have hs : intText (Int.negSucc n) = ⟨['-'] ++ Nat.toDigits 10 (n + 1)⟩ := rfl
    have hget : (intText (Int.negSucc n)).get 0 = '-' := by
      rw [hs]; have := get_at [] (Nat.toDigits 10 (n + 1)) '-'
      simpa [go_nil] using this
    have hminus : String.utf8ByteSize.go ['-'] = 1 := rfl
    have hE : String.utf8ByteSize.go (['-'] ++ Nat.toDigits 10 (n + 1)) =
        String.utf8ByteSize.go (Nat.toDigits 10 (n + 1)) + 1 := by
      rw [go_append, hminus]; omega
    have hdpos : String.utf8ByteSize.go (Nat.toDigits 10 (n + 1)) ≠ 0 := by
      revert hne; cases Nat.toDigits 10 (n + 1) with
      | nil => intro h; exact absurd rfl h
      | cons c cs => intro _; exact go_pos c cs
    have hdrop : (intText (Int.negSucc n)).toSubstring.drop 1 =
        ⟨⟨['-'] ++ Nat.toDigits 10 (n + 1)⟩, ⟨String.utf8ByteSize.go ['-']⟩,
          ⟨String.utf8ByteSize.go (['-'] ++ Nat.toDigits 10 (n + 1))⟩⟩ := by
      rw [hs]
      simp only [String.toSubstring, Substring.drop, Substring.nextn, Substring.next, String.endPos,
        String.utf8ByteSize]
      rw [if_neg (fun h => by have := congrArg String.Pos.byteIdx h; exact go_pos '-' _ this.symm)]
      have := get_at [] (Nat.toDigits 10 (n + 1)) '-'
      simp only [List.nil_append, go_nil] at this
      rfl
    have hall : (Nat.toDigits 10 (n + 1)).any (fun c => !c.isDigit) = false := by
      rw [List.any_eq_false]; intro c hc; simp [(hd c hc).1]
    have hsub : ((intText (Int.negSucc n)).toSubstring.drop 1).toNat? = some (n + 1) := by
      rw [hdrop]
      simp only [Substring.toNat?, Substring.isNat, Substring.all, Substring.any, Substring.foldl,
        Substring.isEmpty, Substring.bsize, anyAux_at, foldlAux_at, hall, hval]
      rw [hE, hminus]
      simp [hdpos]
    simp only [String.toInt?, hget, if_true, hsub]
    rfl

end DecodeEncode

open DecodeEncode in
theorem ETerm.decode_encode : ∀ t : ETerm, ETerm.decode t.encode = some t
  | .var _ => rfl
  | .const _ => rfl
  | .num v => by
    have h : ETerm.decode (.arr #[.str "num", .str (intText v)]) = (intText v).toInt?.map ETerm.num := rfl
    rw [show ETerm.decode (ETerm.num v).encode = _ from h, intText_toIntOpt]; rfl
  | .add a b => by
    have h : ETerm.decode (.arr #[.str "add", a.encode, b.encode]) =
        (do pure (.add (← ETerm.decode a.encode) (← ETerm.decode b.encode))) := rfl
    rw [show ETerm.decode (ETerm.add a b).encode = _ from h, ETerm.decode_encode a, ETerm.decode_encode b]; rfl
  | .scale k t => by
    have h : ETerm.decode (.arr #[.str "scale", .str (intText k), t.encode]) =
        (do pure (.scale (← (intText k).toInt?) (← ETerm.decode t.encode))) := rfl
    rw [show ETerm.decode (ETerm.scale k t).encode = _ from h, intText_toIntOpt, ETerm.decode_encode t]; rfl

open DecodeEncode in
theorem reachRefl_kind (k : Bool) : reachRefl (reachKind k) = some k := by cases k <;> rfl

open DecodeEncode in
theorem mapM_decode (ts : List ETerm) : (ts.map ETerm.encode).mapM ETerm.decode = some ts := by
  induction ts with
  | nil => rfl
  | cons t ts ih => rw [List.map_cons, List.mapM_cons, ETerm.decode_encode, ih]; rfl

open DecodeEncode in
theorem EFormula.decode_encode : ∀ A : EFormula, EFormula.decode A.encode = some A
  | .top => rfl
  | .bottom => rfl
  | .pred _ [] => rfl
  | .pred p [t] => by
    have h : EFormula.decode (.arr #[.str "unary", .str p, t.encode]) =
        (do pure (.pred p [← ETerm.decode t.encode])) := rfl
    rw [show EFormula.decode (EFormula.pred p [t]).encode = _ from h, ETerm.decode_encode]; rfl
  | .pred p [t, u] => by
    have h : EFormula.decode (.arr #[.str "binary", .str p, t.encode, u.encode]) =
        (do pure (.pred p [← ETerm.decode t.encode, ← ETerm.decode u.encode])) := rfl
    rw [show EFormula.decode (EFormula.pred p [t, u]).encode = _ from h, ETerm.decode_encode, ETerm.decode_encode]; rfl
  | .pred p (t :: u :: v :: rest) => by
    have h : EFormula.decode (.arr #[.str "atom", .str p, .arr ((t :: u :: v :: rest).map ETerm.encode).toArray]) =
        (do pure (.pred p (← ((t :: u :: v :: rest).map ETerm.encode).toArray.toList.mapM ETerm.decode))) := rfl
    rw [show EFormula.decode (EFormula.pred p (t :: u :: v :: rest)).encode = _ from h, List.toList_toArray,
      mapM_decode]; rfl
  | .eq t u => by
    have h : EFormula.decode (.arr #[.str "eq", t.encode, u.encode]) =
        (do pure (.eq (← ETerm.decode t.encode) (← ETerm.decode u.encode))) := rfl
    rw [show EFormula.decode (EFormula.eq t u).encode = _ from h, ETerm.decode_encode, ETerm.decode_encode]; rfl
  | .lt t u => by
    have h : EFormula.decode (.arr #[.str "lt", t.encode, u.encode]) =
        (do pure (.lt (← ETerm.decode t.encode) (← ETerm.decode u.encode))) := rfl
    rw [show EFormula.decode (EFormula.lt t u).encode = _ from h, ETerm.decode_encode, ETerm.decode_encode]; rfl
  | .le t u => by
    have h : EFormula.decode (.arr #[.str "le", t.encode, u.encode]) =
        (do pure (.le (← ETerm.decode t.encode) (← ETerm.decode u.encode))) := rfl
    rw [show EFormula.decode (EFormula.le t u).encode = _ from h, ETerm.decode_encode, ETerm.decode_encode]; rfl
  | .not a => by
    have h : EFormula.decode (.arr #[.str "not", a.encode]) = (do pure (.not (← EFormula.decode a.encode))) := rfl
    rw [show EFormula.decode (EFormula.not a).encode = _ from h, EFormula.decode_encode a]; rfl
  | .and a b => by
    have h : EFormula.decode (.arr #[.str "and", a.encode, b.encode]) =
        (do pure (.and (← EFormula.decode a.encode) (← EFormula.decode b.encode))) := rfl
    rw [show EFormula.decode (EFormula.and a b).encode = _ from h, EFormula.decode_encode a,
      EFormula.decode_encode b]; rfl
  | .or a b => by
    have h : EFormula.decode (.arr #[.str "or", a.encode, b.encode]) =
        (do pure (.or (← EFormula.decode a.encode) (← EFormula.decode b.encode))) := rfl
    rw [show EFormula.decode (EFormula.or a b).encode = _ from h, EFormula.decode_encode a,
      EFormula.decode_encode b]; rfl
  | .implies a b => by
    have h : EFormula.decode (.arr #[.str "implies", a.encode, b.encode]) =
        (do pure (.implies (← EFormula.decode a.encode) (← EFormula.decode b.encode))) := rfl
    rw [show EFormula.decode (EFormula.implies a b).encode = _ from h, EFormula.decode_encode a,
      EFormula.decode_encode b]; rfl
  | .all s a => by
    have h : EFormula.decode (.arr #[.str "forall", .str s, a.encode]) =
        (do pure (.all s (← EFormula.decode a.encode))) := rfl
    rw [show EFormula.decode (EFormula.all s a).encode = _ from h, EFormula.decode_encode a]; rfl
  | .ex s a => by
    have h : EFormula.decode (.arr #[.str "exists", .str s, a.encode]) =
        (do pure (.ex s (← EFormula.decode a.encode))) := rfl
    rw [show EFormula.decode (EFormula.ex s a).encode = _ from h, EFormula.decode_encode a]; rfl
  | .reachNamed k r t u => by
    have h : EFormula.decode (.arr #[.str "reach", reachKind k, .arr #[.str "named", .str r], t.encode, u.encode]) =
        (do pure (.reachNamed (← reachRefl (reachKind k)) r (← ETerm.decode t.encode)
          (← ETerm.decode u.encode))) := by cases k <;> rfl
    rw [show EFormula.decode (EFormula.reachNamed k r t u).encode = _ from h, reachRefl_kind, ETerm.decode_encode,
      ETerm.decode_encode]; rfl
  | .reachBody k s a t u => by
    have h : EFormula.decode (.arr #[.str "reach", reachKind k, .arr #[.str "body", .str s, a.encode], t.encode,
          u.encode]) =
        (do pure (.reachBody (← reachRefl (reachKind k)) s (← EFormula.decode a.encode) (← ETerm.decode t.encode)
          (← ETerm.decode u.encode))) := by cases k <;> rfl
    rw [show EFormula.decode (EFormula.reachBody k s a t u).encode = _ from h, reachRefl_kind, EFormula.decode_encode a,
      ETerm.decode_encode, ETerm.decode_encode]; rfl

theorem decode_encode : ∀ A : EFormula, EFormula.decode A.encode = some A := by
  exact EFormula.decode_encode

end VE.EnglishGrammar
