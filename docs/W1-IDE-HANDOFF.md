# W1 norm editor handoff (Z3/Z4)

The runtime accepts and renders strict norm units through `ve.norms.NormDocument`,
`ve.norm_strict`, and `ve.norm_english`. The editor should call those functions
for validation and canonical text; it should not infer a rule from the modal
word alone. An edit transaction keeps the block's stable `name` and editor
`handle` when moving, renumbering, or changing that block. A copied block gets
a fresh name and handle. `render_english(..., handles=...)` supplies the bound
manifest, and `parse_english(..., manifest=...)` rejects stale mappings.

For each accepted rule, show its canonical paraphrase, one checked situation
where it decides and one where it does not. Use `NormDocument.selection` and
`outcome` for the two cases, then validate each finite base model with
`ve.norms.check_witness` or the existing evaluator before rendering it in
document terms. `check_conflict` already returns a typed witness and names the
selected rules. For a carve-out, say that this rule is silent, other rules may
decide, and quote the actual `default_sentence(env, predicate)` outcome when
none does. For an exception, include a case where the parent guard fails but
the child applies. A same-sign overlap is named `Overlap`, not a conflict.

The rewrite panel should implement the cases in
[norms.md](spec/norms.md), sections 2.5 and 2.6: undeclared `a report` versus
`each report`, carve-out versus a new permitting exception, rejected `should`
and `generally`, cross-predicate priority as a guard, and `A doctor may` as
`Every doctor may`. For object-position `every`, offer `each`. The IDE must
show the distinguishing checked situation before accepting the rewrite. The
runtime intentionally returns a syntax or declaration diagnostic without an
invented example when no checked model is available.

Z3 owns the explanation and rewrite interaction; Z4 owns edit transactions
and identity-preserving document updates. The Python and Lean wire checkers
continue to regenerate premises from the final norm units.
