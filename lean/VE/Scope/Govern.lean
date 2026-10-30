import VE.Layout.List
import VE.Scope.Effects
import VE.Discourse.Access

/-! Scope's GOVERN step (scope@0, docs/spec/scope.md 1.1, 1.3, 1.5 and 4.2): the reaches, the block's admission and
    `govern`, which returns the complete document with each affected unit's content composed as the chain's own
    norm object, then the precedence edges into it. The anchor and label reaches and the anchor checks are the
    layout's (`VE/Layout/Anchors.lean`, `VE/Layout/List.lean`), called here. The run path `governFast` (1.5.8) is
    last. -/

namespace VE.Scope
open Lean
open VE.SoftNorms (SoftNode)

inductive Reach
  | list (lead : String)
  | listName (name : String)
  | anchor (id : String)
  | label (item : String)
  | rules (names : List String)
  | frontier
  | fixed (units : List String)   -- never on the wire: a frontier reach fixed by one joint choice (SC-5)

structure Governor where
  id : String
  unit : String
  effect : Effect
  reach : Reach
  units : List String       -- the recorded reach, regenerated and compared; empty for a frontier reach

structure SDoc where
  layout : List VE.Layout.Unit
  doc : Json                -- the document as written after RESOLVE: `{"units": [...], ...}`
  block : Json              -- the `scope` block as written
  governors : List Governor
  listNames : List (VE.Discourse.ContentName × String × String)   -- name, its lead-in, its registering unit
  anchors : List VE.Discourse.Anchor
  re : VE.Readings.Wire.ReadingsEnvironment

/-! JSON access (read only; scope decodes no rule field itself) -/

def keysOf (j : Json) : List String := (members j).map (·.1)
def unitsOf (doc : Json) : List Json := match doc.getObjValD "units" with
  | .arr xs => xs.toList
  | _ => []
def idOf (u : Json) : String := (u.getObjValD "id").getStr?.toOption.getD ""
def unitIds (doc : Json) : List String := (unitsOf doc).map idOf
def contentOf (doc : Json) (u : String) : Json :=
  (((unitsOf doc).find? (idOf · == u)).map (·.getObjValD "content")).getD .null
def isPart (c : Json) : Bool := keysOf c == ["part"] || keysOf c == ["cites", "part"]
def isNorm (c : Json) : Bool := keysOf c == ["norm"] || keysOf c == ["cites", "norm"]
def objectOf (c : Json) : Json := if isPart c then c.getObjValD "part" else c.getObjValD "norm"
def normOf (c : Json) : Option Json := (c.getObjVal? "norm").toOption
def partUnits (D : SDoc) : List String := (unitIds D.doc).filter (fun u => isPart (contentOf D.doc u))
def ruleUnits (D : SDoc) : List String :=
  (unitIds D.doc).filter (fun u => isPart (contentOf D.doc u) || isNorm (contentOf D.doc u))
def setUnits (doc : Json) : List String := match doc.getObjValD "reading_sets" with
  | .arr xs => xs.toList.map (fun s => (s.getObjValD "unit").getStr?.toOption.getD "")
  | _ => []

