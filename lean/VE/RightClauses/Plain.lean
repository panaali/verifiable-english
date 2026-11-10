import VE.RightClauses.Tree
import Std.Data.TreeMap
import Std.Data.HashSet

/-! The elaboration `plain` (docs/spec/right-clauses.md 1.2, 8.3) and the head's checks on structured lines (1.1,
1.3, 1.5, 4.1 steps 3 and 4, 7).

`plain` conjoins each structured line's clauses and relation atom to its norm guard and changes nothing else, so
every rights theorem applies to `plain D` unchanged; with no clause and no relation it is the identity
(`plain_identity`). `checkClauses` checks the fixed lines and `checkCandidates` the reading candidates' lines, in
the order of 4.1 with the texts of section 7. The decoding texts of 7 (`elided missing`, `invalid elided`,
`invalid clause <i>`, `invalid relation`) belong to the right-clauses wire decoder (cmp-s3-cfr-1), not to these
checks: a `CLine` already has every field. An entry whose rule is on two lines of the rights document it is checked
against (its right in that document or not) gets rights' own `DuplicateDeclaration` text when that is rights' first
fault on the document (`entryError`). -/
namespace VE.RightClauses
open VE.Rights (RightsDoc SourceLine Line linesOf sourceLines holderSlot sortsOf lineAct limPremisesLabelled
  limPremises WellFormedRights validateRights correlate)
universe u

/-- The relation atom over a context of `k` slots: slot j is variable k-1-j. -/
def relAtom (k : Nat) (rel : Relation) : VE.Formula :=
  .binary rel.pred (.var (k - 1 - rel.slots.1)) (.var (k - 1 - rel.slots.2))
/-- The plain guard (1.2): left-nested conjunction of the guard, the clauses in order, then the relation atom. -/
def plainGuard (k : Nat) (G : VE.Formula) (L : CLine) : VE.Formula :=
  (L.clauses.map (·.formula) ++ (L.relation.map (relAtom k)).toList).foldl .and G
/-- One source line through its entry, if any: only the norm's guard changes. -/
def plainSource (E : VE.SoftNorms.SoftDoc) (cl : List (String × String × CLine)) (R : String) (S : SourceLine) :
    SourceLine :=
  match cl.find? (fun x => x.1 == R && some x.2.1 == lineName S) with
  | some x => { S with norm := S.norm.map (fun N => { N with guard := plainGuard (lineSorts E S).length N.guard x.2.2 }) }
  | none => S
def plain (D : ClauseDoc) : RightsDoc :=
  { D.doc with
    rs := D.doc.rs.map (fun R => { R with lines := R.lines.map (plainSource D.doc.soft D.lines R.name) })
    sourceOrder := D.doc.sourceOrder.map (·.map (fun RS => (RS.1, plainSource D.doc.soft D.lines RS.1 RS.2))) }
/-- A reading candidate's content through its own structured lines (1.4); other contents unchanged. -/
def plainContent (E : VE.SoftNorms.SoftDoc) (cl : List (String × String × CLine)) : VE.Compose.Content → VE.Compose.Content
  | .right R => .right { R with lines := R.lines.map (plainSource E cl R.name) }
  | .rightLines r ls => .rightLines r (ls.map (plainSource E cl r))
  | c => c

/-- The guard of the source line whose rule is `n` (⊤ when there is none). -/
def guardOf (D : RightsDoc) (n : String) : VE.Formula :=
  ((sourceLines D).findSome? (fun RS => RS.2.norm.filter (·.name == n))).elim .top (·.guard)
/-- The holder guard `H_R` (⊤ for an unknown right). -/
def holderGuardOf (D : ClauseDoc) (R : String) : VE.Formula :=
  ((VE.Rights.rightOf D.doc R).map (·.guard)).getD .top

/-! ## The checks (1.1, 1.3, 1.5, 7) -/

