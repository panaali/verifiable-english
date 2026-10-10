"""Audit every project Lean source and every named theorem's dependencies.

The pinned toolchain/build cache under .lake is trusted, not project source.
This is a source/dependency policy check, not an untrusted-code sandbox.

The theorems are the compiled environment's: every constant that `declarations.txt` (written by
tools/lean_statements.py) records with kind `theorem` and a source range, a Prop-class instance included.
The two audit manifests are generated from that list: a module of `ResponseShape` declares a theorem of
`ResponseShape/Audit.lean`, every other module one of `VE/Audit.lean`; each manifest imports exactly the
declaring modules and runs `#print axioms` on every theorem, sorted by name. The list must have been
compiled from the current sources: a module whose SHA-256 differs from the one it records (the manifests
excepted, which are its outputs), or that it does not record, fails the audit.

The audit output of every manifest, in order, is the committed record `axioms.txt`; the audit fails when a
manifest or the record differs from the regenerated one, so a new theorem cannot leave either stale.
`python3 lean/audit.py --write` regenerates both manifests and the record; `--check` (the default) compares.
"""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
RECORD = ROOT / "axioms.txt"
DECLARATIONS = "declarations.txt"
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}
FORBIDDEN = re.compile(r"\b(sorry|sorryAx|axiom|unsafe|native_decide|implemented_by|partial|opaque|extern)\b")
# S3 names its admission function `admit`. A bare occurrence in tactic syntax is a
# hole, while `def admit`, `unfold admit` and `admit E ...` name/apply the function.
# Check token boundaries rather than a line prefix: bullets, `=>` and `<;>` can
# precede the tactic on the same line.
ADMIT_TOKEN = re.compile(r"(?<![\w'])admit(?![\w'])")
ADMIT_CONTEXT = re.compile(r"(?:\bby|=>|<;>|\bdecreasing_by|[·;])\s*$")


def admit_tactic(code):
    for match in ADMIT_TOKEN.finditer(code):
        before, after = code[:match.start()], code[match.end():]
        prefix = before.splitlines()[-1] if before else ""
        if re.search(r"\b(?:def|unfold)\s+$", prefix):
            continue
        if ADMIT_CONTEXT.search(prefix):
            return match
        # A function application has an argument on the same line. A bare
        # occurrence also includes `admit; ...` and `admit` before a closer.
        if not re.match(r"[ \t]+(?:[\w'(]|\.[A-Za-z])", after):
            return match
    return None


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
    """The project Lean sources under `root`, after the forbidden-word and admit-tactic scans."""
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
        tactic = admit_tactic(code)
        if tactic:
            line = code.count("\n", 0, tactic.start()) + 1
            raise AssertionError(f"{source.relative_to(root)}:{line}: forbidden admit tactic")
    return sources


# The audit manifests: the trusted VE tree's (hash-frozen) and the response-shape theorems'
# (lib ResponseShape, outside the trusted tree). Every theorem of every source is in exactly one.
MANIFESTS = ("VE/Audit.lean", "ResponseShape/Audit.lean")
HEADER = "-- generated by `lean/audit.py --write`; do not edit\n"
SCOPE = {"VE/Audit.lean": "every theorem of lean/declarations.txt outside the ResponseShape modules",
         "ResponseShape/Audit.lean": "every theorem of lean/declarations.txt in a ResponseShape module"}


