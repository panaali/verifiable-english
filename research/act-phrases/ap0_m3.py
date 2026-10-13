"""AP-0 item 2: count M3 in the natural view (rule: docs/research/act-phrases-phase1.md 1.3).

    prlimit --as=8589934592 uv run python research/act-phrases/ap0_m3.py

Renders the four UDHR parts and the constitution's main document of run 20261012T1800Z (read-only) with
`ve.document.render_document`, and writes docs/research/evidence/act-phrases/m3-count.json and the renderings under
docs/research/evidence/act-phrases/m3-rendered/. No model call.
"""
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ve.document import render_document  # noqa: E402

PILOTS = Path("/home/seyran/code/manage-agents/pilots")
UDHR = PILOTS / "udhr/run-20261012T1800Z"
CC = PILOTS / "claude-constitution/run-20261012T1800Z"
DOCS = [("udhr", UDHR / f"translation-part0{i}.ve.md") for i in range(1, 5)] + [("constitution", CC / "translation.ve.md")]
OUT = ROOT / "docs/research/evidence/act-phrases"
PHRASES = ("classified as", "has the recorded relation")
ENTITLEMENT = ("has_the_right", "is_entitled")
NAME = re.compile(r'(?:classified as|has the recorded relation) "([^"]+)"')


def predicates(path):
    text = path.read_text()
    end = text.index("\n---\n", 4)
    return json.loads(text[4:end])["environment"]["vocabulary"]["predicates"]


def count(path, text):
    preds = predicates(path)
    plain = {k for k, v in preds.items() if (v.get("regulated") or {}).get("role") == "plain"}
    lines = [ln for ln in text.splitlines() if any(p in ln for p in PHRASES)]
    names = [n for ln in lines for n in NAME.findall(ln)]
    return {
        "lines": len(text.splitlines()),
        "m3_lines": len(lines),
        "occurrences": sum(ln.count(p) for ln in lines for p in PHRASES),
        "occurrences_by_phrase": {p: sum(ln.count(p) for ln in lines) for p in PHRASES},
        "distinct_predicates": sorted(set(names)),
        "lines_naming_plain_regulated": sum(any(n in plain for n in NAME.findall(ln)) for ln in lines),
        "lines_naming_other": sum(any(n not in plain for n in NAME.findall(ln)) for ln in lines),
        "plain_regulated_named": sorted({n for n in names if n in plain}),
        "plain_regulated_declared": sorted(plain),
        # Not pre-registered (added after the run, labelled exploratory in the report): the part documents declare
        # entitlements as ordinary predicates, so the registered split by declared kind cannot see them.
        "exploratory_lines_naming_entitlement_by_name": sum(any(n.startswith(ENTITLEMENT) for n in NAME.findall(ln))
                                                             for ln in lines),
        "exploratory_entitlements_named": sorted({n for n in names if n.startswith(ENTITLEMENT)}),
    }


def main():
    (OUT / "m3-rendered").mkdir(parents=True, exist_ok=True)
    result = {"rule": "docs/research/act-phrases-phase1.md 1.3", "documents": {}}
    for corpus, path in DOCS:
        start = time.monotonic()
        text = render_document(path)
        name = f"{corpus}-{path.name[:-len('.ve.md')]}.md"
        (OUT / "m3-rendered" / name).write_text(text)
        row = {"corpus": corpus, "source": str(path), "seconds": round(time.monotonic() - start, 1), **count(path, text)}
        if corpus == "udhr":
            pilot = UDHR / "rendered-parts" / (path.name[:-len(".ve.md")] + ".md")
            row["same_as_pilot_rendering"] = pilot.read_text() == text
        result["documents"][name] = row
        print(name, row["m3_lines"], row["occurrences"], row["lines_naming_plain_regulated"], row["lines_naming_other"],
              row.get("same_as_pilot_rendering"), row["seconds"], flush=True)
    for corpus in ("udhr", "constitution"):
        rows = [r for r in result["documents"].values() if r["corpus"] == corpus]
        result[corpus] = {k: sum(r[k] for r in rows) for k in
                          ("m3_lines", "occurrences", "lines_naming_plain_regulated", "lines_naming_other",
                           "exploratory_lines_naming_entitlement_by_name")}
        result[corpus]["distinct_predicates"] = len({n for r in rows for n in r["distinct_predicates"]})
    result["m3"] = result["udhr"]["m3_lines"] + result["constitution"]["m3_lines"]
    (OUT / "m3-count.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: result[k] for k in ("udhr", "constitution", "m3")}))


if __name__ == "__main__":
    main()
