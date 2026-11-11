import VE.EnglishGrammar.Norm.Read
import VE.EnglishGrammar.Norm.Elab

/-! The en-s6 fixtures of docs/spec/english-lean-s6.md section 6, at the piece level (DRI decision
reviews/dri-decisions-20261101-en-s6.md item 1): the block faults of f13-f16 and f24, the statements of f7 and f8,
and the carve-outs of f10 and f11. Each piece is the value spec 2.5 gives its sentence. en-s6b's part, below, reads
the texts of section 6 with `readNorm` and compares the nodes with Python's. Each check has an accepting and a
refusing side. -/

namespace VE.EnglishGrammar.Norm.Examples
open Lean VE.EnglishGrammar VE.EnglishGrammar.Norm

/-- A W1 clause over "Every act", as a consequence row gives it (spec 2.5). -/
def cl (f : Force) (u : List EFormula := []) : Clause := ⟨.every "act", .modal f, .strict, "permitted", [], .top, u, []⟩

def hd (n : Nat) (refs : List Nat := []) : Piece := .header ⟨n, refs⟩

def may : Piece := .clause (cl .may)
def mustNot : Piece := .clause (cl .mustNot)

def faultOf (ps : List Piece) : Option BlockFault :=
  match assemble ps with
  | .ok _ => none
  | .error f => some f

def statements (ps : List Piece) : Option (List NormStatement) := (assemble ps).toOption

-- f13: `Rule 2. Every act may be done.` opens block 1 with the wrong number.
#guard faultOf [hd 2, may] == some (.expectedRule 0 1)
#guard statements [hd 1, may] == some [.rule ⟨1, []⟩ (cl .may)]
#guard faultOf [hd 1, may, hd 3, may] == some (.expectedRule 2 2)
-- f14: `Rule 1. Every act may be done.` `Rule 1 takes precedence over rule 3.`
#guard faultOf [hd 1, may, .precedence 1 3] == some (.unknownRule 3)
#guard statements [hd 1, may, .precedence 1 1] == some [.rule ⟨1, []⟩ (cl .may), .precedence 1 1]
-- f15: `Rule 1. Rule 2. Every act may be done.`
#guard faultOf [hd 1, hd 2, may] == some (.noConsequence 0)
#guard (statements [hd 1, may, hd 2, may]).map ruleCount == some 2
#guard faultOf [hd 1, may, hd 2] == some (.noConsequence 2)
-- f16: `Rule 1. Except when this holds in all cases.`
#guard faultOf [hd 1, .exceptWhen .top] == some (.strayCarveOut 1)
#guard statements [hd 1, may, .exceptWhen .top] == some [.rule ⟨1, []⟩ (cl .may [.top])]
-- f24: `Rule 9 takes precedence over rule 1.` with no block; a reference to 0 is out of range too (spec 2.3).
#guard faultOf [.precedence 9 1] == some (.unknownRule 9)
#guard faultOf [hd 1, may, .precedence 1 0] == some (.unknownRule 0)
#guard faultOf [hd 1 [0], may] == some (.unknownRule 0)
#guard faultOf [hd 1 [2], may] == some (.unknownRule 2)
#guard faultOf [hd 1, may, hd 2 [1], may] == none
#guard faultOf [hd 1 [5], may, hd 2, may] == some (.unknownRule 5)
#guard faultOf [hd 1 [5], may, .precedence 1 7] == some (.unknownRule 5)
-- a block's faults come before an unknown reference
#guard faultOf [hd 1, may, .precedence 1 5, hd 3, may] == some (.expectedRule 3 2)
-- a clause sentence outside a block, or a second one in a block
#guard faultOf [may] == some (.strayConsequence 0)
#guard faultOf [hd 1, may, mustNot] == some (.strayConsequence 2)
#guard faultOf [hd 1, may, .precedence 1 1, mustNot] == some (.strayConsequence 3)

-- f7: `Rule 1. Every act must not be done.` `Rule 2. Every act may be done.` `Rule 2 takes precedence over rule 1.`
#guard statements [hd 1, mustNot, hd 2, may, .precedence 2 1] ==
  some [.rule ⟨1, []⟩ (cl .mustNot), .rule ⟨2, []⟩ (cl .may), .precedence 2 1]
-- f8: `Rule 3 (exception to rules 1 and 2).` keeps its targets in text order.
#guard statements [hd 1, mustNot, hd 2, mustNot, hd 3 [1, 2], may] ==
  some [.rule ⟨1, []⟩ (cl .mustNot), .rule ⟨2, []⟩ (cl .mustNot), .rule ⟨3, [1, 2]⟩ (cl .may)]
