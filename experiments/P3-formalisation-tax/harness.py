"""P3 harness: encode item worlds as VE finite models, run the author's VE
formalisation, and differentially test it against the independent reference.

Trust split (see README.md):
  * ``reference*.py`` interpret the SOURCE artefact (Cedar text, RBAC objects,
    IAM JSON, Alloy text) directly. They never import ``ve``.
  * This file is mechanical glue on the VE side: a fixed, per-family encoding of
    a world into a VE finite model (the "fact base"). It contains no policy
    logic, except the per-item ``OPAQUE`` hooks, which compute predicates that
    VE cannot express (numeric comparison, string globbing, datetime). Every
    such hook is counted against VE coverage.
  * ``items/<id>/formalisation.ve`` + ``environment.json`` + ``bindings.json``
    are the untrusted author's work.

Usage:
  python harness.py check <item>...     parse/type-check/evaluate VE only (no reference)
  python harness.py diff <item>...      differential test vs reference (+ perturbations)
  python harness.py all                 diff every item and write results.json
"""
from __future__ import annotations

import copy
import json
import random
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from ve import Environment, FiniteModel, evaluate, parse, prove_entailment, find_countermodel  # noqa: E402
from ve.errors import VEError  # noqa: E402

ITEMS = HERE / "items"
N_PERTURB = int(__import__("os").environ.get("P3_N", "300"))
SEED = 20260922


# ------------------------------------------------------------------ utilities

