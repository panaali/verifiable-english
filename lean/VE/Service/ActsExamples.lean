import VE.Service.FamilyNorms
import VE.EnglishGrammar.Policy
import VE.EnglishGrammar.Encode
import VE.Acts.LexicalExamples
import VE.Norms.Run
import VE.Words.Situation
import VE.NormDefaults.Run
import VE.Readings.Run

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
-- the norm-defaults route sets its profile aside, which must not sort the list `acts@0` is read from
#guard err (VE.NormDefaults.Wire.decodeSourceU (envA ["norm-defaults@0", "acts@0", "norms@0", "relational-fol@0"])
  (Json.arr #[rule "heard"])) == sortedRefusal
#guard err (VE.Service.Standalone.validatedComposedEnvironment
  (envA ["norm-defaults@0", "acts@0", "norms@0", "relational-fol@0"])) == sortedRefusal
-- wherever the disorder or `acts@0` stands in the list: before, after or around `norm-defaults@0`, or last
#guard [["acts@0", "norms@0", "norm-defaults@0", "relational-fol@0"],
    ["acts@0", "norms@0", "relational-fol@0", "norm-defaults@0"], ["norm-defaults@0", "acts@0"]].all fun ps =>
  err (VE.NormDefaults.Wire.decodeSourceU (envA ps) (Json.arr #[rule "heard"])) == sortedRefusal
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

/-! ### ap-1bb: the environment row gives the canonical act its identity hashes, by predicate, for Python to store;
two environments with one identity have the same acts -/

def environmentRow (j : Json) : Json :=
  match VE.Service.Standalone.environmentCase (Json.mkObj [("id", .str "e"), ("environment", j)]) with
  | .ok row => row
  | .error m => .str m
def curly := env actsP [("p", pred ["person", "case"] (perm "{0}  comply with the operator’s instructions in {1}"))]
def straight := env actsP [("p", pred ["person", "case"] (perm "{0} comply with the operator's instructions in {1}"))]
#guard (environmentRow curly).getObjValD "acts" ==
  Json.mkObj [("p", .str "{0} comply with the operator's instructions in {1}")]
#guard (environmentRow curly).getObjValD "environment_id" == (environmentRow straight).getObjValD "environment_id" &&
  (environmentRow curly).getObjValD "acts" == (environmentRow straight).getObjValD "acts"
-- the identity is `environmentIdOf`'s; every regulated act (plain and permission) is listed, in vocabulary order
#guard (environmentRow curly).getObjValD "environment_id" ==
  ((VE.Service.Standalone.environmentIdOf actsP curly).toOption.map Json.str).getD .null
#guard (environmentRow envA).getObjValD "acts" == Json.mkObj [("heard", .str a1), ("paid", .str a2), ("protected", .str a3)]
-- no regulated act: none
#guard (environmentRow (env ["relational-fol@0"] [("p", Json.mkObj [("arguments", toJson ["person"]),
  ("description", .str "d")])])).getObjValD "acts" == Json.mkObj []
-- the route row's members
def members (row : Json) : Option (List String) := row.getObj?.toOption.map (·.toList.map (·.1))
#guard members (environmentRow envA) == some ["acts", "environment_id", "family", "id", "profiles", "status"]
#guard [(environmentRow envA).getObjValD "id", (environmentRow envA).getObjValD "status",
  (environmentRow envA).getObjValD "family", (environmentRow envA).getObjValD "profiles"] ==
  [.str "e", .str "ok", .str "fol", toJson actsP]

/-- A frozen envelope: `language`, then `profile` (v0) or `profiles` (ve.core@0.1), and its `spec_revision`. -/
def frozen (language : String) (profiles : String × Json) (revision : String) : Json :=
  Json.mkObj [("language", .str language), profiles, ("spec_revision", .str revision),
    ("vocabulary", Json.mkObj [("sorts", Json.mkObj [("item", desc "item")]),
      ("predicates", Json.mkObj [("rel", Json.mkObj [("arguments", toJson ["item", "item"]),
        ("description", .str "rel")])]), ("constants", Json.mkObj [])])]
