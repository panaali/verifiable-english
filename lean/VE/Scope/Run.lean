import VE.Scope.English
import VE.Scope.Theorems
import VE.Service.Document

/-! The `ve_service` mode `scope` (docs/spec/scope.md 5.3, SC-1c): the reader's view of a `scope@0` document. For
    every governed unit, the governors that contribute to its rule (id, unit, effect word and reach) and one provenance
    sentence per governor (`VE/Scope/English.lean`). `explainRows` is spec 5.3's definition, read with `govern`'s own
    reaches, and the statements are over it; the runner computes it by `explainFast`, which reads the order, the
    reaches and the base names from tables computed once (`explainFast_eq`). Not here (sc-1cb): the rules an owner
    generates from a unit (`generated`, `explain_generated`) and the rows of a reading set governed per choice. -/

namespace VE.Scope
open Lean
open VE.NormDefaults (forIn_unit_ok)

structure GovRow where
  id : String
  unit : String
  effect : String
  reach : List String
  deriving BEq, Repr

structure Row where
  unit : String
  governors : List GovRow
  provenance : List String     -- Lean's sentences (`VE/Scope/English.lean`, 2.3)
  deriving BEq, Repr

def effectWord : Effect → String
  | .frame _ => "frame" | .reguard _ => "reguard" | .carveOut _ => "carve-out" | .precedes => "precedes"
  | .yields => "yields" | .title => "title"

/-- Every effect word, for the answer's shape (`ResponseShape.Schemas.Scope`). -/
def effectWords : List String :=
  [Effect.frame .null, .reguard .null, .carveOut .null, .precedes, .yields, .title].map effectWord

def contributors (D : SDoc) (u : String) : List Governor :=
  frameOn D u ++ governorsOf D u ++ (ordered D).filter (fun g => match g.effect with
    | .precedes => g.unit == u
    | .yields => coversU D g u
    | _ => false)

/-- `contributors` on the order `os` and the reaches `lv` and `cv` (as `governBody` reads them). -/
def contributorsF (D : SDoc) (os : List Governor) (lv cv : Reach → List String) (u : String) : List Governor :=
  frameOnF D lv u ++ governorsOfF os cv u ++ os.filter (fun g => match g.effect with
    | .precedes => g.unit == u
    | .yields => (cv g.reach).contains u
    | _ => false)

theorem admit_unit (D : SDoc) (h : admitBlock D = .ok ()) (g : Governor) (hg : g ∈ D.governors) :
    g.unit ∈ unitIds D.doc := by
  unfold admitBlock at h
  generalize hA : (forIn D.governors PUnit.unit _ : Except String PUnit) = A at h
  generalize hB : (forIn D.governors PUnit.unit _ : Except String PUnit) = B at h
  simp only [bind, Except.bind, pure, Except.pure] at h
  repeat (split at h; · cases h)
  have ha := (forIn_unit_ok _ ?_ D.governors).mp hA g hg
  · simp only at ha
    split at ha
    · rename_i hc; simpa using hc
    · cases ha
  · intro x r hx
    simp only at hx
    split at hx
    · injection hx with hx; exact hx.symm
    · cases hx

section
variable [Quotes]

/-- Spec 5.3's rows: one per affected unit, in the document's order, after `govern` admits the document. -/
def explainRows (D : SDoc) : Except String (List Row) := do
  let _ ← govern D
  pure ((affected D).map fun u =>
    let gs := contributors D u
    { unit := u,
      governors := gs.map (fun g => ⟨g.id, g.unit, effectWord g.effect, (covered D g.reach).toOption.getD []⟩),
      provenance := gs.map fun g => sentence D (baseName D) u ((covered D g.reach).toOption.getD []).length g })

/-- The rows on the order `os`, the reaches `lv` and `cv` and the base names `bn`. -/
def rowsF (D : SDoc) (os : List Governor) (lv cv : Reach → List String) (bn : String → Option String) : List Row :=
  let aff := (ruleUnits D).filter fun u =>
    isPart (contentOf D.doc u) || !(frameOnF D lv u).isEmpty || !(governorsOfF os cv u).isEmpty ||
    D.governors.any (fun g => match g.effect with
      | .precedes => g.unit == u
      | .yields => (cv g.reach).contains u
      | _ => false)
  aff.map fun u =>
    let gs := contributorsF D os lv cv u
    { unit := u,
      governors := gs.map (fun g => ⟨g.id, g.unit, effectWord g.effect, cv g.reach⟩),
      provenance := gs.map fun g => sentence D bn u (cv g.reach).length g }

