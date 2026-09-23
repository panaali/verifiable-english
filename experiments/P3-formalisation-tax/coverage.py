"""E0-style coverage of each source by the VE formalisation (author-classified).

Units: Cedar = each policy/template in the source; Kubernetes = each RBAC object;
IAM = each policy statement; Alloy = the target paragraph plus every fun/pred it calls.
Classes follow experiments/E0/SURVEY.md, relative to the closure@0 profile:
  a  direct fit (attributes and sets as relations, `in` as rtc[parent], closure)
  b  fits after mechanical reification (record/context nodes, template links
     instantiated, ternary fields as tuple nodes, label key=value strings,
     resource/subresource path string)
  c  fits only through an OPAQUE adapter predicate computed outside VE
     (numeric comparison, datetime arithmetic, string globbing)
  d  not expressed
`gaps`: semantics the VE formula knowingly does not capture (none exercised by the
tests unless stated). `error_semantics`: Cedar evaluation-error behaviour that had
to be encoded by hand (has_/bf_ guards), a source of mistranslation risk.
"""
A, B, C, D = "a", "b", "c", "d"

COVERAGE = {
    "c01_cit_1a": {"units": [A]},
    "c02_cit_2a": {"units": [A]},
    "c03_cit_2b": {"units": [A]},
    "c04_cit_2c": {"units": [A]},
    "c05_cit_3a": {"units": [A]},
    "c06_cit_3b": {"units": [A]},
    "c08_cit_4a": {"units": [C], "opaque": ["jobLevel >= 5"]},
    "c09_cit_4d": {"units": [A]},
    "c10_cit_4e": {"units": [A]},
    "c11_cit_4f": {"units": [A], "error_semantics": ["|| with an erroring left operand"]},
    "c12_cit_5b": {"units": [C], "opaque": ["filesize_mb <= 1", "filesize_mb <= 100"], "reified": ["context record"]},
    "c13_document_cloud": {"units": [A] * 12 + [A, B, A],
                           "error_semantics": ["unless {isPrivate} with missing attribute", "owner.blocked on owner without blocked",
                                               "!context.is_authenticated with missing key"]},
    "c14_github": {"units": [A] * 9},
    "c15_hotel_static": {"units": [B, B, A, B, B, A], "reified": ["record-valued permission attributes"],
                         "error_semantics": ["|| over record fields"]},
    "c16_hotel_templated": {"units": [B] * 6, "reified": ["template links instantiated as constants"]},
    "c17_sales_static": {"units": [A, A, A, B, B, A, A, A, B, B], "reified": ["context.target / targetUser"],
                         "error_semantics": ["unless {X || (Y && Z)} with missing context/job/customerId", "|| chains over owner/editors"]},
    "c18_sales_templated": {"units": [B, B, A, A, B, B, A, A, A, A, B, B], "error_semantics": ["same forbid guards as c17", "principal.job != internal with missing job"],
                            "reified": ["2 linked templates instantiated; 4 unlinked templates contribute nothing"]},
    "c19_streaming": {"units": [C, A, A, C, C, C], "error_semantics": ["unless {isEarlyAccess && ...} with missing attribute"], "opaque": ["now < releaseDate", "Oscar window", "releaseDate.offset(-24h)",
                                                          "local time-of-day window"], "reified": ["subscription/profile records"]},
    "c20_tags_n_roles": {"units": [B, B], "reified": ["record keyed by role name", "containsAll as a universal"]},
    "c21_tax_preparer": {"units": [B, B, B], "error_semantics": ["forbid unless {X && Y}: evaluates-without-error guards"], "reified": ["set of records", "template link", "context.consent record"],
                         "gaps": ["record equality also requires no extra keys in the member record; not expressible over an open "
                                  "attribute vocabulary (never exercised: perturbations do not add keys to set members)"]},
    "c22_photoapp": {"units": [A, A, A, B, A, A], "error_semantics": ["forbid unless {resource.owner == principal} with missing owner"], "reified": ["context.judgingSession"]},
    "c23_gitapp": {"units": [A] * 5},
    "k01_pod_reader": {"units": [A, A]},
    "k02_secret_reader_rolebinding": {"units": [A, A]},
    "k03_secret_reader_global": {"units": [A, A]},
    "k04_monitoring_aggregation": {"units": [B, B], "reified": ["labels as key=value strings"]},
    "k05_crontab_default_roles": {"units": [B], "reified": ["labels as key=value strings"]},
    "k06_configmap_updater": {"units": [A]},
    "k07_subresource_wildcard": {"units": [B, A], "reified": ["resource/subresource path string joined by the adapter"],
                                 "gaps": ["'*/sub' resource forms (not in the item)", "nonResourceURLs (not in the item)"]},
    "w01_s3_rw_bucket": {"units": [C, C], "opaque": ["action glob", "resource glob"]},
    "w02_deny_requested_region": {"units": [C], "opaque": ["action glob (NotAction)"]},
    "w03_mfa_selfmanage": {"units": [C] * 5, "opaque": ["action glob", "resource glob with ${aws:username}"],
                           "gaps": ["Bool is case-insensitive in AWS; VE compares exact strings (perturbations use lower case)"]},
    "l01_genealogy_biology": {"units": [A]},
    "l02_grandpa1_fact": {"units": [A, A]},
    "l03_grandpa1_noselfgrandpa": {"units": [A, A], "note": "assertion + fun grandpas; the check also uses the fact"},
    "l04_graph_weakly_connected": {"units": [A]},
    "l05_graph_ring": {"units": [A, A], "note": "pred ring + pred rootedAt"},
    "l06_graph_tree": {"units": [A, A, A, A], "note": "tree, forest, dag, acyclic (relation.als)"},
    "l07_marksweep_mark": {"units": [B, B], "reified": ["ternary left/right as tuple nodes"], "note": "pred mark + fun reachable"},
    "l08_addressbook_lookup": {"units": [B], "reified": ["ternary addr as tuple nodes; closure body captures parameter b"]},
}


def summary(item_id):
    u = COVERAGE[item_id]["units"]
    n = len(u)
    return {"units": n, "a": u.count(A), "b": u.count(B), "c": u.count(C), "d": u.count(D),
            "expressible_fraction": round((u.count(A) + u.count(B)) / n, 3),
            "fully_expressible": u.count(C) + u.count(D) == 0}
