"""Write AP-6's fixture documents into the directory named (docs/act-phrases/ap-6/fixtures/): per fixture, the binary
route (today's language: the act's last bound slot dropped) and route (a) (the act reified as an event sort with one role
predicate per bound non-subject slot). AST form, ve-document@1. A ve-document@1 environment carries no `events` block
today, so the reified documents declare the event sort and its roles as plain vocabulary (REPORT.md, bar row 2).

    python3 docs/act-phrases/ap-6/fixtures/make.py docs/act-phrases/ap-6/fixtures
"""
import json, sys
from pathlib import Path

OUT = Path(sys.argv[1])
V = lambda i: ["var", i]
C = lambda c: ["const", c]
def un(p, t): return ["unary", p, t]
def bi(p, a, b): return ["binary", p, a, b]
def AND(a, b): return ["and", a, b]
def EX(s, b): return ["exists", s, b]
def NOT(a): return ["not", a]

def doc(name, sorts, preds, consts, norms, facts, claim, events=None, roles=None):
    if roles:  # route (a) also with its hypothesis stated as premises
        _doc(name.replace(".reified", ".reified-otp"), sorts, preds, consts, norms,
             facts + one_event_per_tuple(events[0], roles), claim, events)
    _doc(name, sorts, preds, consts, norms, facts, claim, events)

def _doc(name, sorts, preds, consts, norms, facts, claim, events=None):
    profiles = ["documents@1", "norm-defaults@0", "norms@0", "relational-fol@0"]
    env = {"language": "ve.core@0.2", "profiles": profiles, "spec_revision": "ve-v0.2-expand2-2026-09-25",
           "vocabulary": {"sorts": {s: {"description": s} for s in sorts}, "predicates": preds,
                          "constants": {c: {"sort": s, "description": c} for c, s in consts.items()}}}
    if events:
        env["vocabulary"]["sorts"]["day"] = {"description": "a day"}
        env["vocabulary"]["predicates"]["before"] = {"arguments": ["day", "day"], "description": "before",
                                                     "verbalisation": "{0} is before {1}"}
        for e in events:
            env["vocabulary"]["predicates"][e + "_on"] = {"arguments": [e, "day"], "description": f"{{0}} happens on {{1}}",
                                                         "verbalisation": "{0} happens on {1}"}
    units, lines, at = [], [], 0
    def add(kind, content, text, support="assumption"):
        nonlocal at
        b = (text + "\n").encode()
        units.append({"id": f"u{len(units) + 1}", "span": [at, at + len(b)], "kind": kind, "meaning": "specified",
                      "support": support, "content": content})
        lines.append(text); at += len(b)
    for n in norms:
        add("norm", {"norm": {"name": n["name"], "predicate": n["pred"], "sign": n["sign"], "guard": n["guard"],
                              "unless": [], "over": []}},
            n["text"])
    for ast, text in facts:
        add("asserted", {"ast": ast}, text)
    add("asserted", {"ast": claim[0]}, claim[1])
    d = {"format": "ve-document@1", "environment": env, "units": units, "reading_sets": [],
         "graph": {"root": "claim", "nodes": [{"name": "claim", "ast": claim[0], "unit": units[-1]["id"]}]}}
    (OUT / f"{name}.ve.md").write_text("---\n" + json.dumps(d, indent=1) + "\n---\n" + "\n".join(lines) + "\n")

def ALL(s, b): return ["forall", s, b]
def IMP(a, b): return ["implies", a, b]
def EQ(a, b): return ["eq", a, b]

