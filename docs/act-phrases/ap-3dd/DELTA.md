# ap-3dd delta: `elaborate_faithful` (`VE.Acts`, `lean/VE/Acts/Faithful.lean`)

Base: `git merge-base HEAD main`. See [REPORT.md](REPORT.md).

**Public output: none.** The item adds theorems, two definitions that state them, and fixtures. No route, relay or
schema reads them, and `elaborate` is byte-identical. The one trust row below is what R16 asks a DELTA to itemise.

| # | Change | Evidence | Ruling |
|---|---|---|---|
| 1 | Trust growth, K +0, S +8, V +0 (trusted +8): `lean/VE/Acts/Faithful.lean` +8 (S: `readAs`, `IntendedActs`, spec 6.6) | `uv run python tools/trust_map.py --check`: PASS; `docs/act-phrases/ap-3dd/mutants.json` (each definition's bugs killed by a named `#guard`); FOLLOW-UPS.md "## ap-3dd" | R16 |
