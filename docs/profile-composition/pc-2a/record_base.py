"""Save the parity corpus's answers on the retained loader (F2.3): the method below.

The first rows were saved on the base itself, its service and Python, before the Lean change. The base's mode refused every
soft-norms@0 document with norm-defaults@0 at its first gate, so each answer there was `_load_document`'s. The rows
added later (`_extras` in tests/document_chain_corpus.py) were saved on `_load_document` with the branch PC-2a closes
held open (`lean={}`, which it reads as a discourse admission), after this method gave the base's rows byte for byte;
so were the `--assume-no-exception` answers of every row.
Run: `VE_NATIVE_PREBUILT=1 uv run python docs/profile-composition/pc-2a/record_base.py`.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tests.document_chain_corpus import SAVED, answers, conclusions_of, corpus  # noqa: E402
from ve.document import load  # noqa: E402

retained = load._load_document
load._lean_answer = lambda *args, **kwargs: None
load._load_document = lambda raw, path, lean: retained(raw, path, {})

answered, written = corpus()
saved = json.loads(SAVED.read_text())
same = changed = 0
for name, raw in {**answered, **written}.items():
    with tempfile.TemporaryDirectory() as directory:
        found = answers(raw, Path(directory), conclusions_of(name))
    if name in saved:
        kept = all(found[command] == answer for command, answer in saved[name].items())
        same, changed = (same + 1, changed) if kept else (same, changed + 1)
    saved[name] = found
print(f"saved rows reproduced: {same}, differing: {changed}, total now: {len(saved)}")
if not changed:
    SAVED.write_text(json.dumps(saved, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
