import VE.EnglishGrammar.Norm.Value
import VE.EnglishGrammar.Encode
import VE.Norms.Wire

/-! A read rule block to the W1 node (docs/spec/english-lean-s6.md 2.7, en-e3-norm D4): the one output path is the
norm wire object decoded by `VE.Norms.Wire.decodeNorm`. Rule `i` is named `rule-i`, as Python names a block without
a manifest (`ve/norm_english.py:307`). -/

namespace VE.EnglishGrammar.Norm
open Lean VE.EnglishGrammar

def ruleName (i : Nat) : String := "rule-" ++ toString i

/-- `{"norm": {"name", "predicate", "sign", "guard", "unless", "over"}}`: `predicate` is `c.pred`, `sign`
is `c.force.sign`, `guard` is `c.guard.encode`, `unless` is `c.carveOuts.map EFormula.encode`. -/
def Clause.wire (name : String) (over : List String) (c : Clause) : Lean.Json :=
  Json.mkObj [("norm", Json.mkObj [("name", .str name), ("predicate", .str c.pred), ("sign", .bool c.force.sign),
    ("guard", c.guard.encode), ("unless", .arr (c.carveOuts.map EFormula.encode).toArray),
    ("over", .arr (over.map Json.str).toArray)])]

def Clause.toNode (name : String) (over : List String) (c : Clause) : Except String VE.Norms.Node :=
  VE.Norms.Wire.decodeNorm (c.wire name over)

/-- Rule `n`'s `over`: its header's targets, then the `m` of every `.precedence n m`, in text order
(`norm_english.py:290`, :323). -/
def overOf (rs : List NormStatement) (n : Nat) : List Nat :=
  (rs.filterMap fun | .rule h _ => if h.number = n then some h.exceptionTo else none | _ => none).flatten ++
  rs.filterMap fun | .precedence n2 m => if n2 = n then some m else none | _ => none

/-- The nodes of the rules in order; rule `i` is named `ruleName i` (Python without a manifest, :307). -/
def toNodes (rs : List NormStatement) : Except String (List VE.Norms.Node) :=
  (rs.filterMap fun | .rule h c => some (h, c) | _ => none).mapM fun (h, c) =>
    c.toNode (ruleName h.number) ((overOf rs h.number).map ruleName)

/-! ## `toNode_fields` (spec section 4) -/

/-- `strings` reads back a list of strings. -/
theorem strings_map (o : List String) : VE.Bridge.strings (.arr (o.map Json.str).toArray) = .ok o := by
  unfold VE.Bridge.strings
  simp only [Json.getArr?, pure_bind]
  induction o with
  | nil => rfl
  | cons x xs ih =>
    simp only [List.map_cons, List.mapM_cons, ih]
    rfl

/-- `normFields` reads back every field of `Clause.wire`. -/
theorem fields_wire (n : String) (o : List String) (c : Clause) :
    VE.Norms.Wire.normFields (c.wire n o) = .ok (n, c.pred, c.force.sign, c.guard.encode,
      c.carveOuts.map EFormula.encode, o) := by
  have h : VE.Norms.Wire.normFields (c.wire n o) = (VE.Bridge.strings (.arr (o.map Json.str).toArray)).bind
      fun over => .ok (n, c.pred, c.force.sign, c.guard.encode, c.carveOuts.map EFormula.encode, over) := rfl
  rw [h, strings_map]
  rfl

/-- `decodeNorm`'s loop appends one carve-out per wire formula. -/
theorem forIn_length (f : Json → MProd (List VE.Formula) Nat →
      Except String (ForInStep (MProd (List VE.Formula) Nat)))
    (hf : ∀ x r s, f x r = .ok s → ∃ φ k, s = .yield ⟨r.fst ++ [φ], k⟩) :
    ∀ (xs : List Json) (init r : MProd (List VE.Formula) Nat),
    forIn (m := Except String) xs init f = .ok r → r.fst.length = init.fst.length + xs.length := by
  intro xs
  induction xs with
  | nil => intro init r h; cases h; simp
  | cons x xs ih =>
    intro init r h
    simp only [List.forIn_cons, bind, Except.bind] at h
    cases hx : f x init with
    | error e => rw [hx] at h; cases h
    | ok s =>
      rw [hx] at h
      obtain ⟨φ, k, rfl⟩ := hf x init s hx
      have := ih _ r h
      simp only [List.length_append, List.length_cons, List.length_nil] at this ⊢
      omega

theorem toNode_fields : ∀ (n : String) (o : List String) (c : Clause) (nd : VE.Norms.Node),
  c.toNode n o = .ok nd →
  nd.name = n ∧ nd.pred = c.pred ∧ nd.sign = c.force.sign ∧ nd.over = o ∧ nd.carveOuts.length = c.carveOuts.length := by
  intro n o c nd h
  unfold Clause.toNode VE.Norms.Wire.decodeNorm at h
  rw [fields_wire] at h
  simp only [bind, Except.bind, pure, Except.pure, ite_true] at h
  split at h
  · cases h
  · split at h
    · cases h
    · rename_i v1 _ hf
      cases h
      have := forIn_length _ (fun x r s h => by
        split at h
        · cases h
        · cases h; exact ⟨_, _, rfl⟩) _ _ _ hf
      simp only [List.length_map, List.length_nil] at this
      exact ⟨rfl, rfl, rfl, rfl, by simpa using this⟩

end VE.EnglishGrammar.Norm
