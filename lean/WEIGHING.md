# Weighing reasons, in Lean (`lean/VE/Weighing/*`)

Specification: weighing-PLAN section 3.4 (on branch refresh/weighing-20261028 at bda82d18c; the weighing family's
plan item brings it to main). This file is a stub: so far it holds only the zone's six shared definitions (item
wg-6a), which defeasible's DF-5 also states its zone over. The zone answers (`zoneOf`, `recordCheck`, `ZoneAnswer`)
and their theorems are WG-6's and extend `Zone.lean`. No service mode answers through these files yet, and no
current answer changes.

## Files

| File | Contents |
|---|---|
| `Zone.lean` | `decisionAtoms`, `openNames`, `AdmissibleCompletion`, `OutcomeIn`, `SettledZ`, `ZoneUnknown` |
| `ZoneExamples.lean` | the six on defeasible's decoded DF-α document and on a small literal document, as `#guard`s and proved `example`s |

## Definitions

- **`decisionAtoms D M`.** Every ground atom a decider could settle in the finite situation `M`: each decision
  predicate of the soft document `D` (its exceptions, switches and outweighing choices), at each tuple of `M` of that
  predicate's sorts, predicate by predicate and tuple by tuple in `M`'s order.
- **`openNames L`.** The predicate names a completion may choose freely for the layered document `L`: its decision
  predicates, then the unsaid tables of its unspecified regulated predicates.
- **`AdmissibleCompletion U X M opens record R`.** `R` is a way to finish the situation `M`: it agrees with `M` on
  every predicate outside `opens`, it agrees with the record on every atom the record fixes, and the finished
  situation satisfies the document's base admissibility on `fill U` with the route's extra premises `X`.
- **`OutcomeIn U M R r vs`.** In the situation `M` finished by `R`, the regulated predicate `r` comes out true at
  the tuple `vs` (its base outcome formula on `fill U` holds there).
- **`SettledZ U X M opens record r vs b`.** The outcome of `r` at `vs` is settled as `b`: at least one admissible
  completion exists, and every admissible completion gives the outcome `b`. Without a completion nothing is
  settled, so a contradictory record settles nothing.
- **`ZoneUnknown α`.** Why a zone answer is `unknown`: `budget`, the enumeration stopped because there were more
  open atoms than the limit; or `branch`, a complete enumeration left an assignment that nothing refuted and no
  checked completion confirmed.
