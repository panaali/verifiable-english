import VE.Scales.Theorems
import VE.ModelProofs

/-! Acceptance fixtures of `scales@0` (docs/spec/quantities.md 9.3 and 9.5), computed over finite models
by enumeration. A fixture model is `VE.Bridge.ModelData`, so its admissibility is the checked
`modelData_valid`, and `premises_iff_intended` turns a computed premise check into `Intended`. -/
namespace VE.Scales.Examples
open VE VE.Bridge VE.Scales

/-- Every subset of a list. -/
def subsets {α : Type} : List α → List (List α)
  | [] => [[]]
  | x :: xs => subsets xs ++ (subsets xs).map (x :: ·)

/-- The model with one sort `s` of objects `ns`, each object also a constant of its own name. -/
def model (s : String) (ns : List String) (rs : List (String × List (List Entity))) : ModelData :=
  ⟨[(s, ns)], ns.map fun n => (n, (s, n)), rs⟩

def unaries (s : String) (ns : List String) : List (List Entity) := ns.map fun n => [(s, n)]
def binaries (s : String) (ns : List String) : List (List Entity) :=
  ns.flatMap fun a => ns.map fun b => [(s, a), (s, b)]

def holds (M : ModelData) (fs : List Formula) : Bool := fs.all (·.eval M.toModel [])
def prem (d : Dimension) : List Formula := (premises d).map (·.2)
def count (ms : List ModelData) (fs : List Formula) : Nat := (ms.filter (holds · fs)).length

def c (n : String) : Term := .const n
def u (p n : String) : Formula := .unary p (c n)
def b (p m n : String) : Formula := .binary p (c m) (c n)

/-- A computed premise check gives the intended meaning, and a failed one its absence. -/
theorem intended_of {v : Vocabulary} {ots : List String} {D : ScaleDoc} {M : ModelData}
    (hD : WellFormed v.environment ots D = true) (hv : M.valid v = true) :
    holds M ((scalePremises D).map (·.2)) = true ↔ ∀ d ∈ D.dims, Intended M.toModel.asStructure d := by
  rw [← premises_iff_intended v.environment ots D hD _ (modelData_valid M v hv)]
  simp only [holds, List.all_eq_true, List.mem_map, eval_iff_denote]

/-! FB1 (u0165.s01): "r1 gives serious uplift", "r2 gives more uplift than r1", "r2 does not give
serious uplift" are refuted by upward closure alone. Its lower twin carries the seeded bug. -/

def resp : Vocabulary := ⟨["response"], [("gives_more_uplift", ["response", "response"]),
  ("gives_serious_uplift", ["response"]), ("gives_grave_uplift", ["response"]),
  ("more_harmful", ["response", "response"]), ("minor_harm", ["response"])], [("r1", "response"), ("r2", "response")]⟩
def ots : List String := ["gives_serious_uplift", "gives_grave_uplift", "minor_harm"]
def serious : Grade := ⟨"gives_serious_uplift", .upper⟩
def uplift : Dimension := ⟨"uplift", "response", "gives_more_uplift", none, false, [serious], []⟩
def harm : Dimension := ⟨"harm", "response", "more_harmful", none, false, [⟨"minor_harm", .lower⟩], []⟩

/-- The 64 models over two responses of one comparative and one graded word. -/
def twoResp (m g : String) : List ModelData :=
  (subsets (binaries "response" ["r1", "r2"])).flatMap fun ms =>
    (subsets (unaries "response" ["r1", "r2"])).map fun gs => model "response" ["r1", "r2"] [(m, ms), (g, gs)]

def fb1Facts : List Formula :=
  [u "gives_serious_uplift" "r1", b "gives_more_uplift" "r2" "r1", .not (u "gives_serious_uplift" "r2")]
def fb1Lower : List Formula := [u "minor_harm" "r1", b "more_harmful" "r1" "r2", .not (u "minor_harm" "r2")]

