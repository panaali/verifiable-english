import VE.Acts.MeaningExamples
import VE.Acts.Sources
import VE.Acts.SourcesProofs
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

/-! ### The pilot's phrases: exactly the readings the audit asks for -/

def atoms (A : Act) : List Simple := match A with
  | .one a => [.atom a] | .all _ _ ps | .any _ _ ps => ps.map .atom
/-- An own-*to* "and" under *may* or *has the right to* (D3 revised): each (split), then both together (one act). -/
def eachOrTogether (A : Act) : List (List Simple) := [atoms A, [.whole A]]
-- A5 (u051): `in other countries` on `enjoy`, or on both; each place split, or "seek and enjoy" as one act
#guard pr V5 .right fx5 g5 == .ok (eachOrTogether (.all false false [obj5 "seek" false, obj5 "enjoy" true]) ++
  eachOrTogether (.all false false [obj5 "seek" true, obj5 "enjoy" true]))
#guard match pr V5 .right fx5 g5 with
  | .ok Rs => Rs.contains [.whole (.all false false [obj5 "seek" false, obj5 "enjoy" true])] &&
    Rs.contains (atoms (.all false false [obj5 "seek" false, obj5 "enjoy" true]))
  | .limit => false
-- A8 (u105): *freely* on `participate`, or on all three, each split or together; never on a middle item alone (the
-- seeded bug's guard)
#guard pr V8 .right fx8 g8 == .ok (eachOrTogether (g8t [true, false, false]) ++ eachOrTogether (g8t [true, true, true]))
-- A9 (u055): *must not*: `deprivation_only`, then `both_acts`
#guard pr V9 .mustNot fx9 g9s == .ok [atoms (g9 false), atoms (g9 true)]
#guard pr V9 .may fx9 g9s == .ok []                                                                      -- P9m: D-22
-- A10 (u092): the split's six causes, the modifier on the last or on all
#guard pr V10 .right ["other lack of livelihood"] g10s == .ok [atoms (g10 false), atoms (g10 true)]
-- A11 (u076): each way, or one act
#guard pr V11 .right fx11 g11s == .ok [atoms g11, [.whole g11]]
-- A12 (u087): *for the protection …* on `join`, or on both; "to form and to join" each, or both together, under
-- *has the right to* and under *may*
#guard pr V12 .right [] g12s == .ok (eachOrTogether (g12 false) ++ eachOrTogether (g12 true))
#guard pr V12 .may [] g12s == pr V12 .right [] g12s
#guard np V12 .mustNot [] g12s == some 4                                                                 -- P12n
#guard [np V5 .right fx5 g5, np V8 .right fx8 g8, np V9 .mustNot fx9 g9s,
  np V10 .right ["other lack of livelihood"] g10s, np V11 .right fx11 g11s, np V12 .right [] g12s] ==
  [some 4, some 4, some 2, some 2, some 2, some 4]
-- A split marker's *and* under *may* and *has the right to* keeps its one reading, each (T6s)
#guard [Op.may, .right].all fun op => pr V6 op [] "{0} be subjected to torture and to exile" ==
  .ok [[.atom ⟨false, true, ["subjected"], [("to", .one (w "torture"))], []⟩,
    .atom ⟨false, true, ["subjected"], [("to", .one (w "exile"))], []⟩]]

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

-- G5 has 2 raw derivations: N = 3 lists all four readings (two per derivation), N = 2 is saturated and refused (G5)
#guard np V5 .right fx5 g5 3 == some 4 && np V5 .right fx5 g5 2 == none
-- the step budget: none left is a refusal
#guard pr V5 .right fx5 g5 (b := 0) == .limit
-- the table's lists are charged: L5's 32 meanings give 64 under *must not* (listed), L6's 64 give 128 (refused);
-- under *must* L6 gives 64 (listed, P64); under *has the right to* L6 gives 128 (refused, D3 revised); L7 is over the
-- limit and L8 saturates the raw cap (256)
#guard [5, 6, 7, 8].map (fun k => np V5 .mustNot cities (ln k)) == [some 64, none, none, none]
#guard [6, 7, 8].map (fun k => np V5 .must cities (ln k)) == [some 64, none, none]
#guard [5, 6].map (fun k => np V5 .right cities (ln k)) == [some 64, none]
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

/-! ### Sources (spec 7, 11.4 S1 to S8, S3b, S8b; plan AP-4, F11)

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
/-- G8's first together reading (D3 revised): a whole join, which no candidate on the readings route carries (F11). -/
def together105 : String := noChoice ++ "{0} has the right to freely participate in the cultural life of the " ++
  "community, to enjoy the arts and to share in scientific advancement and its benefits, as one act done together " ++
  "(not each on its own)."
