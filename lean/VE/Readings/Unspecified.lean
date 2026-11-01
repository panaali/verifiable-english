import VE.Readings.SupWireSound
import VE.NormDefaults.Layered

/-! `fill` on a readings document and separation under the completion (docs/spec/readings-defaults.md 1.2 to 1.5 and
6.2; plan RD-1).

On the norms chain every rule is strict, so norm-defaults' `fill` can be applied to the readings document itself:
`fillDoc N` declares `unsaid__p` in the frame, places every root rule on an unspecified predicate under `F_p`, and
appends one fixed unit holding `F_p` per unspecified predicate. Taking a reading's, the free, a choice's or the
superposed document commutes with it (`fillDoc_one`, `fillDoc_free`, `fillDoc_choice`, `fillDoc_sup`), so every
theorem of S1 and S2a about `fillDoc N` is a theorem about the filled documents of norm-defaults 2.3. Separation
compares two readings on one base and one shared filling, the witness's filling respecting its `Fill_T`
(`separates_soundU`, `achievesU_iff`).

Nothing here changes a frozen file: `fillDoc` calls `fillName`, `fillNode` and `unsaidName`, restates only
`fillRoot`'s condition on readings contents, and the equalities prove it the same. -/
namespace VE.Readings
open VE.Norms (Regulated Sat envAt size restrictAll DocumentExpansion)
open VE.SoftNorms (SoftNode SoftDoc soften)
open VE.Rights (RightsDoc correlate)
open VE.Compose (Content)
universe u

/-- A readings document and its frame's `unspecified` predicates (norm-defaults 2.1), read from the environment
    before DRI ruling 4's placeholder `deny` replaced them. -/
structure NDoc where
  D : Doc
  unspec : List String

/-- A document of the route as a norm-defaults document (norm-defaults 7's `UDoc`). -/
def asU (N : NDoc) (X : RightsDoc) : VE.NormDefaults.UDoc := ⟨soften (correlate X), N.unspec⟩
def freeU (N : NDoc) : VE.NormDefaults.UDoc := asU N (free N.D).1
def oneU (N : NDoc) (s : String) (i : Nat) : VE.NormDefaults.UDoc := asU N (one N.D s i).1
def choiceU (N : NDoc) (c : Choice) : VE.NormDefaults.UDoc := asU N (choiceDoc N.D c).1
def supU (N : NDoc) : VE.NormDefaults.UDoc := asU N (sup N.D).1

/-- What the norms chain's decoder guarantees: the frame has no rule and no rights block, and every content is an
    assertion or a strict rule with no party, no exception and no `hard` flag. -/
def strictRule (M : SoftNode) : Bool :=
  M.mode == .strict && M.alterable.isEmpty && M.exception.isNone && !M.hard
def contentStrict : Content → Bool
  | .assertion _ => true
  | .norm M => strictRule M
  | _ => false
def normsShaped (D : Doc) : Bool :=
  D.chain == .norms && D.frame.soft.T.nodes.isEmpty && noRights D.frame &&
  D.items.all (fun it => match it with
    | .fixed _ c _ => contentStrict c
    | .bar _ _ => false
    | .set R => R.candidates.all (fun a => (a.content.map contentStrict).getD true))

/-! ## `fill` on the readings document (norm-defaults 2.3; 1.3 of the spec) -/

/-- `fillRoot` on a readings content: a root rule on an unspecified predicate is placed under its `F_p`. -/
def fillSoftNode (N : NDoc) (M : SoftNode) : SoftNode :=
  if M.pred ∈ N.unspec ∧ M.over = [] then { M with over := [VE.NormDefaults.fillName M.pred] } else M
def fillContent (N : NDoc) : Content → Content
  | .norm M => .norm (fillSoftNode N M)
  | c => c
def fillItem (N : NDoc) : Item → Item
  | .fixed u c cs => .fixed u (fillContent N c) cs
  | .bar u b => .bar u b
  | .set R => .set { R with candidates := R.candidates.map (fun a => { a with content := a.content.map (fillContent N) }) }
/-- A W1 node as a strict readings rule. -/
def strictNodeOf (M : VE.Norms.Node) : SoftNode :=
  { toNode := M, mode := .strict, rank := none, alterable := [], exception := none, hard := false }
/-- `F_p` for every unspecified predicate, in the frame's regulated order, each a fixed unit named by its rule. -/
def fillUnits (N : NDoc) : List Item :=
  (N.D.frame.soft.T.regulated.filter (fun r => r.name ∈ N.unspec)).map (fun r =>
    .fixed (VE.NormDefaults.fillName r.name) (.norm (strictNodeOf (VE.NormDefaults.fillNode r))) [])
/-- `E‴` on the frame: every `unsaid__p` a base predicate with `p`'s sorts (norm-defaults' `fillEnv`). -/
def fillFrameEnv (N : NDoc) : VE.Environment :=
  { N.D.frame.soft.E with predicates := fun n =>
      match N.unspec.find? (fun p => VE.NormDefaults.unsaidName p == n) with
      | some p => some (VE.SoftNorms.sortsOf N.D.frame.soft p)
      | none => N.D.frame.soft.E.predicates n }
def fillDoc (N : NDoc) : Doc :=
  { N.D with frame := { N.D.frame with soft := { N.D.frame.soft with E := fillFrameEnv N } },
             items := N.D.items.map (fillItem N) ++ fillUnits N }

/-- No unit id and no declared name begins `unsaid--` (the names `fill` adds are free; 4.1 step 2). -/
def fillNamesFree (N : NDoc) : Bool :=
  N.D.items.all (fun it => !(itemUnit it).startsWith "unsaid--" && it.names.all (fun n => !n.startsWith "unsaid--")) &&
    N.D.sets.all (fun R => (declaredBy R).all (fun n => !n.2.startsWith "unsaid--"))

/-! ## Proofs: the shape of `fillDoc` -/

/-- A candidate with its content filled, as `fillItem` fills it. -/
def fillCand (N : NDoc) (a : Candidate) : Candidate := { a with content := a.content.map (fillContent N) }
/-- A reading set with its candidates filled, as `fillItem` fills it. -/
def fillSet (N : NDoc) (R : ReadingSet) : ReadingSet := { R with candidates := R.candidates.map (fillCand N) }

theorem fillItem_set (N : NDoc) (R : ReadingSet) : fillItem N (.set R) = .set (fillSet N R) := rfl

/-- The open sets of a list of items. -/
def setsOf (l : List Item) : List ReadingSet := l.filterMap (fun | .set R => some R | _ => none)

theorem setsOf_map (N : NDoc) : ∀ l : List Item, setsOf (l.map (fillItem N)) = (setsOf l).map (fillSet N)
  | [] => rfl
  | .fixed _ _ _ :: l => setsOf_map N l
  | .bar _ _ :: l => setsOf_map N l
  | .set R :: l => congrArg (fillSet N R :: ·) (setsOf_map N l)

theorem setsOf_fillUnits (N : NDoc) : setsOf (fillUnits N) = [] := by
  simp only [setsOf, fillUnits, List.filterMap_map]
  induction (N.D.frame.soft.T.regulated.filter (fun r => r.name ∈ N.unspec)) with
  | nil => rfl
  | cons r rs ih => simp [ih]

theorem sets_fillDoc (N : NDoc) : (fillDoc N).sets = N.D.sets.map (fillSet N) := by
  show setsOf (N.D.items.map (fillItem N) ++ fillUnits N) = (setsOf N.D.items).map (fillSet N)
  simp only [setsOf, List.filterMap_append]
  rw [← setsOf, ← setsOf, setsOf_map, setsOf_fillUnits, List.append_nil]; rfl

theorem candidate_fillDoc (N : NDoc) (s : String) (i : Nat) :
    candidate (fillDoc N) s i = (candidate N.D s i).map (fillCand N) := by
  simp only [candidate, sets_fillDoc, List.find?_map]
  have : ((fun R : ReadingSet => R.id == s) ∘ fillSet N) = (fun R => R.id == s) := rfl
  rw [this]
  cases (N.D.sets.find? (·.id == s)) <;> simp [fillSet]

theorem inForce_fillDoc (N : NDoc) (n : Narrowing) : inForce (fillDoc N) n = (inForce N.D n).map (fillSet N) := by
  simp only [inForce, sets_fillDoc, List.find?_map]
  rfl

theorem labelOf_fillCand (N : NDoc) (a : Candidate) (axis : String) : labelOf (fillCand N a) axis = labelOf a axis :=
  rfl