/-- A premise's body at a valuation (`var 0` is `y`, `var 1` is `x`); `true` when the label or the shape
misses, so a guard that needs the body false cannot pass vacuously. -/
def bodyAt (d : Dimension) (label : String) (ρ : List Entity) (M : ModelData) : Bool :=
  match (premises d).find? (·.1 == label) with
  | some (_, .all _ (.all _ φ)) => φ.eval M.toModel ρ
  | _ => true

#guard WellFormed resp.environment ots ⟨[uplift]⟩ && WellFormed resp.environment ots ⟨[harm]⟩
#guard (premises uplift).map (·.1) == ["uplift/irreflexive", "uplift/transitive", "uplift/gives_serious_uplift/closed"]
#guard (twoResp "gives_more_uplift" "gives_serious_uplift").length == 64
#guard count (twoResp "gives_more_uplift" "gives_serious_uplift") (fb1Facts ++ prem uplift) == 0
#guard count (twoResp "gives_more_uplift" "gives_serious_uplift") (fb1Facts ++ (prem uplift).take 2) > 0
-- The one instance `uplift/gives_serious_uplift/closed` at (r2, r1) refutes the facts alone.
#guard ((twoResp "gives_more_uplift" "gives_serious_uplift").filter fun M => holds M fb1Facts &&
  bodyAt uplift "uplift/gives_serious_uplift/closed" [("response", "r1"), ("response", "r2")] M).length == 0
-- The seeded bug of QT-B1 (the lower closure generated with the comparative reversed) makes this 1.
#guard count (twoResp "more_harmful" "minor_harm") (fb1Lower ++ prem harm) == 0
#guard count (twoResp "more_harmful" "minor_harm") (fb1Lower ++ (prem harm).take 2) > 0

/-! FB2 (u0226.s01, s02): "every other disposition lies strictly between them" orders the two ends only
when a third disposition exists; the endpoint premise orders them always (A2). -/

def disp : Vocabulary := ⟨["disposition"], [("more_autonomous", ["disposition", "disposition"])],
  [("fully_corrigible", "disposition"), ("fully_autonomous", "disposition")]⟩
def autonomy : Dimension := ⟨"autonomy", "disposition", "more_autonomous", none, false, [], []⟩
def between : Formula := .all "disposition" (.implies
  (.and (.not (.eq (.var 0) (c "fully_corrigible"))) (.not (.eq (.var 0) (c "fully_autonomous"))))
  (.and (.binary "more_autonomous" (.var 0) (c "fully_corrigible"))
    (.binary "more_autonomous" (c "fully_autonomous") (.var 0))))
def endpoint : Formula := b "more_autonomous" "fully_autonomous" "fully_corrigible"
def aboveTop : Formula := .ex "disposition" (.binary "more_autonomous" (.var 0) (c "fully_autonomous"))
def dispModels (ns : List String) : List ModelData :=
  (subsets (binaries "disposition" ns)).map fun ms => model "disposition" ns [("more_autonomous", ms)]
def ends : List String := ["fully_corrigible", "fully_autonomous"]

#guard WellFormed disp.environment [] ⟨[autonomy]⟩
#guard (count (dispModels ends) (between :: prem autonomy),
  count (dispModels ends) (aboveTop :: between :: prem autonomy)) == (3, 1)
#guard (count (dispModels (ends ++ ["d3"])) (between :: prem autonomy),
  count (dispModels (ends ++ ["d3"])) (aboveTop :: between :: prem autonomy)) == (1, 0)
#guard [ends, ends ++ ["d3"]].all fun ns => (count (dispModels ns) (endpoint :: between :: prem autonomy),
  count (dispModels ns) (aboveTop :: endpoint :: between :: prem autonomy)) == (1, 0)

