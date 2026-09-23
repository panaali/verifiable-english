"""D-gate: build the artefact copies and the item file (no model calls, no network).

    CEDAR=/path/to/cedar DGATE_DATA=~/code/ve-claude/data python3 build_items.py

Inputs: the 29 P3 artefacts (experiments/P3-formalisation-tax/items/{c*,k*}) and the pinned
upstream clones listed in data/README.md (only for the Cedar schemas and template links; the
policy text is checked byte-for-byte against upstream). Outputs:

  artefacts/<id>/source.cedar | source.yaml   verbatim artefact (copied from P3)
  artefacts/<id>/schema.cedarschema           verbatim upstream schema (Cedar)
  artefacts/<id>/analysis.cedar               templated artefacts only: the policy set Cedar evaluates,
                                              static policies plus every upstream link instantiated
  artefacts/<id>/world.json                   the RBAC objects (K8s; verbatim + labelled filler)
  artefacts/<id>/edit-<item>.cedar|.json      a planted single edit, for edited items
  items.json                                  item definitions (question, domain, assumptions,
                                              reference-verifier encoding); no answers

The `cedar` CLI is used only to translate policies to JSON and back when instantiating template
links (`translate-policy`) and to list request environments (`translate-schema`).
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
P3 = HERE.parent / "P3-formalisation-tax" / "items"
ART = HERE / "artefacts"
DATA = Path(os.path.expanduser(os.environ.get("DGATE_DATA", "~/code/ve-claude/data")))
CEDAR = os.environ.get("CEDAR", "cedar")

CEDAR_DOMAIN = (
    "All authorization requests and entity stores that are valid for the stated Cedar schema "
    "(any number of entities, any attribute values of the declared types, any parent edges the "
    "schema's `in` declarations allow; request context as declared per action; action entities and "
    "action groups exactly as declared in the schema). Every referenced entity exists in the entity "
    "store: the request's principal and resource, every entity in the request context, and every "
    "entity named by an attribute or a parent edge of a stored entity. Cedar 4 semantics: default deny, any "
    "applicable forbid overrides every permit, and a policy whose condition raises an error "
    "(e.g. missing attribute, overflow) is ignored."
)
K8S_DOMAIN = (
    "All Kubernetes resource requests (any user name, any list of groups, any verb, API group, "
    "resource, subresource (possibly empty; resource and subresource contain no '/'), namespace (empty for cluster-scoped or all-namespace "
    "requests) and object name (empty when the request names no object; get, update, patch and delete "
    "requests name one, and list and watch requests may name one through a metadata.name field selector)); "
    "non-resource URLs are excluded. RBAC "
    "authorizer semantics: allow iff some binding's subject matches and some rule of the bound "
    "role matches; RoleBindings apply only to requests in their own namespace."
)
K8S_ASSUMPTIONS = (
    "Closed world: exactly the listed RBAC objects exist. No bootstrap roles or bindings (e.g. "
    "cluster-admin bound to system:masters), no other authorizer. The ClusterRole aggregation "
    "controller has converged (an aggregated ClusterRole's rules are the union of the rules of every "
    "other ClusterRole whose labels match one of its selectors, transitively)."
)

# ----------------------------------------------------------------------------------------------
# Cedar items. kind:
#   only_if  every ALLOWED request (in the listed request environments) satisfies phi
#            encoded as SymCC implies(artefact, {permit(principal,action,resource) when {phi};})
#   if       every request satisfying phi (in the environments) is ALLOWED
#            encoded as SymCC implies({permit ... when {phi};}, artefact)
# Answer YES iff the implication holds in every environment. `actions` lists action ids whose
# schema appliesTo lists are expanded into (principal type, action, resource type) environments;
# "all" means every action with a non-empty appliesTo. Optional principal/resource type filters.
# ----------------------------------------------------------------------------------------------
C = []
# restriction: "every allowed request satisfies phi" (a necessary condition for access; a wrong YES on a
#              NO item is a false approval of unsafe access)
# guarantee:   "every request satisfying phi is allowed" (a sufficient condition for access; a wrong YES
#              on a NO item overstates availability, not safety)
DIRECTION = {"only_if": "restriction", "if": "guarantee"}


def cedar(id, art, question, kind, phi, actions="all", principal_types=None, resource_types=None,
          edit=None, tags=(), assumptions=""):
    C.append(dict(id=id, artefact=art, family="cedar", question=question, kind=kind, phi=phi,
                  actions=actions, principal_types=principal_types, resource_types=resource_types,
                  edit=edit, tags=list(tags), extra_assumptions=assumptions))


cedar("D01", "c01_cit_1a",
      "Is every allowed request exactly User::\"alice\" performing Action::\"view\" on Photo::\"VacationPhoto94.jpg\"?",
      "only_if", 'principal == User::"alice" && action == Action::"view" && resource == Photo::"VacationPhoto94.jpg"',
      tags=["control"])
cedar("D02", "c02_cit_2a",
      "Is every principal that is ever allowed any action a (direct or transitive) member of UserGroup::\"jane_friends\"?",
      "only_if", 'principal in UserGroup::"jane_friends"')
cedar("D03", "c02_cit_2a",
      "Is every principal that is ever allowed any action a (direct or transitive) member of UserGroup::\"jane_friends\"?",
      "only_if", 'principal in UserGroup::"jane_friends"',
      edit=dict(description="scope widened to any principal; group test moved into a condition that also admits Administrators",
                replace=[['principal in UserGroup::"jane_friends",', "principal,"],
                         [');', ')\nwhen { principal in UserGroup::"jane_friends" || principal is Administrator };']]),
      tags=["planted-edit"])
cedar("D04", "c03_cit_2b",
      "Is every resource that User::\"alice\" is ever allowed to view a Photo (never a Video)?",
      "only_if", 'resource is Photo', actions=["view"])
cedar("D05", "c04_cit_2c",
      "Is every allowed request whose resource is a Video an Action::\"view\" request?",
      "only_if", '!(resource is Video) || action == Action::"view"')
cedar("D06", "c05_cit_3a",
      "Is it true that no Administrator is ever allowed any action?",
      "only_if", '!(principal is Administrator)')
cedar("D07", "c06_cit_3b",
      "Is it true that User::\"alice\" is never allowed Action::\"listAlbums\"?",
      "only_if", 'action != Action::"listAlbums"')
cedar("D08", "c06_cit_3b",
      "Is every resource that User::\"alice\" is allowed to view outside Account::\"bob\" (not a descendant of it)?",
      "only_if", '!(resource in Account::"bob")', actions=["view"])
cedar("D09", "c08_cit_4a",
      "Is every User whose department is \"HardwareEngineering\" and whose jobLevel is at least 5 allowed Action::\"listPhotos\" on Album::\"device_prototypes\" itself?",
      "if", 'principal.department == "HardwareEngineering" && principal.jobLevel >= 5 && resource == Album::"device_prototypes"',
      actions=["listPhotos"])
cedar("D10", "c09_cit_4d",
      "For every Account, is the Account's owner allowed Action::\"listAlbums\" on that Account?",
      "if", 'principal == resource.owner', actions=["listAlbums"])
cedar("D11", "c10_cit_4e",
      "Is every User allowed to view every Photo whose account they own (principal == resource.account.owner)?",
      "if", 'principal == resource.account.owner', actions=["view"])
cedar("D12", "c11_cit_4f",
      "Is every User who is listed in an Account's `admins` allowed Action::\"delete\" on every Photo whose `account` is that Account?",
      "if", 'resource.account.admins.contains(principal)', actions=["delete"])
cedar("D13", "c12_cit_5b",
      "Is every allowed Action::\"addPhoto\" request for a photo larger than 1 MB (filesize_mb > 1) made by a member of UserGroup::\"AVTeam\"?",
      "only_if", 'context.photo.filesize_mb <= 1 || principal in UserGroup::"AVTeam"', actions=["addPhoto"])
cedar("D14", "c13_document_cloud",
      "Is every allowed request of any kind on a Document whose isPrivate is true made by that Document's owner?",
      "only_if", '!resource.isPrivate || principal == resource.owner', resource_types=["Document"])
cedar("D15", "c13_document_cloud",
      "Is every allowed request of any kind on a Document whose isPrivate is true made by that Document's owner?",
      "only_if", '!resource.isPrivate || principal == resource.owner', resource_types=["Document"],
      edit=dict(description="the last policy (forbid non-owners on private documents) deleted",
                replace=[["""forbid (principal, action, resource)
