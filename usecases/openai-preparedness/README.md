# OpenAI's Preparedness Framework, to be translated into VE

This case will translate OpenAI's *Preparedness Framework*, version 2 (last updated 15 April 2025), into VE, by the
method of [safety-framework](../safety-framework/README.md) and [anthropic-rsp](../anthropic-rsp/README.md). VE will
answer four questions about it:

- What does each level require, per activity?
- Do any two commitments conflict?
- Which levels or situations does no rule cover?
- Which commitments can never apply?

The plan, with the answer key written and frozen before any VE run, is [PLAN.md](PLAN.md); the freeze is
[KEY-FREEZE.md](KEY-FREEZE.md). **Status (2026-10-28):** the plan, the frozen key and its transcription only. The
baseline (vocabulary, rules, span accounting, stage 0 and gaps, PLAN sections 7 to 10) is the follow-up
`usecase-safetyfw-b`. The harness that answers the 239 key items is `usecase-pf-run`. No byte of the text is
measured yet.

## The source

| Field | Value |
|---|---|
| Document | OpenAI, *Preparedness Framework*, version 2, "Last updated: 15th April, 2025", 22 pages |
| URL | `https://cdn.openai.com/pdf/18a02b5d-6b67-4cec-ab64-68cdfbddebcd/preparedness-framework-v2.pdf` |
| Retrieved | 2026-10-28 |
| PDF SHA-256 | `fae6e4cc6f7212a010bb9348fc0cde1fe711b9cad426c6a99db97740ee52729b` |
| Text SHA-256 | `d2e3dd5b80e5bb86079911230358e0c2bb78f12435757959e14dae50e4d48d0f` (67,418 bytes, from [source/extract_text.py](source/extract_text.py)) |

The PDF states no licence, so neither it nor its text is committed. The stored copy is in
`~/code/manage-agents/pilots/openai-preparedness/source/`.

## Files

| File | Contents |
|---|---|
| [PLAN.md](PLAN.md), [KEY-FREEZE.md](KEY-FREEZE.md) | the plan and the freeze of its section 6 (SHA-256 recorded) |
| [cases.json](cases.json), [answer-key.json](answer-key.json) | the 67 cases and the 239 answers of PLAN sections 5 and 6, transcribed after the freeze |
| [source/extract_text.py](source/extract_text.py) | the pinned extractor (`pypdf==6.19.0`) |
| [../../tests/test_safetyfw_usecases.py](../../tests/test_safetyfw_usecases.py) | the test: the section-6 hash, the item total, each family's count and the stated verdict totals |
