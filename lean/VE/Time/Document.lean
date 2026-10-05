import VE.Time.Wire
import VE.Route.Admission

/-! W6a document admission (units-schema §3.2, PLAN-EXPAND2 3.6 on the quantity route).

A quantity document is the P0 admission input with every formula replaced by a
submitted `ve-quantity@1` statement: units carry `content` quantities, reading
sets carry quantity readings, and claim-graph nodes carry a `quantity`. Every
statement passes `decodeQuantity` (Lean regeneration and admission before
erasure). Deductions carry a `ve-quantity-certificate@1`, checked by
`checkW6Certificate` against the annotated meaning ids of exactly the premise
nodes and the node, so the report binds the annotated statements.

The provenance rules are the base route's (`VE.Route.Admission`): asserted leaves
formalise asserted units, quoted units enter only through bridge leaves naming
them, and open-term, reading and narrowing leaves name declared objects. The
units-only layer generates no Background, so no background leaf is admitted.

Citations are bound by checked lemmas. A lemma carries its conclusion, its
transitive leaves (labelled statements, none a citation) and a
`ve-quantity-certificate@1` from exactly those leaves, in order, to the
conclusion; decoding checks the certificate. A `cite:<bundle>/<lemma>` leaf is
admitted when it states that lemma's conclusion, and the report must carry each
of the lemma's leaves with its label, as on the base route.

`admit_quantity_report_sound`: in every admissible tagged structure where the
report's non-citation assumptions hold, its root holds; every assumption is a
decoded leaf with exactly its label satisfying its leaf rule; reading choices
agree. -/
namespace VE.Time.Document
universe v
open Lean
open VE.Bridge (exactFields fields stringField strings)
open VE.Time.Wire
open VE.Route.Admission (Kind decodeKind renderKind parseLabel token compatible agentMatches)

def graphRejected : String :=
  "graph rejected: cycle, duplicate name, dangling premise, ill-typed claim or invalid certificate"

def isCite (label : String) : Bool :=
  match parseLabel label with
  | some (.cite _ _) => true
  | _ => false

structure QUnit where
  id : String
  start : Nat
  stop : Nat
  kind : Kind
  content : Option QFormula

structure QReadingSet where
  id : String
  version : Nat
  readings : List QFormula

/-- A checked lemma: its certificate establishes the conclusion from exactly its
leaves, in order, bound to their annotated meaning ids. No leaf is a citation. -/
structure QLemma (w : W6Env) where
  name : String
  conclusion : Admission w
  leaves : List (Admission w × String)
  certificate : W6Certificate
  transitive : leaves.all (fun l => !isCite l.2) = true
  checked : checkW6Certificate (leaves.map (·.1)) conclusion certificate = .ok true

structure QDoc (w : W6Env) where
  units : List QUnit
  lemmas : List (QLemma w)
  openTerms : List String
  readingSets : List QReadingSet
  narrowings : List String

/-- A decoded node: an admitted statement, its label, the unit it formalises
(if any) and its deduction (if any). -/
structure QNode (w : W6Env) where
  name : String
  adm : Admission w
  label : String
  unit : Option String
  deduction : Option (List String × W6Certificate)

/-- The content of a `readings:<set>@<version>:all` leaf. -/
def qdisjunction : List QFormula → Option QFormula
  | [] => none
  | [a] => some a
  | a :: as => (qdisjunction as).map (.or a)

/-! ## The admission rules, as independent propositions -/

def AssertedUnit {w : W6Env} (D : QDoc w) (u : String) (φ : QFormula) : Prop :=
  ∃ x ∈ D.units, x.id = u ∧ x.kind = .asserted ∧ x.content = some φ

def QuotedUnit {w : W6Env} (D : QDoc w) (agent u : String) (φ : QFormula) : Prop :=
  ∃ x ∈ D.units, x.id = u ∧ x.kind.quoted = true ∧ x.content = some φ ∧
    agentMatches x.kind agent = true

