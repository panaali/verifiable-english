"""Kubernetes RBAC, AWS IAM and Alloy items (see build_items.py).

Kubernetes objects are the documentation's YAML, transcribed field-for-field to
JSON (the YAML is kept verbatim as the source). Requests, and any object marked
``"synthetic": true``, are filler written for this experiment and labelled.
Alloy instances are synthetic finite instances for real model paragraphs.
"""
from __future__ import annotations

from pathlib import Path

from build_items import ALLOY, AWS, DATA, FETCHED, K8S

K8S_DOC = "content/en/docs/reference/access-authn-authz/rbac.md"
K8S_EX = "content/en/examples/access/"

POD_READER = {"kind": "Role", "metadata": {"namespace": "default", "name": "pod-reader"},
              "rules": [{"apiGroups": [""], "resources": ["pods"], "verbs": ["get", "watch", "list"]}]}
READ_PODS = {"kind": "RoleBinding", "metadata": {"name": "read-pods", "namespace": "default"},
             "subjects": [{"kind": "User", "name": "jane", "apiGroup": "rbac.authorization.k8s.io"}],
             "roleRef": {"kind": "Role", "name": "pod-reader", "apiGroup": "rbac.authorization.k8s.io"}}
SECRET_READER = {"kind": "ClusterRole", "metadata": {"name": "secret-reader"},
                 "rules": [{"apiGroups": [""], "resources": ["secrets"], "verbs": ["get", "watch", "list"]}]}
READ_SECRETS = {"kind": "RoleBinding", "metadata": {"name": "read-secrets", "namespace": "development"},
                "subjects": [{"kind": "User", "name": "dave", "apiGroup": "rbac.authorization.k8s.io"}],
                "roleRef": {"kind": "ClusterRole", "name": "secret-reader", "apiGroup": "rbac.authorization.k8s.io"}}
READ_SECRETS_GLOBAL = {"kind": "ClusterRoleBinding", "metadata": {"name": "read-secrets-global"},
                       "subjects": [{"kind": "Group", "name": "manager", "apiGroup": "rbac.authorization.k8s.io"}],
                       "roleRef": {"kind": "ClusterRole", "name": "secret-reader", "apiGroup": "rbac.authorization.k8s.io"}}
MONITORING = {"kind": "ClusterRole", "metadata": {"name": "monitoring"},
              "aggregationRule": {"clusterRoleSelectors": [{"matchLabels": {"rbac.example.com/aggregate-to-monitoring": "true"}}]}}
MONITORING_ES = {"kind": "ClusterRole", "metadata": {"name": "monitoring-endpointslices",
                                                     "labels": {"rbac.example.com/aggregate-to-monitoring": "true"}},
                 "rules": [{"apiGroups": [""], "resources": ["services", "pods"], "verbs": ["get", "list", "watch"]},
                           {"apiGroups": ["discovery.k8s.io"], "resources": ["endpointslices"], "verbs": ["get", "list", "watch"]}]}
CRON_EDIT = {"kind": "ClusterRole", "metadata": {"name": "aggregate-cron-tabs-edit", "labels": {
    "rbac.authorization.k8s.io/aggregate-to-admin": "true", "rbac.authorization.k8s.io/aggregate-to-edit": "true"}},
    "rules": [{"apiGroups": ["stable.example.com"], "resources": ["crontabs"],
               "verbs": ["get", "list", "watch", "create", "update", "patch", "delete"]}]}
CRON_VIEW = {"kind": "ClusterRole", "metadata": {"name": "aggregate-cron-tabs-view", "labels": {
    "rbac.authorization.k8s.io/aggregate-to-view": "true"}},
    "rules": [{"apiGroups": ["stable.example.com"], "resources": ["crontabs"], "verbs": ["get", "list", "watch"]}]}
