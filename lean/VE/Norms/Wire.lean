import VE.Norms.SmallModel
import VE.Route.Run

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

Scope: FOL documents without W3 definitions (W3's decoder is not on this
branch). W2 admission and report theorems are in `Norms.Admission` and
`Norms.Run`. -/
namespace VE.Norms.Wire
open Lean
open VE.Bridge (exactFields fields stringField strings)

/-- Python `ve/environment.py` `RESERVED`, the words an act phrase may not use. -/
def actReserved : List String :=
  ["true", "false", "is", "equals", "not", "and", "or", "if", "then", "for", "every", "there",
   "exists", "believes", "must", "eventually"]

/-- `{d}` slot occurrences in order, and the text with every slot replaced by
`slot` (Python `re.findall`/`re.sub` on `\{([0-9]+)\}`); fuel is the length. -/
def scanSlotsAux : Nat → List Char → List String × List Char
  | 0, cs => ([], cs)
  | _ + 1, [] => ([], [])
  | n + 1, '{' :: rest =>
    let digits := rest.takeWhile Char.isDigit
    match rest.drop digits.length with
    | '}' :: after =>
      if digits.isEmpty then
        let (ss, out) := scanSlotsAux n rest
        (ss, '{' :: out)
      else
        let (ss, out) := scanSlotsAux n after
        (String.mk digits :: ss, "slot".toList ++ out)
    | _ =>
      let (ss, out) := scanSlotsAux n rest
      (ss, '{' :: out)
  | n + 1, c :: rest =>
    let (ss, out) := scanSlotsAux n rest
    (ss, c :: out)

def scanSlots (cs : List Char) : List String × List Char := scanSlotsAux (cs.length + 1) cs

/-- Python `str.isspace`, the separator set of the no-argument `str.split()`
that Python `_regulated` normalises act phrases with (wider than
`Char.isWhitespace`: vertical tab, form feed, U+001C–U+001F, U+0085, no-break
and the Unicode space separators). -/
def pyWhitespace (c : Char) : Bool :=
  let n := c.toNat
  (0x09 ≤ n && n ≤ 0x0D) || (0x1C ≤ n && n ≤ 0x20) || n == 0x85 || n == 0xA0 ||
    n == 0x1680 || (0x2000 ≤ n && n ≤ 0x200A) || n == 0x2028 || n == 0x2029 ||
    n == 0x202F || n == 0x205F || n == 0x3000

def words (s : String) : List String := (s.split pyWhitespace).filter (· ≠ "")

def asciiLetter (c : Char) : Bool := ('a' ≤ c && c ≤ 'z') || ('A' ≤ c && c ≤ 'Z')

def actWord (w : String) : Bool :=
  match w.toList with
  | c :: cs => asciiLetter c && cs.all (fun d => asciiLetter d || d == '\'' || d == '-')
  | [] => false

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

/-- One `regulated` declaration (3.1), as Python `_regulated` validates it. -/
def decodeRegulated (name : String) (args : List String) (raw : Json) : Except String Regulated := do
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
  let allowed := required ++ (if role == .obligation then ["permission"] else [])
  unless keys.all allowed.contains && required.all keys.contains do
    throw s!"InvalidInput: invalid regulated fields for {name}"
  let act ← if role == .plain then pure none
    else some <$> canonicalAct name args.length (raw.getObjValD "act")
  let permission ← match raw.getObjVal? "permission" with
    | .error _ => pure none
    | .ok .null => pure none
    | .ok (.str m) => pure (some m)
    | .ok _ => throw s!"InvalidInput: invalid permission dual for {name}"
  pure ⟨name, args, allow, role, act, permission⟩

/-- A decoded norms environment: the complete environment, its literals, the
regulated declarations (in vocabulary order) and the original JSON. -/
structure NormsEnvironment where
  rv : VE.Route.Wire.RouteVocabulary
  regulated : List Regulated
  profiles : List String
  json : Json

/-- Separate `regulated` from each predicate entry, decode the rest with the
frozen P0 decoder, then decode and retain every `regulated` extension. -/
def decodeNormsEnvironment (environment : Json) : Except String NormsEnvironment := do
  let e ← VE.Route.Gate.decodeEnvelope environment
  unless e.profiles.contains "norms@0" do throw "UnsupportedProfile: norms@0 is required"
  unless e.family == .fol do
    throw (VE.Route.Gate.unsupported "the norms route admits FOL documents only")
  let vocab := e.vocabulary
  let predicates ← fields (← vocab.getObjVal? "predicates")
  let stripped ← predicates.mapM fun (p, entry) => do
    pure (p, Json.mkObj ((← fields entry).filter (·.1 != "regulated")))
  let vocab' := vocab.setObjVal! "predicates" (Json.mkObj stripped)
  let rv ← VE.Route.Wire.decodeVocabulary vocab'
  let regs ← predicates.filterMapM fun (p, entry) => do
    match entry.getObjVal? "regulated" with
    | .error _ => pure none
    | .ok raw =>
      let args ← strings (← entry.getObjVal? "arguments")
      some <$> decodeRegulated p args raw
  if regs.length > 64 then throw "ResourceLimit: regulated predicates"
  pure ⟨rv, regs, e.profiles, environment⟩

/-- Python hashes `Environment.to_dict()`, which stores normalised act phrases.
Apply that same canonicalisation before any source environment binding. -/
def canonicalEnvironmentJson (environment : Json) : Except String Json := do
  let vocab ← environment.getObjVal? "vocabulary"
  let predicates ← fields (← vocab.getObjVal? "predicates")
  let canonical ← predicates.mapM fun (name, entry) => do
    let entry ← match entry.getObjVal? "regulated" with
      | .error _ => pure entry
      | .ok reg =>
        let reg ← match reg.getObjVal? "act" with
          | .error _ => pure reg
          | .ok act =>
            let args ← strings (← entry.getObjVal? "arguments")
            pure (reg.setObjVal! "act" (.str (← canonicalAct name args.length act)))
        pure (entry.setObjVal! "regulated" reg)
    pure (name, entry)
  pure (environment.setObjVal! "vocabulary"
    (vocab.setObjVal! "predicates" (Json.mkObj canonical)))

/-- One norm object `{"norm": {...}}` (3.2). -/
def decodeNorm (j : Json) : Except String Node := do
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
  let guard ← VE.Bridge.decodeFormula 64 (raw.getObjValD "guard")
  let carve ← unlessJ.mapM (VE.Bridge.decodeFormula 64)
  pure ⟨name, predicate, sign, guard, carve, over⟩

/-- A decoded source: the norms environment and a well-formed tree over it. -/
structure Source where
  ne : NormsEnvironment
  D : Doc
  wf : WellFormed D = true
  env : D.E = ne.rv.environment
  lits : D.lits = ne.rv.literals

/-- Decode the environment and the norm objects (no W3 definitions on this
path); the diagnostics are those of `validate`. -/
def decodeSource (environment norms : Json) : Except String Source := do
  let ne ← decodeNormsEnvironment environment
  let units ← match norms with
    | .arr xs => pure xs.toList
    | _ => throw "InvalidInput: norms must be an array"
  if units.length > 256 then throw "ResourceLimit: rules"
  let nodes ← units.mapM decodeNorm
  let D : Doc := ⟨ne.rv.environment, ne.rv.literals, ⟨ne.regulated, [], nodes⟩⟩
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