def ReadingContent {w : W6Env} (D : QDoc w) (s : String) (ver : Nat) (c : Option Nat)
    (φ : QFormula) : Prop :=
  ∃ rs ∈ D.readingSets, rs.id = s ∧ rs.version = ver ∧
    match c with
    | some i => rs.readings[i]? = some φ
    | none => qdisjunction rs.readings = some φ

/-- The provenance rule for an undischarged leaf; background leaves are never
admitted on this route, and a citation states a checked lemma's conclusion. -/
def LeafAdmitted {w : W6Env} (D : QDoc w) (n : QNode w) : Prop :=
  match parseLabel n.label with
  | some .asserted => ∃ u, n.unit = some u ∧ AssertedUnit D u n.adm.formula
  | some (.bridge a u) => (n.unit = none ∨ n.unit = some u) ∧ QuotedUnit D a u n.adm.formula
  | some (.cite b l) => n.unit = none ∧
      ∃ m ∈ D.lemmas, m.name = b ++ "/" ++ l ∧ m.conclusion.formula = n.adm.formula
  | some (.openTerm t) => n.unit = none ∧ t ∈ D.openTerms
  | some (.readings s ver c) => n.unit = none ∧ ReadingContent D s ver c n.adm.formula
  | some (.narrowing m) => n.unit = none ∧ m ∈ D.narrowings
  | _ => False

/-- A deduction is an asserted claim; a unit it names is asserted with exactly
its statement. -/
def NodeAdmitted {w : W6Env} (D : QDoc w) (n : QNode w) : Prop :=
  match n.deduction with
  | some _ => n.label = "asserted" ∧ ∀ u, n.unit = some u → AssertedUnit D u n.adm.formula
  | none => LeafAdmitted D n

/-- The label cites this lemma. -/
def citesLemma {w : W6Env} (label : String) (m : QLemma w) : Bool :=
  match parseLabel label with
  | some (.cite b l) => m.name == b ++ "/" ++ l
  | _ => false

instance {w : W6Env} (D : QDoc w) (u : String) (φ : QFormula) : Decidable (AssertedUnit D u φ) := by
  unfold AssertedUnit; infer_instance

instance {w : W6Env} (D : QDoc w) (a u : String) (φ : QFormula) :
    Decidable (QuotedUnit D a u φ) := by
  unfold QuotedUnit; infer_instance

instance {w : W6Env} (D : QDoc w) (s : String) (ver : Nat) (c : Option Nat) (φ : QFormula) :
    Decidable (ReadingContent D s ver c φ) := by
  unfold ReadingContent
  cases c <;> infer_instance

instance {w : W6Env} (D : QDoc w) (n : QNode w) : Decidable (LeafAdmitted D n) := by
  unfold LeafAdmitted
  split <;> infer_instance

instance {w : W6Env} (D : QDoc w) (n : QNode w) : Decidable (NodeAdmitted D n) := by
  unfold NodeAdmitted
  split
  · exact decidable_of_iff (n.label = "asserted" ∧
      ∀ u ∈ n.unit.toList, AssertedUnit D u n.adm.formula) (by simp)
  · infer_instance

def unitOf {w : W6Env} (D : QDoc w) (u : String) : Option QUnit := D.units.find? (fun x => x.id == u)

/-- The base route's diagnostics (untrusted text). -/
def nodeDiagnostic {w : W6Env} (D : QDoc w) (n : QNode w) : String :=
  let bridgeNaming := match parseLabel n.label, n.deduction with
    | some (.bridge _ u), none => some u
    | _, _ => none
  match n.unit.bind (unitOf D) with
  | some x =>
    if x.kind.quoted && bridgeNaming != some x.id then
      s!"AdmissionError: quoted content of unit {x.id} is used without a bridge leaf"
    else s!"AdmissionError: node {n.name} is not admitted under label {n.label}"
  | none =>
    match parseLabel n.label with
    | none => s!"AdmissionError: invalid label {n.label}"
    | some _ => s!"AdmissionError: node {n.name} is not admitted under label {n.label}"

