import VE.NormDefaults.Packs

/-! The acceptance fixtures of premise packs on `Packs.lean` alone (docs/spec/premise-packs.md 4: A1–A9; 2.10's kind
table). The fixtures over today's sources (F1, F1′, the kind table's legacy rows) are in `PacksLegacyExamples.lean`;
A9′ reads the response shape, so it sits with the encoder theorem (`ResponseShape/Encoders/NormDefaults.lean`). -/
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
#guard X [soft, weighing] = [φ, φ, .bottom]

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

-- 2.10: the kind table. A row needing no pack runs; a row needing a pack runs only when the source has it, and is
-- refused otherwise; the first row for a kind is the one; a kind with no row is `none`, not a refusal.
def kinds : List (KindRow Nat) :=
  [⟨"echo", none, fun n id _ => pure (.str s!"{id}:{n}")⟩,
   ⟨"weigh", some "weighing", fun n _ _ => pure (.num n)⟩,
   ⟨"echo", some "events", fun _ _ _ => throw "second echo row"⟩,
   ⟨"fails", none, fun _ _ _ => throw "InvalidInput: refused by the row"⟩]
def kindDiag : Except String (Option Lean.Json) → String
  | .ok none => "none"
  | .ok (some a) => a.compress
  | .error e => e
#guard kindDiag (dispatch kinds [] 7 "c1" "echo" .null) == "\"c1:7\""
#guard kindDiag (dispatch kinds ["soft", "weighing"] 7 "c1" "weigh" .null) == "7"
#guard kindDiag (dispatch kinds ["soft", "rights"] 7 "c1" "weigh" .null) ==
  "UnsupportedProfile: case kind weigh needs the weighing premise pack"
#guard kindDiag (dispatch kinds ["events"] 7 "c1" "echo" .null) == "\"c1:7\""
#guard kindDiag (dispatch kinds ["weighing"] 7 "c1" "fails" .null) == "InvalidInput: refused by the row"
#guard kindDiag (dispatch kinds ["weighing"] 7 "c1" "attitudes-elaborate" .null) == "none"
#guard kindDiag (dispatch [] [] 7 "c1" "echo" .null) == "none"

end VE.NormDefaults.Packs.Fixtures
