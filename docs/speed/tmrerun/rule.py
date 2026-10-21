"""The carry rule step 1 measured (speed-tmrerun), for a `tools/trust_mutants.py --again PREV.json`, which was not built
(REPORT.md section 1: the rule carries under half of the rerun mutants). It reuses PREV's verdict on a mutant only
where nothing that verdict reads changed:

- the same mutant (`Reads.key`): its file, definition, operator, declaration text and edit, byte for byte;
- INVALID: the lines before the declaration in its file and its module's import closure read the same (`scope`);
- KILLED: those, and its killing check (the file:line in `detail`), byte for byte, with the lines before it in its
  file and its module's import closure (`check`). A check moved by lines added above it keeps its kill;
- nothing else: SURVIVOR, UNKNOWN, NOT RUN and ALLOWED rerun.

"Reads" is the tool's own data: the import closure (`check_lean_imports.imports`) and the commands `classify` and
trust_map's spans give each file. Of those files every line counts as written (comments and docstrings too: a
`#guard_msgs` reads its docstring; blank lines dropped, so a line moved by an insertion above it reads the same) but
the lines of a theorem, `example` or check command (`classify`: check or proof) with no attribute and a name no
counted line names: nothing elaborated after them reads them. A carried KILLED stands on its check's refutation; a new
check or proof elsewhere in its build that the mutant would make fail otherwise is not looked for."""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from trust_mutants import Mutant, Tree, code_only, file_roles, imports  # noqa: E402


def digest(*parts: str) -> str:
    return hashlib.sha256("\0".join(parts).encode()).hexdigest()[:16]


class Reads:
    """What a verdict reads of one checkout, as digests; `verdict` writes them on a mutant, `carry` compares."""

    def __init__(self, root: Path, tree: Tree, outside: list[Path]):
        self.tree, self.memo = tree, {}
        self.roles = {**tree.roles, **{str(t): file_roles(t) for t in outside}}
        self.texts = {**{f: (root / "lean" / f).read_text() for f in tree.files.values()},
                      **{str(t): t.read_text() for t in outside}}
        codes = {f: code_only(text).split("\n") for f, text in self.texts.items()}
        # file -> line -> the name of the theorem, `example` or check command on it with no attribute
        self.loose: dict[str, dict[int, str | None]] = {
            f: {n: name for s, e, r, name in self.roles.get(f, ()) if r != "other" and "@[" not in "\n".join(
                code[s - 1:e]) for n in range(s, e + 1)} for f, code in codes.items()}
        named = {w for f, code in codes.items() for n, line in enumerate(code, 1) if n not in self.loose[f]
                 for w in re.findall(r"[^\W\d][\w']*", line)}
        for lines in self.loose.values():
            for n in [n for n, name in lines.items() if name and name.rpartition(".")[2] in named]:
                del lines[n]

    def kept(self, f: str, before: int) -> str:
        """The digest of the lines of `f` before line `before` that count."""
        if (f, before) not in self.memo:
            self.memo[f, before] = digest(*(line.rstrip() for n, line in enumerate(
                self.texts[f].split("\n")[:before - 1], 1) if line.strip() and n not in self.loose[f]))
        return self.memo[f, before]

    def closure(self, f: str) -> str:
        """The digest of every module of lean/ that `f` imports, transitively, as its lines count."""
        if f not in self.memo:
            seen, todo = set(), [f]
            while todo:
                new = {x for x in imports(self.texts[todo.pop()]) if x in self.tree.files} - seen
                seen |= new
                todo += [self.tree.files[x] for x in new]
            self.memo[f] = digest(*(f"{x} {self.kept(self.tree.files[x], 1 << 30)}" for x in sorted(seen)))
        return self.memo[f]

    def key(self, m: Mutant) -> str:
        lines = self.texts[m.file].split("\n")
        first = sum(len(line) + 1 for line in lines[:m.lines[0] - 1])
        return digest(m.file, m.definition, m.operator, "\n".join(lines[m.lines[0] - 1:m.lines[1]]),
                      str(m.start - first), self.texts[m.file][m.start:m.edit[0]], m.edit[1])

    def scope(self, m: Mutant) -> str:
        return digest(self.kept(m.file, m.lines[0]), self.closure(m.file))

    def check(self, m: Mutant, f: str, first: int, last: int) -> str:
        return digest(self.scope(m), "\n".join(self.texts[f].split("\n")[first - 1:last]), self.kept(f, first),
                      self.closure(f))

    def killer(self, detail: str) -> tuple[str, int] | None:
        """The file and line of the check a KILLED detail cites (`settle`)."""
        if not (at := re.match(r"(\S+?\.lean):(\d+): ", detail)):
            return None
        f = at[1].removeprefix("lean/") if at[1].removeprefix("lean/") in self.tree.roles else at[1]
        return (f, int(at[2])) if f in self.texts else None

    def verdict(self, m: Mutant) -> None:
        """m.reads (and m.killed_at) for a KILLED or INVALID verdict: what `carry` compares."""
        m.reads, m.killed_at = "", None
        if m.status == "INVALID":
            m.reads = self.scope(m)
        elif m.status == "KILLED" and (at := self.killer(m.detail)):
            if span := next(((s, e) for s, e, r, _ in self.roles.get(at[0], ()) if r == "check" and s <= at[1] <= e),
                            None):
                m.reads, m.killed_at = self.check(m, at[0], *span), span

    def carry(self, m: Mutant, p: dict, head: str) -> None:
        """PREV's verdict `p` on m (the same key) when what it reads reads the same here: m.carried_from = head."""
        try:
            if p["status"] == "INVALID" and p["reads"] == self.scope(m):
                m.status, m.detail, m.reads, m.carried_from = "INVALID", str(p["detail"]), p["reads"], head
            elif p["status"] == "KILLED" and (at := self.killer(p["detail"])):
                (f, n), (s0, e0) = at, (int(x) for x in p["killed_at"])
                for s, e, *_ in sorted((x for x in self.roles.get(f, ()) if x[2] == "check" and x[1] - x[0] == e0 - s0),
                                       key=lambda x: abs(x[0] - s0)):
                    if self.check(m, f, s, e) == p["reads"]:
                        m.status, m.reads, m.killed_at, m.carried_from = "KILLED", p["reads"], (s, e), head
                        m.detail = re.sub(r"(?<=\.lean:)\d+", str(n - s0 + s), p["detail"], count=1)
                        return
        except (KeyError, TypeError, ValueError):
            return
