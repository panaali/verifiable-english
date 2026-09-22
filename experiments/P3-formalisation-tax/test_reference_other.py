"""Unit tests for reference_rbac.py and reference_alloy.py, plus a dump of every k*/w*/l* answer.

Run:  python3 test_reference_other.py
"""

from __future__ import annotations

import glob
import json
import os

import reference_alloy as A
import reference_rbac as R

HERE = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------------------------------------
# Kubernetes RBAC
# --------------------------------------------------------------------------------------


def req(**kw):
    base = dict(user="u", groups=[], verb="get", apiGroup="", resource="pods", subresource="",
                namespace="ns", name="")
    base.update(kw)
    return base


def role(ns, name, rules):
    return {"kind": "Role", "metadata": {"namespace": ns, "name": name}, "rules": rules}


def crole(name, rules=None, labels=None, agg=None):
    o = {"kind": "ClusterRole", "metadata": {"name": name}}
    if labels:
        o["metadata"]["labels"] = labels
    if rules is not None:
        o["rules"] = rules
    if agg is not None:
        o["aggregationRule"] = {"clusterRoleSelectors": agg}
    return o


def rb(ns, subjects, kind, name):
    return {"kind": "RoleBinding", "metadata": {"name": "b", "namespace": ns}, "subjects": subjects,
            "roleRef": {"kind": kind, "name": name}}


def crb(subjects, name):
    return {"kind": "ClusterRoleBinding", "metadata": {"name": "cb"}, "subjects": subjects,
            "roleRef": {"kind": "ClusterRole", "name": name}}


U = [{"kind": "User", "name": "u"}]
RULE = {"apiGroups": [""], "resources": ["pods"], "verbs": ["get"]}


