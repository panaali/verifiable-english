import VE.Service.FamilyNorms
import VE.EnglishGrammar.Policy
import VE.EnglishGrammar.Encode
import VE.Acts.LexicalExamples

/-! act-phrases AP-1, the profile part (ap-1b): `acts@0` documents through the norms decoder, the environment
mode, the family route and Lean's English (spec 2.1, 2.8, 3.1-3.3, 4.4; fixtures A1-A3, A5, A6, A19 of 11.1).
Each environment is built as a service request carries it. -/

namespace VE.Service.ActsExamples
open Lean VE.Grammar VE.EnglishGrammar

def a1 := "{0} in full equality to a fair and public hearing by an independent and impartial tribunal in {1}"
def a2 := "{0} to equal pay for equal work without any discrimination"
def a3 := "{0} to the protection of the moral and material interests resulting from {1}"
def a5 := "{0} to seek and to enjoy in other countries asylum from persecution"
def a6 := "{0} be subjected to torture or to cruel, inhuman or degrading treatment or punishment"
def fxs : List String := ["a fair and public hearing by an independent and impartial tribunal",
  "equal pay for equal work", "the moral and material interests"]

def desc (d : String) : Json := Json.mkObj [("description", .str d)]
def pred (args : List String) (reg : List (String × Json)) : Json :=
  Json.mkObj [("arguments", toJson args), ("description", .str "d"), ("regulated", Json.mkObj reg)]
def plain (act form : String) : List (String × Json) :=
  [("role", .str "plain"), ("default", .str "deny"), ("act", .str act), ("form", .str form)]
def perm (act : String) : List (String × Json) := [("role", .str "permission"), ("default", .str "allow"), ("act", .str act)]
/-- An environment with `profiles`, the predicates `preds` and, when given, the `acts` block. -/
def env (profiles : List String) (preds : List (String × Json)) (acts : Option Json := none) : Json :=
  Json.mkObj [("language", .str "ve.core@0.2"), ("profiles", toJson profiles),
    ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"),
    ("vocabulary", Json.mkObj ([("sorts", Json.mkObj [("person", desc "person"), ("case", desc "case")]),
      ("predicates", Json.mkObj preds), ("constants", Json.mkObj [])] ++ acts.toList.map ("acts", ·)))]
def block (fx : List String) : Json := Json.mkObj [("fixed", toJson fx)]
def actsP : List String := ["acts@0", "norms@0", "relational-fol@0"]
/-- A1, A2 (plain, with their forms) and A3 (a permission), with their fixed phrases. -/
def envA (profiles : List String := actsP) : Json :=
  env profiles [("heard", pred ["person", "case"] (plain a1 "is entitled")),
    ("paid", pred ["person"] (plain a2 "has the right")), ("protected", pred ["person", "case"] (perm a3))]
    (some (block fxs))

def err {α} (e : Except String α) : String := match e with | .error m => m | .ok _ => "ok"
def decodeA (j : Json) := VE.Norms.Wire.decodeNormsEnvironment j (acts := true)