#guard (statements [hd 1, mustNot, hd 2, mustNot, hd 3 [1, 2], may]).map (·.flatMap NormStatement.refs) ==
  some [1, 2]

-- f10, f11: an inline carve-out stays first, and except-when sentences append theirs in text order.
def a : EFormula := .pred "describes_mitigation_and_deviates" [.var 0]
def b : EFormula := .pred "noteworthy" [.var 0]
#guard statements [hd 1, .clause (cl .may [a]), .exceptWhen b] == some [.rule ⟨1, []⟩ (cl .may [a, b])]
#guard statements [hd 1, may, .exceptWhen a, .exceptWhen b] == some [.rule ⟨1, []⟩ (cl .may [a, b])]
#guard statements [hd 1, may, .exceptWhen a, .exceptWhen b] != some [.rule ⟨1, []⟩ (cl .may [b, a])]
#guard faultOf [hd 1, may, .precedence 1 1, .exceptWhen a] == some (.strayCarveOut 3)

-- W1's stored signs (`norm_english.py:97-100`), and a plain wording's own sign (R2).
#guard [Force.must, .needNot, .may, .mustNot].map (Polarity.sign ∘ .modal) == [true, false, true, false]
#guard [true, false].map (Polarity.sign ∘ .plain) == [true, false]
-- The values later layers produce (EN-4, EN-5, EN-7) are distinct; authoring produces none of them.
#guard [Bearer.every "act", .named "the company", .author, .unstated].eraseDups.length == 4
#guard [Place.act, .guard, .carveOut, .bearer].eraseDups.length == 4
#guard Mode.default "decider" != .strict
#guard cl .may != { cl .may with residuals := [⟨0, 4, "word|frame|profile", "EN-7", .act⟩] }
#guard NState.init.scope == none
-- A translation-mode statement has its clauses, no number and no reference.
#guard (NormStatement.source [cl .may, cl .mustNot]).clauses == [cl .may, cl .mustNot]
#guard (NormStatement.source [cl .may]).refs == [] && (NormStatement.source [cl .may]).number? == none
#guard ruleCount [.source [cl .may], .rule ⟨1, []⟩ (cl .may), .precedence 1 1] == 1
#guard (statements [hd 1, may, .precedence 1 1]).map (·.flatMap NormStatement.clauses) == some [cl .may]

/-! ## en-s6b: the reader on the texts of spec section 6

