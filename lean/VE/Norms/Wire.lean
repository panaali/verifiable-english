import VE.Acts.Lexical
import VE.Norms.LayersOnce
import VE.Route.Gate
import VE.Route.Wire
import VE.Limits

/-! The norms-route decoder (docs/spec/norms.md 3.1, 3.2 and 11.4 steps 1-3),
for the regeneration cases of the `ve_norms_route` executable.

The frozen `Route.Wire.decodeVocabulary` rejects the `regulated` field. This
decoder separates the recognised `regulated` extension from each predicate
entry, validates the ordinary declaration fields with the frozen decoder,
validates the extension exactly as Python `ve/environment.py` does (role,
default, act phrase lint, dual field), and keeps the original environment JSON
for identity. Norm objects (3.2) are decoded into `Node`s. Nothing on the wire
supplies an elaboration: premises, Background and conflict formulas are
regenerated from the decoded values.

Scope: FOL documents, with W3 definitions; `data@0` flags on document
admission only (`decodeSource`). W2 admission and report theorems are in `Norms.Admission` and
`Norms.Run`. -/
namespace VE.Norms.Wire
open Lean
open VE.Bridge (exactFields fields stringField strings)

/-- The canonical act phrase: whitespace normalised, slots `{0}…{k-1}` in order,
at most 80 characters, at least two words, no reserved word. -/
def canonicalAct (name : String) (arity : Nat) (raw : Json) : Except String String := do
  let act := " ".intercalate (words ((raw.getStr?).toOption.getD ""))
  let (slots, replaced) := scanSlots act.toList
  let ws := words (String.mk replaced)
  unless act.length ≤ 80 && act.startsWith "{0} " &&
      slots == (List.range arity).map toString && ws.length ≥ 2 &&
      ws.all actWord && !(ws.any (fun w => w != "slot" && actReserved.contains w.toLower)) do
    throw s!"InvalidInput: invalid act phrase for {name}"
  pure act

/-- The act check of a document's profiles: `Acts.Lexical.check` with the document's fixed phrases `fx` under
`acts@0` (act-phrases 3.3), `canonicalAct` otherwise. -/
def canonicalActIn (profiles fx : List String) (name : String) (k : Nat) (raw : Json) : Except String String :=
  if profiles.contains "acts@0" then VE.Acts.Lexical.check fx name k raw else canonicalAct name k raw

/-- One `regulated` declaration (3.1), as Python `_regulated` validates it, with the act check `actCheck`. With
`acts` (act-phrases 3.2) a plain declaration may carry an act and its form, both or neither. -/
def decodeRegulatedWith (acts : Bool) (actCheck : String → Nat → Json → Except String String) (name : String)
    (args : List String) (raw : Json) : Except String Regulated := do
  let obj ← match raw.getObj? with
    | .ok o => pure o.toList
    | .error _ => throw s!"InvalidInput: regulated declaration {name} needs role and default"
  let keys := obj.map Prod.fst
  unless keys.contains "role" && keys.contains "default" do
    throw s!"InvalidInput: regulated declaration {name} needs role and default"
  let role ← match raw.getObjValD "role" with
    | .str "permission" => pure Role.permission
    | .str "obligation" => pure Role.obligation
    | .str "plain" => pure Role.plain
    | _ => throw s!"InvalidInput: invalid regulated role or default for {name}"
  let allow ← match raw.getObjValD "default" with
    | .str "allow" => pure true
    | .str "deny" => pure false
    | _ => throw s!"InvalidInput: invalid regulated role or default for {name}"
  let required := ["role", "default"] ++ (if role == .plain then [] else ["act"])
  let allowed := required ++ (if role == .obligation then ["permission"] else []) ++
    (if acts && role == .plain then ["act", "form"] else [])
  unless keys.all allowed.contains && required.all keys.contains do
    throw s!"InvalidInput: invalid regulated fields for {name}"
  if acts && role == .plain then
    if keys.contains "act" != keys.contains "form" then
      throw s!"InvalidInput: a plain act for {name} needs its form, and a form needs its act"
    if keys.contains "form" && ((raw.getObjValD "form").getStr?.toOption.bind VE.Acts.Lexical.Form.ofText?).isNone then
      throw s!"InvalidInput: invalid form for {name}"
  let act ← if role == .plain && !(acts && keys.contains "act") then pure none
    else some <$> actCheck name args.length (raw.getObjValD "act")
  let permission ← match raw.getObjVal? "permission" with
    | .error _ => pure none
    | .ok .null => pure none
    | .ok (.str m) => pure (some m)
    | .ok _ => throw s!"InvalidInput: invalid permission dual for {name}"
  pure ⟨name, args, allow, role, act, permission⟩

