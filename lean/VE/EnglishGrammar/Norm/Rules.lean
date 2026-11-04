import VE.EnglishGrammar.Read
import VE.EnglishGrammar.Fixed.Norms
import VE.Norms.Wire
import VE.Grammar.Extension
import VE.SoftNorms.Wire

/-! The norm grammar, its actions and types (docs/spec/english-lean-s6.md 2.5): `grammar E L` first and unchanged,
then the norm table (`Fixed/Norms.lean`, generated from `ve/english_grammar/norms@0.json`), then one consequence row
per wording `_consequence` and `_block_grammar` generate for a regulated predicate and a sign
(`ve/norm_english.py:90-109`, :216-228). A norm action reads its arguments once: the numerals, the rule list, the
consequence and the conditions, each condition in a fresh discourse state under the consequence's bindings (R4). -/

namespace VE.EnglishGrammar.Norm
open VE.Grammar VE.EnglishGrammar

/-- R6: the regulated declarations, as the norms route decodes them (`decodeSource`, `Wire.lean:371`). R7: an
environment that names `soft-norms@0` is decoded without its soft constructs. -/
def regulatedOf (E : Env) : List VE.Norms.Regulated :=
  let soft := (VE.Route.Gate.profilesOf E.source).toOption.any (·.contains VE.SoftNorms.Wire.softProfile)
  match (if soft then VE.SoftNorms.Wire.stripSoft E.source else .ok E.source) >>=
      (VE.Norms.Wire.decodeNormsEnvironment · (acts := true)) with
  | .ok ne => ne.regulated
  | .error _ => []

/-- `_bindings` (`norm_english.py:28-44`): the scope, innermost first, and each slot's display. -/
def bindings (L : Lexicon) (sorts : List String) : Option (Scope × List String) := do
  let slots ← (List.range sorts.length).zip sorts |>.mapM fun (i, s) => do
    let noun ← L.nouns.lookup s
    match sorts.count s, (sorts.take i).count s with
    | 1, _ => pure ((s, "that " ++ noun), noun)
    | 2, 0 => pure ((s, "the first " ++ noun), "first " ++ noun)
    | 2, _ => pure ((s, "the second " ++ noun), "second " ++ noun)
    | _, _ => none
  pure ((slots.map (·.1)).reverse, slots.map (·.2))

/-- The force of a role's consequence of sign `b` (`norm_english.py:97-100`). -/
def Polarity.of : VE.Norms.Role → Bool → Polarity
  | .obligation, b => .modal (if b then .must else .needNot)
  | .permission, b => .modal (if b then .may else .mustNot)
  | .plain, b => .plain b

/-- `_consequence`'s wording of `r` with sign `b`, over the bindings `σ` and their displays `ds`. -/
def wording (L : Lexicon) (r : VE.Norms.Regulated) (σ : Scope) (ds : List String) (b : Bool) : Option String :=
  let fill (xs : List String) (w : String) := (fillHoles w fun k => xs.getD k "").2
  let every := ("Every " ++ ds.headD "") :: ds.tail.map ("each " ++ ·)
  let modal (m : String) := r.act.map fun a => fill every (replaceFirst a "{0} " ("{0} " ++ m ++ " "))
  match r.role, (if b then none else L.negatives.lookup r.name), L.wordings.lookup r.name with
  | .obligation, _, _ => modal (if b then "must" else "need not")
  | .permission, _, _ => modal (if b then "may" else "must not")
  | .plain, some w, _ => fill every w
  | .plain, none, some w => if b then fill every w else
    capitalise (", ".intercalate (("for every " ++ ds.headD "") :: ds.tail.map ("for each " ++ ·))) ++
      ", it is not the case that " ++ fill (σ.reverse.map (·.2)) w
  | .plain, none, none => none