def admitNodes {w : W6Env} (D : QDoc w) (ns : List (QNode w)) : Except String Unit :=
  match ns.find? (fun n => !decide (NodeAdmitted D n)) with
  | some n => .error (nodeDiagnostic D n)
  | none => .ok ()

theorem admitNodes_ok {w : W6Env} (D : QDoc w) (ns : List (QNode w)) (h : admitNodes D ns = .ok ()) :
    ∀ n ∈ ns, NodeAdmitted D n := by
  unfold admitNodes at h
  split at h
  · cases h
  · rename_i hf
    intro n hn
    have := List.find?_eq_none.mp hf n hn
    simpa using this

/-! ## The claim graph -/

/-- A checked node with the leaves it rests on, as `(name, statement, label)`. -/
structure Entry (w : W6Env) where
  name : String
  adm : Admission w
  label : String
  assumptions : List (String × Admission w × String)

/-- The entry's statement holds in every admissible tagged structure in which
its leaves hold. -/
def Entry.Sound {w : W6Env} (e : Entry w) : Prop :=
  ∀ (α : Type v) (T : TStructure α), T.Admissible w.vocab.env →
    (∀ x ∈ e.assumptions, x.2.1.formula.tdenote T []) → e.adm.formula.tdenote T []

def lookupEntry {w : W6Env} (acc : List (Entry w)) (p : String) : Except String (Entry w) :=
  match acc.find? (fun e => e.name == p) with
  | some e => .ok e
  | none => .error graphRejected

def leafEntry {w : W6Env} (n : QNode w) : Entry w := ⟨n.name, n.adm, n.label, [(n.name, n.adm, n.label)]⟩

/-- Nodes in submitted order: names are unique, premises name earlier nodes,
and each certificate is checked against exactly its premise statements. -/
def checkGraph (w : W6Env) : List (QNode w) → List (Entry w) → Except String (List (Entry w))
  | [], acc => .ok acc
  | n :: ns, acc =>
    if acc.any (fun e => e.name == n.name) then .error graphRejected else
    match n.deduction with
    | none => checkGraph w ns (acc ++ [leafEntry n])
    | some (ps, cert) =>
      match ps.mapM (lookupEntry acc) with
      | .error e => .error e
      | .ok children =>
        match checkW6Certificate (children.map (·.adm)) n.adm cert with
        | .ok true => checkGraph w ns
            (acc ++ [⟨n.name, n.adm, n.label, children.flatMap (·.assumptions)⟩])
        | _ => .error graphRejected

theorem lookupEntry_mem {w : W6Env} {acc : List (Entry w)} {p : String} {e : Entry w}
    (h : lookupEntry acc p = .ok e) : e ∈ acc := by
  unfold lookupEntry at h
  split at h
  · rename_i x hx
    cases h
    exact List.mem_of_find?_eq_some hx
  · cases h

theorem mapM_lookup_mem {w : W6Env} {acc : List (Entry w)} :
    ∀ {ps : List String} {cs : List (Entry w)}, ps.mapM (lookupEntry acc) = .ok cs → ∀ c ∈ cs, c ∈ acc
  | [], cs, h => by
    simp only [List.mapM_nil, pure, Except.pure, Except.ok.injEq] at h
    subst h
    simp
  | p :: ps, cs, h => by
    simp only [List.mapM_cons, bind, Except.bind] at h
    split at h
    · cases h
    · rename_i e he
      split at h
      · cases h
      · rename_i es hes
        simp only [pure, Except.pure, Except.ok.injEq] at h
        subst h
        intro c hc
        rcases List.mem_cons.mp hc with rfl | hc
        · exact lookupEntry_mem he
        · exact mapM_lookup_mem hes c hc

