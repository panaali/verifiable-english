# English runner root delta

User-visible output delta: **none**. The pre-change and rebuilt `ve_english_run`
returned byte-identical exit codes, stdout, and stderr for all six existing
English service-corpus payloads. The recorded input and output hashes are in
[`evidence/english-output-diff.json`](evidence/english-output-diff.json).
`tests/test_english_runner_root.py` also pins four exact byte responses,
including malformed input. No standing ruling or DRI signature is needed.
