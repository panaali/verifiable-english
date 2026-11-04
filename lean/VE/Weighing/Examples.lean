import VE.Weighing.Conditions
import VE.Weighing.Zone
import VE.Defaults.Examples

/-! # Weighing fixtures (docs/spec/weighing.md 7.2), the part wg-2 needs

Documents are wire JSON decoded by `decodeSoftSource`, as in the statement stub; premises are `Conditions.lean`'s; an
assignment of the decision atoms is admissible when soft's labelled premises and `Weigh_T` hold (`Formula.eval`).
W-μ is the one fixture with a binary act, so it alone exercises the argument order. The other rows of 7.2 are
wg-2b's. -/

namespace VE.Weighing.Examples
open Lean VE.Norms VE.SoftNorms VE.Weighing
open VE.Defaults.Fixtures (regJ baseJ ruleJ xReq xPerm)

abbrev GAtom := String × List String

def attrJ (p owner : String) : String :=
  "\"" ++ p ++ "\":{\"arguments\":[\"assistant\",\"user\"],\"description\":\"" ++ p ++ "\",\"instruction_of\":\"" ++
    owner ++ "\"}"
def softJ (ranks : List String) (edges : List (String × String)) (holistic : Bool) (parties : List String := []) :=
  "{\"parties\":" ++ (toJson parties).compress ++ ",\"ranks\":" ++ (toJson ranks).compress ++ ",\"outranks\":" ++
    (toJson (edges.map (fun e => [e.1, e.2]))).compress ++ ",\"outranking\":" ++
    (if holistic then "{\"mode\":\"holistic\",\"decided_by\":\"assistant\"}" else "{\"mode\":\"strict\"}") ++ "}"
def envOf (preds : List String) (soft : String) : Json :=
  (Json.parse ("{\"language\":\"ve.core@0.2\",\"profiles\":[\"norms@0\",\"relational-fol@0\",\"soft-norms@0\"]," ++
    "\"spec_revision\":\"ve-v0.2-expand2-2026-09-25\",\"vocabulary\":{\"sorts\":{\"assistant\":{\"description\":" ++
    "\"assistant\"},\"user\":{\"description\":\"user\"}},\"predicates\":{" ++ ",".intercalate preds ++
    "},\"constants\":{},\"soft\":" ++ soft ++ "}}")).toOption.get!
def dfltR (name pred : String) (sign : Bool) (rank : String) : String :=
  ruleJ name pred sign (",\"mode\":\"default\",\"exception\":{\"decided_by\":\"assistant\",\"sufficient\":[]," ++
    "\"necessary\":[],\"factors\":[]},\"rank\":\"" ++ rank ++ "\"")
/-- The decoded soft document, or the empty one when the source is refused (every guard below then fails). -/
def decode (env : Json) (rules : List String) : SoftDoc :=
  match VE.SoftNorms.Wire.decodeSoftSource env (Json.parse ("[" ++ ",".intercalate rules ++ "]")).toOption.get! with
  | .ok S => S.D
  | .error _ => ⟨⟨[], fun _ => none, fun _ => none⟩, [], ⟨[], [], [], [], .strict, none, none, [], []⟩, ⟨[], [], []⟩⟩

def W (always : List (String × String) := []) (conditions : List CondDecl := []) (grants : List GrantDecl := []) :
    WeighEnv := ⟨always, conditions, [], grants⟩
def wd (D : SoftDoc) (w : WeighEnv := W) (sm : VE.Acts.SplitMap := ⟨[], []⟩) : WeighDoc := ⟨D, w, sm⟩
def verdict (Wd : WeighDoc) : String := match checkWeigh Wd with
  | .ok () => "accepted"
  | .error e => e
def U (a : String) : VE.Formula := .unary a (.var 0)
def tOut (L H : String) : Target := .outweighs "x_permitted" L H

/-! ## W-α, W-ε and the strict flag: strength premises, conditions, refusals -/

def alphaOf (ranks : List String) (edges : List (String × String)) (hi lo : String) (holistic := true) : SoftDoc :=
  decode (envOf [xReq "deny", xPerm, baseJ "urgent", baseJ "serious"] (softJ ranks edges holistic))
    [dfltR "h" "x_required" true hi, dfltR "l" "x_permitted" false lo]
def α : SoftDoc := alphaOf ["a", "b"] [("a", "b")] "a" "b"
def wα : WeighDoc := wd α (W [("a", "b")])

#guard verdict wα == "accepted" && WellFormedWeigh wα && weighWarnings wα == []
#guard weighOrigins wα == [("weigh:strength:a:b:x_permitted", ["environment", "vocabulary", "weighing", "always", "0"])]
#guard strengthPremises wα == [bindAll ["assistant"] (.not (outweighsF α "x_permitted" "b" "a"))]
#guard strengthPremises (wd α) == [] && strictPair wα "a" "b" && !strictPair (wd α) "a" "b"
#guard weighWarnings (wd (alphaOf ["a", "b"] [("a", "b")] "a" "b" false) (W [("a", "b")])) == ["StrengthInert: a, b"]
#guard verdict (wd α (W [("b", "a")])) == "StrengthOnUndeclaredEdge: b, a"
#guard verdict (wd α (W [] [⟨tOut "b" "a", .necessary, U "urgent"⟩] )) == "accepted"
#guard verdict (wd (alphaOf ["a", "b"] [("a", "b")] "a" "b" false) (W [] [⟨tOut "b" "a", .necessary, U "urgent"⟩])) ==
  "NoSuchDecision: outweighs x_permitted, b, a"
