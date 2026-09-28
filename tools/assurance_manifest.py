"""Print, or with --write regenerate, the operation table in docs/spec/assurance-manifest.md."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve.assurance import render_markdown  # noqa: E402

DOC = ROOT / "docs/spec/assurance-manifest.md"
BEGIN = "<!-- BEGIN GENERATED: python tools/assurance_manifest.py --write -->\n"
END = "<!-- END GENERATED -->"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="rewrite the generated section in place")
    args = parser.parse_args(argv)
    table = render_markdown()
    if not args.write:
        print(table, end="")
        return 0
    text = DOC.read_text()
    head, rest = text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    DOC.write_text(head + BEGIN + table + END + tail)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