/-- The run path: `governFast`'s tables, then the rows on them, each governor unit's base name read once. -/
def explainFast (D : SDoc) : Except String (List Row) := do
  admitBlock D
  let os := ordered D
  let (lv, cv) := fastReads D
  let _ ← governBody D os lv cv
  let name := fun u => ((baseObjF D lv u).toOption.bind fun o => (VE.Readings.Wire.decodeNorm D.re o).toOption).map (·.name)
  pure (rowsF D os lv cv (memo (D.governors.map fun g => (g.unit, name g.unit)) name))

theorem explainFast_eq (D : SDoc) : explainFast D = explainRows D := by
  unfold explainFast explainRows
  rw [fastReads_eq, governBody_slow]
  cases admitBlock D with
  | error => rfl
  | ok _ =>
    simp only [bind, Except.bind, pure, Except.pure]
    cases governBody D (ordered D) (fun r => (coveredLayout D r).toOption.getD [])
      (fun r => (covered D r).toOption.getD []) with
    | error => rfl
    | ok _ =>
      simp only [rowsF, baseObjF_slow]
      have hn := memo_map D.governors (·.unit) (baseName D)
      unfold baseName at hn ⊢
      simp only [hn]
      rfl

theorem explain_bound (D : SDoc) (rows : List Row) (h : explainRows D = .ok rows) (r : Row) (hr : r ∈ rows) :
    r.unit ∈ unitIds D.doc ∧ ∀ x ∈ r.governors, x.unit ∈ unitIds D.doc ∧ ∃ g ∈ D.governors, g.id = x.id := by
  unfold explainRows at h
  cases hg : govern D with
  | error => rw [hg] at h; cases h
  | ok out =>
    rw [hg] at h
    simp only [bind, Except.bind, pure, Except.pure, Except.ok.injEq] at h
    subst h
    have ha := govern_admits D out hg
    obtain ⟨u, hu, rfl⟩ := List.mem_map.mp hr
    have hgov : ∀ g ∈ contributors D u, g ∈ D.governors := by
      intro g hg'
      simp only [contributors, frameOn, governorsOf, List.mem_append, List.mem_filter] at hg'
      rcases hg' with (⟨h1, _⟩ | ⟨h1, _⟩) | ⟨h1, _⟩
      · exact h1
      · exact (mem_ordered D g).mp h1
      · exact (mem_ordered D g).mp h1
    refine ⟨?_, fun x hx => ?_⟩
    · simp only [affected, ruleUnits, List.mem_filter] at hu
      exact hu.1.1
    · obtain ⟨g, hg', rfl⟩ := List.mem_map.mp hx
      exact ⟨admit_unit D ha g (hgov g hg'), g, hgov g hg', rfl⟩

theorem explainRows_effect (D : SDoc) (rows : List Row) (h : explainRows D = .ok rows) (r : Row) (hr : r ∈ rows)
    (x : GovRow) (hx : x ∈ r.governors) : x.effect ∈ effectWords := by
  unfold explainRows at h
  cases hg : govern D with
  | error => rw [hg] at h; cases h
  | ok out =>
    rw [hg] at h
    simp only [bind, Except.bind, pure, Except.pure, Except.ok.injEq] at h
    subst h
    obtain ⟨u, _, rfl⟩ := List.mem_map.mp hr
    obtain ⟨g, _, rfl⟩ := List.mem_map.mp hx
    cases g.effect <;> simp [effectWords, effectWord]

theorem explain_rows_iff (D : SDoc) (rows : List Row) (h : explainRows D = .ok rows) (u : String) :
    (∃ r ∈ rows, r.unit = u) ↔ u ∈ affected D := by
  unfold explainRows at h
  cases hg : govern D with
  | error => rw [hg] at h; cases h
  | ok out =>
    rw [hg] at h
    simp only [bind, Except.bind, pure, Except.pure, Except.ok.injEq] at h
    subst h
    constructor
    · rintro ⟨r, hr, rfl⟩
      obtain ⟨v, hv, rfl⟩ := List.mem_map.mp hr
      exact hv
    · intro hu
      exact ⟨_, List.mem_map_of_mem hu, rfl⟩

end

end VE.Scope

namespace VE.Scope.Run
open Lean VE.Scope

/-- The cells an answer may hold (a row's governors' reach units, summed), so that it stays within the service's
    line limit: beyond it the answer is `ResourceLimit` (UNKNOWN). -/
def cellLimit : Nat := 524288

/-- A bound on an answer's cells read from the block as written: every row lists each reach at most once, and an
    admitted block's reaches are its recorded `units`. -/
def cellBound (D : SDoc) (rows : Nat) : Nat := rows * (D.governors.foldl (fun n g => n + g.units.length + 1) 0)

/-- `decodeScope`'s steps after the split (`readSplit_scope`), so that the runner splits the document once and keeps
    its source. -/
def readSplit (doc : VE.Discourse.Loader.Split) : Except String SDoc := do
  let environment := doc.front.getObjValD "environment"
  let _ ← VE.Service.Document.environmentOf (VE.Service.Document.lowerScope environment)
    (senses := (doc.front.getObjVal? "senses").isOk)
  decodeBlock doc.front doc.source (← VE.Service.Document.scopeReadings environment)

theorem readSplit_scope (j : Json) : decodeScope j =
    (do readSplit (← VE.Service.Document.split (← VE.Bridge.stringField j "document") (senses := true))) := rfl

/-- Each governor unit's quote (2.3's `<text>`), from the source bytes `b`, once per governor. -/
def quotesOf (D : SDoc) (b : ByteArray) : List (String × String) :=
  D.governors.map fun g => (g.unit, match D.layout.find? (·.id == g.unit) with
    | some x => quote ((String.fromUTF8? (b.extract x.span.1 x.span.2)).getD "")
    | none => "")