def closure01 := frozen "ve.core@0.1" ("profiles", toJson ["closure@0", "relational-fol@0"]) "ve-v0.1-closure-2026-09-21"
def core0 := frozen "ve.core@0" ("profile", .str "relational-fol@0") "ve-v0-draft-2026-09-20"
-- ve.core@0.1 lists its profiles, its family and no act; v0 names its one profile and has no `acts`
#guard members (environmentRow closure01) == some ["acts", "environment_id", "family", "id", "profiles", "status"]
#guard [(environmentRow closure01).getObjValD "acts", (environmentRow closure01).getObjValD "family",
  (environmentRow closure01).getObjValD "profiles"] == [Json.mkObj [], .str "closure", toJson ["closure@0", "relational-fol@0"]]
#guard members (environmentRow core0) == some ["environment_id", "family", "id", "profile", "status"]
#guard [(environmentRow core0).getObjValD "family", (environmentRow core0).getObjValD "profile"] ==
  [.str "fol", .str "relational-fol@0"]

/-! ### 4.4: the environment mode and the family route gate `acts@0` by its row first -/

#guard err (VE.Service.Standalone.validatedComposedEnvironment envA) == "ok"
-- the row admits the readings route, whose decoder reads `acts@0` (ap-1bd; its refusals in section "ap-1bd")
#guard err (VE.Service.Standalone.validatedComposedEnvironment (envA ["acts@0", "norms@0", "readings@1",
  "relational-fol@0"])) == "ok"
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

/-! ### ap-1bb: the norms route's `norms-elaborate` row gives the same wording of each plain act (`wordings`), by
its predicate, for Python to display; no other predicate has one -/

