"""measure.py: for each targeted trust-mutant inventory, the prior record's kills at a check line changed since it.

Usage: python3 docs/infra/tm-inventory-flag/measure.py SIDECAR.inventory.json... > counts.json, in a VE checkout
that has the record and item heads (a record whose worktree is gone is read at the item head). A kill "at a changed
check line" is a KILLED row of the sidecar's record whose killed_at lines (in its file named by detail, at the record's head) overlap a line the diff record_head..item_head
removes or changes (the old side; a pure insertion touches the lines on both sides of it). It "joins" when the
inventory (the sidecar's keys: definition, operator, before, after) does not already hold it for another reason.
"""
import json, re, subprocess, sys


def old_lines(h, head):
    """{file under lean/: [(first, last), ...]} of h's lines that h..head changes (h's numbering)."""
    out, f = {}, None
    diff = subprocess.run(["git", "diff", "-U0", h, head, "--", "lean"], capture_output=True, text=True, check=True)
    for x in diff.stdout.splitlines():
        if x.startswith("--- "):
            f = x[6:].removeprefix("lean/") if x[4:6] == "a/" else None
        elif (g := re.match(r"@@ -(\d+)(?:,(\d+))? ", x)) and f:
            a, n = int(g[1]), int(g[2]) if g[2] is not None else 1
            out.setdefault(f, []).append((a, a + n - 1) if n else (a, a + 1))
    return out


def measure(path):
    side = json.load(open(path))
    try:
        record = json.load(open(side["record"]))
    except FileNotFoundError:  # a removed worktree's record: the copy committed at the item's head
        kept = "docs/" + side["record"].split("/docs/", 1)[1]
        record = json.loads(subprocess.run(["git", "show", f"{side['item_head']}:{kept}"], capture_output=True,
                                           text=True, check=True).stdout)
    changed = old_lines(side["record_head"], side["item_head"])
    keys = side.get("keys")
    if keys is None:  # an older sidecar: the keys of its ids in the targeted run's own record beside it
        rows = json.load(open(path.removesuffix(".inventory.json")))["mutants"]
        keys = {m["id"]: (m["definition"], m["operator"], m["before"], m["after"]) for m in rows}
        keys = {i: keys[i] for i in side["ids"]}
    held = {tuple(k) for k in keys.values()}
    rows = []
    for m in record["mutants"]:
        site = re.match(r"lean/(\S+?\.lean):\d+:", m.get("detail") or "")
        if m.get("raw_status") != "KILLED" or not site or not m.get("killed_at"):
            continue
        a, b = m["killed_at"]
        if any(x <= b and a <= y for x, y in changed.get(site[1], ())):
            rows.append({"id": m["id"], "definition": m["definition"], "operator": m["operator"],
                         "status": m["status"], "check": f"{site[1]}:{a}",
                         "in_inventory": (m["definition"], m["operator"], m["before"], m["after"]) in held})
    kills = sum(m.get("raw_status") == "KILLED" for m in record["mutants"])
    return {"sidecar": path.rsplit("/", 1)[-1], "record_head": side["record_head"], "item_head": side["item_head"],
            "inventory": len(side["ids"]), "record_kills": kills, "changed_check_files": sorted(
                f for f in changed if any(r["check"].startswith(f + ":") for r in rows)),
            "killed_at_changed_check": len(rows), "already_in": sum(r["in_inventory"] for r in rows),
            "would_join": sum(not r["in_inventory"] for r in rows), "rows": rows}


if __name__ == "__main__":
    json.dump([measure(p) for p in sys.argv[1:]], sys.stdout, indent=1)
    print()