-- S1 is refused (F11): its first together reading has no choice; S8 (rs_u105c before u105a: each choice's rules in
-- another order) is refused with the same full text, so the order comparison (SR14) does not refuse it first
#guard sc S1 V8 fx8 s105 == together105
#guard sc (d105 [setC [cFirst, cAll], u105a, setB [bFirst, bAll]]) V8 fx8 s105 == together105
-- S2: the "all" candidate removed from both sets: still refused, now first at the together reading (F11)
#guard sc (d105 [u105a, setB [bFirst], setC [cFirst]]) V8 fx8 s105 == together105
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
-- and so is each rule's: a candidate under another guard is no reading
#guard sc (d105 [u105a, setB [bFirst, cand "all" { rl "u105b-all" "enjoy_freely" with guard := .bottom } "all"],
  setC [cFirst, cAll]]) V8 fx8 s105 == notReading

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
-- S8b: S4 with the items reordered (rs_u055 before u055a), so each choice's rules, `both_acts`'s among them, come in
-- another order: passes, rules are compared up to order (SR14); so does S6's set reordered
#guard sc (mkDoc (e055 false "deny") (u055.reverse)) V9 fx9 s055 == "ok"
#guard sc (mkDoc (e055 true "unspecified") (u055.reverse)) V9 fx9 s055u == "ok"
-- S3b: S4 plus a candidate whose choice is no reading of G9 (the deprivation without *arbitrarily*, beside the shared
-- arbitrary one): refused, a choice is not a reading; the isolated guard for the rule S3 exercises on G8
def e055x : Json := envJ fx9 false [("depr", "permission", "deny", "{0} be arbitrarily deprived of their nationality"),
  ("denied", "permission", "deny", "{0} be denied the right to change their nationality"),
  ("denied_arbitrarily", "permission", "deny", "{0} be arbitrarily denied the right to change their nationality"),
  ("depr_plain", "permission", "deny", "{0} be deprived of their nationality")]
def u055x (extra : List Candidate) : List Item := (u055).take 1 ++ [.set ⟨"rs_u055", "u055b", 2,
    [⟨"deprivation_only", some (.norm (rl "u055-d" "denied" false)), [], []⟩,
     ⟨"both_acts", some (.norm (rl "u055-b" "denied_arbitrarily" false)), [], []⟩] ++ extra⟩]
#guard sc (mkDoc e055x (u055x [])) V9 fx9 s055 == "ok"
#guard sc (mkDoc e055x (u055x [⟨"denial_only", some (.norm (rl "u055-n" "depr_plain" false)), [], []⟩])) V9 fx9 s055 ==
  notReading
-- a set the source does not list is projected away, and the choices that then coincide are one choice (moved from S1,
-- now refused under F11, to S4)
def other : Item := .set ⟨"rs_other", "u_other", 1,
  [cand "x" (rl "o-x" "depr" false) "x", cand "y" (rl "o-y" "denied" false) "y"]⟩
#guard sc (mkDoc (e055 false "deny") (u055 ++ [other])) V9 fx9 s055 == "ok"
-- S7: S6 with one candidate predicate's default changed from `unspecified` to `deny`, nothing else: refused
#guard sc (mkDoc (e055 true "unspecified" "deny") (u055)) V9 fx9 s055u == notReading
-- the phrase's other modals: *may* has no reading (D-22's cell), and a plain act with sign false no modal word
#guard sc (mkDoc (e055 false "deny") (u055)) V9 fx9 { s055 with sign := true } == notReading
#guard sc (mkDoc (e055 false "deny") (u055)) V9 fx9 { s055 with role := .plain } ==
  "InvalidInput: the source has no modal word for its act"
-- the choice limit: `VE.Readings.choices` stops after 65, so a document with more than 64 choices is refused with
-- `ResourceLimit`, never compared on the part listed (ap-4b F1). L5's 64 readings against seven uncoupled sets of two
-- (128 choices, cut at 65) end there
def choiceLimit : String := "ResourceLimit: the document has more than 64 choices, too many to compare with the " ++
  "source phrase's readings"
def wide : List Item := (List.range 7).map fun k =>
  .set ⟨s!"rs_{k}", s!"u_{k}", 1, [cand "x" (rl s!"w{k}-x" "enjoy") "x", cand "y" (rl s!"w{k}-y" "share") "y"]⟩
#guard (mkDoc e105 wide).map (fun (D, _) => (choicesOn D ((List.range 7).map (s!"rs_{·}"))).length) == some 65 &&
  sc (mkDoc e105 wide) V5 cities { s105 with phrase := ln 5, units := [], sets := (List.range 7).map (s!"rs_{·}") } ==
    choiceLimit
-- F1's probe: S5's flipped candidate as rs_u055's third, beside n unrelated sets of two. With six (192 choices, cut at
-- 65) the cut projection lists the first two candidates only and never sees the flipped one: refused at the limit, not
-- passed. With none (3 choices) S5's refusal stands; with four (48) the projection is complete and it still stands
def u055f (n : Nat) : List Item := (u055).take 1 ++ [.set ⟨"rs_u055", "u055b", 2,
    [⟨"deprivation_only", some (.norm (rl "u055-d" "denied" false)), [], []⟩,
     ⟨"both_acts", some (.norm (rl "u055-b" "denied_arbitrarily" false)), [], []⟩,
     ⟨"flipped", some (.norm (rl "u055-f" "denied_arbitrarily" true)), [], []⟩]⟩] ++
  (List.range n).map fun k => .set ⟨s!"rs_d{k}", s!"ud{k}", 1,
    [⟨"x", some (.norm (rl s!"dx{k}" "depr" false)), [], []⟩, ⟨"y", some (.norm (rl s!"dy{k}" "denied" false)), [], []⟩]⟩
