import VE.Route.Wire
import VE.RoundTrip

/-! The round trip of the route's formula codec (kernel boundary 1.3 and 7, KB-4 and KB-9a).

The route encodes a formula with `encodeFormula` and decodes premises with `decodeFormulas` and one
closed formula with `decodeClosed`. This file states that decoding an encoding gives the formula
back, for every closed formula the decoders' own gates admit:

* `hCheck`: the formula is closed and typed in the environment (`Formula.check E []`, the decoders'
  own typing gate; `Formula.WellFormed E []` through `check_iff_wellFormed` in the corollaries);
* `hDepth`: its nesting depth is within `VE.Limits.maxDepth` (`VE.Surface.formulaDepth` counts an
  atom as 0, so `formulaDepth φ < maxDepth` is `decodeFormula maxDepth`'s fuel and
  `AstLimit.walk`'s 64 levels);
* `hNodes`: its formula and term nodes (`VE.Bridge.formulaNodes`, the count `AstLimit.check` and
  `nodeLimit` both make) are at most `VE.Limits.maxNodes`; for a list, all of them together;
* `hData`: on a data-stage route (`data = true`) no quantifier ranges over `$string`.

Each hypothesis is a gate of the decoder: the end of this file refuses, for each one, a formula (or a
list) that breaks it and only it (`decodeClosed_refuses_depth`, `decodeFormulas_refuses_depth` and
the `#guard`s). The encoder and the decoders are unchanged; this file holds statements only. -/
namespace VE.Route.Wire
open Lean
open VE.Route.AstLimit (walk Halt)

/-- Decoding an encoded term gives it back. -/
theorem decodeTerm_encodeTerm (t : VE.Term) : VE.Bridge.decodeTerm (encodeTerm t) = .ok t := by
  cases t <;> rfl

/-- Decoding an encoded formula with depth fuel above its depth gives it back. -/
theorem decodeFormula_encodeFormula (φ : VE.Formula) (n : Nat) (h : VE.Surface.formulaDepth φ < n) :
    VE.Bridge.decodeFormula n (encodeFormula φ) = .ok φ := by
  open VE.Bridge in
  induction φ generalizing n with
  | top | bottom => cases n with | zero => omega | succ n => rfl
  | unary p t => cases n with
    | zero => omega
    | succ n =>
      show (VE.Formula.unary p <$> decodeTerm (encodeTerm t)) = _
      rw [decodeTerm_encodeTerm]; rfl
  | binary p t u => cases n with
    | zero => omega
    | succ n =>
      show (do let x ← decodeTerm (encodeTerm t); VE.Formula.binary p x <$> decodeTerm (encodeTerm u)) = _
      rw [decodeTerm_encodeTerm, decodeTerm_encodeTerm]; rfl
  | eq t u => cases n with
    | zero => omega
    | succ n =>
      show (do let x ← decodeTerm (encodeTerm t); VE.Formula.eq x <$> decodeTerm (encodeTerm u)) = _
      rw [decodeTerm_encodeTerm, decodeTerm_encodeTerm]; rfl
  | not a ih => cases n with
    | zero => omega
    | succ n =>
      simp only [VE.Surface.formulaDepth] at h
      show (VE.Formula.not <$> decodeFormula n (encodeFormula a)) = _
      rw [ih n (by omega)]; rfl
  | all s a ih => cases n with
    | zero => omega
    | succ n =>
      simp only [VE.Surface.formulaDepth] at h
      show (VE.Formula.all s <$> decodeFormula n (encodeFormula a)) = _
      rw [ih n (by omega)]; rfl
  | ex s a ih => cases n with
    | zero => omega
    | succ n =>
      simp only [VE.Surface.formulaDepth] at h
      show (VE.Formula.ex s <$> decodeFormula n (encodeFormula a)) = _
      rw [ih n (by omega)]; rfl
  | and a b iha ihb => cases n with
    | zero => omega
    | succ n =>
      simp only [VE.Surface.formulaDepth] at h
      show (do let x ← decodeFormula n (encodeFormula a); VE.Formula.and x <$> decodeFormula n (encodeFormula b)) = _
      rw [iha n (by omega), ihb n (by omega)]; rfl
  | or a b iha ihb => cases n with
    | zero => omega
    | succ n =>
      simp only [VE.Surface.formulaDepth] at h
      show (do let x ← decodeFormula n (encodeFormula a); VE.Formula.or x <$> decodeFormula n (encodeFormula b)) = _
      rw [iha n (by omega), ihb n (by omega)]; rfl
  | implies a b iha ihb => cases n with
    | zero => omega
    | succ n =>
      simp only [VE.Surface.formulaDepth] at h
      show (do let x ← decodeFormula n (encodeFormula a); VE.Formula.implies x <$> decodeFormula n (encodeFormula b)) = _
      rw [iha n (by omega), ihb n (by omega)]; rfl

/-! ### The AST limits on an encoding

`AstLimit.walk` is unfolded one node at a time by `rfl` (each lemma below is one step of its
definition at one shape of the encoding); the limit checks are discharged by `node_step`. -/

/-- One node within the node limit and at a depth within the depth limit passes both checks. -/
theorem node_step {n d : Nat} (k : Except Halt Nat) (h1 : ¬ n + 1 > VE.Limits.maxNodes)
    (h2 : ¬ d > VE.Limits.maxDepth) :
    (do
      if n + 1 > VE.Limits.maxNodes then throw (Halt.limit AstLimit.nodeLimit)
      if d > VE.Limits.maxDepth then throw (Halt.limit AstLimit.depthLimit)
      k) = k := by
  simp only [h1, h2, if_false]; rfl

/-- One term node within the node limit passes the node check (its depth is 1). -/
theorem term_step {n : Nat} (k : Except Halt Nat) (h1 : ¬ n + 1 > VE.Limits.maxNodes) :
    (do
      if n + 1 > VE.Limits.maxNodes then throw (Halt.limit AstLimit.nodeLimit)
      k) = k := by
  simp only [h1, if_false]; rfl

theorem walk_var (i f n : Nat) :
    walk (f + 1) true 1 n (encodeTerm (.var i)) =
      (do
        if n + 1 > VE.Limits.maxNodes then throw (Halt.limit AstLimit.nodeLimit)
        if AstLimit.validIndex (toJson i) then pure (n + 1) else throw Halt.stop) := rfl

theorem walk_const (c : String) (f n : Nat) :
    walk (f + 1) true 1 n (encodeTerm (.const c)) =
      (do
        if n + 1 > VE.Limits.maxNodes then throw (Halt.limit AstLimit.nodeLimit)
        pure (n + 1)) := rfl

/-- `AstLimit.walk` counts an encoded term as one node and reports no limit (a variable index it does
not read as an index stops the walk, which is not a limit). -/
theorem walk_encodeTerm (t : VE.Term) (fuel n : Nat) (hf : 1 ≤ fuel) (hn : n + 1 ≤ VE.Limits.maxNodes) :
    walk fuel true 1 n (encodeTerm t) = .ok (n + 1) ∨
      walk fuel true 1 n (encodeTerm t) = .error .stop := by
  obtain ⟨fuel, rfl⟩ : ∃ f, fuel = f + 1 := ⟨fuel - 1, by omega⟩
  have h1 : ¬ n + 1 > VE.Limits.maxNodes := by omega
  cases t with
  | var i =>
    rw [walk_var, term_step _ h1]
    by_cases hv : AstLimit.validIndex (toJson i) = true
    · exact .inl (by rw [if_pos hv]; rfl)
    · exact .inr (by rw [if_neg hv]; rfl)
  | const c => exact .inl (by rw [walk_const, term_step _ h1]; rfl)

/-- Two walk steps that each count or stop count or stop together. -/
theorem walk_bind {r : Except Halt Nat} {k m : Nat} {f : Nat → Except Halt Nat}
    (hr : r = .ok k ∨ r = .error .stop) (hf : f k = .ok m ∨ f k = .error .stop) :
    (r >>= f) = .ok m ∨ (r >>= f) = .error .stop := by
  rcases hr with rfl | rfl
  · exact hf
  · exact .inr rfl

/-- Every encoded formula is a JSON array. -/
theorem encodeFormula_arr (φ : VE.Formula) : ∃ xs, encodeFormula φ = .arr xs := by
  cases φ <;> exact ⟨_, rfl⟩

theorem walk_leafNode {φ : VE.Formula} {f d n : Nat} (hφ : φ = .top ∨ φ = .bottom) :
    walk (f + 1) false d n (encodeFormula φ) =
      (do
        if n + 1 > VE.Limits.maxNodes then throw (Halt.limit AstLimit.nodeLimit)
        if d > VE.Limits.maxDepth then throw (Halt.limit AstLimit.depthLimit)
        pure (n + 1)) := by
  rcases hφ with rfl | rfl <;> rfl

theorem walk_unaryAtom (p : String) (t : VE.Term) (f d n : Nat) :
    walk (f + 1) false d n (encodeFormula (.unary p t)) =
      (do
        if n + 1 > VE.Limits.maxNodes then throw (Halt.limit AstLimit.nodeLimit)
        if d > VE.Limits.maxDepth then throw (Halt.limit AstLimit.depthLimit)
        walk f true 1 (n + 1) (encodeTerm t)) := rfl

theorem walk_pairAtom {φ : VE.Formula} {t u : VE.Term} {f d n : Nat}
    (hφ : (∃ p, φ = .binary p t u) ∨ φ = .eq t u) :
    walk (f + 1) false d n (encodeFormula φ) =
      (do
        if n + 1 > VE.Limits.maxNodes then throw (Halt.limit AstLimit.nodeLimit)
        if d > VE.Limits.maxDepth then throw (Halt.limit AstLimit.depthLimit)
        let n ← walk f true 1 (n + 1) (encodeTerm t)
        walk f true 1 n (encodeTerm u)) := by
  rcases hφ with ⟨p, rfl⟩ | rfl <;> rfl

/-- `AstLimit.walk` at the encoding of a one-child formula node (`not`, `forall`, `exists`). -/
theorem walk_unaryNode {φ a : VE.Formula} {xs : Array Json} {f d n : Nat}
    (hφ : φ = .not a ∨ (∃ s, φ = .all s a) ∨ (∃ s, φ = .ex s a)) (hx : encodeFormula a = .arr xs) :
    walk (f + 1) false d n (encodeFormula φ) =
      (do
        if n + 1 > VE.Limits.maxNodes then throw (Halt.limit AstLimit.nodeLimit)
        if d > VE.Limits.maxDepth then throw (Halt.limit AstLimit.depthLimit)
        walk f false (d + 1) (n + 1) (.arr xs)) := by
  rcases hφ with rfl | ⟨s, rfl⟩ | ⟨s, rfl⟩ <;> simp only [encodeFormula, hx] <;> rfl

/-- `AstLimit.walk` at the encoding of a two-child formula node (`and`, `or`, `implies`). -/
theorem walk_binaryNode {φ a b : VE.Formula} {xs ys : Array Json} {f d n : Nat}
    (hφ : φ = .and a b ∨ φ = .or a b ∨ φ = .implies a b) (hx : encodeFormula a = .arr xs)
    (hy : encodeFormula b = .arr ys) :
    walk (f + 1) false d n (encodeFormula φ) =
      (do
        if n + 1 > VE.Limits.maxNodes then throw (Halt.limit AstLimit.nodeLimit)
        if d > VE.Limits.maxDepth then throw (Halt.limit AstLimit.depthLimit)
        let n ← walk f false (d + 1) (n + 1) (.arr xs)
        walk f false (d + 1) n (.arr ys)) := by
  rcases hφ with rfl | rfl | rfl <;> simp only [encodeFormula, hx, hy] <;> rfl

/-- `AstLimit.walk` counts an encoded formula's `formulaNodes` and reports no limit when the formula
is within the depth and node limits from where the walk starts. -/
theorem walk_encodeFormula (φ : VE.Formula) (fuel d n : Nat)
    (hfuel : VE.Surface.formulaDepth φ + 2 ≤ fuel)
    (hd : d + VE.Surface.formulaDepth φ ≤ VE.Limits.maxDepth)
    (hn : n + VE.Bridge.formulaNodes φ ≤ VE.Limits.maxNodes) :
    walk fuel false d n (encodeFormula φ) = .ok (n + VE.Bridge.formulaNodes φ) ∨
      walk fuel false d n (encodeFormula φ) = .error .stop := by
  obtain ⟨fuel, rfl⟩ : ∃ f, fuel = f + 1 := ⟨fuel - 1, by omega⟩
  induction φ generalizing fuel d n with
  | top | bottom =>
    simp only [VE.Bridge.formulaNodes, VE.Surface.formulaDepth] at hn hd ⊢
    have h1 : ¬ n + 1 > VE.Limits.maxNodes := by omega
    have h2 : ¬ d > VE.Limits.maxDepth := by omega
    rw [walk_leafNode (by simp), node_step _ h1 h2]
    exact .inl rfl
  | unary p t =>
    simp only [VE.Bridge.formulaNodes, VE.Bridge.termNodes, VE.Surface.formulaDepth] at hn hd hfuel ⊢
    have h1 : ¬ n + 1 > VE.Limits.maxNodes := by omega
    have h2 : ¬ d > VE.Limits.maxDepth := by omega
    rw [walk_unaryAtom, node_step _ h1 h2]
    exact walk_encodeTerm t fuel (n + 1) (by omega) (by omega)
  | binary _ t u | eq t u =>
    simp only [VE.Bridge.formulaNodes, VE.Bridge.termNodes, VE.Surface.formulaDepth] at hn hd hfuel ⊢
    have h1 : ¬ n + 1 > VE.Limits.maxNodes := by omega
    have h2 : ¬ d > VE.Limits.maxDepth := by omega
    rw [walk_pairAtom (t := t) (u := u) (by simp), node_step _ h1 h2]
    refine walk_bind (walk_encodeTerm t fuel (n + 1) (by omega) (by omega)) ?_
    exact walk_encodeTerm u fuel (n + 1 + 1) (by omega) (by omega)
  | not a ih | all _ a ih | ex _ a ih =>
    simp only [VE.Bridge.formulaNodes, VE.Surface.formulaDepth] at hn hd hfuel ⊢
    have h1 : ¬ n + 1 > VE.Limits.maxNodes := by omega
    have h2 : ¬ d > VE.Limits.maxDepth := by omega
    obtain ⟨xs, hx⟩ := encodeFormula_arr a
    rw [walk_unaryNode (by simp) hx, node_step _ h1 h2, ← hx]
    obtain ⟨f, rfl⟩ : ∃ f, fuel = f + 1 := ⟨fuel - 1, by omega⟩
    rcases ih (d := d + 1) (n := n + 1) (fuel := f) (by omega) (by omega) (by omega) with h | h <;> rw [h]
    · exact .inl (by congr 1; omega)
    · exact .inr rfl
  | and a b iha ihb | or a b iha ihb | implies a b iha ihb =>
    simp only [VE.Bridge.formulaNodes, VE.Surface.formulaDepth] at hn hd hfuel ⊢
    have h1 : ¬ n + 1 > VE.Limits.maxNodes := by omega
    have h2 : ¬ d > VE.Limits.maxDepth := by omega
    obtain ⟨xs, hx⟩ := encodeFormula_arr a
    obtain ⟨ys, hy⟩ := encodeFormula_arr b
    rw [walk_binaryNode (by simp) hx hy, node_step _ h1 h2, ← hx, ← hy]
    obtain ⟨f, rfl⟩ : ∃ f, fuel = f + 1 := ⟨fuel - 1, by omega⟩
    refine walk_bind (iha (d := d + 1) (n := n + 1) (fuel := f) (by omega) (by omega) (by omega)) ?_
    have e : n + (1 + VE.Bridge.formulaNodes a + VE.Bridge.formulaNodes b) =
      n + 1 + VE.Bridge.formulaNodes a + VE.Bridge.formulaNodes b := by omega
    rw [e]
    exact ihb (d := d + 1) (n := n + 1 + VE.Bridge.formulaNodes a) (fuel := f) (by omega) (by omega) (by omega)

/-- A successful step of an `Except` computation passes its value on. -/
theorem ok_bind {ε α β : Type} (a : α) (f : α → Except ε β) : (Except.ok a >>= f) = f a := rfl

/-- The decoder's node sum. -/
theorem foldl_add (l : List Nat) (k : Nat) : l.foldl (· + ·) k = k + l.sum := by
  induction l generalizing k with
  | nil => simp
  | cons x xs ih => simp [List.foldl_cons, ih]; omega

/-- `AstLimit.walk` over a case's encoded formulas, counted together, reports no limit. -/
theorem foldlM_walk_encode (fs : List VE.Formula) (n : Nat)
    (hDepth : ∀ φ ∈ fs, VE.Surface.formulaDepth φ < VE.Limits.maxDepth)
    (hNodes : n + (fs.map VE.Bridge.formulaNodes).sum ≤ VE.Limits.maxNodes) :
    (fs.map encodeFormula).foldlM (walk 256 false 1) n = .ok (n + (fs.map VE.Bridge.formulaNodes).sum) ∨
      (fs.map encodeFormula).foldlM (walk 256 false 1) n = .error .stop := by
  induction fs generalizing n with
  | nil => exact .inl rfl
  | cons φ fs ih =>
    simp only [List.map_cons, List.foldlM_cons, List.sum_cons] at hNodes ⊢
    have hφ := hDepth φ (by simp)
    refine walk_bind (walk_encodeFormula φ 256 1 n (by have : VE.Limits.maxDepth = 64 := rfl; omega) (by omega) (by omega)) ?_
    have e : n + (VE.Bridge.formulaNodes φ + (fs.map VE.Bridge.formulaNodes).sum) =
      n + VE.Bridge.formulaNodes φ + (fs.map VE.Bridge.formulaNodes).sum := by omega
    rw [e]
    exact ih _ (fun ψ hψ => hDepth ψ (by simp [hψ])) (by omega)

/-- The AST limits pass on a case's encoded formulas within the depth and node limits. -/
theorem astLimit_check_encode (fs : List VE.Formula)
    (hDepth : ∀ φ ∈ fs, VE.Surface.formulaDepth φ < VE.Limits.maxDepth)
    (hNodes : (fs.map VE.Bridge.formulaNodes).foldl (· + ·) 0 ≤ VE.Limits.maxNodes) :
    AstLimit.check (fs.map encodeFormula) = .ok () := by
  rw [foldl_add] at hNodes
  unfold AstLimit.check
  rcases foldlM_walk_encode fs 0 hDepth hNodes with h | h <;> rw [h]

/-- Depth-fuelled decoding of a list of encodings gives the list back. -/
theorem mapM_decodeFormula_encode (fs : List VE.Formula)
    (hDepth : ∀ φ ∈ fs, VE.Surface.formulaDepth φ < VE.Limits.maxDepth) :
    (fs.map encodeFormula).mapM (VE.Bridge.decodeFormula VE.Limits.maxDepth) = .ok fs := by
  induction fs with
  | nil => rfl
  | cons φ fs ih =>
    simp only [List.map_cons, List.mapM_cons,
      decodeFormula_encodeFormula φ _ (hDepth φ (by simp)), ih (fun ψ hψ => hDepth ψ (by simp [hψ]))]
    rfl

/-- (1) One closed formula: `decodeClosed` reads `encodeFormula φ` as `φ` for every formula its own
gates admit (the AST limits, the depth fuel, the data flag and `Formula.check E []`). -/
theorem decodeClosed_encodeFormula (E : VE.Environment) (φ : VE.Formula) (data : Bool)
    (hCheck : φ.check E [] = true)
    (hDepth : VE.Surface.formulaDepth φ < VE.Limits.maxDepth)
    (hNodes : VE.Bridge.formulaNodes φ ≤ VE.Limits.maxNodes)
    (hData : data = true → usesStringBinder φ = false) :
    decodeClosed E (encodeFormula φ) data = .ok φ := by
  have hA : AstLimit.check [encodeFormula φ] = .ok () :=
    astLimit_check_encode [φ] (by simpa using hDepth) (by simpa using hNodes)
  have hD : (data && usesStringBinder φ) = false := by cases data <;> simp_all
  simp only [decodeClosed, hA, decodeFormula_encodeFormula φ _ hDepth, ok_bind, hD, hCheck]
  rfl

/-- (1) with the typing predicate: `Formula.WellFormed E []` for the executable check. -/
theorem decodeClosed_encodeFormula_wellFormed (E : VE.Environment) (φ : VE.Formula) (data : Bool)
    (hWellFormed : φ.WellFormed E [])
    (hDepth : VE.Surface.formulaDepth φ < VE.Limits.maxDepth)
    (hNodes : VE.Bridge.formulaNodes φ ≤ VE.Limits.maxNodes)
    (hData : data = true → usesStringBinder φ = false) :
    decodeClosed E (encodeFormula φ) data = .ok φ :=
  decodeClosed_encodeFormula E φ data ((VE.check_iff_wellFormed E [] φ).mpr hWellFormed) hDepth hNodes hData

/-- (2) The list form: `decodeFormulas` reads the array of encodings of `fs` as `fs`, in order, when
every member passes the per-formula gates and all of them together are within the node limit (the
list-level limit both `AstLimit.check` and `nodeLimit` apply). -/
theorem decodeFormulas_encode (E : VE.Environment) (fs : List VE.Formula) (data : Bool)
    (hCheck : ∀ φ ∈ fs, φ.check E [] = true)
    (hDepth : ∀ φ ∈ fs, VE.Surface.formulaDepth φ < VE.Limits.maxDepth)
    (hNodes : (fs.map VE.Bridge.formulaNodes).foldl (· + ·) 0 ≤ VE.Limits.maxNodes)
    (hData : data = true → ∀ φ ∈ fs, usesStringBinder φ = false) :
    decodeFormulas E (Json.arr (fs.map encodeFormula).toArray) data = .ok fs := by
  have hA := astLimit_check_encode fs hDepth hNodes
  have hL : nodeLimit (fs.map VE.Bridge.formulaNodes) = .ok () := by
    unfold nodeLimit; simp only [Nat.not_lt.mpr hNodes, if_false]
  have hD : (data && fs.any usesStringBinder) = false := by
    cases data
    · rfl
    · simpa using hData rfl
  have hC : fs.all (fun a => a.check E []) = true := List.all_eq_true.mpr hCheck
  simp only [decodeFormulas, formulasJson, Json.getArr?, pure_bind, Option.toList,
    List.append_nil, hA, ok_bind, mapM_decodeFormula_encode fs hDepth, hL, hD, hC]
  rfl

/-- (2) with the typing predicate: `Formula.WellFormed E []` for every member. -/
theorem decodeFormulas_encode_wellFormed (E : VE.Environment) (fs : List VE.Formula) (data : Bool)
    (hWellFormed : ∀ φ ∈ fs, φ.WellFormed E [])
    (hDepth : ∀ φ ∈ fs, VE.Surface.formulaDepth φ < VE.Limits.maxDepth)
    (hNodes : (fs.map VE.Bridge.formulaNodes).foldl (· + ·) 0 ≤ VE.Limits.maxNodes)
    (hData : data = true → ∀ φ ∈ fs, usesStringBinder φ = false) :
    decodeFormulas E (Json.arr (fs.map encodeFormula).toArray) data = .ok fs :=
  decodeFormulas_encode E fs data
    (fun φ hφ => (VE.check_iff_wellFormed E [] φ).mpr (hWellFormed φ hφ)) hDepth hNodes hData

/-! ### The depth hypothesis is the decoder's bound, not a weaker one

`hDepth` cannot be relaxed by one level: the encoding of the chain of `maxDepth` negations over `⊤`
(its `formulaDepth` is `maxDepth`, 65 formula levels) is refused with the depth diagnostic, alone and
as a premise list. The route checks depth twice (`AstLimit.walk` and `decodeFormula`'s fuel) with the
same diagnostic, so these two statements fail only when both checks admit one more level. -/

/-- The negation chain one level past `hDepth`: its depth is exactly `maxDepth`. -/
theorem depth_negationChain : VE.Surface.formulaDepth (Nat.repeat .not VE.Limits.maxDepth .top) = VE.Limits.maxDepth :=
  rfl

/-- `decodeClosed` refuses the encoding of a formula of depth `maxDepth` (a closed formula, typed in
every environment) with the depth limit. -/
theorem decodeClosed_refuses_depth (E : VE.Environment) (data : Bool) :
    decodeClosed E (encodeFormula (Nat.repeat .not VE.Limits.maxDepth .top)) data =
      .error AstLimit.depthLimit :=
  rfl

/-- `decodeFormulas` refuses a premise list holding that encoding with the depth limit. -/
theorem decodeFormulas_refuses_depth (E : VE.Environment) (data : Bool) :
    decodeFormulas E (Json.arr #[encodeFormula (Nat.repeat .not VE.Limits.maxDepth .top)]) data =
      .error AstLimit.depthLimit :=
  rfl

/-! ### The other hypotheses are the decoder's gates too

Each `#guard` below is a formula (or list) that breaks exactly one hypothesis of
`decodeClosed_encodeFormula` or `decodeFormulas_encode` and is refused with that gate's diagnostic. -/

-- hNodes: a balanced conjunction of 16,383 nodes (depth 13) is refused by the node limit.
#guard (match decodeClosed ⟨[], fun _ => none, fun _ => none⟩
    (encodeFormula (Nat.repeat (fun a => .and a a) 13 .top)) false with
  | .error e => e == AstLimit.nodeLimit
  | .ok _ => false)
-- hNodes for a list: two formulas of 8,191 nodes, each within the limit, are refused together.
#guard VE.Bridge.formulaNodes (Nat.repeat (fun a => VE.Formula.and a a) 12 .top) ≤ VE.Limits.maxNodes
#guard (match decodeFormulas ⟨[], fun _ => none, fun _ => none⟩
    (Json.arr #[encodeFormula (Nat.repeat (fun a => .and a a) 12 .top),
      encodeFormula (Nat.repeat (fun a => .and a a) 12 .top)]) false with
  | .error e => e == AstLimit.nodeLimit
  | .ok _ => false)
-- hCheck: an unbound variable is refused by the typing gate.
#guard (match decodeClosed ⟨[], fun _ => none, fun _ => none⟩ (encodeFormula (.eq (.var 0) (.var 0))) false with
  | .error e => e == "ill-typed or unbound conclusion"
  | .ok _ => false)
-- hData: a `$string` binder, typed in an environment that declares the sort, is refused on a data
-- route and read back on any other.
#guard (match decodeClosed ⟨[Background.stringSort], fun _ => none, fun _ => none⟩
    (encodeFormula (.all Background.stringSort .top)) true with
  | .error e => e == "UnsupportedProfile: $string quantification requires data stage 2"
  | .ok _ => false)
#guard (match decodeClosed ⟨[Background.stringSort], fun _ => none, fun _ => none⟩
    (encodeFormula (.all Background.stringSort .top)) false with
  | .ok φ => φ == .all Background.stringSort .top
  | .error _ => false)

end VE.Route.Wire
