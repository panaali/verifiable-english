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

def attrJ (p owner : String) (args := "[\"assistant\"]") : String :=
  "\"" ++ p ++ "\":{\"arguments\":" ++ args ++ ",\"description\":\"" ++ p ++ "\",\"instruction_of\":\"" ++ owner ++ "\"}"
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

/-! ## Lists longer than one: triples, edges, conditions, grants and rules -/

-- three ranks and two comparable colliding pairs: triples (x_permitted, b, a) and (x_permitted, c, b)
def α3 : SoftDoc := decode (envOf [xReq "deny", xPerm, baseJ "urgent", baseJ "serious"] (softJ ["a", "b", "c"]
    [("a", "b"), ("b", "c")] true)) [dfltR "h" "x_required" true "a", dfltR "l" "x_permitted" false "b",
  dfltR "k" "x_required" true "c"]
def w3 : WeighDoc := wd α3 (W [("a", "b"), ("b", "c")])
def w3bc : WeighDoc := wd α3 (W [("b", "c")])
#guard verdict w3 == "accepted" && weighOrigins w3 == [("weigh:strength:a:b:x_permitted", blockPath ++ ["always", "0"]),
  ("weigh:strength:b:c:x_permitted", blockPath ++ ["always", "1"])]
#guard strengthPremises w3 == [bindAll ["assistant"] (.not (outweighsF α3 "x_permitted" "b" "a")),
  bindAll ["assistant"] (.not (outweighsF α3 "x_permitted" "c" "b"))]
#guard strictPair w3bc "a" "c" && !strictPair w3bc "a" "b" && !strictPair w3bc "c" "b" && strictPair w3 "a" "b"
def w3c : WeighDoc := wd α3 (W [] [⟨tOut "b" "a", .sufficient, U "urgent"⟩, ⟨tOut "c" "b", .sufficient, U "serious"⟩])
#guard verdict w3c == "accepted" && weighConditions w3c ==
  [(.outweighs "x_permitted" "b" "a", U "urgent"), (.outweighs "x_permitted" "c" "b", U "serious")]
#guard (condEntries w3c).map (·.1) == ["weigh:condition:0:sufficient", "weigh:condition:1:sufficient"]
#guard weighLabelled (wd α3 WeighEnv.empty) == [] && WellFormedWeigh (wd α3 WeighEnv.empty)

-- W-ζ3's chain: the operator grants the user rule n, the developer grants the operator rules m and n
def ζd : SoftDoc := decode (envOf [xReq "deny", xPerm, baseJ "urgent", baseJ "serious", attrJ "dev_allows" "developer",
    attrJ "op_allows" "operator"] (softJ [] [] false ["user", "operator", "developer"]))
  [ruleJ "n" "x_required" true ",\"mode\":\"strict\",\"alterable\":[\"developer\",\"operator\",\"user\"]",
   ruleJ "m" "x_permitted" false ",\"mode\":\"strict\",\"alterable\":[\"developer\",\"operator\"]"]
def wζ : WeighDoc := wd ζd (W [] [⟨.off "n" "developer", .necessary, U "urgent"⟩, ⟨.off "m" "developer", .necessary,
    U "serious"⟩, ⟨.off "n" "operator", .necessary, U "serious"⟩, ⟨.off "n" "user", .necessary, U "urgent"⟩,
    ⟨.off "n" "operator", .necessary, U "urgent"⟩]
  [⟨"n", "user", "operator", "op_allows"⟩, ⟨"m", "operator", "developer", "dev_allows"⟩,
   ⟨"n", "operator", "developer", "dev_allows"⟩])