/-- FB2's refutation, over every admissible structure rather than the counted models: with the endpoint
premise, the "between" facts and the premises, no disposition is more autonomous than fully autonomous.
Such a disposition is fully autonomous (irreflexive), fully corrigible (transitive through the endpoint
premise) or another one, which lies below fully autonomous (transitive through "between"). -/
theorem fb2_refuted :
    Entails disp.environment (endpoint :: between :: (scalePremises ⟨[autonomy]⟩).map (·.2)) (.not aboveTop) := by
  intro S hS hall ⟨x, hx, v, w, hv, hw, hr⟩
  have hI : Intended S autonomy :=
    (premises_iff_intended disp.environment [] ⟨[autonomy]⟩ (by decide) S hS).mp
      (fun a ha => hall a (List.mem_cons_of_mem _ (List.mem_cons_of_mem _ ha))) autonomy (by simp)
  obtain ⟨a, b, ha, hb, hab⟩ := hall endpoint (by simp)
  have hbt := hall between (by simp)
  obtain ⟨a', ha', hda⟩ := hS.1 "fully_autonomous" "disposition" (by decide)
  obtain ⟨b', hb', hdb⟩ := hS.1 "fully_corrigible" "disposition" (by decide)
  simp only [Term.denote, c, ha', hb', List.getElem?_cons_zero, Option.some.injEq] at hv hw ha hb
  subst hv hw ha hb
  have hmore : autonomy.more = "more_autonomous" := rfl
  rw [← hmore] at hr hab
  by_cases hxa : x = a'
  · subst hxa; exact hI.irrefl _ hx hr
  by_cases hxb : x = b'
  · subst hxb; exact hI.irrefl _ hx (hI.trans _ _ _ hx hda hx hr hab)
  obtain ⟨-, ⟨a₁, x₁, ha₁, hx₁, hax⟩⟩ := hbt x hx
    ⟨fun ⟨_, h₁, h₂⟩ => hxb (by simp_all [Term.denote, c]), fun ⟨_, h₁, h₂⟩ => hxa (by simp_all [Term.denote, c])⟩
  simp only [Term.denote, c, ha', List.getElem?_cons_zero, Option.some.injEq] at ha₁ hx₁
  subst ha₁ hx₁
  rw [← hmore] at hax
  exact hI.irrefl _ hx (hI.trans _ _ _ hx hda hx hr hax)

/-! FB3 (u0043.s01): "different levels of trust" is the reading set {not all the same; pairwise
different}; a model with Anthropic and operators equally trusted, users less, distinguishes them. -/

def principals : Vocabulary := ⟨["principal_type"], [("more_trusted", ["principal_type", "principal_type"]),
  ("equally_trusted", ["principal_type", "principal_type"])],
  [("anthropic", "principal_type"), ("operators", "principal_type"), ("users", "principal_type")]⟩
def trust : Dimension := ⟨"trust", "principal_type", "more_trusted", some "equally_trusted", true, [], []⟩
def notAllSame : Formula := .not (.all "principal_type" (.all "principal_type" (rel2 "equally_trusted" 1 0)))
def pairwiseDifferent : Formula := .all "principal_type" (.all "principal_type"
  (.implies (.not (.eq (.var 1) (.var 0))) (.not (rel2 "equally_trusted" 1 0))))
def pt (n : String) : Entity := ("principal_type", n)
def trustModel (same more : List (String × String)) : ModelData :=
  model "principal_type" ["anthropic", "operators", "users"]
    [("equally_trusted", (["anthropic", "operators", "users"].map fun n => [pt n, pt n]) ++
        same.map fun p => [pt p.1, pt p.2]),
     ("more_trusted", more.map fun p => [pt p.1, pt p.2])]
/-- Anthropic and operators equally trusted, users less. -/
def twoLevels : ModelData := trustModel [("anthropic", "operators"), ("operators", "anthropic")]
  [("anthropic", "users"), ("operators", "users")]
def threeLevels : ModelData := trustModel [] [("anthropic", "operators"), ("anthropic", "users"), ("operators", "users")]
/-- Irreflexivity broken: Anthropic more trusted than itself. -/
def reflexiveMore : ModelData := trustModel [] [("anthropic", "anthropic"), ("anthropic", "operators"),
  ("anthropic", "users"), ("operators", "users")]
/-- "As much as" not transitive: Anthropic as operators, operators as users, Anthropic not as users. -/
def sameNotTrans : ModelData := trustModel [("anthropic", "operators"), ("operators", "anthropic"),
  ("operators", "users"), ("users", "operators")] [("anthropic", "users")]

#guard WellFormed principals.environment [] ⟨[trust]⟩
#guard [twoLevels, threeLevels, reflexiveMore, sameNotTrans].all (·.valid principals)
#guard ([notAllSame, pairwiseDifferent].map (·.eval twoLevels.toModel [])) == [true, false]
#guard ([notAllSame, pairwiseDifferent].map (·.eval threeLevels.toModel [])) == [true, true]

/-- 9.5, `premises_iff_intended` true on both sides: the two trust models have the intended meaning. -/
theorem trust_intended : Intended twoLevels.toModel.asStructure trust ∧
    Intended threeLevels.toModel.asStructure trust :=
  ⟨(intended_of (v := principals) (ots := []) (D := ⟨[trust]⟩) (by decide) (by decide)).mp (by decide) trust (by simp),
   (intended_of (v := principals) (ots := []) (D := ⟨[trust]⟩) (by decide) (by decide)).mp (by decide) trust (by simp)⟩

/-- 9.5, false on both sides: irreflexivity broken, or "as much as" not transitive. -/
theorem trust_not_intended : ¬ Intended reflexiveMore.toModel.asStructure trust ∧
    ¬ Intended sameNotTrans.toModel.asStructure trust := by
  refine ⟨fun h => ?_, fun h => ?_⟩
  · have := (intended_of (v := principals) (ots := []) (D := ⟨[trust]⟩) (M := reflexiveMore) (by decide) (by decide)).mpr
      (by simpa using h)
    exact absurd this (by decide)
  · have := (intended_of (v := principals) (ots := []) (D := ⟨[trust]⟩) (M := sameNotTrans) (by decide) (by decide)).mpr
      (by simpa using h)
    exact absurd this (by decide)

/-! FB4 (UDHR u094): "all children enjoy the same social protection" is `∀c₁ c₂. same(c₁, c₂)`, a
statement the premises neither give nor exclude. -/

def children : Vocabulary := ⟨["child"], [("more_social_protection", ["child", "child"]),
  ("same_social_protection", ["child", "child"])], []⟩
def protection : Dimension :=
  ⟨"social_protection", "child", "more_social_protection", some "same_social_protection", false, [], []⟩
def allSame : Formula := .all "child" (.all "child" (rel2 "same_social_protection" 1 0))
def kid (n : String) : Entity := ("child", n)
def kids (same more : List (List Entity)) : ModelData :=
  ⟨[("child", ["k1", "k2"])], [], [("same_social_protection", same), ("more_social_protection", more)]⟩
def equalKids : ModelData := kids (binaries "child" ["k1", "k2"]) []
def unequalKids : ModelData := kids [[kid "k1", kid "k1"], [kid "k2", kid "k2"]] [[kid "k1", kid "k2"]]

#guard WellFormed children.environment [] ⟨[protection]⟩ && allSame.check children.environment []
#guard holds equalKids (allSame :: prem protection) && holds unequalKids (prem protection) &&
  !allSame.eval unequalKids.toModel []

/-! FB8 (hostile `WellFormed`), and duplicate labels (A3). -/

def grave : Grade := ⟨"gives_grave_uplift", .upper⟩
def withGrades (gs : List Grade) (above : List (String × String)) : Dimension := { uplift with grades := gs, above := above }
def wf (ds : List Dimension) : Bool := WellFormed resp.environment ots ⟨ds⟩
def labels (ds : List Dimension) : List String := (scalePremises ⟨ds⟩).map (·.1)

#guard !wf [{ uplift with more := "gives_less_uplift" }]
#guard !wf [withGrades [serious, grave] [("gives_grave_uplift", "gives_serious_uplift"),
  ("gives_serious_uplift", "gives_grave_uplift")]]
