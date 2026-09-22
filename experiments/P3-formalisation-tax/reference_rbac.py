"""Independent reference evaluators for Kubernetes RBAC and AWS IAM (identity policies).

Stdlib only.  Written from the public documentation and the upstream Kubernetes
RBAC authorizer (plugin/pkg/auth/authorizer/rbac/rbac.go, pkg/apis/rbac/v1/evaluation_helpers.go,
pkg/controller/clusterroleaggregation), not from the system under test.

    k8s_authorize(objects, request) -> bool
    iam_authorize(policies, request) -> bool
"""

from __future__ import annotations

import re

# --------------------------------------------------------------------------------------
# Kubernetes RBAC
# --------------------------------------------------------------------------------------


def _labels(obj: dict) -> dict:
    return (obj.get("metadata") or {}).get("labels") or {}


def _selector_matches(selector: dict, labels: dict) -> bool:
    """metav1.LabelSelector semantics (matchLabels AND matchExpressions)."""
    for k, v in (selector.get("matchLabels") or {}).items():
        if labels.get(k) != v:
            return False
    for expr in selector.get("matchExpressions") or []:
        key, op, vals = expr["key"], expr["operator"], expr.get("values") or []
        if op == "In":
            if key not in labels or labels[key] not in vals:
                return False
        elif op == "NotIn":
            if key in labels and labels[key] in vals:
                return False
        elif op == "Exists":
            if key not in labels:
                return False
        elif op == "DoesNotExist":
            if key in labels:
                return False
        else:
            raise ValueError(f"unknown selector operator {op}")
    return True


def effective_cluster_role_rules(objects: list) -> dict:
    """name -> list of rules, after running the aggregation controller to a fixpoint.

    An aggregated ClusterRole's rules are overwritten by the union of the rules of every
    *other* ClusterRole selected by any of its clusterRoleSelectors (the controller skips
    the role itself).  Because the controller reads the selected roles' current (possibly
    aggregated) rules, aggregation composes transitively; iterate to a fixpoint.
    """
    crs = {o["metadata"]["name"]: o for o in objects if o.get("kind") == "ClusterRole"}
    rules = {}
    for name, o in crs.items():
        rules[name] = [] if o.get("aggregationRule") is not None else list(o.get("rules") or [])

    def key(r):
        return repr(sorted((k, repr(v)) for k, v in r.items()))

    changed = True
    while changed:
        changed = False
        for name, o in crs.items():
            agg = o.get("aggregationRule")
            if agg is None:
                continue
            new, seen = [], set()
            for sel in agg.get("clusterRoleSelectors") or []:
                for other_name in sorted(crs):
                    if other_name == name:
                        continue
                    if _selector_matches(sel, _labels(crs[other_name])):
                        for r in rules[other_name]:
                            if key(r) not in seen:
                                seen.add(key(r))
                                new.append(r)
            if {key(r) for r in new} != {key(r) for r in rules[name]}:
                rules[name] = new
                changed = True
    return rules


def _subject_applies(subject: dict, user: str, groups: list, binding_namespace: str) -> bool:
    kind = subject.get("kind")
    if kind == "User":
        return subject.get("name") == user
    if kind == "Group":
        return subject.get("name") in (groups or [])
    if kind == "ServiceAccount":
        ns = subject.get("namespace") or binding_namespace
        if not ns:
            return False
        return user == f"system:serviceaccount:{ns}:{subject.get('name')}"
    return False


def _verb_matches(rule, verb):
    return any(v == "*" or v == verb for v in rule.get("verbs") or [])


def _api_group_matches(rule, group):
    return any(g == "*" or g == group for g in rule.get("apiGroups") or [])


def _resource_matches(rule, resource, subresource):
    combined = resource if subresource == "" else f"{resource}/{subresource}"
    for rr in rule.get("resources") or []:
        if rr == "*":
            return True
        if rr == combined:
            return True
        # upstream also accepts "*/<subresource>"; it does NOT accept "<resource>/*"
        if subresource and rr == "*/" + subresource:
            return True
    return False


def _resource_name_matches(rule, name):
    names = rule.get("resourceNames") or []
    if not names:
        return True
    return name in names


def rule_allows(rule: dict, request: dict) -> bool:
    return (
        _verb_matches(rule, request["verb"])
        and _api_group_matches(rule, request.get("apiGroup", ""))
        and _resource_matches(rule, request["resource"], request.get("subresource", "") or "")
        and _resource_name_matches(rule, request.get("name", "") or "")
    )


def k8s_authorize(objects: list, request: dict) -> bool:
    cr_rules = effective_cluster_role_rules(objects)
    roles = {
        (o["metadata"].get("namespace", ""), o["metadata"]["name"]): list(o.get("rules") or [])
        for o in objects
        if o.get("kind") == "Role"
    }
    user = request.get("user", "")
    groups = request.get("groups") or []
    req_ns = request.get("namespace", "") or ""

    def rules_for(roleref, binding_ns):
        kind, name = roleref.get("kind"), roleref.get("name")
        if kind == "ClusterRole":
            return cr_rules.get(name, [])
        if kind == "Role" and binding_ns:
            return roles.get((binding_ns, name), [])
        return []

    for o in objects:
        kind = o.get("kind")
        if kind == "ClusterRoleBinding":
            bns = ""
        elif kind == "RoleBinding":
            bns = o["metadata"].get("namespace", "") or ""
            if not req_ns or req_ns != bns:
                continue
        else:
            continue
        if not any(_subject_applies(s, user, groups, bns) for s in o.get("subjects") or []):
            continue
        if any(rule_allows(r, request) for r in rules_for(o.get("roleRef") or {}, bns)):
            return True
    return False


