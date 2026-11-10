import VE.Presupposition.Admit
import VE.English.Render
import VE.English.Parse
import VE.English.Check
import VE.Presupposition.Examples

/-! # The presupposition report (docs/spec/presupposition.md 4.7 "Where the report goes", 2.3, 5; plan PS-2a)

The value the Lean document mode's answer carries as its `presuppositions` field (plan PS-4; DRI PS-C9: no service
mode, no runner and no schema of its own). It is read off `admit`'s answer, never recomputed. `admit` decides the
block as a whole and answers its first failing step, so the outcome is the block's: checked, refused with the
diagnostic, or `ResourceLimit: presuppositions`, UNKNOWN and never a refusal (spec 5). Not every refusal names the
obligation at fault: steps 2 and 4 do; steps 3 and 5 name the unit's or rule's first obligation, the tree check the
block's first rule act, else its first obligation, else none (an empty block: `PresuppositionMismatch: : rule`); step
5's readings refusals (`needsModelText`, `notSeparatedText`, `softText`) name no obligation and no unit (guards below).
An admitted block gives one row per obligation in the block's order: id, unit, carrier, the regenerated goal with its
English line, and for an unresolved obligation the readings its unit carries with their aliases. Then the
`PresuppositionRefuted` lines (2.3) the existing inconsistency report gives.

