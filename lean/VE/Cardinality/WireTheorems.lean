import VE.Cardinality.Wire

/-! What the `ve-cardinality@1` decoders establish (docs/spec/quantities.md 4.1–4.3), apart from their fixtures, so
a seeded bug in a decoder is caught by `VE.Cardinality.WireExamples`' guards as well as here. Every trusted
definition of `Wire.lean` is stated about here (`tests/test_cardinality_exercised.py`). -/
namespace VE.Cardinality.Wire
open Lean
open VE.Order.ProfileGate (bind_ok)

/-- E2's lists project onto W6a's own: an environment past E2 meets W6a's profile check at E4. -/
theorem profileLists_projected {ps : List String} (h : ps ∈ profileLists) :
    ps.filter (· != "cardinality@0") ∈ VE.Time.Wire.w6Profiles := by
  simp only [profileLists, List.mem_map] at h
  obtain ⟨l, hl, rfl⟩ := h
  simp only [VE.Time.Wire.w6Profiles, List.mem_cons, List.not_mem_nil, or_false] at hl
  rcases hl with rfl | rfl <;> decide

/-- E6: at most 64 finite sorts are declared. -/
theorem finiteSorts_length {env : Json} {xs : List String} (h : finiteSorts env = .ok xs) :
    xs.length ≤ maxFiniteSorts := by
  unfold finiteSorts at h
  split at h
  · simp only [bind, Except.bind] at h
    split at h
    · cases h
    · cases h; omega
  · cases h

/-- What the environment decoder establishes (spec 4.1, 4.3): its identity is the original environment's, under a
profile list E2 admits; `w6` is W6a's decoding of the projection; and the cardinality environment is W6a's vocabulary
with the declared finite sorts. -/
theorem decodeEnvironment_sound {env : Json} {w : CardEnv} (h : decodeEnvironment env = .ok w) :
    (∃ ps, ps ∈ profileLists ∧ VE.Route.Wire.environmentId ps env = .ok w.environmentId) ∧
    (∃ j, projectW6 env = .ok j ∧ VE.Time.Wire.decodeEnvironment j = .ok w.w6) ∧
    ∃ finite, finiteSorts env = .ok finite ∧ w.env = ⟨w.w6.vocab.env, finite⟩ := by
  unfold decodeEnvironment at h
  obtain ⟨_, -, h⟩ := bind_ok h
  obtain ⟨_, -, h⟩ := bind_ok h
  obtain ⟨ps, -, h⟩ := bind_ok h
  simp only at h
  split at h
  case isFalse => cases h
  rename_i hps
  obtain ⟨_, -, h⟩ := bind_ok h
  obtain ⟨_, -, h⟩ := bind_ok h
  split at h
  case isFalse => cases h
  obtain ⟨_, -, h⟩ := bind_ok h
  obtain ⟨j, hj, h⟩ := bind_ok h
  obtain ⟨w6, hw6, h⟩ := bind_ok h
  obtain ⟨finite, hf, h⟩ := bind_ok h
  obtain ⟨_, -, h⟩ := bind_ok h
  obtain ⟨id, hid, h⟩ := bind_ok h
  split at h
  case isFalse => cases h
  cases h
  exact ⟨⟨ps, List.contains_iff_mem.mp hps, hid⟩, ⟨j, hj, hw6⟩, finite, hf, rfl⟩

/-- A decoded statement's meaning id is over the canonical object of the admitted formula, in the cardinality
environment's identity. -/
theorem decodeStatement_identity {w : CardEnv} {j : Json} {a : CAdmission w} (h : decodeStatement w j = .ok a) :
    VE.Route.Wire.meaningId w.profiles w.environmentId (canonical a.formula) = .ok a.meaningId := by
  unfold decodeStatement at h
  simp only at h
  split at h
  case isFalse => cases h
  obtain ⟨_, -, h⟩ := bind_ok h
  obtain ⟨_, -, h⟩ := bind_ok h
  split at h
  case isFalse => cases h
  obtain ⟨_, -, h⟩ := bind_ok h
  obtain ⟨f, -, h⟩ := bind_ok h
  split at h
  case isFalse => cases h
  obtain ⟨m, hm, h⟩ := bind_ok h
  cases h
  exact hm

/-- S2 holds of the whole formula of every decoded statement: at most 10,000 array nodes, nested at most 64 deep
(review F2 of qt-a3). -/
theorem decodeStatement_fits {w : CardEnv} {j : Json} {a : CAdmission w} (h : decodeStatement w j = .ok a) :
    ∃ source, j.getObjVal? "formula" = .ok source ∧ sourceFits source = true := by
  unfold decodeStatement at h
  simp only at h
  split at h
  case isFalse => cases h
  obtain ⟨_, -, h⟩ := bind_ok h
  obtain ⟨source, hsrc, h⟩ := bind_ok h
  split at h
  case isFalse => cases h
  exact ⟨source, hsrc, by assumption⟩

