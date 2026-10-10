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

**Binding is a closed list of relations to the request.** A field of a Lean answer is *bound* when its value
stands in one of these relations to the request the client sent, which the client can read off that request
without VE's semantics:

| # | Relation | The field … | Schema keywords today ([dialect](../../ve/backends/lean_service_schema/README.md)) |
|---|---|---|---|
| 1 | echoes | repeats a request value unchanged, or `null` where the request has none (the request `id`, `mode`, a case id, a label) | `x-echo`, `x-digest` |
| 2 | equals | equals a request value at a pointer that must exist | `x-equals` |
| 3 | counts | is the number of items of a request list | `x-count`, `x-count-where`, `x-count-presence` |
| 4 | measures | is as long as a request list, or is a span within a request text | `x-length` |
| 5 | indexes | is a position in, or a row-for-row pairing with, a request list | `x-index`, `x-zip`, `x-zip-or-empty`, `x-rows` |
| 6 | references | names an id, span, unit or choice that occurs in the request | `x-references` |
| 7 | is bounded by | is at most a request value (a budget, a limit) | none yet (AR-11a adds `atMost`, rendered `x-at-most`) |

The envelope's case digest (`x-digest`: the SHA-256 of the bytes of case `i` as the client sent it) is relation 1
over the request's bytes: a hash of the client's own text, not a VE identity domain.

**Derived values are Lean's.** A value computed with VE's semantics (a sum, a coverage, an identity hash over a
`ve-` domain, an unfolding, a verdict, a regenerated premise) is not bound by any relation above. It is covered by
a Lean theorem (an encoder theorem such as `runMode_fits`, or a soundness theorem of the runner) or by a
`ResponseDecode` invariant, and **Python never recomputes it to check it**.

**What Python checks** (R8): (a) the schema, fully typed: every leaf has a type, and a leaf with a closed domain
is checked against it; (b) binding: every id, span, count and choice the answer names exists in the request by one
of relations 1–7, and no row is empty or extra. Nothing else.

**Every leaf is accounted for.** A string or integer leaf of a response shape is bound (relations 1–7), in a closed
domain (`const`, `enum`, `pattern`, `x-tagged`, a Lean grammar), or marked as display text that the client never compares
with the request. A Lean census holds the count of unaccounted leaves at a shrinking list (AR-11a) and then at
zero (AR-11b).

## Consequences

- Review prompts and build checklists cite this ADR. "Python accepts a tampered derived field" is not a B finding
  when (a), (b) and the covering Lean theorem or invariant hold; a missing type or a missing binding is (R8).
- New relaying code adds no Python recomputation of a derived value. Existing recomputations are debt with an
  owner batch: the document coverage arithmetic (AR-11), identity preimages in relayed modules (the AR-6 lint
  ratchet, then AR-15, lf-16g, RD-7), the readings S2 regeneration (AR-17), the speech scope (AR-12c).
- A relation outside the list (for example "is the sum of request counts") is a derived value, or needs a new
  ADR that extends the list.
- Python's own records (assist, adapters, proposals, argument packages, checker build) are not Lean answers and
  keep their own identities (D7).
