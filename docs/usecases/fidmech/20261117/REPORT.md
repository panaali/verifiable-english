# fid-mech report (counts only)

Headline: **Units passing the stated checks (L1, L2, L3, D, K-structural)**. Never "faithful". blind spot: K cannot see act or legend wording (opaque atoms); L1-L3 and D see the text, not the rule's meaning; see the escapes of plan 11.

Inputs read by sha256: adjudications.json a4e1c3feb6699dea..., defects.json 9ba691dd7b789ee7..., fp1.json 2a0a6dcb9e1f94ec..., plants.json 5173f2b5f2154007...

## anthropic-rsp (in-sample)

batch status ok; 467 mutants, 457 run, 0 with an INVALID K (no good sentinel confirmed the run: left out of every K denominator), 0 not run; stillborn 10 (listed, never scored) {'qualifier': 1, 'actor': 9}; equivalent {}; inputs_sha256 39537b30c4c11e02dcad8bed896323d4915225c0afff357c2a56a0736f0264ed

- Units passing the stated checks (L1, L2, L3, D, K-structural), all ops: 0 of 85 (failing 76, incomplete 0, untested 9; units with at least one K survivor 75); failing units by cause (a unit can have several) {'K survivor': 74, 'K survivor, no text hit': 1, 'text hit D': 58, 'text hit L1': 31, 'text hit L2': 47, 'text hit L3': 12}
- Units passing the stated checks (L1, L2, L3, D, K-structural), without flip-force: 0 of 85 (failing 76, incomplete 0, untested 9; units with at least one K survivor 71); failing units by cause (a unit can have several) {'K survivor': 70, 'K survivor, no text hit': 1, 'text hit D': 58, 'text hit L1': 31, 'text hit L2': 47, 'text hit L3': 12}
- Units passing the stated checks (L1, L2, L3, D, K-structural), declared equivalents counted as survivors: 0 of 85 (failing 76, incomplete 0, untested 9; units with at least one K survivor 75); failing units by cause (a unit can have several) {'K survivor': 74, 'K survivor, no text hit': 1, 'text hit D': 58, 'text hit L1': 31, 'text hit L2': 47, 'text hit L3': 12}
- Units whose structural mutants K killed, K-structural alone (decomposition, not the headline): 1 of 85 (failing 75, incomplete 0, untested 9; units with at least one K survivor 75); failing units by cause (a unit can have several) {'K survivor': 75}

| op | scored | K | L1 | L2 | L3 | L4 | D | CR | any | none | K left out |
|---|---|---|---|---|---|---|---|---|---|---|---|
| drop-conjunct | 62 | 9/62 | 0/62 | 0/62 | 0/62 | 0/62 | 50/62 | 0/0 | 50/62 | {'CR not read': 12} | {} |
| drop-unless | 3 | 1/3 | 0/3 | 0/3 | 0/3 | 0/3 | 2/3 | 0/0 | 3/3 | {} | {} |
| drop-disjunct | 2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 2/2 | 0/0 | 2/2 | {} | {} |
| drop-exception | 3 | 3/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 | 0/0 | 3/3 | {} | {} |
| flip-force | 73 | 0/70 | 0/73 | 0/73 | 0/73 | 0/73 | 0/73 | 0/0 | 0/73 | {'CR not read': 70, 'some instrument did not run': 3} | {'error': 3} |
| add-guard-true | 10 | 5/10 | 0/10 | 0/10 | 1/10 | 0/10 | 0/10 | 0/0 | 6/10 | {'CR not read': 4} | {} |
| rule-drop | 76 | 29/76 | 0/76 | 0/76 | 0/76 | 0/76 | 40/76 | 0/0 | 45/76 | {'CR not read': 31} | {} |
| widen-quantifier | 5 | 3/5 | 0/5 | 0/5 | 0/5 | 0/5 | 2/5 | 0/0 | 5/5 | {} | {} |
| quantity | 45 | 0/40 | 0/45 | 5/45 | 2/45 | 0/45 | 1/45 | 0/0 | 8/45 | {'CR not read': 36, 'some instrument did not run': 1} | {'error': 5} |
| actor | 49 | 0/44 | 0/49 | 13/49 | 0/49 | 0/49 | 17/49 | 0/0 | 30/49 | {'CR not read': 18, 'some instrument did not run': 1} | {'error': 5} |
| attachment | 5 | 0/5 | 0/5 | 4/5 | 0/5 | 0/5 | 0/5 | 0/0 | 4/5 | {'CR not read': 1} | {} |
| qualifier | 103 | 0/88 | 0/103 | 26/103 | 0/103 | 0/103 | 34/103 | 0/0 | 60/103 | {'CR not read': 43} | {'error': 15} |
| all | 436 | 50/408 | 0/436 | 48/436 | 3/436 | 0/436 | 148/436 | 0/0 | 216/436 | {'CR not read': 215, 'some instrument did not run': 5} | {'error': 28} |

