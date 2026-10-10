"""`tools/identity_lint.py` (architecture plan AR-6): no new Lean-owned identity preimage in Python."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from tools import identity_lint, relay_lint

ROOT = Path(__file__).resolve().parents[1]
# The commit the architecture plan measured, before the allowlist existed.
PLAN_BASE = "c24aeab2"


def _module(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "relayed.py"
    path.write_text("import hashlib\nfrom ve.wire import digest\n\n\ndef f(v, p, s):\n    " + body + "\n")
    return path


def _entry(site: identity_lint.Site, **extra) -> dict:
    return {"path": site.path, "scope": site.scope, "domain": site.domain, **extra}


def test_the_tree_passes_and_has_not_grown_since_the_merge_base():
    base = subprocess.run(["git", "merge-base", "HEAD", "main"], cwd=ROOT, check=True, capture_output=True,
                          text=True).stdout.strip()
    assert identity_lint.main([]) == 0
    assert identity_lint.main(["--base", base]) == 0


def test_the_allowlist_is_written_in_its_canonical_form():
    entries = json.loads(identity_lint.ALLOWLIST.read_text())
    assert entries and identity_lint.entry_problems(entries) == []
    expected = "[\n" + ",\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n]\n"
    assert identity_lint.ALLOWLIST.read_text() == expected


def test_the_relayed_modules_come_from_the_relay_lint(monkeypatch):
    # Review C2: the relay lint's helpers are relayed too; today it names none, so one is injected.
    helper = ROOT / "ve/wire.py"
    monkeypatch.setattr(relay_lint, "helpers", lambda modules: [helper])
    scopes = identity_lint.relayed_scopes()
    assert set(relay_lint.RELAYED) | {"ve/wire.py"} == {p for p, s in scopes.items() if s is True}
    for name, functions in relay_lint.RELAYED_FUNCTIONS.items():
        assert scopes[name] == tuple(functions)


@pytest.mark.parametrize("prefix", identity_lint.LEAN_PREFIXES)
def test_every_lean_owned_prefix_fails_in_a_relayed_module(tmp_path, prefix):
    module = _module(tmp_path, f'return digest(f"{prefix}{{v}}\\n", p)')
    assert [site.relayed for site in identity_lint.sites(module, True)] == [True]
    assert identity_lint.main([str(module)]) == 1


@pytest.mark.parametrize("body, domain", [
    ('return digest(f"ve-meaning-{v}\\n", p)', "ve-meaning-{}\n"),
    ('return hashlib.sha256((f"ve-source-{v}\\n" + s).encode("utf-8")).hexdigest()', "ve-source-{}\n"),
    ('return hashlib.sha256(f"ve-source-{v}\\n".encode("ascii") + s).hexdigest()', "ve-source-{}\n"),
    ('DOMAIN = "ve-report-"\n    return digest(DOMAIN + v + "\\n", p)', "ve-report-"),
    ('return digest("ve-report-" + v + "\\n", p)', "ve-report-{}\n"),
    ('return digest("ve-meaning-%s\\n" % v, p)', "ve-meaning-%s\n"),
    ('return digest("ve-meaning-{}\\n".format(v), p)', "ve-meaning-{}\n"),
    ('return hashlib.sha256(b"ve-model-x\\n" + s).hexdigest()', "ve-model-x\n"),
    ('return digest("ve-document@2\\n", p)', "ve-document@2\n"),
    ('return digest("ve-my-record-v1\\n", p)', "ve-my-record-v1\n"),
])
def test_seeded_preimages_in_a_relayed_module_fail(tmp_path, body, domain):
    module = _module(tmp_path, body)
    assert [site.domain for site in identity_lint.sites(module, True)] == [domain]
    assert identity_lint.main([str(module)]) == 1


@pytest.mark.parametrize("body", [
    '"""ve-meaning-{v}\nA docstring is not a preimage."""',
    'return p.get("format") == "ve-document@2"',
    'raise ValueError("ve-document@2 needs JSON front matter\\n")',
    'return digest("ve-a b\\n", p)',
    'return "the ve-meaning- domain\\n"',
])
def test_text_that_builds_no_preimage_passes(tmp_path, body):
    module = _module(tmp_path, body)
    assert identity_lint.sites(module, True) == []
    assert identity_lint.main([str(module)]) == 0


@pytest.mark.parametrize("body, found", [
    ('return digest("ve-my-record-v1\\n", p)', True),
    ('return digest(f"ve-meaning-{v}\\n", p)', True),
    ('return digest("ve-meaning-".encode() + v + b"\\n", p)', True),
    ('DOMAIN = "ve-meaning-"', False),
    ('return digest("ve-document@2", p)', False),
])
def test_rule_two_reads_domain_literals_in_every_module(tmp_path, body, found):
    module = _module(tmp_path, body)
    assert bool(identity_lint.sites(module, False)) is found
    assert not any(site.relayed for site in identity_lint.sites(module, False))


def test_only_the_relayed_functions_of_a_module_are_relayed(tmp_path):
    path = tmp_path / "mixed.py"
    path.write_text('def relayed(v):\n    return "ve-meaning-"\n\n\ndef own(v):\n    return "ve-meaning-"\n\n\n'
                    'def both(v):\n    return f"ve-meaning-{v}\\n"\n\n\n'
                    'def outer(v):\n    def inner():\n        return "ve-source-"\n    return inner\n')
    found = identity_lint.sites(path, ("relayed", "both", "outer"))
    assert [(site.scope, site.relayed) for site in found] == [("relayed", True), ("both", True),
                                                               ("outer.inner", True)]


def test_an_allowlisted_site_passes_and_a_new_one_fails(tmp_path):
    module = _module(tmp_path, 'a = digest(f"ve-meaning-{v}\\n", p)\n    return digest(f"ve-meaning-{v}\\n", a)')
    found = identity_lint.sites(module, True)
    assert len(found) == 2 and found[0].key == found[1].key
    one = [_entry(found[0], owner="lean", removed_by="AR-15")]
    assert identity_lint.problems(found, one * 2) == []
    [problem] = identity_lint.problems(found, one)
    assert "relayed module builds the Lean-owned identity preimage 've-meaning-{}\\n'" in problem
    assert ":7:" in problem


def test_an_entry_whose_site_is_gone_is_stale(tmp_path):
    module = _module(tmp_path, 'return digest(f"ve-meaning-{v}\\n", p)')
    [site] = identity_lint.sites(module, True)
    entry = _entry(site, owner="lean", removed_by="lf-16g")
    [problem] = identity_lint.problems([site], [entry, entry])
    assert "stale entry" in problem and "1 site(s) gone (1 left)" in problem
    moved = dict(entry, scope="g")
    assert len(identity_lint.problems([site], [moved])) == 2
    assert identity_lint.prune([site], [entry, entry, moved]) == [entry]
    assert identity_lint.prune([], [entry]) == []


@pytest.mark.parametrize("change", [
    {"owner": "python", "record": "adapters", "removed_by": None},
    {"removed_by": "AR-99"},
    {"removed_by": ""},
    {"removed_by": True},
    {"extra": "x"},
    {"owner": "rust"},
    {"scope": None},
])
def test_a_malformed_lean_entry_fails(change):
    entry = {"path": "ve/x.py", "scope": "f", "domain": "ve-meaning-{}\n", "owner": "lean", "removed_by": "AR-15"}
    entry.update(change)
    entry = {k: v for k, v in entry.items() if v is not None}
    assert identity_lint.entry_problems([entry])
    assert identity_lint.problems([], [entry])


@pytest.mark.parametrize("record, domain, ok", [
    ("proposals", "ve-proposal-source-v1\n", True),
    ("argument package", "ve-composition-v1\n", True),
    ("checker build", "ve-python-checker-build-v1\n", True),
    ("bundles", "ve-bundle-v0\n", False),
    ("proposals", "ve-meaning-{}\n", False),
    ("proposals", "ve-meaning-unheld-v9\n", False),
    ("assist", "ve-document@2\n", False),
])
def test_a_python_entry_names_a_record_of_d7_and_no_lean_domain(record, domain, ok):
    entry = {"path": "ve/x.py", "scope": "f", "domain": domain, "owner": "python", "record": record}
    assert (identity_lint.entry_problems([entry]) == []) is ok


def test_the_allowlist_must_be_a_list():
    assert identity_lint.entry_problems({"path": "ve/x.py"})
    assert identity_lint.entry_problems(["ve/x.py"])


def test_the_sites_only_shrink_whatever_their_owner():
    lean = {"path": "ve/x.py", "scope": "f", "domain": "ve-meaning-{}\n", "owner": "lean", "removed_by": "AR-15"}
    python = {"path": "ve/x.py", "scope": "f", "domain": "ve-proposal-a-v1\n", "owner": "python",
              "record": "proposals"}
    for entry in (lean, python):
        assert identity_lint.growth([entry], [entry]) == []
        assert identity_lint.growth([entry, entry], [entry]) == []
        assert identity_lint.growth([entry], [dict(entry, scope="g")]) == []
        assert len(identity_lint.growth([entry], [entry, dict(entry, path="ve/y.py")])) == 1
    [problem] = identity_lint.growth([lean], [lean, lean])
    assert "Lean-owned site ve/x.py 've-meaning-{}\\n' added since the base" in problem
    [problem] = identity_lint.growth([lean], [lean, python])
    assert "Python-owned site ve/x.py 've-proposal-a-v1\\n' added since the base" in problem
    assert len(identity_lint.growth([], [lean, dict(lean, domain="ve-source-{}\n")])) == 2


def _flipped(entry: dict) -> dict:
    """`entry` under the other owner."""
    keys = {"path": entry["path"], "scope": entry["scope"], "domain": entry["domain"]}
    return {**keys, "owner": "lean", "removed_by": "AR-15"} if entry["owner"] == "python" else \
        {**keys, "owner": "python", "record": "proposals"}


ALLOWED = json.loads(identity_lint.ALLOWLIST.read_text())


@pytest.mark.parametrize("domain", sorted(identity_lint.owners(ALLOWED)))
def test_no_domain_changes_owner_or_gains_a_second_one(domain):
    """Review B1: one owner per domain, and no owner changes against the base, for every allowlisted domain."""
    flipped = [_flipped(e) if e["domain"] == domain else e for e in ALLOWED]
    [owner] = {e["owner"] for e in flipped if e["domain"] == domain}
    changed = [p for p in identity_lint.growth(ALLOWED, flipped) if "the owner of" in p]
    assert changed == [f"{identity_lint.ALLOWLIST_NAME}: the owner of {domain!r} changed since the base: "
                       f"{identity_lint.owners(ALLOWED)[domain]} to {owner} (a new owner needs a DRI signature)"]
    if owner == "python":
        assert identity_lint.growth(ALLOWED, flipped)[0].startswith(f"{identity_lint.ALLOWLIST_NAME}: Python-owned")
    one = next(e for e in ALLOWED if e["domain"] == domain)
    second = dict(_flipped(one), path="ve/elsewhere.py")
    problems = identity_lint.entry_problems([*ALLOWED, second])
    assert problems and (f"{domain!r} has two owners (lean/python)" in problems[-1] or "Lean-owned domain" in
                         problems[-1])
    assert any("added since the base" in p for p in identity_lint.growth(ALLOWED, [*ALLOWED, second]))


@pytest.mark.parametrize("domain", sorted(d for d, owner in identity_lint.owners(ALLOWED).items() if owner == "lean"
                                          and identity_lint.lean_holders(d)))
def test_a_domain_lean_computes_cannot_be_python_owned(domain):
    """Review B1: a Lean-owned domain outside `LEAN_PREFIXES` is still Lean's when a Lean file holds its text."""
    entry = {"path": "ve/x.py", "scope": "f", "domain": domain, "owner": "python", "record": "proposals"}
    [problem] = identity_lint.entry_problems([entry])
    assert f"{domain!r} is a Lean-owned domain" in problem


