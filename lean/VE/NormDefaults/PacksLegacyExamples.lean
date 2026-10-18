import VE.NormDefaults.PacksExamples
import VE.NormDefaults.PacksLegacy
import VE.Rights.Examples
import VE.Readings.UnspecifiedWire

/-! The premise-pack fixtures over today's sources (docs/spec/premise-packs.md 4): today's rights documents assemble
unchanged, `envX` and `fullEnv` on a real tree, F1, and F1′, the counterexample to the approved
`legacy_labels_nodup`; and the norms chain's empty pack list. -/
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

/-! ## F1′: the approved `legacy_labels_nodup` is false

`WellFormedRights` checks neither limitation names nor predicate names for `:` (only the route's JSON environment
decoder applies `VE.Bridge.identifier` to predicate names). With limitations `x` and `x:p` over every line, and act
keys `p:q` and `q`, the label `rights:limitation:<limitation>:<act>:necessary:c` of (`x`, `p:q`) is that of
(`x:p`, `q`). The statement's hypotheses hold and its conclusion fails; its repair is a DRI decision. -/

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
