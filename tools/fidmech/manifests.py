"""The frozen blind inputs of plan 5.3 and 8 (manage-agents reviews/fid-mech-harness/inputs/): loaded by sha256, never
written; the plants and real defects turned into mutant records by unit text.

- **Load.** `load(directory)` reads adjudications.json, defects.json, fp1.json and plants.json and refuses
  (InputsError) any file whose sha256 is not the one pinned in SHA256 (the values of the directory's SHA256SUMS, named
  in the batch task). VE keeps no copy of these files; its tests use small fixtures with their own pins.
- **Plants** (`plant_records`): a plant is applied alone to the tree under test. When the plant's parent block text
  still stands once in the rules file it is replaced whole; otherwise each line the plant changes is rebased by its
  text (it must stand exactly once in the file); otherwise the plant is "not applicable" with the reason. Controls
  (`excluded`) are never applied.
- **Real defects** (`defect_records`): the mutant puts the defective text back where the repaired text stands (text
  the repair only added is deleted). A defect with no repair commit is "no repair yet" and unscored. Repaired text
  that no longer stands at the tree under test (a later change) makes the defect "not applicable": a later change is
  never read as the repair. So does a repair that deleted text the defect needs: no unit text marks where it stood.
- A plant or defect that edits a `*vocabulary.py` gets environment.d1.json regenerated from the edited module's
  text(), as the module's own __main__ writes it, so the text checks read what the kernel reads.
"""
from __future__ import annotations

import difflib
import hashlib
import importlib.util
import itertools
import json
import sys
import tempfile
from pathlib import Path

from tools.fidmech import mutants as M

SHA256 = {
    "adjudications.json": "a4e1c3feb6699deac070e2c0797e83b1d585b2277289681de72128e5096c85f8",
    "defects.json": "9ba691dd7b789ee77e1cdb7ea8f67b2261e5b636170af26faec7ff375d2f6394",
    "fp1.json": "2a0a6dcb9e1f94ecce820bbcfe4a6deef4107435ce51417cbe4c829c0c35988b",
    "plants.json": "5173f2b5f2154007bd956774bc00cddef3deb93e93fcc0c5f43c39bbd09e637a",
}
ENVIRONMENT = "environment.d1.json"
_NAMES = itertools.count()


class InputsError(ValueError):
    """An inputs file that is missing or whose sha256 is not the pinned one."""


def load(directory, pins=None):
    """{name without .json: parsed content, "sha256": {name: sha256}} of the four inputs; any mismatch refuses."""
    pins = SHA256 if pins is None else pins
    directory = Path(directory)
    out, shas = {}, {}
    for name, want in pins.items():
        path = directory / name
        if not path.is_file():
            raise InputsError(f"{path}: missing")
        data = path.read_bytes()
        got = hashlib.sha256(data).hexdigest()
        if got != want:
            raise InputsError(f"{path}: sha256 {got} is not the pinned {want}; refused, nothing run")
        out[name.removesuffix(".json")] = json.loads(data)
        shas[name] = got
    out["sha256"] = shas
    return out


def _case_name(path):
    """usecases/<doc>/<name> -> name; any other path is refused."""
    parts = Path(path).parts
    if len(parts) != 3 or parts[0] != "usecases":
        raise InputsError(f"an input edit outside usecases/<doc>/: {path}")
    return parts[2]


