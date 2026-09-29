import VE.Data.Background
import VE.Bridge

/-! Functional and total tables in one pass, as Python `_valid_flags` and Rust
check them. The reference check, `VE.Data.Background.flagsValid`, evaluates the
generated flag premises, three nested quantifiers over the domains for a
functional table; `fastFlags` reads each table once and gives the same Boolean
(`fastFlags_eq`), so every theorem about `flagsValid` applies. -/
namespace VE.Route.Flags
open VE.Data.Background (Flag Intended Functional Total)

abbrev Entity := VE.Bridge.Entity

/-- The rows of `f`'s table typed by its signature, as pairs. -/
def typedRows (M : VE.FiniteModel Entity) (f : Flag) : List (Entity × Entity) :=
  let src := Std.HashSet.ofList (M.domains f.source)
  let tgt := Std.HashSet.ofList (M.domains f.target)
  (M.relations f.name).filterMap fun row => match row with
    | [x, y] => if src.contains x && tgt.contains y then some (x, y) else none
    | _ => none

theorem contains_ofList (ys : List Entity) (y : Entity) :
    (Std.HashSet.ofList ys).contains y = true ↔ y ∈ ys := by
  simp [Std.HashSet.contains_ofList]

theorem mem_typedRows (M : VE.FiniteModel Entity) (f : Flag) (x y : Entity) :
    (x, y) ∈ typedRows M f ↔
      x ∈ M.domains f.source ∧ y ∈ M.domains f.target ∧ [x, y] ∈ M.relations f.name := by
  simp only [typedRows, List.mem_filterMap]
  constructor
  · rintro ⟨row, hr, he⟩
    split at he
    · rename_i a b
      split at he
      · rename_i hc
        simp only [Option.some.injEq, Prod.mk.injEq] at he
        obtain ⟨rfl, rfl⟩ := he
        simp only [Bool.and_eq_true, contains_ofList] at hc
        exact ⟨hc.1, hc.2, hr⟩
      · cases he
    · cases he
  · rintro ⟨hx, hy, hr⟩
    refine ⟨[x, y], hr, ?_⟩
    simp only
    rw [if_pos (by simp only [Bool.and_eq_true, contains_ofList]; exact ⟨hx, hy⟩)]

/-- No source has two targets, reading pairs once with a map from source to
target; `m` holds the pairs already read. -/
def functionalGo : List (Entity × Entity) → Std.HashMap Entity Entity → Bool
  | [], _ => true
  | (x, y) :: rest, m => match m[x]? with
    | some y' => y' == y && functionalGo rest m
    | none => functionalGo rest (m.insert x y)

/-- A pair already read into `m` or still to be read. -/
def Seen (m : Std.HashMap Entity Entity) (l : List (Entity × Entity)) (x y : Entity) : Prop :=
  m[x]? = some y ∨ (x, y) ∈ l

