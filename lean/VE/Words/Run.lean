import VE.Words.Situation
import VE.EnglishGrammar.Run
import VE.CertificateWire

/-! The `words` service mode (plan Q2.4): the one owner of the situation lines, point clauses, filled-gap sentences and
pair sentences that the readings and norm-defaults English shows. Python relays these lines (`ve/words.py`); it
words none of them itself (`tools/relay_lint.py`).

A request is `{"id", "environment", "lexicon", "items"}`. The environment is identified by its canonical JSON
(`Standalone.environmentIdOf`, the identity of every profile, the statement layers' included), decoded as the
English reader decodes it, and the lexicon must be the selection for that environment (its `environment_id`) and pass
the vocabulary policy. Each item is one line:

* `{"kind": "situation", "model", "facts", "suppose"}`: the model's elements by sort, named by their ids, then the
  true rows of each predicate of `facts`, then each `suppose` line (the soft and rights suppositions, which stay
  Python's, plan 4.5), as `VE.Words.situationText` joins them. `model` is `{"domains", "relations", "constants"}`;
* `{"kind": "point", "constants", "predicate", "tuple", "value"}`: the regulated predicate's clause at the tuple,
  each element named by the first constant (in name order) of `constants` that denotes it (`VE.Words.clauseAt`);
* `{"kind": "filling", ...}` with the same fields: the filled-gap sentence of that point's positive clause, answering
  `value` (`VE.Words.fillingSentence`);
* `{"kind": "pair", "required"}`: the pair sentence of an obligation that declares its permission
  (`VE.Words.pairSentence`).

The answer is `{"environment_id", "lexicon_id", "lines"}`, one line per item in order; an item Lean cannot word (an
undeclared sort, predicate or constant, a predicate that is not regulated, a row of the wrong arity, an argument
sort repeated three times) refuses the whole request with `InvalidInput`. -/

namespace VE.Words.Run
open Lean VE.EnglishGrammar

/-- At most this many items per request. -/
def maxItems : Nat := 10000

def invalid {α : Type} (message : String) : Except String α := throw s!"InvalidInput: words: {message}"

/-- The object's keys are exactly `keys`. -/
def exactKeys (j : Json) (what : String) (keys : List String) : Except String Unit := do
  let actual ← match j.getObj? with
    | .ok o => pure (o.toList.map Prod.fst)
    | .error _ => invalid s!"{what} is not an object"
  unless actual.length == keys.length && keys.all actual.contains do
    invalid s!"{what} has fields {actual}, not {keys}"

def text (j : Json) (what : String) : Except String String :=
  match j with
  | .str s => pure s
  | _ => invalid s!"{what} is not a string"

def texts (j : Json) (what : String) : Except String (List String) :=
  match j with
  | .arr xs => xs.toList.mapM (text · what)
  | _ => invalid s!"{what} is not a list"

def entries (j : Json) (what : String) : Except String (List (String × Json)) :=
  match j.getObj? with
  | .ok o => pure o.toList
  | .error _ => invalid s!"{what} is not an object"

/-- A shown model: its domains, its relations and its constants, each as ids. -/
structure Shown where
  domains : List (String × List String)
  relations : List (String × List (List String))
  constants : List (String × String)

def decodeShown (j : Json) : Except String Shown := do
  exactKeys j "model" ["domains", "relations", "constants"]
  let domains ← (← entries (j.getObjValD "domains") "domains").mapM fun (s, xs) => do
    pure (s, ← texts xs s!"the domain of {s}")
  let relations ← (← entries (j.getObjValD "relations") "relations").mapM fun (p, rows) => do
    match rows with
    | .arr rs => pure (p, ← rs.toList.mapM (texts · s!"a row of {p}"))
    | _ => invalid s!"the rows of {p} are not a list"
  let constants ← (← entries (j.getObjValD "constants") "constants").mapM fun (c, x) => do
    pure (c, ← text x s!"the element of {c}")
  pure ⟨domains, relations, constants⟩

/-- A situation item's line. -/
def situationLine (E : Env) (L : Lexicon) (j : Json) : Except String String := do
  exactKeys j "a situation item" ["kind", "model", "facts", "suppose"]
  let m ← decodeShown (j.getObjValD "model")
  let facts ← texts (j.getObjValD "facts") "facts"
  let suppose ← texts (j.getObjValD "suppose") "suppose"
  unless suppose.all (·.startsWith "suppose ") do invalid "a supposition does not start with `suppose `"
  let elements ← m.domains.mapM fun (s, ids) => do
    match L.nouns.lookup s with
    | some noun => pure (s, noun, ids)
    | none => invalid s!"the sort {s} has no noun"
  let rows ← facts.eraseDups.mapM fun p => do
    let some d := E.predicate? p | invalid s!"the predicate {p} is not declared"
    let some w := L.wordings.lookup p | invalid s!"the predicate {p} has no wording"
    let rs := (VE.Bridge.lookup m.relations p).getD []
    unless rs.all (·.length == d.arity) do invalid s!"a row of {p} has the wrong arity"
    pure (p, w, rs)
  pure (situationText elements rows suppose)

/-- A point or filling item's clause. -/
def pointLine (E : Env) (L : Lexicon) (kind : String) (j : Json) : Except String String := do
  exactKeys j s!"a {kind} item" ["kind", "constants", "predicate", "tuple", "value"]
  let consts ← (← entries (j.getObjValD "constants") "constants").mapM fun (c, x) => do
    unless (E.constants.find? (·.name == c)).isSome do invalid s!"the constant {c} is not declared"
    pure (c, ← text x s!"the element of {c}")
  let p ← text (j.getObjValD "predicate") "predicate"
  let ids ← texts (j.getObjValD "tuple") "tuple"
  let value ← match j.getObjValD "value" with
    | .bool b => pure b
    | _ => invalid "value is not a boolean"
  let some d := E.predicate? p | invalid s!"the predicate {p} is not declared"
  unless ids.length == d.arity do invalid s!"the tuple of {p} has the wrong arity"
  let names := ids.map (nameOf E L consts id)
  if kind == "point" then
    match clauseAt E L p names value with
    | some clause => pure clause
    | none => invalid s!"the predicate {p} is not regulated"
  else
    match clauseAt E L p names true with
    | some clause => pure (fillingSentence clause value)
    | none => invalid s!"the predicate {p} is not regulated"

/-- A pair item's sentence. -/
def pairLine (E : Env) (L : Lexicon) (j : Json) : Except String String := do
  exactKeys j "a pair item" ["kind", "required"]
  let r ← text (j.getObjValD "required") "required"
  match pairSentence E L r with
  | some t => pure t
  | none => invalid s!"{r} is no obligation with a declared permission and at most two arguments of a sort"

def line (E : Env) (L : Lexicon) (j : Json) : Except String String := do
  match j.getObjValD "kind" with
  | .str "situation" => situationLine E L j
  | .str "point" => pointLine E L "point" j
  | .str "filling" => pointLine E L "filling" j
  | .str "pair" => pairLine E L j
  | _ => invalid "an item's kind is not situation, point, filling or pair"

def wordsCase (j : Json) : Except String Json := do
  exactKeys j "the request" ["id", "environment", "lexicon", "items"]
  let id ← text (j.getObjValD "id") "id"
  let environment := j.getObjValD "environment"
  let lexicon := j.getObjValD "lexicon"
  let profiles ← VE.Route.Gate.profilesOf environment
  let environmentId ← VE.Service.Standalone.environmentIdOf profiles environment
  let E ← Env.decode environment (Json.mkObj [])
  let L ← EnglishGrammar.Run.decodeLexicon
    (← VE.Service.Standalone.environmentIdOf profiles (displayJson environment (Json.mkObj []))) lexicon
  unless L.policyOk E {} do
    throw "CheckerUnavailable: the lexicon does not pass the vocabulary policy for this environment"
  let items ← match j.getObjValD "items" with
    | .arr xs => pure xs.toList
    | _ => invalid "items is not a list"
  if items.length > maxItems then throw s!"ResourceLimit: a words request has at most {maxItems} items"
  let lines ← items.mapM (line E L)
  pure (VE.Route.Wire.ok id [("result", Json.mkObj [("environment_id", .str environmentId),
    ("lexicon_id", .str (← VE.CertificateWire.digest "ve-english-lexicon-v1\n" lexicon)),
    ("lines", Json.arr (lines.map Json.str).toArray)])])

def caseReported (j : Json) : Json :=
  match wordsCase j with
  | .ok row => row
  | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]

end VE.Words.Run
