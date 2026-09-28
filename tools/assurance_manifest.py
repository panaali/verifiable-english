"""Print, or with --write regenerate, the generated tables in docs/spec/assurance-manifest.md."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve.assurance import render_decoders_markdown, render_markdown  # noqa: E402

DOC = ROOT / "docs/spec/assurance-manifest.md"
END = "<!-- END GENERATED -->"
# Marker -> renderer, in document order.
SECTIONS = {
    "<!-- BEGIN GENERATED DECODERS: python tools/assurance_manifest.py --write -->\n": render_decoders_markdown,
    "<!-- BEGIN GENERATED: python tools/assurance_manifest.py --write -->\n": render_markdown,
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="rewrite the generated sections in place")
    args = parser.parse_args(argv)
    if not args.write:
        print("\n".join(render() for render in SECTIONS.values()), end="")
        return 0
    text = DOC.read_text()
    for begin, render in SECTIONS.items():
        head, rest = text.split(begin, 1)
        _, tail = rest.split(END, 1)
        text = head + begin + render() + END + tail
    DOC.write_text(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