CONFIGMAP_UPDATER = {"kind": "Role", "metadata": {"namespace": "default", "name": "configmap-updater"},
                     "rules": [{"apiGroups": [""], "resources": ["configmaps"], "resourceNames": ["my-configmap"],
                                "verbs": ["update", "get"]}]}
POD_LOGS = {"kind": "Role", "metadata": {"namespace": "default", "name": "pod-and-pod-logs-reader"},
            "rules": [{"apiGroups": [""], "resources": ["pods", "pods/log"], "verbs": ["get", "list"]}]}
SUPERUSER = {"kind": "Role", "metadata": {"namespace": "default", "name": "example.com-superuser"},
             "rules": [{"apiGroups": ["example.com"], "resources": ["*"], "verbs": ["*"]}]}


def syn(obj: dict) -> dict:
    return {**obj, "synthetic": True}


def rb(name, ns, subjects, kind, role):
    return syn({"kind": "RoleBinding", "metadata": {"name": name, "namespace": ns},
                "subjects": subjects, "roleRef": {"kind": kind, "name": role, "apiGroup": "rbac.authorization.k8s.io"}})


def crb(name, subjects, role):
    return syn({"kind": "ClusterRoleBinding", "metadata": {"name": name},
                "subjects": subjects, "roleRef": {"kind": "ClusterRole", "name": role, "apiGroup": "rbac.authorization.k8s.io"}})


def U(n):
    return {"kind": "User", "name": n, "apiGroup": "rbac.authorization.k8s.io"}


def G(n):
    return {"kind": "Group", "name": n, "apiGroup": "rbac.authorization.k8s.io"}


def req(user, groups, verb, group, resource, ns, name="", sub=""):
    return {"user": user, "groups": groups, "verb": verb, "apiGroup": group, "resource": resource,
            "subresource": sub, "namespace": ns, "name": name}


def q(desc, request):
    return {"description": desc, "request": request, "recorded_decision": None}


