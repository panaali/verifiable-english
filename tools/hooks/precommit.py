"""Fast pre-commit checks over STAGED content only; see tools/hooks/README.md.

Every check reads blobs from the index (GIT_INDEX_FILE is honoured) with
`git cat-file`, which applies no attributes, filters or diff drivers; nothing
reads the working tree. The policy code the checks reuse (tools/layer_policy.py,
tools/check_lean_imports.py, tools/check_rust_deps.py, lean/audit.py) and the
module layout it resolves imports against are the STAGED versions too, loaded
from a snapshot of the index. No check runs tests or builds; staged Lean headers
are cross-checked with the pinned toolchain's `lean --deps` when it is
installed. The gate re-runs
only the Lean audit and (through the tests) the frozen-source check; secrets and
layer imports have no later check (see the README's bypass section).
"""
from __future__ import annotations

import ast
import contextlib
import functools
import hashlib
import importlib
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
from types import SimpleNamespace
from typing import NamedTuple

PYTHON_LEDGER = "tools/layer-exceptions.json"
LEAN_LEDGER = "tools/lean-layer-exceptions.json"
INVENTORY = "lean/VE/Route/frozen-sources.sha256"
FROZEN_SCRIPT = "lean/VE/Route/frozen.py"
MAIN = "lean/Main.lean"
LEAN_TOOLCHAIN = "lean/lean-toolchain"
POLICY = {"layer_policy": "tools/layer_policy.py", "check_lean_imports": "tools/check_lean_imports.py",
          "check_rust_deps": "tools/check_rust_deps.py", "audit": "lean/audit.py"}
LAKEFILE = "lean/lakefile.toml"  # its executable roots are tool-layer entry modules
RUST_MANIFEST = re.compile(r"rust/(?:.+/)?Cargo\.toml")
BLOB_MODES = {"100644", "100755", "120000"}
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
NOTES: list[str] = []  # printed with --timings


def git(*args: str, data: bytes | None = None) -> bytes:
    result = subprocess.run(["git", "-c", "core.quotePath=false", *args], input=data,
                            capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.decode(errors='replace')}")
    return result.stdout


class Change(NamedTuple):
    status: str
    old_mode: str
    mode: str
    old_blob: str
    blob: str


