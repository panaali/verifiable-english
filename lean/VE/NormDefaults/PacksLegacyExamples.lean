import VE.NormDefaults.PacksExamples
import VE.NormDefaults.PacksLegacy
import VE.NormDefaults.PacksLabels
import VE.Rights.Examples
import VE.Readings.UnspecifiedWire
import VE.Defaults.Examples

/-! The premise-pack fixtures over today's sources (docs/spec/premise-packs.md 4): today's rights documents assemble
unchanged, `envX` and `fullEnv` on a real tree, F1, and F1′, the counterexample to the approved
`legacy_labels_nodup` and the act-key hypothesis of its replacement `legacy_labels_nodup_of_actKeys`; the kind
table's legacy rows (2.10); and the norms chain's empty pack list. -/
namespace VE.NormDefaults.Packs.Fixtures
open VE.NormDefaults.Packs

/-! ## Today's sources -/

open VE.Rights.Examples (mu mayPublish noAttack exceptionCite) in
/-- Fixture μ with a sufficient condition on its liberty: two colliding default lines, so its soft pack has an exception
and a coherence premise, and its tree has decision predicates. -/
def muX : VE.Rights.RightsDoc :=
  mu { mayPublish with exception := some ⟨some "unstated", [.top], [], []⟩ } noAttack exceptionCite exceptionCite

open VE.Rights.Examples (alpha gamma gamma7 rho epsilon l29) in
def rightsDocs : List VE.Rights.RightsDoc :=
  [alpha, gamma, gamma7, rho, epsilon, muX, { gamma with limits := [l29, l29] },
   { gamma with limits := [{ l29 with conditions := l29.conditions ++ l29.conditions.take 1 }] }]
def legacyU (R : VE.Rights.RightsDoc) : UDoc := ⟨VE.SoftNorms.soften (VE.Rights.correlate R), []⟩
def legacyPacks (R : VE.Rights.RightsDoc) : List Pack :=
  [VE.NormDefaults.Wire.softPack (legacyU R) (VE.Rights.correlate R), VE.NormDefaults.Wire.rightsPack R]
def legacyLabels (R : VE.Rights.RightsDoc) : List String := (labelledX (legacyPacks R)).map (·.1)
def gen (n : String) : Pack := ⟨"soft", .vocabulary, [(n, [])], [], [], []⟩

-- The sources reach every guard below: μ has soft labels of both kinds, decision names and layer symbols.
#guard legacyLabels muX ==
  ["soft:exception:may-publish:sufficient:0", "soft:coherence:may-publish,no-attack",
   "rights:limitation:l29:publish_about_permitted:necessary:determined_by_law",
   "rights:limitation:l29:publish_about_permitted:necessary:solely_for_permitted_purpose"]
#guard VE.SoftNorms.decisionNames (VE.Rights.correlate muX) == ["soft__excepted__may_publish", "soft__excepted__no_attack"]
#guard VE.Norms.layerNames (fill (legacyU muX)).T == ["publish_about_permitted", "publish_about_required"]

-- Today's rights sources assemble unchanged, soft first, whichever order they are listed in; the soft pack alone too.
#guard (rightsDocs.take 6).all fun R =>
  diag (assemble (legacyU R) 0 (legacyPacks R)) == diag (.ok (legacyPacks R)) &&
  diag (assemble (legacyU R) 0 (legacyPacks R).reverse) == diag (.ok (legacyPacks R)) &&
  diag (assemble (legacyU R) 0 ((legacyPacks R).take 1)) == diag (.ok ((legacyPacks R).take 1))
-- A generated name that the filled tree declares is refused: a decision predicate, a layer symbol (which only
-- `fullEnv` declares, not `envAt (fill U) 0`) and, with `p` unspecified, `unsaid__p` (which only `fill` declares).
#guard (VE.SoftNorms.decisionNames (VE.Rights.correlate muX) ++ VE.Norms.layerNames (fill (legacyU muX)).T).all fun n =>
  diag (assemble (legacyU muX) 0 [gen n]) == s!"InvalidInput: generated name {n} of pack soft is already declared"
#guard diag (assemble ((legacyU muX).switch "publish_about_permitted") 0 [gen "unsaid__publish_about_permitted"]) ==
  "InvalidInput: generated name unsaid__publish_about_permitted of pack soft is already declared"
