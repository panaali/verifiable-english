import json
import sys
from pathlib import Path

sys.path.insert(0, "/private/tmp/ve-e0-integration")
import ve

ROOT = Path(__file__).resolve().parents[3]
DRAW = ROOT / "experiments/E0/survey_samples/_drawn/gatekeeper.json"
OUT = ROOT / "experiments/E0/second_rater_work/gatekeeper.jsonl"


def env(sorts, predicates, constants):
    data = {
        "language": "ve.core@0",
        "profile": "relational-fol@0",
        "spec_revision": "ve-v0-draft-2026-09-20",
        "vocabulary": {
            "sorts": {s: {"description": d} for s, d in sorts.items()},
            "predicates": {p: {"arguments": a, "description": d} for p, (a, d) in predicates.items()},
            "constants": {c: {"sort": s, "description": d} for c, (s, d) in constants.items()},
        },
    }
    return data


base_sorts = {"request": "An admission request.", "container": "A mechanically reified container.", "value": "A field value.", "item": "A mechanically reified collection item."}

fits = {
"gatekeeper-library/src/general/automount-serviceaccount-token/src.rego": (
    env(base_sorts, {
        "is_update": (["request"], "The request is an update under exclude_update."),
        "automount_present": (["request"], "The automountServiceAccountToken field is present."),
        "automount_true": (["request"], "The automountServiceAccountToken field has Boolean value true."),
        "has_container": (["request", "container"], "The request object has this ordinary or init container."),
        "has_mount": (["container", "value"], "The container has a volume mount whose mountPath has this value."),
    }, {"review": ("request", "The input review."), "sa_path": ("value", "The literal /var/run/secrets/kubernetes.io/serviceaccount.")}),
    "(not (@review is is_update)) and ((@review is automount_true) or ((not (@review is automount_present)) and (there exists container c, ((@review has_container c) and (c has_mount @sa_path)))))."
),
"gatekeeper-library/src/general/block-loadbalancer-services/src.rego": (
    env({"request": "An admission request."}, {"service_kind": (["request"], "The review kind.kind equals Service."), "loadbalancer_type": (["request"], "The object spec.type equals LoadBalancer.")}, {"review": ("request", "The input review.")}),
    "(@review is service_kind) and (@review is loadbalancer_type)."
),
"gatekeeper-library/src/general/containerresources/src.rego": (
    env(base_sorts, {"has_container": (["request", "container"], "The request has this ordinary or init container."), "exempt": (["container"], "The imported exempt_container helper exempts this container."), "required_limit": (["item"], "This resource name occurs in parameters.limits."), "required_request": (["item"], "This resource name occurs in parameters.requests."), "has_limit": (["container", "item"], "The limits map has this resource key with a truthy value."), "has_request": (["container", "item"], "The requests map has this resource key with a truthy value.")}, {"review": ("request", "The input review.")}),
    "there exists container c, (((@review has_container c) and (not (c is exempt))) and ((there exists item r, ((r is required_limit) and (not (c has_limit r)))) or (there exists item q, ((q is required_request) and (not (c has_request q))))))."
),
"gatekeeper-library/src/general/noupdateserviceaccount/src.rego": (
    env(base_sorts | {"group": "A user group.", "account": "A service-account-name value."}, {"update_operation": (["request"], "The operation field equals UPDATE."), "old_account": (["request", "account"], "The supported old object has this serviceAccountName."), "new_account": (["request", "account"], "The supported new object has this serviceAccountName."), "actor_allowed": (["request"], "The review username occurs in parameters.allowedUsers, using the empty-string default."), "actor_group": (["request", "group"], "A group in review.userInfo.groups, using the empty-list default."), "allowed_group": (["group"], "A group in parameters.allowedGroups, using the empty-list default.")}, {"review": ("request", "The input review.")}),
    "(@review is update_operation) and (((not (there exists account n, (@review new_account n))) or (not (there exists account o, (@review old_account o)))) or (((not (@review is actor_allowed)) and (not (there exists group g, ((@review actor_group g) and (g is allowed_group))))) and (there exists account a, (there exists account b, (((@review old_account a) and (@review new_account b)) and (not (a equals b)))))))."
),
"gatekeeper-library/src/pod-security-policy/seccompv2/src.rego": (
    env(base_sorts, {"has_container": (["request", "container"], "The review has this ordinary, init, or ephemeral container."), "exempt": (["container"], "The imported helper exempts the container."), "wildcard_profiles": (["request"], "allowedProfiles contains the literal wildcard."), "effective_profile": (["container", "value"], "Mechanical precedence result: container profile, else pod profile, else the not-configured literal."), "localhost_profile": (["value"], "The profile value equals Localhost."), "allowed_profile": (["value"], "The non-Localhost value occurs in allowedProfiles."), "wildcard_files": (["request"], "allowedLocalhostFiles contains the literal wildcard."), "effective_file": (["container", "item"], "The selected localhostProfile file, with empty-string default."), "allowed_file": (["item"], "A file occurs in allowedLocalhostFiles, with the policy's default list." )}, {"review": ("request", "The input review.")}),
    "(not (@review is wildcard_profiles)) and (there exists container c, (((@review has_container c) and (not (c is exempt))) and (there exists value p, ((c effective_profile p) and (((not (p is localhost_profile)) and (not (p is allowed_profile))) or ((p is localhost_profile) and ((not (@review is wildcard_files)) and (there exists item f, ((c effective_file f) and (not (f is allowed_file)))))))))))."
),
"gatekeeper-library/src/pod-security-policy/privileged-containers/src.rego": None,
"gatekeeper-library/src/pod-security-policy/host-namespaces/src.rego": None,
"gatekeeper-library/src/general/requiredprobes/src.rego": None,
"gatekeeper-library/src/pod-security-policy/host-process/src.rego": None,
"gatekeeper-library/src/general/externalip/src.rego": None,
"gatekeeper-library/src/general/uniqueserviceselector/src.rego": None,
"gatekeeper-library/src/general/disallowinteractive/src.rego": None,
"gatekeeper-library/src/pod-security-policy/allow-privilege-escalation/src.rego": None,
}


