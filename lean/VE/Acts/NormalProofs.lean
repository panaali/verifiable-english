import VE.Acts.Readings
import VE.Grammar.TableInvariant
import VE.Grammar.TableProofs

/-! The existence and bounds halves of `read_normal` (docs/spec/act-phrases.md 5.6); `read_normal` itself, with the
uniqueness half, is in `VE.Acts.NormalUnique`.

Proofs only. (1) `normal_derived`: a derivation of `a.normal` whose meaning is `.one a.canon`, built rule by rule
from 5.2's table. (2) `parse_bounds`: for any input and any well-formed grammar, a raw cap and a step budget from
which the parse is complete and unsaturated, for every larger cap and budget. `read_normal_of_unique` combines them
with the uniqueness half, taken as a hypothesis.
-/

namespace VE.Acts.NormalProofs

set_option linter.unusedSimpArgs false
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
    (∀ w ∈ V.adverbs, w.toLower = w) ∧ (∀ f ∈ V.frames, "" ∉ f.mods) := by
  have h' : checkVocab V = .ok () := by
    unfold framesOk at h; cases hc : checkVocab V <;> simp_all [Except.isOk, Except.toBool]
  unfold checkVocab at h'
  simp only [bind, Except.bind, pure, Except.pure] at h'
  split at h'; · cases h'
  split at h'; · cases h'
  split at h'; · cases h'
  next h3 =>
  iterate 6 (split at h'; · cases h')
  split at h'; · cases h'
  next h10 =>
  iterate 2 (split at h'; · cases h')
  split at h'; · cases h'
  next h13 =>
  iterate 3 (split at h'; · cases h')
  split at h'; · cases h'
  next h17 =>
  refine ⟨fun f hf w hw => ?_, fun f hf m hm hne w hw => ?_, fun w hw => ?_, fun f hf he => ?_⟩
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
  · have := Lexical.forIn_ok h10 (by intro x; split <;> simp) f hf
    rw [if_pos (List.elem_iff.mpr he)] at this
    cases this

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
theorem ap_FW_to : applyRule ⟨.FW, kwSyms ["to"], .shape⟩ [.w "to"] = some [.fw true false] := by
  have := lower_to; have := lower_be
  unfold applyRule <;> split <;> simp_all [attachOf, kwSyms]
theorem ap_FW_be : applyRule ⟨.FW, kwSyms ["be"], .shape⟩ [.w "be"] = some [.fw false true] := by
  have := lower_to; have := lower_be
  unfold applyRule <;> split <;> simp_all [attachOf, kwSyms]
theorem ap_FW_tobe : applyRule ⟨.FW, kwSyms ["to", "be"], .shape⟩ [.w "to", .w "be"] = some [.fw true true] := by
  have := lower_to; have := lower_be
  unfold applyRule <;> split <;> simp_all [attachOf, kwSyms]
theorem ap_S : applyRule ⟨.S, [.t .subj, .n .SINGLE], .shape⟩ cs = some cs := by ap_tac
theorem ap_SINGLE (rhs : List NT) (hr : rhs = [.SC] ∨ rhs = [.ADVSO, .SC] ∨ rhs = [.FW, .SC] ∨
    rhs = [.FW, .ADVSO, .SC]) : applyRule ⟨.SINGLE, rhs.map .n, .shape⟩ cs =
    (itemOf cs).map (fun (fw, h, es) => [.act (singleAct fw h es)]) := by
  rcases hr with rfl | rfl | rfl | rfl <;> ap_tac
theorem ap_SINGLE_of (rhs : List NT) (hr : rhs = [.SC] ∨ rhs = [.ADVSO, .SC] ∨ rhs = [.FW, .SC] ∨
    rhs = [.FW, .ADVSO, .SC]) {ps : List Piece}
    (hp : (itemOf cs).map (fun (fw, h, es) => [Piece.act (singleAct fw h es)]) = some ps) :
    applyRule ⟨.SINGLE, rhs.map .n, .shape⟩ cs = some ps := by
  rw [ap_SINGLE cs rhs hr, hp]

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

/-! ### Elements: arguments, the object, modifiers, adverbs -/

/-- What the frame `f` (numbered `h`) gives the elements: its marker words are lower case and not empty. -/
structure FrameOk (V : Vocab) (f : Frame) (h : Nat) : Prop where
  mem : (f, h) ∈ V.frames.zipIdx
  frame : f ∈ V.frames
  lower : ∀ m ∈ f.markers ++ f.mods, m ≠ "" → ∀ w ∈ wordsOf m, w.toLower = w
  words : ∀ m ∈ f.markers ++ f.mods, m ≠ "" → wordsOf m ≠ []
  mods : "" ∉ f.mods

theorem gen_MK_of (hF : FrameOk V f h) {m : String} (hm : m ∈ f.markers ++ f.mods) (hne : m ≠ "") :
    Gen V (.n (.MK m)) ((wordsOf m).map .word) [] :=
  gen_MK hF.frame hm hne (hF.lower m hm hne) (hF.words m hm hne)

/-- An argument other than the object, as `EE`: `AR m` for one part, `LST m false` for a joined filler. -/
theorem gen_arg (hF : FrameOk V f h) {m : String} {fl : Filler} (hm : m ∈ f.markers) (hne : m ≠ "")
    (hok : ∀ p ∈ fl.parts, PartOk V f p)
    (hj : ∀ j ps, fl = .joined j ps → f.split.contains m = false ∧ 2 ≤ ps.length ∧ longEnd ps = false) :
    Gen V (.n (.F h .EE)) ((wordsOf m).map .word ++ fl.toks) [.elt (.arg m fl) .own] := by
  have hmk := gen_MK_of hF (List.mem_append_left _ hm) hne
  cases fl with
  | one p =>
    have hr : (⟨.F h (.AR m), [.n (.MK m), .n (.F h .FL)], .shape⟩ : RuleS) ∈ schema V :=
      mem_frame hF.mem (by frame_unfold; simp [hm, hne])
    have har := gen2 hr hmk (gen_FL hF.mem p (hok p (by simp [Filler.parts]))) (by simpa using ap_AR h m p)
    have hr2 : (⟨.F h .EE, [.n (.F h (.AR m))], .shape⟩ : RuleS) ∈ schema V :=
      mem_frame hF.mem (by frame_unfold; simp [hm, hne])
    exact gen1 hr2 har (ap_EE1 h _ _)
  | joined j ps =>
    obtain ⟨hs, hlen, hle⟩ := hj j ps rfl
    have hr : (⟨.F h (.OL m), [.n (.MK m), .n (.F h .PL)], .shape⟩ : RuleS) ∈ schema V :=
      mem_frame hF.mem (by frame_unfold; simp [hm, hne])
    have hol := gen2 hr hmk (gen_PL hF.mem j ps hlen hok hle) (by simpa using ap_OL h m j ps)
    have hr2 : (⟨.F h (.LST m false), [.n (.F h (.OL m))], .shape⟩ : RuleS) ∈ schema V :=
      mem_frame hF.mem (by frame_unfold; simp_all)
    have hlst := gen1 hr2 hol (ap_LST h m j ps)
    have hr3 : (⟨.F h .EE, [.n (.F h (.LST m false))], .shape⟩ : RuleS) ∈ schema V :=
      mem_frame hF.mem (by frame_unfold; simp_all)
    exact gen1 hr3 hlst (ap_EE1 h _ _)

/-- A prepositional modifier, as `EE`. -/
theorem gen_prep (hF : FrameOk V f h) {m : String} {p : Part} (hm : m ∈ f.mods) (hok : PartOk V f p) :
    Gen V (.n (.F h .EE)) ((wordsOf m).map .word ++ p.toks) [.elt (.mod (.prep m p)) .own] := by
  have hne : m ≠ "" := fun he => hF.mods (he ▸ hm)
  have hr : (⟨.F h .EE, [.n (.MK m), .n (.F h .FL)], .shape⟩ : RuleS) ∈ schema V :=
    mem_frame hF.mem (by frame_unfold; simp [hm])
  exact gen2 hr (gen_MK_of hF (List.mem_append_right _ hm) hne) (gen_FL hF.mem p hok) (by simpa using ap_EEmod h m p)