- mutation score (K) 50/408, any-instrument score 216/436; with declared equivalents counted as survivors: K 50/408, any 216/436. No Wilson interval: mutants of one unit are correlated and generated, not sampled.
- unprobed rules: 39 of 76 rule blocks are selected by no item (the adapter's rule ids); every K mutant of such a rule is expected to survive K (Opus round 2 point 9), unless an item that reads the whole document (FSF C-doc) moves; measured K verdicts of their scored mutants: {'survived': 160, 'error': 7}.
- K errors (VE refused the mutated document when it ran, or the run failed), by last line: {'ve.errors.SyntaxError: Norm consequence has no single declared reading; use a declared act phrase': 22, 've.errors.VEError: SoftOverHard': 3, 've.errors.VEError: InvalidInput': 2, 've.errors.VEError: Invalid ASCII identifier': 1}
- control false alarms (new hits on syntactic equivalents): 0
- blind spot (no kill among the instruments run), by op: {'drop-conjunct': 12, 'flip-force': 73, 'add-guard-true': 4, 'rule-drop': 31, 'quantity': 37, 'qualifier': 43, 'attachment': 1, 'actor': 19}
- baseline hits by class: {'L1m': 2, 'L1n': 0, 'L1u': 4, 'L1c': 39, 'L1e': 1, 'L1a': 9, 'L2b': 25, 'L2q': 19, 'L2a': 2, 'L3w': 12, 'L4u': 20, 'L4l': 72, 'D': 1232, 'L4g': 0}; also gated: {}
- hits each lever clears / adds when off: {'extra': {'cleared': 65, 'added': 6}, 'suppress': {'cleared': 0, 'added': 0}, 'abbrev': {'cleared': 0, 'added': 0}, 'furniture': {'cleared': 87, 'added': 87}, 'footnotes': {'cleared': 164, 'added': 85}, 'hand-footnotes': {'cleared': 16, 'added': 1}, 'ruled_out': {'cleared': 0, 'added': 0}, 'unformalised': {'cleared': 15, 'added': 0}, 'sidecar': {'cleared': 173, 'added': 3}}
- adjudication of the baseline hits: 0 confirmed, 0 contradicted, 1437 unadjudicated; the document's findings: {'findings': 33, 'REAL-by-both': 23, 'NOT-by-both': 3, 'split': 7, 'unit_fp1_unchanged': 0} (a hit matches only a finding whose unit's fp-1 is unchanged since the adjudication)
- false-discovery proportion among hits not measured: 0 confirmed, 0 contradicted, 1437 unadjudicated. Item 32's false-alarm figure needs a seeded adjudication sample (two blind adjudicators, about 20 hits per document), offered to the DRI and not run here.
- plants: {"entries": 24, "excluded": 12, "applied": 11, "not applicable": 1, "K_killed": 5, "K_decided": 11, "K_invalid": 0, "any_killed": 7, "text_killed": 6, "not_applicable_by": {"the unit text is gone at the tree under test": 1}}
- defects: {"entries": 14, "applied": 10, "not applicable": 4, "K_killed": 1, "K_decided": 10, "K_invalid": 0, "any_killed": 10, "text_killed": 10, "not_applicable_by": {"the repair deleted text the defect needs": 4}}
- old joint-run figures (item 49, the joint K + CR run before this harness, not isolated): 6/12 plants, 0/14 real RSP defects
- run cost (measured): {"wall_s": 2754.0, "schedule_wall_s": 2610.7, "child_cpu_s": 35591.9, "run_cpu_s": 35590.8, "peak_concurrency": 16, "mean_concurrency": 15.72, "admission_wait_s": 0.0, "per_mutant_s": {"mean": 78.3, "median": 82.3, "max": 101.6}, "baseline_s": 59.123, "worker_peak_rss_bytes": 297955328, "max_peak_rss_bytes": 530628608, "lean_service_start": {"first_s": 0.3943415629910305, "second_s": 0.11779605702031404, "start_s": 0.277}, "cpu_h_per_100": 2.16, "wall_min_per_100": 10.0}; tokens 0. the challenger's 2.8 CPU-h per 100 mutants is an estimate for a 280-question set; RSP has 126 questions, so the figures are not like for like.