Limits, charged before the work: the block (`maxObligations`) and each goal (W1's nodes) in `admit`; a refused block
is not walked. The lexicon once per report (`lexiconOk`: `maxLexicon` entries, templates of at most two places,
then `VE.English.admissible`); each goal against `maxLineNodes` before it is rendered and parsed back. -/

namespace VE.Presupposition

/-- The block's outcome: admitted, refused with `admit`'s diagnostic, or over a limit (UNKNOWN). -/
inductive Outcome where
  | checked
  | refused (diagnostic : String)
  | unknown (diagnostic : String)
  deriving DecidableEq, Repr

/-- A goal's English line: shown; not shown, because the lexicon is not admissible or the sentence does not parse back
    to exactly the goal; or UNKNOWN, because the goal or the lexicon is over its limit. -/
inductive Line where
  | shown (text : String)
  | notShown
  | unknown
  deriving DecidableEq, Repr

/-- A regenerated goal: the formula (PS-4 encodes it in P0's wire form) and its English line. -/
structure Goal where
  formula : VE.Formula
  english : Line
  deriving DecidableEq, Repr

/-- One admitted obligation's row. `readings` is the unit's open set for an unresolved obligation, in the unit's
    order, each with its aliases (R-1), and empty otherwise. -/
structure Row where
  id : String
  unit : String
  carrier : Carrier
  goal : Goal
  readings : List RReading
  deriving DecidableEq, Repr

/-- The `presuppositions` field: the outcome, the rows of an admitted block in block order (none when refused), and
    the `PresuppositionRefuted` lines. -/
structure Shown where
  outcome : Outcome
  rows : List Row
  refuted : List String
  deriving DecidableEq, Repr

/-- The existing inconsistency report (P0's `INCONSISTENT`): the checked premise list and a certificate of `⊥` on it. -/
structure Inconsistency where
  premises : List VE.Formula
  cert : VE.Tableau.Certificate

/-- The lexicon's limits: entries, and the parser's work, which enumerates `pool ^ arity` tuples per template. -/
def maxLexicon : Nat := 512
def maxLineNodes : Nat := 200

/-- Checked once per report: none (UNKNOWN) over `maxLexicon` entries or with a template of more than two places
    (a formula's atoms have one or two); else whether the lexicon is admissible, the hypothesis of the core
    renderer's round trip and unique reading (`checked_parse_render`, lean/VE/English/Proofs.lean). -/
def lexiconOk (L : VE.English.Lexicon) : Option Bool :=
  if L.sorts.length + L.predicates.length + L.constants.length ≤ maxLexicon &&
      L.predicates.all (fun p => ((L.template p).map (fun T => decide (T.arity ≤ 2))).getD true) then
    some (VE.English.admissible L)
  else none

/-- A clause's tokens as one line: separated by spaces, punctuation attached to the word before it. -/
def lineOf (ts : List VE.English.Tok) : String :=
  ts.foldl (fun s t => match t with
    | .word w => if s.isEmpty then w else if [",", ";", ":", "."].contains w then s ++ w else s ++ " " ++ w
    | .label l i => (if s.isEmpty then "" else s ++ " ") ++ l ++ toString i) ""

/-- The goal's English line under the lexicon `L` (`ok` is `lexiconOk L`): the core renderer's clause, without the
    full stop so that 2.3's lines can quote it ("Assumed (from ‘…’): <goal>."), shown only when the sentence parses
    back, in the document's environment `E`, to exactly the goal. The goal is charged against `maxLineNodes` first. -/
def englishLine (E : VE.Environment) (L : VE.English.Lexicon) (ok : Option Bool) (A : VE.Formula) : Line :=
  match ok with
  | none => .unknown
  | some false => .notShown
  | some true =>
    if VE.Bridge.formulaNodes A ≤ maxLineNodes then
      let ts := (VE.English.renderStatement L A).yield L 0
      if VE.English.parse E L (ts ++ [.word "."]) == some [A] then .shown (lineOf ts) else .notShown
    else .unknown

def outcomeOf (e : String) : Outcome := if e == budget then .unknown e else .refused e

def checkedRow (L : VE.English.Lexicon) (ok : Option Bool) (D : PDoc) (c : Checked) : Row :=
  { id := c.ob.id, unit := c.ob.unit, carrier := c.ob.carrier, goal := ⟨c.goal, englishLine (env D) L ok c.goal⟩,
    readings := if c.ob.carrier == .unresolved then (unitReadings D c.ob.unit).getD [] else [] }

/-- A premise of `D`: a declared background formula or the content of an asserted claim unit. -/
def docPremise (D : PDoc) (a : VE.Formula) : Bool :=
  D.background.contains a || D.units.any (fun x => x.asserted && x.content == .claim a)

/-- 2.3: when the report's premises are `D`'s and its certificate checks, `PresuppositionRefuted: <o>: <unit>` for
    each assumed obligation whose goal the refutation uses: a premise equal to the goal, and the certificate no
    longer checks with those premises replaced by `⊤`. The other premises then refute the goal. Block order. -/
def refutedLines (D : PDoc) (R : Report) : Option Inconsistency → List String
  | none => []
  | some i =>
    let refutes (ps : List VE.Formula) := VE.Tableau.checkCertificate (env D) ps .bottom i.cert
    if i.premises.all (docPremise D) && refutes i.premises then
      R.checked.filterMap (fun c => match c.ob.carrier with
        | .assumed u =>
          if i.premises.contains c.goal && !refutes (i.premises.map (fun p => if p == c.goal then .top else p)) then
            some s!"PresuppositionRefuted: {c.ob.id}: {u}"
          else none
        | _ => none)
    else []

/-- The field from `admit`'s answer `a` on `D`: absent without the block (as `admitWrapped`). -/
def shownOf (L : VE.English.Lexicon) (inc : Option Inconsistency) (D : PDoc) (a : Except String Report) :
    Option Shown :=
  D.block.map (fun _ => match a with
    | .ok R => let ok := lexiconOk L; ⟨.checked, R.checked.map (checkedRow L ok D), refutedLines D R inc⟩
    | .error e => ⟨outcomeOf e, [], []⟩)

/-- The field PS-4 puts in the document mode's answer, on `admit`. -/
def shown (L : VE.English.Lexicon) (inc : Option Inconsistency) (D : PDoc) : Option Shown :=
  shownOf L inc D (admit D)

end VE.Presupposition

/-! ## Guards over spec 7.3's admission fixtures A1-A28 (`VE.Presupposition.Examples`) -/

namespace VE.Presupposition.RunExamples
open VE.Presupposition VE.Presupposition.Examples

/-- A fixture lexicon over `envA`'s words: admissible. -/
def lexA : VE.English.Lexicon :=
  { sorts := ["entity"], noun := fun _ => ["entity"], letter := fun _ => "E",
    predicates := ["owner", "ready", "manager", "trusts", "core_value_of"],
    template := fun p => match p with
      | "owner" => some [.hole 0, .word "is", .word "an", .word "owner"]
      | "ready" => some [.hole 0, .word "is", .word "ready"]
      | "manager" => some [.hole 0, .word "is", .word "a", .word "manager"]
      | "trusts" => some [.hole 0, .word "trusts", .hole 1]
      | "core_value_of" => some [.hole 0, .word "is", .word "a", .word "core", .word "value", .word "of", .hole 1]
      | _ => none,
    constants := ["claude"], spelling := fun c => if c == "claude" then ["Claude"] else [] }
def rowsOf (s : Option Shown) : List Row := (s.map (·.rows)).getD []
def lineA (A : VE.Formula) : Line := englishLine envA lexA (lexiconOk lexA) A
def isShown : Line → Bool
  | .shown _ => true
  | _ => false

-- Rows in block order (A18b: two assumed obligations on one unit, admitted on `admit`); the reversed block gives the
-- reversed rows. Id, unit and carrier are the obligation's.
#guard (rowsOf (shown lexA none doc18b)).map (fun r => (r.id, r.unit, r.carrier)) ==
  [("p1", "u1", .assumed "u0"), ("p2", "u1", .assumed "u00")]
#guard (rowsOf (shown lexA none { doc18b with block := doc18b.block.map List.reverse })).map (·.id) == ["p2", "p1"]
-- outcome checked; readings only for an unresolved obligation
#guard (shown lexA none doc18b).map (·.outcome) == some .checked &&
  (rowsOf (shown lexA none doc18b)).map (·.readings) == [[], []]
-- goal: `admit`'s regenerated goal and its English line (A24: a heading assumed on its own unit, goal `pre`)
#guard rowsOf (shown lexA none (docH coreU (.assumed "u0013.presupposition"))) ==
  [⟨"p2", "u0013.presupposition", .assumed "u0013.presupposition",
    ⟨coreU, .shown "there is an entity such that that entity is a core value of Claude"⟩, []⟩]
#guard (rowsOf (shown lexA none doc18b)).map (·.goal.formula) ==
  ((admit doc18b).toOption.map (·.checked.map (·.goal))).getD []
-- the English line: punctuation attached, list labels and numbered entity labels kept (A1's goal, the owner exists)
#guard lexiconOk lexA == some true && lineA theOwnerU == .shown ("there is a first entity such that both of the " ++
  "following hold: (a) the first entity is an owner; (b) for every second entity, if the second entity is an " ++
  "owner, then the second entity is the same as the first entity")
#guard lineOf [.word "if", .label "E" 1, .word "is", .word "an", .word "owner", .word ",", .word "then", .word "."] ==
  "if E1 is an owner, then." && lineOf [.label "E" 2, .word "is", .word "ready"] == "E2 is ready"
-- one-letter words and labels first, a multi-letter label, a word that only starts with punctuation
#guard lineOf [.word "a", .word "b", .label "AB" 12, .word "c", .word ".net"] == "a b AB12 c .net" &&
  lineOf [.word "a", .label "E" 3] == "a E3"
-- not shown: a predicate without a wording (A18b's p2 without "manager"); a lexicon that words "ready" as "owner", or
-- "owner" as "ready", is not admissible, so no line is shown (the second would read "… is ready" for an owner)
def lexNoMgr : VE.English.Lexicon := { lexA with predicates := lexA.predicates.erase "manager" }
def lexClash : VE.English.Lexicon :=
  { lexA with template := fun p => lexA.template (if p == "ready" then "owner" else p) }
#guard (rowsOf (shown lexNoMgr none doc18b)).map (isShown ·.goal.english) == [true, false]
#guard (rowsOf (shown lexA none doc18b)).map (isShown ·.goal.english) == [true, true]
def lexClash2 : VE.English.Lexicon :=
  { lexA with template := fun p => lexA.template (if p == "owner" then "ready" else p) }
#guard lexiconOk lexClash == some false && englishLine envA lexClash (lexiconOk lexClash) theOwnerU == .notShown
#guard lexiconOk lexClash2 == some false && englishLine envA lexClash2 (lexiconOk lexClash2) theOwnerU == .notShown
-- UNKNOWN: a goal over `maxLineNodes` (191 and 203 nodes); a lexicon over `maxLexicon` or with a three-place template
def conj : Nat → VE.Formula
  | 0 => theOwnerU
  | n + 1 => .and theOwnerU (conj n)
#guard VE.Bridge.formulaNodes (conj 15) ≤ maxLineNodes && isShown (lineA (conj 15))
#guard VE.Bridge.formulaNodes (conj 16) > maxLineNodes && lineA (conj 16) == .unknown
-- exactly at the limit (200 nodes) and one over
def oc : VE.Formula := .unary "owner" (.const "claude")
def rc : VE.Formula := .unary "ready" (.const "claude")
#guard VE.Bridge.formulaNodes (.and (conj 15) (.and (.and oc rc) oc)) == maxLineNodes &&
  isShown (lineA (.and (conj 15) (.and (.and oc rc) oc))) &&
  VE.Bridge.formulaNodes (.and (conj 15) (.and oc (.and rc (.not oc)))) == maxLineNodes + 1 &&
  lineA (.and (conj 15) (.and oc (.and rc (.not oc)))) == .unknown
def lexBig : VE.English.Lexicon := { lexA with constants := (List.range 507).map toString }
def lex3 : VE.English.Lexicon :=
  { lexA with template := fun p => if p == "trusts" then some [.hole 0, .hole 1, .hole 2] else lexA.template p }
#guard lexiconOk { lexA with constants := (List.range 506).map toString } != none && lexiconOk lexBig == none &&
  lexiconOk lex3 == none && englishLine envA lexBig (lexiconOk lexBig) theOwnerU == .unknown
-- each list counts: 513 entries made of sorts, or of predicates; a three-place template first or last
def names (n : Nat) : List String := (List.range n).map (s!"n{·}")
#guard lexiconOk { lexA with sorts := lexA.sorts ++ names 505 } != none &&
  lexiconOk { lexA with sorts := lexA.sorts ++ names 506 } == none &&
  lexiconOk { lexA with predicates := lexA.predicates ++ names 505 } != none &&
  lexiconOk { lexA with predicates := lexA.predicates ++ names 506 } == none
def place3 (q : String) : VE.English.Lexicon :=
  { lexA with template := fun p => if p == q then some [.hole 0, .hole 1, .hole 2] else lexA.template p }
#guard lexiconOk (place3 "owner") == none && lexiconOk (place3 "core_value_of") == none
-- a predicate without a template is no limit: the lexicon is not admissible
#guard lexiconOk { lexA with template := fun p => if p == "ready" then none else lexA.template p } == some false
-- a refused block: its outcome is `admit`'s diagnostic and it has no rows (A20: assumed on its own unit; A18: p2 in
-- p1's restriction)
#guard shown lexA none (docA [cu "u1" theOwner] [pA (.assumed "u1")]) ==
  some ⟨.refused "PresuppositionAssumedUnit: p1: u1", [], []⟩
#guard shown lexA none (doc18 [0, 0]) == some ⟨.refused "PresuppositionPosition: p2", [], []⟩
-- A15: 257 obligations are UNKNOWN, never refused, and not walked; 256 on one unit give 256 rows with their lines
#guard shown lexA none (docA [cu "u0" theOwnerU, cu "u1" theOwner] (many 257)) ==
  some ⟨.unknown "ResourceLimit: presuppositions", [], []⟩
#guard (rowsOf (shown lexA none (docA [cu "u0" theOwnerU, cu "u1" theOwner] (many 256)))).map (·.goal.english) ==
  List.replicate 256 (lineA theOwnerU)
-- A17: without the block the field is absent
#guard (shown lexA none { docA1 with block := none }).isNone

-- Unresolved obligations: the unit's readings, each with its aliases. A1 (the fixture table): assumed, conditioned.
#guard (rowsOf (shownOf lexA none docA1 (admitWith fixtureTable fx1 docA1))).map (fun r => (r.carrier, r.readings)) ==
  [(.unresolved, [rdAs, rdCo])]
-- a proved heading obligation on A1's open unit carries no readings
def selfArgs : Args := { sort := some "entity", restriction := some (.eq (.var 0) (.var 0)) }
def pHd : Obligation := obA "p2" "u1" "plural" .heading selfArgs (.proved "d1")
def docHd : PDoc := { docA [⟨"u1", true, .readings [rdAs, rdCo]⟩] [pA .unresolved, pHd] (proofs := [("d1", certC)]) with
  background := [.ex "entity" (.eq (.var 0) (.var 0))] }
#guard (rowsOf (shownOf lexA none docHd (admitWith fixtureTable fx1 docHd))).map (fun r => (r.id, r.readings)) ==
  [("p1", [rdAs, rdCo]), ("p2", [])]
-- R-1: in place is an alias of the conditioned reading at a shallow frame. The fixture table's negated cell
-- [assumed, conditioned, in place] gives an open set that step 5 never admits: there `¬U` entails `B`, so the assumed
-- `B` and the conditioned `U → B` are equivalent and no situation separates them. A cell [conditioned, asserted, in
-- place] gives one it admits.
def readingsAt (t : CandidateTable) : List RReading :=
  ((admitWith t fxN (docA [cu "u1" (negF.plug theOwner)] [pA .inPlace (.path [0])])).toOption.bind
    (fun R => R.checked.head?.bind (expectedReadings t R))).getD []
def docNeg (t : CandidateTable) : PDoc := docA [⟨"u1", true, .readings (readingsAt t)⟩] [pA .unresolved (.path [0])]
#guard (readingsAt fixtureTable).map (fun r => (r.cand, r.aliases)) == [(.assumed, []), (.conditioned, [.inPlace])] &&
  [(0, 1), (1, 0)].all (fun (w, o) => errOf (admitWith fixtureTable ⟨.norms, [("u1", w, o, sitNo)]⟩
    (docNeg fixtureTable)) == notSeparatedText)
def tC : CandidateTable := fun _ pc =>
  if pc == .negated then [.conditioned, .asserted, .inPlace] else [.assumed, .conditioned]
#guard tableOk rowNames tC && errOf (admitWith tC ⟨.norms, [("u1", 0, 1, sitNo)]⟩ (docNeg tC)) == "admitted"
#guard (rowsOf (shownOf lexA none (docNeg tC) (admitWith tC ⟨.norms, [("u1", 0, 1, sitNo)]⟩ (docNeg tC)))).map
  (·.readings.map (fun r => (r.cand, r.aliases))) == [[(.conditioned, [.inPlace]), (.asserted, [])]]

-- PresuppositionRefuted (2.3). A18b with one more asserted unit: the inconsistency certificate on the document's
-- premises names each assumed obligation whose goal the refutation uses, in block order. None when the refutation does
-- not use the goal, a premise is not the document's, the certificate does not check, there is no report, the carrier
-- is not assumed, or the block is refused.
def certOf (t : VE.Tableau.Trace) : VE.Tableau.Certificate := { certC with trace := t }
def g1 : VE.Formula := rOut18b.pre
def g2 : VE.Formula := f18b.goal rIn18b.pre
def with18b (extra : List VE.Formula) (asserted := true) : PDoc :=
  { doc18b with units := doc18b.units ++ extra.zipIdx.map (fun (a, i) => cu s!"x{i}" a asserted) }
def premises18b (extra : List VE.Formula) : List VE.Formula := [g1, g2, rOut18b.strong] ++ extra
def refutedOf (D : PDoc) (ps : List VE.Formula) (t : VE.Tableau.Trace) : List String :=
  ((shown lexA (some ⟨ps, certOf t⟩) D).map (·.refuted)).getD []
-- ¬(g1 ∧ g2): both goals used
#guard refutedOf (with18b [.not (.and g1 g2)]) (premises18b [.not (.and g1 g2)])
  (.expand 3 none [.expand 5 none [.close, .close]]) ==
  ["PresuppositionRefuted: p1: u0", "PresuppositionRefuted: p2: u00"]
-- ¬g1: only p1's
#guard refutedOf (with18b [.not g1]) (premises18b [.not g1]) (.expand 3 none [.close]) ==
  ["PresuppositionRefuted: p1: u0"]
-- the premise from the declared background
#guard refutedOf { doc18b with background := [.not g1] } (.not g1 :: premises18b []) (.expand 0 none [.close]) ==
  ["PresuppositionRefuted: p1: u0"]
-- a contradiction that uses neither goal; a premise not in the document, or only in a unit that is not asserted; a
-- trace that does not close
#guard refutedOf (with18b [isOpen, .not isOpen]) (premises18b [isOpen, .not isOpen]) (.expand 4 none [.close]) == []
#guard refutedOf (with18b []) (premises18b [.not g1]) (.expand 3 none [.close]) == [] &&
  refutedOf (with18b [.not g1] false) (premises18b [.not g1]) (.expand 3 none [.close]) == [] &&
  refutedOf (with18b []) (.not g1 :: premises18b []) (.expand 0 none [.close]) == []
-- any order of the document's premises: the goal last; the background premise between two others
#guard refutedOf { doc18b with background := [.not g1] } [.not g1, g2, g1] (.expand 0 none [.close]) ==
  ["PresuppositionRefuted: p1: u0"] &&
  refutedOf { doc18b with background := [.top, .not g1, .top] } (.top :: .not g1 :: .top :: premises18b [])
    (.expand 1 none [.close]) == ["PresuppositionRefuted: p1: u0"]
#guard refutedOf (with18b [.not g1]) (premises18b [.not g1]) .close == [] &&
  (shown lexA none doc18b).map (·.refuted) == some []
-- a proved carrier (A8) and a refused block (A18) give none
#guard refutedOf (docA [cu "u0" theMgrU, cu "u1" theMgr, cu "x0" (.not theMgrU)] [pP "u1"] (proofs := [("d1", certC)]))
  [theMgrU, theMgr, .not theMgrU] (.expand 2 none [.close]) == []
#guard refutedOf { doc18 [0, 0] with units := (doc18 [0, 0]).units ++ [cu "x0" (.not g1)] }
  [rOut18.pre, .not rOut18.pre] (.expand 1 none [.close]) == []


-- What a refusal names (review F1). `refusal D a` is the refused field's diagnostic, whether it quotes an obligation id
-- of `D`'s block, and whether it quotes a unit id of `D` (each as `: <id>`); none unless refused with no rows.
def refusal (D : PDoc) (a : Except String Report) : Option (String × Bool × Bool) :=
  let quotes (e i : String) := (e.splitOn (": " ++ i)).length > 1
  (shownOf lexA none D a).bind (fun s => match s.outcome, s.rows, s.refuted with
    | .refused e, [], [] => some (e, (D.block.getD []).any (quotes e ·.id), D.units.any (quotes e ·.id))
    | _, _, _ => none)
def docEmpty : PDoc := docA [cu "u0" theOwnerU, cu "u1" theOwner] [] (tree7 [r7bad])
-- steps 2 and 4 name the obligation at fault (step 2: the second `p2`, not the block's first; A20 also its unit);
-- step 3 names the unit's first obligation (A11: p1 and p2 on u1)
#guard (fun D => refusal D (admit D) == some ("PresuppositionMismatch: p2: id", true, false)) (docA
  [cu "u0" theOwnerU, cu "u1" theOwner]
  [pA (.assumed "u0"), { pA (.assumed "u0") with id := "p2" }, { pA (.assumed "u0") with id := "p2" }])
#guard (fun D => refusal D (admitWith t16 fxN D) == some ("PresuppositionMismatch: p1: content", true, false))
  (docA [cu "u1" wrong16] obs16)
#guard refusal (docA [cu "u1" theOwner] [pA (.assumed "u1")]) (admit (docA [cu "u1" theOwner] [pA (.assumed "u1")])) ==
  some ("PresuppositionAssumedUnit: p1: u1", true, true)
#guard refusal (doc18 [0, 0]) (admit (doc18 [0, 0])) == some ("PresuppositionPosition: p2", true, false)
-- step 5's readings refusals name no obligation and no unit, though each block holds one: not separated (the review's
-- probe, `docNeg` holds p1), no distinguishing model (A1), and the soft chain's conditioned rule reading (A26)
#guard (docNeg fixtureTable).block.map (·.map (·.id)) == some ["p1"] &&
  refusal (docNeg fixtureTable) (admitWith fixtureTable ⟨.norms, [("u1", 0, 1, sitNo)]⟩ (docNeg fixtureTable)) ==
    some (notSeparatedText, false, false)
#guard docA1.block.map (·.map (·.id)) == some ["p1"] &&
  refusal docA1 (admitWith fixtureTable fxN docA1) == some (needsModelText, false, false)
#guard ((doc7u false ["p"]).block.map List.length).getD 0 > 0 &&
  refusal (doc7u false ["p"]) (admitWith fixtureTable (fx7 .soft) (doc7u false ["p"])) == some (softText, false, false)
-- step 5's tree check names the block's first obligation when no rule act exists, and none on an empty block
#guard refusal (docA [cu "u0" theOwnerU, cu "u1" theOwner] [pA (.assumed "u0")] (tree7 [r7bad]))
  (admit (docA [cu "u0" theOwnerU, cu "u1" theOwner] [pA (.assumed "u0")] (tree7 [r7bad]))) ==
  some ("PresuppositionMismatch: p1: rule", true, false)
#guard refusal docEmpty (admit docEmpty) == some ("PresuppositionMismatch: : rule", false, false)

end VE.Presupposition.RunExamples
