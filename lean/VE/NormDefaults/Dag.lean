import VE.Route.Route

/-! Two facts about the shared `VE.Route.dependencyOrder` that `fill_wellFormed`
needs (docs/spec/norm-defaults.md 7, proof plan):

* `dependencyOrder_ok`: on a graph with distinct node names and no cycle, Kahn's
  search never fails and its result passes `verifyOrder`, so the order exists.
  `fill` adds sink rules and edges into them, so the precedence DAG of `T‴` is
  acyclic whenever that of `T` is, and this gives its order.
* `dependencyOrder_congr`: the order reads each node only through its name and
  its node-to-node edges, so two graphs with the same names and edges have the
  same order. `fill` adds only base predicates to the stratum DAG's mentions. -/
namespace VE.NormDefaults
open VE.Route

/-! ## Counting -/

theorem countP_lt_of {α : Type} {p q : α → Bool} : ∀ {l : List α}, (∀ x ∈ l, p x = true → q x = true) →
    (∃ x ∈ l, q x = true ∧ p x = false) → l.countP p < l.countP q
  | [], _, ⟨_, hx, _⟩ => absurd hx List.not_mem_nil
  | a :: l, hpq, ⟨x, hx, hqx, hpx⟩ => by
    rw [List.countP_cons, List.countP_cons]
    have hmono := List.countP_mono_left (l := l) (fun y hy => hpq y (List.mem_cons_of_mem _ hy))
    rcases List.mem_cons.mp hx with rfl | hx
    · simp only [hqx, hpx, if_true]
      simp only [Bool.false_eq_true, if_false]
      omega
    · have ih := countP_lt_of (fun y hy => hpq y (List.mem_cons_of_mem _ hy)) ⟨x, hx, hqx, hpx⟩
      by_cases ha : p a = true
      · simp only [ha, hpq a List.mem_cons_self ha, if_true]
        omega
      · simp only [ha, Bool.false_eq_true, if_false]
        split <;> omega

/-- A duplicate-free list drawn from `L` is no longer than `L`. -/
theorem nodup_length_le {α : Type} [DecidableEq α] : ∀ {l L : List α}, l.Nodup → (∀ x ∈ l, x ∈ L) →
    l.length ≤ L.length
  | [], _, _, _ => Nat.zero_le _
  | a :: l, L, hn, hs => by
    obtain ⟨ha, hl⟩ := List.nodup_cons.mp hn
    have haL := hs a List.mem_cons_self
    have hsub : ∀ x ∈ l, x ∈ L.erase a := fun x hx =>
      (List.mem_erase_of_ne (fun (e : x = a) => ha (e ▸ hx))).mpr (hs x (List.mem_cons_of_mem _ hx))
    have h₁ := nodup_length_le hl hsub
    rw [List.length_erase_of_mem haL] at h₁
    have h₂ : 0 < L.length := List.length_pos_of_mem haL
    simp only [List.length_cons]
    omega

theorem count_le_one_of_nodup : ∀ {l : List String}, l.Nodup → ∀ x, l.count x ≤ 1
  | [], _, x => by simp
  | a :: l, h, x => by
    obtain ⟨ha, hl⟩ := List.nodup_cons.mp h
    rw [List.count_cons]
    by_cases hax : a = x
    · subst hax; rw [List.count_eq_zero_of_not_mem ha]; simp
    · have := count_le_one_of_nodup hl x
      have : (a == x) = false := by simpa using hax
      simp [this]; omega

/-! ## Kahn's search succeeds on acyclic graphs -/

theorem smallest_mem : ∀ {l : List String} {m : String}, smallest l = some m → m ∈ l
  | [], _, h => by cases h
  | x :: xs, m, h => by
    simp only [smallest, Option.some.injEq] at h
    subst h
    suffices ∀ (acc : String) (ys : List String), ys.foldl (fun acc y => if y < acc then y else acc) acc ∈ acc :: ys by
      exact this x xs
    intro acc ys
    induction ys generalizing acc with
    | nil => exact List.mem_cons_self
    | cons y ys ih =>
      simp only [List.foldl_cons]
      split
      · exact List.mem_cons_of_mem _ (ih y)
      · rcases List.mem_cons.mp (ih acc) with h | h
        · rw [h]; exact List.mem_cons_self
        · exact List.mem_cons_of_mem _ (List.mem_cons_of_mem _ h)

theorem smallest_some {l : List String} (h : l ≠ []) : ∃ m, smallest l = some m := by
  cases l with
  | nil => exact absurd rfl h
  | cons x xs => exact ⟨_, rfl⟩

theorem mem_nodeNames {ns : List DepNode} {x : String} : x ∈ nodeNames ns ↔ ∃ n ∈ ns, n.name = x := by
  simp [nodeNames]

