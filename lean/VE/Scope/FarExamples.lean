import VE.Scope.Examples

/-! SC-4's fixtures (docs/spec/scope.md 7.6): far precedence (F11, F11-a, F11-y, F11′, F11-u, F11″) through `govern`,
    and the forward declarations (F12, F12-f, F12-f0) through `forwardCheck` and `govern`, each refusal with its exact
    text; the bound on the declarations (257 refused, 256 admitted); and F-raw-edges, the counterfixture to 5.6's
    `precedes_edges` and `yields_edges` on a tree no JSON parser builds. F15 is a candidate, not a fixture (7.6). -/

namespace VE.Scope.FarExamples
open Lean VE.Scope
open VE.Scope.Examples (j lDoc anc spanOver sdocL overOf errorOf same rawJ nd)

/-- A unary `p` and a unary `q`, both regulated (the soft chain's environment). -/
def farEnv : Json := j "{\"language\": \"ve.core@0.2\", \"profiles\": [\"norms@0\", \"readings@1\", \"relational-fol@0\", \"soft-norms@0\"], \"spec_revision\": \"ve-v0.2-expand2-2026-09-25\", \"vocabulary\": {\"sorts\": {\"person\": {\"description\": \"p\"}}, \"predicates\": {\"p\": {\"arguments\": [\"person\"], \"description\": \"p\", \"regulated\": {\"role\": \"plain\", \"default\": \"allow\"}}, \"q\": {\"arguments\": [\"person\"], \"description\": \"q\", \"regulated\": {\"role\": \"plain\", \"default\": \"allow\"}}}, \"constants\": {}}}"
def rule (n pred : String) (sign : Bool := false) (over : List String := []) : Json :=
  Json.mkObj [("norm", Json.mkObj [("name", .str n), ("predicate", .str pred), ("sign", .bool sign),
    ("guard", toJson ["top"]), ("unless", Json.arr #[]), ("over", toJson over)])]
/-- `govern` on the layout of `pieces` under `anchors`, with the block's forward declarations `fs`. -/
def govW (pieces : List (String × String)) (anchors : List VE.Discourse.Anchor) (doc : Json) (gs : List Governor)
    (fs : List (String × String × String) := []) : Except String Json := do
  govern { sdocL pieces anchors doc gs (← VE.Readings.Wire.decodeEnvironment farEnv) with forwards := fs }

/-! ## F11: "Notwithstanding section 3, every operator may share." on r9, outside section 3 -/

def farPieces : List (String × String) := [
  ("s9", "Notwithstanding section 3, every operator may share.\n\n"),
  ("s3.h", "## Section 3\n\n"),
  ("s3.a", "Every operator must not share.\n\n"),
  ("s3.b", "Every user may not ask.\n")]
def farAnchors : List VE.Discourse.Anchor := [anc "doc" none "Far" (spanOver farPieces "s9" "s3.b"),
  anc "sec3" (some "doc") "Section 3" (spanOver farPieces "s3.h" "s3.b")]
/-- r9 and r3a are on `p`, r3b on `q`. -/
def farRules (r3a : Json := rule "r3a" "p") : List (String × Json) :=
  [("s9", rule "r9" "p" true), ("s3.a", r3a), ("s3.b", rule "r3b" "q")]
def far (gs : List Governor) (cs : List (String × Json) := farRules) : Except String Json :=
  govW farPieces farAnchors (lDoc farPieces cs) gs
def g11 : Governor := ⟨"g11", "s9", .precedes, .rules ["r3a", "r3b"], ["s3.a", "s3.b"]⟩
def overs (r : Except String Json) : List (Option String) := ["s9", "s3.a", "s3.b"].map (overOf r)

-- F11: r9's `over` gains the same-predicate rule r3a; r3b (on `q`) adds nothing
#guard overs (far [g11]) == [some "[\"r3a\"]", some "[]", some "[]"]
-- F11-a: reached by `anchor` from outside section 3 (end to end); as `yields`, r3a's `over` gains r9; a narrowing
-- over the same anchor on the same unit is refused: a unary governor sits on the anchor's heading
def g11a : Governor := {g11 with reach := .anchor "sec3"}
def g11n : Governor := ⟨"g11n", "s9", .carveOut (j "[\"top\"]"), .anchor "sec3", ["s3.a", "s3.b"]⟩
#guard (overs (far [g11a]), overs (far [{g11a with effect := .yields}]), errorOf (far [g11n])) ==
  ([some "[\"r3a\"]", some "[]", some "[]"], [some "[]", some "[\"r9\"]", some "[]"],
   "ManifestMismatch: scope.governors.g11n.unit")
-- F11-y: the same as `yields`
#guard overs (far [{g11 with effect := .yields}]) == [some "[]", some "[\"r9\"]", some "[]"]
-- F11′: the same over r3b only; F11-u: an unknown rule name
#guard errorOf (far [{g11 with reach := .rules ["r3b"], units := ["s3.b"]}]) == "ScopeNoEffect: g11"
#guard errorOf (far [{g11 with reach := .rules ["r7"], units := []}]) == "ScopeUnknownRule: r7"
-- F11″: r3a is written over r9, so the edge r9 → r3a closes a cycle: W1's own precedence nodes (name, `over`) of
-- the governed rules give W1's `DependencyCycle`, unchanged; without the governor the rules are acyclic
def w1Order (r : Except String Json) : String :=
  match (do
    let out ← r
    let re ← VE.Readings.Wire.decodeEnvironment farEnv
    let ns ← ["s9", "s3.a", "s3.b"].mapM fun u => VE.Readings.Wire.decodeNorm re ((normOf (contentOf out u)).getD .null)
    VE.Route.dependencyOrder (ns.map fun N => ⟨N.name, N.over⟩) : Except String (List String)) with
  | .ok _ => "acyclic"
  | .error e => e
def cyclic : List (String × Json) := farRules (rule "r3a" "p" false ["r9"])
#guard (w1Order (far [g11] cyclic), w1Order (govW farPieces farAnchors (lDoc farPieces cyclic) [] [])) ==
  ("DependencyCycle: r3a, r9", "acyclic")

/-! ## F12: u0047.s05–s06, a forward announcement whose exceptions the source never identifies -/

def u0047 : List (String × String) := [
  ("u0047.s05", "If Anthropic asks Claude to do something it thinks is wrong, Claude is not required to comply. "),
  ("u0047.s06", "That said, we discuss some exceptions to this in the section on “[broad safety](https://docs.google.com/document/d/1jXbcFqsI5nxiKcTcx_YezX_-78jfOQ4IQim7zAnPYq8/edit?tab=t.0#heading=h.k9yfkhnapmlg)” below. ")]
/-- The pinned translation's two units: no content, UNFORMALISED (`meaning: {"unformalised": "norms"}`). -/
def u0047Doc : Json := Json.mkObj [("units", .arr ((VE.Scope.Examples.layoutOf u0047).map fun x => Json.mkObj
  [("id", .str x.id), ("support", .str "none"), ("kind", toJson ["unformalised", "norms"]),
   ("meaning", Json.mkObj [("unformalised", .str "norms")])]).toArray)]
def u0047Anchors : List VE.Discourse.Anchor := [anc "doc" none "Constitution" (spanOver u0047 "u0047.s05" "u0047.s06")]
-- no rule is named, so nothing is recorded: the document is returned as written (u0047.s06 keeps no content and is
-- UNFORMALISED, `meaning: {"unformalised": "norms"}`, with no residual: `UnresolvedScope` is SC-5's, spec 1612, and is
-- not built; `VE.Service.ScopeExamples.u0047Statuses` checks the status); a declaration guessed for it is refused,
-- never a guessed edge
#guard same (govW u0047 u0047Anchors u0047Doc []) u0047Doc
#guard errorOf (govW u0047 u0047Anchors u0047Doc [] [("u0047.s06", "broad-safety", "doc")]) ==
  "ScopeForward: u0047.s06: rule broad-safety has no later exception in doc"
-- the pinned spans [26947, 27042] and [27042, 27251] are 95 and 209 bytes: the same units
#guard (VE.Scope.Examples.layoutOf u0047).map (fun x => x.span.2 - x.span.1) == [95, 209]

/-! ## F12-f, F12-f0: "Rule r1 has exceptions stated later in this section." on h.s02 -/

def hPieces : List (String × String) := [
  ("h.s01", "Every operator may share when the user asks.\n\n"),
  ("h.s02", "Rule r1 has exceptions stated later in this section.\n\n"),
  ("h.s03", "Every operator must not share.\n\n"),
  ("h.s04", "Every operator may share in an emergency.\n\n"),
  ("t.s01", "Every operator may share when the law requires it.\n")]
def hAnchors : List VE.Discourse.Anchor := [anc "doc" none "Doc" (spanOver hPieces "h.s01" "t.s01"),
  anc "sec" (some "doc") "Sharing" (spanOver hPieces "h.s01" "h.s04")]
/-- With `later`, h.s04's rule names r1 in its `over`; without, the only exceptions are earlier (h.s01) or outside
    the section (t.s01). -/
def hDoc (later : Bool) : Json := lDoc hPieces [("h.s01", rule "r0" "p" true ["r1"]), ("h.s03", rule "r1" "p"),
  ("h.s04", rule "r2" "p" true (if later then ["r1"] else [])), ("t.s01", rule "r3" "p" true ["r1"])]
def hD (later : Bool) : Except String SDoc := do
  pure { sdocL hPieces hAnchors (hDoc later) [] (← VE.Readings.Wire.decodeEnvironment farEnv) with
    forwards := [("h.s02", "r1", "sec")] }
def checkF (later : Bool) : String := match (do forwardCheck (← hD later) "h.s02" "r1" "sec") with
  | .ok () => "ok"
  | .error e => e

-- F12-f: the later units of `sec` are h.s03 and h.s04; with h.s04's exception `.ok ()`, without it the earlier one
-- (h.s01) and the one outside the section (t.s01) do not count
#guard (do pure (laterUnitsIn (← hD true) "sec" "h.s02") : Except String _).toOption == some ["h.s03", "h.s04"]
#guard (checkF true, checkF false) == ("ok", "ScopeForward: h.s02: rule r1 has no later exception in sec")
-- F12-f0: the failing declaration in a document with no governor is refused by `govern` (`admitBlock` step 9),
-- never the document; with a graph governor that adds an edge too; the passing one returns the document as written
def fwd : List (String × String × String) := [("h.s02", "r1", "sec")]
def gE : Governor := ⟨"gE", "h.s04", .precedes, .rules ["r1"], ["h.s03"]⟩
#guard [errorOf (govW hPieces hAnchors (hDoc false) [] fwd),
  errorOf (govW hPieces hAnchors (hDoc false) [gE] fwd)] ==
  ["ScopeForward: h.s02: rule r1 has no later exception in sec", "ScopeForward: h.s02: rule r1 has no later exception in sec"]
#guard same (govW hPieces hAnchors (hDoc true) [] fwd) (hDoc true)
-- step 9 comes after step 8, and the declarations are checked in block order
#guard [errorOf (govW hPieces hAnchors (hDoc false) [⟨"gU", "h.s09", .title, .anchor "sec", []⟩] fwd),
  errorOf (govW hPieces hAnchors (hDoc true) [] (fwd ++ [("h.s03", "r2", "sec"), ("h.s02", "r9", "sec")]))] ==
  ["ScopeUnknownUnit: h.s09", "ScopeForward: h.s03: rule r2 has no later exception in sec"]
-- the bound (step 1): 256 declarations are checked, 257 are `ResourceLimit` (UNKNOWN), before any is read
#guard [errorOf (govW hPieces hAnchors (hDoc true) [] (List.replicate 256 ("h.s02", "r1", "sec"))),
  errorOf (govW hPieces hAnchors (hDoc true) [] (List.replicate 257 ("h.s02", "r9", "sec")))] ==
  ["ok", "ResourceLimit: scope forward declarations"]
-- the bound is step 1, after the governors' and list names' and before a repeated governor id (step 2)
#guard [errorOf (govW hPieces hAnchors (hDoc true) [gE, gE] (List.replicate 257 ("h.s02", "r1", "sec"))),
  errorOf (govW hPieces hAnchors (hDoc true) (List.replicate 257 gE) (List.replicate 257 ("h.s02", "r1", "sec")))] ==
  ["ResourceLimit: scope forward declarations", "ResourceLimit: scope governors"]

/-! ## F-raw-edges (this item's statement gate, a counterfixture to 5.6's `precedes_edges` and `yields_edges`):
    as in F-raw (`Examples.lean`), a unit object no JSON parser builds loses its `id` when `govern` writes its
    content, so every premise holds and the governed unit's content is not found. The two statements need
    `JsonWF D.doc`, as 5.1's do (spec 11.3's `Pinned.JsonWF`). -/

