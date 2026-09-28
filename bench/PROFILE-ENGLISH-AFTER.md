# English path optimization: before and after

The same offline harness (`PATH=$HOME/.elan/bin:$PATH PYTHONPATH=. lake env /home/seyran/code/ve-profile/.venv/bin/python bench/profile_english.py`) ran five sequential warm-process repeats per case. It called no proposer or model service. Raw repeat times, input hashes, machine load, and cProfile rows are in [before](PROFILE-ENGLISH-BEFORE.json) and [after](PROFILE-ENGLISH-AFTER.json).

| Path | Before p50 / p95 ms | After p50 / p95 ms |
|---|---:|---:|
| BlueDot document check | 18,919.9 / 21,939.9 | 3,622.2 / 3,850.8 |
| Latest Claude document check | 90.0 / 98.8 | 122.6 / 131.6 |
| Latest UDHR document check | 6.8 / 8.2 | 7.5 / 8.4 |
| Editor scope catalogue | 173.8 / 304.4 | 220.5 / 609.4 |
| Editor reference catalogue | 123.4 / 127.9 | 138.7 / 147.5 |
| Editor checked wording | 7.4 / 29.9 | 20.0 / 20.9 |
| Editor recovery classify | 181.6 / 183.1 | 258.2 / 315.0 |
| Longest admitted sentence (150 tokens), parse plus natural display | 158.4 / 200.1 | 184.9 / 285.1 |

BlueDot's p95 fell 82.4%, below the 5-second budget. The final run had higher machine load (about 19 versus 17 in the editor samples, with a much higher five-minute average), so its editor and short-document tail differences cannot be attributed to the code alone. The editor catalogue cProfile counted eight `_parse_english_document` calls before and eight wrapper calls after, but only four full parser/derivation audits after; exact repeated sentence audits were reused. The stand-alone sentence path does not use the editor request cache. Replay of one randomized editor history fell from 143.5 to 22.2 seconds when the cache was extended through recovery commands and ledger replay.

[Pre-optimization output hashes](PROFILE-GOLDEN.json) pin all available Claude, UDHR, BlueDot, and W6A pilot documents by source hash. Run `PATH=$HOME/.elan/bin:$PATH PYTHONPATH=.:bench lake env /home/seyran/code/ve-profile/.venv/bin/python bench/check_profile_goldens.py` to compare exact JSON bytes for nine accepted documents, the W6A schema diagnostic, and two editor catalogues plus checked wording. All comparisons passed after the changes.

The full suite requires `PATH=$HOME/.elan/bin:$PATH lake build` in `lean/` before pytest. One deadline test's original 0.3-second setup expired before reaching the seal on this loaded host, including on untouched HEAD; its test window was widened to exercise the same sealing deadline assertion reliably. A randomized ledger validity test uses a larger budget for its many replays; dedicated deadline tests retain their original limits.

Final verification: `PATH=$HOME/.elan/bin:$PATH PYTHONPATH=. lake env /home/seyran/code/ve-profile/.venv/bin/python -m pytest -q -x` completed with 2,161 passed, 5 optional skips, and 1 live test deselected. The golden comparison above was rerun after the suite and passed. Three distinct countermodel queries also returned identical complete results with and without the shared model scope.