/-- An entry `(R, n, L)` of `cl` is the only entry named `n`, its right is in `Dr`, and `L.line` is the one source
    line of `src` whose rule is `n`, of right `R`. An entry that fails it (right in `Dr` or not) gets `entryError`. -/
def entryOk (cl : List (String × String × CLine)) (Dr : RightsDoc) (src : List (String × SourceLine))
    (x : String × String × CLine) : Bool :=
  (VE.Rights.rightOf Dr x.1).isSome && decide (cl.filter (·.2.1 == x.2.1) = [x]) &&
    decide (src.filter (fun RS => lineName RS.2 == some x.2.1) = [(x.1, x.2.2.line)])
/-- The refusal of an entry of rule `n` that fails `entryOk`, whether or not its right is in `Dr`. When `n` is the rule of more than one line of `Dr`'s
    rights (the lines rights' own name check reads) and rights' first fault on `Dr` (`checkRights`, rights 8) is a
    `DuplicateDeclaration`, that text, unchanged; otherwise `InvalidInput: invalid clauses of rule <n>`. Rights'
    diagnostics are strings, so its kind is read from the text's `DuplicateDeclaration: ` prefix. -/
def entryError (Dr : RightsDoc) (n : String) : String :=
  let invalid := s!"InvalidInput: invalid clauses of rule {n}"
  match VE.Rights.checkRights Dr with
  | .error e =>
    if (Dr.rs.flatMap (fun R : VE.Rights.Right => R.lines)).countP (fun S : SourceLine => lineName S == some n) > 1 &&
        e.startsWith "DuplicateDeclaration: " then e
    else invalid
  | .ok () => invalid
/-- 1.1: clauses and a relation only on a claim, liberty or immunity line with a norm and no fan-out. -/
def shapeOk (L : CLine) : Bool :=
  (L.clauses.isEmpty && L.relation.isNone) ||
    (L.line.kind != .power && L.line.fanOut.isEmpty && L.line.norm.isSome)
/-- Spans in wire order: each non-empty, inside the unit `u`, and disjoint from every earlier one (7, K6). The earlier
    spans (`earlier`, end by start) are non-empty and pairwise disjoint, so their ends grow with their starts: a span
    `[a, b)` overlaps one of them exactly when it overlaps the one with the greatest start below `b`. One lookup per
    span, so the check is `O(s log s)`, not quadratic (W1 fixture, the evaluator rule of 2026-10-27); the answers are
    the pairwise check's (`checkSpansPairwise`, Examples.lean). -/
def checkSpans (n : String) (u : Nat × Nat) : Std.TreeMap Nat Nat → List (Nat × Nat) → Except String Unit
  | _, [] => .ok ()
  | earlier, s :: rest =>
    if s.1 < s.2 && u.1 ≤ s.1 && s.2 ≤ u.2 && (earlier.getEntryLT? s.2).all (fun t => t.2 ≤ s.1) then
      checkSpans n u (earlier.insert s.1 s.2) rest
    else .error s!"ClauseSpan: {n}: [{s.1}, {s.2})"
/-- 1.1, 1.3, 1.5: two distinct slots of the line; `pred` a declared binary base predicate of their sorts with no
    reserved prefix; `total`, when set, one of the two slots, the line's holder slot `hs`, with `H_R` typed over
    the base vocabulary `B`. -/
def relationOk (B : VE.Environment) (Rt : VE.Rights.Right) (hs : Option Nat) (ss : List String) (rel : Relation) :
    Bool :=
  rel.slots.1 != rel.slots.2 && rel.slots.1 < ss.length && rel.slots.2 < ss.length &&
    B.predicates rel.pred == some [ss.getD rel.slots.1 "", ss.getD rel.slots.2 ""] &&
    !(rel.pred.startsWith "rights__" || rel.pred.startsWith "soft__" || rel.pred.startsWith "ve__") &&
    rel.total.all (fun j => (j == rel.slots.1 || j == rel.slots.2) && hs == some j && Rt.guard.check B [Rt.holder])
/-- Clause typing, spans, the relation and its cites of one entry whose right is `Rt` (4.1 step 3). `units` is the
    set of `D.doc`'s unit ids, built once per document, so a cite costs one lookup (the evaluator rule of 2026-10-27). -/
def checkBody (D : ClauseDoc) (units : Std.HashSet String) (Dr : RightsDoc) (Rt : VE.Rights.Right) (x : String × String × CLine) :
    Except String Unit := do
  let (R, n, L) := x
  let ss := lineSorts D.doc.soft L.line
  for (c, i) in L.clauses.zipIdx do
    unless c.formula.check (baseEnv D) ss.reverse do throw s!"InvalidInput: ill-typed clause {i} of rule {n}"
  checkSpans n L.unitSpan ∅ (L.clauses.map (·.span) ++ L.elided)
  for rel in L.relation.toList do
    unless relationOk (baseEnv D) Rt ((VE.Rights.instancesOf R L.line 0).head?.map (holderSlot Dr)) ss rel do
      throw s!"RelationShape: {n}"
    for u in rel.cites do
      unless units.contains u do throw s!"UnknownSymbol: unit {u}"
/-- One entry against the entries `cl` it belongs to, the rights document `Dr` holding its right and the source
    lines `src` it may name: the entry, the line shape, then `checkBody`. -/
def checkEntry (D : ClauseDoc) (units : Std.HashSet String) (cl : List (String × String × CLine)) (Dr : RightsDoc)
    (src : List (String × SourceLine)) (x : String × String × CLine) : Except String Unit :=
  match VE.Rights.rightOf Dr x.1 with
  | some Rt =>
    if !entryOk cl Dr src x then .error (entryError Dr x.2.1)
    else if !shapeOk x.2.2 then .error s!"ClauseLineShape: {x.2.1}"
    else checkBody D units Dr Rt x
  | none => .error (entryError Dr x.2.1)

/-- 1.1, 1.3, 7: shape, typing, spans, relation and cites of every entry; the entries name distinct rules, each the
    rule of exactly one source line of `D.doc`, of the right the entry names, and `L.line` is that source line;
    and, for a total relation, `(holderGuardOf D R).check (baseEnv D) [holder]`. -/
def checkClauses (D : ClauseDoc) : Except String Unit :=
  D.lines.forM (checkEntry D (Std.HashSet.ofList D.doc.sourceUnits) D.lines D.doc (sourceLines D.doc))
def WellFormedClauses (D : ClauseDoc) : Bool := match checkClauses D with | .ok () => true | .error _ => false
/-- The rights document holding a candidate's right and the source lines its entries may name: the candidate's
    own right for `.right`, else `D.doc` with the content's lines. -/
def candSource (D : ClauseDoc) : VE.Compose.Content → RightsDoc × List (String × SourceLine)
  | .right R => ({ D.doc with rs := [R] }, R.lines.map (R.name, ·))
  | .rightLines r ls => (D.doc, ls.map (r, ·))
  | _ => (D.doc, [])
/-- 4.1 steps 3 and 4 over `D.cands`, in order. First the checks of 1.1, 1.3 and 7 on each candidate's entries
    against its content's lines, each span against its own `unitSpan`, types over `baseEnv D`. The right (holder
    sort, `H_R`) is the candidate's own when its content is `.right`, else `D.doc`'s; unit ids are `D.doc`'s. Then
    `RelationOnCandidate` for the first total relation. -/
