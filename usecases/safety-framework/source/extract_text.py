"""Extract the pinned FSF 3.1 text that the span accounting partitions.

Usage: uv run --no-project --with pypdf==6.19.0 python extract_text.py IN.pdf OUT.txt

The PDF must have the SHA-256 pinned in ../PLAN.md section 1. Each page's
pypdf text has its whitespace collapsed to single spaces; pages are joined
by one newline, and the file ends with a newline. Page headers, footers and
footnotes stay where pypdf puts them; the plan accounts for them as layout.
"""
import hashlib
import sys

import pypdf

PDF_SHA256 = "ad10d2d240e0d557ecad406dbccedcbb4a70295f8ba8eec46bfe01803cb9c301"


def main(src, dst):
    data = open(src, "rb").read()
    if hashlib.sha256(data).hexdigest() != PDF_SHA256:
        sys.exit("PDF does not match the pinned SHA-256")
    if pypdf.__version__ != "6.19.0":
        sys.exit(f"pypdf {pypdf.__version__} is not the pinned 6.19.0")
    pages = pypdf.PdfReader(src).pages
    text = "\n".join(" ".join(page.extract_text().split()) for page in pages) + "\n"
    open(dst, "w", encoding="utf-8", newline="\n").write(text)
    print(hashlib.sha256(text.encode("utf-8")).hexdigest(), len(text.encode("utf-8")))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
