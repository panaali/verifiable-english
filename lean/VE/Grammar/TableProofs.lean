import VE.Grammar.TableInvariant

/-! The statements of the parser and the verdict (docs/spec/english-lean.md 5.4).

`parse_sound`, `parse_nodup`, `parse_length` and `verdict_many` follow from the last pass alone;
`parse_mono` and `parse_adequate` from the budget check after each row. `parse_complete`, the one hard
theorem, is proved from the cap invariant in `VE/Grammar/TableInvariant.lean`.
-/

namespace VE.Grammar

variable {X : Type}

theorem mem_dedup [DecidableEq X] {x : X} : ∀ {xs : List X}, x ∈ dedup xs ↔ x ∈ xs
  | [] => by simp [dedup]
  | y :: ys => by
    unfold dedup
    split
    · rename_i h
      rw [mem_dedup]
      constructor
      · intro hx; exact List.mem_cons_of_mem _ hx
      · intro hx
        rcases List.mem_cons.mp hx with rfl | hx
        · exact h
        · exact hx
    · simp [mem_dedup]

theorem nodup_dedup [DecidableEq X] : ∀ (xs : List X), (dedup xs).Nodup
  | [] => by simp [dedup]
  | y :: ys => by
    unfold dedup
    split
    · exact nodup_dedup ys
    · rename_i h
      refine List.nodup_cons.mpr ⟨?_, nodup_dedup ys⟩
      rw [mem_dedup]; exact h

theorem dedup_of_nodup [DecidableEq X] : ∀ {xs : List X}, xs.Nodup → dedup xs = xs
  | [], _ => by simp [dedup]
  | y :: ys, h => by
    have ⟨hy, hys⟩ := List.nodup_cons.mp h
    simp [dedup, hy, dedup_of_nodup hys]

variable {T K : Type} [DecidableEq T] [DecidableEq K] [Accepts K T]
variable {G : Grammar K} {cap b b2 : Nat} {w : Array T} {ts : List (Tree T)} {t u : Tree T}

theorem mem_finalPass {ts : List (Tree T)} :
    t ∈ finalPass G cap w ts → t ∈ ts ∧ Derives G (.n G.start) w.toList t := by
  intro h
  unfold finalPass at h
  have h1 := List.mem_of_mem_take h
  rw [mem_dedup, List.mem_filter] at h1
  simp only [Bool.and_eq_true, beq_iff_eq] at h1
  exact ⟨h1.1, h1.2.1, h1.2.2⟩

theorem finalPass_nodup {ts : List (Tree T)} : (finalPass G cap w ts).Nodup := by
  unfold finalPass
  exact (nodup_dedup _).sublist (List.take_sublist _ _)

theorem finalPass_length {ts : List (Tree T)} : (finalPass G cap w ts).length ≤ cap := by
  unfold finalPass
  simp only [List.length_take]
  omega

theorem parse_eq {ts : List (Tree T)} : parse G cap b w = some ts →
    ∃ last steps, G.prepare.table cap b w = some (last, steps) ∧
      ts = finalPass G cap w ((last.getD G.start []).get w.size) := by
  unfold parse Prepared.parse
  split
  · simp
  · rename_i last steps h
    intro e
    simp only [Option.some.injEq] at e
    exact ⟨last, steps, h, by rw [← e]; rfl⟩

theorem parse_sound : parse G cap b w = some ts → t ∈ ts → Derives G (.n G.start) w.toList t := by
  intro h ht
  obtain ⟨_, _, _, rfl⟩ := parse_eq h
  exact (mem_finalPass ht).2

theorem parse_nodup : parse G cap b w = some ts → ts.Nodup := by
  intro h
  obtain ⟨_, _, _, rfl⟩ := parse_eq h
  exact finalPass_nodup

theorem parse_length : parse G cap b w = some ts → ts.length ≤ cap := by
  intro h
  obtain ⟨_, _, _, rfl⟩ := parse_eq h
  exact finalPass_length

omit [DecidableEq T] [DecidableEq K] in
theorem fill_mono {P : Prepared K} {empty : SufRow T} : ∀ (k : Nat) (suf : Array (SufRow T)) (steps : Nat)
    (last : NtRow T) (r : NtRow T × Nat), fill P cap w empty b k suf steps last = some r → b ≤ b2 →
    fill P cap w empty b2 k suf steps last = some r
  | 0, _, _, _, _, h, _ => by simpa [fill] using h
  | k + 1, suf, steps, last, r, h, hb => by
    unfold fill at h ⊢
    simp only at h ⊢
    split at h
    · simp at h
    · rename_i hle
      rw [if_neg (by omega)]
      exact fill_mono k _ _ _ r h hb

theorem parse_mono : parse G cap b w = some ts → b ≤ b2 → parse G cap b2 w = some ts := by
  intro h hb
  unfold parse Prepared.parse at h ⊢
  unfold Prepared.table at h ⊢
  split at h
  · simp at h
  · rename_i r hr
    rw [fill_mono _ _ _ _ _ hr hb]
    exact h

