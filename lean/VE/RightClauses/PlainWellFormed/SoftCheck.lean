import VE.RightClauses.PlainWellFormed.W1Check

/-! `checkSoft` under a change of guards (8.3, `plain_wellFormed`). `checkSoft D` is `checkSoftK D (checkW1 D.base)
(tailK D)` (`checkSoft_eq`, `rfl`): a prefix that reads no guard, with two holes, W1's check of the base document
and the tail (6.9-6.15). On `mapG γ C` the prefix is the same (`checkSoftK_mapG`), and the tail throws nothing but
resource limits apart from `validateW1 (soften ·)`. Proof vocabulary only. -/
namespace VE.RightClauses.PWF
open VE.SoftNorms
open VE.Norms (syms elabPremise targets targetConclusion)

/-- `checkSoft` from 6.9 on (the same statements). -/
def tailK (D : SoftDoc) : Except String Unit := do
  for (N, s) in D.T.nodes.zip (derivedSizes D) do
    if N.carveOuts.length + (if hasDerived N then 1 else 0) > 8 || (hasDerived N && !fits s) then
      throw s!"ResourceLimit: derived carve-out of rule {N.name}"
  for N in D.T.nodes do
    unless (derivedList D N).all withinLimits do
      throw s!"ResourceLimit: derived carve-out of rule {N.name}"
  validateW1 (soften D)
  let sizes := generatedSizes D
  for s in sizes.soft do
    unless fits s do throw "ResourceLimit: generated soft premise"
  for φ in softPremises D do
    unless withinLimits φ do throw "ResourceLimit: generated soft premise"
  for (p, s) in sizes.layers do
    unless fits s do throw s!"ResourceLimit: generated norm layer layer:norms:{p}"
  for s in syms (soften D).T do
    if let .reg r := s then
      unless withinLimits (elabPremise (soften D).T r) do
        throw s!"ResourceLimit: generated norm layer layer:norms:{r.name}"
  for (t, s) in sizes.targets do
    unless fits s do throw s!"ResourceLimit: generated conflict target {t}"
  for t in targets (soften D) do
    unless withinLimits (targetConclusion t) do throw s!"ResourceLimit: generated conflict target {t.1}"
  unless fitsTogether ((VE.Norms.background (soften D)).map (fsize noSubst) ++ sizes.soft) do
    throw "ResourceLimit: generated background"
  unless fitsTogether (sizes.layers.map (·.2) ++ [fsize noSubst .top]) do
    throw "ResourceLimit: generated norm layers"

/-- `checkSoft` up to 6.9, with W1's check of the base document as `w` and the rest as `k`. -/
def checkSoftK (D : SoftDoc) (w k : Except String Unit) : Except String Unit := do
  let env := D.soft
  checkSoftEnv D
  for (p, _) in D.T.regulated.map (fun r => (r.name, r.sorts)) do
    if containsDunder p then throw s!"InvalidInput: invalid soft name {p}"
  for p in D.T.definitions.map (·.name) do
    if reservedPredicate p then throw s!"InvalidInput: invalid soft name {p}"
  w
  for N in D.T.nodes do
    checkSoftRule D N
  for N in D.T.nodes do
    if N.mode = .default then
      for m in N.over do
        match D.T.nodes.find? (·.name == m) with
        | some M => if M.mode = .strict then throw s!"SoftOverHard: rule {N.name} over {M.name}"
        | none => pure ()
  match checkSoft.dependencyOrderOf env with
  | .error e => throw e
  | .ok _ => pure ()
  for (a, b) in env.ties do
    if outranksPlus env a b || outranksPlus env b a then throw s!"TieAgainstOrder: {a}, {b}"
  if (env.ties.map (fun (a, b) => if a ≤ b then (a, b) else (b, a))).eraseDups.length != env.ties.length then
    throw "DuplicateDeclaration: tie"
  k

theorem checkSoft_eq (D : SoftDoc) : checkSoft D = checkSoftK D (checkW1 D.base) (tailK D) := rfl

theorem forIn_map_congr {α β ε : Type} (h : α → β) (l : List α) (f : β → PUnit → Except ε (ForInStep PUnit))
    (g : α → PUnit → Except ε (ForInStep PUnit)) (hfg : ∀ a ∈ l, f (h a) = g a) :
    forIn (l.map h) PUnit.unit f = forIn l PUnit.unit g := by
  rw [List.forIn_map]; exact forIn_congr_fun l _ _ hfg

variable (γ : String → VE.Formula → VE.Formula)