#guard match VE.Route.dependencyOrder (aboveNodes (withGrades [serious, grave]
    [("gives_grave_uplift", "gives_serious_uplift"), ("gives_serious_uplift", "gives_grave_uplift")])) with
  | .error e => e.startsWith "DependencyCycle:"
  | .ok _ => false
#guard !wf [withGrades [serious, { grave with direction := .lower }] [("gives_grave_uplift", "gives_serious_uplift")]]
#guard !wf [{ uplift with comparable := true }]
#guard !WellFormed resp.environment ["gives_grave_uplift"] ⟨[uplift]⟩
#guard !wf [{ uplift with same := some "gives_more_uplift" }] && wf [{ uplift with same := some "more_harmful" }]
#guard wf [uplift] && wf [withGrades [serious, grave] []] &&
  wf [withGrades [serious, grave] [("gives_grave_uplift", "gives_serious_uplift")]]
#guard ((labels [uplift, { harm with name := "uplift" }]).length,
  (labels [uplift, { harm with name := "uplift" }]).eraseDups.length) == (6, 4)
#guard !wf [uplift, { harm with name := "uplift" }] && wf [uplift, harm]
#guard (labels [uplift, harm]).eraseDups.length == 6
#guard ((labels [withGrades [serious, grave] [("gives_grave_uplift", "gives_serious_uplift"),
    ("gives_grave_uplift", "gives_serious_uplift")]]).length,
  (labels [withGrades [serious, grave] [("gives_grave_uplift", "gives_serious_uplift"),
    ("gives_grave_uplift", "gives_serious_uplift")]]).eraseDups.length) == (6, 5)
