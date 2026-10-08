import VE.Readings.Unspecified
import VE.Readings.SupRun
import VE.NormDefaults.Admission

/-! The wire under the unspecified completion (docs/spec/readings-defaults.md 1.1, 3, 4.1 to 4.3, 5 and 6.3; plan
RD-2a).

A document is under the completion when its profiles hold `readings@1` and `norm-defaults@0` on the norms chain and
some set is content-bearing (`underCompletion`). Its admission (`admitND`, 4.1) is S1's and S2a's as today, then the
reserved names `unsaid--…` (step 2), norm-defaults' author checks and `WellFormedU` on the free document and on each
reading's document (step 3, `ndText`), S1's checks of the filled document `fillDoc N` (step 4), and each compatible
choice, at most 64: S2a's chain check on the filled choice and norm-defaults' author checks on `choiceU N c` (step 5,
`ndChoiceText`). The texts are `checkAuthorN`'s and S1's, a reading's suffixed ` under <set>@<v>:<i>` and a choice's
` under <choice>`.

Separation (4.2) runs S1's replay on the filled document: the situation's base is over the filled frame's author
vocabulary, `unsaid__p` included (`filledEnvironment`), and the witness's `Fill_T` must hold on it (`fillHolds`).
Each choice (4.3) is checked by norm-defaults' own checkers on the regenerated `choiceU N c`, read as the layered
branch's source with no extra base premise (`choiceLayered`): conflict packages bound to the choice's `E‴_base` and
document hash, filled witnesses, statuses, the report, certificates (`acceptanceU`) and base models with a separate
filling (`modelCheckU`). Nothing here is decided from JSON a caller supplies: the filled documents and every choice are
regenerated from the decoded document. -/
namespace VE.Readings.Wire
open Lean
open VE.Readings
open VE.Bridge (stringField)
open VE.Norms (envAt size targets)
open VE.SoftNorms (soften)
open VE.Rights (RightsDoc correlate)
open VE.NormDefaults (EntailsU)
universe u

/-! ## Where the completion applies (1.1) -/

def normDefaultsProfile : String := "norm-defaults@0"

/-- Under the completion: `norm-defaults@0` beside `readings@1` on the norms chain, with a content-bearing set (the
    documents that reached the abstention before RD-2a). -/
def underCompletion (re : ReadingsEnvironment) (D : Doc) : Bool :=
  re.lower.contains normDefaultsProfile && re.chain == .norms && D.sets.any contentBearing

/-- The frame's unspecified predicates, from the environment the frame was decoded from. -/
def unspecOf (re : VE.Readings.Wire.ReadingsEnvironment) (D : Doc) : List String :=
  (D.frame.soft.T.regulated.map (·.name)).filter ((VE.NormDefaults.Wire.unspecifiedNames re.lowerJson).contains ·)

/-! ## Admission (4.1) -/

/-- The names a set's readings declare. -/
def setDeclared : Item → List String
  | .set R => (declaredBy R).map (·.2)
  | _ => []

/-- 4.1 step 2: the first unit id, rule name or declared name beginning `unsaid--`, in source order. -/
def reservedUnsaid (N : NDoc) : Option String :=
  firstSome N.D.items (fun it => (itemUnit it :: (it.names ++ setDeclared it)).find? (·.startsWith "unsaid--"))

/-- Step 2 is what makes `fillNamesFree` hold of every admitted document. -/
theorem fillNamesFree_of_reservedUnsaid (N : NDoc) (h : reservedUnsaid N = none) : fillNamesFree N = true := by
  have hi := firstSome_eq_none h
  have hn : ∀ it ∈ N.D.items, ∀ n ∈ itemUnit it :: (it.names ++ setDeclared it), n.startsWith "unsaid--" = false :=
    fun it hit n hn => by
      have := List.find?_eq_none.mp (hi it hit) n hn
      simpa using this
  simp only [fillNamesFree, Bool.and_eq_true, List.all_eq_true, Bool.not_eq_true']
  refine ⟨fun it hit => ⟨hn it hit _ List.mem_cons_self, fun n hm =>
    hn it hit n (List.mem_cons_of_mem _ (List.mem_append_left _ hm))⟩, fun R hR n hm => ?_⟩
  have hit : Item.set R ∈ N.D.items := by
    obtain ⟨it, hit, he⟩ := List.mem_filterMap.mp hR
    cases it with
    | set R' => cases he; exact hit
    | fixed => cases he
    | bar => cases he
  exact hn _ hit n.2 (List.mem_cons_of_mem _ (List.mem_append_right _ (List.mem_map.mpr ⟨n, hm, rfl⟩)))

/-- norm-defaults' author checks on one document in `checkAuthorN`'s order, then `WellFormedU`. -/
def ndDocText (re : ReadingsEnvironment) (U : VE.NormDefaults.UDoc) : Option String :=
  match VE.NormDefaults.Wire.checkAuthorN re.lowerJson 0 U with
  | .error e => some e
  | .ok () => if VE.NormDefaults.WellFormedU U then none else some "InvalidInput: norm-defaults document is not well formed"

/-- A passing `ndDocText` is `WellFormedU`. -/
theorem wellFormedU_of_ndDocText {re : ReadingsEnvironment} {U : VE.NormDefaults.UDoc} (h : ndDocText re U = none) :
    VE.NormDefaults.WellFormedU U = true := by
  unfold ndDocText at h
  split at h
  · cases h
  · split at h
    · assumption
    · cases h

/-- 4.1 steps 2 and 3, each reading's document read from `side` (at run time the request's table, so no reading's
    document is built again; `one` as specified): reserved names, then norm-defaults' author checks and `WellFormedU`
    on the free document and on each reading's document with content, in admission order, a reading's text suffixed
    ` under <set>@<v>:<i>`. -/