def test_k8s():
    k = R.k8s_authorize
    # RoleBinding -> Role, namespace scoping
    objs = [role("ns", "r", [RULE]), rb("ns", U, "Role", "r")]
    assert k(objs, req())
    assert not k(objs, req(namespace="other"))
    assert not k(objs, req(namespace=""))  # cluster-scoped request never uses RoleBindings
    # Role must live in the binding's namespace
    assert not k([role("x", "r", [RULE]), rb("ns", U, "Role", "r")], req())
    # RoleBinding -> ClusterRole grants only in binding namespace
    objs = [crole("cr", [RULE]), rb("ns", U, "ClusterRole", "cr")]
    assert k(objs, req()) and not k(objs, req(namespace="o")) and not k(objs, req(namespace=""))
    # ClusterRoleBinding applies everywhere incl. cluster scope
    objs = [crole("cr", [RULE]), crb(U, "cr")]
    assert k(objs, req()) and k(objs, req(namespace="")) and k(objs, req(namespace="o"))
    # CRB cannot reference a Role
    assert not k([role("ns", "r", [RULE]), {"kind": "ClusterRoleBinding", "metadata": {"name": "x"},
                  "subjects": U, "roleRef": {"kind": "Role", "name": "r"}}], req())
    # subjects
    g = [{"kind": "Group", "name": "devs"}]
    objs = [crole("cr", [RULE]), crb(g, "cr")]
    assert k(objs, req(groups=["devs"])) and not k(objs, req(user="devs"))
    sa = [{"kind": "ServiceAccount", "name": "bot", "namespace": "ns"}]
    objs = [crole("cr", [RULE]), crb(sa, "cr")]
    assert k(objs, req(user="system:serviceaccount:ns:bot"))
    assert not k(objs, req(user="bot"))
    sa_nons = [{"kind": "ServiceAccount", "name": "bot"}]
    assert k([crole("cr", [RULE]), rb("ns", sa_nons, "ClusterRole", "cr")],
             req(user="system:serviceaccount:ns:bot"))  # defaults to binding namespace
    assert not k([crole("cr", [RULE]), crb(sa_nons, "cr")], req(user="system:serviceaccount:ns:bot"))
    assert not k([crole("cr", [RULE]), crb(U, "cr")], req(user="v"))
    # verbs / apiGroups
    objs = lambda rule: [crole("cr", [rule]), crb(U, "cr")]  # noqa: E731
    assert not k(objs(RULE), req(verb="list"))
    assert k(objs(dict(RULE, verbs=["*"])), req(verb="delete"))
    assert not k(objs(RULE), req(apiGroup="apps"))
    assert k(objs(dict(RULE, apiGroups=["*"])), req(apiGroup="apps"))
    # resources and subresources
    assert not k(objs(RULE), req(subresource="log"))
    assert k(objs(dict(RULE, resources=["pods/log"])), req(subresource="log"))
    assert not k(objs(dict(RULE, resources=["pods/log"])), req())
    assert k(objs(dict(RULE, resources=["*"])), req(subresource="exec"))
    assert k(objs(dict(RULE, resources=["*"])), req(resource="nodes"))
    assert k(objs(dict(RULE, resources=["*/log"])), req(resource="x", subresource="log"))
    assert not k(objs(dict(RULE, resources=["*/log"])), req(resource="x", subresource="exec"))
    assert not k(objs(dict(RULE, resources=["*/log"])), req(resource="x"))
    assert not k(objs(dict(RULE, resources=["pods/*"])), req(subresource="log"))  # upstream: no res/*
    # resourceNames
    rn = dict(RULE, resourceNames=["a"])
    assert k(objs(rn), req(name="a")) and not k(objs(rn), req(name="b")) and not k(objs(rn), req(name=""))
    assert k(objs(dict(RULE, resourceNames=[])), req(name="z"))
    # aggregation: own rules replaced, any selector suffices, all labels of a selector needed
    objs = [
        crole("agg", rules=[dict(RULE, verbs=["delete"])], agg=[{"matchLabels": {"a": "1", "b": "2"}},
                                                                 {"matchLabels": {"c": "3"}}]),
        crole("p1", [RULE], labels={"a": "1", "b": "2"}),
        crole("p2", [dict(RULE, verbs=["list"])], labels={"a": "1"}),
        crole("p3", [dict(RULE, verbs=["watch"])], labels={"c": "3"}),
        crb(U, "agg"),
    ]
    assert k(objs, req(verb="get")) and k(objs, req(verb="watch"))
    assert not k(objs, req(verb="list")) and not k(objs, req(verb="delete"))
    # transitive aggregation, independent of object order
    for order in (1, -1):
        objs = [
            crole("top", agg=[{"matchLabels": {"to-top": "y"}}]),
            crole("mid", labels={"to-top": "y"}, agg=[{"matchLabels": {"to-mid": "y"}}]),
            crole("leaf", [RULE], labels={"to-mid": "y"}),
            crb(U, "top"),
        ][::order]
        assert k(objs, req())
    # self-selecting aggregated role does not loop
    objs = [crole("s", labels={"x": "1"}, agg=[{"matchLabels": {"x": "1"}}]), crb(U, "s")]
    assert not k(objs, req())
    # extra key 'synthetic' is ignored
    objs = [dict(crole("cr", [RULE]), synthetic=True), dict(crb(U, "cr"), synthetic=True)]
    assert k(objs, req())


# --------------------------------------------------------------------------------------
# AWS IAM
# --------------------------------------------------------------------------------------


def pol(*stmts):
    return {"Version": "2012-10-17", "Statement": list(stmts)}


def ireq(action, resource="*", **ctx):
    return {"action": action, "resource": resource, "context": ctx}