theorem sourceFits_iff (source : Json) : sourceFits source = true ↔
    VE.Time.Wire.jsonNodes (VE.Limits.maxJsonDepth + 1) source ≤ VE.Limits.maxNodes ∧
      arrayDepth (VE.Limits.maxDepth + 1) source ≤ VE.Limits.maxDepth := by
  simp [sourceFits]

/-! ## The elaborators' parts: each name, operator and operand (review F1 of qt-a3)

The statements spell each name of spec 4.1 by an exhaustive match, so a constructor added to `Rel`, `Cmp` or
`Rounding` breaks them until it is spelled, and a swapped or second spelling does not prove. -/

theorem elabName_mem {α : Type} {names : List (String × α)} {s : String} {x : α} (h : elabName names s = .ok x) :
    (s, x) ∈ names := by
  unfold elabName at h
  split at h
  · cases h; exact VE.Order.lookup_mem _ _ _ (by assumption)
  · cases h

theorem relNames_spelled (s : String) (r : Rel) :
    elabName relNames s = .ok r ↔ s = (match r with | .lt => "lt" | .le => "le" | .eq => "eq") := by
  constructor
  · intro h
    have := elabName_mem h
    simp only [relNames, List.mem_cons, Prod.mk.injEq, List.not_mem_nil, or_false] at this
    rcases this with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ <;> rfl
  · rintro rfl; cases r <;> rfl

theorem cmpNames_spelled (s : String) (c : Cmp) :
    elabName cmpNames s = .ok c ↔
      s = (match c with | .gt => "gt" | .ge => "ge" | .lt => "lt" | .le => "le" | .eq => "eq") := by
  constructor
  · intro h
    have := elabName_mem h
    simp only [cmpNames, List.mem_cons, Prod.mk.injEq, List.not_mem_nil, or_false] at this
    rcases this with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ <;> rfl
  · rintro rfl; cases c <;> rfl

/-- `elabRule` reads `ruleNames`, which spells each rule once. -/
theorem ruleNames_spelled (s : String) (r : VE.Numbers.Rounding) :
    (elabRule s = .ok r ↔ (s, r) ∈ ruleNames) ∧ ((s, r) ∈ ruleNames ↔
      s = (match r with | .tiesUp => "ties_up" | .halfEven => "half_even" | .down => "down" | .up => "up")) := by
  have spelled : (s, r) ∈ ruleNames ↔
      s = (match r with | .tiesUp => "ties_up" | .halfEven => "half_even" | .down => "down" | .up => "up") := by
    constructor
    · intro h
      simp only [ruleNames, List.mem_cons, Prod.mk.injEq, List.not_mem_nil, or_false] at h
      rcases h with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩ <;> rfl
    · rintro rfl; cases r <;> decide
  refine ⟨⟨fun h => ?_, fun h => ?_⟩, spelled⟩
  · unfold elabRule at h
    split at h
    · cases h; exact VE.Order.lookup_mem _ _ _ (by assumption)
    · cases h
  · obtain rfl := spelled.mp h
    cases r <;> rfl

theorem items_ok (j : Json) (xs : List Json) : items j = .ok xs ↔ ∃ a, j = .arr a ∧ a.toList = xs := by
  cases j <;> simp [items, Json.getArr?, pure, Except.pure, throw, throwThe, MonadExceptOf.throw]

