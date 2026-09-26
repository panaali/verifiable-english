import VE.English.Parse
import VE.English.Render
import VE.English.Check
import VE.Bridge

/-! # Differential runner for `conformance/english_lean.py`

Reads one JSON object `{"environment", "lexicon", "cases"}` and prints, for each
case, the Lean core parse of its tokens, the Lean core rendering of its
formulas, and whether that rendering parses back, together with the result of
the finite lexical check `admissible` (when it holds, `checked_parse_render`
proves every such rendering parses back). Run from `lean/` after
`lake build`:

    lake env lean --run VE/English/Run.lean cases.json

Tokens are JSON strings (words) or `[letter, index]` pairs (labels); template
slots are strings (words) or natural numbers (placeholders); formulas use the
indexed wire form decoded by `VE.Bridge.decodeFormula`. This file is a harness
entry point only; no theorem depends on it. -/
namespace VE.English.Run
open Lean

def decodeTok (j : Json) : Except String Tok :=
  match j with
  | .str w => pure (.word w)
  | _ => do
    match (← j.getArr?).toList with
    | [.str c, n] => pure (.label c (← n.getNat?))
    | _ => throw "invalid token"

def encodeTok : Tok → Json
  | .word w => .str w
  | .label c k => .arr #[.str c, toJson k]

def decodeSlot (j : Json) : Except String Slot :=
  match j with
  | .str w => pure (.word w)
  | _ => do pure (.hole (← j.getNat?))

def strings (j : Json) : Except String (List String) := do
  (← j.getArr?).toList.mapM fun s => s.getStr?

def entries (j : Json) : Except String (List (String × Json)) := do
  return (← j.getObj?).toList

def lookupD {α : Type} (xs : List (String × α)) (d : α) (k : String) : α :=
  (xs.find? (·.1 == k)).map (·.2) |>.getD d

def lookupO {α : Type} (xs : List (String × α)) (k : String) : Option α :=
  (xs.find? (·.1 == k)).map (·.2)

/-- `{"sorts": {s: {"noun": [...], "letter": L}}, "predicates": {p: [slot...]},
"constants": {c: [...]}}` -/
def decodeLexicon (j : Json) : Except String Lexicon := do
  let sorts ← entries (← j.getObjVal? "sorts")
  let nouns ← sorts.mapM fun (s, e) => do pure (s, ← strings (← e.getObjVal? "noun"))
  let letters ← sorts.mapM fun (s, e) => do pure (s, ← (← e.getObjVal? "letter").getStr?)
  let preds ← entries (← j.getObjVal? "predicates")
  let templates ← preds.mapM fun (p, e) => do pure (p, ← (← e.getArr?).toList.mapM decodeSlot)
  let consts ← entries (← j.getObjVal? "constants")
  let spellings ← consts.mapM fun (c, e) => do pure (c, ← strings e)
  pure { sorts := nouns.map (·.1), noun := lookupD nouns [], letter := lookupD letters ""
         predicates := templates.map (·.1), template := lookupO templates
         constants := spellings.map (·.1), spelling := lookupD spellings [] }

/-- `{"sorts": [...], "predicates": {p: [sort...]}, "constants": {c: sort}}` -/
def decodeEnvironment (j : Json) : Except String Environment := do
  let sorts ← strings (← j.getObjVal? "sorts")
  let preds ← (← entries (← j.getObjVal? "predicates")).mapM fun (p, e) => do pure (p, ← strings e)
  let consts ← (← entries (← j.getObjVal? "constants")).mapM fun (c, e) => do pure (c, ← e.getStr?)
  pure { sorts := sorts, predicates := lookupO preds, constants := lookupO consts }

def encodeTerm : Term → Json
  | .var i => .arr #[.str "var", toJson i]
  | .const c => .arr #[.str "const", .str c]

def encodeFormula : Formula → Json
  | .top => .arr #[.str "top"]
  | .bottom => .arr #[.str "bottom"]
  | .unary p t => .arr #[.str "unary", .str p, encodeTerm t]
  | .binary p t u => .arr #[.str "binary", .str p, encodeTerm t, encodeTerm u]
  | .eq t u => .arr #[.str "eq", encodeTerm t, encodeTerm u]
  | .not a => .arr #[.str "not", encodeFormula a]
  | .and a b => .arr #[.str "and", encodeFormula a, encodeFormula b]
  | .or a b => .arr #[.str "or", encodeFormula a, encodeFormula b]
  | .implies a b => .arr #[.str "implies", encodeFormula a, encodeFormula b]
  | .all s a => .arr #[.str "forall", .str s, encodeFormula a]
  | .ex s a => .arr #[.str "exists", .str s, encodeFormula a]

/-- Decide `Covers L E` over the finite environment entries in the runner input. -/
def covers (L : Lexicon) (j : Json) : Except String Bool := do
  let sorts ← strings (← j.getObjVal? "sorts")
  let preds ← (← entries (← j.getObjVal? "predicates")).mapM fun (p, e) => do
    pure (p, ← strings e)
  let consts ← entries (← j.getObjVal? "constants")
  pure <| sorts.all (L.sorts.contains ·) &&
    consts.all (fun (c, _) => L.constants.contains c) &&
    preds.all (fun (p, ss) =>
      match L.template p with
      | none => false
      | some T => L.predicates.contains p && T.arity == ss.length &&
          (List.range ss.length).all (fun i => T.contains (.hole i)))

def runCase (E : Environment) (L : Lexicon) (j : Json) : Except String Json := do
  let tokens ← (← (← j.getObjVal? "tokens").getArr?).toList.mapM decodeTok
  let formulas ← (← (← j.getObjVal? "formulas").getArr?).toList.mapM (Bridge.decodeFormula 64)
  let parsed := match parse E L tokens with
    | some fs => Json.arr (fs.map encodeFormula).toArray
    | none => Json.null
  let checked := !formulas.isEmpty && formulas.all (fun A => A.check E [])
  let rendered := render L formulas
  pure <| Json.mkObj [
    ("parsed", parsed),
    ("checked", .bool checked),
    ("rendered", if checked then Json.arr (rendered.map encodeTok).toArray else Json.null),
    ("roundtrip", .bool (checked && parse E L rendered == some formulas))]

def run (input : String) : Except String Json := do
  let j ← Json.parse input
  let envJson ← j.getObjVal? "environment"
  let E ← decodeEnvironment envJson
  let L ← decodeLexicon (← j.getObjVal? "lexicon")
  let cases ← (← j.getObjVal? "cases").getArr?
  let results ← cases.mapM (runCase E L)
  pure <| Json.mkObj [("admissible", .bool (admissible L)),
                     ("covers", .bool (← covers L envJson)), ("results", .arr results)]

end VE.English.Run

def main (args : List String) : IO UInt32 := do
  let input ← match args with
    | [path] => IO.FS.readFile path
    | _ => (← IO.getStdin).readToEnd
  match VE.English.Run.run input with
  | .ok j => IO.println j.compress; return 0
  | .error e => IO.eprintln e; return 2
