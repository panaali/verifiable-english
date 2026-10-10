# AR-6: identity inventory with a ratchet lint

Architecture plan `docs/ARCHITECTURE-REVIEW-2026-10.md` (branch `design/arch-review`), section 4.3, row AR-6;
DRI decisions D1 and D7 (`manage-agents/arch-dri-decisions.md`, standing ruling R11).

## What changed

- `tools/identity_lint.py`: rule 4 of the relay lint, read with Python's `ast`.
  1. In a relayed module (the relay lint's `RELAYED`, its `helpers` and the functions of `RELAYED_FUNCTIONS`, imported
     from `tools/relay_lint.py`, which stays their one owner), no string expression starts with a Lean-owned prefix
     (`ve-meaning-`, `ve-environment-`, `ve-source-`, `ve-report-`, `ve-document@` in domain form, `ve-rights-`,
     `ve-soft-norms-`, `ve-norms-`, `ve-situation-`, `ve-model-`). This is stronger than "a `digest` or `sha256`
     call over such a literal": a prefix kept in a constant and passed later is also found.
  2. In every `ve/` module, no `ve-` domain literal: a string expression whose text is `ve-`, no whitespace, then a
     newline (the separator form every domain has). A string expression is a literal, an f-string, a `+` of them,
     or their `.encode()`; bytes literals count; docstrings do not.
- `tools/identity-sites.json`: today's sites, one entry per site, keyed by module, enclosing scope and domain. A
  Lean-owned entry names the batch that removes it (`AR-15`, `lf-16g` or `RD-7`); a Python-owned entry names its D7
  record (assist, adapters, proposals, argument package, checker build) and may not use a Lean-owned prefix.
  A site without an entry fails; an entry whose site is gone fails (stale).
- The ratchet: `--base REV` fails when a module's Lean-owned sites of a domain grew against the allowlist at REV (a
  site moved to another function of its module is not growth). `--prune` deletes stale entries and adds none.
  `tests/test_identity_lint.py` runs the lint on the tree with `--base $(git merge-base HEAD main)`.
- `docs/arch/AR-6/`: this report, `report.py` (evidence and the generated block below), `seed_faults.py`, and
  `evidence/` (census, Lean-domain search, scope, seeded faults). `tests/test_ar6_report.py` checks the report
  against the saved evidence only. The batch prompt asks for a saved-evidence report test; under D4 it moves to an
  `evidence.toml` check in AR-5b.

## Measured outcome

<!-- BEGIN GENERATED AR-6 METRICS -->
Census at `a4e873a4` (`tools/identity_lint.py --json`): **46 identity sites in 20 modules**, every one allowlisted; **33 Lean-owned** in 18 modules, 13 Python-owned records; 3 in relayed modules.

| Owner | Removed by or record | Sites |
|---|---|---:|
| Lean | AR-15 | 32 |
| Lean | lf-16g | 1 |
| Python | adapters | 2 |
| Python | argument package | 4 |
| Python | checker build | 1 |
| Python | proposals | 6 |

