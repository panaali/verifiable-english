import VE.Acts.MeaningExamples
import VE.Acts.Sources
import VE.Acts.Situation
import VE.Readings.UnspecifiedWire

/-! Fixtures of `phraseReadings` and the edge rule (docs/spec/act-phrases.md 7, 11.4; plan 2.4, AP-4, G5).

A5, A8 to A12 are the pilot's phrases (P5 to P12 of 11.4) under the modal their source rule uses, each with exactly the
readings the audit asks for; P12n and P9m the table's other cells on them; `phraseReadings_exact` by value on P11 in
both directions; the limits at both sides (N − 1 and N raw derivations on G5, 64 lists listed and more refused, an
exhausted step budget, a saturated raw cap); and the edge rule's kinds on the rule table.
-/

namespace VE.Acts.ReadingsExamples
open VE.Acts VE.Acts.Examples VE.Acts.RuleExamples VE.Acts.TableExamples VE.Acts.MeaningExamples

def pr (V : Vocab) (op : Op) (fx : List String) (s : String) (N := rawCap) (b := stepBudget) : Listing (List Simple) :=
  phraseReadings V op N b (toks fx s)
/-- The number of readings; `none` is the limit outcome. -/
def np (V : Vocab) (op : Op) (fx : List String) (s : String) (N := rawCap) : Option Nat :=
  match pr V op fx s N with | .ok Rs => some Rs.length | .limit => none

def g9s := "{0} be arbitrarily deprived of their nationality nor denied the right to change their nationality"
def fx9 : List String := ["the right to change their nationality"]
def g10s := "{0} to security in the event of unemployment, sickness, disability, widowhood, old age or other lack of " ++
  "livelihood in circumstances beyond their control"
def g11s := "{0} to take part in {1} directly or through freely chosen representatives"
def g12s := "{0} to form and to join trade unions for the protection of their interests"

/-! ### The pilot's phrases: exactly two readings each -/

def atoms (A : Act) : List Simple := match A with
  | .one a => [.atom a] | .all _ _ ps | .any _ _ ps => ps.map .atom
-- A5 (u051): `in other countries` on `enjoy`, or on both
#guard pr V5 .right fx5 g5 == .ok [atoms (.all false false [obj5 "seek" false, obj5 "enjoy" true]),
  atoms (.all false false [obj5 "seek" true, obj5 "enjoy" true])]
-- A8 (u105): *freely* on `participate`, or on all three; never on a middle item alone (the seeded bug's guard)
#guard pr V8 .right fx8 g8 == .ok [atoms (g8t [true, false, false]), atoms (g8t [true, true, true])]
-- A9 (u055): *must not*: `deprivation_only`, then `both_acts`
#guard pr V9 .mustNot fx9 g9s == .ok [atoms (g9 false), atoms (g9 true)]
#guard pr V9 .may fx9 g9s == .ok []                                                                      -- P9m: D-22
-- A10 (u092): the split's six causes, the modifier on the last or on all
#guard pr V10 .right ["other lack of livelihood"] g10s == .ok [atoms (g10 false), atoms (g10 true)]
-- A11 (u076): each way, or one act
#guard pr V11 .right fx11 g11s == .ok [atoms g11, [.whole g11]]
-- A12 (u087): *for the protection …* on `join`, or on both
#guard pr V12 .right [] g12s == .ok [atoms (g12 false), atoms (g12 true)]
#guard np V12 .mustNot [] g12s == some 4                                                                 -- P12n
#guard [np V5 .right fx5 g5, np V8 .right fx8 g8, np V9 .mustNot fx9 g9s,
  np V10 .right ["other lack of livelihood"] g10s, np V11 .right fx11 g11s, np V12 .right [] g12s] ==
  [some 2, some 2, some 2, some 2, some 2, some 2]

-- `phraseReadings_exact` both ways on P11: both readings are derived; "only through …" (one atom) is neither
#guard [atoms g11, [.whole g11]].all (fun R => (meanings V11 fx11 g11s).any (fun A => (table .right A).contains R))
#guard !(match pr V11 .right fx11 g11s with | .ok Rs => Rs.contains [.atom through] | .limit => true) &&
  !(meanings V11 fx11 g11s).any (fun A => (table .right A).contains [.atom through])

/-! ### Phrases with no edge modifier read as AP-2 read them, through the table -/