/-- The graph invariant: each entry is a submitted node, rests only on
submitted leaves, and is sound. -/
def Good {w : W6Env} (all : List (QNode w)) (e : Entry w) : Prop :=
  (∃ n ∈ all, n.name = e.name ∧ n.adm = e.adm ∧ n.label = e.label) ∧
  (∀ x ∈ e.assumptions, ∃ n ∈ all, n.deduction = none ∧ (n.name, n.adm, n.label) = x) ∧
  Entry.Sound.{v} e

theorem checkGraph_good {w : W6Env} (all : List (QNode w)) :
    ∀ (ns : List (QNode w)) (acc out : List (Entry w)), (∀ n ∈ ns, n ∈ all) →
      (∀ e ∈ acc, Good.{v} all e) → checkGraph w ns acc = .ok out → ∀ e ∈ out, Good.{v} all e
  | [], acc, out, _, hacc, h => by
    simp only [checkGraph, Except.ok.injEq] at h
    subst h
    exact hacc
  | n :: ns, acc, out, hns, hacc, h => by
    have hn : n ∈ all := hns n (List.mem_cons_self ..)
    have hrest : ∀ m ∈ ns, m ∈ all := fun m hm => hns m (List.mem_cons_of_mem _ hm)
    simp only [checkGraph] at h
    split at h
    · cases h
    · split at h
      · rename_i hd
        refine checkGraph_good all ns _ out hrest ?_ h
        intro e he
        rcases List.mem_append.mp he with he | he
        · exact hacc e he
        · simp only [List.mem_singleton] at he
          subst he
          refine ⟨⟨n, hn, rfl, rfl, rfl⟩, ?_, ?_⟩
          · intro x hx
            simp only [leafEntry, List.mem_singleton] at hx
            exact ⟨n, hn, hd, hx.symm⟩
          · intro α T _ hx
            exact hx (n.name, n.adm, n.label) (by simp [leafEntry])
      · rename_i ps cert _
        split at h
        · cases h
        · rename_i children hch
          split at h
          · rename_i hcert
            refine checkGraph_good all ns _ out hrest ?_ h
            intro e he
            rcases List.mem_append.mp he with he | he
            · exact hacc e he
            · simp only [List.mem_singleton] at he
              subst he
              have hmem := mapM_lookup_mem hch
              refine ⟨⟨n, hn, rfl, rfl, rfl⟩, ?_, ?_⟩
              · intro x hx
                obtain ⟨c, hc, hxc⟩ := List.mem_flatMap.mp hx
                exact (hacc c (hmem c hc)).2.1 x hxc
              · intro α T hT hx
                have hent := (checkW6Certificate_sound.{v} _ _ _ hcert).2.2.2
                apply hent α T hT
                intro a ha
                obtain ⟨b, hb, rfl⟩ := List.mem_map.mp ha
                obtain ⟨c, hc, rfl⟩ := List.mem_map.mp hb
                exact (hacc c (hmem c hc)).2.2 α T hT
                  (fun x hxc => hx x (List.mem_flatMap.mpr ⟨c, hc, hxc⟩))
          · cases h

/-! ## Admission -/

def ChoicesCompatible {w : W6Env} (e : Entry w) : Prop :=
  ∀ a ∈ e.assumptions, ∀ b ∈ e.assumptions, compatible a.2.2 b.2.2 = true

instance {w : W6Env} (e : Entry w) : Decidable (ChoicesCompatible e) := by
  unfold ChoicesCompatible; infer_instance

/-- Every cited lemma's leaves are in the report with their labels. -/
def CitationsClosed {w : W6Env} (D : QDoc w) (e : Entry w) : Prop :=
  ∀ x ∈ e.assumptions, ∀ m ∈ D.lemmas, citesLemma x.2.2 m = true →
    ∀ l ∈ m.leaves, ∃ y ∈ e.assumptions, y.2.1.formula = l.1.formula ∧ y.2.2 = l.2

instance {w : W6Env} (D : QDoc w) (e : Entry w) : Decidable (CitationsClosed D e) := by
  unfold CitationsClosed; infer_instance

