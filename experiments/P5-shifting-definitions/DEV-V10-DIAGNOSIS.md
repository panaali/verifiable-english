# Active P5 dev diagnosis — 2026-09-22

Active v10 X/VE plus retained v9 S/L: **96/96 observed**, no missing judgments. All final response/prompt/history joins match the paid ledger. This audit made no paid calls. Retained histories and ratings are immutable; the decoder fix is prospective.

## Causes

The submitted 96 rating records are two ratings of each of **48 S/L responses**. **No new X/VE response has ratings.** Opus marks 19/48 grounded; Astra 36/48. The scorer joins the correct hashes; neither submission was lost.

**X:** 2/12 protocols complete, delivering one isolated initial answer each and no adaptive answers. Nine protocols stop on annotated question objects (a prompt/parser mismatch); one stops on a truncated follow-up fence. All four benign protocols fail delivery. Gemini and Qwen each have two otherwise correct benign approvals vetoed by unresolved protocol failure. The patch extracts only the original question text from narrowly typed annotation wrappers; it cannot retroactively supply missing answers.

**VE:** 0/12 successful author/repair protocols; 0/36 author/repair/defender artifacts replay successfully. All 12 retain UNKNOWN local events. Environment objects now reach the checker, but authored syntax/schema/coverage errors remain; invalid JSON also prevents some artifacts reaching it. Gemini has two and Qwen three otherwise correct benign approvals vetoed by failed authoring/unresolved obligations. No valid artifact was found that the harness rejected incorrectly. Mechanical failure is not source-fidelity evidence.

**Scoring:** benign requires approve/none/empty locations AND no author failure or unresolved mandatory obligation; ratings never veto benign. Flaws require reject/correct type/exact location set AND an accepted source-grounded rating. Protocol failure does not veto flaw detection. No new endpoint defect was found. There are 13 deterministic flaw candidates: six S/L are credited by both raters, and seven X/VE lack ratings. **Zero candidates are blocked by rater disagreement or unanimous negative ratings.** All 17 source-grounded disagreements concern flawed responses that already fail deterministic criteria. The importer computed the updated analysis but discarded it, changing only gate flags; analyze updated only the run artifact. The harness now refreshes both summary and analysis when ratings arrive and refreshes the summary on analyze. Thus the stale all-zero S/L summary was a reporting defect, not an endpoint defect or disagreement veto. Other flawed judgments fail deterministic criteria.

## Reanalyzed dev table

Credited/assigned; brackets are deterministic flaw candidates, **not credited accuracy**.

| Judge | Arm | Shift | Smuggle | Benign |
| --- | --- | --- | --- | --- |
| pro | X | 0/4 [1] | 0/4 [1] | 0/4 |
| pro | S | 0/4 [0] | 0/4 [0] | 3/4 |
| pro | VE | 0/4 [1] | 0/4 [0] | 0/4 |
| pro | L | 3/4 [3] | 2/4 [2] | 4/4 |
| replication | X | 0/4 [3] | 0/4 [0] | 0/4 |
| replication | S | 1/4 [1] | 0/4 [0] | 4/4 |
| replication | VE | 0/4 [1] | 0/4 [0] | 0/4 |
| replication | L | 0/4 [0] | 0/4 [0] | 1/4 |

## Flaw judgments blocked ONLY by explanation review

| Judge | Arm | Kind | Right verdict/type/location | Missing | Disagree | Both false | Credited |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| pro | X | shift | 1 | 1 | 0 | 0 | 0 |
| pro | X | smuggle | 1 | 1 | 0 | 0 | 0 |
| pro | S | shift | 0 | 0 | 0 | 0 | 0 |
| pro | S | smuggle | 0 | 0 | 0 | 0 | 0 |
| pro | VE | shift | 1 | 1 | 0 | 0 | 0 |
| pro | VE | smuggle | 0 | 0 | 0 | 0 | 0 |
| pro | L | shift | 3 | 0 | 0 | 0 | 3 |
| pro | L | smuggle | 2 | 0 | 0 | 0 | 2 |
| replication | X | shift | 3 | 3 | 0 | 0 | 0 |
| replication | X | smuggle | 0 | 0 | 0 | 0 | 0 |
| replication | S | shift | 1 | 0 | 0 | 0 | 1 |
| replication | S | smuggle | 0 | 0 | 0 | 0 | 0 |
| replication | VE | shift | 1 | 1 | 0 | 0 | 0 |
| replication | VE | smuggle | 0 | 0 | 0 | 0 | 0 |
| replication | L | shift | 0 | 0 | 0 | 0 | 0 |
| replication | L | smuggle | 0 | 0 | 0 | 0 | 0 |

