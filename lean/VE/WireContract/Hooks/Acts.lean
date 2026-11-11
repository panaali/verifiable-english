import VE.Compose.Dispatch
import VE.Norms.Wire
import VE.WireContract.Hooks.Norms
import VE.WireContract.Tables.Acts

/-! The hand-written classifier and adapter of the contract `acts@0`, in shadow (ap-1bf; act-phrases-PLAN.md 2.8,
edit 2 of plan synthesis round 2): it reports and refuses nothing.

`Hooks.Norms.w1Environment` and `typingEnvironment` decode without `acts := true`, so they refuse every `acts@0`
environment; this module's 1.1 decodes with it, as `Norms.Wire.decodeSource` does. When the decoder refuses, the
member is the limit of `VE.Acts.Lexical` whose own function gives exactly the decoder's text: `decodeFixed` on the
declared phrases (1.1a), `phraseToks` on one of them (1.1b) or `check` on one act (1.1c); any other refusal is
1.1d. The limits and texts are Lexical's, read here and never copied. After a refusal the classifier reads each
declared phrase and each act once more, so its work is linear in the environment. Diagnostic only: no verdict
depends on this module. -/

namespace VE.WireContract.Hooks.Acts
open Lean
open VE.WireContract
open VE.Acts.Lexical (check decodeFixed maxActBytes maxPhraseBytes maxPhrases phraseToks)
open VE.WireContract.Hooks.Norms (environmentOf message)

/-- 1.1d: `acts@0`'s profile row, which the environment mode reads before every decoder (act-phrases 4.4;
`Service.Standalone.validatedLayerEnvironment`), so that without `norms@0` the row's own refusal is the text (ap-1bf
review F1); then the norms route's environment decoder reading `acts@0`, then `decodeSource`'s `definitions@0`
check; a joined act is read by the act check, as the environment row reads it (ap-3dc). -/
def decoded (environment : Json) : Except String Unit := do
  let listed := (VE.Bridge.strings (environment.getObjValD "profiles")).toOption.getD []
  if listed.contains "acts@0" then
    let _ ← VE.Compose.gateOf VE.Compose.baseRows listed
  let ne ← VE.Norms.Wire.decodeNormsEnvironment environment (acts := true) (joined := true)
  unless ne.rv.definitions.isEmpty || ne.profiles.contains "definitions@0" do
    throw "defined declarations require the definitions@0 profile"

def refusedWith {α : Type} (e : String) : Except String α → Bool
  | .error e' => e' == e
  | .ok _ => false

/-- The declared fixed phrases, as written (`[]` when they are not a string array). -/
def fixedOf (environment : Json) : List String :=
  (VE.Bridge.strings (((environment.getObjValD "vocabulary").getObjValD "acts").getObjValD "fixed")).toOption.getD []

/-- Each regulated predicate's name, arity and act, in vocabulary order. -/
def actsOf (environment : Json) : List (String × Nat × Json) :=
  match ((environment.getObjValD "vocabulary").getObjValD "predicates").getObj? with
  | .ok kvs => kvs.toList.filterMap fun (p, entry) =>
    match ((entry.getObjValD "regulated").getObjVal? "act"), VE.Bridge.strings (entry.getObjValD "arguments") with
    | .ok raw, .ok args => some (p, args.length, raw)
    | _, _ => none
  | .error _ => []

/-- The member of the decoder's refusal `e`. `check` runs without the phrases: its limit refusal comes before it
    reads them. -/
def member (environment : Json) (e : String) : ClassifierResult :=
  let fx := fixedOf environment
  if !e.startsWith "ResourceLimit:" then .fail "1.1d" (message e)
  else if fx.length > maxPhrases then .fail (if refusedWith e (decodeFixed fx) then "1.1a" else "1.1d") (message e)
  else if fx.any (refusedWith e ∘ phraseToks) then .fail "1.1b" (message e)
  else if (actsOf environment).any (fun (p, k, raw) => refusedWith e (check [] p k raw)) then .fail "1.1c" (message e)
  else .fail "1.1d" (message e)

/-! ## The rule phases: `norms@0`'s, with an environment that reads `acts@0` (ap-1bfb)

