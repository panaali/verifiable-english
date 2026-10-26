import VE.Calc.Run
import VE.Calc.Render

/-! Route cases of the `calc` runner (math-evidence plan ME-2; spec 13.2, 13.3 and 13.6): each case's answer from
`VE.Calc.Run.runCaseReported`, as `#guard`s that `lake build` evaluates, one per family. -/

namespace VE.Calc.RunExamples
open Lean VE.Calc VE.Numbers

def answer (s : String) : Json := match Json.parse s with
  | .ok j => Run.runCaseReported j
  | .error e => .str e

def field (j : Json) (k : String) : String := (j.getObjValD k).getStr?.toOption.getD ""

/-- Each row's claim and outcome, with an unknown's reason and a reproduction row; or the refusal. -/
def says (s : String) : List String :=
  let a := answer s
  match a.getObjVal? "rows" with
  | .ok (.arr rows) => rows.toList.map fun r => s!"{field r "claim"} {field r "outcome"}" ++
      (if field r "reason" = "" then "" else s!" ({field r "reason"})") ++
      (if field r "reproduction" = "" then "" else " reproduction unknown")
  | _ => [field a "error"]

def meaning (s : String) : String := field (answer s) "meaning_id"

/-- A case of these values and claims, with more fields. -/
def req (values claims : String) (more : String := "") : String :=
  r#"{"format": "ve-calc@0", "values": ["# ++ values ++ r#"], "claims": ["# ++ claims ++ "]" ++ more ++ "}"

def stated (n v : String) : String := s!"\{\"name\": \"{n}\", \"words\": \"the {n}\", \"stated\": {v}}"
def defined (n e : String) : String := s!"\{\"name\": \"{n}\", \"words\": \"the {n}\", \"defined\": {e}}"
def claim (i c : String) : String := s!"\{\"id\": \"{i}\", \"claim\": {c}}"
def c1 (c : String) : String := claim "c1" c
def x1 : String := stated "x" r#""1""#
def ok1 : String := c1 r#"["eq", ["val", "x"], ["lit", "1"]]"#
def ones (n : Nat) : String := String.mk (List.replicate n '1')
def nulls (n : Nat) : String := ",".intercalate (List.replicate n "null")

/-- Every row's answer (its second member) is its expected one (its third); the first is its key. -/
def expect (rows : List (String × List String × List String)) : Bool := rows.all fun (_, got, want) => got == want

/-! ## Spec 13.6: R-1 (V-1, V-1n) and R-2 (V-11, with a third claim), every field of every row -/

