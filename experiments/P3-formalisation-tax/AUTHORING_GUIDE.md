# Authoring guide for independent VE authors (P3)

You are the **untrusted author**: formalise one source artefact in Verifiable
English (VE) so that a checker can answer the item's questions by evaluating your
VE on a finite model. You will be scored by differential testing against an
independent evaluator of the source language, on the item's questions and on
hundreds of randomly perturbed worlds you do not see. Formalise the **source
semantics**, not just the sample answers.

## What to write

Three files in `items/<id>/agent/`:

* `environment.json`: the VE vocabulary (sorts, predicates, constants) you use.
* `formalisation.ve`: statement 0 must be TRUE exactly when the answer is
  "allow" (Cedar/K8s/IAM) or "the target paragraph holds" (Alloy).
* `bindings.json`: maps your extra constants to world values (see below); `{}` if none.

Check your work with (from `/Users/seyran/code/ve-opus-p3`):

```sh
cd experiments/P3-formalisation-tax && UV_CACHE_DIR=/private/tmp/ve-uv-cache-p3 uv run python harness.py check-packet <id>
```

It parses and type-checks your files and prints VE's answer to each packet
question (no expected answers are shown). Parse/type errors come back as
messages. Iterate as often as you like, but **count** the runs that returned an
error, and report the count.

## VE syntax (strict; one statement per line, each ending with `.` and a newline)

```text
formula = true | false
        | t is p                     (unary predicate p)
        | t r u                      (binary predicate r)
        | t equals u
        | not (F)
        | (F) and (G)   | (F) or (G)  | if (F), then (G)
        | for every S x, (F)  | there exists S x, (F)
        | tc[r](t, u)   | rtc[r](t, u)                    (closure of a homogeneous binary predicate r)
        | tc[S a, b | (F)](t, u)  | rtc[S a, b | (F)](t, u)  (closure of the edge a->b defined by F)
term    = variable | @constant
```

* Connectives are binary and fully parenthesised: `(A) and ((B) and (C))`.
* `tc` = one or more steps (transitive closure), `rtc` = zero or more (reflexive
  transitive). `tc[r](t, u)` means u is reachable FROM t: t r x1, x1 r x2, ..., xk r u.
* In the body form, `a` is the step source and `b` the destination; the body may
  mention outer variables and constants.
* Identifiers: `[a-z][a-z0-9_]*`; variables must not reuse a constant or
  predicate name; no shadowing. Reserved: true false is equals not and or if then
  for every there exists believes must eventually.
* Semantics: classical first-order logic over the finite model; closed world
  inside the model (absent tuple = false). Constants may denote the same element
  unless the model says otherwise (in evaluation they denote what `bindings` say).

Environment file shape (declare only what you use; every predicate needs `arguments` and `description`):

```json
{"language": "ve.core@0.1", "profiles": ["closure@0", "relational-fol@0"],
 "spec_revision": "ve-v0.1-closure-2026-09-21",
 "vocabulary": {
   "sorts": {"entity": {"description": "..."}},
   "predicates": {"parent": {"arguments": ["entity", "entity"], "description": "..."}},
   "constants": {"principal": {"sort": "entity", "description": "..."}}}}
```

Predicate and sort names must be exactly the fixed encoding's names below; the
model is built mechanically from the world and only contains those relations.

## Fixed encodings of the world (the model you evaluate on)

### Cedar (sorts `entity`, `value`)

```text
parent(e, p)          immediate parent edge (entity store parents; action groups from the schema)
type_<t>(e)           entity type tag; <t> = lower-cased type with non-alphanumerics as "_" (PhotoApp::User -> type_photoapp_user)
has_<a>(o)            attribute a is present on o (entity, record node, or the context node)
ea_<a>(o, e)          entity-valued or record-valued attribute (records become anonymous record nodes)
sa_<a>(o, v)          string / long / extension-valued attribute (value sort)
bt_<a>(o) / bf_<a>(o) Boolean attribute present and true / present and false
es_<a>(o, e)          member of an entity-set or record-set attribute
ss_<a>(o, v)          member of a string/long set attribute
type_record(r)        r is an anonymous record node
nattrs_<n>(r)         record node r has exactly n attributes (Cedar record equality needs equal key sets)
                      [added after the review of 2026-09-22; not in the brief the independent authors saw]
<a> = attribute name lower-cased, non-alphanumerics -> "_" (isPrivate -> isprivate, "Role-A" -> role_a)
Constants always available: principal, action, resource (entity), context (entity: the context record node).
```

