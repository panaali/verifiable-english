"""GitHub Copilot Extension Developer Policy (statute corpus batch 4, NON-STATUTE (c), STAND-IN): the VE translation, one pass
with today's language. CROSS-FAMILY questions (Codex writer), Opus translator.

Row statute-corpus-github-copilot-ext (dri-statute-corpus-github-copilot-ext-w-1124, Opus 5.5). Written from the pinned source
only (manage-agents reviews/spare/statute-corpus/batch4/github-copilot-ext/source.txt, sha256 39a98d0c...131f; units.jsonl
d68574fd...ea09, 38 units) and the decisions D1-D13 of that folder's ISOLATION.md, BEFORE the encoder's question file
(questions-enc.jsonl) was opened. Evidence branch: nothing here is a Lean kernel line, a profile, a refuses pair or a lint
change.

WHAT IS CARRIED, AND HOW. The policy's duties and prohibitions are carried as yes/no CLASSIFICATIONS of the items a case
names (ve-quantity@1 formulas over one sort, item), not as norms@0 rules (ve-units@1 refuses norms@0, ../PAGE.md): an act
of the developer or its Extension is FORBIDDEN when one of the in-scope bans or duty failures classifies it; a duty item is
REQUIRED when one of the in-scope duty clauses covers it. Dates are Lean dates (time@0): the thirty days of unit 18 and the
termination days of unit 37 are compared in Lean, never in Python.

READINGS fixed here, before the questions were read (refuse when in doubt: where two readings give two answers no rule
fires and the question is OPEN):
R1  CLOSURE OVER THE DEVELOPER'S ACTS. The policy is a list of restrictions on an activity the Agreement allows ("we want
    You to develop useful ... Extensions", unit 2). An act of the developer or its Extension that no in-scope ban or duty
    failure classifies is NOT forbidden ("may": yes). An act that "should not" (unit 23: an unsafe environment or hardship),
    an act that would end the Agreement in a way the text does not name, and an act that exercises a right GitHub granted
    after termination where the granting section survives (R10) are neither forbidden nor allowed (OPEN).
R2  CLOSURE OVER DUTIES. A duty item no in-scope duty clause covers is not required ("must": no). GitHub's acts are not
    closed: GitHub may do what units 1 and 37 let it do; anything else about GitHub is OPEN (the text does not bind GitHub).
R3  PERSONAL DATA (unit 1, D3): data is Personal Data if it is content made available by Users via the Platform (code,
    text, data uploaded, posted, User inputs, Extension outputs), or if it is information relating to an individual User,
    customer or employee that could identify them; the second is a fact the encoder states only where the case settles it.
R4  CONTACT (unit 13, D7). Reading A: every contact with a User is limited to emergencies (safety and security at risk)
    and to contact in compliance with the law, and contact outside GitHub also needs a clear and separate permission.
    Reading B: the bullet bans using Personal Data to contact Users, and the two sentences after it open contact outside
    GitHub (permission, emergency, lawful); contact inside GitHub is banned exactly when it uses Personal Data. Outside
    GitHub both readings agree. Inside GitHub: forbidden when it uses Personal Data and is not (an emergency and lawful);
    allowed when it does not use Personal Data and is an emergency and lawful; otherwise OPEN.
R5  AGGREGATED AND ANONYMIZED (unit 22, D7). The "You may, however" permission lifts unit 22's ban; whether it also lifts
    the other Personal Data bans (units 12-21) is two readings: an act inside the permission that another unit 12-21 ban
    classifies is OPEN; one that only a ban outside units 12-22 classifies is forbidden.
R6  COPIES (unit 19). Merging Personal Data with data from other sources for unrelated purposes is banned. Creating copies
    of Personal Data (or building a database) for unrelated purposes without merging: "including" makes it an example of
    the ban (banned) or an example of merging (not banned without merging): OPEN.
R7  THIRTY DAYS (unit 18, D5): the latest day is the event's day + 30 (the brief's fixed convention, written as shift_days
    30 in Lean); met = all the associated Personal Data deleted on or before that day. A User's request for deletion with
    none of the three events: no period (latest day OPEN, "met" OPEN); ignoring the request is banned, and deleting on
    request is required (the only course that is not "ignoring" it that the text names).
R8  IN FORCE (unit 37, D10): the Agreement ends on the day the developer discontinues use of the Platform, the day GitHub
    terminates it, or the day of an act that breaches an in-scope term (a done act this translation classifies forbidden)
    or a stated breach of another term. On a later day it is not in force; on an earlier day (with no earlier end) it is;
    ON the end day itself the text gives no time of day: OPEN. A missed unit 18 period also ends it (R13).
R9  SURVIVAL (unit 38, D9): a duty of section 2 (units 2-35) or section 3 (unit 36) survives; one of section 6 (units 37,
    38) does not; out-of-scope sections by the list (1, 4 second and last paragraphs, 5, 7-19 survive; 4's other paragraphs
    do not), the duty's section a stated fact. Still bound on a day = required and (in force that day or surviving).
    Unit 38's own duties (return or destroy Pre-release Materials, certify) arise on termination: survival does not cut
    them (counted with the surviving duties).
    GUARDS (encode.py C2): a stated judgment is read only on the acts its plain guard names (configures_systems,
    tells_users, privacy_policy_act, monitors, targets_trait, requests_permissions); outside outcomes (ToS, applicable
    laws, legality, a breach of an out-of-scope term) are plain facts: the brief makes the writer state them where a
    question turns on them.
R10 RIGHTS AFTER TERMINATION (unit 38): "all of the rights and licenses we granted you ... cease" against "the rights ... in
    Sections 1, ... 5 ... survive": an act exercising a right granted in a surviving section after termination is OPEN; one
    granted elsewhere is forbidden. Pre-release Materials: on termination the developer must return them unless GitHub asks
    for destruction ("return (or, at our request, destroy)": then destroy, not return), and must certify in writing on
    termination whether or not it held any ("you will certify in writing that you've complied with these requirements";
    fidelity fix 2026-11-26, FL07 and FL08). Asked on the termination day itself (terminated_on_qday), these duties are
    OPEN: the text gives no time of day (R8; the fix's fidelity step flag FL05).
R11 GITHUB (units 1, 37): GitHub may terminate for any reason and without notice (so it need not give notice), and may take
    an action against an Extension if the Extension violates the Agreement (a forbidden done act it is linked to, or a stated
    violation of its spirit) and GitHub deems the action necessary (stated).
R12 FEEDBACK (unit 33): the mechanism must reach both the developer and GitHub ("to You and GitHub").
R13 A MISSED UNIT 18 PERIOD (units 18, 37; fidelity fix 2026-11-26, FL04): "you must delete all associated Personal Data
    within thirty days" is a term of the Agreement, so a deletion item whose data was all deleted on a stated day after
    the last day of its period (R7) is a breach that ends it ("will terminate immediately ... if you breach any term").
    The breach is complete when the last day ends: the Agreement is not in force on any later day and, for this item, is
    in force up to and on the last day. Where the case does not state that all the data was deleted and on which day,
    the breach is unknown (all_deleted is closed by C1, so its absence does not say the data was kept): the Agreement
    after the last day is OPEN. A request with none of the three events has no period (R7) and no such breach (ignoring
    it is unit 18's ban, a forbidden act under R8).
"""
from __future__ import annotations

