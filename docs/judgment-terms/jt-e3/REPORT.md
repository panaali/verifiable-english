Status: **PASS**, κ = 424/529 = 0.801512; HEAD: the `feature/jt-e3` commit containing this report.
Changed: preregistered 60-term sample, two independent raw ratings, and count sensitivity in `RESULTS.md`.
Open items: none in JT-E3. No signature is reserved; no product or theorem statement changed.
Model calls: `SIGNED by the DRI 2026-10-28 (prompts/dri-task-lp2001.txt item 5; recorded in reviews/lp-answers-20261028T2001.md item 5)`.

## Delivery and limits

| Acceptance item | Owner | Evidence |
|---|---|---|
| Frame and statement gate | AGENT | `64339b6ce:research/judgment-terms/open_term_class.tsv` exists (91 rows, 89 terms); `git diff main...HEAD` adds or changes no theorem statement |
| Sample and bar before calls | AGENT | `9792edb01` committed `PRE-REGISTRATION.md` and `SAMPLE.tsv` before either rater; `d9c7681df` froze 60 blind source sentences before calls |
| Two independent models | AGENT | Claude Sonnet 5.5 on the picker-selected `claude-saeedi-danial`; Codex GPT-6 Astra after `codex-allowed.sh` passed; raw outputs and provenance in this directory |
| Agreement and counts | AGENT | `RESULTS.json`, `RESULTS.md`; `analyze.py`; `tests/test_jt_e3.py` |

One Codex CLI initialization failed before a model call because its account
state was read-only; `codex.init-failure.stderr.txt` records it. The runner
then used a private `/tmp` state directory with the same subscription OAuth
file. There were **two successful rater calls total**, one per model, each
covering all 60 terms. Prompt bytes were 21,063 per rater and answer bytes
were 4,040 (Codex) and 3,902 (Claude), far under 1M CW. Codex reported 7,702
tokens used; Claude's CLI reported 12,045 cache-created, 9,624 cache-read,
2 direct input, and 3,060 output tokens. No API key or paid credits were used.
Claude's raw wrapper contains list-price accounting, not a payment receipt.

Plan section 6 JT-E3's sample, independent classification, κ ≥ 0.7 bar,
fail consequence, five constitution terms and two reporting axes are delivered.
D5 remains a measurement annotation only. The pilot-byte delta expected from
this experiment is **0 B**; the retrospective counts do not assert new coverage.
`DELTA`: none (docs, evidence, and an experiment runner only). Trusted growth:
0 K, 0 S, 0 V; no `ve/`, `lean/`, or `rust/` product change. No generated
input changed, so regen, Lean build/audit and trust mutants do not apply.
No full release gate was run here; the chain runs it on committed final HEAD.
Next item: **JT-3, after JT-E1**.

## Seeded bugs, restored

| Changed file | Planted bug | Failing test |
|---|---|---|
| `analyze.py` | Force observed agreement to zero | `test_hand_computed_kappa` |
| `runner.py` | Ignore the requested answer id | `test_answer_retypes_and_rebinds_every_row` |
| `analyze.py` | Ignore the disagreeing-term exclusion | `test_count_excludes_disagreement_and_borderline_independently` |

Each mutant failed its named test with exit 1 and was removed. The real tests
passed with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv/bin/python -m pytest
--noconftest -q tests/test_jt_e3.py`. The repository conftest normally starts
a full native build even for this model-free test; `--noconftest` kept the
iterative check limited to the code touched.
Final selected run: Mac `select_tests --base 9d646572f --run`, 148 units, 0 failed (snapshot `511448cc`).

## Self-review against BUILDER-CHECKLIST

1. N.A. — no Lean response route.
2. PASS — section 6 rows and `RESULTS.json` cover all experiment deliverables.
3. PASS — three seeded failures in `test_jt_e3.py` (table above).
4. N.A. — no Python/Lean/Rust product answer changed.
5. N.A. — no relayed Lean field or request binding changed.
6. N.A. — release gate belongs to the chain on final HEAD.
7. PASS — the DRI's item-5 signature above covers calls; no DELTA row.
8. PASS — `git diff main...HEAD` changes no product output; DELTA none.
9. PASS — selected tests include `tests/test_jt_e3.py` (selected run recorded in final handoff).
10. N.A. — no Lean statement or proof changed.
11. PASS — `runner.py` uses one call per model; provenance records two, below both caps.
12. N.A. — no checker CPU or memory path changed.
13. N.A. — no test was removed or renamed.