def checkCandidates (D : ClauseDoc) : Except String Unit := do
  let units := Std.HashSet.ofList D.doc.sourceUnits
  for (_, _, c, cl) in D.cands do
    cl.forM (checkEntry D units cl (candSource D c).1 (candSource D c).2)
  for (s, i, _, cl) in D.cands do
    for x in cl do
      if (x.2.2.relation.bind (·.total)).isSome then throw s!"RelationOnCandidate: {s}:{i}: {x.2.1}"

/-! ## Proofs -/

/-- `plainSource` changes at most the norm's guard. -/
theorem plainSource_eq (E : VE.SoftNorms.SoftDoc) (cl : List (String × String × CLine)) (R : String)
    (S : SourceLine) : ∃ g : VE.SoftNorms.SoftNode → VE.Formula,
    plainSource E cl R S = { S with norm := S.norm.map (fun N => { N with guard := g N }) } := by
  unfold plainSource
  split
  · exact ⟨_, rfl⟩
  · exact ⟨(·.guard), by obtain ⟨_, n, _⟩ := S; cases n <;> rfl⟩

theorem plainSource_nil (E : VE.SoftNorms.SoftDoc) (cl : List (String × String × CLine))
    (h : ∀ x ∈ cl, x.2.2.clauses = [] ∧ x.2.2.relation = none) (R : String) : plainSource E cl R = id := by
  funext S
  unfold plainSource
  split
  · next x hx =>
    have hc := h x (List.mem_of_find?_eq_some hx)
    obtain ⟨_, n, _⟩ := S
    cases n <;> simp [plainGuard, hc.1, hc.2]
  · rfl

