"""Audit every project Lean source and every named theorem's dependencies.

The pinned toolchain/build cache under .lake is trusted, not project source.
This is a source/dependency policy check, not an untrusted-code sandbox.
"""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}
FORBIDDEN = re.compile(r"\b(sorry|sorryAx|admit|axiom|unsafe|native_decide|implemented_by|partial|opaque|extern)\b")


def code_only(text):
    """Blank nested comments and string literals, retaining source line numbers."""
    out, i, depth, quoted = [], 0, 0, False
    while i < len(text):
        pair = text[i:i + 2]
        c = text[i]
        if depth:
            if pair == "/-":
                depth += 1
                out.extend("  "); i += 2; continue
            if pair == "-/":
                depth -= 1
                out.extend("  "); i += 2; continue
            out.append("\n" if c == "\n" else " ")
        elif quoted:
            if c == "\\":
                out.extend("  "); i += 2; continue
            if c == '"':
                quoted = False
            out.append("\n" if c == "\n" else " ")
        elif pair == "/-":
            depth = 1
            out.extend("  "); i += 2; continue
        elif pair == "--":
            end = text.find("\n", i)
            if end < 0:
                end = len(text)
            out.extend(" " * (end - i)); i = end; continue
        elif c == "'" and (char := re.match(r"'(?:\\(?:x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4}|.)|[^'\\\n])'", text[i:])):
            out.extend(" " * len(char[0])); i += len(char[0]); continue
        elif c == '"':
            quoted = True
            out.append(" ")
        else:
            out.append(c)
        i += 1
    return "".join(out)


def scan_sources(root):
    actual = set()
    sources = [p for p in sorted(root.rglob("*.lean")) if ".lake" not in p.relative_to(root).parts]
    for source in sources:
        text = source.read_text()
        # Conservative literal scan also catches terms inside interpolation and
        # quotations. Comments/strings do not exempt forbidden tokens from policy.
        forbidden = FORBIDDEN.search(text)
        if forbidden:
            line = text.count("\n", 0, forbidden.start()) + 1
            raise AssertionError(f"{source.relative_to(root)}:{line}: forbidden {forbidden[0]}")
        code = code_only(text)
        scopes = []
        for line in code.splitlines():
            namespace = re.match(r"\s*namespace\s+(\S+)", line)
            if namespace:
                scopes.append(namespace[1])
            elif re.match(r"\s*section\b", line):
                scopes.append("")
            elif re.match(r"\s*end(?:\s|$)", line):
                if scopes:
                    scopes.pop()
            declaration = re.match(r"\s*(?:@\[[^\]]*\]\s*)*(?:(?:private|protected)\s+)*theorem\s+([\w'.]+)", line)
            if declaration:
                name = ".".join([s for s in scopes if s] + [declaration[1]])
                actual.add(name.removeprefix("_root_."))
    return actual, sources


# The audit manifests: the trusted VE tree's (hash-frozen) and the response-shape theorems'
# (lib ResponseShape, outside the trusted tree). Every theorem of every source is in exactly one.
MANIFESTS = ("VE/Audit.lean", "ResponseShape/Audit.lean")


def unwrapped(output):
    """The lines of `#print axioms` output, a long one that Lean wrapped joined back."""
    lines = []
    for line in output.splitlines():
        if line.startswith(" ") and lines:
            lines[-1] += line
        else:
            lines.append(line)
    return lines


def recorded_in(manifest):
    return set(re.findall(r"^#print axioms (\S+)", code_only((ROOT / manifest).read_text()), re.M))


def main():
    actual, sources = scan_sources(ROOT)
    recorded = [recorded_in(manifest) for manifest in MANIFESTS]
    assert not set.intersection(*recorded), {"listed twice": set.intersection(*recorded)}
    assert actual == set.union(*recorded), {"missing": actual - set.union(*recorded),
                                           "extra": set.union(*recorded) - actual}
    seen = set()
    for manifest in MANIFESTS:
        result = subprocess.run(["lake", "env", "lean", manifest], cwd=ROOT,
                                text=True, capture_output=True, check=True)
        for line in unwrapped(result.stdout):
            match = re.fullmatch(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[(.*)\])", line)
            if not match:
                raise AssertionError(f"Unexpected audit output: {line}")
            name, _, dependencies = match.groups()
            seen.add(name)
            axioms = set(dependencies.split(", ")) if dependencies else set()
            assert axioms <= ALLOWED, (name, axioms - ALLOWED)
        print(result.stdout, end="")
    assert seen == actual
    print(f"PASS: {len(sources)} source files; {len(seen)} named theorem declarations audited "
          "(headline results and helper lemmas); only the declared standard axiom allowlist.")


if __name__ == "__main__":
    main()