The environments are those of `tests/test_norm_english.py` (from `tests.test_norms`), as `Env.decode` reads them:
`act` (`permission()`), `two` (`permission()` and `obligation()`), `help` (a permission over a state and a person),
`pair` (a permission over two acts), `item n` (the plain environment of f12, without and with a selected negative),
and `fd` (`ReadExamples`' `FD` with `norms@0` and a permission `used` over a service). Each lexicon is the one Python
selects (`ve.english_grammar.export`). Python's nodes are `parse_english`'s, recorded at e4575ba73. f20 to f22 read
the RSP, FSF and constitution environments, too large for this file: `tests/test_english_statement_blocks.py`. -/

/-- An environment with `norms@0`, from the JSON of its sorts and predicates. -/
def envOf (sorts preds : String) (profiles := "") (soft := "") (first := "") : Env :=
  match (Json.parse ("{\"language\": \"ve.core@0.2\", \"profiles\": [" ++ first ++ "\"norms@0\", \"relational-fol@0\"" ++
      profiles ++ "], \"spec_revision\": \"ve-v0.2-expand2-2026-09-25\", \"vocabulary\": {\"constants\": {}, \"sorts\": " ++
      sorts ++ ", \"predicates\": " ++ preds ++ soft ++ "}}")).bind (Env.decode · .null) with
  | .ok E => E
  | .error _ => { sorts := [], predicates := [], constants := [] }

def regulated (role act : String) (args := "[\"act\"]") (more := "") : String :=
  "{\"arguments\": " ++ args ++ ", \"description\": \"" ++ role ++ "\", \"regulated\": {\"role\": \"" ++ role ++
    "\", \"default\": \"deny\"" ++ act ++ more ++ "}}"
def permitted (act := "{0} be done") (args := "[\"act\"]") : String :=
  "{\"permitted\": " ++ regulated "permission" (", \"act\": \"" ++ act ++ "\"") args ++ "}"
def actSorts := "{\"act\": {\"description\": \"act\"}}"

def act : Env := envOf actSorts permitted
def two : Env := envOf actSorts ("{\"permitted\": " ++ regulated "permission" ", \"act\": \"{0} be done\"" ++
  ", \"required\": " ++ regulated "obligation" ", \"act\": \"{0} be done\"" "[\"act\"]" ", \"permission\": \"permitted\"" ++ "}")
def help : Env := envOf "{\"state\": {\"description\": \"state\"}, \"person\": {\"description\": \"person\"}}"
  (permitted "{0} help {1}" "[\"state\", \"person\"]")
def pair : Env := envOf actSorts (permitted "{0} help {1}" "[\"act\", \"act\"]")
def item (negative : String) : Env := envOf "{\"item\": {\"description\": \"item\"}}"
  ("{\"admitted\": {\"arguments\": [\"item\"], \"description\": \"admitted\", \"verbalisation\": \"{0} is admitted\", " ++
    negative ++ "\"regulated\": {\"role\": \"plain\", \"default\": \"deny\"}}}")
def fd : Env := envOf ("{\"person\": {\"description\": \"A sort.\"}, \"service\": {\"description\": \"A sort.\"}, " ++
    "\"dservice\": {\"description\": \"A sort.\", \"verbalisation\": {\"singular\": \"deployed service\", " ++
    "\"plural\": \"deployed services\"}}}")
  ("{\"deployed\": {\"arguments\": [\"service\"], \"description\": \"d\", \"verbalisation\": \"{0} is deployed\"}, " ++
    "\"reviewed\": {\"arguments\": [\"service\"], \"description\": \"r\", \"verbalisation\": \"{0} is reviewed\"}, " ++
    "\"used\": " ++ regulated "permission" ", \"act\": \"{0} be used\"" "[\"service\"]" ++ "}")

/-- Python's lexicon (`ve.english_grammar.export`). -/
def lexOf (nouns letters wordings : List (String × String)) (negatives : List (String × String) := []) : Lexicon :=
  { nouns, letters, wordings, negatives, aliases := [], spellings := [] }
def LA := lexOf [("act", "act")] [("act", "C")] [("permitted", "{0} may be done")]
def L2 := lexOf [("act", "act")] [("act", "C")] [("permitted", "{0} may be done"), ("required", "{0} must be done")]
def LH := lexOf [("person", "person"), ("state", "state")] [("person", "P"), ("state", "S")] [("permitted", "{0} may help {1}")]
def LS := lexOf [("act", "act")] [("act", "C")] [("permitted", "{0} may help {1}")]
def LI (negatives : List (String × String)) := lexOf [("item", "item")] [("item", "T")] [("admitted", "{0} is admitted")] negatives
def LD := lexOf [("dservice", "deployed service"), ("person", "person"), ("service", "service")]
  [("dservice", "D"), ("person", "P"), ("service", "S")] [("deployed", "{0} is deployed"), ("reviewed", "{0} is reviewed"),
    ("used", "{0} may be used")]

/-- An outcome without its values: where and why the reader stopped. -/
def outcome : NormOutcome → String
  | .ok _ => "ok"
  | .invalidGrammar g => s!"invalidGrammar {repr g}"
  | .lexical r => s!"lexical {repr r}"
  | .stopped i .noDerivation => s!"stopped {i} noDerivation"
  | .stopped i (.ambiguous t u) => s!"stopped {i} ambiguous {decide (t ≠ u)}"
  | .stopped i (.rejected r) => s!"stopped {i} rejected {repr r}"
  | .stopped i .budget => s!"stopped {i} budget"
  | .stopped i (.ok _ _) => s!"stopped {i} ok"
  | .misplaced f => s!"misplaced {repr f}"

def stmts : NormOutcome → Option (List NormStatement)
  | .ok rs => some rs
  | _ => none

def clauses (o : NormOutcome) : Option (List Clause) := (stmts o).map (·.flatMap NormStatement.clauses)

/-- Python's nodes (a JSON array of `norm` objects), through the one decoder. -/
def python (s : String) : Except String (List VE.Norms.Node) := do
  match ← Json.parse s with
  | .arr xs => xs.toList.mapM fun j => VE.Norms.Wire.decodeNorm (Json.mkObj [("norm", j)])
  | _ => throw "not an array"

def nodes (o : NormOutcome) : Except String (List VE.Norms.Node) :=
  match o with
  | .ok rs => toNodes rs
  | o => throw (outcome o)

def same (a b : Except String (List VE.Norms.Node)) : Bool :=
  match a, b with
  | .ok x, .ok y => x == y
  | _, _ => false

/-- The W1 document of the rules read (section 4, "not claimed"): `decodeSource` on their wire objects. -/
def document (E : Env) (o : NormOutcome) : Bool :=
  match o with
  | .ok rs => (VE.Norms.Wire.decodeSource E.source (.arr ((rs.filterMap fun | .rule h c => some (h, c) | _ => none).map
      fun (h, c) => Json.mkObj [("norm", (c.wire (ruleName h.number) ((overOf rs h.number).map ruleName)).getObjValD "norm")]).toArray)).toBool
  | _ => false

/-- `readNorm_authoring`'s and `readNorm_regulated`'s conclusions, decided. Section 4 lets a `#guard` over every
fixture of section 6 stand for their proofs; this item records that substitution (REPORT). -/
def authored (E : Env) (o : NormOutcome) : Bool :=
  match stmts o with
  | some rs => rs.all (fun | .source _ => false | _ => true) && (rs.flatMap NormStatement.clauses).all fun c =>
      c.mode == .strict && c.residuals.isEmpty && c.args.isEmpty && (regulatedOf E).any fun r =>
        r.name == c.pred && c.force.fits r.role && r.sorts.head?.any (c.bearer == .every ·)
  | none => false

/-- The one reading of this file, so `authored` runs on every text that reads and a fixture cannot leave it out: a
reading it refuses comes back as a stop, which no accepting guard passes. -/
def rd (E : Env) (L : Lexicon) (s : String) : NormOutcome :=
  match readNorm E {} L workBudget s with
  | .ok rs => if authored E (.ok rs) then .ok rs else .stopped 0 .noDerivation
  | o => o

-- f1: the four rules `render_english` gives in `test_four_wordings_and_identity_manifest`.
def f1 := "Rule 1. Every act must not be done.\nRule 2 (exception to rule 1). Every act may be done.\nRule 3. Every act must be done.\nRule 4. Every act need not be done."
def f1Python := "[{\"guard\": [\"top\"], \"name\": \"rule-1\", \"over\": [], \"predicate\": \"permitted\", \"sign\": false, \"unless\": []}, {\"guard\": [\"top\"], \"name\": \"rule-2\", \"over\": [\"rule-1\"], \"predicate\": \"permitted\", \"sign\": true, \"unless\": []}, {\"guard\": [\"top\"], \"name\": \"rule-3\", \"over\": [], \"predicate\": \"required\", \"sign\": true, \"unless\": []}, {\"guard\": [\"top\"], \"name\": \"rule-4\", \"over\": [], \"predicate\": \"required\", \"sign\": false, \"unless\": []}]"
#guard same (nodes (rd two L2 f1)) (python f1Python) && document two (rd two L2 f1)
#guard !same (nodes (rd two L2 (f1.replace "Rule 4. Every act need not" "Rule 4. Every act must"))) (python f1Python)
#guard !document two (rd two L2 (f1.replace "rule 1)" "rule 4)")) && !authored two (rd two L2 "")
-- f2: `No act may be done` is a permission of sign false.
#guard clauses (rd act LA "Rule 1. No act may be done.") == some [cl .mustNot]
#guard same (nodes (rd act LA "Rule 1. No act may be done.")) (python "[{\"guard\": [\"top\"], \"name\": \"rule-1\", \"over\": [], \"predicate\": \"permitted\", \"sign\": false, \"unless\": []}]")
#guard outcome (rd act LA "Rule 1. No act must be done.") == "stopped 1 noDerivation"
-- f3, f4, f17: no consequence row matches; the declared wording does.
#guard outcome (rd act LA "Rule 1. A act may be done.") == "stopped 1 noDerivation"
#guard outcome (rd act LA "Rule 1. Every act should be done.") == "stopped 1 noDerivation"
#guard outcome (rd act LA "Rule 1. Every act must be sung.") == "stopped 1 noDerivation"
#guard clauses (rd act LA "Rule 1. Every act may be done.") == some [cl .may]
-- f5, f6, f23: "each" and "any" bind the second slot; "every" does not.
#guard clauses (rd help LH "Rule 1. Every state may help each person.") ==
  some [⟨.every "state", .modal .may, .strict, "permitted", [], .top, [], []⟩]
#guard stmts (rd help LH "Rule 1. Every state may help any person.") == stmts (rd help LH "Rule 1. Every state may help each person.")
#guard outcome (rd help LH "Rule 1. Every state may help every person.") == "stopped 1 noDerivation"
#guard clauses (rd pair LS "Rule 1. Every first act may help each second act.") == some [cl .may]
#guard stmts (rd pair LS "Rule 1. Every first act may help any second act.") == stmts (rd pair LS "Rule 1. Every first act may help each second act.")
#guard outcome (rd pair LS "Rule 1. Every first act may help every second act.") == "stopped 1 noDerivation"
-- f7: a precedence line adds to the rule's `over`.
def f7 := "Rule 1. Every act must not be done.\nRule 2. Every act may be done.\nRule 2 takes precedence over rule 1."
#guard (stmts (rd act LA f7)).map (overOf · 2) == some [1] && document act (rd act LA f7)
#guard (nodes (rd act LA f7)).toOption.map (·.map (·.over)) == some [[], ["rule-1"]]
#guard outcome (rd act LA (f7.replace "over rule 1" "over rule 3")) == "misplaced VE.EnglishGrammar.Norm.BlockFault.unknownRule 3"
-- f8, f9: a header's targets, in text order; `rules 1, and 2` has no derivation.
def f8 := "Rule 1. Every act must not be done.\nRule 2. Every act must not be done.\nRule 3 (exception to rules 1 and 2). Every act may be done."
#guard (stmts (rd act LA f8)).map (·.flatMap NormStatement.refs) == some [1, 2] && document act (rd act LA f8)
#guard (stmts (rd act LA (f8.replace "rules 1 and 2" "rules 2, 1"))).map (·.flatMap NormStatement.refs) == some [2, 1]
#guard outcome (rd act LA (f8.replace "rules 1 and 2" "rules 1, and 2")) == "stopped 4 noDerivation"
-- f10: `, except when` and `, unless` give one carve-out each, and no guard.
#guard clauses (rd act LA "Rule 1. Every act may be done, except when this holds in all cases.") == some [cl .may [.top]]
#guard clauses (rd act LA "Rule 1. Every act may be done, unless that act may be done.") ==
  some [cl .may [.pred "permitted" [.var 0]]]
#guard clauses (rd act LA "Rule 1. Every act may be done, if that act may be done.") ==
  some [{ cl .may with guard := .pred "permitted" [.var 0] }]
-- f11: a guard, then two except-when sentences read under the clause's bindings.
def f11 := "Rule 1. Every act may be done.\nRule 2. Every act must be done, if that act may be done. Except when that act may be done. Except when this holds in all cases."
def f11Python := "[{\"guard\": [\"top\"], \"name\": \"rule-1\", \"over\": [], \"predicate\": \"permitted\", \"sign\": true, \"unless\": []}, {\"guard\": [\"unary\", \"permitted\", [\"var\", 0]], \"name\": \"rule-2\", \"over\": [], \"predicate\": \"required\", \"sign\": true, \"unless\": [[\"unary\", \"permitted\", [\"var\", 0]], [\"top\"]]}]"
#guard same (nodes (rd two L2 f11)) (python f11Python) && document two (rd two L2 f11)
#guard !same (nodes (rd two L2 (f11.replace "Except when that act may be done. Except when this holds in all cases."
  "Except when this holds in all cases. Except when that act may be done."))) (python f11Python)
