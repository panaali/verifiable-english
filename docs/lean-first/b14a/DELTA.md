# Batch 14a delta: the `definitions@0` sugar is Lean's

Base `main` at `f1b719c7` (the merge base); head: this branch. Plan row 14a (draft 3): the `definitions@0`
surface sugar (`no S is P`, `every S x that is P, (A)`, `(A) iff (B)`, `define p(x, …) as (A)`) is read and
decided by Lean's `parse` mode, and the Python fallback that batch 13b retained for it (13b `DELTA.md`, retained
fallback 1) is deleted in the same batch. [LEDGER.md](LEDGER.md) maps each deleted Python decision site to its Lean
owner.

## Size

| Language | Files | Added | Deleted |
|---|---|---|---|
| Lean (`lean/VE`, product code, generated inventories excluded) | 9 | 416 | 122 |
| Python (`ve/parser.py`) | 1 | 8 | 39 |
| Python tools (`tools/inventory_lint.py`, the deleted helper's entry) | 1 | 1 | 1 |
| Tests (`tests/test_lean_first_b14a.py` new, `tests/test_stage2_parse.py`) | 2 | 300 | 8 |

The deleted Python is the whole fallback: the `definitions@0` branch of `parser._parse_lean`,
`parser._parse_python_marked`, the `_Parser.sugar` mark and the `definitions_sugar` exception tag. Rust is unchanged.

## Gate 5.1

1. **Suite.** The full gate runs once, last, on the committed final HEAD (the commit that adds
   [REPORT.md](REPORT.md)); its record is `gate-result.json` in the worktree and its numbers are in the build report. Test changes are only
   the sugar tests: `tests/test_stage2_parse.py` now asserts that Lean is asked about every sugared source.
2. **Corpus A/B** (`evidence/corpus-ab.json`, made by `tools/lean_first_diff.py compare` with
   [`DELTA.json`](DELTA.json)): probe (python and lean authorities), conformance (both authorities), every
   historical pilot document (501, all `pilot/*` branches at recording time), readings, norm defaults and the
   document corpus, 65,772 records. **65,768 are identical; 4 are unavailable on both sides with identical
   outputs; 0 unlisted.** Base and head recordings are byte-identical (sha256 `b5d08cbb…ce9` both): no source in these corpora
   reaches the changed path with a different answer. The rights, discourse and quantity corpora were not
   recorded: none holds a `definitions@0` environment with surface text (the rights generator's profiles are
   `relational-fol@0, norms@0, soft-norms@0, rights@0`; the discourse corpus has no `definitions@0`; the quantity
   corpus has one `definitions@0` environment but its operations take ASTs, not surface text), and the deleted
   branch ran only for an environment with `definitions@0`, so their path is unchanged.
   **The batch's own corpus** (`sugar_ab.py`, `evidence/sugar-ab.json`, recordings `evidence/sugar-*.json.gz`):
   every sugar fixture of `tests/test_lean_first_b14a.py` (accepted, rejected, n-ary, perturbed and two-fault
   sources over every family it names, plus the bare environment) through the public `parse` and `canonicalize`,
   760 records: 410 identical, 350 wording (below), 0 unlisted.
   **Differential fuzzer** (`difffuzz_ab.py`, `evidence/difffuzz-ab.json`): `--ci` and `--deep 1` for the 14 date
   seeds 2026-09-29..2026-10-12 at base and head. Every run is `ok`: the same new-signature counts on both
   sides, **0 head-only signatures**, the baseline 250 entries on both sides, none unreproduced or unreviewed.
   **The baseline does not grow.**
   **Use-case harnesses:** not rerun by the A/B tool; their answer keys are pinned by the suite (item 1).
3. **Deletion ledger.** [LEDGER.md](LEDGER.md). `tools/relay_lint.py` and `tools/inventory_lint.py` pass;
   `test_the_retained_sugar_reading_is_deleted` checks that the deleted symbols are gone.
   **Relay mutation gate** (`tools/relay_mutation_gate.py`, `evidence/relay-gate-{base,head}.txt`): the `parse`
   route refuses or allows its 326 mutants with no failure. The gate reports 133 failures at the head and the
   same 133 lines at the base (stale allow-list entries and five readings-route acceptances): they are `main`'s,
   not this batch's.
4. **Latency** (`latency.py`, `evidence/latency.json`, 5 interleaved runs per side, host load ≈155 on both):
   the parse service's CPU per call stays at 0.34–0.56 ms (p50) for plain and sugared sources on both sides. The
   public `parse` of a sugared source now asks Lean (base: Python only), so its wall time p50 rises from
   0.2–31 ms to 9–49 ms; the plain sources are unchanged in kind. Every value is far inside section 4's budgets.

## Deltas

| # | Class | Delta | Records | Ruling |
|---|---|---|---|---|
| W1 | wording | A sugar diagnostic under the default authority now carries Lean's class prefix: `expected ' is '` becomes `SyntaxError: expected ' is '` (18 text pairs, listed in `evidence/sugar-ab.json` `wording_pairs`). The code and the span are the same in every record, and the head text is the base text after `Code: `, so every quoted name is kept; `sugar_ab.py compare` checks these three conditions for each record and classes any other change `unlisted`. These are the same texts that 13a/13b already gave the non-sugar productions. | 350 (sugar corpus) | SIGNED by standing ruling R1 (DRI-RULINGS.md) |
| U1 | unavailable on both sides | The constitution pilot's `probes/companion/translation-companions-with_source_word.ve.md` (runs 20261010T1800Z and 20261012T1800Z): `CheckerUnavailable` (ReadingsConstruction … KeyError) at base and head, identical. No `definitions@0` source. | 2 | SIGNED by standing ruling R7 (DRI-RULINGS.md) |
| U2 | unavailable on both sides | The UDHR pilot's `experiment-whole/translation-whole.ve.md`, run 20261012T0600Z: **base exceeds 8 GB**. Re-recorded once under an 8 GB address-space limit with `VE_RUST_TIMEOUT=300` (`rerecord.py`), the Rust checker's allocation fails at base and head with the same text; neither side has the infra/oom-rootcause memory budget. Run 20261012T1800Z: the recorder's 600 s limit on both sides (`add_pilots.py`). | 2 | SIGNED by standing ruling R7 (DRI-RULINGS.md) |
| C1 | latency | Lean now parses sugared sources the base read in Python; the service's CPU stays under 1 ms per call and the public wall time under 50 ms (item 4). | — | SIGNED by standing ruling R4 (DRI-RULINGS.md) |
| T1 | trust budget | Trusted Lean lines grow (`docs/trust-baseline.json` history entry for batch 14a: V 37,154 → 37,451, S 9,788 → 9,775): the sugar readers, the sugar diagnostics and the parse mode's sugar table replace the Python decision path deleted in the same change. The 25 new declarations are classified in `tools/trust-classes.json` with the class of the declaration each extends (the family readers and `Standalone`'s reader D[V], like `parseRaw` and `parseCase`; the scanner's `define` and `Definitions` G[V], like `formula` and `Cursor`), so `unclassified` is 0 and V is unchanged by the classification. (The history entry's remark that they stay unclassified predates this; the file is generated, so it is not hand-edited.) | — | SIGNED by standing ruling R6 (DRI-RULINGS.md) |