/-! Applying effects (on the rule's JSON object) -/

def applyEffect (u : String) : Effect → Json → Except String Json
  | .reguard c, o => match o.getObjVal? "guard" with
    | .ok g => pure (o.setObjVal! "guard" (substOwn g depthLimit c))
    | .error _ => throw s!"ScopeNotARule: {u}"
  | .carveOut c, o => match o.getObjVal? "guard", o.getObjVal? "unless" with
    | .ok g, .ok (.arr xs) => pure (o.setObjVal! "unless" (.arr (xs.push (substOwn g depthLimit c))))
    | _, _ => throw s!"ScopeNotARule: {u}"
  | _, o => pure o

/-- An item's rule as the chain reads it (the explain route). -/
def itemRule (D : SDoc) (u : String) (lead item : Json) : Except String SoftNode :=
  do VE.Readings.Wire.decodeNorm D.re (← mergeParts u lead item)

/-! Reaches -/

def isFrame : Effect → Bool | .frame _ => true | _ => false
def unary : Effect → Bool | .reguard _ | .carveOut _ => true | _ => false
def graph : Effect → Bool | .precedes | .yields => true | _ => false

def coveredLayout (D : SDoc) : Reach → Except String (List String)
  | .list lead => VE.Layout.listRun D.layout lead
  | .listName n => match D.listNames.find? (·.1.name == n) with
    | some (cn, lead, _) => do
      let us ← VE.Layout.listRun D.layout lead
      if cn.units == us then pure us else throw s!"ManifestMismatch: scope.list_names.{n}.units"
    | none => throw s!"ScopeUnknownName: {n}"
  | .anchor a => VE.Layout.anchorReach D.layout D.anchors a
  | .label i => VE.Layout.itemRun D.layout i
  | .rules _ => .ok []
  | .frontier => throw "UnsupportedProfile: scope@0 frontier reach requires SC-5"   -- SC-5: its addendum (9.4)
  | .fixed us => .ok us

def frameOn (D : SDoc) (u : String) : List Governor :=
  D.governors.filter (fun g => isFrame g.effect && ((coveredLayout D g.reach).toOption.getD []).contains u)

def baseObj (D : SDoc) (u : String) : Except String Json :=
  let c := contentOf D.doc u
  if !(isPart c || isNorm c) then .error s!"ScopeNotARule: {u}" else
  match frameOn D u with
  | [] => if isPart c then .error s!"ScopeOrphanPart: {u}" else .ok (objectOf c)
  | [g] => match g.effect with
    | .frame lead => mergeParts u lead (objectOf c)
    | _ => .ok (objectOf c)
  | g₁ :: g₂ :: _ => .error s!"ScopeOrder: {u}: {g₁.id}, {g₂.id}"

def baseName (D : SDoc) (u : String) : Option String :=
  ((baseObj D u).toOption.bind fun o => (VE.Readings.Wire.decodeNorm D.re o).toOption).map (·.name)

def covered (D : SDoc) : Reach → Except String (List String)
  | .rules ns => do
    for n in ns do
      unless (ruleUnits D).any (fun u => baseName D u == some n) do throw s!"ScopeUnknownRule: {n}"
    pure ((ruleUnits D).filter (fun u => (baseName D u).any ns.contains))
  | r => coveredLayout D r

/-! Order (plan 1.4) -/

def classOf : Reach → Nat
  | .anchor _ => 0 | .label _ => 1 | .list _ => 2 | .listName _ => 2 | .rules _ => 3 | .frontier => 4
  | .fixed _ => 4

def position (D : SDoc) (u : String) : Nat := (VE.Layout.indexOf D.layout u).getD D.layout.length

def ordered (D : SDoc) : List Governor :=
  D.governors.mergeSort (fun g h => classOf g.reach < classOf h.reach ||
    (classOf g.reach == classOf h.reach && position D g.unit ≤ position D h.unit))

def coversU (D : SDoc) (g : Governor) (u : String) : Bool := ((covered D g.reach).toOption.getD []).contains u

def governorsOf (D : SDoc) (u : String) : List Governor := (ordered D).filter (fun g => unary g.effect && coversU D g u)

def composed (D : SDoc) (u : String) : Except String Json := do
  (governorsOf D u).foldlM (fun o g => applyEffect u g.effect o) (← baseObj D u)

def orderCheck (D : SDoc) : Except String Unit := do
  for u in unitIds D.doc do
    let gs := governorsOf D u
    for g₁ in gs do
      for g₂ in gs do
        if g₁.id != g₂.id && !Commutes g₁.effect g₂.effect then throw s!"ScopeOrder: {u}: {g₁.id}, {g₂.id}"

def affected (D : SDoc) : List String :=
  (ruleUnits D).filter fun u =>
    isPart (contentOf D.doc u) || !(frameOn D u).isEmpty || !(governorsOf D u).isEmpty ||
    D.governors.any (fun g => match g.effect with
      | .precedes => g.unit == u
      | .yields => coversU D g u
      | _ => false)

/-! Precedence: the graph step over the composed rules (SC-4) -/

def edgesOf (D : SDoc) (rule : String → Option SoftNode) (g : Governor) : List (String × String) :=
  let targets := (covered D g.reach).toOption.getD []
  match rule g.unit with
  | none => []
  | some N => match g.effect with
    | .precedes => targets.filterMap fun v => (rule v).bind fun M =>
        if M.pred == N.pred && M.name != N.name then some (g.unit, M.name) else none
    | .yields => targets.filterMap fun v => (rule v).bind fun M =>
        if M.pred == N.pred && M.name != N.name then some (v, N.name) else none
    | _ => []

def edgesInto (D : SDoc) (rule : String → Option SoftNode) (u : String) : List String :=
  (((ordered D).filter (graph ·.effect)).flatMap (edgesOf D rule)).filterMap fun (w, n) => if w == u then some n else none

def ruleTable (D : SDoc) : Except String (List (String × SoftNode)) := do
  let gs := (ordered D).filter (graph ·.effect)
  let needed := (ruleUnits D).filter (fun u => gs.any (fun g => g.unit == u || coversU D g u))
  needed.mapM (fun u => do pure (u, ← VE.Readings.Wire.decodeNorm D.re (← composed D u)))

def edgesFor (D : SDoc) (u : String) : Except String (List String) := do
  let t ← ruleTable D
  pure (edgesInto D (fun v => t.lookup v) u)

def addOver (names : List String) (o : Json) : Json :=
  match o.getObjVal? "over" with
  | .ok (.arr xs) =>
    let old := xs.toList.filterMap (·.getStr?.toOption)
    let fresh := names.foldl (fun acc n => if old.contains n || acc.contains n then acc else acc ++ [n]) []
    if fresh.isEmpty then o else o.setObjVal! "over" (.arr (xs ++ (fresh.map Json.str).toArray))
  | _ => o

/-! The block's admission and `govern` -/

def conditions : Effect → List Json
  | .reguard c => [c]
  | .carveOut c => [c]
  | _ => []

def vocabularyNames (D : SDoc) : List String :=
  let v := D.re.se.ne.rv.vocabulary
  v.sorts ++ v.predicates.map (·.1) ++ v.constants.map (·.1)

def firstDup : List String → Option String
  | [] => none
  | x :: xs => if xs.contains x then some x else firstDup xs

def kindOf (doc : Json) (u : String) : String :=
  (((unitsOf doc).find? (idOf · == u)).map (fun x => (x.getObjValD "kind").getStr?.toOption.getD "")).getD ""

/-- The spans of the definition units, for discourse's export check. -/
def defSpans (D : SDoc) : List (Nat × Nat) :=
  (D.layout.filter (fun x => kindOf D.doc x.id == "definition")).map (·.span)

/-- Spec 6.2's steps 1 to 8; step 7 is discourse's anchor checks, on the block's anchors. -/
def admitBlock (D : SDoc) : Except String Unit := do
  if D.governors.length > 256 then throw "ResourceLimit: scope governors"
  if D.listNames.length > 256 then throw "ResourceLimit: scope list names"
  if let some i := firstDup (D.governors.map (·.id)) then throw s!"DuplicateDeclaration: governor {i}"
  if let some n := firstDup (D.listNames.map (·.1.name)) then throw s!"DuplicateDeclaration: list name {n}"
  for g in D.governors do
    unless (unitIds D.doc).contains g.unit do throw s!"ScopeUnknownUnit: {g.unit}"
  if D.governors.any (fun g => !(conditions g.effect).isEmpty) && (vocabularyNames D).contains "own" then
    throw "ScopeReserved: own"
  for (cn, lead, unit) in D.listNames do
    unless cn.scope == "doc" do throw s!"InvalidInput: scope@0 list_names.{cn.name}.scope must be doc"
    unless (unitIds D.doc).contains unit do throw s!"ScopeUnknownUnit: {unit}"
    let us ← VE.Layout.listRun D.layout lead
    unless cn.units == us do throw s!"ManifestMismatch: scope.list_names.{cn.name}.units"
  VE.Layout.anchorsOk D.anchors (defSpans D) (VE.Discourse.unaryPred D.re.se.ne.rv.environment)
  for g in D.governors do
    for c in conditions g.effect do
      unless depthOk depthLimit c do throw "ResourceLimit: scope condition depth exceeds 64"
      unless ownSafe depthLimit c do throw s!"ScopeOwnBound: {g.id}"
    match g.effect, g.reach with
    | .frame _, .list lead =>
      unless lead == g.unit do throw s!"ManifestMismatch: scope.governors.{g.id}.unit"
    | .frame _, .listName n =>
      unless (D.listNames.find? (·.1.name == n)).any (·.2.1 == g.unit) do
        throw s!"ManifestMismatch: scope.governors.{g.id}.unit"
    | .frame _, _ => throw s!"ScopeReach: {g.id}"
    | .title, .anchor _ => pure ()
    | .title, .label _ => pure ()
    | .title, _ => throw s!"ScopeReach: {g.id}"
    | .precedes, .frontier => throw s!"ScopeReach: {g.id}"
    | .yields, .frontier => throw s!"ScopeReach: {g.id}"
    | _, _ => pure ()
    match g.reach with
    | .anchor a =>
      unless graph g.effect || VE.Layout.headingOf D.layout D.anchors a == some g.unit do
        throw s!"ManifestMismatch: scope.governors.{g.id}.unit"
    | .label i => unless graph g.effect || i == g.unit do throw s!"ManifestMismatch: scope.governors.{g.id}.unit"
    | _ => pure ()
    let us ← covered D g.reach
    unless us == g.units do throw s!"ManifestMismatch: scope.governors.{g.id}.units"
    for u in g.unit :: us do
      if (setUnits D.doc).contains u then throw s!"ScopeReadings: {u}"
    if isFrame g.effect || unary g.effect then
      for u in us do
        let c := contentOf D.doc u
        unless c.isNull || isPart c || isNorm c do throw s!"ScopeNotARule: {u}"

def newContent (c o : Json) : Json :=
  if isPart c then Json.mkObj ((members c).filter (·.1 != "part") ++ [("norm", o)]) else c.setObjVal! "norm" o

def patch (D : SDoc) (comp : List (String × Json)) : Json :=
  D.doc.setObjVal! "units" (.arr ((unitsOf D.doc).map fun u =>
    match comp.lookup (idOf u) with
    | some o => u.setObjVal! "content" (newContent (u.getObjValD "content") o)
    | none => u).toArray)

/-- The block is admitted first, with or without governors. -/
def govern (D : SDoc) : Except String Json := do
  admitBlock D
  if D.governors.isEmpty then
    match partUnits D with
    | [] => pure D.doc
    | u :: _ => throw s!"ScopeOrphanPart: {u}"
  else
    orderCheck D
    let comp ← (affected D).mapM (fun u => do pure (u, ← composed D u))
    let t ← ruleTable D
    for g in (ordered D).filter (graph ·.effect) do
      if (edgesOf D (fun v => t.lookup v) g).isEmpty then throw s!"ScopeNoEffect: {g.id}"
    pure (patch D (comp.map fun (u, o) => (u, addOver (edgesInto D (fun v => t.lookup v) u) o)))

/-! What the statements of 5.1 claim -/

/-- The DRI's fix (a) of 2026-10-27 (spec 11.3's `Pinned.JsonWF`): every JSON object, at any depth, is a
    well-formed tree, as every JSON parser builds it. F-raw (`Examples.lean`) is why 5.1's statements take it. -/
