import VE.Compose.Dispatch
import VE.Norms.Wire
import VE.WireContract.Hooks.Norms
import VE.WireContract.Tables.Acts

/-! The hand-written classifier and adapter of the contract `acts@0`, in shadow (ap-1bf; act-phrases-PLAN.md 2.8,
edit 2 of plan synthesis round 2): it reports and refuses nothing.

`Hooks.Norms.w1Environment` and `typingEnvironment` decode without `acts := true`, so they refuse every `acts@0`
environment; this module's 1.1 decodes with it, as `Norms.Wire.decodeSource` does. When the decoder refuses, the
member is the limit of `VE.Acts.Lexical` whose own function gives exactly the decoder's text: `decodeFixed` on the
declared phrases (1.1a), `phraseToks` on one of them (1.1b) or `check` on one act (1.1c); a refusal of the `acts`
block's frames and adverbs (D-31, `Acts.Syntax.checkVocab`; ap-1bfb) is 1.1e at its limit (31a) and 1.1f otherwise,
when the decoder reaches them: it refuses the block alone in the vocabulary with the same text and accepts it without
its frames and adverbs (`framesRefusal`), so a text the frames share with an earlier check, such as "String
expected", is that check's; any other refusal is 1.1d. The limits and texts are Lexical's and D-31's, read here and
never copied. After a refusal the classifier reads each declared phrase and each act once more, and decodes the
block twice. The rule phases (4.7) type each rule once per run over one decode of the environment (`hooksFor`).
Diagnostic only: no verdict depends on this module. -/

namespace VE.WireContract.Hooks.Acts
open Lean
open VE.WireContract
open VE.Acts.Lexical (check decodeFixed maxActBytes maxPhraseBytes maxPhrases phraseToks)
open VE.WireContract.Hooks.Norms (environmentOf message)

/-- 1.1d: `acts@0`'s profile row, which the environment mode reads before every decoder (act-phrases 4.4;
`Service.Standalone.validatedLayerEnvironment`), so that without `norms@0` the row's own refusal is the text (ap-1bf
review F1); then the norms route's environment decoder reading `acts@0`, then `decodeSource`'s `definitions@0`
check; a joined act is read by the act check, as the environment row reads it (ap-3dc). -/
def decodeOf (environment : Json) : Except String VE.Norms.Wire.NormsEnvironment :=
  VE.Norms.Wire.decodeNormsEnvironment environment (acts := true) (joined := true)

/-- `decoded`, with the norms route's decoder's result `ne` read only after the profile row holds. -/
def decodedBy (environment : Json) (ne : Unit → Except String VE.Norms.Wire.NormsEnvironment) :
    Except String Unit := do
  let listed := (VE.Bridge.strings (environment.getObjValD "profiles")).toOption.getD []
  if listed.contains "acts@0" then
    let _ ← VE.Compose.gateOf VE.Compose.baseRows listed
  let ne ← ne ()
  unless ne.rv.definitions.isEmpty || ne.profiles.contains "definitions@0" do
    throw "defined declarations require the definitions@0 profile"

def decoded (environment : Json) : Except String Unit := decodedBy environment fun _ => decodeOf environment

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

/-- The `acts` block of the environment's vocabulary, whose frames and adverbs `Acts.Wire.decodeVocab` reads. -/
def blockOf (environment : Json) : Json := (environment.getObjValD "vocabulary").getObjValD "acts"

/-- The environment with the `acts` block alone in its vocabulary, with its `frames` and `adverbs` (`frames`) or
    without them; `none` when the block is not an object. Every check the decoder makes before the frames reads the
    same members of both as of the environment, and every check after them holds on both (no sort, predicate or
    constant is declared). -/
def alone (environment : Json) (frames : Bool) : Option Json :=
  match blockOf environment with
  | .obj kvs => some (environment.setObjVal! "vocabulary" (Json.mkObj [("sorts", Json.mkObj []),
      ("predicates", Json.mkObj []), ("constants", Json.mkObj []),
      ("acts", if frames then .obj kvs else .obj ((kvs.erase "frames").erase "adverbs"))]))
  | _ => none

