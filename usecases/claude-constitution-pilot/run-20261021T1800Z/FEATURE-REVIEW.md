# Feature review, run 20261021T1800Z (tag ve-green-ap-1b, previous ve-green-sc-1ad)

Six batches merged since the previous tag. Read: the `DELTA.md` and `REPORT.md` of each, `git diff ve-green-sc-1ad..ve-green-ap-1b --stat -- ve`, and `evidence/new-profile-probe.json`.

| Batch | What it adds | Reaches a document? |
|---|---|---|
| ap-1b | the `acts@0` profile: profile-table row (requires `norms@0`; refuses `soft-norms@0`, `rights@0`, `alternatives@0`, `speech-acts@0`, `closure@0`, `order@0`, `ve.discourse@1`), an `acts` vocabulary block of fixed phrases, a plain declaration's `form` ("is entitled", "has the right"); read by the environment mode and the norms, plain and norm-defaults routes | **No.** `ve document check` refuses it: the main translation answers `UnsupportedProfile: Unsupported profile acts@0`; the strict companion with an `acts` block of one fixed phrase answers `CheckerUnavailable: the Lean English reader's answer is malformed: a formula does not decode ... acts@0`. Measured in `evidence/new-profile-probe.json` |
| ap-1d | theorems and the specification `Accepts` for the act-phrase check (`LexicalProofs.lean`) | no (proofs only) |
| sc-3ab | anchor and label reach in `govern`/`governFast` | no (no caller until the document mode SC-1b); `scope@0` is still refused |
| me-5b | lowering of a derivation's claims (`Follows`, `HasCounterexample`) | no; `calc@0` is still refused |
| me-9b | inlining and identities over named values | no |
| speed-tmrescore | `tools/trust_mutants.py --rescore` | no (tooling) |

**Feature upgrades: 0 units, +0 B.** What `acts@0` would give the constitution once a document can name it: fixed phrases (an act may contain "and" or "or" inside a declared phrase, so the "existence-or-content" workaround of u0156.s03 and the other `shortened`/`folded`/`pointer` act workarounds of the 14 M4 units could become the source's own words; not measured, since no document can use the profile) and the entitlement forms for rights. It cannot be combined with `soft-norms@0`, `rights@0`, `alternatives@0` or `ve.discourse@1` at all, which a document that wanted those layers would need.

Unchanged and still refused: `scope@0`, `defaults@0`, `calc@0`, `judgments@0`. The unchanged start document rebuilt cmp-identical to the previous run's translation before any repair (`nd.py all`, 54 s).
