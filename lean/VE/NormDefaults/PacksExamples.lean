import VE.NormDefaults.PacksLegacy
import VE.Rights.Examples
import VE.Readings.UnspecifiedWire

/-! The acceptance fixtures of premise packs (docs/spec/premise-packs.md 4: A1–A8, F1, and F1′, the counterexample to
the approved `legacy_labels_nodup`). A9′ reads the response shape, so it sits with the encoder theorem
(`ResponseShape/Encoders/NormDefaults.lean`). -/
namespace VE.NormDefaults.Packs.Fixtures
open VE.NormDefaults.Packs

/-- An author environment: `person`, the predicate `helps`, the author name `attitudes__knows__1` (fixture A4) and the
author constant `date__d`. -/
def E : VE.Environment :=
  ⟨["person"], fun n => if n == "helps" || n == "attitudes__knows__1" then some ["person"] else none,
   fun n => if n == "date__d" then some "person" else none⟩

/-- The fixtures' provider rows (attitudes AT-2, events ET-4 add theirs in their own batches). -/
def fixturePrefixes : List (String × String) := [("attitudes", "attitudes__"), ("events", "date__")]

/-- The prefix table with the two provider rows the fixtures need. -/
def P : List (String × String) := reservedPrefixes ++ fixturePrefixes

def φ : VE.Formula := .top

def soft : Pack := ⟨"soft", .constraint, [], [],
  [("soft:exception:r1:sufficient:0", φ), ("soft:coherence:r1,r2", φ)], []⟩
def rights : Pack := ⟨"rights", .constraint, [], [], [("rights:limitation:l1:act:necessary:c1", φ)], []⟩
def weighing : Pack := ⟨"weighing", .constraint, [], [], [("weigh:strength:a:b:x_permitted", .bottom)], []⟩

def diag : Except String (List Pack) → String
  | .ok qs => "ok " ++ toString (qs.map (·.id)) ++ " " ++ toString ((labelledX qs).map (·.1))
  | .error e => e

-- A1: today's lists, in either order, give today's X order (soft, then rights).
#guard diag (assembleIn P E 3 [soft, rights]) ==
  "ok [soft, rights] [soft:exception:r1:sufficient:0, soft:coherence:r1,r2, rights:limitation:l1:act:necessary:c1]"
#guard diag (assembleIn P E 3 [rights, soft]) == diag (assembleIn P E 3 [soft, rights])
#guard diag (assembleIn P E 3 [weighing, soft]) ==
  "ok [soft, weighing] [soft:exception:r1:sufficient:0, soft:coherence:r1,r2, weigh:strength:a:b:x_permitted]"

-- A2: a repeated id.
#guard diag (assembleIn P E 3 [soft, rights, soft]) == "InvalidInput: premise pack soft is given twice"

-- A3: a repeated label, within one pack and across two.
#guard diag (assembleIn P E 3 [{ soft with labelled := soft.labelled ++ [("soft:coherence:r1,r2", φ)] }]) ==
  "InvalidInput: premise label soft:coherence:r1,r2 of pack soft is used twice"
#guard diag (assembleIn P E 3 [soft, { weighing with labelled := [("soft:coherence:r1,r2", φ)] }]) ==
  "InvalidInput: premise label soft:coherence:r1,r2 of pack weighing is used twice"

-- A4: a generated name that E declares (a predicate or a constant), that another pack declares, or that lacks its
-- prefix.
def att (n : String) : Pack := ⟨"attitudes", .vocabulary, [(n, ["person"])], [], [], [(n, ["environment"])]⟩
def ev (n : String) : Pack := ⟨"events", .constraint, [], [(n, "person")], [], [(n, ["environment"])]⟩
#guard diag (assembleIn P E 3 [att "attitudes__knows__1"]) ==
  "InvalidInput: generated name attitudes__knows__1 of pack attitudes is already declared"
#guard diag (assembleIn P E 3 [att "helps"]) == "InvalidInput: generated name helps of pack attitudes is already declared"
#guard diag (assembleIn P E 3 [ev "date__d"]) == "InvalidInput: generated name date__d of pack events is already declared"
#guard diag (assembleIn P E 3 [att "shared__x", ev "shared__x"]) ==
  "InvalidInput: generated name shared__x of pack events is declared twice"
