"""Fast pre-commit checks over STAGED content only; see tools/hooks/README.md.

Every check reads blobs from the index (GIT_INDEX_FILE is honoured), never the
working tree, and no check runs tests or builds. The full checkers still run in
the gate: this hook only rejects the cheap-to-detect mistakes early.
"""
from __future__ import annotations

import ast
import bisect
import codecs
import contextlib
import hashlib
import importlib.util
import io
import json
import multiprocessing
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from check_lean_imports import imports as lean_imports  # noqa: E402
import check_rust_deps  # noqa: E402
from layer_policy import lean_layer, python_exports, python_imports, python_layer  # noqa: E402


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


audit = _load("ve_lean_audit", ROOT / "lean/audit.py")

PYTHON_LEDGER = "tools/layer-exceptions.json"
LEAN_LEDGER = "tools/lean-layer-exceptions.json"
INVENTORY = "lean/VE/Route/frozen-sources.sha256"
FROZEN_SCRIPT = "lean/VE/Route/frozen.py"
MAIN = "lean/Main.lean"
ALLOW_SECRET = b"pragma: allowlist secret"

ASSIGNED = rb"\b[\"']?\s*[:=]\s*[\"'](?=[a-z0-9/+_.-]*\d)(?=[a-z0-9/+_.-]*[a-z])[a-z0-9/+_.-]{24,}[\"']"
# (kind, bytes pattern, needs a word boundary before the match, match the ASCII-
# lowercased text). Every pattern starts with a literal so the regex engine can
# skip ahead; a leading \b or (?i) disables that and is about 20x slower, so the
# boundary is checked by hand and case-insensitive keys match lowercased bytes.
SECRETS = [(kind, re.compile(pattern), bounded, folded) for kind, pattern, bounded, folded in [
    ("private key block", rb"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY(?: BLOCK)?-----", False, False),
    ("AWS access key id", rb"AKIA[0-9A-Z]{16}\b", True, False),
    ("AWS access key id", rb"ASIA[0-9A-Z]{16}\b", True, False),
    ("GitHub token", rb"gh[pousr]_[A-Za-z0-9]{36,}\b", True, False),
    ("GitHub token", rb"github_pat_[A-Za-z0-9_]{40,}", True, False),
    ("Anthropic API key", rb"sk-ant-[A-Za-z0-9_-]{20,}", True, False),
    ("OpenAI API key", rb"sk-(?!ant-)(?:proj-|svcacct-|admin-)?[A-Za-z0-9_-]{32,}", True, False),
    ("Google API key", rb"AIza[0-9A-Za-z_-]{35}\b", True, False),
    ("Google OAuth client secret", rb"GOCSPX-[A-Za-z0-9_-]{28}\b", True, False),
    ("Slack token", rb"xox[abposr]-[A-Za-z0-9-]{10,}", True, False),
    ("Hugging Face token", rb"hf_[A-Za-z0-9]{34,}\b", True, False),
    ("Stripe live key", rb"sk_live_[A-Za-z0-9]{20,}", True, False),
    ("Stripe live key", rb"rk_live_[A-Za-z0-9]{20,}", True, False),
    *(("credential assignment", key + ASSIGNED, True, True)
      for key in (rb"api[_-]?key", rb"secret[_-]?key", rb"client[_-]?secret",
                  rb"access[_-]?token", rb"auth[_-]?token", rb"password")),
]]


def secrets_in(text: bytes):
    """Yield (offset, kind, matched bytes) for every secret-shaped match."""
    folded_text = text.lower()  # ASCII-only, so offsets are unchanged
    for kind, pattern, bounded, folded in SECRETS:
        for match in pattern.finditer(folded_text if folded else text):
            start = match.start()
            before = text[start - 1:start]
            if not (bounded and (before.isalnum() or before == b"_")):
                yield start, kind, text[start:match.end()]
