import VE.EnglishGrammar.Actions
import VE.Route.Gate
import VE.Route.Wire
import VE.Core.Bridge

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

/-- The typed check of a document of encoded formulas against an environment JSON, by the standalone
typing service's decoders, family by family. -/
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
    let e ← VE.Route.Gate.decodeEnvelope environment
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
    let noun := match VE.Bridge.lookup oSorts name with
      | some o => (o.getObjValD "verbalisation").getObjValD "singular" |>.getStr?.toOption
      | none => (entry.getObjValD "verbalisation").getObjValD "singular" |>.getStr?.toOption
    pure ({ name, noun } : SortDecl)
  let predicates ← (← VE.Bridge.fields (← vocabulary.getObjVal? "predicates")).mapM fun (name, entry) => do
    let args ← VE.Bridge.strings (← entry.getObjVal? "arguments")
    let (wording, negative) := match VE.Bridge.lookup oPreds name with
      | some o => (optString o "verbalisation", optString o "negative_verbalisation")
      | none => (optString entry "verbalisation", optString entry "negative_verbalisation")
    pure ({ name, arity := args.length, wording, negative, args } : PredDecl)
  let constants ← (← VE.Bridge.fields (← vocabulary.getObjVal? "constants")).mapM fun (name, entry) => do
    let sort ← VE.Bridge.stringField entry "sort"
    let display := (VE.Bridge.lookup oConsts name).bind (optString · "verbalisation")
    pure ({ name, display, sort } : ConstDecl)
  pure { sorts, predicates, constants, profiles, source := environment }

end VE.EnglishGrammar
