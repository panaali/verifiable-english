import Lean.Data.Json

/-! Scope's authoring wordings (docs/spec/scope.md 2.2, 5.8 and 8.1; SC-7): a writer types one of 2.2's wordings, and
    `Pinned.parseGovernor` gives the part of the scope@0 block (spec 3) the wording fixes; `Pinned.renderGovernor`
    writes the wording back, and `Pinned.paraphrase` gives 2.2's one reading for the IDE to show.

    A parsed block holds what the wording says and nothing the layout decides: the reach in spec 3's form where the
    wording names it (`{"list_name": n}`, `"frontier"`), otherwise what the wording says of it (`"list"`: the list this
    line leads; `{"anchor": {"heading": h, "level": k}}`: the section this heading opens; `{"anchor": {"section": s}}`:
    the section the wording numbers), and each condition or rule the English reader has still to read as
    `{"english": text}` at its place. Unit and anchor ids and the readings of those texts are the IDE's (sc-7b).

    Only 2.2's wordings are accepted, with no spacing or spelling variant (english-lean ruling 1): a wording is read
    by every row, and accepted only when exactly one row's block renders back to the same bytes; two readings are
    refused, never chosen. The list name, the condition, the rule, the section and the heading are the slots; every
    other word is fixed. -/

namespace VE.Scope
open Lean

namespace Pinned

/-- Words with one space between them, no other whitespace, and at least one word. -/
def spaced (s : String) : Bool := (s.splitOn " ").all fun w => !w.isEmpty && w.all (!·.isWhitespace)

/-- A condition or a rule: spaced, and not itself ending a sentence or a lead-in. -/
def clause (s : String) : Bool := spaced s && !s.endsWith "." && !s.endsWith ":"

/-- A list name: "the" and at least one more word ("the hard constraints"). -/
def listName (n : String) : Bool := n.startsWith "the " && spaced n

/-- The list name at the start of a sentence, and back. -/
def cap (n : String) : String := "The" ++ n.drop 3
def uncap (h : String) : Option String := if h.startsWith "The " then some ("the" ++ h.drop 3) else none