class Index:
    """Staged changes against HEAD, with blob access through one cat-file process.

    `snapshot` is a scratch directory that receives the staged policy code and
    module layout on first use of `policy()`.
    """

    def __init__(self, snapshot: Path) -> None:
        head = subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD^{commit}"],
                              capture_output=True, text=True, check=False).stdout.strip()
        self.base = head or git("hash-object", "-t", "tree", "--stdin", data=b"").decode().strip()
        self.changed: dict[str, Change] = {}
        fields = git("diff-index", "--cached", "-z", "--no-renames", "--ignore-submodules=all",
                     self.base).split(b"\0")
        for meta, path in zip(fields[0::2], fields[1::2]):
            if meta:
                old_mode, mode, old_blob, blob, status = meta.decode().lstrip(":").split()
                self.changed[path.decode("utf-8", "replace")] = Change(status[0], old_mode, mode,
                                                                        old_blob, blob)
        self.snapshot = snapshot
        self._objects: dict[str, bytes | None] = {}
        self._listing: dict[str, str] | None = None
        self._policy: SimpleNamespace | None = None

    def staged(self, predicate=lambda path: True) -> list[str]:
        """Added or modified regular files (no deletions, symlinks or gitlinks)."""
        return sorted(path for path, change in self.changed.items()
                      if change.status != "D" and change.mode in {"100644", "100755"} and predicate(path))

    def listing(self) -> dict[str, str]:
        """Every index path with its blob id."""
        if self._listing is None:
            self._listing = {}
            for row in git("ls-files", "-s", "-z").split(b"\0"):
                if row:
                    meta, path = row.split(b"\t", 1)
                    self._listing[path.decode("utf-8", "replace")] = meta.split()[1].decode()
        return self._listing

    def objects(self, ids: list[str]) -> dict[str, bytes | None]:
        """Raw object contents by id (no attributes or filters); one batch process for all misses."""
        missing = list(dict.fromkeys(i for i in ids if i not in self._objects))
        if missing:
            out = git("cat-file", "--batch", data="".join(f"{i}\n" for i in missing).encode())
            offset = 0
            for object_id in missing:
                end = out.index(b"\n", offset)
                header = out[offset:end].split()
                if header[-1] == b"missing":
                    self._objects[object_id] = None
                    offset = end + 1
                    continue
                size = int(header[2])
                self._objects[object_id] = out[end + 1:end + 1 + size]
                offset = end + 2 + size
        return {i: self._objects[i] for i in ids}

    def read(self, names: list[str]) -> dict[str, bytes | None]:
        """Staged contents by path; None for a path that is not in the index."""
        ids = {name: (self.changed[name].blob if name in self.changed and self.changed[name].status != "D"
                      else self.listing().get(name)) for name in names}
        found = self.objects([i for i in ids.values() if i is not None])
        return {name: None if i is None else found[i] for name, i in ids.items()}

    def text(self, name: str) -> str | None:
        blob = self.read([name])[name]
        return None if blob is None else blob.decode("utf-8", "replace")

    def policy(self) -> SimpleNamespace:
        """Load the staged policy modules from a snapshot of the index.

        The snapshot holds the policy code, `ve/__init__.py`, the Lake and Rust
        manifests, every staged directory and an empty stand-in for every other staged `.py`
        path, so module resolution (`layer_policy.python_imports` tests file and
        directory existence) sees the staged tree, never the working tree.
        """
        if self._policy is None:
            listing = self.listing()
            real = [*POLICY.values(), LAKEFILE, "ve/__init__.py",
                    *(p for p in listing if RUST_MANIFEST.fullmatch(p))]
            blobs = self.read(real)
            for path, blob in blobs.items():
                if blob is None and path in {*POLICY.values(), LAKEFILE}:
                    raise RuntimeError(f"policy file {path} is missing from the index")
            for folder in {PurePosixPath(p).parent for p in listing}:
                (self.snapshot / folder).mkdir(parents=True, exist_ok=True)
            for path in [p for p in listing if p.endswith(".py")] + real:
                target = self.snapshot / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(blobs.get(path) or b"")
            sys.dont_write_bytecode = True  # the snapshot is deleted on exit
            sys.path.insert(0, str(self.snapshot / "tools"))
            modules = {name: importlib.import_module(name) for name in POLICY if name != "audit"}
            spec = importlib.util.spec_from_file_location("ve_lean_audit", self.snapshot / POLICY["audit"])
            modules["audit"] = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modules["audit"])
            for name, module in modules.items():
                if Path(module.__file__).resolve() != (self.snapshot / POLICY[name]).resolve():
                    raise RuntimeError(f"{name} did not load from the staged snapshot")
            self._policy = SimpleNamespace(**modules)
        return self._policy


def check_secrets(index: Index) -> list[str]:
    """Scan the staged blob of every added or modified file for new secrets.

    A match counts when a line it covers is not a line of the same path at HEAD
    (so edits and moves of already-committed lines stay quiet), unless one of
    those lines carries ALLOW_SECRET.
    """
    errors = []
    paths = []
    for path, change in sorted(index.changed.items()):
        if change.status == "D" or change.mode not in BLOB_MODES:
            continue
        paths.append(path)
        parts = PurePosixPath(path).parts
        if ".webapp-private" in parts:
            errors.append(f"{path}: files under .webapp-private/ must never be committed")
        elif PRIVATE_KEY_FILE.fullmatch(parts[-1]) and not PUBLIC_ENV_FILE.fullmatch(parts[-1]):
            errors.append(f"{path}: private key or environment file")
    for path, blob in index.read(paths).items():
        hits = sorted(secrets_in(blob or b""))
        if not hits:
            continue
        change = index.changed[path]
        old = index.objects([change.old_blob])[change.old_blob] if change.old_mode in BLOB_MODES else None
        old_lines = set((old or b"").split(b"\n"))
        for offset, kind, found in hits:
            start = blob.rfind(b"\n", 0, offset) + 1
            end = blob.find(b"\n", offset + len(found))
            covered = blob[start:len(blob) if end < 0 else end]
            if ALLOW_SECRET in covered or set(covered.split(b"\n")) <= old_lines:
                continue
            number = blob.count(b"\n", 0, offset) + 1
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


