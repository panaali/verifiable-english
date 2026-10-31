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

/-- 1.1d: the norms route's environment decoder reading `acts@0`, then `decodeSource`'s `definitions@0` check. -/
def decoded (environment : Json) : Except String Unit := do
  let ne ← VE.Norms.Wire.decodeNormsEnvironment environment (acts := true)
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

def classifier : String → Json → List Pointer → ClassifierResult
  | "acts_environment", root, _ => match decoded (environmentOf root) with
    | .ok () => .ok
    | .error e => member (environmentOf root) e
  | _, _, _ => .ok

def hooks : Hooks := ⟨fun _ _ _ => .ok, classifier, fun _ v => v⟩

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

def registered : List String := ["acts_environment"]

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
-- the records through the generated table
#guard recordOf (envOf [] (actOf maxActBytes)) == none
#guard Tables.Acts.table.revision == 1  -- acts@0.json's revision: a new revision updates this pin
#guard [(envOf (phrasesOf (maxPhrases + 1)) (actOf 20), "1.1a", "ACTS_RESOURCE_LIMIT", "ResourceLimit"),
    (envOf [phraseOf (maxPhraseBytes + 1)] (actOf 20), "1.1b", "ACTS_RESOURCE_LIMIT", "ResourceLimit"),
    (envOf [] (actOf (maxActBytes + 1)), "1.1c", "ACTS_RESOURCE_LIMIT", "ResourceLimit"),
    (envOf [] "{0} seek and enjoy asylum", "1.1d", "ACTS_INVALID_ENVIRONMENT", "InvalidInput")].all fun (j, c, k, l) =>
  recordOf j == some (["acts@0", c, k, l, "/environment", "environment"].map Json.str ++ [(recordOf j).get!.getD 6 .null,
    toJson true])
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