#guard pr V6 .must fx6 "{0} be subjected to torture or to cruel, inhuman or degrading treatment or punishment" ==
  .ok [] &&                                                                                              -- split *or*
  pr V7 .must fx7 "{0} be held by secret vote or by equivalent free voting procedures" == .ok [[.atom held]]
#guard pr V14 .mustNot ["its core identity or principles", "to be human",
  "genuinely deceptive tactics that could harm users", "health or safety", "Anthropic’s guidelines"]
  ("{0} abandon its core identity or principles, claim to be human, use genuinely deceptive tactics that could harm " ++
  "users, endanger health or safety, or act against Anthropic’s guidelines") == .ok [atoms g14v]          -- G14v

/-! ### The limits at both sides -/

-- G5 has 2 raw derivations: N = 3 lists both readings, N = 2 is saturated and refused (G5)
#guard np V5 .right fx5 g5 3 == some 2 && np V5 .right fx5 g5 2 == none
-- the step budget: none left is a refusal
#guard pr V5 .right fx5 g5 (b := 0) == .limit
-- the table's lists are charged: L5's 32 meanings give 64 under *must not* (listed), L6's 64 give 128 (refused);
-- under *has the right to* L6 gives 64 (listed); L7 is over the limit and L8 saturates the raw cap (256)
#guard [5, 6, 7, 8].map (fun k => np V5 .mustNot cities (ln k)) == [some 64, none, none, none]
#guard [6, 7, 8].map (fun k => np V5 .right cities (ln k)) == [some 64, none, none]
#guard rawOf V5 cities (ln 8) == some rawCap && pr V5 .right cities (ln 8) == .limit

/-! ### The edge rule's kinds on the table (2.4) -/

/-- Every left side the table gives an edge kind, each once. -/
def edgeSides (V : Vocab) : List (NT × Attach) :=
  firsts ((schema V).filterMap (fun r => (attachOf r.kind).map (r.lhs, ·)))
-- `first` only at `E1X`; `last` at the four trailing edges; `all` at all five; no other left side
#guard edgeSides V5 == [(.E1X, .first), (.E1X, .all), (.F 0 .TE, .last), (.F 0 .TE, .all), (.F 0 .RE, .last),
  (.F 0 .RE, .all), (.F 0 .REt, .last), (.F 0 .REt, .all), (.F 0 .PX, .last), (.F 0 .PX, .all), (.F 1 .TE, .last),
  (.F 1 .TE, .all), (.F 1 .RE, .last), (.F 1 .RE, .all), (.F 1 .REt, .last), (.F 1 .REt, .all), (.F 1 .PX, .last),
  (.F 1 .PX, .all)]
-- `edgeLhs` both ways: each attachment where 2.4 puts it, and none at a middle item's or an own element's left side
#guard edgeLhs .E1X .first && edgeLhs .E1X .all && !edgeLhs .E1X .last &&
  [NT.F 0 .TE, .F 0 .RE, .F 1 .REt, .F 1 .PX].all (fun x => edgeLhs x .last && edgeLhs x .all && !edgeLhs x .first)
#guard [NT.L false .bare, .L true .own, .F1 false .bare, .ADVO, .F 0 .EE, .F 0 .MEL, .F 0 (.AR "in")].all
  (fun x => [Attach.first, .last, .all].all (!edgeLhs x ·))
#guard attachOf .shape == none && [Attach.first, .last, .all].all (fun a => attachOf (.edge a) == some a)
-- `closed`, whose rules now carry a kind: one `X → never` per nonterminal of a right side that has no rule, in order of
-- first occurrence, wherever it stands (first, middle or last symbol; first or last rule; the last one scanned), and
-- none for one that has
def rsC : List RuleS := [⟨.J, [.n .TOK, .n .ADVO], .shape⟩, ⟨.S, [.t .subj, .n .J, .n .FW], .shape⟩,
  ⟨.ADVO, [.t .comma, .n .J, .n .E1X], .edge .all⟩]
#guard closed rsC == rsC ++ [⟨.TOK, [.t .never], .shape⟩, ⟨.FW, [.t .never], .shape⟩, ⟨.E1X, [.t .never], .shape⟩]

/-! ### Sources (spec 7, 11.4 S1 to S8; plan AP-4, F11)

