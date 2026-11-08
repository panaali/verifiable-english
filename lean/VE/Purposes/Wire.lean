import VE.Purposes.Decl
import VE.Bridge

/-! The front-matter `purposes` block on the wire (purpose-explanation plan 2.2, spec 1.2): exact fields, an absent
`share` is `plain`, and `prevents` or any other relation word is refused (plan D8, D9). The texts are spec 7.1's,
in its fault order. -/

namespace VE.Purposes
open Lean
open VE.Route.Admission (token)

def Share.wire : Share → String
  | .plain => "plain" | .sole => "sole" | .partly => "partly" | .notSole => "not_sole"

def Share.ofWire? : String → Option Share
  | "plain" => some .plain | "sole" => some .sole | "partly" => some .partly | "not_sole" => some .notSole
  | _ => none

def Polarity.wire : Polarity → String
  | .affirmed => "affirmed" | .denied => "denied"

def Polarity.ofWire? : String → Option Polarity
  | "affirmed" => some .affirmed | "denied" => some .denied
  | _ => none

/-- An id: a string that is a token (`VE.Route.Admission.token`). -/
def idOf : Json → Except String String
  | .str s => if token s then pure s else throw s!"InvalidPurposes: invalid id {s}"
  | j => throw s!"InvalidPurposes: invalid id {j.compress}"

/-- A closed word: a string `f` knows; the text quotes a string as it is and anything else compressed. -/
def wordOf {α : Type} (f : String → Option α) (text : String → String) : Json → Except String α
  | .str s => match f s with
    | some x => pure x
    | none => throw (text s)
  | j => throw (text j.compress)

def sideText (lid : String) : String :=
  s!"InvalidPurposes: link {lid} has a side that is not a list of parts or mentions"

def decodeRef (lid : String) (j : Json) : Except String Ref :=
  match VE.Bridge.fields j with
  | .ok [("part", .str i)] => Ref.part <$> idOf (.str i)
  | .ok [("mention", .str i)] => Ref.mention <$> idOf (.str i)
  | _ => throw (sideText lid)

def decodeRefs (lid : String) : List Json → Except String (List Ref)
  | [] => pure []
  | j :: js => do pure ((← decodeRef lid j) :: (← decodeRefs lid js))

def decodeSide (lid : String) : Json → Except String (List Ref)
  | .arr a => decodeRefs lid a.toList
  | _ => throw (sideText lid)

def linkFields : List String := ["id", "relation", "polarity", "reason", "target", "marker"]

/-- Link `n` (from 1) has exactly the six fields, or the six and `share`. -/
def linkFieldsOk (n : Nat) (j : Json) : Except String Unit :=
  if (VE.Bridge.exactFields j linkFields).isOk || (VE.Bridge.exactFields j ("share" :: linkFields)).isOk then
    pure ()
  else
    throw s!"InvalidPurposes: link {n} must have id, relation, polarity, reason, target and marker, and may have share"

/-- An absent `share` is `plain`. -/
def shareOf (id : String) (j : Json) : Except String Share :=
  match j.getObjVal? "share" with
  | .ok s => wordOf Share.ofWire? (fun s =>
      s!"InvalidPurposes: link {id} has share {s}; it must be plain, sole, partly or not_sole") s
  | .error _ => pure .plain

def decodeLink (n : Nat) (j : Json) : Except String Link := do
  linkFieldsOk n j
  let id ← idOf (j.getObjValD "id")
  let marker ← idOf (j.getObjValD "marker")
  let relation ← wordOf Relation.ofWire? (fun r =>
    s!"InvalidPurposes: link {id} has relation {r}; a purposes link's relation is because or in order to")
    (j.getObjValD "relation")
  let polarity ← wordOf Polarity.ofWire? (fun p =>
    s!"InvalidPurposes: link {id} has polarity {p}; it must be affirmed or denied") (j.getObjValD "polarity")
  let share ← shareOf id j
  let reason ← decodeSide id (j.getObjValD "reason")
  let target ← decodeSide id (j.getObjValD "target")
  pure { id, relation, polarity, share, reason, target, marker }