def ndTextWith (re : ReadingsEnvironment) (N : NDoc) (side : String → Nat → RightsDoc × List VE.Formula) :
    Option String :=
  ((reservedUnsaid N).map (s!"InvalidInput: reserved name {·}")).or <|
  (ndDocText re (freeU N)).or <|
  firstSome (activeOf N.D) (fun c =>
    (ndDocText re (asU N (side c.1.id c.2).1)).map (· ++ s!" under {c.1.id}@{c.1.version}:{c.2}"))

/-- 4.1 steps 2 and 3: reserved names, then norm-defaults' author checks and `WellFormedU` on the free document and
    on each reading's document with content, in admission order, a reading's text suffixed ` under <set>@<v>:<i>`. -/
def ndText (re : VE.Readings.Wire.ReadingsEnvironment) (N : NDoc) : Option String := ndTextWith re N (one N.D)

theorem ndTextWith_eq {re : ReadingsEnvironment} {N : NDoc} {side : String → Nat → RightsDoc × List VE.Formula}
    (h : ∀ s i, side s i = one N.D s i) : ndTextWith re N side = ndText re N := by
  have : side = one N.D := funext fun s => funext fun i => h s i
  subst this
  rfl

/-- 4.1 step 5 for one choice, after S2a's `choiceChainText (fillDoc N) c`: norm-defaults' author checks on
    `choiceU N c` in `checkAuthorN`'s order, then `WellFormedU`, the text suffixed ` under <choice>` in
    `choiceText`'s form (SR1). -/
def ndChoiceText (re : VE.Readings.Wire.ReadingsEnvironment) (N : NDoc) (c : Choice) : Option String :=
  (ndDocText re (choiceU N c)).map (· ++ " under " ++ choiceText N.D c)

/-- 4.1 step 5: when the compatible choices number at most 64, each in canonical order, S2a's chain check on the
    filled choice and then `ndChoiceText`; the first text found. -/
def choiceStepText (re : ReadingsEnvironment) (N : NDoc) : Option String :=
  if (choices N.D).length ≤ maxChoices then
    (choices N.D).findSome? (fun c => (choiceChainText (fillDoc N) c).or (ndChoiceText re N c))
  else none

/-- `WellFormedND` without S1's `WellFormedDoc`, which S2a's admission has established. -/
def ndRest (N : NDoc) : Bool :=
  normsShaped N.D && fillNamesFree N && VE.NormDefaults.WellFormedU (freeU N) &&
  N.D.sets.all (fun R => (List.range R.candidates.length).all (fun i =>
    (R.candidates[i]?.bind (·.content)).isNone || VE.NormDefaults.WellFormedU (oneU N R.id i)))

theorem wellFormedND_eq (N : NDoc) : WellFormedND N = (WellFormedDoc N.D && ndRest N) := by
  simp only [WellFormedND, ndRest, Bool.and_assoc]

/-- A passing `ndText` has established every conjunct of `WellFormedND` after S1's but `normsShaped`: admission
    evaluates each norm-defaults check once. -/
theorem option_or_none {α : Type} {a b : Option α} (h : a.or b = none) : a = none ∧ b = none := by
  cases a <;> simp_all

/-- A passing `ndText` has established every conjunct of `WellFormedND` after S1's but `normsShaped`: admission
    evaluates each norm-defaults check once. -/
theorem ndRest_of_ndText {re : ReadingsEnvironment} {N : NDoc} (h : ndText re N = none)
    (hs : normsShaped N.D = true) : ndRest N = true := by
  unfold ndText ndTextWith at h
  obtain ⟨h1, h23⟩ := option_or_none h
  obtain ⟨h2, h3⟩ := option_or_none h23
  have hfree := fillNamesFree_of_reservedUnsaid N (Option.map_eq_none_iff.mp h1)
  have hU := wellFormedU_of_ndDocText h2
  have hone := firstSome_eq_none h3
  simp only [ndRest, hs, hfree, hU, Bool.true_and, List.all_eq_true, Bool.or_eq_true]
  intro R hR i hi
  by_cases hp : (R.candidates[i]?.bind (·.content)).isNone = true
  · exact Or.inl hp
  · refine Or.inr (wellFormedU_of_ndDocText (Option.map_eq_none_iff.mp (hone (R, i) ?_)))
    refine List.mem_filter.mpr ⟨List.mem_flatMap.mpr ⟨R, hR, List.mem_map.mpr ⟨i, hi, rfl⟩⟩, ?_⟩
    cases hb : R.candidates[i]?.bind (·.content) <;> simp_all [pendingAt]