def routeWordings (j : Json) : Json := match VE.Norms.Run.runCase (Json.mkObj [("id", .str "w"),
    ("kind", .str "norms-elaborate"), ("environment", j), ("norms", Json.arr #[])]) with
  | .ok row => row.getObjValD "wordings"
  | .error m => .str m
#guard routeWordings envA == Json.mkObj [
  ("heard", .str "{0} is entitled in full equality to a fair and public hearing by an independent and impartial tribunal in {1}"),
  ("paid", .str "{0} has the right to equal pay for equal work without any discrimination")]
-- each is Lean's English selection (A1 109 B, A2 72 B)
#guard ["heard", "paid"].map (fun p => (routeWordings envA).getObjValD p) ==
  (((wordings envA).filterMap (·.1)).take 2).map Json.str
-- A21 as a plain act: its 414-byte wording
#guard ((routeWordings (env actsP [("heard", pred ["person"] (plain VE.Acts.LexicalExamples.a21 "has the right"))])).getObjValD
  "heard").getStr?.toOption.map String.utf8ByteSize == some 414
-- a permission, and every predicate without `acts@0`, has none
#guard routeWordings (env actsP seek) == Json.mkObj []
#guard routeWordings (env ["norms@0", "relational-fol@0"] seek) == Json.mkObj []

/-! ### R16: the profile lists that tell each reader's list apart (`tools/trust_mutants.py` survivors)

`acts@0` sorts before every known profile, so a list that lists it starts with it; the lists below put an unknown
profile before it, leave it alone, or put the profile that decides last. -/

def bad : Option Json := some (block ["the court that is competent"])
def withRevision (j : Json) : Json := j.setObjVal! "spec_revision" (.str "x")
def profilesOr (e : Except String Json) : Json := match e with
  | .ok j => j.getObjValD "profiles"
  | .error m => .str m

-- `readsActs` reads the whole list: `acts@0` anywhere, and every pair in order
#guard [["acts@0"], ["a@0", "acts@0"], ["acts@0", "norms@0", "b@0"], ["norms@0", "acts@0"], ["norms@0"], []].map
  VE.Norms.Wire.readsActs == [true, true, false, false, false, false]
-- a list of `acts@0` alone is read: its block is checked and its envelope lacks the checker profile
#guard err (VE.Norms.Wire.canonicalEnvironmentJson (env ["acts@0"] seek bad)) ==
  "InvalidInput: fixed phrase 'the court that is competent' uses the clause word 'is'"
#guard err (decodeA (envA ["acts@0"])) == "UnsupportedProfile: Missing profile relational-fol@0"
-- the plain route gates the list before it reads the block, wherever `acts@0` stands in it
#guard plainRun (env ["a@0", "acts@0", "norms@0", "relational-fol@0"] seek bad) ==
  "UnsupportedProfile: Unsupported profile a@0"
#guard plainRun (env ["acts@0"] seek bad) == "UnsupportedProfile: Missing profile relational-fol@0"
-- the replay's base environment without `acts@0`: `norms@0` set aside, the rest kept
#guard profilesOr (VE.Norms.Replay.baseEnvironmentJson (env ["norms@0", "relational-fol@0"] seek)) ==
  toJson ["relational-fol@0"]
-- the typing view reads `acts@0` wherever it is listed
#guard profilesOr (typingView (env ["a@0", "acts@0", "norms@0", "relational-fol@0"] seek (some (block fxs)))) ==
  toJson ["a@0", "norms@0", "relational-fol@0"]
#guard profilesOr (typingView (env ["acts@0"] seek (some (block fxs)))) == toJson ([] : List String)
-- ap-1b recheck F3: each stage of the typing view reduces the list the stages before it left, so `acts@0` never
-- lists again a profile an earlier stage erased. Every list of `actsP` and one or two more environment profiles
-- that the table admits: its view lists exactly the rest, and the service validates it.
def admittedWithActs : List (List String) :=
  let extras := VE.Compose.environmentProfiles.filter (fun q => !actsP.contains q)
  let lists := extras.map ([·]) ++ extras.flatMap fun q => extras.filterMap fun r => if q < r then some [q, r] else none
  (lists.map fun xs => (actsP ++ xs).mergeSort (fun a b => !(b < a))).filter fun ps =>
    (VE.Compose.gateOf VE.Compose.profileTable ps).toOption.isSome
#guard admittedWithActs.any (·.contains "norm-defaults@0") && admittedWithActs.any (·.contains "readings@1")
#guard admittedWithActs.all fun ps => profilesOr (typingView (envA ps)) ==
  toJson (ps.filter fun p => !["acts@0", "norm-defaults@0", "readings@1"].contains p)
#guard admittedWithActs.all fun ps =>
  err (typingView (envA ps) >>= fun v => (fun _ => ()) <$> VE.Service.Standalone.validated v) == "ok"
-- `acts@0` is read from the submitted list, not the reduced one: this list is sorted once `norm-defaults@0` is erased
#guard profilesOr (typingView (envA ["norm-defaults@0", "acts@0", "norms@0", "relational-fol@0"])) ==
  toJson ["acts@0", "norms@0", "relational-fol@0"]
-- Lean's English reads `norms@0` and `norm-defaults@0` wherever they are listed (an `unspecified` default is read
-- as its placeholder only under `norm-defaults@0`)
def unspecified : List (String × Json) := [("p", pred ["person"]
  [("role", .str "permission"), ("default", .str "unspecified"), ("act", .str "{0} seek asylum")])]
def modal (j : Json) : String := match Env.decode j (Json.mkObj []) with
  | .ok E => toString (E.modal "p")
  | .error m => m
#guard [modal (env ["acts@0", "norm-defaults@0", "norms@0", "relational-fol@0"] unspecified),
  modal (env ["norms@0", "norm-defaults@0"] unspecified), modal (env ["norm-defaults@0", "norms@0"] unspecified),
  modal (env ["norms@0"] seek)] == ["true", "true", "true", "true"]
-- the environment mode: the whole table gates a list with `readings@1` (its last profile when the checker is
-- missing), `acts@0` alone is gated, and `checkRegulated` runs, before the envelope, only without `norm-defaults@0`
-- (wherever it is listed) and `acts@0`
#guard err (VE.Service.Standalone.validatedComposedEnvironment (envA ["acts@0", "norms@0", "readings@1"])) ==
  "UnsupportedProfile: Missing profile relational-fol@0"
#guard err (VE.Service.Standalone.validatedComposedEnvironment (env ["acts@0"] seek bad)) ==
  "UnsupportedProfile: Missing profile relational-fol@0"
