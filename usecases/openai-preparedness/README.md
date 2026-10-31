# OpenAI Preparedness Framework v2: VE translation and answers

This case records a VE translation of the *Preparedness Framework*, version 2, and VE's answers to its frozen key.
The 239-item answer key in [PLAN.md](PLAN.md) section 6 was frozen before this translation and is unchanged. The
baseline (`usecase-safetyfw-b`) measured source coverage and stage 0 admission; `usecase-pf-run` completed the
reading choices the key needs and added the key-answering harness. The answer counts below are **not
audit-validated**: `uc-audit` has not reviewed this translation.

The translation answers per reading choice. It covers the six Table 1 level facts, source-linked rules for every
F family and the reading alternatives the key names. It names other located clauses as OPEN or UNFORMALISED; it
does not claim that pending reading sets, Appendix B process, C.3 practices or severe-harm numbers are certified.
PLAN section 12 lists the deviations of both rounds.

## Source

| Field | Value |
|---|---|
| Document | OpenAI, *Preparedness Framework*, version 2, last updated 15 April 2025, 22 pages |
| URL | `https://cdn.openai.com/pdf/18a02b5d-6b67-4cec-ab64-68cdfbddebcd/preparedness-framework-v2.pdf` |
| Retrieved | 2026-10-28 |
| PDF SHA-256 | `fae6e4cc6f7212a010bb9348fc0cde1fe711b9cad426c6a99db97740ee52729b` |
| Text SHA-256 | `d2e3dd5b80e5bb86079911230358e0c2bb78f12435757959e14dae50e4d48d0f` (67,418 bytes) |

The source states no licence. The PDF, extracted text and generated `.ve.md` document stay in the pinned source
area outside git. `build_document.py --check` accepts `--source`, verifies the hash, and writes its temporary
document under `/tmp` for VE's check.

## Files and run

| File | Role |
|---|---|
| [pf_vocabulary.py](pf_vocabulary.py), [environment.d1.json](environment.d1.json) | D1 vocabulary: six levels, three categories and source-linked regulated acts |
| [rules.d1.ve](rules.d1.ve), [facts.d1.ve](facts.d1.ve) | Source-linked rules, reading alternatives and six level/category facts |
| [pf_translation.py](pf_translation.py) | VE one-reading parser for each rule and fact block |
| [build_document.py](build_document.py), [spans.json](spans.json), [coverage.json](coverage.json) | Source partition and VE coverage status |
| [stage0.py](stage0.py), [environment.d2.json](environment.d2.json), [environment.d3.json](environment.d3.json) | D2 risk and D3 quantity/date probes, P1 to P8, P7 lint and M6 audit |
| [measure.py](measure.py), [gaps.json](../../docs/usecases/safetyfw/openai-preparedness/gaps.json) | Families and sole blockers for each non-CHECKED unit |
| [cases.json](cases.json), [answer-key.json](answer-key.json) | Frozen-key transcription: 67 cases, 239 items |
| [run.py](run.py), [results.json](results.json) | VE's answer, route and reason for every key item; metrics M1 to M10; mutants m1 to m6; the unscored reruns without N1 and N2 |
| [reference.py](reference.py) | Independent stdlib reading of PLAN 3 and 4 for families A, B, C and G |

After building the Lean service, run `uv run python usecases/openai-preparedness/build_document.py --check`,
`stage0.py --check`, `measure.py --check` and `run.py --check` (about ten minutes: it reruns the key under each
mutant and narrowing) from the repository root. Without the pinned source, source-dependent
tests skip their rerun; saved evidence invariants remain tested.

## Coverage, 2026-10-30

VE classified 389 contiguous units covering all 67,418 bytes. The master map equals the D1 map.
CHECKED covers six Table 1 level markers and the SSC visibility clause. Three formerly CHECKED rule
units remain UNFORMALISED because they carry an AT wait or omit a source clause. Claims in headings and illustrative
sections remain visible whenever the whole source unit contains a duty or hedge.

| Status | Units | Bytes | Share |
|---|---:|---:|---:|
| CHECKED | 7 | 170 | 0.3% |
| OPEN | 44 | 9,073 | 13.5% |
| LABELLED | 48 | 5,327 | 7.9% |
| UNFORMALISED | 290 | 52,848 | 78.4% |

Each non-CHECKED byte has a blocker in [gaps.json](../../docs/usecases/safetyfw/openai-preparedness/gaps.json).
OPEN reading sets remain pending. UNFORMALISED units name the missing D1 feature or
source clause; these classifications do not certify the source claim. A unit with several blockers
counts under each. “Alone” means exactly one recorded blocker.

