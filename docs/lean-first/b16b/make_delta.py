"""Write the 16b signed list (`delta.json`) from a `tools/lean_first_diff.py compare --json` run without one.

    python docs/lean-first/b16b/make_delta.py COMPARE.json DOCUMENT_TEXTS.json

Every difference of the `document` corpus is a rejection on both sides whose Python text is another decoder's
(`conformance/document_wrapper.owner_of`: the environment decoder, batch 12b; the formula decoder or W2
admission, batch 13b), which the switch now relays from Lean; each record is listed with that owner, and the
script refuses (exit 1) a document difference that is not such a rejection. The pilots' differences are the
scratch directory's name in a stderr text (wording) and `english.check` refusals identical on both sides
(unavailable). `DOCUMENT_TEXTS.json` is the corpus file `lean_first_diff.py record` wrote (`*.document.json`).
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from conformance import document_wrapper as dw  # noqa: E402
from tools.lean_first_diff import text_pairs  # noqa: E402

PILOT_UNAVAILABLE = ("both sides answer the same english.check CheckerUnavailable (the pilot's vocabulary is "
                     "refused by the V3 lexicon check); no document wrapper decision is involved")


def main(argv=None) -> int:
    compare_path, texts_path = (argv or sys.argv[1:])
    rows = json.loads(Path(compare_path).read_text())["differences"]
    texts = {row["case"]: row["text"] for row in json.loads(Path(texts_path).read_text())}
    owners = {}
    delta = {"wording": [], "order": [], "verdict": [], "availability": [], "unavailable": []}
    pairs = set()
    for row in rows:
        key = {k: row[k] for k in ("corpus", "authority", "case", "op")}
        if row["corpus"] == "document":
            if not ("raised" in row["base"] and "raised" in row["head"]):
                print(f"not a rejection on both sides: {key}", file=sys.stderr)
                return 1
            if row["case"] not in owners:
                owners[row["case"]] = dw.python_answer(texts[row["case"]]).get("owner")
            owner = owners[row["case"]]
            if owner not in dw.OWNED_ELSEWHERE:
                print(f"the wrapper's own text changed: {key}", file=sys.stderr)
                return 1
        elif row["corpus"] == "pilots" and row["class"] == "unavailable":
            delta["unavailable"].append({**key, "reason": PILOT_UNAVAILABLE})
            continue
        elif row["corpus"] != "pilots" or row["class"] != "wording":
            print(f"unexpected difference: {key} {row['class']}", file=sys.stderr)
            return 1
        if row["class"] == "wording":
            pairs.update((json.dumps(a), json.dumps(b)) for a, b in text_pairs(row["base"], row["head"]))
        else:
            disposition = {"disposition": "path pending lf-12"} if row["class"] == "verdict" else {}
            delta[row["class"]].append({**key, "owner": owner, "base": row["base"], "head": row["head"],
                                        **disposition})
    delta["wording"] = [{"base": json.loads(a), "head": json.loads(b)} for a, b in sorted(pairs)]
    (HERE / "delta.json").write_text(json.dumps(delta, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    counts = {klass: len(items) for klass, items in delta.items()}
    by_owner = {}
    for case, owner in owners.items():
        by_owner[owner] = by_owner.get(owner, 0) + 1
    print(json.dumps({"listed": counts, "document_cases_by_owner": by_owner}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