`acts@0.json` includes `norms@0`'s phases from `profiles` to `semantic`; their hooks are `Hooks.Norms`', except 4.7,
whose `Hooks.Norms.typingEnvironment` decodes without `acts` and so is `none` on every `acts@0` source. -/

/-- The environment 4.7 reads: the norms route's, decoded reading `acts@0` as 1.1 decodes it; `none` before 1.1
    holds. -/
def typingEnvironment (root : Json) : Option VE.Environment := do
  let ne ← (VE.Norms.Wire.decodeNormsEnvironment (environmentOf root) (acts := true) (joined := true)).toOption
  pure ne.rv.environment

/-- 4.7 at the `i`-th rule: `Hooks.Norms.ruleTyping`'s walk, one running total over the earlier rules (each well
    typed, by rule 2) and then this one, over `typingEnvironment`. -/
def ruleTyping (root : Json) (i : Nat) : ClassifierResult :=
  match typingEnvironment root with
  | none => .ok
  | some E =>
    let data := (Hooks.Norms.profiles root).contains "data@0"
    let rec go : Nat → Nat → List Json → ClassifierResult
      | _, _, [] => .ok
      | 0, n, rule :: _ => match Hooks.Norms.typeRule E data rule n with
        | some (.error e) => Hooks.Norms.typingMember e
        | _ => .ok
      | j + 1, n, rule :: rest => match Hooks.Norms.typeRule E data rule n with
        | some (.ok next) => go j next rest
        | _ => .ok
    go i 0 (Hooks.Norms.rulesOf root)

def classifier : String → Json → List Pointer → ClassifierResult
  | "acts_environment", root, _ => match decoded (environmentOf root) with
    | .ok () => .ok
    | .error e => member (environmentOf root) e
  | "rule_typing", root, items => match Hooks.Norms.itemIndex items 0 with
    | some i => ruleTyping root i
    | none => .ok
  | name, root, items => Hooks.Norms.classifier name root items

def hooks : Hooks := ⟨Hooks.Norms.predicate, classifier, Hooks.Norms.view⟩

/-- `acts@0` listed, and the source without it in `norms@0`'s domain: no `norm-defaults@0`, no statement layer. -/
def inDomain (environment norms : Json) : Bool :=
  match environment.getObjValD "profiles" with
  | .arr ps =>
    let rest := environment.setObjVal! "profiles" (.arr (ps.filter (· != .str "acts@0")))
    ps.contains (.str "acts@0") && Hooks.Norms.inSharedDomain rest norms &&
      !(VE.NormDefaults.Wire.profilesOf rest).contains VE.NormDefaults.Wire.profile
  | _ => false

/-- The adapter `acts_source`: the norms route's kinds and `admission`, in `inDomain`. -/
def adapter (case : Json) : Except String Json :=
  Hooks.Norms.sourceAdapter (fun k => k == "norms-elaborate" || k == "norms-conflict" || k == "norms-certificate")
    inDomain case

def registered : List String := "acts_environment" :: Hooks.Norms.registered

#guard Tables.Acts.table.hookNames.all registered.contains

/-! Fixtures at and around each limit, on both sides; the limits are Lexical's. -/

def envOf (fixed : List String) (act : String) (profiles := ["acts@0", "norms@0", "relational-fol@0"])
    (args := ["person"]) (others : List String := []) (defined := false) (plain := "paid") : Json :=
  let pred := fun (args : List String) (reg : List (String × Json)) => Json.mkObj [("arguments", toJson args),
    ("description", "d"), ("regulated", Json.mkObj reg)]
  let permission := pred ["person"] [("role", "permission"), ("default", "allow"), ("act", "{0} seek protection")]
  let c := Json.mkObj ([("arguments", toJson ["person"]), ("description", "w")] ++
    if defined then [("defined", Json.mkObj [("arguments", toJson ["person"]), ("body", toJson ["top"])])] else [])
  Json.mkObj [("language", "ve.core@0.2"), ("profiles", toJson profiles),
    ("spec_revision", "ve-v0.2-expand2-2026-09-25"),
    ("vocabulary", Json.mkObj [("sorts", Json.mkObj [("person", Json.mkObj [("description", "person")])]),
      ("predicates", Json.mkObj ([(plain, pred args [("role", "plain"), ("default", "deny"), ("act", .str act),
        ("form", "has the right")]), ("w", c)] ++ others.map (·, permission))), ("constants", Json.mkObj []),
      ("acts", Json.mkObj [("fixed", toJson fixed)])])]