#guard diag (assembleIn P E 3 [att "shared__x"]) ==
  "InvalidInput: a generated name of pack attitudes lacks its reserved prefix"

-- A4′: fresh, prefixed names pass, in packOrder, and extend the environment.
#guard diag (assembleIn P E 3 [ev "date__e", att "attitudes__k__2", soft]) ==
  "ok [soft, attitudes, events] [soft:exception:r1:sufficient:0, soft:coherence:r1,r2]"
#guard (extendEnv E [("attitudes__k__2", ["person"])] [("date__e", "person")]).predicates "attitudes__k__2" ==
  some ["person"]
#guard (extendEnv E [("attitudes__k__2", ["person"])] [("date__e", "person")]).constants "date__e" == some "person"
#guard (extendEnv E [("attitudes__k__2", ["person"])] []).predicates "helps" == some ["person"]

-- A5: the empty pack list.
#guard diag (assembleIn P E 3 []) == "ok [] []"
#guard X [] = []

-- A6: an unknown id, and the vocabulary limit (the prefix rows of a provider are added by its batch).
#guard diag (assembleIn P E 3 [{ soft with id := "acts" }]) == "InvalidInput: unknown premise pack acts"
#guard diag (assembleIn P E 257 []) == "ResourceLimit: vocabulary size"
#guard diag (assembleIn P E 256 []) == "ok [] []"
#guard diag (assembleIn P E 254 [att "attitudes__k__2", ev "date__e"]) == "ok [attitudes, events] []"
#guard diag (assembleIn P E 255 [att "attitudes__k__2", ev "date__e"]) == "ResourceLimit: vocabulary size"

-- A7: diagnostics. Legacy lists keep today's text; a new combination names the pack and the label.
def holds (a : VE.Formula) : Bool := a != .bottom
#guard packFault [soft, rights] (fun a => a != φ) == "InvalidModel(soft): the model violates a background premise"
#guard packFault [soft, { rights with labelled := [("rights:limitation:l1:act:necessary:c1", .bottom)] }] holds ==
  "InvalidModel(rights): the model violates a background premise"
#guard packFault [soft] (fun a => a != φ) == "InvalidModel(soft): the model violates a background premise"
#guard packFault [soft, weighing] holds ==
  "InvalidModel(weighing): the model violates a background premise: weigh:strength:a:b:x_permitted"
#guard firstFailing [soft, weighing] holds == some ("weighing", "weigh:strength:a:b:x_permitted")
#guard firstFailing [soft, rights] holds == none

-- A8: packPremises and the collision witness's X.
#guard (packPremises [soft, rights] "rights").map (·.1) == ["rights:limitation:l1:act:necessary:c1"]
#guard (packPremises [soft] "rights").isEmpty
#guard xWithout [soft, weighing] ["soft:coherence:r1,r2"] = [φ, .bottom]