-- A fresh, prefixed name passes and counts against the vocabulary already used.
#guard diag (assemble (legacyU muX) 0 [gen "soft__fresh"]) == "ok [soft] []" &&
  diag (assemble (legacyU muX) 256 [gen "soft__fresh"]) == "ResourceLimit: vocabulary size"
-- `envX` is the base environment extended by every pack's names; the base predicates stay, the layer symbols do not.
#guard (envX (legacyU muX) [att "attitudes__k__2", ev "date__e"]).predicates "attitudes__k__2" == some ["person"] &&
  (envX (legacyU muX) [att "attitudes__k__2", ev "date__e"]).constants "date__e" == some "person" &&
  (VE.SoftNorms.decisionNames (VE.Rights.correlate muX)).all (fun n =>
    (envX (legacyU muX) [att "attitudes__k__2"]).predicates n == some ["person", "person"]) &&
  (VE.Norms.layerNames (fill (legacyU muX)).T).all (fun n =>
    (envX (legacyU muX) []).predicates n == none && (fullEnv (legacyU muX)).predicates n == some ["person", "person"])
-- The coherence labels are the soft pack's `soft:coherence:` labels.
#guard coherenceLabels (VE.Rights.correlate muX) == ["soft:coherence:may-publish,no-attack"]
#guard (rightsDocs.take 6).all fun R =>
  coherenceLabels (VE.Rights.correlate R) ==
    (legacyLabels R).filter (·.startsWith "soft:coherence:")

-- F1: `WellFormedSoft (correlate R)` and `WellFormedU` hold on a rights document that repeats a limitation (or a
-- condition), yet its labels repeat; `WellFormedRights` refuses it.
#guard (rightsDocs.drop 6).all fun R => VE.SoftNorms.WellFormedSoft (VE.Rights.correlate R) &&
  WellFormedU (legacyU R) && !decide (legacyLabels R).Nodup && !VE.Rights.WellFormedRights R
#guard rightsDocs.all fun R => !VE.Rights.WellFormedRights R || decide (legacyLabels R).Nodup
#guard rightsDocs.all fun R => !VE.SoftNorms.WellFormedSoft (VE.Rights.correlate R) ||
  decide (((VE.NormDefaults.Wire.softLabelledU (legacyU R) (VE.Rights.correlate R)).map (·.1)).Nodup)
#guard (rightsDocs.map VE.Rights.WellFormedRights) == [true, true, true, true, true, true, false, false]

/-! ## 2.10: the kind table's legacy rows