PRIVATE_KEY_FILE = re.compile(r"id_(?:rsa|dsa|ecdsa|ed25519)|.*\.(?:p12|pfx)|\.env(?:\..+)?")
PUBLIC_ENV_FILE = re.compile(r"\.env\.(?:example|sample|template)")
CORE_LEAN = re.compile(r"\b(sorry|sorryAx|admit|axiom)\b")


def git(*args: str, data: bytes | None = None) -> bytes:
    result = subprocess.run(["git", "-c", "core.quotePath=false", *args], input=data,
                            capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.decode(errors='replace')}")
    return result.stdout


def unquote(path: bytes) -> str:
    """Undo git's C-style path quoting."""
    if path.startswith(b'"') and path.endswith(b'"'):
        path = codecs.escape_decode(path[1:-1])[0]
    return path.decode("utf-8", "replace")


class Index:
    """Staged changes against HEAD, with blob access through one cat-file process."""

    def __init__(self) -> None:
        head = subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD^{commit}"],
                              capture_output=True, text=True, check=False).stdout.strip()
        self.base = head or git("hash-object", "-t", "tree", "--stdin", data=b"").decode().strip()
        self.changed: dict[str, tuple[str, str, str]] = {}  # path -> (status, mode, blob)
        fields = git("diff-index", "--cached", "-z", "--no-renames", "--ignore-submodules=all",
                     self.base).split(b"\0")
        for meta, path in zip(fields[0::2], fields[1::2]):
            if meta:
                _, mode, _, blob, status = meta.decode().lstrip(":").split()
                self.changed[path.decode("utf-8", "replace")] = (status[0], mode, blob)
        self._blobs: dict[str, bytes | None] = {}
        self._listing: dict[str, str] | None = None

    def staged(self, predicate=lambda path: True) -> list[str]:
        """Added or modified regular files (no deletions, symlinks or gitlinks)."""
        return sorted(path for path, (status, mode, _) in self.changed.items()
                      if status != "D" and mode in {"100644", "100755"} and predicate(path))

    def listing(self) -> dict[str, str]:
        """Every index path with its blob id."""
        if self._listing is None:
            self._listing = {}
            for row in git("ls-files", "-s", "-z").split(b"\0"):
                if row:
                    meta, path = row.split(b"\t", 1)
                    self._listing[path.decode("utf-8", "replace")] = meta.split()[1].decode()
        return self._listing

    def read(self, names: list[str]) -> dict[str, bytes | None]:
        """Read staged paths (`path`) or objects; one batch process for all misses."""
        specs = {name: (self.changed[name][2] if name in self.changed else f":{name}")
                 for name in names if name not in self._blobs}
        if specs:
            out = git("cat-file", "--batch", data="".join(f"{spec}\n" for spec in specs.values()).encode())
            offset = 0
            for name in specs:
                end = out.index(b"\n", offset)
                header = out[offset:end].split()
                if header[-1] == b"missing":
                    self._blobs[name] = None
                    offset = end + 1
                    continue
                size = int(header[2])
                self._blobs[name] = out[end + 1:end + 1 + size]
                offset = end + 2 + size
        return {name: self._blobs[name] for name in names}

    def text(self, name: str) -> str | None:
        blob = self.read([name])[name]
        return None if blob is None else blob.decode("utf-8", "replace")