import hashlib
import json

DAY = "day"
THIRTY = 30

KINDS = {
    "act": {"day": (DAY, "the day the act is done")},
    "gh": {"day": (DAY, "the day GitHub does the act")},
    "duty": {"qday": (DAY, "the day the question asks about")},
    "del": {"ev": (DAY, "the day of the event that starts the thirty days"),
            "dd": (DAY, "the day the last of the associated Personal Data was deleted"),
            "last": (DAY, "the latest day for deleting all associated Personal Data (event day + 30)"),
            "qday": (DAY, "the day the question asks about")},
    "q": {"qday": (DAY, "the day the question asks about")},
}
STATED_BASES = ("day", "qday", "ev", "dd")
STEP_BASES = ("last",)

# --- facts on a developer / Extension act ("act" items). PLAIN facts: the encoder's closed world (C1: what the case does
# not say the act is or does, it is not / does not). STATED facts: judgments and outside outcomes, never closed (unknown
# unless the case states them). ---------------------------------------------------------------------------------------
ACT_PLAIN = {
    "done": "the act was done (on the act's day)",
    # data the act concerns (R3)
    "d_content": "the data is content made available by Users via the Platform (code, text, data uploaded, posted, User "
                 "inputs, Extension outputs)",
    "collects": "the act collects the data", "stores": "the act stores the data", "uses": "the act uses the data",
    "encrypted": "the stored data is encrypted",
    # unit 2
    "relies_copilot": "the act relies on GitHub Copilot for a task",
    # units 5-10
    "degrades_security": "the act degrades or compromises security",
    "bypasses_controls": "the act bypasses or circumvents protocols or access controls",
    "calls_api": "the act uses an API", "api_published": "GitHub has published the API",
    "transmits_code": "the act transmits code (a virus or other code)",
    "reverse_engineers": "the act attempts to reverse engineer or otherwise derive source code, trade secrets or know-how of "
                         "the Platform or a portion of it",
    # units 12-22
    "contacts": "the act contacts a User", "outside_github": "the contact is outside GitHub",
    "contact_uses_pd": "the contact uses Personal Data (e.g. the User's email address)",
    "requests_sensitive": "the act requests Users to provide sensitive, private or confidential information (e.g. credit "
                          "card numbers or passwords)",
    "shares_third": "the act rents, sells or shares the data with a third party",
    "encourages_circumvent": "the Extension encourages Users to circumvent or interfere with their own workplace and "
                             "employer data, privacy and security policies",
    "creates_profiles": "the act uses the data to create User profiles",
    "ignores_request": "the act ignores a User's request for deletion",
    "merges": "the act merges the data with data gathered from other sources",
    "copies": "the act builds a database of, or otherwise creates copies of, the data",
    "assists_obtain": "the act allows or assists an entity to obtain Personal Data using the developer's access to the "
                      "Platform",
    "exploits_other": "the act otherwise exploits the data (other than collecting, storing, using, contacting, requesting, "
                      "sharing, profiling, merging, copying or surveillance)",
    "analytics_dev": "the use is for analytics and development related to the Extension",
    # units 24-30
    "infers_emotion": "the act infers people's emotional states from physical, physiological or behavioral characteristics",
    "infers_sensitive": "the act infers a sensitive attribute of a person (e.g. gender, race, nationality, religion, "
                        "specific age)",
    "categorizes_biometric": "the act categorizes people based on their biometric data",
    "categorizes_infer": "the act categorizes people to infer characteristics or affiliations such as race, political "
                         "opinions, trade union membership, religious or philosophical beliefs, sex life or sexual orientation",
    "scores_profiles": "the act is social scoring or predictive profiling of persons or groups",
    "rt_facial": "the act is real-time facial recognition technology on mobile cameras",
    "law_enforcement": "the technology is used by law enforcement",
    "in_wild": "it attempts to identify individuals in uncontrolled, 'in the wild' environments",
    "rt_identification": "the act is real-time or near real-time identification of an individual",
    "persistent_tracking": "the act is persistent tracking of an individual",
    "uses_personal_info": "the act uses the individual's personal information (including biometric data)",
    # duty failures (units 20, 31-36)
    "no_privacy_policy": "the Extension provides Users no privacy policy",
    "pp_not_public": "the Extension's privacy policy is not publicly available",
    "pp_incomplete": "the privacy policy does not explain how the Extension collects, uses, processes and stores Personal "
                     "Data and what control Users have over it",
    "hides_ai": "the act shows Users generative AI content without informing them that it is",
    "no_use_info": "the developer does not inform Users of the Extension's intended use cases, best practices and "
                   "limitations",
    "untested": "the Extension is not tested to ensure its outputs do not violate the Agreement",
    "feedback_no_dev": "the Extension offers Users no mechanism to report feedback to the developer",
    "feedback_no_github": "the Extension offers Users no mechanism to report feedback to GitHub",
    "no_capability_info": "the developer does not inform Users of the Extension's capabilities",
    "perm_need_undefined": "the Extension's description does not clearly define the need for the permissions it requests",
    "promotes_illegal": "materials used with or in the Extension promote illegal activities",
    "unlicensed_third_party": "the developer uses, includes, integrates or distributes third-party software without a "
                              "right or licence necessary to do so",
    "lower_support": "the developer gives end user customers lower technical support when the Extension operates with the "
                     "Platform than when it operates on its own",
    # unit 23 'should not'; unit 37; unit 38
    "violates_tos": "the Extension does not comply with the GitHub Terms of Service including the Acceptable Use Policy "
                    "(stated outcome)",
    "violates_law": "the Extension does not comply with all applicable laws and legal requirements where it is made "
                    "available (stated outcome)",
    "materials_illegal": "materials used with or in the Extension are not legal in a jurisdiction where it is used (stated)",
    "oos_breach": "the act breaches a term of the Agreement outside the in-scope text (stated outcome)",
    # guards: the acts a stated judgment concerns (C2: the judgment is read only where its guard holds)
    "configures_systems": "the act is how the developer configures its systems to protect Personal Data",
    "tells_users": "the act concerns what Users are told or shown about the Extension's functionality, performance, origin "
                   "or Personal Data use",
    "privacy_policy_act": "the act is how the Extension provides its privacy policy",
    "monitors": "the act monitors or watches individuals, or lets an entity do so",
    "targets_trait": "the act targets a person's characteristic such as age, disability or socio-economic situation",
    "requests_permissions": "the act is the Extension's request for permissions",
    "unsafe_hardship": "the act creates an unsafe environment or hardship for Users",
    "discontinues_platform": "the act is the developer discontinuing use of the Platform",
    "other_termination": "the act is meant to end the Agreement in another way (not discontinuing use of the Platform)",
    "exercises_grant": "the act exercises a right or licence GitHub granted the developer in the Agreement",
    "grant_surviving": "that right or licence is granted in a section the survival list names (1, 2, 3, 4 second or last "
                       "paragraph, 5, 7-19)",
    "after_termination": "the act is done after the Agreement terminated (the case states the termination and the day)",
}
ACT_STATED = {
    "d_identifying": "the data relates to an individual User, customer or employee and could, alone or with other "
                     "information, identify them (R3; stated where the case settles it)",
    "proper_consent": "proper User consent was obtained for the act (stated judgment)",
    "significant_harm": "the use of Copilot for the task could lead to significant harm (stated judgment)",
    "improper_config": "the developer's systems are not properly configured to protect Personal Data (stated judgment)",
    "misleads": "the act misleads or deceives Users about functionality, performance, origin or Personal Data use (stated)",
    "may_damage": "the transmitted code may damage, detrimentally interfere with, surreptitiously intercept or expropriate a "
                  "system or Personal Data (stated)",
    "sep_permission": "the developer gained permission through a clear and separate permissions process (stated)",
    "emergency": "the contact is in an emergency in which the User's safety and security is at risk (stated)",
    "lawful_contact": "the contact is in compliance with the law (stated)",
    "spec_necessary": "the information is specifically necessary for the legitimate purpose of the Extension (stated)",
    "beyond_necessary": "the profiles go beyond what is necessary for the Extension to function (stated)",
    "unrelated_purpose": "the purpose is unrelated to the use of the Extension (stated)",
    "pp_not_accessible": "the privacy policy is not easily accessible (stated)",
    "surveillance": "the act is (accessing data for) surveillance or allows or assists an entity to conduct surveillance "
                    "(stated)",
    "ongoing_surveillance": "the act is ongoing surveillance of the individual (stated)",
    "gh_approved": "GitHub has approved this use (stated)",
    "disclosed_permitted": "the use is disclosed to and permitted by Users (stated)",
    "aggregated_anonymized": "the data is both aggregated and anonymized (stated)",
    "harmful_treatment": "the scoring or profiling would lead to discriminatory, unfair, biased, detrimental, unfavorable or "
                         "harmful treatment of certain persons or groups (stated)",
    "exploits_vulnerability": "the act exploits a vulnerability of a person (stated)",
    "valid_consent": "the individual gave valid consent (stated)",
    "permissions_unnecessary": "the Extension requests permissions that are not appropriate and necessary (stated)",
}
# --- GitHub's acts ("gh" items) ---
GH_PLAIN = {"done": "GitHub did the act (on its day)",
            "gh_terminates": "the act is GitHub terminating the Agreement",
            "gh_action": "the act is an action GitHub takes against the Extension to protect Users (e.g. removing it)",
            "with_notice_only": "the act is GitHub terminating only after giving notice (the question asks whether "
                                "notice is needed)"}