/-- Each body operator, its children in order. -/
theorem elabBody_cases (n : Nat) (p : String) (a b : Json) :
    elabBody (n + 1) (.arr #[.str "is", .str p]) = .ok (.atom p) ∧
    elabBody (n + 1) (.arr #[.str "any"]) = .ok .any ∧
    elabBody (n + 1) (.arr #[.str "not", a]) = Body.not <$> elabBody n a ∧
    elabBody (n + 1) (.arr #[.str "and", a, b]) = (do pure (Body.and (← elabBody n a) (← elabBody n b))) ∧
    elabBody (n + 1) (.arr #[.str "or", a, b]) = (do pure (Body.or (← elabBody n a) (← elabBody n b))) := by
  refine ⟨rfl, rfl, ?_, ?_, ?_⟩ <;> cases a <;> rfl

/-- A ratio operand: a W6a term with its type, or a count of a body with S5 and S6, dimensionless. -/
theorem elabOperand_cases (w : CardEnv) (t b : Json) (s : String) :
    elabOperand w (.arr #[.str "quantity", t]) = (do
      let (τ, q) ← VE.Time.Wire.elabTerm w.w6.vocab [] VE.Limits.maxDepth t
      pure (τ, .quantity q)) ∧
    elabOperand w (.arr #[.str "count", .str s, b]) = (do
      let b ← elabBody VE.Limits.maxDepth b
      countedSort w.env s [b]
      pure (.qty VE.Time.dimensionless, .count s b)) := ⟨rfl, rfl⟩

/-- S9: a decoded ratio's operands are the two operands' terms, in order, of one quantity tag that is not `day`. -/
theorem elabRatio_sound {w : CardEnv} {x y : Json} {a b : CTerm} (h : elabRatio w x y = .ok (a, b)) :
    ∃ g, elabOperand w x = .ok (.qty g, a) ∧ elabOperand w y = .ok (.qty g, b) ∧ g ≠ VE.Time.dayTag := by
  unfold elabRatio at h
  obtain ⟨⟨τ, x'⟩, hx, h1⟩ := bind_ok h
  simp only at h1
  obtain ⟨⟨σ, y'⟩, hy, h2⟩ := bind_ok h1
  simp only at h2
  obtain ⟨_, hs, h3⟩ := bind_ok h2
  have hτ : τ = σ := by
    unfold VE.Time.Wire.same at hs
    split at hs
    · exact beq_iff_eq.mp (by assumption)
    · split at hs <;> cases hs
  subst hτ
  cases τ with
  | obj _ => cases h3
  | qty g =>
    simp only at h3
    split at h3
    · cases h3
    · cases h3
      exact ⟨g, hx, hy, by simpa using (by assumption : ¬(g == VE.Time.dayTag) = true)⟩

/-- A printed number is W6a's decimal reading: its digits and its written places. -/
theorem printed_eq (s : String) :
    printed s = (fun d => (d.significand, d.places)) <$> VE.Time.parseDecimal s := by
  simp only [printed]; cases VE.Time.parseDecimal s <;> rfl

/-! ## The encoders' cases (review F4 of qt-a3d)

`encode` and its parts write the answers' formulas (D[V]): each case's wire name and argument order, as spec 4.1
spells them and the `elab*_cases` above read them, so a swapped name or argument fails here. -/

theorem encBody_cases (p : String) (a b : Body) :
    encBody (.atom p) = Json.arr #[.str "is", .str p] ∧ encBody .any = Json.arr #[.str "any"] ∧
    encBody (.not a) = Json.arr #[.str "not", encBody a] ∧
    encBody (.and a b) = Json.arr #[.str "and", encBody a, encBody b] ∧
    encBody (.or a b) = Json.arr #[.str "or", encBody a, encBody b] := ⟨rfl, rfl, rfl, rfl, rfl⟩

theorem encOperand_cases (t : VE.Time.QTerm) (s : String) (b : Body) :
    encOperand (.quantity t) = Json.arr #[.str "quantity", VE.Time.Wire.encTerm t] ∧
    encOperand (.count s b) = Json.arr #[.str "count", .str s, encBody b] := ⟨rfl, rfl⟩

/-- A printed number is the decimal of its digits at its places (`Time.renderAmount`, which `printed` reads back). -/
theorem encPrinted_eq (D : Int) (k : Nat) : encPrinted D k = .str (VE.Time.renderAmount k D) := rfl

theorem encode_cases (q : VE.Time.QFormula) (c : CountAtom) (p : Proportion) (r : VE.Numbers.Rounding)
    (x y : CTerm) (D : Int) (k : Nat) (a b : CFormula) :
    encode (.quantity q) = Json.arr #[.str "quantity", VE.Time.Wire.encQ q] ∧
    encode (.count c) = Json.arr #[.str "count", .str c.sort,
      Json.arr (c.terms.map fun kb => Json.arr #[.str (toString kb.1), encBody kb.2]).toArray,
      .str (nameOf relNames c.rel), .str (toString c.bound)] ∧
    encode (.proportion p) = Json.arr #[.str "proportion", .str p.sort, encBody p.whole, encBody p.part,
      .str (nameOf cmpNames p.cmp), .str (toString p.num), .str (toString p.den)] ∧
    encode (.roundsTo r x y D k) = Json.arr #[.str "rounds_to", .str (nameOf ruleNames r), encOperand x,
      encOperand y, encPrinted D k] ∧
    encode (.percentOf x y D k) = Json.arr #[.str "percent_of", encOperand x, encOperand y, encPrinted D k] ∧
    encode (.percentRoundsTo r x y D k) = Json.arr #[.str "percent_rounds_to", .str (nameOf ruleNames r),
      encOperand x, encOperand y, encPrinted D k] ∧
    encode (.not a) = Json.arr #[.str "not", encode a] ∧
    encode (.and a b) = Json.arr #[.str "and", encode a, encode b] ∧
    encode (.or a b) = Json.arr #[.str "or", encode a, encode b] ∧
    encode (.implies a b) = Json.arr #[.str "implies", encode a, encode b] :=
  ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩

end VE.Cardinality.Wire