def k8s_items(write_item, sha):
    doc = (FETCHED / "k8s-rbac.md").read_text()

    def example(name):
        return (FETCHED / f"k8s-{name}.yaml").read_text()

    def doc_block(marker: str) -> str:
        start = doc.index(marker)
        a = doc.rindex("```yaml", 0, start)
        b = doc.index("```", start)
        return doc[a + 8:b]

    base = {"family": "k8s", "synthetic": False,
            "question": "Does Kubernetes RBAC authorize each request given these RBAC objects?"}

    def prov(paths):
        return {"repository": K8S[0], "commit": K8S[1], "licence": K8S[2], "paths": paths,
                "note": "YAML objects are verbatim documentation examples; requests and objects marked synthetic are experiment filler."}

    j = lambda n: [q(f"{n}-{i}", r) for i, r in enumerate(REQS[n])]
    REQS = {
        "k01": [req("jane", [], "get", "", "pods", "default", "web-1"),
                req("jane", [], "watch", "", "pods", "default"),
                req("jane", [], "list", "", "pods", "kube-system"),
                req("jane", [], "delete", "", "pods", "default", "web-1"),
                req("jane", [], "get", "", "pods", "default", "web-1", "log"),
                req("bob", ["jane"], "get", "", "pods", "default", "web-1"),
                req("jane", [], "get", "apps", "pods", "default", "web-1")],
        "k02": [req("dave", [], "get", "", "secrets", "development", "db-pass"),
                req("dave", [], "list", "", "secrets", "default"),
                req("dave", [], "list", "", "secrets", ""),
                req("dave", [], "get", "", "pods", "development", "p"),
                req("erin", [], "get", "", "secrets", "development", "db-pass")],
        "k03": [req("carol", ["manager"], "get", "", "secrets", "kube-system", "token"),
                req("carol", ["manager"], "list", "", "secrets", ""),
                req("manager", [], "get", "", "secrets", "default", "x"),
                req("carol", ["managers"], "get", "", "secrets", "default", "x"),
                req("carol", ["manager"], "delete", "", "secrets", "default", "x")],
        "k04": [req("sam", ["sre"], "list", "discovery.k8s.io", "endpointslices", "default"),
                req("sam", ["sre"], "get", "", "pods", "prod", "api-0"),
                req("sam", ["sre"], "delete", "", "pods", "prod", "api-0"),
                req("sam", ["sre"], "list", "", "endpointslices", "prod"),
                req("sam", ["sre"], "watch", "", "services", ""),
                req("tom", ["dev"], "get", "", "pods", "prod", "api-0")],
        "k05": [req("ana", [], "get", "stable.example.com", "crontabs", "team-a", "nightly"),
                req("ana", [], "delete", "stable.example.com", "crontabs", "team-a", "nightly"),
                req("ed", [], "create", "stable.example.com", "crontabs", "team-a"),
                req("vic", [], "list", "stable.example.com", "crontabs", "team-a"),
                req("vic", [], "create", "stable.example.com", "crontabs", "team-a"),
                req("vic", [], "list", "stable.example.com", "crontabs", "team-b"),
                req("ana", [], "get", "", "crontabs", "team-a", "nightly")],
        "k06": [req("ci-bot", [], "update", "", "configmaps", "default", "my-configmap"),
                req("ci-bot", [], "get", "", "configmaps", "default", "my-configmap"),
                req("ci-bot", [], "update", "", "configmaps", "default", "other"),
                req("ci-bot", [], "list", "", "configmaps", "default"),
                req("ci-bot", [], "delete", "", "configmaps", "default", "my-configmap"),
                req("ci-bot", [], "get", "", "configmaps", "staging", "my-configmap")],
        "k07": [req("lee", [], "get", "", "pods", "default", "p", "log"),
                req("lee", [], "list", "", "pods", "default"),
                req("lee", [], "get", "", "pods", "default", "p", "exec"),
                req("root", ["platform"], "delete", "example.com", "widgets", "default", "w1"),
                req("root", ["platform"], "delete", "example.com", "widgets", "other", "w1"),
                req("root", ["platform"], "get", "", "pods", "default", "p")],
    }
    write_item("k01_pod_reader", {**base, "provenance": prov([K8S_EX + "simple-role.yaml", K8S_EX + "simple-rolebinding-with-role.yaml"]),
               "world": {"objects": [POD_READER, READ_PODS]}, "questions": j("k01")},
               {"source.yaml": example("simple-role") + "---\n" + example("simple-rolebinding-with-role")})
    write_item("k02_secret_reader_rolebinding", {**base, "provenance": prov([K8S_EX + "simple-clusterrole.yaml", K8S_EX + "simple-rolebinding-with-clusterrole.yaml"]),
               "world": {"objects": [SECRET_READER, READ_SECRETS]}, "questions": j("k02")},
               {"source.yaml": example("simple-clusterrole") + "---\n" + example("simple-rolebinding-with-clusterrole")})
    write_item("k03_secret_reader_global", {**base, "provenance": prov([K8S_EX + "simple-clusterrole.yaml", K8S_EX + "simple-clusterrolebinding.yaml"]),
               "world": {"objects": [SECRET_READER, READ_SECRETS_GLOBAL]}, "questions": j("k03")},
               {"source.yaml": example("simple-clusterrole") + "---\n" + example("simple-clusterrolebinding")})
    write_item("k04_monitoring_aggregation", {**base, "provenance": prov([K8S_DOC + "#aggregated-clusterroles"]),
               "world": {"objects": [MONITORING, MONITORING_ES, crb("sre-monitoring", [G("sre")], "monitoring")]},
               "questions": j("k04")},
               {"source.yaml": doc_block("name: monitoring\naggregationRule") + "---\n" + doc_block("name: monitoring-endpointslices")})
    # Default user-facing roles: aggregation skeleton of the upstream bootstrap policy
    # (kubernetes/kubernetes plugin/pkg/auth/authorizer/rbac/bootstrappolicy/policy.go): admin selects
    # aggregate-to-admin, edit is labelled aggregate-to-admin and selects aggregate-to-edit, view is
    # labelled aggregate-to-edit and selects aggregate-to-view. Their own rules are omitted (synthetic).
    A = "rbac.authorization.k8s.io/aggregate-to-"
    defaults = [syn({"kind": "ClusterRole", "metadata": {"name": "admin"},
                     "aggregationRule": {"clusterRoleSelectors": [{"matchLabels": {A + "admin": "true"}}]}}),
                syn({"kind": "ClusterRole", "metadata": {"name": "edit", "labels": {A + "admin": "true"}},
                     "aggregationRule": {"clusterRoleSelectors": [{"matchLabels": {A + "edit": "true"}}]}}),
                syn({"kind": "ClusterRole", "metadata": {"name": "view", "labels": {A + "edit": "true"}},
                     "aggregationRule": {"clusterRoleSelectors": [{"matchLabels": {A + "view": "true"}}]}})]
    write_item("k05_crontab_default_roles", {**base, "provenance": {**prov([K8S_DOC + "#aggregated-clusterroles", K8S_DOC + "#user-facing-roles"]),
               "note": "CronTab ClusterRoles verbatim; admin/edit/view aggregation skeleton from upstream bootstrap policy, rules omitted (synthetic); bindings synthetic."},
               "world": {"objects": [CRON_EDIT, CRON_VIEW, *defaults,
                                     rb("ana-admin", "team-a", [U("ana")], "ClusterRole", "admin"),
                                     rb("ed-edit", "team-a", [U("ed")], "ClusterRole", "edit"),
                                     rb("vic-view", "team-a", [U("vic")], "ClusterRole", "view")]},
               "questions": j("k05")},
               {"source.yaml": doc_block("name: aggregate-cron-tabs-edit")})
    write_item("k06_configmap_updater", {**base, "provenance": prov([K8S_DOC + "#referring-to-resources"]),
               "world": {"objects": [CONFIGMAP_UPDATER, rb("ci-configmap", "default", [U("ci-bot")], "Role", "configmap-updater")]},
               "questions": j("k06")},
               {"source.yaml": doc_block("name: configmap-updater")})
    write_item("k07_subresource_wildcard", {**base, "provenance": prov([K8S_DOC + "#referring-to-resources"]),
               "world": {"objects": [POD_LOGS, SUPERUSER,
                                     rb("lee-logs", "default", [U("lee")], "Role", "pod-and-pod-logs-reader"),
                                     rb("platform-super", "default", [G("platform")], "Role", "example.com-superuser")]},
               "questions": j("k07")},
               {"source.yaml": doc_block("name: pod-and-pod-logs-reader") + "---\n" + doc_block("name: example.com-superuser")})