#guard [0, 4, 6].map (fun n => sc (mkDoc (e055 false "deny") (u055f n)) V9 fx9 s055) ==
  [notReading, notReading, choiceLimit]
#guard (mkDoc (e055 false "deny") (u055f 6)).map (fun (D, _) => choicesOn D ["rs_u055"]) ==
  some [[("rs_u055", 0)], [("rs_u055", 1)]]
-- the boundary: S4 beside five sets of two is 64 choices and passes; beside six, 128, refused at the limit
def u055w (n : Nat) : List Item := u055 ++ (List.range n).map fun k => .set ⟨s!"rs_d{k}", s!"ud{k}", 1,
    [⟨"x", some (.norm (rl s!"dx{k}" "depr" false)), [], []⟩, ⟨"y", some (.norm (rl s!"dy{k}" "denied" false)), [], []⟩]⟩
#guard [5, 6].map (fun n => sc (mkDoc (e055 false "deny") (u055w n)) V9 fx9 s055) == ["ok", choiceLimit]
#guard [5, 6].map (fun n => (mkDoc (e055 false "deny") (u055w n)).map (fun (D, _) => (choices D).length)) ==
  [some 64, some 65]
-- item 8c's counterexample (`sourceCheck_complete_needs_bound`): S4 beside six sets is 128 choices, cut at 65; the
-- theorem's decidable premises hold on it (lexing, op, readings, paraphrases, D-29 passing on the cut `choiceViews`,
-- 65 > 64), so `SourceExact` holds while `sourceCheck` refuses: `sourceCheck_complete` needs the bound
def cutExact (x : Option (Doc × List String)) (V : Vocab) (fx : List String) (s : Source) : Bool :=
  match x, Lexical.lex fx s.phrase, opOfSource s with
  | some (D, u), .ok ts, some op => match phraseReadings V op rawCap stepBudget ts.toArray with
    | .ok Rs => match paraphrases fx op s.form "the source phrase" Rs with
      | .ok ps => (compareViews ps (choiceViews D u s) (readingViews fx s Rs)).toBool
      | .error _ => false
    | .limit => false
  | _, _, _ => false
#guard framesOk V9 && cutExact (mkDoc (e055 false "deny") (u055w 6)) V9 fx9 s055 &&
  (mkDoc (e055 false "deny") (u055w 6)).map (fun (D, _) => decide (maxChoices < (choices D).length)) == some true &&
  sc (mkDoc (e055 false "deny") (u055w 6)) V9 fx9 s055 == choiceLimit
-- `sourceCheck` compares `viewsOn` of the choices it bounded; spec 7's `choiceViews` is the same views (`viewsOn_choices`),
-- checked here on documents with several choices and rules, choices that coincide once projected, and `unspecified`
#guard [(S1, s105), (d105 [u105a, setB [bFirst, bAll], setC [cFirst, cAll], other], s105),
    (mkDoc e105 [setC [cFirst, cAll], u105a, setB [bFirst, bAll]], s105), (mkDoc (e055 false "deny") (u055f 0), s055),
    (mkDoc (e055 true "unspecified") (u055), s055u)].all fun
  | (some (D, u), s) => choiceViews D u s == viewsOn D u s (choices D) && (choiceViews D u s).length ≥ 2
  | (none, _) => false
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
-- on acts of two arguments the probe's tuple has two elements; every constant names the base's one element
def d076 := mkDoc (e076 [("dir", "{0} to directly take part in {1}"),
  ("thr", "{0} to take part in {1} through freely chosen representatives")])
  [.set ⟨"rs_u076", "u076", 1, [cand "dir" (rl "u076-dir" "dir") "x", cand "thr" (rl "u076-thr" "thr") "y"]⟩]
#guard [sep d076 "rs_u076" 0 1, sep d076 "rs_u076" 1 0] == [true, true] &&
  (d076.map fun (D, _) => (atomSituation D "rs_u076" 1 0).probe) == some (.selects "norm" "thr" [0, 0])
#guard (S1.map fun (D, _) => let M := (atomSituation D "rs_u105b" 1 0).base
  ["c", "d"].all (fun c => (M.constants c).any (fun v => ["person", "country"].all (fun t => (M.domains t).contains v)))) ==
  some true
-- two candidates on one act: no act tells them apart, the probe is `holds`, and `separates` refuses the situation
def same := d105 [u105a, setB [bFirst, cand "same" (rl "u105b-same" "enjoy" false) "all"], setC [cFirst, cAll]]
#guard !sep same "rs_u105b" 1 0 && (same.map fun (D, _) => (atomSituation D "rs_u105b" 1 0).probe) == some .holds

end Sources

end VE.Acts.ReadingsExamples