#guard !wf [withGrades [serious, grave] [("gives_grave_uplift", "gives_serious_uplift"),
  ("gives_grave_uplift", "gives_serious_uplift")]]

def cycle : Dimension := withGrades [serious, grave]
  [("gives_grave_uplift", "gives_serious_uplift"), ("gives_serious_uplift", "gives_grave_uplift")]
def chain : Dimension := withGrades [serious, grave] [("gives_grave_uplift", "gives_serious_uplift")]
/-- "Whatever gives grave uplift gives serious uplift": r1 grave and not serious breaks it. -/
def graveOnly (serious : List String) : ModelData := model "response" ["r1", "r2"]
  [("gives_grave_uplift", [[("response", "r1")]]), ("gives_serious_uplift", unaries "response" serious)]
#guard !holds (graveOnly []) (prem chain) && holds (graveOnly ["r1"]) (prem chain)
def shared : Dimension := { uplift with same := some "gives_more_uplift" }
def manyGrades (n : Nat) (edges : Nat) : Dimension :=
  withGrades ((List.range n).map fun i => ⟨toString i, .upper⟩) ((List.range edges).map fun _ => ("0", "0"))

/-- The `above` order is acyclic by `kahn`, and within QS-1's caps (16 grades, 64 pairs). -/
theorem order_cases : (VE.Route.dependencyOrder (aboveNodes cycle)).isOk = false ∧
    (VE.Route.dependencyOrder (aboveNodes chain)).isOk = true ∧
    ((gradeOrder (manyGrades 16 64)).admit gradeCaps).isOk = true ∧
    ((gradeOrder (manyGrades 17 0)).admit gradeCaps).isOk = false ∧
    ((gradeOrder (manyGrades 16 65)).admit gradeCaps).isOk = false := by decide

/-- One dimension per predicate: a predicate both comparative and equative is refused. -/
theorem symbols_cases : uplift.symbols = ["gives_more_uplift", "gives_serious_uplift"] ∧
    shared.symbols = ["gives_more_uplift", "gives_more_uplift", "gives_serious_uplift"] ∧
    decide (ScaleDoc.symbols ⟨[uplift, harm]⟩).Nodup = true ∧
    decide (ScaleDoc.symbols ⟨[shared]⟩).Nodup = false ∧
    decide (ScaleDoc.symbols ⟨[uplift, { harm with more := "gives_more_uplift" }]⟩).Nodup = false := by decide

/-- Each remaining conjunct of `WellFormed`, alone: a sort not declared, a one-place equative, a
two-place graded word, a predicate in two dimensions, 17 grades. -/
def ghost : Vocabulary := ⟨["response"], resp.predicates ++ [("ghost_more", ["ghost", "ghost"])] ++
  (List.range 17).map fun i => (toString i, ["response"]), resp.constants⟩
