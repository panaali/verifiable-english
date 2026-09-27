"""Inventory shipped web text for the app copy measurement."""
from __future__ import annotations

import ast
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HTML = 've_webapp/static/index.html'
JS = 've_webapp/static/app.js'
PYTHON = ('ve_webapp/server.py', 've_webapp/worker.py', 've_webapp/drafts.py',
          've_webapp/rules.py', 've_webapp/examples.py')
SOURCES = (HTML, JS, *PYTHON)


class VisibleHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items: set[str] = set()
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1
        for name, value in attrs:
            if name in ('aria-label', 'placeholder', 'title') and value:
                self.items.add(value.strip())

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.items.add(data.strip())


def html_text(source: str) -> set[str]:
    parser = VisibleHTML()
    parser.feed(source)
    return parser.items


def js_literals(source_path: Path = ROOT / JS) -> set[str]:
    result = subprocess.run(['node', str(Path(__file__).with_name('extract-js.cjs')),
                             str(source_path)], check=True, capture_output=True, text=True)
    return set(json.loads(result.stdout))


def python_literals(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    return {node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)}


def inventory(html_source: str | None = None) -> dict[str, set[str]]:
    return {HTML: html_text(html_source if html_source is not None else (ROOT / HTML).read_text()),
            JS: js_literals(),
            **{name: python_literals(ROOT / name) for name in PYTHON}}
