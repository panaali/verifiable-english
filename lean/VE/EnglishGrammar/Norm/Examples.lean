import VE.EnglishGrammar.Norm.Elab

/-! The en-s6 fixtures of docs/spec/english-lean-s6.md section 6, at the piece level (DRI decision
reviews/dri-decisions-20261101-en-s6.md item 1): the block faults of f13-f16 and f24, the `over` lists of f7 and f8,
and the nodes of f2, f7, f8, f20 and f21 against Python's. Each piece is the value spec 2.5 gives its sentence;
the reader that computes them from the text is en-s6b, whose fixtures read the same texts. Each check has an
accepting and a refusing side.

Python's nodes are `ve.norm_english.parse_english`'s `norm` objects: f2, f7, f8 and f21 recorded at 03edaf200
(f2, f7, f8 in `test_norm_english`'s `permission` environment, f21 in the constitution environment of
`tests/data/route-cases.jsonl`), f20 from `tests/data/norm-blocks/rsp.jsonl`. Both sides go through the one
decoder, `VE.Norms.Wire.decodeNorm`. -/

namespace VE.EnglishGrammar.Norm.Examples
open Lean VE.EnglishGrammar VE.EnglishGrammar.Norm

/-- A W1 clause over "Every <s>", as a consequence row gives it (spec 2.5). -/
def cl (p : String) (f : Polarity) (g : EFormula := .top) (u : List EFormula := []) (s : String := "act") :
    Clause :=
  ⟨.every s, f, .strict, p, [], g, u, []⟩

def hd (n : Nat) (refs : List Nat := []) : Piece := .header ⟨n, refs⟩

def may : Piece := .clause (cl "permitted" (.modal .may))
def mustNot : Piece := .clause (cl "permitted" (.modal .mustNot))

/-- Python's nodes (a JSON array of `norm` objects), through the one decoder. -/
def python (s : String) : Except String (List VE.Norms.Node) := do
  match ← Json.parse s with
  | .arr xs => xs.toList.mapM fun j => VE.Norms.Wire.decodeNorm (Json.mkObj [("norm", j)])
  | _ => throw "not an array"

/-- Lean's nodes of a piece list: `assemble`, then `toNodes`. -/
def lean (ps : List Piece) : Except String (List VE.Norms.Node) :=
  match assemble ps with
  | .ok rs => toNodes rs
  | .error f => throw (reprStr f)

def same (a b : Except String (List VE.Norms.Node)) : Bool :=
  match a, b with
  | .ok x, .ok y => x == y
  | _, _ => false

def faultOf (ps : List Piece) : Option BlockFault :=
  match assemble ps with
  | .ok _ => none
  | .error f => some f

def isOk (ps : List Piece) : Bool := (assemble ps).toBool

-- f13: `Rule 2. Every act may be done.` opens block 1 with the wrong number.
#guard faultOf [hd 2, may] == some (.expectedRule 0 1)
#guard isOk [hd 1, may]
-- f14: `Rule 1. … Rule 1 takes precedence over rule 3.`
#guard faultOf [hd 1, may, .precedence 1 3] == some (.unknownRule 3)
#guard isOk [hd 1, may, .precedence 1 1]
-- f15: `Rule 1. Rule 2. Every act may be done.`
#guard faultOf [hd 1, hd 2, may] == some (.noConsequence 0)
#guard isOk [hd 1, may, hd 2, may]
#guard faultOf [hd 1, may, hd 2] == some (.noConsequence 2)
-- f16: `Rule 1. Except when this holds in all cases.`
#guard faultOf [hd 1, .exceptWhen .top] == some (.strayCarveOut 1)
#guard (assemble [hd 1, may, .exceptWhen .top]).toOption ==
  some [.rule ⟨1, []⟩ (cl "permitted" (.modal .may) .top [.top])]
-- f24: `Rule 9 takes precedence over rule 1.` with no block; a reference to 0 is out of range too (spec 2.3).
#guard faultOf [.precedence 9 1] == some (.unknownRule 9)
#guard faultOf [hd 1, may, .precedence 1 0] == some (.unknownRule 0)
#guard faultOf [hd 1 [0], may] == some (.unknownRule 0)
-- a clause sentence outside a block, or a second one in a block
#guard faultOf [may] == some (.strayConsequence 0)
#guard faultOf [hd 1, may, mustNot] == some (.strayConsequence 2)
#guard faultOf [hd 1, may, .precedence 1 1, mustNot] == some (.strayConsequence 3)

-- f2: `Rule 1. No act may be done.`; permission, sign false.
def f2Python := "[{\"name\": \"rule-1\", \"predicate\": \"permitted\", \"sign\": false, \"guard\": [\"top\"], \"unless\": [], \"over\": []}]"
#guard same (lean [hd 1, mustNot]) (python f2Python)
#guard !same (lean [hd 1, may]) (python f2Python)
#guard !same (lean [hd 1, .clause (cl "permitted" (.modal .must))]) (python f2Python)
-- f21: u0125.s04.p2's block, `Rule 1. Every instance of Claude must not directly deny being Claude.`
def f21Python := "[{\"name\": \"rule-1\", \"predicate\": \"denial_of_being_claude_permitted\", \"sign\": false, \"guard\": [\"top\"], \"unless\": [], \"over\": []}]"
def f21 (f : Force) : List Piece :=
  [hd 1, .clause (cl "denial_of_being_claude_permitted" (.modal f) (s := "claude_instance"))]
#guard same (lean (f21 .mustNot)) (python f21Python)
#guard !same (lean (f21 .may)) (python f21Python)