#guard outcome (rd two L2 "Rule 1. Every act must be done. Except when that act may be done.\nRule 2. Except when this holds in all cases.") ==
  "misplaced VE.EnglishGrammar.Norm.BlockFault.strayCarveOut 4"
-- f12: a plain role of sign false, with and without a selected negative; each form needs its own lexicon.
def plainNo := "[{\"guard\": [\"top\"], \"name\": \"rule-1\", \"over\": [], \"predicate\": \"admitted\", \"sign\": false, \"unless\": []}]"
def universal := "Rule 1. For every item, it is not the case that that item is admitted."
def negative := "\"negative_verbalisation\": \"{0} is not admitted\", "
#guard same (nodes (rd (item "") (LI []) universal)) (python plainNo)
#guard same (nodes (rd (item negative) (LI [("admitted", "{0} is not admitted")]) "Rule 1. Every item is not admitted.")) (python plainNo)
#guard clauses (rd (item "") (LI []) "Rule 1. Every item is admitted.") == some [⟨.every "item", .plain true, .strict, "admitted", [], .top, [], []⟩]
#guard outcome (rd (item "") (LI []) "Rule 1. Every item is not admitted.") == "stopped 1 noDerivation"
#guard outcome (rd (item negative) (LI [("admitted", "{0} is not admitted")]) universal) == "stopped 1 noDerivation"
-- f13-f16, f24: the block faults, from the text.
#guard outcome (rd act LA "Rule 2. Every act may be done.") == "misplaced VE.EnglishGrammar.Norm.BlockFault.expectedRule 0 1"
#guard outcome (rd act LA "Rule 1. Every act may be done.\nRule 1 takes precedence over rule 3.") ==
  "misplaced VE.EnglishGrammar.Norm.BlockFault.unknownRule 3"
