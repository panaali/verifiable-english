import VE.Acts.Decode
import VE.Acts.ElaborateExamples
import VE.Acts.MeaningExamples

/-! Fixtures of `checkAct`, step 6 and `decodeElaboratedU` (docs/spec/act-phrases.md 6.3, 6.4; D-15 to D-18; 11.3:
A6, A7, A14 from the act text, E13 to E15). Each check on both sides; the act trees come from the parse. -/

namespace VE.Acts.DecodeExamples
open Lean VE.Acts VE.Acts.Wire VE.Acts.Decode VE.Acts.Examples VE.Acts.RuleExamples VE.Acts.TableExamples
open VE.Acts.ElaborateExamples VE.Norms VE.NormDefaults
open VE.Acts.MeaningExamples (fx5)

def ck (fx : List String) (V : Vocab) (name : String) (k : Nat) (s : String) := checkAct fx V name k (.str s)
def errText {α : Type} (e : Except String α) : String := match e with | .error m => m | .ok _ => "ok"

/-! ### `checkAct` (6.4) -/

def a6 := "{0} be subjected to torture or to cruel, inhuman or degrading treatment or punishment"
def a7 := "{0} be held by secret vote or by equivalent free voting procedures"
def fx14 : List String := ["its core identity or principles", "to be human",
  "genuinely deceptive tactics that could harm users", "health or safety", "Anthropic's guidelines"]
def a14 := "{0} abandon its core identity or principles, claim to be human, use genuinely deceptive tactics that " ++
  "could harm users, endanger health or safety, or act against Anthropic's guidelines"
-- A lexical act is `Lexical.check`'s, normalised, with no tree.
#guard (ck fx6 V6 "p" 1 "{0}  be subjected to torture").toOption == some ("{0} be subjected to torture", none)
-- A6, A7, A14: a joined act and its one meaning; A7's is one atom (a joined filler, "by" is not a split marker).
#guard (ck fx6 V6 "p027" 1 a6).toOption == some (a6, some g6)
#guard (ck fx7 V7 "p079" 1 a7).toOption == some (a7, some g7)
#guard (ck fx14 V14 "p123" 1 a14).toOption == some (a14, some g14v)
-- A14's explicit residual: the sixth act holds the clause word *false* (F10), refused before the grammar (D-3).
#guard errText (ck fx14 V14 "p123" 1 (a14 ++ ", or provide false information that could deceive the user")) ==
  "InvalidInput: act phrase for p123 uses the clause word 'false'; write the condition in the rule's guard"
-- D-15 (G5d): every meaning, with no modal, in derivation order.
#guard errText (ck fx5 V5 "p051" 1 g5) == "InvalidInput: act phrase for p051 has more than one reading: 1. to seek " ++
  "asylum from persecution and to enjoy asylum from persecution in other countries. 2. to seek asylum from " ++
  "persecution in other countries and to enjoy asylum from persecution in other countries."
-- D-16, D-17 (L7: 128 raw derivations), D-18; the slot check runs before the parse.
#guard errText (ck fx6 ⟨[], []⟩ "p" 1 a6) == "InvalidInput: act phrase for p has no reading under the declared frames"
#guard errText (ck cities V5 "p" 1 (ln 7)) ==
  "ResourceLimit: act phrase for p has too many readings to list; split the sentence"
#guard (ck cities V5 "p" 1 (ln 6)).toOption.isNone && (ck cities V5 "p" 1 (ln 5)).toOption.isNone
#guard errText (ck [] V5 "p" 2 "{0} seek {1}s and enjoy asylum") ==
  "InvalidInput: act phrase for p has a slot joined to a word"
#guard ["{0} seek {1}s and enjoy asylum", "{0} seek asylum and enjoy {1}s", "{0} seek asylum and enjoy x{1}"].all
  fun s => errText (ck [] ⟨[], []⟩ "p" 2 s) == "InvalidInput: act phrase for p has a slot joined to a word"
-- Every other refusal of `Lexical.check` is its own: a comma at the end, a bad slot.
#guard errText (ck fx6 V6 "p" 1 (a6 ++ ",")) == "InvalidInput: act phrase for p ends with a comma"
#guard errText (ck fx6 V6 "p" 2 a6) == "InvalidInput: invalid act phrase for p"
-- A comma outside a fixed phrase (D-5) also goes to the grammar: G14v's list.
#guard errText (ck [] V5 "p" 1 "{0} seek asylum, enjoy asylum") ==
  "InvalidInput: act phrase for p has no reading under the declared frames"

/-! ### The pilot units from their text: `actsOf`, then `elaborateMap` -/

def U1 (n : String) (role : Role) (act : String) (ns : List Node) (unspec : List String := []) : UDoc :=
  (doc [rg n role (some act), rg "k" .obligation] (ns ++ [nd "rk" "k" true])).U |> fun U => { U with unspec }
