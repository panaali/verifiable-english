"""B1's input (docs/spec/scope-PLAN.md, benchmark B1): F1-doc's document over the full pinned constitution pilot.

The pilot is run 20261012T1800Z's `translation.ve.md` at pilot commit `ecfd1ace7`, kept byte for byte in
`data/` (gzip) and checked against its git blob id. B1's text is its first 184,893 bytes, the pinned constitution
SC-M0 read (its SHA-256 is SC-M0's input hash), without the trailing English fence; its units are the pilot's 1,132,
with the hard-constraint block's ten (u0164.s01 to u0166.s01) replaced by F1's (`tests/data/scope/
hard-constraints.scope.md`: the lead-in's part and seven item parts), each at the same span. The front matter is
the pilot's with F1's `scope` block, `scope@0` and F1's vocabulary and open terms added (F1's entry wins a shared
name). The bench reads only the layout and the run path `governFast` of it (`lean/ScopeBenchMain.lean`).

C11's layout: `LAYOUT_SHA256` is the hash of `layout_rows` of SC-M0's own transcription of `ofSource`
(`research/scope/sc_m0_tally.py` at 9a98c33f1, the layout C11 checked) on this text and these spans
(docs/scope/sc-1bb/layout-evidence.json). The bench compares Lean's layout with it before it times anything.

    uv run python tools/bench/scope_b1.py <case.json>   writes the case `ve_scope_bench` reads
"""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
COPY = Path(__file__).with_name("data") / "translation-ecfd1ace.ve.md.gz"
BLOB = "9933b4334226e995601e072a364839bd2c7bc98c"  # `git rev-parse ecfd1ace7:usecases/claude-constitution-pilot/run-20261012T1800Z/translation.ve.md`
SHA256 = "adecddd32c6c13068253be88c7af2703044ac72d802afaed86efc517bb7145c0"
F1 = ROOT / "tests/data/scope/hard-constraints.scope.md"
SOURCE_BYTES = 184893
SOURCE_SHA256 = "fa10ed489e758ab009fe420954a385afbe3b11978afd79c4e9f4ae97e02d50dd"  # SC-M0's constitution input
UNITS = 1132
LAYOUT_SHA256 = "a65198066a739dd36e121ab30ea8ac9bce7f535503cc7b18d14b2292f28eb60a"
LEAD = "u0164.s02"
F1_RUN = [f"u0165.s0{i}" for i in range(1, 8)]  # C11's F1 run on the full layout
GOVERNED = [u for u in F1_RUN if u != "u0165.s03"]  # F1's six item parts, each composed with the lead-in's part


def _split(data: bytes) -> tuple[dict, bytes]:
    end = data.index(b"\n---\n", 4)
    return json.loads(data[4:end]), data[end + 5:]


def pinned() -> tuple[dict, bytes]:
    """(front matter, constitution bytes) of the pinned translation, checked against the pilot commit's blob."""
    data = gzip.decompress(COPY.read_bytes())
    assert hashlib.sha256(data).hexdigest() == SHA256
    assert hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest() == BLOB
    front, body = _split(data)
    source = body[:SOURCE_BYTES]
    assert hashlib.sha256(source).hexdigest() == SOURCE_SHA256 and len(front["units"]) == UNITS
    return front, source


def document() -> str:
    """B1's document: the pinned pilot with F1's hard-constraint block, at the block's place in the constitution."""
    front, source = pinned()
    f1, excerpt = _split(F1.read_bytes())
    at = source.index(excerpt)
    assert source.find(excerpt, at + 1) == -1, "F1's excerpt is not one place in the constitution"
    ours = {u["id"]: {**u, "span": [u["span"][0] + at, u["span"][1] + at]} for u in f1["units"]}
    units = [ours.pop(u["id"], u) for u in front["units"]]
    assert not ours and all(u["span"] == p["span"] for u, p in zip(units, front["units"]))
    environment = front["environment"]
    profiles = sorted(set(environment["profiles"]) | set(f1["environment"]["profiles"]))
    vocabulary = {k: {**environment["vocabulary"].get(k, {}), **v} for k, v in f1["environment"]["vocabulary"].items()}
    named = {t["name"] for t in f1["open_terms"]}
    meta = {**front, "environment": {**environment, "profiles": profiles,
                                     "vocabulary": {**environment["vocabulary"], **vocabulary}},
            "units": units, "open_terms": [t for t in front["open_terms"] if t["name"] not in named] + f1["open_terms"],
            "scope": f1["scope"]}
    return "---\n" + json.dumps(meta, ensure_ascii=False) + "\n---\n" + source.decode()


def case() -> dict:
    """The document mode's case of B1's document."""
    return {"id": "b1", "document": document()}


def layout_rows(rows: list) -> str:
    """The canonical text of a layout, one unit per row: id, span, item, midLine, lead, label and para."""
    return "".join(json.dumps([r["id"], list(r["span"]), r["item"], r["midLine"], r["lead"], r["label"], r["para"]],
                              separators=(",", ":")) + "\n" for r in rows)


def layout_sha256(rows: list) -> str:
    return hashlib.sha256(layout_rows(rows).encode()).hexdigest()


def problems(out: dict, govern: bool) -> list[str]:
    """Why a run of `ve_scope_bench` on B1's case is not B1, one line each: the bench reports these and times
    nothing."""
    if "error" in out:
        return [f"the scope block does not decode: {out['error']}"]
    found = []
    if layout_sha256(out["layout"]) != LAYOUT_SHA256:
        found.append(f"the layout is not C11's: SHA-256 {layout_sha256(out['layout'])}, C11's {LAYOUT_SHA256} "
                     "(rerun C11 on the new layout before a new baseline)")
    if (out["lead"], out["run"]) != (LEAD, F1_RUN):
        found.append(f"the list run of {out['lead']} is {out['run']}, C11's F1 run of {LEAD} is {F1_RUN}")
    if govern and out["governFast"] != {"ok": GOVERNED}:
        found.append(f"governFast answered {out['governFast']}, not ok with {GOVERNED} changed")
    return found


if __name__ == "__main__":
    Path(sys.argv[1]).write_text(json.dumps(case(), ensure_ascii=False))