GH_STATED = {"deems_necessary": "GitHub deems the action necessary (stated)",
             "spirit_violation": "the Extension violates the spirit (or the letter, outside the in-scope text) of the "
                                 "Agreement (stated)"}
# --- duty items ("duty"): what the question asks the developer to do (the duty's content), closed (C1) ---
DUTY_PLAIN = {
    "k_understand": "understand the use cases and limitations of GitHub Copilot (unit 2)",
    "k_no_harm_reliance": "not rely on GitHub Copilot for tasks where its use could lead to significant harm (unit 2)",
    "k_comply_policy": "comply with this Policy (unit 2)",
    "k_comply_tos": "make the Extension comply with the GitHub Terms of Service including the Acceptable Use Policy (unit 3)",
    "k_configure": "properly configure its systems to protect Personal Data (unit 4)",
    "k_encrypt": "ensure stored data is encrypted (unit 4)",
    "stored": "the data is stored", "d_content": ACT_PLAIN["d_content"],
    "k_contact_permission": "gain permission through a clear and separate permissions process before contacting a User "
                            "outside GitHub (unit 13)",
    "contact_outside": "the developer contacts or would contact a User outside GitHub",
    "k_delete_event": "delete all associated Personal Data after a User deleted the Extension, the developer discontinued it "
                      "or it was removed (unit 18)",
    "event_happened": "one of those three events happened",
    "k_delete_request": "delete a User's data on the User's request for deletion (unit 18, R7)",
    "user_requested": "the User requested deletion",
    "k_privacy_policy": "provide Users an easily accessible and publicly-available privacy policy (unit 20)",
    "k_comply_law": "make the Extension comply with all applicable laws and legal requirements (unit 23)",
    "k_inform_use": "inform Users of the Extension's intended use cases, best practices and limitations (unit 31)",
    "k_inform_ai": "inform Users when they are interacting with generative AI content (unit 31)",
    "k_test": "test the Extension to ensure outputs do not violate the Agreement (unit 32)",
    "k_feedback": "provide a mechanism for Users to report feedback to the developer and GitHub (unit 33)",
    "k_inform_capabilities": "inform Users of the Extension's capabilities (unit 34)",
    "k_request_needed": "request only the appropriate and necessary permissions (unit 35)",
    "k_define_need": "clearly define the need for permissions within the Extension's description (unit 35)",
    "k_responsible": "develop, operate and maintain all aspects of the Extension (unit 36)",
    "k_legal_materials": "ensure materials used with or in the Extension are legal where it is used and do not promote "
                         "illegal activities (unit 36)",
    "k_licences": "obtain rights or licences necessary to use or distribute third-party software used with the Extension "
                  "(unit 36)",
    "uses_third_party": "the Extension uses, includes, integrates or distributes third-party software",
    "k_support": "provide end user customers the same high-quality technical support with the Platform as on its own (unit 36)",
    "k_return_prerelease": "return GitHub's Pre-release Materials and copies (unit 38)",
    "k_destroy_prerelease": "destroy GitHub's Pre-release Materials and copies (unit 38)",
    "k_certify": "certify in writing compliance with the return or destruction (unit 38)",
    "has_prerelease": "the developer has Pre-release Materials or copies in its possession or control",
    "gh_asked_destroy": "GitHub asked for destruction",
    "terminated_before": "the Agreement terminated before the question's day (the case states the end and its day)",
    "terminated_on_qday": "the Agreement terminated on the question's day itself (the case states the end and its day)",
    "k_gh_notice": "GitHub gives notice before terminating the Agreement (unit 37)",
    "k_other": "a duty no in-scope clause names (a duty the question asks about that the in-scope text does not state)",
    "oos_duty": "a duty of an out-of-scope section that the case states (cross-reference)",
    "sec1": "the duty is in section 1", "sec4a": "the duty is in section 4, second or last paragraph",
    "sec4b": "the duty is in section 4, another paragraph", "sec5": "the duty is in section 5",
    "sec7_19": "the duty is in sections 7 to 19",
}
DUTY_STATED = {"d_identifying": ACT_STATED["d_identifying"]}
DEL_PLAIN = {"user_deleted_ext": "a User deleted the Extension", "discontinued_ext": "the developer discontinued the Extension",
             "ext_removed": "the Extension was removed", "all_deleted": "all associated Personal Data was deleted (on dd)",
             "request_only": "a User asked for deletion with none of the three events"}

