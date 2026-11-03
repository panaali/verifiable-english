import VE.Defaults.Zone
import VE.Defaults.MeaningExamples

/-! DF-5's fixtures (docs/spec/defeasible.md 8.6), each computed by `defaultZoneOf` over `openAtomsAll` on a document
decoded by the real `decodeSoftU`, at a finite situation with no relation except the guards named. `X` is the
document's assembled premise packs (`Packs.labelledX`). Each check has an accepting and a refusing side. -/
namespace VE.Defaults.ZoneFixtures
open Lean
open VE.Defaults
open VE.Defaults.Fixtures (regJ xReq xPerm baseJ ruleJ dfltJ un holds val layered envJ outw dα dβ dγ dδ dε Entity)
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
  | .unknown (.branch _ y) => "branch " ++ y
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

/-! ## Switches: DF-ε at {a}, where the user may turn r1 off -/

-- The switch is off unless the record says otherwise: by default yes; the record turning it on leaves it not said.
#guard holds dε fun L => switchesOffRecord L.D M1 [] == [(("soft__off__r1__user", [a0]), false)] &&
  switchesOffRecord L.D M1 [(("soft__off__r1__user", [a0]), true)] == [] && zone L M1 [] "x_required" [a0] == "yes" &&
  zoneR L M1 [(("soft__off__r1__user", [a0]), true)] [] "x_required" [a0] == "notSaid"

/-! ## Observations and records that no completion meets -/

-- Observing `x_permitted(a)` no at DF-α's situation contradicts the permission allowed by default: no completion.
#guard holds dα fun L => zone L M1 [((reg L "x_permitted", [a0]), false)] "x_required" [a0] == "noCompletion" &&
  zone L M1 [((reg L "x_permitted", [a0]), true)] "x_required" [a0] == "yes"
-- A record that says one atom both ways, or a true atom at an undeclared predicate (even one the model holds): no
-- completion.
#guard holds dα fun L => zoneR L M1 [(("soft__excepted__r1", [a0]), true), (("soft__excepted__r1", [a0]), false)] []
    "x_required" [a0] == "noCompletion" &&
  zoneR L M1 [(("zzz", [a0]), true)] [] "x_required" [a0] == "noCompletion" &&
  zoneR L (sit "assistant" 1 ["zzz"]) [(("zzz", [a0]), true)] [] "x_required" [a0] == "noCompletion" &&
  zoneR L M1 [(("soft__excepted__r1", [a0]), true)] [] "x_required" [a0] == "notSaid"

/-! ## The records and the form at two elements (every switch, exception and ranking atom in order) -/