def test_iam():
    i = R.iam_authorize
    allow_all = {"Effect": "Allow", "Action": "*", "Resource": "*"}
    assert not i([], ireq("s3:GetObject"))  # implicit deny
    assert i([pol(allow_all)], ireq("s3:GetObject"))
    # explicit deny wins, across policies
    assert not i([pol(allow_all), pol({"Effect": "Deny", "Action": "s3:*", "Resource": "*"})],
                 ireq("s3:GetObject"))
    # action glob, case-insensitive, ? wildcard
    s = lambda a, r="*", **kw: pol(dict({"Effect": "Allow", "Action": a, "Resource": r}, **kw))  # noqa
    assert i([s("s3:Get*")], ireq("S3:GETOBJECT"))
    assert not i([s("s3:Get*")], ireq("s3:PutObject"))
    assert i([s("s3:Get?bject")], ireq("s3:GetObject"))
    assert not i([s("s3:*Object")], ireq("s3:GetObjectAcl"))
    assert i([s(["ec2:Run*", "s3:List*"])], ireq("s3:ListBucket"))
    # NotAction
    na = pol({"Effect": "Allow", "NotAction": ["iam:*"], "Resource": "*"})
    assert i([na], ireq("s3:GetObject")) and not i([na], ireq("iam:CreateUser"))
    # resource glob, case-sensitive
    assert i([s("s3:*", "arn:aws:s3:::b/*")], ireq("s3:GetObject", "arn:aws:s3:::b/x/y"))
    assert not i([s("s3:*", "arn:aws:s3:::b/*")], ireq("s3:GetObject", "arn:aws:s3:::b"))
    assert not i([s("s3:*", "arn:aws:s3:::B/*")], ireq("s3:GetObject", "arn:aws:s3:::b/x"))
    assert i([s("s3:*", "arn:aws:s3:::b?")], ireq("s3:GetObject", "arn:aws:s3:::bc"))
    # NotResource
    nr = pol({"Effect": "Allow", "Action": "*", "NotResource": "arn:aws:s3:::secret/*"})
    assert i([nr], ireq("s3:GetObject", "arn:aws:s3:::pub/x"))
    assert not i([nr], ireq("s3:GetObject", "arn:aws:s3:::secret/x"))
    # policy variables
    pv = s("iam:*", "arn:aws:iam::*:user/${aws:username}")
    assert i([pv], ireq("iam:GetUser", "arn:aws:iam::1:user/al", **{"aws:username": "al"}))
    assert not i([pv], ireq("iam:GetUser", "arn:aws:iam::1:user/bo", **{"aws:username": "al"}))
    assert not i([pv], ireq("iam:GetUser", "arn:aws:iam::1:user/al"))  # missing variable
    assert not i([pv], ireq("iam:GetUser", "arn:aws:iam::1:user/${aws:username}"))
    assert not i([s("iam:*", "arn:x/${aws:username}")],
                 ireq("iam:GetUser", "arn:x/aXb", **{"aws:username": "a*b"}))  # substituted literally
    # conditions
    c = lambda cond: s("*", "*", Condition=cond)  # noqa: E731
    assert i([c({"StringEquals": {"k": ["a", "b"]}})], ireq("x:Y", k="b"))
    assert not i([c({"StringEquals": {"k": "a"}})], ireq("x:Y", k="A"))
    assert not i([c({"StringEquals": {"k": "a"}})], ireq("x:Y"))  # missing -> false
    assert i([c({"StringNotEquals": {"k": ["a", "b"]}})], ireq("x:Y", k="c"))
    assert not i([c({"StringNotEquals": {"k": ["a", "b"]}})], ireq("x:Y", k="a"))
    assert i([c({"StringNotEquals": {"k": "a"}})], ireq("x:Y"))  # negated, missing -> true
    assert i([c({"StringLike": {"k": "a*"}})], ireq("x:Y", k="abc"))
    assert not i([c({"StringLike": {"k": "a*"}})], ireq("x:Y", k="Abc"))
    assert not i([c({"StringLike": {"k": "a*"}})], ireq("x:Y"))
    assert i([c({"StringNotLike": {"k": "a*"}})], ireq("x:Y"))
    assert i([c({"Bool": {"m": "true"}})], ireq("x:Y", m="TRUE"))
    assert not i([c({"Bool": {"m": "true"}})], ireq("x:Y", m="false"))
    assert not i([c({"Bool": {"m": "true"}})], ireq("x:Y"))
    assert i([c({"BoolIfExists": {"m": "false"}})], ireq("x:Y"))
    assert i([c({"BoolIfExists": {"m": "false"}})], ireq("x:Y", m="false"))
    assert not i([c({"BoolIfExists": {"m": "false"}})], ireq("x:Y", m="true"))
    assert i([c({"StringEqualsIfExists": {"k": "a"}})], ireq("x:Y"))
    assert not i([c({"StringEqualsIfExists": {"k": "a"}})], ireq("x:Y", k="b"))
    # all operators and keys are ANDed
    both = c({"StringEquals": {"k": "a", "j": "b"}, "Bool": {"m": "true"}})
    assert i([both], ireq("x:Y", k="a", j="b", m="true"))
    assert not i([both], ireq("x:Y", k="a", j="b", m="false"))
    assert not i([both], ireq("x:Y", k="a", j="c", m="true"))
    # deny with condition
    d = pol(allow_all, {"Effect": "Deny", "Action": "*", "Resource": "*",
                        "Condition": {"StringNotEquals": {"r": "eu"}}})
    assert i([d], ireq("x:Y", r="eu")) and not i([d], ireq("x:Y", r="us")) and not i([d], ireq("x:Y"))