#guard [["norms@0", "relational-fol@0"], ["definitions@0", "norm-defaults@0", "norms@0", "relational-fol@0"],
    ["norms@0", "relational-fol@0", "norm-defaults@0"], ["norm-defaults@0", "norms@0", "relational-fol@0"]].map
  (fun ps => err (VE.Service.Standalone.validatedComposedEnvironment (withRevision (envA ps)))) ==
  ["InvalidInput: invalid regulated fields for heard", "UnsupportedProfile: Unsupported specification revision x",
   "UnsupportedProfile: Unsupported specification revision x",
   "UnsupportedProfile: Unsupported specification revision x"]
-- the family route gates a list with `acts@0` wherever it stands, and its FOL view drops exactly the three
-- checker-family profiles
#guard err (VE.Service.FamilyNorms.folView (envA ["a@0", "acts@0", "norms@0", "relational-fol@0"])) ==
  "UnsupportedProfile: Unsupported profile a@0"
#guard err (VE.Service.FamilyNorms.folView (envA ["acts@0"])) == "UnsupportedProfile: Missing profile relational-fol@0"
#guard [["closure@0", "norms@0", "relational-fol@0"], ["closure@0", "nary@0", "norms@0", "relational-fol@0"],
    ["norms@0", "order@0", "relational-fol@0"]].map (fun ps => profilesOr (VE.Service.FamilyNorms.folView (env ps seek))) ==
  List.replicate 3 (toJson ["norms@0", "relational-fol@0"])

/-! ### ap-1bc: the words route decodes a clause's declaration as Lean's English does (`VE.Words.regulatedOf`):
`acts@0` read from the environment's list with its block's fixed phrases (act-phrases 3.2), else today's decoder -/

/-- The role and act `regulatedOf` decodes for `p` in the environment `j`, reading the declarations, profiles and
block of `source` (by default `j` itself). -/
def regulatedIn (j : Json) (p : String) (source : Json := j) : Option (VE.Norms.Role × Option String) :=
  match Env.decode j (Json.mkObj []) with
  | .ok E => (VE.Words.regulatedOf { E with source } p).map fun r => (r.role, r.act)
  | .error _ => none
def threeOf (j : Json) (source : Json := j) := ["heard", "paid", "protected"].map (regulatedIn j · source)
def withBlock (j : Json) (b : Option Json) : Json := match j.getObjValD "vocabulary" with
  | .obj kvs => j.setObjVal! "vocabulary" (.obj (match b with | some b => kvs.insert "acts" b | none => kvs.erase "acts"))
  | _ => j
-- accepted: A1 and A2 plain with their acts and A3 a permission, each act with a fixed phrase (`and`, `for`)
#guard threeOf envA == [some (.plain, some a1), some (.plain, some a2), some (.permission, some a3)]
-- refused: without `acts@0` in the list, or with it in a list that is not sorted and unique (today's decoder)
#guard threeOf envA (envA ["norms@0", "relational-fol@0"]) == [none, none, none]
#guard unsorted.all fun ps => threeOf envA (envA ps) == [none, none, none]
-- the block's phrases are read: without the block, or without one phrase, that act's `and` or `for` is outside a
-- phrase; a block with a refused phrase decodes nothing
#guard threeOf envA (withBlock envA none) == [none, none, none]
#guard threeOf envA (withBlock envA (some (block (fxs.erase "equal pay for equal work")))) ==
  [some (.plain, some a1), none, some (.permission, some a3)]
#guard threeOf envA (withBlock envA (some (block (fxs ++ ["the court that is competent"])))) == [none, none, none]
-- the act limits: today's 80 characters (at it both decoders accept, one past it only `acts@0`'s), and `acts@0`'s
-- 400 bytes (at it accepted, one past it refused); A19's apostrophe folded
def ab (k : Nat) (tail : String := "") : String := "{0}" ++ String.join (List.replicate k " ab") ++ tail
def permEnv (profiles : List String) (act : String) : Json := env profiles [("p", pred ["person"] (perm act))]
#guard [ab 25 " a", ab 26, VE.Acts.LexicalExamples.a21, ab 132 " a"].map String.utf8ByteSize == [80, 81, 400, 401]
#guard [ab 25 " a", ab 26, VE.Acts.LexicalExamples.a21].all fun a => regulatedIn (permEnv actsP a) "p" == some (.permission, some a)
#guard [ab 25 " a", ab 26].map (fun a => regulatedIn (permEnv actsP a) "p" (permEnv ["norms@0", "relational-fol@0"] a)) ==
  [some (.permission, some (ab 25 " a")), none]