#guard outcome (rd act LA "Rule 1. Every act may be done.\nRule 1 takes precedence over rule 1.") == "ok"
#guard outcome (rd act LA "Rule 1. Rule 2. Every act may be done.") == "misplaced VE.EnglishGrammar.Norm.BlockFault.noConsequence 0"
#guard outcome (rd act LA "Rule 1. Except when this holds in all cases.") == "misplaced VE.EnglishGrammar.Norm.BlockFault.strayCarveOut 1"
#guard outcome (rd act LA "Rule 9 takes precedence over rule 1.") == "misplaced VE.EnglishGrammar.Norm.BlockFault.unknownRule 9"
-- f18: a condition with two derivations stops the reading, with both trees; one derivation reads.
#guard outcome (rd fd LD "Rule 1. Every service may be used, if every deployed service is reviewed.") == "stopped 1 ambiguous true"
#guard clauses (rd fd LD "Rule 1. Every service may be used, if that service is reviewed.") ==
  some [⟨.every "service", .modal .may, .strict, "used", [], .pred "reviewed" [.var 0], [], []⟩]
-- R7 (DRI decision 20261102-en-s6b item 2): the soft constructs are stripped only when `soft-norms@0` is named.
def softAct (profiles : String) : Env := envOf actSorts permitted profiles ", \"soft\": {}"
#guard (softAct "").predicates.length == 1 && (regulatedOf (softAct "")).isEmpty
#guard outcome (rd (softAct "") LA "Rule 1. Every act may be done.") == "stopped 1 noDerivation"
#guard (regulatedOf (softAct ", \"soft-norms@0\"")).map (·.name) == ["permitted"]
#guard clauses (rd (softAct ", \"soft-norms@0\"") LA "Rule 1. Every act may be done.") == some [cl .may]
#guard (regulatedOf (softAct ", \"soft-norms@0\", \"time@0\"")).map (·.name) == ["permitted"]
-- The trust mutants' fixtures (docs/english-lean/en-s6b/mutants.json). Both bindings in a condition:
#guard clauses (rd help LH "Rule 1. Every state may help each person, if that state may help that person.") ==
  some [⟨.every "state", .modal .may, .strict, "permitted", [], .pred "permitted" [.var 1, .var 0], [], []⟩]
