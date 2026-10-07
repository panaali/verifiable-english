import VE.Service.TypingDiagnostic
import VE.Surface

/-! Error reporting for rejected strict surface sources. The family surface
parsers decide acceptance. This walk runs only after rejection and names the
first lexical or grammar fault in source order, including its source span. -/
namespace VE.Service.ParseDiagnostic
open Lean

structure Error where
  code : String
  message : String
  start : Nat
  stop : Nat

structure Cursor where
  source : Array Char
  offset : Nat := 0
  binders : List String := []
  signature : VE.Service.TypingDiagnostic.Signature
  order : Bool
  closure : Bool
  nary : Bool
  nodes : Nat := 0

abbrev Scan := StateT Cursor (Except Error)

def fails {α : Type} (code message : String) (start : Option Nat := none) : Scan α := do
  let c ← get
  let p := start.getD c.offset
  throw ⟨code, message, p, min c.source.size (max (p + 1) c.offset)⟩

def current : Scan (Option Char) := do
  let c ← get
  pure c.source[c.offset]?

def hasPrefix (text : String) : Scan Bool := do
  let c ← get
  let mut i := c.offset
  for ch in text.toList do
    if c.source[i]? != some ch then return false
    i := i + 1
  return true

def advance (n : Nat) : Scan Unit := modify fun c => { c with offset := c.offset + n }

def pyQuote (s : String) : String :=
  "'" ++ (((s.replace "\\" "\\\\").replace "\n" "\\n").replace "\r" "\\r").replace "\t" "\\t" ++ "'"

def literal (text : String) : Scan Unit := do
  unless ← hasPrefix text do fails "SyntaxError" ("expected " ++ pyQuote text)
  advance text.length

def identChar (c : Char) : Bool :=
  (c ≥ 'a' && c ≤ 'z') || (c ≥ '0' && c ≤ '9') || c == '_'

def ident (role : String) : Scan (String × Nat) := do
  let c ← get
  let start := c.offset
  let some ch := c.source[start]? | fails "SyntaxError" ("expected " ++ role)
  unless ch ≥ 'a' && ch ≤ 'z' do fails "SyntaxError" ("expected " ++ role)
  let mut i := start + 1
  while (c.source[i]?.map identChar).getD false do i := i + 1
  let name := String.mk ((c.source.toList.drop start).take (i - start))
  advance (i - start)
  if name.length > 64 then fails "ResourceLimit" (role ++ " exceeds 64 ASCII bytes") (some start)
  pure (name, start)

def reserved : List String := VE.Surface.reserved

def numeral : Scan Unit := do
  let c ← get
  let start := c.offset
  if ← hasPrefix "-" then advance 1
  let c ← get
  let mut i := c.offset
  while (c.source[i]?.map fun x => x ≥ '0' && x ≤ '9').getD false do i := i + 1
  if i == c.offset then fails "SyntaxError" "expected an integer numeral"
  let digits := String.mk ((c.source.toList.drop c.offset).take (i - c.offset))
  advance (i - c.offset)
  if i - start > 40 then fails "ResourceLimit" "numeral exceeds 40 characters" (some start)
  if (digits.length > 1 && digits.startsWith "0") ||
      (digits == "0" && c.offset > start) then
    fails "SyntaxError" "non-canonical integer numeral" (some start)