/-- The entry's statement holds in every admissible tagged structure in which
its non-citation leaves hold. -/
def Entry.SoundOverLeaves {w : W6Env} (e : Entry w) : Prop :=
  ∀ (α : Type v) (T : TStructure α), T.Admissible w.vocab.env →
    (∀ x ∈ e.assumptions, isCite x.2.2 = false → x.2.1.formula.tdenote T []) →
      e.adm.formula.tdenote T []

theorem isCite_parse {s : String} (h : isCite s = true) : ∃ b l, parseLabel s = some (.cite b l) := by
  unfold isCite at h
  split at h
  · rename_i b l hp
    exact ⟨b, l, hp⟩
  · cases h

/-- A citation leaf is discharged by its checked lemma, whose leaves the report
carries with their labels; so the root rests only on non-citation leaves. -/
theorem cites_discharged {w : W6Env} (D : QDoc w) (nodes : List (QNode w)) (e : Entry w)
    (hleaves : ∀ x ∈ e.assumptions, ∃ n ∈ nodes, n.deduction = none ∧
      (n.name, n.adm, n.label) = x ∧ LeafAdmitted D n)
    (hclosed : CitationsClosed D e) (hsound : Entry.Sound.{v} e) : Entry.SoundOverLeaves.{v} e := by
  intro α T hT hnc
  apply hsound α T hT
  intro x hx
  obtain ⟨n, _, _, hnx, hadm⟩ := hleaves x hx
  subst hnx
  cases hcite : isCite n.label
  · exact hnc _ hx hcite
  · obtain ⟨b, l, hp⟩ := isCite_parse hcite
    show n.adm.formula.tdenote T []
    unfold LeafAdmitted at hadm
    rw [hp] at hadm
    obtain ⟨_, m, hm, hmn, hmc⟩ := hadm
    have hcites : citesLemma n.label m = true := by
      unfold citesLemma
      rw [hp, hmn]
      simp
    have hent := (checkW6Certificate_sound.{v} _ _ _ m.checked).2.2.2
    rw [← hmc]
    apply hent α T hT
    intro a ha
    obtain ⟨b', hb, rfl⟩ := List.mem_map.mp ha
    obtain ⟨leaf, hleaf, rfl⟩ := List.mem_map.mp hb
    obtain ⟨y, hy, hyf, hyl⟩ := hclosed _ hx m hm hcites leaf hleaf
    have htr : isCite leaf.2 = false := by
      have := List.all_eq_true.mp m.transitive leaf hleaf
      simpa using this
    rw [← hyf]
    exact hnc y hy (by rw [hyl]; exact htr)

structure Admitted (w : W6Env) where
  doc : QDoc w
  nodes : List (QNode w)
  entries : List (Entry w)
  root : Entry w

/-- The logical checks on a decoded document. -/
def admitDecoded (w : W6Env) (D : QDoc w) (nodes : List (QNode w)) (root : String) :
    Except String (Admitted w) :=
  match admitNodes D nodes with
  | .error e => .error e
  | .ok () =>
    match checkGraph w nodes [] with
    | .error e => .error e
    | .ok entries =>
      match entries.find? (fun e => e.name == root) with
      | none => .error graphRejected
      | some r =>
        if decide (CitationsClosed D r) then
          if decide (ChoicesCompatible r) then .ok ⟨D, nodes, entries, r⟩
          else .error "AdmissionError: incompatible reading choices"
        else .error "AdmissionError: a cited lemma's leaves are missing from the report"

