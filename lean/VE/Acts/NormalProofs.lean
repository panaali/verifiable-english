import VE.Acts.Readings
import VE.Grammar.TableInvariant

/-! `read_normal` (docs/spec/act-phrases.md 5.6): the normal form of a `normalOk` atom reads back as its canonical
atom.

Proofs only. (1) `normal_derived`: a derivation of `a.normal` whose meaning is `.one a.canon`, built rule by rule
from 5.2's table. (2) `normal_bounds`: a raw cap and a step budget from which the parse of `a.normal` is complete and
unsaturated, for every larger cap and budget.
-/

namespace VE.Acts.NormalProofs
open VE.Acts
open VE.Grammar (Tree Sym derivesAll yieldAll)
open VE.Acts.Lexical (Tok)

/-! ### Derivations over the rule table, with their pieces -/

/-- The number `build` gives the nonterminal `X`. -/
def nm (V : Vocab) (X : NT) : Nat := (firsts ((closed (schema V)).map (·.lhs))).idxOf X
/-- The symbol `build` makes of a right-side symbol. -/
def symB (V : Vocab) : RSym → Sym Term
  | .n x => .n (nm V x)
  | .t a => .t a

/-- The symbol `Y` derives `w` with pieces `ps`. -/
def Gen (V : Vocab) (Y : RSym) (w : List Tok) (ps : List Piece) : Prop :=
  ∃ t : Tree Tok, t.derives (grammar V) (symB V Y) = true ∧ t.yield = w ∧
    piecesOf (closed (schema V)).toArray t = some ps
/-- The symbols `Ys` derive `w` with pieces `ps`, in order. -/
def GenAll (V : Vocab) (Ys : List RSym) (w : List Tok) (ps : List Piece) : Prop :=
  ∃ ts : List (Tree Tok), derivesAll (grammar V) (Ys.map (symB V)) ts = true ∧ yieldAll ts = w ∧
    (ts.mapM (piecesOf (closed (schema V)).toArray)).map List.flatten = some ps

variable {V : Vocab}

theorem grammar_rule {i : Nat} {r : RuleS} (h : (closed (schema V))[i]? = some r) :
    (grammar V).rules[i]? = some ⟨nm V r.lhs, r.rhs.map (symB V), 0, ""⟩ := by
  simp only [grammar, build, List.getElem?_toArray, List.getElem?_map, h, Option.map_some]
  congr 3

theorem piecesOf_node (rs : Array RuleS) (i : Nat) (kids : List (Tree Tok)) :
    piecesOf rs (.node i kids) = (rs[i]?).bind (fun r =>
      (kids.mapM (piecesOf rs)).bind (fun l => applyRule r l.flatten)) := by
  rw [piecesOf]
  simp only [bind, Option.bind]
  rw [List.mapM_subtype (g := piecesOf rs) (fun _ _ => rfl), List.unattach_attach]

theorem genAll_nil : GenAll V [] [] [] := ⟨[], rfl, rfl, rfl⟩

theorem genAll_cons {Y : RSym} {Ys : List RSym} {w1 w2 : List Tok} {p1 p2 : List Piece}
    (h1 : Gen V Y w1 p1) (h2 : GenAll V Ys w2 p2) : GenAll V (Y :: Ys) (w1 ++ w2) (p1 ++ p2) := by
  obtain ⟨t, ht, hy, hp⟩ := h1
  obtain ⟨ts, hts, hys, hps⟩ := h2
  refine ⟨t :: ts, ?_, ?_, ?_⟩
  · simp [VE.Grammar.derivesAll_cons, ht, hts]
  · simp [VE.Grammar.yieldAll_cons, hy, hys]
  · simp only [List.mapM_cons, hp]
    cases hm : ts.mapM (piecesOf (closed (schema V)).toArray) with
    | none => simp [hm] at hps
    | some l => simp_all