## safety-framework (out-of-sample under the freeze rule)

batch status ok; 256 mutants, 64 run, 0 with an INVALID K (no good sentinel confirmed the run: left out of every K denominator), 192 not run; stillborn 0 (listed, never scored) {}; equivalent {}; inputs_sha256 34ec93f778fab87851470d1e6701342afa6499140adfa08444ae3ed85c60b04d

- Units passing the stated checks (L1, L2, L3, D, K-structural), all ops: 0 of 61 (failing 45, incomplete 0, untested 16; units with at least one K survivor 23); failing units by cause (a unit can have several) {'K survivor': 23, 'text hit D': 33, 'text hit L1': 37, 'text hit L2': 45, 'text hit L3': 22}
- Units passing the stated checks (L1, L2, L3, D, K-structural), without flip-force: 0 of 61 (failing 45, incomplete 0, untested 16; units with at least one K survivor 23); failing units by cause (a unit can have several) {'K survivor': 23, 'text hit D': 33, 'text hit L1': 37, 'text hit L2': 45, 'text hit L3': 22}
- Units passing the stated checks (L1, L2, L3, D, K-structural), declared equivalents counted as survivors: 0 of 61 (failing 45, incomplete 0, untested 16; units with at least one K survivor 23); failing units by cause (a unit can have several) {'K survivor': 23, 'text hit D': 33, 'text hit L1': 37, 'text hit L2': 45, 'text hit L3': 22}
- Units passing the stated checks (L1, L2, L3, D, K-structural), without D (no sidecar): 0 of 61 (failing 45, incomplete 0, untested 16; units with at least one K survivor 23); failing units by cause (a unit can have several) {'K survivor': 23, 'text hit L1': 37, 'text hit L2': 45, 'text hit L3': 22}
- Units whose structural mutants K killed, K-structural alone (decomposition, not the headline): 0 of 61 (failing 23, incomplete 22, untested 16; units with at least one K survivor 23); failing units by cause (a unit can have several) {'K survivor': 23}

| op | scored | K | L1 | L2 | L3 | L4 | D | CR | any | none | K left out |
|---|---|---|---|---|---|---|---|---|---|---|---|
| drop-conjunct | 60 | 30/60 | 0/60 | 0/60 | 0/60 | 0/60 | 40/60 | 0/0 | 50/60 | {'CR not read': 10} | {} |
| drop-unless | 8 | 0/4 | 0/8 | 0/8 | 0/8 | 0/8 | 4/8 | 0/0 | 4/8 | {'CR not read': 4} | {'not-run': 4} |
| drop-disjunct | 18 | 0/0 | 0/18 | 0/18 | 0/18 | 0/18 | 10/18 | 0/0 | 10/18 | {'some instrument did not run': 8} | {'not-run': 18} |
| drop-exception | 2 | 0/0 | 0/2 | 0/2 | 0/2 | 0/2 | 1/2 | 0/0 | 1/2 | {'some instrument did not run': 1} | {'not-run': 2} |
| flip-force | 41 | 0/0 | 0/41 | 0/41 | 0/41 | 0/41 | 0/41 | 0/0 | 0/41 | {'some instrument did not run': 41} | {'not-run': 41} |
| add-guard-true | 16 | 0/0 | 0/16 | 0/16 | 0/16 | 0/16 | 0/16 | 0/0 | 0/16 | {'some instrument did not run': 16} | {'not-run': 16} |
| rule-drop | 44 | 0/0 | 0/44 | 0/44 | 0/44 | 0/44 | 28/44 | 0/0 | 28/44 | {'some instrument did not run': 16} | {'not-run': 44} |
| widen-quantifier | 2 | 0/0 | 0/2 | 0/2 | 0/2 | 0/2 | 2/2 | 0/0 | 2/2 | {} | {'not-run': 2} |
| qualifier | 23 | 0/0 | 0/23 | 0/23 | 0/23 | 0/23 | 6/23 | 0/0 | 6/23 | {'some instrument did not run': 17} | {'not-run': 23} |
| quantity | 27 | 0/0 | 0/27 | 0/27 | 5/27 | 0/27 | 0/27 | 0/0 | 5/27 | {'some instrument did not run': 22} | {'not-run': 27} |
| actor | 14 | 0/0 | 0/14 | 0/14 | 0/14 | 0/14 | 2/14 | 0/0 | 2/14 | {'some instrument did not run': 12} | {'not-run': 14} |
| attachment | 1 | 0/0 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/0 | 0/1 | {'some instrument did not run': 1} | {'not-run': 1} |
| all | 256 | 30/64 | 0/256 | 0/256 | 5/256 | 0/256 | 93/256 | 0/0 | 108/256 | {'CR not read': 14, 'some instrument did not run': 134} | {'not-run': 192} |