# ------------------------------------------------------------------------ AWS

S3_RW = {"Version": "2012-10-17", "Statement": [
    {"Sid": "ListObjectsInBucket", "Effect": "Allow", "Action": ["s3:ListBucket"], "Resource": ["arn:aws:s3:::bucket-name"]},
    {"Sid": "AllObjectActions", "Effect": "Allow", "Action": "s3:*Object", "Resource": ["arn:aws:s3:::bucket-name/*"]}]}
DENY_REGION = {"Version": "2012-10-17", "Statement": [
    {"Sid": "DenyAllOutsideRequestedRegions", "Effect": "Deny",
     "NotAction": ["cloudfront:*", "iam:*", "organizations:*", "route53:*", "support:*"], "Resource": "*",
     "Condition": {"StringNotEquals": {"aws:RequestedRegion": ["eu-central-1", "eu-west-1", "eu-west-2", "eu-west-3"]}}}]}
ADMIN = {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]}
MFA = {"Version": "2012-10-17", "Statement": [
    {"Sid": "AllowListActions", "Effect": "Allow", "Action": ["iam:ListUsers", "iam:ListVirtualMFADevices"], "Resource": "*"},
    {"Sid": "AllowUserToCreateVirtualMFADevice", "Effect": "Allow", "Action": ["iam:CreateVirtualMFADevice"], "Resource": "arn:aws:iam::*:mfa/*"},
    {"Sid": "AllowUserToManageTheirOwnMFA", "Effect": "Allow",
     "Action": ["iam:EnableMFADevice", "iam:GetMFADevice", "iam:ListMFADevices", "iam:ResyncMFADevice"],
     "Resource": "arn:aws:iam::*:user/${aws:username}"},
    {"Sid": "AllowUserToDeactivateTheirOwnMFAOnlyWhenUsingMFA", "Effect": "Allow", "Action": ["iam:DeactivateMFADevice"],
     "Resource": ["arn:aws:iam::*:user/${aws:username}"], "Condition": {"Bool": {"aws:MultiFactorAuthPresent": "true"}}},
    {"Sid": "BlockMostAccessUnlessSignedInWithMFA", "Effect": "Deny",
     "NotAction": ["iam:CreateVirtualMFADevice", "iam:EnableMFADevice", "iam:ListMFADevices", "iam:ListUsers",
                   "iam:ListVirtualMFADevices", "iam:ResyncMFADevice"], "Resource": "*",
     "Condition": {"BoolIfExists": {"aws:MultiFactorAuthPresent": "false"}}}]}