def simple_container(extra_preds, body, update=True, exempt=True):
    preds = {"has_container": (["request", "container"], "The review has a container of every policy-enumerated category.")}
    if update:
        preds["is_update"] = (["request"], "The imported exclude_update helper classifies the request as an update.")
    if exempt:
        preds["exempt"] = (["container"], "The imported exempt_container helper exempts the container.")
    preds.update(extra_preds)
    prefix = "(not (@review is is_update)) and (" if update else ""
    inner = "there exists container c, ((@review has_container c) and ("
    if exempt:
        inner += f"(not (c is exempt)) and ({body})"
    else:
        inner += body
    inner += "))"
    source = prefix + inner + (")" if update else "") + "."
    return env(base_sorts, preds, {"review": ("request", "The input review.")}), source


fits["gatekeeper-library/src/pod-security-policy/privileged-containers/src.rego"] = simple_container({"privileged_true": (["container"], "securityContext.privileged is truthy.")}, "c is privileged_true")
fits["gatekeeper-library/src/pod-security-policy/host-namespaces/src.rego"] = (env({"request": "An admission request."}, {"is_update": (["request"], "The imported exclude_update helper classifies the request as an update."), "host_pid_true": (["request"], "spec.hostPID is truthy."), "host_ipc_true": (["request"], "spec.hostIPC is truthy.")}, {"review": ("request", "The input review.")}), "(not (@review is is_update)) and ((@review is host_pid_true) or (@review is host_ipc_true)).")
probe_sorts = base_sorts | {"probe": "A mechanically reified truthy probe object."}
fits["gatekeeper-library/src/general/requiredprobes/src.rego"] = (env(probe_sorts, {"is_update": (["request"], "The imported helper says review.operation equals UPDATE."), "has_container": (["request", "container"], "The review object has this ordinary container."), "required_probe": (["item"], "A probe field name occurs in parameters.probes."), "required_probe_type": (["value"], "A probe subfield name occurs in parameters.probeTypes."), "container_probe": (["container", "probe"], "The container has this truthy probe object."), "probe_name": (["probe", "item"], "This reified probe came from the named container field."), "probe_type_truthy": (["probe", "value"], "This exact reified probe has a truthy subfield with the given name.")}, {"review": ("request", "The input review.")}), "(not (@review is is_update)) and (there exists container c, ((@review has_container c) and (there exists item p, ((p is required_probe) and ((not (there exists probe z, ((c container_probe z) and (z probe_name p)))) or (there exists probe q, (((c container_probe q) and (q probe_name p)) and (for every value t, (if (t is required_probe_type), then (not (q probe_type_truthy t))))))))))).")
fits["gatekeeper-library/src/pod-security-policy/host-process/src.rego"] = (env(base_sorts, {"is_update": (["request"], "The imported exclude_update helper classifies the request as an update."), "pod_hostprocess_true": (["request"], "Pod-level windowsOptions.hostProcess equals true."), "has_container": (["request", "container"], "The review has an ordinary, init, or ephemeral container."), "exempt": (["container"], "The imported helper exempts the container."), "container_hostprocess_true": (["container"], "Container-level windowsOptions.hostProcess equals true.")}, {"review": ("request", "The input review.")}), "(not (@review is is_update)) and ((@review is pod_hostprocess_true) or (there exists container c, (((@review has_container c) and (not (c is exempt))) and (c is container_hostprocess_true)))).")
fits["gatekeeper-library/src/general/externalip/src.rego"] = (env(base_sorts, {"service_core": (["request"], "Kind is Service and group is empty."), "external_ip": (["request", "value"], "An IP occurs in spec.externalIPs."), "allowed_ip": (["value"], "An IP occurs in parameters.allowedIPs.")}, {"review": ("request", "The input review.")}), "(@review is service_core) and (there exists value i, ((@review external_ip i) and (not (i is allowed_ip)))).")
fits["gatekeeper-library/src/general/uniqueserviceselector/src.rego"] = (env(base_sorts | {"service": "A service object.", "assignment": "A reified selector key-value assignment."}, {"review_service_v1": (["request"], "The review is a core/v1 Service."), "inventory_service": (["service"], "A Service in the inventory."), "identical_service": (["request", "service"], "Namespace, name, kind, and apiVersion all equal the reviewed object's values."), "input_assignment": (["assignment"], "A key-value assignment in the reviewed object's selector."), "service_assignment": (["service", "assignment"], "An assignment in the inventory service selector; assignments are canonical pairs of exact key and value." )}, {"review": ("request", "The input review.")}), "(@review is review_service_v1) and (there exists service s, (((s is inventory_service) and (not (@review identical_service s))) and ((for every assignment a, (if (a is input_assignment), then (s service_assignment a))) and (for every assignment b, (if (s service_assignment b), then (b is input_assignment)))))).")
fits["gatekeeper-library/src/general/disallowinteractive/src.rego"] = simple_container({"stdin_present_nonfalse": (["container"], "stdin is present and is not Boolean false."), "tty_present_nonfalse": (["container"], "tty is present and is not Boolean false.")}, "(c is stdin_present_nonfalse) or (c is tty_present_nonfalse)", update=False)
fits["gatekeeper-library/src/pod-security-policy/allow-privilege-escalation/src.rego"] = simple_container({"security_context_present": (["container"], "securityContext is present and truthy."), "allow_escalation_false": (["container"], "securityContext.allowPrivilegeEscalation equals Boolean false.")}, "(not (c is security_context_present)) or (not (c is allow_escalation_false))")