#guard clauses (rd help LH "Rule 1. Every state may help each person, if that person may help that state.") ==
  some [⟨.every "state", .modal .may, .strict, "permitted", [], .pred "permitted" [.var 0, .var 1], [], []⟩]
-- a guard and an inline carve-out in one clause, each read once and kept in its place
#guard clauses (rd act LA "Rule 1. Every act may be done, if that act may be done, unless this holds in all cases.") ==
  some [⟨.every "act", .modal .may, .strict, "permitted", [], .pred "permitted" [.var 0], [.top], []⟩]
#guard clauses (rd act LA "Rule 1. Every act may be done, if this holds in all cases, except when that act may be done.") ==
  some [⟨.every "act", .modal .may, .strict, "permitted", [], .top, [.pred "permitted" [.var 0]], []⟩]
-- each condition place reads a formula, not only an atom (the rows' `.base 2`)
def neg := "it is not the case that that act may be done"
#guard ([", if " ++ neg ++ ".", ", unless " ++ neg ++ ".", ", except when " ++ neg ++ ".", ", if " ++ neg ++ ", unless " ++
  neg ++ ".", ", if " ++ neg ++ ", except when " ++ neg ++ ".", ". Except when " ++ neg ++ "."].map fun t =>
    (clauses (rd act LA ("Rule 1. Every act may be done" ++ t))).map (·.map fun c =>
      ((c.guard :: c.carveOuts).filter (· matches .not _)).length)) == [some [1], some [1], some [1], some [2], some [2], some [1]]