The pilot's sets rs_u055 and rs_u105b/rs_u105c re-written in `acts@0` form (finding F3): each candidate is one rule on
a declared single act, the frame decoded by the readings route's own decoder, the completion's `unspecified` names by
`VE.Readings.Wire.unspecOf`. A reading's simple acts are the shared units' rules and the chosen candidates' rules. -/

section Sources
open Lean VE.Readings

def regJ (role dflt act : String) : Json := Json.mkObj ([("role", .str role), ("default", .str dflt),
  ("act", .str act)] ++ if role == "plain" then [("form", .str "has the right")] else [])
/-- A readings environment over `acts@0` (and `norm-defaults@0` when `nd`) with the fixed phrases `fx` and the
    regulated predicates `(name, role, default, act)`; `{1}` is a country. -/
def envJ (fx : List String) (nd : Bool) (preds : List (String × String × String × String)) : Json :=
  Json.mkObj [("language", .str "ve.core@0.2"), ("profiles", toJson ((if nd then ["acts@0", "norm-defaults@0"]
      else ["acts@0"]) ++ ["norms@0", "readings@1", "relational-fol@0"])),
    ("spec_revision", .str "ve-v0.2-expand2-2026-09-25"), ("vocabulary", Json.mkObj [
      ("sorts", Json.mkObj [("person", Json.mkObj [("description", .str "p")]),
        ("country", Json.mkObj [("description", .str "c")])]),
      ("predicates", Json.mkObj (preds.map fun (p, role, dflt, act) => (p, Json.mkObj [("description", .str "d"),
        ("arguments", toJson (if (act.splitOn "{1}").length > 1 then ["person", "country"] else ["person"])),
        ("regulated", regJ role dflt act)]))),
      ("constants", Json.mkObj []), ("acts", Json.mkObj [("fixed", toJson fx)])])]
/-- A strict rule with guard `top`, no carve-out and no precedence. -/
def rl (n p : String) (sign := true) : VE.SoftNorms.SoftNode :=
  { name := n, pred := p, sign := sign, guard := .top, carveOuts := [], over := [], mode := .strict, rank := none,
    alterable := [], exception := none, hard := false }
def cand (id : String) (N : VE.SoftNorms.SoftNode) (l : String) : Candidate := ⟨id, some (.norm N), [], [("freely", l)]⟩
/-- The document over the decoded frame, with its `unspecified` names. -/
def mkDoc (e : Json) (items : List Item) (ks : List Coupling := []) : Option (Doc × List String) :=
  match VE.Readings.Wire.decodeEnvironment e with
  | .ok re => let D : Doc := ⟨.norms, VE.Readings.Wire.frameOf re (items.map itemUnit), items, ks, []⟩
    some (D, VE.Readings.Wire.unspecOf re D)
  | .error _ => none
def sc (x : Option (Doc × List String)) (V : Vocab) (fx : List String) (s : Source) : String :=
  match x with
  | some (D, u) => match sourceCheck D u V fx rawCap stepBudget s with | .ok () => "ok" | .error m => m
  | none => "no frame"
def tmpl : VE.Norms.Node := ⟨"", "", true, .top, [], []⟩

-- u105 (A8): *freely* on `participate` (u105a, fixed) or on all three; rs_u105b and rs_u105c coupled on `freely`
def e105 : Json := envJ fx8 false [("part", "plain", "deny", "{0} to freely participate in the cultural life of the community"),
  ("enjoy", "plain", "deny", "{0} to enjoy the arts"), ("enjoy_freely", "plain", "deny", "{0} to freely enjoy the arts"),
  ("share", "plain", "deny", "{0} to share in scientific advancement and its benefits"),
  ("share_freely", "plain", "deny", "{0} to freely share in scientific advancement and its benefits")]
def u105a : Item := .fixed "u105a" (.norm (rl "u105a-r" "part")) []
def setB (cs : List Candidate) : Item := .set ⟨"rs_u105b", "u105b", 3, cs⟩
def setC (cs : List Candidate) : Item := .set ⟨"rs_u105c", "u105c", 3, cs⟩
def bFirst := cand "first" (rl "u105b-first" "enjoy") "first"
def bAll := cand "all" (rl "u105b-all" "enjoy_freely") "all"
def cFirst := cand "first" (rl "u105c-first" "share") "first"
def cAll := cand "all" (rl "u105c-all" "share_freely") "all"
def k105 : Coupling := ⟨"k_u105", "freely", [("rs_u105b", 3), ("rs_u105c", 3)]⟩
def d105 (items : List Item) := mkDoc e105 items [k105]
def s105 : Source := ⟨g8, .plain, true, some .right, tmpl, .deny, ["u105a"], ["rs_u105b", "rs_u105c"]⟩
def S1 := d105 [u105a, setB [bFirst, bAll], setC [cFirst, cAll]]
def noChoice : String := "InvalidInput: a reading of the source phrase has no choice: "
def notReading : String := "InvalidInput: a choice is not a reading of the source phrase, or changes the source " ++
  "rule's modal, guard, exceptions, precedence or completion"