/-- **W6 report soundness.** An admitted quantity document's report root is a
submitted node named by the graph root; in every admissible tagged structure
where the report's assumptions hold, the root statement holds, and it holds
already where the non-citation assumptions hold; every assumption is a
submitted leaf with exactly its statement and label, satisfying its provenance
rule; cited lemmas' leaves are in the report; every node satisfies its
admission rule; and reading choices are compatible. -/
theorem admitDecoded_sound {w : W6Env} (D : QDoc w) (nodes : List (QNode w)) (root : String)
    (res : Admitted w) (h : admitDecoded w D nodes root = .ok res) :
    res.doc = D ∧ res.nodes = nodes ∧ res.root.name = root ∧
    (∃ n ∈ nodes, n.name = root ∧ n.adm = res.root.adm ∧ n.label = res.root.label) ∧
    (∀ n ∈ nodes, NodeAdmitted D n) ∧
    (∀ x ∈ res.root.assumptions, ∃ n ∈ nodes, n.deduction = none ∧
      (n.name, n.adm, n.label) = x ∧ LeafAdmitted D n) ∧
    CitationsClosed D res.root ∧ ChoicesCompatible res.root ∧ Entry.Sound.{v} res.root ∧
    Entry.SoundOverLeaves.{v} res.root := by
  unfold admitDecoded at h
  split at h
  · cases h
  · rename_i hadm
    split at h
    · cases h
    · rename_i entries hg
      split at h
      · cases h
      · rename_i r hr
        split at h
        · rename_i hcl
          split at h
          · rename_i hc
            cases h
            have hnodes := admitNodes_ok D nodes hadm
            have hgood := checkGraph_good.{v} nodes nodes [] entries (fun n hn => hn)
              (fun e he => by cases he) hg r (List.mem_of_find?_eq_some hr)
            have hname : r.name = root := by
              simpa using List.find?_some hr
            obtain ⟨⟨n, hn, hnn, hna, hnl⟩, hleaves, hsound⟩ := hgood
            have hadmitted : ∀ x ∈ r.assumptions, ∃ n ∈ nodes, n.deduction = none ∧
                (n.name, n.adm, n.label) = x ∧ LeafAdmitted D n := by
              intro x hx
              obtain ⟨m, hm, hmd, hmx⟩ := hleaves x hx
              refine ⟨m, hm, hmd, hmx, ?_⟩
              have := hnodes m hm
              unfold NodeAdmitted at this
              rw [hmd] at this
              exact this
            exact ⟨rfl, rfl, hname, ⟨n, hn, hnn.trans hname, hna, hnl⟩, hnodes, hadmitted,
              of_decide_eq_true hcl, of_decide_eq_true hc, hsound,
              cites_discharged.{v} D nodes r hadmitted (of_decide_eq_true hcl) hsound⟩
          · cases h
        · cases h

/-! ## Decoding -/

def decodeUnit (w : W6Env) (j : Json) : Except String QUnit := do
  shape j ["id", "span", "kind"] ["content"]
  let id ← stringField j "id"
  unless token id do throw s!"invalid unit id {id}"
  let (start, stop) ← match (← (← j.getObjVal? "span").getArr?).toList with
    | [a, b] => pure (← a.getNat?, ← b.getNat?)
    | _ => throw "invalid span"
  unless start ≤ stop do throw "invalid span"
  let kind ← decodeKind 16 (← j.getObjVal? "kind")
  let content ← match j.getObjVal? "content" with
    | .ok q => do pure (some (← decodeQuantity w q).formula)
    | .error _ => pure none
  pure ⟨id, start, stop, kind, content⟩

def sortedSpans : List QUnit → Bool
  | a :: b :: rest => a.stop ≤ b.start && sortedSpans (b :: rest)
  | _ => true

def decodeReadingSet (w : W6Env) (j : Json) : Except String QReadingSet := do
  exactFields j ["id", "version", "readings"]
  let id ← stringField j "id"
  unless token id do throw s!"invalid reading set id {id}"
  let version ← (← j.getObjVal? "version").getNat?
  let readings ← (← (← j.getObjVal? "readings").getArr?).toList.mapM
    (fun q => do pure (← decodeQuantity w q).formula)
  unless !readings.isEmpty && readings.length ≤ 64 do throw "reading sets hold 1 to 64 readings"
  pure ⟨id, version, readings⟩

def tokenList (j : Json) : Except String (List String) := do
  let xs ← strings j
  unless xs.all token do throw "invalid name"
  pure xs

