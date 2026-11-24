"""The encoder's cases, from questions-enc.jsonl ONLY (sha256 checked at import). CROSS-FAMILY questions, Opus encoder.

Encoder: dri-statute-corpus-github-copilot-ext-w-1124 (Opus 5.5), after the translation was committed (b62b022dd6). Each
in-scope case is transcribed by hand into items (encode.py: act / gh / duty / del / q) with their plain facts (closed world,
C1), the stated judgments the case states (C2) and the stated days. The question's form is read from its text:
"may <developer / Extension> ..." -> may; "may GitHub ..." -> may_gh; "must <developer> <duty>" -> must; "must <developer>
change / add / replace ..." about an act as it stands -> must_cure; "is the Agreement still in force on D" -> inforce; "is
<developer> still bound on D by ..." -> bound; the latest deletion day -> last; "did <developer> meet the deletion
deadline" -> met. "judgement": what the encoder decided beyond copying a stated fact (listed as encoder judgement).
REFUSED: questions the encoder could not transcribe into the translation's vocabulary (OPEN, listed, not correct).
PROBES: out-of-scope cases (every answer UNSUPPORTED). UNSUPPORTED: none.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENC_SHA256 = "016e68c08e6183e057327ec20e1b853b9e789d482236a9f090bb0aa0fa7a2a07"
if hashlib.sha256((HERE / "questions-enc.jsonl").read_bytes()).hexdigest() != ENC_SHA256:
    raise SystemExit("questions-enc.jsonl differs from the sealed encoder file")


def act(x, facts=(), stated=None, day=None):
    return {"id": x, "kind": "act", "facts": list(facts), "stated": dict(stated or {}), **({"day": day} if day else {})}


def gh(x, facts=(), stated=None, day=None):
    return {"id": x, "kind": "gh", "facts": list(facts), "stated": dict(stated or {}), **({"day": day} if day else {})}


def duty(x, facts=(), stated=None, qday=None):
    return {"id": x, "kind": "duty", "facts": list(facts), "stated": dict(stated or {}), **({"qday": qday} if qday else {})}


def dele(x, facts=(), ev=None, dd=None, qday=None):
    d = {"id": x, "kind": "del", "facts": list(facts)}
    for kk, v in (("ev", ev), ("dd", dd), ("qday", qday)):
        if v:
            d[kk] = v
    return d


def qd(x, qday):
    return {"id": x, "kind": "q", "qday": qday}


def case(cid, items, questions, links=(), judgement=()):
    """questions: [(n, form, item)] -> qid f"{cid}-{n}"."""
    return {"id": cid, "judgement": list(judgement),
            "subs": [{"spec": {"items": items, "links": list(links)},
                      "questions": [{"qid": f"{cid}-{n}", "form": f, "item": x} for n, f, x in questions]}]}


C = {"proper_consent": True}
CODE = ("d_content",)
CSU = ("collects", "stores", "uses")
CASES = [
    case("G001", [duty("e_code", ("k_encrypt", "stored", "d_content")),
                  duty("e_mail", ("k_encrypt", "stored"), {"d_identifying": True}),
                  act("a", CSU + CODE + ("encrypted", "calls_api", "api_published"), C)],
         [(1, "must", "e_code"), (2, "must", "e_mail"), (4, "may", "a")],
         judgement=["G001-2: the email address on Lena's GitHub account relates to her and could identify her "
                    "(d_identifying true)"]),
    case("G002", [act("a", ("stores", "d_content"), C), act("cfg", ("configures_systems",), {"improper_config": True}),
                  act("held", ("done", "stores", "d_content"), C), act("cfgd", ("done", "configures_systems"),
                                                                       {"improper_config": True}),
                  qd("q", "2027-01-06")],
         [(1, "may", "a"), (2, "must_cure", "cfg"), (3, "inforce", "q")],
         judgement=["G002-3: the unencrypted holding and the configuration are done acts with no stated first day (days "
                    "unknown)"]),
    case("G003", [duty("enc", ("k_encrypt", "d_content")), act("api1", ("calls_api", "api_published")),
                  act("api2", ("calls_api",)), act("byp", ("bypasses_controls",))],
         [(1, "must", "enc"), (2, "may", "api1"), (3, "may", "api2"), (4, "may", "byp")]),
    case("G004", [act("auth", ("degrades_security",)), act("tx", ("transmits_code",), {"may_damage": True}),
                  act("rev", ("reverse_engineers",))],
         [(1, "may", "auth"), (2, "may", "tx"), (3, "may", "rev")],
         judgement=["G004-1: removing the Platform's authentication protection so anyone can access the protected service "
                    "degrades or compromises security (degrades_security)"]),
    case("G005", [act("claim", ("done", "tells_users"), {"misleads": True}, day="2027-01-09"),
                  act("rely", ("relies_copilot",), {"significant_harm": True}),
                  gh("susp", ("gh_action",), {"deems_necessary": True, "spirit_violation": True})],
         [(1, "may", "claim"), (2, "may", "rely"), (3, "may_gh", "susp")], links=[("susp", "claim")]),
    case("G006", [act("tos", ("violates_tos",)), act("fr", ("violates_law",))],
         [(1, "may", "tos"), (2, "may", "fr")]),
    case("G007", [act("em", ("contacts", "contact_uses_pd"), {"emergency": True, "lawful_contact": True}),
                  act("promo", ("contacts", "contact_uses_pd"), {"emergency": False, "lawful_contact": True})],
         [(1, "may", "em"), (2, "may", "promo")],
         judgement=["G007: addressing the in-GitHub message with the User's account name uses Personal Data "
                    "(contact_uses_pd)"]),
    case("G008", [act("em", ("contacts", "outside_github", "contact_uses_pd"),
                      {"sep_permission": True, "emergency": True, "lawful_contact": True}),
                  act("ad", ("contacts", "outside_github", "contact_uses_pd"),
                      {"sep_permission": True, "emergency": False, "lawful_contact": True})],
         [(1, "may", "em"), (2, "may", "ad")]),
    case("G009", [act("em", ("contacts", "outside_github", "contact_uses_pd"),
                      {"sep_permission": False, "emergency": True, "lawful_contact": True}),
                  duty("perm", ("k_contact_permission", "contact_outside"))],
         [(1, "may", "em"), (2, "must", "perm")]),
    case("G010", [act("pw1", ("requests_sensitive",), {"spec_necessary": True}),
                  act("pw2", ("requests_sensitive",), {"spec_necessary": False}),
                  act("cc1", ("requests_sensitive",), {"spec_necessary": True}),
                  act("cc2", ("requests_sensitive",), {"spec_necessary": False})],
         [(1, "may", "pw1"), (2, "may", "pw2"), (3, "may", "cc1"), (4, "may", "cc2")],
         judgement=["G010: each act is the request only (no answer yet, so nothing is collected by it)"]),
    case("G011", [act("t1", ("shares_third", "d_content"), C), act("t2", ("shares_third", "d_content"), C),
                  act("t3", ("shares_third", "d_content"), C)],
         [(1, "may", "t1"), (2, "may", "t2"), (3, "may", "t3")]),
    case("G012", [act("p1", CSU + CODE + ("encrypted", "creates_profiles"), {**C, "beyond_necessary": False}),
                  act("p2", CSU + CODE + ("encrypted", "creates_profiles"), {**C, "beyond_necessary": True}),
                  act("help", ("encourages_circumvent",))],
         [(1, "may", "p1"), (2, "may", "p2"), (3, "may", "help")]),
    case("G013", [act("mkt", CSU + CODE + ("encrypted", "merges"), {**C, "unrelated_purpose": True}),
                  act("exp", CSU + CODE + ("encrypted", "merges"), {**C, "unrelated_purpose": False}),
                  act("pp", ("privacy_policy_act",), {"pp_not_accessible": False})],
         [(1, "may", "mkt"), (2, "may", "exp"), (3, "must_cure", "pp")]),
    case("G014", [act("pp", ("privacy_policy_act", "pp_not_public"), {"pp_not_accessible": False}),
                  act("ign", ("ignores_request",)),
                  dele("d", ("request_only",))],
         [(1, "must_cure", "pp"), (2, "may", "ign"), (3, "last", "d")]),
    case("G015", [act("agg", ("uses", "analytics_dev"), {"d_identifying": False, "aggregated_anonymized": True}),
                  act("omar", ("uses", "analytics_dev"), {"d_identifying": True, "aggregated_anonymized": False,
                                                          "proper_consent": False}),
                  act("ada", ("uses", "analytics_dev", "d_content"), {"aggregated_anonymized": False,
                                                                     "proper_consent": False})],
         [(1, "may", "agg"), (2, "may", "omar"), (3, "may", "ada")],
         judgement=["G015-2, -3: the stated consent covers collection and storage for code assistance, not the analytics "
                    "use (proper_consent false for the analytics act)",
                    "G015-2: request counts grouped under Omar's account name relate to him and could identify him",
                    "G015-1: request counts generated by the Extension are not content made available by Users"]),
    case("G016", [act("surv", ("collects", "uses", "monitors"), {**C, "surveillance": True, "valid_consent": True}),
                  act("mw", ("assists_obtain", "monitors"), {**C, "surveillance": True, "valid_consent": True})],
         [(1, "may", "surv"), (2, "may", "mw")],
         judgement=["G016: accessing account activity to watch Lena is an act that monitors individuals (monitors)"]),
    case("G017", [act("theo", ("collects", "uses", "persistent_tracking", "uses_personal_info", "monitors"),
                      {"d_identifying": False, "surveillance": False, "valid_consent": True}),
                  act("nia", ("collects", "uses", "persistent_tracking", "uses_personal_info", "monitors"),
                      {"d_identifying": False, "surveillance": False, "valid_consent": False})],
         [(1, "may", "theo"), (2, "may", "nia")],
         judgement=["G017: the volunteers are not Users, customers or employees, so their coordinates are not Personal Data "
                    "under the definition's first clause (d_identifying false); tracking monitors individuals"]),
    case("G018", [act("range"), act("age", ("infers_sensitive",)), act("mouth"), act("hair"),
                  act("gender", ("infers_sensitive",))],
         [(1, "may", "range"), (2, "may", "age"), (3, "may", "mouth"), (4, "may", "hair"), (5, "may", "gender")],
         judgement=["G018: inferring one person's age range, mouth position or hair colour from a photograph is not "
                    "categorizing people based on biometric data (unit 26) and not an emotional state (unit 24)"]),
    case("G019", [act("voice", ("infers_emotion",)), act("face", ("infers_emotion",)), act("typing", ("infers_emotion",))],
         [(1, "may", "voice"), (2, "may", "face"), (3, "may", "typing")]),
    case("G020", [act("fp", ("categorizes_biometric",)), act("prof", ("scores_profiles",), {"harmful_treatment": True}),
                  act("dis", ("targets_trait",), {"exploits_vulnerability": True})],
         [(1, "may", "fp"), (2, "may", "prof"), (3, "may", "dis")]),
    case("G021", [act("police", ("rt_facial", "law_enforcement", "in_wild", "rt_identification", "uses_personal_info",
                                 "monitors"), {"surveillance": True, "valid_consent": False, "d_identifying": False}),
                  act("theater", ("rt_identification", "uses_personal_info"),
                      {"surveillance": False, "valid_consent": True, "d_identifying": False})],
         [(1, "may", "police"), (2, "may", "theater")],
         judgement=["G021-2: a fixed camera in a rehearsal room is not facial recognition on mobile cameras (rt_facial "
                    "false)"]),
    case("G022", [act("alt1"), duty("ai", ("k_inform_ai",))],
         [(1, "must_cure", "alt1"), (2, "must", "ai")]),
    case("G023", [act("f1", ("feedback_no_github",)), act("f2", ("feedback_no_dev",)), act("f3")],
         [(1, "must_cure", "f1"), (2, "must_cure", "f2"), (3, "must_cure", "f3")]),
    case("G024", [duty("test", ("k_test",)), duty("cap", ("k_inform_capabilities",)),
                  act("erase", ("requests_permissions", "perm_need_undefined"), {"permissions_unnecessary": True}),
                  duty("need", ("k_define_need",))],
         [(1, "must", "test"), (2, "must", "cap"), (3, "may", "erase"), (4, "must", "need")]),
    case("G025", [dele("d", ("user_deleted_ext", "all_deleted"), ev="2027-01-31", dd="2027-03-01"),
                  duty("del", ("k_delete_event", "event_happened", "d_content"))],
         [(1, "last", "d"), (2, "met", "d"), (3, "must", "del")]),
    case("G026", [dele("d", ("discontinued_ext", "all_deleted"), ev="2028-02-27", dd="2028-03-28"),
                  act("disc", ("done",), day="2028-02-27"), qd("q", "2028-03-28")],
         [(1, "last", "d"), (2, "met", "d"), (3, "inforce", "q")],
         judgement=["G026-3: discontinuing the Extension while continuing to use the Platform is not discontinuing use of "
                    "the Platform (discontinues_platform false)"]),
    case("G027", [dele("d", ("ext_removed", "all_deleted"), ev="2027-02-28", dd="2027-03-31")],
         [(1, "last", "d"), (2, "met", "d")]),
    case("G028", [dele("code", ("user_deleted_ext", "all_deleted"), ev="2027-12-31", dd="2028-01-29"),
                  dele("all", ("user_deleted_ext", "all_deleted"), ev="2027-12-31", dd="2028-01-31")],
         [(1, "last", "all"), (2, "met", "code"), (3, "met", "all")],
         judgement=["G028-2: 'the deadline for Sol's code' read as the code's own deletion day (all of the code deleted on "
                    "29 January)"]),
    case("G029", [dele("d", ("discontinued_ext", "all_deleted"), ev="2028-01-31", dd="2028-03-01")],
         [(1, "last", "d"), (2, "met", "d")]),
    case("G030", [dele("d", ("ext_removed", "all_deleted"), ev="2026-12-31", dd="2027-01-31")],
         [(1, "last", "d"), (2, "met", "d")],
         judgement=["G030: the developer removing the Extension from the Platform is the event 'Your Extension is removed'"]),
    case("G031", [act("diag", ("materials_illegal",)), duty("lic", ("k_licences", "uses_third_party")),
                  duty("sup", ("k_support",)), duty("resp", ("k_responsible",))],
         [(1, "may", "diag"), (2, "must", "lic"), (3, "must", "sup"), (4, "must", "resp")]),
    case("G032", [act("stop", ("done", "discontinues_platform"), day="2027-02-04"), qd("q", "2027-02-05"),
                  duty("enc", ("k_encrypt", "stored", "d_content"), qday="2027-02-05"),
                  duty("ret", ("k_return_prerelease", "has_prerelease", "terminated_before")),
                  duty("cert", ("k_certify", "has_prerelease", "terminated_before"))],
         [(1, "inforce", "q"), (2, "bound", "enc"), (3, "must", "ret"), (4, "must", "cert")],
         judgement=["G032-3, -4: terminated_before and has_prerelease set from the stated discontinuation of all Platform "
                    "use (unit 37 applied by the encoder) and the materials held at that instant"]),
    case("G033", [gh("term", ("done", "gh_terminates"), day="2027-02-06"), qd("q", "2027-02-07"),
                  duty("dest", ("k_destroy_prerelease", "has_prerelease", "terminated_before", "gh_asked_destroy")),
                  duty("cert", ("k_certify", "has_prerelease", "terminated_before"))],
         [(1, "may_gh", "term"), (2, "inforce", "q"), (3, "must", "dest"), (4, "must", "cert")],
         judgement=["G033-3, -4: terminated_before and has_prerelease set from GitHub's stated termination and the copies "
                    "Bryn controlled at that instant"]),
    case("G034", [act("api", ("done", "calls_api"), day="2027-02-08"), qd("q", "2027-02-08"),
                  duty("fb", ("k_feedback",), qday="2027-02-09"), duty("maint", ("k_responsible",), qday="2027-02-09")],
         [(1, "inforce", "q"), (2, "bound", "fb"), (3, "bound", "maint")]),
    case("G035", [gh("term", ("done", "gh_terminates"), day="2027-02-10"),
                  duty("s4a", ("oos_duty", "sec4a"), qday="2027-02-11"),
                  duty("s4b", ("oos_duty", "sec4b"), qday="2027-02-11"),
                  act("grant", ("exercises_grant", "after_termination", "grant_surviving"))],
         [(1, "bound", "s4a"), (2, "bound", "s4b"), (3, "may", "grant")],
         judgement=["G035-1, -2: the obligations of section 4's paragraphs exist (oos_duty, cross-reference: section 4 is "
                    "out of scope)", "G035-2: 'after 10 February 2027' asked on 11 February 2027"]),
]

REFUSED = {
    "G001": {"G001-3": "unit 11 ('You do not have independent rights to any Personal Data') is not written: the "
                       "translation has no word for a claim of rights, so the act cannot be transcribed (C1 would "
                       "wrongly close it)"},
    "G027": {"G027-3": "whether missing the thirty-day deadline is a breach that ends the Agreement, and on which day, "
                       "is not carried (the translation's ending events are a done forbidden act, discontinuing the "
                       "Platform, GitHub's termination or a stated breach)"},
}

PROBE_QIDS = {"G036": ["G036-1", "G036-2", "G036-3"], "G037": ["G037-1", "G037-2"], "G038": ["G038-1", "G038-2"],
              "G039": ["G039-1", "G039-2"], "G040": ["G040-1", "G040-2"], "G041": ["G041-1"], "G042": ["G042-1"],
              "G043": ["G043-1", "G043-2", "G043-3", "G043-4"], "G044": ["G044-1", "G044-2", "G044-3"],
              "G045": ["G045-1"]}
PROBES = {cid: "scope out (questions-enc.jsonl), D12" for cid in PROBE_QIDS}
UNSUPPORTED = {}