def test_review_b1_a_python_entry_for_a_lean_domain_in_a_relayed_module_fails():
    """The review's reproduction: a `ve-english-vocabulary-v1` digest appended to the relayed module
    `ve/backends/speech_source.py` with a Python entry passed the lint and `--base main`."""
    entry = {"path": "ve/backends/speech_source.py", "scope": "decide_source", "domain": "ve-english-vocabulary-v1\n",
             "owner": "python", "record": "proposals"}
    assert identity_lint.entry_problems([*ALLOWED, entry])
    assert identity_lint.problems([], [*ALLOWED, entry])
    assert identity_lint.growth(ALLOWED, [*ALLOWED, entry])


@pytest.mark.parametrize("change", ["drop lean", "drop python", "flip"])
def test_main_with_base_fails_on_a_grown_allowlist(monkeypatch, change):
    """Review C1: `main` reads `--base` and fails on the growth it finds."""
    lean = next(n for n, e in enumerate(ALLOWED) if e["owner"] == "lean")
    python = next(n for n, e in enumerate(ALLOWED) if e["owner"] == "python")
    base = {"drop lean": ALLOWED[:lean] + ALLOWED[lean + 1:], "drop python": ALLOWED[:python] + ALLOWED[python + 1:],
            "flip": [_flipped(e) if e["domain"] == ALLOWED[python]["domain"] else e for e in ALLOWED]}[change]
    monkeypatch.setattr(identity_lint, "base_entries", lambda rev: base if rev == "grown" else ALLOWED)
    assert identity_lint.main(["--base", "same"]) == 0
    assert identity_lint.main(["--base", "grown"]) == 1


