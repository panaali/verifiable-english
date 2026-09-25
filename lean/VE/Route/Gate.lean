import VE.Order.WireGate
import VE.Route.Route

/-! The `ve.core@0.2` envelope and its profile gate (PLAN-EXPAND2 3.3, 3.4).
An envelope declares a sorted, duplicate-free `profiles` list drawn from the
profile registry, always including `relational-fol@0`. Its checker profiles
select exactly one of four allowed checker families: FOL (no checker profile),
closure (`closure@0`), closure+n-ary (`closure@0` and `nary@0`; its checker is
gated until W4 lands) and order (`order@0` alone). Any other list is rejected
with an `UnsupportedProfile` diagnostic naming the profile or the pair, before
any checking. The registry and the diagnostics mirror Python `ve/profiles.py`.

The existing entry points (evaluation, `check-certificate`, `order`) never
accept a `ve.core@0.2` envelope (`legacy_routes_reject_v02`), so every existing
gate theorem is unchanged and still exact. -/
namespace VE.Route.Gate
open Lean

def language : String := "ve.core@0.2"
def specRevision : String := "ve-v0.2-expand2-2026-09-25"
def base : String := "relational-fol@0"

/-- The four allowed checker families. -/
inductive Family where
  | fol
  | closure
  | closureNary
  | order
  deriving DecidableEq, Repr

def Family.name : Family → String
  | .fol => "fol"
  | .closure => "closure"
  | .closureNary => "closure+n-ary"
  | .order => "order"

/-- One profile: its statement-layer generator (empty for checker profiles),
its layer and, for checker profiles, the checker it selects. -/
structure ProfileRecord where
  name : String
  generator : String
  layer : String
  deriving DecidableEq, Repr

/-- The ordered profile registry, as in `ve/profiles.py`. -/
def registry : List ProfileRecord := [
  ⟨"closure@0", "", "checker"⟩,
  ⟨"data@0", "data", "statement"⟩,
  ⟨"definitions@0", "definitions", "statement"⟩,
  ⟨"documents@1", "documents", "statement"⟩,
  ⟨"nary@0", "", "checker"⟩,
  ⟨"norms@0", "norms", "statement"⟩,
  ⟨"order@0", "", "checker"⟩,
  ⟨base, "", "checker"⟩,
  ⟨"time@0", "time", "statement"⟩]

def known (p : String) : Bool := (registry.map ProfileRecord.name).contains p

/-- The independent specification of an allowed profile list and its family. -/
def AllowedFamily (ps : List String) (f : Family) : Prop :=
  ps.Pairwise (· < ·) ∧ (∀ p ∈ ps, known p = true) ∧ base ∈ ps ∧
    match f with
    | .fol => "closure@0" ∉ ps ∧ "nary@0" ∉ ps ∧ "order@0" ∉ ps
    | .closure => "closure@0" ∈ ps ∧ "nary@0" ∉ ps ∧ "order@0" ∉ ps
    | .closureNary => "closure@0" ∈ ps ∧ "nary@0" ∈ ps ∧ "order@0" ∉ ps
    | .order => "order@0" ∈ ps ∧ "closure@0" ∉ ps ∧ "nary@0" ∉ ps

def unsupported (message : String) : String := "UnsupportedProfile: " ++ message

/-- The executable classifier, with Python's diagnostics. -/
def classify (ps : List String) : Except String Family :=
  if !decide (ps.Pairwise (· < ·)) then .error (unsupported "profiles must be sorted and unique")
  else match ps.find? (fun p => !known p) with
  | some p => .error (unsupported s!"Unsupported profile {p}")
  | none =>
    if !ps.contains base then .error (unsupported s!"Missing profile {base}")
    else if ps.contains "order@0" && ps.contains "closure@0" then
      .error (unsupported "Unsupported profile combination closure@0 x order@0")
    else if ps.contains "order@0" && ps.contains "nary@0" then
      .error (unsupported "Unsupported profile combination nary@0 x order@0")
    else if ps.contains "nary@0" && !ps.contains "closure@0" then
      .error (unsupported "Unsupported profile nary@0 without closure@0")
    else if ps.contains "order@0" then .ok .order
    else if ps.contains "nary@0" then .ok .closureNary
    else if ps.contains "closure@0" then .ok .closure
    else .ok .fol