def memberOf (environment : Json) : Option String :=
  match classifier "acts_environment" (Json.mkObj [("environment", environment)]) [] with
  | .ok => none
  | .fail m _ => some m

/-- The engine's record over the generated table: its check, code and class, its path and phase, and its text,
    which is the decoder's own; `none` when clean. -/
def recordOf (environment : Json) : Option (List Json) :=
  (run Tables.Acts.table hooks (Json.mkObj [("environment", environment), ("norms", Json.arr #[])])).map fun f =>
    let r := record Tables.Acts.table f
    ["contract", "check", "code", "class", "path", "phase", "text"].map r.getObjValD ++
      [toJson ((decoded environment).toOption.isNone && (r.getObjValD "text") == .str
        (match decoded environment with | .error e => e | .ok () => ""))]

def phraseOf (n : Nat) : String := "zeta " ++ String.mk (List.replicate (n - 5) 'a')
def actOf (n : Nat) : String := "{0} enjoy " ++ String.mk (List.replicate (n - 10) 'b')
def phrasesOf (n : Nat) : List String :=
  (List.range n).map fun i => let t := String.mk [Char.ofNat (97 + i / 26), Char.ofNat (97 + i % 26)]; s!"p{t} q{t}"
def around : List String := ["anna", "zora"]

#guard (phraseOf maxPhraseBytes).utf8ByteSize == maxPhraseBytes && (actOf maxActBytes).utf8ByteSize == maxActBytes
#guard memberOf (envOf [] (actOf maxActBytes)) == none
#guard memberOf (envOf [] (actOf (maxActBytes + 1)) (others := around)) == some "1.1c"
#guard memberOf (envOf [] (actOf (maxActBytes - 3) ++ " {1}") (args := ["person", "person"])) == some "1.1c"
#guard memberOf (envOf [] (actOf (maxActBytes + 1)) (plain := "zz")) == some "1.1c"
#guard memberOf (envOf [phraseOf maxPhraseBytes] (actOf 20)) == none
#guard memberOf (envOf ["equal pay", phraseOf (maxPhraseBytes + 1), "fair hearing"] (actOf 20)) == some "1.1b"
#guard memberOf (envOf (phrasesOf maxPhrases) (actOf 20)) == none
#guard memberOf (envOf (phrasesOf (maxPhrases + 1)) (actOf 20)) == some "1.1a"
#guard memberOf (envOf (phrasesOf maxPhrases) (actOf (maxActBytes + 1))) == some "1.1c"
-- around: the count before a long phrase, the act's shape before its size, an earlier phrase before a long act,
-- a limit that is none of the three, and `definitions@0`
#guard memberOf (envOf (phrasesOf maxPhrases ++ [phraseOf (maxPhraseBytes + 1)]) (actOf 20)) == some "1.1a"
#guard memberOf (envOf [] ("enjoy " ++ actOf maxActBytes)) == some "1.1d"
#guard memberOf (envOf ["seek and"] (actOf (maxActBytes + 1))) == some "1.1d"
#guard memberOf (envOf [] "{0} seek and enjoy asylum") == some "1.1d"
#guard memberOf (envOf ["equal pay"] (actOf 20) (others := (List.range 64).map (s!"q{·}"))) == some "1.1d"
#guard memberOf (envOf [] (actOf 20) (defined := true)) == some "1.1d"
#guard memberOf (envOf [] (actOf 20) ["acts@0", "definitions@0", "norms@0", "relational-fol@0"] (defined := true)) == none
-- without `norms@0`, the profile row's text, as the environment mode gives it (ap-1bf review F1)
#guard (match decoded (envOf [] (actOf 20) ["acts@0", "relational-fol@0"]) with | .error e => e | .ok () => "") ==
  "UnsupportedProfile: acts@0 requires norms@0"
-- the records through the generated table
#guard recordOf (envOf [] (actOf maxActBytes)) == none
#guard Tables.Acts.table.revision == 2  -- acts@0.json's revision: a new revision updates this pin
#guard [(envOf (phrasesOf (maxPhrases + 1)) (actOf 20), "1.1a", "ACTS_RESOURCE_LIMIT", "ResourceLimit"),
    (envOf [phraseOf (maxPhraseBytes + 1)] (actOf 20), "1.1b", "ACTS_RESOURCE_LIMIT", "ResourceLimit"),
    (envOf [] (actOf (maxActBytes + 1)), "1.1c", "ACTS_RESOURCE_LIMIT", "ResourceLimit"),
    (envOf [] "{0} seek and enjoy asylum", "1.1d", "ACTS_INVALID_ENVIRONMENT", "InvalidInput")].all fun (j, c, k, l) =>
  recordOf j == some (["acts@0", c, k, l, "/environment", "environment"].map Json.str ++ [(recordOf j).get!.getD 6 .null,
    toJson true])
-- the rule phases (ap-1bfb): `norms@0`'s members, under the include `norms`, typed over `acts@0`'s environment
def ruleOf (name pred : String) (guard : Json) : Json := Json.mkObj [("norm", Json.mkObj [("name", name),
  ("predicate", pred), ("sign", true), ("guard", guard), ("unless", Json.arr #[]), ("over", Json.arr #[])])]
def unaryOn (p : String) : Json := toJson [toJson "unary", toJson p, toJson [toJson "var", toJson 0]]
def checkOf (norms : List Json) (environment : Json := envOf [] (actOf 20)) : Option String :=
  (run Tables.Acts.table hooks (Json.mkObj [("environment", environment), ("norms", toJson norms)])).map fun f =>
    ((record Tables.Acts.table f).getObjValD "check").getStr?.toOption.getD ""
#guard checkOf [ruleOf "r0" "paid" (unaryOn "w")] == none && (typingEnvironment (Json.mkObj
  [("environment", envOf [] (actOf 20))])).isSome
#guard checkOf [ruleOf "r0" "paid" (unaryOn "w"), ruleOf "r1" "paid" (unaryOn "nope")] == some "norms/4.7b"
#guard checkOf [ruleOf "r0" "paid" (toJson [toJson "unary", toJson "w", toJson [toJson "const", toJson "k"]])] ==
  some "norms/4.7b"
#guard checkOf [ruleOf "r0" "w" (unaryOn "w")] == some "norms/4.4"
#guard checkOf [ruleOf "r0" "paid" (unaryOn "w"), ruleOf "r0" "paid" (unaryOn "w")] == some "norms/4.2"
-- 1.1 comes first, and a rule is not typed over an environment 1.1 refuses
#guard checkOf [ruleOf "r0" "paid" (unaryOn "nope")] (envOf [] (actOf (maxActBytes + 1))) == some "1.1c"
-- the adapter reads `acts@0` sources of the norms route only, wherever `acts@0` is listed
def caseOf (kind : String) (ps : List String) : Json :=
  Json.mkObj [("kind", kind), ("environment", envOf [] (actOf 20) ps), ("norms", Json.arr #[])]
#guard ["norms-elaborate", "norms-conflict", "norms-certificate"].all fun k =>
  [["norms@0", "relational-fol@0", "acts@0"], ["acts@0", "norms@0"], ["norms@0", "acts@0", "relational-fol@0"]].all
    fun ps => (adapter (caseOf k ps)).isOk
#guard !(adapter (caseOf "norm-defaults-elaborate" ["acts@0", "norms@0", "relational-fol@0"])).isOk
#guard [["norms@0", "relational-fol@0"], ["acts@0", "norms@0", "relational-fol@0", "norm-defaults@0"],
    ["acts@0", "norm-defaults@0", "norms@0", "relational-fol@0"], ["acts@0", "norms@0", "relational-fol@0", "soft-norms@0"],
    ["soft-norms@0", "acts@0", "norms@0"], ["acts@0", "soft-norms@0", "norms@0"]].all fun ps =>
  !(adapter (caseOf "norms-elaborate" ps)).isOk
#guard !(adapter (Json.mkObj [("kind", "norms-elaborate"), ("environment", Json.mkObj []), ("norms", Json.arr #[])])).isOk
#guard !refusedWith "a" (.error "b" : Except String Unit) && !refusedWith "a" (.ok () : Except String Unit)

end VE.WireContract.Hooks.Acts
