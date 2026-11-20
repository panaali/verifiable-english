"""usage: planlist.py <root> <base> <out.json>: the trust_mutants plan (id, file) at <root> since <base>, trusted classes."""
import json, sys
from pathlib import Path
root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / "tools"))
import trust_mutants as tm
found, tree, fatal = tm.plan(root, sys.argv[2], tm.classes_of(",".join(tm.TRUSTED)))
json.dump({"fatal": fatal, "mutants": [[m.id, m.file] for m in found]}, open(sys.argv[3], "w"))
print(len(found), "mutants;", len(fatal), "fatal")