DERIVED = {
    "pd": "the data is Personal Data (unit 1, R3)",
    "b2": "unit 2 classifies the act (reliance where significant harm could result)",
    "b3": "unit 3 classifies the act (the Extension does not comply with the ToS / AUP)",
    "b4": "unit 4 classifies the act (stored Personal Data not encrypted, or systems not properly configured)",
    "b5": "unit 5 bans the act", "b6": "unit 6 bans the act", "b7": "unit 7 bans the act (an unpublished API)",
    "b8": "unit 8 bans the act", "b9": "unit 9 bans the act", "b10": "unit 10 bans the act",
    "b12": "unit 12 bans the act (Personal Data without proper consent)",
    "b13": "unit 13 bans the contact", "a13": "unit 13 allows the contact",
    "b14": "unit 14 bans the request", "b15": "unit 15 bans the sharing", "b16": "unit 16 bans the Extension's design",
    "b17": "unit 17 bans the profiling", "b18": "unit 18 bans ignoring the request",
    "b19": "unit 19 bans the merging", "c19": "unit 19 copies without merging for an unrelated purpose (R6: two readings)",
    "b20": "unit 20 classifies a failure to notify Users about privacy", "b21": "unit 21 bans the act",
    "b22": "unit 22 bans the act", "perm22": "unit 22's permission covers the act (aggregated and anonymized, R5)",
    "b23": "unit 23 classifies the act (applicable laws)",
    "b24": "unit 24 bans the inference", "b25": "unit 25 bans the inference", "b26": "unit 26 bans the categorizing",
    "b27": "unit 27 bans the scoring", "b28": "unit 28 bans the act", "b29": "unit 29 bans the use",
    "b30": "unit 30 bans the use", "b31": "unit 31 classifies a failure to inform", "b32": "unit 32 classifies the failure",
    "b33": "unit 33 classifies the failure (R12)", "b34": "unit 34 classifies the failure", "b35": "unit 35 classifies the act",
    "b36": "unit 36 classifies the failure", "b38": "unit 38 classifies the act (a ceased right, R10)",
    "banx": "a ban outside units 12-22 classifies the act", "banp": "a unit 12-21 ban classifies the act",
    "doubt": "the act falls where the text gives two answers or none (R1, R4, R6, R10)",
    "forbidden": "the act is forbidden for the developer or its Extension",
    "ends": "the act ends the Agreement on its day (R8)",
    "inforce": "the Agreement is in force on the question's day (R8)",
    "violation": "the Extension violates the Agreement (R11)",
    "ghmay": "GitHub may do the act (R11)",
    "required": "the developer (or GitHub, for k_gh_notice) must do it",
    "survives": "the duty survives the termination of the Agreement (R9)",
    "bound": "the developer is still bound on the question's day by the duty (R9)",
    "trig": "one of the three events of unit 18 happened",
    "met": "all associated Personal Data was deleted within thirty days (R7)",
    "keep_ok": "keeping the associated Personal Data on the question's day does not miss the thirty days",
}


# --- formula helpers (ve-quantity@1 wire shapes) ------------------------------------------------------------------

def c(n): return ["const", n]
def U(p, x): return ["unary", p, c(x)]
def Not(f): return ["not", f]
def Implies(a, b): return ["implies", a, b]
def Iff(a, b): return ["and", ["implies", a, b], ["implies", b, a]]
def no_later(a, b): return ["date_no_later", a, b]
def before(a, b): return ["date_before", a, b]
def shift(a, b, n): return ["shift_days", a, b, str(n)]      # a is n days after b
def Eq(a, b): return ["eq", a, b]


TRUE, FALSE = ["top"], ["bottom"]


def And(*fs):
    fs = [f for f in fs if f is not None]
    if not fs:
        return TRUE
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["and", f, r]
    return r


def Or(*fs):
    fs = [f for f in fs if f is not None]
    if not fs:
        return FALSE
    r = fs[-1]
    for f in reversed(fs[:-1]):
        r = ["or", f, r]
    return r


UNIT_OF = {b: u for kind in KINDS.values() for b, (u, _) in kind.items()}


def k(base, x):
    return ["const", UNIT_OF[base], f"{base}_{x}"]


def key(formula):
    return json.dumps(formula, sort_keys=True, separators=(",", ":"))


def A(p, x):
    return key(U(p, x))


# --- the case context ---------------------------------------------------------------------------------------------

class Ctx:
    """items: [(id, kind)] with kind in KINDS; links: {(gh item, act item)}: the acts a GitHub action is about (R11)."""

    def __init__(self, items, links=()):
        self.items = list(items)
        self.links = set(links)

    def of(self, kind):
        return [x for x, kd in self.items if kd == kind]


# --- unit builders: each returns [(formula, target key or None)] -------------------------------------------------

def _iff(p, x, body):
    return (Iff(U(p, x), body), A(p, x))


def _pd(ctx):
    return [_iff("pd", x, Or(U("d_content", x), U("d_identifying", x))) for x in ctx.of("act") + ctx.of("duty")]


def _acts(fn):
    return lambda ctx: [r for x in ctx.of("act") for r in fn(x, ctx)]


