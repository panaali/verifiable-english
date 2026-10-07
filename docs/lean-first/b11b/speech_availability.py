"""Record the three W2 record kinds newly reachable through the public speech caller."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))

from test_speech_source_lean import base_env, done_document, judged, nominated  # noqa: E402
from tests.frozen_speech.speech_document import SpeechSource as Frozen  # noqa: E402
from ve.speech_document import SpeechSource  # noqa: E402
from ve.errors import VEError  # noqa: E402


def main():
    out = ROOT / "docs/lean-first/b11b/evidence/speech-availability.json"
    # Human attestations are not measurements. Preserve them when the measured
    # base/head rows are regenerated, and keep the attestation tied to its case.
    signed = {row["case"]: row.get("dri_signature") for row in json.loads(out.read_text())} if out.exists() else {}
    cases = {
        "gap": judged(base_env()),
        "external_compliance": done_document(base_env()),
        "nomination": nominated([{"question": "r", "by": "alice", "support": "testimony", "nominate": 1}]),
    }
    rows = []
    for name, (metadata, source) in cases.items():
        try:
            Frozen(metadata, source.encode(), {})
        except VEError as exc:
            base = {"status": "error", "code": exc.code, "message": exc.message}
        else:
            raise AssertionError(f"frozen caller unexpectedly accepted {name}")
        new = SpeechSource(metadata, source.encode(), {})
        head = {"status": "ok", "document_id": new.document_id,
                "answers": new.answer_lines, "compliance": new.compliance_lines,
                "nominations": new.report["nominations"]}
        rows.append({"case": name, "class": "availability", "base": base, "head": head,
                     "dri_signature": signed.get(name)})
    out.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} availability rows to {out}")


if __name__ == "__main__":
    main()
