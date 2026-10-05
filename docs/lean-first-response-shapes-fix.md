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

## Acceptance

| Item | Owner | Evidence |
| --- | --- | --- |
| Selector preserved for each request kind | AGENT | `tests/test_encoder_shapes.py::test_quantity_select_keeps_the_request_kind`; quantity encoder mutation failed the Lean build |
| Generated predicate entries have `arguments` | AGENT | `tests/test_encoder_shapes.py::test_generated_environment_predicate_has_arguments`; decision encoder mutation failed the Lean build |
| Prime environment field comes from the encoder | AGENT | `tests/test_encoder_shapes.py::test_environment_field_is_bound_to_the_prime_encoder`; replacing it with `{}` failed the Lean build |
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
