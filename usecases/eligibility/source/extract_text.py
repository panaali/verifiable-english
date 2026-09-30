"""Extract the main-content text of a pinned GOV.UK page (stdlib only).

Usage: python extract_text.py PAGE.html [ROOT_TAG] > PAGE.txt

Keeps the text inside ROOT_TAG (default <main>; use `body` for the
legislation.gov.uk XHTML), one block element per line, so the pinned
HTML bytes and the reviewed text can be compared by anyone.
"""

import sys
from html.parser import HTMLParser

BLOCKS = {"p", "li", "h1", "h2", "h3", "h4", "tr", "td", "th", "div", "br", "caption"}


class MainText(HTMLParser):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.depth = 0
        self.skip = 0
        self.out = []

    def handle_starttag(self, tag, attrs):
        if tag == self.root:
            self.depth += 1
        if tag in ("script", "style"):
            self.skip += 1
        if self.depth and tag in BLOCKS:
            self.out.append("\n")
        if self.depth and tag in ("td", "th"):
            self.out.append(" | ")

    def handle_endtag(self, tag):
        if tag == self.root:
            self.depth -= 1
        if tag in ("script", "style"):
            self.skip -= 1

    def handle_data(self, data):
        if self.depth and not self.skip:
            self.out.append(data)


def main():
    parser = MainText(sys.argv[2] if len(sys.argv) > 2 else "main")
    with open(sys.argv[1], encoding="utf-8") as handle:
        parser.feed(handle.read())
    lines = (" ".join(line.split()) for line in "".join(parser.out).splitlines())
    print("\n".join(line for line in lines if line))


if __name__ == "__main__":
    main()