-- A9 (pk-1's part): today's two arrays on every list, and today's soft array JSON.
#guard (elaborateArrays [soft, rights]).map (·.1) == ["soft", "rights"]
#guard (elaborateArrays []).map (·.1) == ["soft", "rights"]
#guard (elaborateArrays [soft, weighing, ev "date__e"]).map (·.1) == ["soft", "rights"]
#guard ((elaborateArrays [soft, rights]).lookup "soft").map (·.compress) ==
  some "[{\"ast\":[\"top\"],\"label\":\"soft:exception:r1:sufficient:0\"},{\"ast\":[\"top\"],\"label\":\"soft:coherence:r1,r2\"}]"
#guard ((elaborateArrays [soft, rights]).lookup "rights").map (·.compress) ==
  some "[{\"ast\":[\"top\"],\"label\":\"rights:limitation:l1:act:necessary:c1\"}]"

-- The reserved prefixes are pairwise disjoint (no prefix begins another), and their owners.
#guard reservedPrefixes.all fun (o, x) => reservedPrefixes.all fun (o', y) => o == o' || !x.startsWith y
#guard ["soft__x", "rights__x", "unsaid__x"].all reserved && !["helps", "soft_x", "attitudes__x"].any reserved
#guard ownPrefix soft "soft__x" && !ownPrefix soft "rights__x" && !ownPrefix weighing "soft__x"

/-! ## Today's sources -/

open VE.Rights.Examples (alpha gamma gamma7 rho epsilon l29) in
def rightsDocs : List VE.Rights.RightsDoc :=
  [alpha, gamma, gamma7, rho, epsilon, { gamma with limits := [l29, l29] },
   { gamma with limits := [{ l29 with conditions := l29.conditions ++ l29.conditions.take 1 }] }]
def legacyU (R : VE.Rights.RightsDoc) : UDoc := ⟨VE.SoftNorms.soften (VE.Rights.correlate R), []⟩
def legacyPacks (R : VE.Rights.RightsDoc) : List Pack :=
  [VE.NormDefaults.Wire.softPack (legacyU R) (VE.Rights.correlate R), VE.NormDefaults.Wire.rightsPack R]
def legacyLabels (R : VE.Rights.RightsDoc) : List String := (labelledX (legacyPacks R)).map (·.1)

-- Today's rights sources assemble unchanged, soft first, whichever order they are listed in; the soft pack alone too.
#guard (rightsDocs.take 5).all fun R =>
  diag (assemble (legacyU R) 0 (legacyPacks R)) == diag (.ok (legacyPacks R)) &&
  diag (assemble (legacyU R) 0 (legacyPacks R).reverse) == diag (.ok (legacyPacks R)) &&
  diag (assemble (legacyU R) 0 ((legacyPacks R).take 1)) == diag (.ok ((legacyPacks R).take 1))
-- A generated name that the filled tree declares (a soft decision predicate of `fullEnv`) is refused.
#guard (VE.SoftNorms.decisionNames (VE.Rights.correlate VE.Rights.Examples.gamma)).head?.all fun n =>
  diag (assemble (legacyU VE.Rights.Examples.gamma) 0 [⟨"soft", .vocabulary, [(n, [])], [], [], []⟩]) ==
    s!"InvalidInput: generated name {n} of pack soft is already declared"
-- `envX` is the base environment extended by every pack's names; the base predicates stay.
#guard (envX (legacyU VE.Rights.Examples.gamma) [att "attitudes__k__2", ev "date__e"]).predicates "attitudes__k__2" ==
    some ["person"] &&
  (envX (legacyU VE.Rights.Examples.gamma) [att "attitudes__k__2", ev "date__e"]).constants "date__e" == some "person" &&
  (VE.SoftNorms.decisionNames (VE.Rights.correlate VE.Rights.Examples.gamma)).all fun n =>
    (envX (legacyU VE.Rights.Examples.gamma) [att "attitudes__k__2"]).predicates n ==
      (VE.Norms.envAt (fill (legacyU VE.Rights.Examples.gamma)) 0).predicates n
-- The coherence labels are the soft pack's `soft:coherence:` labels.
#guard (rightsDocs.take 5).all fun R =>
  coherenceLabels (VE.Rights.correlate R) ==
    (legacyLabels R).filter (·.startsWith "soft:coherence:")

-- F1: `WellFormedSoft (correlate R)` and `WellFormedU` hold on a rights document that repeats a limitation (or a
-- condition), yet its labels repeat; `WellFormedRights` refuses it.
#guard (rightsDocs.drop 5).all fun R => VE.SoftNorms.WellFormedSoft (VE.Rights.correlate R) &&
  WellFormedU (legacyU R) && !decide (legacyLabels R).Nodup && !VE.Rights.WellFormedRights R
#guard rightsDocs.all fun R => !VE.Rights.WellFormedRights R || decide (legacyLabels R).Nodup
#guard rightsDocs.all fun R => !VE.SoftNorms.WellFormedSoft (VE.Rights.correlate R) ||
  decide (((VE.NormDefaults.Wire.softLabelledU (legacyU R) (VE.Rights.correlate R)).map (·.1)).Nodup)
#guard (rightsDocs.map VE.Rights.WellFormedRights) == [true, true, true, true, true, false, false]

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