#guard outcome (rd act LA "Rule 1. Every act may be done, if may be done.") == "stopped 1 noDerivation"
-- a binary plain role without a negative: the universal form binds both slots, "each" or "any"
def assigned : Env := envOf "{\"item\": {\"description\": \"item\"}, \"person\": {\"description\": \"person\"}}"
  ("{\"assigned\": {\"arguments\": [\"item\", \"person\"], \"description\": \"assigned\", \"verbalisation\": " ++
    "\"{0} is assigned to {1}\", \"regulated\": {\"role\": \"plain\", \"default\": \"deny\"}}}")
def LAs := lexOf [("item", "item"), ("person", "person")] [("item", "T"), ("person", "P")]
  [("assigned", "{0} has the recorded relation \"assigned\" to {1}")]
def binaryNo := "Rule 1. For every item, for each person, it is not the case that that item has the recorded relation \"assigned\" to that person."
#guard clauses (rd assigned LAs binaryNo) == some [⟨.every "item", .plain false, .strict, "assigned", [], .top, [], []⟩]
#guard stmts (rd assigned LAs (binaryNo.replace "for each" "for any")) == stmts (rd assigned LAs binaryNo)
#guard outcome (rd assigned LAs (binaryNo.replace "that person." "that item.")) == "stopped 1 noDerivation"
-- the plain predicate's wording and negative read among others
def u (v : String) (more := "") : String := "{\"arguments\": [\"item\"], \"description\": \"" ++ v ++
  "\", \"verbalisation\": \"{0} is " ++ v ++ "\", \"negative_verbalisation\": \"{0} is not " ++ v ++ "\"" ++ more ++ "}"
def items : Env := envOf "{\"item\": {\"description\": \"item\"}}" ("{\"accepted\": " ++ u "accepted" ++
  ", \"admitted\": " ++ u "admitted" ", \"regulated\": {\"role\": \"plain\", \"default\": \"deny\"}" ++
  ", \"approved\": " ++ u "approved" ++ "}")
def LIs := lexOf [("item", "item")] [("item", "T")] (["accepted", "admitted", "approved"].map fun v => (v, "{0} is " ++ v))
  (["accepted", "admitted", "approved"].map fun v => (v, "{0} is not " ++ v))
#guard clauses (rd items LIs "Rule 1. Every item is not admitted.") == some [⟨.every "item", .plain false, .strict, "admitted", [], .top, [], []⟩]
#guard clauses (rd items LIs "Rule 1. Every item is admitted.") == some [⟨.every "item", .plain true, .strict, "admitted", [], .top, [], []⟩]
#guard outcome (rd items LIs "Rule 1. Every item is not approved.") == "stopped 1 noDerivation"
-- `over`: a rule's own targets, then its precedence lines, wherever they stand in the text
def overs (o : NormOutcome) : Option (List (List String)) := (nodes o).toOption.map (·.map (·.over))
#guard overs (rd act LA f8) == some [[], [], ["rule-1", "rule-2"]]
#guard overs (rd act LA ("Rule 1 takes precedence over rule 2.\nRule 1. Every act must not be done.\nRule 2. Every act must " ++
  "not be done.\nRule 3 (exception to rule 2). Every act may be done.")) == some [["rule-2"], [], ["rule-2"]]
#guard overs (rd act LA "Rule 1 (exception to rule 2). Every act may be done.\nRule 2. Every act must not be done.") ==
  some [["rule-2"], []]
-- the header's targets come before the precedence lines', each in text order (`norm_english.py:323`); the differential
-- is `test_lean_orders_over_as_python`
#guard (statements [hd 1, may, hd 2, may, hd 3 [2], may, .precedence 3 1]).map (overOf · 3) == some [2, 1]
#guard overs (rd act LA ("Rule 1. Every act must not be done.\nRule 2. Every act must not be done.\nRule 3. Every act must " ++
  "not be done.\nRule 4 (exception to rules 3 and 1). Every act may be done.\nRule 4 takes precedence over rule 2.")) ==
  some [[], [], [], ["rule-3", "rule-1", "rule-2"]]
-- no norm sentence is marked (`normMeaning_unmarked`, on the pieces `readNorm` assembles)
def marks (E : Env) (L : Lexicon) (s : String) : Option (List Bool) :=
  match lex s with
  | .ok ws => match VE.Grammar.readDocument (normGrammar E L) (normMeaning (normGrammar E L) (normActs E L)) NState.init workBudget
      ws.toList with
    | (.ok ps, _) => some (ps.map (·.2))
    | _ => none
  | .error _ => none
