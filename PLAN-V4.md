# VE plan v4: frontier-scale tests close to the literature (supersedes PLAN-V3 priorities; PLAN-V3 pilots P1 done, P5 finishing)

Direction from the lead (2026-09-22): show whether VE helps FRONTIER models, using Opus 5.5 through the lead's Claude
subscription (`claude -p`, system prompt replaced, tools disabled, one fresh turn per call), close to published datasets
and protocols; own tasks allowed if paired with a published anchor. Evidence base: `~/code/manage-agents/reviews/
lit-frontier-benefit.md` (primary sources). Key facts: Kenton et al. 2024 ran consultancy vs debate on PrOntoQA with
judge logic errors the dominant failure (11/12 debate errors); no consultancy/debate study exists on first-order
deduction with frontier models; ProverQA-hard (6-9 steps, unary/binary, no arithmetic; fits VE) has no frontier numbers,
while unary-only FOL sets are saturated for Gemini 3.1 Pro (99%); FOLIO has 8.4% wrong labels; BABILong qa15 exists only at
0k (long versions must be generated); public sets are contaminated, so fresh generated instances are required.

## Phase 0: difficulty calibration (gate for everything else)

Generate fresh ProverQA-style items with ProverGen (its public generator) at depths 6, 9, 12, 15 with distractors, VE-
expressible only (checked by our E0 fit tool). Measure answer-alone accuracy of Opus 5.5, Sonnet 5 and Haiku 4.5 (40 items
per depth, subscription) and Gemini 3.1 Pro (API, as a second family). Pick the smallest depth where Opus answer-alone is
<= 80% and Haiku <= 65%. If Opus stays > 95% at depth 15, report that as a ceiling result and run Phase 1 with the weak
judge only. Cost: subscription quota plus about $5 of Vertex.

## Phase 1 (headline): consultancy vs debate vs VE-backed variants, Kenton protocol

Binary task as in Kenton (true answer vs a plausible wrong one), fresh items at the calibrated depth, plus the public
PrOntoQA subset as an ANCHOR to reproduce Kenton's consultancy/debate gap. Debaters/consultants: Opus 5.5 (assigned side,
dishonest half the time). Judges: Opus 5.5 (frontier) and Haiku 4.5 (weak). Arms at matched judge-input tokens:
(a) judge alone; (b) consultancy (prose); (c) debate (two prose debaters, 3 rounds); (d) VE-consultancy: the consultant
must also submit a VE claim graph; the trusted checker reports, through the system channel, whether the deduction is
certified and which leaves are NOT literally among the given facts (mechanical lookup); (e) VE-debate: both debaters submit
graphs; the checker reports on both. Primary: judge accuracy, (d) and (e) vs (b) and (c), per judge. Harm controls: honest
completion (true side approved) and a forged-checker arm on 10% of items (P1 lesson). Charge authoring tokens to VE arms.
Refuted if VE arms do not beat debate by a preregistered margin for the frontier judge, or honest completion drops.

## Phase 2: VE as the solver in the Logic-LM/LINC pipeline

Opus 5.5 CoT vs Opus formalises into VE + checker with a countermodel repair loop, vs published Logic-LM/LINC numbers, on
corrected FOLIO (VE-expressible subset) and the Phase-0 fresh items. Report accuracy, certified-answer rate and the
formalisation error rate (hand-audited sample). Not an oversight result; a verifiability result.

## Phase 3 (small): long context

Generate BABILong-style qa15 (deduction; qa16 excluded) at 32K/128K/512K with the BABILong code; Opus 5.5 reads the whole
haystack vs extract-to-VE + checker (extraction charged). 20 items per length. Quota-limited.

## Own-task extension (after Phase 1): policy/reachability audits (RBAC/IAM-style, closure@0), agent claims "no access";
same protocol as Phase 1, anchored by Phase 1's published-protocol results.

## Rules

Preregister each phase with external timestamp; P1 infrastructure (structured verdicts, ledgers, provenance, resumability);
no arm contains the answer; blinded leakage gate on fresh items; Opus judge never sees items it generated; Claude calls via
subscription with fixed prompt files and logged model id; Gemini via Vertex. Nothing about the English surface is claimed.
