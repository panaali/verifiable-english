import VE.SoftNorms.Status

/-! The soft validation table (docs/spec/soft-norms.md 8), as ordered phases.

`checkSource` runs the phases over the whole source (environment and norm
objects) in table order: envelope, vocabulary declarations, profiles, rule
fields, cross references, and the rank checks of the semantic phase. No check
of a phase runs before every check of the earlier phases has passed, so the
first diagnostic is fixed by the table, not by the order in which a decoder
happens to visit the input. Every check carries its own stable code; inherited
W1/P0 checks run their decoder at their position and report
`SOFT_INVALID_INPUT` whatever class their text names. `ve/softnorms.py` is the
same list. The remaining semantic checks (6.4 to 6.10) are `validateSoft`'s, on
the decoded document. -/
namespace VE.SoftNorms.Phases
open Lean
open VE.Norms
open VE.Bridge (exactFields fields strings)

/-- A failed check: its stable code and its human-readable text. -/
structure Fault where
  code : String
  message : String

abbrev Check := Except Fault

def fail {α : Type} (code message : String) : Check α := .error ⟨code, message⟩

/-- An inherited W1/P0 check, classified by its position in the table. -/
def inherited {α : Type} (x : Except String α) (code : String := "SOFT_INVALID_INPUT") : Check α :=
  match x with
  | .ok a => .ok a
  | .error e => .error ⟨code, e⟩

def softProfile : String := "soft-norms@0"
def inheritedProfiles : List String := ["data@0", "definitions@0", "documents@1", "time@0"]
def checkerProfiles : List String := ["closure@0", "nary@0", "order@0"]
def w1Keys : List String := ["name", "predicate", "sign", "guard", "unless", "over"]
def softKeys : List String := ["mode", "rank", "alterable", "exception", "hard"]

def keysOf (j : Json) : Option (List String) := (fields j).toOption.map (·.map (·.1))

def sameKeys (actual expected : List String) : Bool :=
  actual.length == expected.length && expected.all actual.contains

def deciderOk (d : String) : Bool := !d.isEmpty && d.utf8ByteSize ≤ 64

/-! ## Phase 1: envelope -/

def normArray (norms : Json) : Check (List Json) := do
  let units ← match norms with
    | .arr xs => pure xs.toList
    | _ => fail "SOFT_INVALID_INPUT" "InvalidInput: expected an array of norm objects"
  if units.length > 256 then fail "SOFT_RESOURCE_LIMIT" "ResourceLimit: rules"
  pure units

/-- 1.1 to 1.7; the profiles and the norm objects. -/
def envelope (environment norms : Json) : Check (List String × List Json) := do
  unless (keysOf environment).any (sameKeys · ["language", "profiles", "spec_revision", "vocabulary"]) do
    fail "SOFT_INVALID_INPUT" "InvalidInput: invalid environment envelope"
  unless environment.getObjValD "language" == .str VE.Route.Gate.language do
    fail "SOFT_UNSUPPORTED_PROFILE" "UnsupportedProfile: Unsupported language"
  let profiles ← match strings (environment.getObjValD "profiles") with
    | .ok ps => pure ps
    | .error _ => fail "SOFT_UNSUPPORTED_PROFILE" "UnsupportedProfile: profiles must be a sorted unique array"
  unless environment.getObjValD "spec_revision" == .str VE.Route.Gate.specRevision do
    fail "SOFT_UNSUPPORTED_PROFILE" "UnsupportedProfile: Unsupported specification revision"
  let vocab := environment.getObjValD "vocabulary"
  let required := ["sorts", "predicates", "constants"]
  unless (keysOf vocab).any (fun ks => required.all ks.contains &&
      ks.all (fun k => required.contains k || k == "soft")) &&
      required.all (fun k => (keysOf (vocab.getObjValD k)).isSome) do
    fail "SOFT_INVALID_INPUT" "InvalidInput: invalid vocabulary"
  pure (profiles, ← normArray norms)

/-! ## Phase 2: vocabulary declarations -/