# --------------------------------------------------------------------------------------
# AWS IAM (identity-based policies only)
# --------------------------------------------------------------------------------------


class _MissingVariable(Exception):
    pass


_VAR_RE = re.compile(r"\$\{([^}]*)\}")


def _glob_regex(pattern: str, context: dict | None, ignore_case: bool) -> re.Pattern:
    """Translate an IAM glob (with optional ${var} substitution) to an anchored regex."""
    out = []
    i = 0
    while i < len(pattern):
        m = _VAR_RE.match(pattern, i) if context is not None else None
        if m:
            inner = m.group(1).strip()
            if inner in ("*", "?", "$"):
                out.append(re.escape(inner))
            else:
                default = None
                if "," in inner:
                    inner, d = inner.split(",", 1)
                    inner, d = inner.strip(), d.strip()
                    if len(d) >= 2 and d[0] == d[-1] == "'":
                        default = d[1:-1]
                if inner in context:
                    out.append(re.escape(str(context[inner])))
                elif default is not None:
                    out.append(re.escape(default))
                else:
                    raise _MissingVariable(inner)
            i = m.end()
            continue
        c = pattern[i]
        if c == "*":
            out.append(".*")
        elif c == "?":
            out.append(".")
        else:
            out.append(re.escape(c))
        i += 1
    return re.compile("".join(out) + r"\Z", re.DOTALL | (re.IGNORECASE if ignore_case else 0))


def _as_list(x):
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


def action_matches(pattern: str, action: str) -> bool:
    return bool(_glob_regex(pattern, None, True).match(action))


def resource_matches(pattern: str, resource: str, context: dict) -> bool:
    if pattern == "*":
        return True
    return bool(_glob_regex(pattern, context, False).match(resource))


def _str(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def _single_condition(op: str, key: str, values, context: dict) -> bool:
    if_exists = op.endswith("IfExists")
    base = op[: -len("IfExists")] if if_exists else op
    if base.startswith("ForAnyValue:") or base.startswith("ForAllValues:"):
        raise NotImplementedError(f"set operator {op}")
    vals = [_str(v) for v in _as_list(values)]
    present = key in context

    if base == "Null":
        want_absent = vals[0].lower() == "true"
        return (not present) == want_absent

    negated = base in (
        "StringNotEquals",
        "StringNotEqualsIgnoreCase",
        "StringNotLike",
        "ArnNotEquals",
        "ArnNotLike",
        "NumericNotEquals",
        "DateNotEquals",
    )
    if not present:
        if if_exists:
            return True
        return negated

    cv = context[key]
    cvals = [_str(x) for x in cv] if isinstance(cv, list) else [_str(cv)]

    def any_match(pred):
        return any(pred(c, v) for c in cvals for v in vals)

    def pvars(v):  # policy variables inside condition values
        try:
            return _VAR_RE.sub(lambda m: _subst_var(m, context), v)
        except _MissingVariable:
            return None

    if base in ("StringEquals", "StringNotEquals"):
        hit = any_match(lambda c, v: pvars(v) is not None and c == pvars(v))
    elif base in ("StringEqualsIgnoreCase", "StringNotEqualsIgnoreCase"):
        hit = any_match(lambda c, v: pvars(v) is not None and c.lower() == pvars(v).lower())
    elif base in ("StringLike", "StringNotLike", "ArnLike", "ArnNotLike", "ArnEquals", "ArnNotEquals"):

        def like(c, v):
            try:
                return bool(_glob_regex(v, context, False).match(c))
            except _MissingVariable:
                return False

        hit = any_match(like)
    elif base == "Bool":
        hit = any_match(lambda c, v: c.lower() == v.lower())
    elif base.startswith("Numeric"):
        cmp = {
            "NumericEquals": lambda a, b: a == b,
            "NumericNotEquals": lambda a, b: a == b,
            "NumericLessThan": lambda a, b: a < b,
            "NumericLessThanEquals": lambda a, b: a <= b,
            "NumericGreaterThan": lambda a, b: a > b,
            "NumericGreaterThanEquals": lambda a, b: a >= b,
        }[base]
        hit = any_match(lambda c, v: cmp(float(c), float(v)))
    else:
        raise NotImplementedError(f"condition operator {op}")
    return (not hit) if negated else hit


def _subst_var(m, context):
    inner = m.group(1).strip()
    if inner in ("*", "?", "$"):
        return inner
    if inner in context:
        return str(context[inner])
    raise _MissingVariable(inner)


def conditions_hold(cond: dict | None, context: dict) -> bool:
    for op, block in (cond or {}).items():
        for key, values in block.items():
            if not _single_condition(op, key, values, context):
                return False
    return True


def statement_matches(stmt: dict, request: dict) -> bool:
    action = request["action"]
    resource = request["resource"]
    context = request.get("context") or {}
    if "Action" in stmt:
        if not any(action_matches(p, action) for p in _as_list(stmt["Action"])):
            return False
    elif "NotAction" in stmt:
        if any(action_matches(p, action) for p in _as_list(stmt["NotAction"])):
            return False
    else:
        return False
    try:
        if "Resource" in stmt:
            if not any(resource_matches(p, resource, context) for p in _as_list(stmt["Resource"])):
                return False
        elif "NotResource" in stmt:
            if any(resource_matches(p, resource, context) for p in _as_list(stmt["NotResource"])):
                return False
        else:
            return False
    except _MissingVariable:
        return False
    return conditions_hold(stmt.get("Condition"), context)


def iam_authorize(policies: list, request: dict) -> bool:
    stmts = [s for p in policies for s in _as_list(p.get("Statement"))]
    if any(s.get("Effect") == "Deny" and statement_matches(s, request) for s in stmts):
        return False
    return any(s.get("Effect") == "Allow" and statement_matches(s, request) for s in stmts)