structure AdmittedND where
  b : VE.Readings.Wire.Admitted2
  N : NDoc
  hN : N.D = b.D
  wfU : WellFormedND N = true
  wfF : WellFormedDoc (fillDoc N) = true

/-! ## The filled document as an admitted S1 document (4.1 step 4, 4.2) -/

/-- `unsaid__p` with `p`'s sorts, for every unspecified `p` (the filled frame's author vocabulary adds them). -/
def unsaidDecls (N : NDoc) : List (String × List String) :=
  N.unspec.map (fun p => (VE.NormDefaults.unsaidName p, VE.SoftNorms.sortsOf N.D.frame.soft p))

/-- The route vocabulary with extra base predicates. A readings frame has no definitions (`frameOf`). -/
def filledRV (rv : VE.Route.Wire.RouteVocabulary) (extra : List (String × List String)) :
    VE.Route.Wire.RouteVocabulary :=
  { rv with vocabulary := { rv.vocabulary with predicates := rv.vocabulary.predicates ++ extra },
            definitions := [], chain := trivial }

/-- The decoded environment of the filled frame: `E‴`'s `unsaid__p` added. Its `json` is the case's, so situation ids
    are the document's, and its `lowerJson` is the case's, so document hashes are the norm-defaults route's. -/
def filledEnvironment (re : ReadingsEnvironment) (N : NDoc) : ReadingsEnvironment :=
  { re with se := { re.se with ne := { re.se.ne with rv := filledRV re.se.ne.rv (unsaidDecls N) } } }

theorem lookup_map_key {β : Type} (l : List String) (k : String → String) (f : String → β) (n : String) :
    VE.Bridge.lookup (l.map (fun p => (k p, f p))) n = (l.find? (fun p => k p == n)).map f := by
  simp only [VE.Bridge.lookup, List.find?_map, Option.map_map]
  rfl

/-- The filled environment's frame is `fillDoc`'s, given that no `unsaid__p` is declared (`reservedFree`). -/
theorem frameOf_filled (re : ReadingsEnvironment) (N : NDoc) (units : List String)
    (hf : N.D.frame = frameOf re units)
    (hfree : N.unspec.all (fun p => VE.Bridge.lookup re.se.ne.rv.vocabulary.predicates
      (VE.NormDefaults.unsaidName p) == none) = true) :
    frameOf (filledEnvironment re N) units = (fillDoc N).frame := by
  simp only [fillDoc, fillFrameEnv]
  rw [hf]
  simp only [frameOf, filledEnvironment, filledRV, VE.Route.Wire.RouteVocabulary.environment,
    VE.Bridge.Vocabulary.environment]
  congr 3
  funext n
  rw [lookup_append_right, unsaidDecls, hf, lookup_map_key]
  simp only [frameOf]
  cases hp : N.unspec.find? (fun p => VE.NormDefaults.unsaidName p == n) with
  | none => simp
  | some p =>
    have hm := List.mem_of_find?_eq_some hp
    have he : VE.NormDefaults.unsaidName p = n := by simpa using List.find?_some hp
    have hl := List.all_eq_true.mp hfree p hm
    rw [he] at hl
    simp only [beq_iff_eq] at hl
    simp only [hl, Option.none_or, Option.map_some]
    rfl

/-- The filled document as S1's admitted document: its chain, frame and items are `fillDoc`'s (and it has no coupling
    or narrowing, which S1 does not read), so every S1 row, pair and situation is read on the filled document, from
    its own request table. -/
structure FilledAdmitted (r : AdmittedND) where
  a : Admitted
  chain : a.D.chain = (fillDoc r.N).chain
  frame : a.D.frame = (fillDoc r.N).frame
  items : a.D.items = (fillDoc r.N).items

/-- An admitted document under the completion with what its run reads: the filled document admitted with its own
    table (4.1 step 4), and the request's table of the author's document holding each reading's document. -/
structure AdmittedNDFull where
  r : AdmittedND
  fa : FilledAdmitted r
  side : ∀ s i, r.b.a.side s i = one r.N.D s i

/-- A reading's document reads the chain, frame and items alone. -/
theorem one_links (D : Doc) (cs : List Coupling) (ns : List Narrowing) (s : String) (i : Nat) :
    one ⟨D.chain, D.frame, D.items, cs, ns⟩ s i = one D s i := by
  simp only [one, attached_links]
  rfl

theorem one_congr {D D' : Doc} (hc : D.chain = D'.chain) (hf : D.frame = D'.frame) (hi : D.items = D'.items)
    (s : String) (i : Nat) : one D s i = one D' s i := by
  obtain ⟨c, f, it, cs, ns⟩ := D
  obtain ⟨c', f', it', cs', ns'⟩ := D'
  simp only at hc hf hi
  subst hc hf hi
  exact (one_links ⟨c, f, it, cs', ns'⟩ cs ns s i)

