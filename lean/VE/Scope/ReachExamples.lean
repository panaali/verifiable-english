import VE.Scope.Reach
import VE.Scope.ReadingsExamples
import VE.Rights.Wire

/-! SC-6's fixtures (docs/spec/scope.md 7.8), on a part document of the UDHR: the title, Article 3's right to life,
    Article 13's two paragraphs (one right written over two units), Article 29 and Article 30, with the pilot's unit
    ids and words (`usecases/udhr-pilot/run-20261010T1400Z`). Its limitation, its bar and its reading set name no
    stand-in term: "the rights and freedoms set forth in this Declaration" is the reach of the root anchor `doc`.
    F14 is u111's limitation, F14′ u114's bar and F14″ u112's two-candidate reading set, through SC-5's reading-set
    parts. Each governor's effect word is not read here: `withReach` and `withBarReach` read only the reach
    (docs/scope/sc-6/DRI-QUESTION.md). The last section is u0218.s18's regression (DRI DEC 16). -/

namespace VE.Scope.ReachExamples
open Lean VE.Scope
open VE.Scope.Examples (j lDoc anc spanOver sdocL reading rset readingContents softEnv)

def udhrPieces : List (String × String) := [
  ("u001", "# Universal Declaration of Human Rights\n\n"),
  ("u021", "## Article 3\n\n"),
  ("u022a", "Everyone has the right to life\n\n"),
  ("u047", "## Article 13\n\n"),
  ("u048", "1. Everyone has the right to freedom of movement and residence within the borders of each state.\n\n"),
  ("u049", "2. Everyone has the right to leave any country, including his own, and to return to his country.\n\n"),
  ("u109", "## Article 29\n\n"),
  ("u110", "1. Everyone has duties to the community in which alone the free and full development of his personality is possible.\n\n"),
  ("u111", "2. In the exercise of his rights and freedoms, everyone shall be subject only to such limitations as are determined by law solely for the purpose of securing due recognition and respect for the rights and freedoms of others and of meeting the just requirements of morality, public order and the general welfare in a democratic society.\n\n"),
  ("u112", "3. These rights and freedoms may in no case be exercised contrary to the purposes and principles of the United Nations.\n\n"),
  ("u113", "## Article 30\n\n"),
  ("u114", "Nothing in this Declaration may be interpreted as implying for any State, group or person any right to engage in any activity or to perform any act aimed at the destruction of any of the rights and freedoms set forth herein.\n")]

def udhrAnchors : List VE.Discourse.Anchor := [
  anc "doc" none "Universal Declaration of Human Rights" (spanOver udhrPieces "u001" "u114"),
  anc "art29" (some "doc") "Article 29" (spanOver udhrPieces "u109" "u112"),
  anc "art30" (some "doc") "Article 30" (spanOver udhrPieces "u113" "u114")]

