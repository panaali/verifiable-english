/-! Wire contract tables (docs/spec/wire-contract.md 5.1).

The data of one contract as the generated table modules write it: phases of
checks, groups and resolved includes, with every limit a numeral, every lexical
class and every code's class written out, and every message template split
into pieces. This module reads no JSON and states no theorem; the engine that
runs a table is `VE.WireContract.Engine`. Nothing on a verdict or identity path
imports it (spec 7.3).
-/

namespace VE.WireContract

abbrev Pointer := List String          -- unescaped RFC 6901 reference tokens, from the root

inductive Step where
  | tok (s : String)
  | star

inductive Base where
  | root
  | item (n : Nat)                     -- the item of the n-th enclosing group; 0 is the innermost

structure Pattern where
  base : Base
  steps : List Step

inductive Value where                  -- a scalar literal of a contract (2.3); it has no `null`
  | bool (b : Bool) | int (n : Nat) | str (s : String)

inductive Atom where
  | null | boolean | integer | string | array | object

inductive TypeForm where
  | atom (a : Atom)
  | arrayOf (a : Atom)
  | tuple (parts : List Atom)

inductive Lit where
  | present (p : Pattern)
  | absent (p : Pattern)
  | equals (p : Pattern) (v : Value)
  | differs (p : Pattern) (v : Value)
  | isType (p : Pattern) (t : List TypeForm)
  | notType (p : Pattern) (t : List TypeForm)

structure NameClass where
  first : Option (List (Nat × Nat))    -- inclusive code point ranges
  rest : Option (List (Nat × Nat))
  minBytes : Option Nat
  maxBytes : Option Nat
  forbidPrefix : List String
  forbidInfix : List String
  oneOf : Option (List String)

inductive Renderer where
  | raw | json | index | count | list

inductive Piece where
  | lit (s : String)
  | arg (name : String) (r : Renderer)

structure Member where                 -- one check of a classifier set (2.5)
  id : String
  code : String
  cls : String
  text : List Piece
  inherited : Bool

inductive Kind where
  | hasType (t : List TypeForm)
  | exactKeys (keys : List String)
  | keys (required optional : List String)
  | const (v : Value)
  | oneOf (vs : List Value)
  | maxItems (limit : Nat)
  | maxBytes (limit : Nat)
  | maxCount (pattern : Pattern) (limit : Nat)
  | name (cls : NameClass) (onKey : Bool)
  | sortedUnique
  | uniqueSoFar
  | declaredIn (set : Pattern)
  | requiresMember (key : String)
  | requiresItem (v : Value)
  | excludesMember (key : String)
  | excludesItem (v : Value)
  | hook (name : String)
  | classifier (name : String) (emits : List Member)

structure Check where
  id : String
  loc : Pattern                        -- `at`
  guard : List Lit                     -- `when`
  kind : Kind
  code : String
  cls : String
  text : List Piece
  args : List (String × Pattern)
  inherited : Bool

inductive Entry where
  | check (c : Check)
  | each (id : String) (over : Pattern) (guard : List Lit) (entries : List Entry)
  | scope (id : String) (loc : Pattern) (view : Option String) (recode : Option (String × String))
      (entries : List Entry)           -- a resolved `include`; `recode` is the `as` code and its class

structure Phase where
  name : String
  entries : List Entry

structure Table where
  contract : String
  revision : Nat
  residual : String × String           -- the residual code and its class
  phases : List Phase

end VE.WireContract