def _u2(x, ctx):
    return [_iff("b2", x, And(U("relies_copilot", x), U("significant_harm", x)))]


def _u3(x, ctx):
    return [_iff("b3", x, U("violates_tos", x))]


def _u4(x, ctx):
    return [_iff("b4", x, Or(And(U("stores", x), U("pd", x), Not(U("encrypted", x))), And(U("configures_systems", x), U("improper_config", x))))]


def _u5_10(x, ctx):
    return [_iff("b5", x, U("degrades_security", x)), _iff("b6", x, U("bypasses_controls", x)),
            _iff("b7", x, And(U("calls_api", x), Not(U("api_published", x)))), _iff("b8", x, And(U("tells_users", x), U("misleads", x))),
            _iff("b9", x, And(U("transmits_code", x), U("may_damage", x))), _iff("b10", x, U("reverse_engineers", x))]


def _u12(x, ctx):
    return [_iff("b12", x, And(Or(U("collects", x), U("stores", x), U("uses", x)), U("pd", x),
                                Not(U("proper_consent", x))))]


def _u13(x, ctx):
    """R4: b13 (banned) and a13 (allowed) for a contact; neither where the readings differ."""
    c_, out_, pdu = U("contacts", x), U("outside_github", x), U("contact_uses_pd", x)
    ok = And(U("emergency", x), U("lawful_contact", x))
    return [
        (Implies(Not(c_), Not(U("b13", x))), A("b13", x)),
        (Implies(And(c_, out_, Not(U("sep_permission", x))), U("b13", x)), A("b13", x)),
        (Implies(And(c_, out_, Not(U("emergency", x))), U("b13", x)), A("b13", x)),
        (Implies(And(c_, out_, Not(U("lawful_contact", x))), U("b13", x)), A("b13", x)),
        (Implies(And(c_, out_, U("sep_permission", x), ok), Not(U("b13", x))), A("b13", x)),
        (Implies(And(c_, Not(out_), pdu, Not(U("emergency", x))), U("b13", x)), A("b13", x)),
        (Implies(And(c_, Not(out_), pdu, Not(U("lawful_contact", x))), U("b13", x)), A("b13", x)),
        (Implies(And(c_, Not(out_), Not(pdu), ok), Not(U("b13", x))), A("b13", x)),
    ]


def _u14_18(x, ctx):
    return [_iff("b14", x, And(U("requests_sensitive", x), Not(U("spec_necessary", x)))),
            _iff("b15", x, And(U("shares_third", x), U("pd", x))),
            _iff("b16", x, U("encourages_circumvent", x)),
            _iff("b17", x, And(U("creates_profiles", x), U("pd", x), U("beyond_necessary", x))),
            _iff("b18", x, U("ignores_request", x))]


def _u19(x, ctx):
    return [_iff("b19", x, And(U("merges", x), U("pd", x), U("unrelated_purpose", x))),
            _iff("c19", x, And(U("copies", x), Not(U("merges", x)), U("pd", x), U("unrelated_purpose", x)))]


def _u20(x, ctx):
    return [_iff("b20", x, Or(U("no_privacy_policy", x), U("pp_not_public", x), U("pp_incomplete", x),
                               And(U("privacy_policy_act", x), U("pp_not_accessible", x))))]


def _u21(x, ctx):
    return [_iff("b21", x, Or(And(U("monitors", x), U("surveillance", x)), U("assists_obtain", x)))]


def _u22(x, ctx):
    return [_iff("b22", x, And(U("exploits_other", x), U("pd", x), Not(U("gh_approved", x)),
                                Not(U("disclosed_permitted", x)))),
            _iff("perm22", x, And(U("uses", x), U("aggregated_anonymized", x), U("analytics_dev", x)))]


def _u23(x, ctx):
    return [_iff("b23", x, U("violates_law", x))]


def _u24_30(x, ctx):
    return [_iff("b24", x, U("infers_emotion", x)), _iff("b25", x, U("infers_sensitive", x)),
            _iff("b26", x, Or(U("categorizes_biometric", x), U("categorizes_infer", x))),
            _iff("b27", x, And(U("scores_profiles", x), U("harmful_treatment", x))),
            _iff("b28", x, And(U("targets_trait", x), U("exploits_vulnerability", x))),
            _iff("b29", x, And(U("rt_facial", x), U("law_enforcement", x), U("in_wild", x))),
            _iff("b30", x, And(Or(And(U("monitors", x), U("ongoing_surveillance", x)), U("rt_identification", x), U("persistent_tracking", x)),
                               U("uses_personal_info", x), Not(U("valid_consent", x))))]


def _u31_35(x, ctx):
    return [_iff("b31", x, Or(U("hides_ai", x), U("no_use_info", x))), _iff("b32", x, U("untested", x)),
            _iff("b33", x, Or(U("feedback_no_dev", x), U("feedback_no_github", x))),
            _iff("b34", x, U("no_capability_info", x)),
            _iff("b35", x, Or(And(U("requests_permissions", x), U("permissions_unnecessary", x)), U("perm_need_undefined", x)))]


def _u36(x, ctx):
    return [_iff("b36", x, Or(U("materials_illegal", x), U("promotes_illegal", x), U("unlicensed_third_party", x),
                               U("lower_support", x)))]


def _u38_act(x, ctx):
    return [_iff("b38", x, And(U("exercises_grant", x), U("after_termination", x), Not(U("grant_surviving", x))))]


BANX = ("b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9", "b10", "b23", "b24", "b25", "b26", "b27", "b28", "b29", "b30",
        "b31", "b32", "b33", "b34", "b35", "b36", "b38")
BANP = ("b12", "b13", "b14", "b15", "b16", "b17", "b18", "b19", "b20", "b21")


def _forbidden(x, ctx):
    """R1 + R5: forbidden / not forbidden; OPEN where the readings differ or the text gives none."""
    bx, bp = Or(*[U(b, x) for b in BANX]), Or(*[U(b, x) for b in BANP])
    doubt = Or(U("c19", x), U("unsafe_hardship", x), U("other_termination", x),
               And(U("exercises_grant", x), U("after_termination", x), U("grant_surviving", x)),
               And(U("contacts", x), Not(U("b13", x)), Not(U("a13", x))))
    f = U("forbidden", x)
    return [
        (Iff(U("banx", x), bx), A("banx", x)), (Iff(U("banp", x), bp), A("banp", x)),
        (Iff(U("doubt", x), doubt), A("doubt", x)),
        (Implies(U("banx", x), f), A("forbidden", x)),
        (Implies(And(U("banp", x), Not(U("perm22", x))), f), A("forbidden", x)),
        (Implies(And(U("b22", x), Not(U("perm22", x))), f), A("forbidden", x)),
        (Implies(And(Not(U("banx", x)), Not(U("banp", x)), Not(U("b22", x)), Not(U("doubt", x))), Not(f)), A("forbidden", x)),
        (Implies(And(Not(U("banx", x)), Not(U("banp", x)), U("perm22", x), Not(U("doubt", x))), Not(f)), A("forbidden", x)),
    ]