def added_lines(index: Index) -> dict[str, list[tuple[int, str]]]:
    """Map each staged text file to its added lines (1-based numbers in the new file)."""
    patch = git("diff", "--cached", "-U0", "--no-color", "--no-ext-diff", "--no-textconv",
                "--no-renames", "--ignore-submodules=all", "--src-prefix=a/", "--dst-prefix=b/",
                index.base)
    files: dict[str, list[tuple[int, bytes]]] = {}
    current = None
    old_left = new_left = 0
    number = 0
    hunk = re.compile(rb"^@@ -\d+(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
    for line in patch.split(b"\n"):
        if old_left > 0 or new_left > 0:
            tag = line[:1]
            if tag == b"+":
                if current is not None:
                    files[current].append((number, line[1:]))
                number += 1
                new_left -= 1
            elif tag == b"-":
                old_left -= 1
            elif tag == b" ":
                number += 1
                old_left -= 1
                new_left -= 1
            continue  # "\ No newline at end of file" lines carry no content
        if line.startswith(b"+++ "):
            name = unquote(line[4:])
            current = name[2:] if name.startswith("b/") else None
            if current is not None:
                files.setdefault(current, [])
        elif (match := hunk.match(line)):
            old_left = int(match[1]) if match[1] is not None else 1
            number = int(match[2])
            new_left = int(match[3]) if match[3] is not None else 1
    return files


def check_secrets(index: Index) -> list[str]:
    errors = []
    for path, (status, _, _) in sorted(index.changed.items()):
        if status == "D":
            continue
        parts = PurePosixPath(path).parts
        if ".webapp-private" in parts:
            errors.append(f"{path}: files under .webapp-private/ must never be committed")
        elif PRIVATE_KEY_FILE.fullmatch(parts[-1]) and not PUBLIC_ENV_FILE.fullmatch(parts[-1]):
            errors.append(f"{path}: private key or environment file")
    for path, lines in added_lines(index).items():
        text = b"\n".join(line for _, line in lines)
        starts = []
        offset = 0
        for _, line in lines:
            starts.append(offset)
            offset += len(line) + 1
        for offset, kind, found in sorted(secrets_in(text)):
            number, line = lines[bisect.bisect_right(starts, offset) - 1]
            if ALLOW_SECRET not in line:
                # Echo only a short prefix: hook output lands in terminals and agent transcripts.
                errors.append(f"{path}:{number}: possible {kind} ({found[:4].decode(errors='replace')}...)")
    return errors


def python_module(path: str) -> tuple[str, bool]:
    p = PurePosixPath(path)
    if p.name == "__init__.py":
        return ".".join(p.parent.parts), True
    return ".".join(p.with_suffix("").parts), False


def lean_module(path: str) -> str:
    return ".".join(PurePosixPath(path).with_suffix("").parts[1:])


def module_layer(module: str) -> int | None:
    # Same mapping as tools/check_python_layers.py (which needs grimp for its full graph).
    return 5 if module == "ve_experiments" or module.startswith("ve_experiments.") else python_layer(module)


def python_targets(item: tuple[str, bytes, dict[str, str]]) -> set[str] | SyntaxError:
    path, source, exports = item
    module, package = python_module(path)
    try:
        return python_imports(module, source.decode("utf-8", "replace"), exports, root=ROOT, package=package)
    except SyntaxError as error:
        return error


def lean_targets(source: bytes) -> list[str]:
    # Only the text through the last line mentioning `import` can hold an import
    # command, and the checker scans left to right, so this prefix gives the same
    # answer as the whole file at a fraction of the character-by-character cost.
    last = source.rfind(b"import")
    if last < 0:
        return []
    end = source.find(b"\n", last)
    return lean_imports(source[:len(source) if end < 0 else end].decode("utf-8", "replace"))


def mapped(func, items: list) -> list:
    """Map per-file work, forking workers only when the commit is large."""
    if len(items) < 16:
        return [func(item) for item in items]
    context = multiprocessing.get_context("fork")
    with context.Pool(min(8, os.cpu_count() or 1)) as pool:
        return pool.map(func, items, chunksize=4)


def check_layers(index: Index) -> list[str]:
    errors = []

    def mappable(path: str, module: str, layer: int | None, kind: str) -> bool:
        # Modules already unmapped at HEAD are the full checker's (and the gate's)
        # business; the hook only rejects a commit that ADDS an unmapped module.
        if layer is None and index.changed[path][0] == "A" and module != "ve":
            errors.append(f"{path}: unmapped {kind} module {module} (add it to tools/layer_policy.py)")
        return layer is not None

    python = [p for p in index.staged(lambda p: p.startswith("ve/") and p.endswith(".py"))
              if mappable(p, python_module(p)[0], module_layer(python_module(p)[0]), "Python")]
    lean = [p for p in index.staged(lambda p: p.startswith("lean/") and p.endswith(".lean")
                                    and ".lake" not in PurePosixPath(p).parts)
            if mappable(p, lean_module(p), lean_layer(lean_module(p)), "Lean")]
    rust = [p for p in index.changed if re.fullmatch(r"rust/(?:.+/)?Cargo\.toml", p)]
    if python:
        blobs = index.read([PYTHON_LEDGER, "ve/__init__.py", *python])
        ledger = json.loads(blobs[PYTHON_LEDGER] or b"{}")
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "ve").mkdir()
            (Path(tmp) / "ve/__init__.py").write_bytes(blobs["ve/__init__.py"] or b"")
            exports = python_exports(Path(tmp))
        found = mapped(python_targets, [(path, blobs[path], exports) for path in python])
        for path, targets in zip(python, found):
            module = python_module(path)[0]
            importer = module_layer(module)
            if isinstance(targets, SyntaxError):
                errors.append(f"{path}:{targets.lineno}: cannot parse imports: {targets.msg}")
                continue
            for target in sorted(targets):
                edge = f"{module} -> {target}"
                layer = module_layer(target)
                if layer is not None and importer < layer and edge not in ledger:
                    errors.append(f"{path}: new outward import {edge} (layer {importer} -> {layer})")
    if lean:
        blobs = index.read([LEAN_LEDGER, *lean])
        ledger = json.loads(blobs[LEAN_LEDGER] or b"{}")
        local = {lean_module(p) for p in index.listing() if p.startswith("lean/") and p.endswith(".lean")}
        for path, targets in zip(lean, mapped(lean_targets, [blobs[path] for path in lean])):
            module = lean_module(path)
            importer = lean_layer(module)
            for target in targets:
                if target not in local:
                    if target.startswith("VE.") or target in {"VE", "Iceberg"}:
                        errors.append(f"{path}: missing local Lean import {target}")
                    continue
                edge = f"{module} -> {target}"
                layer = lean_layer(target)
                if layer is not None and importer < layer and edge not in ledger:
                    errors.append(f"{path}: new outward Lean import {edge} (layer {importer} -> {layer})")
    if rust:
        manifests = [p for p in index.listing() if re.fullmatch(r"rust/(?:.+/)?Cargo\.toml", p)]
        with tempfile.TemporaryDirectory() as tmp:
            git("checkout-index", f"--prefix={tmp}/", "--", *manifests)
            check_rust_deps.WORKSPACE = Path(tmp) / "rust"
            stderr = io.StringIO()
            try:
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
                    failed = check_rust_deps.main()
            except (OSError, KeyError, ValueError) as error:
                failed, stderr = 1, io.StringIO(f"cannot read the staged Rust workspace: {error}\n")
            finally:
                check_rust_deps.WORKSPACE = ROOT / "rust"
        if failed:
            errors.extend(f"rust: {line}" for line in stderr.getvalue().splitlines())
    return errors