def term : Nat → Scan Unit
  | 0 => fails "ResourceLimit" "term exceeds nesting limit 64"
  | fuel + 1 => do
    let c ← get
    if c.order then
      let some ch := c.source[c.offset]? | fails "SyntaxError" "expected term"
      if (ch ≥ '0' && ch ≤ '9') ||
          (ch == '-' && (c.source[c.offset + 1]?.map fun x => x ≥ '0' && x ≤ '9').getD false) then
        numeral
        return
      if ch == '-' then
        advance 1
        term fuel
        return
      if ch == '[' then
        let inner := c.source[c.offset + 1]?
        let coefficient := (inner.map fun x => x ≥ '0' && x ≤ '9').getD false ||
          (inner == some '-' && (c.source[c.offset + 2]?.map fun x => x ≥ '0' && x ≤ '9').getD false)
        advance 1
        term fuel
        if ← hasPrefix " * " then
          unless coefficient do
            fails "SyntaxError" "a scaling coefficient must be an integer numeral" (some c.offset)
          advance 3
        else if ← hasPrefix " + " then
          advance 3
        else if ← hasPrefix " - " then
          advance 3
        else fails "SyntaxError" "expected ' + ', ' - ' or ' * '"
        term fuel
        literal "]"
        return
    if ← hasPrefix "@" then
      advance 1
      let (name, pos) ← ident "constant identifier"
      unless (c.signature.constants.map Prod.fst).contains name do
        fails "UnknownSymbol" ("unknown constant " ++ pyQuote name) (some pos)
      return
    let (name, pos) ← ident "term"
    if reserved.contains name then
      fails "SyntaxError" ("reserved word " ++ pyQuote name ++ " cannot be a term") (some pos)
    unless c.binders.contains name do
      fails "UnboundVariable" ("unbound variable " ++ pyQuote name) (some pos)

def binder (role : String) : Scan String := do
  let (name, pos) ← ident role
  let c ← get
  if reserved.contains name || c.signature.sorts.contains name ||
      (c.signature.predicates.map Prod.fst).contains name ||
      (c.signature.constants.map Prod.fst).contains name then
    fails "SyntaxError" ("invalid binder name " ++ pyQuote name) (some pos)
  if c.binders.contains name then
    fails "ShadowedVariable" ("binder " ++ pyQuote name ++ " shadows an active binder") (some pos)
  pure name

def complete (start : Nat) : Scan Unit := do
  let c ← get
  if c.nodes ≥ 10000 then
    fails "ResourceLimit" "document exceeds 10000 AST nodes" (some start)
  modify fun state => { state with nodes := state.nodes + 1 }