/-- Every family the classifier returns is allowed for exactly that list. -/
theorem classify_sound (ps : List String) (f : Family) (h : classify ps = .ok f) :
    AllowedFamily ps f := by
  unfold classify at h
  split at h
  · cases h
  · rename_i hs
    simp only [Bool.not_eq_true', decide_eq_false_iff_not, Classical.not_not] at hs
    split at h
    · cases h
    · rename_i hk
      have hknown : ∀ p ∈ ps, known p = true := by
        intro p hp
        have := List.find?_eq_none.mp hk p hp
        simpa using this
      refine ⟨hs, hknown, ?_⟩
      split at h
      · cases h
      · rename_i hb
        simp only [Bool.not_eq_true', Bool.not_eq_false, List.contains_iff_mem] at hb
        refine ⟨by simpa using hb, ?_⟩
        have e : ∀ x, ps.contains x = decide (x ∈ ps) := fun x => by simp
        simp only [e] at h
        by_cases ho : "order@0" ∈ ps <;> by_cases hc : "closure@0" ∈ ps <;>
          by_cases hn : "nary@0" ∈ ps <;> simp [ho, hc, hn] at h <;> subst h <;> simp [ho, hc, hn]

/-- Every allowed list is accepted with its family: the four families pass. -/
theorem classify_complete (ps : List String) (f : Family) (h : AllowedFamily ps f) :
    classify ps = .ok f := by
  obtain ⟨hs, hk, hb, hf⟩ := h
  have hfind : ps.find? (fun p => !known p) = none :=
    List.find?_eq_none.mpr (fun p hp => by simp [hk p hp])
  unfold classify
  simp only [hs, decide_true, Bool.not_true, Bool.false_eq_true, if_false, hfind,
    List.contains_iff_mem, decide_true, Bool.not_true]
  cases f <;> simp_all

/-- The profiles field of an environment object, as a string list. -/
def profilesOf (env : Json) : Except String (List String) :=
  match env.getObjVal? "profiles" >>= VE.Bridge.strings with
  | .ok ps => .ok ps
  | .error _ => .error (unsupported "profiles must be a sorted unique array")

/-- A decoded envelope: its profiles, family and raw vocabulary. -/
structure Envelope where
  profiles : List String
  family : Family
  vocabulary : Json

/-- A named check, as one bind step. -/
def require (b : Bool) (message : String) : Except String Unit :=
  if b then .ok () else .error message

theorem require_ok {b : Bool} {message : String} {u : Unit} (h : require b message = .ok u) :
    b = true := by
  unfold require at h
  split at h
  · assumption
  · cases h

/-- The envelope decoder. It checks the field set, the language, the profiles
and the specification revision, in Python's order, before anything else. -/
def decodeEnvelope (env : Json) : Except String Envelope := do
  VE.Bridge.exactFields env ["language", "profiles", "spec_revision", "vocabulary"]
  let l ← VE.Bridge.stringField env "language"
  require (l == language) (unsupported "Unsupported language")
  let ps ← profilesOf env
  let family ← classify ps
  let revision ← VE.Bridge.stringField env "spec_revision"
  require (revision == specRevision) (unsupported s!"Unsupported specification revision {revision}")
  let vocabulary ← env.getObjVal? "vocabulary"
  pure ⟨ps, family, vocabulary⟩

open VE.Order.ProfileGate in
/-- A decoded envelope has language `ve.core@0.2` and an allowed profile list
of the decoded family. -/
theorem decodeEnvelope_sound (env : Json) (e : Envelope) (h : decodeEnvelope env = .ok e) :
    VE.Bridge.stringField env "language" = .ok language ∧ profilesOf env = .ok e.profiles ∧
      AllowedFamily e.profiles e.family := by
  unfold decodeEnvelope at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨l, hl, h⟩ := bind_ok h
  obtain ⟨_, hu, h⟩ := bind_ok h
  obtain ⟨ps, hps, h⟩ := bind_ok h
  obtain ⟨f, hf, h⟩ := bind_ok h
  obtain ⟨r, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨vj, _, h⟩ := bind_ok h
  cases h
  have hl' : l = language := beq_iff_eq.mp (require_ok hu)
  subst hl'
  exact ⟨hl, hps, classify_sound ps f hf⟩

open VE.Order.ProfileGate in
/-- `route_gate`, envelope form: an envelope whose profiles are not an allowed
family never decodes. -/
theorem route_gate_envelope (env : Json) (ps : List String) (hp : profilesOf env = .ok ps)
    (hn : ∀ f, ¬ AllowedFamily ps f) : ∀ e, decodeEnvelope env ≠ .ok e := by
  intro e h
  obtain ⟨_, hp', ha⟩ := decodeEnvelope_sound env e h
  rw [hp] at hp'
  cases hp'
  exact hn _ ha

/-- No existing entry point accepts a `ve.core@0.2` envelope: the evaluation
and certificate routes accept only `ve.core@0` and `ve.core@0.1` closure lists
(`VE.Order.profile_gate`) and the order route only `ve.core@0.1`. -/
theorem legacy_routes_reject_v02 (j r env : Json) (he : j.getObjVal? "environment" = .ok env)
    (hl : VE.Bridge.stringField env "language" = .ok language) :
    VE.CertificateWire.runCase j ≠ .ok r ∧ VE.Order.runEvaluationCase j ≠ .ok r ∧
      VE.Order.Surface.runCase j ≠ .ok r := by
  have hacc : ¬ VE.Order.ProfilesAccepted env := by
    rintro (⟨h, _⟩ | ⟨h, _⟩) <;> rw [hl] at h <;> exact absurd (Except.ok.inj h) (by decide)
  have hord : ¬ VE.Order.OrderProfilesAccepted env := by
    rintro ⟨h, _⟩
    rw [hl] at h
    exact absurd (Except.ok.inj h) (by decide)
  refine ⟨fun h => ?_, fun h => ?_, fun h => ?_⟩
  · obtain ⟨env', he', ha⟩ := VE.Order.profile_gate j r (Or.inl h)
    rw [he] at he'; cases he'; exact hacc ha
  · obtain ⟨env', he', ha⟩ := VE.Order.profile_gate j r (Or.inr h)
    rw [he] at he'; cases he'; exact hacc ha
  · obtain ⟨env', he', ha⟩ := VE.Order.surface_route_gate j r h
    rw [he] at he'; cases he'; exact hord ha

end VE.Route.Gate