Extra constants go in `bindings.json`:
`{"constants": {"jane": {"entity": "User::\"jane\""}, "s_view": {"value": "view"}}}` —
an entity UID exactly as in the source, or a literal value (string or number).
Entities referenced but absent from the store still exist in the `entity` domain
(no attributes, no parents). The request's principal/action/resource are always
in the domain.

### Kubernetes RBAC (sorts `role`, `binding`, `rule`, `sel`, `str`)

```text
is_role / is_clusterrole(role); role_name(role, str); role_ns(role, str)
role_label(role, str "key=value"); has_aggregation(role)
role_selector(role, sel); sel_label(sel, str "key=value")   (one sel per clusterRoleSelectors entry, its matchLabels)
role_rule(role, rule)  (the rules field as written)
rule_verb / rule_group / rule_resource / rule_resname(rule, str)
is_rolebinding / is_clusterrolebinding(binding); binding_ns(binding, str)
ref_role / ref_clusterrole(binding); ref_name(binding, str)
subject_user / subject_group(binding, str)
req_group(str): a group of the requesting user
Constants: user, verb, apigroup, resource, subresource, path ("resource/subresource", or resource if none),
namespace ("" for a cluster-scoped request), name ("" if none), star ("*"), empty (""); extra string
constants via bindings {"constants": {"k": {"value": "..."}}}.
```

### AWS IAM (sorts `stmt`, `cond`, `str`)

```text
allow_stmt / deny_stmt(stmt); uses_action / uses_notaction / uses_resource / uses_notresource(stmt)
action_pat(stmt, str)    patterns under Action or NotAction
resource_pat(stmt, str)  patterns under Resource or NotResource
stmt_cond(stmt, cond); cond_op(cond, str operator); cond_key(cond, str); cond_value(cond, str)  (one cond per operator+key)
ctx(str key, str value)  request context
                      Key names (cond_key, ctx, ${var}) are case-insensitive in IAM and are encoded lower-cased
                      [added after the review of 2026-09-22]
action_glob(str p)    ADAPTER: pattern p matches the request action (case-insensitive * ? glob)
resource_glob(str p)  ADAPTER: pattern p, after ${var} substitution from the context, matches the request resource
                      (case-sensitive glob; false if a variable is missing)
Constants: none built in; add string constants via bindings {"constants": {"k": {"value": "StringEquals"}}}.
```

### Alloy (sorts `atom`, `tuple`)

```text
sig_<S>(atom)                 atom belongs to signature S (<S> lower-cased: Node -> sig_node)
f_<f>(atom, atom)             binary field f as (owner, value) pairs, e.g. marked: HeapState -> set Node
t_<f>_1 / _2 / _3(tuple, atom) ternary field f, one tuple node per tuple (reification)
Constants: every instance binding whose value is an atom, named by the parameter with primes " or '
written _p (hs" -> hs_p); a binding naming a field (e.g. r = edges) is not a constant: use f_edges.
```

## Source semantics to apply

Cedar: allow iff some permit is satisfied and no forbid is satisfied; `in` is
reflexive-transitive over entity parents (`in [A, B]`: in any of them); a policy
whose condition raises an evaluation error (e.g. accessing a missing attribute) is
skipped. Kubernetes RBAC: the standard authorizer, including ClusterRole
aggregation. AWS IAM: explicit deny > allow > implicit deny with the documented
condition-operator semantics. Alloy: standard relational semantics.