# The imported exempt_container helper is part of each complete condition. It
# performs arbitrary suffix trimming and prefix matching for exemptImages, so
# these otherwise-relational witnesses are intentionally not used as fits.
for exempt_dependent in [
    "gatekeeper-library/src/general/containerresources/src.rego",
    "gatekeeper-library/src/pod-security-policy/seccompv2/src.rego",
    "gatekeeper-library/src/pod-security-policy/privileged-containers/src.rego",
    "gatekeeper-library/src/pod-security-policy/host-process/src.rego",
    "gatekeeper-library/src/general/disallowinteractive/src.rego",
    "gatekeeper-library/src/pod-security-policy/allow-privilege-escalation/src.rego",
    "gatekeeper-library/src/general/uniqueserviceselector/src.rego",
]:
    fits.pop(exempt_dependent)


opaque = {
"ephemeralstoragelimit": (["arithmetic", "decimal parsing", "string suffix processing", "ordered comparison", "string prefix"], "Canonical storage parsing, unit multiplication, and the maximum comparison are unavailable in v0; imported exempt_container additionally performs wildcard suffix trimming and arbitrary image-prefix matching."),
"disallowedrepos": (["string prefix"], "Violation depends on startswith over arbitrary image and repository strings."),
"users": (["ordered comparison", "arithmetic ranges", "string prefix", "string suffix"], "Allowed user and group decisions require numeric interval membership; arrays, fallbacks, and missing fields can be reified, while imported container exemptions additionally require wildcard image-prefix matching."),
"requiredlabels": (["regular expressions"], "The missing-label branch is relational, but the full violation condition also applies a parameter-supplied regular expression to label values."),
"replicalimits": (["ordered comparison"], "Replica range membership uses numeric inequalities. The nonempty-range test is expressible as an existential and is not an additional blocker."),
"poddisruptionbudget": (["ordered comparison"], "The policy compares replicas, minAvailable, and maxUnavailable numerically. Selector containment and the relevant nonempty/existence conditions can be mechanically reified."),
"httpsonly": (["regular expressions"], "Ingress apiVersion qualification uses regex matching; TLS presence and annotation equality alone are only a partial skeleton."),
"allowedreposv2": (["string prefix", "string suffix"], "Wildcard handling trims a suffix and performs prefix matching on arbitrary image strings."),
"horizontalpodautoscaler": (["ordered comparison", "arithmetic subtraction"], "Range and minimum-spread branches require inequalities and subtraction. Range nonemptiness is existentially expressible, and the missing inventory target branch does not cover the full condition."),
"uniqueingresshost": (["regular expressions"], "The host-equality conflict skeleton is relational, but both reviewed and inventory API-version qualifications use regex matching."),
"host-network-ports": (["ordered comparison", "string prefix", "string suffix"], "Host-port violations compare numeric ports with configured minima and maxima, and imported container exemptions require wildcard image-prefix matching; hostNetwork is only one disjunct."),
"block-wildcard-ingress": (["string containment"], "Violation requires detecting an asterisk anywhere in an arbitrary hostname, in addition to the relational missing-host default."),
"proc-mount": (["string case conversion", "string prefix", "string suffix"], "Parameter validation uses lower-case normalization, while imported exempt_container uses wildcard suffix trimming and arbitrary image-prefix matching."),
"disallowedtags": (["string suffix", "string splitting", "string containment", "string prefix"], "Both tag branches inspect arbitrary image strings, and imported exempt_container adds wildcard image-prefix matching."),
"containerresourceratios": (["arithmetic", "decimal parsing", "regular expressions", "ordered comparison", "string prefix", "string suffix"], "The policy parses and compares resource quantities, while imported exempt_container also requires wildcard image-prefix matching; missing-field branches are only partial."),
"fsgroup": (["ordered comparison"], "MustRunAs and MayRunAs validate fsGroup against numeric inclusive ranges. A nonempty range list is expressible with an existential."),
"selinux": (["string prefix", "string suffix"], "The four optional SELinux fields and common allowed record can be faithfully reified, but the complete container branch imports exempt_container, whose wildcard image exemptions require arbitrary suffix trimming and prefix matching."),
"containerresources": (["string prefix", "string suffix"], "The missing required-resource test is relational, but imported exempt_container trims a wildcard suffix and performs prefix matching over arbitrary image strings."),
"seccompv2": (["string prefix", "string suffix"], "Profile selection and allowed-value equality can be reified, but the complete condition invokes exempt_container, whose wildcard image exemptions require arbitrary suffix and prefix operations."),
"privileged-containers": (["string prefix", "string suffix"], "The privileged-field branch is relational, but the imported container exemption performs wildcard suffix trimming and arbitrary image-prefix matching."),
"host-process": (["string prefix", "string suffix"], "The pod-level branch is relational, but the complete violation disjunction includes container exemptions implemented by wildcard suffix trimming and arbitrary image-prefix matching."),
"disallowinteractive": (["string prefix", "string suffix"], "The stdin and tty tests are relational, but imported exempt_container adds wildcard suffix trimming and arbitrary image-prefix matching to the full condition."),
"allow-privilege-escalation": (["string prefix", "string suffix"], "Missing securityContext and false-value semantics are relational, but imported exempt_container requires wildcard suffix trimming and arbitrary image-prefix matching."),
"uniqueserviceselector": (["string concatenation", "string sorting"], "The helper flattens each selector into a sorted delimiter-concatenated string and compares those strings. Set equality would silently remove the source helper's delimiter-collision behavior, while v0 cannot express the actual concatenation."),
}


