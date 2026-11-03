"""Save the parity corpus's answers on the code under test (F2.3). Run once on the base, before the Python branch was
deleted, with that commit's service: `VE_NATIVE_PREBUILT=1 uv run python docs/profile-composition/pc-2a/record_base.py`."""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tests.document_chain_corpus import SAVED, answers, conclusions_of, corpus  # noqa: E402

answered, written = corpus()
saved = {}
for name, raw in {**answered, **written}.items():
    with tempfile.TemporaryDirectory() as directory:
        saved[name] = answers(raw, Path(directory), conclusions_of(name))
SAVED.write_text(json.dumps(saved, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