def decodeLinks : Nat → List Json → Except String (List Link)
  | _, [] => pure []
  | n, j :: js => do pure ((← decodeLink n j) :: (← decodeLinks (n + 1) js))

/-- The block is an object whose only member is `links`, an array. -/
def linksOf (j : Json) : Except String (Array Json) :=
  let bad := "InvalidPurposes: purposes must be an object whose only member is links"
  if (VE.Bridge.exactFields j ["links"]).isOk then
    match j.getObjValD "links" with
    | .arr ls => pure ls
    | _ => throw bad
  else throw bad

/-- Exact fields (`VE.Bridge.exactFields`); the texts are 7.1's. -/
def decodeBlock (j : Json) : Except String Block := do
  let ls ← linksOf j
  if ls.size ≤ maxLinks then Block.mk <$> decodeLinks 1 ls.toList
  else throw s!"ResourceLimit: purposes links exceed {maxLinks}"

def Ref.render : Ref → Json
  | .part i => Json.mkObj [("part", .str i)]
  | .mention i => Json.mkObj [("mention", .str i)]

def Link.render (L : Link) : Json :=
  Json.mkObj [("id", .str L.id), ("relation", .str L.relation.wire), ("polarity", .str L.polarity.wire),
    ("share", .str L.share.wire), ("reason", .arr (L.reason.map Ref.render).toArray),
    ("target", .arr (L.target.map Ref.render).toArray), ("marker", .str L.marker)]

/-- The canonical form: every member written, `share` included. -/
def renderBlock (B : Block) : Json := Json.mkObj [("links", .arr (B.links.map Link.render).toArray)]

/-! ## The round trip -/

theorem bind_ok {α β : Type} {x : Except String α} {f : α → Except String β} {b : β}
    (h : (x >>= f) = .ok b) : ∃ a, x = .ok a ∧ f a = .ok b := by
  cases x with
  | error e => cases h
  | ok a => exact ⟨a, rfl, h⟩

theorem map_ok {α β : Type} {x : Except String α} {f : α → β} {b : β}
    (h : (f <$> x) = .ok b) : ∃ a, x = .ok a ∧ f a = b := by
  cases x with
  | error e => cases h
  | ok a => exact ⟨a, rfl, by cases h; rfl⟩

theorem idOf_ok {j : Json} {s : String} (h : idOf j = .ok s) : j = .str s ∧ token s = true := by
  unfold idOf at h
  split at h
  · split at h
    · cases h; exact ⟨rfl, by assumption⟩
    · cases h
  · cases h

theorem idOf_str {s : String} (h : token s = true) : idOf (.str s) = .ok s := by
  simp [idOf, h]; rfl

theorem Polarity.ofWire_wire (p : Polarity) : Polarity.ofWire? p.wire = some p := by
  cases p <;> rfl

theorem Share.ofWire_wire (s : Share) : Share.ofWire? s.wire = some s := by
  cases s <;> rfl

theorem shareOf_render (id : String) (s : Share) :
    shareOf id (Json.mkObj [("share", .str s.wire)]) = .ok s := by
  have h : (Json.mkObj [("share", .str s.wire)]).getObjVal? "share" = .ok (.str s.wire) := rfl
  simp only [shareOf, h, wordOf, Share.ofWire_wire]
  rfl

/-- The ids a ref names are tokens. -/
def Ref.idOk : Ref → Bool
  | .part i | .mention i => token i

theorem decodeRef_ok {lid : String} {j : Json} {r : Ref} (h : decodeRef lid j = .ok r) : r.idOk = true := by
  unfold decodeRef at h
  split at h
  · obtain ⟨i, hi, rfl⟩ := map_ok h
    exact (idOf_ok hi).2
  · obtain ⟨i, hi, rfl⟩ := map_ok h
    exact (idOf_ok hi).2
  · cases h