#guard regulatedIn (permEnv actsP VE.Acts.LexicalExamples.a21) "p" (permEnv actsP (ab 132 " a")) == none
#guard regulatedIn curly "p" == some (.permission, some "{0} comply with the operator's instructions in {1}")

/-- The words route's clause and pair sentence in `j`, with the lexicon Lean's English selects. -/
def lexiconOf (E : Env) : Lexicon := { VE.Words.nounsOnly [("person", "person"), ("case", "case")] with
  wordings := E.predicates.filterMap fun d => (policyPredicate E {} d.name).map (d.name, ·.1) }
def clause (j : Json) (p : String) (names : List String) (value : Bool) : Option String :=
  (Env.decode j (Json.mkObj [])).toOption.bind fun E => VE.Words.clauseAt E (lexiconOf E) p names value
def pair (j : Json) (p : String) : Option String :=
  (Env.decode j (Json.mkObj [])).toOption.bind fun E => VE.Words.pairSentence E (lexiconOf E) p
-- a plain act's clause is its wording whatever the value; a permission's has its modal
#guard [true, false].map (clause envA "heard" ["Ann", "the trial"]) == List.replicate 2
  (some "Ann is entitled in full equality to a fair and public hearing by an independent and impartial tribunal in the trial")
#guard [true, false].map (clause envA "protected" ["Ann", "the trial"]) ==
  [some "Ann may to the protection of the moral and material interests resulting from the trial",
   some "Ann must not to the protection of the moral and material interests resulting from the trial"]
-- refused: a predicate that is not regulated has no clause
def late : List (String × Json) := [("late", Json.mkObj [("arguments", toJson ["person"]), ("description", .str "d")])]
#guard clause (env actsP (seek ++ late)) "late" ["Ann"] true == none
-- the pair sentence of an obligation whose act has a fixed phrase (97 B); a plain act has none
def dual : List (String × Json) := [("must_hear", pred ["person", "case"] [("role", .str "obligation"),
  ("default", .str "deny"), ("act", .str a1), ("permission", .str "may_hear")]), ("may_hear", pred ["person", "case"] (perm a1))]
#guard pair (env actsP dual (some (block fxs))) "must_hear" == some ("Whenever a person must in full equality to a fair " ++
  "and public hearing by an independent and impartial tribunal in a case, it may in full equality to a fair and public " ++
  "hearing by an independent and impartial tribunal in that case.")
#guard pair envA "heard" == none


/-! ### ap-1be: the norm-defaults route's `norm-defaults-elaborate` row gives the norms route's `wordings` of the
decoded source, for `norm-defaults@0` environments; refused sources give no row -/