def govJson (x : GovRow) : Json :=
  Json.mkObj [("id", .str x.id), ("unit", .str x.unit), ("effect", .str x.effect),
    ("reach", .arr (x.reach.map Json.str).toArray)]

def rowJson (r : Row) : Json :=
  Json.mkObj [("unit", .str r.unit), ("governors", .arr (r.governors.map govJson).toArray),
    ("provenance", .arr (r.provenance.map Json.str).toArray)]

/-- The rows of `D` over the source `source`, refused past `limit` cells. -/
def explainWithin (limit : Nat) (D : SDoc) (source : String) : Except String (List Row) := do
  let qs := quotesOf D source.toUTF8
  let rows ← @explainFast ⟨fun u => (qs.lookup u).getD ""⟩ D
  if cellBound D rows.length > limit then throw "ResourceLimit: scope explain answer cells"
  pure rows

theorem explainWithin_effect {limit : Nat} {D : SDoc} {source : String} {rows : List Row}
    (h : explainWithin limit D source = .ok rows) (r : Row) (hr : r ∈ rows) (x : GovRow) (hx : x ∈ r.governors) :
    x.effect ∈ effectWords := by
  unfold explainWithin at h
  simp only [bind, Except.bind] at h
  split at h
  · cases h
  · rename_i rs hrs
    rw [@explainFast_eq ⟨fun u => ((quotesOf D source.toUTF8).lookup u).getD ""⟩] at hrs
    split at h
    · cases h
    · cases h; exact @explainRows_effect ⟨fun u => ((quotesOf D source.toUTF8).lookup u).getD ""⟩ D _ hrs r hr x hx

def explainCase (j : Json) : Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let doc ← VE.Service.Document.split (← VE.Bridge.stringField j "document") (senses := true)
  let ps := VE.Service.Document.listedProfiles (doc.front.getObjValD "environment")
  unless ps.contains "scope@0" do throw "UnsupportedProfile: the scope mode explains a document that lists scope@0"
  let _ ← VE.Compose.gateOf VE.Compose.profileTable ps
  let rows ← explainWithin cellLimit (← readSplit doc) doc.source
  pure (VE.Route.Wire.ok id [("rows", .arr (rows.map rowJson).toArray)])

def runCaseReported (j : Json) : Json :=
  match explainCase j with
  | .ok row => row
  | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]

end VE.Scope.Run