| Domain | Sites | Owner | Lean files whose source holds the domain text |
|---|---:|---|---|
| `ve-adapter-input-v1\n` | 1 | python | none |
| `ve-adapter-table-v1\n` | 1 | python | none |
| `ve-argument-diagnostic-record-v1\n` | 1 | python | none |
| `ve-argument-package-v1\n` | 1 | python | none |
| `ve-bundle-v0\n` | 1 | lean | none |
| `ve-claim-v1\n` | 1 | lean | `lean/VE/Service/Graph.lean`, `lean/VE/Service/Standalone.lean` |
| `ve-composition-v1\n` | 1 | python | none |
| `ve-deduction-v1\n` | 1 | lean | `lean/VE/Service/Family.lean`, `lean/VE/Service/Graph.lean` and 1 more |
| `ve-definitions-v0.2\n` | 1 | lean | none |
| `ve-document@2\n` | 1 | lean | `lean/VE/SpeechActs/Source/Run.lean` |
| `ve-english-grammar-v1\n` | 1 | lean | `lean/VE/EnglishGrammar/Run.lean` |
| `ve-english-lexicon-v1\n` | 1 | lean | `lean/VE/EnglishGrammar/Run.lean` |
| `ve-english-vocabulary-v1\n` | 2 | lean | `lean/VE/EnglishGrammar/Run.lean` |
| `ve-environment-{}\n` | 2 | lean | `lean/VE/CertificateWire.lean`, `lean/VE/Order/Wire.lean` and 3 more |
| `ve-evidence-assessment-v1\n` | 1 | python | none |
| `ve-meaning-{}\n` | 8 | lean | `lean/VE/CertificateWire.lean`, `lean/VE/Order/Wire.lean` and 2 more |
| `ve-model-{}\n` | 1 | lean | `lean/VE/Alternatives/Run.lean`, `lean/VE/Discourse/Loader.lean` and 1 more |
| `ve-norms-{}\n` | 2 | lean | `lean/VE/Norms/Replay.lean` |
| `ve-proposal-environment-v1\n` | 1 | python | none |
| `ve-proposal-overlay-v1\n` | 1 | python | none |
| `ve-proposal-source-v1\n` | 1 | python | none |
| `ve-proposal-{}-v1\n` | 1 | python | none |
| `ve-python-checker-build-v1\n` | 1 | python | none |
| `ve-report-{}\n` | 4 | lean | `lean/VE/Attribution/Run.lean`, `lean/VE/Discourse/Admission.lean` and 3 more |
| `ve-rights-{}\n` | 1 | lean | `lean/VE/Rights/Wire.lean` |
| `ve-senses-dictionary-v1\n` | 1 | lean | `lean/VE/Senses/Decode.lean` |
| `ve-senses-request-v1\n` | 1 | lean | `lean/VE/Senses/Run.lean` |
| `ve-situation-{}\n` | 1 | lean | `lean/VE/Readings/Wire.lean` |
| `ve-soft-norms-{}\n` | 1 | lean | `lean/VE/SoftNorms/Wire.lean` |
| `ve-source-{}\n` | 2 | lean | `lean/VE/Discourse/Loader.lean`, `lean/VE/Service/Family.lean` and 2 more |
| `ve-vocabulary-proposal-v1\n` | 2 | python | none |

Lean-owned domains that no Lean file holds yet: `ve-bundle-v0\n`, `ve-definitions-v0.2\n`.

Commits (`main..HEAD --no-merges`, base `c24aeab2`): 6; files changed: 12, none under `ve/` or `lean/`: yes.
Seeded faults: 6, each failing its named test: yes.
<!-- END GENERATED AR-6 METRICS -->

The plan counted "at least 36 sites in 18 modules (9 of them Python's own records)" with a text search for `"ve-`
strings passed to a hash call. The lint also reads the two domain constants of `ve/english_grammar/__init__.py`, the
bytes literal of `ve/argument.py` (`ve-argument-diagnostic-record-v1`) and the `.encode()` forms of
`ve/identity.py` and `ve/backends/speech_source.py`. The Lean-owned count (33 in 18 modules) is the number AR-15
takes to zero; the ratchet starts there.

## Owner of each domain (D7)

The rule applied: D7's Lean domains (meaning, environment, source, document, report, document hashes) are Lean's;
D7's Python records are Python's; any other domain is Lean's when Lean computes it (one owner per piece of logic),
and otherwise Lean's too, because D7 says Python owns only its app records. Four classifications need the DRI's
confirmation (HUMAN, owner: DRI):

1. `ve-claim-v1` (`ve/argument.py` `Claim.claim_id`) and `ve-deduction-v1` (`deduction_identity`) are classed
   Lean-owned (AR-15): Lean computes both (`lean/VE/Service/Graph.lean`, `Standalone.lean`, `Family.lean`), although
   D7's "argument packages" could be read to cover them. If the DRI reads D7 that way, the two entries become
   `"owner": "python", "record": "argument package"` and the Lean copy is the duplicate.
