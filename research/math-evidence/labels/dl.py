"""ME-0 labels: Jumper et al. 2021, AlphaFold (`dl-alphafold/source.txt`, d001-d721; CC BY 4.0).

Every body unit (d001-d341) was read and labelled by hand; the reference list (d342-d721) is citation, LABELLED.
CHECKED units state measurements, counts, parameters or dates (all on or after 1970-01-01) that W6a expresses
exactly; an approximation word ("around", "approximately") makes a unit UNFORMALISED `approximation`. The graph
certifies what the text implies of those numbers: AlphaFold's medians are below the alternatives' ("whereas",
"compared with"); each printed point estimate lies in its printed interval (a consistency property of the printed
numbers, not a claim of the text); the BFD clustering counts are ordered as "removed" and "added as new clusters"
imply; 75% + 25% = 100%; "batch size of 1 per TPU core, hence 128 cores" for a batch of 128; the test-set date
limit equals the training cut-off it names; and the PDB copy dates restated under "Data availability" equal those in
Methods.
"""
from __future__ import annotations

TARGET = "dl-alphafold"
SOURCES = [("source.txt", "d")]

UNITS = {
    "day": {"scale": "1", "display": {"kind": "iso_date"}},
    "angstrom": {"scale": "100", "display": {"kind": "decimal", "label": "angstrom"}},
    "residue": {"scale": "1", "display": {"kind": "decimal", "label": "residues"}},
    "gdt": {"scale": "10", "display": {"kind": "decimal", "label": "GDT"}},
    "minute": {"scale": "10", "display": {"kind": "decimal", "label": "minutes"}},
    "hour": {"scale": "10", "display": {"kind": "decimal", "label": "hours"}},
    "bp": {"scale": "100", "display": {"kind": "percent"}},
}

CONSTANTS: dict[str, tuple[str, str, str]] = {}


def const(name, tag, desc):
    CONSTANTS[name] = (tag, desc, "the " + desc)
    return ["const", tag, name]


def eq(name, tag, value, desc):
    if tag == "day":
        return ["date_on", const(name, tag, desc), ["date", value]]
    if tag == "dimensionless":
        return ["eq", const(name, tag, desc), ["num", tag, value]]
    return ["eq", const(name, tag, desc), ["decimal", tag, value]]


def both(*fs):
    out = fs[-1]
    for f in reversed(fs[:-1]):
        out = ["and", f, out]
    return out


def c(name):
    return ["const", CONSTANTS[name][0], name]


L, U, C = "L", "U", "C"
D = "dimensionless"