def softNames (block : Json) (field : String) (limit : Nat) : Check (List String) := do
  let values ← match block.getObjVal? field with
    | .error _ => pure []
    | .ok (.arr xs) => pure xs.toList
    | .ok _ => fail "SOFT_INVALID_ARRAY" s!"InvalidInput: {field} must be an array"
  if values.length > limit then fail "SOFT_RESOURCE_LIMIT" s!"ResourceLimit: {field}"
  let mut names := []
  for value in values do
    let name ← match value with
      | .str s => if validSoftName s then pure s
                  else fail "SOFT_INVALID_NAME" s!"InvalidInput: invalid soft name {s}"
      | _ => fail "SOFT_INVALID_NAME" s!"InvalidInput: invalid soft name {value.compress}"
    if names.contains name then
      fail "SOFT_DUPLICATE_DECLARATION"
        s!"DuplicateDeclaration: {if field == "parties" then "party" else "rank"} {name}"
    names := names ++ [name]
  pure names

def softPairs (block : Json) (field code : String) : Check (List (String × String)) := do
  let values ← match block.getObjVal? field with
    | .error _ => pure []
    | .ok (.arr xs) => pure xs.toList
    | .ok _ => fail "SOFT_INVALID_ARRAY" s!"InvalidInput: {field} must be an array"
  let mut pairs := []
  for value in values do
    let pair ← match value with
      | .arr #[.str a, .str b] => pure (a, b)
      | _ => fail code s!"InvalidInput: invalid {field} pair"
    if pair.1 == pair.2 || pairs.contains pair then fail code s!"InvalidInput: invalid {field} pair"
    pairs := pairs ++ [pair]
  pure pairs

/-- A predicate entry without its soft attribute, as W1 decodes it. -/
def stripEntry (entry : Json) : Json :=
  match fields entry with
  | .ok kvs => Json.mkObj (kvs.filter (·.1 != "instruction_of"))
  | .error _ => entry

def noBlock (io : List (String × String)) : SoftEnv := ⟨[], [], [], [], .strict, none, none, io⟩

/-- 2.1 to 2.17: the W1 declarations (decoded under the inherited profiles) and the soft block. -/
def declarations (environment : Json) (profiles : List String) :
    Check (Norms.Wire.NormsEnvironment × SoftEnv) := do
  let vocab := environment.getObjValD "vocabulary"
  -- `fields` enumerates an object in canonical key order.
  let preds ← inherited (fields (vocab.getObjValD "predicates"))
  for (p, e) in preds do
    if reservedPredicate p || (containsDunder p && (e.getObjVal? "regulated").isOk) then
      fail "SOFT_INVALID_NAME" s!"InvalidInput: invalid soft name {p}"
  let mut io := []
  for (p, e) in preds do
    match e.getObjVal? "instruction_of" with
    | .error _ => pure ()
    | .ok (.str π) =>
      if (e.getObjVal? "regulated").isOk || (e.getObjVal? "defined").isOk then
        fail "SOFT_INVALID_INPUT" s!"InvalidInput: instruction_of on {p}"
      io := io ++ [(p, π)]
    | .ok _ => fail "SOFT_INVALID_INPUT" s!"InvalidInput: instruction_of on {p}"
  let base := VE.Route.sortStrings
    ((profiles.filter inheritedProfiles.contains).eraseDups ++ ["norms@0", VE.Route.Gate.base])
  -- Python's W1 accepts a `defined` field only under `definitions@0`.
  unless base.contains "definitions@0" do
    if let some (p, _) := preds.find? (fun (_, e) => (e.getObjVal? "defined").isOk) then
      fail "SOFT_INVALID_INPUT" s!"InvalidInput: {p} declares defined without definitions@0"
  let stripped := (environment.setObjVal! "profiles" (toJson base)).setObjVal! "vocabulary"
    (Json.mkObj [("sorts", vocab.getObjValD "sorts"), ("constants", vocab.getObjValD "constants"),
      ("predicates", Json.mkObj (preds.map (fun (p, e) => (p, stripEntry e))))])
  let ne ← inherited (Norms.Wire.decodeNormsEnvironment stripped)
  let some block := (vocab.getObjVal? "soft").toOption | pure (ne, noBlock io)
  unless (VE.Bridge.displayFields block ["outranking"]
      ["parties", "ranks", "outranks", "ties", "exception_decider"]).isOk do
    fail "SOFT_INVALID_BLOCK" "InvalidInput: invalid soft block"
  let parties ← softNames block "parties" 8
  let ranks ← softNames block "ranks" 16
  let o := block.getObjValD "outranking"
  unless (VE.Bridge.displayFields o ["mode"] ["decided_by"]).isOk do
    fail "SOFT_INVALID_OUTRANKING" "InvalidInput: invalid outranking flag"
  let mode ← match o.getObjValD "mode" with
    | .str "strict" => pure Outranking.strict
    | .str "holistic" => pure Outranking.holistic
    | _ => fail "SOFT_INVALID_OUTRANKING" "InvalidInput: invalid outranking flag"
  let given := (o.getObjVal? "decided_by").toOption
  if mode == .strict && given.isSome then
    fail "SOFT_STRICT_OUTRANKING_DECIDER" "InvalidInput: strict outranking has no decider"
  let decider ← match given with
    | none => pure none
    | some (.str d) => pure (some d)
    | some _ => fail "SOFT_INVALID_DECIDER" "InvalidInput: invalid decider for outranking"
  if mode == .holistic && decider.isNone then
    fail "SOFT_MISSING_DECIDER" "MissingExceptionDecider: outranking"
  for d in decider.toList do
    unless deciderOk d do fail "SOFT_INVALID_DECIDER" "InvalidInput: invalid decider for outranking"
  let exceptionDecider ← match block.getObjVal? "exception_decider" with
    | .error _ => pure none
    | .ok (.str d) => if deciderOk d then pure (some d)
                      else fail "SOFT_INVALID_DECIDER" "InvalidInput: invalid decider for exception"
    | .ok _ => fail "SOFT_INVALID_DECIDER" "InvalidInput: invalid decider for exception"
  let outranks ← softPairs block "outranks" "SOFT_INVALID_OUTRANKS_PAIR"
  let ties ← softPairs block "ties" "SOFT_INVALID_TIES_PAIR"
  pure (ne, ⟨parties, ranks, outranks, ties, mode, decider, exceptionDecider, io⟩)