On a source decoded by the real `decodeSoftU` (DF-1a's fixture γ: two colliding default rules), the route's dispatch
`kindCase` answers each of today's four kinds exactly as `layeredCase` does (three answers and one refusal), and any
other kind (`admission`, dispatched earlier by `softCase`; a future provider's kind) is `none`, so `runLayered`'s
refusal stands. -/

def kindJ : Lean.Json := Lean.Json.mkObj [("id", "c1")]
def legacyAnswers (L : VE.NormDefaults.Wire.LayeredU) : List String :=
  (VE.NormDefaults.Wire.legacyKinds ++ ["admission", "attitudes-elaborate"]).map fun k =>
    kindDiag (VE.NormDefaults.Wire.kindCase L "c1" k kindJ)

#guard VE.NormDefaults.Wire.legacyKinds ==
  ["norm-defaults-elaborate", "norm-defaults-conflict", "norm-defaults-status", "norm-defaults-report"]
#guard VE.Defaults.Fixtures.holds VE.Defaults.Fixtures.dγ fun L => L.packs.map (·.id) == ["soft"] &&
  legacyAnswers L == (VE.NormDefaults.Wire.legacyKinds ++ ["admission", "attitudes-elaborate"]).map
    (fun k => kindDiag (VE.NormDefaults.Wire.layeredCase L "c1" k kindJ)) &&
  (legacyAnswers L).map (fun a => if a.startsWith "{" then "answer" else a) ==
    ["answer", "answer", "property not found: model", "answer", "none", "none"] &&
  ((legacyAnswers L).take 4).all (fun a => !a.startsWith "{" || (a.splitOn "\"id\":\"c1\"").length == 2)
-- The rows answer the kind they are named for: the elaborate row's answer is the elaborate answer, the conflict
-- row's the verdict.
#guard VE.Defaults.Fixtures.holds VE.Defaults.Fixtures.dγ fun L =>
  ((legacyAnswers L)[0]!).startsWith "{\"background\":" && (((legacyAnswers L)[1]!).splitOn "\"verdict\":").length == 2

/-! ## F1′: the approved `legacy_labels_nodup` is false

`WellFormedRights` checks neither limitation names nor predicate names for `:` (only the route's JSON environment
decoder applies `VE.Bridge.identifier` to predicate names). With limitations `x` and `x:p` over every line, and act
keys `p:q` and `q`, the label `rights:limitation:<limitation>:<act>:necessary:c` of (`x`, `p:q`) is that of
(`x:p`, `q`). The statement's hypotheses hold and its conclusion fails. Its replacement
`legacy_labels_nodup_of_actKeys` (DRI decision 2026-10-27, item 3) adds that no act key has `:`, which `cx` fails
and the decoded route ensures (`bridge_identifier_sep`). -/

open VE.Rights.Examples (mkRights line strictNode block) in
open VE.Norms.Checks (perm) in
def cx : VE.Rights.RightsDoc :=
  mkRights ["state", "person"] []
    [perm "p:q" ["state", "person"] true "{0} arrest {1}", perm "q" ["state", "person"] true "{0} detain {1}"]
    [] block
    [⟨"r9", "person", .top, [line .claim (strictNode "no-a" "p:q" false), line .claim (strictNode "no-b" "q" false)]⟩]
    [⟨"x", none, none, some "unstated", [⟨"c", true, "c holds", none⟩], []⟩,
     ⟨"x:p", none, none, some "unstated", [⟨"c", true, "c holds", none⟩], []⟩] []

#guard VE.Rights.WellFormedRights cx && WellFormedU (legacyU cx)
#guard legacyLabels cx ==
  ["rights:limitation:x:p:q:necessary:c", "rights:limitation:x:q:necessary:c",
   "rights:limitation:x:p:p:q:necessary:c", "rights:limitation:x:p:q:necessary:c"]
#guard !decide (legacyLabels cx).Nodup
#guard (VE.Rights.condKeys cx).map (·.2.1) == ["p:q", "q", "p:q", "q"]
-- The route's own repeated-label check refuses it (no decoded document reaches this: predicates are identifiers).
#guard diag (assemble (legacyU cx) 0 (legacyPacks cx)) ==
  "InvalidInput: premise label rights:limitation:x:p:q:necessary:c of pack rights is used twice"

-- The act-key hypothesis of `legacy_labels_nodup_of_actKeys`: `cx` fails it; the well-formed sources hold it (their
-- act keys are route identifiers), and their labels are distinct, as the theorem says.
#guard (VE.Rights.condKeys cx).any (·.2.1.toList.contains ':')
#guard (rightsDocs.take 6).all fun R => (VE.Rights.condKeys R).all (fun k => !k.2.1.toList.contains ':' &&
  VE.Bridge.identifier k.2.1) && decide (legacyLabels R).Nodup
#guard (rightsDocs.take 6).any fun R => !(VE.Rights.condKeys R).isEmpty
-- `VE.Bridge.identifier`, the route's check on predicate names, refuses `:` anywhere and accepts its neighbours
-- `9` and `_`; `;` (just past `:`) and the 64-byte budget are refused too.
#guard ["p", "q", "p9", "p_q", "publish_about_permitted", "a" ++ "".pushn '0' 63].all VE.Bridge.identifier
#guard ["p:q", ":", "p:", ":p", "x:p", "p;", "", "P", "9p", "a" ++ "".pushn '0' 64].all (!VE.Bridge.identifier ·)
#guard (["p:q", "x:p", "q", "p_q"].filter VE.Bridge.identifier) == ["q", "p_q"]

end VE.NormDefaults.Packs.Fixtures

namespace VE.Readings.Wire

/-- The norms chain's layered source has the empty pack list (JT-R2), not a soft pack. -/
theorem choiceLayeredG_norms_packs (b : Admitted2) (N : NDoc) (c : Choice)
    (wfc : VE.NormDefaults.WellFormedU (choiceU N c) = true) (hN : N.D = b.D) (hn : normsShaped N.D = true)
    (L : {L : VE.NormDefaults.Wire.LayeredU // L.U = choiceU N c ∧ L.X = choiceX N c ∧
      ∀ a ∈ L.X, a.WellFormed (VE.Norms.envAt (VE.NormDefaults.fill L.U) 0) []})
    (h : choiceLayeredG b N c wfc hN = .ok L) : L.1.packs = [] := by
  unfold choiceLayeredG at h
  rw [dif_pos hn] at h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  cases h
  rfl

end VE.Readings.Wire