-- S1 passes; S8 (rs_u105c before u105a: each choice's rules in another order) passes
#guard sc S1 V8 fx8 s105 == "ok"
#guard sc (d105 [setC [cFirst, cAll], u105a, setB [bFirst, bAll]]) V8 fx8 s105 == "ok"
-- S2: the "all" candidate removed from both sets: the "all" reading has no choice
#guard sc (d105 [u105a, setB [bFirst], setC [cFirst]]) V8 fx8 s105 == noChoice ++ "{0} has the right to freely " ++
  "participate in the cultural life of the community; {0} has the right to freely enjoy the arts; and {0} has the " ++
  "right to freely share in scientific advancement and its benefits."
-- S3: a skipped-middle candidate (*freely* on `participate` and `share`, not on `enjoy`) is not a reading
#guard sc (d105 [u105a, setB [bFirst, bAll], setC [cFirst, cAll, cand "skip" (rl "u105c-skip" "share_freely") "first"]])
  V8 fx8 s105 == notReading
-- uncoupled, the sets give four choices, two of them no reading; without the shared unit no choice is a reading
#guard sc (mkDoc e105 [u105a, setB [bFirst, bAll], setC [cFirst, cAll]]) V8 fx8 s105 == notReading
#guard sc S1 V8 fx8 { s105 with units := [] } == notReading
-- the template is compared: another guard, carve-out, precedence, sign, role or completion is no reading
#guard [{ s105 with template := { tmpl with guard := .bottom } }, { s105 with template := { tmpl with carveOuts := [.top] } },
  { s105 with template := { tmpl with over := ["r"] } }, { s105 with completion := .allow },
  { s105 with completion := .unspecified }, { s105 with role := .obligation }].map (sc S1 V8 fx8) ==
  List.replicate 6 notReading

-- u055 (A9): *must not* (a permission, sign false); the deprivation (u055a) is shared, rs_u055 reads the denial
def e055 (nd : Bool) (dflt : String) (dA := dflt) : Json := envJ fx9 nd [
  ("depr", "permission", dflt, "{0} be arbitrarily deprived of their nationality"),
  ("denied", "permission", dflt, "{0} be denied the right to change their nationality"),
  ("denied_arbitrarily", "permission", dA, "{0} be arbitrarily denied the right to change their nationality")]
def u055 (signB := false) : List Item := [.fixed "u055a" (.norm (rl "u055a-r" "depr" false)) [],
  .set ⟨"rs_u055", "u055b", 2, [⟨"deprivation_only", some (.norm (rl "u055-d" "denied" false)), [], []⟩,
    ⟨"both_acts", some (.norm (rl "u055-b" "denied_arbitrarily" signB)), [], []⟩]⟩]
def s055 : Source := ⟨g9s, .permission, false, none, { tmpl with sign := false }, .deny, ["u055a"], ["rs_u055"]⟩
def s055u : Source := { s055 with completion := .unspecified }
-- S4 passes; S5 (one candidate's sign flipped: *may* for *must not*) is refused
#guard sc (mkDoc (e055 false "deny") (u055)) V9 fx9 s055 == "ok"
#guard sc (mkDoc (e055 false "deny") (u055 true)) V9 fx9 s055 == notReading
-- S6: under `norm-defaults@0`, every predicate `unspecified`, the source's completion `unspecified`: passes, and the
-- completion is the original metadata's (the frame's placeholder `deny` does not pass for `deny`)
#guard sc (mkDoc (e055 true "unspecified") (u055)) V9 fx9 s055u == "ok"
#guard sc (mkDoc (e055 true "unspecified") (u055)) V9 fx9 s055 == notReading
-- S7: S6 with one candidate predicate's default changed from `unspecified` to `deny`, nothing else: refused
#guard sc (mkDoc (e055 true "unspecified" "deny") (u055)) V9 fx9 s055u == notReading
-- the phrase's other modals: *may* has no reading (D-22's cell), and a plain act with sign false no modal word
#guard sc (mkDoc (e055 false "deny") (u055)) V9 fx9 { s055 with sign := true } == notReading
#guard sc (mkDoc (e055 false "deny") (u055)) V9 fx9 { s055 with role := .plain } ==
  "InvalidInput: the source has no modal word for its act"