when
{
  resource has owner &&
  principal != resource.owner &&
  resource has isPrivate &&
  resource.isPrivate
};""", ""]]),
      tags=["planted-edit"])
cedar("D16", "c14_github",
      "Is every principal allowed Action::\"edit_issue\" on an Issue either in the issue's repository writers group or the issue's reporter?",
      "only_if", 'principal in resource.repo.writers || principal == resource.reporter', actions=["edit_issue"])
cedar("D17", "c14_github",
      "Is every principal allowed Action::\"edit_issue\" on an Issue either in the issue's repository writers group or the issue's reporter?",
      "only_if", 'principal in resource.repo.writers || principal == resource.reporter', actions=["edit_issue"],
      edit=dict(description="writers edit_issue policy now tests resource.repo.readers",
                replace=[["""  action == Action::"edit_issue",
  resource
)
when { principal in resource.repo.writers };""", """  action == Action::"edit_issue",
  resource
)
when { principal in resource.repo.readers };"""]]),
      tags=["planted-edit"])
cedar("D18", "c15_hotel_static",
      "Is every User whose hotelAdminPermissions contains Hotel H allowed Action::\"grantAccessHotel\" on H?",
      "if", 'principal.hotelAdminPermissions.contains(resource)',
      actions=["grantAccessHotel"])
cedar("D19", "c15_hotel_static",
      "Is every User whose hotelAdminPermissions contains Hotel H allowed Action::\"grantAccessHotel\" on H?",
      "if", 'principal.hotelAdminPermissions.contains(resource)',
      actions=["grantAccessHotel"],
      edit=dict(description="parentheses added to the last admin condition",
                replace=[["""  resource in principal.hotelAdminPermissions ||
  resource is Property &&
  resource in principal.propertyAdminPermissions
};""", """  (resource in principal.hotelAdminPermissions ||
  resource is Property) &&
  resource in principal.propertyAdminPermissions
};"""]]),
      tags=["planted-edit"])
cedar("D20", "c16_hotel_templated",
      "With exactly the six upstream template links, is it true that User::\"Alice\" is never allowed Action::\"createReservation\"?",
      "only_if", 'principal != User::"Alice"', actions=["createReservation"])
cedar("D21", "c17_sales_static",
      "Is every allowed Action::\"grantEditAccessToTemplate\" request one whose context has a targetUser whose job is Job::\"internal\"?",
      "only_if", 'context has targetUser && context.targetUser.job == Job::"internal"', actions=["grantEditAccessToTemplate"])
cedar("D22", "c17_sales_static",
      "Is every allowed Action::\"grantViewAccessToPresentation\" request whose target has job Job::\"customer\" made by a distributor (job Job::\"distributor\") with the same customerId as the target?",
      "only_if", 'context.target.job != Job::"customer" || (principal.job == Job::"distributor" && principal.customerId == context.target.customerId)',
      actions=["grantViewAccessToPresentation"])
cedar("D23", "c18_sales_templated",
      "With exactly the two upstream template links, is User::\"Bob\" allowed Action::\"viewPresentation\" on Presentation::\"proposal\" whatever his job?",
      "if", 'principal == User::"Bob" && resource == Presentation::"proposal"', actions=["viewPresentation"])
cedar("D24", "c18_sales_templated",
      "With exactly the two upstream template links, is User::\"Bob\" allowed Action::\"duplicatePresentation\" on Presentation::\"proposal\" whatever his job?",
      "if", 'principal == User::"Bob" && resource == Presentation::"proposal"', actions=["duplicatePresentation"])
cedar("D25", "c19_streaming",
      "Is it true that no FreeMember is ever allowed to watch an early-access Show before its releaseDate (context.now.datetime < resource.releaseDate)?",
      "only_if", '!(resource.isEarlyAccess && context.now.datetime < resource.releaseDate)',
      actions=["watch"], principal_types=["FreeMember"], resource_types=["Show"])
cedar("D26", "c19_streaming",
      "Is every allowed watch request by a Subscriber whose profile isKid one whose local time is defined and lies between 06:00 and 21:00 inclusive? "
      "The local time is the time of day of context.now.datetime offset by context.now.localTimeOffset, computed as Cedar computes it; "
      "it is defined only if that computation raises no error, and a request whose local time is undefined does not satisfy the property.",
      "only_if", '!principal.profile.isKid || (duration("6h") <= context.now.datetime.offset(context.now.localTimeOffset).toTime() && context.now.datetime.offset(context.now.localTimeOffset).toTime() <= duration("21h"))',
      actions=["watch"], principal_types=["Subscriber"], tags=["edge", "edge-error-semantics"])
cedar("D27", "c19_streaming",
      "Is every allowed Action::\"rent\" request made at a time (context.now.datetime) at or after 2025-02-02T19:00:00-0500 and before 2025-03-02T19:00:00-0500?",
      "only_if", 'context.now.datetime >= datetime("2025-02-02T19:00:00-0500") && context.now.datetime < datetime("2025-03-02T19:00:00-0500")',
      actions=["rent"])
cedar("D28", "c20_tags_n_roles",
      "Is every principal ever allowed Action::\"DeleteWorkspace\" in Role::\"Role-A\"?",
      "only_if", 'principal in Role::"Role-A"', actions=["DeleteWorkspace"])
cedar("D29", "c21_tax_preparer",
      "With exactly the upstream template link, is every allowed viewDocument request one whose context.consent.client is the document's owner?",
      "only_if", 'context.consent.client == resource.owner', actions=["viewDocument"])
cedar("D30", "c21_tax_preparer",
      "With exactly the upstream template link, is every allowed viewDocument request one whose context.consent.client is the document's owner?",
      "only_if", 'context.consent.client == resource.owner', actions=["viewDocument"],
      edit=dict(description="consent forbid's `unless` conjunction changed to a disjunction",
                replace=[["""  context.consent.client == resource.owner &&
  context.consent.team_region_list.contains(principal.location)""",
                          """  context.consent.client == resource.owner ||
  context.consent.team_region_list.contains(principal.location)"""]]),
      tags=["planted-edit"])
cedar("D31", "c22_photoapp",
      "Is every allowed request on a Photo whose labels contain \"private\" made by that Photo's owner?",
      "only_if", '!resource.labels.contains("private") || principal == resource.owner')
cedar("D32", "c22_photoapp",
      "Is every allowed request on a Photo whose labels contain \"private\" made by that Photo's owner?",
      "only_if", '!resource.labels.contains("private") || principal == resource.owner',
      edit=dict(description="scope of the label_private forbid widened from `resource in PhotoApp::Application::\"PhotoApp\"` to any resource",
                replace=[["""forbid (
  principal,
  action,
  resource in PhotoApp::Application::"PhotoApp"
)""", """forbid (
  principal,
  action,
  resource
)"""]]),
      tags=["planted-edit"])
cedar("D33", "c23_gitapp",
      "Is every User listed in a Repo's `admins` allowed GitApp::Action::\"addRepoAdmin\" on that Repo?",
      "if", 'resource.admins.contains(principal)', actions=["addRepoAdmin"])
cedar("D34", "c23_gitapp",
      "Is every principal allowed GitApp::Action::\"pushRepo\" on a Repo listed in that Repo's `admins` or `contributors`?",
      "only_if", 'resource.admins.contains(principal) || (resource has contributors && resource.contributors.contains(principal))',
      actions=["pushRepo"],
      edit=dict(description="the contributors_Repo policy's condition now tests `reporters`",
                replace=[["""  resource in GitApp::Application::"GitApp"
)
when { resource has contributors && principal in resource.contributors };""", """  resource in GitApp::Application::"GitApp"
)
when { resource has reporters && principal in resource.reporters };"""]],
                occurrence=2),
      tags=["planted-edit"])

# ----------------------------------------------------------------------------------------------
# Kubernetes items. `z3` is a Z3 Python expression over the request variables
#   user verb api res sub ns name : String;  grp(g) : String -> Bool (group membership)
# and `allowed` (the encoded authorizer). YES iff the expression is valid (its negation unsat).
# ----------------------------------------------------------------------------------------------
K = []


def k8s(id, art, question, z3, edit=None, tags=(), direction="restriction"):
    K.append(dict(id=id, artefact=art, family="k8s", question=question, z3=z3, edit=edit, tags=list(tags),
                  direction=direction))


k8s("D35", "k01_pod_reader",
    "Is it true that no request for a pod subresource (e.g. pods/log) is ever allowed?",
    "Implies(allowed, sub == '')")
k8s("D36", "k02_secret_reader_rolebinding",
    "Is every allowed request made in namespace \"development\" (in particular, no all-namespace or cluster-scoped request is allowed)?",
    "Implies(allowed, ns == 'development')")
k8s("D37", "k03_secret_reader_global",
    "Is every member of group \"manager\" allowed to list secrets (core API group, no subresource) across all namespaces, i.e. with an empty namespace?",
    "Implies(And(grp('manager'), verb == 'list', api == '', res == 'secrets', sub == '', ns == '', name == ''), allowed)",
    direction="guarantee")
k8s("D38", "k04_monitoring_aggregation",
    "Is it true that no request on secrets (any verb, any namespace) is ever allowed?",
    "Implies(allowed, res != 'secrets')")
k8s("D39", "k04_monitoring_aggregation",
    "Is it true that no request on secrets (any verb, any namespace) is ever allowed?",
    "Implies(allowed, res != 'secrets')",
    edit=dict(description="a new ClusterRole secret-reader (get/list/watch on secrets) carrying the label rbac.example.com/aggregate-to-monitoring: \"true\" is added",
              add_objects=[{"kind": "ClusterRole",
                            "metadata": {"name": "secret-reader",
                                         "labels": {"rbac.example.com/aggregate-to-monitoring": "true"}},
                            "rules": [{"apiGroups": [""], "resources": ["secrets"], "verbs": ["get", "list", "watch"]}]}]),
    tags=["planted-edit"])
k8s("D40", "k05_crontab_default_roles",
    "Is every allowed request to delete crontabs made by user \"ana\" (bound to admin)?",
    "Implies(And(allowed, verb == 'delete', res == 'crontabs'), user == 'ana')")
k8s("D41", "k05_crontab_default_roles",
    "Is every allowed request made by user \"vic\" (bound to view) a get, list or watch?",
    "Implies(And(allowed, user == 'vic'), Or(verb == 'get', verb == 'list', verb == 'watch'))")
k8s("D42", "k06_configmap_updater",
    "Is it true that user \"ci-bot\" is never allowed to list configmaps?",
    "Implies(And(allowed, user == 'ci-bot'), verb != 'list')",
    edit=dict(description="verb \"list\" added to the configmap-updater rule (resourceNames kept)",
              set=[[["objects", 0, "rules", 0, "verbs"], ["update", "get", "list"]]]),
    tags=["planted-edit", "edge", "edge-field-selector"])
k8s("D43", "k07_subresource_wildcard",
    "Is every allowed request that names a subresource a request for pods/log in the core API group?",
    "Implies(And(allowed, sub != ''), And(res == 'pods', sub == 'log', api == ''))")


# ----------------------------------------------------------------------------------------------
# What VE can express today (see README "VE coverage"). Default: closure@0 (relational FOL with
# transitive closure; attributes, sets and records reified as predicates; background schema axioms
# for universal claims, as P3 needed for c13).
# ----------------------------------------------------------------------------------------------
GUARDS = "closure@0 + hand-encoded Cedar error/`has` guards"
VE_COVERAGE = {
    "D09": ("closure@0 x order@0", "jobLevel >= 5 together with the `in Album` hierarchy; order@0 is built but gated off and the closure x order gate theorem is pending"),
    "D10": (GUARDS, "Account has no `account` attribute: the `has` guard decides the answer"),
    "D12": (GUARDS, "Photo.account.admins vs Photo.admins; `has account` guard"),
    "D13": ("closure@0 x order@0", "filesize_mb <= 1 / <= 100 together with `in UserGroup` and `in Account`; gated as D09"),
    "D14": (GUARDS, "`has owner` / `has isPrivate` guards; P3 needed schema axioms to prove this property (146 steps)"),
    "D15": (GUARDS, "as D14"),
    "D21": (GUARDS, "optional `targetUser` (`context has targetUser`)"),
    "D25": ("order@0 + datetime adapter", "datetime comparison only (no hierarchy); VE has no datetime type, so datetimes become integers through an OPAQUE-style adapter"),
    "D26": ("not expressible", "datetime.offset(...).toTime() is arithmetic modulo one day, and the answer turns on 64-bit overflow errors that make the forbid policy error and be ignored"),
    "D27": ("order@0 + datetime adapter", "datetime literal bounds; as D25"),
    "D28": (GUARDS, "optional record attributes and Set<String> containsAll in the policy (P3 c20 needed a type-error guard)"),
    "D31": (GUARDS, "optional `subjects`; string-literal set membership reified as a label predicate"),
    "D32": (GUARDS, "as D31"),
    "D33": (GUARDS, "optional `contributors`/`reporters`"),
    "D34": (GUARDS, "as D33"),
    "D38": ("closure@0", "aggregation is a closure whose edge contains a label-subset test; P3's k05 aggregation proof hit ResourceLimit, so certification is untested"),
    "D39": ("closure@0", "as D38"),
    "D40": ("closure@0", "as D38 (k05 itself)"),
    "D41": ("closure@0", "as D38 (k05 itself)"),
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(args, stdin=None):
    return subprocess.run([CEDAR, *args], input=stdin, capture_output=True, text=True, check=True).stdout


def uid_json(s):
    # namespaced types (A::B::"id"): split on the last `::"`
    i = s.rindex('::"')
    return {"type": s[:i], "id": json.loads(s[i + 2:])}


def instantiate_links(policy_text, links):
    """Static policies + one static copy of each linked template (slots replaced); unlinked
    templates are dropped (they cannot apply)."""
    ps = json.loads(run(["translate-policy", "--direction", "cedar-to-json"], stdin=policy_text))
    static = dict(ps.get("staticPolicies") or {})
    for link in links:
        t = copy.deepcopy(ps["templates"][link["template_id"]])
        for var in ("principal", "resource"):
            c = t[var]
            if "slot" in c:
                c.pop("slot")
                c["entity"] = uid_json(link["args"]["?" + var])
        t.setdefault("annotations", {})["id"] = link["link_id"]
        static[link["link_id"]] = t
    return run(["translate-policy", "--direction", "json-to-cedar"],
               stdin=json.dumps({"staticPolicies": static, "templates": {}, "templateLinks": []}))


def apply_replace(text, pairs, occurrence=None):
    for old, new in pairs:
        n = text.count(old)
        if occurrence is None:
            assert n == 1, (old, n)
            text = text.replace(old, new)
        else:
            assert n >= occurrence, (old, n)
            i = -1
            for _ in range(occurrence):
                i = text.index(old, i + 1)
            text = text[:i] + new + text[i + len(old):]
    return text


def schema_actions(schema_path):
    j = json.loads(run(["translate-schema", "--direction", "cedar-to-json", "-s", str(schema_path)]))
    (ns, body), = j.items()
    pre = f"{ns}::" if ns else ""
    envs = {}
    for a, spec in body["actions"].items():
        at = spec.get("appliesTo") or {}
        pts = [t if "::" in t else pre + t for t in at.get("principalTypes") or []]
        rts = [t if "::" in t else pre + t for t in at.get("resourceTypes") or []]
        if pts and rts:
            envs[a] = (pts, rts)
    return pre, envs


def main():
    ART.mkdir(exist_ok=True)
    artefacts = {}
    for d in sorted(P3.iterdir()):
        if not d.name[:1] in "ck" or not (d / "item.json").exists():
            continue
        item = json.loads((d / "item.json").read_text())
        prov = item["provenance"]
        out = ART / d.name
        out.mkdir(exist_ok=True)
        rec = {"id": d.name, "family": item["family"], "provenance": prov}
        if item["family"] == "cedar":
            repo = DATA / prov["repository"].split("/")[1]
            up_pol = repo / prov["policy_path"]
            assert sha(up_pol) == sha(d / "source.cedar"), f"{d.name}: P3 copy differs from upstream"
            schema_rel = prov.get("schema_path") or prov["policy_path"].replace(".cedar", ".cedarschema")
            shutil.copyfile(d / "source.cedar", out / "source.cedar")
            shutil.copyfile(repo / schema_rel, out / "schema.cedarschema")
            src = (d / "source.cedar").read_text()
            links = item["world"].get("linked") or []
            if links:
                (out / "analysis.cedar").write_text(instantiate_links(src, links))
            rec.update(schema_path=schema_rel, links=links,
                       sha256={"source.cedar": sha(out / "source.cedar"),
                               "schema.cedarschema": sha(out / "schema.cedarschema")})
        else:
            shutil.copyfile(d / "source.yaml", out / "source.yaml")
            (out / "world.json").write_text(json.dumps(item["world"], indent=1) + "\n")
            rec.update(synthetic_objects=[o["metadata"]["name"] for o in item["world"]["objects"] if o.get("synthetic")],
                       sha256={"source.yaml": sha(out / "source.yaml")})
        artefacts[d.name] = rec
    assert sum(r["family"] == "cedar" for r in artefacts.values()) == 22
    assert sum(r["family"] == "k8s" for r in artefacts.values()) == 7

    items = []
    for it in C:
        it = dict(it)
        a = artefacts[it["artefact"]]
        base = ART / it["artefact"]
        pre, envs = schema_actions(base / "schema.cedarschema")
        shown_file = "source.cedar"
        policy_file = "analysis.cedar" if a.get("links") else "source.cedar"
        if it["edit"]:
            # edits apply to the source form; linked artefacts are then re-instantiated
            e = it["edit"]
            shown_file = policy_file = f"edit-{it['id']}.cedar"
            edited = apply_replace((base / "source.cedar").read_text(), e["replace"], e.get("occurrence"))
            (base / shown_file).write_text(edited)
            if a.get("links"):
                policy_file = f"edit-{it['id']}.analysis.cedar"
                (base / policy_file).write_text(instantiate_links(edited, a["links"]))
        names = sorted(envs) if it["actions"] == "all" else it["actions"]
        env_list = []
        for n in names:
            pts, rts = envs[n]
            for p in pts:
                if it["principal_types"] and p.split("::")[-1] not in it["principal_types"]:
                    continue
                for r in rts:
                    if it["resource_types"] and r.split("::")[-1] not in it["resource_types"]:
                        continue
                    env_list.append([p, f'{pre}Action::{json.dumps(n)}', r])
        assert env_list, it["id"]
        items.append(dict(
            id=it["id"], artefact=it["artefact"], cluster=it["artefact"], family="cedar",
            variant="planted-edit" if it["edit"] else "original",
            direction=DIRECTION[it["kind"]],
            edit_description=(it["edit"] or {}).get("description"),
            question=it["question"] + " Answer YES or NO.",
            domain=CEDAR_DOMAIN,
            assumptions="The schema shown is the artefact's upstream schema, verbatim, and every entity store is valid for it."
            + (" Exactly the template links shown exist (they are the upstream links); a template without a link has no effect." if a.get("links") else "")
            + (" " + it["extra_assumptions"] if it["extra_assumptions"] else ""),
            shown_to_model=dict(policy=f"artefacts/{it['artefact']}/{shown_file}",
                                schema=f"artefacts/{it['artefact']}/schema.cedarschema",
                                template_links=a.get("links") or None),
            verifier=dict(name="Cedar SymCC (cedar-policy-cli 4.13.0 `cedar symcc`, cvc5 1.4.0)",
                          kind=it["kind"], policies=f"artefacts/{it['artefact']}/{policy_file}",
                          property_policy=f"permit (principal, action, resource) when {{ {it['phi']} }};",
                          environments=env_list),
            tags=it["tags"],
            ve_coverage=dict(zip(("category", "note"), VE_COVERAGE.get(it["id"], ("closure@0", ""))))))
    for it in K:
        base = ART / it["artefact"]
        world_file = "world.json"
        if it["edit"]:
            w = json.loads((base / "world.json").read_text())
            for o in it["edit"].get("add_objects", []):
                w["objects"].append(o)
            for path, val in it["edit"].get("set", []):
                t = w
                for k in path[:-1]:
                    t = t[k]
                t[path[-1]] = val
            world_file = f"edit-{it['id']}.json"
            (base / world_file).write_text(json.dumps(w, indent=1) + "\n")
        items.append(dict(
            id=it["id"], artefact=it["artefact"], cluster=it["artefact"], family="k8s",
            variant="planted-edit" if it["edit"] else "original",
            direction=it["direction"],
            edit_description=(it["edit"] or {}).get("description"),
            question=it["question"] + " Answer YES or NO.",
            domain=K8S_DOMAIN, assumptions=K8S_ASSUMPTIONS,
            shown_to_model=dict(policy=f"artefacts/{it['artefact']}/{world_file}", render="YAML, one document per object, synthetic flags removed"),
            verifier=dict(name="Z3 5.1.0 (z3-solver, string theory) over a direct Python encoding of the RBAC authorizer",
                          policies=f"artefacts/{it['artefact']}/{world_file}", property=it["z3"]),
            tags=it["tags"],
            ve_coverage=dict(zip(("category", "note"), VE_COVERAGE.get(it["id"], ("closure@0", ""))))))
    (HERE / "artefacts.json").write_text(json.dumps(artefacts, indent=1) + "\n")
    (HERE / "items.json").write_text(json.dumps(items, indent=1) + "\n")
    print(f"{len(artefacts)} artefacts, {len(items)} items "
          f"({sum(i['family'] == 'cedar' for i in items)} Cedar, {sum(i['family'] == 'k8s' for i in items)} K8s, "
          f"{sum(i['variant'] == 'planted-edit' for i in items)} planted edits)")


if __name__ == "__main__":
    main()
