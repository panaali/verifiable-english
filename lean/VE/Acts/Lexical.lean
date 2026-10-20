import Lean.Data.Json
import VE.Acts.LexicalBase

/-! Lexical acts (docs/spec/act-phrases.md 1.1 to 1.3, 2.1, 4.2 and 4.3; batch AP-1).

Under `acts@0` an act phrase may be long (at most 400 bytes) and may hold declared **fixed phrases**: word groups,
possibly with *and*, *or*, *nor* or *for*, read as one token. `check` accepts an act with no join word or comma
outside a fixed phrase and returns its canonical string, which stays its identity and its meaning: such an act never
enters the act grammar. A plain predicate with an act is worded "{0} has the right …" or "{0} is entitled …".
-/

namespace VE.Acts.Lexical
open VE.Norms.Wire (actReserved words actWord scanSlots)

/-- A token of an act phrase (1.1): a word, a declared fixed phrase (its index), a slot `{i}`, or a comma. -/
inductive Tok | word (w : String) | fixed (i : Nat) | slot (i : Nat) | comma
  deriving DecidableEq, Repr

/-- Words an act may hold only inside a declared fixed phrase in AP-1, and in the grammar's join positions (1.2). -/
def joinWords : List String := ["and", "or", "nor", "for"]
/-- Words no act may hold, fixed phrases included: today's `actReserved` without the join words (1.2). -/
def clauseWords : List String := VE.Norms.Wire.actReserved.filter (fun w => !joinWords.contains w)

/-- The limits of 12: an act phrase's bytes, a fixed phrase's bytes, and the fixed phrases of a document. -/
def maxActBytes : Nat := 400
def maxPhraseBytes : Nat := 300
def maxPhrases : Nat := 128

/-- U+2019 read as `'` (1.1). -/
def fold (s : String) : String := String.mk (s.toList.map (fun c => if c.toNat == 0x2019 then '\'' else c))
/-- The canonical form of an act or a fixed phrase: folded, whitespace normalised as `canonicalAct` does. -/
def normal (s : String) : String := " ".intercalate (words (fold s))
/-- A word without its final comma. -/
def dropComma (w : String) : String := if w.endsWith "," then w.dropRight 1 else w

/-- A slot `{i}`: `{`, decimal digits and `}`. -/
def slotOf? (w : String) : Option Nat :=
  if w.length ≥ 3 && w.startsWith "{" && w.endsWith "}" then
    let d := (w.drop 1).dropRight 1
    if d.all Char.isDigit then some d.toNat! else none
  else none

/-- One piece between spaces: a slot or a word, then a comma if it ends with one; `"comma"` for a misplaced comma. -/
def pieceToks (p : String) : Except String (List Tok) :=
  let body := dropComma p
  if body.isEmpty || body.contains ',' then .error "comma"
  else
    let t := match slotOf? body with
      | some i => Tok.slot i
      | none => Tok.word body
    .ok (if p.endsWith "," then [t, Tok.comma] else [t])

/-- Words, slots and commas of a normal string (no fixed phrases); a comma must follow a word and precede one. -/
def rawLex (s : String) : Except String (List Tok) := do
  let tss ← ((s.splitOn " ").filter (· ≠ "")).mapM pieceToks
  let ts := tss.foldl (· ++ ·) []
  if ts.getLast? == some Tok.comma then throw "comma"
  pure ts

/-- A declared phrase's tokens, with the diagnostics of 1.1 conditions 2 to 4 (D-8 to D-13). -/
def phraseToks (p : String) : Except String (List Tok) := do
  let n := normal p
  if n.utf8ByteSize > maxPhraseBytes then throw s!"ResourceLimit: fixed phrase '{p}' is over {maxPhraseBytes} bytes"
  let ts ← match rawLex n with
    | .ok ts => pure ts
    | .error _ => throw s!"InvalidInput: fixed phrase '{p}' has a comma that does not follow a word"
  for t in ts do
    match t with
    | .slot _ => throw s!"InvalidInput: fixed phrase '{p}' holds a slot"
    | .word w =>
      unless actWord w do throw s!"InvalidInput: fixed phrase '{p}' has '{w}', which is not a word of letters"
      if clauseWords.contains w.toLower then throw s!"InvalidInput: fixed phrase '{p}' uses the clause word '{w}'"
    | _ => pure ()
  let nw := (ts.filter (fun t => match t with | .word _ => true | _ => false)).length
  unless nw ≥ 2 do throw s!"InvalidInput: fixed phrase '{p}' must hold two words or more"
  let edgeOk : Option Tok → Bool := fun
    | some (.word w) => !joinWords.contains w.toLower
    | _ => false
  unless edgeOk ts.head? && edgeOk ts.getLast? do
    throw s!"InvalidInput: fixed phrase '{p}' must begin and end with a word other than and, or, nor and for"
  pure ts

/-- `q` can start inside an occurrence of `p` (or at its start, for `p ≠ q`). -/
def clash (p q : List Tok) : Bool :=
  (List.range p.length).any (fun k =>
    let r := p.drop k
    (k != 0 || p != q) && (r.isPrefixOf q || q.isPrefixOf r))