-- the step budget: none left is a refusal
def sc0 (x : Option (Doc × List String)) : String :=
  match x with
  | some (D, u) => match sourceCheck D u V9 fx9 rawCap 0 s055 with | .ok () => "ok" | .error m => m
  | none => "no frame"
#guard sc0 (mkDoc (e055 false "deny") (u055)) ==
  "ResourceLimit: the source phrase has too many readings to list; split the sentence"

-- F11 (u076, A11): the one-act reading is a whole join, which the readings route's frame refuses (D-33), so no
-- candidate can carry it and the source cannot pass; the residual waits for the readings elaboration
def e076 (acts : List (String × String)) : Json := envJ fx11 false (acts.map fun (p, a) => (p, "plain", "deny", a))
def s076 : Source := ⟨g11s, .plain, true, some .right, tmpl, .deny, ["u076a", "u076b"], []⟩
#guard sc (mkDoc (e076 [("dir", "{0} to directly take part in {1}"),
    ("thr", "{0} to take part in {1} through freely chosen representatives")])
  [.fixed "u076a" (.norm (rl "u076a-r" "dir")) [], .fixed "u076b" (.norm (rl "u076b-r" "thr")) []]) V11 fx11 s076 ==
  noChoice ++ "{0} has the right to directly take part in {1} or to take part in {1} through freely chosen " ++
  "representatives, as one act done in any one of these ways (not each way on its own)."
-- a frame declaring the one-act reading is refused, as the source words it (D-33) and as `expected` renders it
def dec (e : Json) : String := match VE.Readings.Wire.decodeEnvironment e with | .error m => m | .ok _ => "ok"
#guard [dec (e076 [("one", g11s)]), dec (e076 [("one", Simple.text fx11 (some true) (.whole g11))])] ==
  ["UnsupportedProfile: acts@0 on the readings route admits single acts only; the act of one joins acts",
   "InvalidInput: invalid act phrase for one"]

-- D-29's other texts, on views: two choices that are one reading; more readings than choices
def cv (ps : List String) (cs rs : List (List (Option View))) : String :=
  match compareViews ps cs rs with | .ok () => "ok" | .error m => m
def vw (a : String) : Option View := some (a, .plain, true, .top, [], [], .deny)
#guard cv ["x"] [[vw "a", vw "b"], [vw "b", vw "a"]] [[vw "a", vw "b"]] ==
  "InvalidInput: two choices give the same reading"
#guard cv ["x", "y"] [[vw "a"]] [[vw "a"], [vw "a"]] ==
  "InvalidInput: the reading sets give 1 choices for a phrase with 2 readings"
#guard cv ["x", "y"] [[vw "b"], [vw "a"]] [[vw "a"], [vw "b"]] == "ok"

/-! ### `atomSituation`, checked by `separates` -/

def sep (x : Option (Doc × List String)) (s : String) (i j : Nat) : Bool :=
  match x with | some (D, _) => separates D s i j (atomSituation D s i j) | none => false
-- the u105 and u055 candidates are separated both ways by the act one regulates and the other does not
#guard [sep S1 "rs_u105b" 0 1, sep S1 "rs_u105b" 1 0, sep S1 "rs_u105c" 1 0,
  sep (mkDoc (e055 false "deny") (u055)) "rs_u055" 0 1, sep (mkDoc (e055 false "deny") (u055)) "rs_u055" 1 0] ==
  [true, true, true, true, true]
#guard (S1.map fun (D, _) => (atomSituation D "rs_u105b" 1 0).probe) == some (.selects "norm" "enjoy_freely" [0])
-- two candidates on one act: no act tells them apart, and `separates` refuses the situation
#guard !sep (d105 [u105a, setB [bFirst, cand "same" (rl "u105b-same" "enjoy" false) "all"], setC [cFirst, cAll]])
  "rs_u105b" 1 0

end Sources

end VE.Acts.ReadingsExamples
