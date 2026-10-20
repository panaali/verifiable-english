"""Repairs of the 2026-10-09T0600Z audit (AUDIT.md of run-20261009T0600Z: 14/20 faithful; u022b u022c u029 u037 u096 u112 rejected)
and of the lead's rule of 2026-10-09 (NO DUTY READINGS FOR RIGHTS, EITHER WAY).

* "Everyone has the right to X" (and "freedom of X", "the right freely to X") is ONE reading, the entitlement: who holds the right,
  nothing more. The negative-claim readings (`claim_negative`, `claim`, `claim_avoid`: "must be spared / left free ...") turn the right into
  a duty and are gone from u022a u022b u022c u029 u048 u049 u051 u063 u066 u070 u073 u084a u084b u087 u096 u105a u105b u105c.
  The liberty readings ("may X") of the same units are gone too: the words give the right, and a second reading of "right to X" as a
  permission comes from outside the text (the lead asked for ONE reading). Correlative duties come from the rights layer.
* u112: `exercise_unprotected` only removed protection, which weakens "may in no case be exercised" (a prohibition): gone; the
  prohibition `exercise_prohibited` is the one reading. The predicates `right_protects_exercise`, `exercise_of_declared_right`, `exercise_contrary_to_un` and the sort `exercise`
  that only that formula used are gone from the shared vocabulary (the prohibition's companion declares its own).
* u037: the regulated act was renamed "be ordered" only to make the act phrases distinct; prohibiting orders is not prohibiting arrest,
  detention or exile carried out without an order. The act is again "take place" (the other acts that were "take place" keep
  distinct, equally faithful verbs).
"""
REMOVE = {
    "u022a": ["claim_negative"], "u022b": ["claim_negative"], "u022c": ["claim_negative"], "u029": ["claim"],
    "u048": ["claim_negative", "liberty"], "u049": ["claim", "liberty"], "u051": ["liberty", "claim_avoid"],
    "u063": ["claim_negative", "liberty"], "u066": ["claim_negative", "liberty"], "u070": ["claim_negative", "liberty"],
    "u073": ["claim_negative", "liberty"], "u084a": ["claim_negative", "liberty"], "u084b": ["claim_negative", "liberty"],
    "u087": ["claim_negative", "liberty"], "u096": ["claim_negative"],
    "u105a": ["claim_negative", "liberty"], "u105b": ["claim_negative", "liberty"], "u105c": ["claim_negative", "liberty"],
    "u112": ["exercise_unprotected"],
}
REASON = {
    "u112": "the formula only removed protection from the exercise; it does not prohibit the exercise, so it weakened 'may in no case be "
            "exercised' (a prohibition)",
}
RIGHT_REASON = ("the right is expressed once, as the entitlement (who holds it, nothing more); a separate reading that turns it into a "
                "duty ('must be spared / left free ...') or into a permission ('may ...') is not in the words: correlative duties come "
                "from the rights layer, not from extra readings")
DROP_PREDICATES = ["right_protects_exercise", "exercise_of_declared_right", "exercise_contrary_to_un"]
DROP_SORTS = ["exercise"]
AUDIT_REJECTED = ["u022b", "u022c", "u029", "u037", "u096", "u112"]