# --------------------------------------------------------------------------------------
# Alloy
# --------------------------------------------------------------------------------------

MINI = r"""
module m -- header
open util/relation as rel
/* block
   comment */
sig N { e: set N }
one sig Root extends N {}
fun succ [n: N] : set N { n.e }          // dot call target
fun two [a, b: N] : set N { a + b }
pred edge [a: N, b: N] { b in a.e }
pred loopFree { no n: N | n in n.^e }
fact named { some N }
fact { all n: N | n !in n.e }
assert A1 { all n: N | n not in n.e }
run loopFree for 3
check A1 for 3 expect 0
"""


def inst(sigs, fields, bindings=None):
    return {"sigs": sigs, "fields": fields, "bindings": bindings or {}}


def F(text, sigs, fields, **b):
    return A.evaluate({"source.als": MINI}, {"kind": "formula", "text": text}, inst(sigs, fields, b))


def test_alloy_expressions():
    S = {"N": ["a", "b", "c"], "Root": ["a"]}
    E = {"e": [["a", "b"], ["b", "c"]]}
    assert F("a.e = b", S, E, a="a", b="b")
    assert F("a.^e = b + c", S, E, a="a", b="b", c="c")
    assert F("a.*e = a + b + c", S, E, a="a", b="b", c="c")
    assert F("c.*e = c", S, E, c="c")           # * includes iden over univ
    assert F("no c.^e", S, E, c="c")
    assert F("~e = b->a + c->b", S, E, a="a", b="b", c="c")
    assert F("e[a] = b", S, E, a="a", b="b")     # box join
    assert F("(e + ~e)[b] = a + c", S, E, a="a", b="b", c="c")
    assert F("a.e.e = c", S, E, a="a", c="c")
    assert F("a.succ = b", S, E, a="a", b="b")    # dot-call
    assert F("succ[a] = b", S, E, a="a", b="b")
    assert F("a.two[c] = a + c", S, E, a="a", c="c")   # x.f[y] == f[x,y]
    assert F("a.edge[b] && !a.edge[c] && edge[b, c]", S, E, a="a", b="b", c="c")
    assert F("#N = 3 && #e = 2", S, E)
    assert F("N - Root = b + c", S, E, b="b", c="c")
    assert F("a->b in e && a->c !in e && a->c not in e", S, E, a="a", b="b", c="c")
    assert F("a != b and not a = b", S, E, a="a", b="b")
    assert F("(N & Root) = a", S, E, a="a")
    assert F("iden & e = none", S, E)
    assert F("some e && one Root && lone Root && no none", S, E)
    assert F("a <: e = a->b && e :> c = b->c", S, E, a="a", b="b", c="c")
    assert F("e ++ a->c = a->c + b->c", S, E, a="a", b="b", c="c")
    assert F("univ = N", S, E)
    # precedence: multiplicity covers the whole & expression; && binds looser than one
    assert F("some a.e & N", S, E, a="a")
    assert F("one a.e && a in N", S, E, a="a")
    # quantifiers
    assert F("all x: N | x in N", S, E)
    assert F("some x: N | no x.e", S, E)
    assert F("one x: N | no x.e", S, E)
    assert F("lone x: N | no x.e", S, E)
    assert F("no x: N | x in x.e", S, E)
    assert F("all x, y: N | x->y in e => y !in Root", S, E)
    assert F("some disj x, y: N | x->y in e", S, E)
    assert not F("some disj x, y: Root | x = y", S, E)
    assert F("all x: N, y: x.e | x->y in e", S, E)
    assert F("one x: N, y: N | x->y in e && no y.e", S, E)     # combination count
    assert not F("one x: N, y: N | x->y in e", S, E)
    # implication / else / iff / blocks / let
    assert F("a in Root => a.e = b else no a.e", S, E, a="a", b="b")
    assert F("c in Root => some c.e else no c.e", S, E, c="c")
    assert F("a in Root implies some a.e", S, E, a="a")
    assert F("(a in Root) <=> (some a.e)", S, E, a="a")
    assert F("a in Root iff some b.e", S, E, a="a", b="b")
    assert F("{ a in N  b in N }", S, E, a="a", b="b")
    assert not F("{ a in N  a in b }", S, E, a="a", b="b")
    assert F("let x = a.e | x = b", S, E, a="a", b="b")
    assert F("let x = a.e, y = x.e | y = c", S, E, a="a", c="c")
    assert F("a in Root || c in Root", S, E, a="a", c="c")
    assert F("{x: N | no x.e} = c", S, E, c="c")
    # binding a relation by field name
    assert A.evaluate({"source.als": MINI}, {"kind": "formula", "text": "some r"}, inst(S, E, {"r": "e"}))