/-- Whether `e` is the refusal of the `acts` block's frames and adverbs (D-31): the decoder refuses the block alone
    with `e`, and accepts it without its frames and adverbs, so no check before them refuses the environment (ap-1bfb
    review F1: a text such as "String expected" that the frames share with an earlier check is that check's). Python's
    `acts_contract.vocabulary_refusal` asks Lean's decoder the same two questions. -/
def framesRefusal (environment : Json) (e : String) : Bool :=
  match alone environment true, alone environment false with
  | some j, some k => refusedWith e (decoded j) && (decoded k).isOk
  | _, _ => false

/-- The member of the decoder's refusal `e`. `check` runs without the phrases: its limit refusal comes before it
    reads them. -/
def member (environment : Json) (e : String) : ClassifierResult :=
  let fx := fixedOf environment
  if framesRefusal environment e then
    .fail (if e.startsWith "ResourceLimit:" then "1.1e" else "1.1f") (message e)
  else if !e.startsWith "ResourceLimit:" then .fail "1.1d" (message e)
  else if fx.length > maxPhrases then .fail (if refusedWith e (decodeFixed fx) then "1.1a" else "1.1d") (message e)
  else if fx.any (refusedWith e ∘ phraseToks) then .fail "1.1b" (message e)
  else if (actsOf environment).any (fun (p, k, raw) => refusedWith e (check [] p k raw)) then .fail "1.1c" (message e)
  else .fail "1.1d" (message e)

/-! ## The rule phases: `norms@0`'s, with an environment that reads `acts@0` (ap-1bfb)

`acts@0.json` includes `norms@0`'s phases from `profiles` to `semantic`; their hooks are `Hooks.Norms`', except 4.7,
whose `Hooks.Norms.typingEnvironment` decodes without `acts` and so is `none` on every `acts@0` source. -/

/-- The environment 4.7 reads: the norms route's, decoded reading `acts@0` as 1.1 decodes it (`ne`); `none` before
    1.1 holds. -/
def typingEnvironment (ne : Except String VE.Norms.Wire.NormsEnvironment) : Option VE.Environment :=
  ne.toOption.map (·.rv.environment)

/-- 1.1 over the decoder's result `ne` on the environment. -/
def environmentBy (environment : Json) (ne : Unit → Except String VE.Norms.Wire.NormsEnvironment) :
    ClassifierResult :=
  match decodedBy environment ne with
  | .ok () => .ok
  | .error e => member environment e

/-- The classifiers; 1.1 reads the decoder's result `ne` on the root's environment, and 4.7 each rule's result from
    `typing` (both built from the root, unless one run's hooks give them built once: `hooksFor`). -/
def classifier (name : String) (root : Json) (items : List Pointer)
    (ne : Json → Except String VE.Norms.Wire.NormsEnvironment := fun r => decodeOf (environmentOf r))
    (typing : Json → Array ClassifierResult := fun r => Hooks.Norms.typingTableOver r (typingEnvironment (ne r))) :
    ClassifierResult :=
  match name with
  | "acts_environment" => environmentBy (environmentOf root) fun _ => ne root
  | "rule_typing" => Hooks.Norms.tableAt (typing root) items
  | _ => Hooks.Norms.classifier name root items

def hooks : Hooks := ⟨Hooks.Norms.predicate, classifier, Hooks.Norms.view⟩

/-- The hooks of one run on the input `j` (ap-1bfb review F2): the environment is decoded once, for 1.1 and 4.7,
    and 4.7's table is built once; each rule is typed once. -/
def hooksFor (j : Json) : Hooks :=
  let decode := fun r => decodeOf (environmentOf r)
  let ne := Thunk.mk fun _ => decode j
  let typing := fun r => Hooks.Norms.typingTableOver r (typingEnvironment (Hooks.Norms.atInput j ne decode r))
  ⟨Hooks.Norms.predicate, fun n r i => classifier n r i (Hooks.Norms.atInput j ne decode)
    (Hooks.Norms.atInput j (Thunk.mk fun _ => typing j) typing), Hooks.Norms.view⟩

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
-- the frames and adverbs (ap-1bfb, D-31): 31a's limit found from `decodeVocab`, never written here
def frameOf (head : String) (markers : List String := []) : Json := Json.mkObj [("head", head),
  ("markers", toJson markers), ("split", Json.arr #[]), ("modifiers", Json.arr #[])]
def framesOf (n : Nat) : List Json :=
  (List.range n).map fun i => frameOf (String.mk ['v', Char.ofNat (97 + i / 26), Char.ofNat (97 + i % 26)])
def framed (frames : List Json) (adverbs : List String := []) : Json :=
  let e := envOf [] (actOf 20)
  e.setObjVal! "vocabulary" ((e.getObjValD "vocabulary").setObjVal! "acts"
    (Json.mkObj [("fixed", Json.arr #[]), ("frames", toJson frames), ("adverbs", toJson adverbs)]))
def framesLimit : Nat :=
  ((List.range 600).find? fun n => !(VE.Acts.Wire.decodeVocab (Json.mkObj [("frames", toJson (framesOf (n + 1)))])).isOk).getD 0
#guard framesLimit > 0 && memberOf (framed (framesOf framesLimit) ["promptly"]) == none
#guard memberOf (framed (framesOf (framesLimit + 1))) == some "1.1e"
#guard memberOf (framed (frameOf "Give" :: framesOf framesLimit)) == some "1.1e"
#guard memberOf (framed [frameOf "Give"]) == some "1.1f"
#guard memberOf (framed [frameOf "give" ["to"], frameOf "up"] ["give"]) == some "1.1f"
#guard memberOf (framed [Json.mkObj [("head", "give")]]) == some "1.1f"
-- a refusal of the frames is not one of the act limits', nor an act's refusal one of the frames'
#guard memberOf ((framed [frameOf "give"]).setObjVal! "language" "x") == some "1.1d"
#guard [(framed (framesOf (framesLimit + 1)), "1.1e", "ACTS_RESOURCE_LIMIT", "ResourceLimit"),
    (framed [frameOf "Give"], "1.1f", "ACTS_INVALID_FRAMES", "InvalidInput")].all fun (j, c, k, l) =>
  recordOf j == some (["acts@0", c, k, l, "/environment", "environment"].map Json.str ++ [(recordOf j).get!.getD 6 .null,
    toJson true])
-- a text the frames share with an earlier check is that check's, and with a later check the frames' (ap-1bfb review
-- F1): a number where a string is expected, in the envelope, in `fixed`, in a predicate, and in a frame or an adverb
def withBlock (block : List (String × Json)) (e : Json := framed []) : Json :=
  e.setObjVal! "vocabulary" ((e.getObjValD "vocabulary").setObjVal! "acts" (Json.mkObj block))
def numberHead : Json := Json.mkObj [("head", (5 : Nat)), ("markers", Json.arr #[]), ("split", Json.arr #[]),
  ("modifiers", Json.arr #[])]
#guard memberOf ((framed [numberHead]).setObjVal! "language" (5 : Nat)) == some "1.1d"
#guard memberOf (withBlock [("fixed", toJson [(5 : Nat)]), ("adverbs", toJson [(5 : Nat)])]) == some "1.1d"
#guard memberOf (withBlock [("frames", toJson [frameOf "Give"])]) == some "1.1d"
#guard memberOf (framed [numberHead]) == some "1.1f" && memberOf (withBlock [("fixed", Json.arr #[]),
  ("adverbs", toJson [(5 : Nat)])]) == some "1.1f"
#guard let e := withBlock [("fixed", Json.arr #[]), ("adverbs", toJson [(5 : Nat)])]
  let v := e.getObjValD "vocabulary"
  memberOf (e.setObjVal! "vocabulary" (v.setObjVal! "predicates" ((v.getObjValD "predicates").setObjVal! "w"
    (Json.mkObj [("arguments", toJson ["person"]), ("description", (5 : Nat))])))) == some "1.1f"
-- a block that is not an object is never the frames'
#guard let e := framed []
  memberOf (e.setObjVal! "vocabulary" ((e.getObjValD "vocabulary").setObjVal! "acts" (5 : Nat))) == some "1.1d"
-- the rule phases (ap-1bfb): `norms@0`'s members, under the include `norms`, typed over `acts@0`'s environment
def ruleOf (name pred : String) (guard : Json) : Json := Json.mkObj [("norm", Json.mkObj [("name", name),
  ("predicate", pred), ("sign", true), ("guard", guard), ("unless", Json.arr #[]), ("over", Json.arr #[])])]
def unaryOn (p : String) : Json := toJson [toJson "unary", toJson p, toJson [toJson "var", toJson 0]]
def checkOf (norms : List Json) (environment : Json := envOf [] (actOf 20)) : Option String :=
  (run Tables.Acts.table hooks (Json.mkObj [("environment", environment), ("norms", toJson norms)])).map fun f =>
    ((record Tables.Acts.table f).getObjValD "check").getStr?.toOption.getD ""
#guard checkOf [ruleOf "r0" "paid" (unaryOn "w")] == none && (typingEnvironment (decodeOf (envOf [] (actOf 20)))).isSome
#guard checkOf [ruleOf "r0" "paid" (unaryOn "w"), ruleOf "r1" "paid" (unaryOn "nope")] == some "norms/4.7b"
#guard checkOf [ruleOf "r0" "paid" (toJson [toJson "unary", toJson "w", toJson [toJson "const", toJson "k"]])] ==
  some "norms/4.7b"
#guard checkOf [ruleOf "r0" "w" (unaryOn "w")] == some "norms/4.4"
#guard checkOf [ruleOf "r0" "paid" (unaryOn "w"), ruleOf "r0" "paid" (unaryOn "w")] == some "norms/4.2"
-- 1.1 comes first, and a rule is not typed over an environment 1.1 refuses
#guard checkOf [ruleOf "r0" "paid" (unaryOn "nope")] (envOf [] (actOf (maxActBytes + 1))) == some "1.1c"
-- a joined act, which 1.1 reads (ap-3dc), is read by 4.7 too
def joinedEnv : Json :=
  let e := envOf ["cruel, inhuman or degrading treatment or punishment"] (actOf 20)
  let v := e.getObjValD "vocabulary"
  let v := v.setObjVal! "acts" (Json.mkObj [("fixed", toJson ["cruel, inhuman or degrading treatment or punishment"]),
    ("frames", toJson [Json.mkObj [("head", "subjected"), ("markers", toJson ["to"]), ("split", toJson ["to"]),
      ("modifiers", Json.arr #[])]])])
  e.setObjVal! "vocabulary" (v.setObjVal! "predicates" ((v.getObjValD "predicates").setObjVal! "p027" (Json.mkObj
    [("arguments", toJson ["person"]), ("description", "d"), ("regulated", Json.mkObj [("role", "permission"),
      ("default", "deny"),
      ("act", "{0} be subjected to torture or to cruel, inhuman or degrading treatment or punishment")])])))
#guard memberOf joinedEnv == none && checkOf [ruleOf "r0" "paid" (unaryOn "nope")] joinedEnv == some "norms/4.7b"
-- `data@0` reaches the typing walk: a `$string` binder is 4.7e with it and 4.7b without it
def stringBinder : Json := toJson [toJson "forall", toJson "$string", toJson [toJson "top"]]
#guard checkOf [ruleOf "r0" "paid" stringBinder] (envOf [] (actOf 20) ["acts@0", "data@0", "norms@0", "relational-fol@0"])
  == some "norms/4.7e" && checkOf [ruleOf "r0" "paid" stringBinder] == some "norms/4.7b"
-- one running node total over the rules, from none: two rules of half the budget each fit, and a third node is
-- refused at the third rule
def balancedOn : Nat → Nat → Json
  | 0, _ => unaryOn "w"
  | fuel + 1, n => if n ≤ 1 then unaryOn "w" else
    toJson [toJson "and", balancedOn fuel ((n + 1) / 2), balancedOn fuel (n - (n + 1) / 2)]
def faultOf (norms : List Json) : Option (String × String) :=
  (run Tables.Acts.table hooks (Json.mkObj [("environment", envOf [] (actOf 20)), ("norms", toJson norms)])).map fun f =>
    let r := record Tables.Acts.table f
    ((r.getObjValD "check").getStr?.toOption.getD "", (r.getObjValD "path").getStr?.toOption.getD "")
#guard let half := balancedOn 32 ((VE.Limits.maxNodes / 2 + 1) / 3)
  faultOf [ruleOf "r0" "paid" half, ruleOf "r1" "paid" half, ruleOf "r2" "paid" (toJson [toJson "top"])] ==
    some ("norms/4.7d", "/norms/2")
-- one run's hooks (`hooksFor`) give the record `hooks` gives, the environment decoded once (ap-1bfb review F2); on
-- another root they are `hooks`
def bothOf (environment : Json) (norms : List Json) : Bool :=
  let j := Json.mkObj [("environment", environment), ("norms", toJson norms)]
  (run Tables.Acts.table (hooksFor j) j).map (record Tables.Acts.table) ==
    (run Tables.Acts.table hooks j).map (record Tables.Acts.table)
def resultOf : ClassifierResult → Option String
  | .ok => none
  | .fail m _ => some m
#guard let half := balancedOn 32 ((VE.Limits.maxNodes / 2 + 1) / 3)
  [([ruleOf "r0" "paid" (unaryOn "w")], envOf [] (actOf 20)),
   ([ruleOf "r0" "paid" (unaryOn "w"), ruleOf "r1" "paid" (unaryOn "nope")], envOf [] (actOf 20)),
   ([ruleOf "r0" "paid" half, ruleOf "r1" "paid" half, ruleOf "r2" "paid" (toJson [toJson "top"])], envOf [] (actOf 20)),
   ([ruleOf "r0" "paid" (unaryOn "nope")], joinedEnv), ([ruleOf "r0" "paid" (unaryOn "nope")], envOf [] (actOf (maxActBytes + 1))),
   ([], framed [frameOf "Give"]), ([], framed (framesOf (framesLimit + 1))),
   ([ruleOf "r0" "paid" stringBinder], envOf [] (actOf 20) ["acts@0", "data@0", "norms@0", "relational-fol@0"])].all
    fun (norms, environment) => bothOf environment norms
#guard let other := Json.mkObj [("environment", envOf [] (actOf 20)), ("norms", toJson [ruleOf "r0" "paid" (unaryOn "nope")])]
  let j := Json.mkObj [("environment", envOf [] (actOf 20)), ("norms", toJson [ruleOf "r0" "paid" (unaryOn "w")])]
  resultOf (hooks.classifier "rule_typing" other [["norms", "0"]]) == some "4.7b" &&
  [("rule_typing", [["norms", "0"]]), ("acts_environment", [])].all fun (n, items) =>
    resultOf ((hooksFor j).classifier n other items) == resultOf (hooks.classifier n other items) &&
      resultOf ((hooksFor j).classifier n j items) == resultOf (hooks.classifier n j items)
-- `norms@0`'s own run, with and without `data@0`: one run's hooks (`Hooks.Norms.hooksFor`) give `Hooks.Norms.hooks`'
-- record, and 4.7, 3.8 and the node total are found
def normsEnv (profiles : List String := ["norms@0", "relational-fol@0"]) : Json :=
  let e := envOf [] (actOf 20) profiles
  let v := match e.getObjValD "vocabulary" with | .obj kvs => Json.obj (kvs.erase "acts") | v => v
  e.setObjVal! "vocabulary" (v.setObjVal! "predicates" ((v.getObjValD "predicates").setObjVal! "paid" (Json.mkObj
    [("arguments", toJson ["person"]), ("description", "d"), ("regulated", Json.mkObj [("role", "permission"),
      ("default", "allow"), ("act", "{0} seek protection")])])))
def normsCheckOf (h : Hooks) (environment : Json) (norms : List Json) : Option String :=
  let j := Json.mkObj [("environment", environment), ("norms", toJson norms)]
  (run Tables.Norms.table h j).map fun f => ((record Tables.Norms.table f).getObjValD "check").getStr?.toOption.getD ""
#guard let half := balancedOn 32 ((VE.Limits.maxNodes / 2 + 1) / 3)
  [([ruleOf "r0" "paid" (unaryOn "w")], normsEnv, none),
   ([ruleOf "r0" "paid" (unaryOn "w"), ruleOf "r1" "paid" (unaryOn "nope")], normsEnv, some "4.7b"),
   ([ruleOf "r0" "paid" (toJson [toJson "nope"])], normsEnv, some "3.8b"),
   ([ruleOf "r0" "paid" half, ruleOf "r1" "paid" half, ruleOf "r2" "paid" (toJson [toJson "top"])], normsEnv, some "4.7d"),
   ([ruleOf "r0" "paid" stringBinder], normsEnv ["data@0", "norms@0", "relational-fol@0"], some "4.7e"),
   ([ruleOf "r0" "paid" stringBinder], normsEnv, some "4.7b")].all fun (norms, environment, check) =>
    let j := Json.mkObj [("environment", environment), ("norms", toJson norms)]
    normsCheckOf (Hooks.Norms.hooksFor j) environment norms == check && normsCheckOf Hooks.Norms.hooks environment norms == check
-- the profile row before the decoder, on any list that names `acts@0`: an unsorted one with an unknown field
#guard (match decoded ((envOf [] (actOf 20) ["norms@0", "relational-fol@0", "acts@0"]).setObjVal! "x" 1) with
  | .error e => e | .ok () => "") == "UnsupportedProfile: profiles must be sorted and unique"
-- the rule phases are `norms@0`'s, as its generated table has them, under the one include `norms`
deriving instance BEq for Step
deriving instance BEq for Base
deriving instance BEq for Pattern
deriving instance BEq for Value
deriving instance BEq for Atom
deriving instance BEq for TypeForm
deriving instance BEq for Lit
deriving instance BEq for NameClass
deriving instance BEq for Renderer
deriving instance BEq for Piece
deriving instance BEq for Member
deriving instance BEq for Kind
deriving instance BEq for Check
deriving instance BEq for Entry
#guard match Tables.Acts.table.phases with
  | [⟨"environment", _⟩, ⟨"rules", [.scope "norms" ⟨.root, []⟩ none none es]⟩] =>
    es == (Tables.Norms.table.phases.filter (·.name != "environment")).flatMap (·.entries) &&
      Tables.Norms.table.phases.map (·.name) == ["environment", "profiles", "rule-shape", "rules", "references", "semantic"]
  | _ => false
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
