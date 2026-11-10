# Per-walk timings (drv2.py.txt, drv3.py.txt)

The variants are made from lean/VE/Events/RouteExamples.lean at main 65e6e4b0e. Each is put in place of
RouteExamples.lean in one unmutated scratch copy (the tool's `Scratch`, with `install`), and
`probe(..., only={first check})` runs twice per variant.

    head -63 lean/VE/Events/RouteExamples.lean > cut63.lean           # ends after guard :62
    sed '3d' cut63.lean > cut63_nochain.lean                          # without import VE.Service.DocumentChain
    sed '62s/.*/#guard (1 : Nat) == 1/' cut63.lean > trivial.lean     # a guard with an empty closure
    uv run python -I drv2.py.txt $PWD cut63.lean cut63_nochain.lean
    uv run python -I drv2.py.txt $PWD trivial.lean
    uv run python -I drv3.py.txt $PWD cut63.lean   # READS copied in memory, both `todo := todo ++ X` made `todo := X ++ todo`

Output (`entries`: line -> [flags without hash, number of `const` lines printed]):

    {"variant": "cut63.lean", "n": 1, "secs": 20.4, "entries": {"62": [["done"], 5070]}}
    {"variant": "cut63.lean", "n": 1, "secs": 16.4, "entries": {"62": [["done"], 5070]}}
    {"variant": "cut63_nochain.lean", "n": 1, "secs": 16.3, "entries": {"61": [["done"], 5070]}}
    {"variant": "cut63_nochain.lean", "n": 1, "secs": 15.9, "entries": {"61": [["done"], 5070]}}
    {"variant": "trivial.lean", "n": 1, "secs": 2.3, "entries": {"62": [["done"], 0]}}
    {"variant": "trivial.lean", "n": 1, "secs": 2.3, "entries": {"62": [["done"], 0]}}
    drv3 {"variant": "cut63.lean", "n": 1, "secs": 8.2, "entries": {"62": [["done"], 5070]}}
    drv3 {"variant": "cut63.lean", "n": 1, "secs": 8.1, "entries": {"62": [["done"], 5070]}}

`probe-log-*.jsonl` come from `drv.py.txt`, which wraps `probe` and `settle` and calls the tool's own `main`, unchanged:
`uv run python -I drv.py.txt <worktree> <log> --base 'a270588eb^' --only M1952 --test lean/VE/Events/WireExamples.lean
--test lean/VE/Events/RouteExamples.lean --jobs 2 [--build-timeout 500] --json <out>`. Their `--json` outputs are
../m509-main.json and ../m509-main-timeout500.json.