def module_layer(policy: SimpleNamespace, module: str) -> int | None:
    # Same mapping as tools/check_python_layers.py (which needs grimp for its full graph).
    if module == "ve_experiments" or module.startswith("ve_experiments."):
        return 5
    return policy.layer_policy.python_layer(module)


def python_targets(resolve, exports: dict[str, str], root: Path,
                   item: tuple[str, bytes]) -> set[str] | SyntaxError:
    path, source = item
    module, package = python_module(path)
    try:
        return resolve(module, source.decode("utf-8", "replace"), exports, root=root, package=package)
    except SyntaxError as error:
        return error


def mapped(func, items: list) -> list:
    """Map per-file work, forking workers only when the commit is large."""
    if len(items) < 16:
        return [func(item) for item in items]
    context = multiprocessing.get_context("fork")
    with context.Pool(min(8, os.cpu_count() or 1)) as pool:
        return pool.map(func, items, chunksize=4)


def check_layers(index: Index) -> list[str]:
    errors = []
    python = index.staged(lambda p: p.startswith("ve/") and p.endswith(".py"))
    lean = index.staged(lambda p: p.startswith("lean/") and p.endswith(".lean")
                        and ".lake" not in PurePosixPath(p).parts)
    rust = [p for p in index.changed if RUST_MANIFEST.fullmatch(p)]
    if not (python or lean or rust):
        return []
    policy = index.policy()
    layers = policy.layer_policy

    def mappable(path: str, module: str, layer: int | None, kind: str) -> bool:
        # Modules already unmapped at HEAD are the full checker's (and the gate's)
        # business; the hook only rejects a commit that ADDS an unmapped module.
        if layer is None and index.changed[path].status == "A" and module != "ve":
            errors.append(f"{path}: unmapped {kind} module {module} (add it to tools/layer_policy.py)")
        return layer is not None

    python = [p for p in python if mappable(p, python_module(p)[0],
                                            module_layer(policy, python_module(p)[0]), "Python")]
    headers = lean  # every staged header must be plain, mapped module or not
    lean = {p for p in lean if mappable(p, lean_module(p), layers.lean_layer(lean_module(p)), "Lean")}
    if python:
        blobs = index.read([PYTHON_LEDGER, *python])
        ledger = json.loads(blobs[PYTHON_LEDGER] or b"{}")
        exports = layers.python_exports(index.snapshot)
        targets = functools.partial(python_targets, layers.python_imports, exports, index.snapshot)
        found = mapped(targets, [(path, blobs[path]) for path in python])
        for path, targets in zip(python, found):
            module = python_module(path)[0]
            importer = module_layer(policy, module)
            if isinstance(targets, SyntaxError):
                errors.append(f"{path}:{targets.lineno}: cannot parse imports: {targets.msg}")
                continue
            for target in sorted(targets):
                edge = f"{module} -> {target}"
                layer = module_layer(policy, target)
                if layer is not None and importer < layer and edge not in ledger:
                    errors.append(f"{path}: new outward import {edge} (layer {importer} -> {layer})")
    if headers:
        reader = policy.check_lean_imports
        blobs = index.read([LEAN_LEDGER, LEAN_TOOLCHAIN, *headers])
        ledger = json.loads(blobs[LEAN_LEDGER] or b"{}")
        local = {lean_module(p) for p in index.listing() if p.startswith("lean/") and p.endswith(".lean")}
        read = {}
        for path in headers:
            try:
                read[path] = reader.imports(blobs[path].decode("utf-8", "replace"))
            except reader.HeaderError as error:
                errors.append(f"{path}: Lean header {error}")
        # The pinned toolchain's own header parser must agree with the plain-layout reading.
        command = reader.pinned_lean((blobs[LEAN_TOOLCHAIN] or b"").decode()) if read else None
        if command is None:
            NOTES.append("lean --deps: pinned toolchain unavailable; plain-layout grammar only")
        else:
            folder = Path(tempfile.mkdtemp(prefix="lean-headers-", dir=index.snapshot))
            files = {}
            for number, path in enumerate(read):
                files[path] = (folder / f"{number}.lean", read[path])
                files[path][0].write_bytes(blobs[path])
            wrong, checked = reader.lean_disagreements(command, files)
            NOTES.append(f"lean --deps confirmed or refuted {checked} of {len(files)} staged Lean headers")
            for path, message in sorted(wrong.items()):
                errors.append(f"{path}: Lean header: {message}; {reader.PLAIN_LAYOUT}")
                del read[path]
        for path, targets in read.items():
            if path not in lean:
                continue
            module = lean_module(path)
            importer = layers.lean_layer(module)
            for target in targets:
                if target not in local:
                    if target.startswith("VE.") or target in {"VE", "Iceberg"}:
                        errors.append(f"{path}: missing local Lean import {target}")
                    continue
                edge = f"{module} -> {target}"
                layer = layers.lean_layer(target)
                if layer is not None and importer < layer and edge not in ledger:
                    errors.append(f"{path}: new outward Lean import {edge} (layer {importer} -> {layer})")
    if rust:
        # The snapshot already holds every staged manifest under its rust/ workspace.
        stderr = io.StringIO()
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
                failed = policy.check_rust_deps.main()
        except (OSError, KeyError, ValueError) as error:
            failed, stderr = 1, io.StringIO(f"cannot read the staged Rust workspace: {error}\n")
        if failed:
            errors.extend(f"rust: {line}" for line in stderr.getvalue().splitlines())
    return errors