def ndP : List String := ["acts@0", "norm-defaults@0", "norms@0", "relational-fol@0"]
def ndRow (j : Json) : Json := VE.NormDefaults.Run.runCaseReported (Json.mkObj [("id", .str "w"),
  ("kind", .str "norm-defaults-elaborate"), ("environment", j), ("norms", Json.arr #[])])
def ndWordings (j : Json) : Json := (ndRow j).getObjValD "wordings"
-- A1 and A2 (109 B and 72 B), exactly the norms route's and Lean's English selection; a permission has none
#guard ndWordings (envA ndP) == routeWordings envA
#guard ["heard", "paid"].map (fun p => (ndWordings (envA ndP)).getObjValD p) ==
  (((wordings envA).filterMap (·.1)).take 2).map Json.str
-- a plain act whose default is `unspecified` has its wording; so has A21 at the 400-byte limit (414 B)
def unspecPlain : List (String × Json) := [("heard", pred ["person"] [("role", .str "plain"),
  ("default", .str "unspecified"), ("act", .str "{0} to be heard"), ("form", .str "has the right")])]
#guard ndWordings (env ndP unspecPlain) == Json.mkObj [("heard", .str "{0} has the right to be heard")]
#guard ((ndWordings (env ndP [("heard", pred ["person"] (plain VE.Acts.LexicalExamples.a21 "has the right"))])).getObjValD
  "heard").getStr?.toOption.map String.utf8ByteSize == some 414
-- none for a permission (`unspecified` or not), and none without `acts@0`
#guard ndWordings (env ndP unspecified) == Json.mkObj [] && ndWordings (env ndP seek) == Json.mkObj []
#guard ndWordings (env ["norm-defaults@0", "norms@0", "relational-fol@0"] unspecified) == Json.mkObj []
-- refused, so no row: a 401-byte act, an unsorted list, and `acts@0` with `soft-norms@0`
#guard [env ndP [("heard", pred ["person"] (plain (VE.Acts.LexicalExamples.a21 ++ "b") "has the right"))],
    envA ["norm-defaults@0", "acts@0", "norms@0", "relational-fol@0"],
    envA ["acts@0", "norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"]].map
  (fun j => ((ndRow j).getObjValD "status", ndWordings j)) == List.replicate 3 (Json.str "error", Json.null)
-- the row's other members are the base's: `wordings` is the one added
#guard members (ndRow (env ndP unspecPlain)) == some ["background", "conflict_targets", "document_hash",
  "environment_id", "fill", "fill_hash", "fill_labels", "filled_environment_id", "fragment", "fragment_fill", "id",
  "order", "premises", "reached", "status", "unsaid", "unspecified", "wordings"]

/-! ### ap-1bd: typing, the model path and the readings route read `acts@0` (`Standalone.regulatedOf`, `actsRead`;
`Readings.Wire.singleActsOnly`, D-33) -/

def typed (j : Json) (ast : Json := Json.arr #[.str "top"]) : String :=
  err (VE.Service.Standalone.checkCase (Json.mkObj [("id", .str "c"), ("environment", j), ("ast", ast)]))
def every (sort p : String) : Json :=
  toJson [toJson "forall", toJson sort, toJson [toJson "unary", toJson p, toJson [toJson "var", toJson 0]]]
-- typing reads the environment: with and without `norm-defaults@0`, and a formula on a plain act's predicate
#guard [typed envA, typed (envA ndP), typed envA (every "person" "paid")] == ["ok", "ok", "ok"]
#guard typed envA (every "case" "paid") == "TypeMismatch: Predicate 'paid' expects ('person',), received ('case',)"
-- refused: without `acts@0` as today, an unsorted list as the base refuses it, the row's refusals first
#guard typed (envA ["norms@0", "relational-fol@0"]) == "InvalidInput: invalid regulated fields for heard"
#guard unsorted.all fun ps => typed (envA ps) == sortedRefusal
#guard typed (envA ["acts@0", "closure@0", "norms@0", "relational-fol@0"]) ==
  "UnsupportedProfile: acts@0 on the closure family is not implemented"
#guard typed (envA ["acts@0", "relational-fol@0"]) == "UnsupportedProfile: acts@0 requires norms@0"
-- the act check is `acts@0`'s, with the block's fixed phrases: A1 without them joins acts; 400 bytes and one past
#guard typed (env actsP [("heard", pred ["person", "case"] (plain a1 "is entitled"))]) ==
  "InvalidInput: act phrase for heard joins acts with 'and' outside a fixed phrase"
#guard [typed (permEnv actsP VE.Acts.LexicalExamples.a21), typed (permEnv actsP (ab 132 " a"))] ==
  ["ok", "ResourceLimit: act phrase for p is over 400 bytes"]

-- the model path: a model is checked against the profile pair of an obligation whose act is `acts@0`'s (97 B)
def modelled (j : Json) (rels : List (String × Json)) : String :=
  err (VE.Service.Standalone.modelCase (Json.mkObj [("id", .str "m"), ("environment", j), ("model", Json.mkObj [
    ("complete", .bool true), ("domains", Json.mkObj [("person", toJson ["p"]), ("case", toJson ["c"])]),
    ("constants", Json.mkObj []), ("relations", Json.mkObj rels)])]))
def dualEnv := env actsP dual (some (block fxs))
#guard modelled envA [("heard", Json.arr #[]), ("paid", toJson [["p"]]), ("protected", Json.arr #[])] == "ok"
#guard modelled dualEnv [("must_hear", toJson [["p", "c"]]), ("may_hear", toJson [["p", "c"]])] == "ok"
#guard modelled dualEnv [("must_hear", toJson [["p", "c"]]), ("may_hear", Json.arr #[])] ==
  "InvalidModel(profile): required relation must_hear exceeds permission may_hear"
#guard modelled (permEnv ["norms@0", "relational-fol@0"] (ab 26)) [("p", Json.arr #[])] ==
  "InvalidInput: invalid act phrase for p"
-- the family routes' Background holds that pair's profile premise
#guard ((decodeA dualEnv).toOption.bind fun ne => (VE.Service.Standalone.folBackground dualEnv ne.rv).toOption.map
  fun bg => (bg.filter (·.2 == "profile")).length) == some 1

