import VE.Defaults.Zone
import VE.Defaults.MeaningExamples

/-! DF-5's fixtures (docs/spec/defeasible.md 8.6), each computed by `defaultZoneOf` over `openAtomsAll` on a document
decoded by the real `decodeSoftU`, at a finite situation with no relation except the guards named. `X` is the
document's assembled premise packs (`Packs.labelledX`). Each check has an accepting and a refusing side. -/
namespace VE.Defaults.ZoneFixtures
open Lean
open VE.Defaults
open VE.Defaults.Fixtures (regJ xReq xPerm baseJ ruleJ dfltJ un holds val layered dα dβ dγ dδ Entity)
open VE.Defaults.MeaningFixtures (dπ)
open VE.NormDefaults.Wire (LayeredU)

/-! ## Documents -/

def envS (sort : String) (preds : List String) (soft : String) : Json :=
  (Json.parse ("{\"language\":\"ve.core@0.2\",\"profiles\":[\"norm-defaults@0\",\"norms@0\",\"relational-fol@0\"," ++
    "\"soft-norms@0\"],\"spec_revision\":\"ve-v0.2-expand2-2026-09-25\",\"vocabulary\":{\"sorts\":{\"" ++ sort ++
    "\":{\"description\":\"" ++ sort ++ "\"}},\"predicates\":{" ++ ",".intercalate preds ++
    "},\"constants\":{},\"soft\":" ++ soft ++ "}}")).toOption.get!
def ruleG (name pred : String) (sign : Bool) (guard : String) (fields : String) : String :=
  "{\"norm\":{\"name\":\"" ++ name ++ "\",\"predicate\":\"" ++ pred ++ "\",\"sign\":" ++ toString sign ++
    ",\"guard\":" ++ guard ++ ",\"unless\":[],\"over\":[]" ++ fields ++ "}}"

