# Lean-first batch 9 (quantities): deletion ledger

Gate item 3 of `docs/LEAN-FIRST-PLAN.md` 5.1. Base `9aaf918d`, head `lean-first/b9`; line counts are
`git diff --numstat 9aaf918d HEAD`.

## Lines

| Language | Deleted | Added | What |
|---|---:|---:|---|
| Python `ve/` | 605 | 167 | `quantity_admission.py` (318); `units.py` elaborator and certificate/countermodel bodies (253 − 35); W6 validator calls in `environment.py` (18 − 42, the relay gate added); W6 branches in `admission.py` (10 − 10); the transport check of review B (`environment_wire.py`, `relay.py`, `rust_jsonl.py`: 6 − 80) |
| Rust | 1,021 | 19 | `ve-profile/src/units.rs` (922), `ve-core/tests/units.rs` (93), re-exports and dispatch; the refusal and its test added |
| Lean | 0 | 22 | the `check` mode's W6 branch (`VE/Service/Standalone.lean`, 10) and its row shape (`ResponseShape/Schemas/Check.lean`, 12); `check.json` is generated from it |

Plan row 9 estimated `units.py` validation and elaboration at about 580 lines. The elaboration and every
W6 use of the validators are gone; the validators themselves (`validate_units`, `validate_tag`,
`validate_slot_units`, `validate_extension`, `check_verbalisations` and the display checks, about 200
lines) stay because the **risk** route's legacy decoder in `Environment._decode` still calls them for
`risk@0` environments. They are batch 5's (risk blocks validated by their route). The numeral and date
helpers (`decimal_exact`, `day_number`, `iso_date`, `render_coordinate`) are the English surface's
(`ve/surface/time.py`) and go with the English track's E3 quantities batch.

## Decision sites and their owner

Every deleted Python and Rust decision site, mapped to the Lean check that now decides it. All W6 Lean
owners are in `lean/VE/Time/` and are reached through the service's `check` mode (typing, identities)
or `quantity` mode (`countermodel`, `certificate`, `document`).

| Deleted site | What it decided | Lean owner now |
|---|---|---|
| `units._Elaborator.term` (`var`, `const`, `num`, `decimal`, `date`, `add`, `scale`) | term typing, unit agreement (`UnitMismatch`, `TypeMismatch`), unknown constants and tags, calendar dates not added or scaled, `$int` variables (numbers2) | `Wire.decodeQuantity` → `elabTerm` (via `check`) |
| `units._Elaborator.formula` (`eq/lt/le`, `unary/binary`, `atom`, connectives, binders, temporal, W6b forms) | formula typing, predicate arities and slot units, order needs quantity terms, n-ary atoms refused, `$int` binders and W6b forms refused (numbers2) | `elabFormula` (via `check`) |
| `units._Elaborator.temporal` | `date_on` … `elapsed_days` regeneration and the date-range guards, nonnegative day offsets | `elabFormula` temporal cases |
| `units._Elaborator.tick`, `_source_nodes` | 10,000 nodes and depth 64 per statement, counted before elaboration | `decodeQuantity`'s `jsonNodes` and depth budgets |
| `units.elaborate_quantity` (fields, `format`, `traces`, claimed `Q`) | the payload shape, `traces` refused, `Quantity Q differs from regenerated formula` | `decodeQuantity` |
| `units.quantity_meaning_id` | the annotated meaning id (`ve-meaning-…` over the environment id and canonical `Q`) | `Admission.meaningId` (the `check` row's `meaning_id`) |
| `units._core_problem` regeneration | each statement's erased core and identity | the `check` row's `core` and `meaning_id` (the generator reads them) |
| `units.check_quantity_certificate` | the certificate's fields, outer binding, inner binding, step limit, replay | `checkW6Certificate` (`quantity` mode, `certificate`) |
| `units.quantity_countermodel` (with `search.check_countermodel` on the regenerated core) | model limits, the evaluation budget, refutation | `quantity` mode `countermodel` (`refutesB` on sorted domains) |
| `quantity_admission.py`: `_decode_unit`, `_decode_reading_set`, `_decode_node`, `_certificate`, `_decode_leaf`, `_decode_lemma` | document shape, ids, spans, kinds, reading sets, node fields, lemma certificates (`not established`), leaf labels | `VE.Time.Document.decodeDocument` |
| `quantity_admission.py`: `_leaf_admitted`, `_node_admitted`, `_diagnostic`, `_check_graph` | provenance per label, bridge/quoted-unit rules, the admission diagnostics, graph edges and their certificates | `VE.Time.Document.checkGraph` and admission |
| `quantity_admission.admit_quantity_document` | `documents@1` required, unit/node counts, duplicates, cited lemmas' leaves in the report, reading-choice compatibility, the report and its id | `VE.Time.Document` (`quantity` mode, `document`) |
| `environment.py` W6 calls: `validate_units`, `validate_slot_units`, `validate_tag`, `validate_extension` and the `unit_schema` type check, for non-risk envelopes | unit declarations, slot and constant units, profile tuple, sort/tag collisions, `$string` refused, verbalisations | `Wire.decodeEnvironment` (via `check`, before Python constructs) |
| `admission.py` W6 branches (`_admit_document_python`, the Lean-authority branch) | which route admits a W6 document | one branch: every W6 document goes to the `quantity` route under every authority |
| Rust `units.rs`: `declarations`, `display_injective`, `affixes`, `spaced`, `term`, `formula`, `temporal`, `exact_decimal`, `date_number`, `budget`, `quantity_limits`, `quantity_payload`, `quantity_case`, `quantity_document`, `meaning` | Rust's copy of every row above | deleted; `ve conformance` refuses `kind: quantity` |

## Kept on purpose

- `prove_quantity` and `check_quantity_limits` (`ve/units.py`): the certificate generator (rule 3,
  untrusted) and its own budget; every certificate it proposes is replayed by Lean before any verdict.
- `units.erased_environment`, `erased_data`, `core_formula`: the target vocabulary the generator searches
  in; the target's identity is checked against Lean's `target_environment_id` by the relay tests.
- `Environment._decode`'s W6 construction (the `units` mapping copy, `argument_units`, constant units):
  construction from input Lean accepted (rule 2); a failure is `CheckerUnavailable`.

## Checks

`tools/relay_lint.py` passes. `tests/test_stage0_inventory.py` and `tests/test_inventory_lint.py` pass
(no consumer of a deleted symbol). `tools/check_rust_deps.py` keeps the module graph with `units` removed
from `ve-profile`'s groups. Two reviewed layer edges are added (`tools/layer-exceptions.json`, synced to
`.importlinter`): `ve.environment -> ve.backends.relay` and `ve.units -> ve.backends.relay`.