def decodeNode (w : W6Env) (j : Json) : Except String (QNode w) := do
  shape j ["name", "quantity"] ["label", "unit", "premises", "certificate"]
  let name ← stringField j "name"
  let label ← match j.getObjVal? "label" with
    | .ok l => do
      let s ← l.getStr?
      if s == "asserted" then throw "non-canonical label: the default label asserted is omitted"
      pure s
    | .error _ => pure "asserted"
  let adm ← decodeQuantity w (← j.getObjVal? "quantity")
  let unit ← match j.getObjVal? "unit" with
    | .ok u => some <$> u.getStr?
    | .error _ => pure none
  let deduction ← match j.getObjVal? "premises", j.getObjVal? "certificate" with
    | .ok ps, .ok c => pure (some (← strings ps, ← decodeW6Certificate c))
    | .error _, .error _ => pure none
    | _, _ => throw "premises and certificate come together"
  pure ⟨name, adm, label, unit, deduction⟩

/-- A lemma leaf: a labelled statement; a citation cannot be a leaf. -/
def decodeLeaf (w : W6Env) (j : Json) : Except String (Admission w × String) := do
  exactFields j ["quantity", "label"]
  let l ← stringField j "label"
  match parseLabel l with
  | none => throw s!"AdmissionError: invalid label {l}"
  | some (.cite _ _) => throw "AdmissionError: lemma leaves must be transitive (no cite labels)"
  | some _ => pure (← decodeQuantity w (← j.getObjVal? "quantity"), l)

def lemmaUnchecked (name : String) : String :=
  s!"AdmissionError: lemma {name} is not established by its certificate"

/-- Decode a lemma and check its certificate against exactly its leaves. -/
def decodeLemma (w : W6Env) (j : Json) : Except String (QLemma w) := do
  exactFields j ["name", "conclusion", "leaves", "certificate"]
  let name ← stringField j "name"
  match parseLabel ("cite:" ++ name) with
  | some (.cite _ _) => pure ()
  | _ => throw s!"invalid lemma name {name}"
  let c ← decodeQuantity w (← j.getObjVal? "conclusion")
  let leaves ← (← (← j.getObjVal? "leaves").getArr?).toList.mapM (decodeLeaf w)
  unless leaves.length ≤ 1000 do throw "ResourceLimit: lemma leaves"
  let cert ← decodeW6Certificate (← j.getObjVal? "certificate")
  if ht : leaves.all (fun l => !isCite l.2) = true then
    match hc : checkW6Certificate (leaves.map (·.1)) c cert with
    | .ok true => pure ⟨name, c, leaves, cert, ht, hc⟩
    | _ => throw (lemmaUnchecked name)
  else throw "AdmissionError: lemma leaves must be transitive (no cite labels)"

def optionalArray (j : Json) (key : String) : Except String (List Json) :=
  match j.getObjVal? key with
  | .ok v => v.getArr?.map Array.toList
  | .error _ => pure []

/-- Decode the document, its graph nodes and root. -/
def decodeDocument (w : W6Env) (j : Json) : Except String (QDoc w × List (QNode w) × String) := do
  unless w.profiles.contains "documents@1" do
    throw "UnsupportedProfile: quantity documents require documents@1"
  shape j ["units", "graph"] ["lemmas", "open_terms", "reading_sets", "narrowings"]
  let units ← (← (← j.getObjVal? "units").getArr?).toList.mapM (decodeUnit w)
  if units.length > 10000 then throw "ResourceLimit: unit count"
  unless (units.map QUnit.id).eraseDups.length == units.length do throw "duplicate unit id"
  unless sortedSpans units do throw "unit spans must be sorted and non-overlapping"
  let lemmas ← (← optionalArray j "lemmas").mapM (decodeLemma w)
  unless (lemmas.map QLemma.name).eraseDups.length == lemmas.length do throw "duplicate lemma"
  let openTerms ← tokenList (Json.arr (← optionalArray j "open_terms").toArray)
  let readingSets ← (← optionalArray j "reading_sets").mapM (decodeReadingSet w)
  unless (readingSets.map (fun r => (r.id, r.version))).eraseDups.length == readingSets.length do
    throw "duplicate reading set version"
  let narrowings ← tokenList (Json.arr (← optionalArray j "narrowings").toArray)
  let graphJson ← j.getObjVal? "graph"
  exactFields graphJson ["root", "nodes"]
  let root ← stringField graphJson "root"
  let nodeArray ← (← graphJson.getObjVal? "nodes").getArr?
  if nodeArray.size > 1000 then throw "ResourceLimit: graph node count"
  let nodes ← nodeArray.toList.mapM (decodeNode w)
  pure (⟨units, lemmas, openTerms, readingSets, narrowings⟩, nodes, root)