def check_lean_tokens(index: Index) -> list[str]:
    errors = []
    paths = index.staged(lambda p: p.endswith(".lean") and ".lake" not in PurePosixPath(p).parts)
    if not paths:
        return []
    audit = index.policy().audit
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


def check_wire_contract(index: Index) -> list[str]:
    """Run the wire generator on staged sources and generated output."""
    watched = ("ve/wire_contract/", "ve/softnorms_contract.py", "ve/softnorms.py",
               "ve/wire.py", "tools/wire_contract.py", "tools/wire_contract_lean.py",
               "docs/spec/soft-norms-wire-table.md", "lean/VE/WireContract/",
               "lean/VE/Route/frozen-sources.sha256", "conformance/wire-contract/contracts/",
               "conformance/wire-contract/soft-norms@0-catalogue.json")
    if not any(path.startswith(watched) for path in index.changed):
        return []
    names = [path for path in index.listing()
             if path.startswith(("ve/", "conformance/wire-contract/contracts/",
                                 "lean/VE/WireContract/")) or path in {
                 "lean/audit.py", "tools/wire_contract.py", "tools/wire_contract_lean.py",
                 "lean/VE/Route/frozen-sources.sha256",
                 "docs/spec/soft-norms-wire-table.md",
                 "conformance/wire-contract/soft-norms@0-catalogue.json",
                 "conformance/wire-contract/engine-golden.json"}]
    for path, blob in index.read(names).items():
        if blob is None:
            continue
        target = index.snapshot / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
    env = {**os.environ, "PYTHONPATH": str(index.snapshot), "PYTHONDONTWRITEBYTECODE": "1"}
    done = subprocess.run([sys.executable, "tools/wire_contract.py", "--check"],
                          cwd=index.snapshot, env=env, capture_output=True, text=True,
                          timeout=30, check=False)
    if done.returncode:
        return [line for line in (done.stdout + done.stderr).splitlines() if line]
    return []


CHECKS = [("secrets", check_secrets), ("layer imports", check_layers),
          ("Lean forbidden tokens", check_lean_tokens), ("frozen files", check_frozen),
          ("wire contract", check_wire_contract)]


def main(argv: list[str]) -> int:
    started = time.perf_counter()
    os.chdir(git("rev-parse", "--show-toplevel").decode().strip())  # ls-files paths are cwd-relative
    with tempfile.TemporaryDirectory(prefix="ve-precommit-") as snapshot:
        index = Index(Path(snapshot))
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
        for note in NOTES:
            print(f"pre-commit: {note}", file=sys.stderr)
        print(f"pre-commit: total {time.perf_counter() - started:.3f} s "
              f"({len(index.changed)} staged paths)", file=sys.stderr)
    if failed:
        print("pre-commit: commit rejected. Fix the findings above; see tools/hooks/README.md for "
              "the emergency bypass (git commit --no-verify or VE_SKIP_HOOKS=1).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