/-- The consequence rows (spec 2.5): for each regulated predicate with arguments and each sign, each variant of
its wording that lexes as one sentence, with its clause skeleton and its bindings. -/
def consequences (E : Env) (L : Lexicon) : List (List (Sym Terminal) × Clause × Scope) :=
  (regulatedOf E).flatMap fun r => match r.sorts, bindings L r.sorts with
    | s1 :: _, some (σ, ds) => [true, false].flatMap fun b => match wording L r σ ds b with
      | none => []
      | some w =>
        let anyOf := if ds.length == 2 then [w.replace ("each " ++ ds.getD 1 "") ("any " ++ ds.getD 1 "")] else []
        let noOf := if r.role == .permission && !b then
          [replaceFirst w ("Every " ++ ds.headD "" ++ " must not ") ("No " ++ ds.headD "" ++ " may ")] else []
        (w :: anyOf ++ noOf).eraseDups.filterMap fun v => (textSyms v contentTerminal).map fun syms =>
          (syms, ⟨.every s1, .of r.role b, .strict, r.name, [], .top, [], []⟩, σ)
    | _, _ => []

/-- A norm row's symbol, with norm nonterminal `i` numbered `n + i`. -/
def NormSym.sym (n : Nat) : NormSym → Sym Terminal
  | .t a => .t a | .base m => .n m | .own i => .n (n + i)

/-- `grammar E L`'s rules first and unchanged, then the norm table's rows (`ve/english_grammar/norms@0.json`),
then the consequence rows generated from `regulatedOf E` and `L`. New nonterminals are numbered from
`(grammar E L).rank.size`; the start symbol is the norm sentence. -/
def normGrammar (E : Env) (L : Lexicon) : VE.Grammar.Grammar Terminal :=
  let n := (grammar E L).rank.size
  let k := (acts E L).size
  { rules := (grammar E L).rules ++
      normRows.mapIdx (fun i r => { lhs := n + r.lhs, rhs := r.rhs.map (·.sym n), act := k + i, tag := r.tag }) ++
      (consequences E L).toArray.mapIdx fun i (syms, c, _) =>
        { lhs := n + normConsequence, rhs := syms, act := k + normRows.size + i, tag := "consequence." ++ c.pred }
    start := n
    rank := (grammar E L).rank ++ normRanks }

/-- `(grammar E L).rank.size` (`baseSize_eq`), without building the rules: `normTy` reads it on every call. -/
def baseSize (E : Env) : Nat := (ranksFor E.profiles).size + (valueSorts E).length

/-- `ty E L` below `(grammar E L).rank.size`; the norm types above. -/
def normTy (E : Env) (L : Lexicon) : Nat → Ty :=
  fun i => if i < baseSize E then ty E L i else normTys.getD (i - baseSize E) .tok

/-- What a norm action reads from an argument: a numeral, a rule list, a consequence or a condition. -/
inductive Arg where | num (n : Nat) | refs (ns : List Nat) | cons (c : Clause) (σ : Scope) | cond (f : Sem .formula)

/-- The arguments a norm action reads, in order; a word or a mark is nothing. -/
def args : (τs : List Ty) → Args sig τs → List Arg
  | [], _ => []
  | .tok :: τs, (t, xs) => (match t with | .numeral v => [.num v.toNat] | _ => []) ++ args τs xs
  | .refs :: τs, (ns, xs) => .refs ns :: args τs xs
  | .consequence :: τs, ((c, σ), xs) => .cons c σ :: args τs xs
  | .formula :: τs, (f, xs) => .cond f :: args τs xs
  | _ :: τs, (_, xs) => args τs xs

def Arg.nums : Arg → List Nat
  | .num n => [n] | .refs ns => ns | _ => []

/-- A condition under the bindings `σ`, in a fresh discourse state (R4). -/
def Arg.read (σ : Scope) : Arg → Except Reject EFormula
  | .cond f => f { Ctx.start DState.init with scope := σ } | _ => .error .internal

