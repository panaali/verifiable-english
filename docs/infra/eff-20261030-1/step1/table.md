| file | where | nodes | wall s | node s | repeated setup s | largest node s | k=2 | k=3 | k=4 | best cut |
|---|---|---|---|---|---|---|---|---|---|---|
| tests/test_consolidation_tools.py | ve-mac-1 | 288 | 357.7 | 356.7 | 7.9 | 290.0 | 298.0 | 298.0 | 298.0 | 17% (k=2) |
| tests/test_acts_vocab_mutants.py | ve-mac-1 | 643 | 129.8 | 129.3 | 0.5 (divisible) | 0.2 | 65.2 | 43.7 | 32.9 | 75% (k=4) |
| tests/test_readings_rd6b_differential.py | ve-mac-1 | 16 | 344.1 | 343.9 | 0.2 | 43.7 | 178.0 | 115.6 | 89.0 | 74% (k=4) |
| tests/test_english_evidence.py | ve-mac-1 | 77 | 510.3 | 509.7 | 0.5 | 26.7 | 255.4 | 170.5 | 128.0 | 75% (k=4) |
| tests/test_trust_mutants.py | ve-mac-1 | 505 | 515.9 | 514.9 | 178.4 | 23.9 | 347.2 | 290.9 | 262.8 | 49% (k=4) |
| tests/test_defaults_checks.py | ve-mac-1 | 3 | 99.2 | 99.1 | 0.1 | 98.1 | 98.3 | 98.3 | 98.3 | 1% (k=2) |
| tests/test_speech_polar_lean.py | ve-mac-1 | 9536 | 608.1 | 575.9 | 32.3 | 22.3 | 320.2 | 224.2 | 176.2 | 71% (k=4) |
| tests/test_lean_conformance.py | ve-mac-1 | 87 | 108.4 | 108.0 | 0.4 | 91.6 | 92.0 | 92.0 | 92.0 | 15% (k=2) |

top 4: 1342 s -> 548 s at each file's best k: cut 59% (stop rule: < 35%, or every top-4 file has a node above half its wall: False) -> BUILD
