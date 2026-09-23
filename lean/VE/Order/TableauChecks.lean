import VE.Order.Wire

/-! Executable regressions for the order@0 Farkas checker. These are not
evidence for soundness (see Tableau.checkCertificate_sound); they pin the
intended accept/reject behaviour on small hand-built certificates. -/
namespace VE.Order.TableauChecks
open VE.Order VE.Order.Tableau

def env : Environment where
  sorts := ["item"]
  constants c := if c == "a" then some (.user "item")
    else if ["c", "d"].contains c then some .int else none
  predicates p := if p == "marked" then some [.int]
    else if p == "value" then some [.user "item", .int] else none

def cert (t : Trace) : Certificate := ⟨checkerVersion, "", [], "", t⟩

def c : Term := .const "c"
def d : Term := .const "d"
def one : Term := .num 1

-- c < d entails c <= d: 0 <= d - c - 1 and 0 <= c - d - 1 sum to 0 <= -2.
#guard checkCertificate env [.lt c d] (.le c d)
  (cert (.farkas [] ⟨[(0, 1), (1, 1)], []⟩))
-- Negative multipliers are rejected on inequalities.
#guard !checkCertificate env [.lt c d] (.le c d)
  (cert (.farkas [] ⟨[(0, -1), (1, 1)], []⟩))
-- A combination whose constant is nonnegative does not close.
#guard !checkCertificate env [.le c d] (.lt c d)
  (cert (.farkas [] ⟨[(0, 1), (1, 1)], []⟩))
-- 2c = 1 is rationally satisfiable: plain Farkas fails, two gcd cuts close.
#guard !checkCertificate env [.eq (.scale 2 c) one] .bottom
  (cert (.farkas [] ⟨[(0, 1), (0, -1)], []⟩))
#guard checkCertificate env [.eq (.scale 2 c) one] .bottom
  (cert (.farkas [⟨⟨[(0, 1)], []⟩, 2⟩, ⟨⟨[(0, -1)], []⟩, 2⟩] ⟨[], [(0, 1), (1, 1)]⟩))
-- A cut whose divisor does not divide every collected coefficient is rejected.
#guard !checkCertificate env [.eq (.scale 2 c) one] .bottom
  (cert (.farkas [⟨⟨[(0, 1)], []⟩, 3⟩, ⟨⟨[(0, -1)], []⟩, 3⟩] ⟨[], [(0, 1), (1, 1)]⟩))
-- Negative equalities need the split rule when no certified c <= d, d <= c pair
-- is literally on the branch (d <= c + 0 is not d <= c).
#guard checkCertificate env [.le c d, .le d (.add c (.num 0))] (.eq c d)
  (cert (.neq 2 [.farkas [] ⟨[(1, 1), (3, 1)], []⟩, .farkas [] ⟨[(0, 1), (3, 1)], []⟩]))
#guard !checkCertificate env [.le c d, .le d (.add c (.num 0))] (.eq c d) (cert .close)
-- With both certified comparisons present the equality closes directly.
#guard checkCertificate env [.le c d, .le d c] (.eq c d) (cert .close)
-- P(c+1) against not P(1+c): no syntactic normalisation closes it ...
#guard !checkCertificate env [.unary "marked" (.add c one)] (.unary "marked" (.add one c))
  (cert .close)
-- ... but certified c+1 <= 1+c and 1+c <= c+1 do.
#guard checkCertificate env [.unary "marked" (.add c one)] (.unary "marked" (.add one c))
  (cert (.split (.le (.add c one) (.add one c))
    [.split (.le (.add one c) (.add c one)) [.close, .farkas [] ⟨[(3, 1)], []⟩],
     .farkas [] ⟨[(2, 1)], []⟩]))
-- Splits on non-linear or object comparisons are rejected.
#guard !checkCertificate env [.unary "marked" (.add c one)] (.unary "marked" (.add one c))
  (cert (.split (.le (.const "a") c) [.close, .close]))
-- Ordinary quantifier rules: every item has value c; the object a has value c.
#guard checkCertificate env [.all "item" (.binary "value" (.var 0) c)]
  (.binary "value" (.const "a") c)
  (cert (.expand 0 (some "c:a") [.close]))
-- Wrong checker version.
#guard !checkCertificate env [.lt c d] (.le c d)
  { cert (.farkas [] ⟨[(0, 1), (1, 1)], []⟩) with checker_version := "ve-tableau-checker@2" }

-- The order wire decoder accepts exactly the order-only profile list.
open Lean in
def envelope (profiles : List String) : Json := Json.mkObj [
  ("language", .str "ve.core@0.1"),
  ("profiles", toJson profiles),
  ("spec_revision", .str "ve-v0.1-order-2026-09-22"),
  ("vocabulary", Json.mkObj [("sorts", Json.mkObj []), ("predicates", Json.mkObj []),
    ("constants", Json.mkObj [])])]

#guard (Wire.decodeEnvironment (envelope ["order@0", "relational-fol@0"])).toBool
#guard !(Wire.decodeEnvironment (envelope ["closure@0", "order@0", "relational-fol@0"])).toBool
#guard !(Wire.decodeEnvironment (envelope ["relational-fol@0", "order@0"])).toBool
-- Declaration objects are validated as in Python and the v0/closure adapters.
open Lean in
def withSort (entry : Json) : Json := Json.mkObj [
  ("language", .str "ve.core@0.1"),
  ("profiles", toJson ["order@0", "relational-fol@0"]),
  ("spec_revision", .str "ve-v0.1-order-2026-09-22"),
  ("vocabulary", Json.mkObj [("sorts", Json.mkObj [("item", entry)]),
    ("predicates", Json.mkObj []), ("constants", Json.mkObj [])])]

open Lean in
#guard (Wire.decodeEnvironment (withSort (Json.mkObj [("description", .str "I")]))).toBool
open Lean in
#guard !(Wire.decodeEnvironment (withSort (.str "not a declaration object"))).toBool
open Lean in
#guard !(Wire.decodeEnvironment (withSort (Json.mkObj [("description", .str "")]))).toBool
open Lean in
#guard !(Wire.decodeEnvironment (withSort (Json.mkObj [("description", .str "I"),
  ("colour", .str "red")]))).toBool

-- Term depth is budgeted separately from formula depth: height 64 decodes, 65 does not.
open Lean in
def nestedAdd : Nat → Json
  | 0 => Json.arr #[.str "const", .str "c"]
  | n + 1 => Json.arr #[.str "add", nestedAdd n, Json.arr #[.str "num", .str "1"]]

open Lean in
def notLe (n : Nat) : Json :=
  Json.arr #[.str "not", Json.arr #[.str "le", nestedAdd n, Json.arr #[.str "num", .str "0"]]]

#guard (Wire.decodeFormula 64 (notLe 63)).toBool
#guard !(Wire.decodeFormula 64 (notLe 64)).toBool

#guard (match Wire.decodeInt "-12" with | .ok z => z == -12 | .error _ => false)
#guard !(Wire.decodeInt "-0").toBool
#guard !(Wire.decodeInt "007").toBool
#guard !(Wire.decodeInt "+7").toBool

end VE.Order.TableauChecks