/-- A norm sentence's piece and next state (spec 2.3): a header or a precedence line closes the scope, a clause
opens its consequence's, an except-when sentence reads its condition under it. -/
def NormAct.step : NormAct → List Arg → NState → Except Reject (Piece × NState)
  | .header, .num n :: xs, _ => .ok (.header ⟨n, xs.flatMap Arg.nums⟩, ⟨none⟩)
  | .precedence, [.num n, .num m], _ => .ok (.precedence n m, ⟨none⟩)
  | .clause g, .cons c σ :: xs, _ => do
    let φs ← xs.mapM (·.read σ)
    .ok (.clause (if g then { c with guard := φs.headD .top, carveOuts := φs.tail } else { c with carveOuts := φs }),
      ⟨some σ⟩)
  | .exceptWhen, [x], st => do .ok (.exceptWhen (← x.read (st.scope.getD [])), st)
  | _, _, _ => .error .internal

/-- A norm row's action over the argument types `τs`: a rule list, or a norm sentence whose mark is `false`. -/
def NormAct.action (τs : List Ty) : NormAct → Action sig
  | .refs => ⟨τs, .refs, fun xs => (args τs xs).flatMap Arg.nums⟩
  | a => ⟨τs, .norm, fun xs st => (fun (p, st2) => (p, false, st2)) <$> a.step (args τs xs) st⟩

/-- `acts E L` first and unchanged, then the norm actions. -/
def normActs (E : Env) (L : Lexicon) : Array (VE.Grammar.Action sig) :=
  let τ := normTy E L
  acts E L ++ normRows.map (fun r => r.act.action (rhsTys τ (r.rhs.map (·.sym (baseSize E))))) ++
    (consequences E L).toArray.map fun (syms, c, σ) => constant .consequence (c, σ) (rhsTys τ syms)

def prefixMap : VE.Grammar.RuleMap := ⟨id, id⟩

/-- The value of a norm sentence's tree: the start symbol's value applied to the state. -/
def normMeaning (G : VE.Grammar.Grammar Terminal) (acts : Array (VE.Grammar.Action sig)) :
    VE.Grammar.Meaning Tok NState Reject Piece :=
  fun st t => match t.sem G sig acts with
    | some ⟨.norm, f⟩ => f st
    | _ => .error .internal

/-! ## The statements of spec section 4 on the grammar -/

/-- A rule of `grammar E L` names an action of `acts E L`. -/
theorem base_act (E : Env) (L : Lexicon) {r : Nat} {R : Rule Terminal} (h : (grammar E L).rules[r]? = some R) :
    R.act < (acts E L).size := by
  simp only [grammar, fixedRules, lexRules, acts, fixedActs, lexActs, Array.getElem?_append, Array.size_append,
    Array.size_map, Array.size_mapIdx, List.size_toArray] at h ⊢
  split at h
  · simp only [Array.getElem?_mapIdx] at h
    cases hx : (fixedTable E.profiles)[r]? <;> simp [hx] at h
    subst h; simp only; omega
  · simp only [Array.getElem?_mapIdx, List.getElem?_toArray] at h
    cases hx : (lexRows E L)[r - (fixedTable E.profiles).size]? <;> simp [hx] at h
    subst h
    have := (List.getElem?_eq_some_iff.mp hx).1
    simp only; omega

theorem prefixMap_ok : ∀ (E : Env) (L : Lexicon),
  prefixMap.Ok (grammar E L) { normGrammar E L with start := (grammar E L).start } (acts E L) (normActs E L) := by
  intro E L
  refine ⟨rfl, fun _ _ _ _ h => h, fun r R h => ⟨R, ?_, rfl, ?_, ?_⟩⟩
  · have hr := (Array.getElem?_eq_some_iff.mp h).1
    simp only [normGrammar, prefixMap, id, Array.append_assoc, Array.getElem?_append_left hr, h]
  · conv => lhs; rw [← List.map_id R.rhs]
    exact List.map_congr_left fun x _ => by cases x <;> rfl
  · simp only [normActs, Array.append_assoc, Array.getElem?_append_left (base_act E L h)]

theorem baseSize_eq (E : Env) (L : Lexicon) : (grammar E L).rank.size = baseSize E := by
  simp [grammar, baseSize]