theorem checkSoftRule_mapG (C : SoftDoc) (N : SoftNode) : checkSoftRule (mapG γ C) (setG γ N) = checkSoftRule C N := rfl
theorem checkSoftEnv_mapG (C : SoftDoc) : checkSoftEnv (mapG γ C) = checkSoftEnv C := rfl

theorem checkSoftK_mapG (C : SoftDoc) (w k : Except String Unit) :
    checkSoftK (mapG γ C) w k = checkSoftK C w k := by
  unfold checkSoftK
  simp only [checkSoftEnv_mapG, mapG_regulated, mapG_definitions, mapG_soft, mapG_nodes]
  rw [forIn_map_congr (setG γ) C.T.nodes _ ?g1 ?h1]
  rw [forIn_map_congr (setG γ) C.T.nodes _ ?g2 ?h2]
  case h1 => intro N _; rfl
  case h2 =>
    intro N _; funext u
    simp only [setG_mode, setG_over]
    split
    · congr 1; congr 1; funext m v
      simp only [List.find?_map, Function.comp_def, setG_name]
      cases C.T.nodes.find? (fun x => x.name == m) with
      | none => rfl
      | some M => rfl
    · rfl

/-! ### `checkSoftK` as a shape over its steps -/

/-- The statements of `checkSoftK`, each a variable. -/
def shapeK (x1 : Except String Unit) (x2 x3 : Except String PUnit) (w : Except String Unit)
    (x4 x5 : Except String PUnit) (m : Except String (List String)) (x6 : Except String PUnit) (c : Bool)
    (k : Except String Unit) : Except String Unit := do
  x1
  x2
  x3
  w
  x4
  x5
  match m with
  | .error e => throw e
  | .ok _ => pure ()
  x6
  if c then throw "DuplicateDeclaration: tie"
  k

def b2 (x : String × List String) (_ : PUnit) : Except String (ForInStep PUnit) := do
  if containsDunder x.1 then throw s!"InvalidInput: invalid soft name {x.1}"
  pure (ForInStep.yield PUnit.unit)
def b3 (p : String) (_ : PUnit) : Except String (ForInStep PUnit) := do
  if reservedPredicate p then throw s!"InvalidInput: invalid soft name {p}"
  pure (ForInStep.yield PUnit.unit)
def b4 (D : SoftDoc) (N : SoftNode) (_ : PUnit) : Except String (ForInStep PUnit) := do
  checkSoftRule D N
  pure (ForInStep.yield PUnit.unit)
def b5 (D : SoftDoc) (N : SoftNode) (_ : PUnit) : Except String (ForInStep PUnit) := do
  if N.mode = .default then
    for m in N.over do
      match D.T.nodes.find? (·.name == m) with
      | some M => if M.mode = .strict then throw s!"SoftOverHard: rule {N.name} over {M.name}"
      | none => pure ()
  pure (ForInStep.yield PUnit.unit)
def b6 (D : SoftDoc) (x : String × String) (_ : PUnit) : Except String (ForInStep PUnit) := do
  if outranksPlus D.soft x.1 x.2 || outranksPlus D.soft x.2 x.1 then throw s!"TieAgainstOrder: {x.1}, {x.2}"
  pure (ForInStep.yield PUnit.unit)
def ck7 (D : SoftDoc) : Bool :=
  (D.soft.ties.map (fun (a, b) => if a ≤ b then (a, b) else (b, a))).eraseDups.length != D.soft.ties.length

theorem checkSoftK_shape (D : SoftDoc) (w k : Except String Unit) :
    checkSoftK D w k = shapeK (checkSoftEnv D) (forIn (D.T.regulated.map (fun r => (r.name, r.sorts))) PUnit.unit b2)
      (forIn (D.T.definitions.map (·.name)) PUnit.unit b3) w (forIn D.T.nodes PUnit.unit (b4 D))
      (forIn D.T.nodes PUnit.unit (b5 D)) (checkSoft.dependencyOrderOf D.soft)
      (forIn D.soft.ties PUnit.unit (b6 D)) (ck7 D) k := rfl

theorem shapeK_ok {x1 : Except String Unit} {x2 x3 : Except String PUnit} {w : Except String Unit}
    {x4 x5 : Except String PUnit} {m : Except String (List String)} {x6 : Except String PUnit} {c : Bool}
    {k : Except String Unit} (h : shapeK x1 x2 x3 w x4 x5 m x6 c k = .ok ()) :
    w = .ok () ∧ k = .ok () ∧ ∀ w' k' : Except String Unit, shapeK x1 x2 x3 w' x4 x5 m x6 c k' = (w' >>= fun _ => k') := by
  unfold shapeK at h ⊢
  cases x1 <;> cases x2 <;> cases x3 <;> cases w <;> cases x4 <;> cases x5 <;> cases m <;> cases x6 <;> cases c <;>
    simp_all [bind, Except.bind, pure, Except.pure, throw, throwThe, MonadExceptOf.throw]