theorem owned_links (D : Doc) (cs : List Coupling) (ns : List Narrowing) (s : String) (i : Nat) :
    owned ⟨D.chain, D.frame, D.items, cs, ns⟩ s i = owned D s i := rfl

/-- S1's separation reads the chain, frame and items alone. -/
theorem separates_links {α : Type u} [DecidableEq α] (D : Doc) (cs : List Coupling) (ns : List Narrowing)
    (s : String) (i j : Nat) (σ : Situation α) :
    separates ⟨D.chain, D.frame, D.items, cs, ns⟩ s i j σ = separates D s i j σ := by
  unfold separates situationWF sideValid sideValue cells assignments tablesFor ownedKeys ownedKeysOf situationWFOf
  simp only [one_links, owned_links]

/-- 4.1 after S1's and S2a's admission, each reading's document read from the request's table: `ndText` (steps 2
    and 3); S1's admission of the filled document (step 4: `admissionText`'s checks on `fillDoc N`, staged, its own
    table built once); step 5 on the at most 64 compatible choices. -/
def admitNDFull (b : Admitted2) : Except String AdmittedNDFull :=
  let re := b.a.re
  let N : NDoc := ⟨b.D, unspecOf re b.D⟩
  if hsd : b.D.chain = b.a.D.chain ∧ b.D.items = b.a.D.items then
    have hside : ∀ s i, b.a.side s i = one N.D s i := fun s i => by
      rw [b.a.side_eq]
      exact one_congr hsd.1.symm (by rw [b.frame]; rfl) hsd.2.symm s i
    match hT : ndTextWith re N b.a.side with
    | some e => .error e
    | none =>
      have hT' : ndText re N = none := (ndTextWith_eq hside) ▸ hT
      if hfree : N.unspec.all (fun p => VE.Bridge.lookup re.se.ne.rv.vocabulary.predicates
          (VE.NormDefaults.unsaidName p) == none) = true then
        if hc : re.chain = N.D.chain then
          let re' := filledEnvironment re N
          let doc' : Decoded2 := ⟨(fillDoc N).items, b.a.doc.itemsJ, b.a.doc.units⟩
          have hF : frameOf re' doc'.units = (fillDoc N).frame := frameOf_filled re N _ b.frame hfree
          have hD : docOf re' doc' = ⟨(fillDoc N).chain, (fillDoc N).frame, (fillDoc N).items, [], []⟩ := by
            show (⟨re'.chain, frameOf re' doc'.units, doc'.items, [], []⟩ : Doc) = _
            rw [hF, show re'.chain = (fillDoc N).chain from hc]
          match ha : admitDecoded re' doc' with
          | .error e => .error e
          | .ok a' =>
            have haD : a'.D = ⟨(fillDoc N).chain, (fillDoc N).frame, (fillDoc N).items, [], []⟩ := by
              obtain ⟨h1, h2⟩ := admitDecoded_ok ha
              simp only [Admitted.D, h1, h2, hD]
            match choiceStepText re N with
            | some e => .error e
            | none =>
              if hs : normsShaped N.D = true then
                .ok ⟨⟨b, N, rfl, by rw [wellFormedND_eq, ndRest_of_ndText hT' hs, Bool.and_true]; exact b.wf,
                    by have h : WellFormedDoc a'.D = true := a'.wf
                       rw [haD, wellFormedDoc_links] at h
                       exact h⟩,
                  ⟨a', by simp only [haD], by simp only [haD], by simp only [haD]⟩, hside⟩
              else .error "InvalidInput: norm-defaults document is not well formed"
        else .error "InvalidInput: readings document is not well-formed"
      else .error "InvalidInput: norm-defaults document is not well formed"
  else .error "InvalidInput: readings document is not well-formed"

/-- 4.1: S1's and S2a's admission as today; then, under the completion, `ndText`; then S1's checks of the filled
    document (`admissionText re (fillDoc N)`), each reading's document built once; then step 5 on the at most 64
    compatible choices, `choiceChainText (fillDoc N) c` and `ndChoiceText re N c` for each (SR1). -/
def admitNDOf (b : Admitted2) : Except String AdmittedND := (admitNDFull b).map (·.r)

/-- The case's admission under the completion, with what its run reads. -/
def admitNDFullJ (environment document : Lean.Json) : Except String AdmittedNDFull := do
  let b ← admitS2 environment document
  unless underCompletion b.a.re b.D do throw "UnsupportedProfile: the document is not under the unspecified completion"
  admitNDFull b

def admitND (environment document : Lean.Json) : Except String AdmittedND := (admitNDFullJ environment document).map (·.r)

theorem candidate_filled {r : AdmittedND} (fa : FilledAdmitted r) (s : String) (i : Nat) :
    candidate fa.a.D s i = candidate (fillDoc r.N) s i := by
  simp only [candidate, Doc.sets, fa.items]

theorem authorEnv_filled {r : AdmittedND} (fa : FilledAdmitted r) : authorEnv fa.a.D = authorEnv (fillDoc r.N) := by
  simp only [authorEnv, fa.frame]

/-- The filled document's admitted form separates as `fillDoc` does: the answer's `separated` is the hypothesis of
    `readings_wire_nd_separate_sound`. -/
theorem separates_filled {r : AdmittedND} (fa : FilledAdmitted r) {α : Type u} [DecidableEq α] (s : String) (i j : Nat)
    (σ : Situation α) : separates fa.a.D s i j σ = separates (fillDoc r.N) s i j σ := by
  have h : fa.a.D = ⟨(fillDoc r.N).chain, (fillDoc r.N).frame, (fillDoc r.N).items, [], []⟩ := by
    rw [← fa.chain, ← fa.frame, ← fa.items]
    rfl
  rw [h, separates_links]

/-- The witness's `Fill_T` on a base, its document read from the request's table (`fillHolds` as run). -/
def fillHoldsOf {α : Type u} [DecidableEq α] (N : NDoc) (X : RightsDoc) (M : VE.FiniteModel α) : Bool :=
  (VE.NormDefaults.fillPremises (asU N X)).all (fun φ => φ.eval M [])

theorem fillHoldsOf_eq (f : AdmittedNDFull) {α : Type u} [DecidableEq α] (s : String) (i : Nat)
    (M : VE.FiniteModel α) : fillHoldsOf f.r.N (f.r.b.a.side s i).1 M = fillHolds f.r.N s i M := by
  rw [f.side]
  rfl

/-! ## Separation (4.2) -/

/-- A replayed separation under the completion: the admitted document, the pair, the situation over the filled
    frame's author vocabulary. -/
structure SeparateReplayU where
  r : AdmittedND
  set : String
  witness : Nat
  other : Nat
  hw : (candidate (fillDoc r.N) set witness).bind (·.content) ≠ none
  ho : (candidate (fillDoc r.N) set other).bind (·.content) ≠ none
  σ : Situation VE.Bridge.Entity
  valid : σ.base.Valid (authorEnv (fillDoc r.N))

/-- A replayed pair is of the admitted document it was replayed on. -/
theorem replayPair_D {a : Admitted} {s sid other : String} {x : SeparateReplay} {sj : SituationJ}
    (h : replayPair a s sid other = .ok (x, sj)) : x.D = a.D := by
  unfold replayPair at h
  simp only [bind, Except.bind] at h
  repeat' (first | (split at h) | (cases h; rfl))
  all_goals (first | (cases h) | skip)

/-- The pair `(witness, other)` of a set and the situation recorded for it, replayed on the filled document. -/
def replayPairU (r : AdmittedND) (fa : FilledAdmitted r) (s sid other : String) : Except String SeparateReplayU :=
  match h : replayPair fa.a s sid other with
  | .error e => .error e
  | .ok (x, _) =>
    .ok ⟨r, x.set, x.witness, x.other,
      by rw [← candidate_filled fa, ← replayPair_D h]; exact x.hw,
      by rw [← candidate_filled fa, ← replayPair_D h]; exact x.ho,
      x.σ, by rw [← authorEnv_filled fa, ← replayPair_D h]; exact x.valid⟩

/-- The `readings-separate` input under the completion: environment, document, set, situation id and the other
    reading. -/
def replaySeparateU (j : Lean.Json) : Except String SeparateReplayU := do
  let f ← admitNDFullJ (← j.getObjVal? "environment") (← j.getObjVal? "document")
  replayPairU f.r f.fa (← stringField j "set") (← stringField j "situation") (← stringField j "other")

theorem readings_wire_nd_separate_sound (j : Lean.Json) (x : SeparateReplayU) (h : replaySeparateU j = .ok x)
    (hs : separates (fillDoc x.r.N) x.set x.witness x.other x.σ = true)
    (hf : fillHolds x.r.N x.set x.witness x.σ.base = true) :
  AchievesU x.r.N x.set x.witness x.σ.base.asStructure (tablesOf x.σ.fixed) x.σ.probe x.σ.value ∧
    ¬ AchievesU x.r.N x.set x.other x.σ.base.asStructure (tablesOf x.σ.fixed) x.σ.probe x.σ.value := by
  -- The replay carries the facts: the filled document admitted, the pair's contents, the base's validity.
  have _ := h
  exact separates_soundU x.r.N x.r.wfF x.set x.witness x.other x.hw x.ho x.σ x.valid hs hf

/-! ## The filled document on the wire (3) -/

def encF (a : VE.Formula) : Json := VE.Route.Wire.encodeFormula a

/-- Per reading with content, in admission order: its `Fill_T` with the labels `unsaid:pair:<r>,<m>`, its document
    read from `side` (the request's table). -/
def fillPremisesJson (N : NDoc) (side : String → Nat → RightsDoc × List VE.Formula) : Json :=
  Json.arr ((activeOf N.D).map (fun c => Json.mkObj [("set", .str c.1.id), ("index", toJson c.2),
    ("premises", Json.arr ((VE.NormDefaults.Admission.fillLabelled (asU N (side c.1.id c.2).1)).map (fun (l, a) =>
      Json.mkObj [("label", .str l), ("ast", encF a)])).toArray)])).toArray

/-- The units of `fillDoc N` in source order: each fixed unit's filled content (the `F_p` units last), each reading's
    filled content with its set and index. -/
def filledUnitsJson (N : NDoc) : List Json :=
  (fillDoc N).items.flatMap (fun it => match it with
    | .fixed u c _ => [Json.mkObj [("unit", .str u), ("content", contentJson c)]]
    | .bar u _ => [Json.mkObj [("unit", .str u), ("content", Json.mkObj [("kind", .str "bar")])]]
    | .set R => (List.range R.candidates.length).filterMap (fun i =>
        (R.candidates[i]?.bind (·.content)).map (fun c => Json.mkObj [("unit", .str R.unit), ("set", .str R.id),
          ("version", toJson R.version), ("index", toJson i), ("content", contentJson c)])))

/-- `filled`: the lower environment with each `unspecified` read as `deny`, `norm-defaults@0` removed and every
    `unsaid__p` added (10a's `withUnsaid`, which reads only the frame's regulated predicates), and the filled units.
    Python's search and English read it. -/
def filledJson (r : AdmittedND) : Except String Json := do
  let env ← VE.NormDefaults.Wire.withUnsaid (asU r.N r.N.D.frame)
    (← VE.NormDefaults.Wire.placeholderJson r.b.a.re.lowerJson)
  pure (Json.mkObj [("environment", env), ("units", Json.arr (filledUnitsJson r.N).toArray)])

/-! ## Each choice (4.3) -/

/-- The superposed kinds' refusal under the completion (until RD-6), as `supReplayOf` words a document that is not
    superposable. -/
def completionRefusal (D : Doc) : String :=
  s!"{notSuperposableText (completionFinding D).1} ({(completionFinding D).2}); use readings-choice"

/-- A choice's replay under the completion: a compatible choice of the admitted document and its decoded
    evidence. -/
structure ChoiceReplayU where
  r : AdmittedND
  c : Choice
  hc : Compatible r.N.D c
  wfc : VE.NormDefaults.WellFormedU (choiceU r.N c) = true
  certs : List (Option VE.Tableau.Certificate)

theorem strict_choice (N : NDoc) (hn : normsShaped N.D = true) (c : Choice) : StrictDoc (choiceDoc N.D c).1 :=
  build_strict N.D (shaped hn) _ _ (fun R a h => by
    cases hi : c.index R.id with
    | none => rw [hi] at h; cases h
    | some i => rw [hi] at h; exact List.mem_of_getElem? h)

/-- A choice's filled document reads the frame's environment. -/
theorem choiceU_E (r : AdmittedND) (c : Choice) : (choiceU r.N c).D.E = r.b.a.re.se.ne.rv.environment := by
  have hn : normsShaped r.N.D = true := by
    have h := r.wfU
    simp only [WellFormedND, Bool.and_eq_true] at h
    exact h.1.1.1.2
  have hX := strict_choice r.N hn c
  simp only [choiceU, asU]
  rw [(correlate_noRights _ hX.1).1, soften_strict _ hX.2]
  show (choiceDoc r.N.D c).1.soft.E = _
  rw [show (choiceDoc r.N.D c).1.soft.E = r.N.D.frame.soft.E from (keepsFrame_build _ _ _).E, r.hN, r.b.frame]
  rfl

/-- The choice's document as the layered branch's source (no extra base premise on the norms chain): its packages
    are bound to the case's environment id, the choice's document hash and its `E‴_base`. -/
def choiceLayered (r : AdmittedND) (c : Choice) (wfc : VE.NormDefaults.WellFormedU (choiceU r.N c) = true) :
    Except String {L : VE.NormDefaults.Wire.LayeredU // L.U = choiceU r.N c} := do
  let re := r.b.a.re
  let U := choiceU r.N c
  let profiles := VE.NormDefaults.Wire.profilesOf re.lowerJson
  let baseEnv ← VE.NormDefaults.Wire.baseEnvironmentJsonU re.lowerJson U
  let envId ← VE.Route.Wire.environmentId profiles (← VE.NormDefaults.Wire.canonicalEnvironmentJsonU re.lowerJson)
  let docHash ← VE.Readings.Run.choiceHash r.b (VE.Readings.Run.choiceJsons r.b.a.doc.itemsJ c)
  pure ⟨⟨"norms@0", correlate (choiceDoc r.N.D c).1, U, wfc, [], 0,
    VE.Norms.Replay.baseModelVocabulary re.se.ne U.D,
    VE.Norms.Replay.baseModel_valid re.se.ne U.D (choiceU_E r c), baseEnv, envId, docHash⟩, rfl⟩

/-- The conflict packages of the case: `conflict.packages` for a certificate, else `packages`. -/
def conflictPackages (inner : Json) : Json :=
  match inner.getObjVal? "conflict" with
  | .ok c => c.getObjValD "packages"
  | .error _ => inner.getObjValD "packages"

/-- Runs `ndChoiceText` on its choice (after S2a's chain check on the filled choice; its text is `ndDocText`'s
    suffixed, as `ndChoiceText` words it) and refuses with its text, so `wfc` is checked for every replayed choice, one beyond the 64 of 4.1 step 5 included (SR1). The certificates are
    the conflict packages decoded against the choice's targets and bindings. -/
def replayChoiceAt (r : AdmittedND) (c : Choice) (inner : Json) :
    Except String (ChoiceReplayU × {L : VE.NormDefaults.Wire.LayeredU // L.U = choiceU r.N c}) := do
  if hc : compatible r.N.D c = true then
    if let some e := choiceChainText (fillDoc r.N) c then throw e
    match hn : ndDocText r.b.a.re (choiceU r.N c) with
    | some e => throw (e ++ " under " ++ choiceText r.N.D c)
    | none =>
      let hw := wellFormedU_of_ndDocText hn
      let L ← choiceLayered r c hw
      pure (⟨r, c, hc, hw, (targets (VE.NormDefaults.fill L.1.U)).map
        (VE.NormDefaults.Wire.decodePackageX L.1 (conflictPackages inner))⟩, L)
  else throw "InvalidInput: the choice is not a compatible complete choice"

def replayChoiceU (j : Lean.Json) : Except String ChoiceReplayU := do
  let r ← admitND (← j.getObjVal? "environment") (← j.getObjVal? "document")
  let c ← decodeChoice (j.getObjValD "choice")
  pure (← replayChoiceAt r c (j.getObjValD "inner")).1

theorem readings_wire_nd_choice_conflict (j : Lean.Json) (x : ChoiceReplayU) (h : replayChoiceU j = .ok x)
    (hv : VE.NormDefaults.Wire.conflictFreeCheckU (choiceU x.r.N x.c) x.certs = true) :
  Compatible x.r.N.D x.c ∧ VE.NormDefaults.ConflictFreeU.{u} (choiceU x.r.N x.c) := by
  -- The replay carries the facts: the choice compatible, its filled document `WellFormedU`.
  have _ := h
  exact ⟨x.hc, VE.NormDefaults.Wire.conflictFreeCheckU_sound _ (VE.NormDefaults.fill_wellFormed _ x.wfc) _ hv⟩

theorem readings_wire_nd_choice_entails (j : Lean.Json) (x : ChoiceReplayU) (h : replayChoiceU j = .ok x)
    (Γ : List VE.Formula) (φ : VE.Formula) (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (envAt (VE.NormDefaults.fill (choiceU x.r.N x.c))
            (size (VE.NormDefaults.fill (choiceU x.r.N x.c))))
            (VE.NormDefaults.Wire.premisesU (choiceU x.r.N x.c) ((choiceDoc x.r.N.D x.c).2 ++ Γ)) φ cert = true)
    (hcf : VE.NormDefaults.Wire.conflictFreeCheckU (choiceU x.r.N x.c) x.certs = true) :
  VE.NormDefaults.ConflictFreeU.{u} (choiceU x.r.N x.c) ∧
    EntailsU.{u} (choiceU x.r.N x.c) ((choiceDoc x.r.N.D x.c).2 ++ Γ) φ :=
  ⟨(readings_wire_nd_choice_conflict j x h hcf).2, VE.NormDefaults.acceptanceU _ x.wfc _ φ cert hv⟩

end VE.Readings.Wire

/-! ## The runners under the completion -/

namespace VE.Readings.Run
open Lean
open VE.Readings
open VE.Readings.Wire
open VE.Norms (envAt size targets)
open VE.NormDefaults (fill)

/-- `readings-elaborate` under the completion: no verdict over no reading (4.1 step 3), then the enumerated row with
    the completion's finding (`elaborateFields`). Step 5 ran in admission. -/
def runElaborateND (id : String) (r : AdmittedND) : Except String Json := do
  if routeOf true r.N.D == .enumerated && (choices r.N.D).isEmpty then throw (unsatText r.N.D)
  pure (okWith id (elaborateFields true r.b.a.re.se.ne.rv.vocabulary.predicates.length r.N.D))

/-- The case's own premises and conclusion over the complete environment of `fill U`, the regenerated assertions of
    the choice first. -/
def ndFormulas (x : ChoiceReplayU) (inner : Json) : Except String (List VE.Formula × VE.Formula) := do
  let E := envAt (fill (choiceU x.r.N x.c)) (size (fill (choiceU x.r.N x.c)))
  -- Absent premises are none, as `runChoice` sends the regenerated assertions alone.
  let (Γ, φ) ← choiceFormulas E (if inner.getObjValD "premises" == .null then inner.setObjVal! "premises" (.arr #[])
    else inner)
  pure ((choiceDoc x.r.N.D x.c).2 ++ Γ, φ)

/-- A certificate of the choice's filled document, bound as the norm-defaults route binds it: the regenerated
    premises of `fill U` and the choice's assertions, then the case's premises as written. The answer is the
    norm-defaults route's (`valid`, the number of premises); `runChoiceND` adds the conflict status. -/
def ndCertificate (x : ChoiceReplayU) (inner : Json) : Except String (List (String × Json)) := do
  let re := x.r.b.a.re
  let U := choiceU x.r.N x.c
  unless (inner.getObjVal? "conflict") matches .ok (.obj _) do
    throw "InvalidInput: a reading's certificate needs the choice's conflict packages"
  let (Γ, φ) ← ndFormulas x inner
  let cert ← VE.CertificateWire.decodeCertificate (← inner.getObjVal? "certificate")
  let own ← match inner.getObjValD "premises" with
    | .null => pure []
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: premises must be an array"
  VE.Route.Wire.bindingOk (VE.NormDefaults.Wire.profilesOf re.lowerJson)
    (← VE.NormDefaults.Wire.canonicalEnvironmentJsonU re.lowerJson)
    ((VE.NormDefaults.Wire.premisesU U (choiceDoc x.r.N.D x.c).2).map encF ++ own)
    (inner.getObjValD "conclusion") cert.environment_id cert.premise_meaning_ids cert.conclusion_meaning_id
  let valid := VE.Tableau.checkCertificate (envAt (fill U) (size (fill U))) (VE.NormDefaults.Wire.premisesU U Γ) φ cert
  pure [("valid", .bool valid), ("premises", toJson (VE.NormDefaults.Wire.premisesU U Γ).length)]

/-- A base model of the choice's document with a separate `filling` (`modelCheckU`). -/
def ndChoiceModel (x : ChoiceReplayU) (L : VE.NormDefaults.Wire.LayeredU) (id : String) (inner : Json)
    (assertions : Nat) : Except String Json := do
  let S ← VE.NormDefaults.Wire.situationX L (← inner.getObjVal? "model")
  let F ← VE.NormDefaults.Wire.decodeFilling L.U S.M (inner.getObjValD "filling")
  let (Γ, φ) ← ndFormulas x inner
  let U := L.U
  let res := VE.NormDefaults.modelCheckU U S.M F Γ φ
  pure (modelAnswer id res.1 res.2
    (Γ.map (fun a => (VE.Norms.subst (fill U).T (size (fill U)) a).eval (S.M.withFill F) [])) assertions)

/-- The inner kinds of a choice under the completion (plan 3.4), answered on `choiceU N c`: the layered kinds by the
    norm-defaults branch's own dispatch (`layeredCase`), so each answer is that route's on the choice's document; any
    other kind is the norm-defaults route's refusal. -/
def ndInner (x : ChoiceReplayU) (L : VE.NormDefaults.Wire.LayeredU) (id kind : String) (inner : Json) (assertions : Nat) : Except String Json := do
  if let some a ← VE.NormDefaults.Wire.layeredCase L id kind inner then return a
  if kind == "norm-defaults-certificate" then return VE.Route.Wire.ok id (← ndCertificate x inner)
  if kind == "choice-model" then return ← ndChoiceModel x L id inner assertions
  throw s!"UnsupportedProfile: case kind {kind} is not available on the norm-defaults route"

/-- `readings-choice` under the completion: the choice replayed (`replayChoiceAt`), then its inner kind on the
    regenerated `choiceU N c`. The answer's shape is `runChoice`'s: the choice, its document hash, the number of its
    regenerated assertions, the inner answer (an error row when the inner case is refused), and for a certificate
    the conflict status and acceptance. -/
def runChoiceND (id : String) (r : AdmittedND) (j : Json) : Except String Json := do
  let c ← decodeChoice (j.getObjValD "choice")
  let inner := j.getObjValD "inner"
  let (x, L) ← replayChoiceAt r c inner
  let kind := match inner.getObjValD "kind" with | .str k => k | _ => ""
  let units := choiceJsons r.b.a.doc.itemsJ c
  let assertions := (choiceDoc r.N.D c).2.length
  let answer := match ndInner x L.1 id kind inner assertions with
    | .ok a => a
    | .error e => Json.mkObj [("id", .str id), ("status", .str "error"), ("error", .str e)]
  -- As `runChoice`: a certificate is accepted only with the choice's conflict packages CONFLICT-FREE (S2a 14.8),
  -- here `conflictFreeCheckU` on the replayed certificates, the hypothesis of `readings_wire_nd_choice_entails`.
  let free := VE.NormDefaults.Wire.conflictFreeCheckU (choiceU x.r.N x.c) x.certs
  let valid := answer.getObjValD "valid" == .bool true
  let accepted := if kind == "norm-defaults-certificate" then
      [("conflict_free", .bool free), ("accepted", .bool (free && valid))]
    else []
  pure (okWith id ([("choice", choiceJson c), ("document_hash", .str (← choiceHash r.b units)),
    ("assertions", toJson assertions), ("inner", answer)] ++ accepted))

end VE.Readings.Run
