# Lean-first batch 16c: document mode progress, incomplete

The branch forked from `67ae1e5a` (`main` at start). The saved scope captures the later
`main..f0c44d43 --no-merges` range after `main` advanced to `abc30811`.
This is an incremental implementation of the JSON boundary and response binding. The batch's
profile composition, 99% pilot target, corpus targets, Python deletion, and nine-corpus A/B
gate are **not complete**. No claim of batch 16c acceptance is made.

## Saved measurement

`report.py` renders this block only from the captured files in `evidence/`.
`tests/test_b16c_evidence.py` regenerates it and checks the per-case ledger. The scope is
`main..HEAD --no-merges` as captured at the final code commit, so later syncs and merges do not
change the historical report.

<!-- BEGIN GENERATED B16C METRICS -->
- Saved scope: `abc30811..f0c44d43 --no-merges`, 5 commit(s): `f0c44d43`, `1fde205e`, `c686d65f`, `8ff3ef5d`, `d094b056`.
- pilots: Lean decides 4/412; 408 listed residues.
- rights: Lean decides 0/1250; 1250 listed residues.
- norm_defaults: Lean decides 0/1010; 1010 listed residues.
- document: Lean decides 843/1816; 973 listed residues.
- Per-case residue rows: 3641. Seeded faults caught: 10/10.
- Clean gate at `f0c44d43`: passed; 13362 passed, 92 skipped, 0 failed; 36 Rust tests passed.
<!-- END GENERATED B16C METRICS -->

The 412 pilot inputs include eight `ve-document@2` documents, which go to the discourse
route. The @1 share is 4/404. Every residue, including invalid inputs the current mode
marks undecided, is named with its cause and source hash in `evidence/residues.json.gz`.
The dominant causes are norm-defaults (904 document-corpus cases, 339 pilots and all
1,010 norm-defaults cases), rights/readings (all 1,250 rights cases), soft norms (22
pilots), norm content (18 pilots), senses (7 pilots), fenced content (9 document cases),
and distinguishing models (26 document cases). The ledger preserves the smaller
malformed-profile and environment-key groups individually.

## Boundary and binding change

The document mode's case array and front matter use Lean's `Json.parse`. The frozen
`VE.JsonInput` parser and hash-frozen `Main.lean` are untouched. Certificate
canonicalisation keeps its null-refusing behavior; the document identity serializer
includes authored nulls, as Python's does.

`Json.parse` reads some texts as values other than Python's `json.loads` reads (16c
review B2), so after it accepts a front matter one lexical pass (`foreignLexeme`) and one
structural pass (`strayNull`) decide what the mode may read:

- a number other than a natural at most 2^53-1 (`2e0`, `2.0`, `-0`, `20e-1`, a larger
  integer) is `CheckerUnavailable`: Python reads a float or a negative integer where Lean
  reads a natural or another number;
- `null` is read only where Python's loader reads it as absent: a unit's `content` and
  `status` and a `MIXED` part's `content`. Any other `null` is `CheckerUnavailable`;
- an unpaired surrogate escape gets the JSON boundary's `InvalidInput` diagnostic in both
  loaders: `JSON strings must not contain lone UTF-16 surrogates` (`ve.wire.LONE_SURROGATE`,
  docs/spec/v0-language.md). Python's loader used to crash on one outside the environment
  (`UnicodeEncodeError` in the document identity). In the environment it already got this
  text from the relay's wire check, which `tests/test_relay_wire_check.py` pins.

`tests/test_lean_document_wrapper.py::test_null_and_number_forms_agree_with_python_or_fail_closed`
sets every front-matter member of every seed to `null` and writes every natural in six
number forms, through the first, second and last element of each list. Every mutant is
Python's answer or `CheckerUnavailable`. On the earlier 16c code, the review's exhaustive
probes of the same kind found 107 accepted-to-rejected flips on `null` and 355 changed
outcomes on number forms. The same probes now give 2,639 and 2,650 mutants, all agreeing or
failing closed. The constitution seed is now refused for its `null` reading content, as on
`main`.

The response schema is fully typed (16c review B1, B3). Each answer unit is a `RowUnit`
whose kind, meaning, support and status are decoded values (`Route.Admission.Kind`,
`Meaning`, `Support`, `UnitStatus`), rendered by `unitJson`. The schema names their domains:
`common.json#/$defs/kind`, the four meaning forms, and `Loader.supports` and
`Loader.statuses` as enums generated from the Lean lists. `ResponseShape.Encoders.Document.unit_fits`
and `meaning_fits` prove that every rendered row fits. The relayed narrowings are typed as
the front-matter narrowing objects that `Loader.narrowingIds` checked; they were typed as
token strings, so every `alternatives@0` or `risk@0` document with a narrowing was
`CheckerUnavailable`. The generated `alternatives-narrowed` seed now carries a nonempty
narrowing through every seed-based test. The receiver still binds each unit's authored
fields, checked AST, identities, parents, coverage tables and residual counts to the request.

## Verification and outstanding work

- `lake build ve_service`, `lake build ve_response_decode`, schema generation/check, and
  `lean/audit.py` passed. The audit found 4,865 named theorem declarations with only the
  approved axiom allowlist. No theorem statement changed.
- `evidence/mutants.json` (`seed_faults.py`): ten seeded faults each made its named test fail
  and were then removed. They are: treating null content as present; accepting a forged
  alternate checked formula; an untyped formula, narrowing or meaning in the response
  schema; Python reading an unpaired surrogate; and, in Lean, deciding every `null`,
  deciding every number form, refusing a `null` status, and reading an unpaired surrogate.
  The Lean faults are built into a temporarily pinned `ve_service`. A fault inside
  `foreignLexeme` itself fails the build at its `#guard`s.
- The full gate passed on clean code commit `f0c44d43` (`evidence/gate.json`):
  13,362 passed, 92 allowed skips, zero failures, and 36 Rust tests passed. The
  Lean full build and audit passed. `python3 tools/trust_map.py --check` passed
  with zero trusted-line growth. The initial clean gate found a deep JSON parser
  crash and stale inventories; the second had zero test failures but two unlisted
  Rust-scope skips. Both were fixed before the passing run.
- Nine-corpus A/B, differential fuzz across all parsers, and latency measurement
  were **not run** for this incomplete migration. The earlier document-focused
  suite and the saved per-case share are the only corpus measurements here.
- Lean still needs composition of the norm-defaults, rights, readings@1 (including
  defaults in parts), soft-norms, senses, norms, surface, model and remaining family
  routes. The Python document loader, coverage and report wrapper remain necessary for
  the listed residues and were not deleted. Deletion must follow a measured empty
  retained-path ledger and zero unlisted A/B differences.

Acceptance classification: the JSON boundary, binding and tests are AGENT work completed
here. The 16c profile/deletion/corpus gates are AGENT work pending. Any DRI acceptance of
diagnostic changes is HUMAN work pending; none is claimed.