inductive JsonWF : Json → Prop
  | null : JsonWF .null
  | bool (b : Bool) : JsonWF (.bool b)
  | num (n : JsonNumber) : JsonWF (.num n)
  | str (s : String) : JsonWF (.str s)
  | arr (xs : Array Json) : (∀ x ∈ xs, JsonWF x) → JsonWF (.arr xs)
  | obj (kvs : Std.TreeMap.Raw String Json) : kvs.WF → (∀ kv ∈ kvs.toList, JsonWF kv.2) → JsonWF (.obj kvs)

/-! `JsonWF` as a check (sc-1af, the DRI's decision of 2026-10-28 item 1): the route runs it on every document it
    parses, since no lemma can be proved about the output of a parser that is not total. A tree is well formed when
    its stored sizes are right and it is balanced at every node (`Impl.Balanced`), and its keys ascend in order
    (`Impl.Ordered`). Each node is read once; the keys are listed only once the tree is balanced, so in `O(n log n)`. -/

/-- Strictly ascending keys. -/
def ascending : List String → Bool
  | a :: b :: rest => compare a b == .lt && ascending (b :: rest)
  | _ => true

open Std.DTreeMap.Internal in
/-- `Impl.Balanced` as a check: each node's stored size, and the balance of its two sides. -/
def balanced? : Impl String (fun _ => Json) → Bool
  | .leaf => true
  | .inner sz _ _ l r => balanced? l && balanced? r &&
      (l.size + r.size ≤ 1 || l.size ≤ delta * r.size && r.size ≤ delta * l.size) && sz == l.size + 1 + r.size

mutual
/-- `JsonWF` as a total check: `jsonWF?_sound`. -/
def jsonWF? : Json → Bool
  | .null => true
  | .bool _ => true
  | .num _ => true
  | .str _ => true
  | .arr ⟨xs⟩ => listWF? xs
  | .obj ⟨⟨t⟩⟩ => balanced? t && ascending (t.toListModel.map (·.1)) && implWF? t
termination_by structural j => j
/-- Every member of an array passes `jsonWF?`. -/
def listWF? : List Json → Bool
  | [] => true
  | x :: xs => jsonWF? x && listWF? xs
termination_by structural xs => xs
/-- Every value of an object's tree passes `jsonWF?`. -/
def implWF? : Std.DTreeMap.Internal.Impl String (fun _ => Json) → Bool
  | .leaf => true
  | .inner _ _ v l r => implWF? l && jsonWF? v && implWF? r
termination_by structural t => t
end

open Std.DTreeMap.Internal in
theorem balanced?_sound : ∀ t : Impl String (fun _ => Json), balanced? t = true → t.Balanced
  | .leaf, _ => .leaf
  | .inner sz _ _ l r, h => by
    simp only [balanced?, Bool.and_eq_true, Bool.or_eq_true, decide_eq_true_eq, beq_iff_eq] at h
    exact .inner (balanced?_sound l h.1.1.1) (balanced?_sound r h.1.1.2) h.1.2 h.2

theorem ascending_sound : ∀ ks : List String, ascending ks = true → ks.Pairwise (compare · · = .lt)
  | [], _ => .nil
  | [_], _ => List.pairwise_singleton _ _
  | a :: b :: rest, h => by
    simp only [ascending, Bool.and_eq_true, beq_iff_eq] at h
    have ih := ascending_sound (b :: rest) h.2
    refine List.Pairwise.cons (fun c hc => ?_) ih
    rcases List.mem_cons.mp hc with rfl | hc
    · exact h.1
    · exact Std.TransCmp.lt_trans h.1 (List.rel_of_pairwise_cons ih hc)

mutual
theorem jsonWF?_sound {j : Json} (h : jsonWF? j = true) : JsonWF j := match j, h with
  | .null, _ => .null
  | .bool b, _ => .bool b
  | .num n, _ => .num n
  | .str s, _ => .str s
  | .arr ⟨xs⟩, h => .arr _ fun x hx => listWF?_sound (by simpa [jsonWF?] using h) x (by simpa using hx)
  | .obj ⟨⟨t⟩⟩, h => by
    simp only [jsonWF?, Bool.and_eq_true] at h
    have ho : t.Ordered := List.pairwise_map.mp (ascending_sound _ h.1.2)
    refine .obj _ ⟨⟨.wf (balanced?_sound t h.1.1) ho⟩⟩ fun kv hkv => ?_
    · simp only [Std.TreeMap.Raw.toList, Std.DTreeMap.Raw.Const.toList,
        Std.DTreeMap.Internal.Impl.Const.toList_eq_toListModel_map,
        List.mem_map] at hkv
      obtain ⟨e, he, rfl⟩ := hkv
      exact implWF?_sound h.2 e he
theorem listWF?_sound {xs : List Json} (h : listWF? xs = true) : ∀ x ∈ xs, JsonWF x := match xs, h with
  | [], _ => fun _ hx => absurd hx List.not_mem_nil
  | y :: ys, h => by
    simp only [listWF?, Bool.and_eq_true] at h
    intro x hx
    rcases List.mem_cons.mp hx with rfl | hx
    · exact jsonWF?_sound h.1
    · exact listWF?_sound h.2 x hx
theorem implWF?_sound {t : Std.DTreeMap.Internal.Impl String (fun _ => Json)} (h : implWF? t = true) :
    ∀ e ∈ t.toListModel, JsonWF e.2 := match t, h with
  | .leaf, _ => fun _ he => absurd he List.not_mem_nil
  | .inner _ k v l r, h => by
    simp only [implWF?, Bool.and_eq_true] at h
    intro e he
    simp only [Std.DTreeMap.Internal.Impl.toListModel, List.mem_append, List.mem_cons] at he
    rcases he with he | rfl | he
    · exact implWF?_sound h.1.1 e he
    · exact jsonWF?_sound h.1.2
    · exact implWF?_sound h.2 e he
end

/-- A JSON string value occurs in a JSON value (object keys are not values). -/
inductive HasStr (s : String) : Json → Prop
  | str : HasStr s (.str s)
  | arr {xs : Array Json} {x : Json} : x ∈ xs → HasStr s x → HasStr s (.arr xs)
  | obj {j x : Json} {k : String} : j.getObjVal? k = .ok x → HasStr s x → HasStr s j

/-- What a governor's effect can write into the output: its frame part or its condition; nothing for the others. -/
def payload : Effect → Json
  | .frame p => p
  | .reguard c => c
  | .carveOut c => c
  | _ => .null

/-- The decoded governors are bound to the block as written: every string value of a payload is one of the block. -/
def BlockBound (D : SDoc) : Prop :=
  ∀ g ∈ D.governors, ∀ s, HasStr s (payload g.effect) → HasStr s D.block

/-! The run path (1.5.8): `govern`'s steps after the admission, reading the order, each reach (as `frameOn` reads
    it, `lv`, and as the other steps read it, `cv`) and each rule unit's base name from tables computed once.
    `governFast_eq` (Theorems.lean) proves that it answers as `govern`. -/

