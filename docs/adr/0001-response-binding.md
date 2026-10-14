# ADR 0001: What Python checks in a relayed Lean answer (response binding)

**Status:** Accepted. Signed by the DRI on 2026-10-10 as decision D1 of the architecture review
(`manage-agents/arch-dri-decisions.md`: "D1 binding contract: T1(a)"), with standing rulings R8 and R11 of
`manage-agents/DRI-RULINGS.md`. The review is `docs/ARCHITECTURE-REVIEW-2026-10.md` on branch `design/arch-review`,
section 3, T1(a), and section 5, D1.

**Map:** [the architecture map](../ARCHITECTURE.md), section 3.

## Context

Lean decides; Python relays Lean's answer and displays it (lean-first rule 2). Python must still refuse an answer
that was not computed for its request: a row omitted, reordered, duplicated or substituted, or an answer for a
different case. Two texts disagreed on how far that check goes:

- [the service specification](../spec/lean-service.md), "Threat model": the client checks binding and
  well-formedness and "does **not** re-derive semantic content";
- the build checklists and the reviews of the lean-first and readings batches: bind every named id and count. The
  fixes met that by recomputing Lean's content in Python, for example the document coverage in `ve/document.py`
  and identity hashes over `ve-` domains at about 36 sites (review section 2.1, rows P2 and P3). That recreates the
  duplicated logic lean-first removes.

## Decision

D1 as the DRI signed it (review section 5):

- Binding is a closed list of relations to the request. A field that names a request item is bound only by
  `references` or `equals`.
- Derived values are Lean's, proved or checked by `ResponseDecode` invariants, and never recomputed in Python.
  Their leaves carry the `derived (guarantee)` mark. An encoder theorem is preferred, because a `ResponseDecode`
  invariant is checked only at test time.
- The census proves that every leaf is classified, not that it is correctly classified.

The rest of this section is T1(a) and T1(b) of the review, which D1 adopts, stated for the dialect of today.

**Binding is a closed list of relations to the request.** A field of a Lean answer is *bound* when its value
stands in one of these relations to the request the client sent, which the client can read off that request
without VE's semantics:

| # | Relation | The field … | Schema keywords today ([dialect](../../ve/backends/lean_service_schema/README.md)) |
|---|---|---|---|
| 1 | echoes | repeats the request's own `id` unchanged, or `null` where the request has none; or is the digest of its case | `x-echo`, `x-digest` |
| 2 | equals | equals a request value at a pointer that must exist (the `mode`, a label, a unit, a kind) | `x-equals` |
| 3 | counts | is the number of items of a request list | `x-count`, `x-count-where`, `x-count-presence` |
| 4 | measures | is as long as a request list | `x-length` |
| 5 | indexes | is a position in, or a row-for-row pairing with, a request list | `x-index`, `x-zip`, `x-zip-or-empty`, `x-rows` |
| 6 | references | names an id, span, unit or choice that is a member of a request set | `x-references` |
| 7 | is bounded by | is at most a request value (a budget, a limit) | none yet (AR-11a adds `atMost`, rendered `x-at-most`) |

The envelope's case digest (`x-digest`: the SHA-256 of the bytes of case `i` as the client sent it) is relation 1
over the request's bytes: a hash of the client's own text, not a VE identity domain.

**A field that names a request item is bound only by `references` or `equals`** (relation 6 or 2) to the relevant
request set. A format check is not a binding: `pattern`, `minLength` and `maxLength` constrain how a value is
written, not whether the request holds it, so an id that only matches a `pattern` is unbound. An `x-echo` does not
bind a named item either, because it accepts `null` when the item is absent. Python binds a stored value it owns by
equality and never by echo (D7).

**Derived values are Lean's.** A derived value (a sum, a coverage, an identity hash over a `ve-` domain, an
unfolding, an elaborated formula, a verdict, a regenerated premise) is not bound by any relation above. It is
proved by a Lean theorem on the encoder (such as `runMode_fits`) or checked by a `ResponseDecode` invariant, and
**Python never recomputes it to check it**. Its leaf carries the `derived (guarantee)` mark, naming that theorem or
invariant (`x-derived`, added by AR-11a). An encoder theorem is preferred wherever it is feasible, because a
`ResponseDecode` invariant is checked only at test time: a value covered only by an invariant is not checked at run
time, and a batch that relies on one says so and lists the values.

**What Python checks** (R8): (a) the schema, fully typed: every leaf has a type, and a leaf with a closed domain
is checked against it; (b) binding: every id, span, count and choice the answer names stands in its relation to
the request, a named request item by relation 2 or 6 only, and no row is empty or extra. Nothing else.

**Every leaf is in one of four classes.** Every string and integer leaf of every response shape is in exactly one
of these classes:

| Class | The leaf … | Shapes |
|---|---|---|
| bound | stands in one of relations 1–7 to the request; a leaf that names a request item, in relation 2 or 6 only | the keywords of the relations above |
| closed domain | takes its value from a fixed set | `const`, `enum`; `lean` and `copied` only when their inner shape is itself bound or closed; `x-tagged` when each of its branches is |
| derived (guarantee) | is a derived value, with the Lean theorem or invariant that guarantees it named in the mark | `x-derived` (AR-11a) |
| text | is display text that the client never compares with the request | `x-text` (AR-11a) |

`pattern` checks a format and puts a leaf in no class. A Lean census holds the leaves in no class at a shrinking
list (AR-11a) and then at zero (AR-11b). **The census proves that every leaf is classified, not that it is
correctly classified**: each mark stays a review item in its batch's statement review.

## Consequences

- Review prompts and build checklists cite this ADR. "Python accepts a tampered derived field" is not a B finding
  when (a), (b) and the covering Lean theorem or invariant hold; a missing type or a missing binding is (R8).
- New relaying code adds no Python recomputation of a derived value. Existing recomputations are debt with an
  owner batch: the document coverage arithmetic (AR-11), identity preimages in relayed modules (the AR-6 lint
  ratchet, then AR-15, lf-16g, RD-7), the readings S2 regeneration (AR-17), the speech scope (AR-12c).
- A relation outside the list (for example "is the sum of request counts") is a derived value, or needs a new
  ADR that extends the list.
- This decision changes only by a new signature of the DRI. `tests/test_architecture_docs.py` holds D1's clauses,
  each relation's keywords and each class's shapes, and pins the hash of the Decision section; a batch that adds a dialect
  keyword or a `Shape` constructor (AR-11a) records it here in the same merge.
- Python's own records (assist, adapters, proposals, argument packages, checker build) are not Lean answers and
  keep their own identities (D7).