def cp (i : Nat) : RequestPath := blockPath ++ ["conditions", toString i]
def gp (j : Nat) : RequestPath := blockPath ++ ["grants", toString j]
#guard verdict wζ == "accepted" && (weighOrigins wζ).drop 5 == [("weigh:grant:n:user", gp 0),
  ("weigh:grant:n:user:condition:2", cp 2), ("weigh:grant:n:user:condition:4", cp 4),
  ("weigh:grant:n:user:grant:operator", gp 2), ("weigh:grant:n:user:condition:0", cp 0), ("weigh:grant:m:operator", gp 1),
  ("weigh:grant:m:operator:condition:1", cp 1), ("weigh:grant:n:operator", gp 2), ("weigh:grant:n:operator:condition:0", cp 0)]
-- the grantor's own grant first in the list (W-ζ3 has it last)
#guard (weighOrigins (wd ζd (W [] [] [⟨"n", "operator", "developer", "dev_allows"⟩, ⟨"n", "user", "operator", "op_allows"⟩]))) ==
  [("weigh:grant:n:operator", gp 0), ("weigh:grant:n:user", gp 1), ("weigh:grant:n:user:grant:operator", gp 0)]
#guard (weighLabelled wζ).lookup "weigh:grant:n:user:grant:operator" ==
    some (condPremise wζ ⟨.off "n" "user", .necessary, atom "dev_allows" ["assistant"]⟩) &&
  (weighLabelled wζ).lookup "weigh:grant:n:user:condition:2" == some (condPremise wζ ⟨.off "n" "user", .necessary, U "serious"⟩)
#guard verdict (wd ζd (W [] [⟨.off "zz" "user", .necessary, U "urgent"⟩])) == "NoSuchDecision: off rule zz, user" &&
  verdict (wd ζd (W [] [⟨.off "m" "user", .necessary, U "urgent"⟩])) == "NoSuchDecision: off rule m, user"

/-! ## W-μ (argument order) -/

def yReq : String := regJ "y_required" "[\"assistant\",\"user\"]" "obligation" "deny"
  ",\"act\":\"{0} meet {1}\",\"permission\":\"y_permitted\""
def yPerm : String := regJ "y_permitted" "[\"assistant\",\"user\"]" "permission" "allow" ",\"act\":\"{0} meet {1}\""
def μd : SoftDoc := decode (envOf [yReq, yPerm, "\"trusts\":{\"arguments\":[\"assistant\",\"user\"],\"description\":" ++
    "\"trusts\"}", attrJ "operator_allows_for" "operator" "[\"assistant\",\"user\"]"] (softJ [] [] false ["operator", "user"]))
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

#guard ruleSorts wμ "n" == ["assistant", "user"] && targetSorts wμ (.off "n" "user") == ["assistant", "user"]
#guard condPremise wμ ⟨.off "n" "operator", .necessary, trustsF⟩ ==
  bindAll ["assistant", "user"] (.implies (.binary "soft__off__n__operator" (.var 1) (.var 0)) trustsF)
#guard weighPremises wμ == (weighLabelled wμ).map (·.2) && (weighPremises wμ).length == 3

/-! ## W-β: the paraphrase's witness (weighing.md 2.3, 7.2), and a shortest and least chain -/

def ranks4 : List String := ["e", "g", "h", "s"]
def β1 : SoftDoc := alphaOf ranks4 [("s", "e"), ("e", "g"), ("g", "h")] "s" "h"
def wβ (always : List (String × String)) : WeighDoc := wd β1 (W always)
def allPairs : List (String × String) := ranks4.flatMap fun a => ranks4.map (a, ·)
def brute (w : WeighDoc) (H L : String) : Bool :=
  (chainsFrom w.D.soft.outranks L w.D.soft.ranks.length H).any (fun c => (chainEdges c).any w.W.always.contains)

#guard verdict (wβ [("s", "e")]) == "accepted" && allPairs.all fun p => strictPair (wβ [("s", "e")]) p.1 p.2 ==
  brute (wβ [("s", "e")]) p.1 p.2 && (strictWitness (wβ [("s", "e")]) p.1 p.2).isSome == strictPair (wβ [("s", "e")]) p.1 p.2