theorem plain_identity (D : ClauseDoc) (h : ∀ x ∈ D.lines, x.2.2.clauses = [] ∧ x.2.2.relation = none) :
  plain D = D.doc := by
  have hp := plainSource_nil D.doc.soft D.lines h
  unfold plain
  simp only [hp, id_eq]
  cases D.doc; simp

theorem plainContent_identity (E : VE.SoftNorms.SoftDoc) (cl : List (String × String × CLine))
    (h : ∀ x ∈ cl, x.2.2.clauses = [] ∧ x.2.2.relation = none) (c : VE.Compose.Content) : plainContent E cl c = c := by
  cases c <;> simp [plainContent, plainSource_nil E cl h]

theorem lineRuleNames_plain (E : VE.SoftNorms.SoftDoc) (cl : List (String × String × CLine)) (R : String)
    (S : SourceLine) : VE.Compose.lineRuleNames (plainSource E cl R S) = VE.Compose.lineRuleNames S := by
  obtain ⟨g, hg⟩ := plainSource_eq E cl R S
  rw [hg]; obtain ⟨_, n, _⟩ := S; cases n <;> simp [VE.Compose.lineRuleNames]

/-- Declared names, kinds and needs are unchanged, so S1's interface and cross-set checks see the same names. -/
theorem plainContent_declared (E) (cl) (c : VE.Compose.Content) :
  (plainContent E cl c).declared = c.declared ∧ (plainContent E cl c).kind = c.kind ∧
  (plainContent E cl c).needs = c.needs := by
  cases c <;> simp [plainContent, VE.Compose.Content.declared, VE.Compose.Content.kind, VE.Compose.Content.needs,
    List.flatMap_map, lineRuleNames_plain]

/-! ### Line instances keep everything but guards -/

/-- What `plain` keeps of a line instance. -/
def lineKey (RN : String × Line) :=
  (RN.1, RN.2.kind, RN.2.ikind, RN.2.node.name, RN.2.node.pred, RN.2.bearer, RN.2.source.holderSlot, RN.2.right)

theorem instancesOf_key (R : String) (S : SourceLine) (g : VE.SoftNorms.SoftNode → VE.Formula) (k : Nat) :
    ((VE.Rights.instancesOf R { S with norm := S.norm.map (fun N => { N with guard := g N }) } k).map
      (fun N => lineKey (R, N))) = (VE.Rights.instancesOf R S k).map (fun N => lineKey (R, N)) := by
  obtain ⟨kd, n, l, r, f, hs, cs⟩ := S
  cases kd <;> cases n <;> simp [VE.Rights.instancesOf, lineKey] <;> split <;>
    simp [List.mapIdx_eq_zipIdx_map, Function.comp_def]