def admitDocument (w : W6Env) (j : Json) : Except String (Admitted w) := do
  let (D, nodes, root) ← decodeDocument w j
  admitDecoded w D nodes root

theorem admit_quantity_report_sound {w : W6Env} (j : Json) (res : Admitted w)
    (h : admitDocument w j = .ok res) :
    (∃ n ∈ res.nodes, n.name = res.root.name ∧ n.adm = res.root.adm ∧ n.label = res.root.label) ∧
    (∀ n ∈ res.nodes, NodeAdmitted res.doc n) ∧
    (∀ x ∈ res.root.assumptions, ∃ n ∈ res.nodes, n.deduction = none ∧
      (n.name, n.adm, n.label) = x ∧ LeafAdmitted res.doc n) ∧
    CitationsClosed res.doc res.root ∧ ChoicesCompatible res.root ∧ Entry.Sound.{v} res.root ∧
    Entry.SoundOverLeaves.{v} res.root := by
  unfold admitDocument at h
  obtain ⟨⟨D, nodes, root⟩, _, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨hd, hn, _, hroot, hnodes, hleaves, hcl, hc, hs, hso⟩ :=
    admitDecoded_sound.{v} D nodes root res h
  rw [hd, hn]
  obtain ⟨n, hmem, hnn, hna, hnl⟩ := hroot
  exact ⟨⟨n, hmem, hnn.trans (by rw [‹res.root.name = root›]), hna, hnl⟩, hnodes, hleaves,
    hcl, hc, hs, hso⟩

/-! ## The runner case -/

def claimJson {w : W6Env} (name : String) (a : Admission w) (label : String) : Json :=
  Json.mkObj ([("name", .str name),
    ("quantity", Json.mkObj [("format", .str "ve-quantity@1"), ("formula", a.Q),
      ("traces", Json.arr #[])]),
    ("meaning_id", .str a.meaningId)] ++
    if label == "asserted" then [] else [("label", .str label)])

def runDocument (w : W6Env) (id : String) (j : Json) : Except String Json := do
  let document ← j.getObjVal? "document"
  let res ← admitDocument w document
  let report := Json.mkObj [("root", claimJson res.root.name res.root.adm res.root.label),
    ("assumptions", Json.arr (res.root.assumptions.map (fun x => claimJson x.1 x.2.1 x.2.2)).toArray)]
  let reportId ← VE.CertificateWire.digest s!"ve-report-{VE.Route.Wire.identityVersion w.profiles}\n"
    (Json.mkObj [("environment_id", .str w.environmentId), ("document", document), ("report", report)])
  pure (ok id [("admitted", .bool true), ("assurance", .str "lean-admitted"), ("report", report),
    ("report_id", .str reportId), ("environment_id", .str w.environmentId),
    ("kinds", Json.arr (res.doc.units.map (fun u => renderKind u.kind)).toArray)])

/-- The `document` case kind of the quantity route (`ve_service` mode `quantity`). -/
def extension : Extension := fun w id kind j =>
  if kind == "document" then runDocument w id j else noExtension w id kind j

end VE.Time.Document