def _a13(x, ctx):
    """a13: the contact is allowed by unit 13 (both readings); used only to mark R4's doubt region."""
    c_, out_, pdu = U("contacts", x), U("outside_github", x), U("contact_uses_pd", x)
    ok = And(U("emergency", x), U("lawful_contact", x))
    return [_iff("a13", x, And(c_, Or(And(out_, U("sep_permission", x), ok), And(Not(out_), Not(pdu), ok))))]


def _ends(ctx):
    out = []
    for x in ctx.of("act"):
        out.append(_iff("ends", x, And(U("done", x), Or(U("discontinues_platform", x), U("forbidden", x),
                                                          U("oos_breach", x)))))
    for x in ctx.of("gh"):
        out.append(_iff("ends", x, And(U("done", x), U("gh_terminates", x))))
    for x in ctx.of("del"):      # R13: all the data deleted after the last day of a unit 18 period is a breach
        u = lambda p: U(p, x)  # noqa: E731
        out.append((Implies(And(u("trig"), u("all_deleted"), before(k("last", x), k("dd", x))), u("ends")), A("ends", x)))
        out.append((Implies(Or(Not(u("trig")), And(u("all_deleted"), no_later(k("dd", x), k("last", x)))), Not(u("ends"))),
                    A("ends", x)))
    return out


def _inforce(ctx):
    """R8 (and R13 for a missed unit 18 period) for every item that carries a question day."""
    ev = ctx.of("act") + ctx.of("gh")
    dl = ctx.of("del")
    out = []
    for x in ctx.of("q") + ctx.of("duty") + ctx.of("del"):
        qd = k("qday", x)
        for e in ev:
            out.append((Implies(And(U("ends", e), before(k("day", e), qd)), Not(U("inforce", x))), A("inforce", x)))
        for e in dl:
            out.append((Implies(And(U("ends", e), before(k("last", e), qd)), Not(U("inforce", x))), A("inforce", x)))
        out.append((Implies(And(*[Or(Not(U("ends", e)), before(qd, k("day", e))) for e in ev],
                                *[Or(Not(U("ends", e)), no_later(qd, k("last", e))) for e in dl]), U("inforce", x)),
                    A("inforce", x)))
    return out


def _ends_1124(ctx):
    """The frozen unit 37 ending events (28765183ad), kept only for mutant M14: no deletion item ends the Agreement."""
    out = []
    for x in ctx.of("act"):
        out.append(_iff("ends", x, And(U("done", x), Or(U("discontinues_platform", x), U("forbidden", x),
                                                          U("oos_breach", x)))))
    for x in ctx.of("gh"):
        out.append(_iff("ends", x, And(U("done", x), U("gh_terminates", x))))
    return out


def _inforce_1124(ctx):
    """The frozen R8 (28765183ad), kept only for mutant M14."""
    ev = ctx.of("act") + ctx.of("gh")
    out = []
    for x in ctx.of("q") + ctx.of("duty") + ctx.of("del"):
        qd = k("qday", x)
        for e in ev:
            out.append((Implies(And(U("ends", e), before(k("day", e), qd)), Not(U("inforce", x))), A("inforce", x)))
        out.append((Implies(And(*[Or(Not(U("ends", e)), before(qd, k("day", e))) for e in ev]), U("inforce", x)),
                    A("inforce", x)))
    return out


def _ghmay(ctx):
    out = []
    for x in ctx.of("gh"):
        linked = [a for (g, a) in sorted(ctx.links) if g == x]
        out.append(_iff("violation", x, Or(*[And(U("done", a), U("forbidden", a)) for a in linked],
                                            U("spirit_violation", x))))
        out.append((Implies(Or(U("gh_terminates", x), And(U("gh_action", x), U("violation", x), U("deems_necessary", x))),
                            U("ghmay", x)), A("ghmay", x)))
    return out


DUTIES = ("k_understand", "k_no_harm_reliance", "k_comply_policy", "k_comply_tos", "k_configure", "k_comply_law",
          "k_inform_use", "k_inform_ai", "k_test", "k_feedback", "k_inform_capabilities", "k_request_needed",
          "k_define_need", "k_responsible", "k_legal_materials", "k_support", "k_privacy_policy")


def _prerelease(u):
    """Unit 38 (R10): on termination, return the Pre-release Materials held unless GitHub asked for destruction (FL07),
    destroy them when it asked, and certify in writing on termination whether or not any were held (FL08)."""
    return [And(u("k_return_prerelease"), u("has_prerelease"), u("terminated_before"), Not(u("gh_asked_destroy"))),
            And(u("k_destroy_prerelease"), u("has_prerelease"), u("terminated_before"), u("gh_asked_destroy")),
            And(u("k_certify"), u("terminated_before"))]


def _prerelease_1124(u):
    """The frozen unit 38 duties (28765183ad), kept only for mutant M15."""
    return [And(Or(u("k_return_prerelease"), u("k_certify")), u("has_prerelease"), u("terminated_before")),
            And(u("k_destroy_prerelease"), u("has_prerelease"), u("terminated_before"), u("gh_asked_destroy"))]


def _pending(u):
    """R10 (fidelity step flag FL05 of the fix): asked on the termination day itself, a unit 38 duty is OPEN, not 'not
    required' (the text gives no time of day, R8)."""
    return And(Or(u("k_return_prerelease"), u("k_destroy_prerelease"), u("k_certify")), u("terminated_on_qday"))


def _required(ctx, prerelease=_prerelease, pending=_pending):
    out = []
    for x in ctx.of("duty"):
        u = lambda p: U(p, x)  # noqa: E731
        req = Or(*[u(p) for p in DUTIES],
                 And(u("k_encrypt"), u("stored"), u("pd")),
                 And(u("k_contact_permission"), u("contact_outside")),
                 And(u("k_delete_event"), u("event_happened"), u("pd")),
                 And(u("k_delete_request"), u("user_requested"), u("pd")),
                 And(u("k_licences"), u("uses_third_party")),
                 *prerelease(u),
                 u("oos_duty"))
        if pending is None:
            out.append(_iff("required", x, req))
        else:
            out.append((Implies(req, U("required", x)), A("required", x)))
            out.append((Implies(And(Not(req), Not(pending(u))), Not(U("required", x))), A("required", x)))
        sec2_3 = Or(*[u(p) for p in DUTIES + ("k_encrypt", "k_contact_permission", "k_delete_event", "k_delete_request",
                                              "k_licences", "k_return_prerelease", "k_destroy_prerelease", "k_certify")])
        out.append(_iff("survives", x, Or(sec2_3, u("sec1"), u("sec4a"), u("sec5"), u("sec7_19"))))
        out.append(_iff("bound", x, And(U("required", x), Or(U("inforce", x), U("survives", x)))))
    return out