omit [DecidableEq T] [DecidableEq K] in
theorem fill_adequate {P : Prepared K} {empty : SufRow T} : ∀ (k : Nat) (suf : Array (SufRow T)) (steps : Nat)
    (last : NtRow T), ∃ b0, ∀ b, b0 ≤ b → (fill P cap w empty b k suf steps last).isSome = true
  | 0, _, _, _ => ⟨0, fun _ _ => by simp [fill]⟩
  | k + 1, suf, steps, last => by
    obtain ⟨b1, h1⟩ := fill_adequate k (suf.setIfInBounds k (rowAt P cap w empty suf k).2.1)
      (steps + (rowAt P cap w empty suf k).2.2) (rowAt P cap w empty suf k).1
    refine ⟨max b1 (steps + (rowAt P cap w empty suf k).2.2), fun b hb => ?_⟩
    unfold fill
    simp only
    rw [if_neg (by omega)]
    exact h1 b (by omega)

theorem parse_adequate : G.wf = true → ∃ b0, ∀ b, b0 ≤ b → (parse G cap b w).isSome = true := by
  intro _
  obtain ⟨b0, h⟩ := fill_adequate (P := G.prepare) (cap := cap) (w := w)
    (empty := G.prepare.shape.map fun n => Array.replicate n []) w.size
    (Array.replicate (w.size + 1) #[]) 0 #[]
  refine ⟨b0, fun b hb => ?_⟩
  have := h b hb
  unfold parse Prepared.parse Prepared.table
  split
  · rename_i hn
    rw [hn] at this
    simp at this
  · simp

theorem parse_complete : G.wf = true → parse G cap b w = some ts → ts.length < cap →
    Derives G (.n G.start) w.toList t → t ∈ ts := by
  intro hG hp hl hd
  obtain ⟨last, steps, htab, rfl⟩ := parse_eq hp
  have hcap : 0 < cap := by have := finalPass_length (G := G) (cap := cap) (w := w) (ts := (last.getD G.start []).get w.size); omega
  have hn : 0 < w.size := by
    rcases Nat.eq_zero_or_pos w.size with h | h
    · exfalso
      have hy := yield_ne_nil hG hd.1
      rw [hd.2] at hy
      exact hy (by simp [Array.toList_eq_nil_iff, ← Array.size_eq_zero_iff, h])
    · exact h
  unfold Prepared.table at htab
  have hfull := fill_ok (G := G) (w := w) hG hcap w.size _ 0 #[] (last, steps) (Nat.le_refl _) (by simp)
    (fun p h1 h2 => by
      have : p = w.size := by omega
      subst this
      simp only [Array.getD_eq_getD_getElem?, Array.getElem?_replicate, Nat.lt_succ_self, if_true,
        Option.getD_some]
      exact sufRowOk_end hG) (fun h => absurd h (Nat.lt_irrefl _)) htab hn
  have hB := hfull G.start
  have hspan : ∀ u, Span G w (.n G.start) 0 w.size u ↔ Derives G (.n G.start) w.toList u := by
    intro u
    unfold Span
    rw [List.drop_zero, Nat.sub_zero, List.take_of_length_le (by simp)]
  have hfe : finalPass G cap w ((last.getD G.start []).get w.size) = (last.getD G.start []).get w.size := by
    unfold finalPass
    rw [List.filter_eq_self.mpr, dedup_of_nodup (hB.nodup _), List.take_of_length_le (hB.length _)]
    intro u hu
    have := (hspan u).mp (hB.sound _ u hu)
    simp [this.1, this.2]
  rw [hfe] at hl ⊢
  exact hB.complete w.size (Nat.le_refl _) hl t ((hspan t).mpr hd)

theorem verdict_parse {v : Verdict T} : verdict G b w = some v →
    ∃ ts, parse G 2 b w = some ts ∧
      match v with
      | .zero => ts = []
      | .one t => ts = [t]
      | .many t u => ∃ rest, ts = t :: u :: rest := by
  unfold verdict
  split <;> intro h <;> simp only [Option.some.injEq, reduceCtorEq] at h <;> subst h <;>
    rename_i ts' hp <;> exact ⟨_, hp, by simp⟩

theorem verdict_zero : G.wf = true → verdict G b w = some .zero →
    ∀ u, ¬ Derives G (.n G.start) w.toList u := by
  intro hG h u hu
  obtain ⟨ts, hp, rfl⟩ := verdict_parse h
  exact absurd (parse_complete hG hp (by simp) hu) (by simp)

theorem verdict_one : G.wf = true → verdict G b w = some (.one t) →
    Derives G (.n G.start) w.toList t ∧ ∀ u, Derives G (.n G.start) w.toList u → u = t := by
  intro hG h
  obtain ⟨ts, hp, rfl⟩ := verdict_parse h
  refine ⟨parse_sound hp (by simp), fun u hu => ?_⟩
  have := parse_complete hG hp (by simp) hu
  simpa using this

theorem verdict_many : verdict G b w = some (.many t u) →
    Derives G (.n G.start) w.toList t ∧ Derives G (.n G.start) w.toList u ∧ t ≠ u := by
  intro h
  obtain ⟨ts, hp, rest, rfl⟩ := verdict_parse h
  have hn := parse_nodup hp
  refine ⟨parse_sound hp (by simp), parse_sound hp (by simp), ?_⟩
  intro e
  subst e
  simp at hn

end VE.Grammar
