import VE.Acts.Decode
import VE.Compose.Dispatch

/-! The `acts-elaborate` case kind of the `norms` and `norm-defaults` modes (act-phrases 6.7, C18): the elaborated
document of an `acts@0` case and the map from each generated part to its source, which Python binds to the request
and relays. One runner answers both modes; each passes the decoder its route reads before elaboration
(`Norms.Wire.decodeSource` with its flags, or `NormDefaults.Wire.decodeSourceU`).

The row is `ELABORATED` with the parts' declarations (`predicates`), the part rules (`rules`), the joined acts that
did not split (`kept`) and, per split source, its parts and D-28's text (`split`); or `REFUSED` with the
elaboration's diagnostic and every list empty. A refusal of the decoder itself (the act check's D-15 to D-18) is the
case's error, as on every other kind. Each list is read off `e.U'` and `e.M` once: the decoded document is bounded by
the decoder's limits (64 regulated predicates, 256 rules) and the elaboration by step 6's (6.3). -/

namespace VE.Acts.Run
open Lean VE.Acts VE.NormDefaults

def roleJson : VE.Norms.Role → Json
  | .permission => "permission"
  | .obligation => "obligation"
  | .plain => "plain"

def completionJson (U : UDoc) (r : VE.Norms.Regulated) : Json :=
  match completionOf U r with
  | .allow => "allow"
  | .deny => "deny"
  | .unspecified => "unspecified"

def optJson : Option String → Json
  | some s => .str s
  | none => .null

/-- One row per part declared in `U'`, with its source and index from `M.preds`. -/
def predicatesJson (U' : UDoc) (M : SplitMap) : Json :=
  Json.arr (U'.D.T.regulated.filterMap fun r => (M.preds.find? (·.1 == r.name)).map fun (_, p, i) =>
    Json.mkObj [("name", .str r.name), ("source", .str p), ("index", toJson i), ("sorts", toJson r.sorts),
      ("role", roleJson r.role), ("default", completionJson U' r), ("act", optJson r.act),
      ("permission", optJson r.permission)]).toArray

/-- One row per part rule in `U'`, with its source rule and index from `M.rules`. -/
def rulesJson (U' : UDoc) (M : SplitMap) : Json :=
  Json.arr (U'.D.T.nodes.filterMap fun N => (M.rules.find? (·.1 == N.name)).map fun (_, n, i) =>
    Json.mkObj [("name", .str N.name), ("source", .str n), ("index", toJson i), ("pred", .str N.pred),
      ("sign", .bool N.sign), ("guard", VE.Norms.Wire.enc N.guard),
      ("unless", Json.arr (N.carveOuts.map VE.Norms.Wire.enc).toArray), ("over", toJson N.over)]).toArray

/-- D-28: the refusal of a model, data or question that names the split source `p`. -/
def partsText (p : String) (parts : List String) : String :=
  s!"InvalidInput: name one of its parts: {p} is split into {", ".intercalate parts}"

/-- Per split source, in the map's order: its parts in index order and D-28's text. -/
def splitRows (M : SplitMap) : Json :=
  Json.arr ((M.preds.map (·.2.1)).eraseDups.map fun p =>
    let parts := (M.preds.filter (·.2.1 == p)).map (·.1)
    Json.mkObj [("source", .str p), ("parts", toJson parts), ("text", .str (partsText p parts))]).toArray

/-- The elaborated row's lists. -/
def elaboratedFields (e : VE.Acts.Decode.ElaboratedU) : List (String × Json) :=
  [("predicates", predicatesJson e.U' e.M), ("rules", rulesJson e.U' e.M),
   ("kept", toJson ((e.D.acts.map (·.1)).filter fun p => !e.M.preds.any (·.2.1 == p))),
   ("split", splitRows e.M)]

def emptyFields : List (String × Json) :=
  [("predicates", Json.arr #[]), ("rules", Json.arr #[]), ("kept", Json.arr #[]), ("split", Json.arr #[])]

/-- `acts-elaborate`: the case's source decoded by `decode`, then `elaborateSource` and `sourceOf`, as the route
that reads it runs them (6.4); the identity is the route's own (`Flagged.decodePackage`). -/
def runElaborate (decode : Json → Json → Except String VE.NormDefaults.Wire.SourceU) (j : Json) :
    Except String Json := do
  let id ← VE.Bridge.stringField j "id"
  let written ← j.getObjVal? "environment"
  let environment ← VE.Compose.decidingEnvironment written
  if (VE.Norms.Wire.actsProfiles true environment).isEmpty then
    throw "UnsupportedProfile: acts-elaborate requires acts@0"
  let s ← decode environment (j.getObjValD "norms")
  let envId ← VE.Route.Wire.environmentId s.src.ne.profiles (← VE.Norms.Wire.canonicalEnvironmentJson written)
  match VE.Acts.Decode.elaborateSource environment s >>= fun e => (VE.Acts.Decode.sourceOf e).map fun _ => e with
  | .ok e => pure (VE.Route.Wire.ok id
      ([("environment_id", .str envId), ("verdict", .str "ELABORATED")] ++ elaboratedFields e))
  | .error d => pure (VE.Route.Wire.ok id
      ([("environment_id", .str envId), ("verdict", .str "REFUSED"), ("diagnostic", .str d)] ++ emptyFields))

/-- The norms route's decoder before elaboration (`Acts.Decode.decodeElaboratedFlagged`'s first step). -/
def normsSource (environment norms : Json) : Except String VE.NormDefaults.Wire.SourceU :=
  VE.Acts.Decode.plainU <$> VE.Norms.Wire.decodeSource environment norms (flags := true)

def isElaborate (j : Json) : Bool :=
  match j.getObjValD "kind" with
  | .str k => k == "acts-elaborate"
  | _ => false

/-! ### The `act-readings` mode (act-phrases 7, AP-4)

The readings of one act phrase under a rule's modal words, and their paraphrases, which the translator's tool writes
into a reading set that `sourceCheck` then checks. Lean lexes the phrase: `tokens` is each token's UTF-8 byte span in
the request's `phrase`, and each act's `from` the indices of the tokens its text reads. The request is charged
against the act phrase's 400 bytes (`Lexical.maxActBytes`), the fixed phrases' and frames' limits (`decodeFixed`,
`checkVocab`) and the parse limits (`rawCap`, `stepBudget`, 64 readings): the phrase is lexed once, its readings
listed once (`phraseReadings`, at most 64: `phraseReadings_length`) and paraphrased once. -/

/-- Each token's UTF-8 byte span in `s` as written: its text (`tokStr`, folded, single-spaced) read after the
    whitespace before it. `none` only for a slot written with leading zeros. -/
def spans (fx : List String) (s : String) (ts : List Lexical.Tok) : Option (List (Nat × Nat)) :=
  let ws : Char → Bool := VE.Norms.Wire.pyWhitespace
  let rec skip : List Char → Nat → List Char × Nat
    | c :: cs, p => if ws c then skip cs (p + c.utf8Size) else (c :: cs, p)
    | [], p => ([], p)
  let rec read : List Char → List Char → Nat → Option (List Char × Nat)
    | [], cs, p => some (cs, p)
    | x :: t, c :: cs, p =>
      if x == ' ' then (if ws c then let (r, q) := skip cs (p + c.utf8Size); read t r q else none)
      else if (if c.toNat == 0x2019 then '\'' else c) == x then read t cs (p + c.utf8Size) else none
    | _ :: _, [], _ => none
  (ts.foldlM (fun (acc : List (Nat × Nat) × List Char × Nat) t => do
    let (r, p) := skip acc.2.1 acc.2.2
    let (r', q) ← read (tokStr fx t).toList r p
    pure (acc.1 ++ [(p, q)], r', q)) ([], s.toList, 0)).map Prod.fst

/-! #### The readings with their derivations, from one parse

`witnessed` is `phraseReadings` (`witnessed_readings`) computed from the same one parse, keeping for each meaning its
first derivation and for each reading the meaning (its place in that list) and the table row it comes from. `from` is
read off that derivation, so no act is lexed again and no token is searched for by its text. -/

/-- First occurrences by the key `f`, in order: `firsts` on the keys (`firstsBy_map`). -/
def firstsBy {α β : Type} [DecidableEq β] (f : α → β) : List α → List α
  | [] => []
  | x :: xs => x :: (firstsBy f xs).filter (fun y => f y ≠ f x)

theorem firstsBy_map {α β : Type} [DecidableEq β] (f : α → β) (xs : List α) :
    (firstsBy f xs).map f = firsts (xs.map f) := by
  induction xs with
  | nil => rfl
  | cons x xs ih => simp only [firstsBy, firsts, List.map_cons, ← ih, List.filter_map]; rfl

/-- The listing of `phraseReadings` (`none` its limit), from one parse: each meaning with its first derivation, in the listing's order,
    and each reading with the place of the first meaning whose table row lists it and its place in that row. -/
def witnessed (V : Vocab) (op : Op) (N b : Nat) (ts : Array Lexical.Tok) :
    Option (List (Act × VE.Grammar.Tree Lexical.Tok) × List (List Simple × Nat × Nat)) :=
  match VE.Grammar.parse (grammar V) N b ts with
  | none => none
  | some trees =>
    if N ≤ trees.length then none else
    let ms := firstsBy Prod.fst (trees.filterMap fun t => (valueOf (meaning V) t).map (·, t))
    if maxReadings < ms.length then none else
    let Rs := firstsBy Prod.fst (ms.zipIdx.flatMap fun ((A, _), k) => (table op A).zipIdx.map fun (R, j) => (R, k, j))
    if maxReadings < Rs.length then none else some (ms, Rs)

/-- The readings `witnessed` lists are `phraseReadings`' (one owner), and its limit is theirs. -/
theorem witnessed_readings (V : Vocab) (op : Op) (N b : Nat) (ts : Array Lexical.Tok) :
    phraseReadings V op N b ts = match witnessed V op N b ts with
      | none => .limit
      | some (_, Rs) => .ok (Rs.map Prod.fst) := by
  have hm : ∀ trees : List (VE.Grammar.Tree Lexical.Tok),
      (firstsBy Prod.fst (trees.filterMap fun t => (valueOf (meaning V) t).map (·, t))).map Prod.fst =
        firsts (trees.filterMap (valueOf (meaning V))) := by
    intro trees
    rw [firstsBy_map, List.map_filterMap]
    congr 2; funext t; cases valueOf (meaning V) t <;> rfl
  have hr : ∀ ms : List (Act × VE.Grammar.Tree Lexical.Tok),
      (firstsBy Prod.fst (ms.zipIdx.flatMap fun ((A, _), k) =>
        (table op A).zipIdx.map fun (R, j) => (R, k, j))).map Prod.fst =
        firsts ((ms.map Prod.fst).flatMap (table op)) := by
    intro ms
    rw [firstsBy_map, List.map_flatMap]
    congr 1
    have : ∀ (L : List (List Simple)) (k : Nat),
        ((L.zipIdx.map fun (R, j) => (R, k, j)).map Prod.fst) = L := by
      intro L k; simp [List.map_map, Function.comp_def]
    simp only [this]
    rw [List.flatMap_map]
    induction ms with
    | nil => rfl
    | cons m ms ih => simp [List.zipIdx_cons, List.flatMap_cons, ← ih, List.flatMap_map, List.zipIdx_succ]
  unfold phraseReadings readings readingsIn listing witnessed
  cases VE.Grammar.parse (grammar V) N b ts with
  | none => rfl
  | some trees =>
    dsimp only
    by_cases h1 : N ≤ trees.length
    · simp only [h1, if_true]
    · simp only [h1, if_false]
      rw [← hm trees]
      generalize firstsBy Prod.fst (trees.filterMap fun t => (valueOf (meaning V) t).map (·, t)) = ms
      by_cases h2 : maxReadings < ms.length
      · simp only [List.length_map, h2, if_true]
      · simp only [List.length_map, h2, if_false]
        rw [← hr ms]
        generalize firstsBy Prod.fst (ms.zipIdx.flatMap fun ((A, _), k) =>
          (table op A).zipIdx.map fun (R, j) => (R, k, j)) = Rs
        by_cases h3 : maxReadings < Rs.length
        · simp only [List.length_map, h3, if_true]
        · simp only [List.length_map, h3, if_false]

/-- Each leaf of the derivation `t` from place `p` on, with the meaning's content leaves tagged by their place: a
    word as `#p`, a slot other than the subject's `{0}` or a fixed phrase as index `base + p` (`base` is above every
    index of the phrase). The leaves whose word the meaning reads (under a join word, function word or marker rule,
    `J`, `FW`, `MK`), the subject and commas are kept as written: they are the phrase's function tokens. -/
def tagTree (rs : Array RuleS) (base : Nat) (keep : Bool) : VE.Grammar.Tree Lexical.Tok → Nat →
    VE.Grammar.Tree Lexical.Tok × Nat
  | .leaf t, p => (.leaf (if keep then t else match t with
      | .word _ => .word ("#" ++ toString p)
      | .slot 0 => .slot 0
      | .slot _ => .slot (base + p)
      | .fixed _ => .fixed (base + p)
      | .comma => .comma), p + 1)
  | .node i kids, p =>
    let keep' := keep || (match rs[i]? with
      | some ⟨.J, _, _⟩ | some ⟨.FW, _, _⟩ | some ⟨.MK _, _, _⟩ => true
      | _ => false)
    let (ks, q) := kids.attach.foldl (fun (acc : List (VE.Grammar.Tree Lexical.Tok) × Nat) ⟨k, _⟩ =>
      let (k', q) := tagTree rs base keep' k acc.2
      (acc.1 ++ [k'], q)) ([], p)
    (.node i ks, q)
termination_by t => sizeOf t
decreasing_by have := List.sizeOf_lt_of_mem ‹_›; simp_wf; omega

/-- A tagged token's place in the phrase, `none` for a token the meaning writes itself. -/
def placeOf (base : Nat) : Lexical.Tok → Option Nat
  | .word w => if w.startsWith "#" then (w.drop 1).toNat? else none
  | .slot i | .fixed i => if base ≤ i then some (i - base) else none
  | .comma => none

/-- One token, read as the grammar's terminals read a word (`Term.accepts`: case-insensitively). -/
def sameTok : Lexical.Tok → Lexical.Tok → Bool
  | .word v, .word w => v.toLower == w.toLower
  | t, u => t == u

/-- An act's tokens: an atom's normal form (`Atom.text`'s tokens), a whole join's atoms joined as `Act.text` joins
    them (`listText`: commas, then the join word). Read off a tagged meaning, each content token is its place. -/
def Act.toks (inf : Option Bool) : Act → List Lexical.Tok
  | .one a => (a.withTo inf).normal
  | .all _ _ ps => .slot 0 :: joinToks (.word "and") (ps.map fun a => (a.withTo inf).normal.drop 1)
  | .any nor _ ps => .slot 0 :: joinToks (.word (if nor then "nor" else "or")) (ps.map fun a => (a.withTo inf).normal.drop 1)
where
  joinToks (j : Lexical.Tok) : List (List Lexical.Tok) → List Lexical.Tok
    | [] => []
    | [x] => x
    | [x, y] => x ++ [j] ++ y
    | x :: rest => x ++ [.comma] ++ joinToks j rest

def Simple.toks (inf : Option Bool) : Simple → List Lexical.Tok
  | .atom a => (a.withTo inf).normal
  | .whole A => Act.toks inf A

/-- An act's `from`, its tokens `xs` read off the tagged derivation: a content token at its place; a token the
    meaning writes itself (the subject, *to*, *be*, a marker's or join word, a comma) at the nearest equal function
    token of the phrase (`fn`) before the next content token new to the act (a shared token read again, as in a whole
    join, is no anchor); a token the rendering adds that the phrase lacks (*to* after *has the right*) has none; each
    place once, in the act's order. Every index is a phrase token's. -/
def fromOf (ps : List Lexical.Tok) (fn : List Nat) (base : Nat) (xs : List Lexical.Tok) : List Nat :=
  let places := xs.map (placeOf base)
  -- a content token's place, marked `true` when no earlier token of the act has it
  let fresh := (places.foldl (fun (acc : List (Option (Nat × Bool)) × List Nat) o => match o with
    | some p => (acc.1 ++ [some (p, !acc.2.contains p)], acc.2 ++ [p])
    | none => (acc.1 ++ [none], acc.2)) ([], [])).1
  let marked := ((xs.zip fresh).foldr (fun (x, o) (acc : List (Lexical.Tok × Option Nat × Nat) × Nat) =>
    match o with
    | some (p, true) => ((x, some p, p) :: acc.1, p)
    | some (p, false) => ((x, some p, acc.2) :: acc.1, acc.2)
    | none => ((x, none, acc.2) :: acc.1, acc.2)) ([], ps.length)).1
  marked.foldl (fun acc (x, o, next) =>
    let at? := match o with
      | some p => if p < ps.length then some p else none
      | none => (fn.filter fun i => i < next && (ps[i]?.map (sameTok x)).getD false).max?
    match at? with
    | some i => if acc.contains i then acc else acc ++ [i]
    | none => acc) []

/-- One simple act of a reading: `act`, its text as a predicate declares it (*to* exactly when `plain`, as
    `Sources.expected` renders it); `text`, the act under the modal (`sentence`); `from`, its tokens in the phrase,
    read off `x'`, the same act in the tagged meaning. -/
def actJson (fx : List String) (op : Op) (f : Option Lexical.Form) (plain : Bool) (ps : List Lexical.Tok)
    (fn : List Nat) (base : Nat) (x x' : Simple) : Json :=
  Json.mkObj [("act", .str (Simple.text fx (some plain) x)), ("text", .str (sentence fx op f x)),
    ("from", toJson (fromOf ps fn base (Simple.toks (some plain) x')))]

/-- The tagged meaning of a derivation (`piecesOf` on `tagTree`'s tree) and the places of its function tokens. -/
def tagged (V : Vocab) (base : Nat) (t : VE.Grammar.Tree Lexical.Tok) : Option Act × List Nat :=
  let rs := (closed (schema V)).toArray
  let t' := (tagTree rs base false t 0).1
  ((match piecesOf rs t' with | some [.act A'] => some A' | _ => none),
   ((t'.yield.zipIdx).filter fun (x, _) => (placeOf base x).isNone).map (·.2))

/-- One reading `R` (its witness `k`, `j`) and its paraphrase: its acts, each read against the same act of the
    tagged meaning (`tags[k]`'s table row `j`), and the paraphrase. -/
def readingJson (fx : List String) (op : Op) (f : Option Lexical.Form) (plain : Bool) (ps : List Lexical.Tok)
    (tags : List (Option Act × List Nat)) (base : Nat) (x : (List Simple × Nat × Nat) × String) : Json :=
  let ((R, k, j), text) := x
  let (A', fn) := tags.getD k (none, [])
  let R' := ((A'.map (table op)).getD []).getD j []
  Json.mkObj [("acts", Json.arr (R.zipIdx.map fun (x, i) => actJson fx op f plain ps fn base x (R'.getD i x)).toArray),
    ("paraphrase", .str text)]

/-- The phrase's tag base: above every slot and fixed-phrase index it writes. -/
def tagBase (ps : List Lexical.Tok) : Nat :=
  ps.foldl (fun m t => match t with | .slot i | .fixed i => max m (i + 1) | _ => m) 0

/-- The readings' rows: their paraphrases first, refused with D-32 (`paraphrases`, "this act phrase") when two read
    the same, then each reading's acts, read against its meaning's tagged derivation (each meaning tagged once). -/
def rowsOf (fx : List String) (V : Vocab) (op : Op) (f : Option Lexical.Form) (plain : Bool) (ps : List Lexical.Tok)
    (ms : List (Act × VE.Grammar.Tree Lexical.Tok)) (Ws : List (List Simple × Nat × Nat)) :
    Except String (List Json) := do
  let texts ← paraphrases fx op f "this act phrase" (Ws.map Prod.fst)
  let tags := ms.map fun (_, t) => tagged V (tagBase ps) t
  pure ((Ws.zip texts).map (readingJson fx op f plain ps tags (tagBase ps)))

/-- The `LISTED` row: the phrase's token spans, then each reading's acts and paraphrase. The limits come first: the
    act phrase's 400 bytes, the lexing (`decodeFixed`'s limits), the parse limits; then D-32 (`paraphrases`). -/
def listReadings (id : String) (fx : List String) (V : Vocab) (op : Op) (f : Option Lexical.Form) (plain : Bool)
    (phrase : String) : Except String Json := do
  if Lexical.maxActBytes < phrase.utf8ByteSize then
    throw s!"ResourceLimit: this act phrase is over {Lexical.maxActBytes} bytes"
  let ts ← (Lexical.lex fx phrase).mapError fun e =>
    if e == "comma" then "InvalidInput: this act phrase ends with a comma" else e
  let some sp := spans fx phrase ts | throw "InvalidInput: this act phrase writes a slot with a leading zero"
  match witnessed V op rawCap stepBudget ts.toArray with
  | none => throw "ResourceLimit: this act phrase has too many readings to list; split the sentence"
  | some (_, []) => throw "InvalidInput: this act phrase has no reading under the declared frames and its modal words"
  | some (ms, Ws) =>
    let rows ← rowsOf fx V op f plain ts ms Ws
    pure (VE.Route.Wire.ok id [("verdict", .str "LISTED"),
      ("tokens", Json.arr (sp.map fun (a, b) => Json.arr #[toJson a, toJson b]).toArray),
      ("readings", Json.arr rows.toArray)])

/-- A refusal's verdict: `LIMIT` exactly when it is a `ResourceLimit`, else `REFUSED`. -/
def verdictOf (d : String) : String := if d.startsWith "ResourceLimit:" then "LIMIT" else "REFUSED"

/-- A refusal of the phrase: its verdict and diagnostic, both lists empty. -/
def refusedRow (id d : String) : Json :=
  VE.Route.Wire.ok id [("verdict", .str (verdictOf d)), ("tokens", Json.arr #[]), ("readings", Json.arr #[]),
    ("diagnostic", .str d)]

/-- The request's members (7): `form`, a plain act's form, may be absent (the service's JSON has no `null`). -/
def decodeRequest (j : Json) :
    Except String (String × String × List String × VE.Norms.Role × Bool × Option Lexical.Form) := do
  VE.Bridge.exactFields j (["id", "phrase", "fixed", "frames", "adverbs", "role", "sign"] ++
    if (j.getObjVal? "form").isOk then ["form"] else [])
  let role ← match j.getObjValD "role" with
    | .str "permission" => pure VE.Norms.Role.permission
    | .str "obligation" => pure .obligation
    | .str "plain" => pure .plain
    | _ => throw "InvalidInput: role is not permission, obligation or plain"
  let .bool sign := j.getObjValD "sign" | throw "InvalidInput: sign is not a boolean"
  let f ← match j.getObjVal? "form" with
    | .error _ => pure none
    | .ok (.str t) => match Lexical.Form.ofText? t with
      | some f => pure (some f)
      | none => throw "InvalidInput: form is not has the right or is entitled"
    | _ => throw "InvalidInput: form is not has the right or is entitled"
  pure (← VE.Bridge.stringField j "id", ← VE.Bridge.stringField j "phrase", ← VE.Bridge.strings (j.getObjValD "fixed"),
    role, sign, f)

/-- The frames and adverbs (`decodeVocab`, D-31), the op of the role and sign (`opOf`), then `listReadings`. -/
def listed (j : Json) (id phrase : String) (fx : List String) (role : VE.Norms.Role) (sign : Bool)
    (f : Option Lexical.Form) : Except String Json := do
  let V ← VE.Acts.Wire.decodeVocab (Json.mkObj [("frames", j.getObjValD "frames"), ("adverbs", j.getObjValD "adverbs")])
  let some op := opOf ⟨"", [], false, role, none, none⟩ sign
    | throw "InvalidInput: this act phrase has no modal word: a plain act with sign false"
  listReadings id fx V op f (role == .plain) phrase

/-- `act-readings`: a malformed request is the case's error, a refusal of its content a `REFUSED` or `LIMIT` row. -/
def runActReadings (j : Json) : Except String Json := do
  let (id, phrase, fx, role, sign, f) ← decodeRequest j
  pure (match listed j id phrase fx role sign f with
    | .ok row => row
    | .error d => refusedRow id d)

def actReadingsReported (j : Json) : Json :=
  match runActReadings j with
  | .ok row => row
  | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]

end VE.Acts.Run