/-! ## Phase 3: profiles -/

def unsupported (message : String) : Check Unit :=
  fail "SOFT_UNSUPPORTED_PROFILE" s!"UnsupportedProfile: {message}"

/-- 3.1 to 3.5. -/
def profileChecks (profiles : List String) (ne : Norms.Wire.NormsEnvironment) : Check Unit := do
  unless decide (profiles.Pairwise (· < ·)) do unsupported "profiles must be sorted and unique"
  for p in profiles do
    unless VE.Route.Gate.known p || p == softProfile do unsupported s!"Unsupported profile {p}"
  unless profiles.contains VE.Route.Gate.base do unsupported s!"Missing profile {VE.Route.Gate.base}"
  unless profiles.contains softProfile do unsupported "soft-norms@0 is required"
  unless profiles.contains "norms@0" do unsupported "soft-norms@0 requires norms@0"
  if profiles.any checkerProfiles.contains then unsupported "the norms route admits FOL documents only"
  unless ne.rv.definitions.isEmpty do unsupported "norms route with definitions is not implemented"
  unless ne.rv.flags.isEmpty do unsupported "norms route with data flags is not implemented"

/-! ## Phase 4: rule fields -/

/-- 4.9 to 4.14: a default rule's exception object. -/
def exceptionFields (exceptionDecider : Option String) (name : String) (j : Json) : Check Exception := do
  unless (VE.Bridge.displayFields j ["sufficient", "necessary", "factors"] ["decided_by"]).isOk do
    fail "SOFT_MISSING_EXCEPTION" s!"InvalidInput: rule {name} needs an exception"
  let decidedBy ← match j.getObjVal? "decided_by" with
    | .error _ | .ok .null => pure none
    | .ok (.str s) => pure (some s)
    | .ok _ => fail "SOFT_INVALID_DECIDER" s!"InvalidInput: invalid decider for rule {name}"
  if decidedBy.isNone && exceptionDecider.isNone then
    fail "SOFT_MISSING_DECIDER" s!"MissingExceptionDecider: rule {name}"
  for d in decidedBy.toList do
    unless deciderOk d do fail "SOFT_INVALID_DECIDER" s!"InvalidInput: invalid decider for rule {name}"
  let conditions (k : String) : Check (List VE.Formula) :=
    match j.getObjValD k with
    | .arr xs => xs.toList.mapM (fun x => inherited (Norms.Wire.decodeBudgeted x))
    | _ => fail "SOFT_EXCEPTION_ARRAY" s!"InvalidInput: exception {k} must be an array"
  let sufficient ← conditions "sufficient"
  let necessary ← conditions "necessary"
  let factors ← match strings (j.getObjValD "factors") with
    | .ok fs => if fs.all (·.utf8ByteSize ≤ 200) then pure fs
                else fail "SOFT_INVALID_FACTORS" s!"InvalidInput: invalid factors of rule {name}"
    | .error _ => fail "SOFT_INVALID_FACTORS" s!"InvalidInput: invalid factors of rule {name}"
  pure ⟨decidedBy, sufficient, necessary, factors⟩