def run (fx : List String) (V : Vocab) (U : UDoc) : Except String (UDoc × SplitMap) :=
  actsOf fx V U >>= fun acts => elaborateMap ⟨U, V, fx, acts, 0⟩
def view (r : Except String (UDoc × SplitMap)) :
    Option (List String × List (Option String) × List (String × List String) × SplitMap) := r.toOption.map fun (U, M) =>
  (U.D.T.regulated.map (·.name), U.D.T.regulated.map (·.act), U.D.T.nodes.map (fun N => (N.name, N.over)), M)
-- A6 (u027): two prohibitions; a rule over the source splits pairwise.
#guard view (run fx6 V6 (U1 "p027" .permission a6 [nd "r" "p027" false, nd "s" "p027" true ["r"]])) == some
  (["p027__1", "p027__2", "k"], [some "{0} be subjected to torture",
    some "{0} be subjected to cruel, inhuman or degrading treatment or punishment", some "{0} k"],
   [("r-a1", []), ("r-a2", []), ("s-a1", ["r-a1"]), ("s-a2", ["r-a2"]), ("rk", [])],
   ⟨[("p027__1", "p027", 1), ("p027__2", "p027", 2)], [("r-a1", "r", 1), ("r-a2", "r", 2), ("s-a1", "s", 1),
     ("s-a2", "s", 2)]⟩)
-- A7 (u079b): one obligation on the whole act, unchanged (`elaborate_identity`'s case).
#guard view (run fx7 V7 (U1 "p079" .obligation a7 [nd "r" "p079" true])) ==
  some (["p079", "k"], [some a7, some "{0} k"], [("r", []), ("rk", [])], ⟨[], []⟩)
-- A14 (u0123.s03): five prohibitions.
#guard (view (run fx14 V14 (U1 "p123" .permission a14 [nd "r" "p123" false]))).map (·.1) ==
  some ["p123__1", "p123__2", "p123__3", "p123__4", "p123__5", "k"]
-- Acts read on a predicate with no act, and a lexical act, give no entry; the first refusal is raised.
#guard (actsOf fx6 V6 (U1 "p" .permission "{0} be subjected to torture" [])).toOption == some []
-- Each act is checked at its predicate's arity (two slots on a binary predicate).
#guard (actsOf [] ⟨[], []⟩ (doc [rg "t" .permission (some "{0} meet {1}") (sorts := ["person", "person"])] []).U).toOption
  == some []
#guard errText (actsOf fx6 ⟨[], []⟩ ((doc [rg "q" .permission (some "{0} q"), rg "p" .permission (some a6),
  rg "z" .permission (some (a6 ++ ","))] []).U)) ==
  "InvalidInput: act phrase for p has no reading under the declared frames"

/-! ### Step 6: the author limits of the result (E13 to E15) -/

-- E13: E1 with 255 declared predicates (256 after the split), then 256 (257).
#guard refusal { e1 with declared := 255 } == none
#guard refusal { e1 with declared := 256 } == some "ResourceLimit: vocabulary size"
/-- `.any` of two atoms with heads `h{i}a`, `h{i}b` (*must not*: two prohibitions, acts distinct across `i`). -/
def pair (i : Nat) : Act := .any false true [⟨false, false, [s!"h{i}a"], [], []⟩, ⟨false, false, [s!"h{i}b"], [], []⟩]
-- Two split sources count each source once and each part once: 254 − 2 + 4 = 256, then 257.
def two : ActsDoc := withActs (doc [rg "p027" .permission, rg "p028" .permission] [nd "r027" "p027" false,
  nd "r028" "p028" false]) [] [("p027", pair 0), ("p028", pair 1)]
-- The spec's `splitAtoms` and `partNames` (6.3, 6.6) read every entry of `acts`, the first and the last.
#guard ["p027", "p028", "k"].map (fun p => ((splitAtoms two p).map (·.length), partNames two p)) ==
  [(some 2, ["p027__1", "p027__2"]), (some 2, ["p028__1", "p028__2"]), (none, ["k"])]
#guard refusal { two with declared := 254 } == none && refusal { two with declared := 255 } ==
  some "ResourceLimit: vocabulary size"
-- E14: an unspecified source of 53 bytes (parts of 56), then 54 (57); the source passes at 54.
def e14 (n : Nat) : ActsDoc := let p := String.mk (List.replicate n 'p')
  withActs (doc [rg p .permission] [nd "r" p false] [p]) fx6 [(p, g6)]