def aws_items(write_item, sha):
    import json
    base = {"family": "iam", "synthetic": False,
            "question": "Is each request allowed by these identity-based policies (explicit deny > allow > implicit deny)?"}
    url = "https://docs.aws.amazon.com/IAM/latest/UserGuide/"
    prov = lambda page, note="": {"repository": AWS[0], "commit": AWS[1], "licence": AWS[2], "url": url + page + ".html",
                                  "note": "Policy JSON verbatim from the page; requests synthetic." + note}
    R = lambda a, r, c=None: {"action": a, "resource": r, "context": c or {}}
    s3q = [R("s3:ListBucket", "arn:aws:s3:::bucket-name"), R("s3:GetObject", "arn:aws:s3:::bucket-name/photos/a.jpg"),
           R("s3:PutObject", "arn:aws:s3:::bucket-name/x"), R("s3:GetObjectAcl", "arn:aws:s3:::bucket-name/x"),
           R("s3:DeleteBucket", "arn:aws:s3:::bucket-name"), R("s3:ListBucket", "arn:aws:s3:::other-bucket"),
           R("s3:GetObject", "arn:aws:s3:::bucket-name"), R("s3:getobject", "arn:aws:s3:::bucket-name/k")]
    write_item("w01_s3_rw_bucket", {**base, "provenance": prov("reference_policies_examples_s3_rw-bucket"),
               "world": {"policies": [S3_RW]}, "questions": [q(f"w01-{i}", r) for i, r in enumerate(s3q)]},
               {"source.json": json.dumps(S3_RW, indent=4) + "\n"})
    rg = lambda region: {"aws:RequestedRegion": region}
    drq = [R("ec2:RunInstances", "*", rg("eu-west-1")), R("ec2:RunInstances", "*", rg("us-east-1")),
           R("iam:CreateUser", "*", rg("us-east-1")), R("s3:GetObject", "arn:aws:s3:::b/k", {}),
           R("route53:ChangeResourceRecordSets", "*", rg("ap-south-1")), R("ec2:RunInstances", "*", rg("EU-WEST-1")),
           R("support:DescribeCases", "*", rg("us-west-2")), R("cloudfrontx:Get", "*", rg("us-west-2"))]
    write_item("w02_deny_requested_region", {**base, "provenance": {**prov("reference_policies_examples_aws_deny-requested-region",
               " The Allow-all policy is the AWS managed AdministratorAccess document, added (synthetic pairing) so the deny is observable."),
               "synthetic_parts": ["AdministratorAccess pairing", "requests"]},
               "world": {"policies": [DENY_REGION, ADMIN]}, "questions": [q(f"w02-{i}", r) for i, r in enumerate(drq)]},
               {"source.json": json.dumps(DENY_REGION, indent=4) + "\n"})
    arn = "arn:aws:iam::123456789012:"
    m = lambda v: {"aws:MultiFactorAuthPresent": v}
    mq = [R("iam:EnableMFADevice", arn + "user/alice", {"aws:username": "alice"}),
          R("iam:DeactivateMFADevice", arn + "user/alice", {"aws:username": "alice", **m("true")}),
          R("iam:DeactivateMFADevice", arn + "user/alice", {"aws:username": "alice", **m("false")}),
          R("iam:DeactivateMFADevice", arn + "user/alice", {"aws:username": "alice"}),
          R("iam:ListUsers", "*", {"aws:username": "alice"}),
          R("iam:EnableMFADevice", arn + "user/bob", {"aws:username": "alice", **m("true")}),
          R("iam:CreateVirtualMFADevice", arn + "mfa/alice", {"aws:username": "alice"}),
          R("iam:GetMFADevice", arn + "user/alice", {"aws:username": "alice", **m("false")}),
          R("iam:GetMFADevice", arn + "user/alice", {"aws:username": "alice", **m("true")})]
    write_item("w03_mfa_selfmanage", {**base, "provenance": prov("reference_policies_examples_iam_mfa-selfmanage"),
               "world": {"policies": [MFA]}, "questions": [q(f"w03-{i}", r) for i, r in enumerate(mq)]},
               {"source.json": json.dumps(MFA, indent=4) + "\n"})


