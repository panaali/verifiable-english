"""Audit every project Lean source and every named theorem's dependencies.

The pinned toolchain/build cache under .lake is trusted, not project source.
This is a source/dependency policy check, not an untrusted-code sandbox.

The theorems are the compiled environment's: every constant that `declarations.txt` (written by
tools/lean_statements.py) records with kind `theorem` and a source range, a Prop-class instance included.
The two audit manifests are generated from that list: a module of `ResponseShape` declares a theorem of
`ResponseShapeAudit.lean`, every other module one of `VE/Audit.lean`; each manifest imports exactly the
declaring modules and runs `#print axioms` on every theorem, sorted by name. The list must have been
compiled from the current sources: a module whose SHA-256 differs from the one it records (the manifests
excepted, which are its outputs), or that it does not record, fails the audit.

The audit output of every manifest, in order, is the committed record `axioms.txt`; the audit fails when a
manifest or the record differs from the regenerated one, so a new theorem cannot leave either stale.
`python3 lean/audit.py --write` regenerates both manifests and the record; `--check` (the default) compares.
With `--check` or `--write` named, the `#print axioms` output of an earlier run on the same inputs is replayed
(tools/lean_dump_cache.py, `VE_RUN_CACHE=off` turns it off); every check above runs on it as on a fresh one.
The plain `python3 lean/audit.py` (the gate's) always runs Lean.
"""
from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
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
# They and the record are train-only files: read through `inventory_path`, written by `write_inventory`
# (tools/lean_statements.py), by their repository names.
MANIFESTS = ("VE/Audit.lean", "ResponseShapeAudit.lean")
HEADER = "-- generated by `lean/audit.py --write`; do not edit\n"
SCOPE = dict(zip(MANIFESTS, ("every theorem of lean/declarations.txt outside the ResponseShape modules",
                             "every theorem of lean/declarations.txt in a ResponseShape module")))
# Theorems per `lean` run. Parts run with a bounded pool: each imports about 1.4 GB.
PART = 400