def check_lean_tokens(index: Index) -> list[str]:
    errors = []
    paths = index.staged(lambda p: p.endswith(".lean") and ".lake" not in PurePosixPath(p).parts)
    for path, blob in index.read(paths).items():
        text = blob.decode("utf-8", "replace")
        if path.startswith("lean/"):
            # lean/audit.py policy: whole words, comments and strings included.
            scanned, pattern = text, audit.FORBIDDEN
        else:
            scanned, pattern = audit.code_only(text), CORE_LEAN
        for match in pattern.finditer(scanned):
            line = scanned.count("\n", 0, match.start()) + 1
            errors.append(f"{path}:{line}: forbidden Lean token '{match[0]}'")
    return errors


def frozen_constants(source: str) -> tuple[str, tuple[str, ...]]:
    values = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in {"MAIN_BASE", "ROUTE_LINES"}:
                values[node.targets[0].id] = ast.literal_eval(node.value)
    return values["MAIN_BASE"], values["ROUTE_LINES"]


def check_frozen(index: Index) -> list[str]:
    staged = {p.removeprefix("lean/") for p in index.changed if p.startswith("lean/")}
    whole = INVENTORY in index.changed or FROZEN_SCRIPT in index.changed
    if not whole and not any(p.startswith("VE/") and p.endswith(".lean") for p in staged) \
            and MAIN not in index.changed:
        return []
    errors = []
    hint = f"rehash it in {INVENTORY} in the same commit (then python3 VE/Route/frozen.py from lean/)"
    inventory_text = index.text(INVENTORY)
    if inventory_text is None:
        return [f"{INVENTORY}: frozen-source inventory missing from the index"]
    recorded = {}
    for line in inventory_text.splitlines():
        if line.strip():
            expected, name = line.split(maxsplit=1)
            recorded[name] = expected
    trusted = {p.removeprefix("lean/") for p in index.listing()
               if p.startswith("lean/VE/") and p.endswith(".lean")}
    names = sorted(recorded if whole else recorded.keys() & staged)
    blobs = index.read([f"lean/{name}" for name in names])
    for name in names:
        blob = blobs[f"lean/{name}"]
        if blob is None:
            errors.append(f"lean/{name}: frozen file deleted but still listed; remove it from {INVENTORY}")
        elif hashlib.sha256(blob).hexdigest() != recorded[name]:
            errors.append(f"lean/{name}: frozen file changed without an inventory update; {hint}")
    for name in sorted((trusted if whole else trusted & staged) - recorded.keys()):
        errors.append(f"lean/{name}: unlisted trusted module; add its hash to {INVENTORY}")
    if whole or MAIN in index.changed:
        script = index.text(FROZEN_SCRIPT)
        text = index.text(MAIN)
        if script is None or text is None:
            errors.append(f"{MAIN}: {FROZEN_SCRIPT} or {MAIN} missing from the index")
        else:
            base, route_lines = frozen_constants(script)
            for route_line in route_lines:
                if text.count(route_line) != 1:
                    errors.append(f"{MAIN}: expected exactly one {route_line.strip()!r}")
                text = text.replace(route_line, "")
            if hashlib.sha256(text.encode()).hexdigest() != base:
                errors.append(f"{MAIN}: existing subcommands changed (hash-frozen by MAIN_BASE in "
                              f"{FROZEN_SCRIPT}; add a new lean_exe instead)")
    return errors