def _deletion(ctx):
    out = []
    for x in ctx.of("del"):
        u = lambda p: U(p, x)  # noqa: E731
        out.append(_iff("trig", x, Or(u("user_deleted_ext"), u("discontinued_ext"), u("ext_removed"))))
        out.append((Implies(u("trig"), shift(k("last", x), k("ev", x), THIRTY)), "last_" + x))
        out.append((Implies(And(u("trig"), u("all_deleted"), no_later(k("dd", x), k("last", x))), u("met")), A("met", x)))
        out.append((Implies(And(u("trig"), Or(Not(u("all_deleted")), before(k("last", x), k("dd", x)))), Not(u("met"))),
                    A("met", x)))
        out.append((Implies(And(u("trig"), no_later(k("qday", x), k("last", x))), u("keep_ok")), A("keep_ok", x)))
        out.append((Implies(And(u("trig"), before(k("last", x), k("qday", x))), Not(u("keep_ok"))), A("keep_ok", x)))
    return out


def _gh_notice(ctx):
    """R11: GitHub need not give notice (k_gh_notice on a duty item: not required): written inside _required's closure."""
    return []


def _merge(*builders):
    return lambda ctx: [r for b in builders for r in b(ctx)]


UNITS = {
    1: ("PART", _merge(_pd, _ghmay), "definition by reference",
        "'User' is defined only by the ToS (a stated fact: who is a User); 'Personal Data' written (R3; 'could identify' a "
        "stated fact where the case settles it); GitHub's right to act written (R11) with 'deem necessary' and 'spirit' "
        "stated"),
    2: ("PART", _acts(_u2), "other:norm", "'must understand ... and not rely on it' written as a ban on reliance where "
        "significant harm could result (stated) and duty items k_understand / k_no_harm_reliance / k_comply_policy; the "
        "duty on a state of mind ('understand') is only a duty item"),
    3: ("RULE", _acts(_u3), "the ToS / AUP outcome a stated fact (cross-reference secondary)"),
    4: ("RULE", _acts(_u4), "stored Personal Data not encrypted; 'properly configure' stated; lead-in to 5-10"),
    5: ("RULE", _acts(_u5_10), "units 5-10 in one builder"),
    6: ("RULE", lambda ctx: [], "carried by unit 5's builder"), 7: ("RULE", lambda ctx: [], "carried by unit 5's builder"),
    8: ("RULE", lambda ctx: [], "carried by unit 5's builder ('mislead/deceive' stated)"),
    9: ("RULE", lambda ctx: [], "carried by unit 5's builder ('may damage' stated)"),
    10: ("RULE", lambda ctx: [], "carried by unit 5's builder"),
    11: ("RULE", lambda ctx: [], "lead-in of 12-22 (no rule of its own: 'You do not have independent rights' adds none)"),
    12: ("RULE", _acts(_u12), "'proper User consent' stated"),
    13: ("PART", _merge(_acts(_u13), _acts(_a13)), "other:judgment standard",
         "R4: two readings, written where they agree; 'clear and separate', 'emergency', 'in compliance with the law' stated"),
    14: ("RULE", _acts(_u14_18), "units 14-18 bans in one builder ('specifically necessary' stated)"),
    15: ("RULE", lambda ctx: [], "carried by unit 14's builder ('under any circumstances': consent does not lift it)"),
    16: ("RULE", lambda ctx: [], "carried by unit 14's builder"),
    17: ("RULE", lambda ctx: [], "carried by unit 14's builder ('beyond what is necessary' stated)"),
    18: ("PART", _deletion, "deadline/time limit",
         "R7: thirty days written in Lean (shift_days 30, the brief's convention); 'ignoring' a ban (unit 14's builder); a "
         "request with none of the three events has no period (OPEN)"),
    19: ("PART", _acts(_u19), "other:judgment standard", "R6: copies without merging OPEN; 'unrelated' stated"),
    20: ("RULE", _acts(_u20), "'easily accessible' stated; the duty as a failure classification and a duty item"),
    21: ("RULE", _acts(_u21), "'surveillance' stated"),
    22: ("PART", _acts(_u22), "other:judgment standard",
         "R5: the permission against units 12-21 OPEN; 'approved by GitHub', 'aggregated and anonymized' stated"),
    23: ("PART", _acts(_u23), "other:norm", "'should not create unsafe environments' not carried (R1: OPEN); applicable "
         "laws a stated outcome"),
    24: ("RULE", _acts(_u24_30), "units 24-30 in one builder"),
    25: ("RULE", lambda ctx: [], "carried by unit 24's builder (age range, mouth position, hair colour are not sensitive "
         "attributes: infers_sensitive false)"),
    26: ("RULE", lambda ctx: [], "carried by unit 24's builder"),
    27: ("RULE", lambda ctx: [], "carried by unit 24's builder ('would lead to ... treatment' stated)"),
    28: ("RULE", lambda ctx: [], "carried by unit 24's builder ('vulnerabilities' stated)"),
    29: ("RULE", lambda ctx: [], "carried by unit 24's builder"),
    30: ("RULE", lambda ctx: [], "carried by unit 24's builder ('valid consent', 'surveillance' stated)"),
    31: ("RULE", _merge(_acts(_u31_35), _required), "units 31-35 failures; every duty item (units 2-36, 38) and survival "
         "(R9) in _required"),
    32: ("RULE", lambda ctx: [], "carried by unit 31's builder"), 33: ("RULE", lambda ctx: [], "carried (R12)"),
    34: ("RULE", lambda ctx: [], "carried by unit 31's builder ('appropriate level of human oversight' is the purpose)"),
    35: ("RULE", lambda ctx: [], "carried by unit 31's builder ('appropriate and necessary' stated)"),
    36: ("RULE", _acts(_u36), "'legal' stated; duty items in _required"),
    37: ("RULE", _merge(_acts(_forbidden), _ends, _inforce), "R8, R13 (a missed unit 18 period); R1 closure; GitHub's "
         "'any reason without notice' in unit 1's builder (R11) and k_gh_notice (not required)"),
    38: ("RULE", _acts(_u38_act), "R9 survival in _required; R10 ceased rights; return / destroy / certify duty items"),
}