theorem compatible_fillDoc_eq (N : NDoc) (c : Choice) : compatible (fillDoc N) c = compatible N.D c := by
  have hc : (fillDoc N).couplings = N.D.couplings := rfl
  have hn : (fillDoc N).narrowings = N.D.narrowings := rfl
  have hcomp : complete (fillDoc N) c = complete N.D c := by
    simp only [complete, sets_fillDoc, List.map_map, candidate_fillDoc, Option.isSome_map]
    rfl
  have hk : ∀ K, couplingHolds (fillDoc N) c K = couplingHolds N.D c K := by
    intro K
    simp only [couplingHolds, candidate_fillDoc]
    congr 1; funext x
    split <;> simp [Option.bind_map, Function.comp_def, labelOf_fillCand]
  have hw : ∀ n, narrowingHolds (fillDoc N) c n = narrowingHolds N.D c n := by
    intro n
    simp only [narrowingHolds, inForce_fillDoc]
    cases inForce N.D n with
    | none => rfl
    | some R =>
      have hid : (fillSet N R).id = R.id := rfl
      simp only [Option.map_some, hid]
      cases c.index R.id <;> simp [fillSet, Function.comp_def, fillCand]
  have hk' : couplingHolds (fillDoc N) c = couplingHolds N.D c := funext hk
  have hw' : narrowingHolds (fillDoc N) c = narrowingHolds N.D c := funext hw
  simp only [compatible, hcomp, hc, hn, hk', hw']

/-- The open sets, their candidates, labels, couplings and narrowings are untouched. -/
theorem compatible_fillDoc (N : NDoc) (c : Choice) : Compatible (fillDoc N) c ↔ Compatible N.D c := by
  simp only [Compatible, compatible_fillDoc_eq]

theorem fillContent_nil (N : NDoc) (h0 : N.unspec = []) (c : Content) : fillContent N c = c := by
  cases c <;> simp [fillContent, fillSoftNode, h0]

theorem fillDoc_conservative (N : NDoc) (h0 : N.unspec = []) : fillDoc N = N.D := by
  have hE : fillFrameEnv N = N.D.frame.soft.E := by
    simp only [fillFrameEnv, h0, List.find?_nil]
  have hu : fillUnits N = [] := by simp [fillUnits, h0]
  have hi : N.D.items.map (fillItem N) = N.D.items := by
    conv => rhs; rw [← List.map_id N.D.items]
    apply List.map_congr_left
    intro it _
    cases it with
    | fixed u c cs => simp [fillItem, fillContent_nil N h0]
    | bar => rfl
    | set R =>
      have : (fun a : Candidate => { a with content := a.content.map (fillContent N) }) = id := by
        have hc : fillContent N = id := funext (fillContent_nil N h0)
        funext a; simp [hc]
      simp [fillItem, this]
  simp only [fillDoc, hE, hu, hi, List.append_nil]

/-! ## Proofs: `fillNamesFree` keeps attachment -/

theorem unsaid_ascii : AsciiL "unsaid--".data := by decide

theorem fillName_unsaid (p : String) : (VE.NormDefaults.fillName p).startsWith "unsaid--" = true :=
  startsWith_append_ascii _ _ unsaid_ascii

/-- `fillNamesFree`, unpacked. -/
structure NamesFree (N : NDoc) : Prop where
  unit : ∀ it ∈ N.D.items, (itemUnit it).startsWith "unsaid--" = false
  names : ∀ it ∈ N.D.items, ∀ n ∈ it.names, n.startsWith "unsaid--" = false
  sets : ∀ R ∈ N.D.sets, ∀ n ∈ declaredBy R, n.2.startsWith "unsaid--" = false