#guard !WellFormed ghost.environment [] ⟨[{ autonomy with sort := "ghost", more := "ghost_more" }]⟩
#guard !wf [{ uplift with same := some "minor_harm" }]
#guard !WellFormed resp.environment ("more_harmful" :: ots) ⟨[withGrades [⟨"more_harmful", .upper⟩] []]⟩
#guard !wf [uplift, { harm with more := "gives_more_uplift" }]
#guard !WellFormed ghost.environment ((List.range 17).map toString) ⟨[manyGrades 17 0]⟩ &&
  WellFormed ghost.environment ((List.range 16).map toString) ⟨[manyGrades 16 0]⟩

/-! One role per predicate, position by position of `Dimension.symbols` (comparative, equative, two graded
words): each pair of positions of one arity, given one predicate across two dimensions or within one, is
refused, and the same block with the second position renamed apart is accepted, so each refusal is the
sharing's. A graded word is unary and the other two binary, so a pair of two arities is the signature
conjuncts' to refuse. -/

/-- Dimension `i`: comparative `more_i`, equative `same_i`, graded words `grade_i_a` and `grade_i_b`. -/
def base (i : String) : Dimension := ⟨"dim_" ++ i, "response", "more_" ++ i, some ("same_" ++ i), false,
  [⟨"grade_" ++ i ++ "_a", .upper⟩, ⟨"grade_" ++ i ++ "_b", .upper⟩], []⟩
/-- `d` with position `k` of its symbols given to `p`. -/
def setAt (d : Dimension) : Nat → String → Dimension
  | 0, p => { d with more := p }
  | 1, p => { d with same := some p }
  | k + 2, p => { d with grades := d.grades.set k ⟨p, .upper⟩ }
/-- The predicate a position shares (`true`) or is renamed apart to (`false`), of the position's arity. -/
def roleName (k : Nat) (shared : Bool) : String :=
  (if shared then "shared" else "apart") ++ (if 2 ≤ k then "_grade" else "")
def roleUnaries : List String := ["grade_1_a", "grade_1_b", "grade_2_a", "grade_2_b", "shared_grade", "apart_grade"]
def roleVocab : Vocabulary := ⟨["response"],
  (["more_1", "more_2", "same_1", "same_2", "shared", "apart"].map fun p => (p, ["response", "response"])) ++
    roleUnaries.map fun p => (p, ["response"]), []⟩
def roleWf (ds : List Dimension) : Bool := WellFormed roleVocab.environment roleUnaries ⟨ds⟩
def rolePairs : List (Nat × Nat) := (List.range 4).flatMap fun k =>
  ((List.range 4).filter fun l => (2 ≤ k) == (2 ≤ l)).map (k, ·)

-- The positions are exactly `Dimension.symbols`: `setAt` changes position k and nothing else.
#guard (base "1").symbols.length == 4 &&
  (List.range 4).all fun k => (setAt (base "1") k "x").symbols == (base "1").symbols.set k "x"
#guard roleWf [base "1"] && roleWf [base "1", base "2"]
#guard rolePairs.length == 8 && rolePairs.all fun (k, l) =>
  !roleWf [setAt (base "1") k (roleName k true), setAt (base "2") l (roleName l true)] &&
  roleWf [setAt (base "1") k (roleName k true), setAt (base "2") l (roleName l false)]
#guard (rolePairs.filter fun (k, l) => k < l) == [(0, 1), (2, 3)] &&
  (rolePairs.filter fun (k, l) => k < l).all fun (k, l) =>
    !roleWf [setAt (setAt (base "1") k (roleName k true)) l (roleName l true)] &&
    roleWf [setAt (setAt (base "1") k (roleName k true)) l (roleName l false)]
-- Each dimension's own conjuncts are checked in every position of the block.
#guard !roleWf [base "1", { base "2" with more := "undeclared" }] &&
  !roleWf [{ base "1" with more := "undeclared" }, base "2"]

end VE.Scales.Examples
