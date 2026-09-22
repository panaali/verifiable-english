"""Write naive-author variants (items/<id>/naive_variants.json): realistic
mistranslations a less careful author would plausibly produce. naive.py checks
whether the differential test catches each one."""
import json

from author_cedar import AND, OR, NOT, EX, ALL, IMP, EQ, IN, INANY

p, a, r, c = "@principal", "@action", "@resource", "@context"
V = {}
V["c04_cit_2c"] = [("action-in-as-equality", "Cedar `action in [A,B,C]` translated as equality (ignores the action hierarchy).",
    AND(EQ(p, "@alice"), OR(EQ(a, "@view"), EQ(a, "@edit"), EQ(a, "@comment")), IN(r, "@jane_vacation")))]
V["c02_cit_2a"] = [("in-as-direct-edge", "`principal in UserGroup` as a single parent edge (no transitive membership).",
    AND(f"{p} parent @jane_friends", EQ(a, "@view"), EQ(r, "@photo94")))]
V["c11_cit_4f"] = [("ignore-error-semantics", "`A || B` as plain disjunction; an erroring left operand should skip the policy.",
    OR(EX("entity", "a", AND(f"{r} ea_account a", f"a ea_owner {p}")), f"{r} es_admins {p}"))]


def document_cloud_naive():
    np_ = NOT(f"{r} is bt_isprivate")
    owner_is_p = f"{r} ea_owner {p}"
    pols = [AND(EQ(a, "@create_document"), EQ(r, "@drive")),
            AND(EQ(a, "@view_document"), owner_is_p),
            AND(EQ(a, "@view_document"), EX("entity", "acl", AND(f"{r} ea_viewacl acl", IN(p, "acl"))), np_),
            AND(EQ(p, "@public"), EQ(a, "@view_document"), OR(f"{r} sa_publicaccess @s_view", f"{r} sa_publicaccess @s_edit"), np_),
            AND(EQ(a, "@modify_document"), owner_is_p),
            AND(EQ(a, "@modify_document"), EX("entity", "acl", AND(f"{r} ea_modifyacl acl", IN(p, "acl"))), np_),
            AND(INANY(a, "@edit_is_private", "@add_to_share_acl", "@edit_public_access"), owner_is_p),
            AND(INANY(a, "@add_to_share_acl", "@edit_public_access"), EX("entity", "acl", AND(f"{r} ea_manageacl acl", IN(p, "acl")))),
            AND(EQ(a, "@create_group"), EQ(r, "@drive")),
            AND(INANY(a, "@modify_group", "@delete_group"), owner_is_p)]
    f1 = AND(INANY(a, "@view_document", "@modify_document", "@edit_is_private", "@add_to_share_acl", "@edit_public_access", "@delete_document"),
             f"{p} is has_blocked", EX("entity", "o", AND(f"{r} ea_owner o", OR(f"o es_blocked {p}", f"{p} es_blocked o"))))
    f2 = NOT(f"{c} is bt_is_authenticated")
    f3 = AND(EX("entity", "o", AND(f"{r} ea_owner o", NOT(EQ(p, "o")))), f"{r} is bt_isprivate")
    return AND(OR(*pols), NOT(OR(f1, f2, f3)))


V["c13_document_cloud"] = [("naive-unless-and-negation", "`unless {isPrivate}` as `not (isPrivate = true)`, `!context.is_authenticated` as `not (is_authenticated = true)`, and no has-blocked guard on the owner: Cedar skips a policy whose condition errors on a missing attribute.",
    document_cloud_naive())]

job = lambda x, j: f"{x} ea_job @job_{j}"


def in_set(attr):
    return EX("entity", "m", AND(f"{r} es_{attr} m", IN(p, "m")))


same_cust = lambda t: EX("value", "v", AND(f"{p} sa_customerid v", f"{t} sa_customerid v"))
_permits = [AND(IN(a, "@external_prez_view"), in_set("viewers")),
            AND(IN(a, "@internal_prez_view"), job(p, "internal"), in_set("viewers")),
            AND(IN(a, "@prez_edit"), OR(f"{r} ea_owner {p}", in_set("editors"))),
            AND(IN(a, "@market_template_view"), in_set("viewermarkets")),
            AND(IN(a, "@internal_template_view"), job(p, "internal"), in_set("viewers")),
            AND(IN(a, "@template_edit"), OR(f"{r} ea_owner {p}", in_set("editors"), in_set("editormarkets")))]
_forbids = [AND(EQ(a, "@grant_view_prez"), NOT(EX("entity", "t", AND(f"{c} ea_target t", OR(NOT(job("t", "customer")), AND(job(p, "distributor"), same_cust("t"))))))),
            AND(EQ(a, "@grant_edit_prez"), NOT(EX("entity", "t", AND(f"{c} ea_target t", job("t", "internal"))))),
            AND(EQ(a, "@grant_view_template"), EX("entity", "t", AND(f"{c} ea_targetuser t", job("t", "customer"), OR(NOT(job(p, "distributor")), NOT(same_cust("t")))))),
            AND(EQ(a, "@grant_edit_template"), EX("entity", "t", AND(f"{c} ea_targetuser t", NOT(job("t", "internal")))))]
V["c17_sales_static"] = [("ignore-error-semantics", "Conditions translated as plain Boolean logic; Cedar skips a policy whose condition errors (missing context.target, job, owner).",
    AND(OR(*_permits), NOT(OR(*_forbids))))]