2. `ve-bundle-v0` (`ve/bundle.py`) and `ve-definitions-v0.2` (`ve/definitions.py`) are classed Lean-owned (AR-15)
   by D7's closed Python list, but no Lean code computes them yet. AR-15 would add them to Lean's rows, or the DRI
   adds them to D7's Python records.
3. `ve/document.py` `_report` is removed by lf-16g (inside the plan's P1 range 1226-1443, measured on `c24aeab2`);
   every other Lean-owned site is AR-15's. No site is RD-7's: RD-7 deletes `Superposed`'s assembly, `_dependencies`,
   `_replays`, `_mentions` and the wording selection, none of which holds a site.
4. The English grammar, vocabulary and senses ids are Lean-owned (Lean computes them in
   `lean/VE/EnglishGrammar/Run.lean`, `lean/VE/Senses/{Decode,Run}.lean`); their AR-15 part is offered to the English
   track's owner (plan 4.2).

## Coordination (plan 4.2)

Files touched: `tools/identity_lint.py`, `tools/identity-sites.json`, `tests/test_identity_lint.py`,
`tests/test_ar6_report.py`, `docs/arch/AR-6/*`, and the shared inventory `tools/gate-collection.json`. Checked
against `git diff --name-only main...<branch>` for every `lean-first/*`, `readings-defaults/*`,
`question-answering/*` and `infra/*` branch on 2026-10-10:

- `lean-first/b13b` and `question-answering/integrate` edit `tools/relay_lint.py` (each adds a module to
  `RELAYED`). The plan puts rule 4 in that file; to avoid the overlap it lives in `tools/identity_lint.py`, which
  imports `RELAYED`, so their additions are read by rule 1 once they merge. Moving the rule into `relay_lint.py`
  is a later one-file change.
- `tools/gate-collection.json` is a shared inventory (plan 4.2). Collision rule: "conflict in
  `tools/gate-collection.json`: take `main`'s file, run `uv run python tools/gate_collection.py --write`".
- `lean-first/b13b` moves `ve/admission.py`'s `ve-report-` digest from `_admit_document_python` to another function.
  After its sync the lint names the new site and the stale entry; per module and domain nothing grew, so the fix is
  the entry's `scope`. Collision rule for the allowlist: "conflict in `tools/identity-sites.json`: take `main`'s
  file, run `python3 tools/identity_lint.py --prune`; a site that moved to another function updates its entry's
  `scope`; a new Lean-owned site is refused (it needs a DRI signature)".
- `ve/ask.py` (question answering) and `ve/norm_admission.py` (b13b, already holding one allowlisted site) join the
  relayed modules when those branches merge; neither branch adds a domain literal elsewhere.

## Behaviour and rulings

No file under `ve/` or `lean/` changed (scope evidence), so no checker output can change: gate items 2 (corpus A/B)
and 3 (Lean statements, trust) have nothing to compare, and `DELTA.md` has no rows. No user-visible delta, so no
standing ruling R1-R10 is claimed. D7 (R11) is applied in the owner classification above.

## Seeded faults (each made its named test fail, then was removed)

Listed with their test and failure excerpt in `evidence/mutants.json` (`python docs/arch/AR-6/seed_faults.py`):
rule 1 off in relayed modules; rule 2 limited to relayed modules; stale entries accepted; the ratchet inverted; `+`
not read as one string expression; a Python record allowed on a Lean-owned domain.

## Tests and gate

- `tests/test_identity_lint.py`: the tree passes and has not grown since the merge base; every Lean-owned prefix
  fails in a relayed module; ten seeded preimage spellings fail and five non-preimages pass; rule 2 in every
  module; relayed functions only; allowlisted, new and stale sites; malformed entries; D7 records; the ratchet;
  `--prune`. `tests/test_relay_lint.py` is unchanged and passes.
- `tests/test_ar6_report.py`: the generated block, the census arithmetic, the Lean-domain search and the scope and
  mutants, all from saved files.
- Not run: `tools/lean_first_diff.py`, `lean/audit.py` and `lean_statements.py --check` (no `ve/` or `lean/` change).
  The full release gate runs once on the final HEAD; its result is in the batch's handoff report, since recording it
  in the tree would move HEAD.