def rebase(text, before, after):
    """(new text, how) with `before` replaced by `after`: whole when `before` stands once; else line by line, each
    changed line by its text, which must stand once in `text`. (None, reason) when it does not apply."""
    if before == after:
        return None, "the edit changes nothing"
    if text.count(before) == 1:
        return text.replace(before, after, 1), "whole"
    old, new = before.splitlines(keepends=False), after.splitlines(keepends=False)
    out = text
    for tag, i0, i1, j0, j1 in difflib.SequenceMatcher(a=old, b=new, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        if i0 == i1:
            return None, "an inserted line has no unit text to stand beside"
        find, put = "\n".join(old[i0:i1]), "\n".join(new[j0:j1])
        n = out.count(find)
        if n != 1:
            return None, (f"the changed text {find[:80]!r} stands {n} times in the file under test"
                          if n else f"the unit text {find[:80]!r} is gone from the file under test")
        out = out.replace(find, put, 1)
    return out, "lines"


def environment_text(vocabulary_text):
    """environment.d1.json as an edited vocabulary module's text() writes it (imported from a temporary file)."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "vocabulary_under_test.py"
        path.write_text(vocabulary_text, encoding="utf-8")
        name = f"fidmech_vocabulary_{next(_NAMES)}"
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            return module.text()
        finally:
            sys.modules.pop(name, None)


def _record(document, unit, class_, op, files, changed):
    """A plant or real-defect mutant record of `changed` ({name: new text}), environment regenerated when a
    vocabulary module changed."""
    vocab = [n for n in changed if n.endswith("vocabulary.py")]
    if vocab and ENVIRONMENT not in changed and ENVIRONMENT in files:
        changed = {**changed, ENVIRONMENT: environment_text(changed[vocab[0]])}
    edits = [e for name in sorted(changed) if changed[name] != files[name]
             for e in M.line_edits(name, files[name], changed[name])]
    if not edits:
        return None, "the edit leaves the files under test unchanged"
    return M.record(document, unit, class_, op, "rule", edits, files), None


def _apply(files, edits):
    """{name: new text} of `edits` [(name, before, after)] applied in order, or (None, reason)."""
    changed, hows = {}, []
    for name, before, after in edits:
        if name not in files:
            return None, f"{name} is not a case file under test"
        text, how = rebase(changed.get(name, files[name]), before, after)
        if text is None:
            return None, f"{name}: {how}"
        changed[name] = text
        hows.append(how)
    return changed, "rebased by line" if "lines" in hows else "applied whole"


def plant_records(plants, document, case_dir):
    """(records, rows): a record per applicable plant of `document` (class "plant", op the plant id) and a row per
    plant {"id", "unit", "status": "applied"/"not applicable"/"excluded", "how" or "reason"}."""
    files = M.case_files(case_dir)
    records, rows = [], []
    for p in plants:
        if p["case"] != document:
            continue
        row = {"id": p["id"], "unit": p["unit"], "class": p["class"]}
        if p.get("excluded"):
            rows.append({**row, "status": "excluded", "reason": p.get("reason") or "a control, excluded by name"})
            continue
        edits = [(_case_name(p["file"]), p["before"], p["after"])]
        edits += [(_case_name(v["file"]), v["before"], v["after"]) for v in p.get("vocabulary_edits") or ()]
        changed, how = _apply(files, edits)
        rec, why = _record(document, p["unit"], "plant", p["id"], files, changed) if changed else (None, how)
        if rec is None:
            rows.append({**row, "status": "not applicable", "reason": why})
            continue
        records.append({**rec, "id": f"{document}:plant:{p['id']}"})
        rows.append({**row, "status": "applied", "how": how, "mutant": records[-1]["id"]})
    return records, rows


def defect_records(defects, document, case_dir):
    """(records, rows): a record per real defect of `document` whose repaired text stands (class "real-defect": the
    defective text put back), and a row per defect with status "applied", "no repair yet" (unscored) or
    "not applicable" (the reason)."""
    files = M.case_files(case_dir)
    records, rows = [], []
    for d in defects:
        if d["case"] != document:
            continue
        row = {"id": d["id"], "unit": d["unit"]}
        if not d.get("repair_commit"):
            rows.append({**row, "status": "no repair yet", "reason": "no repair commit: unscored"})
            continue
        gone = [e["what"] for e in d["edits"] if e["after"] is None]
        if gone:
            rows.append({**row, "status": "not applicable", "reason": (
                f"the repair deleted {', '.join(gone)}; no unit text marks where the defective text stood")})
            continue
        # A repair that only added text (before None) is undone by deleting that text.
        edits = [(_case_name(e["file"]), e["after"], e["before"] or "") for e in d["edits"]]
        changed, how = _apply(files, edits)
        if changed is None:
            how = f"{how} (the repaired text no longer stands: a later change is never read as the repair)"
        rec, why = _record(document, d["unit"], "real-defect", d["id"], files, changed) if changed else (None, how)
        if rec is None:
            rows.append({**row, "status": "not applicable", "reason": why})
            continue
        records.append({**rec, "id": f"{document}:defect:{d['id']}"})
        rows.append({**row, "status": "applied", "how": how, "mutant": records[-1]["id"]})
    return records, rows