CHECKED = {
    "d024": ("comparison", both(
        eq("af_backbone_median", "angstrom", "0.96", "AlphaFold median backbone r.m.s.d.95 on CASP14 domains"),
        eq("af_backbone_ci_low", "angstrom", "0.85", "lower end of AlphaFold's backbone 95% interval"),
        eq("af_backbone_ci_high", "angstrom", "1.16", "upper end of AlphaFold's backbone 95% interval"),
        eq("next_backbone_median", "angstrom", "2.8", "next best method's median backbone r.m.s.d.95"),
        eq("next_backbone_ci_low", "angstrom", "2.7", "lower end of the next best method's 95% interval"),
        eq("next_backbone_ci_high", "angstrom", "4.0", "upper end of the next best method's 95% interval"))),
    "d027": ("comparison", both(
        eq("af_allatom", "angstrom", "1.5", "AlphaFold all-atom r.m.s.d.95"),
        eq("af_allatom_ci_low", "angstrom", "1.2", "lower end of AlphaFold's all-atom 95% interval"),
        eq("af_allatom_ci_high", "angstrom", "1.6", "upper end of AlphaFold's all-atom 95% interval"),
        eq("alt_allatom", "angstrom", "3.5", "best alternative method's all-atom r.m.s.d.95"),
        eq("alt_allatom_ci_low", "angstrom", "3.1", "lower end of the alternative's 95% interval"),
        eq("alt_allatom_ci_high", "angstrom", "4.2", "upper end of the alternative's 95% interval"))),
    "d194": ("quantity", both(eq("bfd_families", D, "65983866", "number of BFD families"),
                              eq("bfd_sequences", D, "2204359010", "number of sequences BFD covers"))),
    "d196": ("quantity", both(eq("bfd_collected", D, "2423213294", "number of sequences collected for BFD"),
                              eq("bfd_identity", "bp", "30", "clustering sequence identity"),
                              eq("bfd_coverage", "bp", "90", "enforced alignment coverage"))),
    "d197": ("quantity", eq("bfd_clusters_initial", D, "345159030", "number of initial BFD clusters")),
    "d198": ("quantity", both(eq("bfd_min_members", D, "3", "smallest kept cluster size"),
                              eq("bfd_clusters_kept", D, "61083719", "number of BFD clusters kept"))),
    "d199": ("quantity", both(eq("bfd_added", D, "166510624", "number of Metaclust sequences added"),
                              eq("bfd_min_length", "residue", "150", "shortest Metaclust sequence kept"))),
    "d201": ("quantity", eq("bfd_unassigned", D, "25347429", "number of added sequences not assigned")),
    "d204": ("quantity", eq("pdb_training_copy", "day", "2019-08-28", "download date of the training PDB copy")),
    "d205": ("quantity", both(eq("pdb_template_copy", "day", "2020-05-14", "download date of the template PDB copy"),
                              eq("pdb70_copy", "day", "2020-05-13", "download date of PDB70"))),
    "d214": ("quantity", both(eq("drop_without_bfd", "gdt", "0.4", "mean accuracy drop without BFD"),
                              eq("drop_without_mgnify", "gdt", "0.7", "mean accuracy drop without MGnify"),
                              eq("drop_without_both", "gdt", "6.1", "mean accuracy drop without both"))),
    "d219": ("quantity", eq("training_cutoff", "day", "2018-04-30", "latest release date in training")),
    "d221": ("quantity", both(eq("crop_size", "residue", "256", "training crop size"),
                              eq("batch_size", D, "128", "training batch size"))),
    "d222": ("quantity", both(eq("batch_per_core", D, "1", "batch size per TPU core"),
                              eq("tpu_cores", D, "128", "number of TPU v3 cores"))),
    "d231": ("quantity", eq("distillation_set", D, "355993", "number of Uniclust sequences predicted")),
    "d232": ("quantity", both(eq("share_uniclust", "bp", "75", "share of examples from the Uniclust set"),
                              eq("share_pdb", "bp", "25", "share of examples from the PDB set"))),
    "d239": ("quantity", both(eq("time_256_ensembled", "minute", "4.8", "time for 256 residues, ensembled"),
                              eq("time_384_ensembled", "minute", "9.2", "time for 384 residues, ensembled"),
                              eq("time_2500_ensembled", "hour", "18", "time for 2,500 residues, ensembled"))),
    "d246": ("quantity", both(eq("cloud_protein_length", "residue", "2500", "protein length in the cloud setup"),
                              eq("gpus_requested", D, "4", "number of GPUs requested"))),
    "d258": ("quantity", eq("pdb_test_copy", "day", "2021-02-15", "download date of the test PDB copy")),
    "d259": ("quantity", eq("test_release_limit", "day", "2018-04-30", "release date limit of the test set")),
    "d262": ("quantity", eq("min_resolved_residues", "residue", "16", "fewest resolved residues kept")),
    "d263": ("quantity", eq("dedup_identity", "bp", "40", "sequence identity of the de-duplication clustering")),
    "d264": ("quantity", both(eq("min_ca_resolved", "residue", "80", "fewest residues with resolved alpha carbon"),
                              eq("max_chain_length", "residue", "1400", "longest chain kept"))),
    "d265": ("quantity", eq("test_set_size", D, "10795", "number of sequences in the test set")),
    "d267": ("quantity", eq("seqres_copy", "day", "2021-02-15", "download date of PDB SEQRES")),
    "d268": ("quantity", eq("template_release_limit", "day", "2018-04-30", "release date limit of templates")),
    "d323": ("quantity", both(eq("pdb_training_copy_da", "day", "2019-08-28",
                                 "training PDB download date (Data availability)"),
                              eq("pdb_template_copy_da", "day", "2020-05-14",
                                 "template PDB download date (Data availability)"))),
    "d324": ("quantity", eq("pdb70_copy_da", "day", "2020-05-13", "PDB70 download date (Data availability)")),
}

LISTS = {
    ("caption", L, None): [*range(30, 36), *range(40, 56), *range(78, 86), *range(122, 128), 138, *range(151, 155)],
    ("meta", L, None): [1, 2, 3, 13, 56, 60, 61, 73, 97, 117, 131, 139, 141, 142, 155, 161, 174, 175, 176, 177, 178,
                        189, 203, 208, 218, 230, 235, 248, 257, *range(273, 323), *range(325, 342)],
    ("citation", L, None): [156],
    ("empirical claim", U, "quantities"): [9, 10, 11, 19, 20, 23, 28, 29, 101, 134, 136, 137, 147, 149, 163, 164,
                                           169, 193, 215, 240],
    ("quantity", U, "approximation"): [5, 25, 119, 144, 145, 216, 223, 224, 244, 245],
    ("empirical claim", U, "events"): [8, 21],
    ("hedge", U, "attitudes"): [146, 148, 150, 167, 172, 173],
    ("empirical claim", U, "attribution"): [157, 159, 168],
    ("comparison", U, "calc-data"): [26, 36, 37, 38, 39, 57, 72, 92, 93, 104, 118, 121, 140, 217, 241],
    ("definition", U, "calc-stats"): [249, 250, 252, 253, 254, 255, 256, 272],
    ("definition", U, "calc"): [220],
}

