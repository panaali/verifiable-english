# oseq-pf-d2d3-unit: the D2D3 unit holds every definition its D2/D3 code reads (fix round 1)

- Status: fix round 1 for `manage-agents/oseq-pf-d2d3-unit-review.final.md` (F1 B, F2 B, F-ready1 B), staged as `.new-pfd3`
  in `manage-agents/tools-local` (uc-audit.py, omission-seq-read.py, test_oseq_pf_d2d3.py). INSTALL WAITS FOR DECIDER READ.
  DRI DECISION ASKED (not a DELTA row; nothing reserved in VE): lift FSF's hold, `OMIT_CODE_HELD_OPEN`. Lifting it moves FSF's
  frozen D2D3 hash; the recommendation and the measured cost are below. The PF fix and its install do not wait on it.
- What changed: (1) F1: the closure now follows Python's scope rules. That covers imports inside a function, locals scoped to
  their own function, `global X`, class bodies, whole unit files followed through, and imports nested in a top-level if/try.
  The lines are cut where the parser counts them. (2) F2: every case's D2/D3 code is closure-checked (`OMIT_CODE_SEED`).
  RSP's closure is empty. FSF's is held open, pending the DRI.
- Tests: `test_oseq_pf_d2d3.py.new-pfd3`: 7 of 13 fail on the live code and all 13 pass on the staged code. The sibling
  suites pass. 12 seeded bugs, each caught. VE: docs only, so there are no VE product changes and no Lean/Python/Rust
  seeded bugs.

## Scope

The VE branch holds only this report and its evidence. The product is manage-agents `tools-local/` (the omission-seq counter
`uc-audit.py`, the reader `omission-seq-read.py` and the test `test_oseq_pf_d2d3.py`). The installed files are the reviewed
round-2 files (sha256 239bd9d2, 92da62b5, d9dc9e17). The staged diff against them is `fix1-changes.diff`.

## F1 (B): `_omit_reads` treated a name bound in any function of the part as local everywhere

Class: the closure's name analysis is not Python's, so it shows less than the D2/D3 code reads. The fix is structural.
`_omit_scopes` builds Python's scopes (module, function, lambda, class, comprehension, with `global`, `nonlocal`, `:=`,
`except as`, `match` captures and imports), and `_omit_resolve` resolves each read through them. `_omit_reads` returns:
- module-level reads (bare, `n.attr`, and declared globals);
- for a name bound by an import inside a function, `('import', statement, alias, how)`, which the closure follows like a
  top-level import.

