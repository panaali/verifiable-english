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
          've_webapp/rules.py', 've_webapp/examples.py', 've_webapp/asimov.py')
# Built by VE (python -m ve_webapp.asimov --write) and served as the Asimov section.
ASIMOV = 've_webapp/asimov.json'
SOURCES = (HTML, JS, *PYTHON, ASIMOV)
# Keys of the Asimov data that hold identifiers, verdict codes or checker evidence.
ASIMOV_INTERNAL_KEYS = frozenset({'format', 'id', 'focus', 'robot', 'law', 'group', 'verdict',
                                  'status', 'value', 'number', 'targets', 'checked_by'})


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


def reader_strings(value, key=None):
    """Every string of the Asimov data that the page can show."""
    if key in ASIMOV_INTERNAL_KEYS:
        return
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from reader_strings(v, k)
    elif isinstance(value, list):
        for item in value:
            yield from reader_strings(item, key)


def asimov_strings(path: Path = ROOT / ASIMOV) -> set[str]:
    return set(reader_strings(json.loads(path.read_text())))


def inventory(html_source: str | None = None) -> dict[str, set[str]]:
    return {HTML: html_text(html_source if html_source is not None else (ROOT / HTML).read_text()),
            JS: js_literals(),
            **{name: python_literals(ROOT / name) for name in PYTHON},
            ASIMOV: asimov_strings()}