- mutation score (K) 30/64, any-instrument score 108/256; with declared equivalents counted as survivors: K 30/64, any 108/256. No Wilson interval: mutants of one unit are correlated and generated, not sampled.
- unprobed rules: 11 of 45 rule blocks are selected by no item (the adapter's rule ids); every K mutant of such a rule is expected to survive K (Opus round 2 point 9), unless an item that reads the whole document (FSF C-doc) moves; measured K verdicts of their scored mutants: {'survived': 9, 'killed': 1, 'not-run': 40}.
- K errors (VE refused the mutated document when it ran, or the run failed), by last line: {}
- control false alarms (new hits on syntactic equivalents): 0
- blind spot (no kill among the instruments run), by op: {'drop-conjunct': 10, 'drop-unless': 4, 'drop-disjunct': 8, 'drop-exception': 1, 'flip-force': 41, 'add-guard-true': 16, 'rule-drop': 16, 'quantity': 22, 'qualifier': 17, 'actor': 12, 'attachment': 1}
- baseline hits by class: {'L1m': 17, 'L1n': 0, 'L1u': 0, 'L1c': 38, 'L1e': 1, 'L1a': 4, 'L2b': 26, 'L2q': 1, 'L2a': 0, 'L3w': 24, 'L4u': 18, 'L4l': 50, 'D': 386, 'L4g': 0}; also gated: {}
- hits each lever clears / adds when off: {'extra': {'cleared': 0, 'added': 0}, 'suppress': {'cleared': 0, 'added': 0}, 'abbrev': {'cleared': 0, 'added': 0}, 'furniture': {'cleared': 5, 'added': 27}, 'footnotes': {'cleared': 48, 'added': 10}, 'hand-footnotes': {'cleared': 0, 'added': 0}, 'ruled_out': {'cleared': 0, 'added': 0}, 'unformalised': {'cleared': 33, 'added': 0}, 'sidecar': {'cleared': 0, 'added': 0}}
- adjudication of the baseline hits: 0 confirmed, 0 contradicted, 565 unadjudicated; the document's findings: {'findings': 8, 'split': 6, 'REAL-by-both': 2, 'unit_fp1_unchanged': 0} (a hit matches only a finding whose unit's fp-1 is unchanged since the adjudication)
- false-discovery proportion among hits not measured: 0 confirmed, 0 contradicted, 565 unadjudicated. Item 32's false-alarm figure needs a seeded adjudication sample (two blind adjudicators, about 20 hits per document), offered to the DRI and not run here.
- run cost (measured): {"wall_s": 11605.3, "schedule_wall_s": 11500.9, "child_cpu_s": 16439.0, "run_cpu_s": 16437.8, "peak_concurrency": 16, "mean_concurrency": 2.91, "admission_wait_s": 9368.5, "per_mutant_s": {"mean": 416.7, "median": 337.6, "max": 750.7}, "baseline_s": 170.397, "worker_peak_rss_bytes": 147525632, "max_peak_rss_bytes": 265408512, "lean_service_start": {"first_s": 0.40130474301986396, "second_s": 0.08203832898288965, "start_s": 0.319}, "cpu_h_per_100": 7.13, "wall_min_per_100": 302.2}; tokens 0. the challenger's 2.8 CPU-h per 100 mutants is an estimate for a 280-question set; RSP has 126 questions, so the figures are not like for like.