def one_event_per_tuple(ev, roles):
    """`OneEventPerTuple` (route (a)'s hypothesis) as premises, for an act with two slots `roles = [(sort, role)] * 2`:
    each role functional and total on the event sort, an event for every filler tuple, and at most one."""
    (s1, r1), (s2, r2) = roles
    out = []
    for s, r in roles:
        out.append((ALL(ev, ALL(s, ALL(s, IMP(AND(bi(r, V(2), V(1)), bi(r, V(2), V(0))), EQ(V(1), V(0)))))),
                    f"Each {ev} has at most one {r} filler."))
        out.append((ALL(ev, EX(s, bi(r, V(1), V(0)))), f"Each {ev} has a {r} filler."))
    out.append((ALL(s1, ALL(s2, EX(ev, AND(bi(r1, V(0), V(2)), bi(r2, V(0), V(1)))))),
                f"Every pair of fillers has a {ev}."))
    out.append((ALL(ev, ALL(ev, ALL(s1, ALL(s2, IMP(AND(AND(bi(r1, V(3), V(1)), bi(r2, V(3), V(0))),
                                                     AND(bi(r1, V(2), V(1)), bi(r2, V(2), V(0)))), EQ(V(3), V(2))))))),
                f"Every pair of fillers has at most one {ev}."))
    return out

def reg(args, act, role="permission", default="allow"):
    return {"arguments": args, "description": act, "regulated": {"role": role, "default": default, "act": act}}
def base(args, desc):
    return {"arguments": args, "description": desc, "verbalisation": desc}

# u019: no distinction by a bearer against a person on a ground (UDHR Article 2)
doc("u019.binary", ["bearer", "person", "ground"],
    {"distinguish_permitted": reg(["bearer", "person"], "{0} make a distinction against {1}"),
     "listed_ground": base(["ground"], "{0} is a listed ground")},
    {"state": "bearer", "ann": "person", "race": "ground"},
    [{"name": "r019", "pred": "distinguish_permitted", "sign": False, "guard": ["top"],
      "text": "No bearer may make a distinction against a person."}],
    [(un("listed_ground", C("race")), "Race is a listed ground.")],
    (NOT(bi("distinguish_permitted", C("state"), C("ann"))), "The state may not make a distinction against Ann."))
doc("u019.reified", ["bearer", "person", "ground", "distinction"],
    {"distinguish_permitted": reg(["bearer", "distinction"], "{0} make {1}"),
     "listed_ground": base(["ground"], "{0} is a listed ground"),
     "distinction_against": base(["distinction", "person"], "{0} is against {1}"),
     "distinction_ground": base(["distinction", "ground"], "{0} is on the ground of {1}")},
    {"state": "bearer", "ann": "person", "race": "ground", "d1": "distinction"},
    [{"name": "r019", "pred": "distinguish_permitted", "sign": False,
      "guard": EX("person", AND(bi("distinction_against", V(1), V(0)),
                                EX("ground", AND(bi("distinction_ground", V(2), V(0)), un("listed_ground", V(0)))))),
      "text": "No bearer may make a distinction against a person on a listed ground."}],
    [(un("listed_ground", C("race")), "Race is a listed ground."),
     (bi("distinction_against", C("d1"), C("ann")), "Distinction d1 is against Ann."),
     (bi("distinction_ground", C("d1"), C("race")), "Distinction d1 is on the ground of race.")],
    (NOT(bi("distinguish_permitted", C("state"), C("d1"))), "The state may not make distinction d1."),
    events=["distinction"], roles=[("person", "distinction_against"), ("ground", "distinction_ground")])

# u057 (reworded): the right to found a family and to marry, without any limitation due to a ground
fam = {"found_a_family_entitled": reg(["person"], "{0} found a family", "permission", "deny"),
       "marry_entitled": reg(["person"], "{0} marry", "permission", "deny"),
       "of_full_age": base(["person"], "{0} is of full age")}
fam_norms = [{"name": "r057-a1", "pred": "found_a_family_entitled", "sign": True, "guard": un("of_full_age", V(0)),
              "text": "Every person of full age has the right to found a family."},
             {"name": "r057-a2", "pred": "marry_entitled", "sign": True, "guard": un("of_full_age", V(0)),
              "text": "Every person of full age has the right to marry."}]
doc("u057.binary", ["bearer", "person", "ground"],
    {**fam, "limit_permitted": reg(["bearer", "person"], "{0} limit the right of {1} to marry"),
     "marriage_ground": base(["ground"], "{0} is race, nationality or religion")},
    {"state": "bearer", "ann": "person", "religion": "ground"},
    fam_norms + [{"name": "r057-l", "pred": "limit_permitted", "sign": False, "guard": un("of_full_age", V(0)),
                  "text": "No bearer may limit the right of a person of full age to marry."}],
    [(un("of_full_age", C("ann")), "Ann is of full age."),
     (un("marriage_ground", C("religion")), "Religion is such a ground.")],
    (AND(un("marry_entitled", C("ann")), NOT(bi("limit_permitted", C("state"), C("ann")))),
     "Ann has the right to marry and the state may not limit it."))