| Family | Units | Bytes | Alone: units, bytes | Here |
|---|---:|---:|---:|---|
| AP | 119 | 21,554 | 111, 19,678 | D1 has no act or complete rule for these duties |
| AT | 57 | 12,623 | 53, 11,750 | hedges, beliefs and expectations |
| DF | 12 | 2,098 | 0, 0 | default readings |
| ET | 28 | 8,086 | 16, 5,728 | event order and deadlines |
| JT | 34 | 6,282 | 11, 1,966 | open judgments |
| QT | 2 | 702 | 1, 305 | quantities and ratios |
| SC | 28 | 4,896 | 25, 3,945 | per-item or universal scope |
| WG | 1 | 183 | 0, 0 | weighing of risks |
| external reference | 2 | 309 | 2, 309 | outside standards |
| no claim to check | 48 | 5,327 | 48, 5,327 | title, contents, pure headings and marked examples |
| readings | 95 | 14,325 | 82, 11,019 | unselected source readings |

The 290 UNFORMALISED units carry specific blocker codes in `spans.json`; no unit remains
`not_translated`. VE reports 21 declared open terms and 31 unresolved reading sets as
residual. `usecase-pf-run` moved ten units from UNFORMALISED to OPEN (2,021 bytes): each now carries the reading
set or rule the key needs (section 1's deployment sentence, the two Table 1 contribution bullets, 3.3's first next
step, the residual-risk bullet, 5.2's third-party evaluation, Appendix B's decisions without the SAG, the Board's
reversal and the fast track, and C.3's access practice). No assumption, bridge leaf or exception is represented as certified.

## Stage 0

[stage0.json](../../docs/usecases/safetyfw/openai-preparedness/stage0.json) saves the VE answers. P1 admits F2 as
OPEN with its RS3 reading set unresolved. P2 admits the strict/default Table 1 set with UNKNOWN premises and one unresolved reading set. P3 admits the
severe-harm risk environment and checks four Table 1 `might` cells without deriving `leads`; the two AIS cells
retain stated AT gaps. P4 replays W6a certificates for the version/retrieval ordering, two conditional 365-day
date shifts and the 2021/2024 baseline ordering. It admits the one-fifth elapsed-time inequality; the vague
harm-count thresholds remain QT gaps. P5 and P6
confirm the 67,418-byte partition. P7 finds no packed identifier and M6 finds no untraced authored block. P8
refuses D1 with `judgments@0` plus `soft-norms@0`: the composed Lean route is unavailable.

## Answers to the frozen key (2026-10-30)

`run.py` asks VE each of the 239 key questions through the document built from `rules.d1.ve` and `facts.d1.ve`
(D1: soft-norms@0 rule selection under both completion defaults and every reading choice the question's rules
name; W1 conflict checks with certificates; relational-fol@0 entailment certificates), D2's risk tables (S6 to S8)
and D3's quantity certificates (T, S1 to S5, D). A case model is built from `cases.json` and VE evaluates every
selected premise on it before a rule is asked. `results.json`'s `comparison` array gives each item's `key`, `ve`,
`agree`, `status` (`agree`, `disagree`, `UNDECIDED-faithful`, `resource-limit`), `route` and `cause`. The useful
answers figure is `comparison[].agree` (`metrics.useful_answers`). These counts are not audit-validated.

| Family | Correct / key | Undecided (named VE or translation limit) | Disagree |
|---|---:|---:|---:|
| A per level and activity | 140 / 140 | 0 | 0 |
| B per level | 36 / 42 | 0 | 6 (key finding: truncated cells) |
| K process triggers | 22 / 22 | 0 | 0 |
| T AIS-C indicator | 2 / 2 | 0 | 0 |
| C conflicts | 7 / 7 | 0 | 0 |
| G gaps | 9 / 10 | 1 (G7: SC) | 0 |
| N never applies | 3 / 4 | 1 (N4: SC) | 0 |
| S severity | 8 / 8 | 0 | 0 |
| D dates | 4 / 4 | 0 | 0 |
| **Total** | **231 / 239** | **2** | **6** |

The six disagreements are B-*L*/MREP: `answer-key.json` holds the cell `SOME(N` (and a stray `soft: RS1=default`)
where PLAN 6.2 says `SOME(N ∧ unscoped)`; VE's answer equals the PLAN cell, and `reference.py` reports the same six.
The key is not edited (PLAN 12, REPORT "Key findings"). Against PLAN 6.2's cells the count would be 237 / 239.
G7 stays undecided because footnote 5's indicator relation is not in D1; N4 because D1 has no closure premise that
Table 1's six levels are all the levels there are. Neither is counted as correct.

All six PLAN 11 mutants change exactly their named results (M9 6/6); the m2 rule is flagged by the invention audit.
Without N1 (every RS0 statement read as a prediction) 35 answers change: 34 rest on a statement made with "we
will" or in the present tense (B's CAPREP, SAFEREP, DISC and PUBRES, K1, K4, K5, K12, K14, K15, K17, G10), and N3
becomes undecided because those rules leave the document; without N2 only C2 and C-doc change, as PLAN 6.5 says.
Neither rerun is scored.