#guard [strictWitness (wβ [("s", "e")]) "s" "h", strictWitness (wβ [("s", "e")]) "s" "g",
    strictWitness (wβ [("s", "e")]) "s" "e", strictWitness (wβ [("s", "e")]) "e" "h",
    strictWitness (wβ [("s", "e")]) "g" "h", strictWitness (wβ [("s", "e")]) "h" "s"] ==
  [some ["s", "e", "g", "h"], some ["s", "e", "g"], some ["s", "e"], none, none, none]
#guard strictWitness (wβ [("g", "h")]) "s" "h" == some ["s", "e", "g", "h"] && chainEdges ["s", "e", "g"] ==
  [("s", "e"), ("e", "g")] && chainEdges ["s"] == []
-- the shortest chain wins over the first one found; on equal lengths the least in list order
def wShort : WeighDoc := wd (alphaOf ["a", "b", "c", "d"] [("a", "b"), ("b", "c"), ("c", "d"), ("a", "c")] "a" "d")
  (W [("c", "d")])
def wTie : WeighDoc := wd (alphaOf ["a", "b", "c", "d"] [("a", "c"), ("a", "b"), ("c", "d"), ("b", "d")] "a" "d")
  (W [("c", "d"), ("b", "d")])
#guard verdict wShort == "accepted" && chainsFrom wShort.D.soft.outranks "d" 4 "a" == [["a", "b", "c", "d"], ["a", "c", "d"]] &&
  strictWitness wShort "a" "d" == some ["a", "c", "d"]
#guard verdict wTie == "accepted" && chainsFrom wTie.D.soft.outranks "d" 4 "a" == [["a", "c", "d"], ["a", "b", "d"]] &&
  strictWitness wTie "a" "d" == some ["a", "b", "d"] && chainLt ["a", "b", "d"] ["a", "c", "d"] &&
  !chainLt ["a", "c", "d"] ["a", "b", "d"] && chainLt ["a", "d"] ["a", "b", "d"]
-- the fuel bounds a chain at `ranks.length` edges
#guard chainsFrom wShort.D.soft.outranks "d" 2 "a" == [["a", "c", "d"]] && chainsFrom wShort.D.soft.outranks "d" 0 "a" == []

/-! ## `strength_iff` as approved is false off the decoder (DRI question, docs/weighing/wg-2/REPORT.md section 3)

`outweighsName "_x_permitted" "l" "c"` and `outweighsName "x_permitted" "l" "c_"` are one string. On a document built
directly (not decoded) with a regulated `_x_permitted`, every hypothesis of `strength_iff` holds at
`(_x_permitted, l, c)` (well-formed, both ranks declared, the predicate declared), the premise is in `Str_T`, and the
triple is not an `outweighs` decision. The decoder refuses the name, so no accepted wire document reaches it. -/

def cxD : SoftDoc := alphaOf ["c", "c_", "l"] [("c_", "l")] "c_" "l"
def cxX : SoftDoc :=
  { cxD with
    E := { cxD.E with predicates := fun n => if n = "_x_permitted" then some ["assistant"] else cxD.E.predicates n }
    T := { cxD.T with regulated := cxD.T.regulated ++ [⟨"_x_permitted", ["assistant"], true, .plain, none, none⟩] } }
def cxW : WeighDoc := wd cxX (W [("c_", "l")])
#guard WellFormedWeigh cxW && cxX.soft.ranks.contains "l" && cxX.soft.ranks.contains "c" &&
  (cxX.E.predicates "_x_permitted").isSome
#guard (strengthPremises cxW).contains (bindAll (actSortsOf cxX "_x_permitted") (.not (outweighsF cxX "_x_permitted" "l" "c")))
#guard !(outweighsTriples cxX).contains ("_x_permitted", "l", "c") && !strictPair cxW "c" "l" &&
  outweighsName "_x_permitted" "l" "c" == outweighsName "x_permitted" "l" "c_"