LABELS: dict = {}
for (kind, status, feature), ids in LISTS.items():
    for i in ids:
        uid = f"d{i:03d}"
        assert uid not in LABELS, uid
        LABELS[uid] = (kind, status, feature) if feature else (kind, status)
for uid, (kind, formula) in CHECKED.items():
    assert uid not in LABELS, uid
    LABELS[uid] = (kind, C, formula)
LABELS["d242"] = ("mixed", [(None, "comparison", U, "calc"),
                            ("the representative timings", "quantity", C, both(
                                eq("time_256_plain", "minute", "0.6", "time for 256 residues, not ensembled"),
                                eq("time_384_plain", "minute", "1.1", "time for 384 residues, not ensembled"),
                                eq("time_2500_plain", "hour", "2.1", "time for 2,500 residues, not ensembled")))])
for i in range(1, 342):
    LABELS.setdefault(f"d{i:03d}", ("exposition", L))
for i in range(342, 722):
    LABELS[f"d{i:03d}"] = ("citation", L)


def graph(content, prefix, env, prove, q):
    leaves = {u: f"leaf_{u}" for u in ("d024", "d027", "d194", "d197", "d198", "d199", "d201", "d204", "d205",
                                       "d219", "d221", "d222", "d232", "d259", "d323", "d324")}
    nodes = [{"name": name, "quantity": content[u], "unit": u} for u, name in leaves.items()]
    b = "bp"
    claims = [
        ("alphafold_medians_below_alternatives",
         both(["lt", c("af_backbone_median"), c("next_backbone_median")], ["lt", c("af_allatom"), c("alt_allatom")]),
         ["d024", "d027"]),
        ("point_estimates_inside_their_intervals", both(
            *[f for lo, x, hi in (("af_backbone_ci_low", "af_backbone_median", "af_backbone_ci_high"),
                                  ("next_backbone_ci_low", "next_backbone_median", "next_backbone_ci_high"),
                                  ("af_allatom_ci_low", "af_allatom", "af_allatom_ci_high"),
                                  ("alt_allatom_ci_low", "alt_allatom", "alt_allatom_ci_high"))
              for f in (["le", c(lo), c(x)], ["le", c(x), c(hi)])]), ["d024", "d027"]),
        ("bfd_counts_ordered_as_described", both(
            ["le", c("bfd_clusters_kept"), c("bfd_clusters_initial")],
            ["le", c("bfd_clusters_kept"), c("bfd_families")],
            ["le", c("bfd_unassigned"), c("bfd_added")],
            ["le", c("bfd_families"), ["add", D, c("bfd_clusters_kept"), c("bfd_unassigned")]]),
         ["d194", "d197", "d198", "d199", "d201"]),
        ("sampling_shares_sum_to_whole",
         ["eq", ["add", b, c("share_uniclust"), c("share_pdb")], ["decimal", b, "100"]], ["d232"]),
        ("one_example_per_core_gives_the_batch",
         ["eq", c("batch_size"), ["scale", D, "1", c("tpu_cores")]], ["d221", "d222"]),
        ("test_limit_is_training_cutoff", ["eq", c("test_release_limit"), c("training_cutoff")], ["d219", "d259"]),
        ("data_availability_dates_match_methods", both(
            ["eq", c("pdb_training_copy_da"), c("pdb_training_copy")],
            ["eq", c("pdb_template_copy_da"), c("pdb_template_copy")],
            ["eq", c("pdb70_copy_da"), c("pdb70_copy")]), ["d204", "d205", "d323", "d324"]),
    ]
    by = {n["name"]: n["quantity"] for n in nodes}
    for name, formula, units in claims:
        premises = [leaves[u] for u in units]
        cert = prove(env, [by[p] for p in premises], q(formula))
        if cert is None:
            raise SystemExit(f"no certificate for {name}")
        nodes.append({"name": name, "quantity": q(formula), "premises": premises, "certificate": cert})
        by[name] = q(formula)
    names = [n for n, _, _ in claims]
    root = q(both(*[by[n]["formula"] for n in names]))
    nodes.append({"name": "stated_numbers_cohere", "quantity": root, "premises": names,
                  "certificate": prove(env, [by[n] for n in names], root)})
    return {"root": "stated_numbers_cohere", "nodes": nodes}


def _control(specs):
    """Negative control: the training PDB date under "Data availability" becomes 2019-08-29; the certificate built
    for the true date is kept, so only Lean's replay can catch it."""
    kind, status, formula = specs["d323"]
    specs["d323"] = (kind, status, _swap(formula, ["date", "2019-08-28"], ["date", "2019-08-29"]))
    return specs


def _swap(formula, old, new):
    if formula == old:
        return new
    return [_swap(x, old, new) for x in formula] if isinstance(formula, list) else formula


CONTROL = ("source.txt", _control)
