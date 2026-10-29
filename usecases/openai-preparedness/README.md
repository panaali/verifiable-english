# OpenAI Preparedness Framework v2: VE baseline

This case records a first VE translation of the *Preparedness Framework*, version 2. The 239-item answer key in
[PLAN.md](PLAN.md) section 6 was frozen before this translation and is unchanged. The baseline measures source
coverage and stage 0 admission. The key-answering harness remains `usecase-pf-run`.

The translation is deliberately sparse. It covers the six Table 1 level facts, selected F1 guideline readings and
direct D1 rules. It names other located clauses as OPEN or UNFORMALISED; it does not claim that untranslated Table 2
responses, Appendix B process, C.3 practices or severe-harm numbers are certified. PLAN section 12 lists deviations
from the planned D1 to D3 translation.

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
| [pf_vocabulary.py](pf_vocabulary.py), [environment.d1.json](environment.d1.json) | D1 vocabulary: six levels, three categories, 29 regulated predicates |
| [rules.d1.ve](rules.d1.ve), [facts.d1.ve](facts.d1.ve) | Source-linked rules, reading alternatives and six level/category facts |
| [pf_translation.py](pf_translation.py) | VE one-reading parser for each rule and fact block |
| [build_document.py](build_document.py), [spans.json](spans.json), [coverage.json](coverage.json) | Source partition and VE coverage status |
| [stage0.py](stage0.py), [environment.d2.json](environment.d2.json), [environment.d3.json](environment.d3.json) | D2 risk and D3 date probes, P1 to P8, P7 lint and M6 audit |
| [measure.py](measure.py), [gaps.json](../../docs/usecases/safetyfw/openai-preparedness/gaps.json) | Families and sole blockers for each non-CHECKED unit |
| [cases.json](cases.json), [answer-key.json](answer-key.json) | Frozen-key transcription: 67 cases, 239 items |

After building the Lean service, run `uv run python usecases/openai-preparedness/build_document.py --check`,
`stage0.py --check` and `measure.py --check` from the repository root. Without the pinned source, source-dependent
tests skip their rerun; saved evidence invariants remain tested.

## Coverage, 2026-10-29

VE classified 389 contiguous units covering all 67,418 bytes. The master map equals the D1 map.
CHECKED covers six Table 1 level markers and the SSC visibility clause. Three formerly CHECKED rule
units remain UNFORMALISED because they carry an AT wait or omit a source clause. Claims in headings and illustrative
sections remain visible whenever the whole source unit contains a duty or hedge.

| Status | Units | Bytes | Share |
|---|---:|---:|---:|
| CHECKED | 7 | 170 | 0.3% |
| OPEN | 29 | 5,446 | 8.1% |
| LABELLED | 48 | 5,327 | 7.9% |
| UNFORMALISED | 305 | 56,475 | 83.8% |

Each non-CHECKED byte has a blocker in [gaps.json](../../docs/usecases/safetyfw/openai-preparedness/gaps.json).
An OPEN reading set remains pending. UNFORMALISED units name the missing D1 feature or
source clause; these classifications do not certify the source claim. A unit with several blockers
counts under each. “Alone” means exactly one recorded blocker.

| Family | Units | Bytes | Alone: units, bytes | Here |
|---|---:|---:|---:|---|
| AP | 116 | 20,766 | 116, 20,766 | D1 has no act or complete rule for these duties |
| AT | 58 | 12,973 | 56, 12,386 | hedges, beliefs and expectations |
| DF | 7 | 1,185 | 0, 0 | default readings |
| ET | 28 | 8,086 | 17, 6,071 | event order and deadlines |
| JT | 24 | 4,157 | 10, 1,613 | open judgments |
| QT | 2 | 702 | 1, 305 | quantities and ratios |
| SC | 27 | 4,457 | 26, 4,341 | per-item or universal scope |
| WG | 1 | 183 | 0, 0 | weighing of risks |
| external reference | 2 | 309 | 2, 309 | outside standards |
| no claim to check | 48 | 5,327 | 48, 5,327 | title, contents, pure headings and marked examples |
| readings | 92 | 13,372 | 88, 12,489 | unselected source readings |

The 305 UNFORMALISED units carry specific blocker codes in `spans.json`; no unit remains
`not_translated`. VE reports 21 declared open terms and 14 unresolved reading sets as
residual. No assumption, bridge leaf or exception is represented as certified.

## Stage 0

[stage0.json](../../docs/usecases/safetyfw/openai-preparedness/stage0.json) saves the VE answers. P1 admits F2 as
OPEN. P2 admits the strict/default Table 1 set with UNKNOWN premises and one unresolved reading set. P3 admits the
severe-harm risk environment and checks one stated BIO-C `might` cell without deriving `leads`. P4 replays a W6a
certificate that the version date precedes retrieval; the 1/5th ratio and harm counts remain QT gaps. P5 and P6
confirm the 67,418-byte partition. P7 finds no packed identifier and M6 finds no untraced authored block. P8
refuses D1 with `judgments@0` plus `soft-norms@0`: the composed Lean route is unavailable.