/-- r9's unit (or r3a's) as an unbalanced tree whose `id` sits below `content`'s right child. -/
def rawAt (u : String) : Json :=
  lDoc farPieces farRules |>.setObjVal! "units" (.arr ((unitsOf (lDoc farPieces farRules)).map fun x =>
    if idOf x == u then rawJ (nd "kind" "rule" (nd "content" (x.getObjValD "content") .leaf (nd "c2" "C" .leaf (nd "id" (.str u)))))
    else x).toArray)
/-- The premises of `precedes_edges` (or `yields_edges`) on `g`, `v`, and whether the conclusion's unit has a norm. -/
def edgePremises (doc : Json) (g : Governor) (v w : String) : Except String (List Bool) := do
  let D := sdocL farPieces farAnchors doc [g] (← VE.Readings.Wire.decodeEnvironment farEnv)
  let out ← govern D
  let t ← ruleTable D
  let us ← covered D g.reach
  let some N := t.lookup g.unit | throw "no N"
  let some M := t.lookup v | throw "no M"
  pure [jsonWF? doc, us.contains v, M.pred == N.pred, M.name != N.name, (normOf (contentOf out w)).isSome]
#guard [edgePremises (rawAt "s9") g11 "s3.a" "s9", edgePremises (rawAt "s3.a") {g11 with effect := .yields} "s3.a" "s3.a",
  edgePremises (lDoc farPieces farRules) g11 "s3.a" "s9"].map (·.toOption) ==
  [some [false, true, true, true, false], some [false, true, true, true, false], some [true, true, true, true, true]]

end VE.Scope.FarExamples
