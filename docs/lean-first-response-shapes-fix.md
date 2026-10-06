# Lean response-shape follow-up

## Result

The row skeleton keeps the first matching request selector. The quantity `lower`
answer therefore requires `coordinate`; changing its encoder to emit `amount`
fails `lake build ResponseShape.Encoders.Quantity`.

The common environment shape uses `encodedEnvironment` instead of `copied`.
Its producer obligation binds `environment_prime` to `primeJson` or `primeJsonR`
and proves that every newly generated predicate entry fits the entry shape
extracted from the environment schema. The response checker still applies the
complete rendered environment schema. The request decoder supplies the source
environment fields; the producer skeleton does not reprove those copied fields.

## Enumerated values (shapes-fix3, B4)

The skeleton used to keep a field's allowed values only for a field named `status`, so
`document_status`, `point_status`, the conflict `verdict`s, `gaps` and the discourse `statuses`
were proved with any value. Extraction now keeps every `enum` and `const` wherever the schema
declares it (`Skel.ofEnum`: strings as `strIn`, other scalars as `Skel.lit`), and an array or
object alternative beside a literal domain keeps that it holds no string, so an `anyOf` of a word
list and a tagged array (`kinds`) or of `null` and an object (`witness`) keeps its words.

The encoder theorems now prove what the runners write: rejection codes and soft error codes
(every check of `SoftNorms.Phases`, through `ErrP`), diagnose classes (every finding of the wire
contract engine names a class of its table, and every registered table names public codes),
discourse unit statuses (through the loader), rendered kinds of every admission, background
generators, premise labels, and renderers of enumerations. Two values are request copies the
encoders do not produce, marked `copied` and checked by the client: the discourse mention `form`
(Lean's `Json` equality is not available to proofs, and the manifest decoder skips mentions of a
`{}` block) and, as before, its `target`. The rights `kinds` declare no enum.

`ResponseShape.EnumSites` lists every declaration and every field whose value resolves to one;
`tests/test_enum_domains.py` checks the list against the rendered schema files and proves, per
field, that every declared value fits and that `BOGUS`, the opposite Boolean and every value a
field of the same name declares elsewhere (the opposite verdict, another status word) do not.

## Acceptance

| Item | Owner | Evidence |
| --- | --- | --- |
| Selector preserved for each request kind | AGENT | `tests/test_encoder_shapes.py::test_quantity_select_keeps_the_request_kind`; quantity encoder mutation failed the Lean build |
| Generated predicate entries have `arguments` | AGENT | `tests/test_encoder_shapes.py::test_generated_environment_predicate_has_arguments`; decision encoder mutation failed the Lean build |
| Prime environment field comes from the encoder | AGENT | `tests/test_encoder_shapes.py::test_environment_field_is_bound_to_the_prime_encoder`; replacing it with `{}` failed the Lean build |
| Every enum and const field keeps its values | AGENT | `tests/test_enum_domains.py::test_every_field_keeps_its_domain` (each declared value proved, `BOGUS` and siblings proved not to fit), `::test_every_declaration_is_listed`, `::test_every_value_declaration_has_a_proved_field` |
| Reviewer's B4 probes rejected | AGENT | `tests/test_enum_domains.py::test_document_status`, `::test_point_status`, `::test_packages_conflict_verdict`, `::test_witness_conflict_verdict` |
| Independent review of new producer proof obligations | HUMAN, VE formalization lead | Deferred for review |
| External acceptance | EXTERNAL | None |

## Seeded failures

Each seed was applied to the worktree, checked in the foreground, and removed:

1. `Skeleton.lean`: collapse `.select` branches to a union. The full
   `ResponseShape` build failed in mode proofs. The separate quantity test
   checks the precise `lower` branch.
2. `Schemas/Common.lean`: make generated predicate `arguments` optional.
   The build accepted the weaker schema; the generated-entry regression test
   failed because an entry without `arguments` became provable.
3. `Skeleton.lean`: extract the encoded environment as `any`.
   The build accepted the weakened skeleton; the prime-environment regression
   test failed.

4. `Skeleton.lean`: extract every `enum` as `any`. The `ResponseShape` build
   failed: lemmas stated against schema domains (`rejectionCode_fits`) no
   longer type-check.
5. `Skeleton.lean`: extract a non-string `const` as `any`. The build accepted
   the weaker skeleton; `tests/test_enum_domains.py::test_every_field_keeps_its_domain`
   failed on the opposite-Boolean and `BOGUS` probes.

The two reported encoder mutations were also checked directly: removing
`arguments` from `decisionEntry`, and replacing `environment_prime` with
`{}`. Both made their Lean encoder-shape builds fail.

## Checks and scope

`lake build ResponseShape`, schema generation check, the focused encoder-shape
suite, and the axiom audit pass. `tools/lean_statements.py --check` reports
no change to approved theorem statements; its declaration inventory and the
gate collection list were regenerated. The work changes response-shape proof
coverage and generated schema organization. Input decoding, normalization,
budgets, verdicts, ledger state, English parsing, and use-case rules are outside
this change.