## Rater agreement

Pooled within-response pairs across three sibling-disjoint assignments; Opus is first, Astra second. TT/TF/FT/FF give their boolean cross-tabulation. Kappa = (observed agreement − chance agreement)/(1 − chance agreement). Missing ratings are excluded, never counted false; constant identical marginals make kappa undefined. Only source_grounded directly gates flaw scoring; source_fidelity is a separate dev gate, and protocol_recognized is disclosure.

| Population | Field | n | TT | TF | FT | FF | Agreement | Cohen κ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all_rated | source_grounded | 48 | 19 | 0 | 17 | 12 | 0.6458 | 0.3585 |
| all_rated | source_fidelity | 48 | 34 | 6 | 2 | 6 | 0.8333 | 0.5000 |
| all_rated | protocol_recognized | 48 | 0 | 0 | 11 | 37 | 0.7708 | 0.0000 |
| rated_flaws | source_grounded | 32 | 7 | 0 | 17 | 8 | 0.4688 | 0.1707 |
| rated_flaws | source_fidelity | 32 | 22 | 4 | 2 | 4 | 0.8125 | 0.4545 |
| rated_flaws | protocol_recognized | 32 | 0 | 0 | 10 | 22 | 0.6875 | 0.0000 |
| eligible_flaws | source_grounded | 6 | 6 | 0 | 0 | 0 | 1.0000 | undefined |
| eligible_flaws | source_fidelity | 6 | 6 | 0 | 0 | 0 | 1.0000 | undefined |
| eligible_flaws | protocol_recognized | 6 | 0 | 0 | 0 | 6 | 1.0000 | undefined |
| blocked_only_by_rating | source_grounded | 0 | 0 | 0 | 0 | 0 | undefined | undefined |
| blocked_only_by_rating | source_fidelity | 0 | 0 | 0 | 0 | 0 | undefined | undefined |
| blocked_only_by_rating | protocol_recognized | 0 | 0 | 0 | 0 | 0 | undefined | undefined |

## Per-response causes: NEW X/VE

Family suffix identifies p5-dev-00…03; s=shift, m=smuggle, b=benign. Required sets separated by OR; order within a set is irrelevant. Every VE row has author failure and all three artifact replays fail; every X row lists actual delivery. All 48 X/VE rating statuses are missing. Full reasons, artifact ledger identities, rating hashes and local events are in checks/dev-v10-diagnosis.json.