/-- 4.1 to 4.14 for one norm object; `mode` defaults to `strict`. -/
def ruleFields (exceptionDecider : Option String) (j : Json) : Check SoftNode := do
  let raw := j.getObjValD "norm"
  unless (keysOf j).any (sameKeys · ["norm"]) && (keysOf raw).isSome do
    fail "SOFT_INVALID_INPUT" "InvalidInput: expected norm object"
  let obj ← inherited (fields raw)
  let keys := obj.map (·.1)
  unless w1Keys.all keys.contains && keys.all (fun k => w1Keys.contains k || softKeys.contains k) do
    fail "SOFT_INVALID_INPUT" "InvalidInput: invalid norm fields"
  -- Python's `_fol` gives the guard and each carve-out its own node budget.
  let N ← inherited (Norms.Wire.decodeNorm
    (Json.mkObj [("norm", Json.mkObj (obj.filter (fun kv => w1Keys.contains kv.1)))]) (shared := false))
  unless ruleName N.name do fail "SOFT_INVALID_INPUT" s!"InvalidInput: invalid rule name {pyRepr N.name}"
  if N.carveOuts.length > 8 then fail "SOFT_INVALID_INPUT" "InvalidInput: invalid sign or too many carve-outs"
  let mode ← match raw.getObjVal? "mode" with
    | .error _ => pure Mode.strict
    | .ok (.str "strict") => pure Mode.strict
    | .ok (.str "default") => pure Mode.default
    | .ok _ => fail "SOFT_INVALID_RULE_FIELDS" s!"InvalidInput: invalid mode for rule {N.name}"
  let rank ← match raw.getObjVal? "rank" with
    | .error _ | .ok .null => pure none
    | .ok (.str r) => pure (some r)
    | .ok _ => fail "SOFT_INVALID_RULE_FIELDS" s!"InvalidInput: invalid soft fields for {N.name}"
  let badAlterable := s!"InvalidInput: alterable of rule {N.name} must be sorted and distinct"
  let alterable ← match raw.getObjVal? "alterable" with
    | .error _ => pure []
    | .ok v => match strings v with
      | .ok ps => pure ps
      | .error _ => fail "SOFT_INVALID_ALTERABLE" badAlterable
  unless sortedDistinct alterable do fail "SOFT_INVALID_ALTERABLE" badAlterable
  let hard ← match raw.getObjVal? "hard" with
    | .error _ => pure false
    | .ok (.bool b) => pure b
    | .ok _ => fail "SOFT_INVALID_RULE_FIELDS" s!"InvalidInput: hard of rule {N.name} must be Boolean"
  if hard && (mode == .default || !alterable.isEmpty) then
    fail "SOFT_HARD_CONSTRAINT" s!"HardConstraintAltered: rule {N.name}"
  let given := match raw.getObjVal? "exception" with
    | .error _ | .ok .null => none
    | .ok e => some e
  let exception ← match mode, given with
    | .strict, none => pure none
    | .strict, some _ =>
      fail "SOFT_STRICT_EXCEPTION" s!"InvalidInput: rule {N.name} is strict and declares an exception"
    | .default, none => fail "SOFT_MISSING_EXCEPTION" s!"InvalidInput: rule {N.name} needs an exception"
    | .default, some e => some <$> exceptionFields exceptionDecider N.name e
  pure { N with mode, rank, alterable, exception, hard }

/-! ## Phase 5: cross references -/

/-- 5.1 and 5.2. -/
def environmentReferences (soft : SoftEnv) : Check Unit := do
  for (_, π) in soft.instructionOf do
    unless soft.parties.contains π do fail "SOFT_UNKNOWN_PARTY" s!"UnknownSymbol: party {π}"
  for (a, b) in soft.outranks ++ soft.ties do
    for r in [a, b] do
      unless soft.ranks.contains r do fail "SOFT_UNKNOWN_RANK" s!"UnknownRank: {r}"

/-- W1's typing of one formula (inherited). -/
def typed (E : VE.Environment) (Γ : List String) (φ : VE.Formula) (message : String) : Check Unit := do
  inherited (typeDiagnostic E Γ φ)
  unless φ.check E Γ do fail "SOFT_INVALID_INPUT" message