doc("u057.reified", ["bearer", "person", "ground", "limitation"],
    {**fam, "limit_permitted": reg(["bearer", "limitation"], "{0} make {1}"),
     "marriage_ground": base(["ground"], "{0} is race, nationality or religion"),
     "limitation_of": base(["limitation", "person"], "{0} limits the right of {1} to marry"),
     "limitation_ground": base(["limitation", "ground"], "{0} is due to {1}")},
    {"state": "bearer", "ann": "person", "religion": "ground", "l1": "limitation"},
    fam_norms + [{"name": "r057-l", "pred": "limit_permitted", "sign": False,
                  "guard": EX("person", AND(bi("limitation_of", V(1), V(0)),
                                            EX("ground", AND(bi("limitation_ground", V(2), V(0)),
                                                             AND(un("of_full_age", V(1)), un("marriage_ground", V(0))))))),
                  "text": "No bearer may limit the right of a person of full age to marry due to such a ground."}],
    [(un("of_full_age", C("ann")), "Ann is of full age."),
     (un("marriage_ground", C("religion")), "Religion is such a ground."),
     (bi("limitation_of", C("l1"), C("ann")), "Limitation l1 limits the right of Ann to marry."),
     (bi("limitation_ground", C("l1"), C("religion")), "Limitation l1 is due to religion.")],
    (AND(un("marry_entitled", C("ann")), NOT(bi("limit_permitted", C("state"), C("l1")))),
     "Ann has the right to marry and the state may not make limitation l1."),
    events=["limitation"], roles=[("person", "limitation_of"), ("ground", "limitation_ground")])

# rights.md (mu): publish_about(person, item, person); liberty of right 19, claim of right 12 as its exception
doc("mu.binary", ["person", "item"],
    {"publish_about_permitted": reg(["person", "item"], "{0} publish {1}", "permission", "deny"),
     "attacks_honour_of_someone": base(["item"], "{0} attacks the honour of a person")},
    {"bob": "person", "leak": "item"},
    [{"name": "r19", "pred": "publish_about_permitted", "sign": True, "guard": NOT(un("attacks_honour_of_someone", V(0))),
      "text": "Every person may publish each item, unless that item attacks the honour of a person."}],
    [(un("attacks_honour_of_someone", C("leak")), "The leak attacks the honour of a person.")],
    (NOT(bi("publish_about_permitted", C("bob"), C("leak"))), "Bob may not publish the leak."))
doc("mu.reified", ["person", "item", "publication"],
    {"publish_about_permitted": reg(["person", "publication"], "{0} make {1}", "permission", "deny"),
     "attacks_honour": base(["item", "person"], "{0} attacks the honour of {1}"),
     "publication_of": base(["publication", "item"], "{0} publishes {1}"),
     "publication_about": base(["publication", "person"], "{0} is about {1}")},
    {"bob": "person", "carol": "person", "leak": "item", "p1": "publication"},
    [{"name": "r19", "pred": "publish_about_permitted", "sign": True,
      "guard": EX("item", AND(bi("publication_of", V(1), V(0)),
                              EX("person", AND(bi("publication_about", V(2), V(0)),
                                               NOT(bi("attacks_honour", V(1), V(0))))))),
      "text": "Every person may publish each item about each person, unless that item attacks the honour of that person."}],
    [(bi("attacks_honour", C("leak"), C("carol")), "The leak attacks the honour of Carol."),
     (bi("publication_of", C("p1"), C("leak")), "Publication p1 publishes the leak."),
     (bi("publication_about", C("p1"), C("carol")), "Publication p1 is about Carol.")],
    (NOT(bi("publish_about_permitted", C("bob"), C("p1"))), "Bob may not make publication p1."),
    events=["publication"], roles=[("item", "publication_of"), ("person", "publication_about")])