deriving instance DecidableEq for Reach

/-- `f x`, read from the table `t` when it has `x`. -/
def memo [BEq α] (t : List (α × β)) (f : α → β) (x : α) : β := match t.lookup x with
  | some v => v
  | none => f x

def frameOnF (D : SDoc) (lv : Reach → List String) (u : String) : List Governor :=
  D.governors.filter (fun g => isFrame g.effect && (lv g.reach).contains u)

def baseObjF (D : SDoc) (lv : Reach → List String) (u : String) : Except String Json :=
  let c := contentOf D.doc u
  if !(isPart c || isNorm c) then .error s!"ScopeNotARule: {u}" else
  match frameOnF D lv u with
  | [] => if isPart c then .error s!"ScopeOrphanPart: {u}" else .ok (objectOf c)
  | [g] => match g.effect with
    | .frame lead => mergeParts u lead (objectOf c)
    | _ => .ok (objectOf c)
  | g₁ :: g₂ :: _ => .error s!"ScopeOrder: {u}: {g₁.id}, {g₂.id}"

def coveredBy (D : SDoc) (bn : String → Option String) : Reach → Except String (List String)
  | .rules ns => do
    for n in ns do
      unless (ruleUnits D).any (fun u => bn u == some n) do throw s!"ScopeUnknownRule: {n}"
    pure ((ruleUnits D).filter (fun u => (bn u).any ns.contains))
  | r => coveredLayout D r