There are no verdict, order or availability changes, so no row needs a further DRI signature.

## Final review corrections

The three review probes F1–F3 are regressions in `tests/test_lf14a_long_parse.py`
and `tests/test_lf14a_response_shape.py`.
F1 restores the base acceptance of long, valid sugar sources: the relay compares
the whole canonical text internally without imposing the public printer's
65,536-byte output limit. F2 gives parse AST rows a typed grammar for every
formula, term and edge constructor; this is R8's schema condition. F3 binds
diagnostic offsets and line/column to the request source through the shared
`x-source-span` shape rule; this is R8's request-binding condition. Neither
schema correction changes a genuine service answer. Like b14d's
`x-reading-plan`, the new `x-source-span` keyword awaits D1 classification in
ADR 0001; `tests/test_architecture_docs.py` tracks it in the pending D1 set,
and `docs/INTEGRATION-GAPS.md` names it. The existing W1, U1,
U2, C1 and T1 deltas retain their standing signatures R1, R7, R7, R4 and R6,
respectively, with the evidence and tests listed above.

The 7 sense-pack probes of the constitution pilot run 20261008T0600Z first differed only in the recorder's
scratch path inside a missing-file message (the recorder copies `.ve.md` files, not their `pack.json`). They were
re-recorded with the pack beside them (`rerecord.py`) and are now identical.

## Seeded bugs (`evidence/mutants.json`)

Each was planted, shown to fail the named test, and removed.

| Id | Language | File | Behaviour |
|---|---|---|---|
| M1 | Lean | `lean/VE/Service/Standalone.lean` | `define` is accepted only with its identity-bound body |
| M2 | Lean | `lean/VE/Service/ParseDiagnostic.lean` | a rejection inside a sugar production gets the retained reader's code, message and span from Lean |
| M3 | Python | `ve/parser.py` | Lean, not Python, is asked about every sugared source (the fallback restored) |
| M4 | Lean | `lean/VE/Core/Surface.lean` | the family parsers read the sugar as the core formula it abbreviates |

## Not changed, recorded

* `parser._Parser`'s sugar productions remain as the constructor of the Python document after Lean accepts (plan
  rule 2), and as the reader of the environments outside Lean's `parse` scope (statement layers and W6 units,
  13b's scope gap 5). For those environments the Python texts of the sugar diagnostics still reach the user;
  they equal Lean's without the class prefix. Moving those environments into Lean's scope is outside 14a
  (FOLLOW-UP, owner: the 13b scope-gap batch).
* Batches 14b–d (non-first-order norm guards, n-ary core definitions, coupled reading sets) are not touched.