/-- DF-λ: plain `instructs(operator)`, unspecified; g1 "Every operator instructs, unless an exception applies." -/
def dlam : Except String LayeredU :=
  layered (envS "operator" [regJ "instructs" "[\"operator\"]" "plain" "unspecified"]
    r#"{"parties":["operator"],"outranking":{"mode":"strict"}}"#)
  [ruleJ "g1" "instructs" true (dfltJ (dec := "operator"))]
/-- DF-μ′: plain `p`, unspecified; r1 (+, guard `cond_a`) and r2 (−, guard `cond_b`), both default, unranked. -/
def dμ' : Except String LayeredU :=
  layered (envS "assistant" [regJ "p" "[\"assistant\"]" "plain" "unspecified", baseJ "cond_a", baseJ "cond_b"]
    r#"{"outranking":{"mode":"strict"}}"#)
  [ruleG "r1" "p" true (un "cond_a") dfltJ, ruleG "r2" "p" false (un "cond_b") dfltJ]

/-! ## Situations -/

def el (s : String) (i : Nat) : Entity := (s, "e_" ++ s ++ toString i)
/-- `k` elements of `sort`, the base predicates `on` true of every element. -/
def sit (sort : String) (k : Nat) (on : List String) : VE.FiniteModel Entity :=
  ⟨fun s => if s == sort then (List.range k).map (el sort) else [], fun _ => none,
   fun p => if on.contains p then (List.range k).map (fun i => [el sort i]) else []⟩
def reg (L : LayeredU) (n : String) : VE.Norms.Regulated :=
  (L.U.D.T.regulated.find? (·.name == n)).getD ⟨n, [], true, .plain, none, none⟩
def Xl (L : LayeredU) : List (String × VE.Formula) := VE.NormDefaults.Packs.labelledX L.packs

/-- The zone, as a tag. -/
def tag : DefaultZone Entity → String
  | .byDefault b _ => if b then "yes" else "no"
  | .leftTo _ _ _ => "leftTo"
  | .notSaid _ _ => "notSaid"
  | .noCompletion _ => "noCompletion"
  | .unknown (.budget n k) => s!"budget {n} {k}"
  | .unknown (.branch _ _) => "branch"
abbrev Obs := List ((VE.Norms.Regulated × List Entity) × Bool)
def zoneR (L : LayeredU) (M : VE.FiniteModel Entity) (rec : List ((String × List Entity) × Bool)) (obs : Obs)
    (n : String) (vs : List Entity) : String :=
  tag (defaultZoneOf L (Xl L) M rec obs (reg L n) vs [])
def zone (L : LayeredU) (M : VE.FiniteModel Entity) (obs : Obs) (n : String) (vs : List Entity) : String :=
  zoneR L M [] obs n vs
/-- The number of default completions found (`0` when the enumeration ends early). -/
def minCount (L : LayeredU) (M : VE.FiniteModel Entity) (rec : List ((String × List Entity) × Bool)) (obs : Obs) :
    Nat :=
  match zoneMin L (Xl L) M rec obs with
  | .ok m => m.length
  | .error _ => 0
def short (L : LayeredU) (M : VE.FiniteModel Entity) : Bool := zoneForm L M [] == .short
def a0 : Entity := el "assistant" 0
def M1 : VE.FiniteModel Entity := sit "assistant" 1 []

/-! ## DF-μ: DF-λ at {o1, o2}, `instructs(o1)` observed no -/

def M2 : VE.FiniteModel Entity := sit "operator" 2 []
def obsμ (L : LayeredU) : Obs := [((reg L "instructs", [el "operator" 0]), false)]

-- 4 open atoms; two default completions (the same decisions, differing in the filling at o2); by default yes at o2
-- and no at o1; the short form (every open decision atom is an exception).
#guard holds dlam fun L => (openAtomsAll L M2 []).length == 4 && minCount L M2 [] (obsμ L) == 2 &&
  zone L M2 (obsμ L) "instructs" [el "operator" 1] == "yes" && zone L M2 (obsμ L) "instructs" [el "operator" 0] == "no"
#guard holds dlam fun L => short L M2
-- Nothing observed: by default yes at o1 too.
#guard holds dlam fun L => zone L M2 [] "instructs" [el "operator" 0] == "yes"

/-! ## DF-μ′ and DF-μ′b: two unranked default rules of opposite sign on plain `p` -/

-- Both guards hold: left to a decider, with 4 default completions (r1 or r2 excepted, two fillings each).
#guard holds dμ' fun L => zone L (sit "assistant" 1 ["cond_a", "cond_b"]) [] "p" [a0] == "leftTo" &&
  minCount L (sit "assistant" 1 ["cond_a", "cond_b"]) [] [] == 4 && short L (sit "assistant" 1 ["cond_a", "cond_b"])
-- Neither guard: not said, with 2 default completions differing only in the filling.
#guard holds dμ' fun L => zone L M1 [] "p" [a0] == "notSaid" && minCount L M1 [] [] == 2

/-! ## DF-μ″: DF-γ at {a}, the zone of `x_permitted` (full enumeration, never the query's cone) -/

#guard holds dγ fun L => zone L M1 [] "x_permitted" [a0] == "leftTo" && minCount L M1 [] [] == 3 && short L M1

/-! ## DF-δz: DF-δ at {a}, the zone of `x_required` (the ranking atom is open) -/

#guard holds dδ fun L => zone L M1 [] "x_required" [a0] == "yes" && minCount L M1 [] [] == 2 && !short L M1

/-! ## DF-π′: DF-π at {a} (both pair members unspecified) -/

#guard holds dπ fun L => zone L M1 [] "x_required" [a0] == "yes" && minCount L M1 [] [] == 2

/-! ## DF-ξ: Z-ε's shape, DF-α at {a}, against weighing's settled answer under `noExceptionRecord` -/

def settled (L : LayeredU) (M : VE.FiniteModel Entity) (rec : List ((String × List Entity) × Bool)) (n : String) :
    Option Bool :=
  VE.NormDefaults.enumerateSettledX L.U ((Xl L).map (·.2)) M (VE.Weighing.openNames L) (openAtomsAll L M rec) 12 rec
    n [a0]

-- By default yes; weighing's answer under its record is settled yes and a completion meets the record (`hadm`);
-- without the record weighing's answer is not settled. DF-π at {a} likewise.
#guard holds dα fun L => zone L M1 [] "x_required" [a0] == "yes" &&
  settled L M1 (noExceptionRecord L.D M1) "x_required" == some true &&
  zoneR L M1 (noExceptionRecord L.D M1) [] "x_required" [a0] == "yes" && settled L M1 [] "x_required" == none
#guard holds dπ fun L => settled L M1 (noExceptionRecord L.D M1) "x_required" == some true &&
  zoneR L M1 (noExceptionRecord L.D M1) [] "x_required" [a0] == "yes"

/-! ## DF-ξ′: DF-β at {a} with `urgent(a)`: `hadm` fails -/

def Mu : VE.FiniteModel Entity := sit "assistant" 1 ["urgent"]

-- The stated condition forces the exception: `x_required` is not said, `x_permitted` is by default yes, and no
-- completion meets weighing's record "no exception" (so `defaultZone_eq_noException` needs `hadm`).
#guard holds dβ fun L => zone L Mu [] "x_required" [a0] == "notSaid" && zone L Mu [] "x_permitted" [a0] == "yes" &&
  zoneR L Mu (noExceptionRecord L.D Mu) [] "x_required" [a0] == "noCompletion" &&
  zoneR L Mu (noExceptionRecord L.D Mu) [] "x_permitted" [a0] == "noCompletion"
-- Without `urgent(a)` the record is met.
#guard holds dβ fun L => zoneR L M1 (noExceptionRecord L.D M1) [] "x_required" [a0] == "yes"

/-! ## Observations and records that no completion meets -/

-- Observing `x_permitted(a)` no at DF-α's situation contradicts the permission allowed by default: no completion.
#guard holds dα fun L => zone L M1 [((reg L "x_permitted", [a0]), false)] "x_required" [a0] == "noCompletion" &&
  zone L M1 [((reg L "x_permitted", [a0]), true)] "x_required" [a0] == "yes"
-- A record that says one atom both ways, or a true atom at an undeclared predicate: no completion.
#guard holds dα fun L => zoneR L M1 [(("soft__excepted__r1", [a0]), true), (("soft__excepted__r1", [a0]), false)] []
    "x_required" [a0] == "noCompletion" &&
  zoneR L M1 [(("zzz", [a0]), true)] [] "x_required" [a0] == "noCompletion" &&
  zoneR L M1 [(("soft__excepted__r1", [a0]), true)] [] "x_required" [a0] == "notSaid"

/-! ## The budget: every value read once, the open atoms charged against `maxDefaultAtoms` -/

-- DF-λ at 13 operators: 26 open atoms > 12, `unknown (budget 26)` before any assignment is built.
#guard holds dlam fun L => zone L (sit "operator" 13 []) [] "instructs" [el "operator" 0] == "budget 26 12"
-- The largest well-formed situation within the limit (6 operators, 12 open atoms, 4,096 assignments) ends.
#guard holds dlam fun L => (openAtomsAll L (sit "operator" 6 []) []).length == maxDefaultAtoms &&
  zone L (sit "operator" 6 []) [((reg L "instructs", [el "operator" 5]), false)] "instructs" [el "operator" 5] == "no"

end VE.Defaults.ZoneFixtures
