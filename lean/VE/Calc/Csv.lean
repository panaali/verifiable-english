import VE.Calc.Table

/-! The CSV subset of spec 4.1: comma separator, double-quote quoting (a doubled quote inside), a header row, LF or
CRLF line ends. `csvRecords` reads in a mode with the current field and the record's earlier fields (both reversed)
after the records read (reversed). `columnTypes` gives the declared type of each header column: every header column
declared once, and every declared column present. -/

namespace VE.Calc

inductive CsvMode where
  | plain | quoted | closed
  deriving DecidableEq

def csvRecords : List Char → CsvMode → List Char → List String → List (List String) →
    Except String (List (List String))
  | [], .quoted, _, _, _ => .error "TableFormat: a quoted field is not closed"
  | [], m, cur, fs, rs => .ok (match m, cur, fs with | .plain, [], [] => rs.reverse | _, _, _ => (((String.mk cur.reverse :: fs).reverse :: rs).reverse))
  | '"' :: '"' :: cs, .quoted, cur, fs, rs => csvRecords cs .quoted ('"' :: cur) fs rs
  | '"' :: cs, .quoted, cur, fs, rs => csvRecords cs .closed cur fs rs
  | c :: cs, .quoted, cur, fs, rs => csvRecords cs .quoted (c :: cur) fs rs
  | ',' :: cs, _, cur, fs, rs => csvRecords cs .plain [] (String.mk cur.reverse :: fs) rs
  | '\n' :: cs, _, cur, fs, rs => csvRecords cs .plain [] [] ((String.mk cur.reverse :: fs).reverse :: rs)
  | '\r' :: '\n' :: cs, _, cur, fs, rs => csvRecords cs .plain [] [] ((String.mk cur.reverse :: fs).reverse :: rs)
  | '"' :: cs, .plain, [], fs, rs => csvRecords cs .quoted [] fs rs
  | c :: cs, .plain, cur, fs, rs =>
      if c = '"' ∨ c = '\r' then .error "TableFormat: a quote or carriage return inside an unquoted field"
      else csvRecords cs .plain (c :: cur) fs rs
  | _ :: _, .closed, _, _, _ => .error "TableFormat: a character after a closing quote"

def columnTypes (decl : List (String × ColType)) (header : List String) : Except String (List ColType) := do
  unless header.eraseDups.length = header.length do throw "TableFormat: a repeated column"
  if let some (c, _) := decl.find? (fun d => !header.contains d.1) then throw s!"TableFormat: no column {c}"
  header.mapM fun h => (decl.lookup h).elim (throw s!"TableFormat: an undeclared column {h}") pure

def decodeCsv (decl : List (String × ColType)) (bytes : ByteArray) : Except String Table := do
  let some text := String.fromUTF8? bytes | throw "TableFormat: the bytes are not UTF-8"
  let header :: rows ← csvRecords text.toList .plain [] [] [] | throw "TableFormat: no header row"
  tableDimensions decl.length rows.length
  let types ← columnTypes decl header
  let rows ← rows.mapM fun r =>
    if r.length = types.length then pure (types.zipWith readCell r) else throw "TableFormat: a row of the wrong length"
  pure ⟨header, rows⟩

end VE.Calc