def r1 : String := req (stated "scored" r#""176""# ++ ", " ++ stated "trials" r#""594""# ++ ", " ++
  defined "baseline" r#"["div", ["val", "scored"], ["val", "trials"]]"#)
  (c1 r#"["rounds", ["val", "baseline"], "0.296"]"# ++ ", " ++ claim "c2" r#"["rounds", ["val", "baseline"], "0.297"]"#)

def r2 : String := req (stated "x" r#"["sci", "1", 39]"# ++ ", " ++ defined "y" r#"["pow", ["val", "x"], 64]"# ++
  ", " ++ defined "z" r#"["mul", ["val", "y"], ["val", "y"]]"#)
  (claim "v1" r#"["lt", ["val", "z"], ["lit", "1"]]"# ++ ", " ++
   claim "v2" r#"["eq", ["div", ["lit", "1"], ["sub", ["val", "x"], ["val", "x"]]], ["lit", "1"]]"# ++ ", " ++
   claim "v3" r#"["lt", ["val", "y"], ["lit", "1"]]"#)

#guard (answer r1).compress == r#"{"meaning_id":"5a074a4cee5cfdce99fabb04e758d3d76f6bfdec93c035dbf66cc199c41aa2d1","rows":[{"claim":"c1","claim_id":"c29d5014aeadc1df87761d40af3cd23185d0356ad7f8289017e9b2f5f22e7770","kind":"claim","outcome":"holds","reason":null,"reproduction":null,"status":"ok"},{"claim":"c2","claim_id":"10e8ddf440fe268947bffacb61601502f0017d93d0822b8f392ead09ffb270b5","kind":"claim","outcome":"fails","reason":null,"reproduction":null,"status":"ok"}],"status":"ok"}"#
#guard (answer r2).compress == r#"{"meaning_id":"82923ee3bfaa2f6b000be5e76ef40fbde32b0e4b1af8ef39e41d91ff54b595b5","rows":[{"claim":"v1","claim_id":"01f0a37df1028bee5e1e6e7ef5e835cf7ee6cf040d681f0a2973959fb5408c0e","kind":"claim","outcome":"unknown","reason":"unknown: an exact value would have more than 4,096 digits","reproduction":null,"status":"ok"},{"claim":"v2","claim_id":"ff9880069d728e0abc8479047f3961fd1facb733004d19f7156f50dc0a59f9aa","kind":"claim","outcome":"undefined","reason":null,"reproduction":null,"status":"ok"},{"claim":"v3","claim_id":"ddeccbbd1a0c426b1889c101c3e7453effa4650cf2b5f16d3fbf60078d079883","kind":"claim","outcome":"fails","reason":null,"reproduction":null,"status":"ok"}],"status":"ok"}"#
-- `Run.outcomeAt` reads each row back; a refusal and a row past the last read nothing.
#guard [0, 1, 2].map (Run.outcomeAt (answer r2)) ==
  [some (.unknown (.limit .digits)), some (.decided .undefined), some (.decided .fails)]
#guard Run.outcomeAt (answer r1) 2 == none && Run.outcomeAt (answer (req x1 "")) 0 == none
#guard Run.words (.unknown .floatingPointNotModelled) == ("unknown", some "unknown: floating-point computation not modelled")

/-! ## Route cases: V-1, V-2, V-5, V-9, V-8's rules, I-1 and each claim form -/

def v5Rows : List (Nat × String) :=
  [(151, "0.621"), (155, "0.638"), (136, "0.560"), (144, "0.593"), (127, "0.523"), (127, "0.523"), (121, "0.498"),
   (124, "0.510"), (127, "0.523"), (90, "0.370"), (62, "0.255"), (62, "0.255"), (71, "0.292"), (63, "0.259"),
   (60, "0.247"), (31, "0.128"), (43, "0.177"), (52, "0.214"), (41, "0.169"), (37, "0.152")]

/-- V-5: the twenty rows of `paper/generated/posthoc-weakening-rates.md`, each approved count over 243 against its
printed pooled rate, in one case. -/
def v5 : String := req
  (", ".intercalate (stated "attacks" r#""243""# :: v5Rows.zipIdx.map fun ((a, _), i) => stated s!"a{i}" s!"\"{a}\""))
  (", ".intercalate (v5Rows.zipIdx.map fun ((_, p), i) =>
    claim s!"r{i}" s!"[\"rounds\", [\"div\", [\"val\", \"a{i}\"], [\"val\", \"attacks\"]], \"{p}\"]"))

def v2 : String := req (stated "strict" r#""52""# ++ ", " ++ stated "symbols" r#""31""# ++ ", " ++
  stated "attacks" r#""243""# ++ ", " ++ defined "rate_strict" r#"["div", ["val", "strict"], ["val", "attacks"]]"# ++
  ", " ++ defined "rate_symbols" r#"["div", ["val", "symbols"], ["val", "attacks"]]"# ++ ", " ++
  defined "increase" r#"["mul", ["lit", "100"], ["sub", ["val", "rate_strict"], ["val", "rate_symbols"]]]"#)
  (c1 r#"["rounds", ["val", "rate_strict"], "0.214"]"# ++ ", " ++
   claim "c2" r#"["rounds", ["val", "rate_symbols"], "0.128"]"# ++ ", " ++
   claim "c3" r#"["rounds", ["val", "increase"], "8.6"]"#) r#", "rounding": "ties-up""#

/-- V-8: 4/512 printed at six places is a tie, 0.0078125. -/
def p512 : String := stated "approved" r#""4""# ++ ", " ++ defined "p" r#"["div", ["val", "approved"], ["lit", "512"]]"#
def r827 : String := stated "x" r#""8""# ++ ", " ++ defined "r" r#"["div", ["val", "x"], ["lit", "27"]]"#
/-- I-1 (H-8): length over wavelength printed "2 times ten to the power 7". -/
def h8 (wavelength printed : String) : String := req (stated "length" r#""11""# ++ ", " ++ stated "wavelength" wavelength)
  (c1 s!"[\"rounds\", [\"div\", [\"val\", \"length\"], [\"val\", \"wavelength\"]], {printed}]")

#guard expect [
  ("v1", says (req (stated "scored" r#""176""# ++ ", " ++ stated "trials" r#""594""# ++ ", " ++
      defined "baseline" r#"["div", ["val", "scored"], ["val", "trials"]]"#)
      (c1 r#"["rounds", ["val", "baseline"], "0.296"]"# ++ ", " ++ claim "c2" r#"["lt", ["val", "baseline"], ["lit", "0.30"]]"#)),
    ["c1 holds", "c2 holds"]),
  ("v2", says v2, ["c1 holds", "c2 holds", "c3 holds"]),
  ("v5", says v5, (List.range 20).map (s!"r{·} holds")),
  ("v9", says (req (stated "x" r#""2.675""#) (c1 r#"["rounds", ["val", "x"], "2.67"]"#) r#", "software": "Python 3.12""#),
    ["c1 fails reproduction unknown"]),
  ("v8", says (req p512 (claim "up" r#"["rounds", ["val", "p"], "0.007812"]"# ++ ", " ++
      claim "even" r#"["rounds", ["val", "p"], "0.007812", "half-even"]"#)), ["up fails", "even holds"]),
  ("v8-case-rule", says (req p512 (claim "up" r#"["rounds", ["val", "p"], "0.007812", "ties-up"]"# ++ ", " ++
      claim "even" r#"["rounds", ["val", "p"], "0.007812"]"#) r#", "rounding": "half-even""#), ["up fails", "even holds"]),
  ("i1", says (h8 r#"["sci", "5.89", -7]"# r#"["sci", "2", 7]"#), ["c1 holds"]),
  ("i1-places", says (h8 r#""0.000000589""# r#""20000000""#), ["c1 fails"]),
  ("forms", says (req x1 (c1 r#"["within", ["val", "x"], ["lit", "0.5"], ["lit", "1"]]"# ++ ", " ++
      claim "c2" r#"["within", ["val", "x"], ["lit", "1.5"], ["lit", "2"]]"# ++ ", " ++
      claim "c3" r#"["gt", ["val", "x"], ["lit", "1"]]"# ++ ", " ++ claim "c4" r#"["ge", ["val", "x"], ["lit", "1"]]"# ++
      ", " ++ claim "c5" r#"["le", ["val", "x"], ["lit", "1"]]"#)),
    ["c1 holds", "c2 fails", "c3 fails", "c4 holds", "c5 holds"]),
  ("bounds", says (req r827 (c1 r#"["rounds-down", ["val", "r"], "0.296"]"# ++ ", " ++
      claim "c2" r#"["rounds-up", ["val", "r"], "0.297"]"# ++ ", " ++ claim "c3" r#"["rounds-down", ["val", "r"], "0.297"]"#)),
    ["c1 holds", "c2 holds", "c3 fails"]),
  ("sign", says (req x1 (c1 r#"["rounds", ["val", "x"], "-1"]"#)), ["c1 fails"]),
  ("order", says (req x1 (c1 r#"["lt", ["val", "x"], ["lit", "2"]]"# ++ ", " ++
      claim "c2" r#"["le", ["val", "x"], ["lit", "2"]]"# ++ ", " ++ claim "c3" r#"["gt", ["val", "x"], ["lit", "2"]]"# ++
      ", " ++ claim "c4" r#"["ge", ["val", "x"], ["lit", "2"]]"# ++ ", " ++ claim "c5" r#"["gt", ["lit", "2"], ["val", "x"]]"#)),
    ["c1 holds", "c2 holds", "c3 fails", "c4 fails", "c5 holds"]),
  ("short-names", says (req x1 (claim "c" r#"["eq", ["val", "x"], ["lit", "1"]]"#) r#", "software": "P""#),
    ["c holds reproduction unknown"])]

-- What a decided row means (`Check.OutcomeMeans`), read on a claim that holds.
#guard let k := Check.claim (.compare ⟨.eq, false⟩ (.val "x") (.lit 1))
  let ds : List Decl := [⟨"x", .stated 1⟩]
  decide (k.OutcomeMeans ds (.decided .holds)) && !decide (k.OutcomeMeans ds (.decided .fails)) &&
    match k.run ds with
    | .decided v => decide (k.OutcomeMeans ds (.decided v))
    | .unknown _ => false

-- A literal-only claim reads no exhausted counted value; its evaluation-limit cause is impossible.
-- This negative instance keeps the unknown clause from becoming a tautology.
example : ¬ (Check.claim (.compare ⟨.eq, false⟩ (.lit 1) (.lit 2))).UnknownCause [] (.limit .evaluations) := by
  simp [Check.UnknownCause, Claim.ReadsExhausted, Expr.ReadsExhausted, Claim.exprs, Expr.names]

/-! ## Identity (3.3, J1): what changes the `meaning_id` and what does not

One table holds every normalisation of 3.3 and every hashed field, one family each. A family is a list of classes:
the requests of a class share their `meaning_id` and claim ids, and no two classes of a family share a
`meaning_id`. A normalisation the hash skips splits a class; a field or rule the hash drops (or pins to a constant)
merges two classes. Each class names one spelling per place the decoder reads it, so a family fails whichever
branch of `Wire` loses its normalisation. -/

def identity (s : String) : List String :=
  let a := answer s
  field a "meaning_id" :: match a.getObjVal? "rows" with
    | .ok (.arr rows) => rows.toList.map (field · "claim_id")
    | _ => []

/-- A one-claim case over `x` = 1: `rounding` is the case's rule, when it names one. -/
def x1c (c : String) (rounding : String := "") : String :=
  req x1 (c1 c) (if rounding = "" then "" else s!", \"rounding\": \"{rounding}\"")

/-- A literal written at each place the decoder reads one: a stated value, a claim's `lit`, a defined value's `lit`,
a `within` bound's `lit` and a `pow` base's `lit`. -/
def literalSites : List (String → String) := [
  fun l => req (stated "x" l) ok1,
  fun l => x1c s!"[\"eq\", [\"val\", \"x\"], [\"lit\", {l}]]",
  fun l => req (x1 ++ ", " ++ defined "y" s!"[\"add\", [\"val\", \"x\"], [\"lit\", {l}]]") ok1,
  fun l => x1c s!"[\"within\", [\"val\", \"x\"], [\"lit\", {l}], [\"lit\", \"2\"]]",
  fun l => x1c s!"[\"lt\", [\"pow\", [\"lit\", {l}], 2], [\"val\", \"x\"]]"]

/-- A printed number at each claim that reads one. -/
def printedSites : List (String → String) := [
  fun p => x1c s!"[\"rounds\", [\"val\", \"x\"], {p}]",
  fun p => x1c s!"[\"rounds-down\", [\"val\", \"x\"], {p}]",
  fun p => x1c s!"[\"rounds-up\", [\"val\", \"x\"], {p}]"]

def identityFamilies : List (String × List (List String)) :=
  -- 3.3: every value literal is its shortest plain decimal string, never "-0" and with no `sci` left.
  (literalSites.zipIdx.flatMap fun (site, i) => [
    (s!"literal {i}: plain", [
      [r#""0.3""#, r#""0.30""#, r#"["sci", "3", -1]"#, r#"["sci", "0.03", 1]"#].map site,
      [r#""0.31""#].map site, [r#""-0.3""#, r#"["sci", "-3", -1]"#].map site,
      [r#""20000000""#, r#""20000000.0""#, r#"["sci", "2", 7]"#, r#"["sci", "20", 6]"#].map site]),
    (s!"literal {i}: zero", [[r#""0""#, r#""-0""#, r#""0.00""#, r#""-0.0""#, r#"["sci", "-0", 3]"#].map site,
      [r#""1""#].map site])]) ++
  -- 3.3: every printed number is [digits, places]: written places count, a `sci` spelling of the same pair does not.
  (printedSites.zipIdx.map fun (site, i) => (s!"printed {i}", [
    [r#""0.3""#, r#"["sci", "3", -1]"#, r#"["sci", "0.3", 0]"#].map site, [r#""0.30""#, r#"["sci", "30", -2]"#].map site,
    [r#""0.300""#, r#"["sci", "3.00", -1]"#].map site,
    [r#""20000000""#].map site, [r#"["sci", "2", 7]"#].map site, [r#"["sci", "20", 6]"#].map site,
    [r#""0.0""#, r#""-0.0""#].map site])) ++ [
  -- 3.3: every `rounds` claim carries its rule, its own or else the case's; the other claims carry none.
  ("tie rule", [
    [x1c r#"["rounds", ["val", "x"], "1"]"#, x1c r#"["rounds", ["val", "x"], "1"]"# "ties-up",
     x1c r#"["rounds", ["val", "x"], "1", "ties-up"]"#, x1c r#"["rounds", ["val", "x"], "1", "ties-up"]"# "half-even"],
    [x1c r#"["rounds", ["val", "x"], "1"]"# "half-even", x1c r#"["rounds", ["val", "x"], "1", "half-even"]"#,
     x1c r#"["rounds", ["val", "x"], "1", "half-even"]"# "ties-up"],
    [x1c r#"["rounds-down", ["val", "x"], "1"]"#, x1c r#"["rounds-down", ["val", "x"], "1"]"# "half-even"],
    [x1c r#"["rounds-up", ["val", "x"], "1"]"#, x1c r#"["rounds-up", ["val", "x"], "1"]"# "half-even"]]),
  ("case rule without a rounds claim", [
    [req x1 ok1, x1c r#"["eq", ["val", "x"], ["lit", "1"]]"# "ties-up",
     x1c r#"["eq", ["val", "x"], ["lit", "1"]]"# "half-even"]]),
  -- 3.3: `words` are removed, and the order of keys does not matter.
  ("words and key order", [
    [req x1 ok1, req r#"{"words": "the other words", "stated": "1", "name": "x"}"# ok1,
     req x1 r#"{"claim": ["eq", ["val", "x"], ["lit", "1"]], "id": "c1"}"#,
     r#"{"claims": [{"claim": ["eq", ["val", "x"], ["lit", "1"]], "id": "c1"}], "values": [{"stated": "1", "words": "w", "name": "x"}], "format": "ve-calc@0"}"#]]),
  -- 3.3: `gt` and `ge` are kept as written, and every operand keeps its place.
  ("comparisons as written", [
    [x1c r#"["gt", ["val", "x"], ["lit", "2"]]"#], [x1c r#"["lt", ["lit", "2"], ["val", "x"]]"#],
    [x1c r#"["ge", ["val", "x"], ["lit", "2"]]"#], [x1c r#"["le", ["lit", "2"], ["val", "x"]]"#]]),
  ("claim forms", [
    [x1c r#"["rounds-down", ["val", "x"], "1"]"#], [x1c r#"["rounds-up", ["val", "x"], "1"]"#],
    [x1c r#"["rounds", ["val", "x"], "1"]"#], [x1c r#"["rounds", ["val", "x"], "1", "half-even"]"#]]),
  ("within bounds", [
    [x1c r#"["within", ["val", "x"], ["lit", "0"], ["lit", "2"]]"#],
    [x1c r#"["within", ["val", "x"], ["lit", "2"], ["lit", "0"]]"#],
    [x1c r#"["within", ["val", "x"], ["lit", "0"], ["lit", "3"]]"#],
    [x1c r#"["within", ["val", "x"], ["lit", "1"], ["lit", "2"]]"#]]),
  ("operations", (["add", "sub", "mul", "div"].flatMap fun op => [
    [x1c s!"[\"eq\", [\"{op}\", [\"val\", \"x\"], [\"lit\", \"2\"]], [\"lit\", \"1\"]]"],
    [x1c s!"[\"eq\", [\"{op}\", [\"lit\", \"2\"], [\"val\", \"x\"]], [\"lit\", \"1\"]]"]])),
  ("comparison operands", (["eq", "lt", "le", "gt", "ge"].flatMap fun op => [
    [x1c s!"[\"{op}\", [\"val\", \"x\"], [\"lit\", \"2\"]]"], [x1c s!"[\"{op}\", [\"lit\", \"2\"], [\"val\", \"x\"]]"]])),
  -- 3.3: natural numbers stay JSON numbers.
  ("pow exponent", [
    [x1c r#"["eq", ["pow", ["val", "x"], 2], ["lit", "1"]]"#], [x1c r#"["eq", ["pow", ["val", "x"], 3], ["lit", "1"]]"#],
    [x1c r#"["eq", ["mul", ["val", "x"], ["val", "x"]], ["lit", "1"]]"#]]),
  -- 3.3: values, their sources, `support`, `span`, `software` and claim ids are part of the identity.
  ("value source", [[req x1 ok1], [req (defined "x" r#"["lit", "1"]"#) ok1]]),
  ("value names and order", [
    [req (x1 ++ ", " ++ stated "y" r#""2""#) ok1], [req (stated "y" r#""2""# ++ ", " ++ x1) ok1],
    [req (stated "y" r#""1""#) (c1 r#"["eq", ["val", "y"], ["lit", "1"]]"#)]]),
  ("support", [req x1 ok1] :: ["observation", "testimony", "assumption"].map fun support =>
    [req s!"\{\"name\": \"x\", \"words\": \"w\", \"stated\": \"1\", \"support\": \"{support}\"}" ok1]),
  ("claim span", [req x1 ok1] :: [[3, 3], [3, 5], [3, 6], [4, 5]].map fun span =>
    [req x1 s!"\{\"id\": \"c1\", \"claim\": [\"eq\", [\"val\", \"x\"], [\"lit\", \"1\"]], \"span\": {toJson span |>.compress}}"]),
  ("value span", [req x1 ok1] :: [[3, 3], [3, 5], [3, 6], [4, 5]].map fun span =>
    [req s!"\{\"name\": \"x\", \"words\": \"w\", \"stated\": \"1\", \"span\": {toJson span |>.compress}}" ok1]),
  ("software", [req x1 ok1] :: ["P", "Q", "Python 3.12"].map fun software =>
    [req x1 ok1 s!", \"software\": \"{software}\""]),
  ("claim ids", ["c1", "c2", "c-1"].map fun id => [req x1 (claim id r#"["eq", ["val", "x"], ["lit", "1"]]"#)])]

/-- The families the table refutes: a refused request, a class whose identities differ, or two classes that share a
`meaning_id`. -/
def identityFaults : List String := identityFamilies.filterMap fun (name, classes) =>
  let ids := classes.map (·.map identity)
  let sound := ids.all fun c => c.all fun i => i.all (· != "") && i.length > 1 && some i == c.head?
  if sound && decide ((ids.filterMap fun c => c.head?.bind List.head?).Nodup) then none else some name

#guard identityFaults == []

-- I-1's digests, pinned: the two wavelength spellings and the `"20000000"` printing.
#guard meaning (h8 r#""0.000000589""# r#"["sci", "2", 7]"#) == meaning (h8 r#"["sci", "5.89", -7]"# r#"["sci", "2", 7]"#)
#guard meaning (h8 r#"["sci", "5.89", -7]"# r#"["sci", "2", 7]"#) ==
  "b3798e85cad76f4bb79a0d6505ec54b46a48a9c00b74af0b8f77af74d962cb28"
#guard meaning (h8 r#""0.000000589""# r#""20000000""#) ==
  "c7cd36a48d5d80dcdac30bb4df5c47dfe7a5b51e38700d01c2acfc8b65ceb0c1"

-- Every already canonical claim is its own hashed form.
#guard (List.singleton r#"["within", ["val", "x"], ["lit", "0"], ["lit", "2"]]"# ++
  (["eq", "lt", "le", "gt", "ge"].flatMap fun op => [
    s!"[\"{op}\", [\"val\", \"x\"], [\"lit\", \"2\"]]",
    s!"[\"{op}\", [\"lit\", \"2\"], [\"val\", \"x\"]]"]) ++
  (["add", "sub", "mul", "div"].map fun op =>
    s!"[\"eq\", [\"{op}\", [\"val\", \"x\"], [\"lit\", \"2\"]], [\"lit\", \"1\"]]")).all fun s =>
    match Json.parse s with
    | .error _ => false
    | .ok j => match Wire.claim ("ties-up", .tiesUp) "claims.0.claim" j with
      | .ok (_, canonical) => canonical == j
      | .error _ => false

-- A claim with a printed number is hashed with its name as written, `[digits, places]` and its rule (I-1).
#guard [
    (r#"["rounds", ["val", "x"], "0.30"]"#, r#"["rounds",["val","x"],["30","2"],"ties-up"]"#),
    (r#"["rounds", ["val", "x"], ["sci", "2", 7], "half-even"]"#, r#"["rounds",["val","x"],["2","-7"],"half-even"]"#),
    (r#"["rounds-down", ["val", "x"], "-1.5"]"#, r#"["rounds-down",["val","x"],["-15","1"]]"#),
    (r#"["rounds-up", ["val", "x"], ["sci", "-0", 2]]"#, r#"["rounds-up",["val","x"],["0","-2"]]"#)].all
  fun (s, want) => match Json.parse s with
    | .error _ => false
    | .ok j => match Wire.claim ("ties-up", .tiesUp) "claims.0.claim" j with
      | .ok (_, canonical) => canonical.compress == want
      | .error _ => false

/-! Accepted edges of the decoder. A refusal-only corpus cannot pin these branches. -/
#guard meaning (req x1 (claim "c-1" r#"["eq", ["val", "x"], ["lit", "1"]]"#)) != ""
#guard ["observation", "testimony", "assumption"].all fun support =>
  meaning (req s!"\{\"name\": \"x\", \"words\": \"w\", \"stated\": \"1\", \"support\": \"{support}\"}" ok1) != ""
#guard meaning (req x1 r#"{"id": "c1", "claim": ["eq", ["val", "x"], ["lit", "1"]], "span": [3, 3]}"#) != ""
#guard meaning (req r#"{"name": "x", "words": "w", "stated": "1", "span": [3, 3]}"# ok1) != ""

-- Exact digests pin the encoding of each optional identity field, including JSON number type and span order.
#guard meaning (req x1 ok1 r#", "software": "P""#) ==
  "7c2d5ac13c8312f41b811897bb1d41afd4e06c5d634fc6652befb813ab97203e"
#guard meaning (req r#"{"name": "x", "words": "w", "stated": "1", "support": "observation"}"# ok1) ==
  "23602c987e56328857e0654cb9c82410ab7d64076d27d6e0a409ce1b023d72c8"
#guard meaning (req x1 r#"{"id": "c1", "claim": ["eq", ["val", "x"], ["lit", "1"]], "span": [3, 5]}"#) ==
  "5eed16c6aae468b703a685bb5ffd070f3c30476b09f097de7c0f898d4d6dffb5"
#guard meaning (req r#"{"name": "x", "words": "w", "stated": "1", "span": [3, 5]}"# ok1) ==
  "2e10e6d03ab1c276745095d8150d9c2fc21ecad2287b54c54e118ff5c68564dc"

-- The whole finite support vocabulary keeps its exact JSON spelling, not just distinct digests.
#guard Wire.supports.all fun s =>
  match Wire.recordJson "values.0" (Json.mkObj [("support", .str s)]) [] with
  | .ok j => j == Json.mkObj [("support", .str s)]
  | .error _ => false

/-! ## Limits (3.2), each on both sides, and their order -/

def pad (k : Nat) : String := req "" "" s!", \"pad\": [{nulls k}]"
def deep (d : Nat) : String := req "" "" s!", \"pad\": {String.mk (List.replicate d '[' ++ List.replicate d ']')}"
def name64 : String := String.mk (List.replicate 64 'x')

/-- Put a faulty array at the last admitted JSON level. The case object and 62 wrappers
make the fault array level 64, so a scan with less fuel misses it without a depth refusal. -/
def deepScanFault (fault : String) : String :=
  let nested := (List.range 62).foldl (fun s _ => s!"[{s}]") fault
  req x1 ok1 s!", \"pad\": {nested}"

def multiByteNames : List String :=
  [String.mk (List.replicate 32 'é'),
   "x" ++ String.mk (List.replicate 21 '€'),
   String.mk (List.replicate 16 '🐍')]

-- Ten times the largest flat limit fixture: count and depth must use bounded stack on a wide array.
#guard Wire.count 100002 [.arr (Array.replicate 100000 Json.null)] == 100001 &&
  Wire.depth 2 (.arr (Array.replicate 100000 Json.null)) == 1

-- Limit 1 comes before limit 2 at any nesting: values nested past the parser's 256 levels are still counted, and
-- a chain of 10,001 arrays is too many values, one of 10,000 too deep.
#guard [256, 300].all (fun d =>
    says (req x1 ok1 s!", \"pad\": {String.join (List.replicate d "[")}{nulls 20000}{String.join (List.replicate d "]")}") ==
      ["ResourceLimit: the number of JSON values exceeds 10000"]) &&
  [(10001, "ResourceLimit: the number of JSON values exceeds 10000"), (10000, "ResourceLimit: the JSON depth exceeds 64")].all
    fun (d, want) => match Json.parse (String.join (List.replicate d "[") ++ String.join (List.replicate d "]")) with
      | .ok j => Wire.limitFault j == some want
      | .error _ => false

-- Depth 64 remains usable for both expression entry points; depth 65 is a resource limit.
#guard
  let nestedExpr (n : Nat) : String := (List.range n).foldl
    (fun s _ => s!"[\"add\", {s}, [\"lit\", \"0\"]]") r#"["lit", "1"]"#
  meaning (req x1 (c1 s!"[\"eq\", {nestedExpr 59}, [\"lit\", \"1\"]]")) != "" &&
  says (req x1 (c1 s!"[\"eq\", {nestedExpr 60}, [\"lit\", \"1\"]]")) ==
    ["ResourceLimit: the JSON depth exceeds 64"] &&
  meaning (req (x1 ++ ", " ++ defined "y" (nestedExpr 60)) ok1) != "" &&
  says (req (x1 ++ ", " ++ defined "y" (nestedExpr 61)) ok1) ==
    ["ResourceLimit: the JSON depth exceeds 64"]

-- Every printed-number branch reaches the 40-digit boundary and refuses 41 digits as a resource limit.
#guard ["rounds", "rounds-down", "rounds-up"].all fun kind =>
  meaning (req x1 (c1 s!"[\"{kind}\", [\"val\", \"x\"], \"{ones 40}\"]")) != "" &&
  says (req x1 (c1 s!"[\"{kind}\", [\"val\", \"x\"], \"{ones 41}\"]")) ==
    ["ResourceLimit: Decimal literal exceeds 40 digits"]

#guard ["rounds", "rounds-down", "rounds-up"].all fun kind =>
  meaning (req x1 (c1 s!"[\"{kind}\", [\"val\", \"x\"], [\"sci\", \"{ones 40}\", 0]]")) != "" &&
  says (req x1 (c1 s!"[\"{kind}\", [\"val\", \"x\"], [\"sci\", \"{ones 41}\", 0]]")) ==
    ["ResourceLimit: Decimal literal exceeds 40 digits"]

#guard meaning (req (stated "x" s!"[\"sci\", \"{ones 40}\", 0]") ok1) != "" &&
  says (req (stated "x" s!"[\"sci\", \"{ones 41}\", 0]") ok1) ==
    ["ResourceLimit: Decimal literal exceeds 40 digits"]
#guard meaning (req (stated "x" r#"["sci", "1", 64]"#) ok1) != ""

#guard says (req x1 (claim name64 r#"["eq", ["val", "x"], ["lit", "1"]]"#)) == [name64 ++ " holds"]

-- The name limit counts UTF-8 bytes at all three name sites. These malformed names
-- are admitted by the limit at 64 bytes, then refused by the identifier grammar;
-- one more byte must instead be ResourceLimit before that grammar or name lookup.
#guard multiByteNames.all fun atLimit =>
  let over := atLimit ++ "x"
  atLimit.utf8ByteSize == VE.Limits.maxIdentifierBytes &&
  over.utf8ByteSize == VE.Limits.maxIdentifierBytes + 1 &&
  says (req (stated atLimit r#""1""#) ok1) == ["InvalidInput: values.0.name must be a name"] &&
  says (req (stated over r#""1""#) ok1) == ["ResourceLimit: a string exceeds 64"] &&
  says (req x1 (claim atLimit r#"["eq", ["val", "x"], ["lit", "1"]]"#)) ==
    ["InvalidInput: claims.0.id must be a claim id"] &&
  says (req x1 (claim over r#"["eq", ["val", "x"], ["lit", "1"]]"#)) ==
    ["ResourceLimit: a string exceeds 64"] &&
  says (req x1 (c1 s!"[\"eq\", [\"val\", \"{atLimit}\"], [\"lit\", \"1\"]]")) ==
    [s!"UnknownName: {atLimit} (declare it before the value that uses it)"] &&
  says (req x1 (c1 s!"[\"eq\", [\"val\", \"{over}\"], [\"lit\", \"1\"]]")) ==
    ["ResourceLimit: a string exceeds 64"]

/-! Limit 7 caps every string and object key of the case (2.6, 3.2); a value record's `words` string is the one
string it does not reach. -/

def strings64 : List String := name64 :: multiByteNames

-- F16: `software` of 64 bytes is a convention and one byte more a resource limit, ASCII and multi-byte.
#guard strings64.all fun s =>
  let sw (v : String) := req x1 ok1 s!", \"software\": \"{v}\""
  meaning (sw s) != "" && says (sw s) == ["c1 holds reproduction unknown"] &&
  says (sw (s ++ "x")) == ["ResourceLimit: a string exceeds 64"]

/-- Places me-2 checks no length of, or does not read: each refuses its string of 64 bytes otherwise, if at all. -/
def stringSites : List (String → String) := [
  fun s => req s!"\{\"name\": \"x\", \"words\": \"w\", \"stated\": \"1\", \"support\": \"{s}\"}" ok1,
  fun s => req x1 ok1 s!", \"rounding\": \"{s}\"",
  fun s => s!"\{\"format\": \"{s}\", \"values\": [{x1}], \"claims\": [{ok1}]}",
  fun s => req x1 (c1 s!"[\"{s}\", [\"val\", \"x\"], [\"lit\", \"1\"]]"),
  fun s => req x1 (c1 s!"[\"eq\", [\"{s}\", [\"val\", \"x\"], [\"lit\", \"1\"]], [\"lit\", \"1\"]]"),
  fun s => req x1 (c1 s!"[\"rounds\", [\"val\", \"x\"], \"1\", \"{s}\"]"),
  fun s => req x1 ok1 s!", \"premises\": [\{\"id\": \"{s}\"}]",
  fun s => req x1 ok1 s!", \"note\": \"{s}\"",
  fun s => req s!"\"{s}\"" ok1,
  -- `words` outside a value record, or not a string, is capped like any other string
  fun s => req x1 s!"\{\"id\": \"c1\", \"claim\": [\"eq\", [\"val\", \"x\"], [\"lit\", \"1\"]], \"words\": \"{s}\"}",
  fun s => req x1 ok1 s!", \"words\": \"{s}\"",
  fun s => req s!"\{\"name\": \"x\", \"words\": [\"{s}\"], \"stated\": \"1\"}" ok1,
  fun s => req s!"\{\"name\": \"x\", \"words\": \"w\", \"defined\": \{\"words\": \"{s}\"}}" ok1,
  -- object keys
  fun s => req x1 ok1 s!", \"{s}\": 1",
  fun s => req s!"\{\"name\": \"x\", \"words\": \"w\", \"stated\": \"1\", \"{s}\": 1}" ok1,
  fun s => req x1 s!"\{\"id\": \"c1\", \"claim\": [\"eq\", [\"val\", \"x\"], [\"lit\", \"1\"]], \"{s}\": 1}"]

#guard stringSites.all fun site => strings64.all fun s =>
  (says (site s)).all (!·.startsWith "ResourceLimit") && says (site (s ++ "x")) == ["ResourceLimit: a string exceeds 64"]

-- A value's `words` of any length is no resource limit.
#guard strings64.all fun s => meaning (req s!"\{\"name\": \"x\", \"words\": \"{s}{s}{s}\", \"stated\": \"1\"}" ok1) != ""

-- A literal of more than 40 digits and 64 bytes is limit 6, at each place a literal is read; earlier limits come
-- before the string cap too.
#guard (ones 65).utf8ByteSize > VE.Limits.maxIdentifierBytes &&
  [req (stated "x" s!"\"{ones 65}\"") ok1, req (stated "x" s!"[\"sci\", \"{ones 65}\", 0]") ok1,
    req x1 (c1 s!"[\"eq\", [\"val\", \"x\"], [\"lit\", \"{ones 65}\"]]"),
    req x1 (c1 s!"[\"rounds\", [\"val\", \"x\"], \"{ones 65}\"]")].all
    (says · == ["ResourceLimit: Decimal literal exceeds 40 digits"]) &&
  says (req (x1 ++ ", " ++ defined "y" r#"["pow", ["lit", "1"], 65]"#) ok1 s!", \"software\": \"{name64}x\"") ==
    ["ResourceLimit: an exponent exceeds 64"] &&
  says (req (nulls 513) ok1 s!", \"software\": \"{name64}x\"") == ["ResourceLimit: the number of values exceeds 512"]

#guard expect [
  ("nodes", says (pad 9995), ["InvalidInput: case.pad is unknown"]),
  ("nodes-over", says (pad 9996), ["ResourceLimit: the number of JSON values exceeds 10000"]),
  ("depth", says (deep 63), ["InvalidInput: case.pad is unknown"]),
  ("depth-over", says (deep 64), ["ResourceLimit: the JSON depth exceeds 64"]),
  ("values", says (req (nulls 512) ok1), ["InvalidInput: values.0 must be an object"]),
  ("values-over", says (req (nulls 513) ok1), ["ResourceLimit: the number of values exceeds 512"]),
  ("claims", says (req "" (nulls 512)), ["InvalidInput: claims.0 must be an object"]),
  ("claims-over", says (req "" (nulls 513)), ["ResourceLimit: the number of claims exceeds 512"]),
  ("pow", says (req (x1 ++ ", " ++ defined "y" r#"["pow", ["lit", "1"], 64]"#) ok1), ["c1 holds"]),
  ("pow-over", says (req (x1 ++ ", " ++ defined "y" r#"["pow", ["lit", "1"], 65]"#) ok1),
    ["ResourceLimit: an exponent exceeds 64"]),
  ("sci", says (req (stated "x" r#"["sci", "1", -64]"#) ok1), ["c1 fails"]),
  ("sci-over", says (req (stated "x" r#"["sci", "1", -65]"#) ok1), ["ResourceLimit: an exponent exceeds 64"]),
  ("digits", says (req (stated "x" s!"\"{ones 40}\"") ok1), ["c1 fails"]),
  ("digits-over", says (req (stated "x" s!"\"{ones 41}\"") ok1), ["ResourceLimit: Decimal literal exceeds 40 digits"]),
  ("digits-printed", says (req x1 (c1 s!"[\"rounds\", [\"val\", \"x\"], \"0.{ones 41}\"]")),
    ["ResourceLimit: Decimal literal exceeds 40 digits"]),
  ("digits-lit", says (req x1 (c1 s!"[\"eq\", [\"val\", \"x\"], [\"lit\", [\"sci\", \"{ones 41}\", 1]]]")),
    ["ResourceLimit: Decimal literal exceeds 40 digits"]),
  ("digits-lit-plain", says (req x1 (c1 s!"[\"eq\", [\"val\", \"x\"], [\"lit\", \"{ones 41}\"]]")),
    ["ResourceLimit: Decimal literal exceeds 40 digits"]),
  ("name", says (req (stated name64 r#""1""#) (c1 s!"[\"eq\", [\"val\", \"{name64}\"], [\"lit\", \"1\"]]")), ["c1 holds"]),
  ("name-over", says (req (stated (name64 ++ "x") r#""1""#) ok1), ["ResourceLimit: a string exceeds 64"]),
  ("id-over", says (req x1 (claim (name64 ++ "c") r#"["eq", ["val", "x"], ["lit", "1"]]"#)),
    ["ResourceLimit: a string exceeds 64"]),
  ("val-over", says (req x1 (c1 s!"[\"eq\", [\"val\", \"{name64}x\"], [\"lit\", \"1\"]]")),
    ["ResourceLimit: a string exceeds 64"]),
  ("order-digits-name", says (req (stated (name64 ++ "x") s!"\"{ones 41}\"") ok1),
    ["ResourceLimit: Decimal literal exceeds 40 digits"]),
  ("order-exponent-digits", says (req (stated "x" s!"\"{ones 41}\"" ++ ", " ++ defined "y" r#"["pow", ["val", "x"], 65]"#) ok1),
    ["ResourceLimit: an exponent exceeds 64"]),
  ("order-limit-field", says (req (stated "x" s!"\"{ones 41}\"") ok1 r#", "meaning_id": "forged""#),
    ["ResourceLimit: Decimal literal exceeds 40 digits"])]

-- Keep scanning to the admitted depth, including literals nested beyond six containers.
#guard
  let deepLit := (List.range 8).foldl
    (fun s _ => s!"[\"add\", {s}, [\"lit\", \"0\"]]") (s!"[\"lit\", \"{ones 41}\"]")
  says (req x1 (c1 s!"[\"eq\", {deepLit}, [\"lit\", \"1\"]]")) ==
    ["ResourceLimit: Decimal literal exceeds 40 digits"]

-- Every node-local limit is found at the last admitted depth. The first check pins
-- the shape, so a shallower JSON-depth refusal cannot make the scanner test pass.
#guard
  let faults := [
    (r#"["pow", "1", 65]"#, "ResourceLimit: an exponent exceeds 64"),
    (r#"["sci", "1", -65]"#, "ResourceLimit: an exponent exceeds 64"),
    (s!"[\"lit\", \"{ones 41}\"]", "ResourceLimit: Decimal literal exceeds 40 digits"),
    (s!"[\"val\", \"{name64}x\"]", "ResourceLimit: a string exceeds 64"),
    (s!"[\"{name64}x\"]", "ResourceLimit: a string exceeds 64"),
    (s!"\{\"{name64}x\": 1}", "ResourceLimit: a string exceeds 64")]
  faults.all fun (fault, want) =>
    let input := deepScanFault fault
    match Json.parse input with
    | .error _ => false
    | .ok j =>
      Wire.depth (VE.Limits.maxJsonDepth + 1) j == VE.Limits.maxDepth && says input == [want]

-- A well-formed expression also needs its deep exponent checked before evaluation.
#guard
  let nestedPow := (List.range 25).foldl
    (fun s _ => s!"[\"pow\", {s}, 1]") r#"["pow", ["val", "x"], 65]"#
  says (req x1 (c1 s!"[\"eq\", {nestedPow}, [\"lit\", \"1\"]]")) ==
    ["ResourceLimit: an exponent exceeds 64"]

/-! ## The hostile set and every refusal of the decoder -/

#guard expect [
  ("unknown-name", says (req (defined "y" r#"["add", ["val", "w"], ["lit", "1"]]"#) ok1),
    ["UnknownName: w (declare it before the value that uses it)"]),
  ("defined-after-use", says (req (defined "y" r#"["add", ["val", "x"], ["lit", "1"]]"# ++ ", " ++ x1) ok1),
    ["UnknownName: x (declare it before the value that uses it)"]),
  ("unknown-claim-name", says (req x1 (c1 r#"["lt", ["val", "q"], ["lit", "1"]]"#)),
    ["UnknownName: q (declare it before the value that uses it)"]),
  ("sign-spelling", says (req x1 (c1 r#"["rounds", ["val", "x"], "+1"]"#)), ["InvalidInput: claims.0.claim.2 must be a decimal"]),
  ("forged-meaning-id", says (req x1 ok1 r#", "meaning_id": "5a074a4cee5cfdce99fabb04e758d3d76f6bfdec93c035dbf66cc199c41aa2d1""#),
    ["InvalidInput: case.meaning_id is unknown"]),
  ("duplicate-name", says (req (x1 ++ ", " ++ x1) ok1), ["DuplicateName: x"]),
  ("duplicate-claim", says (req x1 (ok1 ++ ", " ++ ok1)), ["DuplicateClaimId: c1"]),
  ("no-claims", says (req x1 ""), ["NoClaims: a calculation needs at least one claim"]),
  ("not-object", says "[]", ["InvalidInput: case must be an object"]),
  ("format", says r#"{"format": "ve-calc@1", "values": [], "claims": []}"#, [r#"InvalidInput: case.format must be "ve-calc@0""#]),
  ("values-list", says r#"{"format": "ve-calc@0", "values": {}, "claims": []}"#, ["InvalidInput: case.values must be a list"]),
  ("rounding", says (req x1 ok1 r#", "rounding": "half-up""#),
    [r#"InvalidInput: case.rounding must be "ties-up" or "half-even""#]),
  ("claim-rule", says (req x1 (c1 r#"["rounds", ["val", "x"], "1", "half-up"]"#)),
    [r#"InvalidInput: claims.0.claim.3 must be "ties-up" or "half-even""#]),
  ("software", says (req x1 ok1 r#", "software": """#), ["InvalidInput: case.software must not be empty"]),
  ("follows-eq", says (req x1 (c1 r#"["follows", ["eq", ["val", "x"], ["lit", "2"]], [], []]"#)),
    ["InvalidInput: claims.0.claim.1 must be an lt, le, gt or ge claim"]),
  ("follows-form", says (req x1 (c1 r#"["follows", ["lt", ["val", "x"], ["lit", "2"]], []]"#)),
    ["InvalidInput: claims.0.claim must be a claim"]),
  ("sqrt-rounds", says (req x1 (c1 r#"["sqrt-rounds", ["val", "x"], "1"]"#)), ["InvalidInput: claims.0.claim must be a claim"]),
  ("expression", says (req x1 (c1 r#"["eq", ["neg", ["val", "x"]], ["lit", "1"]]"#)),
    ["InvalidInput: claims.0.claim.1 must be an expression"]),
  ("free", says (req r#"{"name": "x", "words": "the x", "free": false}"# ok1), ["InvalidInput: values.0.free must be true"]),
  ("no-source", says (req r#"{"name": "x", "words": "the x"}"# ok1),
    ["InvalidInput: values.0 must have one of stated, defined and free"]),
  ("two-sources", says (req r#"{"name": "x", "words": "the x", "stated": "1", "defined": ["lit", "1"]}"# ok1),
    ["InvalidInput: values.0 must have one of stated, defined and free"]),
  ("stated-free", says (req r#"{"name": "x", "words": "the x", "stated": "1", "free": true}"# ok1),
    ["InvalidInput: values.0 must have one of stated, defined and free"]),
  ("name", says (req r#"{"name": "X", "words": "the x", "stated": "1"}"# ok1), ["InvalidInput: values.0.name must be a name"]),
  ("words", says (req r#"{"name": "x", "words": 7, "stated": "1"}"# ok1), ["InvalidInput: values.0.words must be a string"]),
  ("support", says (req r#"{"name": "x", "words": "the x", "stated": "1", "support": "rumour"}"# ok1),
    ["InvalidInput: values.0.support must be observation, testimony or assumption"]),
  ("span", says (req r#"{"name": "x", "words": "the x", "stated": "1", "span": [5, 3]}"# ok1),
    ["InvalidInput: values.0.span must not end before it starts"]),
  ("span-form", says (req x1 r#"{"id": "c1", "claim": ["eq", ["val", "x"], ["lit", "1"]], "span": [1]}"#),
    ["InvalidInput: claims.0.span must be two natural numbers"]),
  ("claim-id", says (req x1 (claim "C 1" r#"["eq", ["val", "x"], ["lit", "1"]]"#)),
    ["InvalidInput: claims.0.id must be a claim id"]),
  ("pow-natural", says (req x1 (c1 r#"["eq", ["pow", ["val", "x"], -1], ["lit", "1"]]"#)),
    ["InvalidInput: claims.0.claim.1.2 must be a natural number"]),
  ("claim-id-first", says (req x1 (claim "Ac" r#"["eq", ["val", "x"], ["lit", "1"]]"#)),
    ["InvalidInput: claims.0.id must be a claim id"]),
  ("claim-id-last", says (req x1 (claim "aC" r#"["eq", ["val", "x"], ["lit", "1"]]"#)),
    ["InvalidInput: claims.0.id must be a claim id"]),
  ("claim-id-empty", says (req x1 (claim "" r#"["eq", ["val", "x"], ["lit", "1"]]"#)),
    ["InvalidInput: claims.0.id must be a claim id"])]

/-! Each argument's JSON path in a refusal -/

def bad : String := r#"["neg"]"#

#guard expect [
  ("rounds-1", says (req x1 (c1 s!"[\"rounds\", {bad}, \"1\"]")), ["InvalidInput: claims.0.claim.1 must be an expression"]),
  ("within-1", says (req x1 (c1 s!"[\"within\", {bad}, [\"lit\", \"1\"], [\"lit\", \"1\"]]")),
    ["InvalidInput: claims.0.claim.1 must be an expression"]),
  ("within-2", says (req x1 (c1 s!"[\"within\", [\"lit\", \"1\"], {bad}, [\"lit\", \"1\"]]")),
    ["InvalidInput: claims.0.claim.2 must be an expression"]),
  ("within-3", says (req x1 (c1 s!"[\"within\", [\"lit\", \"1\"], [\"lit\", \"1\"], {bad}]")),
    ["InvalidInput: claims.0.claim.3 must be an expression"]),
  ("compare-2", says (req x1 (c1 s!"[\"eq\", [\"val\", \"x\"], {bad}]")), ["InvalidInput: claims.0.claim.2 must be an expression"]),
  ("add-1", says (req x1 (c1 s!"[\"eq\", [\"add\", {bad}, [\"val\", \"x\"]], [\"lit\", \"1\"]]")),
    ["InvalidInput: claims.0.claim.1.1 must be an expression"]),
  ("add-2", says (req x1 (c1 s!"[\"eq\", [\"add\", [\"val\", \"x\"], {bad}], [\"lit\", \"1\"]]")),
    ["InvalidInput: claims.0.claim.1.2 must be an expression"]),
  ("pow-1", says (req x1 (c1 s!"[\"eq\", [\"pow\", {bad}, 2], [\"lit\", \"1\"]]")),
    ["InvalidInput: claims.0.claim.1.1 must be an expression"]),
  ("lit-1", says (req x1 (c1 r#"["eq", ["lit", 5], ["lit", "1"]]"#)), ["InvalidInput: claims.0.claim.1.1 must be a literal"]),
  ("lit-sci", says (req x1 (c1 r#"["eq", ["lit", ["sci", "1"]], ["lit", "1"]]"#)),
    ["InvalidInput: claims.0.claim.1.1 must be a literal"]),
  ("sci-2", says (req x1 (c1 r#"["eq", ["lit", ["sci", "1", 1.5]], ["lit", "1"]]"#)),
    ["InvalidInput: claims.0.claim.1.1.2 must be an integer"])]

/-! Malformed input: each field of a valid case, of a value record and of a claim entry, replaced by each malformed
JSON value, is a refusal and never a row (checklist item 1). -/

def malformed : List String := ["7", "true", "null", "[]", "{}", "1.5", "\"\"", "[[[[[[[[1]]]]]]]]"]

#guard malformed.all fun v => [
    s!"\{\"format\": {v}, \"values\": [{x1}], \"claims\": [{ok1}]}",
    s!"\{\"format\": \"ve-calc@0\", \"values\": {v}, \"claims\": [{ok1}]}",
    s!"\{\"format\": \"ve-calc@0\", \"values\": [{x1}], \"claims\": {v}}",
    req x1 ok1 s!", \"rounding\": {v}", req x1 ok1 s!", \"software\": {v}",
    req s!"\{\"name\": {v}, \"words\": \"w\", \"stated\": \"1\"}" ok1,
    req s!"\{\"name\": \"x\", \"words\": \"w\", \"stated\": {v}}" ok1,
    req s!"\{\"name\": \"x\", \"words\": \"w\", \"defined\": {v}}" ok1,
    req s!"\{\"name\": \"x\", \"words\": \"w\", \"stated\": \"1\", \"support\": {v}}" ok1,
    req s!"\{\"name\": \"x\", \"words\": \"w\", \"stated\": \"1\", \"span\": {v}}" ok1,
    req x1 s!"\{\"id\": {v}, \"claim\": [\"eq\", [\"val\", \"x\"], [\"lit\", \"1\"]]}",
    req x1 s!"\{\"id\": \"c1\", \"claim\": {v}}",
    req x1 (c1 s!"[\"eq\", [\"val\", \"x\"], {v}]"), req x1 (c1 s!"[\"rounds\", [\"val\", \"x\"], {v}]"),
    req x1 (c1 s!"[\"eq\", [\"lit\", {v}], [\"lit\", \"1\"]]")] ++
    -- words are any string until me-2b's words checks (W6, spec 11.2), so "" is no malformed words
    (if v == "\"\"" then [] else [req s!"\{\"name\": \"x\", \"words\": {v}, \"stated\": \"1\"}" ok1]) |>.all fun c =>
  (answer c).getObjVal? "rows" |>.toOption |>.isNone

/-! ## Derivations (ME-5; spec 3.1, 5 and 13.6): R-3 (H-6) follows, R-4 (H-6n) does not -/

def free (n w : String) : String := s!"\{\"name\": \"{n}\", \"words\": \"{w}\", \"free\": true}"
def premise (i c : String) (support : String := "assumption") : String :=
  s!"\{\"id\": \"{i}\", \"claim\": {c}, \"support\": \"{support}\"}"
def premises (ps : List String) : String := s!", \"premises\": [{", ".intercalate ps}]"
/-- R-3's values: the velocity ratio r, its square s and the displacement d, all free. -/
def rsd : String := free "r" "the velocity ratio" ++ ", " ++ free "s" "the squared velocity ratio" ++ ", " ++
  free "d" "the displacement"
/-- H-6's premises: p1, d = 0.4 s, and p2, d < `bound`. -/
def h6P (bound : String) : String := premises [premise "p1" r#"["eq", ["val", "d"], ["mul", ["lit", "0.4"], ["val", "s"]]]"#,
  premise "p2" s!"[\"lt\", [\"val\", \"d\"], [\"lit\", \"{bound}\"]]"]
/-- "r is less than 1 divided by `n`" from p1 and p2, across `links`. -/
def h6 (n : String) (links : String := r#"[["s", "r"]]"#) : String :=
  claim "h6" s!"[\"follows\", [\"lt\", [\"val\", \"r\"], [\"div\", [\"lit\", \"1\"], [\"lit\", \"{n}\"]]], [\"p1\", \"p2\"], {links}]"
def r3 : String := req rsd (h6 "4") (h6P "0.02")
def r4 : String := req rsd (h6 "5") (h6P "0.02")

#guard (answer r3).compress == r#"{"meaning_id":"3c3a2954052d22eb052c63806177a653dcae39bacaf7e6e65f14816e1c87ef32","rows":[{"claim":"h6","claim_id":"9bcd6eb6e369e68ef65aec41156ba5c6707016e9af7b9f1ed1ca1478cb94b08c","kind":"follows","outcome":"holds","reason":null,"reproduction":null,"status":"ok"}],"status":"ok"}"#
#guard (answer r4).compress == r#"{"meaning_id":"3648cca05ab8e1b20013ad47ea9648f021dada6fb32638bd495af5e049fef02e","rows":[{"claim":"h6","claim_id":"4dee606f697d7fea6bac0ab5b7eee2b2f69ba5f70d99c4d2e0d90fdede93a868","kind":"follows","outcome":"fails","reason":null,"reproduction":null,"status":"ok"}],"status":"ok"}"#

/-- A case over a free `x` with these premises and one derivation `c1` of `conclusion` from them. -/
def onX (ps : List String) (conclusion ids : String) (links : String := "[]") (values : String := free "x" "the x") :
    String := req values (c1 s!"[\"follows\", {conclusion}, {ids}, {links}]") (premises ps)
def xle (n : String) : String := s!"[\"le\", [\"val\", \"x\"], [\"lit\", \"{n}\"]]"
/-- A chain of definitions, each the sum of the one before with itself: its inlined tree doubles at each step. -/
def chain (n : Nat) : String := ", ".intercalate ((List.range n).map fun i =>
  defined s!"v{i + 1}" s!"[\"add\", [\"val\", \"v{i}\"], [\"val\", \"v{i}\"]]")
def steps : String := "unknown: the derivation search ran out of its 10,000 combination steps"
def nonlinear (path : String) : List String := [s!"NonlinearPremise: {path} (declare a square link or name the product)"]

#guard expect [
  ("h6p", says (req rsd (h6 "6") (h6P "0.01")), ["h6 holds"]),
  ("h6a-no-link", says (req rsd (h6 "4" "[]") (h6P "0.02")), ["h6 fails"]),
  ("h6-le", says (req rsd (claim "h6" r#"["follows", ["le", ["val", "r"], ["lit", "0.25"]], ["p1", "p2"], [["s", "r"]]]"#)
      (h6P "0.02")), ["h6 holds"]),
  ("h6-gt", says (req rsd (claim "h6" r#"["follows", ["gt", ["lit", "0.25"], ["val", "r"]], ["p1", "p2"], [["s", "r"]]]"#)
      (h6P "0.02")), ["h6 holds"]),
  ("h6-gt-fails", says (req rsd (claim "h6" r#"["follows", ["gt", ["lit", "0.2"], ["val", "r"]], ["p1", "p2"], [["s", "r"]]]"#)
      (h6P "0.02")), ["h6 fails"]),
  -- r ≤ 1/5 does not follow either, but the claimed bound satisfies it and no step of the square rule reaches it.
  ("h6-ge-edge", says (req rsd (claim "h6" r#"["follows", ["ge", ["lit", "0.2"], ["val", "r"]], ["p1", "p2"], [["s", "r"]]]"#)
      (h6P "0.02")), ["h6 unknown (unknown: no certificate and no counterexample was found)"]),
  ("no-solution", says (onX [premise "p1" (xle "1"), premise "p2" r#"["ge", ["val", "x"], ["lit", "2"]]"#]
      r#"["lt", ["val", "x"], ["lit", "0"]]"# r#"["p1", "p2"]"#), ["c1 holds"]),
  ("one-premise", says (onX [premise "p1" (xle "1"), premise "p2" r#"["ge", ["val", "x"], ["lit", "2"]]"#]
      r#"["lt", ["val", "x"], ["lit", "0"]]"# r#"["p1"]"#), ["c1 fails"]),
  ("within", says (onX [premise "p1" r#"["within", ["val", "x"], ["lit", "1"], ["lit", "2"]]"# "observation"]
      r#"["gt", ["val", "x"], ["lit", "0.5"]]"# r#"["p1"]"#), ["c1 holds"]),
  ("stated", says (req x1 (c1 r#"["follows", ["lt", ["val", "x"], ["lit", "2"]], [], []]"# ++ ", " ++
      claim "c2" r#"["follows", ["lt", ["val", "x"], ["lit", "0"]], [], []]"#)), ["c1 holds", "c2 fails"]),
  ("mixed", says (req (x1 ++ ", " ++ free "y" "the y") (ok1.replace "c1" "c0" ++ ", " ++
      c1 r#"["follows", ["lt", ["val", "y"], ["val", "x"]], ["p1"], []]"#) (premises [premise "p1" r#"["lt", ["mul", ["lit", "2"], ["val", "y"]], ["div", ["val", "x"], ["lit", "2"]]]"#])),
    ["c0 holds", "c1 holds"]),
  ("lower-bound", says (onX [premise "p1" r#"["gt", ["val", "s"], ["lit", "1"]]"#]
      r#"["gt", ["val", "x"], ["lit", "1"]]"# r#"["p1"]"# r#"[["s", "x"]]"# (free "x" "the x" ++ ", " ++ free "s" "the s")),
    [s!"c1 unknown (unknown: no certificate and no counterexample was found)"]),
  -- 64 facts and the negated conclusion are past the search's 64 facts; 63 are within them.
  ("facts-64", says (onX ((List.range 64).map fun i => premise s!"p{i}" (xle (toString i)))
      r#"["lt", ["val", "x"], ["lit", "100"]]"# (toJson ((List.range 64).map (s!"p{·}"))).compress), [s!"c1 unknown ({steps})"]),
  ("facts-63", says (onX ((List.range 63).map fun i => premise s!"p{i}" (xle (toString i)))
      r#"["lt", ["val", "x"], ["lit", "100"]]"# (toJson ((List.range 63).map (s!"p{·}"))).compress), ["c1 holds"]),
  ("chain", says (onX [premise "p1" r#"["lt", ["val", "v20"], ["lit", "1"]]"#] r#"["lt", ["val", "x"], ["lit", "1"]]"#
      r#"["p1"]"# "[]" (free "x" "the x" ++ ", " ++ defined "v0" r#"["val", "x"]"# ++ ", " ++ chain 20)),
    [s!"c1 unknown ({steps})"]),
  ("premises-512", says (onX ((List.range 512).map fun i => premise s!"p{i}" (xle "1")) (xle "1") "[]"), ["c1 fails"]),
  ("premises-513", says (onX ((List.range 513).map fun i => premise s!"p{i}" (xle "1")) (xle "1") "[]"),
    ["ResourceLimit: the number of premises exceeds 512"]),
  ("unknown-premise", says (req rsd (claim "h6" r#"["follows", ["lt", ["val", "r"], ["lit", "1"]], ["p1", "p3"], []]"#)
      (h6P "0.02")), ["UnknownPremise: p3"]),
  ("unknown-link-stated", says (req (rsd ++ ", " ++ stated "k" r#""1""#) (h6 "4" r#"[["s", "r"], ["k", "r"]]"#) (h6P "0.02")),
    ["UnknownLink: k"]),
  ("unknown-link-name", says (req rsd (h6 "4" r#"[["s", "q"]]"#) (h6P "0.02")), ["UnknownLink: q"]),
  ("nonlinear-square", says (onX [premise "p1" r#"["eq", ["val", "s"], ["mul", ["val", "x"], ["val", "x"]]]"#]
      (xle "1") r#"["p1"]"# "[]" (free "x" "the x" ++ ", " ++ free "s" "the s")), nonlinear "premises.0.claim.2"),
  ("nonlinear-pow", says (onX [premise "p1" r#"["lt", ["add", ["lit", "1"], ["pow", ["val", "x"], 2]], ["lit", "1"]]"#]
      (xle "1") r#"["p1"]"#), nonlinear "premises.0.claim.1.2"),
  ("nonlinear-divisor", says (onX [premise "p1" r#"["lt", ["div", ["lit", "1"], ["val", "x"]], ["lit", "1"]]"#]
      (xle "1") r#"["p1"]"#), nonlinear "premises.0.claim.1"),
  ("nonlinear-zero", says (onX [premise "p1" r#"["lt", ["div", ["val", "x"], ["sub", ["lit", "1"], ["lit", "1"]]], ["lit", "1"]]"#]
      (xle "1") r#"["p1"]"#), nonlinear "premises.0.claim.1"),
  ("nonlinear-conclusion", says (onX [] r#"["lt", ["lit", "1"], ["mul", ["val", "x"], ["val", "x"]]]"# "[]"),
    nonlinear "claims.0.claim.1.2"),
  ("nonlinear-defined", says (onX [premise "p1" (xle "1"), premise "p2" r#"["le", ["val", "q"], ["lit", "1"]]"#]
      (xle "1") r#"["p1"]"# "[]" (free "x" "the x" ++ ", " ++ defined "q" r#"["mul", ["val", "x"], ["val", "x"]]"#)),
    nonlinear "premises.1.claim.1"),
  ("linear-constants", says (onX [premise "p1" r#"["le", ["mul", ["pow", ["lit", "2"], 3], ["div", ["val", "x"], ["lit", "4"]]], ["pow", ["val", "x"], 1]]"#]
      (xle "0") r#"["p1"]"#), ["c1 holds"]),
  ("rounds-premise", says (onX [premise "p1" r#"["rounds", ["val", "x"], "1"]"#] (xle "1") r#"["p1"]"#),
    ["InvalidInput: premises.0.claim must be a comparison or a range"]),
  ("premise-support", says (onX [r#"{"id": "p1", "claim": ["le", ["val", "x"], ["lit", "1"]]}"#] (xle "1") r#"["p1"]"#),
    ["InvalidInput: premises.0.support is missing"]),
  ("premise-support-form", says (onX [premise "p1" (xle "1") "rumour"] (xle "1") r#"["p1"]"#),
    ["InvalidInput: premises.0.support must be observation, testimony or assumption"]),
  ("premise-field", says (onX [r#"{"id": "p1", "claim": ["le", ["val", "x"], ["lit", "1"]], "support": "assumption", "words": "w"}"#]
      (xle "1") r#"["p1"]"#), ["InvalidInput: premises.0.words is unknown"]),
  ("premise-id", says (onX [premise "p1" (xle "1")] (xle "1") "[1]"), ["InvalidInput: claims.0.claim.2.0 must be a premise id"]),
  ("link-form", says (onX [premise "p1" (xle "1")] (xle "1") r#"["p1"]"# r#"[["x"]]"#),
    ["InvalidInput: claims.0.claim.3.0 must be two names"]),
  ("premises-list", says (req (free "x" "the x") (c1 (s!"[\"follows\", {xle "1"}, [], []]")) r#", "premises": {}"#),
    ["InvalidInput: case.premises must be a list"]),
  ("premise-claim-id", says (onX [premise "c1" (xle "1")] (xle "1") r#"["c1"]"#), ["DuplicateClaimId: c1"]),
  ("premise-ids", says (onX [premise "p1" (xle "1"), premise "p1" (xle "2")] (xle "1") r#"["p1"]"#), ["DuplicateClaimId: p1"]),
  ("premise-name", says (onX [premise "p1" (xle "1"), premise "p2" r#"["le", ["val", "w"], ["lit", "1"]]"#] (xle "1") r#"["p1"]"#),
    ["UnknownName: w (declare it before the value that uses it)"])]

-- J10: R-3's line, each square link two numbered premises after the case's (spec 13.6).
#guard let words (n : String) : Option String :=
    [("r", "the velocity ratio"), ("s", "the squared velocity ratio"), ("d", "the displacement")].lookup n
  match ((Json.parse r3).toOption.bind (Wire.decodeCase · |>.toOption)).map (·.claims) with
  | some [(_, Check.follows P links C)] => VE.Calc.English.renderFollows words P links C == some
      ("Assume the following. 1. The displacement equals the product of 0.4 and the squared velocity ratio. " ++
       "2. The displacement is less than 0.02. 3. The squared velocity ratio equals the square of the velocity ratio. " ++
       "4. The velocity ratio is at least 0. From these, it follows that the velocity ratio is less than 1 divided by 4.")
  | _ => false

-- A derivation reading a value that has none is undefined, and one reading an exhausted counted value is unknown at
-- the budget (2.7), the first fault in the conclusion and then the premises deciding. Counted values reach the wire
-- with ME-4, so these are checked on declarations.
#guard let ds : List Decl := [⟨"r", .free⟩, ⟨"n", .counted (Thunk.pure none) (.ok none)⟩,
    ⟨"m", .counted (Thunk.pure none) .exhausted⟩]
  let lt (a b : String) : Claim := .compare ⟨.lt, false⟩ (.val a) (.val b)
  [Check.follows [] [] (lt "r" "n"), .follows [lt "r" "m"] [] (lt "r" "r"), .follows [lt "r" "n"] [] (lt "r" "m"),
    .follows [lt "r" "m", lt "r" "n"] [] (lt "r" "r")].map (·.run ds) ==
  [.decided .undefined, .unknown (.limit .evaluations), .unknown (.limit .evaluations), .unknown (.limit .evaluations)]

-- Spec 3.3: free values, premises (their ids, claims, supports and spans) and a derivation's parts are hashed; an
-- empty `premises` list is no premise.
def deriv (ps : List String) (ids links : String) : String := onX ps (xle "1") ids links (free "x" "the x" ++ ", " ++ free "s" "the s")
#guard identityFaults.isEmpty && [
    ("premises", [[deriv [] "[]" "[]", req (free "x" "the x" ++ ", " ++ free "s" "the s") (c1 s!"[\"follows\", {xle "1"}, [], []]")],
      [deriv [premise "p1" (xle "1")] "[]" "[]"], [deriv [premise "p1" (xle "2")] "[]" "[]"],
      [deriv [premise "q1" (xle "1")] "[]" "[]"], [deriv [premise "p1" (xle "1") "observation"] "[]" "[]"],
      [deriv [r#"{"id": "p1", "claim": ["le", ["val", "x"], ["lit", "1"]], "support": "assumption", "span": [3, 5]}"#] "[]" "[]"]]),
    ("derivation", [[deriv [premise "p1" (xle "1")] r#"["p1"]"# "[]"], [deriv [premise "p1" (xle "1")] "[]" r#"[["s", "x"]]"#],
      [deriv [premise "p1" (xle "1")] "[]" r#"[["x", "s"]]"#], [deriv [premise "p1" (xle "1")] "[]" "[]"]]),
    ("free", [[req (free "x" "the x") (ok1.replace "eq" "le")], [req x1 (ok1.replace "eq" "le")]])].all fun (_, classes) =>
  let ids := classes.map (·.map identity)
  ids.all (fun c => c.all fun i => i.all (· != "") && i.length > 1 && some i == c.head?) &&
    decide ((ids.filterMap fun c => c.head?.bind List.head?).Nodup)

end VE.Calc.RunExamples
