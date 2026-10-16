# Batch 14a deletion ledger

Base: `main` at `f1b719c7`. Plan row 14a (draft 3): the `definitions@0` surface sugar (`no S is P`,
`every S x that is P, (A)`, `(A) iff (B)` and the statement `define p(x, …) as (A)`) becomes Lean's, and the
Python fallback that batch 13b retained for it (13b `DELTA.md`, retained fallback 1) is deleted in the same
batch. Every deleted Python decision site is mapped to the Lean check that now owns it.

| Deleted Python decision site | Lean owner (caller) |
|---|---|
| `parser._parse_lean`, the `definitions@0` branch: a source the Python reader accepted through a sugar production kept Python's reading (acceptance, document and canonical text decided in Python) | `parse` mode, `Standalone.parseCase` through `Standalone.surfaceReader`: the family parsers `VE.Surface.parseWith`, `VE.Closure.Surface.parseWith`, `VE.Core.Surface.parseWith` read the sugar (`readNo`, `readEvery`, `iff`, `readStatement`/`readDefine`) with `Standalone.sugarOf` giving each defined predicate's sorts and identity-bound body; the family's typing check (`Formula.check`) then decides the statement. Caller `parser._parse_lean` (all sources, no branch) |
| the same branch: a source the Python reader rejected inside a sugar production kept Python's diagnostic (`exc.definitions_sugar`) | `parse` mode's rejection, `Standalone.parseRejection` → `ParseDiagnostic.scan` with the environment's `ParseDiagnostic.Definitions` (code, message and span, in source order, for every sugar production and `define`'s argument, body and identity checks). Caller `parser._parse_lean` |
| `parser._parse_python_marked` and the `_Parser.sugar` mark (which production was read) | deleted; no consumer (`test_the_retained_sugar_reading_is_deleted`, `tools/inventory_lint.py` no longer lists it) |

**Not a decision site, kept.** `parser._Parser`'s sugar productions stay as the constructor of the Python
document after Lean accepts (plan rule 2, "Lean validates, Python constructs": a Python rejection after Lean
accepted is `CheckerUnavailable`, and Lean's document must equal Python's, or the parse is `CheckerUnavailable`),
and as the reader of the environments outside Lean's `parse` scope (statement layers and W6 units, 13b's
recorded scope gap 5, which this batch does not change). `parser._parse_python` remains listed in
`tools/inventory_lint.py` for that reason.

`tools/relay_lint.py` and `tools/inventory_lint.py` pass on this branch. The order family takes no sugar:
the environment gate refuses `definitions@0` with `order@0` (`UnsupportedProfile: definitions on the order
family require an order definition layer`), so `surfaceReader` gives the order parser no sugar.