/-- One `regulated` declaration under a document's profiles, with its fixed phrases `fx` (act-phrases 4.2). -/
def decodeRegulatedIn (profiles fx : List String) : String → List String → Json → Except String Regulated :=
  decodeRegulatedWith (profiles.contains "acts@0") (canonicalActIn profiles fx)

/-- One `regulated` declaration without `acts@0`. -/
def decodeRegulated : String → List String → Json → Except String Regulated :=
  decodeRegulatedWith false canonicalAct

theorem canonicalActIn_without_acts (ps fx : List String) (h : "acts@0" ∉ ps) :
    canonicalActIn ps fx = canonicalAct := by
  funext name k raw
  simp [canonicalActIn, h]

/-- Without `acts@0` a declaration decodes as today, whatever the fixed phrases (act-phrases 4.3). -/
theorem decodeRegulated_without_acts (ps fx : List String) (h : "acts@0" ∉ ps) :
    decodeRegulatedIn ps fx = decodeRegulated := by
  simp only [decodeRegulatedIn, decodeRegulated, canonicalActIn_without_acts ps fx h,
    show ps.contains "acts@0" = false by simpa using h]

/-- The branch an `if` that answered `.ok` took, with its condition. -/
theorem ite_ok_cases {ε α : Type} {c : Prop} [Decidable c] {a b : Except ε α} {r : α}
    (h : (if c then a else b) = .ok r) : (c ∧ a = .ok r) ∨ (¬c ∧ b = .ok r) := by
  by_cases hc : c
  · exact .inl ⟨hc, by simpa [hc] using h⟩
  · exact .inr ⟨hc, by simpa [hc] using h⟩

/-- Today's decoder never produces an act on a plain predicate, so `Tree.check`'s dropped refusal admits only
    `acts@0` documents. -/
theorem decodeRegulated_plain {name : String} {args : List String} {raw : Lean.Json} {r : VE.Norms.Regulated}
    (h : decodeRegulated name args raw = .ok r) (hp : r.role = .plain) : r.act = none := by
  -- walk the decoder one step at a time: a bind, an `if` with its condition, or a `match`; a leaf is a refusal,
  -- or a declaration whose role and act the steps fixed
  simp only [decodeRegulated, decodeRegulatedWith] at h
  repeat' (first
    | (cases h; done)
    | (cases h; first | rfl | cases hp)
    | (have h' := VE.Order.ProfileGate.bind_ok h; clear h; obtain ⟨_, _, h⟩ := h'; try dsimp only at h)
    | (have h' := ite_ok_cases h; clear h
       rcases h' with ⟨hc, h⟩ | ⟨hc, h⟩ <;> try (simp at hc; done))
    | split at h)
  all_goals simp_all [pure, Except.pure]

/-- The wording of a plain act (act-phrases 2.1): `Lexical.wording` of the form its declaration `raw` carries; none
for any other declaration. Lean's English (`modalForm`) and the norms route's `wordings` read it. -/
def plainWording (r : Regulated) (raw : Json) : Option String :=
  match r.role, r.act, (raw.getObjValD "form").getStr?.toOption.bind VE.Acts.Lexical.Form.ofText? with
  | .plain, some act, some f => some (VE.Acts.Lexical.wording f act)
  | _, _, _ => none

