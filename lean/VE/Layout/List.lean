/-! Scope's layout (scope@0, docs/spec/scope.md 1.2 and 4.1): what the source bytes say about each unit, and the
    list run of a lead-in. The layout is read from the source bytes and each unit's span, never from the wire. -/

namespace VE.Layout

/-- A unit as the layout reads it from its own source bytes. -/
structure Unit where
  id : String
  span : Nat × Nat
  item : Option Nat      -- some d: the unit begins a list item at depth d
  midLine : Bool         -- some non-space byte precedes the unit on its line
  lead : Bool            -- its last byte that is not a space, tab, CR or LF is ":"
  label : Bool           -- it begins a list item whose text after the marker opens with a bold label ending in ":"
  para : Nat             -- the number of blank lines before the unit's first byte
  deriving DecidableEq, Repr

def sp : UInt8 := 32
def nl : UInt8 := 10
def isBlank (c : UInt8) : Bool := c == 32 || c == 9 || c == 10 || c == 13

def lineStart (b : ByteArray) : Nat → Nat
  | 0 => 0
  | k + 1 => if b.get! k == nl then k + 1 else lineStart b k

def spacesOnly (b : ByteArray) (i j : Nat) : Bool :=
  (List.range (j - i)).all (fun k => b.get! (i + k) == sp)

def skipSpaces (b : ByteArray) (i e : Nat) : Nat :=
  (((List.range (e - i)).find? (fun k => b.get! (i + k) != sp)).map (i + ·)).getD e

def isDigit (c : UInt8) : Bool := 48 ≤ c && c ≤ 57

def markerLen (b : ByteArray) (f e : Nat) : Option Nat :=
  let c := b.get! f
  if f + 1 < e && (c == 42 || c == 45 || c == 43) && b.get! (f + 1) == sp then some 2
  else
    let n := ((List.range (e - f)).find? (fun k => !isDigit (b.get! (f + k)))).getD (e - f)
    if 0 < n && f + n + 1 < e && b.get! (f + n) == 46 && b.get! (f + n + 1) == sp then some (n + 2) else none

def lastNonBlank (b : ByteArray) (s e : Nat) : Option UInt8 :=
  ((List.range (e - s)).reverse.find? (fun k => !isBlank (b.get! (s + k)))).map (fun k => b.get! (s + k))

def boldLabel (b : ByteArray) (p e : Nat) : Bool :=
  p + 1 < e && b.get! p == 42 && b.get! (p + 1) == 42 &&
  match (List.range (e - (p + 2))).find? (fun k => b.get! (p + 2 + k) == nl ||
      (b.get! (p + 2 + k) == 42 && p + 3 + k < e && b.get! (p + 3 + k) == 42)) with
  | some k => b.get! (p + 2 + k) == 42 && 0 < k &&
      (b.get! (p + 1 + k) == 58 || (p + 4 + k < e && b.get! (p + 4 + k) == 58))
  | none => false

/-- One pass over the bytes: at each position `s ≤ b.size`, the number of blank lines (a newline, then only
    spaces, tabs or CRs, then a newline) whose last newline lies before `s`. -/
