# en-s6 delta

No user-visible verdict, diagnostic, fault-order, limit or rendered-text delta: authoring mode, no mode, no relay, no
Python product change, and no reading reads the new values yet (`actions_version` and `grammar_id` unchanged).

| Delta | Evidence | Ruling |
|---|---|---|
| Trusted Lean growth in `VE/EnglishGrammar/Norm/Value.lean`: S +142, K +0, D +0, G +0 against the merge base `3148e87c47dc` (`Norm/Examples.lean` is T, +0). | `tools/trust_map.py --check` on the final HEAD; every new trusted definition is exercised by a `Norm/Examples.lean` `#guard` that can fail (`trust-mutants.json`: 82 KILLED, 0 SURVIVOR, 0 UNKNOWN, 25 ALLOWED with reasons in `trust-mutants-allow.json`); the ties pass is the FOLLOW-UPS.md row under "## en-s6". | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