theorem fanCount_plain (S : SourceLine) (g : VE.SoftNorms.SoftNode → VE.Formula) :
    VE.Rights.fanCount { S with norm := S.norm.map (fun N => { N with guard := g N }) } = VE.Rights.fanCount S := by
  obtain ⟨kd, n, _⟩ := S; cases kd <;> cases n <;> simp [VE.Rights.fanCount]

theorem linesAux_key (E : VE.SoftNorms.SoftDoc) (cl : List (String × String × CLine)) :
    ∀ (l : List (String × SourceLine)) (k : Nat),
    (VE.Rights.linesAux (l.map (fun RS => (RS.1, plainSource E cl RS.1 RS.2))) k).map lineKey =
      (VE.Rights.linesAux l k).map lineKey
  | [], _ => rfl
  | (R, S) :: rest, k => by
    obtain ⟨g, hg⟩ := plainSource_eq E cl R S
    simp only [List.map_cons, VE.Rights.linesAux, List.map_append, List.map_map]
    rw [linesAux_key E cl rest, hg, fanCount_plain]
    congr 1
    simpa [List.map_map, Function.comp_def] using instancesOf_key R S g k

theorem sourceLines_plain (D : ClauseDoc) :
    sourceLines (plain D) = (sourceLines D.doc).map (fun RS => (RS.1, plainSource D.doc.soft D.lines RS.1 RS.2)) := by
  unfold sourceLines plain
  cases D.doc.sourceOrder <;> simp [List.map_flatMap, List.flatMap_map, Function.comp_def]

theorem linesOf_plain_key (D : ClauseDoc) : (linesOf (plain D)).map lineKey = (linesOf D.doc).map lineKey := by
  unfold linesOf; rw [sourceLines_plain]; exact linesAux_key _ _ _ 0

theorem rightOf_plain (D : ClauseDoc) (r : String) :
    (VE.Rights.rightOf (plain D) r).map (·.holder) = (VE.Rights.rightOf D.doc r).map (·.holder) := by
  simp [VE.Rights.rightOf, plain, List.find?_map, Function.comp_def, Option.map_map]

/-- Everything but guards is unchanged. -/
theorem plain_shape (D : ClauseDoc) :
  (plain D).soft = D.doc.soft ∧ (plain D).rights = D.doc.rights ∧ (plain D).limits = D.doc.limits ∧
  (plain D).bars = D.doc.bars ∧ (plain D).sourceUnits = D.doc.sourceUnits ∧
  (linesOf (plain D)).map (fun RN => (RN.1, RN.2.kind, RN.2.ikind, RN.2.node.name, RN.2.node.pred, RN.2.bearer)) =
    (linesOf D.doc).map (fun RN => (RN.1, RN.2.kind, RN.2.ikind, RN.2.node.name, RN.2.node.pred, RN.2.bearer)) ∧
  ∀ RN ∈ linesOf (plain D), ∃ RN' ∈ linesOf D.doc, RN'.1 = RN.1 ∧ RN'.2.node.name = RN.2.node.name ∧
    holderSlot (plain D) RN.2 = holderSlot D.doc RN'.2 ∧ sortsOf (plain D) RN.2 = sortsOf D.doc RN'.2 ∧
    lineAct (plain D) RN.2 = lineAct D.doc RN'.2 := by
  have hk := linesOf_plain_key D
  refine ⟨rfl, rfl, rfl, rfl, rfl, ?_, ?_⟩
  · have := congrArg (List.map (fun K => (K.1, K.2.1, K.2.2.1, K.2.2.2.1, K.2.2.2.2.1, K.2.2.2.2.2.1))) hk
    simpa [List.map_map, Function.comp_def, lineKey] using this
  · intro RN hRN
    obtain ⟨RN', hRN', he⟩ := List.mem_map.1 (hk ▸ List.mem_map_of_mem (f := lineKey) hRN)
    simp only [lineKey, Prod.mk.injEq] at he
    obtain ⟨h1, -, hik, hn, hp, -, hhs, hr⟩ := he
    have hso : sortsOf (plain D) RN.2 = sortsOf D.doc RN'.2 := by simp [sortsOf, hp]; rfl
    refine ⟨RN', hRN', h1, hn, ?_, hso, by simp [lineAct, hp]; rfl⟩
    have hR := rightOf_plain D RN.2.right
    unfold holderSlot
    rw [hik, hhs, hso, hr]
    split <;> try rfl
    split <;> try rfl
    cases h1 : VE.Rights.rightOf (plain D) RN.2.right <;> cases h2 : VE.Rights.rightOf D.doc RN.2.right <;>
      simp_all

