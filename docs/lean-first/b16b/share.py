"""How many documents the 16b switch hands to Lean, per corpus (saved as `evidence/share.json`).

    python docs/lean-first/b16b/share.py RECORD_PREFIX

RECORD_PREFIX is the `--out` of a `tools/lean_first_diff.py record` run of the head (its `.document.json`,
`.rights.json` and `.norm_defaults.json` corpus files beside it); the pilots are this checkout's
(`lean_first_diff.pilot_documents`). For every `ve-document@1` text, the head's `ve.document._lean_answer`
decides: `lean` (Lean's answer is the result: accepted, or rejected verbatim) or `retained` with the mode's
reason, its profile, block and family names kept, its other details cut at the first parenthesis.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def classify(raw: bytes):
    from ve.backends import relay
    from ve.discourse import is_discourse_text
    if is_discourse_text(raw):
        return "discourse route (ve-document@2)"
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return "retained: not UTF-8"
    _, error = relay.answer("document", {"id": "d", "document": text, "admit": True})
    if error is None or type(error).__name__ not in ("CheckerUnavailable", "ResourceLimit"):
        return "lean"
    message = getattr(error, "message", str(error)).removeprefix("CheckerUnavailable: ")
    return "retained: " + message.split(" (")[0][:120]


def main(argv=None) -> int:
    prefix = Path((argv or sys.argv[1:])[0])
    from tools.lean_first_diff import pilot_documents
    corpora = {name: [row["text"].encode("utf-8") for row in json.loads(prefix.with_suffix(f".{name}.json").read_text())]
               for name in ("document", "rights", "norm_defaults")}
    corpora["pilots"] = [data for _, _, data in pilot_documents(ROOT)]
    out = {}
    for name, texts in corpora.items():
        counts = Counter(classify(raw) for raw in texts)
        out[name] = {"documents": len(texts), "lean": counts.pop("lean", 0), "other": dict(sorted(counts.items()))}
    (HERE / "evidence/share.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({name: [row["documents"], row["lean"]] for name, row in out.items()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
