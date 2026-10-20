# F16's class: a number of the step-1 table or of a named sentence that the evidence does not give. Each cell of the
# table (counts, seconds, survivors, yes/no) and each number of each named sentence is changed alone, and each named
# sentence is removed alone, in a copy of REPORT.md; claims.py's table and named checks must give UNBOUND on every copy,
# and none on REPORT.md itself.
uv run python - <<'PY'
import re, sys, tempfile
from pathlib import Path
sys.path.insert(0, "docs/speed/trustmut")
import claims

report = claims.DOCS[0].read_text()
def bad(text):
    path = Path(tempfile.mkdtemp()) / "REPORT.md"
    path.write_text(text)
    return [line for line in claims.tabled(path) + claims.bindings(path) if " UNBOUND " in line]
assert not bad(report), bad(report)
def changed(cell):
    if m := re.search(r"\d+", cell):
        return cell[:m.start()] + str(int(m[0]) + 1) + cell[m.end():]
    return {"yes": "no", "no": "yes", "NO": "yes"}.get(cell, cell + "x")
copies = []
lines = report.split("\n")
for n, line in enumerate(lines):
    if re.match(r"\| (pk-1|qt-a1|ap-2) F\d+ \|", line):
        cells = line.split("|")
        for j in range(1, len(cells) - 1):
            cells2 = cells[:j] + [f" {changed(cells[j].strip())} "] + cells[j + 1:]
            copies.append((f"table line {n + 1} cell {j}", "\n".join(lines[:n] + ["|".join(cells2)] + lines[n + 1:])))
flat = report
for words, numbers, _ in claims.named():
    spaced = r"(\d[\d,]*)".join(r"\s+".join(map(re.escape, part.split(" "))) for part in words.split("{}"))
    first = re.search(spaced, flat)  # the sentence as the report wraps it
    assert first, words
    for k in range(1, len(first.groups()) + 1):
        copies.append((f"{words[:30]} number {k}", flat[:first.start(k)] + "9" + flat[first.start(k):]))
    copies.append((f"{words[:30]} removed", flat[:first.start()] + flat[first.end():]))
missed = [what for what, text in copies if not bad(text)]
print(f"F16c: {len(copies) - len(missed)} of {len(copies)} changed copies UNBOUND")
if missed:
    print("not flagged:", missed)
sys.exit(1 if missed else 0)
PY