/-! ### The tail: resource limits around `validateW1 (soften ·)` -/

/-- Success with any value, or a resource limit. -/
def OkOrRLV {α : Type} (x : Except String α) : Prop := (∃ a, x = .ok a) ∨ ∃ e, x = .error e ∧ RL e

theorem okOrRLV_forIn {α : Type} (l : List α) (f : α → PUnit → Except String (ForInStep PUnit))
    (hf : ∀ a u, f a u = .ok (.yield PUnit.unit) ∨ ∃ e, f a u = .error e ∧ RL e) :
    OkOrRLV (forIn l PUnit.unit f) := by
  induction l with
  | nil => exact Or.inl ⟨_, rfl⟩
  | cons a l ih =>
    rw [List.forIn_cons]
    rcases hf a PUnit.unit with h | ⟨e, h, he⟩
    · rw [h]; exact ih
    · exact Or.inr ⟨e, by rw [h]; rfl, he⟩

def bt1 (x : SoftNode × FSize) (_ : PUnit) : Except String (ForInStep PUnit) := do
  if x.1.carveOuts.length + (if hasDerived x.1 then 1 else 0) > 8 || (hasDerived x.1 && !fits x.2) then
    throw s!"ResourceLimit: derived carve-out of rule {x.1.name}"
  pure (ForInStep.yield PUnit.unit)
def bt2 (D : SoftDoc) (N : SoftNode) (_ : PUnit) : Except String (ForInStep PUnit) := do
  unless (derivedList D N).all withinLimits do
    throw s!"ResourceLimit: derived carve-out of rule {N.name}"
  pure (ForInStep.yield PUnit.unit)

/-- `tailK` after `validateW1 (soften D)`. -/
def restT (D : SoftDoc) : Except String Unit := do
  let sizes := generatedSizes D
  for s in sizes.soft do
    unless fits s do throw "ResourceLimit: generated soft premise"
  for φ in softPremises D do
    unless withinLimits φ do throw "ResourceLimit: generated soft premise"
  for (p, s) in sizes.layers do
    unless fits s do throw s!"ResourceLimit: generated norm layer layer:norms:{p}"
  for s in syms (soften D).T do
    if let .reg r := s then
      unless withinLimits (elabPremise (soften D).T r) do
        throw s!"ResourceLimit: generated norm layer layer:norms:{r.name}"
  for (t, s) in sizes.targets do
    unless fits s do throw s!"ResourceLimit: generated conflict target {t}"
  for t in targets (soften D) do
    unless withinLimits (targetConclusion t) do throw s!"ResourceLimit: generated conflict target {t.1}"
  unless fitsTogether ((VE.Norms.background (soften D)).map (fsize noSubst) ++ sizes.soft) do
    throw "ResourceLimit: generated background"
  unless fitsTogether (sizes.layers.map (·.2) ++ [fsize noSubst .top]) do
    throw "ResourceLimit: generated norm layers"

def shapeT (y1 y2 : Except String PUnit) (v rest : Except String Unit) : Except String Unit := do
  y1
  y2
  v
  rest

theorem tailK_shape (D : SoftDoc) :
    tailK D = shapeT (forIn (D.T.nodes.zip (derivedSizes D)) PUnit.unit bt1) (forIn D.T.nodes PUnit.unit (bt2 D))
      (validateW1 (soften D)) (restT D) := rfl

theorem rl_lit {e t : String} (h : e = "ResourceLimit: " ++ t) : RL e := ⟨t, h⟩

def br1 (s : FSize) (_ : PUnit) : Except String (ForInStep PUnit) := do
  unless fits s do throw "ResourceLimit: generated soft premise"
  pure (ForInStep.yield PUnit.unit)
def br2 (φ : VE.Formula) (_ : PUnit) : Except String (ForInStep PUnit) := do
  unless withinLimits φ do throw "ResourceLimit: generated soft premise"
  pure (ForInStep.yield PUnit.unit)
def br3 (x : String × FSize) (_ : PUnit) : Except String (ForInStep PUnit) := do
  unless fits x.2 do throw s!"ResourceLimit: generated norm layer layer:norms:{x.1}"
  pure (ForInStep.yield PUnit.unit)
