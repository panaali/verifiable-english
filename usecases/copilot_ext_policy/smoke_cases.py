"""Made-up smoke cases (written with the translation, before questions-enc.jsonl was opened), hand-worked from the readings
R1-R12 of translation.py, not by running it. Each case: {"id", "subs": [{"spec": encode spec, "questions": [...]}]}."""


def act(x, facts=(), stated=None, day=None):
    return {"id": x, "kind": "act", "facts": list(facts), "stated": dict(stated or {}), **({"day": day} if day else {})}


def gh(x, facts=(), stated=None, day=None):
    return {"id": x, "kind": "gh", "facts": list(facts), "stated": dict(stated or {}), **({"day": day} if day else {})}


def duty(x, facts=(), qday=None):
    return {"id": x, "kind": "duty", "facts": list(facts), **({"qday": qday} if qday else {})}


def dele(x, facts=(), ev=None, dd=None, qday=None):
    d = {"id": x, "kind": "del", "facts": list(facts)}
    for k, v in (("ev", ev), ("dd", dd), ("qday", qday)):
        if v:
            d[k] = v
    return d


def qd(x, qday):
    return {"id": x, "kind": "q", "qday": qday}


def case(cid, items, questions, links=()):
    return {"id": cid, "subs": [{"spec": {"items": items, "links": list(links)},
                                 "questions": [{"qid": f"{cid}-{i + 1}", "form": f, "item": x}
                                               for i, (f, x) in enumerate(questions)]}]}