def paraCounts (b : ByteArray) : Array Nat :=
  let r := b.foldl (fun (acc : Array Nat × Nat × Bool) c =>
    let (arr, cnt, blank) := acc
    let arr := arr.push cnt
    if c == nl then (arr, if blank then cnt + 1 else cnt, true)
    else if c == sp || c == 9 || c == 13 then (arr, cnt, blank)
    else (arr, cnt, false)) (#[], 0, false)
  r.1.push r.2.1

def ofSource (prose : String) (units : List (String × Nat × Nat)) : List Unit :=
  let b := prose.toUTF8
  let pc := paraCounts b
  units.map fun (id, s, e) =>
    let ls := lineStart b s
    let f := skipSpaces b s e
    let mid := !spacesOnly b ls s
    let m := if mid then none else markerLen b f e
    let item := match m with
      | some _ => if (f - ls) % 2 == 0 then some ((f - ls) / 2) else none
      | none => none
    let label := match item, m with
      | some _, some k => boldLabel b (f + k) e
      | _, _ => false
    { id, span := (s, e), item, midLine := mid, lead := lastNonBlank b s e == some 58, label,
      para := pc.getD s 0 }

def indexOf (L : List Unit) (u : String) : Option Nat := L.findIdx? (·.id == u)

def continues (d : Nat) (x : Unit) : Bool := x.item.any (d ≤ ·) || x.midLine

def runFrom (d : Nat) : List Unit → List String
  | [] => []
  | x :: xs => if continues d x then (if x.item == some d then x.id :: runFrom d xs else runFrom d xs) else []

def listRun (L : List Unit) (lead : String) : Except String (List String) :=
  match indexOf L lead with
  | none => .error s!"ScopeUnknownUnit: {lead}"
  | some i =>
    match L[i]?, L[i + 1]? with
    | some x, some y =>
      if x.lead then
        match y.item with
        | some d => .ok (runFrom d (L.drop (i + 1)))
        | none => .error s!"NotALeadIn: {lead}"
      else .error s!"NotALeadIn: {lead}"
    | _, _ => .error s!"NotALeadIn: {lead}"

/-- Independent statement of a governed item (SC-1a). -/
def GovernedItem (L : List Unit) (lead u : String) : Prop :=
  ∃ (i j d : Nat), (L[i]?).map (·.id) = some lead ∧ (L[i]?).map (·.lead) = some true ∧
    (L[i+1]?).bind (·.item) = some d ∧ i < j ∧ (L[j]?).map (·.id) = some u ∧ (L[j]?).bind (·.item) = some d ∧
    ∀ k, i < k → k < j → ∃ x, L[k]? = some x ∧ ((∃ e, x.item = some e ∧ d ≤ e) ∨ x.midLine = true)

/-! ## Theorems (spec 5.1) -/

theorem continues_iff (d : Nat) (x : Unit) :
    continues d x = true ↔ (∃ e, x.item = some e ∧ d ≤ e) ∨ x.midLine = true := by
  cases h : x.item <;> simp [continues, h]

/-- A unit is in the run of depth `d` exactly when it is an item of depth `d` and every unit before it continues. -/
theorem mem_runFrom (d : Nat) (u : String) : ∀ (M : List Unit),
    u ∈ runFrom d M ↔ ∃ (j : Nat) (x : Unit), M[j]? = some x ∧ x.id = u ∧ x.item = some d ∧
      ∀ k : Nat, k < j → ∃ y : Unit, M[k]? = some y ∧ continues d y = true
  | [] => by simp [runFrom]
  | x :: xs => by
    have ih := mem_runFrom d u xs
    have tail : (∃ (j : Nat) (y : Unit), xs[j]? = some y ∧ y.id = u ∧ y.item = some d ∧
          ∀ k, k < j → ∃ z, xs[k]? = some z ∧ continues d z = true) →
        continues d x = true → ∃ (j : Nat) (y : Unit), (x :: xs)[j]? = some y ∧ y.id = u ∧ y.item = some d ∧
          ∀ k, k < j → ∃ z, (x :: xs)[k]? = some z ∧ continues d z = true := by
      rintro ⟨j, y, hy, hu, hd, hk⟩ hc
      refine ⟨j + 1, y, by simpa using hy, hu, hd, fun k hk' => ?_⟩
      cases k with
      | zero => exact ⟨x, rfl, hc⟩
      | succ k => simpa using hk k (Nat.lt_of_succ_lt_succ hk')
    have untail : ∀ (j : Nat) (y : Unit), (x :: xs)[j + 1]? = some y → y.id = u → y.item = some d →
        (∀ k, k < j + 1 → ∃ z, (x :: xs)[k]? = some z ∧ continues d z = true) →
        ∃ (j : Nat) (y : Unit), xs[j]? = some y ∧ y.id = u ∧ y.item = some d ∧
          ∀ k, k < j → ∃ z, xs[k]? = some z ∧ continues d z = true :=
      fun j y hy hu hd hk => ⟨j, y, by simpa using hy, hu, hd, fun k hk' => by
        simpa using hk (k + 1) (Nat.succ_lt_succ hk')⟩
    by_cases hc : continues d x = true
    · by_cases hi : x.item = some d
      · simp only [runFrom, hc, hi, if_true, beq_self_eq_true, List.mem_cons, ih]
        constructor
        · rintro (rfl | h)
          · exact ⟨0, x, rfl, rfl, hi, fun k hk => absurd hk (Nat.not_lt_zero _)⟩
          · exact tail h hc
        · rintro ⟨j, y, hy, hu, hd, hk⟩
          cases j with
          | zero => simp at hy; subst hy; exact Or.inl hu.symm
          | succ j => exact Or.inr (untail j y hy hu hd hk)
      · have hne : (x.item == some d) = false := by simpa using hi
        simp only [runFrom, hc, hne, if_true, Bool.false_eq_true, if_false, ih]
        constructor
        · exact fun h => tail h hc
        · rintro ⟨j, y, hy, hu, hd, hk⟩
          cases j with
          | zero => simp at hy; subst hy; exact absurd hd hi
          | succ j => exact untail j y hy hu hd hk
    · simp only [runFrom, hc, Bool.false_eq_true, if_false, List.not_mem_nil, false_iff]
      rintro ⟨j, y, hy, _, hd, hk⟩
      cases j with
      | zero =>
        simp at hy; subst hy
        exact hc ((continues_iff d x).mpr (Or.inl ⟨d, hd, Nat.le_refl d⟩))
      | succ j =>
        obtain ⟨z, hz, hcz⟩ := hk 0 (Nat.zero_lt_succ j)
        simp at hz; subst hz; exact hc hcz

theorem indexOf_iff (L : List Unit) (hd : (L.map (·.id)).Nodup) (u : String) (i : Nat) :
    indexOf L u = some i ↔ (L[i]?).map (·.id) = some u := by
  constructor
  · intro h
    obtain ⟨hl, hp, _⟩ := List.findIdx?_eq_some_iff_getElem.mp h
    simp only [List.getElem?_eq_getElem hl, Option.map_some, Option.some.injEq]
    simpa using hp
  · intro h
    obtain ⟨x, hx, hxu⟩ := Option.map_eq_some_iff.mp h
    cases hf : indexOf L u with
    | none =>
      have := List.findIdx?_eq_none_iff.mp hf x (List.mem_of_getElem? hx)
      simp [hxu] at this
    | some j =>
      obtain ⟨hl, hp, _⟩ := List.findIdx?_eq_some_iff_getElem.mp hf
      have hj : (L.map (·.id))[j]? = (L.map (·.id))[i]? := by
        simp only [List.getElem?_map, List.getElem?_eq_getElem hl, hx, Option.map_some, hxu]
        simpa using hp
      exact congrArg some (List.getElem?_inj (by simpa using hl) hd hj)

/-- What a successful list run is made of. -/
theorem listRun_ok (L : List Unit) (lead : String) (us : List String) (h : listRun L lead = .ok us) :
    ∃ i x y d, indexOf L lead = some i ∧ L[i]? = some x ∧ L[i + 1]? = some y ∧ x.lead = true ∧
      y.item = some d ∧ us = runFrom d (L.drop (i + 1)) := by
  unfold listRun at h
  cases hi : indexOf L lead with
  | none => simp [hi] at h
  | some i =>
    cases hx : L[i]? with
    | none => simp [hi, hx] at h
    | some x =>
      cases hy : L[i + 1]? with
      | none => simp [hi, hx, hy] at h
      | some y =>
        cases hl : x.lead with
        | false => simp [hi, hx, hy, hl] at h
        | true =>
          cases hd : y.item with
          | none => simp [hi, hx, hy, hl, hd] at h
          | some d =>
            simp only [hi, hx, hy, hl, hd, if_true, Except.ok.injEq] at h
            exact ⟨i, x, y, d, rfl, hx, hy, hl, hd, h.symm⟩

theorem listRun_ok_iff (L : List Unit) (hd : (L.map (·.id)).Nodup) (lead : String) :
    (listRun L lead).isOk = true ↔
      ∃ i d, (L[i]?).map (·.id) = some lead ∧ (L[i]?).map (·.lead) = some true ∧ (L[i+1]?).bind (·.item) = some d := by
  constructor
  · intro h
    cases hr : listRun L lead with
    | error e => simp [hr, Except.isOk, Except.toBool] at h
    | ok us =>
      obtain ⟨i, x, y, d, hi, hx, hy, hl, hdy, _⟩ := listRun_ok L lead us hr
      refine ⟨i, d, (indexOf_iff L hd lead i).mp hi, by simp [hx, hl], by simp [hy, hdy]⟩
  · rintro ⟨i, d, hid, hl, hit⟩
    have hi := (indexOf_iff L hd lead i).mpr hid
    obtain ⟨x, hx, hxl⟩ := Option.map_eq_some_iff.mp hl
    obtain ⟨y, hy, hyd⟩ := Option.bind_eq_some_iff.mp hit
    simp [listRun, hi, hx, hy, hxl, hyd, Except.isOk, Except.toBool]

theorem listRun_iff (L : List Unit) (hd : (L.map (·.id)).Nodup) (lead : String) (us : List String)
    (h : listRun L lead = .ok us) (u : String) : u ∈ us ↔ GovernedItem L lead u := by
  obtain ⟨i, x, y, d, hi, hx, hy, hl, hdy, rfl⟩ := listRun_ok L lead us h
  have hid := (indexOf_iff L hd lead i).mp hi
  rw [mem_runFrom]
  constructor
  · rintro ⟨j, z, hz, hzu, hzd, hk⟩
    refine ⟨i, i + 1 + j, d, hid, by simp [hx, hl], by simp [hy, hdy], by omega, ?_, ?_, ?_⟩
    · simp only [List.getElem?_drop] at hz; simp [hz, hzu]
    · simp only [List.getElem?_drop] at hz; simp [hz, hzd]
    · intro k hik hkj
      obtain ⟨w, hw, hcw⟩ := hk (k - (i + 1)) (by omega)
      simp only [List.getElem?_drop] at hw
      rw [show i + 1 + (k - (i + 1)) = k by omega] at hw
      exact ⟨w, hw, (continues_iff d w).mp hcw⟩
  · rintro ⟨i', j, d', hid', _, hit', hij, hju, hjd, hk⟩
    have hii : i' = i := by
      have : (L.map (·.id))[i']? = (L.map (·.id))[i]? := by simp only [List.getElem?_map, hid, hid']
      have hlen : i' < (L.map (·.id)).length := by
        rcases Nat.lt_or_ge i' (L.map (·.id)).length with h' | h'
        · exact h'
        · simp [List.getElem?_eq_none (by simpa using h')] at hid'
      exact List.getElem?_inj hlen hd this
    subst hii
    have hdd : d' = d := by simp [hy, hdy] at hit'; exact hit'.symm
    subst hdd
    obtain ⟨z, hz, hzu⟩ := Option.map_eq_some_iff.mp hju
    obtain ⟨z', hz', hzd⟩ := Option.bind_eq_some_iff.mp hjd
    rw [hz] at hz'; cases hz'
    refine ⟨j - (i' + 1), z, ?_, hzu, hzd, fun k hk' => ?_⟩
    · simp only [List.getElem?_drop]; rw [show i' + 1 + (j - (i' + 1)) = j by omega]; exact hz
    · obtain ⟨w, hw, hcw⟩ := hk (i' + 1 + k) (by omega) (by omega)
      exact ⟨w, by simpa only [List.getElem?_drop] using hw, (continues_iff d' w).mpr hcw⟩

end VE.Layout