CHECKS = [("secrets", check_secrets), ("layer imports", check_layers),
          ("Lean forbidden tokens", check_lean_tokens), ("frozen files", check_frozen)]


def main(argv: list[str]) -> int:
    started = time.perf_counter()
    os.chdir(git("rev-parse", "--show-toplevel").decode().strip())  # ls-files paths are cwd-relative
    index = Index()
    failed = False
    for name, check in CHECKS:
        begin = time.perf_counter()
        try:
            errors = check(index)
        except Exception as error:  # a broken check must block, not pass silently
            errors = [f"internal error: {type(error).__name__}: {error}"]
        if "--timings" in argv:
            print(f"pre-commit: {name}: {time.perf_counter() - begin:.3f} s", file=sys.stderr)
        if errors:
            failed = True
            print(f"pre-commit: {name} check failed:", file=sys.stderr)
            for error in errors:
                print(f"  {error}", file=sys.stderr)
    if "--timings" in argv:
        print(f"pre-commit: total {time.perf_counter() - started:.3f} s "
              f"({len(index.changed)} staged paths)", file=sys.stderr)
    if failed:
        print("pre-commit: commit rejected. Fix the findings above; see tools/hooks/README.md for "
              "the emergency bypass (git commit --no-verify or VE_SKIP_HOOKS=1).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