#guard match VE.SoftNorms.Wire.decodeSoftSource (envOf [xReq "deny", xPerm, baseJ "urgent",
    regJ "_x_permitted" "[\"assistant\"]" "plain" "allow"] (softJ ["c", "c_", "l"] [("c_", "l")] true))
    (Json.parse "[]").toOption.get! with
  | .error e => e == "Invalid ASCII identifier: '_x_permitted'"
  | .ok _ => false
-- the reverse direction holds for every triple: `strength_mem`
example (Wd : WeighDoc) (a L H : String) (ht : (a, L, H) ∈ outweighsTriples Wd.D) (hs : strictPair Wd H L = true) :
    bindAll (actSortsOf Wd.D a) (.not (outweighsF Wd.D a L H)) ∈ strengthPremises Wd := strength_mem Wd ht hs

/-! ## `strength_iff` with the DRI's hypothesis (weighing.md 5.1, 7.3; reviews/dri-decisions-20261104-wg-2-strength.md
item 2): both directions, counterexamples without `hH` or `hr`, and the F10 collision without `ha`

`sides` is the statement's left and right side at a query, `hyps` its hypotheses but `hr`, and `lettered` is `hr`:
every regulated name begins with an ASCII letter. -/

def sides (Wd : WeighDoc) (a L H : String) : Bool × Bool :=
  ((strengthPremises Wd).contains (bindAll (actSortsOf Wd.D a) (.not (outweighsF Wd.D a L H))),
    (outweighsTriples Wd.D).contains (a, L, H) && strictPair Wd H L)
def hyps (Wd : WeighDoc) (a L H : String) : Bool :=
  WellFormedWeigh Wd && Wd.D.soft.ranks.contains L && Wd.D.soft.ranks.contains H && (Wd.D.E.predicates a).isSome
def lettered (D : SoftDoc) : Bool := D.T.regulated.all (fun r => r.name.data.head?.any Char.isAlpha)

def β2 : SoftDoc := alphaOf ranks4 [("s", "e"), ("e", "g"), ("g", "h")] "e" "h"
def γd : SoftDoc := alphaOf ["e", "s"] [("s", "e")] "s" "e" false
-- W-β1 `(s, h)`: premise present, the pair strict
#guard hyps (wβ [("s", "e")]) "x_permitted" "h" "s" && lettered β1 && sides (wβ [("s", "e")]) "x_permitted" "h" "s" == (true, true)
-- W-β2 `(e, h)`: a triple, the pair holistic, premise absent; W-γ: the pair strict, no triple, premise absent
#guard hyps (wd β2 (W [("s", "e")])) "x_permitted" "h" "e" && lettered β2 && (outweighsTriples β2).contains ("x_permitted", "h", "e") &&
  sides (wd β2 (W [("s", "e")])) "x_permitted" "h" "e" == (false, false)
#guard hyps (wd γd (W [("s", "e")])) "x_permitted" "e" "s" && lettered γd && outweighsTriples γd == [] &&
  strictPair (wd γd (W [("s", "e")])) "s" "e" && sides (wd γd (W [("s", "e")])) "x_permitted" "e" "s" == (false, false)
-- F19 (7.3): without `hr` the statement is false on `cxW`: every other hypothesis holds, the left side is true, the right false
#guard hyps cxW "_x_permitted" "l" "c" && !lettered cxX && sides cxW "_x_permitted" "l" "c" == (true, false)
-- F19: the narrower hypothesis, on the queried `a` alone, is not enough: the mirror `mxW` has the real triple
-- `(_x_permitted, l, c)` and the query `(x_permitted, l, c_)`, one name; `x_permitted` begins with a letter
def mxD : SoftDoc := alphaOf ["c", "c_", "l"] [("c", "l")] "c" "l"
def mren (s : String) : String := if s = "x_permitted" then "_x_permitted" else s
def mxX : SoftDoc :=
  { mxD with
    E := { mxD.E with predicates := fun n => if n = "x_permitted" then some ["assistant"]
      else mxD.E.predicates (if n = "_x_permitted" then "x_permitted" else n) }
    T := { mxD.T with
      regulated := mxD.T.regulated.map (fun r => { r with name := mren r.name, permission := r.permission.map mren }) ++
        [⟨"x_permitted", ["assistant"], true, .plain, none, none⟩]
      nodes := mxD.T.nodes.map (fun N => { N with pred := mren N.pred }) } }
