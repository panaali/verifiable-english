# Anthropic's Responsible Scaling Policy, translated into VE

This case translates a published frontier-lab safety policy into VE: Anthropic's *Responsible Scaling Policy*,
version 3.4, effective 8 July 2026. It follows the method of [safety-framework](../safety-framework/README.md)
(Google DeepMind's Frontier Safety Framework 3.1). VE will answer four questions about it:

- What does the policy require at each named threshold?
- Do any two of its commitments conflict?
- Which thresholds or situations does no rule cover?
- Which commitments can never apply?

The text is someone else's, so the translation keeps every reading the text allows. It names every vague term as an
open term with the person or body who decides it. It adds no default, permission, threshold or causal link that the
text does not state.

The plan, with the answer key written and frozen before any VE run, is [PLAN.md](PLAN.md); the freeze is
[KEY-FREEZE.md](KEY-FREEZE.md). The baseline contains the translation, byte accounting and stage 0 probes. The
`usecase-rsp-run` round adds the key-answering harness. PLAN section 12 lists both rounds' deviations. No key cell
changed. The answer counts below are **not audit-validated**; `uc-audit` has not reviewed this translation.

**Conflict of interest.** This is the policy of the company that makes the model that wrote the translation. Every
rule cites its source sentence. The plan was reviewed by a model of another company (gpt-6-astra). The run round's
`reference.py` recomputes families A, B, C and G from PLAN sections 3 and 4 alone.

## The source

| Field | Value |
|---|---|
| Document | Anthropic, *Responsible Scaling Policy*, version 3.4, "Effective July 8, 2026", 21 pages |
| URL | `https://www-cdn.anthropic.com/files/4zrzovbb/website/0bacdc8440ea96e62a8766d99ebe1d4eea6d5f3a.pdf` |
| Retrieved | 2026-10-28 |
| PDF SHA-256 | `6247b9e4001fd342827526fabc476c9d4dd6b2041ac00055f0ccda26f4d0b07d` |
| Text SHA-256 | `c7de7fe2f1f44cdd650efb327ecd798f1140034cf6328eb2e494de587c2c3063` (59,410 bytes, from [source/extract_text.py](source/extract_text.py)) |

The PDF states no licence, so neither it nor its text is committed. The build reads the stored copy in
`~/code/manage-agents/pilots/anthropic-rsp/source/` and checks its hash. Committed files hold hashes, byte spans,
unit ids and short quotations only.

## Files

| File | Contents |
|---|---|
| [rules.d1.ve](rules.d1.ve) | 76 VE rules: one per commitment and per reading of it, each with the sentence it translates |
| [facts.d1.ve](facts.d1.ve) | 11 premise blocks (15 premises): the four thresholds, the "highly capable" definition, and T4's definitions under RS3o, RS3i and RS3c |
| [rsp_vocabulary.py](rsp_vocabulary.py), [environment.d1.json](environment.d1.json) | the vocabulary, with 64 regulated predicates (Lean's limit); each predicate's description is its legend, and each open term names its decider |
| [rsp_translation.py](rsp_translation.py) | loads and parses the rules and premises with VE's one-reading check |
| [cases.json](cases.json), [answer-key.json](answer-key.json) | the cases and the 126 answers of PLAN sections 5 and 6, transcribed after the freeze |
| [build_document.py](build_document.py), [spans.json](spans.json), [coverage.json](coverage.json) | the byte-by-byte accounting of the source text: 303 units |
| [stage0.py](stage0.py) | stage 0: probes P1 to P8, the identifier lint and the invention audit ([stage0.json](../../docs/usecases/safetyfw/anthropic-rsp/stage0.json)) |
| [measure.py](measure.py) | what each byte that is not CHECKED waits for ([units.json, gaps.json](../../docs/usecases/safetyfw/anthropic-rsp/)) |
| [run.py](run.py), [results.json](results.json) | each key item, VE route and reason, comparison, metrics M1–M10 and six exact-change mutants |
| [reference.py](reference.py) | independent stdlib reading of PLAN sections 3–4 for families A, B, C and G |
| [../../tests/test_safetyfw_usecases.py](../../tests/test_safetyfw_usecases.py) | the test: the frozen key and its transcription, the span accounting, stage 0 and the gaps |

Run, after `lake build` in `lean/` and `python3 tools/rust_build.py`:

```
uv run python usecases/anthropic-rsp/rsp_vocabulary.py   # environment.d1.json
uv run python usecases/anthropic-rsp/build_document.py   # spans.json, coverage.json (needs the pinned source)
uv run python usecases/anthropic-rsp/stage0.py           # stage0.json
uv run python usecases/anthropic-rsp/measure.py          # units.json, gaps.json
uv run python usecases/anthropic-rsp/run.py              # results.json and M1–M10
uv run python usecases/anthropic-rsp/reference.py        # independent A/B/C/G reference
```

The generators take `--check` to compare with the committed output instead of writing it. `reference.py` prints
its comparison without writing a file.

## Answers to the frozen key (2026-10-29)

`results.json` records one row per key item in `comparison`, with `agree`, `status`, `route` and `cause`. The progress
score can read `comparison[].agree` for useful answers and `status == "UNDECIDED-faithful"` for faithful undecided
answers. These counts are not audit-validated until `uc-audit` reviews the translation.

| Family | Correct / key | Faithful undecided |
|---|---:|---:|
| A thresholds | 40 / 40 | 0 |
| B scope | 12 / 12 | 0 |
| K process | 21 / 27 | 6 |
| T automated R&D | 9 / 9 | 0 |
| C conflicts in the translation | 8 / 8 | 0 |
| G gaps | 5 / 8 | 3 |
| N never applies | 3 / 5 | 2 |
| S severity | 7 / 8 | 1 |
| D dates | 6 / 9 | 3 |
| **Total** | **111 / 126** | **15** |

All 15 undecided rows name a translation or VE feature limit in `comparison[].cause`; none is counted as a wrong
verdict. W1 conflict answers identify conflicts in the translated rules. Their status as source-policy conflicts
awaits the independent source check required by DRI ruling R14.

## Span accounting (2026-10-28)

All 59,410 bytes of the source are in exactly one of the document's 303 units. VE gives each unit its status when
it loads the D1 document. A unit routed to D2 (severity) or D3 (dates) is CHECKED when stage 0 admits that document
with its evidence.

| Status | Units | Bytes | Share |
|---|---|---|---|
| CHECKED | 51 | 5,327 | 9.0% |
| OPEN | 63 | 13,214 | 22.2% |
| LABELLED | 169 | 37,248 | 62.7% |
| UNFORMALISED | 20 | 3,621 | 6.1% |

Within D1 alone, 4,676 bytes are CHECKED. D3 checks 449 bytes (the changelog dates, the effective date and 3.1's
coverage date) and D2 checks 202 bytes (footnote 1's instance of catastrophic risk). The plan expected under 10%.

The 51 CHECKED units are 5 premise units, the 12 routed units and the 34 commitments whose guards use no open
term. Among the commitments are publishing Risk Reports (K1), the LTBT's approval of the reviewers (K12), refusing a
reviewer with a financial interest (K13), a Board member among the recipients of a report on the RSO (K16) and
publishing an update with its Change Log (K17). Sharing an approved report with the Board and LTBT (K7) is OPEN,
because it is to be done "promptly" (OT12).

The 3.6.1 financial-interest paragraph has three source clauses. Only its 95-byte organization clause is CHECKED;
the 182-byte individual/review-chain financial-interest clause and 142-byte close-personal-relationship clause are
UNFORMALISED (SC) until their actors and reporting-chain scope are represented.

## What each byte that is not CHECKED waits for

From [gaps.json](../../docs/usecases/safetyfw/anthropic-rsp/gaps.json). A unit counts under every family it waits for;
"alone" counts the units with that one blocker, whose bytes move when that one feature lands.

| Family | Units | Bytes | Alone: units, bytes | What it is here |
|---|---|---|---|---|
| no claim to check | 130 | 31,104 | 130, 31,104 | layout, exposition, definitions, examples, the changelog's history (N2) |
| JT judgment terms | 50 | 11,372 | 33, 6,892 | the 28 open terms (whether a threshold is crossed, "highly capable", "significantly redacted", "promptly", ...) and 3.2's degree terms |
| AT attitudes | 43 | 6,510 | 43, 6,510 | beliefs, expectations, hopes, intents, the hedged "may" and "could", and the aims of RS12 |
| readings | 17 | 3,989 | 10, 2,106 | RS1 (ov: no rule), RS3o/RS3i/RS3c, RS4, RS6, RS7: readings that differ in which rules hold, and the row parts written in their own units |
| SC scope | 9 | 1,935 | 4, 693 | RS2 (a recommendation to the field, or the company too), RS5 (existential import), recommendations to others and the reviewer/reporting-chain prohibitions |
| ET time | 7 | 1,390 | 3, 489 | RS9 (every 3-6 months), RS11 (at deployment or no deadline), "promptly", "prior to or on its effective date", no stated trigger |
| DF defaults | 4 | 866 | 3, 405 | RS8 and RS13: a "should" or "usually" read as strict or default |
| external reference | 6 | 797 | 6, 797 | the Roadmap's page, RAND SL4, California SB 53, separate compliance documents, "see here" |
| WG weighing and causation | 2 | 551 | 2, 551 | "could result in", "could cause" |
| QT quantities | 2 | 105 | 0, 0 | "within a factor of 5" (T5), the 3-6 month cadence |
| AP act phrases | 0 | 0 | 0, 0 | none blocks a status; some acts are shorter than their sentence (PLAN 12, item 3) |

## Stage 0 (PLAN 9)

| Probe | Result |
|---|---|
| P1 an obligation with open terms in its guard (f14-full-review) | admitted; the rule is OPEN |
| P2 RS1 on its unit, `ve document check` | the set stays pending: premises UNKNOWN, one unresolved set |
| P3 D2 (`risk@0` with `alternatives@0`) | admitted with the T1 to T3 harms and footnote 1's instance, each catastrophic; three stated `might` cells, no `leads` cell. With T4's harm, which states no class, refused: `HarmUnclassified` |
| P4 D3 (`ve-units@1`) | the changelog dates increase (D1), v3.4 is effective before retrieval (D2), and the day counts of D3b, D4 and D5 hold, each with a certificate VE replays |
| P5 D1 over the text | 303 units; `bytes_by_status` totals 59,410 |
| P6 the routed units | 202 B to D2, 449 B to D3; the master map is total and contiguous |
| P7 identifier lint | 0 violations |
| P8 D1 with `judgments@0` | refused: `judgments@0 with soft-norms@0 needs its composed Lean route` (jt-2c is not merged) |
| M6 invention audit | 0 untraced rules or premises; every default rule is a default reading of a set and every permission the P reading of an RS6 set; no order or causal predicate |

## Remaining limits

The 15 faithful undecided rows in `results.json` name the missing AP, SC, ET, QT and WG representations. The
translation's conflicts remain candidates until the independent source check under R14. The answer counts remain
unvalidated until `uc-audit` has checked the source units and the item dependencies.

`results.json` also records three unscored section 9 comparisons. Removing N1 changes 42 answer cells, including
all 20 PROT cells; removing N2 changes G1 and N5; removing N3 changes K13. These variants rerun the VE routes with
each narrowing removed alone. W1 conflict-free rows now have replayed proof certificates, and a failed W1 or D3
proof stays undecided. M6 audits the rules and threshold facts built by the m2 and m4 mutants, rather than names
inferred from their presets.