## openai-preparedness (out-of-sample under the freeze rule)

batch status ok; 518 mutants, 96 run, 0 with an INVALID K (no good sentinel confirmed the run: left out of every K denominator), 415 not run; stillborn 7 (listed, never scored) {'actor': 7}; equivalent {}; inputs_sha256 50ac2c228942aa3dc55ecde6ef24436bd0471dc9d41e1f5b0eed6e516149f4b7

- Units passing the stated checks (L1, L2, L3, D, K-structural), all ops: 0 of 101 (failing 88, incomplete 3, untested 10; units with at least one K survivor 36); failing units by cause (a unit can have several) {'K survivor': 36, 'text hit D': 62, 'text hit L1': 66, 'text hit L2': 81, 'text hit L3': 12}
- Units passing the stated checks (L1, L2, L3, D, K-structural), without flip-force: 0 of 101 (failing 88, incomplete 3, untested 10; units with at least one K survivor 36); failing units by cause (a unit can have several) {'K survivor': 36, 'text hit D': 62, 'text hit L1': 66, 'text hit L2': 81, 'text hit L3': 12}
- Units passing the stated checks (L1, L2, L3, D, K-structural), declared equivalents counted as survivors: 0 of 101 (failing 88, incomplete 3, untested 10; units with at least one K survivor 36); failing units by cause (a unit can have several) {'K survivor': 36, 'text hit D': 62, 'text hit L1': 66, 'text hit L2': 81, 'text hit L3': 12}
- Units whose structural mutants K killed, K-structural alone (decomposition, not the headline): 0 of 101 (failing 36, incomplete 55, untested 10; units with at least one K survivor 36); failing units by cause (a unit can have several) {'K survivor': 36}

| op | scored | K | L1 | L2 | L3 | L4 | D | CR | any | none | K left out |
|---|---|---|---|---|---|---|---|---|---|---|---|
| drop-conjunct | 139 | 50/96 | 0/139 | 0/139 | 0/139 | 0/139 | 38/139 | 0/0 | 77/139 | {'CR not read': 37, 'some instrument did not run': 25} | {'not-run': 43} |
| drop-unless | 5 | 0/0 | 0/5 | 0/5 | 0/5 | 0/5 | 2/5 | 0/0 | 2/5 | {'some instrument did not run': 3} | {'not-run': 5} |
| drop-disjunct | 8 | 0/0 | 0/8 | 0/8 | 0/8 | 0/8 | 0/8 | 0/0 | 0/8 | {'some instrument did not run': 8} | {'not-run': 8} |
| drop-exception | 8 | 0/0 | 0/8 | 0/8 | 0/8 | 0/8 | 1/8 | 0/0 | 1/8 | {'some instrument did not run': 7} | {'not-run': 8} |
| flip-force | 91 | 0/0 | 0/91 | 0/91 | 0/91 | 0/91 | 1/91 | 0/0 | 1/91 | {'some instrument did not run': 90} | {'not-run': 91} |
| add-guard-true | 63 | 0/0 | 0/63 | 0/63 | 11/63 | 0/63 | 0/63 | 0/0 | 11/63 | {'some instrument did not run': 52} | {'not-run': 63} |
| rule-drop | 90 | 0/0 | 0/90 | 0/90 | 0/90 | 0/90 | 32/90 | 0/0 | 32/90 | {'some instrument did not run': 58} | {'not-run': 90} |
| qualifier | 24 | 0/0 | 0/24 | 2/24 | 0/24 | 0/24 | 3/24 | 0/0 | 5/24 | {'some instrument did not run': 19} | {'not-run': 24} |
| actor | 51 | 0/0 | 0/51 | 6/51 | 0/51 | 0/51 | 3/51 | 0/0 | 9/51 | {'some instrument did not run': 42} | {'not-run': 51} |
| quantity | 31 | 0/0 | 0/31 | 1/31 | 8/31 | 0/31 | 3/31 | 0/0 | 10/31 | {'some instrument did not run': 21} | {'not-run': 31} |
| attachment | 1 | 0/0 | 0/1 | 0/1 | 0/1 | 0/1 | 0/1 | 0/0 | 0/1 | {'some instrument did not run': 1} | {'not-run': 1} |
| all | 511 | 50/96 | 0/511 | 9/511 | 19/511 | 0/511 | 83/511 | 0/0 | 148/511 | {'CR not read': 37, 'some instrument did not run': 326} | {'not-run': 415} |

