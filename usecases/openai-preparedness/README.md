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
| [pf_vocabulary.py](pf_vocabulary.py), [environment.d1.json](environment.d1.json) | D1 vocabulary: six levels, three categories, 28 regulated predicates |
| [rules.d1.ve](rules.d1.ve), [facts.d1.ve](facts.d1.ve) | Source-linked rules, reading alternatives and six level/category facts |
| [pf_translation.py](pf_translation.py) | VE one-reading parser for each rule and fact block |
| [build_document.py](build_document.py), [spans.json](spans.json), [coverage.json](coverage.json) | Source partition and VE coverage status |
| [stage0.py](stage0.py), [environment.d2.json](environment.d2.json), [environment.d3.json](environment.d3.json) | D2 risk and D3 date probes, P1 to P8, P7 lint and M6 audit |
| [measure.py](measure.py), [gaps.json](../../docs/usecases/safetyfw/openai-preparedness/gaps.json) | Families and sole blockers for each non-CHECKED unit |
| [cases.json](cases.json), [answer-key.json](answer-key.json) | Frozen-key transcription: 67 cases, 239 items |

After building the Lean service, run `uv run python usecases/openai-preparedness/build_document.py --check`,
`stage0.py --check` and `measure.py --check` from the repository root. Without the pinned source, source-dependent
tests skip their rerun; saved evidence invariants remain tested.

## Coverage, 2026-10-28

VE classified 389 contiguous units covering all 67,418 bytes. The master map equals the D1 map: D2 and D3 have
probes, but no source byte is promoted on their basis. CHECKED covers six short Table 1 markers and four
source clauses. The four F7/F9 clauses that lost temporal or per-item scope now retain their blockers. The
change-log RS15 undertakings and Appendix C restatements are OPEN rather than exposition.

| Status | Units | Bytes | Share |
|---|---:|---:|---:|
| CHECKED | 10 | 454 | 0.7% |
| OPEN | 28 | 5,292 | 7.8% |
| LABELLED | 67 | 10,345 | 15.3% |
| UNFORMALISED | 284 | 51,327 | 76.1% |

Each non-CHECKED byte has a blocker in [gaps.json](../../docs/usecases/safetyfw/openai-preparedness/gaps.json).
An OPEN reading set remains pending; a `not_translated` unit is counted under “readings” because its source reading
still needs an explicit translation. These bytes are a translation backlog, not a claim that a VE feature alone will
certify them. A unit with several blockers counts under each. “Alone” means exactly one recorded blocker.

| Family | Units | Bytes | Alone: units, bytes | Here |
|---|---:|---:|---:|---|
| readings | 225 | 37,657 | 221, 36,774 | untranslated clauses and pending RS0/RS4/RS5/RS15 choices |
| no claim to check | 67 | 10,345 | 67, 10,345 | title, contents and illustrative material |
| AT attitudes | 43 | 10,246 | 41, 9,659 | “could”, “may”, beliefs and expectations without a deontic reading |
| ET time | 28 | 6,319 | 17, 4,304 | before/during clauses, periodic review, the self-improvement interval |
| JT judgments | 23 | 4,003 | 10, 1,613 | named open terms, including threshold and safeguard sufficiency |
| DF defaults | 6 | 1,031 | 0, 0 | Table 1 guidelines and footnote 6 |
| QT quantities | 2 | 702 | 1, 305 | severe-harm definition and 1/5th over an interval |
| external reference | 2 | 309 | 2, 309 | named outside standards |
| WG weighing | 1 | 183 | 0, 0 | marginal-risk adjustment |
| SC scope | 4 | 284 | 3, 168 | Tracked Category suff/iff choice and per-item F9 scope |
| AP act phrases | 0 | 0 | 0, 0 | no separate AP-only unit in this partition |

The 284 UNFORMALISED units carry per-unit reasons in `spans.json`: `not_translated` 219, `hedged_claim` 41,
`event_order` 17, `quantifier_scope` 3, `quantity` 2 and `external_reference` 2. VE reports 21 declared open terms and 13 unresolved
reading sets as residual. No assumption, bridge leaf or exception is represented as certified.

## Stage 0

[stage0.json](../../docs/usecases/safetyfw/openai-preparedness/stage0.json) saves the VE answers. P1 admits F2 as
OPEN. P2 admits the strict/default Table 1 set with UNKNOWN premises and one unresolved reading set. P3 admits the
severe-harm risk environment and checks one stated BIO-C `might` cell without deriving `leads`. P4 replays a W6a
certificate that the version date precedes retrieval; the 1/5th ratio and harm counts remain QT gaps. P5 and P6
confirm the 67,418-byte partition. P7 finds no packed identifier and M6 finds no untraced authored block. P8
refuses D1 with `judgments@0` plus `soft-norms@0`: the composed Lean route is unavailable.