theorem start_norm : ∀ (E : Env) (L : Lexicon), normTy E L (normGrammar E L).start = .norm := by
  intro E L
  simp [normTy, normGrammar, normTys, baseSize_eq]

mutual
theorem tree_id : ∀ t : Tree Tok, prefixMap.tree t = t
  | .leaf _ => rfl
  | .node r kids => by rw [RuleMap.tree, trees_id kids]; rfl
theorem trees_id : ∀ ts : List (Tree Tok), prefixMap.trees ts = ts
  | [] => rfl
  | t :: ts => by simp only [RuleMap.trees, tree_id t, trees_id ts]
end
-- `lean/audit.py` reads the `end` of a `mutual` block as the end of the namespace (see `VE.Grammar.Extension`).
end VE.EnglishGrammar.Norm

namespace VE.EnglishGrammar.Norm
open VE.Grammar VE.EnglishGrammar

mutual
/-- `Tree.derives` reads a grammar's rules only. -/
theorem derives_start (G : Grammar Terminal) (s : Nat) :
    ∀ (X : Sym Terminal) (t : Tree Tok), t.derives { G with start := s } X = t.derives G X
  | .t _, .leaf _ => rfl
  | .n _, .leaf _ => rfl
  | .t _, .node _ _ => rfl
  | .n _, .node r kids => by
    simp only [derives_node]
    split <;> simp only [derivesAll_start G s]
theorem derivesAll_start (G : Grammar Terminal) (s : Nat) :
    ∀ (Xs : List (Sym Terminal)) (ts : List (Tree Tok)), derivesAll { G with start := s } Xs ts = derivesAll G Xs ts
  | [], [] => rfl
  | [], _ :: _ => rfl
  | _ :: _, [] => rfl
  | X :: Xs, t :: ts => by simp only [derivesAll_cons, derives_start G s X t, derivesAll_start G s Xs ts]
end
-- `lean/audit.py` reads the `end` of a `mutual` block as the end of the namespace (see `VE.Grammar.Extension`).
end VE.EnglishGrammar.Norm

namespace VE.EnglishGrammar.Norm
open VE.Grammar VE.EnglishGrammar

mutual
/-- `Tree.sem` reads a grammar's rules only. -/
theorem sem_start (G : Grammar Terminal) (s : Nat) (acts : Array (Action sig)) :
    ∀ t : Tree Tok, t.sem { G with start := s } sig acts = t.sem G sig acts
  | .leaf _ => rfl
  | .node r kids => by
    simp only [Tree.sem, semAll_start G s acts kids]
theorem semAll_start (G : Grammar Terminal) (s : Nat) (acts : Array (Action sig)) :
    ∀ ts : List (Tree Tok), semAll { G with start := s } sig acts ts = semAll G sig acts ts
  | [] => rfl
  | t :: ts => by simp only [semAll, sem_start G s acts t, semAll_start G s acts ts]
end
-- `lean/audit.py` reads the `end` of a `mutual` block as the end of the namespace (see `VE.Grammar.Extension`).
end VE.EnglishGrammar.Norm

namespace VE.EnglishGrammar.Norm
open VE.Grammar VE.EnglishGrammar

theorem condition_same : ∀ (E : Env) (L : Lexicon) (X : VE.Grammar.Sym Terminal) (t : VE.Grammar.Tree Tok),
  t.derives (grammar E L) X = true →
  t.derives (normGrammar E L) X = true ∧ t.sem (normGrammar E L) sig (normActs E L) = t.sem (grammar E L) sig (acts E L) := by
  intro E L X t h
  obtain ⟨hd, -, hs⟩ := rule_map_sem (prefixMap_ok E L) h
  rw [tree_id] at hd hs
  have hX : X.rename prefixMap.nt = X := by cases X <;> rfl
  rw [hX, derives_start] at hd
  rw [sem_start] at hs
  exact ⟨hd, hs⟩

/-! No action of `acts E L` gives a norm sentence, and no norm action marks one. -/