theorem decodeRef_render (lid : String) (r : Ref) (h : r.idOk = true) : decodeRef lid r.render = .ok r := by
  cases r with
  | part i =>
    have e : VE.Bridge.fields (Ref.render (.part i)) = .ok [("part", .str i)] := rfl
    simp only [Ref.idOk] at h
    simp only [decodeRef, e, idOf_str h]; rfl
  | mention i =>
    have e : VE.Bridge.fields (Ref.render (.mention i)) = .ok [("mention", .str i)] := rfl
    simp only [Ref.idOk] at h
    simp [decodeRef, e, idOf_str h]; rfl

theorem decodeRefs_ok {lid : String} : ∀ {js : List Json} {rs : List Ref}, decodeRefs lid js = .ok rs →
    ∀ r ∈ rs, r.idOk = true
  | [], rs, h => by cases h; simp
  | j :: js, rs, h => by
    obtain ⟨r, hr, h⟩ := bind_ok h
    obtain ⟨rs', hrs, h⟩ := bind_ok h
    cases h
    intro x hx
    rcases List.mem_cons.mp hx with rfl | hx
    · exact decodeRef_ok hr
    · exact decodeRefs_ok hrs x hx

theorem decodeRefs_render (lid : String) : ∀ (rs : List Ref), (∀ r ∈ rs, r.idOk = true) →
    decodeRefs lid (rs.map Ref.render) = .ok rs
  | [], _ => rfl
  | r :: rs, h => by
    simp only [List.map, decodeRefs, decodeRef_render lid r (h r List.mem_cons_self),
      decodeRefs_render lid rs (fun x hx => h x (List.mem_cons_of_mem _ hx))]
    rfl

theorem decodeSide_ok {lid : String} {j : Json} {rs : List Ref} (h : decodeSide lid j = .ok rs) :
    ∀ r ∈ rs, r.idOk = true := by
  unfold decodeSide at h
  split at h
  · exact decodeRefs_ok h
  · cases h

theorem decodeSide_render (lid : String) (rs : List Ref) (h : ∀ r ∈ rs, r.idOk = true) :
    decodeSide lid (.arr (rs.map Ref.render).toArray) = .ok rs := by
  simp only [decodeSide]
  exact decodeRefs_render lid rs h

/-- What a decoded link carries: token ids, and refs whose ids are tokens. -/
def Link.idsOk (L : Link) : Prop :=
  token L.id = true ∧ token L.marker = true ∧ (∀ r ∈ L.reason, r.idOk = true) ∧ ∀ r ∈ L.target, r.idOk = true

theorem decodeLink_ok {n : Nat} {j : Json} {L : Link} (h : decodeLink n j = .ok L) : L.idsOk := by
  unfold decodeLink at h
  obtain ⟨_, -, h⟩ := bind_ok h
  obtain ⟨i, hi, h⟩ := bind_ok h
  obtain ⟨m, hm, h⟩ := bind_ok h
  obtain ⟨_, -, h⟩ := bind_ok h
  obtain ⟨_, -, h⟩ := bind_ok h
  obtain ⟨_, -, h⟩ := bind_ok h
  obtain ⟨rs, hrs, h⟩ := bind_ok h
  obtain ⟨ts, hts, h⟩ := bind_ok h
  cases h
  exact ⟨(idOf_ok hi).2, (idOf_ok hm).2, decodeSide_ok hrs, decodeSide_ok hts⟩