/-- DF-ε with r1 alterable by the operator and by the user. -/
def dε2 : Except String LayeredU := layered (envJ [xReq, xPerm] r#"{"parties":["operator","user"],"outranking":{"mode":"strict"}}"#)
  [ruleJ "r1" "x_required" true (dfltJ (extra := ",\"alterable\":[\"operator\",\"user\"]"))]
/-- DF-δ with a third default rule on `x_permitted` at rank honesty: two ranking decisions. -/
def dδ3 : Except String LayeredU := layered (envJ [xReq, xPerm]
    r#"{"ranks":["safety","helpfulness","honesty"],"outranks":[["safety","helpfulness"],["safety","honesty"]],"outranking":{"mode":"holistic","decided_by":"assistant"}}"#)
  [ruleJ "r1" "x_required" true (dfltJ (extra := ",\"rank\":\"safety\"")),
   ruleJ "r2" "x_permitted" false (dfltJ (extra := ",\"rank\":\"helpfulness\"")),
   ruleJ "r3" "x_permitted" false (dfltJ (extra := ",\"rank\":\"honesty\""))]
def A2 : VE.FiniteModel Entity := sit "assistant" 2 []
def a1 : Entity := el "assistant" 1
def off (π : String) (e : Entity) : String × List Entity := ("soft__off__r1__" ++ π, [e])
def exc (r : String) (e : Entity) : String × List Entity := ("soft__excepted__" ++ r, [e])

-- Every switch at every tuple, off, but the atoms the record fixes; the form stays short (every switch is fixed).
#guard holds dε2 fun L => switchesOffRecord L.D A2 [] ==
    [(off "operator" a0, false), (off "operator" a1, false), (off "user" a0, false), (off "user" a1, false)] &&
  switchesOffRecord L.D A2 [(off "user" a0, true), (off "operator" a1, true)] ==
    [(off "operator" a0, false), (off "user" a1, false)] && short L A2
-- Weighing's record: every exception at every tuple, false.
#guard holds dγ fun L => noExceptionRecord L.D A2 ==
  [(exc "r1" a0, false), (exc "r1" a1, false), (exc "r2" a0, false), (exc "r2" a1, false)]
-- The form reads every open atom the record leaves: short only when both ranking atoms are fixed; long when the
-- ranking atom is the first or the last one open.
#guard holds dδ fun L => zoneForm L A2 [((outw, [a0]), true), ((outw, [a1]), true)] == .short &&
  zoneForm L A2 [((outw, [a1]), true)] == .long &&
  zoneForm L M1 [(exc "r1" a0, false), (exc "r2" a0, false)] == .long &&
  zoneForm L M1 [(exc "r1" a0, false), (exc "r2" a0, false), (("unsaid__x_required", [a0]), false)] == .long
-- Every ranking decision is a decision: one left open makes the form long.
#guard holds dδ3 fun L => zoneForm L M1 [(("soft__outweighs__honesty__safety__x_permitted", [a0]), true)] == .long &&
  zoneForm L M1 [((outw, [a0]), true), (("soft__outweighs__honesty__safety__x_permitted", [a0]), true)] == .short

/-! ## The budget: the charge counts the record, the open atoms and the typed atoms before listing any -/

-- DF-λ at 13 operators: 26 open atoms > 12, `unknown (budget 26)` before any assignment is built.
#guard holds dlam fun L => zone L (sit "operator" 13 []) [] "instructs" [el "operator" 0] == "budget 26 12" &&
  zoneFormOf L (sit "operator" 13 []) [] == none
-- The largest well-formed situation within the limit (6 operators, 12 open atoms, 4,096 assignments) ends.
#guard holds dlam fun L => (openAtomsAll L (sit "operator" 6 []) []).length == maxDefaultAtoms &&
  zone L (sit "operator" 6 []) [((reg L "instructs", [el "operator" 5]), false)] "instructs" [el "operator" 5] == "no"

/-- DF-λ wide (review F1): ten binary plain predicates, each with a default rule decided by `o`. -/
def dwide : Except String LayeredU :=
  let ps := (List.range 10).map fun i => s!"p{i}"
  layered (envS "o" (ps.map fun p => regJ p "[\"o\",\"o\"]" "plain" "unspecified")
      r#"{"parties":["o"],"outranking":{"mode":"strict"}}"#)
    (ps.map fun p => ruleJ ("g" ++ p) p true (dfltJ (dec := "o")))
-- At 1,000 entities: 20,000,000 open atoms (an exception and an unsaid atom per pair, per predicate), counted from
-- the sorts' sizes and answered at once, never listed (listing them took 96 s and 5 GB).
#guard holds dwide fun L => zone L (sit "o" 1000 []) [] "p0" [el "o" 0, el "o" 0] == "budget 20000000 12"
-- At 100,000 entities: 2 × 10¹¹ open atoms, which no listing could hold.
#guard holds dwide fun L => zone L (sit "o" 100000 []) [] "p0" [el "o" 0, el "o" 0] == "budget 200000000000 12"

/-- `k` copies of one operator: every typed atom listed `k` times. -/
def dupSit (k : Nat) : VE.FiniteModel Entity :=
  ⟨fun s => if s == "operator" then List.replicate k (el "operator" 0) else [], fun _ => none, fun _ => []⟩
def e0 : Entity := el "operator" 0
def recN (k : Nat) : List ((String × List Entity) × Bool) := List.replicate k (exc "g1" e0, false)
def fixBoth : List ((String × List Entity) × Bool) := [(exc "g1" e0, false), (("unsaid__instructs", [e0]), true)]

-- The record: `maxZoneRecord` entries are read, one more is `unknown` before the record is read, even with more
-- than `maxDefaultAtoms` atoms open.
#guard holds dlam fun L => zoneR L (sit "operator" 2 []) (recN maxZoneRecord) [] "instructs" [el "operator" 1] == "yes" &&
  zoneR L (sit "operator" 2 []) (recN (maxZoneRecord + 1)) [] "instructs" [el "operator" 1] == "branch record size" &&
  zoneR L (sit "operator" 13 []) (recN (maxZoneRecord + 1)) [] "instructs" [el "operator" 1] == "branch record size"
-- The typed atoms: with every atom fixed, 2 × 518 = `maxZoneRecord + maxDefaultAtoms` copies are listed, 2 × 519 are
-- `unknown`; unfixed, they are the exact budget.
#guard holds dlam fun L => zoneR L (dupSit 518) fixBoth [] "instructs" [e0] == "yes" &&
  zoneR L (dupSit 519) fixBoth [] "instructs" [e0] == "branch size" &&
  zoneR L (dupSit 2000) fixBoth [] "instructs" [e0] == "branch size" &&
  zone L (dupSit 2000) [] "instructs" [e0] == "budget 4000 12" && zoneFormOf L (dupSit 519) fixBoth == none

-- The count is `openAtomsAll`'s length (`openAtomsCount_eq`) on records that repeat an atom, say it both ways, name an
-- undeclared predicate or a tuple of the wrong length, and on domains that list an element twice.
def recs : List (List ((String × List Entity) × Bool)) :=
  [[], [((outw, [a0]), true)], [((outw, [a0]), true), ((outw, [a0]), false), ((outw, [a0]), true)],
   [(exc "r1" a0, false), (exc "r2" a1, true), (("unsaid__x_required", [a1]), false)], [(("zzz", [a0]), true)],
   [((outw, [a0, a1]), true), ((outw, []), true)]]
def dupA : VE.FiniteModel Entity :=
  ⟨fun s => if s == "assistant" then [a0, a1, a0] else [], fun _ => none, fun _ => []⟩
#guard holds dδ3 fun L => [M1, A2, dupA].all fun M => recs.all fun r =>
  openAtomsCount L M r == (openAtomsAll L M r).length
-- Four unary predicates: 4 × 3 listed elements, less the two copies of the fixed `outw(a0)`; 4 × 2 at two elements.
#guard holds dδ fun L => openAtomsCount L dupA [((outw, [a0]), true)] == 10 && openAtomsCount L A2 [] == 8
-- The form behind the charge is the form.
#guard holds dδ fun L => zoneFormOf L M1 [] == some .long && zoneFormOf L A2 [((outw, [a0]), true), ((outw, [a1]), true)] == some .short

/-! ## `forcedAll`: the exception atoms every default completion holds (8.6, DF-μ′ and DF-μ″ as they bear on it) -/

/-- `forcedAllOf` with no proposal. -/
def forced (L : LayeredU) (M : VE.FiniteModel Entity) (rec : List ((String × List Entity) × Bool)) (obs : Obs) :
    Option (List (String × List Entity)) :=
  forcedAllOf L (Xl L) M rec obs []

-- DF-μ: both default completions hold g1's exception at o1 (observed `instructs(o1)` = no), so it is forced and
-- nothing else is; with nothing observed, nothing is forced.
#guard holds dlam fun L => forced L M2 [] (obsμ L) == some [exc "g1" (el "operator" 0)] && forced L M2 [] [] == some []
-- DF-μ′: four default completions, r1 excepted in two and r2 in the other two, so neither alternative exception is
-- forced (seeded bug "forced read from one default completion": [r2's]); with neither guard nothing is forced.
#guard holds dμ' fun L => forced L (sit "assistant" 1 ["cond_a", "cond_b"]) [] [] == some [] && forced L M1 [] [] == some []
-- DF-μ″: three default completions, r2 excepted in two and r1 in one: neither is forced (the same seeded bug: [r2's]).
#guard holds dγ fun L => forced L M1 [] [] == some []
-- DF-δz: no default completion has an exception.
#guard holds dδ fun L => forced L M1 [] [] == some []
-- An exception the record fixes has one value in every completion: forced when true, not when false.
#guard holds dlam fun L => forced L M2 [(exc "g1" (el "operator" 1), true)] [] == some [exc "g1" (el "operator" 1)] &&
  forced L M2 [(exc "g1" (el "operator" 1), false)] (obsμ L) == some [exc "g1" (el "operator" 0)]
-- A decision atom true in every completion that is not an exception (the ranking atom) is not listed.
#guard holds dδ fun L => forced L M1 [((outw, [a0]), true)] [] == some []
-- No complete enumeration, no list: over the budget, over the record bound, no default completion.
#guard holds dlam fun L => forced L (sit "operator" 13 []) [] [] == none &&
  forced L (sit "operator" 2 []) (recN (maxZoneRecord + 1)) [] == none
#guard holds dα fun L => forced L M1 [] [((reg L "x_permitted", [a0]), false)] == none
#guard holds dwide fun L => forced L (sit "o" 1000 []) [] [] == none
-- Large well-formed situations within the limits end: 12 open atoms (4,096 assignments), and 2 × 518 typed atoms
-- listed (one past it is `none`). An atom a domain lists three times is reported once.
#guard holds dlam fun L =>
  forced L (sit "operator" 6 []) [] [((reg L "instructs", [el "operator" 5]), false)] == some [exc "g1" (el "operator" 5)] &&
  forced L (dupSit 518) fixBoth [] == some [] && forced L (dupSit 519) fixBoth [] == none &&
  forced L (dupSit 3) [] [((reg L "instructs", [e0]), false)] == some [exc "g1" e0]

end VE.Defaults.ZoneFixtures