# ---------------------------------------------------------------------- Alloy

def alloy_items(write_item, sha):
    root = DATA / "alloy-models"
    base = {"family": "alloy", "synthetic": False,
            "question": "Does the target paragraph hold in each finite instance (or: do the facts entail the assertion)?"}

    def prov(path, note=""):
        return {"repository": ALLOY[0], "commit": ALLOY[1], "licence": ALLOY[2], "path": path,
                "note": "Model text verbatim; instances synthetic." + note}

    def src(path):
        return (root / path).read_text()

    def inst(sigs, fields, bind=None):
        return {"sigs": sigs, "fields": fields, "bindings": bind or {}}

    def qq(desc, target, instance):
        return {"description": desc, "target": target, "instance": instance, "recorded_decision": None}

    # genealogy: Person = Man + Woman, Adam in Man, Eve in Woman
    P = lambda men, women, adam, eve: {"Person": men + women, "Man": men, "Woman": women, "Adam": [adam], "Eve": [eve]}
    gp = P(["adam", "cain", "abel"], ["eve", "awan"], "adam", "eve")
    bio = {"kind": "fact", "name": "Biology"}
    write_item("l01_genealogy_biology", {**base, "provenance": prov("simple-models/genealogy/genealogy.als"),
        "questions": [
            qq("acyclic", bio, inst(gp, {"parents": [["cain", "adam"], ["cain", "eve"], ["abel", "adam"], ["abel", "eve"], ["awan", "adam"], ["awan", "eve"]], "spouse": []})),
            qq("self-parent", bio, inst(gp, {"parents": [["cain", "cain"]], "spouse": []})),
            qq("3-cycle", bio, inst(gp, {"parents": [["cain", "abel"], ["abel", "awan"], ["awan", "cain"]], "spouse": []})),
            qq("empty", bio, inst(gp, {"parents": [], "spouse": []})),
            qq("long chain", bio, inst(gp, {"parents": [["abel", "cain"], ["cain", "awan"], ["awan", "eve"], ["eve", "adam"]], "spouse": []}))]},
        {"source.als": src("simple-models/genealogy/genealogy.als")})

    G1 = "software-abstractions-book/chapter4/grandpa1.als"
    gs = {"Person": ["m1", "m2", "w1", "w2"], "Man": ["m1", "m2"], "Woman": ["w1", "w2"]}
    f0 = {"kind": "fact", "index": 0}
    write_item("l02_grandpa1_fact", {**base, "provenance": prov(G1),
        "questions": [
            qq("ok", f0, inst(gs, {"father": [["m2", "m1"], ["w2", "m1"]], "mother": [["m2", "w1"]], "wife": [["m1", "w1"]], "husband": [["w1", "m1"]]})),
            qq("husband not converse", f0, inst(gs, {"father": [], "mother": [], "wife": [["m1", "w1"]], "husband": [["w2", "m1"]]})),
            qq("mixed cycle", f0, inst(gs, {"father": [["w1", "m1"]], "mother": [["m1", "w1"]], "wife": [], "husband": []})),
            qq("mother self", f0, inst(gs, {"father": [], "mother": [["w2", "w2"]], "wife": [], "husband": []})),
            qq("empty", f0, inst(gs, {"father": [], "mother": [], "wife": [], "husband": []}))]},
        {"source.als": src(G1)})
    ns = {"kind": "assert", "name": "NoSelfGrandpa"}
    write_item("l03_grandpa1_noselfgrandpa", {**base, "provenance": prov(G1, " The check question uses the file's own scope (4 Person)."),
        "questions": [
            qq("own grandpa instance", ns, inst(gs, {"father": [["w1", "m1"], ["m1", "m2"], ["m2", "m1"]], "mother": [], "wife": [], "husband": []})),
            qq("normal family", ns, inst(gs, {"father": [["m2", "m1"], ["w2", "m2"]], "mother": [["m2", "w1"]], "wife": [], "husband": []})),
            qq("check NoSelfGrandpa under facts", {"kind": "check", "name": "NoSelfGrandpa", "scope": 3}, None)]},
        {"source.als": src(G1)})

    GR = "utilities/types/graph.als"
    REL = "utilities/types/relation.als"
    nodes = lambda n: {"node": [f"n{i}" for i in range(n)]}
    E = lambda *pairs: [[f"n{a}", f"n{b}"] for a, b in pairs]
    wc = lambda edges, n=4: inst(nodes(n), {"edges": edges}, {"r": "edges"})
    pw = {"kind": "pred", "name": "weaklyConnected", "args": ["r"]}
    write_item("l04_graph_weakly_connected", {**base, "provenance": prov(GR),
        "questions": [qq("path", pw, wc(E((0, 1), (2, 1), (2, 3)))), qq("two components", pw, wc(E((0, 1), (2, 3)))),
                      qq("singleton", pw, wc([], 1)), qq("isolated node", pw, wc(E((0, 1), (1, 2)))),
                      qq("empty graph", pw, wc([], 0))]},
        {"source.als": src(GR)})
    pr = {"kind": "pred", "name": "ring", "args": ["r"]}
    write_item("l05_graph_ring", {**base, "provenance": prov(GR),
        "questions": [qq("4-ring", pr, wc(E((0, 1), (1, 2), (2, 3), (3, 0)))), qq("two 2-rings", pr, wc(E((0, 1), (1, 0), (2, 3), (3, 2)))),
                      qq("branch", pr, wc(E((0, 1), (0, 2), (1, 2), (2, 3), (3, 0)))), qq("self loop singleton", pr, wc(E((0, 0)), 1)),
                      qq("rho shape", pr, wc(E((0, 1), (1, 2), (2, 3), (3, 1))))]},
        {"source.als": src(GR)})
    pt = {"kind": "pred", "name": "tree", "args": ["r"]}
    write_item("l06_graph_tree", {**base, "provenance": {**prov(GR), "also": REL},
        "questions": [qq("binary tree", pt, wc(E((0, 1), (0, 2), (2, 3)))), qq("two roots (forest)", pt, wc(E((0, 1), (2, 3)))),
                      qq("diamond", pt, wc(E((0, 1), (0, 2), (1, 3), (2, 3)))), qq("cycle", pt, wc(E((0, 1), (1, 2), (2, 0)), 3)),
                      qq("empty", pt, wc([], 0)), qq("chain", pt, wc(E((0, 1), (1, 2), (2, 3))))]},
        {"source.als": src(GR), "relation.als": src(REL)})

    GC = "algorithms/gc/marksweepgc.als"
    hs = lambda: {"Node": ["a", "b", "c", "d"], "HeapState": ["h0", "h1"]}
    heap = lambda left, right, m0, m1: inst(hs(), {
        "left": [["h0", x, y] for x, y in left] + [["h1", x, y] for x, y in left],
        "right": [["h0", x, y] for x, y in right] + [["h1", x, y] for x, y in right],
        "marked": [["h0", x] for x in m0] + [["h1", x] for x in m1], "freeList": []},
        {"hs": "h0", "from": "a", 'hs"': "h1"})
    pm = {"kind": "pred", "name": "mark", "args": ["hs", "from", 'hs"']}
    write_item("l07_marksweep_mark", {**base, "provenance": prov(GC, " The file writes primes as hs\"; the target predicate is mark."),
        "questions": [qq("correct mark", pm, heap([("a", "b"), ("b", "c")], [], [], ["a", "b", "c"])),
                      qq("missed root", pm, heap([("a", "b")], [], [], ["b"])),
                      qq("over-marked", pm, heap([("a", "b")], [], [], ["a", "b", "d"])),
                      qq("via right+cycle", pm, heap([("a", "b"), ("c", "a")], [("b", "c")], [], ["a", "b", "c"])),
                      qq("left changed", pm, inst(hs(), {"left": [["h0", "a", "b"]], "right": [], "marked": [["h1", "a"]], "freeList": []}, {"hs": "h0", "from": "a", 'hs"': "h1"}))]},
        {"source.als": src(GC)})

    AB = "software-abstractions-book/chapter2/addressBook3a.als"
    abs_ = {"Target": ["a1", "a2", "al", "g1", "g2"], "Addr": ["a1", "a2"], "Name": ["al", "g1", "g2"],
            "Alias": ["al"], "Group": ["g1", "g2"], "Book": ["b0"]}
    book = lambda triples, names, target_name, addr: inst(abs_, {"names": [["b0", n] for n in names],
                                                               "addr": [["b0", x, y] for x, y in triples]},
                                                        {"b": "b0", "n": target_name, "t": addr})
    lk = {"kind": "formula", "text": "t in lookup[b, n]", "note": "membership in the source's lookup function"}
    write_item("l08_addressbook_lookup", {**base, "provenance": prov(AB, " Question formula 't in lookup[b, n]' is written for this experiment over the source's fun lookup."),
        "questions": [qq("direct", lk, book([("al", "a1")], ["al"], "al", "a1")),
                      qq("via group", lk, book([("g1", "al"), ("al", "a2")], ["g1", "al"], "g1", "a2")),
                      qq("two hops groups", lk, book([("g2", "g1"), ("g1", "al"), ("al", "a1")], ["g2", "g1", "al"], "g2", "a1")),
                      qq("not reachable", lk, book([("g1", "a1"), ("al", "a2")], ["g1", "al"], "g1", "a2")),
                      qq("name itself not an address", lk, book([("g1", "al")], ["g1", "al"], "g1", "al"))]},
        {"source.als": src(AB)})


def build(which, write_item, sha):
    if "k8s" in which:
        k8s_items(write_item, sha)
    if "aws" in which:
        aws_items(write_item, sha)
    if "alloy" in which:
        alloy_items(write_item, sha)