#guard marks two L2 f11 == some (List.replicate 6 false) && marks two L2 "Rule 1." == some [false]
#guard marks two L2 "Rule 1. Every act should be done." == none
-- `acts@0`: the regulated declarations are decoded as the norms route decodes them (`acts := true`)
def actsAct : Env := envOf actSorts permitted (soft := ", \"acts\": {\"fixed\": []}") (first := "\"acts@0\", ")
#guard (regulatedOf actsAct).map (·.name) == ["permitted"] && clauses (rd actsAct LA "Rule 1. Every act may be done.") == some [cl .may]
#guard (regulatedOf (envOf actSorts permitted (soft := ", \"acts\": {\"fixed\": []}"))).isEmpty
-- f19 and a zero budget: nothing is read.
#guard outcome (rd act LA "") == "lexical VE.EnglishGrammar.Reject.emptyDocument"
#guard outcome (readNorm act {} LA 0 "Rule 1. Every act may be done.") == "stopped 0 budget"
-- an invalid lexicon refuses before reading
#guard outcome (rd act (lexOf [] [] []) "Rule 1. Every act may be done.") == "invalidGrammar VE.EnglishGrammar.GrammarFault.lexicon"
-- `authored` refuses a clause the environment does not regulate, or one that is not W1's
#guard !authored act (.ok [.rule ⟨1, []⟩ { cl .may with pred := "required" }]) && !authored act (.ok [.rule ⟨1, []⟩ (cl .must)])
#guard !authored act (.ok [.rule ⟨1, []⟩ { cl .may with mode := .default "d" }]) && !authored act (.ok [.source [cl .may]])

-- f20, f21 at the node level: the clauses of the RSP blocks f6-maintain, f8-public and f10-in-line and of the
-- constitution's u0125.s04.p2, against their recorded nodes (`tests/data/norm-blocks/rsp.jsonl`, route-cases).
def situation (p : String) (f : Polarity) (g : EFormula := .top) (s := "situation") : List Piece :=
  [hd 1, .clause ⟨.every s, f, .strict, p, [], g, [], []⟩]

/-- Lean's nodes of a piece list: `assemble`, then `toNodes`. -/
def lean (ps : List Piece) : Except String (List VE.Norms.Node) :=
  match assemble ps with
  | .ok rs => toNodes rs
  | .error f => throw (reprStr f)

def f8Public := "[{\"guard\": [\"unary\", \"publicly_deployed\", [\"var\", 0]], \"name\": \"rule-1\", \"over\": [], \"predicate\": \"in_scope\", \"sign\": true, \"unless\": []}]"
#guard same (lean (situation "in_scope" (.plain true) (.pred "publicly_deployed" [.var 0]))) (python f8Public)
#guard !same (lean (situation "in_scope" (.plain false) (.pred "publicly_deployed" [.var 0]))) (python f8Public)
def f21Python := "[{\"name\": \"rule-1\", \"predicate\": \"denial_of_being_claude_permitted\", \"sign\": false, \"guard\": [\"top\"], \"unless\": [], \"over\": []}]"
#guard same (lean (situation "denial_of_being_claude_permitted" (.modal .mustNot) (s := "claude_instance"))) (python f21Python)
#guard !same (lean (situation "denial_of_being_claude_permitted" (.modal .may) (s := "claude_instance"))) (python f21Python)

/-- A long well-formed block: a header, its clause and `k` except-when sentences. `assemble` reads each piece
once, by structural recursion on the list; the node's guard and carve-outs are charged against the decoder's one
budget, `VE.Limits.maxNodes` = 10000 nodes (`decodeNorm`): the guard costs 1 and each carve-out 2, so 4999
carve-outs end within it and 5000 give `ResourceLimit`. -/
def long (k : Nat) : List Piece := hd 1 :: may :: List.replicate k (.exceptWhen a)

#guard (statements (long 5000)).map (·.flatMap (·.clauses.map (·.carveOuts.length))) == some [5000]
#guard faultOf (long 5000 ++ [hd 2]) == some (.noConsequence 5002)
#guard (lean (long 4999)).toOption.map (·.map (·.carveOuts.length)) == some [4999]
#guard match lean (long 5000) with
  | .error e => e == "ResourceLimit: AST exceeds depth or node budget"
  | .ok _ => false

end VE.EnglishGrammar.Norm.Examples
