"""Print, or with --write regenerate (--check: compare), the generated tables in docs/spec/assurance-manifest.md."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from lean_statements import inventory_path, write_inventory  # noqa: E402
import regen_generated  # noqa: E402
from ve.assurance import render_decoders_markdown, render_markdown  # noqa: E402

# A train-only file (tools/regen_generated.py): the committed copy is the template of its hand-written parts; the
# check reads the copy `inventory_path` gives, the write goes to `write_inventory`'s.
DOC = regen_generated.entry_named("assurance-doc").paths[0]
END = "<!-- END GENERATED -->"
# Marker -> renderer, in document order.
SECTIONS = {
    "<!-- BEGIN GENERATED DECODERS: python tools/assurance_manifest.py --write -->\n": render_decoders_markdown,
    "<!-- BEGIN GENERATED: python tools/assurance_manifest.py --write -->\n": render_markdown,
}


def decoder_total_lines(manifest: dict) -> int:
    """`lean_decoders.total_lines`: the lines of every pinned decoder range (both ends included)."""
    return sum(end - start + 1 for entry in manifest["lean_decoders"]["files"] for start, end in entry["ranges"])


def document() -> str:
    text = (ROOT / DOC).read_text()
    for begin, render in SECTIONS.items():
        head, rest = text.split(begin, 1)
        _, tail = rest.split(END, 1)
        text = head + begin + render() + END + tail
    return text


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--write", action="store_true", help="rewrite the generated sections in place")
    action.add_argument("--check", action="store_true", help="exit 1 if the generated sections are stale")
    args = parser.parse_args(argv)
    if args.check:
        if inventory_path(DOC, ROOT).read_text() != document():
            print(f"{DOC} is stale; run python tools/assurance_manifest.py --write", file=sys.stderr)
            return 1
        return 0
    if not args.write:
        print("\n".join(render() for render in SECTIONS.values()), end="")
        return 0
    write_inventory(DOC, document(), ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
