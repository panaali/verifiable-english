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

## REVISION after review (2026-09-22): both reviewers "proceed with changes, large". Adopted; this section overrides the above.

Reviews: `~/code/manage-agents/reviews/plan4-review-astra.md`, `plan4-review-opus.md`. Common ground: as written, the VE
arms win by construction (closed-world items with given premises: "certified + every leaf among the facts" IS the
label); Opus judging Opus has no capability gap; depth mostly adds tedium; the subscription CLI needs strict controls.

Revised order:
- **A. Endpoint audit (no science).** Claude CLI from an empty dir, clean CLAUDE_CONFIG_DIR, --strict-mcp-config empty,
  no hooks/settings/memory, pinned CLI version, fixed MAX_THINKING_TOKENS; log stream-json init (model, tools) and input
  tokens per call; assert constant overhead; canary probe for injected context; reject any call not served by the Opus 5.5
  model id (silent fallback). ~10% replicated via API later. k>=3 samples per item (no temperature control).
- **B. Formalisation-fidelity audit (was Phase 2, shrunk, moved first).** Items given in free English; Opus writes the
  English->VE translation table + graph; measure faithful-translation rate (hand + independent-model audit, checked
  against the generator's gold logic) and certified-answer rate. VE's Phase-C value depends on this rate.
- **C. Calibration.** Fresh ProverGen items, VE-expressible, with difficulty levers crossed at roughly constant length:
  Uncertain (non-entailed) items, proof by cases, xor, modus-tollens chains, near-miss distractors, nested quantifiers
  over binary predicates, belief-inconsistent vocabulary. Calibrate each judge separately; count only errors that recur
  across k=3 samples; select item TYPES on a Sonnet dev split, test on a held-out split (never select Opus failures).
  A declared thinking-token cap on the judge is allowed as an explicit oversight gap and reported as such.
- **D. Headline, Kenton-style binary, powered.** Premises shown in free English to everyone. Arms at matched TOTAL
  reasoning/authoring budget: judge alone (majority-of-k); consultancy; debate; judge-formalises-and-checks (Logic-LM
  style); VE-consultancy and VE-debate where the arguer supplies the English->VE translation table + graph, the checker
  certifies deduction through the trusted channel, and THE JUDGE MUST DECIDE WHETHER THE TRANSLATION IS FAITHFUL (the
  non-trivial residual). **Adaptive mistranslation attack:** the dishonest side gets the checker as a tool (best-of-n) so
  it can only win via a certified graph built on a mistranslated premise; measure judge catch rate vs catching the flaw in
  matched prose debate. **Factorial:** premise lookup on/off x proof checking on/off with graphs and presentation fixed.
  Judges Opus 5.5 and Haiku 4.5; Gemini 3.1 Pro replication judge. Sample size from a power calculation; paired,
  template-clustered intervals; multiplicity control; honest-completion noninferiority. PrOntoQA anchor for Haiku only.
  Success requires beating BOTH debate and the strong direct baseline; an underpowered null is inconclusive.
- **Cut:** long-context qa15 (strawman; 1-2 hops); FOLIO as a headline. Own-task RBAC extension after D.
- Confirm bulk automated use of the subscription fits its terms before large runs; otherwise run D via API.