def test_alloy_paragraphs():
    S = {"N": ["a", "b"], "Root": ["a"]}
    src = {"source.als": MINI}
    good = inst(S, {"e": [["a", "b"]]})
    bad = inst(S, {"e": [["a", "a"]]})
    assert A.evaluate(src, {"kind": "fact", "name": "named"}, good)
    assert A.evaluate(src, {"kind": "fact", "index": 1}, good)
    assert not A.evaluate(src, {"kind": "fact", "index": 1}, bad)
    assert A.evaluate(src, {"kind": "assert", "name": "A1"}, good)
    assert not A.evaluate(src, {"kind": "assert", "name": "A1"}, bad)
    assert A.evaluate(src, {"kind": "pred", "name": "loopFree", "args": []}, good)
    assert not A.evaluate(src, {"kind": "pred", "name": "loopFree", "args": []}, bad)
    assert A.evaluate(src, {"kind": "pred", "name": "edge", "args": ["x", "y"]},
                      inst(S, {"e": [["a", "b"]]}, {"x": "a", "y": "b"}))
    # primed identifiers, comments with '--' and '//' inside paragraphs
    src2 = {"source.als": 'sig S { f: set S }\npred p[s, s" : S] { -- c\n s".f = s.f // c\n }'}
    assert A.evaluate(src2, {"kind": "pred", "name": "p", "args": ["s", 's"']},
                      inst({"S": ["x", "y"]}, {"f": [["x", "y"], ["y", "y"]]}, {"s": "x", 's"': "y"}))


GRANDPA_NOACYC = """
abstract sig Person { father: lone Man, mother: lone Woman }
sig Man extends Person { wife: lone Woman }
sig Woman extends Person { husband: lone Man }
fact { wife = ~husband }
fun grandpas [p: Person] : set Person { p.(mother+father).father }
assert NoSelfGrandpa { no p: Person | p in p.grandpas }
assert NoSelfFather { no m: Man | m = m.father }
"""