The same class also covered these cases, now fixed:
- A file the unit already shows whole (PF's stage0.py) was never followed. Now what the reached definitions read is followed,
  without repeating the file. This replaces the test-only check, which looked at module-level imports only.
- A file given whole for a bare module read, or with a star import, was not followed. Now its statements' reads are
  followed, and a star-imported module is given whole.
- `_omit_binds` missed imports and bindings nested in a top-level `if`/`try`, and later top-level mutations (`X[k] = v`,
  `X.a = v`, `X += v`, `X.m(...)`). A function that rebinds `X` under `global` is not a binding of X: PF's mutation harness
  rebinds MUTANT, and an honest run holds the module value. Counting it pulls in the harness, about 90 KB.
- Lines were cut with `str.splitlines`, which also breaks on `\x0c`, `\x1c`-`\x1e`, `\x85` and ` `/` ` (review
  note C). `_omit_lines` now cuts at `\r\n`, `\r` and `\n` only, as the parser does. It is shared by `omit_code_section` and
  the closure.
- The reader refuses a counter without `OMIT_CLOSURE_VERSION = 'scope-1'`, so the 12:30Z counter cannot be paired with it.

Effect at the frozen commits: PF's parts, carry hash and largest prompt (110,338 bytes) are byte-identical to round 2. The
reviewer's "PF has no miss" holds, now checked by the closure itself. RSP and FSF are unchanged (`test_frozen`).

PROBE F1, run against the live counter: AssertionError, with the closure `''`. Against `uc-audit.py.new-pfd3` it passes,
with the closure `'def k(v):\n    return v\nQ = 1\n'`.

## F2 (B): FSF's s4() decides S4 outside the unit

Class: a D2/D3 decision path reads code outside its unit, and only PF's section was closure-checked. Structural fix:
`OMIT_CODE_SEED` names the D2/D3 code inside each whole OMIT_CODE file. RSP's seeds are stage0.py's `# --- D2:` and `# --- D3:`
sections; FSF's seed is severity_and_dates.py whole. `omit_code_parts` appends each seed's closure, as it does for PF's
section. `test_sweep` checks that every case in OMIT_CODE is seeded and that its closure is inside the unit or held open.
- RSP @ c8a4263c37e3: the d2()/d3() closure is empty, so the unit and its hash `324e55cb…` do not move. This confirms the
  reviewer's sweep.
- FSF @ da0822ae80: S4 reads outside the unit. `omit_code_open(FSF)` returns three parts:
  - run.py: `refute`, `fact_atoms`, `_model`, `holds`, `DOMAINS`, `predicates_of`, `constants_of`, `PROVER_*` and imports (3,793 bytes);
  - translation.py: `facts`, `base_environment`, `read_blocks`, `rule_fact_blocks`, `READING_SETS`… (4,672 bytes);
  - vocabulary.py: `LEVELS`, `DOMAINS`, `environment`, `BASE`… (20,402 bytes).

  This is the list the review asks for. `family_s` imports vocabulary but reads nothing from it, which matches the sweep.
  Round 2's FSF statement ("None… no FSF stored answer is affected") was wrong. `test_fsf_route` now checks the closure,
  not run.py's function names.

**The conflict (sent to the DRI).** The ruling `reviews/dri-decisions-20261116-oseq-render-unit.md` item 3 says both:
- "else the same fix for FSF, which has stored calls: list affected answers, do not re-read";
- "RSP and FSF carry hashes must not move".

Adding FSF's closure moves FSF's D2D3 hash from `ae4cbcc8…` to `33b87f17…`. The staged counter therefore holds FSF open:
`OMIT_CODE_HELD_OPEN`. The closure is computed and pinned, but not shown, carried or hashed. Lifting the hold means deleting
FSF's entry from `OMIT_CODE_HELD_OPEN`, a one-line change. `test_fsf_fixed` runs that variant.

**Measured cost of lifting the hold:** the stored D2D3 answers it would void.
- FSF run fsf-da0822ae80-20261115T1529Z: 15 answers have D2D3 in their units: S1-L1..L7, S2..S6 and D1..D3. All 15 Codex
  calls failed ("not a Codex run"), and the Opus seat has none, so no stored D2D3 answer is voided.
- Older reads `reviews/uc-audit-omission/fsf-reads.tsv` @ 9be13b93: D2D3 rows S1-L1..L7 and S3 cleared, S5 and S6 not
  cleared. They cannot carry to da0822ae80 either way: the vid differs (`ceea4e4b…` vs `be563496…`), the held D2D3 hash
  already differs (`a92fc6a5…` vs `ae4cbcc8…`), and no version-equality record exists. **Voided: none.**
- da0822ae80 to VE main 828449f6c0: with the hold lifted the D2D3 hash is equal at both commits (`33b87f17…`), so lifting
  it blocks no carry.
- run.py and translation.py are already in FSF's version id, since they are case harness files. A change to them already
  blocks carry.
- Prompt size with the hold lifted: 30 FSF D2D3 prompts, every unit exposed; the largest is 111,910 bytes (D3), under
  ARG_LIMIT 131,000.

**Recommendation:** lift the hold, with the same fix for FSF. It voids no stored answer, it costs at most 111,910 bytes per
prompt, and without it the 15 FSF D2D3 answers still to be read (S4 among them) would be judged on a unit missing what S4
calls: the X36 class item 3 names. The "must not move" condition protected stored answers, and there are none here.

PROBE F2: it fails on the live counter (lacks all six). On the staged counter with the hold in place it still fails, by
design until the DRI rules. With the hold lifted it passes (`test_fsf_fixed` asserts this).

## F-ready1 (B): 0 commits ahead

This branch now carries this report and its evidence, as other infra items do: p1-ready-unstartable-alert,
p1-path-hold-alert.

## Tests (python3 -I, run directly; logs in this directory)

| suite | live (installed) | staged (.new-pfd3) |
|---|---|---|
| test_oseq_pf_d2d3.py.new-pfd3 (13) | 7 fail: test_closure_rules, test_closure_scope, test_reads_oracle, test_fsf_route, test_fsf_fixed, test_sweep, test_reader_refuses_open_counter (`fix1-run-live.log`) | 13 OK (`fix1-run-staged.log`) |
| test_oseq_render_unit | n/a | 6 OK |
| test_omission_seq_read | n/a | 6 OK |
| test_oseq_bind | n/a | 20 OK |
| test_uc_omission_seq | n/a | 7 OK |
| test_uc_read_carryover | n/a | 6 OK |
| test_uc_audit_omission.sh | n/a | PASS |

New regression tests:
- `test_closure_scope` holds PROBE F1 and the rest of the class.
- `test_reads_oracle` is a differential: `_omit_reads` must equal CPython's `symtable` on every top-level statement of the
  three cases' D2D3 files and siblings, and on synthetic scope cases. It rewrites list/set/dict comprehensions as genexps
  because 3.12's PEP 709 inlining hides references in `symtable`.
- `test_fsf_route` and `test_fsf_fixed` hold PROBE F2.
- `test_sweep` covers the F2 class.

`test_closure`'s independent check now uses `symtable`, and its stage0 check covers imports inside the function.

Seeded bugs (`seeded-bugs.json`, temp copies in /tmp, staged files untouched): 11 in the counter and 1 in the reader. Each
makes at least one test fail. One mutant (m11, class body without the global fallback) survived the first run, and a
synthetic class case was added that kills it.

VE checks (docs-only change), all on 424fed4ed7:
- the selected tests (`mac-pytest.sh --select`, GitHub Actions run oseq-pf-d2d3-unit-424fed4e-t843380, 2 shards) exit 0.
  Two slow files selected only for weak reasons were deferred to the chain gate: tests/test_select_tests.py and
  tests/test_wire_gate_corpus.py.
- `lake build` passed (1475 jobs).
- `python3 lean/audit.py` passed (896 files, 10116 theorems, standard axioms only).

Not run: a new full gate (the merge train runs it). review-ready [gate] reads the worktree's full gate of f97dd2d0 (main, no
VE change). Its only failure passed on the same-commit rerun (R13):
`tests/test_ownership_floor.py::test_the_safety_framework_adapter_records_plan_12_item_27`. That is the item_27 flake from
`reviews/trial-stack-trip-20261116-cause.md`; this branch does not touch it. No test in main-known-red.txt was touched.

