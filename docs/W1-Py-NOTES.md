# W1 Python/Rust implementation status

This branch implements a standalone `norms@0` Python runtime. `ve.norms.NormDocument`
validates rule names, typed guards and carve-outs, same-predicate precedence,
precedence depth, and regulated dependency cycles. It computes applicability,
subtree yielding, selection, outcomes, three-clause elaboration, and base
conflict formulas. `check_conflict` returns `CONFLICT` only for a validated
finite base witness and `CONFLICT-FREE` only after replaying a tableau
certificate for every target. Missing or exhausted evidence is `UNKNOWN`.
Witness tuples retain predicate argument order. Same-sign overlap has a
separate witness report.

Regulated declarations, canonical act phrases, dual links, profile background
premises, and finite-model profile validity are implemented in Python. Rust
accepts the declaration schema and checks profile validity; as required by
section 11.6, it does not elaborate norms. Existing environments without a
`regulated` declaration retain their canonical bytes and identity.

`ve.norm_english` provides the four deontic rule wordings, default sentences,
guards and carve-outs, a stable-name manifest, and bare import. `ve.norm_strict`
round-trips named rules through the existing strict formula parser. The norm
English parser counts declared consequence matches and rejects a non-unique
match. It also closes each guard/carve-out with the rule binders and runs P0's
independent Earley all-derivations check on that formula. The numbered block
envelope itself is parsed deterministically; a single combined Earley grammar
for the whole rule block remains to be added. The `ve.surface.norms` records reserve the statement keywords,
but the standalone entry point is separate from the existing formula parser.
The export manifest verifies environment, text and document hashes. Editing
transactions and IDE example/rewrite explanations are not yet implemented.

`ve.adapters.cedar.translate` handles the no-attribute fragment for a supplied
finite request set, preserving Boolean tag errors, all-member set checks,
short-circuiting, `if` branch choice, entity membership, forbid override, and
linked templates. It names unsupported constructs as exclusions; if a policy
is excluded, `decisions()` does not claim a decision for the batch. The adapter
enumerates values occurring in the supplied requests, so it does not establish
a universal policy translation over arbitrary new requests. The W5 functional
and total attribute layer has not landed in this worktree; attribute and
context expressions remain explicit exclusions.

The W2 document units, W3 definition substitution and interleaving, W5 flags,
new `norms-route` Lean wire admission, and cross-language elaboration gate are
not present in this branch. The legacy P0 checker is unchanged. `ve assist`
has no W1 norm hooks yet; its norm support is explicitly **not yet**.
These are remaining W1 acceptance obligations, not claims made by the Python
certificate helper. No Lean theorem was added by this worker.