theorem filterMap_key {α β γ : Type} (k : α → β) (f g : α → Option γ) (hfg : ∀ a b, k a = k b → f a = g b) :
    ∀ l1 l2 : List α, l1.map k = l2.map k → l1.filterMap f = l2.filterMap g
  | [], [], _ => rfl
  | a :: l1, b :: l2, h => by
    simp only [List.map_cons, List.cons.injEq] at h
    simp only [List.filterMap_cons, hfg a b h.1, filterMap_key k f g hfg l1 l2 h.2]
  | [], _ :: _, h | _ :: _, [], h => by simp at h

theorem limActs_plain (D : ClauseDoc) (L : VE.Rights.Limitation) :
    VE.Rights.limActs (plain D) L = VE.Rights.limActs D.doc L := by
  unfold VE.Rights.limActs
  rw [filterMap_key lineKey _ _ ?_ _ _ (linesOf_plain_key D)]
  intro a b h
  simp only [lineKey, Prod.mk.injEq] at h
  simp [VE.Rights.inScope, lineAct, h.1, h.2.1, h.2.2.2.2.1]; rfl

theorem plain_limPremises (D : ClauseDoc) : limPremisesLabelled (plain D) = limPremisesLabelled D.doc := by
  have hl : VE.Rights.limKeys (plain D) = VE.Rights.limKeys D.doc := by
    simp only [VE.Rights.limKeys, limActs_plain]; rfl
  have hc : VE.Rights.condKeys (plain D) = VE.Rights.condKeys D.doc := by
    simp only [VE.Rights.condKeys, limActs_plain]; rfl
  unfold limPremisesLabelled VE.Rights.keyPremise VE.Rights.limPremise VE.Rights.limAtom VE.Rights.condAtom
    VE.Rights.limIndex VE.Rights.condIndex
  rw [hl, hc]; rfl

/-! ### The plain guard, read -/