/-- The object, as `O`. -/
theorem gen_obj (hF : FrameOk V f h) (hobj : "" ∈ f.markers) {fl : Filler} (hok : ∀ p ∈ fl.parts, PartOk V f p)
    (hj : ∀ j ps, fl = .joined j ps → f.split.contains "" = false ∧ 2 ≤ ps.length ∧ longEnd ps = false) :
    Gen V (.n (.F h .O)) fl.toks [.elt (.arg "" fl) .own] := by
  cases fl with
  | one p =>
    have hr : (⟨.F h .O, [.n (.F h .FL)], .shape⟩ : RuleS) ∈ schema V := mem_frame hF.mem (by frame_unfold; simp [hobj])
    exact gen1 hr (gen_FL hF.mem p (hok p (by simp [Filler.parts]))) (ap_O1 h p)
  | joined j ps =>
    obtain ⟨hs, hlen, hle⟩ := hj j ps rfl
    have hr : (⟨.F h .O, [.n (.F h .PL)], .shape⟩ : RuleS) ∈ schema V :=
      mem_frame hF.mem (by frame_unfold; simp_all)
    exact gen1 hr (gen_PL hF.mem j ps hlen hok hle) (ap_O2 h j ps)

/-- A run of elements, as `ER`. -/
theorem gen_ER (hF : FrameOk V f h) : ∀ L : List (List Tok × Piece), L ≠ [] →
    (∀ q ∈ L, Gen V (.n (.F h .EE)) q.1 [q.2]) → Gen V (.n (.F h .ER)) (L.flatMap (·.1)) (L.map (·.2))
  | [], hne, _ => absurd rfl hne
  | [q], _, hq => by
    have hr : (⟨.F h .ER, [.n (.F h .EE)], .shape⟩ : RuleS) ∈ schema V := mem_frame hF.mem (by frame_unfold; simp)
    simpa using gen1 hr (hq q (by simp)) (ap_ER1 h _)
  | q :: q2 :: L, _, hq => by
    have hr : (⟨.F h .ER, [.n (.F h .EE), .n (.F h .ER)], .shape⟩ : RuleS) ∈ schema V :=
      mem_frame hF.mem (by frame_unfold; simp)
    have h2 := gen_ER hF (q2 :: L) (by simp) (fun x hx => hq x (by simp [hx]))
    simpa using gen2 hr (hq q (by simp)) h2 (ap_ER2 h _)

/-- A run of adverbs, as `ADVSO`. -/
theorem gen_ADVSO : ∀ ws : List String, ws ≠ [] → (∀ w ∈ ws, w ∈ V.adverbs ∧ w.toLower = w) →
    Gen V (.n .ADVSO) (ws.map .word) (ws.map (fun w => .elt (.mod (.adv w)) .own))
  | [], hne, _ => absurd rfl hne
  | w :: ws, _, hw => by
    have hr1 : (⟨.ADVO, [.t (.adv V.adverbs)], .shape⟩ : RuleS) ∈ schema V := mem_global (by global_unfold; simp)
    have ha : Gen V (.n .ADVO) [.word w] [.elt (.mod (.adv w)) .own] := by
      have hl := (hw w (by simp)).2
      have := gen1 hr1 (gen_word (by simp [Term.accepts, hl, (hw w (by simp)).1])) (ap_ADVO V.adverbs w)
      rwa [hl] at this
    cases ws with
    | nil =>
      have hr : (⟨.ADVSO, [.n .ADVO], .shape⟩ : RuleS) ∈ schema V := mem_global (by global_unfold; simp)
      simpa using gen1 hr ha (ap_ADVSO1 _)
    | cons u ws =>
      have hr : (⟨.ADVSO, [.n .ADVO, .n .ADVSO], .shape⟩ : RuleS) ∈ schema V := mem_global (by global_unfold; simp)
      have h2 := gen_ADVSO (u :: ws) (by simp) (fun x hx => hw x (by simp [hx]))
      simpa using gen2 hr ha h2 (ap_ADVSO2 _)

/-- The function words, as `FW`. -/
theorem gen_FW (t b : Bool) (htb : t = true ∨ b = true) :
    Gen V (.n .FW) ((if t then [Tok.word "to"] else []) ++ (if b then [Tok.word "be"] else [])) [.fw t b] := by
  have hl : ∀ w ∈ ["to", "be"], w.toLower = w := by simp [lower_to, lower_be]
  cases t <;> cases b <;> simp at htb
  · have hr : (⟨.FW, kwSyms ["be"], .shape⟩ : RuleS) ∈ schema V := mem_global (by global_unfold; simp [kwSyms])
    simpa using gen_node hr (gen_kws ["be"] (by simp [lower_be])) ap_FW_be
  · have hr : (⟨.FW, kwSyms ["to"], .shape⟩ : RuleS) ∈ schema V := mem_global (by global_unfold; simp [kwSyms])
    simpa using gen_node hr (gen_kws ["to"] (by simp [lower_to])) ap_FW_to
  · have hr : (⟨.FW, kwSyms ["to", "be"], .shape⟩ : RuleS) ∈ schema V := mem_global (by global_unfold; simp [kwSyms])
    simpa using gen_node hr (gen_kws ["to", "be"] hl) ap_FW_tobe

/-! ### The item: head and elements (`SC`), function words and adverbs (`SINGLE`), the start -/

/-- The head and its elements, as `SC`: the object first when the frame has one, then the other elements. -/
theorem gen_SC (hF : FrameOk V f h) (hl : ∀ w ∈ f.head, w.toLower = w) (hne : f.head ≠ [])
    (obj : List (List Tok × Piece))
    (hobj : ("" ∈ f.markers ∧ ∃ q, obj = [q] ∧ Gen V (.n (.F h .O)) q.1 [q.2]) ∨ ("" ∉ f.markers ∧ obj = []))
    (L : List (List Tok × Piece)) (hL : ∀ q ∈ L, Gen V (.n (.F h .EE)) q.1 [q.2]) :
    Gen V (.n .SC) (f.head.map .word ++ (obj ++ L).flatMap (·.1)) (.head f.head :: (obj ++ L).map (·.2)) := by
  have hhd := gen_HD hF.mem hl hne
  have hsc2 : (⟨.SC, [.n (.F h .HD), .n (.F h .SM)], .shape⟩ : RuleS) ∈ schema V :=
    mem_frame hF.mem (by frame_unfold; simp)
  rcases hobj with ⟨ho, q, rfl, hq⟩ | ⟨ho, rfl⟩
  · have hsm : (⟨.F h .SM, [.n (.F h .OWNM)], .shape⟩ : RuleS) ∈ schema V := mem_frame hF.mem (by frame_unfold; simp [ho])
    have hown : Gen V (.n (.F h .OWNM)) (([q] ++ L).flatMap (·.1)) (([q] ++ L).map (·.2)) := by
      cases L with
      | nil =>
        have hr : (⟨.F h .OWNM, [.n (.F h .O)], .shape⟩ : RuleS) ∈ schema V :=
          mem_frame hF.mem (by frame_unfold; simp [ho])
        simpa using gen1 hr hq (ap_OWNM1 h _)
      | cons q2 L =>
        have hr : (⟨.F h .OWNM, [.n (.F h .O), .n (.F h .ER)], .shape⟩ : RuleS) ∈ schema V :=
          mem_frame hF.mem (by frame_unfold; simp [ho])
        simpa using gen2 hr hq (gen_ER hF (q2 :: L) (by simp) hL) (ap_OWNM2 h _)
    exact gen2 hsc2 hhd (gen1 hsm hown (ap_SM h _ _)) (ap_SC2 h _)
  · cases L with
    | nil =>
      have hr : (⟨.SC, [.n (.F h .HD)], .shape⟩ : RuleS) ∈ schema V := mem_frame hF.mem (by frame_unfold; simp)
      simpa using gen1 hr hhd (ap_SC1 h _)
    | cons q2 L =>
      have hsm : (⟨.F h .SM, [.n (.F h .ER)], .shape⟩ : RuleS) ∈ schema V := mem_frame hF.mem (by frame_unfold; simp [ho])
      have her := gen1 hsm (gen_ER hF (q2 :: L) (by simp) hL) (ap_SM h _ _)
      simpa using gen2 hsc2 hhd her (ap_SC2 h _)