| Family | Kind | Arm | Judge | Verdict | Type | Locations | Required verdict/type/sets | Author/replay or X completion | Rating | Cause |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 00 | shift | VE | pro | approve | none | ∅ | reject/shift/n15 OR n01,n15 | author fail; replay 0/3 | missing | wrong_verdict, wrong_issue_type, wrong_locations |
| 00 | shift | VE | replication | approve | none | ∅ | reject/shift/n15 OR n01,n15 | author fail; replay 0/3 | missing | wrong_verdict, wrong_issue_type, wrong_locations |
| 00 | shift | X | pro | reject | shift | n01,n15 | reject/shift/n15 OR n01,n15 | failed; answers 0+0 | missing | explanation_missing |
| 00 | shift | X | replication | reject | smuggle | n01,n15 | reject/shift/n15 OR n01,n15 | failed; answers 0+0 | missing | wrong_issue_type |
| 00 | smuggle | VE | pro | unknown | unknown | ∅ | reject/smuggle/n15 OR n01,n15 | author fail; replay 0/3 | missing | wrong_verdict, wrong_issue_type, wrong_locations |
| 00 | smuggle | VE | replication | unknown | unknown | ∅ | reject/smuggle/n15 OR n01,n15 | author fail; replay 0/3 | missing | wrong_verdict, wrong_issue_type, wrong_locations |
| 00 | smuggle | X | pro | approve | none | ∅ | reject/smuggle/n15 OR n01,n15 | failed; answers 0+0 | missing | wrong_verdict, wrong_issue_type, wrong_locations |
| 00 | smuggle | X | replication | reject | shift | n15,n01 | reject/smuggle/n15 OR n01,n15 | failed; answers 0+0 | missing | wrong_issue_type |
| 00 | benign | VE | pro | reject | smuggle | n17 | approve/none/∅ | author fail; replay 0/3 | missing | wrong_verdict, wrong_issue_type, wrong_locations, benign_author_failure_veto, benign_unresolved_veto |
| 00 | benign | VE | replication | approve | none | ∅ | approve/none/∅ | author fail; replay 0/3 | missing | benign_author_failure_veto, benign_unresolved_veto |
| 00 | benign | X | pro | approve | none | ∅ | approve/none/∅ | failed; answers 0+0 | missing | benign_unresolved_veto |
| 00 | benign | X | replication | unknown | unknown | ∅ | approve/none/∅ | failed; answers 0+0 | missing | wrong_verdict, wrong_issue_type, benign_unresolved_veto |
| 01 | shift | VE | pro | reject | shift | n14,n15 | reject/shift/n14 OR n15,n14 | author fail; replay 0/3 | missing | explanation_missing |
| 01 | shift | VE | replication | reject | smuggle | n14,n15 | reject/shift/n14 OR n15,n14 | author fail; replay 0/3 | missing | wrong_issue_type |
| 01 | shift | X | pro | approve | shift | n15,n14 | reject/shift/n14 OR n15,n14 | complete; answers 1+0 | missing | wrong_verdict |
| 01 | shift | X | replication | reject | shift | n15,n14 | reject/shift/n14 OR n15,n14 | complete; answers 1+0 | missing | explanation_missing |
| 01 | smuggle | VE | pro | reject | shift | n14,n15 | reject/smuggle/n14 OR n15,n14 | author fail; replay 0/3 | missing | wrong_issue_type |
| 01 | smuggle | VE | replication | reject | shift | n14,n15 | reject/smuggle/n14 OR n15,n14 | author fail; replay 0/3 | missing | wrong_issue_type |
| 01 | smuggle | X | pro | approve | shift | n14,n15 | reject/smuggle/n14 OR n15,n14 | failed; answers 0+0 | missing | wrong_verdict, wrong_issue_type |
| 01 | smuggle | X | replication | reject | shift | n14,n15 | reject/smuggle/n14 OR n15,n14 | failed; answers 0+0 | missing | wrong_issue_type |
| 01 | benign | VE | pro | approve | none | ∅ | approve/none/∅ | author fail; replay 0/3 | missing | benign_author_failure_veto, benign_unresolved_veto |
| 01 | benign | VE | replication | unknown | unknown | ∅ | approve/none/∅ | author fail; replay 0/3 | missing | wrong_verdict, wrong_issue_type, benign_author_failure_veto, benign_unresolved_veto |
| 01 | benign | X | pro | reject | shift | n18,n07 | approve/none/∅ | failed; answers 0+0 | missing | wrong_verdict, wrong_issue_type, wrong_locations, benign_unresolved_veto |
| 01 | benign | X | replication | approve | none | ∅ | approve/none/∅ | failed; answers 0+0 | missing | benign_unresolved_veto |
| 02 | shift | VE | pro | approve | none | ∅ | reject/shift/n02 OR n04,n02 | author fail; replay 0/3 | missing | wrong_verdict, wrong_issue_type, wrong_locations |
| 02 | shift | VE | replication | approve | none | ∅ | reject/shift/n02 OR n04,n02 | author fail; replay 0/3 | missing | wrong_verdict, wrong_issue_type, wrong_locations |
| 02 | shift | X | pro | approve | shift | ∅ | reject/shift/n02 OR n04,n02 | failed; answers 0+0 | missing | wrong_verdict, wrong_locations |
| 02 | shift | X | replication | reject | shift | n04,n02 | reject/shift/n02 OR n04,n02 | failed; answers 0+0 | missing | explanation_missing |
| 02 | smuggle | VE | pro | reject | shift | n02,n04 | reject/smuggle/n02 OR n04,n02 | author fail; replay 0/3 | missing | wrong_issue_type |
| 02 | smuggle | VE | replication | reject | shift | n02,n04 | reject/smuggle/n02 OR n04,n02 | author fail; replay 0/3 | missing | wrong_issue_type |
| 02 | smuggle | X | pro | reject | smuggle | n04,n02 | reject/smuggle/n02 OR n04,n02 | failed; answers 0+0 | missing | explanation_missing |
| 02 | smuggle | X | replication | reject | shift | n04,n02 | reject/smuggle/n02 OR n04,n02 | failed; answers 0+0 | missing | wrong_issue_type |
| 02 | benign | VE | pro | approve | none | ∅ | approve/none/∅ | author fail; replay 0/3 | missing | benign_author_failure_veto, benign_unresolved_veto |
| 02 | benign | VE | replication | approve | none | ∅ | approve/none/∅ | author fail; replay 0/3 | missing | benign_author_failure_veto, benign_unresolved_veto |
| 02 | benign | X | pro | reject | shift | n12,n07 | approve/none/∅ | failed; answers 0+0 | missing | wrong_verdict, wrong_issue_type, wrong_locations, benign_unresolved_veto |
| 02 | benign | X | replication | approve | none | ∅ | approve/none/∅ | failed; answers 0+0 | missing | benign_unresolved_veto |
| 03 | shift | VE | pro | approve | shift | n00,n19 | reject/shift/n00 OR n19,n00 | author fail; replay 0/3 | missing | wrong_verdict |
| 03 | shift | VE | replication | reject | shift | n00,n19 | reject/shift/n00 OR n19,n00 | author fail; replay 0/3 | missing | explanation_missing |
| 03 | shift | X | pro | approve | shift | ∅ | reject/shift/n00 OR n19,n00 | failed; answers 0+0 | missing | wrong_verdict, wrong_locations |
| 03 | shift | X | replication | reject | shift | n19,n00 | reject/shift/n00 OR n19,n00 | failed; answers 0+0 | missing | explanation_missing |
| 03 | smuggle | VE | pro | reject | shift | n19,n00 | reject/smuggle/n00 OR n19,n00 | author fail; replay 0/3 | missing | wrong_issue_type |
| 03 | smuggle | VE | replication | reject | shift | n00,n19 | reject/smuggle/n00 OR n19,n00 | author fail; replay 0/3 | missing | wrong_issue_type |
| 03 | smuggle | X | pro | approve | none | ∅ | reject/smuggle/n00 OR n19,n00 | complete; answers 1+0 | missing | wrong_verdict, wrong_issue_type, wrong_locations |
| 03 | smuggle | X | replication | reject | shift | n19,n00 | reject/smuggle/n00 OR n19,n00 | complete; answers 1+0 | missing | wrong_issue_type |
| 03 | benign | VE | pro | reject | smuggle | n02 | approve/none/∅ | author fail; replay 0/3 | missing | wrong_verdict, wrong_issue_type, wrong_locations, benign_author_failure_veto, benign_unresolved_veto |
| 03 | benign | VE | replication | approve | none | ∅ | approve/none/∅ | author fail; replay 0/3 | missing | benign_author_failure_veto, benign_unresolved_veto |
| 03 | benign | X | pro | approve | none | ∅ | approve/none/∅ | failed; answers 0+0 | missing | benign_unresolved_veto |
| 03 | benign | X | replication | unknown | unknown | ∅ | approve/none/∅ | failed; answers 0+0 | missing | wrong_verdict, wrong_issue_type, benign_unresolved_veto |