def frameWording : String := "Every instance of Claude must not:"
/-- The condition of the "In place of" row (F3's): the attitude words of spec 3's `g2`. -/
def kindWording : String := "Claude knows that the act is of its kind, or thinks it quite likely that it is"

def english (s : String) : Json := Json.mkObj [("english", .str s)]
def narrowing (c : String) : Json := Json.mkObj [("reguard", Json.arr #[.str "and", .str "own", english c])]
def attitude (mode : String) (degree : Option String) : Json :=
  let holder := Json.arr #[.str "var", toJson (0 : Nat)]
  Json.mkObj [("attitude", match degree with
    | none => Json.mkObj [("holder", holder), ("mode", .str mode), ("content", .str "own")]
    | some d => Json.mkObj [("holder", holder), ("mode", .str mode), ("degree", .str d), ("content", .str "own")])]
/-- F3's condition, as spec 3's `g2` writes it. -/
def kindCondition : Json :=
  Json.arr #[.str "or", Json.arr #[.str "and", .str "own", attitude "knows" none], attitude "thinks" (some "quite likely")]
def frameBlock : Json := Json.mkObj [("reach", .str "list"), ("effect", Json.mkObj [("frame",
  Json.mkObj [("sign", .bool false), ("unless", Json.arr #[]), ("over", Json.arr #[])])])]
def onName (n : String) (effect : Json) : Json := Json.mkObj [("reach", Json.mkObj [("list_name", .str n)]), ("effect", effect)]
def heading (k : Nat) (h : String) (effect : Json) : Json :=
  Json.mkObj [("reach", Json.mkObj [("anchor", Json.mkObj [("heading", .str h), ("level", toJson k)])]), ("effect", effect)]

/-- 2.2's rows, each with its slots. -/
inductive Row where
  | frame | named (n : String) | narrowed (n c : String) | inPlace (n : String) | carved (n c : String)
  | precedes (s r : String) | whenHeading (k : Nat) (h c : String) | title (k : Nat) (h : String) | frontier (c : String)
  deriving Repr, DecidableEq

def textOf (j : Json) : String := j.getStr?.toOption.getD ""
def englishOf (j : Json) : String := textOf (j.getObjValD "english")
def narrowed? (e : Json) : Option String :=
  match e.getObjValD "reguard" with
  | .arr #[.str "and", .str "own", c] => some (englishOf c)
  | _ => none

/-- The row a block is written by. -/
def classify (b : Json) : Row :=
  let r := b.getObjValD "reach"
  let e := b.getObjValD "effect"
  let n := textOf (r.getObjValD "list_name")
  let a := r.getObjValD "anchor"
  let k := (a.getObjValD "level").getNat?.toOption.getD 0
  match b.getObjValD "list_name", r, a.getObjValD "section", a.getObjValD "heading" with
  | .str m, _, _, _ => .named m
  | _, .str "list", _, _ => .frame
  | _, .str "frontier", _, _ => .frontier ((narrowed? e).getD "")
  | _, _, .str s, _ => .precedes s (englishOf (b.getObjValD "rule"))
  | _, _, _, .str h => match narrowed? e with
    | some c => .whenHeading k h c
    | none => .title k h
  | _, _, _, _ =>
    if e.getObjValD "reguard" == kindCondition then .inPlace n
    else match narrowed? e with
    | some c => .narrowed n c
    | none => .carved n (englishOf (e.getObjValD "carve_out"))

/-- 2.2's wording of a row. -/
def Row.wording : Row → String
  | .frame => frameWording
  | .named n => s!"The rules below are called {n}."
  | .narrowed n c => s!"{cap n} apply only where {c}."
  | .inPlace n => s!"In place of their own condition, {n} apply only where {kindWording}."
  | .carved n c => s!"{cap n} do not apply when {c}."
  | .precedes s r => s!"Notwithstanding the rules of section {s}, {r}."
  | .whenHeading k h _ | .title k h => "".pushn '#' k ++ " " ++ h
  | .frontier c => s!"This applies only where {c}."

def renderGovernor (b : Json) : String := (classify b).wording

/-- What the paraphrase reads from the document, not the wording: the number of rules a list name covers, the default
    sentence of each rule's predicate (W1 2.5), the governor's own rule's name, and for a frontier reach the one
    candidate established to fit ("the rule above", "the list above"; SC-5), none for a question. -/
structure Context where
  count : Nat := 0
  defaults : String := ""
  rule : String := ""
  fits : Option String := none

/-- 2.2's right column: the one reading the IDE shows. -/
def Row.paraphrase (x : Context) : Row → String
  | .frame => s!"Each item below is its own rule: ‘{frameWording.dropRight 1} <item>.’"
  | .named n => s!"‘{cap n}’ names the rules of the list that follows."
  | .narrowed n c => s!"Each of the {x.count} rules called ‘{n}’ applies only where {c}."
  | .inPlace _ => s!"Each of the {x.count} rules now applies where {kindWording}, instead of where its own act occurs; " ++
      "its existing carve-outs still apply. ‘Its kind’ is each rule's own act."
  | .carved _ c => s!"None of the {x.count} rules applies when {c}; other rules may decide; if none does, {x.defaults}."
  | .precedes s _ => s!"Wherever {x.rule}, or a rule that takes precedence over it directly or through other rules, " ++
      s!"applies, no rule of section {s} decides on that act."
  | .whenHeading _ h c =>
    s!"Every rule in this section applies only {if h.startsWith "If " then "if" else "when"} {c}."
  | .title _ _ => "A title: it changes no rule."
  | .frontier _ => match x.fits with
    | some f => s!"This qualifies {f}."
    | none => "Which rule or list above does this qualify?"

def paraphrase (x : Context) (b : Json) : String := (classify b).paraphrase x

def between (w pre suf : String) : Option String :=
  (w.dropPrefix? pre).bind fun s => (s.toString.dropSuffix? suf).map (·.toString)
def splitOnce (w sep : String) : Option (String × String) :=
  match w.splitOn sep with
  | [a, b] => some (a, b)
  | _ => none

/-- A list-name row "<The name> <verb> <condition>.": the name and the condition. -/
def onList (w verb : String) : Option (String × String) := do
  let (h, rest) ← splitOnce w s!" {verb} "
  let n ← uncap h
  let c ← (rest.dropSuffix? ".").map (·.toString)
  if listName n && clause c then some (n, c) else none

/-- A heading of level 1 to 6: a full "When"/"If" clause narrows its section; any other heading is a title. A
    heading whose first word is "When" or "If" and whose rest is no clause is refused, never a title. -/
def readHeading (w : String) : Option Json := do
  let k := (w.takeWhile (· == '#')).length
  let h ← ((w.drop k).dropPrefix? " ").map (·.toString)
  if !(1 ≤ k && k ≤ 6 && spaced h) then none
  match h.splitOn " " with
  | first :: rest =>
    if first == "When" || first == "If" then
      let c := " ".intercalate rest
      if clause c then some (heading k h (narrowing c)) else none
    else some (heading k h (.str "title"))
  | [] => none

/-- Every row's block for `w`, before the rendering test. -/
def readings (w : String) : List Json :=
  [if w == frameWording then some frameBlock else none,
   (between w "The rules below are called " ".").bind fun n =>
     if listName n then some (Json.mkObj [("list_name", .str n)]) else none,
   (onList w "apply only where").bind fun (n, c) =>
     if (c.splitOn "its kind").length == 1 then some (onName n (narrowing c)) else none,
   (between w "In place of their own condition, " s!" apply only where {kindWording}.").bind fun n =>
     if listName n then some (onName n (Json.mkObj [("reguard", kindCondition)])) else none,
   (onList w "do not apply when").map fun (n, c) => onName n (Json.mkObj [("carve_out", english c)]),
   (between w "Notwithstanding the rules of section " ".").bind fun rest =>
     match rest.splitOn ", " with
     | s :: more => let r := ", ".intercalate more
       if !s.isEmpty && s.all (fun ch => !ch.isWhitespace && ch != ',') && clause r then
         some (Json.mkObj [("reach", Json.mkObj [("anchor", Json.mkObj [("section", .str s)])]),
           ("effect", .str "precedes"), ("rule", english r)])
       else none
     | [] => none,
   readHeading w,
   (between w "This applies only where " ".").bind fun c =>
     if clause c then some (Json.mkObj [("reach", .str "frontier"), ("effect", narrowing c)]) else none].filterMap id

/-- The block of an authoring wording: the one row's block that renders back to `w`, or none (not a wording of 2.2, or
    two readings). -/
def parseGovernor (w : String) : Option Json :=
  match (readings w).filter (renderGovernor · == w) with
  | [b] => some b
  | _ => none

end Pinned

theorem scope_parseRender (w : String) (b : Json) (h : Pinned.parseGovernor w = some b) :
    Pinned.renderGovernor b = w := by
  unfold Pinned.parseGovernor at h
  split at h
  · rename_i hf
    cases h
    have hm : b ∈(Pinned.readings w).filter (Pinned.renderGovernor · == w) := by rw [hf]; simp
    simpa using (List.mem_filter.mp hm).2
  · cases h

theorem scope_renderParse (w : String) (b : Json) (h : Pinned.parseGovernor w = some b) :
    Pinned.parseGovernor (Pinned.renderGovernor b) = some b := by
  rw [scope_parseRender w b h]
  exact h

end VE.Scope