def governorsOfF (os : List Governor) (cv : Reach → List String) (u : String) : List Governor :=
  os.filter (fun g => unary g.effect && (cv g.reach).contains u)

def composedF (D : SDoc) (lv : Reach → List String) (os : List Governor) (cv : Reach → List String) (u : String) :
    Except String Json := do
  (governorsOfF os cv u).foldlM (fun o g => applyEffect u g.effect o) (← baseObjF D lv u)

def edgesOfF (cv : Reach → List String) (rule : String → Option SoftNode) (g : Governor) : List (String × String) :=
  match rule g.unit with
  | none => []
  | some N => match g.effect with
    | .precedes => (cv g.reach).filterMap fun v => (rule v).bind fun M =>
        if M.pred == N.pred && M.name != N.name then some (g.unit, M.name) else none
    | .yields => (cv g.reach).filterMap fun v => (rule v).bind fun M =>
        if M.pred == N.pred && M.name != N.name then some (v, N.name) else none
    | _ => []

def orderCheckF (D : SDoc) (os : List Governor) (cv : Reach → List String) : Except String Unit := do
  for u in unitIds D.doc do
    let gs := governorsOfF os cv u
    for g₁ in gs do
      for g₂ in gs do
        if g₁.id != g₂.id && !Commutes g₁.effect g₂.effect then throw s!"ScopeOrder: {u}: {g₁.id}, {g₂.id}"