theorem decodeLink_render (n : Nat) (L : Link) (h : L.idsOk) : decodeLink n L.render = .ok L := by
  obtain ⟨hi, hm, hr, ht⟩ := h
  have e1 : linkFieldsOk n L.render = .ok () := rfl
  have e2 : L.render.getObjValD "id" = .str L.id := rfl
  have e3 : L.render.getObjValD "marker" = .str L.marker := rfl
  have e4 : L.render.getObjValD "relation" = .str L.relation.wire := rfl
  have e5 : L.render.getObjValD "polarity" = .str L.polarity.wire := rfl
  have e6 : L.render.getObjVal? "share" = .ok (.str L.share.wire) := rfl
  have e7 : L.render.getObjValD "reason" = .arr (L.reason.map Ref.render).toArray := rfl
  have e8 : L.render.getObjValD "target" = .arr (L.target.map Ref.render).toArray := rfl
  simp only [decodeLink, shareOf, e1, e2, e3, e4, e5, e6, e7, e8, idOf_str hi, idOf_str hm,
    decodeSide_render _ _ hr, decodeSide_render _ _ ht]
  simp [wordOf, Relation.ofWire_wire, Polarity.ofWire_wire, Share.ofWire_wire]
  rfl

theorem decodeLinks_ok : ∀ {n : Nat} {js : List Json} {Ls : List Link}, decodeLinks n js = .ok Ls →
    ∀ L ∈ Ls, L.idsOk
  | _, [], Ls, h => by cases h; simp
  | n, j :: js, Ls, h => by
    obtain ⟨L, hL, h⟩ := bind_ok h
    obtain ⟨Ls', hLs, h⟩ := bind_ok h
    cases h
    intro x hx
    rcases List.mem_cons.mp hx with rfl | hx
    · exact decodeLink_ok hL
    · exact decodeLinks_ok hLs x hx

theorem decodeLinks_length : ∀ {n : Nat} {js : List Json} {Ls : List Link}, decodeLinks n js = .ok Ls →
    Ls.length = js.length
  | _, [], Ls, h => by cases h; rfl
  | n, j :: js, Ls, h => by
    obtain ⟨_, -, h⟩ := bind_ok h
    obtain ⟨Ls', hLs, h⟩ := bind_ok h
    cases h
    simp [decodeLinks_length hLs]

theorem decodeLinks_render : ∀ (n : Nat) (Ls : List Link), (∀ L ∈ Ls, L.idsOk) →
    decodeLinks n (Ls.map Link.render) = .ok Ls
  | _, [], _ => rfl
  | n, L :: Ls, h => by
    simp only [List.map, decodeLinks, decodeLink_render n L (h L List.mem_cons_self),
      decodeLinks_render (n + 1) Ls (fun x hx => h x (List.mem_cons_of_mem _ hx))]
    rfl

theorem decodeBlock_render (j : Json) (B : Block) (h : decodeBlock j = .ok B) :
    decodeBlock (renderBlock B) = .ok B := by
  have hB : B.links.length ≤ maxLinks ∧ ∀ L ∈ B.links, L.idsOk := by
    unfold decodeBlock at h
    obtain ⟨ls, -, h⟩ := bind_ok h
    split at h
    · rename_i hs
      obtain ⟨Ls, hLs, h⟩ := map_ok h
      cases h
      refine ⟨?_, decodeLinks_ok hLs⟩
      rw [decodeLinks_length hLs, Array.length_toList]
      exact hs
    · cases h
  obtain ⟨hn, hL⟩ := hB
  have e1 : linksOf (renderBlock B) = .ok (B.links.map Link.render).toArray := rfl
  have e2 : (decodeBlock (renderBlock B)) = Block.mk <$> decodeLinks 1 (B.links.map Link.render) := by
    simp [decodeBlock, e1, bind, Except.bind, hn]
  rw [e2, decodeLinks_render 1 B.links hL]
  rfl

theorem decodeBlock_relations (j : Json) (B : Block) (_h : decodeBlock j = .ok B) :
    ∀ L ∈ B.links, L.relation.wire ∈ VE.Route.Admission.relations ∧ L.relation.wire ≠ "prevents" :=
  fun L _ => ⟨L.relation.wire_mem, L.relation.wire_ne_prevents⟩
end VE.Purposes
