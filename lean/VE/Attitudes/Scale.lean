import VE.Closure.Order

/-! The likelihood scale of `attitudes@0` and its frozen table (docs/spec/attitudes.md section 2.1).
A word is admitted after "thinks it" only if E1's certainty item passed it; `table` records each
admitted entry with the pre-registered item that passed it (E1 and E2, 2026-10-13), and
`Table.reviewed` is its closure review. The closure is QS-1's `VE.Closure.Order.atLeast`, never a
second one (edit 1). -/

namespace VE.Attitudes

abbrev Word := String
/-- The id of the pre-registered E1 or E2 item that passed an entry, e.g. "E1.pair.very-likely.quite-likely". -/
abbrev Item := String

/-- `above` lists pairs `(a, b)` read "a is at least as likely as b". -/
structure Scale where
  words : List Word
  above : List (Word × Word)
  deriving DecidableEq, Repr

def Scale.toOrder (σ : Scale) : VE.Closure.Order Word := ⟨σ.words, σ.above⟩

/-- The reflexive and transitive closure of `above`: QS-1's, never a second closure. -/
def Scale.atLeast (σ : Scale) (a b : Word) : Bool := σ.toOrder.atLeast a b

/-- The frozen meaning of `attitudes@0`: each admitted entry with the item that passed it. -/
structure Table where
  /-- E1's words, in E1's order -/
  candidates : List Word
  /-- words whose certainty item passed (E1, at least 34 of 40): the only words admitted after "thinks it" -/
  lowerBound : List (Word × Item)
  /-- `(a, b, item)`: "a is at least as likely as b", passed by its own E1 or E2 item -/
  above : List (Word × Word × Item)
  /-- frame premise 1 (E2's three factivity items); `none`: `knows` is not admitted -/
  factive : Option Item
  /-- frame premise 2 (E2's three knows-believes items); `none`: no such premise -/
  knowsBelieves : Option Item
  /-- frame premise 3, per word (E2's per-word items); a word not listed gets no premise 3 of its own -/
  knowsThinks : List (Word × Item)
  deriving DecidableEq, Repr

def Table.words (t : Table) : List Word := t.lowerBound.map (·.1)
def Table.scale (t : Table) : Scale := ⟨t.words, t.above.map (fun p => (p.1, p.2.1))⟩
def Table.hasPair (t : Table) (a b : Word) : Bool := t.above.any (fun p => p.1 == a && p.2.1 == b)

/-- The closure review: the closure of the frozen pairs adds no pair, and no premise-3 word, without its own
    passing item; every entry is between admitted words; premises 2 and 3 need premise 1. -/
def Table.reviewed (t : Table) : Bool :=
  let ws := t.words
  t.candidates.length ≤ 8 &&
  ws.all t.candidates.contains &&
  t.above.all (fun p => ws.contains p.1 && ws.contains p.2.1) &&
  t.knowsThinks.all (fun p => ws.contains p.1) &&
  ws.all (fun a => ws.all (fun b => a == b || !t.scale.atLeast a b || t.hasPair a b)) &&
  t.knowsThinks.all (fun p => ws.all (fun w => !t.scale.atLeast p.1 w || t.knowsThinks.any (·.1 == w))) &&
  (t.factive.isSome || (t.knowsBelieves.isNone && t.knowsThinks.isEmpty))

def e1Words : List Word :=
  ["almost certain", "very likely", "quite likely", "likely", "more likely than not", "as likely as not",
    "unlikely", "very unlikely"]

/-- The frozen table: E1's and E2's outcomes (2026-10-13), each entry with the item that passed it. -/
def table : Table :=
  { candidates := e1Words,
    lowerBound := [("almost certain", "E1.cert.almost-certain"), ("very likely", "E1.cert.very-likely"),
      ("quite likely", "E1.cert.quite-likely"), ("likely", "E1.cert.likely"),
      ("more likely than not", "E1.cert.more-likely-than-not")],
    above := [("almost certain", "very likely", "E1.pair.almost-certain.very-likely"),
      ("almost certain", "quite likely", "E1.pair.almost-certain.quite-likely"),
      ("almost certain", "likely", "E1.pair.almost-certain.likely"),
      ("almost certain", "more likely than not", "E1.pair.almost-certain.more-likely-than-not"),
      ("very likely", "quite likely", "E1.pair.very-likely.quite-likely"),
      ("very likely", "likely", "E1.pair.very-likely.likely"),
      ("very likely", "more likely than not", "E1.pair.very-likely.more-likely-than-not"),
      ("quite likely", "likely", "E1.pair.quite-likely.likely"),
      ("quite likely", "more likely than not", "E1.pair.quite-likely.more-likely-than-not"),
      ("likely", "more likely than not", "E1.pair.likely.more-likely-than-not")],
    factive := some "E2.factive",
    knowsBelieves := some "E2.knows-believes",
    knowsThinks := [("almost certain", "E2.knows-thinks.almost-certain"), ("very likely", "E2.knows-thinks.very-likely"),
      ("quite likely", "E2.knows-thinks.quite-likely"), ("likely", "E2.knows-thinks.likely"),
      ("more likely than not", "E2.knows-thinks.more-likely-than-not")] }

/-- The bounds on a document's scale (A5): E1's eight words and 64 pairs, checked by QS-1's `Order.admit`. -/
def scaleCaps : VE.Closure.Caps := ⟨8, 64⟩

/-- The frozen table passes its closure review. -/
theorem table_reviewed : table.reviewed = true := by decide

#guard table.reviewed

end VE.Attitudes