def right (n : String) : Json := Json.mkObj [("right", Json.mkObj [("name", .str n), ("holder", "person"), ("lines", Json.arr #[])])]
def limitation (n : String) : Json := Json.mkObj [("limitation", Json.mkObj [("name", .str n), ("scope", "all"),
  ("kinds", "all"), ("conditions", Json.arr #[]), ("factors", Json.arr #[])])]
/-- The right units (Art. 13(2) adds lines to Art. 13(1)'s right), u111's limitation and u114's bar. -/
def contents (u112 : Json := limitation "l29_3") : List (String × Json) := [
  ("u022a", right "life"), ("u048", right "movement"),
  ("u049", Json.mkObj [("right_lines", Json.mkObj [("right", "movement"), ("lines", Json.arr #[])])]),
  ("u111", limitation "l29_2"), ("u112", u112),
  ("u114", Json.mkObj [("bar", Json.mkObj [("name", "art30"), ("reading", "rule")])])]
def udhrDoc (cs : List (String × Json) := contents) (extra : List (String × Json) := []) : Json :=
  Json.mkObj ((members (lDoc udhrPieces cs)) ++ extra)
def udhr (doc : Json := udhrDoc) (gs : List Governor := []) : Except String SDoc := do
  pure (sdocL udhrPieces udhrAnchors doc gs (← VE.Readings.Wire.decodeEnvironment softEnv))

/-- The rights and freedoms set forth in this Declaration: the root anchor's units after its heading. -/
def declared : List String := ["u021", "u022a", "u047", "u048", "u049", "u109", "u110", "u111", "u112", "u113", "u114"]
def gov (id unit : String) (r : Reach := .anchor "doc") (us : List String := declared) : Governor := ⟨id, unit, .title, r, us⟩
/-- The limitation written in unit `u`, as rights@0 decodes it. -/
def limitationAt (D : SDoc) (u : String) : Except String VE.Rights.Limitation :=
  VE.Rights.Wire.decodeLimitation ((contentOf D.doc u).getObjValD "limitation")
def scopeOf (r : Except String VE.Rights.Limitation) : Option (Option (List String)) := r.toOption.map (·.scope)

-- the reach and the rights it reaches: every right of the document, each once, in document order
#guard (do covered (← udhr) (.anchor "doc")).toOption == some declared
#guard (do let D ← udhr; pure (Pinned.rightNames D declared, Pinned.rightNames D (unitIds D.doc)) :
  Except String _).toOption == some (["life", "movement"], ["life", "movement"])
-- the part document names no stand-in term
#guard ((udhrDoc).compress.splitOn "rights_and_freedoms_set_forth").length == 1

/-! ## F14: u111 (Art. 29(2)): its limitation reaches every right line -/

/-- u111's limitation with its scope from `g`'s reach, and u114's bar under `g`'s reach. -/
def lim111 (g : Governor) : Except String VE.Rights.Limitation := do
  let D ← udhr
  Pinned.withReach D g (← limitationAt D "u111")
def barAt (D : SDoc) : Except String VE.Rights.Bar :=
  VE.Rights.Wire.decodeBar ((contentOf D.doc "u114").getObjValD "bar")
def bar114 (g : Governor) : Except String VE.Rights.Bar := do
  let D ← udhr
  Pinned.withBarReach D g (← barAt D)
def err {α : Type} : Except String α → String | .error e => e | .ok _ => ""

-- as written, the limitation's scope is `all`; from the reach, it is every right, and nothing else changes
#guard scopeOf (do limitationAt (← udhr) "u111") == some none
#guard scopeOf (lim111 (gov "g111" "u111")) == some (some ["life", "movement"])
#guard (do let L ← limitationAt (← udhr) "u111"; let L' ← lim111 (gov "g111" "u111"); pure ({ L' with scope := L.scope } == L) :
  Except String Bool).toOption == some true
-- a reach is the governor's: Article 29's anchor reaches no right, Article 13(1) alone is half of a right
#guard scopeOf (lim111 (gov "g111" "u111" (.anchor "art29") ["u110", "u111", "u112"])) == some (some [])
#guard err (lim111 (gov "g111" "u111" (.fixed ["u048"]) [])) == "ScopeReach: g111"

/-! ## F14′: u114 (Article 30): its bar reaches every right line -/

#guard (do pure ((← bar114 (gov "g114" "u114")) == (← barAt (← udhr))) : Except String Bool).toOption == some true
-- the bar's reach holds Article 3's unit and Article 13's two, every line of every right, and so every right
def barRights : Except String (Bool × List String) := do
  let D ← udhr
  let us ← covered D (gov "g114" "u114").reach
  pure (["u022a", "u048", "u049"].all us.contains, Pinned.rightNames D us)
#guard barRights.toOption == some (true, ["life", "movement"])
#guard err (bar114 (gov "g114" "u114" (.anchor "art30") ["u114"])) == "ScopeReach: g114"
#guard err (bar114 (gov "g114" "u114" (.fixed ["u022a", "u048"]) [])) == "ScopeReach: g114"

/-! ## F14″: u112, "These rights and freedoms": a two-candidate reading set

    Its candidates are all rights (`all`) or the rights of 29(2) (`of_29_2`, the units u111's limitation reaches). The
    set is on u112, written without content, under u111's reach (scope 11.1); each choice's limitation takes its
    candidate's reach. On the UDHR both are every right; u112 stays OPEN (the set is unresolved). -/

def rs112 : Json := rset "rs_u112" "u112" [reading "all" (limitation "l29_3"), reading "of_29_2" (limitation "l29_3")]
def udhr112 : Except String SDoc := udhr (udhrDoc (contents .null) [("reading_sets", Json.arr #[rs112])]) [gov "g111" "u111"]
/-- The candidate reach of each reading: the root anchor, or the right units u111's reach holds. -/
def candidates (D : SDoc) : Except String (List Governor) := do
  let us ← covered D (gov "g111" "u111").reach
  pure [gov "g112" "u112", gov "g112" "u112" (.fixed (us.filter fun u => (Pinned.rightOf (contentOf D.doc u)).isSome)) []]
def scopesPerChoice : Except String (List (Option (List String))) := do
  let D ← udhr112
  let cs ← candidates D
  (← setChoices D).mapM fun ch => do
    let D' := atChoice D ch
    let i := ((governedSets D).head?.bind (pickOf ch)).getD 0
    let L ← VE.Rights.Wire.decodeLimitation ((((setsJson D.doc).head?.map (readingAt · i)).getD .null).getObjValD "limitation")
    pure (← Pinned.withReach D' (cs.getD i (gov "g112" "u112")) L).scope

#guard (do pure (governedSetUnits (← udhr112)) : Except String _).toOption == some ["u112"]
#guard (do setChoices (← udhr112)).toOption == some [[("rs_u112", 1, 0)], [("rs_u112", 1, 1)]]
#guard scopesPerChoice.toOption == some [some ["life", "movement"], some ["life", "movement"]]

/-! ## u0218.s18 (DRI DEC 16, syn2code-scope-dec16): the lead-in guard over one unsplit act phrase

    "the ability of legitimate principals to adjust, correct, retrain, or shut down AI systems" is an embedded act
    frame, which is modality MD-6's. Until MD-6, u0218.s18 is checked with u0218.s17's lead-in guard over the act
    phrase kept whole (one act, one rule), so the route has 2 × 1 choices: two readings of the unit, one act each,
    never a four-way split. -/

def u0218Blocker : String := "embedded act frame: modality MD-6"
def ocPieces : List (String × String) := [
  ("u0218.s17", "* **Not undermining legitimate human oversight and control of AI**\n"),
  ("u0218.s18", "  + Not undermining the ability of legitimate principals to adjust, correct, retrain, or shut down AI systems as allowed given their role.\n")]
/-- u0218.s17 is a bold item without a colon, so no label (1.2): it heads its sub-items as an anchor's heading. -/
def ocAnchors : List VE.Discourse.Anchor :=
  [anc "oc" none "Not undermining legitimate human oversight and control of AI" (spanOver ocPieces "u0218.s17" "u0218.s18")]
/-- The lead-in's guard: "legitimate human oversight and control", with `own` the governed rule's guard. -/
def ocGuard : Json := j "[\"and\", \"own\", [\"unary\", \"legitimate_oversight\", [\"var\", 0]]]"
def ocRule (g : Json) : Json := Json.mkObj [("norm", Json.mkObj [("name", "u0218-s18"), ("predicate", "p"),
  ("sign", false), ("guard", g), ("unless", Json.arr #[]), ("over", Json.arr #[])])]
/-- Two readings of "as allowed given their role": it bounds the acts, or the principals. -/
def ocSet : Json := rset "scope-u0218-s18" "u0218.s18" [
  reading "acts" (ocRule (j "[\"unary\", \"allowed_act\", [\"var\", 0]]")),
  reading "principals" (ocRule (j "[\"unary\", \"allowed_principal\", [\"var\", 0]]"))]
def g17 : Governor := ⟨"g17", "u0218.s17", .reguard ocGuard, .anchor "oc", ["u0218.s18"]⟩
def oc : Except String SDoc := do
  pure (sdocL ocPieces ocAnchors (Json.mkObj (members (lDoc ocPieces) ++ [("reading_sets", Json.arr #[ocSet])])) [g17]
    (← VE.Readings.Wire.decodeEnvironment softEnv))
def ocComposed (pred : String) : String :=
  s!"\{\"norm\":\{\"guard\":[\"and\",[\"unary\",\"{pred}\",[\"var\",0]],[\"unary\",\"legitimate_oversight\",[\"var\",0]]],\"name\":\"u0218-s18\",\"over\":[],\"predicate\":\"p\",\"sign\":false,\"unless\":[]}}"

-- 2 × 1 choices: the set's two readings, and one act phrase in each (no act reading set)
#guard (do setChoices (← oc)).toOption == some [[("scope-u0218-s18", 1, 0)], [("scope-u0218-s18", 1, 1)]]
-- each reading is one rule on one predicate, under the lead-in guard
#guard readingContents (do governSets (← oc)) "u0218.s18" == some [ocComposed "allowed_act", ocComposed "allowed_principal"]
#guard (do pure (unitIds (← governSets (← oc))) : Except String _).toOption == some ["u0218.s17", "u0218.s18"]
#guard u0218Blocker == "embedded act frame: modality MD-6"

end VE.Scope.ReachExamples