theorem mem_closed {r : RuleS} (h : r ∈ schema V) : ∃ i : Nat, (closed (schema V))[i]? = some r := by
  obtain ⟨i, hi, he⟩ := List.getElem_of_mem h
  exact ⟨i, by simp only [closed]; rw [List.getElem?_append_left hi, List.getElem?_eq_getElem hi, he]⟩

theorem gen_node {r : RuleS} (hr : r ∈ schema V) {w : List Tok} {cs ps : List Piece}
    (hk : GenAll V r.rhs w cs) (ha : applyRule r cs = some ps) : Gen V (.n r.lhs) w ps := by
  obtain ⟨i, hi⟩ := mem_closed hr
  obtain ⟨ts, hts, hys, hps⟩ := hk
  refine ⟨.node i ts, ?_, ?_, ?_⟩
  · show (Tree.node i ts).derives (grammar V) (.n (nm V r.lhs)) = true
    rw [VE.Grammar.derives_node, grammar_rule hi]; simp [hts]
  · rw [VE.Grammar.yield_node, hys]
  · rw [piecesOf_node]
    cases hm : ts.mapM (piecesOf (closed (schema V)).toArray) with
    | none => simp [hm] at hps
    | some l =>
      simp only [hm, Option.map_some, Option.some.injEq] at hps
      simp [List.getElem?_toArray, hi, hps, ha]

theorem gen_leaf {a : Term} {x : Tok} {ps : List Piece} (ha : a.accepts x = true)
    (hp : piecesOf (closed (schema V)).toArray (.leaf x) = some ps) : Gen V (.t a) [x] ps :=
  ⟨.leaf x, by simpa [symB, VE.Grammar.derives_leaf] using ha, rfl, hp⟩

theorem gen1 {X : NT} {Y : RSym} {k : Kind} (hr : ⟨X, [Y], k⟩ ∈ schema V) {w : List Tok} {cs ps : List Piece}
    (h1 : Gen V Y w cs) (ha : applyRule ⟨X, [Y], k⟩ cs = some ps) : Gen V (.n X) w ps :=
  gen_node hr (by simpa using genAll_cons h1 genAll_nil) ha

theorem gen2 {X : NT} {Y1 Y2 : RSym} {k : Kind} (hr : ⟨X, [Y1, Y2], k⟩ ∈ schema V) {w1 w2 : List Tok}
    {c1 c2 ps : List Piece} (h1 : Gen V Y1 w1 c1) (h2 : Gen V Y2 w2 c2) (ha : applyRule ⟨X, [Y1, Y2], k⟩ (c1 ++ c2) = some ps) :
    Gen V (.n X) (w1 ++ w2) ps :=
  gen_node hr (by simpa using genAll_cons h1 (genAll_cons h2 genAll_nil)) ha

theorem gen3 {X : NT} {Y1 Y2 Y3 : RSym} {k : Kind} (hr : ⟨X, [Y1, Y2, Y3], k⟩ ∈ schema V) {w1 w2 w3 : List Tok}
    {c1 c2 c3 ps : List Piece} (h1 : Gen V Y1 w1 c1) (h2 : Gen V Y2 w2 c2) (h3 : Gen V Y3 w3 c3)
    (ha : applyRule ⟨X, [Y1, Y2, Y3], k⟩ (c1 ++ c2 ++ c3) = some ps) : Gen V (.n X) (w1 ++ w2 ++ w3) ps :=
  gen_node hr (by simpa using genAll_cons h1 (genAll_cons h2 (genAll_cons h3 genAll_nil))) ha

/-! ### Lower case: a word whose letters are lower case is its own `toLower` -/
theorem utf8SetAux_get (f : Char → Char) : ∀ (cs : List Char) (i p : String.Pos), (∀ c ∈ cs, f c = c) →
    String.utf8SetAux (f (String.utf8GetAux cs i p)) cs i p = cs
  | [], _, _, _ => rfl
  | c :: cs, i, p, hf => by
    simp only [String.utf8SetAux, String.utf8GetAux]
    split
    · rw [hf c (by simp)]
    · rw [utf8SetAux_get f cs _ p (fun d hd => hf d (by simp [hd]))]

