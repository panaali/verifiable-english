"""sa-checked-view statement gate (the pattern of docs/attitudes/at-1d/spec_text_check.py): each of the eight
declarations of docs/spec/purpose-explanation.md 5.1's Lean block appears, with its docstring, after whitespace
normalisation, in lean/VE/Service/DocumentView.lean (or the one path given), each definition and theorem followed by
` :=` and the structure by the next docstring, so appended text is refused. Run from the repo root."""
import re
import sys

EIGHT = ("CheckedView", "checkDocSetsView", "activeKinds", "checkDocSetsView_answer", "checkDocSetsView_rows",
         "checkDocSetsView_candidates", "checkDocSetsView_readings", "checkDocSetsView_packs")
HEAD = re.compile(r"^(/--|theorem |def |structure )")
spec = open("docs/spec/purpose-explanation.md").read().splitlines()
norm = lambda s: " ".join(s.split())


def pieces(first, last):
    """The docstring-and-declaration pieces of the Lean blocks between these two headings."""
    lines = spec[spec.index(first):spec.index(last)]
    out, inside = [], False
    for line in lines:
        if line.startswith("```"):
            inside = line.startswith("```lean")
            continue
        if not inside or not line.strip() or line.startswith(("namespace ", "end ")):
            continue
        if HEAD.match(line) and not (out and out[-1][0].startswith("/--") and out[-1][-1].endswith("-/")
                                     and not any(HEAD.match(x) and not x.startswith("/--") for x in out[-1])):
            out.append([])
        out[-1].append(line)
    return out


def name(p):
    m = re.search(r"^(?:theorem|def|structure) (\S+)", "\n".join(p), re.M)
    return m.group(1) if m else None


def main(source="lean/VE/Service/DocumentView.lean"):
    src = norm(open(source).read())
    statements = [p for p in pieces(
        "### 5.1 The checked view (owner: the document model, `VE.Service.Document`; DRI 2(d))",
        "### 5.2 Front-matter keys (owner: W2's loader, `VE.Discourse.Loader`)")
                  if name(p) in EIGHT]
    tail = lambda p: " /--" if name(p) == "CheckedView" else " :="
    missing = [name(p) for p in statements if norm("\n".join(p)) + tail(p) not in src]
    found = {name(p) for p in statements}
    print(f"{len(statements)} statements, {len(missing)} missing, {len(found)} of 8 found", *missing, sep="\n")
    return 1 if missing or found != set(EIGHT) or len(statements) != 8 else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