theorem namesFree {N : NDoc} (h : fillNamesFree N = true) : NamesFree N := by
  simp only [fillNamesFree, Bool.and_eq_true, List.all_eq_true, Bool.not_eq_true'] at h
  exact ⟨fun it hit => (h.1 it hit).1, fun it hit => (h.1 it hit).2, h.2⟩

theorem NamesFree.declared {N : NDoc} (h : NamesFree N) {u : String} {c : Content}
    {cs : List (String × List String)} (hx : Item.fixed u c cs ∈ N.D.items) {m : String × String}
    (hm : m ∈ c.declared) : m.2.startsWith "unsaid--" = false :=
  h.names _ hx m.2 (List.mem_map.mpr ⟨m, hm, rfl⟩)

theorem NamesFree.fixed_unit {N : NDoc} (h : NamesFree N) {u : String} (hu : u ∈ fixedNames N.D) :
    u.startsWith "unsaid--" = false := by
  obtain ⟨⟨u', c, cs⟩, hx, he⟩ := List.mem_map.mp hu
  have := h.unit _ (mem_fixedUnits.mp hx)
  simp only [itemUnit] at this
  simp only at he
  rw [← he]; exact this

theorem mem_fillUnits {N : NDoc} {it : Item} :
    it ∈ fillUnits N ↔ ∃ r ∈ N.D.frame.soft.T.regulated, r.name ∈ N.unspec ∧
      it = .fixed (VE.NormDefaults.fillName r.name) (.norm (strictNodeOf (VE.NormDefaults.fillNode r))) [] := by
  simp only [fillUnits, List.mem_map, List.mem_filter, decide_eq_true_eq]
  constructor
  · rintro ⟨r, ⟨hr, hn⟩, rfl⟩; exact ⟨r, hr, hn, rfl⟩
  · rintro ⟨r, hr, hn, rfl⟩; exact ⟨r, ⟨hr, hn⟩, rfl⟩

theorem fixed_mem_fillDoc {N : NDoc} {u : String} {c : Content} {cs : List (String × List String)} :
    Item.fixed u c cs ∈ (fillDoc N).items ↔
      (∃ c0, Item.fixed u c0 cs ∈ N.D.items ∧ c = fillContent N c0) ∨
      ∃ r ∈ N.D.frame.soft.T.regulated, r.name ∈ N.unspec ∧ u = VE.NormDefaults.fillName r.name ∧
        c = .norm (strictNodeOf (VE.NormDefaults.fillNode r)) ∧ cs = [] := by
  show Item.fixed u c cs ∈ N.D.items.map (fillItem N) ++ fillUnits N ↔ _
  rw [List.mem_append, List.mem_map, mem_fillUnits]
  apply or_congr
  · constructor
    · rintro ⟨it, hit, he⟩
      cases it with
      | fixed u' c' cs' =>
        simp only [fillItem, Item.fixed.injEq] at he
        obtain ⟨rfl, rfl, rfl⟩ := he
        exact ⟨c', hit, rfl⟩
      | bar => simp [fillItem] at he
      | set => simp [fillItem] at he
    · rintro ⟨c0, hx, rfl⟩; exact ⟨_, hx, rfl⟩
  · constructor
    · rintro ⟨r, hr, hn, he⟩
      simp only [Item.fixed.injEq] at he
      obtain ⟨rfl, rfl, rfl⟩ := he
      exact ⟨r, hr, hn, rfl, rfl, rfl⟩
    · rintro ⟨r, hr, hn, rfl, rfl, rfl⟩; exact ⟨r, hr, hn, rfl⟩

theorem uses_fillUnit (r : Regulated) : uses (.norm (strictNodeOf (VE.NormDefaults.fillNode r))) [] = [] := rfl

theorem declared_fillContent (N : NDoc) (c : Content) : (fillContent N c).declared = c.declared := by
  cases c with
  | norm M =>
    simp only [fillContent, fillSoftNode, Content.declared]
    split <;> rfl
  | _ => rfl

theorem uses_sub_fillContent (N : NDoc) (c : Content) (cs : List (String × List String)) {n : String × String}
    (h : n ∈ uses c cs) : n ∈ uses (fillContent N c) cs := by
  cases c with
  | norm M =>
    simp only [fillContent, fillSoftNode, uses, List.mem_append] at h ⊢
    split
    · rename_i hc
      rcases h with h | h
      · simp [nodeUses, hc.2] at h
      · exact Or.inr h
    · exact h
  | _ => exact h

theorem uses_fillContent_new (N : NDoc) (c : Content) (cs : List (String × List String)) {n : String × String}
    (h : n ∈ uses (fillContent N c) cs) : n ∈ uses c cs ∨ ∃ p, n = ("rule", VE.NormDefaults.fillName p) := by
  cases c with
  | norm M =>
    simp only [fillContent, fillSoftNode, uses, List.mem_append] at h ⊢
    split at h
    · rcases h with h | h
      · simp only [nodeUses, List.map_cons, List.map_nil, List.mem_singleton] at h
        exact Or.inr ⟨_, h⟩
      · exact Or.inl (Or.inr h)
    · exact Or.inl h
  | _ => exact Or.inl h

theorem declaredBy_fillSet (N : NDoc) (R : ReadingSet) : declaredBy (fillSet N R) = declaredBy R := by
  simp only [declaredBy, fillSet]
  induction R.candidates with
  | nil => rfl
  | cons a l ih =>
    rw [List.map_cons, List.filterMap_cons, List.filterMap_cons]
    cases ha : a.content with
    | none => simp only [fillCand, ha, Option.map_none]; exact ih
    | some c =>
      simp only [fillCand, ha, Option.map_some, List.flatMap_cons, declared_fillContent]
      rw [ih]

theorem mem_sets_fillDoc {N : NDoc} {R : ReadingSet} : R ∈ (fillDoc N).sets ↔ ∃ R0 ∈ N.D.sets, R = fillSet N R0 := by
  rw [sets_fillDoc, List.mem_map]
  constructor
  · rintro ⟨R0, h, rfl⟩; exact ⟨R0, h, rfl⟩
  · rintro ⟨R0, h, rfl⟩; exact ⟨R0, h, rfl⟩

/-- Attachment in `N.D` survives the fill. -/
theorem attached_of_N {N : NDoc} {u t : String} (h : Attached N.D u t) : Attached (fillDoc N) u t := by
  induction h with
  | direct hu n hn R hR ht hd =>
    refine .direct (fixed_mem_fillDoc.mpr (Or.inl ⟨_, hu, rfl⟩)) n (uses_sub_fillContent N _ _ hn) (fillSet N R)
      (mem_sets_fillDoc.mpr ⟨R, hR, rfl⟩) ht ?_
    rw [declaredBy_fillSet]; exact hd
  | step hu hu' n hn hd _ ih =>
    refine .step (fixed_mem_fillDoc.mpr (Or.inl ⟨_, hu, rfl⟩)) (fixed_mem_fillDoc.mpr (Or.inl ⟨_, hu', rfl⟩)) n
      (uses_sub_fillContent N _ _ hn) ?_ ih
    rw [declared_fillContent]; exact hd

/-- Attachment in `fillDoc N` comes from `N.D` (review A1: needs `fillNamesFree`). -/
theorem attached_of_fill {N : NDoc} (hf : NamesFree N) {u t : String} (h : Attached (fillDoc N) u t) :
    Attached N.D u t := by
  induction h with
  | direct hu n hn R hR ht hd =>
    obtain ⟨R0, hR0, rfl⟩ := mem_sets_fillDoc.mp hR
    rw [declaredBy_fillSet] at hd
    rcases fixed_mem_fillDoc.mp hu with ⟨c0, hx, rfl⟩ | ⟨r, _, _, rfl, rfl, rfl⟩
    · rcases uses_fillContent_new N c0 _ hn with hn | ⟨p, rfl⟩
      · exact .direct hx n hn R0 hR0 ht hd
      · have := hf.sets R0 hR0 _ hd
        rw [fillName_unsaid] at this; cases this
    · rw [uses_fillUnit] at hn; cases hn
  | step hu hu' n hn hd hA ih =>
    rcases fixed_mem_fillDoc.mp hu with ⟨c0, hx, rfl⟩ | ⟨r, _, _, rfl, rfl, rfl⟩
    · rcases fixed_mem_fillDoc.mp hu' with ⟨c0', hx', rfl⟩ | ⟨r', _, _, rfl, rfl, rfl⟩
      · rw [declared_fillContent] at hd
        rcases uses_fillContent_new N c0 _ hn with hn | ⟨p, rfl⟩
        · exact .step hx hx' n hn hd ih
        · have := hf.declared hx' hd
          rw [fillName_unsaid] at this; cases this
      · obtain ⟨q, hq⟩ := attached_path_iff.mp ih
        have := hf.fixed_unit (pathTo_fixed _ hq _ List.mem_cons_self)
        rw [fillName_unsaid] at this; cases this
    · rw [uses_fillUnit] at hn; cases hn

/-- The sets a unit is attached to are the same in `fillDoc N` and `N.D`, as members. -/
theorem mem_attached_fillDoc (N : NDoc) (hf : fillNamesFree N = true) (u t : String) :
    t ∈ attached (fillDoc N) u ↔ t ∈ attached N.D u := by
  rw [attached_iff, attached_iff]
  exact ⟨attached_of_fill (namesFree hf), attached_of_N⟩

theorem all_congr_mem {l l' : List String} (h : ∀ x, x ∈ l ↔ x ∈ l') (p : String → Bool) : l.all p = l'.all p := by
  apply Bool.eq_iff_iff.mpr
  simp only [List.all_eq_true]
  exact ⟨fun hl x hx => hl x ((h x).mpr hx), fun hl x hx => hl x ((h x).mp hx)⟩

theorem isEmpty_congr_mem {l l' : List String} (h : ∀ x, x ∈ l ↔ x ∈ l') : l.isEmpty = l'.isEmpty := by
  cases l with
  | nil =>
    cases l' with
    | nil => rfl
    | cons y _ => exact absurd ((h y).mpr List.mem_cons_self) List.not_mem_nil
  | cons x _ =>
    cases l' with
    | nil => exact absurd ((h x).mp List.mem_cons_self) List.not_mem_nil
    | cons => rfl

/-- The `F_p` units are attached to no set. -/
theorem attached_fillUnit (N : NDoc) (hf : fillNamesFree N = true) (r : Regulated) :
    attached (fillDoc N) (VE.NormDefaults.fillName r.name) = [] := by
  apply List.eq_nil_iff_forall_not_mem.mpr
  intro t ht
  have hA := attached_of_fill (namesFree hf) ((attached_iff _ _ _).mp ht)
  obtain ⟨q, hq⟩ := attached_path_iff.mp hA
  have := (namesFree hf).fixed_unit (pathTo_fixed _ hq _ List.mem_cons_self)
  rw [fillName_unsaid] at this; cases this

/-! ## Proofs: building the filled document -/

/-- A built document with the frame environment `E` and every rule filled. -/
def fillX (N : NDoc) (E : VE.Environment) (X : RightsDoc) : RightsDoc :=
  { X with soft := { X.soft with E := E, T := { X.soft.T with nodes := X.soft.T.nodes.map (fillSoftNode N) } } }
/-- The rules of the `F_p` units, in their order. -/
def fillUnitNodes (N : NDoc) : List SoftNode :=
  (N.D.frame.soft.T.regulated.filter (fun r => r.name ∈ N.unspec)).map
    (fun r => strictNodeOf (VE.NormDefaults.fillNode r))
/-- `X` with rules appended. -/
def addNodes (X : RightsDoc) (ns : List SoftNode) : RightsDoc :=
  { X with soft := { X.soft with T := { X.soft.T with nodes := X.soft.T.nodes ++ ns } } }

theorem fillSoftNode_name (N : NDoc) (M : SoftNode) : (fillSoftNode N M).name = M.name := by
  unfold fillSoftNode; split <;> rfl
theorem fillSoftNode_mode (N : NDoc) (M : SoftNode) : (fillSoftNode N M).mode = M.mode := by
  unfold fillSoftNode; split <;> rfl
theorem fillSoftNode_alterable (N : NDoc) (M : SoftNode) : (fillSoftNode N M).alterable = M.alterable := by
  unfold fillSoftNode; split <;> rfl

theorem asserted_fillContent (N : NDoc) (c : Content) : asserted (fillContent N c) = asserted c := by
  cases c <;> rfl

theorem place_fillX (N : NDoc) (E : VE.Environment) (X : RightsDoc) (c : Content)
    (cs : List (String × List String)) : place (fillX N E X) (fillContent N c) cs = fillX N E (place X c cs) := by
  cases c with
  | norm M => simp [place, fillX, fillContent, fillSoftNode_name]
  | _ => rfl

theorem foldl_fillX (N : NDoc) (E : VE.Environment) (keep keep' : String → Bool)
    (pick pick' : ReadingSet → Option Candidate) : ∀ (l : List Item),
    (∀ u c cs, Item.fixed u c cs ∈ l → keep' u = keep u) → (∀ u b, Item.bar u b ∈ l → keep' u = keep u) →
    (∀ R, Item.set R ∈ l → pick' (fillSet N R) = (pick R).map (fillCand N)) →
    ∀ (X : RightsDoc) (A : List VE.Formula),
    (l.map (fillItem N)).foldl (buildStep keep' pick') (fillX N E X, A) =
      (fillX N E (l.foldl (buildStep keep pick) (X, A)).1, (l.foldl (buildStep keep pick) (X, A)).2)
  | [], _, _, _, _, _ => rfl
  | it :: l, hk, hb, hp, X, A => by
    have hk' : ∀ u c cs, Item.fixed u c cs ∈ l → keep' u = keep u :=
      fun u c cs h => hk u c cs (List.mem_cons_of_mem _ h)
    have hb' : ∀ u b, Item.bar u b ∈ l → keep' u = keep u := fun u b h => hb u b (List.mem_cons_of_mem _ h)
    have hp' : ∀ R, Item.set R ∈ l → pick' (fillSet N R) = (pick R).map (fillCand N) :=
      fun R h => hp R (List.mem_cons_of_mem _ h)
    have ih := foldl_fillX N E keep keep' pick pick' l hk' hb' hp'
    simp only [List.map_cons, List.foldl_cons]
    cases it with
    | fixed u c cs =>
      have := hk u c cs List.mem_cons_self
      simp only [fillItem, buildStep, this]
      split
      · rw [place_fillX, asserted_fillContent]; exact ih _ _
      · exact ih _ _
    | bar u b =>
      have := hb u b List.mem_cons_self
      simp only [fillItem, buildStep, this]
      split
      · exact ih { X with bars := X.bars ++ [b] } A
      · exact ih _ _
    | set R =>
      rw [fillItem_set]
      simp only [buildStep, hp R List.mem_cons_self]
      cases hR : pick R with
      | none => exact ih _ _
      | some a =>
        cases ha : a.content with
        | none => simp only [Option.map_some, Option.bind_some, fillCand, ha, Option.map_none]; exact ih _ _
        | some c =>
          simp only [Option.map_some, Option.bind_some, fillCand, ha]
          rw [place_fillX, asserted_fillContent]; exact ih _ _

theorem foldl_fillUnits_gen (keep' : String → Bool) (pick' : ReadingSet → Option Candidate) :
    ∀ (rs : List Regulated), (∀ r ∈ rs, keep' (VE.NormDefaults.fillName r.name) = true) →
    ∀ (Y : RightsDoc) (A : List VE.Formula),
    (rs.map (fun r => Item.fixed (VE.NormDefaults.fillName r.name)
        (.norm (strictNodeOf (VE.NormDefaults.fillNode r))) [])).foldl (buildStep keep' pick') (Y, A) =
      (addNodes Y (rs.map (fun r => strictNodeOf (VE.NormDefaults.fillNode r))), A)
  | [], _, Y, A => by simp [addNodes]
  | r :: rs, hk, Y, A => by
    simp only [List.map_cons, List.foldl_cons, buildStep, hk r List.mem_cons_self, if_true]
    rw [foldl_fillUnits_gen keep' pick' rs (fun r' h => hk r' (List.mem_cons_of_mem _ h))]
    simp [addNodes, place, asserted]

theorem frame_fillDoc (N : NDoc) (h0 : N.D.frame.soft.T.nodes = []) :
    (fillDoc N).frame = fillX N (fillFrameEnv N) N.D.frame := by
  simp only [fillDoc, fillX, h0, List.map_nil]
  rw [← h0]

/-- Building the filled document is building the author's document, then filling: the frame's environment
    becomes `E‴`, every rule is filled, and the `F_p` rules come last. -/
theorem build_fillDoc (N : NDoc) (h0 : N.D.frame.soft.T.nodes = []) (keep keep' : String → Bool)
    (pick pick' : ReadingSet → Option Candidate)
    (hk : ∀ u c cs, Item.fixed u c cs ∈ N.D.items → keep' u = keep u)
    (hb : ∀ u b, Item.bar u b ∈ N.D.items → keep' u = keep u)
    (hp : ∀ R, Item.set R ∈ N.D.items → pick' (fillSet N R) = (pick R).map (fillCand N))
    (hu : ∀ r ∈ N.D.frame.soft.T.regulated, r.name ∈ N.unspec → keep' (VE.NormDefaults.fillName r.name) = true) :
    build (fillDoc N) keep' pick' =
      (addNodes (fillX N (fillFrameEnv N) (build N.D keep pick).1) (fillUnitNodes N), (build N.D keep pick).2) := by
  rw [build_eq, build_eq]
  show (N.D.items.map (fillItem N) ++ fillUnits N).foldl _ ((fillDoc N).frame, []) = _
  rw [List.foldl_append, frame_fillDoc N h0, foldl_fillX N _ keep keep' pick pick' _ hk hb hp]
  unfold fillUnits fillUnitNodes
  rw [foldl_fillUnits_gen keep' pick' _ (fun r h => by
    simp only [List.mem_filter, decide_eq_true_eq] at h
    exact hu r h.1 h.2)]

/-! ## Proofs: `soften` on strict documents -/

/-- Every rule strict and unswitchable. -/
def StrictNodes (S : SoftDoc) : Prop := ∀ M ∈ S.T.nodes, M.mode = .strict ∧ M.alterable = []

/-- `soften_hard_identity` without its unused well-formedness hypothesis (SoftNorms is frozen). -/
theorem decisions_strict (S : SoftDoc) (hh : StrictNodes S) : VE.SoftNorms.decisions S = [] := by
  have hcp : VE.SoftNorms.collidingPairs S = [] := by
    cases hc : VE.SoftNorms.collidingPairs S with
    | nil => rfl
    | cons x xs =>
      have hx : (x.1, x.2) ∈ VE.SoftNorms.collidingPairs S := by rw [hc]; exact List.mem_cons_self
      obtain ⟨hM, _, hd, _⟩ := VE.SoftNorms.mem_collidingPairs.mp hx
      rw [(hh _ hM).1] at hd
      cases hd
  simp only [VE.SoftNorms.decisions, VE.SoftNorms.exceptedDecisions, VE.SoftNorms.offDecisions,
    VE.SoftNorms.outweighsDecisions, VE.SoftNorms.outweighsTriples, hcp,
    List.append_eq_nil_iff, List.map_eq_nil_iff, List.filter_eq_nil_iff, List.flatMap_eq_nil_iff]
  refine ⟨⟨fun N hN => by simp [(hh N hN).1], fun N hN => by simp [(hh N hN).2]⟩, ?_⟩
  split <;> rfl

theorem soften_strict (S : SoftDoc) (hh : StrictNodes S) :
    soften S = ⟨S.E, S.lits, ⟨S.T.regulated, S.T.definitions, S.T.nodes.map SoftNode.toNode⟩⟩ := by
  have hE := VE.SoftNorms.envPrime_of_no_decisions S (decisions_strict S hh)
  simp only [soften, hE, VE.Norms.Doc.mk.injEq, VE.Norms.Tree.mk.injEq, true_and, List.map_inj_left]
  intro M hM
  simp [VE.SoftNorms.primeNode, VE.SoftNorms.derivedList, (hh M hM).1, (hh M hM).2]

theorem strictNodes_fill (N : NDoc) (E : VE.Environment) (X : RightsDoc) (hh : StrictNodes X.soft) :
    StrictNodes (addNodes (fillX N E X) (fillUnitNodes N)).soft := by
  intro M hM
  simp only [addNodes, fillX, List.mem_append, List.mem_map, fillUnitNodes] at hM
  rcases hM with ⟨M0, hM0, rfl⟩ | ⟨r, _, rfl⟩
  · rw [fillSoftNode_mode, fillSoftNode_alterable]; exact hh M0 hM0
  · exact ⟨rfl, rfl⟩

theorem noRights_fill (N : NDoc) (E : VE.Environment) (X : RightsDoc) :
    noRights (addNodes (fillX N E X) (fillUnitNodes N)) = noRights X := rfl

/-- `F_p` and `fillRoot` read on the readings rules. -/
theorem fillSoftNode_toNode (N : NDoc) (U : VE.NormDefaults.UDoc) (hU : U.unspec = N.unspec) (M : SoftNode) :
    (fillSoftNode N M).toNode = VE.NormDefaults.fillRoot U M.toNode := by
  unfold fillSoftNode VE.NormDefaults.fillRoot
  rw [hU]
  split <;> rfl

/-- The filled built document, softened, is `fill` of the softened built document. -/
theorem soften_fill (N : NDoc) (X : RightsDoc) (hX : noRights X = true) (hh : StrictNodes X.soft)
    (hreg : X.soft.T.regulated = N.D.frame.soft.T.regulated) (E : VE.Environment)
    (hE : E = VE.NormDefaults.fillEnv ⟨soften (correlate X), N.unspec⟩) :
    soften (correlate (addNodes (fillX N E X) (fillUnitNodes N))) =
      VE.NormDefaults.fill ⟨soften (correlate X), N.unspec⟩ := by
  have hX' : noRights (addNodes (fillX N E X) (fillUnitNodes N)) = true := by rw [noRights_fill]; exact hX
  have hh' := strictNodes_fill N E X hh
  rw [(correlate_noRights _ hX').1, soften_strict _ hh']
  rw [(correlate_noRights _ hX).1] at hE ⊢
  rw [soften_strict _ hh] at hE ⊢
  subst hE
  simp only [VE.NormDefaults.fill, VE.NormDefaults.fillTree, VE.NormDefaults.fillNodes, addNodes, fillX,
    VE.Norms.Doc.mk.injEq, VE.Norms.Tree.mk.injEq, true_and, List.map_append, List.map_map]
  congr 1
  · apply List.map_congr_left
    intro M _
    exact fillSoftNode_toNode N _ rfl M
  · rw [hreg]; simp [fillUnitNodes, List.map_map, Function.comp_def, strictNodeOf]

/-- `E‴` on the frame is `fillEnv` of a built document that keeps the frame. -/
theorem fillFrameEnv_eq (N : NDoc) (X : RightsDoc) (hX : noRights X = true) (hh : StrictNodes X.soft)
    (hk : KeepsFrame N.D X) : fillFrameEnv N = VE.NormDefaults.fillEnv ⟨soften (correlate X), N.unspec⟩ := by
  rw [(correlate_noRights _ hX).1, soften_strict _ hh]
  simp only [fillFrameEnv, VE.NormDefaults.fillEnv, hk.E]
  congr 1
  funext n
  cases h : N.unspec.find? (fun p => VE.NormDefaults.unsaidName p == n) <;>
    simp [VE.NormDefaults.sortsOf, VE.SoftNorms.sortsOf, VE.SoftNorms.sortsIn, hk.regulated]

/-! ## Proofs: the norms chain's shape -/

/-- `normsShaped`, unpacked. -/
structure Shaped (D : Doc) : Prop where
  nodes : D.frame.soft.T.nodes = []
  frame : noRights D.frame = true
  fixed : ∀ u c cs, Item.fixed u c cs ∈ D.items → contentStrict c = true
  bar : ∀ u b, Item.bar u b ∉ D.items
  set : ∀ R, Item.set R ∈ D.items → ∀ a ∈ R.candidates, ∀ c, a.content = some c → contentStrict c = true

theorem shaped {D : Doc} (h : normsShaped D = true) : Shaped D := by
  simp only [normsShaped, Bool.and_eq_true, List.isEmpty_iff, List.all_eq_true] at h
  obtain ⟨⟨⟨_, hn⟩, hr⟩, hi⟩ := h
  refine ⟨hn, hr, fun u c cs hx => hi _ hx, fun u b hx => by simpa using hi _ hx, fun R hx a ha c hc => ?_⟩
  have := hi _ hx
  simp only [List.all_eq_true] at this
  simpa [hc] using this a ha

/-- No rights content and every rule strict. -/
def StrictDoc (X : RightsDoc) : Prop := noRights X = true ∧ StrictNodes X.soft

theorem place_strict (X : RightsDoc) (c : Content) (cs : List (String × List String)) (hX : StrictDoc X)
    (hc : contentStrict c = true) : StrictDoc (place X c cs) := by
  cases c with
  | assertion => exact hX
  | norm M =>
    simp only [contentStrict, strictRule, Bool.and_eq_true, beq_iff_eq, List.isEmpty_iff] at hc
    refine ⟨hX.1, fun M' hM' => ?_⟩
    simp only [place, List.mem_append, List.mem_singleton] at hM'
    rcases hM' with h | rfl
    · exact hX.2 M' h
    · exact ⟨hc.1.1.1, hc.1.1.2⟩
  | _ => simp [contentStrict] at hc

theorem build_strict (D : Doc) (hs : Shaped D) (keep : String → Bool) (pick : ReadingSet → Option Candidate)
    (hp : ∀ R a, pick R = some a → a ∈ R.candidates) : StrictDoc (build D keep pick).1 := by
  rw [build_eq]
  suffices ∀ (l : List Item), (∀ it ∈ l, it ∈ D.items) → ∀ acc : RightsDoc × List VE.Formula, StrictDoc acc.1 →
      StrictDoc (l.foldl (buildStep keep pick) acc).1 from
    this D.items (fun _ h => h) _ ⟨hs.frame, by rw [StrictNodes, hs.nodes]; simp⟩
  intro l
  induction l with
  | nil => intro _ acc h; exact h
  | cons it l ih =>
    intro hl acc h
    apply ih (fun x hx => hl x (List.mem_cons_of_mem _ hx))
    have hit := hl it List.mem_cons_self
    cases it with
    | fixed u c cs =>
      simp only [buildStep]
      split
      · exact place_strict _ c cs h (hs.fixed u c cs hit)
      · exact h
    | bar u b => exact absurd hit (hs.bar u b)
    | set R =>
      simp only [buildStep]
      cases hR : pick R with
      | none => exact h
      | some a =>
        cases ha : a.content with
        | none => simp only [Option.bind_some, ha, Option.map_none]; exact h
        | some c =>
          simp only [Option.bind_some, ha, Option.map_some]
          exact place_strict _ c _ h (hs.set R hit a (hp R a hR) c ha)

/-- The equality for any `keep` and `pick` that agree on the two documents. -/
theorem soften_build_fillDoc (N : NDoc) (hn : normsShaped N.D = true) (keep keep' : String → Bool)
    (pick pick' : ReadingSet → Option Candidate) (hpc : ∀ R a, pick R = some a → a ∈ R.candidates)
    (hk : ∀ u, keep' u = keep u)
    (hp : ∀ R, Item.set R ∈ N.D.items → pick' (fillSet N R) = (pick R).map (fillCand N))
    (hu : ∀ r ∈ N.D.frame.soft.T.regulated, r.name ∈ N.unspec → keep' (VE.NormDefaults.fillName r.name) = true) :
    soften (correlate (build (fillDoc N) keep' pick').1) =
        VE.NormDefaults.fill ⟨soften (correlate (build N.D keep pick).1), N.unspec⟩ ∧
      (build (fillDoc N) keep' pick').2 = (build N.D keep pick).2 := by
  have hs := shaped hn
  rw [build_fillDoc N hs.nodes keep keep' pick pick' (fun u _ _ _ => hk u) (fun u _ _ => hk u) hp hu]
  have hX := build_strict N.D hs keep pick hpc
  exact ⟨soften_fill N _ hX.1 hX.2 (keepsFrame_build N.D keep pick).regulated _
    (fillFrameEnv_eq N _ hX.1 hX.2 (keepsFrame_build N.D keep pick)), rfl⟩

theorem candidates_fillSet (N : NDoc) (R : ReadingSet) (i : Nat) :
    (fillSet N R).candidates[i]? = R.candidates[i]?.map (fillCand N) := by
  simp [fillSet]

/-- Taking a reading's, the free, a choice's or the superposed document commutes with `fill` (review A1: each
    needs `fillNamesFree`; F-ND5). -/
theorem fillDoc_one (N : NDoc) (hn : normsShaped N.D = true) (hf : fillNamesFree N = true) (s : String) (i : Nat) :
    soften (correlate (one (fillDoc N) s i).1) = VE.NormDefaults.fill (oneU N s i) ∧
      (one (fillDoc N) s i).2 = (one N.D s i).2 :=
  soften_build_fillDoc N hn _ _ _ _
    (fun R a h => by
      by_cases hs : (R.id == s) = true
      · rw [if_pos hs] at h; exact List.mem_of_getElem? h
      · rw [if_neg hs] at h; cases h)
    (fun u => all_congr_mem (mem_attached_fillDoc N hf u) _)
    (fun R _ => by
      show (if R.id == s then (fillSet N R).candidates[i]? else none) = _
      rw [candidates_fillSet]; split <;> rfl)
    (fun r _ _ => by rw [attached_fillUnit N hf r]; rfl)

theorem fillDoc_free (N : NDoc) (hn : normsShaped N.D = true) (hf : fillNamesFree N = true) :
    soften (correlate (free (fillDoc N)).1) = VE.NormDefaults.fill (freeU N) ∧ (free (fillDoc N)).2 = (free N.D).2 :=
  soften_build_fillDoc N hn _ _ _ _ (fun _ _ h => by cases h)
    (fun u => isEmpty_congr_mem (mem_attached_fillDoc N hf u)) (fun _ _ => rfl)
    (fun r _ _ => by rw [attached_fillUnit N hf r]; rfl)

-- `hf` is the approved statement's; this equality does not need it (`choiceDoc` keeps every fixed unit).
set_option linter.unusedVariables false in
theorem fillDoc_choice (N : NDoc) (hn : normsShaped N.D = true) (hf : fillNamesFree N = true) (c : Choice) :
    soften (correlate (choiceDoc (fillDoc N) c).1) = VE.NormDefaults.fill (choiceU N c) ∧
      (choiceDoc (fillDoc N) c).2 = (choiceDoc N.D c).2 :=
  soften_build_fillDoc N hn _ _ _ _
    (fun R a h => by
      change (c.index R.id).bind (R.candidates[·]?) = some a at h
      cases hc : c.index R.id with
      | none => rw [hc] at h; cases h
      | some k => rw [hc] at h; exact List.mem_of_getElem? h)
    (fun _ => rfl)
    (fun R _ => by
      show ((c.index R.id).bind ((fillSet N R).candidates[·]?)) = _
      cases c.index R.id <;> simp [candidates_fillSet])
    (fun _ _ _ => rfl)

/-! ## Proofs: the superposed document -/

theorem setSize_fillDoc (N : NDoc) (m : Nat) : setSize (fillDoc N) m = setSize N.D m := by
  simp only [setSize, sets_fillDoc, List.getElem?_map]
  cases N.D.sets[m]? <;> simp [fillSet]

theorem position_fillDoc (N : NDoc) (m i : Nat) : position (fillDoc N) m i = position N.D m i := by
  simp [position, sets_fillDoc, ← List.map_take, List.map_map, Function.comp_def, fillSet]

theorem interfaceOf_fillSet (N : NDoc) (R : ReadingSet) : interfaceOf (fillSet N R) = interfaceOf R := by
  simp only [interfaceOf, declaredBy_fillSet]
  congr 1
  funext n
  simp only [fillSet, List.all_map, Function.comp_def, fillCand, Option.map_map, declared_fillContent]

theorem copies_fillDoc (N : NDoc) : copies (fillDoc N) = copies N.D := by
  funext n
  simp only [copies, sets_fillDoc, List.findIdx?_map, Function.comp_def, interfaceOf_fillSet, setSize_fillDoc,
    position_fillDoc]

theorem copyCites_fillDoc (N : NDoc) : copyCites (fillDoc N) = copyCites N.D := by
  funext cs; simp only [copyCites, copies_fillDoc]

theorem copyContent_fillDoc (N : NDoc) : copyContent (fillDoc N) = copyContent N.D := by
  funext c; cases c <;> simp only [copyContent, copyOver, copies_fillDoc]

theorem gateContent_fillDoc (N : NDoc) : gateContent (fillDoc N) = gateContent N.D := by
  funext m i c; cases c <;> simp only [gateContent, setSize_fillDoc, position_fillDoc]

theorem bitDecls_fillDoc (N : NDoc) : bitDecls (fillDoc N) = bitDecls N.D := by
  simp only [bitDecls, sets_fillDoc, List.length_map, setSize_fillDoc]

theorem choiceEnv_fillDoc (N : NDoc) (E : VE.Environment) : choiceEnv (fillDoc N) E = choiceEnv N.D E := by
  simp only [choiceEnv, sets_fillDoc, List.isEmpty_map, bitDecls_fillDoc]

/-- An interface name has a copy per candidate of its set, and a fixed name itself: never none. -/
theorem copies_ne_nil (D : Doc) (n : String) : copies D n ≠ [] := by
  unfold copies
  split
  · rename_i m hm
    obtain ⟨hlt, hp, _⟩ := List.findIdx?_eq_some_iff_getElem.mp hm
    have hpos : 0 < setSize D m := by
      simp only [setSize, List.getElem?_eq_getElem hlt, Option.map_some, Option.getD_some]
      simp only [List.contains_iff_mem] at hp
      have hd : ("rule", n) ∈ declaredBy D.sets[m] := (List.mem_filter.mp hp).1
      cases hc : D.sets[m].candidates with
      | nil => simp [declaredBy, hc] at hd
      | cons _ _ => simp
    simp only [ne_eq, List.map_eq_nil_iff, List.range_eq_nil]
    omega
  · simp

/-- The name `fill` adds is no set's interface name, so `sup` does not expand it (review A1). -/
theorem copies_fillName {N : NDoc} (hf : NamesFree N) (p : String) :
    copies N.D (VE.NormDefaults.fillName p) = [VE.NormDefaults.fillName p] := by
  unfold copies
  rw [List.findIdx?_eq_none_iff.mpr]
  intro R hR
  cases h : (interfaceOf R).contains ("rule", VE.NormDefaults.fillName p) with
  | false => rfl
  | true =>
    simp only [List.contains_iff_mem] at h
    have := hf.sets R hR _ (List.mem_filter.mp h).1
    rw [fillName_unsaid] at this; cases this

theorem copyContent_fill {N : NDoc} (hf : NamesFree N) (c : Content) :
    copyContent N.D (fillContent N c) = fillContent N (copyContent N.D c) := by
  cases c with
  | norm M =>
    simp only [copyContent, fillContent, copyOver, fillSoftNode]
    by_cases h : M.pred ∈ N.unspec ∧ M.over = []
    · have h' : M.pred ∈ N.unspec ∧ M.over.flatMap (copies N.D) = [] := ⟨h.1, by rw [h.2]; rfl⟩
      rw [if_pos h, if_pos h']
      simp [copies_fillName hf]
    · have h' : ¬ (M.pred ∈ N.unspec ∧ M.over.flatMap (copies N.D) = []) := by
        rintro ⟨h1, h2⟩
        apply h
        refine ⟨h1, List.eq_nil_iff_forall_not_mem.mpr fun x hx => ?_⟩
        exact copies_ne_nil N.D x (List.flatMap_eq_nil_iff.mp h2 x hx)
      rw [if_neg h, if_neg h']
  | _ => rfl

theorem gateContent_fill (N : NDoc) (D : Doc) (m i : Nat) (c : Content) :
    gateContent D m i (fillContent N c) = fillContent N (gateContent D m i c) := by
  cases c with
  | norm M =>
    simp only [gateContent, fillContent, fillSoftNode]
    by_cases h : M.pred ∈ N.unspec ∧ M.over = [] <;> simp [h]
  | _ => rfl

/-- One candidate of `sup`'s set step. -/
def candStep (D : Doc) (k : Nat) (R : ReadingSet) (acc : RightsDoc × List VE.Formula) (i : Nat) :
    RightsDoc × List VE.Formula :=
  match R.candidates[i]?.bind (fun a => a.content.map (fun c => (c, a.cites))) with
  | some (c, cs) => (place acc.1 (gateContent D k i c) cs, acc.2 ++ asserted (gateContent D k i c))
  | none => acc

theorem supStep_set (D : Doc) (acc : (RightsDoc × List VE.Formula) × Nat) (R : ReadingSet) :
    supStep D acc (.set R) = ((List.range R.candidates.length).foldl (candStep D acc.2 R) acc.1, acc.2 + 1) := rfl

theorem candStep_fill (N : NDoc) (E : VE.Environment) (k : Nat) (R : ReadingSet) (X : RightsDoc)
    (A : List VE.Formula) (i : Nat) :
    candStep (fillDoc N) k (fillSet N R) (fillX N E X, A) i =
      (fillX N E (candStep N.D k R (X, A) i).1, (candStep N.D k R (X, A) i).2) := by
  unfold candStep
  rw [candidates_fillSet, gateContent_fillDoc]
  cases R.candidates[i]? with
  | none => rfl
  | some a =>
    cases ha : a.content with
    | none => simp [fillCand, ha]
    | some c => simp [fillCand, ha, gateContent_fill, place_fillX, asserted_fillContent]

theorem foldl_candStep_fill (N : NDoc) (E : VE.Environment) (k : Nat) (R : ReadingSet) : ∀ (is : List Nat)
    (X : RightsDoc) (A : List VE.Formula),
    is.foldl (candStep (fillDoc N) k (fillSet N R)) (fillX N E X, A) =
      (fillX N E (is.foldl (candStep N.D k R) (X, A)).1, (is.foldl (candStep N.D k R) (X, A)).2)
  | [], _, _ => rfl
  | i :: is, X, A => by
    simp only [List.foldl_cons, candStep_fill]
    exact foldl_candStep_fill N E k R is _ _

theorem foldl_sup_fillX {N : NDoc} (hf : NamesFree N) (E : VE.Environment) : ∀ (l : List Item) (X : RightsDoc)
    (A : List VE.Formula) (k : Nat),
    (l.map (fillItem N)).foldl (supStep (fillDoc N)) ((fillX N E X, A), k) =
      ((fillX N E (l.foldl (supStep N.D) ((X, A), k)).1.1, (l.foldl (supStep N.D) ((X, A), k)).1.2),
        (l.foldl (supStep N.D) ((X, A), k)).2)
  | [], _, _, _ => rfl
  | it :: l, X, A, k => by
    simp only [List.map_cons, List.foldl_cons]
    cases it with
    | fixed u c cs =>
      simp only [fillItem, supStep, copyContent_fillDoc, copyCites_fillDoc, copyContent_fill hf, place_fillX,
        asserted_fillContent]
      exact foldl_sup_fillX hf E l _ _ _
    | bar u b => exact foldl_sup_fillX hf E l { X with bars := X.bars ++ [b] } A k
    | set R =>
      rw [fillItem_set, supStep_set, supStep_set]
      have hl : (fillSet N R).candidates.length = R.candidates.length := by simp [fillSet]
      simp only [hl]
      rw [foldl_candStep_fill]
      exact foldl_sup_fillX hf E l _ _ _

theorem foldl_sup_fillUnits (N : NDoc) : ∀ (rs : List Regulated) (Y : RightsDoc) (A : List VE.Formula) (k : Nat),
    (rs.map (fun r => Item.fixed (VE.NormDefaults.fillName r.name)
        (.norm (strictNodeOf (VE.NormDefaults.fillNode r))) [])).foldl (supStep (fillDoc N)) ((Y, A), k) =
      ((addNodes Y (rs.map (fun r => strictNodeOf (VE.NormDefaults.fillNode r))), A), k)
  | [], Y, A, k => by simp [addNodes]
  | r :: rs, Y, A, k => by
    simp only [List.map_cons, List.foldl_cons]
    rw [show supStep (fillDoc N) ((Y, A), k) (Item.fixed (VE.NormDefaults.fillName r.name)
        (.norm (strictNodeOf (VE.NormDefaults.fillNode r))) []) =
        ((addNodes Y [strictNodeOf (VE.NormDefaults.fillNode r)], A), k) by
      simp [supStep, copyContent, copyOver, copyCites, place, addNodes, asserted, strictNodeOf,
        VE.NormDefaults.fillNode]]
    rw [foldl_sup_fillUnits N rs]
    simp [addNodes]

theorem supFrame_fillDoc (N : NDoc) (h0 : N.D.frame.soft.T.nodes = []) :
    supFrame (fillDoc N) = fillX N (choiceEnv N.D (fillFrameEnv N)) (supFrame N.D) := by
  rw [supFrame, supFrame, choiceEnv_fillDoc]
  simp only [fillDoc, fillX, h0, List.map_nil]
  rw [← h0]

theorem sup_fillDoc (N : NDoc) (hf : NamesFree N) (h0 : N.D.frame.soft.T.nodes = []) :
    sup (fillDoc N) = (addNodes (fillX N (choiceEnv N.D (fillFrameEnv N)) (sup N.D).1) (fillUnitNodes N),
      (sup N.D).2) := by
  rw [sup_eq, sup_eq]
  show ((N.D.items.map (fillItem N) ++ fillUnits N).foldl _ ((supFrame (fillDoc N), []), 0)).1 = _
  rw [List.foldl_append, supFrame_fillDoc N h0, foldl_sup_fillX hf]
  unfold fillUnits fillUnitNodes
  rw [foldl_sup_fillUnits]

theorem contentStrict_copy (D : Doc) (c : Content) : contentStrict (copyContent D c) = contentStrict c := by
  cases c <;> rfl

theorem contentStrict_gate (D : Doc) (m i : Nat) (c : Content) : contentStrict (gateContent D m i c) = contentStrict c := by
  cases c with
  | norm M => simp [gateContent, contentStrict, strictRule]
  | _ => rfl

theorem sup_strict (D : Doc) (hs : Shaped D) : StrictDoc (sup D).1 := by
  rw [sup_eq]
  suffices ∀ (l : List Item), (∀ it ∈ l, it ∈ D.items) → ∀ acc : (RightsDoc × List VE.Formula) × Nat,
      StrictDoc acc.1.1 → StrictDoc (l.foldl (supStep D) acc).1.1 from
    this D.items (fun _ h => h) _ ⟨hs.frame, by simp only [StrictNodes, supFrame, hs.nodes]; simp⟩
  intro l
  induction l with
  | nil => intro _ acc h; exact h
  | cons it l ih =>
    intro hl acc h
    apply ih (fun x hx => hl x (List.mem_cons_of_mem _ hx))
    have hit := hl it List.mem_cons_self
    cases it with
    | fixed u c cs =>
      exact place_strict _ _ _ h (by rw [contentStrict_copy]; exact hs.fixed u c cs hit)
    | bar u b => exact absurd hit (hs.bar u b)
    | set R =>
      rw [supStep_set]
      show StrictDoc ((List.range R.candidates.length).foldl (candStep D acc.2 R) acc.1).1
      suffices ∀ (is : List Nat) (a : RightsDoc × List VE.Formula), StrictDoc a.1 →
          StrictDoc (is.foldl (candStep D acc.2 R) a).1 from this _ _ h
      intro is
      induction is with
      | nil => intro a ha; exact ha
      | cons i is ihi =>
        intro a ha
        apply ihi
        unfold candStep
        cases hR : R.candidates[i]? with
        | none => exact ha
        | some x =>
          cases hx : x.content with
          | none => simp only [Option.bind_some, hx, Option.map_none]; exact ha
          | some c =>
            simp only [Option.bind_some, hx, Option.map_some]
            exact place_strict _ _ _ ha (by
              rw [contentStrict_gate]; exact hs.set R hit x (List.mem_of_getElem? hR) c hx)

theorem unsaidName_head (p : String) : (VE.NormDefaults.unsaidName p).data.head? = some 'u' := by
  simp [VE.NormDefaults.unsaidName, String.data_append]

theorem bitDecls_find_unsaid (D : Doc) (p : String) :
    (bitDecls D).find? (·.1 == VE.NormDefaults.unsaidName p) = none := by
  apply List.find?_eq_none.mpr
  intro d hd he
  simp only [beq_iff_eq] at he
  simp only [bitDecls, List.mem_flatMap, List.mem_map, List.mem_range] at hd
  obtain ⟨m, _, j, _, rfl⟩ := hd
  simp only at he
  have h1 := bitName_head (m + 1) j
  rw [he, unsaidName_head] at h1
  cases h1

/-- The choice vocabulary and `E‴` override disjoint names. -/
theorem choiceEnv_fill (N : NDoc) (X : RightsDoc) (hX : noRights X = true) (hh : StrictNodes X.soft)
    (hE : X.soft.E = choiceEnv N.D N.D.frame.soft.E) (hreg : X.soft.T.regulated = N.D.frame.soft.T.regulated) :
    choiceEnv N.D (fillFrameEnv N) = VE.NormDefaults.fillEnv ⟨soften (correlate X), N.unspec⟩ := by
  rw [(correlate_noRights _ hX).1, soften_strict _ hh]
  simp only [VE.NormDefaults.fillEnv, hE]
  unfold choiceEnv
  split
  · simp only [fillFrameEnv]
    congr 1
    funext n
    cases h : N.unspec.find? (fun p => VE.NormDefaults.unsaidName p == n) <;>
      simp [VE.NormDefaults.sortsOf, VE.SoftNorms.sortsOf, VE.SoftNorms.sortsIn, hreg]
  · simp only [fillFrameEnv]
    congr 1
    funext n
    cases h : N.unspec.find? (fun p => VE.NormDefaults.unsaidName p == n) with
    | none => simp
    | some p =>
      have hp : VE.NormDefaults.unsaidName p = n := by simpa using List.find?_some h
      subst hp
      simp [bitDecls_find_unsaid, VE.NormDefaults.sortsOf, VE.SoftNorms.sortsOf, VE.SoftNorms.sortsIn, hreg]

theorem fillDoc_sup (N : NDoc) (hn : normsShaped N.D = true) (hf : fillNamesFree N = true) :
    soften (correlate (sup (fillDoc N)).1) = VE.NormDefaults.fill (supU N) ∧ (sup (fillDoc N)).2 = (sup N.D).2 := by
  have hs := shaped hn
  rw [sup_fillDoc N (namesFree hf) hs.nodes]
  have hX := sup_strict N.D hs
  exact ⟨soften_fill N _ hX.1 hX.2 sup_reg _ (choiceEnv_fill N _ hX.1 hX.2 sup_E sup_reg), rfl⟩

/-! ## Proofs: attachment as a list -/

theorem attached_nodup (D : Doc) (u : String) : (attached D u).Nodup := by
  have h := attachedIter_eq D D.items.length 0
  simp only [attachedLevels, Nat.zero_add] at h
  rw [attached, h]
  cases D.items.length with
  | zero =>
    simp only [attachedLevels, attachedLevel0, VE.SoftNorms.belowAt_map]
    split
    · exact dedup_nodup _
    · exact List.nodup_nil
  | succ n =>
    simp only [attachedLevels, attachedStep, VE.SoftNorms.belowAt_map]
    split
    · exact dedup_nodup _
    · exact List.nodup_nil

/-- Two duplicate-free lists with the same members, all equal, are equal. -/
theorem eq_of_subsingleton {l l' : List String} (h : l.Nodup) (h' : l'.Nodup) (hm : ∀ x, x ∈ l ↔ x ∈ l')
    (hs : ∀ x ∈ l', ∀ y ∈ l', x = y) : l = l' := by
  have single : ∀ {k : List String} (x : String), k.Nodup → x ∈ k → (∀ y ∈ k, y = x) → k = [x] := by
    intro k x hk hx hy
    cases k with
    | nil => cases hx
    | cons a as =>
      have ha : a = x := hy a List.mem_cons_self
      subst ha
      cases as with
      | nil => rfl
      | cons b bs =>
        have hb : b = a := hy b (List.mem_cons_of_mem _ List.mem_cons_self)
        subst hb
        exact absurd List.mem_cons_self (List.nodup_cons.mp hk).1
  cases l' with
  | nil => exact List.eq_nil_iff_forall_not_mem.mpr (fun x hx => List.not_mem_nil ((hm x).mp hx))
  | cons x xs =>
    have hx : x ∈ x :: xs := List.mem_cons_self
    rw [single x h' hx (fun y hy => hs y hy x hx)]
    exact single x h ((hm x).mpr hx) (fun y hy => hs y ((hm y).mp hy) x hx)

set_option linter.unusedVariables false in
/-- The sets a fixed unit is attached to are the same list in `fillDoc N` and `N.D` when every unit is attached
    to one set at most. The approved statement had no `hs`; without it the two lists can differ in order
    (`UnspecifiedExamples`, fixture F-ND11): `attached` iterates its levels once per item, `fillDoc` adds items,
    and on a unit attached to several sets the level lists can alternate in order. -/
theorem attached_fillDoc (N : NDoc) (hf : fillNamesFree N = true) (hs : singlyAttached N.D = true) (u : String)
    (hu : u ∈ fixedNames N.D) : attached (fillDoc N) u = attached N.D u := by
  refine eq_of_subsingleton (attached_nodup _ u) (attached_nodup _ u) (mem_attached_fillDoc N hf u) ?_
  intro x hx y hy
  exact (singlyAttached_spec N.D).mp hs u x y ((attached_iff _ _ _).mp hx) ((attached_iff _ _ _).mp hy)

/-! ## Admission's facts (1.4) -/

def WellFormedND (N : NDoc) : Bool :=
  WellFormedDoc N.D && normsShaped N.D && fillNamesFree N && VE.NormDefaults.WellFormedU (freeU N) &&
  N.D.sets.all (fun R => (List.range R.candidates.length).all (fun i =>
    (R.candidates[i]?.bind (·.content)).isNone || VE.NormDefaults.WellFormedU (oneU N R.id i)))

/-! ## Separation under the completion (1.5) -/

/-- S1's `Achieves` on the filled document, the filling respecting `Fill_T` of the reading's own document. -/
def AchievesU (N : NDoc) (s : String) (i : Nat) (B : VE.Structure.{u}) (F : Tables B.Carrier)
    (q : Probe B.Carrier) (v : Bool) : Prop :=
  Achieves (fillDoc N) s i B F q v ∧ Sat B (VE.NormDefaults.fillPremises (oneU N s i))
def SeparatedU (N : NDoc) (s : String) (i j : Nat) : Prop :=
  ∃ (B : VE.Structure.{u}) (F : Tables B.Carrier) (q : Probe B.Carrier) (v : Bool),
    (AchievesU N s i B F q v ∧ ¬ AchievesU N s j B F q v) ∨ (AchievesU N s j B F q v ∧ ¬ AchievesU N s i B F q v)
/-- The witness's step 2 under the completion: its `Fill_T` holds on the situation's base. -/
def fillHolds {α : Type u} [DecidableEq α] (N : NDoc) (s : String) (i : Nat) (M : VE.FiniteModel α) : Bool :=
  (VE.NormDefaults.fillPremises (oneU N s i)).all (fun φ => φ.eval M [])

theorem fillHolds_sat {α : Type u} [DecidableEq α] (N : NDoc) (s : String) (i : Nat) (M : VE.FiniteModel α)
    (h : fillHolds N s i M = true) : Sat M.asStructure (VE.NormDefaults.fillPremises (oneU N s i)) := by
  intro φ hφ
  simp only [fillHolds, List.all_eq_true] at h
  exact (VE.eval_iff_denote M [] φ).mp (h φ hφ)

theorem separates_soundU {α : Type u} [DecidableEq α] (N : NDoc) (hF : WellFormedDoc (fillDoc N) = true)
    (s : String) (i j : Nat) (hi : (candidate (fillDoc N) s i).bind (·.content) ≠ none)
    (hj : (candidate (fillDoc N) s j).bind (·.content) ≠ none) (σ : Situation α)
    (valid : σ.base.Valid (authorEnv (fillDoc N))) (h : separates (fillDoc N) s i j σ = true)
    (hf : fillHolds N s i σ.base = true) :
    AchievesU N s i σ.base.asStructure (tablesOf σ.fixed) σ.probe σ.value ∧
      ¬ AchievesU N s j σ.base.asStructure (tablesOf σ.fixed) σ.probe σ.value := by
  have h1 := separates_sound (fillDoc N) hF s i j hi hj σ valid h
  exact ⟨⟨h1.1, fillHolds_sat N s i σ.base hf⟩, fun hA => h1.2 hA.1⟩

theorem separates_separatedU {α : Type u} [DecidableEq α] (N : NDoc) (hF : WellFormedDoc (fillDoc N) = true)
    (s : String) (i j : Nat) (hi : (candidate (fillDoc N) s i).bind (·.content) ≠ none)
    (hj : (candidate (fillDoc N) s j).bind (·.content) ≠ none) (σ : Situation α)
    (valid : σ.base.Valid (authorEnv (fillDoc N))) (h : separates (fillDoc N) s i j σ = true)
    (hf : fillHolds N s i σ.base = true) : SeparatedU.{u} N s i j :=
  ⟨σ.base.asStructure, tablesOf σ.fixed, σ.probe, σ.value,
    Or.inl (separates_soundU N hF s i j hi hj σ valid h hf)⟩

/-! ## Proofs: on the norms chain no key is generated -/

theorem one_fillDoc (N : NDoc) (hn : normsShaped N.D = true) (hf : fillNamesFree N = true) (s : String)
    (i : Nat) : one (fillDoc N) s i =
      (addNodes (fillX N (fillFrameEnv N) (one N.D s i).1) (fillUnitNodes N), (one N.D s i).2) :=
  build_fillDoc N (shaped hn).nodes _ _ _ _
    (fun u _ _ _ => all_congr_mem (mem_attached_fillDoc N hf u) _)
    (fun u _ _ => all_congr_mem (mem_attached_fillDoc N hf u) _)
    (fun R _ => by
      show (if R.id == s then (fillSet N R).candidates[i]? else none) = _
      rw [candidates_fillSet]; split <;> rfl)
    (fun r _ _ => by rw [attached_fillUnit N hf r]; rfl)

theorem one_strict (D : Doc) (hn : normsShaped D = true) (s : String) (i : Nat) : StrictDoc (one D s i).1 :=
  build_strict D (shaped hn) _ _ (fun R a h => by
    by_cases hs : (R.id == s) = true
    · rw [if_pos hs] at h; exact List.mem_of_getElem? h
    · rw [if_neg hs] at h; cases h)

theorem strict_one_fillDoc (N : NDoc) (hn : normsShaped N.D = true) (hf : fillNamesFree N = true) (s : String)
    (i : Nat) : StrictDoc (one (fillDoc N) s i).1 := by
  have hX := one_strict N.D hn s i
  rw [one_fillDoc N hn hf s i]
  exact ⟨by rw [noRights_fill]; exact hX.1, strictNodes_fill N _ _ hX.2⟩

theorem genKeys_strict (X : RightsDoc) (hX : StrictDoc X) : genKeys X = [] := by
  have hn := hX.1
  simp only [noRights, Bool.and_eq_true, List.isEmpty_iff] at hn
  obtain ⟨⟨⟨_, hl⟩, hb⟩, _⟩ := hn
  have h := genKeys_names X
  rw [(correlate_noRights X hX.1).1, decisions_strict _ hX.2, VE.Rights.genDecls_nil X hl hb] at h
  exact List.map_eq_nil_iff.mp h

theorem withTables_nil (X : RightsDoc) (h : genKeys X = []) (B : VE.Structure.{u}) (G : Tables B.Carrier) :
    withTables X B G = B := by
  simp only [withTables, h, List.find?_nil]

theorem softPremises_strict (S : SoftDoc) (hh : StrictNodes S) : VE.SoftNorms.softPremises S = [] := by
  have hcp : VE.SoftNorms.collidingPairs S = [] := by
    cases hc : VE.SoftNorms.collidingPairs S with
    | nil => rfl
    | cons x xs =>
      have hx : (x.1, x.2) ∈ VE.SoftNorms.collidingPairs S := by rw [hc]; exact List.mem_cons_self
      obtain ⟨hM, _, hd, _⟩ := VE.SoftNorms.mem_collidingPairs.mp hx
      rw [(hh _ hM).1] at hd
      cases hd
  simp only [VE.SoftNorms.softPremises, VE.SoftNorms.cohPremises, hcp, List.map_nil, List.append_nil,
    VE.SoftNorms.excPremises, List.flatMap_eq_nil_iff]
  intro M hM
  simp [VE.SoftNorms.excPremisesOf, (hh M hM).1]

/-- A probe is read the same on a structure with the same relations. -/
theorem observes_rel_congr (X : RightsDoc) (A : List VE.Formula) (B : VE.Structure.{u})
    (r : String → List B.Carrier → Prop) (hr : ∀ p vs, r p vs ↔ B.relation p vs) (q : Probe B.Carrier) (v : Bool) :
    Observes X A { B with relation := r } q v ↔ Observes X A B q v := by
  have : r = B.relation := funext fun p => funext fun vs => propext (hr p vs)
  subst this
  exact Iff.rfl

theorem observes_withTables_nil (X : RightsDoc) (h : genKeys X = []) (Y : RightsDoc) (A : List VE.Formula)
    (B : VE.Structure.{u}) (G : Tables B.Carrier) (q : Probe B.Carrier) (v : Bool) :
    Observes Y A (withTables X B G) q v ↔ Observes Y A B q v :=
  observes_rel_congr Y A B _ (fun p vs => by rw [h]; exact Iff.rfl) q v

/-- On the norms chain no key is generated: `AchievesU` is an admissible filled situation of the reading's filled
    document (norm-defaults' `BaseAdmissibleU`) where the probe has the value. -/
theorem achievesU_iff (N : NDoc) (hn : normsShaped N.D = true) (hf : fillNamesFree N = true) (s : String)
    (i : Nat) (B : VE.Structure.{u}) (F : Tables B.Carrier) (q : Probe B.Carrier) (v : Bool) :
    AchievesU N s i B F q v ↔
      B.Admissible (authorEnv (fillDoc N)) ∧ VE.NormDefaults.BaseAdmissibleU (oneU N s i) B ∧
        Observes (one (fillDoc N) s i).1 (one (fillDoc N) s i).2 B q v := by
  have hX := strict_one_fillDoc N hn hf s i
  have hg := genKeys_strict _ hX
  have hR : ∀ B : VE.Structure.{u}, VE.Rights.BaseAdmissibleR (one (fillDoc N) s i).1 B ↔
      VE.Norms.BaseAdmissible (VE.NormDefaults.fill (oneU N s i)) B := by
    intro B
    have hc := correlate_noRights _ hX.1
    simp only [VE.Rights.BaseAdmissibleR, VE.SoftNorms.BaseAdmissible', hc.2, (fillDoc_one N hn hf s i).1]
    rw [hc.1, softPremises_strict _ hX.2]
    simp [Sat]
  unfold AchievesU Achieves VE.NormDefaults.BaseAdmissibleU
  constructor
  · rintro ⟨⟨hA, G, _, hB, hO⟩, hS⟩
    rw [withTables_nil _ hg] at hB
    exact ⟨hA, ⟨(hR B).mp hB, hS⟩, (observes_withTables_nil _ hg _ _ B G q v).mp hO⟩
  · rintro ⟨hA, ⟨hB, hS⟩, hO⟩
    refine ⟨⟨hA, F, fun _ _ _ => Iff.rfl, ?_, ?_⟩, hS⟩
    · rw [withTables_nil _ hg]; exact (hR B).mpr hB
    · exact (observes_withTables_nil _ hg _ _ B F q v).mpr hO

end VE.Readings