theorem mapAux_id (f : Char → Char) (s : String) (hf : ∀ c ∈ s.data, f c = c) :
    ∀ n (i : String.Pos), s.endPos.1 - i.1 = n → String.mapAux f i s = s := by
  have hs : ∀ i, s.set i (f (s.get i)) = s := by
    intro i; cases s with
    | mk cs => simp only [String.set, String.get]; rw [utf8SetAux_get f cs 0 i hf]
  intro n
  induction n using Nat.strongRecOn with
  | _ n ih =>
    intro i hn
    rw [String.mapAux]
    split
    · rfl
    · rename_i h
      have hl := String.mapAux_lemma s i (f (s.get i)) h
      simp only [hs] at hl ⊢
      exact ih _ (by omega) _ rfl

theorem toLower_of (s : String) (h : ∀ c ∈ s.data, c.toLower = c) : s.toLower = s :=
  mapAux_id _ s h _ 0 rfl

theorem lower_and : "and".toLower = "and" := toLower_of _ (by decide)
theorem lower_or : "or".toLower = "or" := toLower_of _ (by decide)
theorem lower_nor : "nor".toLower = "nor" := toLower_of _ (by decide)
theorem lower_to : "to".toLower = "to" := toLower_of _ (by decide)
theorem lower_be : "be".toLower = "be" := toLower_of _ (by decide)

/-! ### What `framesOk` gives: lower-case heads, marker words and adverbs -/
theorem wordOk_lower {w : String} (h : wordOk w = true) : w.toLower = w := by
  simp only [wordOk, Bool.and_eq_true, beq_iff_eq] at h; exact h.2.symm