/-- The function-word piece of an item, when it has one. -/
theorem gen_SINGLE (t b : Bool) (ws : List String) (hws : ∀ w ∈ ws, w ∈ V.adverbs ∧ w.toLower = w)
    {w : List Tok} {cs ps : List Piece} (hsc : Gen V (.n .SC) w cs)
    (hp : (itemOf ((if t || b then [Piece.fw t b] else []) ++ ws.map (fun w => .elt (.mod (.adv w)) .own) ++ cs)).map
      (fun (fw, h, es) => [Piece.act (singleAct fw h es)]) = some ps) :
    Gen V (.n .SINGLE) ((if t then [Tok.word "to"] else []) ++ (if b then [Tok.word "be"] else []) ++
      ws.map .word ++ w) ps := by
  have hmem (rhs : List NT) (hr : rhs = [.SC] ∨ rhs = [.ADVSO, .SC] ∨ rhs = [.FW, .SC] ∨ rhs = [.FW, .ADVSO, .SC]) :
      (⟨.SINGLE, rhs.map .n, .shape⟩ : RuleS) ∈ schema V := by
    refine mem_global ?_
    rcases hr with rfl | rfl | rfl | rfl <;> (global_unfold; simp)
  by_cases htb : t = true ∨ b = true
  · have hfw := gen_FW (V := V) t b htb
    have htb' : (t || b) = true := by rcases htb with h | h <;> simp [h]
    rw [htb'] at hp
    cases ws with
    | nil =>
      have := gen2 (hmem [.FW, .SC] (by simp)) hfw hsc (ap_SINGLE_of _ [.FW, .SC] (by simp) (by simpa using hp))
      simpa using this
    | cons u ws =>
      have ha := gen_ADVSO (u :: ws) (by simp) hws
      have := gen3 (hmem [.FW, .ADVSO, .SC] (by simp)) hfw ha hsc (ap_SINGLE_of _ [.FW, .ADVSO, .SC] (by simp) (by simpa using hp))
      simpa using this
  · obtain ⟨rfl, rfl⟩ : t = false ∧ b = false := by cases t <;> cases b <;> simp_all
    cases ws with
    | nil =>
      have := gen1 (hmem [.SC] (by simp)) hsc (ap_SINGLE_of _ [.SC] (by simp) (by simpa using hp))
      simpa using this
    | cons u ws =>
      have ha := gen_ADVSO (u :: ws) (by simp) hws
      have := gen2 (hmem [.ADVSO, .SC] (by simp)) ha hsc (ap_SINGLE_of _ [.ADVSO, .SC] (by simp) (by simpa using hp))
      simpa using this

/-- The start: `{0}` and an item. -/
theorem gen_S {w : List Tok} {ps : List Piece} (h1 : Gen V (.n .SINGLE) w ps) : Gen V (.n .S) (.slot 0 :: w) ps := by
  have hr : (⟨.S, [.t .subj, .n .SINGLE], .shape⟩ : RuleS) ∈ schema V := mem_global (by global_unfold; simp)
  have hs : Gen V (.t .subj) [.slot 0] [] := gen_leaf rfl (by simp [piecesOf])
  simpa using gen2 hr hs h1 (by simpa using ap_S ps)

/-! ### The meaning of the item: one atom, its elements in order -/

theorem wordsOf_empty : wordsOf "" = [] := by
  have h0 : "".utf8ByteSize = 0 := rfl
  have h1 : "".extract 0 0 = "" := by decide
  simp only [wordsOf, String.splitOn]
  rw [String.splitOnAux]
  simp [String.atEnd, h0, h1]

/-- An atom's adverbs, in order. -/
def advWords : List Modifier → List String
  | [] => []
  | .adv w :: ms => w :: advWords ms
  | .prep _ _ :: ms => advWords ms
/-- An atom's prepositional modifiers, in order. -/
def preps : List Modifier → List (String × Part)
  | [] => []
  | .adv _ :: ms => preps ms
  | .prep m p :: ms => (m, p) :: preps ms

theorem add_mods : ∀ (ms : List Modifier) (x : Atom), (ms.map Elt.mod).foldl Atom.add x = { x with mods := x.mods ++ ms }
  | [], x => by simp
  | md :: ms, x => by simp [Atom.add, add_mods ms]

theorem add_args : ∀ (L : List (String × Filler)) (x : Atom),
    (L.map (fun q => Elt.arg q.1 q.2)).foldl Atom.add x = { x with args := x.args ++ L }
  | [], x => by simp
  | q :: L, x => by simp [Atom.add, add_args L]

theorem fold_elts : ∀ (es : List Elt) (x : Atom),
    (es.map (fun e => Piece.elt e .own)).foldl (fun as p => addPiece (as.length - 1) as p) [x] = [es.foldl Atom.add x]
  | [], _ => rfl
  | e :: es, x => by
    rw [List.map_cons, List.foldl_cons]
    have : addPiece ([x].length - 1) [x] (Piece.elt e .own) = [x.add e] := by simp [addPiece]
    rw [this, fold_elts es]; rfl
theorem filterMap_none {α β : Type} (l : List α) : l.filterMap (fun _ => (none : Option β)) = [] := by
  induction l <;> simp_all
theorem findSome_none {α β : Type} (l : List α) : l.findSome? (fun _ => (none : Option β)) = none := by
  induction l <;> simp_all
theorem single_meaning (t b : Bool) (ws hd : List String) (es : List Elt) :
    (itemOf ((if t || b then [Piece.fw t b] else []) ++ ws.map (fun w => Piece.elt (.mod (.adv w)) .own) ++
      (Piece.head hd :: es.map (fun e => Piece.elt e .own)))).map (fun (fw, h, es) => [Piece.act (singleAct fw h es)]) =
    some [.act (.one ((ws.map (fun w => Elt.mod (.adv w)) ++ es).foldl Atom.add ⟨t, b, hd, [], []⟩))] := by
  have hw : ws.map (fun w => Piece.elt (.mod (.adv w)) .own) =
      (ws.map (fun w => Elt.mod (.adv w))).map (fun e => Piece.elt e .own) := by simp
  rw [hw]
  generalize ws.map (fun w => Elt.mod (.adv w)) = A
  have hfold (F : List Piece) (hF : ∀ y, F.foldl (fun as p => addPiece (as.length - 1) as p) [y] = [y]) (x : Atom) :
      (F ++ A.map (fun e => Piece.elt e .own) ++ (Piece.head hd :: es.map (fun e => Piece.elt e .own))).foldl
        (fun as p => addPiece (as.length - 1) as p) [x] = [(A ++ es).foldl Atom.add x] := by
    rw [List.foldl_append, List.foldl_append, hF, fold_elts, List.foldl_cons, List.foldl_append]
    exact fold_elts es _
  have h1 := hfold [] (fun _ => rfl)
  have h2 (t b : Bool) := hfold [Piece.fw t b] (fun _ => rfl)
  simp only [List.nil_append] at h1
  cases t <;> cases b <;> simp only [Bool.or_false, Bool.or_true, Bool.false_or, Bool.false_eq_true, ↓reduceIte] <;>
    simp only [itemOf, singleAct, List.filterMap_append, List.filterMap_map, List.filterMap_cons, Function.comp_def,
      filterMap_none, List.nil_append, List.findSome?_append, List.findSome?_map, findSome_none,
      List.findSome?_cons, Option.none_or, Option.some_or, Option.map_some, List.filterMap_nil] <;>
    (try simp only [h1, h2, List.findSome?_append, List.findSome?_map, Function.comp_def, findSome_none,
      List.findSome?_cons, List.findSome?_nil, Option.none_or]) <;>
    rfl

theorem canon_eq (a : Atom) : a.canon = ((advWords a.mods).map (fun w => Elt.mod (.adv w)) ++
    (a.canon.args.map (fun q => Elt.arg q.1 q.2) ++ (preps a.mods).map (fun q => Elt.mod (.prep q.1 q.2)))).foldl
      Atom.add ⟨a.toWord, a.beWord, a.head, [], []⟩ := by
  have e1 : (advWords a.mods).map (fun w => Elt.mod (.adv w)) = ((advWords a.mods).map Modifier.adv).map Elt.mod := by
    simp
  have e2 : (preps a.mods).map (fun q => Elt.mod (.prep q.1 q.2)) =
      ((preps a.mods).map (fun q => Modifier.prep q.1 q.2)).map Elt.mod := by simp
  rw [e1, e2, List.foldl_append, List.foldl_append, add_mods, add_args, add_mods]
  simp only [Atom.canon, List.nil_append]
  congr 1
  generalize a.mods = ms
  congr 1
  · induction ms with
    | nil => rfl
    | cons md ms ih => cases md <;> simp_all [advWords]
  · induction ms with
    | nil => rfl
    | cons md ms ih => cases md <;> simp_all [preps]

/-- The normal form, in the pieces the derivation reads: `{0}`, function words, adverbs, head, arguments in `canon`'s
order, prepositional modifiers. -/
theorem normal_toks (a : Atom) : a.normal = .slot 0 :: ((if a.toWord then [Tok.word "to"] else []) ++
    (if a.beWord then [Tok.word "be"] else []) ++ (advWords a.mods).map .word ++
    (a.head.map .word ++ (a.canon.args.flatMap (fun x => (wordsOf x.1).map Tok.word ++ x.2.toks) ++
      (preps a.mods).flatMap (fun q => (wordsOf q.1).map Tok.word ++ q.2.toks)))) := by
  simp only [Atom.normal, List.append_assoc, List.singleton_append, List.cons_append, List.nil_append]
  congr 4
  · generalize a.mods = ms
    induction ms with
    | nil => rfl
    | cons md ms ih => cases md <;> simp_all [advWords]
  · congr 2
    generalize a.mods = ms
    induction ms with
    | nil => rfl
    | cons md ms ih => cases md <;> simp_all [preps]

theorem mem_preps {m : String} {p : Part} : ∀ {ms : List Modifier}, (m, p) ∈ preps ms → .prep m p ∈ ms
  | [], h => by simp [preps] at h
  | .adv _ :: ms, h => List.mem_cons_of_mem _ (mem_preps (ms := ms) (by simpa [preps] using h))
  | .prep m' p' :: ms, h => by
    simp only [preps, List.mem_cons, Prod.mk.injEq] at h
    rcases h with ⟨rfl, rfl⟩ | h
    · simp
    · exact List.mem_cons_of_mem _ (mem_preps h)

theorem mem_advWords {w : String} : ∀ {ms : List Modifier}, w ∈ advWords ms → .adv w ∈ ms
  | [], h => by simp [advWords] at h
  | .prep _ _ :: ms, h => List.mem_cons_of_mem _ (mem_advWords (ms := ms) (by simpa [advWords] using h))
  | .adv w' :: ms, h => by
    simp only [advWords, List.mem_cons] at h
    rcases h with rfl | h
    · simp
    · exact List.mem_cons_of_mem _ (mem_advWords h)

theorem filter_obj (l : List (String × Filler)) :
    (l.filter (·.1 == "") ++ l.filter (·.1 != "")).filter (·.1 == "") = l.filter (·.1 == "") := by
  induction l with
  | nil => rfl
  | cons x l ih =>
    by_cases hx : x.1 = "" <;> simp_all [List.filter_cons]

theorem all_obj (q : String × Filler → Bool) (l : List (String × Filler)) :
    (l.filter (·.1 == "") ++ l.filter (·.1 != "")).all q = l.all q := by
  induction l with
  | nil => rfl
  | cons x l ih =>
    simp only [List.all_append] at ih
    by_cases hx : x.1 = "" <;> cases hq : q x <;> simp_all [List.filter_cons]

/-- `atomOk` does not see the order of the arguments and modifiers. -/
theorem atomOk_canon (V : Vocab) (a : Atom) : atomOk V a.canon = atomOk V a := by
  unfold atomOk Atom.canon
  simp only
  split
  · rfl
  · rw [filter_obj, all_obj]
    congr 1
    generalize a.mods = ms
    induction ms with
    | nil => rfl
    | cons md ms ih =>
      simp only [List.all_append] at ih
      cases md <;> simp_all [List.filter_cons, Bool.and_left_comm]

/-! ### (1) A derivation of the normal form that means the canonical atom -/

theorem normal_derived (V : Vocab) (hV : framesOk V = true) (a : Atom) (ha : normalOk V a = true) :
    Derived V a.normal (.one a.canon) := by
  have hwds := framesOk_words hV
  obtain ⟨lh, lm, la, lmods⟩ := framesOk_lower hV
  have ha0 := ha
  unfold normalOk at ha
  split at ha
  · cases ha
  rename_i f hfind
  have hfr : f ∈ V.frames := List.mem_of_find?_eq_some hfind
  have hfh : f.head = a.head := by simpa using List.find?_some hfind
  obtain ⟨h, hh⟩ : ∃ h, (f, h) ∈ V.frames.zipIdx := by
    obtain ⟨i, hi, he⟩ := List.getElem_of_mem hfr
    exact ⟨i, List.mem_zipIdx_iff_getElem?.mpr (by rw [List.getElem?_eq_getElem hi, he])⟩
  have hF : FrameOk V f h := ⟨hh, hfr, lm f hfr, (hwds f hfr).2, lmods f hfr⟩
  simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at ha
  obtain ⟨⟨⟨hatom, hparts⟩, _⟩, hjoin⟩ := ha
  have hatom0 := hatom
  unfold atomOk at hatom
  rw [hfind] at hatom
  simp only [Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at hatom
  obtain ⟨⟨hcount, hmk⟩, hmods⟩ := hatom
  -- the parts and joined fillers of the arguments, the parts of the modifiers
  have hpa : ∀ x ∈ a.args, ∀ p ∈ x.2.parts, PartOk V f p := by
    intro x hx p hp
    have := hparts p (List.mem_append_left _ (List.mem_flatMap.mpr ⟨x, hx, hp⟩))
    cases p <;> simp_all [PartOk]
  have hpm : ∀ q ∈ preps a.mods, PartOk V f q.2 := by
    intro q hq
    have := hparts q.2 (List.mem_append_right _ (List.mem_filterMap.mpr ⟨.prep q.1 q.2, mem_preps hq, rfl⟩))
    cases hq2 : q.2 <;> simp_all [PartOk]
  have hja : ∀ x ∈ a.args, ∀ j ps, x.2 = .joined j ps →
      f.split.contains x.1 = false ∧ 2 ≤ ps.length ∧ longEnd ps = false := by
    intro x hx j ps he
    have := hjoin x hx
    obtain ⟨m, fl⟩ := x
    simp only at he; subst he
    simp_all
  -- the elements after the object
  let argE (x : String × Filler) : List Tok × Piece := ((wordsOf x.1).map Tok.word ++ x.2.toks, .elt (.arg x.1 x.2) .own)
  let prepE (q : String × Part) : List Tok × Piece :=
    ((wordsOf q.1).map Tok.word ++ q.2.toks, .elt (.mod (.prep q.1 q.2)) .own)
  let objs := a.args.filter (·.1 == "")
  let rest := a.args.filter (·.1 != "")
  let L := rest.map argE ++ (preps a.mods).map prepE
  have hL : ∀ q ∈ L, Gen V (.n (.F h .EE)) q.1 [q.2] := by
    intro q hq
    rcases List.mem_append.mp hq with hq | hq
    · obtain ⟨x, hx, rfl⟩ := List.mem_map.mp hq
      obtain ⟨hxa, hxe⟩ := List.mem_filter.mp hx
      have hm := hmk x hxa
      exact gen_arg hF (by simpa using hm) (by simpa using hxe) (hpa x hxa) (hja x hxa)
    · obtain ⟨y, hy, rfl⟩ := List.mem_map.mp hq
      have hm := hmods (.prep y.1 y.2) (mem_preps hy)
      exact gen_prep hF (by simpa using hm) (hpm y hy)
  -- the object
  have hobj : ("" ∈ f.markers ∧ ∃ q, objs.map argE = [q] ∧ Gen V (.n (.F h .O)) q.1 [q.2]) ∨
      ("" ∉ f.markers ∧ objs.map argE = []) := by
    by_cases ho : "" ∈ f.markers
    · refine .inl ⟨ho, ?_⟩
      have h1 : objs.length = 1 := by simpa [ho] using hcount
      obtain ⟨x, hx⟩ := List.length_eq_one_iff.mp h1
      have hxm : x ∈ objs := by rw [hx]; simp
      obtain ⟨hxa, hxe⟩ := List.mem_filter.mp hxm
      obtain ⟨m, fl⟩ := x
      simp only [beq_iff_eq] at hxe
      subst hxe
      refine ⟨argE ("", fl), by rw [hx]; rfl, ?_⟩
      simp only [argE, wordsOf_empty, List.map_nil, List.nil_append]
      exact gen_obj hF ho (hpa _ hxa) (fun j ps he => hja _ hxa j ps he)
    · refine .inr ⟨ho, ?_⟩
      have h0 : objs = [] := by
        have hc := hcount
        simp only [ho, List.elem_eq_mem, decide_false, Bool.false_eq_true, if_false] at hc
        exact List.length_eq_zero_iff.mp hc
      simp [h0]
  have hsc := gen_SC hF (lh f hfr) (hwds f hfr).1 _ hobj L hL
  -- the item's meaning
  let es : List Elt := a.canon.args.map (fun q => Elt.arg q.1 q.2) ++ (preps a.mods).map (fun q => Elt.mod (.prep q.1 q.2))
  have hes : (objs.map argE ++ L).map (·.2) = es.map (fun e => Piece.elt e .own) := by
    simp [L, es, argE, prepE, objs, rest, Atom.canon, List.map_append, Function.comp_def]
  have hws : ∀ w ∈ advWords a.mods, w ∈ V.adverbs ∧ w.toLower = w := by
    intro w hw
    have := hmods (.adv w) (mem_advWords hw)
    exact ⟨by simpa using this, la w (by simpa using this)⟩
  have hsm := single_meaning a.toWord a.beWord (advWords a.mods) f.head es
  rw [← hes] at hsm
  have hsingle := gen_SINGLE a.toWord a.beWord (advWords a.mods) hws hsc hsm
  obtain ⟨d, hd, hy, hp⟩ := gen_S hsingle
  refine ⟨d, ⟨hd, ?_⟩, false, ?_⟩
  · rw [hy, normal_toks, ← hfh]
    simp [L, argE, prepE, objs, rest, Atom.canon, List.flatMap_append, List.flatMap_map]
  · have hcanon : (List.foldl Atom.add ⟨a.toWord, a.beWord, f.head, [], []⟩
        (List.map (fun w => Elt.mod (Modifier.adv w)) (advWords a.mods) ++ es)) = a.canon := by
      rw [canon_eq a, hfh]
    have hok : actOk V (.one a.canon) = true := by simp [actOk, atomOk_canon, hatom0]
    simp only [meaning, meaningWith, hp, hcanon, hok, if_true]

/-! ## (2) The bounds: finitely many derivations, and a step charge that does not grow with the cap -/

section Bounds
open VE.Grammar

section Finite
variable {T K : Type} [Accepts K T] {G : Grammar K}

/-- Finitely many derivations of `X` over `u`. -/
def FinD (G : Grammar K) (X : Sym K) (u : List T) : Prop :=
  ∃ L : List (Tree T), ∀ t, t.derives G X = true → t.yield = u → t ∈ L
/-- Finitely many derivations of the symbols `Xs` over `u`. -/
def FinDs (G : Grammar K) (Xs : List (Sym K)) (u : List T) : Prop :=
  ∃ L : List (List (Tree T)), ∀ us, derivesAll G Xs us = true → yieldAll us = u → us ∈ L

/-- A family of finite lists, one for each `k < m`, collected into one. -/
theorem collect {α : Type} {P : Nat → α → Prop} : ∀ m, (∀ k < m, ∃ L : List α, ∀ x, P k x → x ∈ L) →
    ∃ L : List α, ∀ k < m, ∀ x, P k x → x ∈ L
  | 0, _ => ⟨[], fun k hk => absurd hk (Nat.not_lt_zero k)⟩
  | m + 1, h => by
    obtain ⟨L1, h1⟩ := collect m (fun k hk => h k (by omega))
    obtain ⟨L2, h2⟩ := h m (by omega)
    refine ⟨L1 ++ L2, fun k hk x hx => ?_⟩
    rcases Nat.lt_or_ge k m with hl | hl
    · exact List.mem_append_left _ (h1 k hl x hx)
    · exact List.mem_append_right _ (h2 x (by rw [show k = m by omega] at hx; exact hx))

theorem finDs_seq (hG : G.wf = true) : ∀ (Xs : List (Sym K)) (u : List T),
    (∀ Y ∈ Xs, ∀ u' : List T, u'.length ≤ u.length → (2 ≤ Xs.length → u'.length < u.length) → FinD G Y u') →
    FinDs G Xs u
  | [], u, _ => ⟨[[]], fun us h _ => by
      match us, h with
      | [], _ => simp⟩
  | Y :: Ys, u, hY => by
    have hk : ∀ k < u.length + 1, ∃ L : List (List (Tree T)), ∀ us, (∃ t ts, us = t :: ts ∧
        t.derives G Y = true ∧ t.yield = u.take k ∧ derivesAll G Ys ts = true ∧ yieldAll ts = u.drop k) → us ∈ L := by
      intro k hk
      by_cases hk0 : k = 0
      · refine ⟨[], fun us ⟨t, ts, _, ht, hy, _⟩ => ?_⟩
        exact absurd (by rw [hy, hk0]; rfl) (yield_ne_nil hG ht)
      by_cases hlast : Ys ≠ [] ∧ k = u.length
      · refine ⟨[], fun us ⟨t, ts, _, _, _, hts, hy⟩ => ?_⟩
        exact absurd (by rw [hy, hlast.2]; simp) (yieldAll_ne_nil hG hts hlast.1)
      have hlen : 2 ≤ (Y :: Ys).length → k < u.length := by
        intro h2
        have hne : Ys ≠ [] := by intro he; simp [he] at h2
        have : k ≠ u.length := fun e => hlast ⟨hne, e⟩
        omega
      obtain ⟨L1, h1⟩ := hY Y (by simp) (u.take k) (by simp only [List.length_take]; omega)
        (fun h2 => by have := hlen h2; simp only [List.length_take]; omega)
      obtain ⟨L2, h2⟩ := finDs_seq hG Ys (u.drop k) (fun Y' hY' u' hu' _ =>
        hY Y' (by simp [hY']) u' (by simp at hu'; omega) (fun _ => by simp at hu'; omega))
      exact ⟨L1.flatMap (fun t => L2.map (t :: ·)), fun us ⟨t, ts, he, ht, hy, hts, hys⟩ =>
        he ▸ List.mem_flatMap.mpr ⟨t, h1 t ht hy, List.mem_map.mpr ⟨ts, h2 ts hts hys, rfl⟩⟩⟩
    obtain ⟨L, hL⟩ := collect _ hk
    refine ⟨L, fun us h hy => ?_⟩
    match us, h with
    | t :: ts, h =>
      rw [derivesAll_cons, Bool.and_eq_true] at h
      rw [yieldAll_cons] at hy
      have hle : t.yield.length ≤ u.length := by rw [← hy]; simp
      refine hL t.yield.length (by omega) _ ⟨t, ts, rfl, h.1, ?_, h.2, ?_⟩
      · rw [← hy]; simp
      · rw [← hy]; simp

theorem finD_term {a : K} {u : List T} : FinD G (.t a) u := by
  refine ⟨u.map .leaf, fun t ht hy => ?_⟩
  match t, ht with
  | .leaf x, _ => rw [yield_leaf] at hy; subst hy; simp

/-- The rank of a symbol: its nonterminal's, `0` for a terminal. -/
def symRank (G : Grammar K) : Sym K → Nat
  | .n A => G.rank.getD A 0
  | .t _ => 0

theorem finD_all (hG : G.wf = true) : ∀ (n r : Nat) (X : Sym K) (u : List T), u.length ≤ n → symRank G X ≤ r →
    FinD G X u := by
  intro n
  induction n with
  | zero =>
    intro r X u hu _
    refine ⟨[], fun t ht hy => ?_⟩
    exact absurd (by rw [hy]; exact List.eq_nil_of_length_eq_zero (by omega)) (yield_ne_nil hG ht)
  | succ n ihn =>
    intro r
    induction r using Nat.strongRecOn with
    | _ rk ihr =>
    intro X u hu hX
    match X with
    | .t a => exact finD_term
    | .n A =>
      have hr : ∀ r < G.rules.size, ∃ L : List (Tree T), ∀ t, (∃ ks R, t = .node r ks ∧ G.rules[r]? = some R ∧
          R.lhs = A ∧ derivesAll G R.rhs ks = true ∧ yieldAll ks = u) → t ∈ L := by
        intro r hrs
        have hR : G.rules[r]? = some G.rules[r] := by simp [hrs]
        by_cases hlhs : G.rules[r].lhs = A
        · obtain ⟨L, hL⟩ := finDs_seq hG G.rules[r].rhs u (fun Y hY u' hu' h2 => by
            by_cases hlt : u'.length < u.length
            · exact ihn (symRank G Y) Y u' (by omega) (Nat.le_refl _)
            · have h1 : G.rules[r].rhs.length < 2 := by
                rcases Nat.lt_or_ge G.rules[r].rhs.length 2 with h | h
                · exact h
                · exact absurd (h2 h) hlt
              obtain ⟨rest, hrest⟩ : ∃ rest, G.rules[r].rhs = Y :: rest := by
                match hm : G.rules[r].rhs, hY with
                | Z :: rest, hY =>
                  have : rest = [] := by rw [hm] at h1; simp at h1; exact List.eq_nil_of_length_eq_zero (by omega)
                  subst this
                  simp at hY; exact ⟨[], by rw [hY]⟩
              match Y, hrest with
              | .t b, _ => exact finD_term
              | .n B, hrest =>
                have hrank := rule_head_rank hG hR hrest
                rw [hlhs] at hrank
                have hX' : G.rank.getD A 0 ≤ rk := hX
                exact ihr (G.rank.getD B 0) (by omega) (.n B) u' (by omega) (Nat.le_refl _))
          exact ⟨L.map (.node r), fun t ⟨ks, R, he, hR', _, hks, hy⟩ => by
            rw [hR] at hR'; cases hR'
            exact he ▸ List.mem_map.mpr ⟨ks, hL ks hks hy, rfl⟩⟩
        · exact ⟨[], fun t ⟨ks, R, _, hR', hl, _⟩ => by rw [hR] at hR'; cases hR'; exact absurd hl hlhs⟩
      obtain ⟨L, hL⟩ := collect _ hr
      refine ⟨L, fun t ht hy => ?_⟩
      obtain ⟨r, ks, R0, rfl, hr0, hl0, hks⟩ := derives_root ht
      have hrs : r < G.rules.size := (Array.getElem?_eq_some_iff.mp hr0).1
      exact hL r hrs _ ⟨ks, R0, rfl, hr0, hl0, hks, by rw [← yield_node]; exact hy⟩
theorem finDs (hG : G.wf = true) (Xs : List (Sym K)) (u : List T) : FinDs G Xs u :=
  finDs_seq hG Xs u (fun Y _ u' _ _ => finD_all hG u'.length (symRank G Y) Y u' (Nat.le_refl _) (Nat.le_refl _))

end Finite

/-! ### The step charge of a parse is bounded independently of the cap -/

section Steps
variable {T K : Type} [DecidableEq T] [DecidableEq K] [Accepts K T]
variable {G : Grammar K} {cap : Nat} {w : Array T}

/-- Every derivation of `Xs` from `i`, by end position, out of the finite lists `F`. -/
def spans (F : List (Sym K) → List T → List (List (Tree T))) (w : Array T) (Xs : List (Sym K)) (i : Nat) :
    List (Nat × List (Tree T)) :=
  (List.range (w.size + 1)).flatMap (fun j => (F Xs (toks w i j)).map (fun us => (j, us)))

variable {F : List (Sym K) → List T → List (List (Tree T))}

theorem cands_le (hF : ∀ Xs u us, derivesAll G Xs us = true → yieldAll us = u → us ∈ F Xs u) {Xs : List (Sym K)}
    {i : Nat} {cands : List (Nat × List (Tree T))} (hn : cands.Nodup)
    (hs : ∀ c ∈ cands, c.1 ≤ w.size ∧ SpanAll G w Xs i c.1 c.2) : cands.length ≤ (spans F w Xs i).length :=
  length_le_of_nodup_subset hn (fun c hc => by
    obtain ⟨hj, hd, hy⟩ := hs c hc
    exact List.mem_flatMap.mpr ⟨c.1, List.mem_range.mpr (by omega), List.mem_map.mpr ⟨c.2, hF _ _ _ hd hy, rfl⟩⟩)

theorem ntRowGo_steps (hG : G.wf = true) (hcap : 0 < cap) {i : Nat} (hi : i < w.size)
    (hF : ∀ Xs u us, derivesAll G Xs us = true → yieldAll us = u → us ∈ F Xs u)
    {suf : Array (SufRow T)} (hsuf : ∀ p, i < p → p ≤ w.size → SufRowOk G cap w p (suf.getD p #[])) :
    ∀ (post pre : List (CRule K)) (row : NtRow T) (steps : Nat), pre ++ post = G.prepare.order →
    NtOk G cap w i (fun r => r ∈ pre.map (·.index)) row →
    (ntRowGo (accepted (termsOf G) w i) cap w i suf post row steps).2 ≤
      steps + (post.map (fun R => 1 + (spans F w R.rhs i).length)).sum
  | [], pre, row, steps, _, _ => by simp [ntRowGo]
  | R :: Rs, pre, row, steps, hpo, hrow => by
    have hRmem : R ∈ G.prepare.order := by rw [← hpo]; simp
    obtain ⟨R0, hR0, hlhs, hrhs0, _⟩ := mem_order hRmem
    have hnot : ¬ R.index ∈ pre.map (·.index) := by
      have hn := order_nodup (G := G)
      rw [← hpo, List.map_append, List.map_cons] at hn
      exact fun hm => (List.nodup_append.mp hn).2.2 _ hm _ (by simp) rfl
    have hD : ∀ r, (r ∈ pre.map (·.index) ∨ r = R.index) ↔ r ∈ (pre ++ [R]).map (·.index) := by
      intro r; simp [eq_comm]
    have hpo2 : (pre ++ [R]) ++ Rs = G.prepare.order := by rw [← hpo]; simp
    have hdone : ∀ B, (∃ rest, R.rhs = .n B :: rest) → ∀ r R1, G.rules[r]? = some R1 → R1.lhs = B →
        r ∈ pre.map (·.index) := by
      rintro B ⟨rest, hrest⟩ r R1 hr1 hl1
      have hrank := rule_head_rank hG hR0 (hrhs0.trans hrest)
      obtain ⟨R', hR', hidx, hl'⟩ := order_complete hr1
      rw [← hpo] at hR'
      rcases List.mem_append.mp hR' with h | h
      · exact List.mem_map.mpr ⟨R', h, hidx⟩
      · exfalso
        have hs := order_sorted (G := G)
        rw [← hpo] at hs
        rcases List.mem_cons.mp h with h | h
        · subst h; rw [hl', hl1] at hlhs; rw [hlhs] at hrank; omega
        · have := (List.pairwise_cons.mp (List.pairwise_append.mp hs).2.1).1 R' h
          rw [hl', hl1, ← hlhs] at this
          omega
    have hsum : ((R :: Rs).map (fun R => 1 + (spans F w R.rhs i).length)).sum =
        1 + (spans F w R.rhs i).length + (Rs.map (fun R => 1 + (spans F w R.rhs i).length)).sum := by simp
    rw [hsum]
    unfold ntRowGo
    split
    · rename_i hr
      exact absurd (hrhs0.trans hr) (rhs_ne_nil_of_mem hG hR0)
    · rename_i Y rest hr
      have hrhs : R0.rhs = Y :: rest := hrhs0.trans hr
      have hstep := fun (row2 : NtRow T) => ruleStep_ok hG hcap hi hsuf hrow hR0 hlhs hrhs hnot
        (fun B hB r R1 hr1 hl1 => hdone B ⟨rest, hB ▸ hr⟩ r R1 hr1 hl1) (row2 := row2)
      have hsz : row.size = G.rank.size := hrow.1
      have hlt : R.lhs < row.size := by rw [hsz, ← hlhs]; exact rule_lhs_lt hG hR0
      split
      · split
        · rename_i hav hnil
          have := ntRowGo_steps hG hcap hi hF hsuf Rs (pre ++ [R]) row (steps + 1) hpo2
            (NtOk.congr (hstep row rfl fun A => by rw [hnil]; split <;> simp [addAll_nil]) hD)
          omega
        · rename_i hav cands hcands
          -- the first symbol's entry is complete-or-full for all its derivations
          have hFst : BOk cap w.size (Span G w Y i) (firstAt w i row Y) := by
            match Y, hr with
            | .t a, _ => exact firstAt_term_ok hi hcap
            | .n B, hr =>
              refine BOk.congr (hrow.2 B) (fun j t _ => ⟨fun h => h.1, fun h => ⟨h, ?_⟩⟩)
              obtain ⟨r, ks, R1, rfl, hr1, hl1, _⟩ := derives_root h.1
              exact hdone B ⟨rest, hr⟩ r R1 hr1 hl1
          have hN : rest ≠ [] → ∀ j1, i < j1 → j1 ≤ w.size →
              BOk cap w.size (SpanAll G w rest j1) (sufGet suf j1 R.index 1) := by
            intro hne j1 h1 h2
            have hlen : 1 < R0.rhs.length := by
              rw [hrhs]; cases rest <;> simp_all
            have := hsuf j1 h1 h2 R.index R0 hR0 1 (Nat.le_refl _) hlen
            rwa [hrhs] at this
          obtain ⟨hca, hcn, _⟩ := combine_ok hG rfl hFst hN
          have hle := cands_le (F := F) hF hcn hca
          rw [← hrhs, hrhs0] at hle
          refine Nat.le_trans (ntRowGo_steps hG hcap hi hF hsuf Rs (pre ++ [R]) _ _ hpo2
            (NtOk.congr (hstep _ Array.size_modify fun A => by rw [getD_modify hlt]) hD)) ?_
          simp only [List.length_map]
          omega
      · rename_i hav
        have hnil := firstAt_nil_of_avail hi hRmem hr (by simpa using hav)
        have := ntRowGo_steps hG hcap hi hF hsuf Rs (pre ++ [R]) row (steps + 1) hpo2
          (NtOk.congr (hstep row rfl fun A => by
            rw [hnil]
            have : combine ([] : Bucket (Tree T)) (fun j1 => sufGet suf j1 R.index 1) rest.isEmpty = [] := by
              simp [combine]
            rw [this]; split <;> simp [addAll_nil]) hD)
        omega

/-- The symbols of a position's rule from the position on. -/
def posRhs (G : Grammar K) (p : SufPos K) : List (Sym K) := ((G.rules[p.rule]?).map (fun R => R.rhs.drop p.pos)).getD []

theorem sufPosGo_steps (hG : G.wf = true) (hcap : 0 < cap) {i : Nat} (hi : i < w.size)
    (hF : ∀ Xs u us, derivesAll G Xs us = true → yieldAll us = u → us ∈ F Xs u)
    {nt : NtRow T} (hnt : NtFull G cap w i nt)
    {suf : Array (SufRow T)} (hsuf : ∀ p, i < p → p ≤ w.size → SufRowOk G cap w p (suf.getD p #[])) :
    ∀ (ps : List (SufPos K)) (out : SufRow T) (c : Nat), (∀ p ∈ ps, ValidPos G p) →
    (sufPosGo cap w i nt suf ps out c).2 ≤ c + (ps.map (fun p => (spans F w (posRhs G p) i).length)).sum
  | [], _, c, _ => by simp [sufPosGo]
  | p :: ps, out, c, hv => by
    obtain ⟨R0, hR0, hpos, hlt, hsym, hlast⟩ := hv p (by simp)
    have hvs : ∀ q ∈ ps, ValidPos G q := fun q hq => hv q (by simp [hq])
    simp only [List.map_cons, List.sum_cons]
    unfold sufPosGo
    split
    · have := sufPosGo_steps hG hcap hi hF hnt hsuf ps out c hvs
      omega
    · have hFst : BOk cap w.size (Span G w p.sym i) (firstAt w i nt p.sym) := by
        match p.sym with
        | .t a => exact firstAt_term_ok hi hcap
        | .n B => exact hnt B
      have hN : R0.rhs.drop (p.pos + 1) ≠ [] → ∀ j1, i < j1 → j1 ≤ w.size →
          BOk cap w.size (SpanAll G w (R0.rhs.drop (p.pos + 1)) j1) (sufGet suf j1 p.rule (p.pos + 1)) := by
        intro hne j1 h1 h2
        have hlen : p.pos + 1 < R0.rhs.length := by
          rcases Nat.lt_or_ge (p.pos + 1) R0.rhs.length with h | h
          · exact h
          · exact absurd (List.drop_eq_nil_of_le h) hne
        exact hsuf j1 h1 h2 p.rule R0 hR0 (p.pos + 1) (by omega) hlen
      obtain ⟨hca, hcn, _⟩ := combine_ok hG hlast hFst hN
      have hle := cands_le (F := F) hF hcn hca
      have hd : p.sym :: R0.rhs.drop (p.pos + 1) = posRhs G p := by
        simp only [posRhs, hR0, Option.map_some, Option.getD_some, hsym]
        exact (List.drop_eq_getElem_cons hlt).symm
      rw [hd] at hle
      refine Nat.le_trans (sufPosGo_steps hG hcap hi hF hnt hsuf ps _ _ hvs) ?_
      omega

theorem sufGroups_steps (hG : G.wf = true) (hcap : 0 < cap) {i : Nat} (hi : i < w.size)
    (hF : ∀ Xs u us, derivesAll G Xs us = true → yieldAll us = u → us ∈ F Xs u)
    {nt : NtRow T} (hnt : NtFull G cap w i nt)
    {suf : Array (SufRow T)} (hsuf : ∀ p, i < p → p ≤ w.size → SufRowOk G cap w p (suf.getD p #[]))
    {on : Nat → Bool} :
    ∀ (gs : List (Nat × List (SufPos K))) (out : SufRow T) (c : Nat), (∀ kg ∈ gs, ∀ p ∈ kg.2, ValidPos G p) →
    (sufGroups cap w i nt suf on gs out c).2 ≤
      c + (gs.map (fun kg => (kg.2.map (fun p => (spans F w (posRhs G p) i).length)).sum)).sum
  | [], _, c, _ => by simp [sufGroups]
  | (k, g) :: gs, out, c, hv => by
    have hvs : ∀ kg ∈ gs, ∀ p ∈ kg.2, ValidPos G p := fun kg hkg => hv kg (by simp [hkg])
    simp only [List.map_cons, List.sum_cons]
    unfold sufGroups
    split
    · have h1 := sufPosGo_steps hG hcap hi hF hnt hsuf g out c (hv (k, g) (by simp))
      cases hq : sufPosGo cap w i nt suf g out c with
      | mk out2 c2 =>
        rw [hq] at h1
        simp only at h1 ⊢
        have := sufGroups_steps hG hcap hi hF hnt hsuf (on := on) gs out2 c2 hvs
        omega
    · have := sufGroups_steps hG hcap hi hF hnt hsuf (on := on) gs out c hvs
      omega

/-- A row's charge, bounded independently of the cap. -/
def rowB (F : List (Sym K) → List T → List (List (Tree T))) (G : Grammar K) (w : Array T) (i : Nat) : Nat :=
  let g := fun (kg : Nat × List (SufPos K)) => (kg.2.map (fun p => (spans F w (posRhs G p) i).length)).sum
  (G.prepare.order.map (fun R => 1 + (spans F w R.rhs i).length)).sum + G.prepare.positions +
    (G.prepare.byTerm.map g).sum + (G.prepare.byNt.map g).sum

theorem rowAt_steps (hG : G.wf = true) (hcap : 0 < cap) {i : Nat} (hi : i < w.size)
    (hF : ∀ Xs u us, derivesAll G Xs us = true → yieldAll us = u → us ∈ F Xs u)
    {suf : Array (SufRow T)} (hsuf : ∀ p, i < p → p ≤ w.size → SufRowOk G cap w p (suf.getD p #[])) :
    (rowAt G.prepare cap w (G.prepare.shape.map fun n => Array.replicate n []) suf i).2.2 ≤ rowB F G w i := by
  have hinit : NtOk G cap w i (fun r => r ∈ ([] : List (CRule K)).map (·.index))
      (Array.replicate G.rank.size []) := by
    refine ⟨by simp, fun A => ?_⟩
    simp only [Array.getD_eq_getD_getElem?, Array.getElem?_replicate]
    have : ∀ (j : Nat) (t : Tree T), j ≤ w.size → 0 < cap →
        ¬ (Span G w (.n A) i j t ∧ rootIn (fun r => r ∈ ([] : List (CRule K)).map (·.index)) t) := by
      intro j t _ _ h
      obtain ⟨_, h⟩ := h
      cases t <;> simp [rootIn] at h
    split <;> exact BOk.nil this
  have hnt := ntRowGo_ok (G := G) hG hcap hi hsuf G.prepare.order [] (Array.replicate G.rank.size []) 0
    (List.nil_append _) hinit
  have hs1 := ntRowGo_steps (F := F) hG hcap hi hF hsuf G.prepare.order [] (Array.replicate G.rank.size []) 0
    (List.nil_append _) hinit
  simp only [rowAt, prepare_terms, prepare_grammar]
  cases hq : ntRowGo (accepted (termsOf G) w i) cap w i suf G.prepare.order (Array.replicate G.rank.size []) 0 with
  | mk nt s1 =>
  rw [hq] at hnt hs1
  simp only at hnt hs1 ⊢
  have hfull : NtFull G cap w i nt := by
    intro A
    refine BOk.congr (hnt.2 A) (fun j t _ => ⟨fun h => h.1, fun h => ⟨h, ?_⟩⟩)
    obtain ⟨r, ks, R1, rfl, hr1, _, _⟩ := derives_root h.1
    obtain ⟨R', hR', hidx, _⟩ := order_complete hr1
    exact List.mem_map.mpr ⟨R', hR', hidx⟩
  have h1 := sufGroups_steps (F := F) hG hcap hi hF hfull hsuf (on := fun k => (accepted (termsOf G) w i).getD k false)
    G.prepare.byTerm (G.prepare.shape.map fun n => Array.replicate n []) 0 (fun kg hkg p hp => (byTerm_sym hkg hp).1)
  cases hq1 : sufGroups cap w i nt suf (fun k => (accepted (termsOf G) w i).getD k false) G.prepare.byTerm
      (G.prepare.shape.map fun n => Array.replicate n []) 0 with
  | mk o1 c1 =>
  rw [hq1] at h1
  simp only at h1 ⊢
  have h2 := sufGroups_steps (F := F) hG hcap hi hF hfull hsuf (on := fun B => !(nt.getD B []).isEmpty)
    G.prepare.byNt o1 c1 (fun kg hkg p hp => (byNt_sym hkg hp).1)
  cases hq2 : sufGroups cap w i nt suf (fun B => !(nt.getD B []).isEmpty) G.prepare.byNt o1 c1 with
  | mk o2 c2 =>
  rw [hq2] at h2
  simp only at h2 ⊢
  simp only [rowB]
  omega

theorem fill_some (hG : G.wf = true) (hcap : 0 < cap) {b : Nat}
    (hF : ∀ Xs u us, derivesAll G Xs us = true → yieldAll us = u → us ∈ F Xs u) :
    ∀ (k : Nat) (suf : Array (SufRow T)) (steps : Nat) (last : NtRow T),
    k ≤ w.size → suf.size = w.size + 1 →
    (∀ p, k ≤ p → p ≤ w.size → SufRowOk G cap w p (suf.getD p #[])) →
    steps + ((List.range k).map (rowB F G w)).sum ≤ b →
    (fill G.prepare cap w (G.prepare.shape.map fun n => Array.replicate n []) b k suf steps last).isSome
  | 0, _, _, _, _, _, _, _ => by simp [fill]
  | k + 1, suf, steps, last, hk, hsz, hsuf, hb => by
    have hrb := rowAt_steps (F := F) (cap := cap) (w := w) hG hcap (i := k) (by omega) hF (suf := suf)
      (fun p h1 h2 => hsuf p (by omega) h2)
    have hrow := rowAt_ok (G := G) (w := w) hG hcap (i := k) (by omega) (suf := suf)
      (fun p h1 h2 => hsuf p (by omega) h2)
    rw [List.range_succ, List.map_append, List.sum_append_nat] at hb
    simp only [List.map_cons, List.map_nil, List.sum_cons, List.sum_nil] at hb
    unfold fill
    simp only
    rw [if_neg (by omega)]
    refine fill_some hG hcap hF k _ _ _ (by omega) (by rw [Array.size_setIfInBounds]; exact hsz) ?_ (by omega)
    intro p h1 h2
    simp only [Array.getD_eq_getD_getElem?, Array.getElem?_setIfInBounds]
    by_cases hp : k = p
    · subst hp
      simp only [if_pos (show k < suf.size by omega)]
      exact hrow.2
    · rw [if_neg hp]
      have := hsuf p (by omega) h2
      simpa [Array.getD_eq_getD_getElem?] using this

end Steps

/-! ### (2) A cap and a budget from which the parse is complete, for every larger one -/

/-- For a well-formed grammar and a fixed sentence, there are a raw cap `N0` and a step budget `b0` such that, for
every cap `N ≥ N0` and budget `b ≥ b0`, the parse finishes within the budget and returns fewer than `N` trees: the
listing it gives is complete (`parse_complete`) and not saturated. -/
theorem parse_bounds {T K : Type} [DecidableEq T] [DecidableEq K] [Accepts K T] {G : Grammar K} (hG : G.wf = true)
    (w : Array T) : ∃ N0 b0, ∀ N b, N0 ≤ N → b0 ≤ b → ∃ ts, parse G N b w = some ts ∧ ts.length < N := by
  let F := fun Xs u => Classical.choose (finDs (T := T) hG Xs u)
  have hF : ∀ Xs u us, derivesAll G Xs us = true → yieldAll us = u → us ∈ F Xs u :=
    fun Xs u => Classical.choose_spec (finDs hG Xs u)
  obtain ⟨L, hL⟩ := finD_all hG w.toList.length (symRank G (.n G.start)) (.n G.start) w.toList
    (Nat.le_refl _) (Nat.le_refl _)
  refine ⟨L.length + 1, ((List.range w.size).map (rowB F G w)).sum, fun N b hN hb => ?_⟩
  have hsome := fill_some (cap := N) (w := w) (b := b) hG (by omega) hF w.size (Array.replicate (w.size + 1) #[]) 0 #[]
    (Nat.le_refl _) (by simp) (fun p h1 h2 => by
      have : p = w.size := by omega
      subst this
      simp only [Array.getD_eq_getD_getElem?, Array.getElem?_replicate, Nat.lt_succ_self, if_true, Option.getD_some]
      exact sufRowOk_end hG) (by omega)
  obtain ⟨res, hres⟩ := Option.isSome_iff_exists.mp hsome
  have hp : ∃ ts, parse G N b w = some ts := by
    unfold parse Prepared.parse Prepared.table
    rw [hres]
    exact ⟨_, rfl⟩
  obtain ⟨ts, hts⟩ := hp
  refine ⟨ts, hts, ?_⟩
  have := length_le_of_nodup_subset (parse_nodup hts) (fun t ht => by
    have hd := parse_sound hts ht
    exact hL t hd.1 hd.2)
  omega

end Bounds

/-! ## `read_normal` from uniqueness

(1) and (2) give `read_normal`'s conclusion for every atom whose normal form has no derivation meaning anything other
than its canonical atom. That uniqueness is spec 5.6's unambiguity argument (deliverable (3)); it is a hypothesis
here, and `VE.Acts.NormalUnique.normal_unique` proves it for every `normalOk` atom. -/

theorem read_normal_of_unique (V : Vocab) (h : framesOk V = true) (a : Atom) (ha : normalOk V a = true)
    (hu : ∀ d B c, VE.Grammar.Derives (grammar V) (.n (grammar V).start) a.normal d →
      meaning V () d = .ok (B, c, ()) → B = .one a.canon) :
    ∃ N0 b0, ∀ N b, N0 ≤ N → b0 ≤ b → read V N b a.normal.toArray = .ok (.one a.canon) := by
  have hG := grammar_wf V h
  obtain ⟨N0, b0, hb⟩ := parse_bounds hG a.normal.toArray
  refine ⟨N0, b0, fun N b hN hB => ?_⟩
  obtain ⟨ts, hts, hlen⟩ := hb N b hN hB
  have hD := normal_derived V h a ha
  unfold read
  rw [readIn_ok]
  have hall : ∀ A ∈ ts.filterMap (valueOf (meaning V)), A = .one a.canon := by
    intro A hA
    obtain ⟨t, ht, hv⟩ := List.mem_filterMap.mp hA
    obtain ⟨c, hc⟩ := valueOf_eq_some.mp hv
    exact hu t A c (VE.Grammar.parse_sound hts ht) hc
  have hmem : Act.one a.canon ∈ ts.filterMap (valueOf (meaning V)) := by
    obtain ⟨d, hd, c, hc⟩ := hD
    exact List.mem_filterMap.mpr ⟨d, VE.Grammar.parse_complete hG hts hlen (by simpa using hd),
      valueOf_eq_some.mpr ⟨c, hc⟩⟩
  have hfs : firsts (ts.filterMap (valueOf (meaning V))) = [.one a.canon] := by
    generalize ts.filterMap (valueOf (meaning V)) = l at hall hmem
    induction l with
    | nil => simp at hmem
    | cons x l ih =>
      have hx := hall x (by simp)
      subst hx
      have : (firsts l).filter (· ≠ Act.one a.canon) = [] := by
        rw [List.filter_eq_nil_iff]
        intro y hy
        simpa using hall y (by simp [mem_firsts.mp hy])
      show Act.one a.canon :: (firsts l).filter (· ≠ Act.one a.canon) = [Act.one a.canon]
      rw [this]
  unfold readingsIn listing
  rw [hts]
  simp only [show ¬ N ≤ ts.length from by omega, if_false, hfs]
  rfl

end VE.Acts.NormalProofs