/-- `govern` after the admission, on the order `os` and the reaches `lv` and `cv`. -/
def governBody (D : SDoc) (os : List Governor) (lv cv : Reach → List String) : Except String Json :=
  if D.governors.isEmpty then
    match partUnits D with
    | [] => pure D.doc
    | u :: _ => throw s!"ScopeOrphanPart: {u}"
  else do
    orderCheckF D os cv
    let aff := (ruleUnits D).filter fun u =>
      isPart (contentOf D.doc u) || !(frameOnF D lv u).isEmpty || !(governorsOfF os cv u).isEmpty ||
      D.governors.any (fun g => match g.effect with
        | .precedes => g.unit == u
        | .yields => (cv g.reach).contains u
        | _ => false)
    let comp ← aff.mapM (fun u => do pure (u, ← composedF D lv os cv u))
    let gs := os.filter (graph ·.effect)
    let needed := (ruleUnits D).filter (fun u => gs.any (fun g => g.unit == u || (cv g.reach).contains u))
    let t ← needed.mapM (fun u => do pure (u, ← VE.Readings.Wire.decodeNorm D.re (← composedF D lv os cv u)))
    for g in gs do
      if (edgesOfF cv (fun v => t.lookup v) g).isEmpty then throw s!"ScopeNoEffect: {g.id}"
    pure (patch D (comp.map fun (u, o) => (u, addOver
      ((gs.flatMap (edgesOfF cv (fun v => t.lookup v))).filterMap fun (w, n) => if w == u then some n else none) o)))

/-- The tables: each governor's reach as a layout reach, then each rule unit's base name, then each reach. -/
def fastReads (D : SDoc) : (Reach → List String) × (Reach → List String) :=
  let lv := memo (D.governors.map fun g => (g.reach, (coveredLayout D g.reach).toOption.getD []))
    (fun r => (coveredLayout D r).toOption.getD [])
  let bn := memo ((ruleUnits D).map fun u =>
    (u, ((baseObjF D lv u).toOption.bind fun o => (VE.Readings.Wire.decodeNorm D.re o).toOption).map (·.name)))
    (baseName D)
  (lv, memo (D.governors.map fun g => (g.reach, (coveredBy D bn g.reach).toOption.getD []))
    (fun r => (covered D r).toOption.getD []))

def governFast (D : SDoc) : Except String Json := do
  admitBlock D
  let (lv, cv) := fastReads D
  governBody D (ordered D) lv cv

end VE.Scope