def test_alloy_check():
    chk = lambda src, name, k: A.evaluate({"source.als": src}, {"kind": "check", "name": name, "scope": k}, None)  # noqa
    # without the acyclicity fact both assertions have counterexamples (e.g. m.father = m)
    assert not chk(GRANDPA_NOACYC, "NoSelfGrandpa", 1)
    assert not chk(GRANDPA_NOACYC, "NoSelfFather", 2)
    gp = open(os.path.join(HERE, "items/l03_grandpa1_noselfgrandpa/source.als")).read()
    assert chk(gp, "NoSelfFather", 3)
    # one sig, abstract partition and signature facts
    src = """
    abstract sig T {}
    one sig X extends T {}
    sig Y extends T { g: lone T } { g != this }
    assert A { no y: Y | y.g = y }
    assert B { lone Y }
    assert C { some X && (all t: T | t in X + Y) }
    assert D { no Y.g }
    """
    assert chk(src, "A", 3)        # holds only thanks to the signature fact
    assert not chk(src, "B", 3)
    assert chk(src, "C", 3)
    assert not chk(src, "D", 2)
    # without the sig fact A fails
    assert not chk(src.replace("{ g != this }", ""), "A", 2)


# --------------------------------------------------------------------------------------
# Item dump
# --------------------------------------------------------------------------------------


def load(item_dir):
    with open(os.path.join(item_dir, "item.json")) as f:
        return json.load(f)


def item_answers():
    out = {}
    for d in sorted(glob.glob(os.path.join(HERE, "items", "[kwl]0*"))):
        it = load(d)
        fam = it["family"]
        ans = []
        for q in it["questions"]:
            if fam == "k8s":
                a = R.k8s_authorize(it["world"]["objects"], q["request"])
            elif fam == "iam":
                a = R.iam_authorize(it["world"]["policies"], q["request"])
            else:
                srcs = {}
                for n in it["source_files"]:
                    with open(os.path.join(d, n)) as fh:
                        srcs[n] = fh.read()
                a = A.evaluate(srcs, q["target"], q["instance"])
            ans.append((q["description"], a))
        out[it["id"]] = ans
    return out


# Hand-checked expectations (reasoned from the docs / model text; see comments in report)
EXPECTED = {
    "k01_pod_reader": "TTFFFFF",
    "k02_secret_reader_rolebinding": "TFFFF",
    "k03_secret_reader_global": "TTFFF",
    "k04_monitoring_aggregation": "TTFFTF",
    "k05_crontab_default_roles": "TTTTFFF",
    "k06_configmap_updater": "TTFFFF",
    "k07_subresource_wildcard": "TTFTFF",
    "w01_s3_rw_bucket": "TTTFFFFT",
    "w02_deny_requested_region": "TFTFTFTF",
    "w03_mfa_selfmanage": "TTFFTFTFT",
    "l01_genealogy_biology": "TFFTT",
    "l02_grandpa1_fact": "TFFFT",
    "l03_grandpa1_noselfgrandpa": "FTT",
    "l04_graph_weakly_connected": "TFTFT",
    "l05_graph_ring": "TFFTF",
    "l06_graph_tree": "TFFFTT",
    "l07_marksweep_mark": "TFFTF",
    "l08_addressbook_lookup": "TTTFF",
}


def test_items():
    got = item_answers()
    for iid, ans in got.items():
        s = "".join("T" if a else "F" for _, a in ans)
        print(f"{iid:34s} {s}   " + ", ".join(f"{d}={'T' if a else 'F'}" for d, a in ans))
        assert s == EXPECTED[iid], (iid, s, EXPECTED[iid])


if __name__ == "__main__":
    test_k8s()
    test_iam()
    test_alloy_expressions()
    test_alloy_paragraphs()
    test_alloy_check()
    print("unit tests: OK")
    test_items()
    print("item answers match hand-checked expectations")