/-- 1.1: the declared phrases' tokens, or the first diagnostic (D-7 to D-14). -/
def decodeFixed (fx : List String) : Except String (List (List Tok)) := do
  if fx.length > maxPhrases then throw s!"ResourceLimit: more than {maxPhrases} fixed phrases"
  let ps ← fx.mapM phraseToks
  for i in List.range ps.length do
    for j in List.range ps.length do
      let p := ps.getD i []
      let q := ps.getD j []
      if i < j ∧ p = q then throw s!"InvalidInput: fixed phrase '{fx.getD j ""}' is declared twice"
      if (i = j ∧ clash p p = true) ∨ (i ≠ j ∧ p ≠ q ∧ clash p q = true) then
        throw s!"InvalidInput: fixed phrases '{fx.getD i ""}' and '{fx.getD j ""}' overlap, or one holds the other"
  pure ps

def fixedOk (fx : List String) : Bool := (decodeFixed fx).isOk

/-- Every occurrence of a declared phrase becomes one `fixed` token (fuel: the length). -/
def group (ps : List (List Tok)) : Nat → List Tok → List Tok
  | 0, ts => ts
  | _ + 1, [] => []
  | n + 1, t :: rest =>
    match (List.range ps.length).find? (fun i => !(ps.getD i []).isEmpty && (ps.getD i []).isPrefixOf (t :: rest)) with
    | some i => .fixed i :: group ps n ((t :: rest).drop (ps.getD i []).length)
    | none => t :: group ps n rest

/-- The tokens of an act phrase under the declared fixed phrases. -/
def lex (fx : List String) (s : String) : Except String (List Tok) := do
  let ps ← decodeFixed fx
  let ts ← rawLex (normal s)
  pure (group ps ts.length ts)

/-- 1.3: AP-1 acceptance; the canonical act, or the diagnostic of 10 (D-1 to D-6, or `decodeFixed`'s). -/
def check (fx : List String) (name : String) (arity : Nat) (raw : Lean.Json) : Except String String := do
  let act := normal ((raw.getStr?).toOption.getD "")
  let (slots, replaced) := scanSlots act.toList
  let ws := words (String.mk replaced)
  unless act.startsWith "{0} " && slots == (List.range arity).map toString && ws.length ≥ 2 &&
      ws.all (fun w => actWord (dropComma w)) do
    throw s!"InvalidInput: invalid act phrase for {name}"
  unless act.utf8ByteSize ≤ maxActBytes do throw s!"ResourceLimit: act phrase for {name} is over {maxActBytes} bytes"
  if let some w := ws.find? (fun w => w != "slot" && clauseWords.contains (dropComma w).toLower) then
    throw s!"InvalidInput: act phrase for {name} uses the clause word '{dropComma w}'; write the condition in the rule's guard"
  let ts ← match lex fx act with
    | .ok ts => pure ts
    | .error e => if e == "comma" then throw s!"InvalidInput: act phrase for {name} ends with a comma" else throw e
  match ts.find? (fun t => match t with | .word w => joinWords.contains w.toLower | .comma => true | _ => false) with
  | some (.word w) => throw s!"InvalidInput: act phrase for {name} joins acts with '{w}' outside a fixed phrase"
  | some _ => throw s!"InvalidInput: act phrase for {name} has a comma outside a fixed phrase"
  | none => pure act

/-- The form of a plain predicate's act (2.1). -/
inductive Form | right | entitled
  deriving DecidableEq, Repr

def Form.text : Form → String
  | .right => "has the right"
  | .entitled => "is entitled"

def Form.ofText? (s : String) : Option Form :=
  if s == "has the right" then some .right else if s == "is entitled" then some .entitled else none

/-- The honest wording of a plain predicate with an act: "{0} has the right …" or "{0} is entitled …", then the act
after its `{0} ` (2.1). -/
def wording (f : Form) (act : String) : String := "{0} " ++ f.text ++ " " ++ act.drop 4

/-! ### Theorems (4.3) -/

/-- An accepted act's tokens hold no join word and no comma outside a fixed phrase. -/
theorem check_no_join {fx : List String} {name : String} {k : Nat} {raw : Lean.Json} {a : String}
    (hc : check fx name k raw = .ok a) {ts : List Tok} (hl : lex fx a = .ok ts) :
    ∀ t ∈ ts, (∀ w, t = .word w → joinWords.contains w.toLower = false) ∧ t ≠ .comma := by
  unfold check at hc
  simp only [bind, Except.bind, pure, Except.pure] at hc
  split at hc
  next =>
    split at hc
    next =>
      split at hc
      next => cases hc
      next =>
        split at hc
        next ts' hlex =>
          split at hc
          next => cases hc
          next => cases hc
          next hnone =>
            cases hc
            rw [hlex] at hl
            cases hl
            intro t ht
            have := List.find?_eq_none.mp hnone t ht
            cases t <;> simp_all
        next => split at hc <;> cases hc
    next => cases hc
  next => cases hc

end VE.Acts.Lexical