DATA = ("d_content", "collects", "uses")
CASES = [
    case("S1", [act("a1", DATA + ("stores", "encrypted"), {"proper_consent": True}),
                act("a2", DATA + ("stores",), {"proper_consent": True}),
                act("a3", DATA, {"proper_consent": False}),
                act("a4", ("calls_api", "api_published")), act("a5", ("calls_api",))],
         [("may", "a1"), ("may", "a2"), ("may", "a3"), ("may", "a4"), ("may", "a5")]),
    case("S2", [act("c1", ("contacts", "outside_github", "contact_uses_pd"),
                    {"sep_permission": True, "emergency": True, "lawful_contact": True}),
                act("c2", ("contacts", "outside_github", "contact_uses_pd"), {"sep_permission": False}),
                act("c3", ("contacts", "contact_uses_pd"), {"emergency": False}),
                act("c4", ("contacts",), {"emergency": True, "lawful_contact": True}),
                act("c5", ("contacts",), {"emergency": False, "lawful_contact": True}),
                act("c6", ("contacts", "contact_uses_pd"), {"emergency": True, "lawful_contact": True})],
         [("may", "c1"), ("may", "c2"), ("may", "c3"), ("may", "c4"), ("may", "c5"), ("may", "c6")]),
    case("S3", [act("i1", ("infers_emotion",)), act("i2", ()), act("i3", ("rt_facial", "law_enforcement", "in_wild")),
                act("i4", ("rt_facial", "rt_identification", "uses_personal_info"), {"valid_consent": False}),
                act("i5", ("rt_identification", "uses_personal_info"), {"valid_consent": True}),
                act("p1", ("uses", "analytics_dev"), {"d_identifying": False, "aggregated_anonymized": True}),
                act("p2", ("uses", "analytics_dev", "shares_third", "d_content"), {"aggregated_anonymized": True}),
                act("p3", ("uses", "analytics_dev", "shares_third", "d_content", "calls_api"), {"aggregated_anonymized": True}),
                act("i6", ("rt_facial", "in_wild")), act("i7", ("infers_sensitive",)),
                act("p4", ("uses", "analytics_dev", "exploits_other", "d_content"),
                    {"aggregated_anonymized": True, "proper_consent": True, "gh_approved": False,
                     "disclosed_permitted": False})],
         [("may", "i1"), ("may", "i2"), ("may", "i3"), ("may", "i4"), ("may", "i5"), ("may", "p1"), ("may", "p2"),
          ("may", "p3"), ("may", "i6"), ("may", "i7"), ("may", "p4")]),
    case("S4", [dele("d1", ("user_deleted_ext", "all_deleted"), ev="2028-02-29", dd="2028-03-30", qday="2028-03-31"),
                dele("d2", ("discontinued_ext", "all_deleted"), ev="2027-12-31", dd="2028-01-31"),
                dele("d3", ("request_only", "all_deleted"), dd="2027-05-01"),
                dele("d4", ("ext_removed",), ev="2027-01-31", dd="2027-02-10")],
         [("last", "d1"), ("met", "d1"), ("keep", "d1"), ("met", "d2"), ("last", "d3"), ("met", "d3"), ("met", "d4"),
          ("last", "d4")]),
    case("S5", [act("e1", ("done", "discontinues_platform"), day="2027-06-10"),
                qd("q1", "2027-06-11"), qd("q2", "2027-06-09"), qd("q3", "2027-06-10"),
                duty("t1", ("k_delete_event", "event_happened", "d_content"), qday="2027-07-01"),
                duty("t2", ("k_return_prerelease", "has_prerelease", "terminated_before"), qday="2027-07-01"),
                duty("t3", ("k_gh_notice",)), duty("t4", ("k_other",)),
                gh("g1", ("done", "gh_terminates"), day="2027-08-01")],
         [("inforce", "q1"), ("inforce", "q2"), ("inforce", "q3"), ("bound", "t1"), ("bound", "t2"), ("must", "t3"),
          ("must", "t4"), ("may_gh", "g1")]),
    case("S6", [act("b1", ("done", "calls_api"), day="2027-03-01"),
                gh("g2", ("gh_action",), {"deems_necessary": True}),
                gh("g3", ("gh_action",), {"deems_necessary": True, "spirit_violation": False}),
                qd("q4", "2027-03-05"), qd("q5", "2027-02-01")],
         [("may_gh", "g2"), ("may_gh", "g3"), ("inforce", "q4"), ("inforce", "q5")], links=[("g2", "b1")]),
    case("S7", [act("f1", ("feedback_no_github",)), act("f2", ("feedback_no_dev",)), act("f3", ()),
                duty("du1", ("k_feedback",)), duty("du2", ("k_encrypt", "stored", "d_content")),
                duty("du3", ("k_encrypt", "d_content")), duty("du4", ("k_licences", "uses_third_party")),
                act("s1", ("shares_third", "d_content"), {"proper_consent": True}), act("s2", ("unsafe_hardship",))],
         [("may", "f1"), ("may", "f2"), ("may", "f3"), ("must", "du1"), ("must", "du2"), ("must", "du3"), ("must", "du4"),
          ("may", "s1"), ("may", "s2")]),
]

Y, N, O = {"answer": "yes"}, {"answer": "no"}, "OPEN"
EXPECTED = {
    "S1-1": Y, "S1-2": N, "S1-3": N, "S1-4": Y, "S1-5": N,
    "S2-1": Y, "S2-2": N, "S2-3": N, "S2-4": Y, "S2-5": O, "S2-6": O,
    "S3-1": N, "S3-2": Y, "S3-3": N, "S3-4": N, "S3-5": Y, "S3-6": Y, "S3-7": O, "S3-8": N, "S3-9": Y, "S3-10": N,
    "S3-11": Y,
    "S4-1": {"answer": "DATE", "value": "2028-03-30"}, "S4-2": Y, "S4-3": N, "S4-4": N, "S4-5": O, "S4-6": O, "S4-7": N,
    "S4-8": {"answer": "DATE", "value": "2027-03-02"},
    "S5-1": N, "S5-2": Y, "S5-3": O, "S5-4": Y, "S5-5": Y, "S5-6": N, "S5-7": N, "S5-8": Y,
    "S6-1": Y, "S6-2": O, "S6-3": N, "S6-4": Y,
    "S7-1": N, "S7-2": N, "S7-3": Y, "S7-4": Y, "S7-5": Y, "S7-6": N, "S7-7": Y, "S7-8": N, "S7-9": O,
}

PROBES, PROBE_QIDS, UNSUPPORTED = {}, {}, {}