theorem ntTy_ne (n : Nat) : ntTy n ≠ .norm := by
  unfold ntTy; split <;> simp

theorem ty_ne (E : Env) (L : Lexicon) (n : Nat) : ty E L n ≠ .norm := by
  unfold ty; split
  · exact ntTy_ne n
  · split <;> simp

theorem fixed_ne (lhs : Ty) (h : lhs ≠ .norm) (τs : List Ty) (k : FixedAct) : (k.action lhs τs).out ≠ .norm := by
  unfold FixedAct.action
  split <;> simp only [build, constant, ofToken, numeralAct, unfit] <;> (repeat' split) <;> simp_all

theorem lex_ne (τs : List Ty) (k : LexAct) : (k.action τs).out ≠ .norm := by
  unfold LexAct.action
  split <;> simp only [build, constant, ofToken, ofSlots, unfit] <;> (repeat' split) <;> simp_all

theorem acts_ne (E : Env) (L : Lexicon) : ∀ a ∈ acts E L, a.out ≠ .norm := by
  intro a ha
  simp only [acts, fixedActs, lexActs, Array.mem_append, Array.mem_map, List.mem_toArray] at ha
  rcases ha with ⟨r, _, rfl⟩ | ⟨r, _, rfl⟩
  · exact fixed_ne _ (ntTy_ne _) _ _
  · exact lex_ne _ _

theorem action_mark (τs : List Ty) (k : NormAct) (xs : Args sig (k.action τs).args) (f : Sem .norm)
    (h : (⟨(k.action τs).out, (k.action τs).run xs⟩ : Val sig) = ⟨.norm, f⟩) :
    ∀ st p c st2, f st = .ok (p, c, st2) → c = false := by
  intro st p c st2 hf
  cases k <;> simp only [NormAct.action] at h
  all_goals cases h
  all_goals revert hf; simp only [Functor.map, Except.map]; split <;> simp_all

/-- Every action of the norm grammar that gives a norm sentence gives it the mark `false`. -/
theorem normActs_mark (E : Env) (L : Lexicon) : ∀ a ∈ normActs E L, ∀ (xs : Args sig a.args) f,
    (⟨a.out, a.run xs⟩ : Val sig) = ⟨.norm, f⟩ → ∀ st p c st2, f st = .ok (p, c, st2) → c = false := by
  intro a ha xs f h
  simp only [normActs, Array.mem_append, Array.mem_map] at ha
  rcases ha with (ha | ⟨r, _, rfl⟩) | ⟨⟨syms, cl, σ⟩, _, rfl⟩
  · exact absurd (Sigma.mk.inj h).1 (acts_ne E L a ha)
  · exact action_mark _ _ xs f h
  · have : (constant .consequence (cl, σ) (rhsTys (normTy E L) syms)).out ≠ .norm := by
      unfold constant; split <;> simp [unfit]
    exact absurd (Sigma.mk.inj h).1 this

theorem normMeaning_unmarked : ∀ (E : Env) (L : Lexicon) (st st2 : NState) (t : VE.Grammar.Tree Tok) (p : Piece)
    (c : Bool),
  normMeaning (normGrammar E L) (normActs E L) st t = .ok (p, c, st2) → c = false := by
  intro E L st st2 t p c h
  unfold normMeaning at h
  split at h
  · rename_i f hs
    cases t with
    | leaf x => simp [Tree.sem, sig] at hs
    | node r kids =>
      simp only [Tree.sem] at hs
      split at hs <;> try cases hs
      split at hs <;> try cases hs
      rename_i a ha
      split at hs <;> try cases hs
      rename_i vs _
      cases hx : toArgs sig a.args vs with
      | none => simp [hx] at hs
      | some xs =>
        simp only [hx, Option.map_some, Option.some.injEq] at hs
        exact normActs_mark E L a (Array.mem_of_getElem? ha) xs f hs st p c st2 h
  · cases h

end VE.EnglishGrammar.Norm