theorem foldl_and_denote (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
    ∀ (l : List VE.Formula) (G : VE.Formula),
    (l.foldl .and G).denote S ρ ↔ G.denote S ρ ∧ ∀ φ ∈ l, φ.denote S ρ
  | [], _ => by simp
  | φ :: l, G => by
    simp only [List.foldl_cons, foldl_and_denote S ρ l, VE.Formula.denote, List.mem_cons, forall_eq_or_imp,
      and_assoc]

theorem findSome_unique {α β : Type} (f : α → Option β) (a : α) :
    ∀ l : List α, (∀ y ∈ l, f y ≠ none → y = a) → a ∈ l → l.findSome? f = f a
  | [], _, h => by simp at h
  | y :: l, hu, ha => by
    rw [List.findSome?_cons]
    cases hy : f y with
    | some b => rw [← hu y (by simp) (by simp [hy])]; exact hy.symm
    | none =>
      by_cases hal : a ∈ l
      · exact findSome_unique f a l (fun z hz => hu z (by simp [hz])) hal
      · have hay : a = y := by simpa [hal] using ha
        rw [hay, hy, List.findSome?_eq_none_iff]
        intro z hz
        cases hfz : f z with
        | none => rfl
        | some b => exact absurd ((hu z (by simp [hz]) (by simp [hfz])) ▸ hz) hal

theorem forM_ok {α : Type} (f : α → Except String Unit) :
    ∀ l : List α, l.forM f = .ok () → ∀ x ∈ l, f x = .ok ()
  | [], _ => by simp
  | y :: l, h => by
    have h' : (f y >>= fun _ => l.forM f) = .ok () := h
    cases hy : f y with
    | error e => rw [hy] at h'; cases h'
    | ok u =>
      have h : l.forM f = .ok () := by rw [hy] at h'; exact h'
      intro x hx
      rcases List.mem_cons.1 hx with rfl | hx
      · exact hy
      · exact forM_ok f l h x hx

theorem checkEntry_ok {D units cl Dr src x} (h : checkEntry D units cl Dr src x = .ok ()) :
    entryOk cl Dr src x = true ∧ shapeOk x.2.2 = true := by
  unfold checkEntry at h
  split at h
  · split at h
    · cases h
    · split at h
      · cases h
      · simp_all
  · cases h

/-- A checked entry: its shape, its line is the one source line of its rule, and `plainSource` plains that line
    through the entry. -/
theorem entry_facts (D : ClauseDoc) (h : WellFormedClauses D = true) (R n : String) (L : CLine)
    (hL : (R, n, L) ∈ D.lines) :
    shapeOk L = true ∧ (R, L.line) ∈ sourceLines D.doc ∧ lineName L.line = some n ∧
    (sourceLines D.doc).filter (fun RS => lineName RS.2 == some n) = [(R, L.line)] ∧
    plainSource D.doc.soft D.lines R L.line = { L.line with norm := L.line.norm.map (fun N =>
      { N with guard := plainGuard (lineSorts D.doc.soft L.line).length N.guard L }) } := by
  have hc : checkClauses D = .ok () := by
    unfold WellFormedClauses at h; split at h <;> simp_all
  obtain ⟨he, hs⟩ := checkEntry_ok (forM_ok _ _ hc _ hL)
  simp only [entryOk, Bool.and_eq_true, decide_eq_true_eq] at he
  obtain ⟨⟨-, hcl⟩, hsrc⟩ := he
  have hmem : (R, L.line) ∈ sourceLines D.doc := (List.mem_filter.1 (show (R, L.line) ∈ _ by rw [hsrc]; simp)).1
  have hname : lineName L.line = some n := by
    have := List.mem_filter.1 (show (R, L.line) ∈ _ by rw [hsrc]; simp); simpa using this.2
  -- `L` is the entry `plainSource` finds for its own line
  have hfind : D.lines.find? (fun x => x.1 == R && some x.2.1 == lineName L.line) = some (R, n, L) := by
    rw [List.find?_eq_some_iff_append]
    obtain ⟨as, bs, hab⟩ := List.append_of_mem hL
    refine ⟨by simp [hname], as, bs, hab, fun y hy => ?_⟩
    have hy' : y ∈ D.lines.filter (·.2.1 == n) → y = (R, n, L) := by rw [hcl]; simp
    have hyl : y ∈ D.lines := by rw [hab]; simp [hy]
    by_cases hyn : y.2.1 = n
    · have := hy' (List.mem_filter.2 ⟨hyl, by simp [hyn]⟩)
      subst this
      have hcount := congrArg List.length hcl
      rw [hab] at hcount
      simp [List.filter_append] at hcount
      have : 1 ≤ (as.filter (·.2.1 == n)).length := List.length_pos_iff_exists_mem.2 ⟨_, List.mem_filter.2 ⟨hy, by simp⟩⟩
      omega
    · simp [hname, hyn]
  exact ⟨hs, hmem, hname, hsrc, by unfold plainSource; rw [hfind]⟩

/-- The plain guard, read (1.2). -/
theorem plain_guard (D : ClauseDoc) (h : WellFormedClauses D = true) (R n : String) (L : CLine)
    (hL : (R, n, L) ∈ D.lines) (S : VE.Structure.{u}) (ρ : VE.Valuation S) :
  (guardOf (plain D) n).denote S ρ ↔
    (guardOf D.doc n).denote S ρ ∧ (∀ c ∈ L.clauses, c.formula.denote S ρ) ∧
    (∀ rel, L.relation = some rel → (relAtom (lineSorts D.doc.soft L.line).length rel).denote S ρ) := by
  obtain ⟨hs, hmem, hname, hsrc, hplain⟩ := entry_facts D h R n L hL
  -- the only source line with a norm named `n` is `L.line`, before and after `plain`
  have huniq : ∀ RS ∈ sourceLines D.doc, (RS.2.norm.filter (·.name == n)) ≠ none → RS = (R, L.line) := by
    intro RS hRS hne
    have : lineName RS.2 = some n := by
      cases hN : RS.2.norm with
      | none => simp [hN] at hne
      | some N =>
        have : N.name = n := by
          rw [hN] at hne; simp only [Option.filter] at hne; split at hne <;> simp_all
        simp [lineName, hN, this]
    have : RS ∈ (sourceLines D.doc).filter (fun RS => lineName RS.2 == some n) := List.mem_filter.2 ⟨hRS, by simp [this]⟩
    rw [hsrc] at this; simpa using this
  have hold : guardOf D.doc n = (L.line.norm.filter (·.name == n)).elim .top (·.guard) := by
    unfold guardOf; rw [findSome_unique _ (R, L.line) _ huniq hmem]
  have hnew : guardOf (plain D) n =
      ((plainSource D.doc.soft D.lines R L.line).norm.filter (·.name == n)).elim .top (·.guard) := by
    unfold guardOf; rw [sourceLines_plain]
    rw [findSome_unique (fun RS => RS.2.norm.filter (·.name == n)) (R, plainSource D.doc.soft D.lines R L.line)
      ((sourceLines D.doc).map (fun RS => (RS.1, plainSource D.doc.soft D.lines RS.1 RS.2))) ?_
      (List.mem_map.2 ⟨_, hmem, rfl⟩)]
    intro y hy hne
    obtain ⟨RS, hRS, rfl⟩ := List.mem_map.1 hy
    obtain ⟨g, hg⟩ := plainSource_eq D.doc.soft D.lines RS.1 RS.2
    have : RS = (R, L.line) := huniq RS hRS (by
      rw [hg] at hne; cases hN : RS.2.norm <;> simp_all [Option.filter])
    subst this; rfl
  rw [hold, hnew, hplain]
  cases hN : L.line.norm with
  | none =>
    have : L.clauses = [] ∧ L.relation = none := by
      simp [shapeOk, hN] at hs; simpa [List.isEmpty_iff] using hs
    simp [this, VE.Formula.denote]
  | some N =>
    have hNn : N.name = n := by simpa [lineName, hN] using hname
    simp only [Option.map_some, Option.filter, hNn, beq_self_eq_true, ite_true, Option.elim_some]
    rw [plainGuard, foldl_and_denote]
    have hm : ∀ l : List Clause, (∀ φ ∈ l.map (·.formula), φ.denote S ρ) ↔ ∀ c ∈ l, c.formula.denote S ρ :=
      fun l => List.forall_mem_map
    cases L.relation <;> simp only [List.forall_mem_append, hm, Option.map_none, Option.map_some, Option.toList_none,
      Option.toList_some, List.not_mem_nil, List.mem_singleton, forall_eq, reduceCtorEq, Option.some.injEq,
      false_implies, implies_true, and_true, forall_eq']
end VE.RightClauses