def _lean_statements():
    """tools/lean_statements.py, the owner of `declarations.txt`'s format and of the source hash."""
    tools = str(Path(__file__).resolve().parents[1] / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import lean_statements
    return lean_statements


def manifest_of(module):
    return MANIFESTS[1] if module == "ResponseShape" or module.startswith("ResponseShape.") else MANIFESTS[0]


def declared_theorems(root, sources):
    """{manifest: {theorem name: declaring module}} from `declarations.txt`, after checking that it was
    compiled from `sources`: every module but the manifests recorded once, with its current SHA-256."""
    tools = _lean_statements()
    path = root / DECLARATIONS
    try:
        declared, hashes = tools.declaration_list(path)
    except (OSError, ValueError) as error:
        raise AssertionError(f"{path.name} cannot be read ({error}); rerun python3 tools/lean_statements.py")
    outputs = {tools.module_name(manifest) for manifest in MANIFESTS}
    current = {tools.module_name(p.relative_to(root).as_posix()): p for p in sources}
    stale = sorted(m for m in (current.keys() | hashes.keys()) - outputs
                   if m not in current or m not in hashes or tools.source_hash(current[m]) != hashes[m])
    if stale:
        raise AssertionError(f"{path.name} is stale: {len(stale)} modules differ from the sources it was compiled "
                             f"from ({', '.join(stale[:5])}); rerun python3 tools/lean_statements.py")
    return manifest_theorems(declared)


def manifest_theorems(declared):
    """{manifest: {theorem name: declaring module}}: every constant of `declared` ({module: [Declared]}, as
    tools/lean_statements.py reads `declarations.txt`) of kind `theorem` with a source range."""
    found = {manifest: {} for manifest in MANIFESTS}
    for module, constants in declared.items():
        for constant in constants:
            if constant.kind != "theorem" or constant.start is None:
                continue
            if any(constant.name in names for names in found.values()):
                raise AssertionError(f"theorem {constant.name} is declared by two modules; "
                                     "`#print axioms` cannot tell them apart")
            found[manifest_of(module)][constant.name] = module
    return found


def manifest_text(manifest, theorems):
    """The generated manifest: the header, an import per declaring module and a `#print axioms` per theorem."""
    imports = "".join(f"import {module}\n" for module in sorted(set(theorems.values())))
    body = "".join(f"#print axioms {name}\n" for name in sorted(theorems))
    return f"{HEADER}-- The `#print axioms` audit of {SCOPE[manifest]}.\n{imports}\n{body}"


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


def recorded_names(text):
    """The theorem names of an audit record such as `axioms.txt`."""
    return re.findall(r"^'([^']+)' (?:does not depend on any axioms|depends on axioms)", text, re.M)


def main(argv=()):
    if list(argv) not in ([], ["--check"], ["--write"]):
        raise SystemExit("usage: python3 lean/audit.py [--check | --write]")
    write = list(argv) == ["--write"]
    sources = scan_sources(ROOT)
    theorems = declared_theorems(ROOT, sources)
    actual = {name for names in theorems.values() for name in names}
    for manifest in MANIFESTS:
        path, text = ROOT / manifest, manifest_text(manifest, theorems[manifest])
        if write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        elif not path.is_file() or path.read_text(encoding="utf-8") != text:
            listed = recorded_in(manifest) if path.is_file() else set()
            raise AssertionError(f"{manifest} is stale: missing {sorted(set(theorems[manifest]) - listed)[:10]}, "
                                 f"extra {sorted(listed - set(theorems[manifest]))[:10]}; "
                                 "regenerate with python3 lean/audit.py --write")
    # Each manifest's imports, built: a module no default target imports has no object file until named.
    imports = sorted({module for names in theorems.values() for module in names.values()})
    if imports:
        subprocess.run(["lake", "build", *imports], cwd=ROOT, text=True, capture_output=True, check=True)
    seen, output = set(), ""
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
        output += result.stdout
    assert seen == actual
    print(output, end="")
    if write:
        RECORD.write_text(output)
    elif RECORD.read_text() != output:
        raise AssertionError(f"{RECORD.name} is stale: {len(recorded_names(RECORD.read_text()))} entries, "
                             f"{len(seen)} audited; regenerate with python3 lean/audit.py --write")
    print(f"PASS: {len(sources)} source files; {len(seen)} theorems of the compiled environment audited "
          f"({', '.join(f'{len(theorems[m])} in {m}' for m in MANIFESTS)}); "
          "only the declared standard axiom allowlist.")


if __name__ == "__main__":
    main(sys.argv[1:])