S = "str"
subject = OR("b subject_user @user", EX(S, "g", AND("b subject_group g", "g is req_group")))
resolves = OR(AND("b is ref_clusterrole", "x is is_clusterrole", EX(S, "n", AND("b ref_name n", "x role_name n"))),
              AND("b is ref_role", "x is is_role", EX(S, "n", AND("b ref_name n", "x role_name n")),
                  EX(S, "ns", AND("b binding_ns ns", "x role_ns ns"))))
agg = "rtc[role s, t | (" + AND("s is has_aggregation", "t is is_clusterrole",
       EX("sel", "q", AND("s role_selector q", ALL(S, "l", IMP("q sel_label l", "t role_label l"))))) + ")](x, y)"
good_applies = OR("b is is_clusterrolebinding", AND("b is is_rolebinding", "b binding_ns @namespace"))


def rule_ok(star=True):
    st = (lambda f, v: OR(f"u {f} {v}", f"u {f} @star")) if star else (lambda f, v: f"u {f} {v}")
    return AND(st("rule_verb", "@verb"), st("rule_group", "@apigroup"), st("rule_resource", "@path"),
               OR(NOT(EX(S, "k", "u rule_resname k")), "u rule_resname @name"))


def k8s(applies, reach, ok):
    return EX("binding", "b", AND(subject, applies, EX("role", "x", AND(resolves, EX("role", "y", AND(
        reach, NOT("y is has_aggregation"), EX("rule", "u", AND("y role_rule u", ok))))))))


one_level = OR(EQ("x", "y"), AND("x is has_aggregation", "y is is_clusterrole",
               EX("sel", "q", AND("x role_selector q", ALL(S, "l", IMP("q sel_label l", "y role_label l"))))))
V["k02_secret_reader_rolebinding"] = [("rolebinding-namespace-ignored", "A RoleBinding treated as granting in every namespace.",
                                       k8s(OR("b is is_clusterrolebinding", "b is is_rolebinding"), agg, rule_ok()))]
V["k05_crontab_default_roles"] = [("aggregation-one-level", "Aggregation followed one level only (no transitive closure).",
                                   k8s(good_applies, one_level, rule_ok()))]
V["k07_subresource_wildcard"] = [("wildcard-ignored", "The \"*\" wildcard treated as a literal string.", k8s(good_applies, agg, rule_ok(False)))]

T, C = "stmt", "cond"
act = OR(AND("t is uses_action", EX(S, "p", AND("t action_pat p", "p is action_glob"))),
         AND("t is uses_notaction", NOT(EX(S, "p", AND("t action_pat p", "p is action_glob")))))
res = OR(AND("t is uses_resource", EX(S, "p", AND("t resource_pat p", "p is resource_glob"))),
         AND("t is uses_notresource", NOT(EX(S, "p", AND("t resource_pat p", "p is resource_glob")))))
has_key = EX(S, "k", EX(S, "v", AND("c cond_key k", "k ctx v")))
eq_val = EX(S, "k", EX(S, "v", AND("c cond_key k", "k ctx v", "c cond_value v")))


def iam(neq, bie):
    holds = OR(AND("c cond_op @op_string_equals", eq_val), AND("c cond_op @op_string_not_equals", neq),
               AND("c cond_op @op_bool", eq_val), AND("c cond_op @op_bool_if_exists", bie))
    m = AND(act, res, ALL(C, "c", IMP("t stmt_cond c", holds)))
    return AND(NOT(EX(T, "t", AND("t is deny_stmt", m))), EX(T, "t", AND("t is allow_stmt", m)))


V["w02_deny_requested_region"] = [("negated-operator-missing-key", "StringNotEquals with the key absent treated as not matching (AWS: it matches).",
                                   iam(AND(has_key, NOT(eq_val)), OR(NOT(has_key), eq_val)))]
V["w03_mfa_selfmanage"] = [("ifexists-ignored", "BoolIfExists treated as Bool (missing key -> false).", iam(NOT(eq_val), eq_val))]

mf = "tc[atom a, b | ((a f_mother b) or (a f_father b))](p, p)"
V["l02_grandpa1_fact"] = [("one-direction-equality", "`wife = ~husband` as the inclusion wife in ~husband only.",
    AND(NOT(EX("atom", "p", AND("p is sig_person", mf))), ALL("atom", "x", ALL("atom", "y", IMP("x f_wife y", "y f_husband x")))))]
V["l05_graph_ring"] = [("closure-direction-swapped", "rootedAt as `root in node.*r` instead of `node in root.*r`.",
    ALL("atom", "n", IMP("n is sig_node", AND(EX("atom", "y", AND("n f_edges y", ALL("atom", "z", IMP("n f_edges z", EQ("z", "y"))))),
                                              ALL("atom", "m", IMP("m is sig_node", "rtc[f_edges](m, n)"))))))]
V["l08_addressbook_lookup"] = [("plus-as-star", "`n.^(b.addr)` written with reflexive closure.",
    AND("@t is sig_addr", "rtc[atom a, c | (there exists tuple u, ((u t_addr_1 @b) and ((u t_addr_2 a) and (u t_addr_3 c))))](@n, @t)"))]
V["l01_genealogy_biology"] = [("star-for-plus", "`p in p.^parents` written with reflexive closure (always true).",
    NOT(EX("atom", "p", AND("p is sig_person", "rtc[f_parents](p, p)"))))]

if __name__ == "__main__":
    for item, vs in V.items():
        with open(f"items/{item}/naive_variants.json", "w") as f:
            json.dump([{"name": n, "description": d, "ve": x + ".\n"} for n, d, x in vs], f, indent=1)
    print(sum(len(v) for v in V.values()), "variants")
