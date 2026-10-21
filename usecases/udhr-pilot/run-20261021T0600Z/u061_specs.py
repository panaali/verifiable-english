"""u061 in run 20261021T0600Z: the entitlement of the family (the institution, as in u060), once, as a companion document.

The 20261020T1800Z audit rejected "every family": the source keeps the subject of u060, "the family", which u060's vocabulary names as the
institution (`the_family`, sort `thing`).  The companion therefore ranges over things and picks out the family with a base predicate; a thing that
is not the family is outside the rule (UNDECIDED, never denied, never allowed).
"""
import repair_specs as RS
import udhr_specs as U

U.VERB["is_the_family"] = "{0} is the family"
CASE = U.case_sort("thing", "things", "a thing the text names: an understanding, an aim or an institution",
                   {"is_the_family": "The thing is the family, the institution Article 16 names"}, ("p", "is_the_family"),
                   [["is_the_family"], []])
SPEC = RS.entitlement("u061", "entitlement", "is_entitled_to_protection_by_society_and_the_state",
                      "{0} is entitled to protection by society and the State",
                      "The thing is entitled to protection by society and the State (the family, as in the previous clause)",
                      ["protection_of_the_family"], case=CASE)
