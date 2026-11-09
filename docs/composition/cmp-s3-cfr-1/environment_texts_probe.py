"""Environment refusal texts of every list relational-fol@0, right-clauses@0 and up to two more environment profiles,
as the build of the tree it runs in answers them (run in a worktree at the base commit and at this item's head):
`python environment_texts_probe.py <lock file>`, run from the worktree root."""
import sys, json, itertools
sys.path.insert(0, '.')
import ve.backends.lean_service as ls
from pathlib import Path
lock = Path(sys.argv[1]); lock.write_text(json.dumps({"ve_service": [ls.executable_sha256(Path('lean/.lake/build/bin/ve_service').resolve())]})); ls.BUILD_LOCK = lock
from ve import Environment
OTHERS = ["acts@0", "alternatives@0", "closure@0", "data@0", "definitions@0", "documents@1", "nary@0", "norm-defaults@0",
          "norms@0", "order@0", "readings@1", "reports@0", "rights@0", "risk@0", "soft-norms@0", "speech-acts@0", "time@0"]
vocab = {"sorts": {"state": {"description": "state"}, "person": {"description": "person"}},
         "predicates": {"country_of": {"arguments": ["state", "person"], "description": "base"}},
         "constants": {"texas": {"sort": "state", "description": "Texas"}}}
out = {}
for k in (0, 1, 2):
    for extra in itertools.combinations(OTHERS, k):
        ps = sorted({"relational-fol@0", "right-clauses@0", *extra})
        v = json.loads(json.dumps(vocab))
        if "acts@0" in ps: v["acts"] = {"fixed": []}
        env = {"language": "ve.core@0.2", "profiles": ps, "spec_revision": "ve-v0.2-expand2-2026-09-25", "vocabulary": v}
        try: Environment(env); out[",".join(ps)] = "ok"
        except Exception as x: out[",".join(ps)] = str(x)
print(json.dumps(out))