theorem functionalGo_iff : ∀ (l : List (Entity × Entity)) (m : Std.HashMap Entity Entity),
    functionalGo l m = true ↔ ∀ x y z, Seen m l x y → Seen m l x z → y = z
  | [], m => by
    simp only [functionalGo, Seen, List.not_mem_nil, or_false, true_iff]
    intro x y z hy hz
    rw [hy] at hz
    exact Option.some.inj hz
  | (x₀, y₀) :: rest, m => by
    simp only [functionalGo]
    cases hm : m[x₀]? with
    | some y' =>
      simp only [Bool.and_eq_true, beq_iff_eq]
      have same : ∀ x y, Seen m ((x₀, y₀) :: rest) x y ↔ Seen m rest x y ∨ (x = x₀ ∧ y = y₀) := by
        intro x y
        simp only [Seen, List.mem_cons, Prod.mk.injEq]
        constructor
        · rintro (h | h | h)
          · exact .inl (.inl h)
          · exact .inr h
          · exact .inl (.inr h)
        · rintro ((h | h) | h)
          · exact .inl h
          · exact .inr (.inr h)
          · exact .inr (.inl h)
      constructor
      · rintro ⟨rfl, h⟩ x y z hy hz
        have ih := (functionalGo_iff rest m).mp h
        have lift : ∀ w, Seen m ((x₀, y') :: rest) x w → Seen m rest x w := by
          intro w hw
          rcases (same x w).mp hw with hw | ⟨rfl, rfl⟩
          · exact hw
          · exact .inl hm
        exact ih x y z (lift y hy) (lift z hz)
      · intro h
        have hy : y' = y₀ := h x₀ y' y₀ (.inl hm) (.inr (List.mem_cons_self ..))
        refine ⟨hy, (functionalGo_iff rest m).mpr fun x y z hy' hz' => ?_⟩
        exact h x y z ((same x y).mpr (.inl hy')) ((same x z).mpr (.inl hz'))
    | none =>
      rw [functionalGo_iff rest (m.insert x₀ y₀)]
      have same : ∀ x y, Seen (m.insert x₀ y₀) rest x y ↔ Seen m ((x₀, y₀) :: rest) x y := by
        intro x y
        simp only [Seen, Std.HashMap.getElem?_insert, List.mem_cons, Prod.mk.injEq]
        by_cases hx : x₀ = x
        · subst hx
          simp only [beq_self_eq_true, ↓reduceIte, Option.some.injEq, hm, reduceCtorEq, false_or,
            true_and]
          constructor
          · rintro (rfl | h)
            · exact .inl rfl
            · exact .inr h
          · rintro (rfl | h)
            · exact .inl rfl
            · exact .inr h
        · have hb : (x₀ == x) = false := beq_eq_false_iff_ne.mpr hx
          simp only [hb, Bool.false_eq_true, ↓reduceIte]
          constructor
          · rintro (h | h)
            · exact .inl h
            · exact .inr (.inr h)
          · rintro (h | ⟨rfl, _⟩ | h)
            · exact .inl h
            · exact absurd rfl hx
            · exact .inr h
      simp only [same]

def functionalFast (M : VE.FiniteModel Entity) (f : Flag) : Bool :=
  functionalGo (typedRows M f) {}

theorem functionalFast_iff (M : VE.FiniteModel Entity) (f : Flag) :
    functionalFast M f = true ↔ Functional M.asStructure f := by
  unfold functionalFast Functional
  rw [functionalGo_iff]
  simp only [Seen, Std.HashMap.getElem?_empty, reduceCtorEq, false_or, mem_typedRows,
    VE.FiniteModel.asStructure]
  constructor
  · intro h x hx y hy z hz hr hs
    exact h x y z ⟨hx, hy, hr⟩ ⟨hx, hz, hs⟩
  · rintro h x y z ⟨hx, hy, hr⟩ ⟨_, hz, hs⟩
    exact h x hx y hy z hz hr hs

def totalFast (M : VE.FiniteModel Entity) (f : Flag) : Bool :=
  let sources := Std.HashSet.ofList ((typedRows M f).map Prod.fst)
  (M.domains f.source).all sources.contains

theorem totalFast_iff (M : VE.FiniteModel Entity) (f : Flag) :
    totalFast M f = true ↔ Total M.asStructure f := by
  unfold totalFast Total
  simp only [List.all_eq_true, contains_ofList, List.mem_map, VE.FiniteModel.asStructure]
  constructor
  · intro h x hx
    obtain ⟨⟨x', y⟩, hp, rfl⟩ := h x hx
    obtain ⟨_, hy, hr⟩ := (mem_typedRows M f _ y).mp hp
    exact ⟨y, hy, hr⟩
  · intro h x hx
    obtain ⟨y, hy, hr⟩ := h x hx
    exact ⟨(x, y), (mem_typedRows M f x y).mpr ⟨hx, hy, hr⟩, rfl⟩

/-- Every flagged table is functional and total as declared. -/
def fastFlags (M : VE.FiniteModel Entity) (flags : List Flag) : Bool :=
  flags.all fun f => (!f.functional || functionalFast M f) && (!f.total || totalFast M f)

theorem fastFlags_iff (M : VE.FiniteModel Entity) (flags : List Flag) :
    fastFlags M flags = true ↔ ∀ f ∈ flags, Intended M.asStructure f := by
  unfold fastFlags Intended
  simp only [List.all_eq_true, Bool.and_eq_true, Bool.or_eq_true, Bool.not_eq_true']
  refine forall_congr' fun f => imp_congr_right fun _ => ?_
  rw [← functionalFast_iff, ← totalFast_iff]
  constructor
  · rintro ⟨h1, h2⟩
    exact ⟨fun hf => h1.resolve_left (by simp [hf]), fun ht => h2.resolve_left (by simp [ht])⟩
  · rintro ⟨h1, h2⟩
    refine ⟨?_, ?_⟩
    · cases hf : f.functional
      · exact .inl rfl
      · exact .inr (h1 hf)
    · cases ht : f.total
      · exact .inl rfl
      · exact .inr (h2 ht)

/-- **The one-pass check is the reference check.** -/
theorem fastFlags_eq (M : VE.FiniteModel Entity) (flags : List Flag) :
    fastFlags M flags = VE.Data.Background.flagsValid M flags := by
  apply Bool.eq_iff_iff.mpr
  rw [fastFlags_iff]
  constructor
  · intro h
    unfold VE.Data.Background.flagsValid
    apply List.all_eq_true.mpr
    intro a ha
    exact (VE.eval_iff_denote M [] a).mpr
      ((VE.Data.Background.generate_sat_iff M.asStructure flags).mpr h a ha)
  · exact VE.Data.Background.flags_model_valid M flags

end VE.Route.Flags
