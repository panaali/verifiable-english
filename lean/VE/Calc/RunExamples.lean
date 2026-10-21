import VE.Calc.Run

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

/-! ## Identity (3.3, J1): what changes the `meaning_id` and what does not -/

#guard meaning (h8 r#""0.000000589""# r#"["sci", "2", 7]"#) == meaning (h8 r#"["sci", "5.89", -7]"# r#"["sci", "2", 7]"#)
#guard meaning (h8 r#"["sci", "5.89", -7]"# r#"["sci", "2", 7]"#) ==
  "b3798e85cad76f4bb79a0d6505ec54b46a48a9c00b74af0b8f77af74d962cb28"
#guard meaning (h8 r#""0.000000589""# r#""20000000""#) ==
  "c7cd36a48d5d80dcdac30bb4df5c47dfe7a5b51e38700d01c2acfc8b65ceb0c1"
#guard meaning (req (stated "x" r#""0.30""#) ok1) == meaning (req (stated "x" r#""0.3""#) ok1)
#guard meaning (req x1 ok1 r#", "rounding": "ties-up""#) == meaning (req x1 ok1)
#guard meaning (req r#"{"words": "the other words", "stated": "1", "name": "x"}"# ok1) == meaning (req x1 ok1)
#guard meaning (req x1 (c1 r#"["rounds", ["val", "x"], "0.30"]"#)) != meaning (req x1 (c1 r#"["rounds", ["val", "x"], "0.3"]"#))
#guard meaning (req x1 (c1 r#"["rounds", ["val", "x"], "0.3", "half-even"]"#)) !=
  meaning (req x1 (c1 r#"["rounds", ["val", "x"], "0.3"]"#))
#guard meaning (req r#"{"name": "x", "words": "w", "stated": "1", "support": "testimony"}"# ok1) != meaning (req x1 ok1)
#guard meaning (req r#"{"name": "x", "words": "w", "stated": "1", "span": [3, 5]}"# ok1) != meaning (req x1 ok1)
#guard meaning (req x1 ok1 r#", "software": "Python 3.12""#) != meaning (req x1 ok1)

/-! ## Limits (3.2), each on both sides, and their order -/

def pad (k : Nat) : String := req "" "" s!", \"pad\": [{nulls k}]"
def deep (d : Nat) : String := req "" "" s!", \"pad\": {String.mk (List.replicate d '[' ++ List.replicate d ']')}"
def name64 : String := String.mk (List.replicate 64 'x')

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
  ("name", says (req (stated name64 r#""1""#) (c1 s!"[\"eq\", [\"val\", \"{name64}\"], [\"lit\", \"1\"]]")), ["c1 holds"]),
  ("name-over", says (req (stated (name64 ++ "x") r#""1""#) ok1), ["ResourceLimit: a name exceeds 64"]),
  ("id-over", says (req x1 (claim (name64 ++ "c") r#"["eq", ["val", "x"], ["lit", "1"]]"#)),
    ["ResourceLimit: a name exceeds 64"]),
  ("val-over", says (req x1 (c1 s!"[\"eq\", [\"val\", \"{name64}x\"], [\"lit\", \"1\"]]")),
    ["ResourceLimit: a name exceeds 64"]),
  ("order-digits-name", says (req (stated (name64 ++ "x") s!"\"{ones 41}\"") ok1),
    ["ResourceLimit: Decimal literal exceeds 40 digits"]),
  ("order-exponent-digits", says (req (stated "x" s!"\"{ones 41}\"" ++ ", " ++ defined "y" r#"["pow", ["val", "x"], 65]"#) ok1),
    ["ResourceLimit: an exponent exceeds 64"]),
  ("order-limit-field", says (req (stated "x" s!"\"{ones 41}\"") ok1 r#", "meaning_id": "forged""#),
    ["ResourceLimit: Decimal literal exceeds 40 digits"])]

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
  ("follows", says (req x1 (c1 r#"["follows", ["lt", ["val", "x"], ["lit", "2"]], [], []]"#)),
    ["InvalidInput: claims.0.claim must be a claim"]),
  ("sqrt-rounds", says (req x1 (c1 r#"["sqrt-rounds", ["val", "x"], "1"]"#)), ["InvalidInput: claims.0.claim must be a claim"]),
  ("expression", says (req x1 (c1 r#"["eq", ["neg", ["val", "x"]], ["lit", "1"]]"#)),
    ["InvalidInput: claims.0.claim.1 must be an expression"]),
  ("free", says (req r#"{"name": "x", "words": "the x", "free": true}"# ok1), ["InvalidInput: values.0.free is unknown"]),
  ("no-source", says (req r#"{"name": "x", "words": "the x"}"# ok1),
    ["InvalidInput: values.0 must have one of stated and defined"]),
  ("two-sources", says (req r#"{"name": "x", "words": "the x", "stated": "1", "defined": ["lit", "1"]}"# ok1),
    ["InvalidInput: values.0 must have one of stated and defined"]),
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

end VE.Calc.RunExamples