-- the readings route reads single acts (A1-A3, with and without `norm-defaults@0`)
def rdP : List String := ["acts@0", "norms@0", "readings@1", "relational-fol@0"]
#guard (VE.Readings.Wire.decodeEnvironment (envA rdP)).toOption.map (·.se.ne.regulated.map (·.act)) ==
  some [some a1, some a2, some a3]
#guard err (VE.Readings.Wire.decodeEnvironment (envA ["acts@0", "norm-defaults@0", "norms@0", "readings@1",
  "relational-fol@0"])) == "ok"
-- and admits a document with a rule on a plain act (the norms chain's `Soften.checkW1` admits the act)
def ruleDoc (p : String) : Json := Json.mkObj [("units", Json.arr #[Json.mkObj [("id", .str "u1"), ("kind", .str "norm"),
  ("content", rule p)]]), ("reading_sets", Json.arr #[])]
#guard err (VE.Readings.Run.validateOne "v" (envA rdP) (ruleDoc "paid")) == "ok"
-- D-33 for a joined act (A5's "and", A6's "or" with its phrase undeclared; plain or a permission); the norms route
-- keeps D-4; every other act refusal (D-5's comma) and the block's refusal without `acts@0` are the decoder's own
def d33 (p : String) : String :=
  s!"UnsupportedProfile: acts@0 on the readings route admits single acts only; the act of {p} joins acts"
#guard [env rdP [("p", pred ["person"] (plain a5 "has the right"))], env rdP [("p", pred ["person"] (perm a5))],
  env rdP [("p", pred ["person"] (plain a6 "has the right"))] (some (block fxs))].map
    (err ∘ VE.Readings.Wire.decodeEnvironment) == List.replicate 3 (d33 "p")
#guard err (VE.Readings.Wire.decodeEnvironment (env rdP [("p", pred ["person"] (plain "{0} seek, asylum" "has the right"))]))
  == "InvalidInput: act phrase for p has a comma outside a fixed phrase"
#guard err (VE.Readings.Wire.decodeEnvironment (envA ["norms@0", "readings@1", "relational-fol@0"])) ==
  "fields do not match: expected [sorts, predicates, constants], got [acts, constants, predicates, sorts]"
-- the environment mode gives the route's refusal; the predicate named is the one D-4 names, never a prefix of it
#guard err (VE.Service.Standalone.validatedComposedEnvironment (env rdP [("p", pred ["person"] (plain a5 "has the right"))]))
  == d33 "p"
#guard VE.Readings.Wire.singleActsOnly ["p", "pp"]
  "InvalidInput: act phrase for pp joins acts with 'or' outside a fixed phrase" == d33 "pp"
#guard VE.Readings.Wire.singleActsOnly ["q"] "InvalidInput: act phrase for p joins acts with 'or' outside a fixed phrase"
  == "InvalidInput: act phrase for p joins acts with 'or' outside a fixed phrase"

end VE.Service.ActsExamples
