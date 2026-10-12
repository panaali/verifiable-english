"""Report numbers rendered from the evidence, never typed: the `[report]` block of a batch's `evidence.toml`.

    python -m tools.evidence report DIR            print the block
The batch writes the rendered block between the markers of [report] file before its gate.

Each line of `lines` is a template. `{name.path|filter|...}` reads the evidence file `name` (`name.json` or
`name.json.gz` in the evidence directory), follows the dotted path (keys, or list indices), then applies the
filters left to right; `{{` and `}}` are literal braces. Filters:

    len           the length of a list or table         short       the first 8 characters (each, of a list)
    code          wrapped in backticks (each, of a list) join:SEP    a list joined by SEP
    map:FIELD     each row's FIELD                       minus:PATH  a number less another evidence value
    killed        the mutant records that failed a test (tools.evidence.killed)

The block sits between `<!-- BEGIN GENERATED <marker> -->` and `<!-- END GENERATED <marker> -->`;
`tools/batch_evidence.py --check` fails when the block in the file is not the rendering.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re

from tools.evidence import EvidenceError, killed, load

NAME = re.compile(r"[a-z0-9_-]+")


class Evidence:
    """The batch's evidence files, each read once, by name."""

    def __init__(self, directory: Path):
        self.directory, self.files = Path(directory), {}

    def __getitem__(self, name: str):
        if name not in self.files:
            if not NAME.fullmatch(name):
                raise EvidenceError(f"{name!r} is no evidence name")
            found = [p for p in (self.directory / f"{name}.json", self.directory / f"{name}.json.gz") if p.is_file()]
            if len(found) != 1:
                raise EvidenceError(f"evidence {name!r}: {len(found)} files in {self.directory}, not one")
            self.files[name] = load(found[0])
        return self.files[name]

    def lookup(self, path: str):
        name, *keys = path.strip().split(".")
        value = self[name]
        for key in keys:
            if isinstance(value, list) and key.lstrip("-").isdigit():
                value = value[int(key)]
            elif isinstance(value, dict) and key in value:
                value = value[key]
            else:
                raise EvidenceError(f"evidence path {path!r}: no {key!r}")
        return value


def _each(value, function):
    return [function(item) for item in value] if isinstance(value, list) else function(value)


def _number(value, what):
    if type(value) not in (int, float):
        raise EvidenceError(f"{what} is not a number: {value!r}")
    return value


def apply(evidence: Evidence, value, step: str):
    name, _, argument = step.partition(":")
    if name == "len":
        if not isinstance(value, (list, dict)):
            raise EvidenceError(f"len of a {type(value).__name__}")
        return len(value)
    if name == "short":
        return _each(value, lambda item: str(item)[:8])
    if name == "code":
        return _each(value, lambda item: f"`{item}`")
    if name == "join":
        if not isinstance(value, list):
            raise EvidenceError("join of a value that is not a list")
        return argument.join(str(item) for item in value)
    if name == "map":
        if not isinstance(value, list) or not all(isinstance(row, dict) and argument in row for row in value):
            raise EvidenceError(f"map:{argument} over rows without {argument!r}")
        return [row[argument] for row in value]
    if name == "minus":
        return _number(value, "minus") - _number(evidence.lookup(argument), argument)
    if name == "killed":
        rows = value.get("mutants") if isinstance(value, dict) else value
        if not isinstance(rows, list):
            raise EvidenceError("killed of a value that holds no mutant records")
        return sum(1 for row in rows if killed(row))
    raise EvidenceError(f"unknown filter {name!r}")


def render_line(evidence: Evidence, template: str) -> str:
    out, i = [], 0
    while i < len(template):
        if template.startswith(("{{", "}}"), i):
            out.append(template[i])
            i += 2
        elif template[i] == "{":
            end = template.find("}", i)
            if end < 0:
                raise EvidenceError(f"unclosed brace in {template!r}")
            path, *steps = template[i + 1:end].split("|")
            value = evidence.lookup(path)
            for step in steps:
                value = apply(evidence, value, step)
            out.append(str(value))
            i = end + 1
        elif template[i] == "}":
            raise EvidenceError(f"stray brace in {template!r}")
        else:
            out.append(template[i])
            i += 1
    return "".join(out)


def render(evidence_dir: Path, lines: list[str]) -> str:
    evidence = Evidence(evidence_dir)
    return "\n".join(render_line(evidence, line) for line in lines)


def markers(marker: str) -> tuple[str, str]:
    return f"<!-- BEGIN GENERATED {marker} -->\n", f"\n<!-- END GENERATED {marker} -->"


def block(text: str, marker: str) -> str:
    """The generated block of `text`; there must be exactly one."""
    begin, end = markers(marker)
    if text.count(begin) != 1 or text.count(end) != 1 or text.index(begin) > text.index(end):
        raise EvidenceError(f"the report has not exactly one {marker!r} block")
    return text.split(begin, 1)[1].split(end, 1)[0]


def replace_block(text: str, marker: str, rendered: str) -> str:
    begin, end = markers(marker)
    block(text, marker)
    head, rest = text.split(begin, 1)
    return head + begin + rendered + end + rest.split(end, 1)[1]


def main(argv=None) -> int:
    from tools.evidence.config import evidence_dir, read

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("batch", type=Path, help="the batch directory holding evidence.toml")
    args = parser.parse_args(argv)
    try:
        config = read(args.batch)
        if "report" not in config:
            raise EvidenceError(f"{args.batch}/evidence.toml has no [report]")
        rendered = render(evidence_dir(args.batch, config), config["report"]["lines"])
    except EvidenceError as exc:
        print(exc)
        return 1
    print(rendered)
    return 0
