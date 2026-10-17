"""u0156.s03, “Claude shouldn’t actively deceive the user about the existence of a system prompt or its content.” (run 20261017T1800Z; audit 20261017T0600Z, u0156.s03 UNFAITHFUL).

The audit of run 20261017T0600Z found the set incomplete: the sentence follows “Consider a situation where Claude is asked to keep its system prompt confidential.”
(u0156.s01) and “In that case, Claude should not directly reveal the system prompt …” (u0156.s02), and it does not itself say “in that case”. The words therefore admit that the
sentence continues that situation (the rule holds there), or that it states a rule for every case. The two candidates strict and default were unconditional, so no candidate
said what the sentence says if it continues the situation.

The set now has four candidates, the force (strict or with one exception the text does not name) times the attachment (every case, or the situation of u0156.s01):

    strict, default                    the rule for every case
    strict-in-frame, default-in-frame  the rule only where Claude is asked to keep its system prompt confidential (guard: the open term below)

This module is the one owner of the names, the wording and the admission texts; repair_20261017T1800Z.py, nd.py and finish_20261017T1800Z.py read them from here.
"""
SET_ID = "force-u0156-s03"
UNIT = "u0156.s03"
FRAME_TERM = "asked_to_keep_system_prompt_confidential"   # unary on claude_instance: the guard of the in-frame candidates
EXCEPTION_TERM = "exception_to_not_deceiving_about_system_prompt"
READINGS = ["strict", "default", "strict-in-frame", "default-in-frame"]
IN_FRAME = ["strict-in-frame", "default-in-frame"]
ENGLISH = "{0} is asked to keep its system prompt confidential"
DESCRIPTION = ("Claude is asked to keep its system prompt confidential: the situation that “Consider a situation where Claude is asked to keep its system prompt confidential.” "
               "(u0156.s01) introduces. The source does not say who asks, how, or what counts as being asked; open term, decided by nobody the source names.")
FACTORS = ["who asks Claude to keep the system prompt confidential (the source does not say)", "what counts as being asked to keep it confidential"]

EVERY_CASE = (" This candidate states the rule for every case: the sentence names no condition itself. The candidates marked in-frame take the rule to hold only in the situation "
              "of u0156.s01.")
IN_FRAME_WHY = (" This candidate states the rule only for the situation in which Claude is asked to keep its system prompt confidential (the open term " + FRAME_TERM + "). "
                "The words admit it: u0156.s01 ends “Consider a situation where Claude is asked to keep its system prompt confidential.”, u0156.s02 begins “In that case”, and this "
                "sentence does not say “in that case” itself, so it may continue that situation; u0156.s05 begins another condition (“If Claude is not given any instructions about "
                "the confidentiality of some information”). The candidates not marked in-frame take the sentence as a rule for every case. No reading comes from outside the text.")


def with_frame(content):
    """The norm with the frame as its guard (the claude instance is variable 1, as in the exception atom)."""
    import copy
    out = copy.deepcopy(content)
    assert out["norm"]["guard"] == ["top"], out["norm"]["guard"]
    out["norm"]["guard"] = ["unary", FRAME_TERM, ["var", 1]]
    return out