theorem mem_deps {ns : List DepNode} {n : DepNode} {m : String} :
    m ∈ deps ns n ↔ m ∈ n.mentions ∧ m ∈ nodeNames ns := by
  simp [deps]

/-- Nodes with the same name are equal when names are distinct. -/
theorem node_eq_of_name {ns : List DepNode} (h : (nodeNames ns).Nodup) {a b : DepNode} (ha : a ∈ ns)
    (hb : b ∈ ns) (e : a.name = b.name) : a = b := by
  induction ns with
  | nil => cases ha
  | cons c ns ih =>
    simp only [nodeNames, List.map_cons, List.nodup_cons] at h
    rcases List.mem_cons.mp ha with ha' | ha' <;> rcases List.mem_cons.mp hb with hb' | hb'
    · rw [ha', hb']
    · subst ha'
      exact absurd (e ▸ List.mem_map_of_mem (f := DepNode.name) hb') h.1
    · subst hb'
      exact absurd (e.symm ▸ List.mem_map_of_mem (f := DepNode.name) ha') h.1
    · exact ih h.2 ha' hb'

open Classical in
/-- The number of node names reachable from `a`. -/
noncomputable def reachCount (ns : List DepNode) (a : String) : Nat :=
  (nodeNames ns).countP (fun x => decide (DepPath ns a x))

theorem reachCount_lt {ns : List DepNode} (hac : DagAcyclic ns) {n : DepNode} (hn : n ∈ ns) {m : String}
    (hm : m ∈ deps ns n) : reachCount ns m < reachCount ns n.name := by
  classical
  have he : DepPath ns n.name m := .edge ⟨n, hn, rfl, hm⟩
  apply countP_lt_of
  · intro x _ hx
    simp only [decide_eq_true_eq] at hx ⊢
    exact .trans he hx
  · refine ⟨m, (mem_deps.mp hm).2, by simpa using he, by simpa using hac m⟩

/-- Every unplaced node reaches (through unplaced dependencies) a ready one. -/
theorem exists_ready {ns : List DepNode} (hac : DagAcyclic ns) (placed : List String) :
    ∀ k, ∀ n ∈ ns, reachCount ns n.name = k → n.name ∉ placed →
      ∃ r ∈ ns, r.name ∉ placed ∧ ∀ m ∈ deps ns r, m ∈ placed := by
  intro k
  induction k using Nat.strongRecOn with
  | ind k ih =>
    intro n hn hk hnp
    by_cases hall : ∀ m ∈ deps ns n, m ∈ placed
    · exact ⟨n, hn, hnp, hall⟩
    · obtain ⟨m, hm, hmp⟩ : ∃ m ∈ deps ns n, m ∉ placed := by
        apply Classical.byContradiction
        intro hno
        exact hall fun m hm => Classical.byContradiction fun hmp => hno ⟨m, hm, hmp⟩
      obtain ⟨n', hn', rfl⟩ := mem_nodeNames.mp (mem_deps.mp hm).2
      exact ih _ (hk ▸ reachCount_lt hac hn hm) n' hn' rfl hmp

/-- The placed names respect every edge: dependencies come strictly earlier. -/
def Ordered (ns : List DepNode) (placed : List String) : Prop :=
  ∀ n ∈ ns, n.name ∈ placed → ∀ m ∈ deps ns n, m ∈ placed ∧ placed.idxOf m < placed.idxOf n.name

theorem idxOf_append_left {l l' : List String} {x : String} (h : x ∈ l) :
    (l ++ l').idxOf x = l.idxOf x := by
  induction l with
  | nil => cases h
  | cons a l ih =>
    simp only [List.cons_append, List.idxOf_cons]
    by_cases hax : (a == x) = true
    · simp [hax]
    · have : x ∈ l := by
        rcases List.mem_cons.mp h with rfl | h
        · simp at hax
        · exact h
      simp only [hax, cond_false, ih this]

theorem idxOf_append_not {l : List String} {x : String} (h : x ∉ l) : (l ++ [x]).idxOf x = l.length := by
  induction l with
  | nil => simp
  | cons a l ih =>
    have hax : (a == x) = false := by
      simp only [beq_eq_false_iff_ne]
      exact fun e => h (e ▸ List.mem_cons_self)
    simp only [List.cons_append, List.idxOf_cons, hax, cond_false, List.length_cons]
    rw [ih (fun hx => h (List.mem_cons_of_mem _ hx))]

theorem idxOf_lt_of_mem {l : List String} {x : String} (h : x ∈ l) : l.idxOf x < l.length :=
  List.idxOf_lt_length_of_mem h

theorem ordered_snoc {ns : List DepNode} (hnd : (nodeNames ns).Nodup) {placed : List String}
    (ho : Ordered ns placed) {r : DepNode} (hr : r ∈ ns) (hrp : r.name ∉ placed)
    (hdeps : ∀ m ∈ deps ns r, m ∈ placed) : Ordered ns (placed ++ [r.name]) := by
  intro n hn hnm m hm
  rcases List.mem_append.mp hnm with hnm | hnm
  · obtain ⟨hmp, hlt⟩ := ho n hn hnm m hm
    refine ⟨List.mem_append_left _ hmp, ?_⟩
    rw [idxOf_append_left hmp, idxOf_append_left hnm]
    exact hlt
  · have hnr : n = r := node_eq_of_name hnd hn hr (List.mem_singleton.mp hnm)
    subst hnr
    have hmp := hdeps m hm
    refine ⟨List.mem_append_left _ hmp, ?_⟩
    rw [idxOf_append_left hmp, idxOf_append_not hrp]
    exact idxOf_lt_of_mem hmp

theorem kahn_ok {ns : List DepNode} (hnd : (nodeNames ns).Nodup) (hac : DagAcyclic ns) :
    ∀ (fuel : Nat) (placed : List String), placed.Nodup → (∀ x ∈ placed, x ∈ nodeNames ns) →
      Ordered ns placed → (nodeNames ns).length < fuel + placed.length →
      ∃ o, kahn ns fuel placed = .ok o ∧ o.Nodup ∧ (∀ x, x ∈ o ↔ x ∈ nodeNames ns) ∧ Ordered ns o
  | 0, placed, hpn, hps, _, hlen => by
    have := nodup_length_le hpn hps
    omega
  | fuel + 1, placed, hpn, hps, ho, hlen => by
    unfold kahn
    simp only
    split
    · rename_i hemp
      refine ⟨placed, rfl, hpn, fun x => ⟨hps x, fun hx => ?_⟩, ho⟩
      obtain ⟨n, hn, rfl⟩ := mem_nodeNames.mp hx
      apply Classical.byContradiction
      intro hnp
      have : n ∈ ns.filter (fun n => !placed.contains n.name) :=
        List.mem_filter.mpr ⟨hn, by simpa using hnp⟩
      rw [List.isEmpty_iff] at hemp
      rw [hemp] at this
      cases this
    · rename_i hemp
      have hne : ∃ n ∈ ns, n.name ∉ placed := by
        rw [List.isEmpty_iff] at hemp
        obtain ⟨n, hn⟩ := List.exists_mem_of_ne_nil _ hemp
        obtain ⟨hn, hnp⟩ := List.mem_filter.mp hn
        exact ⟨n, hn, by simpa using hnp⟩
      obtain ⟨n, hn, hnp⟩ := hne
      obtain ⟨r, hr, hrp, hdeps⟩ := exists_ready hac placed _ n hn rfl hnp
      have hready : r ∈ (ns.filter (fun n => !placed.contains n.name)).filter
          (fun n => (deps ns n).all placed.contains) :=
        List.mem_filter.mpr ⟨List.mem_filter.mpr ⟨hr, by simpa using hrp⟩,
          by simpa [List.all_eq_true] using hdeps⟩
      obtain ⟨m, hm⟩ := smallest_some (l := ((ns.filter (fun n => !placed.contains n.name)).filter
          (fun n => (deps ns n).all placed.contains)).map DepNode.name)
        (List.ne_nil_of_mem (List.mem_map_of_mem hready))
      rw [hm]
      simp only
      obtain ⟨r', hr', rfl⟩ := List.mem_map.mp (smallest_mem hm)
      obtain ⟨hr', hdr'⟩ := List.mem_filter.mp hr'
      obtain ⟨hr', hr'p⟩ := List.mem_filter.mp hr'
      have hr'p : r'.name ∉ placed := by simpa using hr'p
      have hdr' : ∀ m ∈ deps ns r', m ∈ placed := by simpa [List.all_eq_true] using hdr'
      apply kahn_ok hnd hac fuel
      · exact List.nodup_append.mpr ⟨hpn, List.nodup_cons.mpr ⟨by simp, List.nodup_nil⟩, fun a ha b hb e => by
          rw [List.mem_singleton.mp hb] at e; exact hr'p (e ▸ ha)⟩
      · intro x hx
        rcases List.mem_append.mp hx with hx | hx
        · exact hps x hx
        · rw [List.mem_singleton.mp hx]; exact List.mem_map_of_mem hr'
      · exact ordered_snoc hnd ho hr' hr'p hdr'
      · simp only [List.length_append, List.length_singleton]; omega

/-- `dependencyOrder_ok`: distinct names and no cycle give an order. -/
theorem dependencyOrder_ok (ns : List DepNode) (hnd : (nodeNames ns).Nodup) (hac : DagAcyclic ns) :
    ∃ o, dependencyOrder ns = .ok o := by
  obtain ⟨o, hk, hon, hmem, hord⟩ := kahn_ok hnd hac (ns.length + 1) [] List.nodup_nil
    (fun _ h => by cases h) (fun _ _ h => by cases h) (by simp [nodeNames])
  have hdup : (nodeNames ns).find? (fun n => (nodeNames ns).count n > 1) = none := by
    rw [List.find?_eq_none]
    intro x hx
    have := count_le_one_of_nodup hnd x
    simp; omega
  have hver : verifyOrder ns o = true := by
    simp only [verifyOrder, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.contains_iff_mem]
    refine ⟨⟨⟨hon, fun x hx => (hmem x).mpr hx⟩, fun x hx => (hmem x).mp hx⟩, fun n hn m hm => ?_⟩
    have hnm : n.name ∈ o := (hmem _).mpr (List.mem_map_of_mem hn)
    exact (hord n hn hnm m hm).2
  refine ⟨o, ?_⟩
  unfold dependencyOrder
  rw [hdup]
  simp only [hk, hver, if_true]

/-! ## The order reads names and edges only -/

/-- Each node's name and node-to-node edges. -/
def keyOf (ns : List DepNode) : List (String × List String) := ns.map (fun n => (n.name, deps ns n))

theorem nodeNames_keyOf (ns : List DepNode) : nodeNames ns = (keyOf ns).map Prod.fst := by
  simp [nodeNames, keyOf]

theorem filter_names (ns : List DepNode) (f : String × List String → Bool) :
    (ns.filter (fun n => f (n.name, deps ns n))).map DepNode.name = ((keyOf ns).filter f).map Prod.fst := by
  simp only [keyOf, List.filter_map, List.map_map]
  rfl

theorem kahn_congr {ns ns' : List DepNode} (h : keyOf ns = keyOf ns') :
    ∀ (fuel : Nat) (placed : List String), kahn ns fuel placed = kahn ns' fuel placed
  | 0, _ => rfl
  | fuel + 1, placed => by
    have hr : ∀ (l : List DepNode), (fun n : DepNode => !placed.contains n.name) =
        (fun n : DepNode => (fun q : String × List String => !placed.contains q.1) (n.name, deps l n)) :=
      fun _ => rfl
    have hrem : ∀ l : List DepNode, (l.filter (fun n => !placed.contains n.name)).map DepNode.name =
        ((keyOf l).filter (fun q => !placed.contains q.1)).map Prod.fst := fun l =>
      filter_names l (fun q => !placed.contains q.1)
    have hready : ∀ l : List DepNode, ((l.filter (fun n => !placed.contains n.name)).filter
        (fun n => (deps l n).all placed.contains)).map DepNode.name =
        ((keyOf l).filter (fun q => q.2.all placed.contains && !placed.contains q.1)).map Prod.fst := by
      intro l
      rw [List.filter_filter]
      exact filter_names l (fun q => q.2.all placed.contains && !placed.contains q.1)
    have hemp : ∀ l : List DepNode, (l.filter (fun n => !placed.contains n.name)).isEmpty =
        (((keyOf l).filter (fun q => !placed.contains q.1)).map Prod.fst).isEmpty := by
      intro l
      rw [← hrem l, List.isEmpty_map]
    unfold kahn
    simp only
    rw [hemp ns, hemp ns', h]
    split
    · rfl
    · rw [hready ns, hready ns', h, hrem ns, hrem ns', h]
      split
      · rfl
      · exact kahn_congr h fuel _

/-- `dependencyOrder_congr`: the same names and edges give the same order. -/
theorem dependencyOrder_congr {ns ns' : List DepNode} (h : keyOf ns = keyOf ns') :
    dependencyOrder ns = dependencyOrder ns' := by
  have hn : nodeNames ns = nodeNames ns' := by rw [nodeNames_keyOf, nodeNames_keyOf, h]
  have hlen : ns.length = ns'.length := by
    have := congrArg List.length h
    simpa [keyOf] using this
  have hver : ∀ o, verifyOrder ns o = verifyOrder ns' o := by
    intro o
    have hall : ∀ l : List DepNode, l.all (fun n => (deps l n).all (fun m => decide (o.idxOf m < o.idxOf n.name))) =
        (keyOf l).all (fun q => q.2.all (fun m => decide (o.idxOf m < o.idxOf q.1))) := by
      intro l; simp [keyOf, List.all_map]; rfl
    simp only [verifyOrder, hn, hall ns, hall ns', h]
  unfold dependencyOrder
  rw [hn, hlen, kahn_congr h]
  split
  · rfl
  · split
    · rfl
    · rw [hver]

end VE.NormDefaults