/-- 5.4 to 5.8 for one rule. Python types a rule's guard, carve-outs and
exception conditions with one `_Checker`: they share one `MAX_NODES` budget,
checked as each formula is typed (inherited). -/
def ruleReferences (ne : Norms.Wire.NormsEnvironment) (soft : SoftEnv) (N : SoftNode) : Check Unit := do
  let some r := ne.regulated.find? (·.name == N.pred)
    | fail "SOFT_INVALID_INPUT" s!"UnknownSymbol: regulated predicate {N.pred}"
  for a in N.rank.toList do
    unless soft.ranks.contains a do fail "SOFT_UNKNOWN_RANK" s!"UnknownRank: rule {N.name}, {a}"
  for π in N.alterable do
    unless soft.parties.contains π do fail "SOFT_UNKNOWN_PARTY" s!"UnknownSymbol: party {π}"
  let E := ne.rv.environment
  let mut nodes := 0
  for φ in N.guard :: N.carveOuts do
    typed E r.sorts.reverse φ s!"InvalidInput: ill-typed rule {N.name}"
    nodes := nodes + VE.Bridge.formulaNodes φ
    if nodes > Norms.Wire.maxNodes then fail "SOFT_INVALID_INPUT" "ResourceLimit: AST exceeds 10,000 nodes"
  for e in N.exception.toList do
    for C in e.sufficient ++ e.necessary do
      typed E r.sorts.reverse C s!"InvalidInput: ill-typed rule {N.name}"
      nodes := nodes + VE.Bridge.formulaNodes C
      if nodes > Norms.Wire.maxNodes then fail "SOFT_INVALID_INPUT" "ResourceLimit: AST exceeds 10,000 nodes"
      if let some q := (preds C).find? (fun q => (ne.regulated.map (·.name)).contains q ||
          (ne.rv.definitions.map (·.name)).contains q || reservedPredicate q) then
        fail "SOFT_INVALID_EXCEPTION_CONDITION"
          s!"InvalidInput: exception condition of rule {N.name} mentions {q}"

/-- 5.3 to 5.9 over the whole document. -/
def documentReferences (ne : Norms.Wire.NormsEnvironment) (soft : SoftEnv) (nodes : List SoftNode) :
    Check Unit := do
  let mut names := []
  for N in nodes do
    if names.contains N.name then fail "SOFT_DUPLICATE_DECLARATION" s!"DuplicateDeclaration: rule {N.name}"
    names := names ++ [N.name]
  for N in nodes do
    ruleReferences ne soft N
    for m in N.over do
      match nodes.find? (·.name == m) with
      | none => fail "SOFT_INVALID_INPUT" s!"UnknownRule: rule {m}"
      | some M =>
        unless M.pred == N.pred do
          fail "SOFT_INVALID_INPUT"
            s!"PrecedenceAcrossPredicates: rule {N.name} on {N.pred}, rule {M.name} on {M.pred}"

/-! ## Phase 6, environment part: the rank order -/

/-- 6.1 to 6.3. -/
def rankSemantics (soft : SoftEnv) : Check Unit := do
  let _ ← inherited (VE.Route.dependencyOrder (rankNodes soft)) "SOFT_DEPENDENCY_CYCLE"
  for (a, b) in soft.ties do
    if outranksPlus soft a b || outranksPlus soft b a then
      fail "SOFT_TIE_AGAINST_ORDER" s!"TieAgainstOrder: {a}, {b}"
  if (soft.ties.map (fun (a, b) => if a ≤ b then (a, b) else (b, a))).eraseDups.length != soft.ties.length then
    fail "SOFT_DUPLICATE_DECLARATION" "DuplicateDeclaration: tie"

/-! ## The whole source -/

structure Checked where
  ne : Norms.Wire.NormsEnvironment
  soft : SoftEnv
  profiles : List String
  nodes : List SoftNode

/-- Phases 1 to 5 and 6.1 to 6.3, each over the whole source before the next. -/
def checkSource (environment norms : Json) : Check Checked := do
  let (profiles, units) ← envelope environment norms
  let (ne, soft) ← declarations environment profiles
  profileChecks profiles ne
  let nodes ← units.mapM (ruleFields soft.exceptionDecider)
  environmentReferences soft
  documentReferences ne soft nodes
  rankSemantics soft
  pure ⟨ne, soft, profiles, nodes⟩

end VE.SoftNorms.Phases