def classify(item_id):
    if item_id in fits:
        return "DIRECT" if item_id.endswith("block-loadbalancer-services/src.rego") else "REIFIED"
    for key, val in opaque.items():
        if key in item_id:
            return "OPAQUE", val
    raise KeyError(item_id)


items = json.loads(DRAW.read_text())["sample"]
records = []
for item in items:
    item_id = item["id"]
    c = classify(item_id)
    label = c if isinstance(c, str) else c[0]
    if item_id in fits:
        e, source = fits[item_id]
        source += "\n"
        try:
            parsed = ve.check(ve.Environment(e), source)
        except Exception:
            print(item_id)
            print(source)
            raise
        rec = {"dataset": "gatekeeper", "id": item_id, "label": label, "construct_needed": [], "rationale": "The complete violation condition reduces to first-order membership, equality, presence, and negation. Imported update/exemption behavior and missing/default branches are explicit in the witness where applicable.", "formalization": source, "environment": e, "parse_result": parsed, "reification": "Nested Kubernetes objects, list entries, map keys, and configured values are deterministically reified as typed entities and binary membership/field relations; no finite bound is assumed." if label == "REIFIED" else None}
    else:
        _, (needed, why) = c
        rec = {"dataset": "gatekeeper", "id": item_id, "label": label, "construct_needed": needed, "rationale": why, "formalization": None, "environment": None, "parse_result": {"status": "not_checked", "reason": "No faithful full v0 formalization claimed."}, "reification": "A useful relational skeleton exists, but the named interpreted operation remains essential to the complete violation condition."}
    if any(name in item_id for name in (
        "ephemeralstoragelimit", "users/src.rego", "containerresources", "selinux",
        "seccompv2", "privileged-containers", "host-process", "host-network-ports",
        "proc-mount", "disallowedtags", "containerresourceratios", "disallowinteractive",
        "allow-privilege-escalation",
    )):
        rec["helper_evidence"] = {
            "source": "/Users/seyran/code/ve-claude/data/gatekeeper-library/src/rego/lib_exempt_container/lib_exempt_container.rego",
            "sha256": "2f922d8a94b06b0d9a05e3e37b28a3a3a1d03aa9b37236bfe55f30610117649b",
            "semantics": "exemptImages defaults to []; a non-* entry matches image by exact equality; an entry ending * has that suffix removed and matches when image starts with the remaining prefix.",
        }
    records.append(rec)

OUT.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in records))
print(json.dumps({"records": len(records), "counts": {x: sum(r["label"] == x for r in records) for x in ["DIRECT", "REIFIED", "OPAQUE", "NO"]}, "checked": sum(r["parse_result"].get("language") == "accepted" for r in records)}, sort_keys=True))