def test_the_ratchet_starts_at_the_commit_that_adds_the_allowlist():
    assert identity_lint.base_entries(PLAN_BASE) is None
    assert identity_lint.base_entries("HEAD") == json.loads(subprocess.run(
        ["git", "show", f"HEAD:{identity_lint.ALLOWLIST_NAME}"], cwd=ROOT, check=True, capture_output=True,
        text=True).stdout)
    with pytest.raises(subprocess.CalledProcessError):
        identity_lint.base_entries("no-such-revision-ar6")


def test_a_missing_module_fails(tmp_path):
    assert identity_lint.main([str(tmp_path / "absent.py")]) == 1


def test_prune_deletes_stale_entries_and_adds_none(tmp_path, monkeypatch):
    entries = json.loads(identity_lint.ALLOWLIST.read_text())
    stale = {"path": "ve/x.py", "scope": "f", "domain": "ve-meaning-{}\n", "owner": "lean", "removed_by": "AR-15"}
    copy = tmp_path / "identity-sites.json"
    monkeypatch.setattr(identity_lint, "ALLOWLIST", copy)
    identity_lint.write([*entries, stale])
    assert identity_lint.main([]) == 1
    assert identity_lint.main(["--prune"]) == 0
    assert json.loads(copy.read_text()) == entries
    identity_lint.write(entries[1:])
    assert identity_lint.main(["--prune"]) == 1
    assert json.loads(copy.read_text()) == entries[1:]
