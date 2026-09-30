import VE.NormDefaults.Tree

/-! W1's executable `check` (norms 3.1, 4.1, 11.1) as declarative conditions,
for `fill_wellFormed` (docs/spec/norm-defaults.md 7, proof plan: it "walks W1's
`check` and `semanticCheck` on `T‴`").

`checkSteps` is `check` with its loop bodies named; `check_eq` is `rfl`, so
nothing about `check` is restated. `check_iff` reads it as `CheckOK`: the
declaration checks, the rule checks (names, predicate, carve-outs, typing, the
shared AST budget), the precedence references, both DAG orders and the height
limit. -/
namespace VE.NormDefaults
open VE.Norms VE.Route

/-! ## `Except` loops -/

theorem forIn_cons_ok {α σ ε : Type} (f : α → σ → Except ε (ForInStep σ)) (step : σ → σ) (cond : Prop)
    (x : α) (l : List α) (s s' : σ)
    (hf : (f x s = .ok (.yield (step s)) ↔ cond) ∧ (∀ r, f x s = .ok r → r = .yield (step s))) :
    forIn (x :: l) s f = .ok s' ↔ cond ∧ forIn l (step s) f = .ok s' := by
  rw [List.forIn_cons]
  cases hx : f x s with
  | error e =>
    simp only [bind, Except.bind]
    constructor
    · intro h; cases h
    · rintro ⟨hc, _⟩
      have := hf.1.mpr hc
      rw [hx] at this; cases this
  | ok r =>
    have hr := hf.2 r hx
    subst hr
    have hc : cond := hf.1.mp hx
    simp only [bind, Except.bind]
    exact ⟨fun h => ⟨hc, h⟩, fun h => h.2⟩

theorem forIn_nil_ok {α σ ε : Type} (f : α → σ → Except ε (ForInStep σ)) (s s' : σ) :
    forIn ([] : List α) s f = .ok s' ↔ s' = s := by
  simp only [List.forIn_nil, pure, Except.pure, Except.ok.injEq]
  exact eq_comm

theorem forIn_unit_ok {α ε : Type} (f : α → PUnit.{1} → Except ε (ForInStep PUnit.{1}))
    (hf : ∀ x r, f x PUnit.unit = .ok r → r = .yield PUnit.unit) :
    ∀ l : List α, forIn l PUnit.unit f = .ok PUnit.unit ↔ ∀ x ∈ l, f x PUnit.unit = .ok (.yield PUnit.unit)
  | [] => by
    simp only [List.forIn_nil, List.not_mem_nil, false_implies, implies_true, iff_true]
    rfl
  | x :: l => by
    have := forIn_cons_ok f (fun s => s) (f x PUnit.unit = .ok (.yield PUnit.unit)) x l PUnit.unit PUnit.unit
      ⟨Iff.rfl, hf x⟩
    rw [this, forIn_unit_ok f hf l]
    simp only [List.mem_cons, forall_eq_or_imp]

theorem ebind_ok {ε α β : Type} (x : Except ε α) (f : α → Except ε β) (b : β) :
    (x >>= f) = .ok b ↔ ∃ a, x = .ok a ∧ f a = .ok b := by
  cases x <;> simp [bind, Except.bind]

theorem ethrow_ok {ε α : Type} (e : ε) (a : α) : (throw e : Except ε α) = .ok a ↔ False := by
  simp [throw, throwThe, MonadExceptOf.throw]

theorem epure_ok {ε α : Type} (a b : α) : (pure a : Except ε α) = .ok b ↔ a = b := by
  simp [pure, Except.pure]

/-! ## `check` with named loop bodies -/

def dupNameOf (ns : List String) : Option String := ns.find? (fun n => ns.count n > 1)

def regBody (D : Doc) (r : Regulated) (_ : PUnit.{1}) : Except String (ForInStep PUnit.{1}) :=
  if (D.E.predicates r.name == some r.sorts) = true then
    if (r.sorts.length == 1 || r.sorts.length == 2) = true then
      if r.sorts.all D.E.sorts.contains = true then
        match r.role, r.act with
        | .plain, some _ => throw s!"InvalidInput: invalid regulated fields for {r.name}"
        | .permission, none => throw s!"InvalidInput: invalid regulated fields for {r.name}"
        | .obligation, none => throw s!"InvalidInput: invalid regulated fields for {r.name}"
        | _, _ =>
          if (r.role != .obligation && r.permission.isSome) = true then
            throw s!"InvalidInput: invalid regulated fields for {r.name}"
          else pure (.yield PUnit.unit)
      else throw s!"UnknownSymbol: sort of {r.name}"
    else throw s!"UnsupportedArity: regulated predicate {r.name}"
  else throw s!"UnknownSymbol: regulated predicate {r.name}"

def defBody (D : Doc) (d : Definition) (_ : PUnit.{1}) : Except String (ForInStep PUnit.{1}) :=
  if (D.E.predicates d.name == some d.args) = true then
    if (d.args.length == 1 || d.args.length == 2) = true then
      if d.args.all D.E.sorts.contains = true then
        typeDiagnostic D.E d.args.reverse d.body >>= fun _ =>
          if VE.Formula.check D.E d.args.reverse d.body = true then pure (.yield PUnit.unit)
          else throw s!"InvalidInput: ill-typed definition {d.name}"
      else throw s!"UnknownSymbol: sort of {d.name}"
    else throw s!"UnsupportedArity: defined predicate {d.name}"
  else throw s!"UnknownSymbol: defined predicate {d.name}"

def astBody (D : Doc) (r : Regulated) (N : Node) (φ : VE.Formula) (nodes : Nat) :
    Except String (ForInStep Nat) :=
  typeDiagnostic D.E r.sorts.reverse φ >>= fun _ =>
    if VE.Formula.check D.E r.sorts.reverse φ = true then
      if nodes + VE.Bridge.formulaNodes φ > 10000 then throw "ResourceLimit: AST exceeds 10,000 nodes"
      else pure (.yield (nodes + VE.Bridge.formulaNodes φ))
    else throw s!"InvalidInput: ill-typed rule {N.name}"

def ruleBody (D : Doc) (N : Node) (st : MProd (List String) Nat) :
    Except String (ForInStep (MProd (List String) Nat)) :=
  if ruleName N.name = true then
    if st.fst.contains N.name = true then throw s!"DuplicateDeclaration: rule {N.name}"
    else match D.T.regulated.find? (fun x => x.name == N.pred) with
      | none => throw s!"UnknownSymbol: regulated predicate {N.pred}"
      | some r =>
        if N.carveOuts.length > 8 then throw "InvalidInput: invalid sign or too many carve-outs"
        else forIn (N.guard :: N.carveOuts) st.snd (astBody D r N) >>= fun nodes =>
          pure (.yield ⟨st.fst ++ [N.name], nodes⟩)
  else throw s!"InvalidInput: invalid rule name {pyRepr N.name}"

def overInner (D : Doc) (N : Node) (m : String) (_ : PUnit.{1}) : Except String (ForInStep PUnit.{1}) :=
  match D.T.nodes.find? (fun x => x.name == m) with
  | none => throw s!"UnknownRule: rule {m}"
  | some M =>
    if (M.pred == N.pred) = true then pure (.yield PUnit.unit)
    else throw s!"PrecedenceAcrossPredicates: rule {N.name} on {N.pred}, rule {M.name} on {M.pred}"

def overBody (D : Doc) (N : Node) (_ : PUnit.{1}) : Except String (ForInStep PUnit.{1}) :=
  forIn N.over PUnit.unit (overInner D N) >>= fun _ => pure (.yield PUnit.unit)

/-- The steps after the rule loop. -/
def tailSteps (D : Doc) : Except String Unit :=
  forIn D.T.nodes PUnit.unit (overBody D) >>= fun _ =>
  match dependencyOrder (precedenceNodes D.T) with
  | .error e => throw e
  | .ok _ =>
    if (D.T.nodes.any fun N => decide (height D.T D.T.nodes.length N > 16)) = true then
      throw "ResourceLimit: precedence depth"
    else match dependencyOrder (stratumNodes D.T) with
      | .error e => throw e
      | .ok _ => pure ()

def checkSteps (D : Doc) : Except String Unit :=
  if D.T.regulated.length > 64 then throw "ResourceLimit: regulated predicates" else
  match dupNameOf (regulatedNames D.T ++ D.T.definitions.map Definition.name) with
  | some n => throw s!"DuplicateDeclaration: predicate {n}"
  | _ =>
    forIn D.T.regulated PUnit.unit (regBody D) >>= fun _ =>
    actChecks D.T.regulated >>= fun _ =>
    forIn D.T.definitions PUnit.unit (defBody D) >>= fun _ =>
    if D.T.nodes.length > 256 then throw "ResourceLimit: rules" else
    forIn D.T.nodes (⟨[], 0⟩ : MProd (List String) Nat) (ruleBody D) >>= fun r =>
    match r with
    | ⟨_, _⟩ => tailSteps D

/-- `check` is `checkSteps`, definitionally. -/
theorem check_eq (D : Doc) : check D = checkSteps D := rfl

/-! ## The loop bodies as conditions -/

/-- The role, act and dual fields of a regulated declaration (3.1). -/
def fieldsOK (r : Regulated) : Bool :=
  match r.role, r.act with
  | .plain, some _ => false
  | .permission, none => false
  | .obligation, none => false
  | _, _ => !(r.role != .obligation && r.permission.isSome)

def RegOK (D : Doc) (r : Regulated) : Prop :=
  D.E.predicates r.name = some r.sorts ∧ (r.sorts.length = 1 ∨ r.sorts.length = 2) ∧
    (∀ s ∈ r.sorts, s ∈ D.E.sorts) ∧ fieldsOK r = true

theorem regBody_ok (D : Doc) (r : Regulated) :
    (regBody D r PUnit.unit = .ok (.yield PUnit.unit) ↔ RegOK D r) ∧
    (∀ x, regBody D r PUnit.unit = .ok x → x = .yield PUnit.unit) := by
  unfold regBody RegOK fieldsOK
  by_cases h1 : D.E.predicates r.name = some r.sorts <;>
  by_cases h2 : (r.sorts.length = 1 ∨ r.sorts.length = 2) <;>
  by_cases h3 : (∀ s ∈ r.sorts, s ∈ D.E.sorts) <;>
  cases hr : r.role <;> cases ha : r.act <;> cases hp : r.permission <;>
  simp_all [List.all_eq_true, pure, Except.pure] <;>
  (try split) <;> simp_all

def DefOK (D : Doc) (d : Definition) : Prop :=
  D.E.predicates d.name = some d.args ∧ (d.args.length = 1 ∨ d.args.length = 2) ∧
    (∀ s ∈ d.args, s ∈ D.E.sorts) ∧ typeDiagnostic D.E d.args.reverse d.body = .ok () ∧
    VE.Formula.check D.E d.args.reverse d.body = true

theorem defBody_ok (D : Doc) (d : Definition) :
    (defBody D d PUnit.unit = .ok (.yield PUnit.unit) ↔ DefOK D d) ∧
    (∀ x, defBody D d PUnit.unit = .ok x → x = .yield PUnit.unit) := by
  unfold defBody DefOK
  by_cases h1 : D.E.predicates d.name = some d.args <;>
  by_cases h2 : (d.args.length = 1 ∨ d.args.length = 2) <;>
  by_cases h3 : (∀ s ∈ d.args, s ∈ D.E.sorts) <;>
  cases ht : typeDiagnostic D.E d.args.reverse d.body <;>
  by_cases h4 : VE.Formula.check D.E d.args.reverse d.body = true <;>
  simp_all [List.all_eq_true, pure, Except.pure, bind, Except.bind] <;>
  (try split) <;> simp_all

/-- One rule's checks, apart from the shared name list and AST budget. -/
def NodeOK (D : Doc) (N : Node) : Prop :=
  ruleName N.name = true ∧ N.carveOuts.length ≤ 8 ∧
    ∃ r, D.T.regulated.find? (fun x => x.name == N.pred) = some r ∧
      ∀ φ ∈ N.guard :: N.carveOuts,
        typeDiagnostic D.E r.sorts.reverse φ = .ok () ∧ VE.Formula.check D.E r.sorts.reverse φ = true

theorem astBody_ok (D : Doc) (r : Regulated) (N : Node) (φ : VE.Formula) (n : Nat) :
    (astBody D r N φ n = .ok (.yield (n + VE.Bridge.formulaNodes φ)) ↔
      typeDiagnostic D.E r.sorts.reverse φ = .ok () ∧ VE.Formula.check D.E r.sorts.reverse φ = true ∧
        n + VE.Bridge.formulaNodes φ ≤ 10000) ∧
    (∀ x, astBody D r N φ n = .ok x → x = .yield (n + VE.Bridge.formulaNodes φ)) := by
  unfold astBody
  cases ht : typeDiagnostic D.E r.sorts.reverse φ with
  | error e => simp [bind, Except.bind]
  | ok u =>
    simp only [bind, Except.bind]
    by_cases h4 : VE.Formula.check D.E r.sorts.reverse φ = true
    · simp only [h4, if_true]
      by_cases h5 : n + VE.Bridge.formulaNodes φ > 10000
      · simp only [h5, if_true, ethrow_ok, false_iff, false_implies, implies_true, and_true]
        omega
      · simp only [h5, if_false, pure, Except.pure, Except.ok.injEq, true_and]
        exact ⟨⟨fun _ => by omega, fun _ => trivial⟩, fun x hx => hx.symm⟩
    · simp [h4, ethrow_ok]

theorem astLoop_ok (D : Doc) (r : Regulated) (N : Node) :
    ∀ (L : List VE.Formula) (n n' : Nat), forIn L n (astBody D r N) = .ok n' ↔
      (∀ φ ∈ L, typeDiagnostic D.E r.sorts.reverse φ = .ok () ∧ VE.Formula.check D.E r.sorts.reverse φ = true) ∧
      (L ≠ [] → n + (L.map VE.Bridge.formulaNodes).sum ≤ 10000) ∧ n' = n + (L.map VE.Bridge.formulaNodes).sum
  | [], n, n' => by rw [forIn_nil_ok]; simp
  | φ :: L, n, n' => by
    rw [forIn_cons_ok _ (· + VE.Bridge.formulaNodes φ) _ φ L n n' (astBody_ok D r N φ n), astLoop_ok D r N L]
    simp only [List.mem_cons, forall_eq_or_imp, List.map_cons, List.sum_cons, ne_eq, reduceCtorEq,
      not_false_eq_true, forall_const]
    constructor
    · rintro ⟨⟨h1, h2, h3⟩, h4, h5, h6⟩
      refine ⟨⟨⟨h1, h2⟩, h4⟩, ?_, by rw [h6]; omega⟩
      by_cases hL : L = []
      · subst hL; simpa using h3
      · have := h5 hL; omega
    · rintro ⟨⟨⟨h1, h2⟩, h4⟩, h5, h6⟩
      exact ⟨⟨h1, h2, by omega⟩, h4, fun _ => by omega, by rw [h6]; omega⟩

theorem ruleBody_ok (D : Doc) (N : Node) (names : List String) (k : Nat) :
    (ruleBody D N ⟨names, k⟩ = .ok (.yield ⟨names ++ [N.name], k + ruleNodes N⟩) ↔
      NodeOK D N ∧ N.name ∉ names ∧ k + ruleNodes N ≤ 10000) ∧
    (∀ x, ruleBody D N ⟨names, k⟩ = .ok x → x = .yield ⟨names ++ [N.name], k + ruleNodes N⟩) := by
  unfold ruleBody NodeOK
  by_cases h1 : ruleName N.name = true
  · by_cases h2 : names.contains N.name = true
    · have h2' : N.name ∈ names := by simpa using h2
      simp [h1, ethrow_ok, h2']
    · have h2' : N.name ∉ names := by simpa using h2
      simp only [h1, h2, if_true, Bool.false_eq_true, if_false]
      cases hf : D.T.regulated.find? (fun x => x.name == N.pred) with
      | none => simp [ethrow_ok]
      | some r =>
        simp only
        by_cases h3 : N.carveOuts.length > 8
        · simp only [h3, if_true, ethrow_ok, false_iff, false_implies, implies_true, and_true]
          omega
        · simp only [h3, if_false]
          have hl := astLoop_ok D r N (N.guard :: N.carveOuts) k
          constructor
          · rw [ebind_ok]
            constructor
            · rintro ⟨n', hn', hy⟩
              simp only [pure, Except.pure, Except.ok.injEq, ForInStep.yield.injEq, MProd.mk.injEq,
                true_and] at hy
              obtain ⟨hφ, hsum, _⟩ := (hl n').mp hn'
              exact ⟨⟨trivial, by omega, r, rfl, hφ⟩, h2', by unfold ruleNodes; exact hsum (by simp)⟩
            · rintro ⟨⟨_, _, r', hr', hφ⟩, _, hsum⟩
              cases hr'
              exact ⟨_, (hl _).mpr ⟨hφ, fun _ => hsum, rfl⟩, rfl⟩
          · intro x hx
            rw [ebind_ok] at hx
            obtain ⟨n', hn', hy⟩ := hx
            obtain ⟨_, _, rfl⟩ := (hl n').mp hn'
            simp only [pure, Except.pure, Except.ok.injEq] at hy
            rw [← hy]
            rfl
  · simp [h1, ethrow_ok]

def RulesOK (D : Doc) : Prop :=
  (∀ N ∈ D.T.nodes, NodeOK D N) ∧ (D.T.nodes.map Node.name).Nodup ∧ (D.T.nodes.map ruleNodes).sum ≤ 10000

theorem rulesLoop_ok (D : Doc) :
    ∀ (L : List Node) (names : List String) (k : Nat) (s' : MProd (List String) Nat),
      forIn L (⟨names, k⟩ : MProd (List String) Nat) (ruleBody D) = .ok s' ↔
        (∀ N ∈ L, NodeOK D N) ∧ (L.map Node.name).Nodup ∧ (∀ N ∈ L, N.name ∉ names) ∧
        (L ≠ [] → k + (L.map ruleNodes).sum ≤ 10000) ∧
        s' = ⟨names ++ L.map Node.name, k + (L.map ruleNodes).sum⟩
  | [], names, k, s' => by rw [forIn_nil_ok]; simp
  | N :: L, names, k, s' => by
    rw [forIn_cons_ok _ (fun _ => ⟨names ++ [N.name], k + ruleNodes N⟩) _ N L _ s' (ruleBody_ok D N names k),
      rulesLoop_ok D L]
    simp only [List.mem_cons, forall_eq_or_imp, List.map_cons, List.sum_cons, ne_eq, reduceCtorEq,
      not_false_eq_true, forall_const, List.nodup_cons, List.mem_map, List.mem_append,
      List.not_mem_nil, or_false, List.append_assoc, List.singleton_append]
    constructor
    · rintro ⟨⟨h1, h2, h3⟩, h4, h5, h6, h7, h8⟩
      refine ⟨⟨h1, h4⟩, ⟨fun ⟨N', hN', he⟩ => h6 N' hN' (Or.inr he), h5⟩,
        ⟨h2, fun N' hN' h => h6 N' hN' (Or.inl h)⟩, ?_,
        by rw [h8]; congr 1; omega⟩
      by_cases hL : L = []
      · subst hL; simpa using h3
      · have := h7 hL; omega
    · rintro ⟨⟨h1, h4⟩, ⟨h5, h5'⟩, ⟨h2, h6⟩, h7, h8⟩
      refine ⟨⟨h1, h2, by omega⟩, h4, h5', fun N' hN' h => h.elim (h6 N' hN') (fun he => h5 ⟨N', hN', he⟩),
        fun _ => by omega, by rw [h8]; congr 1; omega⟩

def OverOK (D : Doc) : Prop :=
  ∀ N ∈ D.T.nodes, ∀ m ∈ N.over, ∃ M, D.T.nodes.find? (fun x => x.name == m) = some M ∧ M.pred = N.pred

theorem overInner_ok (D : Doc) (N : Node) (m : String) :
    (overInner D N m PUnit.unit = .ok (.yield PUnit.unit) ↔
      ∃ M, D.T.nodes.find? (fun x => x.name == m) = some M ∧ M.pred = N.pred) ∧
    (∀ x, overInner D N m PUnit.unit = .ok x → x = .yield PUnit.unit) := by
  unfold overInner
  cases hf : D.T.nodes.find? (fun x => x.name == m) with
  | none => simp [ethrow_ok]
  | some M =>
    by_cases h : M.pred = N.pred <;> simp [h, ethrow_ok, pure, Except.pure]

theorem overBody_ok (D : Doc) (N : Node) :
    (overBody D N PUnit.unit = .ok (.yield PUnit.unit) ↔
      ∀ m ∈ N.over, ∃ M, D.T.nodes.find? (fun x => x.name == m) = some M ∧ M.pred = N.pred) ∧
    (∀ x, overBody D N PUnit.unit = .ok x → x = .yield PUnit.unit) := by
  unfold overBody
  have hl := forIn_unit_ok (overInner D N) (fun m => (overInner_ok D N m).2) N.over
  constructor
  · simp only [ebind_ok]
    constructor
    · rintro ⟨u, hu, _⟩
      intro m hm
      exact (overInner_ok D N m).1.mp (hl.mp hu m hm)
    · intro h
      exact ⟨PUnit.unit, hl.mpr fun m hm => (overInner_ok D N m).1.mpr (h m hm), rfl⟩
  · intro x hx
    simp only [ebind_ok] at hx
    obtain ⟨_, _, hy⟩ := hx
    simp only [pure, Except.pure, Except.ok.injEq] at hy
    exact hy.symm

theorem tailSteps_ok (D : Doc) :
    tailSteps D = .ok () ↔ OverOK D ∧ (∃ o, dependencyOrder (precedenceNodes D.T) = .ok o) ∧
      (∀ N ∈ D.T.nodes, height D.T D.T.nodes.length N ≤ 16) ∧
      (∃ o, dependencyOrder (stratumNodes D.T) = .ok o) := by
  unfold tailSteps
  have hl := forIn_unit_ok (overBody D) (fun N => (overBody_ok D N).2) D.T.nodes
  rw [ebind_ok]
  have hover : (∃ a, forIn D.T.nodes PUnit.unit (overBody D) = .ok a) ↔ OverOK D := by
    constructor
    · rintro ⟨u, hu⟩ N hN
      exact (overBody_ok D N).1.mp (hl.mp hu N hN)
    · intro h
      exact ⟨PUnit.unit, hl.mpr fun N hN => (overBody_ok D N).1.mpr (h N hN)⟩
  constructor
  · rintro ⟨u, hu, hrest⟩
    refine ⟨hover.mp ⟨u, hu⟩, ?_⟩
    split at hrest
    · simp [ethrow_ok] at hrest
    · rename_i o ho
      refine ⟨⟨o, ho⟩, ?_⟩
      split at hrest
      · simp [ethrow_ok] at hrest
      · rename_i hh
        refine ⟨fun N hN => ?_, ?_⟩
        · apply Nat.le_of_not_lt
          intro hgt
          exact hh (List.any_eq_true.mpr ⟨N, hN, by simpa using hgt⟩)
        · split at hrest
          · simp [ethrow_ok] at hrest
          · rename_i o' ho'
            exact ⟨o', ho'⟩
  · rintro ⟨h1, ⟨o, ho⟩, h3, ⟨o', ho'⟩⟩
    obtain ⟨u, hu⟩ := hover.mpr h1
    refine ⟨u, hu, ?_⟩
    rw [ho]
    simp only
    have hh : (D.T.nodes.any fun N => decide (height D.T D.T.nodes.length N > 16)) = false := by
      rw [Bool.eq_false_iff]
      intro h
      obtain ⟨N, hN, hgt⟩ := List.any_eq_true.mp h
      have := h3 N hN
      simp only [decide_eq_true_eq] at hgt
      omega
    rw [hh]
    simp only [Bool.false_eq_true, if_false, ho']
    rfl

/-- `check`, read declaratively. -/
def CheckOK (D : Doc) : Prop :=
  D.T.regulated.length ≤ 64 ∧
  dupNameOf (regulatedNames D.T ++ D.T.definitions.map Definition.name) = none ∧
  (∀ r ∈ D.T.regulated, RegOK D r) ∧ actChecks D.T.regulated = .ok () ∧
  (∀ d ∈ D.T.definitions, DefOK D d) ∧ D.T.nodes.length ≤ 256 ∧ RulesOK D ∧
  OverOK D ∧ (∃ o, dependencyOrder (precedenceNodes D.T) = .ok o) ∧
  (∀ N ∈ D.T.nodes, height D.T D.T.nodes.length N ≤ 16) ∧
  (∃ o, dependencyOrder (stratumNodes D.T) = .ok o)

theorem check_iff (D : Doc) : check D = .ok () ↔ CheckOK D := by
  rw [check_eq]
  unfold checkSteps CheckOK
  have hreg := forIn_unit_ok (regBody D) (fun r => (regBody_ok D r).2) D.T.regulated
  have hdef := forIn_unit_ok (defBody D) (fun d => (defBody_ok D d).2) D.T.definitions
  have hrules := rulesLoop_ok D D.T.nodes [] 0
  by_cases h64 : D.T.regulated.length > 64
  · rw [if_pos h64]
    simp only [ethrow_ok, false_iff]
    intro h; omega
  · rw [if_neg h64]
    cases hd : dupNameOf (regulatedNames D.T ++ D.T.definitions.map Definition.name) with
    | some n =>
      simp only [ethrow_ok, false_iff]
      intro h
      exact Option.noConfusion h.2.1
    | none =>
      simp only
      constructor
      · intro h
        obtain ⟨u₁, h₁, h⟩ := (ebind_ok _ _ _).mp h
        obtain ⟨u₂, h₂, h⟩ := (ebind_ok _ _ _).mp h
        obtain ⟨u₃, h₃, h⟩ := (ebind_ok _ _ _).mp h
        split at h
        · exact absurd h (by simp [ethrow_ok])
        · rename_i h256
          obtain ⟨st, hst, h⟩ := (ebind_ok _ _ _).mp h
          obtain ⟨hN, hnd, _, hsum, rfl⟩ := (hrules st).mp hst
          have htail : tailSteps D = .ok () := h
          refine ⟨by omega, trivial, fun r hr => (regBody_ok D r).1.mp (hreg.mp h₁ r hr), by cases u₂; exact h₂,
            fun d hd => (defBody_ok D d).1.mp (hdef.mp h₃ d hd), by omega, ⟨hN, hnd, ?_⟩,
            (tailSteps_ok D).mp htail⟩
          by_cases hn : D.T.nodes = []
          · simp [hn]
          · simpa using hsum hn
      · rintro ⟨_, _, hr, hac, hd, h256, ⟨hN, hnd, hsum⟩, htail⟩
        refine (ebind_ok _ _ _).mpr ⟨PUnit.unit, hreg.mpr fun r hr' => (regBody_ok D r).1.mpr (hr r hr'),
          (ebind_ok _ _ _).mpr ⟨(), hac, (ebind_ok _ _ _).mpr ⟨PUnit.unit,
            hdef.mpr fun d hd' => (defBody_ok D d).1.mpr (hd d hd'), ?_⟩⟩⟩
        rw [if_neg (by omega)]
        exact (ebind_ok _ _ _).mpr ⟨_, (hrules _).mpr ⟨hN, hnd, (fun _ _ h => by cases h),
          (fun _ => by simpa using hsum), rfl⟩, (tailSteps_ok D).mpr htail⟩

/-- `WellFormed` read declaratively. -/
theorem wellFormed_iff (D : Doc) : WellFormed D = true ↔ CheckOK D ∧ semanticCheck D = true := by
  unfold WellFormed validate
  rw [← check_iff]
  constructor
  · intro h
    split at h
    · rename_i heq
      split at heq
      · cases heq
      · rename_i hc
        split at heq
        · exact ⟨hc, by assumption⟩
        · cases heq
    · cases h
  · rintro ⟨hc, hs⟩
    rw [hc]
    simp [hs]

end VE.NormDefaults