theorem framesOk_lower {V : Vocab} (h : framesOk V = true) :
    (∀ f ∈ V.frames, ∀ w ∈ f.head, w.toLower = w) ∧
    (∀ f ∈ V.frames, ∀ m ∈ f.markers ++ f.mods, m ≠ "" → ∀ w ∈ wordsOf m, w.toLower = w) ∧
    (∀ w ∈ V.adverbs, w.toLower = w) := by
  have h' : checkVocab V = .ok () := by
    unfold framesOk at h; cases hc : checkVocab V <;> simp_all [Except.isOk, Except.toBool]
  unfold checkVocab at h'
  simp only [bind, Except.bind, pure, Except.pure] at h'
  split at h'; · cases h'
  split at h'; · cases h'
  split at h'; · cases h'
  next h3 =>
  iterate 8 (split at h'; · cases h')
  split at h'; · cases h'
  split at h'; · cases h'
  next h13 =>
  iterate 3 (split at h'; · cases h')
  split at h'; · cases h'
  next h17 =>
  refine ⟨fun f hf w hw => ?_, fun f hf m hm hne w hw => ?_, fun w hw => ?_⟩
  · have := Lexical.forIn_ok h3 (by intro x; split <;> simp) f hf
    split at this
    · cases this
    next hn =>
    cases hx : f.head.find? (!wordOk ·) with
    | some u => exact (hn u hx).elim
    | none => exact wordOk_lower (by simpa using List.find?_eq_none.mp hx w hw)
  · have := Lexical.forIn_ok h13 (by intro x; split <;> simp) f hf
    split at this
    · cases this
    next hn =>
    cases hx : (((f.markers ++ f.mods).filter (· ≠ "")).flatMap wordsOf).find? (!wordOk ·) with
    | some u => exact (hn u hx).elim
    | none =>
      have := List.find?_eq_none.mp hx w
        (List.mem_flatMap.mpr ⟨m, List.mem_filter.mpr ⟨hm, by simpa using hne⟩, hw⟩)
      exact wordOk_lower (by simpa using this)
  · cases hx : List.find? (fun a => (!wordOk a) || List.contains (["and", "or", "nor", "to", "be"] ++
        Lexical.clauseWords) a) V.adverbs with
    | some u => exact (h17 u hx).elim
    | none =>
      have := List.find?_eq_none.mp hx w hw
      simp only [Bool.or_eq_true, Bool.not_eq_true', not_or, Bool.not_eq_true] at this
      exact wordOk_lower (by simpa using this.1)

/-! ### Rules of the table -/

variable {f : Frame} {h : Nat}

/-- A rule of `frameRules` or `globalRules`, by unfolding the table (then `simp` with the facts it needs). -/
macro "frame_unfold" : tactic => `(tactic| simp only [frameRules, many1, tail, List.mem_append, List.mem_cons,
  List.mem_map, List.mem_flatMap])
macro "global_unfold" : tactic => `(tactic| simp only [globalRules, items, many1, tail, List.mem_append, List.mem_cons,
  List.mem_map, List.mem_flatMap])
/-- `applyRule` on a rule and pieces of known shape, by its cases. -/
macro "ap_tac" : tactic => `(tactic| (unfold applyRule <;> split <;> simp_all [attachOf]))

theorem mem_frame (hf : (f, h) ∈ V.frames.zipIdx) {r : RuleS} (hr : r ∈ frameRules V h f) : r ∈ schema V := by
  simp only [schema, List.mem_append, List.mem_flatMap]; exact .inr ⟨(f, h), hf, hr⟩

theorem mem_global {r : RuleS} (hr : r ∈ globalRules V) : r ∈ schema V := by
  simp only [schema, List.mem_append]; exact .inl hr

theorem pieces_word (v : String) : piecesOf (closed (schema V)).toArray (.leaf (.word v)) = some [.w v] := by
  simp [piecesOf]

theorem gen_word {a : Term} {v : String} (ha : a.accepts (.word v) = true) : Gen V (.t a) [.word v] [.w v] :=
  gen_leaf ha (pieces_word v)

/-! ### `applyRule` on the rules a normal form uses -/

section Ap
variable (h : Nat) (m : String) (cs : List Piece) (p : Part) (j : Join) (ps : List Part)
local notation "𝔽" y => RSym.n (NT.F h y)

theorem ap_WR1 (ex : List String) (v : String) : applyRule ⟨.F h .WR, [.t (.fill ex)], .shape⟩ [.w v] = some [.w v] := by
  ap_tac
theorem ap_WR2 (ex : List String) : applyRule ⟨.F h .WR, [.t (.fill ex), 𝔽 .WR], .shape⟩ cs = some cs := by ap_tac
theorem ap_MK (w : String) (ws : List String) : applyRule ⟨.MK m, kwSyms (w :: ws), .shape⟩ cs = some [] := by
  simp only [kwSyms, List.map_cons]; ap_tac
theorem ap_PT1 : applyRule ⟨.F h .PT, [.n .J, 𝔽 .FL], .shape⟩ cs = some cs := by ap_tac
theorem ap_PT2 : applyRule ⟨.F h .PT, [.t .comma, 𝔽 .FL, 𝔽 .PT], .shape⟩ cs = some cs := by ap_tac
theorem mapM_some {α : Type} : ∀ l : List α, l.mapM (fun a => some a) = some l
  | [] => rfl
  | a :: l => by simp only [List.mapM_cons, mapM_some l]; rfl
theorem mapM_part : ∀ ps : List Part,
    (ps.map Piece.part).mapM (fun | .part p | .elt (.arg _ (.one p)) _ => some p | _ => none) = some ps
  | [] => rfl
  | q :: qs => by simp only [List.map_cons, List.mapM_cons, mapM_part qs]; rfl
theorem ap_PL (hl : listOf (.part p :: cs) = some (j, ps.map .part)) (hle : longEnd ps = false) :
    applyRule ⟨.F h .PL, [𝔽 .FL, 𝔽 .PT], .shape⟩ (.part p :: cs) = some [.list j ps] := by
  unfold applyRule
  split <;> simp_all [Function.comp_def, mapM_some]
theorem ap_OL : applyRule ⟨.F h (.OL m), [.n (.MK m), 𝔽 .PL], .shape⟩ [.list j ps] = some [.list j ps] := by ap_tac
theorem ap_LST : applyRule ⟨.F h (.LST m false), [𝔽 (.OL m)], .shape⟩ [.list j ps] =
    some [.elt (.arg m (.joined j ps)) .own] := by ap_tac
theorem ap_AR : applyRule ⟨.F h (.AR m), [.n (.MK m), 𝔽 .FL], .shape⟩ [.part p] =
    some [.elt (.arg m (.one p)) .own] := by ap_tac
theorem ap_EEmod : applyRule ⟨.F h .EE, [.n (.MK m), 𝔽 .FL], .shape⟩ [.part p] =
    some [.elt (.mod (.prep m p)) .own] := by ap_tac
theorem ap_EE1 (y : FNT) : applyRule ⟨.F h .EE, [𝔽 y], .shape⟩ cs = some cs := by ap_tac
theorem ap_ER1 : applyRule ⟨.F h .ER, [𝔽 .EE], .shape⟩ cs = some cs := by ap_tac
theorem ap_ER2 : applyRule ⟨.F h .ER, [𝔽 .EE, 𝔽 .ER], .shape⟩ cs = some cs := by ap_tac
theorem ap_O1 : applyRule ⟨.F h .O, [𝔽 .FL], .shape⟩ [.part p] = some [.elt (.arg "" (.one p)) .own] := by ap_tac
theorem ap_O2 : applyRule ⟨.F h .O, [𝔽 .PL], .shape⟩ [.list j ps] = some [.elt (.arg "" (.joined j ps)) .own] := by
  ap_tac
theorem ap_OWNM1 : applyRule ⟨.F h .OWNM, [𝔽 .O], .shape⟩ cs = some cs := by ap_tac
theorem ap_OWNM2 : applyRule ⟨.F h .OWNM, [𝔽 .O, 𝔽 .ER], .shape⟩ cs = some cs := by ap_tac
theorem ap_SM (y : FNT) : applyRule ⟨.F h .SM, [𝔽 y], .shape⟩ cs = some cs := by ap_tac
theorem ap_SC1 : applyRule ⟨.SC, [𝔽 .HD], .shape⟩ cs = some cs := by ap_tac
theorem ap_SC2 : applyRule ⟨.SC, [𝔽 .HD, 𝔽 .SM], .shape⟩ cs = some cs := by ap_tac
theorem ap_ADVO (ws : List String) (v : String) :
    applyRule ⟨.ADVO, [.t (.adv ws)], .shape⟩ [.w v] = some [.elt (.mod (.adv v.toLower)) .own] := by ap_tac
theorem ap_ADVSO1 : applyRule ⟨.ADVSO, [.n .ADVO], .shape⟩ cs = some cs := by ap_tac
theorem ap_ADVSO2 : applyRule ⟨.ADVSO, [.n .ADVO, .n .ADVSO], .shape⟩ cs = some cs := by ap_tac
theorem ap_S : applyRule ⟨.S, [.t .subj, .n .SINGLE], .shape⟩ cs = some cs := by ap_tac
theorem ap_SINGLE (rhs : List NT) (hr : rhs = [.SC] ∨ rhs = [.ADVSO, .SC] ∨ rhs = [.FW, .SC] ∨
    rhs = [.FW, .ADVSO, .SC]) : applyRule ⟨.SINGLE, rhs.map .n, .shape⟩ cs =
    (itemOf cs).map (fun (fw, h, es) => [.act (singleAct fw h es)]) := by
  rcases hr with rfl | rfl | rfl | rfl <;> ap_tac

end Ap

/-- A run of filler words. -/
theorem gen_WR (hf : (f, h) ∈ V.frames.zipIdx) : ∀ ws : List String, ws ≠ [] →
    (∀ w ∈ ws, (fillExcl V f).contains w.toLower = false) →
    Gen V (.n (.F h .WR)) (ws.map .word) (ws.map .w)
  | [], hne, _ => absurd rfl hne
  | [v], _, hw => by
    have hr : (⟨.F h .WR, [.t (.fill (fillExcl V f))], .shape⟩ : RuleS) ∈ schema V := mem_frame hf (by frame_unfold; simp)
    refine gen1 hr (gen_word ?_) (ap_WR1 h _ v)
    simpa [Term.accepts] using hw v (by simp)
  | v :: u :: ws, _, hw => by
    have h1 : Gen V (.t (.fill (fillExcl V f))) [.word v] [.w v] :=
      gen_word (by simpa [Term.accepts] using hw v (by simp))
    have h2 := gen_WR hf (u :: ws) (by simp) (fun x hx => hw x (by simp [hx]))
    have hr : (⟨.F h .WR, [.t (.fill (fillExcl V f)), .n (.F h .WR)], .shape⟩ : RuleS) ∈ schema V :=
      mem_frame hf (by frame_unfold; simp)
    have := gen2 hr h1 h2 (ap_WR2 h _ _)
    simpa using this

/-- A part `normalOk` admits under frame `f`: a non-empty run of its filler words, a slot other than `{0}`, or a
fixed phrase. -/
def PartOk (V : Vocab) (f : Frame) : Part → Prop
  | .words ws => ws ≠ [] ∧ ∀ w ∈ ws, (fillExcl V f).contains w.toLower = false
  | .slot i => i ≠ 0
  | .fixed _ => True

theorem filterMap_w (ws : List String) : (ws.map Piece.w).filterMap (fun | Piece.w s => some s | _ => none) = ws := by
  induction ws with
  | nil => rfl
  | cons x xs ih => simp only [List.map_cons, List.filterMap_cons, ih]

theorem ap_TOK (a : Term) (ha : a = .slot ∨ a = .fixed) (p : Part) :
    applyRule ⟨.TOK, [.t a], .shape⟩ [.part p] = some [.part p] := by
  rcases ha with rfl | rfl <;> ap_tac
theorem ap_FL_tok (h : Nat) (p : Part) : applyRule ⟨.F h .FL, [.n .TOK], .shape⟩ [.part p] = some [.part p] := by
  ap_tac
theorem ap_FL_words (h : Nat) (ws : List String) :
    applyRule ⟨.F h .FL, [.n (.F h .WR)], .shape⟩ (ws.map .w) = some [.part (.words ws)] := by
  unfold applyRule <;> split <;> simp_all [attachOf, Function.comp_def, List.filterMap_some]

theorem gen_TOK {x : Tok} {a : Term} {p : Part} (hr : (⟨.TOK, [.t a], .shape⟩ : RuleS) ∈ globalRules V)
    (hs : a = .slot ∨ a = .fixed) (ha : a.accepts x = true) (hp : piecesOf (closed (schema V)).toArray (.leaf x) = some [.part p]) :
    Gen V (.n .TOK) [x] [.part p] :=
  gen1 (mem_global hr) (gen_leaf ha hp) (ap_TOK a hs p)

/-- A part, as `FL`. -/
theorem gen_FL (hf : (f, h) ∈ V.frames.zipIdx) : ∀ p : Part, PartOk V f p → Gen V (.n (.F h .FL)) p.toks [.part p]
  | .words ws, ⟨hne, hw⟩ => by
    have hr : (⟨.F h .FL, [.n (.F h .WR)], .shape⟩ : RuleS) ∈ schema V := mem_frame hf (by frame_unfold; simp)
    exact gen1 hr (gen_WR hf ws hne hw) (ap_FL_words h ws)
  | .slot (i + 1), _ => by
    have hr : (⟨.F h .FL, [.n .TOK], .shape⟩ : RuleS) ∈ schema V := mem_frame hf (by frame_unfold; simp)
    exact gen1 hr (gen_TOK (a := .slot) (by global_unfold; simp) (.inl rfl) rfl (by simp [piecesOf])) (ap_FL_tok h _)
  | .fixed i, _ => by
    have hr : (⟨.F h .FL, [.n .TOK], .shape⟩ : RuleS) ∈ schema V := mem_frame hf (by frame_unfold; simp)
    exact gen1 hr (gen_TOK (a := .fixed) (by global_unfold; simp) (.inr rfl) rfl (by simp [piecesOf])) (ap_FL_tok h _)

theorem listOf_part (p : Part) (cs : List Piece) :
    listOf (.part p :: cs) = (listOf cs).map (fun r => (r.1, .part p :: r.2)) := by
  unfold listOf
  simp only [List.filterMap_cons, List.filter_cons]
  split <;> simp_all

theorem ap_J (j : Join) : applyRule ⟨.J, kwSyms [joinWord j], .shape⟩ [.w (joinWord j)] = some [.j j] := by
  have := lower_and; have := lower_or; have := lower_nor
  cases j <;> (unfold applyRule <;> split <;> simp_all [attachOf, kwSyms, joinWord, List.lookup])
theorem ap_HD (h : Nat) (ws : List String) (hl : ∀ w ∈ ws, w.toLower = w) (hne : ws ≠ []) :
    applyRule ⟨.F h .HD, kwSyms ws, .shape⟩ (ws.map .w) = some [.head ws] := by
  obtain ⟨w, ws', rfl⟩ : ∃ w ws', ws = w :: ws' := by cases ws <;> simp_all
  have hm : (w :: ws').map String.toLower = w :: ws' := by
    rw [List.map_congr_left hl, List.map_id']
  simp only [kwSyms, List.map_cons] at hm ⊢
  unfold applyRule <;> split <;> simp_all [attachOf, Function.comp_def, List.filterMap_some]

theorem gen_kws : ∀ ws : List String, (∀ w ∈ ws, w.toLower = w) → GenAll V (kwSyms ws) (ws.map .word) (ws.map .w)
  | [], _ => genAll_nil
  | w :: ws, hl => by
    have := genAll_cons (gen_word (V := V) (a := .kw w) (v := w) (by simp [Term.accepts, hl w (by simp)]))
      (gen_kws ws (fun u hu => hl u (by simp [hu])))
    simpa [kwSyms] using this

theorem gen_J (j : Join) : Gen V (.n .J) [.word (joinWord j)] [.j j] := by
  have hr : (⟨.J, kwSyms [joinWord j], .shape⟩ : RuleS) ∈ schema V :=
    mem_global (by cases j <;> (global_unfold; simp [joinWord]))
  have hl : ∀ w ∈ [joinWord j], w.toLower = w := by
    cases j <;> simp [joinWord, lower_and, lower_or, lower_nor]
  simpa using gen_node hr (gen_kws [joinWord j] hl) (ap_J j)

/-- A marker's words, as `MK m`. -/
theorem gen_MK (hfr : f ∈ V.frames) {m : String} (hm : m ∈ f.markers ++ f.mods) (hne : m ≠ "")
    (hl : ∀ w ∈ wordsOf m, w.toLower = w) (hw : wordsOf m ≠ []) :
    Gen V (.n (.MK m)) ((wordsOf m).map .word) [] := by
  have hr : (⟨.MK m, kwSyms (wordsOf m), .shape⟩ : RuleS) ∈ schema V := by
    refine mem_global ?_
    simp only [globalRules, List.mem_append]
    refine .inr (List.mem_map.mpr ⟨m, mem_firsts.mpr (List.mem_filter.mpr ⟨List.mem_flatMap.mpr ⟨f, hfr, hm⟩,
      by simpa using hne⟩), rfl⟩)
  obtain ⟨w, ws, hws⟩ : ∃ w ws, wordsOf m = w :: ws := by cases h : wordsOf m <;> simp_all
  have := gen_node hr (gen_kws _ hl) (by rw [hws]; exact ap_MK m _ w ws)
  simpa using this

/-- The head, as `HD`. -/
theorem gen_HD (hf : (f, h) ∈ V.frames.zipIdx) (hl : ∀ w ∈ f.head, w.toLower = w) (hne : f.head ≠ []) :
    Gen V (.n (.F h .HD)) (f.head.map .word) [.head f.head] := by
  have hr : (⟨.F h .HD, kwSyms f.head, .shape⟩ : RuleS) ∈ schema V := mem_frame hf (by frame_unfold; simp)
  exact gen_node hr (gen_kws _ hl) (ap_HD h _ hl hne)

/-- The tail of a list of two or more parts, as `PT`. -/
theorem gen_PT (hf : (f, h) ∈ V.frames.zipIdx) (j : Join) : ∀ (q : Part) (rest : List Part),
    (∀ r ∈ q :: rest, PartOk V f r) → ∃ T cs, (∀ p, listToks j (p :: q :: rest) = p.toks ++ T) ∧
      Gen V (.n (.F h .PT)) T cs ∧ ∀ p, listOf (.part p :: cs) = some (j, (p :: q :: rest).map .part)
  | q, [], hok => by
    have hr : (⟨.F h .PT, [.n .J, .n (.F h .FL)], .shape⟩ : RuleS) ∈ schema V := mem_frame hf (by frame_unfold; simp)
    refine ⟨_, _, fun p => ?_, gen2 hr (gen_J j) (gen_FL hf q (hok q (by simp))) (ap_PT1 h _), fun p => ?_⟩
    · simp [listToks]
    · simp [listOf]
  | q, r :: rest, hok => by
    obtain ⟨T, cs, hT, hg, hl⟩ := gen_PT hf j r rest (fun x hx => hok x (by simp [hx]))
    have hr : (⟨.F h .PT, [.t .comma, .n (.F h .FL), .n (.F h .PT)], .shape⟩ : RuleS) ∈ schema V :=
      mem_frame hf (by frame_unfold; simp)
    have hc : Gen V (.t .comma) [.comma] [] := gen_leaf rfl (by simp [piecesOf])
    refine ⟨_, _, fun p => ?_, gen3 hr hc (gen_FL hf q (hok q (by simp))) hg (ap_PT2 h _), fun p => ?_⟩
    · simp [listToks, hT]
    · simp [listOf_part, hl]

/-- A list of two or more parts whose ends are not long, as `PL`. -/
theorem gen_PL (hf : (f, h) ∈ V.frames.zipIdx) (j : Join) (ps : List Part) (hlen : 2 ≤ ps.length)
    (hok : ∀ p ∈ ps, PartOk V f p) (hle : longEnd ps = false) :
    Gen V (.n (.F h .PL)) (listToks j ps) [.list j ps] := by
  obtain ⟨p, q, rest, rfl⟩ : ∃ p q rest, ps = p :: q :: rest := by
    match ps, hlen with
    | p :: q :: rest, _ => exact ⟨p, q, rest, rfl⟩
  obtain ⟨T, cs, hT, hg, hl⟩ := gen_PT hf j q rest (fun x hx => hok x (by simp [hx]))
  have hr : (⟨.F h .PL, [.n (.F h .FL), .n (.F h .PT)], .shape⟩ : RuleS) ∈ schema V :=
    mem_frame hf (by frame_unfold; simp)
  rw [hT p]
  exact gen2 hr (gen_FL hf p (hok p (by simp))) hg (by simpa using ap_PL h cs p j _ (hl p) hle)

end VE.Acts.NormalProofs
