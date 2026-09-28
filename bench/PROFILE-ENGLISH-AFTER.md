# English path optimization: before and after

The before artifact used five timed repeats per case. The current offline harness gives each case one untimed warm-up, then five timed repeats except editor catalogues, which get 20. It calls no proposer or model service. Raw repeat times, input hashes, machine load, and cProfile rows are in [before](PROFILE-ENGLISH-BEFORE.json) and [after](PROFILE-ENGLISH-AFTER.json). See [Reproduce](#reproduce) for the current command.

| Path | Before p50 / p95 ms | After p50 / p95 ms |
|---|---:|---:|
| BlueDot document check | 18,919.9 / 21,939.9 | 1,043.8 / 1,090.6 |
| Latest Claude document check | 90.0 / 98.8 | 50.3 / 50.7 |
| Latest UDHR document check | 6.8 / 8.2 | 3.1 / 3.4 |
| Editor scope catalogue | 173.8 / 304.4 | 88.7 / 90.1 |
| Editor reference catalogue | 123.4 / 127.9 | 54.5 / 55.7 |
| Editor checked wording | 7.4 / 29.9 | 7.4 / 8.4 |
| Editor recovery classify | 181.6 / 183.1 | 97.4 / 124.1 |
| Longest admitted sentence (150 tokens), parse plus natural display | 158.4 / 200.1 | 64.2 / 95.0 |

BlueDot's measured p95 fell 95.0%, below the 5-second budget. The current run had much lower machine load (about 2 versus 17–25 in the original run), so the before/after wall-time differences cannot be attributed to code alone. For the scope catalogue, the BEFORE p95 was 304.4 ms including its cold first call, or 176.0 ms using only its four warm calls; the AFTER p95 was 90.1 ms from 20 warm calls. Most of the apparent 304.4-to-90.1 ms tail drop comes from this change in sampling method, not the code. The editor catalogue cProfile counted eight `_parse_english_document` calls before and eight wrapper calls after, but only four full parser/derivation audits after; exact repeated sentence audits were reused. The stand-alone sentence path does not use the editor request cache. A separate randomized editor history replay fell from 143.5 to 22.2 seconds when the cache was extended through recovery commands and ledger replay.

[Pre-optimization output hashes](PROFILE-GOLDEN.json) pin all available Claude, UDHR, BlueDot, and W6A pilot documents by source hash. Run `PATH="$HOME/.elan/bin:$PATH" PYTHONPATH=.:bench lake env uv run python bench/check_profile_goldens.py` to compare exact JSON bytes for nine accepted documents, the W6A schema diagnostic, and two editor catalogues plus checked wording. All comparisons passed after the changes.

The full suite requires `PATH=$HOME/.elan/bin:$PATH lake build` in `lean/` before pytest. One deadline test's original 0.3-second setup expired before reaching the seal on this loaded host, including on untouched HEAD; its test window was widened to exercise the same sealing deadline assertion reliably. A randomized ledger validity test uses a larger budget for its many replays; dedicated deadline tests retain their original limits.

Verification commands for the current worktree are `PATH="$HOME/.elan/bin:$PATH" lake build` in `lean/`, `python3 lean/audit.py`, and `PATH="$HOME/.elan/bin:$PATH" PYTHONPATH=.:bench lake env uv run python -m pytest -q` at the repository root. The golden comparison and the shared model scope checks were recorded for the earlier optimization run; their results are historical rather than verification of later commits.

## Reproduce

From the repository root, this runs the current offline harness and writes `bench/PROFILE-ENGLISH-REPRO.json`, leaving the committed AFTER artifact intact. The harness has a fixed output filename, so the command redirects that one write to the reproduction file:

```sh
PATH="$HOME/.elan/bin:$PATH" PYTHONPATH=.:bench lake env uv run python - <<'PY'
from pathlib import Path
import bench.profile_english as benchmark

original_write_text = Path.write_text
published_path = benchmark.ROOT / "bench/PROFILE-ENGLISH-AFTER.json"
reproduction_path = Path("bench/PROFILE-ENGLISH-REPRO.json")

def write_reproduction(path, data, *args, **kwargs):
    if path == published_path:
        path = reproduction_path
    return original_write_text(path, data, *args, **kwargs)

Path.write_text = write_reproduction
benchmark.main()
PY
```