def rule (p : String) : Json := Json.mkObj [("norm", Json.mkObj [("name", .str "m"), ("predicate", .str p),
  ("sign", .bool true), ("guard", Json.arr #[.str "top"]), ("unless", Json.arr #[]), ("over", Json.arr #[])])]
def seek : List (String × Json) := [("p", pred ["person"] (perm "{0} seek asylum"))]

/-! ### 2.8, 3.1, 3.2: the norms decoder reads `acts@0` when its route lets it -/

-- A1-A3 accepted, each act as written (A1 97 B, over today's 80), the profiles as listed
#guard (decodeA envA).toOption.map (fun ne => (ne.regulated.map (·.act), ne.profiles)) ==
  some ([some a1, some a2, some a3], actsP)
-- a decoder whose route does not hook `acts@0` refuses it, as today
#guard err (VE.Norms.Wire.decodeNormsEnvironment envA) == "UnsupportedProfile: Unsupported profile acts@0"
-- A5 and A6 refused with D-4; A1 without its fixed phrase too (its "and" is outside a phrase)
#guard err (decodeA (env actsP [("p", pred ["person"] (plain a5 "has the right"))])) ==
  "InvalidInput: act phrase for p joins acts with 'and' outside a fixed phrase"
#guard err (decodeA (env actsP [("p", pred ["person"] (perm a6))]
  (some (block ["cruel, inhuman or degrading treatment or punishment"])))) ==
  "InvalidInput: act phrase for p joins acts with 'or' outside a fixed phrase"
#guard err (decodeA (env actsP [("heard", pred ["person", "case"] (plain a1 "is entitled"))])) ==
  "InvalidInput: act phrase for heard joins acts with 'and' outside a fixed phrase"
-- the block: absent is empty; exactly `fixed`, a list of strings, each phrase checked (A18: D-12)
#guard err (decodeA (env actsP seek)) == "ok"
#guard err (decodeA (env actsP seek (some (Json.mkObj [("fixed", toJson ([] : List String)),
  ("frames", Json.arr #[])])))) == "fields do not match: expected [fixed], got [fixed, frames]"
#guard err (decodeA (env actsP seek (some (Json.mkObj [("fixed", Json.arr #[.num 7])])))) == "String expected"
#guard err (decodeA (env actsP seek (some (block ["the court that is competent"])))) ==
  "InvalidInput: fixed phrase 'the court that is competent' uses the clause word 'is'"
#guard err (decodeA (env actsP [] (some (block ["the court that is competent"])))) ==
  "InvalidInput: fixed phrase 'the court that is competent' uses the clause word 'is'"
-- without `acts@0` the block is refused by today's vocabulary decoder, a block it would refuse too (unread)
#guard err (decodeA (env ["norms@0", "relational-fol@0"] seek (some (block [])))) ==
  "fields do not match: expected [sorts, predicates, constants], got [acts, constants, predicates, sorts]"
#guard err (decodeA (env ["norms@0", "relational-fol@0"] seek (some (block ["the court that is competent"])))) ==
  "fields do not match: expected [sorts, predicates, constants], got [acts, constants, predicates, sorts]"
-- a list with `acts@0` that is not sorted and unique is refused as the base refuses it, on every reader
def unsorted : List (List String) := [["norms@0", "acts@0", "relational-fol@0"],
  ["acts@0", "acts@0", "norms@0", "relational-fol@0"], ["relational-fol@0", "acts@0", "norms@0"]]
def sortedRefusal := "UnsupportedProfile: profiles must be sorted and unique"
#guard unsorted.all fun ps => (VE.Norms.Wire.actsProfiles true (envA ps)).isEmpty
#guard unsorted.all fun ps => err (decodeA (envA ps)) == sortedRefusal
#guard unsorted.all fun ps => err (VE.Norms.Wire.decodeSource (envA ps) (Json.arr #[rule "heard"])) == sortedRefusal
#guard err (VE.NormDefaults.Wire.decodeSourceU (envA ["norm-defaults@0", "norms@0", "acts@0", "relational-fol@0"])
  (Json.arr #[rule "heard"])) == sortedRefusal
-- the replay's base environment keeps `acts@0`, even where setting `norms@0` aside leaves a sorted list
#guard unsorted.map (fun ps => err (VE.Norms.Replay.baseEnvironmentJson (envA ps) >>= VE.Route.Gate.decodeEnvelope)) ==
  ["UnsupportedProfile: Unsupported profile acts@0", sortedRefusal, sortedRefusal]
-- the norms route (`decodeSource`) checks a rule on a plain predicate with an act (`Tree.check` admits it)
#guard err (VE.Norms.Wire.decodeSource envA (Json.arr #[rule "heard"])) == "ok"

-- the norm-defaults route (its own checks admit the plain act), the replay's base environment, the typing view
#guard err (VE.NormDefaults.Wire.decodeSourceU (envA ["acts@0", "norm-defaults@0", "norms@0", "relational-fol@0"])
  (Json.arr #[rule "heard"])) == "ok"
#guard err (VE.Norms.Replay.baseEnvironmentJson envA >>= VE.Route.Gate.decodeEnvelope) == "ok"
-- the typing view reads the environment without `acts@0` and its block
#guard (typingView envA).toOption.map (fun j => (j.getObjValD "profiles",
  ((j.getObjValD "vocabulary").getObjVal? "acts").toOption.isSome)) == some (toJson ["norms@0", "relational-fol@0"], false)
-- an unsorted list is left as it is listed, for the envelope decoder to refuse
#guard unsorted.all fun ps =>
  (typingView (env ps seek (some (block fxs)))).toOption.map (·.getObjValD "profiles") == some (toJson ps)

/-! ### 3.3: the identity's canonical act is `canonicalActIn`'s (A19's apostrophe folded) -/

#guard (VE.Norms.Wire.canonicalEnvironmentJson (env actsP [("p", pred ["person", "case"]
    (perm "{0}  comply with the operator’s instructions in {1}"))])).toOption.map
    (fun j => ((((j.getObjValD "vocabulary").getObjValD "predicates").getObjValD "p").getObjValD "regulated").getObjValD
      "act") == some (.str "{0} comply with the operator's instructions in {1}")
#guard (VE.Norms.Wire.canonicalEnvironmentJson (envA)).toOption.map (·.getObjValD "vocabulary" |>.getObjValD "acts") ==
  some (block fxs)

/-! ### 4.4: the environment mode and the family route gate `acts@0` by its row first -/