def br4 (D : SoftDoc) (s : VE.Norms.Sym) (_ : PUnit) : Except String (ForInStep PUnit) := do
  if let .reg r := s then
    unless withinLimits (elabPremise (soften D).T r) do
      throw s!"ResourceLimit: generated norm layer layer:norms:{r.name}"
  pure (ForInStep.yield PUnit.unit)
def br5 (x : String × FSize) (_ : PUnit) : Except String (ForInStep PUnit) := do
  unless fits x.2 do throw s!"ResourceLimit: generated conflict target {x.1}"
  pure (ForInStep.yield PUnit.unit)
def br6 (t : String × List String × VE.Formula) (_ : PUnit) : Except String (ForInStep PUnit) := do
  unless withinLimits (targetConclusion t) do throw s!"ResourceLimit: generated conflict target {t.1}"
  pure (ForInStep.yield PUnit.unit)

def shapeR (z1 z2 z3 z4 z5 z6 : Except String PUnit) (c1 c2 : Bool) : Except String Unit := do
  z1
  z2
  z3
  z4
  z5
  z6
  unless c1 do throw "ResourceLimit: generated background"
  unless c2 do throw "ResourceLimit: generated norm layers"

theorem restT_shape (D : SoftDoc) :
    restT D = shapeR (forIn (generatedSizes D).soft PUnit.unit br1) (forIn (softPremises D) PUnit.unit br2)
      (forIn (generatedSizes D).layers PUnit.unit br3) (forIn (syms (soften D).T) PUnit.unit (br4 D))
      (forIn (generatedSizes D).targets PUnit.unit br5) (forIn (targets (soften D)) PUnit.unit br6)
      (fitsTogether ((VE.Norms.background (soften D)).map (fsize noSubst) ++ (generatedSizes D).soft))
      (fitsTogether ((generatedSizes D).layers.map (·.2) ++ [fsize noSubst .top])) := rfl

theorem shapeR_rl {z1 z2 z3 z4 z5 z6 : Except String PUnit} (c1 c2 : Bool) (h1 : OkOrRLV z1) (h2 : OkOrRLV z2)
    (h3 : OkOrRLV z3) (h4 : OkOrRLV z4) (h5 : OkOrRLV z5) (h6 : OkOrRLV z6) :
    OkOrRL (shapeR z1 z2 z3 z4 z5 z6 c1 c2) := by
  unfold shapeR
  rcases h1 with ⟨_, rfl⟩ | ⟨e, rfl, he⟩ <;> try exact Or.inr ⟨e, rfl, he⟩
  rcases h2 with ⟨_, rfl⟩ | ⟨e, rfl, he⟩ <;> try exact Or.inr ⟨e, rfl, he⟩
  rcases h3 with ⟨_, rfl⟩ | ⟨e, rfl, he⟩ <;> try exact Or.inr ⟨e, rfl, he⟩
  rcases h4 with ⟨_, rfl⟩ | ⟨e, rfl, he⟩ <;> try exact Or.inr ⟨e, rfl, he⟩
  rcases h5 with ⟨_, rfl⟩ | ⟨e, rfl, he⟩ <;> try exact Or.inr ⟨e, rfl, he⟩
  rcases h6 with ⟨_, rfl⟩ | ⟨e, rfl, he⟩ <;> try exact Or.inr ⟨e, rfl, he⟩
  cases c1 <;> cases c2 <;> simp only [bind, Except.bind, pure, Except.pure, Bool.false_eq_true, if_false, if_true] <;>
    first | exact Or.inl rfl | exact Or.inr ⟨_, rfl, rl_lit (t := "generated background") (by decide)⟩ |
      exact Or.inr ⟨_, rfl, rl_lit (t := "generated norm layers") (by decide)⟩

/-- A loop body that yields or throws one resource-limit text. -/
theorem body_rl {f : PUnit → Except String (ForInStep PUnit)} (c : Bool) (e : String) (he : RL e)
    (hf : f PUnit.unit = if c then pure (ForInStep.yield PUnit.unit) else .error e) :
    f PUnit.unit = .ok (.yield PUnit.unit) ∨ ∃ e', f PUnit.unit = .error e' ∧ RL e' := by
  cases c
  · exact Or.inr ⟨e, by rw [hf]; rfl, he⟩
  · exact Or.inl (by rw [hf]; rfl)

