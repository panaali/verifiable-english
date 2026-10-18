import VE.Alternatives.FillWire

/-! Build-time checks of `decodeAltSourceU` (docs/spec/events-time-causation.md 8, T12c and T12d): each
branch and each failure with its own text (`#guard`: the build fails if one is false). The document is T12's
(nd fixture u10): chooser `agent`, actions `act`, `permitted` the permission member of the `required` pair. -/
namespace VE.Alternatives.FillExamples
open Lean

/-- T12's environment with the given profile list, `permitted`'s default and extra predicate entries. -/
def env (profiles : String) (default : String := "unspecified") (permitted : String := "permitted")
    (extra : String := "") : Json :=
  (Json.parse (r#"{"language": "ve.core@0.2", "spec_revision": "ve-v0.2-expand2-2026-09-25", "profiles": "# ++
    profiles ++ r#", "vocabulary": {"sorts": {"agent": {"description": "agent"}, "act": {"description": "act"},
    "harm": {"description": "harm"}}, "constants": {}, "predicates": {"# ++ extra ++
    r#""available": {"arguments": ["act", "agent"], "description": "available", "verbalisation": "{0} is available to {1}"},
    "leads_to": {"arguments": ["act", "harm"], "description": "leads to", "verbalisation": "{0} leads to {1}"},
    ""# ++ permitted ++ r#"": {"arguments": ["act"], "description": "permission", "regulated":
      {"role": "permission", "default": ""# ++ default ++ r#"", "act": "{0} be performed"}},
    "required": {"arguments": ["act"], "description": "obligation", "regulated":
      {"role": "obligation", "default": "deny", "act": "{0} be performed", "permission": ""# ++ permitted ++ r#""}}}},
    "alternatives": {"chooser": "agent", "action": "act", "harm": "harm", "available": "available",
      "leads_to": "leads_to", "outcomes": "signed",
      "performed": {"permission": ""# ++ permitted ++ r#"", "obligation": "required"}}}"#)).toOption.getD .null

def errorOf (environment : Json) (premises : Json := .null) : String :=
  match decodeAltSourceU environment (.arr #[]) premises with
  | .ok s => s!"ok {s.unspec}"
  | .error e => e

def ndProfiles : String := r#"["alternatives@0", "norm-defaults@0", "norms@0", "relational-fol@0"]"#

-- T12d: with the profile, the decoder reads `permitted` as unspecified.
#guard errorOf (env ndProfiles) == "ok [permitted]"
-- Without the profile and without `unspecified`: today's decoder (the two decoders agree, T12d's first case).
#guard errorOf (env "[]" "allow") == "UnsupportedProfile: alternatives@0 is required"
#guard (match Wire.decodeAltSource (env "[]" "allow") (.arr #[]) .null with
  | .error e => e | .ok _ => "ok") == "UnsupportedProfile: alternatives@0 is required"
#guard errorOf (env r#"["alternatives@0", "norms@0", "relational-fol@0"]"# "allow") == "ok []"
-- `unspecified` without the profile.
#guard errorOf (env r#"["alternatives@0", "norms@0", "relational-fol@0"]"#) ==
  "UnsupportedProfile: unspecified completion requires norm-defaults@0"
-- With the profile: listed twice, an unknown profile, a reserved name, a 57-byte name. (`WellFormedU` after
-- `checkAuthor` and today's decoder has no failing input left: they check each of its conditions.)
#guard errorOf (env r#"["alternatives@0", "norm-defaults@0", "norm-defaults@0", "norms@0", "relational-fol@0"]"#) ==
  "UnsupportedProfile: profiles must be sorted and unique"
#guard errorOf (env r#"["alternatives@0", "norm-defaults@0", "norms@0", "relational-fol@0", "zzz@0"]"#) ==
  "UnsupportedProfile: Unsupported profile zzz@0"
#guard errorOf (env ndProfiles (extra := r#""unsaid__x": {"arguments": ["act"], "description": "x"},"#)) ==
  "InvalidInput: reserved name unsaid__x"
#guard errorOf (env ndProfiles (permitted := String.mk (List.replicate 57 'p'))) ==
  "ResourceLimit: unspecified name length"
-- T12c: a premise naming an unsaid predicate is not typed over the base vocabulary, so no such Γ decodes.
#guard errorOf (env ndProfiles) (Json.arr #[Json.mkObj [("label", "g"),
  ("ast", Json.arr #["forall", "act", Json.arr #["unary", "unsaid__permitted", Json.arr #["var", (0 : Nat)]]])]]) ==
  "InvalidInput: ill-typed premise g"

end VE.Alternatives.FillExamples