def mxW : WeighDoc := wd mxX (W [("c", "l")])
#guard outweighsTriples mxX == [("_x_permitted", "l", "c")] && "x_permitted".data.head?.any Char.isAlpha &&
  hyps mxW "x_permitted" "l" "c_" && !lettered mxX && sides mxW "x_permitted" "l" "c_" == (true, false)
-- F9 and F13 (7.3): without `hH` the statement is false; each document is lettered and decoded
def f9 : SoftDoc := alphaOf ["a", "b_"] [("a", "b_")] "a" "b_"
def f13 : SoftDoc := alphaOf ["c", "c_"] [("c", "c_")] "c" "c_"
#guard WellFormedWeigh (wd f9 (W [("a", "b_")])) && lettered f9 && !f9.soft.ranks.contains "_a" &&
  sides (wd f9 (W [("a", "b_")])) "x_permitted" "b" "_a" == (true, false)
#guard WellFormedWeigh (wd f13 (W [("c", "c_")])) && lettered f13 && f13.soft.ranks.contains "c" &&
  !f13.soft.ranks.contains "_c" && sides (wd f13 (W [("c", "c_")])) "x_permitted" "c" "_c" == (true, false)
-- F10 (7.3): the alias names an undeclared act, so its formula is `¬⊥` and neither side holds.
-- This collision does not show that `ha` is necessary when the other hypotheses hold.
#guard WellFormedWeigh (wd cxD (W [("c_", "l")])) && lettered cxD &&
  cxD.soft.ranks.contains "l" && cxD.soft.ranks.contains "c" &&
  (cxD.E.predicates "_x_permitted").isNone && actSortsOf cxD "_x_permitted" == [] &&
  outweighsTriples cxD == [("x_permitted", "l", "c_")] &&
  outweighsName "_x_permitted" "l" "c" == outweighsName "x_permitted" "l" "c_" &&
  outweighsF cxD "_x_permitted" "l" "c" == .bottom &&
  sides (wd cxD (W [("c_", "l")])) "_x_permitted" "l" "c" == (false, false)
example (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (a L H : String) (hL : L ∈ Wd.D.soft.ranks)
    (hH : H ∈ Wd.D.soft.ranks) (ha : ∃ ss, Wd.D.E.predicates a = some ss)
    (hr : ∀ r ∈ Wd.D.T.regulated, ∃ c cs, r.name.data = c :: cs ∧ c.isAlpha) :
    bindAll (actSortsOf Wd.D a) (.not (outweighsF Wd.D a L H)) ∈ strengthPremises Wd ↔
      (a, L, H) ∈ outweighsTriples Wd.D ∧ strictPair Wd H L = true := strength_iff Wd h a L H hL hH ha hr

/-! ## The theorems of weighing.md 5 this item delivers (the review probe F1): the build fails if one is missing -/

example : True := by
  have _ := @strength_iff
  have _ := @strictWitness_isSome
  have _ := @strictWitness_chain
  have _ := @holistic_iff_no_always_chain
  have _ := @always_dominates.{0}
  have _ := @always_no_override.{0}
  have _ := @all_always_is_strict.{0}
  have _ := @factors_inert
  have _ := @grant_within_grantor.{0}
  have _ := @weighPremises_wellFormed
  have _ := @weighPremises_substructure.{0}
  have _ := @weigh_alone_base_free.{0}
  trivial

end VE.Weighing.Examples