#guard refusal (e14 53) == none
#guard refusal (e14 54) == some "ResourceLimit: unspecified name length"
-- E15: rules plus unspecified names, 256 after the split, then 257.
def e15 (m : Nat) : ActsDoc := withActs (doc [rg "p027" .permission, rg "b" .plain none]
  (nd "r027" "p027" false :: (List.range m).map fun i => nd ("b" ++ toString i) "b" true) ["p027"]) fx6 [("p027", g6)]
#guard refusal (e15 252) == none
#guard refusal (e15 253) == some "ResourceLimit: rules"
-- The order: step 5 before step 6, step 6 before step 7.
#guard refusal { withActs (doc (many 63 ++ [rg "p027" .permission]) [nd "r027" "p027" false]) fx6 [("p027", g6)] with
  declared := 256 } == some "ResourceLimit: regulated predicates"
#guard refusal { withActs (doc [rg "p027" .permission] [nd "r027" "p027" false] ["zzz"]) fx6 [("p027", g6)] with
  declared := 256 } == some "ResourceLimit: vocabulary size"

/-! ### A request at the limits, each act read once: 32 sources, 128 rules; 64 parts and 256 part rules after -/

def big : ActsDoc := withActs (doc ((List.range 32).map fun i => rg ("p" ++ toString i) .permission)
  ((List.range 32).flatMap fun i => (List.range 4).map fun j => nd s!"r{i}x{j}" ("p" ++ toString i) false)) []
  ((List.range 32).map fun i => ("p" ++ toString i, pair i))
#guard (elaborateMap big).toOption.map (fun (U, M) => (U.D.T.regulated.length, U.D.T.nodes.length, M.preds.length)) ==
  some (64, 256, 64)
#guard refusal { big with acts := big.acts ++ [("p0", pair 0)] } == none

/-! ### `decodeElaboratedU` over the wire -/

/-- An environment as a request carries it: `profiles`, permissions `(name, act)` on `person`, and with `acts` the
    `acts` block holding G6's fixed phrase. -/
def jenv (profiles : List String) (preds : List (String × String)) (acts : Bool := true) : Json :=
  Json.mkObj [("language", .str "ve.core@0.2"), ("profiles", toJson profiles),
    ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"),
    ("vocabulary", Json.mkObj ([("sorts", Json.mkObj [("person", Json.mkObj [("description", .str "person")])]),
      ("predicates", Json.mkObj (preds.map fun (p, act) => (p, Json.mkObj [("arguments", toJson ["person"]),
        ("description", .str "d"), ("regulated", Json.mkObj [("role", .str "permission"), ("default", .str "allow"),
          ("act", .str act)])]))), ("constants", Json.mkObj [])] ++
      if acts then [("acts", Json.mkObj [("fixed", toJson fx6)])] else []))]
def jrule (p : String) : Json := Json.mkObj [("norm", Json.mkObj [("name", .str "m"), ("predicate", .str p),
  ("sign", .bool true), ("guard", Json.arr #[.str "top"]), ("unless", Json.arr #[]), ("over", Json.arr #[])])]
def dec (j : Json) (ns : List Json) := (decodeElaboratedU j (Json.arr ns.toArray)).toOption.map fun e =>
  (e.U'.D.T.regulated == e.s.U.D.T.regulated && e.U'.D.T.nodes == e.s.U.D.T.nodes && e.U'.unspec == e.s.U.unspec,
   e.U'.D.T.nodes.length, e.M, e.D.acts.length, e.D.fixed, e.D.declared)
def lexical : List (String × String) :=
  [("p", "{0} be subjected to cruel, inhuman or degrading treatment or punishment"), ("q", "{0} seek asylum")]
-- All acts lexical: the source itself, an empty map, the block's fixed phrases, two declared predicates.
#guard dec (jenv ["acts@0", "norms@0", "relational-fol@0"] lexical) [jrule "p"] == some (true, 1, ⟨[], []⟩, 0, fx6, 2)
#guard dec (jenv ["acts@0", "norm-defaults@0", "norms@0", "relational-fol@0"] lexical) [jrule "p"] ==
  some (true, 1, ⟨[], []⟩, 0, fx6, 2)
#guard dec (jenv ["norms@0", "relational-fol@0"] lexical) [] == none
-- Without `acts@0` no act is read: today's act check admits *nor*, which `checkAct` would send to the grammar.
#guard dec (jenv ["norms@0", "relational-fol@0"] [("p", "{0} seek nor enjoy asylum")] false) [jrule "p"] ==
  some (true, 1, ⟨[], []⟩, 0, [], 1)
-- The norms decoder still refuses a joined act (its hook is `Lexical.check` until ap-3db), with its own text.
#guard errText (decodeElaboratedU (jenv ["acts@0", "norms@0", "relational-fol@0"] [("p027", a6)])
  (Json.arr #[jrule "p027"])) == "InvalidInput: act phrase for p027 joins acts with 'or' outside a fixed phrase"

end VE.Acts.DecodeExamples
