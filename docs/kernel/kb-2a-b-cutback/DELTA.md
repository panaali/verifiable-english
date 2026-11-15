# kb-2a-b-cutback: user-visible delta

None. The item adds theorems and their ties and changes no definition (`git diff main -- lean/VE/Service/CoreCheck.lean`
touches only the proof of `core_facts_round_trip` and adds `facts_round_trip`; `Document.lean`, `DocumentFold.lean`,
`CoreDocument.lean` and the schemas are unchanged). No answer changes: `status-compare.json` (0 differing, the four
fixtures' recomputed statuses identical to kb-2a-b's), `frozen-keys.json` (the five frozen keys exit 0, tree unchanged).

The trusted count falls (K +0, S +0, untied [V] -227 against b6cbafe80a60, `uv run python tools/trust_map.py --check`);
a fall needs no signature and adds no allowance. No new trusted line.

| # | Delta | Evidence | Ruling |
|---|---|---|---|
| 1 | Generated files, through `uv run python tools/regen_generated.py --write --skip route-cases` (route-cases needs a Rust binary this worktree has not built; none of its inputs changed): `lean/statements.txt`, `lean/predicates.txt`, `lean/declarations.txt`, `lean/axioms.txt`, `lean/VE/Audit.lean`, `lean/VE.lean` (the new module's import) and the code map | `uv run python tools/regen_generated.py --check` (the gate) | R12 |
