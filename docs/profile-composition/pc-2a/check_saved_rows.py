"""Show that the rows first saved on the base keep their values in tests/data/composition/pc2a/parity-base.json: compare
each command answer of the file at the commit that first saved it with the file as it stands."""
import json
import subprocess
import sys

PATH = "tests/data/composition/pc2a/parity-base.json"
first = subprocess.run(["git", "log", "--diff-filter=A", "--format=%H", "--", PATH], capture_output=True, text=True,
                       check=True).stdout.split()[-1]
base = json.loads(subprocess.run(["git", "show", f"{first}:{PATH}"], capture_output=True, text=True, check=True).stdout)
now = json.load(open(PATH))
kept = {name: all(now[name].get(k) == v for k, v in rows.items()) for name, rows in base.items() if name in now}
print(f"first saved at {first[:9]}: {len(base)} rows; {len(kept)} remain, {sum(kept.values())} unchanged; "
      f"trimmed {sorted(set(base) - set(now))}; added {len(set(now) - set(base))}")
sys.exit(0 if all(kept.values()) else 1)