## Install (decider)

```
cd /home/seyran/code/manage-agents/tools-local
sha256sum uc-audit.py.new-pfd3 omission-seq-read.py.new-pfd3 test_oseq_pf_d2d3.py.new-pfd3
#   66919fd563035deeb386f7b19df40ade49cee7692a5117f05aed0d0fddd14d8c  uc-audit.py.new-pfd3
#   b287eb96fefb3098d6f126858c43a348717a54522155339d3ba3587d5fd0ccbc  omission-seq-read.py.new-pfd3
#   cdc5b1895920d7f3c8d93cda778658c6e94ee72846e9005c7acb32244c67b575  test_oseq_pf_d2d3.py.new-pfd3
# built against live: uc-audit.py 239bd9d2..., omission-seq-read.py 92da62b5..., test_oseq_pf_d2d3.py d9dc9e17...
for f in uc-audit.py omission-seq-read.py test_oseq_pf_d2d3.py; do cp -p $f $f.bak-20261116-pfd3; mv $f.new-pfd3 $f; done
cd .. && python3 -I tools-local/test_oseq_pf_d2d3.py && python3 -I tools-local/test_oseq_render_unit.py \
  && python3 -I tools-local/test_omission_seq_read.py && python3 -I tools-local/test_oseq_bind.py \
  && python3 -I tools-local/test_uc_omission_seq.py && python3 -I tools-local/test_uc_read_carryover.py \
  && zsh tools-local/test_uc_audit_omission.sh
```
Install all three together: the reader refuses an older counter. Both files are read per run, so no restart is needed.
After a DRI ruling to lift FSF's hold, delete FSF's entry from `OMIT_CODE_HELD_OPEN` in uc-audit.py. Then update the test's
expectations: test_frozen gets FSF `33b87f17…`, and test_fsf_route and test_sweep get the hold lifted.

SIZE: 347 counter + 3 reader diff lines; 306 test diff lines.