#guard err (VE.Service.Standalone.validatedComposedEnvironment envA) == "ok"
-- the row admits the readings route, whose decoder does not read `acts@0` yet (ap-1bb): it refuses the profile
#guard err (VE.Service.Standalone.validatedComposedEnvironment (envA ["acts@0", "norms@0", "readings@1",
  "relational-fol@0"])) == "UnsupportedProfile: Unsupported profile acts@0"
#guard err (VE.Service.Standalone.validatedComposedEnvironment (envA ["acts@0", "norms@0", "relational-fol@0",
  "soft-norms@0"])) == "UnsupportedProfile: acts@0 with soft-norms@0 is not implemented"
#guard err (VE.Service.Standalone.validatedComposedEnvironment (envA ["acts@0", "relational-fol@0"])) ==
  "UnsupportedProfile: acts@0 requires norms@0"
#guard err (VE.Service.FamilyNorms.folView (envA ["acts@0", "closure@0", "norms@0", "relational-fol@0"])) ==
  "UnsupportedProfile: acts@0 on the closure family is not implemented"
#guard err (VE.Service.FamilyNorms.folView (envA ["acts@0", "norms@0", "order@0", "relational-fol@0"])) ==
  "UnsupportedProfile: acts@0 on the order family is not implemented"

-- the plain route (Background, evaluation, countermodels) reads `acts@0` on the FOL family only
def plainRun (j : Json) : String :=
  err (VE.Norms.Plain.run (Json.mkObj [("id", .str "b"), ("kind", .str "background"), ("environment", j)]))
#guard plainRun envA == "ok"
#guard plainRun (envA ["acts@0", "closure@0", "norms@0", "relational-fol@0"]) ==
  "UnsupportedProfile: acts@0 on the closure family is not implemented"
#guard plainRun (envA ["acts@0", "norms@0", "order@0", "relational-fol@0"]) ==
  "UnsupportedProfile: acts@0 on the order family is not implemented"
#guard plainRun (envA ["norms@0", "relational-fol@0"]) == "InvalidInput: invalid regulated fields for heard"
#guard unsorted.all fun ps => plainRun (envA ps) == sortedRefusal
-- the submitted list is gated before the statement layers are set aside: the row's text, the whole list sorted
#guard plainRun (envA ["acts@0", "norms@0", "relational-fol@0", "soft-norms@0"]) ==
  "UnsupportedProfile: acts@0 with soft-norms@0 is not implemented"
#guard plainRun (envA ["acts@0", "norms@0", "relational-fol@0", "speech-acts@0"]) ==
  "UnsupportedProfile: acts@0 with speech-acts@0 is not implemented"
#guard plainRun (envA ["acts@0", "soft-norms@0", "norms@0", "relational-fol@0"]) == sortedRefusal
-- without `acts@0` the block is not read: today's vocabulary decoder refuses it, whatever its phrases
#guard plainRun (env ["norms@0", "relational-fol@0"] seek (some (block ["the court that is competent"]))) ==
  "fields do not match: expected [sorts, predicates, constants], got [acts, constants, predicates, sorts]"

/-! ### 2.1: Lean's English selects `Lexical.wording` for a plain act, over a declared wording, and keeps it
not modal; a permission keeps its modal form -/

def wordings (j : Json) : List (Option String × Bool) := match Env.decode j (Json.mkObj []) with
  | .ok E => ["heard", "paid", "protected"].map fun p =>
    ((policyPredicate E {} p).map (fun (w : String × Option String) => w.1), E.modal p)
  | .error _ => []
#guard wordings envA ==
  [(some "{0} is entitled in full equality to a fair and public hearing by an independent and impartial tribunal in {1}",
    false), (some "{0} has the right to equal pay for equal work without any discrimination", false),
   (some "{0} may to the protection of the moral and material interests resulting from {1}", true)]
#guard (((wordings envA).filterMap (·.1)).take 2).map String.utf8ByteSize == [109, 72]
-- A21 as a plain act (400 B): its 414-byte wording is selected, over the template lint's lengths (spec 2.1, F16)
#guard ((wordings (env actsP [("heard", pred ["person"] (plain VE.Acts.LexicalExamples.a21 "has the right"))])).head?.bind
  (·.1)).map String.utf8ByteSize == some 414
#guard (wordings (env actsP [("heard", Json.mkObj [("arguments", toJson ["person", "case"]), ("description", .str "d"),
    ("verbalisation", .str "{0} is heard in {1}"), ("regulated", Json.mkObj (plain a1 "is entitled"))]),
    ("paid", pred ["person"] (plain a2 "has the right")), ("protected", pred ["person", "case"] (perm a3))]
    (some (block fxs)))).head? ==
  some (some "{0} is entitled in full equality to a fair and public hearing by an independent and impartial tribunal in {1}",
    false)

end VE.Service.ActsExamples
