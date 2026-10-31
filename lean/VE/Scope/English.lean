import VE.Scope.Govern

/-! Scope's provenance sentences (docs/spec/scope.md 2.3, SC-1c): one sentence per governor that contributes to a
    governed rule, from the table below. Lean owns the wording; Python prints it (SC-E2 may change the wording, never
    what a sentence names). A generated rule's sentence (the table's last row) is sc-1cb's. -/

namespace VE.Scope
open Lean

/-- What a sentence quotes: a governor unit's source text, read once per document by the runner (`Run.quotesOf`). -/
class Quotes where
  text : String → String

/-- 2.3's `<text>`: the first 12 words, then "…" when there are more. -/
def quote (s : String) : String :=
  let ws := (s.split Char.isWhitespace).filter (· ≠ "")
  " ".intercalate (ws.take 12) ++ (if ws.length > 12 then " …" else "")

/-- The lead-in of a list or list-name reach. -/
def leadOf (D : SDoc) : Reach → Option String
  | .list lead => some lead
  | .listName n => (D.listNames.find? (·.1.name == n)).map (·.2.1)
  | _ => none

/-- 2.3's `<where>`: where the governor `g` stands, seen from the governed unit `u`. -/
def whereOf (D : SDoc) (g : Governor) (u : String) : String :=
  if leadOf D g.reach == some g.unit then "the line above the list" else
  match g.reach with
  | .anchor _ => "the heading of this section"
  | .label _ => "the label of this item"
  | _ => if position D g.unit < position D u then "an earlier sentence" else "a later sentence"

/-- 2.3's `<cover>`, for a reach of `n` units. -/
def coverOf (g : Governor) (n : Nat) : String :=
  match g.reach with
  | .list _ | .listName _ => s!"all {n} items of this list"
  | _ => if n == 1 then "1 rule" else s!"{n} rules"

/-- 2.3's sentence for the governor `g` on the governed unit `u`, whose reach has `n` units; `name` reads a unit's
    rule name (a `yields` governor names its own rule). -/
def sentence [Quotes] (D : SDoc) (name : String → Option String) (u : String) (n : Nat) (g : Governor) : String :=
  let t := "\"" ++ Quotes.text g.unit ++ "\""
  match g.effect with
  | .frame _ => s!"The start of this rule comes from the line above the list, {t}."
  | .reguard _ => s!"Its condition comes from {whereOf D g u}, {t}, which covers {coverOf g n}."
  | .carveOut _ => s!"Its exception comes from {whereOf D g u}, {t}, which covers {coverOf g n}."
  | .precedes =>
    let over := match g.reach with
      | .rules ns => ", ".intercalate ns
      | _ => coverOf g n
    s!"It takes precedence over {over}; this comes from {t}."
  | .yields => s!"{(name g.unit).getD "Another rule"} takes precedence over it; this comes from {whereOf D g u}, {t}."
  | .title => s!"Its title comes from {whereOf D g u}, {t}."

end VE.Scope