- mutation score (K) 50/96, any-instrument score 148/511; with declared equivalents counted as survivors: K 50/96, any 148/511. No Wilson interval: mutants of one unit are correlated and generated, not sampled.
- unprobed rules: 0 of 91 rule blocks are selected by no item (the adapter's rule ids); every K mutant of such a rule is expected to survive K (Opus round 2 point 9), unless an item that reads the whole document (FSF C-doc) moves; measured K verdicts of their scored mutants: {}.
- K errors (VE refused the mutated document when it ran, or the run failed), by last line: {}
- control false alarms (new hits on syntactic equivalents): 0
- blind spot (no kill among the instruments run), by op: {'drop-conjunct': 62, 'drop-unless': 3, 'drop-disjunct': 8, 'drop-exception': 7, 'flip-force': 90, 'add-guard-true': 52, 'rule-drop': 58, 'qualifier': 19, 'quantity': 21, 'actor': 42, 'attachment': 1}
- baseline hits by class: {'L1m': 0, 'L1n': 0, 'L1u': 14, 'L1c': 64, 'L1e': 0, 'L1a': 1, 'L2b': 44, 'L2q': 9, 'L2a': 2, 'L3w': 16, 'L4u': 12, 'L4l': 0, 'D': 665, 'L4g': 0}; also gated: {'L1m': {'by': 'quote_evidence.py:39 (a block with no quotation)', 'hits': 0}, 'L1u': {'by': 'quote_evidence.py:40 via test_pf_fidelity_fix.py:179 (plain() substring)', 'hits': 14}, 'L1e': {'by': "quote_evidence.py:40 and test_pf_fidelity_fix.py:184 ('…')", 'hits': 0}}
- hits each lever clears / adds when off: {'extra': {'cleared': 0, 'added': 0}, 'suppress': {'cleared': 0, 'added': 0}, 'abbrev': {'cleared': 0, 'added': 0}, 'furniture': {'cleared': 68, 'added': 44}, 'footnotes': {'cleared': 0, 'added': 0}, 'hand-footnotes': {'cleared': 14, 'added': 20}, 'ruled_out': {'cleared': 0, 'added': 0}, 'unformalised': {'cleared': 262, 'added': 0}, 'sidecar': {'cleared': 549, 'added': 19}}
- adjudication of the baseline hits: 0 confirmed, 0 contradicted, 827 unadjudicated; the document's findings: {'findings': 49, 'split': 24, 'REAL-by-both': 24, 'NOT-by-both': 1, 'unit_fp1_unchanged': 0} (a hit matches only a finding whose unit's fp-1 is unchanged since the adjudication)
- false-discovery proportion among hits not measured: 0 confirmed, 0 contradicted, 827 unadjudicated. Item 32's false-alarm figure needs a seeded adjudication sample (two blind adjudicators, about 20 hits per document), offered to the DRI and not run here.
- run cost (measured): {"wall_s": 12561.9, "schedule_wall_s": 12311.3, "child_cpu_s": 40417.3, "run_cpu_s": 40415.6, "peak_concurrency": 16, "mean_concurrency": 6.96, "admission_wait_s": 6596.8, "per_mutant_s": {"mean": 714.7, "median": 791.8, "max": 1008.4}, "baseline_s": 296.729, "worker_peak_rss_bytes": 335855616, "max_peak_rss_bytes": 505724928, "lean_service_start": {"first_s": 0.6483073480194435, "second_s": 0.2007026270730421, "start_s": 0.448}, "cpu_h_per_100": 11.69, "wall_min_per_100": 218.1}; tokens 0. the challenger's 2.8 CPU-h per 100 mutants is an estimate for a 280-question set; RSP has 126 questions, so the figures are not like for like.