#guard verdict (wd α (W [("a", "b")] [⟨tOut "b" "a", .necessary, U "urgent"⟩])) ==
  "ConditionOnStrictPair: outweighs x_permitted, b, a"
-- W-ε: a sufficient condition that implies the necessary one; Pack.conditions exports the sufficient one only
def wε : WeighDoc := wd α (W [] [⟨tOut "b" "a", .sufficient, .and (U "urgent") (U "serious")⟩,
  ⟨tOut "b" "a", .necessary, U "urgent"⟩])
#guard verdict wε == "accepted" && weighConditions wε == [(.outweighs "x_permitted" "b" "a", .and (U "urgent") (U "serious"))]
#guard (weighLabelled wε).map (·.1) == ["weigh:condition:0:sufficient", "weigh:condition:1:necessary"]
#guard verdict (wd α (W [] [⟨tOut "b" "a", .sufficient, U "serious"⟩, ⟨tOut "b" "a", .necessary, U "urgent"⟩])) ==
  "ConditionsDisagree: the checker cannot show that condition 0 implies condition 1"
-- W-λ: a target naming a split act is refused with AP's text
#guard verdict (wd α (W [] [⟨tOut "b" "a", .necessary, U "urgent"⟩]) ⟨[("x_permitted__1", "x_permitted", 1)], []⟩) ==
  "InvalidInput: act x_permitted names a predicate that is split into parts; name one of its parts"
-- θ19/θ20: twelve distinct atoms are decided, thirteen are not
def conj (n : Nat) : VE.Formula := ((List.range n).map (fun i => U s!"p{i}")).foldl .and .top
#guard propImplies (conj 12) (U "p11") && !propImplies (conj 13) (U "p12") && !propImplies (U "p0") (U "p1")
#guard propImplies (.and (U "p0") (.not (U "p0"))) (U "p1") && propImplies (U "p0") (.or (U "p1") (.not (U "p1")))

/-! ## W-μ (argument order) -/

def yReq : String := regJ "y_required" "[\"assistant\",\"user\"]" "obligation" "deny"
  ",\"act\":\"{0} meet {1}\",\"permission\":\"y_permitted\""
def yPerm : String := regJ "y_permitted" "[\"assistant\",\"user\"]" "permission" "allow" ",\"act\":\"{0} meet {1}\""
def μd : SoftDoc := decode (envOf [yReq, yPerm, "\"trusts\":{\"arguments\":[\"assistant\",\"user\"],\"description\":" ++
    "\"trusts\"}", attrJ "operator_allows_for" "operator"] (softJ [] [] false ["operator", "user"]))
  [ruleJ "n" "y_required" true ",\"mode\":\"strict\",\"alterable\":[\"operator\",\"user\"]"]
def trustsF : VE.Formula := .binary "trusts" (.var 1) (.var 0)
def wμ : WeighDoc := wd μd (W [] [⟨.off "n" "operator", .necessary, trustsF⟩] [⟨"n", "user", "operator", "operator_allows_for"⟩])

def doms2 : String → List String := fun s =>
  if s == "assistant" then ["a1", "a2"] else if s == "user" then ["u1", "u2"] else []
def modelOf (facts : List GAtom) : VE.FiniteModel String := ⟨doms2, fun _ => none, fun p => (facts.filter (·.1 == p)).map (·.2)⟩
def baseμ : List GAtom := [("trusts", ["a1", "u2"]), ("operator_allows_for", ["a1", "u2"]), ("operator_allows_for", ["a2", "u1"])]
def assignments : List (List GAtom) := subsetsOf (decisionAtoms μd (modelOf []))
def μAll : List (List GAtom) := assignments.filter fun t =>
  ((VE.SoftNorms.Wire.softLabelled μd ++ weighLabelled wμ).map (·.2)).all (·.eval (modelOf (baseμ ++ t)) [])
def outcome (t : List GAtom) (vs : List String) : Bool :=
  (outcomeBase (soften μd) "y_required").eval (modelOf (baseμ ++ t)) (tupleVal vs)

#guard verdict wμ == "accepted" && WellFormedWeigh wμ
#guard weighOrigins wμ == [("weigh:condition:0:necessary", blockPath ++ ["conditions", "0"]),
  ("weigh:grant:n:user", blockPath ++ ["grants", "0"]), ("weigh:grant:n:user:condition:0", blockPath ++ ["conditions", "0"])]
#guard (μAll.length, assignments.length) == (4, 256) && μAll.all (·.all (·.2 == ["a1", "u2"]))
#guard (μAll.map (outcome · ["a1", "u2"])).count true == 1 && (μAll.filter (outcome · ["a1", "u2"])).map (·.length) == [0]
#guard μAll.all fun t => outcome t ["a2", "u1"] && outcome t ["a1", "u1"] && outcome t ["a2", "u2"]
#guard verdict (wd μd (W [] [⟨.off "n" "operator", .necessary, .binary "trusts" (.var 0) (.var 1)⟩])) ==
  "TypeMismatch: Predicate 'trusts' expects ('assistant', 'user'), received ('user', 'assistant')"
#guard verdict (wd μd (W [] [] [⟨"n", "user", "operator", "trusts"⟩])) == "GrantNotAttributed: trusts, operator"
#guard verdict (wd μd (W [] [⟨.off "n" "operator", .sufficient, trustsF⟩])) ==
  "InvalidInput: condition 0 on a switch must be necessary"

end VE.Weighing.Examples
