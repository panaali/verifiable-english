"""Every legend this item changed keeps its base words in order, and no other field of the symbol changed.

    python3 docs/infra/srccov-anthropic-rsp-1119/evidence/legend_keep.py [BASE]    (BASE defaults to main)
"""
import json
import re
import subprocess
import sys

base = sys.argv[1] if len(sys.argv) > 1 else "main"
old = json.loads(subprocess.run(["git", "show", f"{base}:usecases/anthropic-rsp/environment.d1.json"],
                                capture_output=True, text=True, check=True).stdout)["vocabulary"]
new = json.load(open("usecases/anthropic-rsp/environment.d1.json"))["vocabulary"]


def words(text):
    return re.findall(r"[A-Za-z0-9{}_'-]+", text)


def in_order(a, b):
    it = iter(b)
    return all(x in it for x in a)


bad, changed = [], 0
for section in old:
    assert set(old[section]) == set(new[section]), section
    for name, entry in old[section].items():
        if entry == new[section][name]:
            continue
        changed += 1
        others = {k for k in set(entry) | set(new[section][name]) if k != "description"
                  and entry.get(k) != new[section][name].get(k)}
        if others or not in_order(words(entry["description"]), words(new[section][name]["description"])):
            bad.append((section, name, sorted(others)))
print(f"{changed} changed legends; {len(bad)} lose base words or change another field: {bad}")
sys.exit(1 if bad else 0)