/-- A decoded norms environment: the complete environment, its literals, the
regulated declarations (in vocabulary order) and the original JSON. -/
structure NormsEnvironment where
  rv : VE.Route.Wire.RouteVocabulary
  regulated : List Regulated
  profiles : List String
  json : Json

/-- The wording of each plain act of `ne` by its predicate, in vocabulary order (the norms route's `wordings`). -/
def plainWordings (ne : NormsEnvironment) : List (String × String) :=
  ne.regulated.filterMap fun r => (plainWording r ((((ne.json.getObjValD "vocabulary").getObjValD
    "predicates").getObjValD r.name).getObjValD "regulated")).map (r.name, ·)

/-- The fixed phrases of an environment's `acts` block (act-phrases 3.1), each checked by `Lexical.decodeFixed`,
when its profiles `ps` are read with `acts@0`; else none. An absent block is the empty block. -/
def actsFixed (ps : List String) (environment : Json) : Except String (List String) :=
  match ps.isEmpty, (environment.getObjValD "vocabulary").getObjVal? "acts" with
  | false, .ok block => do
    exactFields block ["fixed"]
    let fx ← strings (← block.getObjVal? "fixed")
    let _ ← VE.Acts.Lexical.decodeFixed fx
    pure fx
  | _, _ => pure []

/-- `acts@0`'s refusal on the checker family `f` (act-phrases 4.4), which the profile row and the plain route read. -/
def actsFamilyRefusal (f : String) : String := s!"acts@0 on the {f} family is not implemented"

/-- Whether `acts@0` is read from the profiles `ps`: they list it and are sorted and unique. Any other list keeps
`acts@0`, and the envelope decoder refuses the list as the base refuses it. -/
def readsActs (ps : List String) : Bool := ps.contains "acts@0" && decide (ps.Pairwise (· < ·))

/-- The profiles of an environment from which `acts@0` is read (`readsActs`), when `acts` lets the decoder read
it; else none. -/
def actsProfiles (acts : Bool) (environment : Json) : List String :=
  match acts, VE.Route.Gate.profilesOf environment with
  | true, .ok ps => if readsActs ps then ps else []
  | _, _ => []

/-- What the frozen envelope and vocabulary decoders read of an `acts@0` environment: the environment without
`acts@0` in `ps` and without the `acts` block, when `acts@0` is read from `ps`; else the environment as it is. -/
def actsView (environment : Json) (ps : List String) : Json :=
  let vocab := match environment.getObjValD "vocabulary" with
    | .obj kvs => Json.obj (kvs.erase "acts")
    | v => v
  if readsActs ps then (environment.setObjVal! "profiles" (toJson (ps.erase "acts@0"))).setObjVal! "vocabulary" vocab
  else environment

/-- Separate `regulated` from each predicate entry, decode the rest with the
frozen P0 decoder, then decode and retain every `regulated` extension. With
`acts`, an environment listing `acts@0` is read with its `acts` block and the
act check of act-phrases 3.2; without it, `acts@0` is refused as today. -/
def decodeNormsEnvironment (environment : Json)
    (displayConstants : Bool := true) (acts : Bool := false) : Except String NormsEnvironment := do
  let ps := actsProfiles acts environment
  let e ← VE.Route.Gate.decodeEnvelope (if ps.isEmpty then environment else actsView environment ps)
  unless e.profiles.contains "norms@0" do throw "UnsupportedProfile: norms@0 is required"
  unless e.family == .fol do
    throw (VE.Route.Gate.unsupported "the norms route admits FOL documents only")
  let fx ← actsFixed ps environment
  let vocab := e.vocabulary
  let predicates ← fields (← vocab.getObjVal? "predicates")
  let stripped ← predicates.mapM fun (p, entry) => do
    pure (p, Json.mkObj ((← fields entry).filter (·.1 != "regulated")))
  let vocab' := vocab.setObjVal! "predicates" (Json.mkObj stripped)
  let rv ← VE.Route.Wire.decodeVocabulary e.profiles vocab' displayConstants
  let regs ← predicates.filterMapM fun (p, entry) => do
    match entry.getObjVal? "regulated" with
    | .error _ => pure none
    | .ok raw =>
      if (entry.getObjVal? "defined").isOk then
        throw s!"RegulatedDefinedPredicate: {p}"
      if (entry.getObjVal? "functional").isOk || (entry.getObjVal? "total").isOk then
        throw s!"RegulatedFlag: {p}"
      let args ← strings (← entry.getObjVal? "arguments")
      some <$> decodeRegulatedIn ps fx p args raw
  if regs.length > 64 then throw "ResourceLimit: regulated predicates"
  actChecks regs
  pure ⟨rv, regs, if ps.isEmpty then e.profiles else ps, environment⟩

/-- Python hashes `Environment.to_dict()`, which stores normalised act phrases.
Apply that same canonicalisation before any source environment binding: each act by
`canonicalActIn` with the environment's profiles and fixed phrases (act-phrases 3.3). -/
def canonicalEnvironmentJson (environment : Json) : Except String Json := do
  let vocab ← environment.getObjVal? "vocabulary"
  let predicates ← fields (← vocab.getObjVal? "predicates")
  let ps := actsProfiles true environment
  let fx ← actsFixed ps environment
  let canonical ← predicates.mapM fun (name, entry) => do
    let entry ← match entry.getObjVal? "regulated" with
      | .error _ => pure entry
      | .ok reg =>
        let reg ← match reg.getObjVal? "act" with
          | .error _ => pure reg
          | .ok act =>
            let args ← strings (← entry.getObjVal? "arguments")
            pure (reg.setObjVal! "act" (.str (← canonicalActIn ps fx name args.length act)))
        pure (entry.setObjVal! "regulated" reg)
    pure (name, entry)
  pure (environment.setObjVal! "vocabulary"
    (vocab.setObjVal! "predicates" (Json.mkObj canonical)))

/-- The act of each regulated predicate of `canonical` (`canonicalEnvironmentJson`'s result) by its predicate, in
vocabulary order: the canonical acts the environment identity hashes. The environment row gives them (`acts`) and
Python stores each as its predicate's act, so the identity determines the environment Python builds (ap-1bb). -/
def canonicalActs (canonical : Json) : Except String (List (String × String)) := do
  let predicates ← fields (← (← canonical.getObjVal? "vocabulary").getObjVal? "predicates")
  predicates.filterMapM fun (p, entry) =>
    match (entry.getObjValD "regulated").getObjVal? "act" with
    | .ok act => do pure (some (p, ← act.getStr?))
    | .error _ => pure none

/-- Append generated predicate declarations to the actual environment vocabulary. Both
soft-norms and rights use this operation, and the response-shape proof fixes its entries. -/
def appendPredicates (environment : Json) (entries : List (String × Json)) : Except String Json := do
  let vocab ← environment.getObjVal? "vocabulary"
  let preds ← fields (← vocab.getObjVal? "predicates")
  pure (environment.setObjVal! "vocabulary" (vocab.setObjVal! "predicates"
    (Json.mkObj (preds ++ entries))))

/-- The append operation exposes the predicate object of the returned environment. In
particular the generated entries are in the final object, after the source entries. -/
theorem appendPredicates_assembly (environment : Json) (entries : List (String × Json)) :
    appendPredicates environment entries = (do
      let vocab ← environment.getObjVal? "vocabulary"
      let preds ← fields (← vocab.getObjVal? "predicates")
      pure (environment.setObjVal! "vocabulary" (vocab.setObjVal! "predicates"
        (Json.mkObj (preds ++ entries))))) := rfl

/-! Python's `_Decoder` over the FOL fragment: `Bridge.decodeFormula 64` plus
the node budget (`MAX_NODES`) and `MAX_INDEX`. One decoder counts every formula
and term node in pre-order and checks the budget on entering a node, before its
shape; `count` is the number of nodes the same decoder has already read. -/

export VE.Limits (maxNodes maxIndex)

def budgetTerm (count : Nat) (j : Json) : Except String (VE.Term × Nat) := do
  if count + 1 > maxNodes then throw "ResourceLimit: AST exceeds depth or node budget"
  let t ← VE.Bridge.decodeTerm j
  if let .var i := t then
    unless i ≤ maxIndex do throw "UnboundVariable: Invalid variable index"
  pure (t, count + 1)

def budgetFormula : Nat → Nat → Json → Except String (VE.Formula × Nat)
  | 0, _, _ => throw "ResourceLimit: formula depth exceeds 64"
  | n + 1, count, j => do
    let count := count + 1
    if count > maxNodes then throw "ResourceLimit: AST exceeds depth or node budget"
    match (← j.getArr?).toList with
    | [.str "top"] => return (.top, count)
    | [.str "bottom"] => return (.bottom, count)
    | [.str "unary", .str p, t] =>
      let (t, count) ← budgetTerm count t
      return (.unary p t, count)
    | [.str "binary", .str p, t, u] =>
      let (t, count) ← budgetTerm count t
      let (u, count) ← budgetTerm count u
      return (.binary p t u, count)
    | [.str "eq", t, u] =>
      let (t, count) ← budgetTerm count t
      let (u, count) ← budgetTerm count u
      return (.eq t u, count)
    | [.str "not", a] =>
      let (a, count) ← budgetFormula n count a
      return (.not a, count)
    | [.str "and", a, b] =>
      let (a, count) ← budgetFormula n count a
      let (b, count) ← budgetFormula n count b
      return (.and a b, count)
    | [.str "or", a, b] =>
      let (a, count) ← budgetFormula n count a
      let (b, count) ← budgetFormula n count b
      return (.or a b, count)
    | [.str "implies", a, b] =>
      let (a, count) ← budgetFormula n count a
      let (b, count) ← budgetFormula n count b
      return (.implies a b, count)
    | [.str "forall", .str s, a] =>
      let (a, count) ← budgetFormula n count a
      return (.all s a, count)
    | [.str "exists", .str s, a] =>
      let (a, count) ← budgetFormula n count a
      return (.ex s a, count)
    | _ => throw "invalid indexed formula"

/-- One formula under a fresh decoder (Python `_Decoder().decode`). -/
def decodeBudgeted (j : Json) : Except String VE.Formula := (·.1) <$> budgetFormula VE.Limits.maxDepth 0 j

/-- The one decoder of a norm's JSON envelope and scalar fields. The FOL and
family readers decode the returned guard and carve-outs in their own syntax. -/
def normFields (j : Json) : Except String (String × String × Bool × Json × List Json × List String) := do
  exactFields j ["norm"]
  let raw ← j.getObjVal? "norm"
  exactFields raw ["name", "predicate", "sign", "guard", "unless", "over"]
  let name ← match raw.getObjValD "name" with
    | .str s => pure s
    | _ => throw "InvalidInput: invalid rule name"
  let predicate ← stringField raw "predicate"
  let sign ← match raw.getObjValD "sign" with
    | .bool b => pure b
    | _ => throw "InvalidInput: invalid sign or too many carve-outs"
  let unlessJ ← match raw.getObjValD "unless" with
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: unless and over must be arrays"
  let over ← match raw.getObjValD "over" with
    | .arr _ => strings (raw.getObjValD "over")
    | _ => throw "InvalidInput: unless and over must be arrays"
  pure (name, predicate, sign, raw.getObjValD "guard", unlessJ, over)

/-- One norm object `{"norm": {...}}` (3.2). As Python `NormDocument._decode`,
one decoder (one node budget) reads the guard and then the carve-outs; with
`shared := false` each formula has its own, as the soft route's `_fol`. -/
def decodeNorm (j : Json) (shared : Bool := true) : Except String Node := do
  let (name, predicate, sign, guardJ, unlessJ, over) ← normFields j
  let (guard, count) ← budgetFormula VE.Limits.maxDepth 0 guardJ
  let mut count := count
  let mut carve := []
  for x in unlessJ do
    let (φ, next) ← budgetFormula VE.Limits.maxDepth (if shared then count else 0) x
    count := next
    carve := carve ++ [φ]
  pure ⟨name, predicate, sign, guard, carve, over⟩

/-- A decoded source: the norms environment and a well-formed tree over it. -/
structure Source where
  ne : NormsEnvironment
  D : Doc
  wf : WellFormed D = true
  env : D.E = ne.rv.environment
  lits : D.lits = ne.rv.literals

/-- Decode the environment and the norm objects; W3 definitions join the tree as
layer symbols. The diagnostics are those of `validate`.

`data@0` flags are admitted only when `flags` is set, which document admission
does: its Background leaves `background:flags` are W2's (`Route.Admission`,
regenerated from the decoded flags), and its report theorem takes the flag
premises as a separate hypothesis. Every other norms case keeps the gate, since
its regenerated Background and conflict checks are stated over literals and
profile premises only (`backgroundBase`). The norms route reads `acts@0`
(act-phrases 2.8); a route that does not hook it calls `decodeNormsEnvironment`
without `acts`, or refuses the profile before it calls this. -/
def decodeSource (environment norms : Json) (flags : Bool := false)
    (displayConstants : Bool := true) : Except String Source := do
  let ne ← decodeNormsEnvironment environment displayConstants (acts := true)
  unless ne.rv.definitions.isEmpty || ne.profiles.contains "definitions@0" do
    throw "defined declarations require the definitions@0 profile"
  unless flags || ne.rv.flags.isEmpty do
    throw "UnsupportedProfile: norms route with data flags is not implemented"
  let units ← match norms with
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: norms must be an array"
  if units.length > 256 then throw "ResourceLimit: rules"
  let nodes ← units.mapM decodeNorm
  let defs := ne.rv.definitions.map fun d => ({ name := d.name, args := d.args, body := d.body } : Definition)
  let D : Doc := ⟨ne.rv.environment, ne.rv.literals, ⟨ne.regulated, defs, nodes⟩⟩
  match hv : validate D with
  | .error e => throw e
  | .ok () => pure ⟨ne, D, by unfold WellFormed; rw [hv], rfl, rfl⟩

/-! ## Regenerated outputs -/

def enc (a : VE.Formula) : Json := VE.Route.Wire.encodeFormula a

/-- The regenerated route premises, Background and conflict targets. -/
def regenerated (D : Doc) : List (String × Json) :=
  [("order", toJson (layerNames D.T)),
   ("background", Json.arr (((definitionPremises D.T).map (fun a => ("definitions", a)) ++
       (backgroundBase D).map (fun a => ("literals", a)) ++
       (pairPremises D.T).map (fun a => ("profile", a))).map
     (fun (g, a) => Json.mkObj [("generator", .str g), ("ast", enc a)])).toArray),
   ("premises", Json.arr ((syms D.T).filterMap (fun
       | .reg r => some (Json.mkObj [("label", .str ("layer:norms:" ++ r.name)),
           ("ast", enc (elabPremise D.T r))])
       | .defn _ => none)).toArray),
   ("conflict_targets", Json.arr ((((syms D.T).filterMap (fun
       | .reg r => some (Json.mkObj [("target", .str r.name), ("sorts", toJson r.sorts),
           ("ast", enc (conflict D r))])
       | .defn _ => none)) ++
     (pairs D.T).map (fun pr => Json.mkObj [("target", .str (pr.req ++ "->" ++ pr.perm)),
       ("sorts", toJson pr.sorts), ("ast", enc (pairConflict D pr))]))).toArray),
   ("fragment", .bool (InFragment D))]

end VE.Norms.Wire