theorem restT_rl (D : SoftDoc) : OkOrRL (restT D) := by
  rw [restT_shape]
  refine shapeR_rl _ _ ?_ ?_ ?_ ?_ ?_ ?_ <;> refine okOrRLV_forIn _ _ (fun x u => ?_) <;> cases u
  · exact body_rl (fits x) "ResourceLimit: generated soft premise" ⟨"generated soft premise", by decide⟩ (by unfold br1; cases fits x <;> rfl)
  · exact body_rl (withinLimits x) "ResourceLimit: generated soft premise" ⟨"generated soft premise", by decide⟩ (by unfold br2; cases withinLimits x <;> rfl)
  · exact body_rl (fits x.2) _ (rl_interp "ResourceLimit: generated norm layer layer:norms:" "generated norm layer layer:norms:" x.1 (by decide))
      (by unfold br3; cases fits x.2 <;> rfl)
  · cases x with
    | defn d => exact Or.inl rfl
    | reg r =>
      exact body_rl (withinLimits (elabPremise (soften D).T r)) _
        (rl_interp "ResourceLimit: generated norm layer layer:norms:" "generated norm layer layer:norms:" r.name (by decide))
        (by unfold br4; dsimp only; cases withinLimits (elabPremise (soften D).T r) <;> rfl)
  · exact body_rl (fits x.2) _ (rl_interp "ResourceLimit: generated conflict target " "generated conflict target " x.1 (by decide))
      (by unfold br5; cases fits x.2 <;> rfl)
  · exact body_rl (withinLimits (targetConclusion x)) _ (rl_interp "ResourceLimit: generated conflict target " "generated conflict target " x.1 (by decide))
      (by unfold br6; cases withinLimits (targetConclusion x) <;> rfl)

theorem tail_loops_rl (D : SoftDoc) : OkOrRLV (forIn (D.T.nodes.zip (derivedSizes D)) PUnit.unit bt1) ∧
    OkOrRLV (forIn D.T.nodes PUnit.unit (bt2 D)) := by
  refine ⟨okOrRLV_forIn _ _ (fun x u => ?_), okOrRLV_forIn _ _ (fun N u => ?_)⟩ <;> cases u
  · exact body_rl (!(x.1.carveOuts.length + (if hasDerived x.1 then 1 else 0) > 8 || (hasDerived x.1 && !fits x.2))) _
      (rl_interp "ResourceLimit: derived carve-out of rule " "derived carve-out of rule " x.1.name (by decide))
      (by
        unfold bt1
        generalize (decide (x.1.carveOuts.length + (if hasDerived x.1 then 1 else 0) > 8) ||
          (hasDerived x.1 && !fits x.2)) = b
        cases b <;> rfl)
  · exact body_rl ((derivedList D N).all withinLimits) _ (rl_interp "ResourceLimit: derived carve-out of rule " "derived carve-out of rule " N.name (by decide))
      (by unfold bt2; cases (derivedList D N).all withinLimits <;> rfl)

theorem shapeT_ok {y1 y2 : Except String PUnit} {v rest : Except String Unit} (h : shapeT y1 y2 v rest = .ok ()) :
    v = .ok () := by
  unfold shapeT at h
  cases y1 <;> cases y2 <;> cases v <;> simp_all [bind, Except.bind]

theorem shapeT_rl {y1 y2 : Except String PUnit} {v rest : Except String Unit} (h1 : OkOrRLV y1) (h2 : OkOrRLV y2)
    (hv : OkOrRL v) (hr : OkOrRL rest) : OkOrRL (shapeT y1 y2 v rest) := by
  unfold shapeT
  rcases h1 with ⟨_, rfl⟩ | ⟨e, rfl, he⟩ <;> try exact Or.inr ⟨e, rfl, he⟩
  rcases h2 with ⟨_, rfl⟩ | ⟨e, rfl, he⟩ <;> try exact Or.inr ⟨e, rfl, he⟩
  rcases hv with rfl | ⟨e, rfl, he⟩ <;> try exact Or.inr ⟨e, rfl, he⟩
  exact hr

/-- The tail passes or reports a resource limit when `validateW1 (soften D)` does. -/
theorem tailK_rl (D : SoftDoc) (hv : OkOrRL (validateW1 (soften D))) : OkOrRL (tailK D) := by
  rw [tailK_shape]
  exact shapeT_rl (tail_loops_rl D).1 (tail_loops_rl D).2 hv (restT_rl D)

theorem tailK_ok (D : SoftDoc) (h : tailK D = .ok ()) : validateW1 (soften D) = .ok () := by
  rw [tailK_shape] at h; exact shapeT_ok h

end VE.RightClauses.PWF