def units_table(mutant=None):
    t = dict(UNITS)
    if mutant is not None:
        t = MUTANTS[mutant][1](t)
    return t


def rules(ctx, mutant=None):
    """Ground rules for a case: [{"id", "unit", "formula", "defines"}]; a formula grounded twice is kept once."""
    out, seen = [], set()
    for n, e in sorted(units_table(mutant).items()):
        if e[1] is None:
            continue
        for i, (f, target) in enumerate(e[1](ctx)):
            kk = key([f, target])
            if kk in seen:
                continue
            seen.add(kk)
            out.append({"id": f"u{n}.{i}", "unit": n, "formula": f, "defines": [] if target is None else [target]})
    return out


# --- structure helpers ----------------------------------------------------------------------------------------------

def q(formula):
    return {"format": "ve-quantity@1", "formula": formula}


def is_iff(f):
    return (type(f) is list and f and f[0] == "and" and type(f[1]) is list and type(f[2]) is list
            and f[1][:1] == ["implies"] and f[2][:1] == ["implies"] and f[1][1] == f[2][2] and f[1][2] == f[2][1])


def atoms_in(f, atoms, constants):
    if type(f) is not list or not f:
        return
    if f[0] in ("unary", "binary"):
        atoms.add(key(f))
        return
    if f[0] == "const" and len(f) == 3:
        constants.add(f[2])
        return
    for part in f[1:]:
        atoms_in(part, atoms, constants)


ALL_FACTS = {**ACT_PLAIN, **ACT_STATED, **GH_PLAIN, **GH_STATED, **DUTY_PLAIN, **DUTY_STATED, **DEL_PLAIN}


def environment(ctx, used=None):
    consts = {}
    for x, kind in ctx.items:
        consts[x] = {"sort": "item", "description": f"The case's {kind} item {x}.", "verbalisation": f"{kind} {x}"}
        for base, (u, w) in KINDS[kind].items():
            name = f"{base}_{x}"
            if used is not None and name not in used:
                continue
            consts[name] = {"sort": "$int", "unit": u, "description": f"{w[0].upper() + w[1:]} ({x}).",
                            "verbalisation": f"{w} ({x})"}
    preds = {n: {"arguments": ["item"], "description": d[0].upper() + d[1:] + "."}
             for n, d in {**ALL_FACTS, **DERIVED}.items()}
    return {"language": "ve.core@0.2", "profiles": ["documents@1", "order@0", "relational-fol@0", "time@0"],
            "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {"item": {"description": "An act, GitHub act, duty, deletion or question day of the case."}},
                           "predicates": preds, "constants": consts},
            "unit_schema": "ve-units@1",
            "units": {DAY: {"scale": "1", "display": {"kind": "iso_date"}}}}


# --- planted errors (run.py --mutants, smoke_test.py): each must change at least one answer ------------------------

def _swap(n, fn):
    def apply(t):
        t = dict(t)
        e = t[n]
        t[n] = (e[0], fn(e[1]), *e[2:])
        return t
    return apply


def _json_sub(a, b):
    return lambda builder: (lambda ctx: [(json.loads(json.dumps(f).replace(a, b)), tg) for f, tg in builder(ctx)])


def _drop_target(pred):
    """Drop the rules that define <pred> (its atom then stays OPEN)."""
    return lambda builder: (lambda ctx: [(f, tg) for f, tg in builder(ctx) if not (tg and f'"{pred}"' in tg)])


def _sub(pred, repl, only=None):
    """Replace every atom <pred>(x) by repl (TRUE / FALSE) in the unit's rules (only: in rules whose target names it)."""
    def walk(f):
        if type(f) is list and len(f) == 3 and f[0] == "unary" and f[1] == pred:
            return repl
        return [walk(g) for g in f] if type(f) is list else f
    return lambda builder: (lambda ctx: [((walk(f) if only is None or (tg and f'"{only}"' in tg) else f), tg)
                                         for f, tg in builder(ctx)])


MUTANTS = {
    "M1": ("unit 18: thirty days read as twenty-nine", _swap(18, _json_sub('"30"]', '"29"]'))),
    "M2": ("unit 18: thirty days read as thirty-one", _swap(18, _json_sub('"30"]', '"31"]'))),
    "M3": ("unit 7: 'unpublished' dropped (every API banned)", _swap(5, _sub("api_published", FALSE))),
    "M4": ("unit 12: proper consent ignored", _swap(12, _sub("proper_consent", FALSE))),
    "M5": ("unit 15: sharing with a third party not banned", _swap(14, _sub("shares_third", FALSE))),
    "M6": ("unit 33 / R12: a mechanism to the developer only accepted", _swap(31, _sub("feedback_no_github", FALSE))),
    "M7": ("unit 29: the law-enforcement condition dropped", _swap(24, _sub("law_enforcement", TRUE))),
    "M8": ("unit 38 / R9: section 2 and 3 duties read as not surviving", _swap(31, _sub("survives", FALSE, "bound"))),
    "M9": ("unit 37 / R8: a breach read as not ending the Agreement", _swap(37, _sub("forbidden", FALSE, "ends"))),
    "M10": ("unit 4: stored Personal Data need not be encrypted", _swap(4, _sub("encrypted", TRUE))),
    "M11": ("unit 22 / R5: the aggregated-and-anonymized permission dropped", _swap(22, _drop_target("perm22"))),
    "M12": ("unit 25: inferring a sensitive attribute not banned", _swap(24, _sub("infers_sensitive", FALSE))),
    "M13": ("unit 13 / R4: contact outside GitHub needs no separate permission", _swap(13, _sub("sep_permission", TRUE))),
    # fidelity fix 2026-11-26 (rows statute-latent-github-copilot-ext-U18, -U38): each restores the frozen rule
    "M14": ("unit 37 / R13 (FL04): the frozen ending events: a missed unit 18 period does not end the Agreement",
            lambda t: {**t, 37: (t[37][0], _merge(_acts(_forbidden), _ends_1124, _inforce_1124), *t[37][2:])}),
    "M15": ("unit 38 (FL07, FL08): the frozen Pre-release duties: return even when GitHub asked for destruction, certify "
            "only when materials are held",
            lambda t: {**t, 31: (t[31][0], _merge(_acts(_u31_35), lambda ctx: _required(ctx, _prerelease_1124, None)),
                                 *t[31][2:])}),
}


def translation_sha256():
    import pathlib
    return hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