-- f7: `Rule 1. Every act must not be done.` `Rule 2. Every act may be done.` `Rule 2 takes precedence over rule 1.`
def f7Python := "[{\"name\": \"rule-1\", \"predicate\": \"permitted\", \"sign\": false, \"guard\": [\"top\"], \"unless\": [], \"over\": []}, {\"name\": \"rule-2\", \"predicate\": \"permitted\", \"sign\": true, \"guard\": [\"top\"], \"unless\": [], \"over\": [\"rule-1\"]}]"
def f7 : List Piece := [hd 1, mustNot, hd 2, may, .precedence 2 1]
#guard (assemble f7).toOption.map (overOf · 2) == some [1]
#guard same (lean f7) (python f7Python)
#guard !same (lean [hd 1, mustNot, hd 2, may, .precedence 1 2]) (python f7Python)
#guard !same (lean [hd 1, mustNot, hd 2, may]) (python f7Python)
-- f8: rule 3 is an exception to rules 1 and 2, in that order.
def f8Python := "[{\"name\": \"rule-1\", \"predicate\": \"permitted\", \"sign\": false, \"guard\": [\"top\"], \"unless\": [], \"over\": []}, {\"name\": \"rule-2\", \"predicate\": \"permitted\", \"sign\": false, \"guard\": [\"top\"], \"unless\": [], \"over\": []}, {\"name\": \"rule-3\", \"predicate\": \"permitted\", \"sign\": true, \"guard\": [\"top\"], \"unless\": [], \"over\": [\"rule-1\", \"rule-2\"]}]"
def f8 (refs : List Nat) : List Piece := [hd 1, mustNot, hd 2, mustNot, hd 3 refs, may]
#guard (assemble (f8 [1, 2])).toOption.map (overOf · 3) == some [1, 2]
#guard same (lean (f8 [1, 2])) (python f8Python)
#guard !same (lean (f8 [2, 1])) (python f8Python)
#guard !same (lean (f8 [1])) (python f8Python)
-- the header's targets come before the precedence lines' (`norm_english.py:323`)
#guard (assemble [hd 1, may, hd 2, may, hd 3 [2], may, .precedence 3 1]).toOption.map (overOf · 3) == some [2, 1]

-- f20: the RSP blocks f6-maintain, f8-public (a plain role) and f10-in-line, against their recorded nodes.
def situation (p : String) (f : Polarity) (g : EFormula := .top) : List Piece :=
  [hd 1, .clause (cl p f g (s := "situation"))]
#guard same (lean (situation "roadmap_maintained" (.modal .must)))
  (python "[{\"guard\": [\"top\"], \"name\": \"rule-1\", \"over\": [], \"predicate\": \"roadmap_maintained\", \"sign\": true, \"unless\": []}]")
#guard !same (lean (situation "roadmap_maintained" (.modal .needNot)))
  (python "[{\"guard\": [\"top\"], \"name\": \"rule-1\", \"over\": [], \"predicate\": \"roadmap_maintained\", \"sign\": true, \"unless\": []}]")
def f8Public := "[{\"guard\": [\"unary\", \"publicly_deployed\", [\"var\", 0]], \"name\": \"rule-1\", \"over\": [], \"predicate\": \"in_scope\", \"sign\": true, \"unless\": []}]"
#guard same (lean (situation "in_scope" (.plain true) (.pred "publicly_deployed" [.var 0]))) (python f8Public)
#guard !same (lean (situation "in_scope" (.plain false) (.pred "publicly_deployed" [.var 0]))) (python f8Public)
#guard !same (lean (situation "in_scope" (.plain true) (.pred "publicly_deployed" [.var 1]))) (python f8Public)
def f10InLine := "[{\"guard\": [\"and\", [\"unary\", \"describes_mitigation_and_deviates\", [\"var\", 0]], [\"unary\", \"noteworthy\", [\"var\", 0]]], \"name\": \"rule-1\", \"over\": [], \"predicate\": \"deviation_reported\", \"sign\": true, \"unless\": []}]"
def deviates : EFormula := .pred "describes_mitigation_and_deviates" [.var 0]
def noteworthy : EFormula := .pred "noteworthy" [.var 0]
#guard same (lean (situation "deviation_reported" (.modal .must) (.and deviates noteworthy))) (python f10InLine)
#guard !same (lean (situation "deviation_reported" (.modal .must) (.and noteworthy deviates))) (python f10InLine)

-- Except-when sentences append their carve-outs in text order (f11's shape).
#guard (lean [hd 1, may, .exceptWhen deviates, .exceptWhen noteworthy]).toOption.map (·.map (·.carveOuts.length)) ==
  some [2]
#guard !same (lean [hd 1, may, .exceptWhen deviates, .exceptWhen noteworthy])
  (lean [hd 1, may, .exceptWhen noteworthy, .exceptWhen deviates])

/-- A long well-formed block: `k` except-when sentences of one atom each. Every piece is read once, and the
node's guard and carve-outs are charged against the decoder's one budget, `VE.Limits.maxNodes` = 10000 nodes
(`decodeNorm`): the guard costs 1 and each carve-out 2, so 4999 carve-outs end within it and 5000 do not. -/
def long (k : Nat) : List Piece := hd 1 :: may :: List.replicate k (.exceptWhen deviates)

#guard (lean (long 4999)).toOption.map (·.map (·.carveOuts.length)) == some [4999]
#guard match lean (long 5000) with
  | .error e => e == "ResourceLimit: AST exceeds depth or node budget"
  | .ok _ => false

end VE.EnglishGrammar.Norm.Examples
