import VE.Defaults.Premises

/-! DF-1a's synthetic fixtures (docs/spec/defeasible.md 8.1 and 8.2, DF-α to DF-ζ, DF-ι, DF-κ, DF-σ) on the premises, the
basis and the form. Each document is decoded by the real `decodeSoftU`; every value is a `#guard`.

Situations have one entity per sort. The one-element check (`check1`, RD-9's `modelCheckX` with `localFree`) is
complete for these documents: every premise and conclusion is universal over one tuple of variables and every
predicate takes exactly that tuple, so a countermodel restricts to the one-element substructure at a failing tuple.
`assume1` is `assumptionsOf` with that complete check in place of a certificate check (spec 8.0); `assumptionsOf`
itself runs on two certificates written here (DF-α). Named strict countermodels are checked on the wire
(`situationX`, `decodeFilling`, RD-9's `xModelOk`). -/
namespace VE.Defaults.Fixtures
open Lean
open VE.Norms (bindAll atom anyF)
open VE.SoftNorms (SoftDoc collidingPairs)
open VE.NormDefaults (UDoc fill unsaidName unsaidNames)
open VE.NormDefaults.Wire (LayeredU)
open VE.Defaults

abbrev Entity := VE.Bridge.Entity

/-! ## Documents (spec 8.0's frame) -/

def regJ (name args role dflt : String) (extra : String := "") : String :=
  "\"" ++ name ++ "\":{\"arguments\":" ++ args ++ ",\"description\":\"" ++ name ++ "\",\"regulated\":{\"role\":\"" ++
    role ++ "\",\"default\":\"" ++ dflt ++ "\"" ++ extra ++ "}}"
def xReq (dflt : String := "unspecified") : String :=
  regJ "x_required" "[\"assistant\"]" "obligation" dflt ",\"act\":\"{0} do x\",\"permission\":\"x_permitted\""
def xPerm : String := regJ "x_permitted" "[\"assistant\"]" "permission" "allow" ",\"act\":\"{0} do x\""
def baseJ (p : String) : String := "\"" ++ p ++ "\":{\"arguments\":[\"assistant\"],\"description\":\"" ++ p ++ "\"}"

def envJ (preds : List String) (soft : String) : Json :=
  (Json.parse ("{\"language\":\"ve.core@0.2\",\"profiles\":[\"norm-defaults@0\",\"norms@0\",\"relational-fol@0\"," ++
    "\"soft-norms@0\"],\"spec_revision\":\"ve-v0.2-expand2-2026-09-25\",\"vocabulary\":{\"sorts\":{" ++
    "\"assistant\":{\"description\":\"assistant\"}},\"predicates\":{" ++ ",".intercalate preds ++
    "},\"constants\":{},\"soft\":" ++ soft ++ "}}")).toOption.get!

def strictSoft : String := r#"{"outranking":{"mode":"strict"}}"#
def userSoft : String := r#"{"parties":["user"],"outranking":{"mode":"strict"}}"#
def holisticSoft : String :=
  r#"{"ranks":["safety","helpfulness"],"outranks":[["safety","helpfulness"]],"outranking":{"mode":"holistic","decided_by":"assistant"}}"#
def strictRankSoft : String :=
  r#"{"ranks":["safety","helpfulness"],"outranks":[["safety","helpfulness"]],"outranking":{"mode":"strict"}}"#

def ruleJ (name pred : String) (sign : Bool) (fields : String := "") : String :=
  "{\"norm\":{\"name\":\"" ++ name ++ "\",\"predicate\":\"" ++ pred ++ "\",\"sign\":" ++ toString sign ++
    ",\"guard\":[\"top\"],\"unless\":[],\"over\":[]" ++ fields ++ "}}"
def dfltJ (suff : List String := []) (extra : String := "") : String :=
  ",\"mode\":\"default\",\"exception\":{\"decided_by\":\"assistant\",\"sufficient\":[" ++
    ",".intercalate suff ++ "],\"necessary\":[],\"factors\":[]}" ++ extra
def un (p : String) : String := "[\"unary\",\"" ++ p ++ "\",[\"var\",0]]"

def layered (env : Json) (rules : List String) : Except String LayeredU :=
  VE.NormDefaults.Wire.decodeSoftU env ((Json.parse ("[" ++ ",".intercalate rules ++ "]")).toOption.get!)

/-- A fixture's claim on its decoded document; a document that does not decode fails every claim. -/
def holds (e : Except String LayeredU) (f : LayeredU → Bool) : Bool :=
  match e with
  | .ok L => f L
  | .error _ => false
def val {β : Type} [Inhabited β] (e : Except String LayeredU) (f : LayeredU → β) : β :=
  match e with
  | .ok L => f L
  | .error _ => default

def dα : Except String LayeredU := layered (envJ [xReq, xPerm] strictSoft) [ruleJ "r1" "x_required" true dfltJ]
def dβ : Except String LayeredU := layered (envJ [xReq, xPerm, baseJ "urgent"] strictSoft)
  [ruleJ "r1" "x_required" true (dfltJ [un "urgent"])]
def dγ : Except String LayeredU := layered (envJ [xReq, xPerm] strictSoft)
  [ruleJ "r1" "x_required" true dfltJ, ruleJ "r2" "x_permitted" false dfltJ]
def dδ : Except String LayeredU := layered (envJ [xReq, xPerm] holisticSoft)
  [ruleJ "r1" "x_required" true (dfltJ (extra := ",\"rank\":\"safety\"")),
   ruleJ "r2" "x_permitted" false (dfltJ (extra := ",\"rank\":\"helpfulness\""))]
def dδs : Except String LayeredU := layered (envJ [xReq, xPerm] strictRankSoft)
  [ruleJ "r1" "x_required" true (dfltJ (extra := ",\"rank\":\"safety\"")),
   ruleJ "r2" "x_permitted" false (dfltJ (extra := ",\"rank\":\"helpfulness\""))]
def dε : Except String LayeredU := layered (envJ [xReq, xPerm] userSoft)
  [ruleJ "r1" "x_required" true (dfltJ (extra := ",\"alterable\":[\"user\"]"))]
def dζ : Except String LayeredU := layered (envJ [xReq, xPerm] strictSoft)
  [ruleJ "r0" "x_required" true, ruleJ "r1" "x_required" true dfltJ]
def dζ0 : Except String LayeredU := layered (envJ [xReq, xPerm] strictSoft) [ruleJ "r0" "x_required" true]
/-- DF-σ: two strict rules of opposite sign on a `deny` obligation. -/
def dσ : Except String LayeredU := layered (envJ [xReq "deny", xPerm] strictSoft)
  [ruleJ "must-x" "x_required" true, ruleJ "must-not-x" "x_required" false]

/-! ## One-element situations -/

def elemOf (s : String) : Entity := (s, "e_" ++ s)
def sitOf (L : LayeredU) (on : List String) : VE.FiniteModel Entity :=
  { domains := fun s => [elemOf s], constants := fun _ => none,
    relations := fun p => match L.sitVocab.predicates.find? (·.1 == p) with
      | some (_, ss) => if on.contains p then [ss.map elemOf] else []
      | none => [] }
def fillOf (L : LayeredU) (on : List String) : VE.NormDefaults.FiniteFill L.U Entity :=
  fun n => match L.U.unspec.find? (fun p => unsaidName p == n) with
    | some p => if on.contains n then [(VE.NormDefaults.sortsOf L.U.D p).map elemOf] else []
    | none => []

def subsets {α : Type} : List α → List (List α)
  | [] => [[]]
  | x :: xs => let r := subsets xs; r ++ r.map (x :: ·)
def configs (L : LayeredU) : List (List String × List String) :=
  (subsets (L.sitVocab.predicates.map (·.1))).flatMap (fun on => (subsets (unsaidNames L.U)).map (on, ·))

/-- `some v`: the situation passes RD-9's check with `X` and has an expansion; `v` is the conclusion's value. -/
def check1 (L : LayeredU) (X Γ : List VE.Formula) (φ : VE.Formula) (on fon : List String) : Option Bool :=
  let r := VE.NormDefaults.modelCheckX L.U X (sitOf L on) (fillOf L fon) Γ φ
  if r.1 && VE.Readings.Wire.localFree L.U (sitOf L on) (fillOf L fon) then some r.2 else none
def follows1 (L : LayeredU) (X Γ : List VE.Formula) (φ : VE.Formula) : Bool :=
  (configs L).all (fun (on, fon) => (check1 L X Γ φ on fon).getD true)
/-- Some one-element situation admits `X` and `Γ`. -/
def model1 (L : LayeredU) (X Γ : List VE.Formula) : Bool :=
  (configs L).any (fun (on, fon) => (check1 L X Γ .bottom on fon).isSome)
def assume1 (L : LayeredU) (Γ : List VE.Formula) (φ : VE.Formula) : List String :=
  VE.Readings.usedLabels (fun ps => follows1 L ps Γ φ) L.X (dfltLabelled L.D) []
/-- RD-9's `xModelOk` on the wire, at the one-element situation `on` with no filling. -/
def modelJ (L : LayeredU) (on : List String) : Json :=
  Json.mkObj [("complete", true),
    ("domains", Json.mkObj (L.sitVocab.sorts.map (fun s => (s, toJson ["e_" ++ s])))),
    ("constants", Json.mkObj []),
    ("relations", Json.mkObj (L.sitVocab.predicates.map (fun (p, ss) =>
      (p, toJson (if on.contains p then [ss.map ("e_" ++ ·)] else ([] : List (List String)))))))]
def wireOk (L : LayeredU) (X Γ : List VE.Formula) (φ : VE.Formula) (on : List String) : Bool :=
  match VE.NormDefaults.Wire.situationX L (modelJ L on) with
  | .ok S => match VE.NormDefaults.Wire.decodeFilling L.U S.M (Json.mkObj []) with
    | .ok F => VE.Readings.Wire.xModelOk L.U X [] Γ φ ⟨S.M, S.valid, F⟩ false
    | .error _ => false
  | .error _ => false

def xAll : VE.Formula := .all "assistant" (.unary "x_required" (.var 0))
def exc1 : String := "soft__excepted__r1"

/-! ## Two certificates on DF-α, over `premisesX U (defaultX D X) []` (indices 0 to 4; `Dflt_T`'s premise is 1)

`cNeeds` proves `∀a. ¬excepted_r1(a)` from `Dflt_T`'s premise; `cStrict` proves `∀a. excepted_r1(a) → excepted_r1(a)`
from nothing. -/

def cert (t : VE.Tableau.Trace) : VE.Tableau.Certificate := ⟨"ve-tableau-checker@2", "", [], "", t⟩
def notExc : VE.Formula := .all "assistant" (.not (.unary exc1 (.var 0)))
def excSelf : VE.Formula := .all "assistant" (.implies (.unary exc1 (.var 0)) (.unary exc1 (.var 0)))
open VE.Tableau.Trace in
def cNeeds : VE.Tableau.Certificate := cert (expand 5 none [expand 6 none [expand 1 (some "w:0") [expand 8 none [close, close]]]])
open VE.Tableau.Trace in
def cStrict : VE.Tableau.Certificate := cert (expand 5 none [expand 6 none [close]])
def ps (L : LayeredU) (Γ : List VE.Formula) : List VE.Formula := VE.NormDefaults.Wire.premisesX L.U (defaultX L.D L.X) Γ
def excN (r : String) : String := "default:exception:" ++ r
def rankL : String := "default:ranking:helpfulness:safety:x_permitted"
def outw : String := "soft__outweighs__helpfulness__safety__x_permitted"

/-! ## DF-α, DF-α′: one default rule, no condition -/

#guard holds dα fun L => dfltLabels L.D == [excN "r1"] &&
  dfltPremises L.D == [.all "assistant" (.implies (.unary exc1 (.var 0)) .bottom)] &&
  defaultX L.D L.X == L.X ++ dfltPremises L.D && withoutDefaults L.D L.X == L.X ++ [.top]
-- strict: does not follow, and the strict countermodel {excepted r1} checks on the wire; the default model {} checks
#guard holds dα fun L => !follows1 L L.X [] xAll && wireOk L L.X [] xAll [exc1] && wireOk L (defaultX L.D L.X) [] .bottom []
#guard holds dα fun L => assume1 L [] xAll == [excN "r1"] &&
  basisOf (assume1 L [] xAll) (wireOk L L.X [] xAll [exc1]) == .needs && followsForm L.D (assume1 L [] xAll) == .short
-- DF-α′: no strict model, or the strict model {}, which does not check (the conclusion holds there): never `needs`
#guard holds dα fun L => !wireOk L L.X [] xAll [] && basisOf (assume1 L [] xAll) (wireOk L L.X [] xAll []) == .unsettled &&
  basisOf (assume1 L [] xAll) false == .unsettled
-- `assumptionsOf` on two certificates: one uses the `Dflt_T` premise (∀a. ¬excepted), one does not (∀a. e → e)
#guard holds dα fun L => (ps L []).length == 5 && certChecks L.U (ps L []) notExc cNeeds &&
  assumptionsOf L.U L.D L.X [] notExc cNeeds == [excN "r1"] && basisOf (assumptionsOf L.U L.D L.X [] notExc cNeeds) false == .unsettled
#guard holds dα fun L => certChecks L.U (ps L []) excSelf cStrict &&
  assumptionsOf L.U L.D L.X [] excSelf cStrict == [] && basisOf (assumptionsOf L.U L.D L.X [] excSelf cStrict) false == .strict
-- with `Dflt_T` read as `⊤` the first certificate fails, so its label is kept
#guard holds dα fun L => !certChecks L.U (VE.NormDefaults.Wire.premisesX L.U (withoutDefaults L.D L.X) []) notExc cNeeds

/-! ## DF-β: a stated sufficient condition -/

def βii : VE.Formula := .all "assistant" (.implies (.not (.unary "urgent" (.var 0))) (.unary "x_required" (.var 0)))

-- `Dflt_T`'s premise is false on {excepted} and true on {urgent, excepted}
#guard holds dβ fun L => dfltLabels L.D == [excN "r1"] && bareExceptionLabels L.D == [] &&
  (dfltPremises L.D).map (fun φ => (φ.eval (sitOf L [exc1]) [], φ.eval (sitOf L ["urgent", exc1]) [])) == [(false, true)]
-- `Exc_T` and `Dflt_T` together: the exception holds exactly where the condition does
#guard holds dβ fun L => (check1 L L.X [] .top ["urgent"] []).isNone &&
  (check1 L (defaultX L.D L.X) [] .top [exc1] []).isNone && (check1 L (defaultX L.D L.X) [] .top ["urgent", exc1] []).isSome
-- (i) does not follow: the default countermodel {urgent, excepted} (the exception is forced) checks on the wire
#guard holds dβ fun L => !follows1 L (defaultX L.D L.X) [] xAll && wireOk L (defaultX L.D L.X) [] xAll ["urgent", exc1]
-- (ii) follows, basis needs (strict countermodel {excepted}), form long (the assumption has a stated condition)
#guard holds dβ fun L => follows1 L (defaultX L.D L.X) [] βii && assume1 L [] βii == [excN "r1"] &&
  basisOf (assume1 L [] βii) (wireOk L L.X [] βii [exc1]) == .needs && followsForm L.D (assume1 L [] βii) == .long

/-! ## DF-γ: unranked colliding defaults -/

-- no one-assistant situation admits `defaultX`, while some admit `X` (the gate's case, df-1ab)
#guard holds dγ fun L => (collidingPairs L.D).map (fun (P, Q) => (P.name, Q.name)) == [("r1", "r2")] &&
  dfltLabels L.D == [excN "r1", excN "r2"] && !model1 L (defaultX L.D L.X) [] && model1 L L.X []

/-! ## DF-δ, DF-δ′: a ranked pair, holistic and strict -/

#guard holds dδ fun L => dfltLabels L.D == [excN "r1", excN "r2", rankL] && bareExceptionLabels L.D == [excN "r1", excN "r2"] &&
  assume1 L [] xAll == [excN "r1", rankL] && followsForm L.D (assume1 L [] xAll) == .long &&
  basisOf (assume1 L [] xAll) (wireOk L L.X [] xAll [outw]) == .needs
#guard holds dδs fun L => dfltLabels L.D == [excN "r1", excN "r2"] && assume1 L [] xAll == [excN "r1"] &&
  followsForm L.D (assume1 L [] xAll) == .short

/-! ## DF-ε: a switch -/

#guard holds dε fun L => dfltLabels L.D == [excN "r1", "default:switch:r1:user"] &&
  dfltPremises L.D == [.all "assistant" (.implies (.unary exc1 (.var 0)) .bottom),
    .all "assistant" (.not (.unary "soft__off__r1__user" (.var 0)))] &&
  assume1 L [] xAll == [excN "r1", "default:switch:r1:user"] && followsForm L.D (assume1 L [] xAll) == .long &&
  basisOf (assume1 L [] xAll) (wireOk L L.X [] xAll ["soft__off__r1__user"]) == .needs

/-! ## DF-ζ, DF-ζ0: strict -/

#guard holds dζ fun L => follows1 L L.X [] xAll && dfltLabels L.D == [excN "r1"] && assume1 L [] xAll == [] &&
  basisOf (assume1 L [] xAll) false == .strict
#guard holds dζ0 fun L => dfltLabelled L.D == [] && assume1 L [] xAll == [] && basisOf [] true == .strict

/-! ## DF-ι: premises no situation satisfies; DF-κ: the default kind binds one premise more -/

#guard holds dβ fun L =>
  let Γ := [.ex "assistant" (.unary "urgent" (.var 0)), .all "assistant" (.not (.unary "urgent" (.var 0)))]
  follows1 L (defaultX L.D L.X) Γ xAll && !model1 L (defaultX L.D L.X) Γ
#guard holds dα fun L => (ps L []).length == (VE.NormDefaults.Wire.premisesX L.U L.X []).length + 1

/-! ## DF-σ: `basis_needs_sound` needs `xModelOk` (local conflict freedom), not `modelCheckX` alone -/

#guard holds dσ fun L =>
  VE.NormDefaults.modelCheckX L.U L.X (sitOf L []) (fillOf L []) [] (.all "assistant" .bottom) == (true, false) &&
  !wireOk L L.X [] (.all "assistant" .bottom) [] && follows1 L L.X [] (.all "assistant" .bottom)

end VE.Defaults.Fixtures