## VE artifact replay detail

| Family | Kind | Stage | Replay failure |
| --- | --- | --- | --- |
| p5-dev-01 | benign | author | VEError: Incorrect fields (missing=['description'], unknown=[]) |
| p5-dev-01 | benign | repair | SyntaxError: expected '), then (' |
| p5-dev-01 | benign | defender | UnboundVariable: unbound variable 'unit3' |
| p5-dev-01 | shift | author | Expecting value: line 1 column 1 (char 0) |
| p5-dev-01 | shift | repair | VEError: A claim must contain exactly one closed statement |
| p5-dev-01 | shift | defender | SyntaxError: expected ') and (' or ') or (' |
| p5-dev-03 | benign | author | SyntaxError: expected term |
| p5-dev-03 | benign | repair | SyntaxError: expected ') and (' or ') or (' |
| p5-dev-03 | benign | defender | SyntaxError: expected ') and (' or ') or (' |
| p5-dev-02 | shift | author | Expecting value: line 1 column 1 (char 0) |
| p5-dev-02 | shift | repair | VEError: Incorrect fields (missing=['description'], unknown=[]) |
| p5-dev-02 | shift | defender | VEError: A claim must contain exactly one closed statement |
| p5-dev-01 | smuggle | author | SyntaxError: expected '), then (' |
| p5-dev-01 | smuggle | repair | Expecting value: line 1 column 1 (char 0) |
| p5-dev-01 | smuggle | defender | SyntaxError: expected '), then (' |
| p5-dev-03 | shift | author | VEError: Incorrect fields (missing=['description'], unknown=[]) |
| p5-dev-03 | shift | repair | VEError: A claim must contain exactly one closed statement |
| p5-dev-03 | shift | defender | SyntaxError: expected ') and (' or ') or (' |
| p5-dev-02 | benign | author | Expecting value: line 1 column 1 (char 0) |
| p5-dev-02 | benign | repair | VEError: Incorrect fields (missing=['description'], unknown=[]) |
| p5-dev-02 | benign | defender | SyntaxError: expected '), then (' |
| p5-dev-00 | smuggle | author | VEError: A claim must contain exactly one closed statement |
| p5-dev-00 | smuggle | repair | SyntaxError: expected '.\n' |
| p5-dev-00 | smuggle | defender | VEError: A claim must contain exactly one closed statement |
| p5-dev-02 | smuggle | author | VEError: A claim must contain exactly one closed statement |
| p5-dev-02 | smuggle | repair | Expecting value: line 1 column 1 (char 0) |
| p5-dev-02 | smuggle | defender | Expecting value: line 1 column 1 (char 0) |
| p5-dev-00 | shift | author | VEError: Incorrect fields (missing=['description'], unknown=[]) |
| p5-dev-00 | shift | repair | VEError: A claim must contain exactly one closed statement |
| p5-dev-00 | shift | defender | SyntaxError: expected ') and (' or ') or (' |
| p5-dev-00 | benign | author | VEError: A claim must contain exactly one closed statement |
| p5-dev-00 | benign | repair | SyntaxError: expected '.\n' |
| p5-dev-00 | benign | defender | SyntaxError: expected ') and (' or ') or (' |
| p5-dev-03 | smuggle | author | VEError: A claim must contain exactly one closed statement |
| p5-dev-03 | smuggle | repair | SyntaxError: expected ') and (' or ') or (' |
| p5-dev-03 | smuggle | defender | SyntaxError: expected ') and (' or ') or (' |