def slug(text: str, limit: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", str(text).lower()).strip("_")
    if not s or not s[0].isalpha():
        s = "k" + s
    return s[:limit].rstrip("_")


class Namer:
    """Injective map from arbitrary keys to VE local IDs."""

    def __init__(self, prefix: str):
        self.prefix, self.ids, self.used = prefix, {}, set()

    def __call__(self, key) -> str:
        if key not in self.ids:
            base = f"{self.prefix}_{slug(key if isinstance(key, str) else json.dumps(key))}"
            name, i = base, 1
            while name in self.used:
                i += 1
                name = f"{base}_{i}"
            self.ids[key] = name
            self.used.add(name)
        return self.ids[key]


class FactBase:
    def __init__(self):
        self.domains: dict[str, set] = {}
        self.rel: dict[str, set] = {}

    def add(self, sort: str, local: str) -> str:
        self.domains.setdefault(sort, set()).add(local)
        return local

    def fact(self, pred: str, *args: str) -> None:
        self.rel.setdefault(pred, set()).add(tuple(args))


# ------------------------------------------------------------ Cedar encoding

UID_RE = re.compile(r'((?:[A-Za-z_][A-Za-z0-9_]*::)+"(?:[^"\\]|\\.)*")')


def uid_type(uid: str) -> str:
    return uid.rsplit("::", 1)[0]


def cedar_facts(world: dict, request: dict, bindings: dict) -> tuple[FactBase, dict]:
    """Fixed Cedar encoding. Sorts: entity, value.

    parent(e, p)          immediate parent edge (store parents)
    type_<t>(e)           entity type tag (slug of the full type name)
    has_<a>(o)            attribute a is present on o (entity, record node or context)
    ea_<a>(o, e)          entity- or record-valued attribute
    sa_<a>(o, v)          string/long/extension-valued attribute (value sort)
    bt_<a>(o) / bf_<a>(o) Boolean attribute is true / false
    es_<a>(o, e)          member of an entity/record set attribute
    ss_<a>(o, v)          member of a string/long set attribute
    type_record(r)        r is an anonymous record node
    nattrs_<n>(r)         record node r has exactly n attributes (record equality needs equal key
                          sets; added after review found c21 blind to extra keys)
    Constants: principal, action, resource, context (entity), plus the author's
    bindings.json constants (Cedar UIDs or literal values).
    """
    fb = FactBase()
    fb.raw = {}  # (owner local ID, attribute slug) -> raw scalar/extension value, for OPAQUE hooks
    fb.domains.setdefault("entity", set())
    fb.domains.setdefault("value", set())  # may be empty: VE admits empty sorts
    ent, val = Namer("e"), Namer("v")
    rec_counter = [0]

    def E(uid):
        return fb.add("entity", ent(uid))

    def V(x):
        # type-tagged keys: the string "5" and the long 5 are different Cedar values
        return fb.add("value", val(("s:" + x) if isinstance(x, str) else ("j:" + json.dumps(x))))

    fb.E, fb.V = E, V

    def attr(owner: str, name: str, value) -> None:
        a = slug(name)
        fb.fact(f"has_{a}", owner)
        if isinstance(value, bool):
            fb.fact(f"{'bt' if value else 'bf'}_{a}", owner)
        elif isinstance(value, dict) and "__entity" in value:
            fb.fact(f"ea_{a}", owner, E(value["__entity"]))
        elif isinstance(value, dict) and "__extn" in value:
            ext = value["__extn"]
            fb.raw[(owner, a)] = value
            fb.fact(f"sa_{a}", owner, V(f'{ext.get("fn")}({ext.get("arg")})'))
        elif isinstance(value, dict):
            fb.fact(f"ea_{a}", owner, record(value))
        elif isinstance(value, list):
            for m in value:
                if isinstance(m, dict) and "__entity" in m:
                    fb.fact(f"es_{a}", owner, E(m["__entity"]))
                elif isinstance(m, dict) and "__extn" not in m:
                    fb.fact(f"es_{a}", owner, record(m))
                else:
                    fb.fact(f"ss_{a}", owner, V(m if not isinstance(m, dict) else json.dumps(m)))
        else:
            fb.raw[(owner, a)] = value
            fb.fact(f"sa_{a}", owner, V(value))

    def record(fields: dict) -> str:
        rec_counter[0] += 1
        r = fb.add("entity", f"rec_{rec_counter[0]}")
        fb.fact("type_record", r)
        for k, v in fields.items():
            attr(r, k, v)
        fb.fact(f"nattrs_{len(fields)}", r)
        return r

    for e in world["entities"]:
        me = E(e["uid"])
        fb.fact(f"type_{slug(uid_type(e['uid']))}", me)
        for p in e["parents"]:
            fb.fact("parent", me, E(p))
        for k, v in e["attrs"].items():
            attr(me, k, v)
    consts = {"principal": E(request["principal"]), "action": E(request["action"]),
              "resource": E(request["resource"])}
    for key in ("principal", "action", "resource"):
        fb.fact(f"type_{slug(uid_type(request[key]))}", consts[key])
    ctx = fb.add("entity", "request_context")
    consts["context"] = ctx
    for k, v in request.get("context", {}).items():
        attr(ctx, k, v)
    for name, spec in bindings.get("constants", {}).items():
        if "entity" in spec:
            consts[name] = E(spec["entity"])
            fb.fact(f"type_{slug(uid_type(spec['entity']))}", consts[name])
        else:
            consts[name] = V(spec["value"])
    fb.records = rec_counter
    return fb, consts


# -------------------------------------------------------------- K8s encoding

def k8s_facts(world: dict, request: dict, bindings: dict) -> tuple[FactBase, dict]:
    """Fixed Kubernetes RBAC encoding. Sorts: role, binding, rule, sel, str.

    is_role / is_clusterrole(role); role_name(role, str); role_ns(role, str)
    role_label(role, str "key=value"); has_aggregation(role)
    role_selector(role, sel); sel_label(sel, str "key=value")
    role_rule(role, rule); rule_verb / rule_group / rule_resource / rule_resname(rule, str)
    is_rolebinding / is_clusterrolebinding(binding); binding_ns(binding, str)
    ref_role / ref_clusterrole(binding); ref_name(binding, str)
    subject_user / subject_group(binding, str)
    req_group(str): the request user's groups
    Constants: user, verb, apigroup, resource, subresource, path (adapter-computed
    "resource/subresource" string, or resource if none), namespace, name, star ("*"),
    empty (""), plus bindings.json constants (strings).
    """
    fb = FactBase()
    S = Namer("s")
    rn, bn, un, sn = Namer("r"), Namer("b"), Namer("u"), Namer("l")

    def s(x):
        return fb.add("str", S(x))

    for sort in ("role", "binding", "rule", "sel", "str"):
        fb.domains.setdefault(sort, set())
    for i, o in enumerate(world["objects"]):
        md = o["metadata"]
        if o["kind"] in ("Role", "ClusterRole"):
            r = fb.add("role", rn(f"{o['kind']}_{md.get('namespace', '')}_{md['name']}_{i}"))
            fb.fact("is_role" if o["kind"] == "Role" else "is_clusterrole", r)
            fb.fact("role_name", r, s(md["name"]))
            if "namespace" in md:
                fb.fact("role_ns", r, s(md["namespace"]))
            for k, v in md.get("labels", {}).items():
                fb.fact("role_label", r, s(f"{k}={v}"))
            if "aggregationRule" in o:
                fb.fact("has_aggregation", r)
                for j, sel in enumerate(o["aggregationRule"].get("clusterRoleSelectors", [])):
                    se = fb.add("sel", sn(f"{i}_{j}"))
                    fb.fact("role_selector", r, se)
                    for k, v in sel.get("matchLabels", {}).items():
                        fb.fact("sel_label", se, s(f"{k}={v}"))
            for j, rule in enumerate(o.get("rules") or []):
                u = fb.add("rule", un(f"{i}_{j}"))
                fb.fact("role_rule", r, u)
                for field, pred in (("verbs", "rule_verb"), ("apiGroups", "rule_group"),
                                    ("resources", "rule_resource"), ("resourceNames", "rule_resname")):
                    for x in rule.get(field, []) or []:
                        fb.fact(pred, u, s(x))
        else:
            b = fb.add("binding", bn(f"{o['kind']}_{md.get('namespace', '')}_{md['name']}_{i}"))
            fb.fact("is_rolebinding" if o["kind"] == "RoleBinding" else "is_clusterrolebinding", b)
            if "namespace" in md:
                fb.fact("binding_ns", b, s(md["namespace"]))
            fb.fact("ref_role" if o["roleRef"]["kind"] == "Role" else "ref_clusterrole", b)
            fb.fact("ref_name", b, s(o["roleRef"]["name"]))
            for sub in o.get("subjects", []):
                if sub["kind"] == "User":
                    fb.fact("subject_user", b, s(sub["name"]))
                elif sub["kind"] == "Group":
                    fb.fact("subject_group", b, s(sub["name"]))
                else:
                    fb.fact("subject_user", b, s(f"system:serviceaccount:{sub.get('namespace', '')}:{sub['name']}"))
    for g in request["groups"]:
        fb.fact("req_group", s(g))
    path = request["resource"] + (f"/{request['subresource']}" if request["subresource"] else "")
    consts = {"user": s(request["user"]), "verb": s(request["verb"]), "apigroup": s(request["apiGroup"]),
              "resource": s(request["resource"]), "subresource": s(request["subresource"]),
              "path": s(path), "namespace": s(request["namespace"]), "name": s(request["name"]),
              "star": s("*"), "empty": s("")}
    for name, spec in bindings.get("constants", {}).items():
        consts[name] = s(spec["value"])
    return fb, consts


# -------------------------------------------------------------- IAM encoding

def glob(pattern: str, text: str, fold: bool) -> bool:
    if fold:
        pattern, text = pattern.lower(), text.lower()
    rx = "".join(".*" if c == "*" else "." if c == "?" else re.escape(c) for c in pattern)
    return re.fullmatch(rx, text, re.S) is not None


def iam_facts(world: dict, request: dict, bindings: dict) -> tuple[FactBase, dict]:
    """Fixed IAM encoding. Sorts: stmt, cond, str.

    allow_stmt / deny_stmt(stmt)
    uses_action / uses_notaction / uses_resource / uses_notresource(stmt)
    action_pat / resource_pat(stmt, str)      (Action|NotAction and Resource|NotResource lists)
    stmt_cond(stmt, cond); cond_op(cond, str operator name); cond_key(cond, str); cond_value(cond, str)
    ctx(str key, str value): request context
    Context-key names are case-insensitive in IAM, so every key name (cond_key, ctx and the
    ${var} names below) is encoded lower-cased; values keep their case.
    ADAPTER-COMPUTED (string matching VE cannot express, counted as opaque):
      action_glob(str pattern): pattern matches the request action (case-insensitive * ? glob)
      resource_glob(str pattern): pattern, after ${var} substitution from context, matches the
                                  request resource (case-sensitive glob); false if a variable is missing
    Constants: bindings.json constants (strings).
    """
    fb = FactBase()
    S, st, cn = Namer("s"), Namer("t"), Namer("c")
    for sort in ("stmt", "cond", "str"):
        fb.domains.setdefault(sort, set())

    def s(x):
        return fb.add("str", S(x))

    def aslist(x):
        return x if isinstance(x, list) else [x]

    ctx = {str(k).lower(): v for k, v in request.get("context", {}).items()}
    for pi, pol in enumerate(world["policies"]):
        for si, stmt in enumerate(aslist(pol["Statement"])):
            t = fb.add("stmt", st(f"{pi}_{si}"))
            fb.fact("allow_stmt" if stmt["Effect"] == "Allow" else "deny_stmt", t)
            for key, uses, pred in (("Action", "uses_action", "action_pat"), ("NotAction", "uses_notaction", "action_pat"),
                                    ("Resource", "uses_resource", "resource_pat"), ("NotResource", "uses_notresource", "resource_pat")):
                if key in stmt:
                    fb.fact(uses, t)
                    for p in aslist(stmt[key]):
                        fb.fact(pred, t, s(p))
                        if pred == "action_pat" and glob(p, request["action"], True):
                            fb.fact("action_glob", s(p))
                        if pred == "resource_pat":
                            sub, ok = p, True
                            for var in re.findall(r"\$\{([^}]*)\}", p):
                                if var.lower() in ctx:
                                    sub = sub.replace("${" + var + "}", ctx[var.lower()])
                                else:
                                    ok = False
                            if ok and glob(sub, request["resource"], False):
                                fb.fact("resource_glob", s(p))
            for ci, (op, kv) in enumerate(stmt.get("Condition", {}).items()):
                for key, values in kv.items():
                    c = fb.add("cond", cn(f"{pi}_{si}_{ci}_{key}"))
                    fb.fact("stmt_cond", t, c)
                    fb.fact("cond_op", c, s(op))
                    fb.fact("cond_key", c, s(key.lower()))
                    for v in aslist(values):
                        fb.fact("cond_value", c, s(v))
    for k, v in ctx.items():
        fb.fact("ctx", s(k), s(v))
    consts = {name: s(spec["value"]) for name, spec in bindings.get("constants", {}).items()}
    return fb, consts


# ------------------------------------------------------------ Alloy encoding

def alloy_facts(world: dict, request: dict | None, bindings: dict) -> tuple[FactBase, dict]:
    """Fixed Alloy encoding. Sorts: atom, tuple.

    sig_<S>(atom)                   atom belongs to signature S
    f_<f>(atom, atom)               binary field f (owner, value)
    f_<f>(atom)                     unary field (e.g. marked: HeapState -> set Node is binary;
                                    unary only for sets of atoms)
    t_<f>_1/2/3(tuple, atom)        ternary field f, one tuple node per tuple (reification)
    Constants: every instance binding whose value is an atom (name = slug of the
    parameter, primes " and ' become _p), plus bindings.json constants (atoms).
    """
    fb = FactBase()
    fb.domains.setdefault("atom", set())
    fb.domains.setdefault("tuple", set())
    A = Namer("a")
    T = Namer("t")

    def a(x):
        return fb.add("atom", A(x))

    for sig, atoms in world["sigs"].items():
        for x in atoms:
            fb.fact(f"sig_{slug(sig)}", a(x))
    for f, tuples in world["fields"].items():
        fs = slug(f)
        for tup in tuples:
            if len(tup) == 1:
                fb.fact(f"f_{fs}", a(tup[0]))
            elif len(tup) == 2:
                fb.fact(f"f_{fs}", a(tup[0]), a(tup[1]))
            else:
                t = fb.add("tuple", T(f"{f}_{'_'.join(tup)}"))
                for k, x in enumerate(tup, 1):
                    fb.fact(f"t_{fs}_{k}", t, a(x))
    consts = {}
    field_names = set(world["fields"])
    for p, v in world.get("bindings", {}).items():
        if v not in field_names:
            consts[slug(p.replace('"', "_p").replace("'", "_p"))] = a(v)
    for name, spec in bindings.get("constants", {}).items():
        consts[name] = a(spec["atom"])
    return fb, consts


ENCODERS = {"cedar": cedar_facts, "k8s": k8s_facts, "iam": iam_facts, "alloy": alloy_facts}


# ------------------------------------------------------------ opaque hooks
# Per-item predicates computed outside VE (numeric/string/datetime). Each takes
# (world, request) and returns {predicate: set_of_tuples_of_raw_keys}; raw keys
# are mapped with the same Namer as the encoder via ``_opaque_tuples``.
import adapters  # noqa: E402


def build_model(env: Environment, family: str, world: dict, request, bindings: dict, item_id: str) -> FiniteModel:
    fb, consts = ENCODERS[family](world, request, bindings)
    hook = adapters.OPAQUE.get(item_id)
    if hook:
        for pred, tuples in hook(world, request, fb, consts).items():
            fb.rel.setdefault(pred, set()).update(tuples)
    domains = {s: sorted(fb.domains.get(s, set())) for s in env.sorts}
    for s in env.sorts:
        if s not in fb.domains:
            raise KeyError(f"sort {s!r} is not produced by the {family} encoding")
    missing_c = [c for c in env.constants if c not in consts]
    if missing_c:
        raise KeyError(f"constants without a binding: {missing_c}")
    relations = {}
    for p in env.predicates:
        tuples = fb.rel.get(p, set())
        if p not in fb.rel and not _known_predicate(family, p, bindings):
            raise KeyError(f"predicate {p!r} is not produced by the {family} encoding or declared in bindings.json")
        relations[p] = sorted([list(t) for t in tuples])
    return FiniteModel.from_dict(env, {"complete": True, "domains": domains,
                                       "constants": {c: consts[c] for c in env.constants},
                                       "relations": relations})


def _known_predicate(family: str, p: str, bindings: dict) -> bool:
    """A declared predicate may be empty in a given world; accept convention names."""
    if p in bindings.get("empty_ok", []):
        return True
    conv = {"cedar": r"(parent|type_\w+|has_\w+|ea_\w+|sa_\w+|bt_\w+|bf_\w+|es_\w+|ss_\w+|type_record|nattrs_\d+)",
            "k8s": r"(is_role|is_clusterrole|role_name|role_ns|role_label|has_aggregation|role_selector|sel_label|role_rule|"
                   r"rule_verb|rule_group|rule_resource|rule_resname|is_rolebinding|is_clusterrolebinding|binding_ns|"
                   r"ref_role|ref_clusterrole|ref_name|subject_user|subject_group|req_group)",
            "iam": r"(allow_stmt|deny_stmt|uses_action|uses_notaction|uses_resource|uses_notresource|action_pat|"
                   r"resource_pat|stmt_cond|cond_op|cond_key|cond_value|ctx|action_glob|resource_glob)",
            "alloy": r"(sig_\w+|f_\w+|t_\w+_[123])"}[family]
    return re.fullmatch(conv, p) is not None or p in adapters.OPAQUE_PREDICATES.get(family, set())


# ------------------------------------------------------------ item loading

def load_item(item_id: str) -> dict:
    d = ITEMS / item_id
    item = json.loads((d / "item.json").read_text())
    item["dir"] = d
    item["sources"] = {p.name: p.read_text() for p in d.iterdir()
                       if p.name.startswith("source") or p.name in ("relation.als", "linked.json")}
    return item


FORMAL_SUBDIR = __import__("os").environ.get("P3_FORMAL_DIR", "")  # e.g. "agent": items/<id>/agent/


def load_formalisation(item: dict):
    d = item["dir"] / FORMAL_SUBDIR if FORMAL_SUBDIR else item["dir"]
    env = Environment.from_json((d / "environment.json").read_bytes())
    doc = parse(env, (d / "formalisation.ve").read_bytes())
    bindings = json.loads((d / "bindings.json").read_text()) if (d / "bindings.json").exists() else {}
    return env, doc, bindings


def question_world(item: dict, q: dict) -> tuple[dict, dict | None]:
    """(world, request) for a question: Alloy questions carry their own instance."""
    if item["family"] == "alloy":
        return q["instance"], None
    return item["world"], q["request"]


def select_statement(doc, bindings: dict, q: dict):
    """The statement answering question q (default: the first)."""
    kind = q.get("target", {}).get("kind") if isinstance(q.get("target"), dict) else None
    idx = bindings.get("statement_for", {}).get(kind or "", 0)
    return doc.formulas[idx]


def ve_answer(item: dict, env, doc, bindings, q: dict, world=None, request=None) -> dict:
    if world is None:
        world, request = question_world(item, q)
    if isinstance(q.get("target"), dict) and q["target"].get("kind") == "check":
        return ve_check_question(item, env, doc, bindings, q)
    try:
        model = build_model(env, item["family"], world, request, bindings, item["id"])
    except (KeyError, VEError) as e:
        return {"answer": None, "status": "EncodingError", "detail": str(e)[:300]}
    res = evaluate(env, select_statement(doc, bindings, q), model, trace=False)
    return {"answer": res.value, "status": res.status, "evaluations": res.evaluations}


def ve_check_question(item, env, doc, bindings, q) -> dict:
    """Assertion check: premises = statements listed in bindings['check']['premises'];
    conclusion = bindings['check']['conclusion']. Found proof -> True; countermodel -> False."""
    spec = bindings["check"]
    prem = [doc.formulas[i] for i in spec["premises"]]
    concl = doc.formulas[spec["conclusion"]]
    t = time.time()
    proof = prove_entailment(env, prem, concl, max_steps=spec.get("max_steps", 20000))
    out = {"prove_status": proof.status, "prove_steps": proof.steps, "prove_seconds": round(time.time() - t, 2)}
    if proof.status == "Found":
        return {**out, "answer": True, "status": "Proved"}
    cm = find_countermodel(env, prem, concl, max_domain_size=spec.get("max_domain", 2), max_models=200000)
    out["countermodel_status"] = cm.status
    if cm.status == "Found":
        return {**out, "answer": False, "status": "Countermodel"}
    return {**out, "answer": None, "status": "Unknown"}


# ------------------------------------------------------------ reference

def ref_answer(item: dict, q: dict, world=None, request=None) -> bool:
    import reference
    if world is None:
        world, request = question_world(item, q)
    return reference.answer(item, q, world, request)


# ------------------------------------------------------------ perturbations

def policy_uids(item) -> list[str]:
    text = item["sources"].get("source.cedar", "") + item["sources"].get("linked.json", "")
    return sorted(set(u.replace('\\"', '"') for u in UID_RE.findall(text)))


def policy_strings(item) -> list[str]:
    text = re.sub(r'(?:[A-Za-z_][A-Za-z0-9_]*::)+"(?:[^"\\]|\\.)*"', "", item["sources"].get("source.cedar", ""))
    text = re.sub(r"//[^\n]*", "", text)
    return sorted(set(re.findall(r'"([^"\\]*)"', text)))


def perturb_cedar(item, rng: random.Random):
    world = copy.deepcopy(item["world"])
    q = rng.choice(item["questions"])
    req = copy.deepcopy(q["request"])
    ents = world["entities"]
    uids = sorted({e["uid"] for e in ents} | set(policy_uids(item)) |
                  {req["principal"], req["action"], req["resource"]})
    actions = [u for u in uids if "Action::" in u]
    strings = sorted(set(policy_strings(item)) | {"x"})
    by_uid = {e["uid"]: e for e in ents}
    ptext = item["sources"].get("source.cedar", "")
    attr_names = sorted(set(re.findall(r"\.([A-Za-z_]\w*)\b(?!\s*\()", re.sub(r"//[^\n]*", "", ptext)))
                        | set(re.findall(r"\bhas\s+([A-Za-z_]\w*)", ptext)))
    ctx_keys = sorted(set(re.findall(r"context\.(\w+)", ptext)) | set(re.findall(r'context\s+has\s+"?(\w+)', ptext)))

    def ancestors(u):
        seen, stack = set(), [u]
        while stack:
            x = stack.pop()
            for p in by_uid.get(x, {}).get("parents", []):
                if p not in seen:
                    seen.add(p)
                    stack.append(p)
        return seen

    def mutate_value(v):
        if isinstance(v, bool):
            return not v
        if isinstance(v, dict) and "__entity" in v:
            return {"__entity": rng.choice(uids)}
        if isinstance(v, str):
            return rng.choice(strings)
        if isinstance(v, int):
            return v + rng.choice([-3, -1, 1, 3])
        if isinstance(v, list):
            v = list(v)
            if v and rng.random() < 0.5:
                v.pop(rng.randrange(len(v)))
            else:
                sample = v[0] if v else None
                if isinstance(sample, dict) and "__entity" in sample or (not v and rng.random() < 0.5):
                    v.append({"__entity": rng.choice(uids)})
                elif not isinstance(sample, dict):
                    v.append(rng.choice(strings))
            return v
        if isinstance(v, dict) and "__extn" not in v and v:
            k = rng.choice(sorted(v))
            v = dict(v)
            v[k] = mutate_value(v[k])
            return v
        return v

    ops = []
    for _ in range(rng.choice([1, 1, 2, 3])):
        op = rng.choice(["principal", "action", "resource", "add_parent", "del_parent",
                         "attr", "attr", "del_attr", "context", "context", "ctx_add", "attr_add",
                         "link_request", "link_request"])
        if op in ("principal", "resource"):
            req[op] = rng.choice(uids)
        elif op == "action" and actions:
            req["action"] = rng.choice(actions)
        elif op == "add_parent":
            child, par = rng.choice(ents), rng.choice(uids)
            if par != child["uid"] and child["uid"] not in ancestors(par) | {par} and par not in child["parents"]:
                child["parents"].append(par)
                if par not in by_uid:
                    stub = {"uid": par, "attrs": {}, "parents": []}
                    ents.append(stub)
                    by_uid[par] = stub
        elif op == "del_parent":
            cands = [e for e in ents if e["parents"]]
            if cands:
                e = rng.choice(cands)
                e["parents"].pop(rng.randrange(len(e["parents"])))
        elif op in ("attr", "del_attr"):
            cands = [e for e in ents if e["attrs"]]
            if cands:
                e = rng.choice(cands)
                k = rng.choice(sorted(e["attrs"]))
                if op == "del_attr":
                    del e["attrs"][k]
                else:
                    e["attrs"][k] = mutate_value(e["attrs"][k])
        elif op == "link_request":
            # policy-aware: connect a request entity to a policy-literal UID by a 1- or 2-hop parent path
            child = req[rng.choice(["principal", "action", "resource"])]
            target = rng.choice(policy_uids(item) or uids)
            hops = [child, target] if rng.random() < 0.5 else [child, rng.choice(uids), target]
            for x, y in zip(hops, hops[1:]):
                for u in (x, y):
                    if u not in by_uid:
                        stub = {"uid": u, "attrs": {}, "parents": []}
                        ents.append(stub)
                        by_uid[u] = stub
                if x != y and x not in ancestors(y) and y not in by_uid[x]["parents"]:
                    by_uid[x]["parents"].append(y)
        elif op == "attr_add" and attr_names:
            # give a random entity an attribute the policy mentions, with a value of a random kind
            e = rng.choice(ents)
            e["attrs"][rng.choice(attr_names)] = rng.choice([
                {"__entity": rng.choice(uids)}, True, False, rng.choice(strings), rng.randint(0, 8),
                [{"__entity": rng.choice(uids)} for _ in range(rng.randint(0, 2))]])
        elif op == "ctx_add" and ctx_keys:
            # add/overwrite a context field the policy mentions, with a value of a random kind
            k = rng.choice(ctx_keys)
            req.setdefault("context", {})[k] = rng.choice([{"__entity": rng.choice(uids)}, True, False, rng.choice(strings)])
        elif op == "context" and req.get("context"):
            k = rng.choice(sorted(req["context"]))
            if rng.random() < 0.25:
                del req["context"][k]
            else:
                req["context"][k] = mutate_value(req["context"][k])
        ops.append(op)
    return world, req, ops


def perturb_k8s(item, rng):
    world = copy.deepcopy(item["world"])
    q = rng.choice(item["questions"])
    req = copy.deepcopy(q["request"])
    reqs = [x["request"] for x in item["questions"]]
    objs = world["objects"]
    names = sorted({r["user"] for r in reqs} | {s["name"] for o in objs for s in o.get("subjects", [])})
    groups = sorted({g for r in reqs for g in r["groups"]} | {s["name"] for o in objs for s in o.get("subjects", []) if s["kind"] == "Group"})
    verbs = sorted({r["verb"] for r in reqs} | {"get", "list", "create", "delete", "update", "watch", "patch"})
    apigroups = sorted({r["apiGroup"] for r in reqs} | {g for o in objs for ru in o.get("rules", []) or [] for g in ru["apiGroups"]})
    resources = sorted({r["resource"] for r in reqs} | {x.split("/")[0] for o in objs for ru in o.get("rules", []) or [] for x in ru["resources"] if x != "*"})
    nss = sorted({r["namespace"] for r in reqs} | {o["metadata"].get("namespace", "") for o in objs} | {""})
    rnames = sorted({r["name"] for r in reqs} | {n for o in objs for ru in o.get("rules", []) or [] for n in ru.get("resourceNames", [])} | {""})
    ops = []
    for _ in range(rng.choice([1, 1, 2, 3])):
        op = rng.choice(["user", "groups", "verb", "verb", "apigroup", "resource", "subresource", "namespace",
                         "name", "del_subject", "binding_ns", "label", "rule_verb_star", "del_rule_verb"])
        if op == "user":
            req["user"] = rng.choice(names)
        elif op == "groups":
            req["groups"] = sorted(set(rng.sample(groups, rng.randint(0, len(groups))))) if groups else []
        elif op == "verb":
            req["verb"] = rng.choice(verbs)
        elif op == "apigroup":
            req["apiGroup"] = rng.choice(apigroups)
        elif op == "resource":
            req["resource"] = rng.choice(resources)
        elif op == "subresource":
            req["subresource"] = rng.choice(["", "", "log", "exec"])
        elif op == "namespace":
            req["namespace"] = rng.choice(nss)
        elif op == "name":
            req["name"] = rng.choice(rnames)
        elif op == "del_subject":
            bs = [o for o in objs if o.get("subjects")]
            if bs:
                o = rng.choice(bs)
                o["subjects"].pop(rng.randrange(len(o["subjects"])))
        elif op == "binding_ns":
            bs = [o for o in objs if o["kind"] == "RoleBinding"]
            if bs:
                rng.choice(bs)["metadata"]["namespace"] = rng.choice([n for n in nss if n] or ["default"])
        elif op == "label":
            cr = [o for o in objs if o["kind"] == "ClusterRole"]
            labels = sorted({k for o in objs for k in o["metadata"].get("labels", {})} |
                            {k for o in objs for s in (o.get("aggregationRule") or {}).get("clusterRoleSelectors", []) for k in s.get("matchLabels", {})})
            if cr and labels:
                o = rng.choice(cr)
                lab = o["metadata"].setdefault("labels", {})
                k = rng.choice(labels)
                if k in lab and rng.random() < 0.5:
                    del lab[k]
                else:
                    lab[k] = rng.choice(["true", "false"])
        elif op in ("rule_verb_star", "del_rule_verb"):
            rs = [ru for o in objs for ru in o.get("rules", []) or []]
            if rs:
                ru = rng.choice(rs)
                if op == "rule_verb_star":
                    ru["verbs"] = ru["verbs"] + ["*"]
                elif len(ru["verbs"]) > 1:
                    ru["verbs"] = [v for v in ru["verbs"] if v != rng.choice(ru["verbs"])]
        ops.append(op)
    return world, req, ops


def perturb_iam(item, rng):
    world = copy.deepcopy(item["world"])
    q = rng.choice(item["questions"])
    req = copy.deepcopy(q["request"])
    reqs = [x["request"] for x in item["questions"]]
    actions = sorted({r["action"] for r in reqs} | {"s3:GetObject", "s3:ListBucket", "ec2:RunInstances", "iam:ListUsers",
                                                     "iam:DeleteUser", "route53:GetZone", "S3:PutObject", "s3:DeleteObjectVersion"})
    resources = sorted({r["resource"] for r in reqs} | {"*", "arn:aws:s3:::bucket-name/a/b", "arn:aws:iam::123456789012:user/carol"})
    keys = sorted({k for r in reqs for k in r["context"]} | {"aws:username", "aws:MultiFactorAuthPresent", "aws:RequestedRegion"})
    values = {"aws:username": ["alice", "bob", "carol"], "aws:MultiFactorAuthPresent": ["true", "false"],
              "aws:RequestedRegion": ["eu-west-1", "eu-central-1", "us-east-1", "ap-south-1", "eu-west-3"]}
    ops = []
    for _ in range(rng.choice([1, 1, 2, 3])):
        op = rng.choice(["action", "action", "resource", "ctx_set", "ctx_del"])
        if op == "action":
            req["action"] = rng.choice(actions)
        elif op == "resource":
            req["resource"] = rng.choice(resources)
        elif op == "ctx_set":
            k = rng.choice(keys)
            req["context"][k] = rng.choice(values.get(k, ["x"]))
        elif op == "ctx_del" and req["context"]:
            del req["context"][rng.choice(sorted(req["context"]))]
        ops.append(op)
    return world, req, ops


ALLOY_SHAPES = {  # column sigs of each field and sig of each atom binding, for random instances
    "l01_genealogy_biology": ({"parents": ["Person", "Person"], "spouse": ["Person", "Person"]}, {}),
    "l02_grandpa1_fact": ({"father": ["Person", "Man"], "mother": ["Person", "Woman"], "wife": ["Man", "Woman"],
                           "husband": ["Woman", "Man"]}, {}),
    "l03_grandpa1_noselfgrandpa": ({"father": ["Person", "Man"], "mother": ["Person", "Woman"], "wife": ["Man", "Woman"],
                                    "husband": ["Woman", "Man"]}, {}),
    "l04_graph_weakly_connected": ({"edges": ["node", "node"]}, {}),
    "l05_graph_ring": ({"edges": ["node", "node"]}, {}),
    "l06_graph_tree": ({"edges": ["node", "node"]}, {}),
    "l07_marksweep_mark": ({"left": ["HeapState", "Node", "Node"], "right": ["HeapState", "Node", "Node"],
                            "marked": ["HeapState", "Node"], "freeList": ["HeapState", "Node"]},
                           {"hs": "HeapState", "from": "Node", 'hs"': "HeapState"}),
    "l08_addressbook_lookup": ({"names": ["Book", "Name"], "addr": ["Book", "Name", "Target"]},
                               {"b": "Book", "n": "Name", "t": "Target"}),
}


def perturb_alloy(item, rng):
    """Half the time: 1-3 single-tuple toggles / binding changes on an item instance
    (stays near the decision boundary); otherwise: redraw every field at random."""
    import itertools
    qs = [q for q in item["questions"] if q["target"].get("kind") != "check"]
    q = rng.choice(qs)
    inst = copy.deepcopy(q["instance"])
    cols, bsorts = ALLOY_SHAPES[item["id"]]
    sigs = inst["sigs"]
    if rng.random() < 0.5:
        ops = []
        for _ in range(rng.choice([1, 1, 2, 3])):
            if bsorts and rng.random() < 0.2:
                p = rng.choice(sorted(bsorts))
                inst["bindings"][p] = rng.choice(sigs[bsorts[p]])
                ops.append("binding")
                continue
            f = rng.choice(sorted(cols))
            if not all(sigs.get(c) for c in cols[f]):
                continue
            tup = [rng.choice(sigs[c]) for c in cols[f]]
            cur = inst["fields"].setdefault(f, [])
            if tup in cur:
                cur.remove(tup)
                ops.append(f"del_{f}")
            else:
                cur.append(tup)
                ops.append(f"add_{f}")
        return q, inst, ops
    density = rng.choice([0.1, 0.2, 0.35, 0.5])
    for f, c in cols.items():
        pools = [sigs.get(x, []) for x in c]
        new = [list(t) for t in itertools.product(*pools)
               if rng.random() < (density / max(1, len(pools[-1])) * 2 if len(pools) > 2 else density)]
        inst["fields"][f] = new
    for p, srt in bsorts.items():
        inst["bindings"][p] = rng.choice(sigs[srt])
    return q, inst, ["redraw"]


N_TARGETED = int(__import__("os").environ.get("P3_NT", "100"))


def _recase(rng, text: str) -> str:
    return rng.choice([str.upper, str.lower, str.swapcase,
                       lambda t: "".join(c.upper() if rng.random() < 0.5 else c.lower() for c in t)])(text)


def _recase_policy_keys(rng, pol):
    """Re-case condition-key names and ${var} names inside Resource/NotResource."""
    for stmt in (pol["Statement"] if isinstance(pol["Statement"], list) else [pol["Statement"]]):
        for op, kv in list(stmt.get("Condition", {}).items()):
            stmt["Condition"][op] = {(_recase(rng, k) if rng.random() < 0.7 else k): v for k, v in kv.items()}
        for key in ("Resource", "NotResource"):
            if key in stmt:
                sub = lambda m: "${" + _recase(rng, m.group(1)) + "}"  # noqa: E731
                stmt[key] = ([re.sub(r"\$\{([^}]*)\}", sub, p) for p in stmt[key]] if isinstance(stmt[key], list)
                             else re.sub(r"\$\{([^}]*)\}", sub, stmt[key]))


def _record_slots(world, request):
    """Every record value (not entity refs / extension values) in entity attributes or the
    request context, including records inside sets and nested records."""
    out = []

    def walk(v):
        if isinstance(v, dict) and "__entity" not in v and "__extn" not in v:
            out.append(v)
            for x in v.values():
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
    for e in world["entities"]:
        for v in e["attrs"].values():
            walk(v)
    for v in (request.get("context") or {}).values():
        walk(v)
    return out


def targeted_perturbations(item, n=N_TARGETED):
    """Perturbations aimed at two semantics the random generator never exercised (found in
    review): IAM context-key names are case-insensitive (re-case keys in the request context
    and in the policy's condition keys / ${var} names); Cedar record equality needs identical
    key sets (add an extra key to a record, including records inside sets). Half start from an
    ordinary perturbation, half from an item question unchanged. Items without records (Cedar)
    or of other families get none."""
    rng = random.Random(f"{SEED}-{item['id']}-targeted")
    out = []
    fam = item["family"]
    if fam == "iam":
        for _ in range(n):
            if rng.random() < 0.5:
                w, r, ops = perturb_iam(item, rng)
            else:
                q = rng.choice(item["questions"])
                w, r, ops = copy.deepcopy(item["world"]), copy.deepcopy(q["request"]), []
            r["context"] = {(_recase(rng, k) if rng.random() < 0.7 else k): v for k, v in r["context"].items()}
            for pol in w["policies"]:
                _recase_policy_keys(rng, pol)
            out.append({"world": w, "request": r, "ops": ops + ["key_case"], "q": {}})
    elif fam == "cedar" and any(_record_slots(item["world"], q["request"]) for q in item["questions"]):
        ptext = re.sub(r"//[^\n]*", "", item["sources"].get("source.cedar", ""))
        extra = ["extra"] + sorted(set(re.findall(r"\.([A-Za-z_]\w*)\b(?!\s*\()", ptext)) |
                                   set(re.findall(r"\b([A-Za-z_]\w*)\s*:", ptext)))  # attribute and record-literal names
        while len(out) < n:
            if rng.random() < 0.5:
                w, r, ops = perturb_cedar(item, rng)
            else:
                q = rng.choice(item["questions"])
                w, r, ops = copy.deepcopy(item["world"]), copy.deepcopy(q["request"]), []
            slots = _record_slots(w, r)
            if not slots:
                continue
            rec = rng.choice(slots)
            k = next((k for k in rng.sample(extra, len(extra)) if k not in rec), None)
            if k is None:
                continue
            rec[k] = rng.choice(["x", True, 3, rng.choice(sorted(set(policy_strings(item))) or ["x"])])
            out.append({"world": w, "request": r, "ops": ops + ["record_extra_key"], "q": {}})
    return out


def perturbations(item, n=N_PERTURB):
    rng = random.Random(f"{SEED}-{item['id']}")
    out = []
    for i in range(n):
        if item["family"] == "cedar":
            w, r, ops = perturb_cedar(item, rng)
            out.append({"world": w, "request": r, "ops": ops, "q": {}})
        elif item["family"] == "k8s":
            w, r, ops = perturb_k8s(item, rng)
            out.append({"world": w, "request": r, "ops": ops, "q": {}})
        elif item["family"] == "iam":
            w, r, ops = perturb_iam(item, rng)
            out.append({"world": w, "request": r, "ops": ops, "q": {}})
        else:
            if all(q["target"].get("kind") == "check" for q in item["questions"]):
                break
            q, inst, ops = perturb_alloy(item, rng)
            out.append({"world": inst, "request": None, "ops": ops, "q": q})
    return out


# ------------------------------------------------------------ runners

def check_item(item_id: str) -> dict:
    item = load_item(item_id)
    try:
        env, doc, bindings = load_formalisation(item)
    except VEError as e:
        return {"item": item_id, "stage": "parse", "error": f"{type(e).__name__}: {e}"}
    rows = []
    for q in item["questions"]:
        rows.append({"q": q["description"], **ve_answer(item, env, doc, bindings, q)})
    return {"item": item_id, "stage": "ok", "statements": len(doc.formulas), "answers": rows}


def diff_item(item_id: str, n=N_PERTURB, verbose=False) -> dict:
    item = load_item(item_id)
    t0 = time.time()
    try:
        env, doc, bindings = load_formalisation(item)
    except VEError as e:
        return {"item": item_id, "family": item["family"], "stage": "parse", "error": f"{type(e).__name__}: {e}"}
    orig = []
    for q in item["questions"]:
        ve = ve_answer(item, env, doc, bindings, q)
        ref = ref_answer(item, q)
        orig.append({"q": q["description"], "ve": ve["answer"], "ve_status": ve["status"], "ref": ref,
                     "recorded": q.get("recorded_decision"), **({"detail": ve["detail"]} if "detail" in ve else {}),
                     **{k: v for k, v in ve.items() if k.startswith(("prove", "countermodel"))}})
    pert = []
    for p in perturbations(item, n) + targeted_perturbations(item):
        q = p["q"] or {}
        ve = ve_answer(item, env, doc, bindings, q, p["world"], p["request"])
        ref = ref_answer(item, q, p["world"], p["request"])
        pert.append({"ve": ve["answer"], "ve_status": ve["status"], "ref": ref, "ops": p["ops"],
                     **({"detail": ve["detail"]} if "detail" in ve else {}),
                     "world": p["world"] if ve["answer"] != ref else None,
                     "request": p["request"] if ve["answer"] != ref else None,
                     "question": q.get("description")})
    o_ok = sum(r["ve"] == r["ref"] for r in orig)
    p_ok = sum(r["ve"] == r["ref"] for r in pert)
    tgt = [r for r in pert if r["ops"][-1:] in (["key_case"], ["record_extra_key"])]
    rec = [r for r in orig if r["recorded"] in ("allow", "deny")]
    return {"item": item_id, "family": item["family"], "stage": "ok",
            "original": {"agree": o_ok, "total": len(orig)},
            "perturbed": {"agree": p_ok, "total": len(pert),
                          "ref_true": sum(bool(r["ref"]) for r in pert)},
            "targeted": {"agree": sum(r["ve"] == r["ref"] for r in tgt), "total": len(tgt),
                         "ref_true": sum(bool(r["ref"]) for r in tgt)},
            "reference_vs_recorded": {"agree": sum((r["ref"] is True) == (r["recorded"] == "allow") for r in rec),
                                      "total": len(rec)},
            "faithful": o_ok == len(orig) and p_ok == len(pert),
            "statuses": sorted({r["ve_status"] for r in orig + pert}),
            "seconds": round(time.time() - t0, 2),
            "original_rows": orig,
            "mismatches": [r for r in pert if r["ve"] != r["ref"]][:5] + [r for r in orig if r["ve"] != r["ref"]]}


def main(argv):
    cmd, *rest = argv
    ids = sorted(p.name for p in ITEMS.iterdir() if p.is_dir()) if rest in ([], ["all"]) else rest
    if cmd == "check-packet":
        # For independent authors: parse/type-check items/<id>/agent/* and print VE's answers to the
        # review-packet questions. Never touches the reference or any expected answer.
        import os
        os.environ["P3_FORMAL_DIR"] = "agent"
        globals()["FORMAL_SUBDIR"] = "agent"
        for i in rest:
            item = load_item(i)
            try:
                env, doc, bindings = load_formalisation(item)
            except Exception as e:  # noqa: BLE001
                print(json.dumps({"item": i, "error": f"{type(e).__name__}: {e}"}))
                continue
            packet = json.loads((HERE / "review_packets" / f"{i}.json").read_text())
            rows = []
            for q in packet["questions"]:
                if "request" in q:
                    ve = ve_answer(item, env, doc, bindings, {}, item["world"], q["request"])
                else:
                    ve = ve_answer(item, env, doc, bindings, {"target": q["target"]}, q["instance"], None)
                rows.append({"n": q["n"], "answer": ve["answer"], "status": ve["status"], **({"detail": ve["detail"]} if "detail" in ve else {})})
            print(json.dumps({"item": i, "statements": len(doc.formulas), "answers": rows}))
        return
    if cmd == "check":
        for i in ids:
            if (ITEMS / i / "formalisation.ve").exists():
                print(json.dumps(check_item(i)))
    elif cmd == "diff":
        for i in ids:
            if not (ITEMS / i / "formalisation.ve").exists():
                continue
            r = diff_item(i)
            brief = {k: r[k] for k in r if k not in ("original_rows", "mismatches")}
            print(json.dumps(brief))
            for m in r.get("mismatches", [])[:3]:
                print("   MISMATCH", json.dumps({k: m[k] for k in m if k not in ("world",)})[:600])


if __name__ == "__main__":
    main(sys.argv[1:])