def formula (depth : Nat) : Nat → Scan Unit
  | 0 => fails "ResourceLimit" "formula exceeds nesting limit 64"
  | fuel + 1 => do
    let c ← get
    if depth > 64 then fails "ResourceLimit" "formula exceeds nesting limit 64"
    if ← hasPrefix "true" then
      let next := c.source[c.offset + 4]?
      if !(next.map identChar).getD false then
        advance 4
        complete c.offset
        return
    if ← hasPrefix "false" then
      let next := c.source[c.offset + 5]?
      if !(next.map identChar).getD false then
        advance 5
        complete c.offset
        return
    if ← hasPrefix "not (" then
      advance 5
      formula (depth + 1) fuel
      literal ")"
      complete c.offset
      return
    if ← hasPrefix "if (" then
      advance 4
      formula (depth + 1) fuel
      literal "), then ("
      formula (depth + 1) fuel
      literal ")"
      complete c.offset
      return
    if (← hasPrefix "for every ") || (← hasPrefix "there exists ") then
      let universal ← hasPrefix "for every "
      advance (if universal then 10 else 13)
      let (sort, pos) ← ident "sort identifier"
      unless c.signature.sorts.contains sort do
        fails "UnknownSymbol" ("unknown sort " ++ pyQuote sort) (some pos)
      literal " "
      let name ← binder "binder name"
      literal ", ("
      modify fun state => { state with binders := name :: state.binders }
      formula (depth + 1) fuel
      modify fun state => { state with binders := state.binders.drop 1 }
      literal ")"
      complete c.offset
      return
    if c.closure && ((← hasPrefix "tc[") || (← hasPrefix "rtc[")) then
      advance (if ← hasPrefix "rtc[" then 4 else 3)
      let (name, pos) ← ident "closure relation or sort"
      if ← hasPrefix "]" then
        advance 1
        unless (c.signature.predicates.map Prod.fst).contains name do
          fails "UnknownSymbol" ("unknown closure relation " ++ pyQuote name) (some pos)
      else
        unless c.signature.sorts.contains name do
          fails "UnknownSymbol" ("unknown sort " ++ pyQuote name) (some pos)
        literal " "
        let src ← binder "closure binder"
        modify fun state => { state with binders := src :: state.binders }
        literal ", "
        let dst ← binder "closure binder"
        literal " | ("
        modify fun state => { state with binders := dst :: state.binders }
        formula (depth + 1) fuel
        modify fun state => { state with binders := state.binders.drop 2 }
        literal ")]"
      literal "("
      term (c.source.size + 1)
      literal ", "
      term (c.source.size + 1)
      literal ")"
      complete c.offset
      return
    if ← hasPrefix "(" then
      advance 1
      formula (depth + 1) fuel
      if ← hasPrefix ") and (" then advance 7
      else if ← hasPrefix ") or (" then advance 6
      else fails "SyntaxError" "expected ') and (' or ') or ('"
      formula (depth + 1) fuel
      literal ")"
      complete c.offset
      return
    if c.nary then
      let candidate := (c.source.toList.drop c.offset).takeWhile identChar
      if !candidate.isEmpty && (candidate.head?.map fun x => x ≥ 'a' && x ≤ 'z').getD false &&
          c.source[c.offset + candidate.length]? == some '(' then
        let (name, pos) ← ident "n-ary predicate"
        let some signature := c.signature.predicates.find? (fun p => p.1 == name &&
            p.2.length ≥ 3 && p.2.length ≤ 6)
          | fails "UnknownSymbol" ("unknown n-ary predicate " ++ pyQuote name) (some pos)
        literal "("
        term (c.source.size + 1)
        let mut count := 1
        while (← hasPrefix ", ") do
          advance 2
          term (c.source.size + 1)
          count := count + 1
          if count > 6 then fails "SyntaxError" "n-ary atom exceeds six arguments" (some c.offset)
        literal ")"
        let _ := signature
        complete c.offset
        return
    let start := c.offset
    term (c.source.size + 1)
    if ← hasPrefix " is " then
      advance 4
      let (name, pos) ← ident "unary predicate"
      unless (c.signature.predicates.find? fun p => p.1 == name && p.2.length == 1).isSome do
        fails "UnknownSymbol" ("unknown unary predicate " ++ pyQuote name) (some pos)
      complete c.offset
      return
    if ← hasPrefix " equals " then
      advance 8
      term (c.source.size + 1)
      complete c.offset
      return
    if c.order && ((← hasPrefix " <= ") || (← hasPrefix " < ")) then
      advance (if ← hasPrefix " <= " then 4 else 3)
      term (c.source.size + 1)
      complete c.offset
      return
    literal " "
    let (name, pos) ← ident "binary predicate"
    unless (c.signature.predicates.find? fun p => p.1 == name && p.2.length == 2).isSome do
      fails "UnknownSymbol" ("unknown binary predicate " ++ pyQuote name) (some pos)
    literal " "
    term (c.source.size + 1)
    if (← get).offset == start then fails "SyntaxError" "expected formula"
    complete c.offset

def scan (signature : VE.Service.TypingDiagnostic.Signature) (source : String)
    (order closure nary : Bool) : Option Error :=
  let chars := source.toList.toArray
  let c : Cursor := ⟨chars, 0, [], signature, order, closure, nary, 0⟩
  let program : Scan Unit := do
    if chars.isEmpty then fails "SyntaxError" "document must contain at least one statement" (some 0)
    while (← get).offset < chars.size do
      formula 1 (chars.size + 1)
      literal ".\n"
  match program.run c with
  | .error e => some e
  | .ok _ => none

def span (source : String) (e : Error) : Json :=
  let before := source.toList.take e.start
  let line := 1 + (before.filter (· == '\n')).length
  let column := 1 + ((before.reverse.takeWhile (· != '\n')).length)
  Json.mkObj [("start", toJson e.start), ("end", toJson e.stop),
    ("line", toJson line), ("column", toJson column)]

end VE.Service.ParseDiagnostic
