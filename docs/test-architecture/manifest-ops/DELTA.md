# tarch-manifest-ops: deltas

No rows. The item stopped after its measurement (REPORT.md, step 1 stop rule). It changes no selector
behaviour and no VE output: no file under `ve/`, `lean/` or `rust/` is touched, and the one `tools/` line registers the
evidence script in `tools/regen_generated.py` `NOT_REGENERATED`. The rest is batch evidence: `measure.py`, its saved rows `evidence/replay.json.gz`, and the report. These are
checked by `python3 docs/test-architecture/manifest-ops/measure.py --check` (D4); there is no permanent test.