def _lean_statements():
    """tools/lean_statements.py, the owner of `declarations.txt`'s format and of the source hash."""
    tools = str(Path(__file__).resolve().parents[1] / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import lean_statements
    return lean_statements


def _dump_cache():
    """tools/lean_dump_cache.py, which replays the `#print axioms` output of an earlier run on the same inputs."""
    _lean_statements()
    import lean_dump_cache
    return lean_dump_cache


def manifest_of(module):
    return MANIFESTS[1] if module == "ResponseShape" or module.startswith("ResponseShape.") else MANIFESTS[0]


def declared_theorems(root, sources):
    """{manifest: {theorem name: declaring module}} from the copy of `declarations.txt` that was compiled from
    the sources of `root` (`inventory_path`: every module but the manifests recorded once, with its current
    SHA-256), or an AssertionError naming the modules no copy describes."""
    tools = _lean_statements()
    try:
        path = tools.inventory_path(tools.DECLARATIONS, root.parent)
        declared, _ = tools.declaration_list(path)
    except tools.StaleInventory as error:
        raise AssertionError(str(error))
    except (OSError, ValueError) as error:
        raise AssertionError(f"declarations.txt cannot be read ({error}); rerun python3 tools/lean_statements.py")
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


def parts(manifest, theorems):
    """The manifest's audit split into texts of at most PART theorems each (in name order), each importing the
    modules that declare its theorems: `#print axioms` prints each theorem alone, so the parts' outputs, in order,
    are the manifest's."""
    names = sorted(theorems)
    return [manifest_text(manifest, {name: theorems[name] for name in names[start:start + PART]})
            for start in range(0, len(names), PART)]


def unwrapped(output):
    """The lines of `#print axioms` output, a long one that Lean wrapped joined back."""
    lines = []
    for line in output.splitlines():
        if line.startswith(" ") and lines:
            lines[-1] += line
        else:
            lines.append(line)
    return lines


def recorded_in(path):
    return set(re.findall(r"^#print axioms (\S+)", code_only(path.read_text()), re.M))


def record_name():
    """The axiom record's repository name: the manifests' entry's one file that is no manifest."""
    tools = _lean_statements()
    return next(name for name in tools.regen_generated.entry_named("lean-audit-manifests").paths
                if name.removeprefix("lean/") not in MANIFESTS)


def recorded_names(text):
    """The theorem names of an audit record such as `axioms.txt`."""
    return re.findall(r"^'([^']+)' (?:does not depend on any axioms|depends on axioms)", text, re.M)


def axiom_outputs(imports, texts, jobs=None):
    """The `#print axioms` output of each text, in order: the modules `imports` built, then the texts elaborated at
    with bounded concurrency."""
    if imports:
        subprocess.run(["lake", "build", *imports], cwd=ROOT, text=True, capture_output=True, check=True)
    if not texts:
        return []
    budget = os.environ.get("VE_AUDIT_JOBS")
    budget = int(budget) if budget is not None else jobs
    if budget is None:
        budget = max(1, (os.cpu_count() or 1) // 4)
    if budget < 1:
        raise ValueError("audit jobs must be positive")
    with tempfile.TemporaryDirectory(prefix="ve-audit-") as scratch:
        files = [Path(scratch) / f"Part{index}.lean" for index in range(len(texts))]
        for file, text in zip(files, texts):
            file.write_text(text, encoding="utf-8")
        with ThreadPoolExecutor(max_workers=min(len(files), budget)) as pool:
            results = list(pool.map(lambda file: subprocess.run(["lake", "env", "lean", str(file)], cwd=ROOT,
                                                                text=True, capture_output=True, check=True),
                                    files))
    return [result.stdout for result in results]


def main(argv=(), cache=False):
    parser = argparse.ArgumentParser(allow_abbrev=False)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    parser.add_argument("--jobs", type=int, help="maximum concurrent Lean parts (VE_AUDIT_JOBS overrides)")
    args = parser.parse_args(list(argv))
    if args.jobs is not None and args.jobs < 1:
        parser.error("--jobs must be positive")
    write = args.write
    sources = scan_sources(ROOT)
    theorems = declared_theorems(ROOT, sources)
    actual = {name for names in theorems.values() for name in names}
    tools, inputs = _lean_statements(), None
    if write:
        inputs = tools.lean_inputs(ROOT.parent)
    for manifest in MANIFESTS:
        text = manifest_text(manifest, theorems[manifest])
        if write:
            tools.write_inventory(f"lean/{manifest}", text, ROOT.parent, inputs)
            continue
        try:
            path = tools.inventory_path(f"lean/{manifest}", ROOT.parent)
        except tools.StaleInventory as error:
            raise AssertionError(str(error))
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            listed = recorded_in(path) if path.is_file() else set()
            raise AssertionError(f"{manifest} is stale: missing {sorted(set(theorems[manifest]) - listed)[:10]}, "
                                 f"extra {sorted(listed - set(theorems[manifest]))[:10]}; "
                                 "regenerate with python3 lean/audit.py --write")
    # Each manifest's imports, built by `axiom_outputs`: a module no default target imports has no object file
    # until named.
    imports = sorted({module for names in theorems.values() for module in names.values()})
    # The manifests' parts, elaborated at once and read in manifest order.
    texts = [text for manifest in MANIFESTS for text in parts(manifest, theorems[manifest])]
    if cache:
        dump_cache = _dump_cache()
        outputs = dump_cache.cached(dump_cache.AUDIT, ROOT.parent, lambda: _lean_statements().sources(ROOT.parent),
                                    lambda: axiom_outputs(imports, texts, args.jobs), count=len(texts),
                                    files=(tools.inventory_path(tools.DECLARATIONS, ROOT.parent)
                                           .relative_to(ROOT.parent).as_posix(),),
                                    values={"texts": hashlib.sha256(json.dumps(texts).encode()).hexdigest()})
    else:
        outputs = axiom_outputs(imports, texts, args.jobs)
    seen, output = set(), ""
    for stdout in outputs:
        for line in unwrapped(stdout):
            match = re.fullmatch(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[(.*)\])", line)
            if not match:
                raise AssertionError(f"Unexpected audit output: {line}")
            name, _, dependencies = match.groups()
            seen.add(name)
            axioms = set(dependencies.split(", ")) if dependencies else set()
            assert axioms <= ALLOWED, (name, axioms - ALLOWED)
        output += stdout
    assert seen == actual
    print(output, end="")
    if write:
        tools.write_inventory(record_name(), output, ROOT.parent, inputs)
    else:
        try:
            record = tools.inventory_path(record_name(), ROOT.parent).read_text()
        except tools.StaleInventory as error:
            raise AssertionError(str(error))
        if record != output:
            raise AssertionError(f"axioms.txt is stale: {len(recorded_names(record))} entries, "
                                 f"{len(seen)} audited; regenerate with python3 lean/audit.py --write")
    print(f"PASS: {len(sources)} source files; {len(seen)} named theorem declarations audited "
          "(headline results and helper lemmas); only the declared standard axiom allowlist.")


def cached_mode(argv):
    """Whether a command line may replay an earlier run's Lean output for the same inputs (tools/lean_dump_cache.py):
    the explicit modes, the regeneration's (tools/regen_generated.py); the plain run, the gate's, always runs Lean."""
    return list(argv) in (["--check"], ["--write"])


if __name__ == "__main__":
    main(sys.argv[1:], cache=cached_mode(sys.argv[1:]))
