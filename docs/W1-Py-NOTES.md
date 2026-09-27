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
match. It closes each guard/carve-out with the rule binders and runs P0's
independent Earley all-derivations check on that formula. A second Earley check
covers the complete numbered block using the declared consequence phrases and
P0's formula grammar for conditions. The `ve.surface.norms` records reserve the statement keywords,
but the standalone entry point is separate from the existing formula parser.
The export manifest verifies environment, text and document hashes. Editing
transactions and IDE example/rewrite explanations are not yet implemented;
the concrete Z3/Z4 handoff is in `docs/W1-IDE-HANDOFF.md`.

`ve.adapters.cedar.translate` handles the no-attribute fragment for a supplied
finite request set, preserving Boolean tag errors, all-member set checks,
short-circuiting, `if` branch choice, entity membership, forbid override, and
linked templates. It names unsupported constructs as exclusions; if a policy
is excluded, `decisions()` does not claim a decision for the batch. The adapter
enumerates values occurring in the supplied requests, so it does not establish
a universal policy translation over arbitrary new requests. The W5 functional
and total attribute layer has not landed in this worktree; attribute and
context expressions remain explicit exclusions.

Active W2 norm units can now enter Python's FOL admission path. Norm objects
remain in the source document, and `layer:norms:<p>` leaves must equal regenerated
premises. The existing W2 graph checker and report identity are reused. W3
definition interleaving, a Lean `admission` case and wire acceptance theorem,
and W5 flags remain outstanding. The committed cross-language gate compares
1,100 Python/Lean elaborations (including 100 paired acts), six conflict
replays, 96 Python/Rust norm formula evaluations, and 22 Rust evaluations of
the pinned Cedar decisions. The legacy P0 checker is unchanged. `ve assist`
has no W1 norm hooks yet; its norm support is explicitly **not yet**.
These are remaining W1 acceptance obligations, not claims made by the Python
certificate helper. No Lean theorem was added by this worker.