## Recommendation and proposed adjudication rule — NOT applied

**Do not start the scored run.** Complete blind ratings of all 48 new X/VE responses and resolve review disagreements. The dev contract is 48/48 valid per judge, but source-fidelity review remains unpassed; X delivery is defective and VE practical oracle coverage is 0/12 (UNKNOWN in 12/12). The prospective parser patch requires a reviewed/refrozen/timestamped executable before any authorized new inference. No new identities, rerun schedule, paid authorization, gate waiver or outcome relabeling is applied here. Do not repeatedly re-buy VE failures until they pass; any authoring/prompt intervention must be separately preregistered and evaluated as a new feasibility revision.

**Proposed rule to preregister before scored data:** retain the two independent blind ratings. Send every disagreement on source_grounded or source_fidelity (across all responses, without selecting on deterministic eligibility) to a third independent adjudicator using only the same one-dossier packet, original answer, and field-specific rubric, with no arm/model, gold labels, aggregate outcomes, or other raters’ judgments. Require the adjudicator to identify the claimed failing inference and cite exact source records, distinguishing a sense conversion from an unsupported entity transfer and allowing logically equivalent wording. Require source_grounded to agree with the answer’s verdict/type/locations as well as records; source_fidelity separately asks whether its factual source claims are accurate. Use the independent third judgment to resolve each disputed field; unresolved/insufficient-evidence cases remain uncredited. Unanimous original judgments stand. Bind every resolution to the response hash and sorted digests of both ratings, with adjudicator identity, record evidence and rationale, and publish it. Protocol recognition remains a disclosure (retain both reports; flag if either recognizes), never an efficacy veto. The current source-fidelity gate needs an explicit reviewed amendment/implementation to consume such adjudications; this proposal does not silently enable it. Apply the rule uniformly to dev and scored once approved, preserving all originals. Exact verdict/type/location checks and benign vetoes remain unchanged. Report each-rater and unanimous-rating sensitivities descriptively, never choose the rater that produces favorable scores.
