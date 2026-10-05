#!/usr/bin/env python3
"""What `readings@1` (composition S1) accepts and refuses around this translation. Writes probes/s1-probe.json.

    uv run python usecases/claude-constitution-pilot/run-20261003T0600Z/probe_s1.py

(a) the main document (norm-defaults@0) with readings@1 added: its sets carry no content, so it validates as today;
(b) the same, one set given a strict norm as content (the only content a norm-defaults@0 document can state): the named abstention;
(c) the S1 document with norm-defaults@0 added: the rejection of norm-defaults@0 beside soft-norms@0.
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))

import importlib.util  # noqa: E402

import build  # noqa: E402
import spec_nd as nd  # noqa: E402

_spec = importlib.util.spec_from_file_location("readings_s1_pilot", ROOT / "tools/readings_s1_pilot.py")
pilot = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pilot)
from ve.document import check_document  # noqa: E402
from ve.errors import VEError  # noqa: E402


def split(path):
    data = Path(path).read_bytes()
    end = data.index(b"\n---\n", 4)
    return json.loads(data[4:end]), data[end + 5:]


def verdict(meta, rest):
    with tempfile.NamedTemporaryFile("wb", suffix=".ve.md", dir=RUN / "scratch", delete=False) as handle:
        handle.write(b"---\n" + json.dumps(meta, ensure_ascii=False, separators=(",", ":")).encode() + b"\n---\n" + rest)
    try:
        report = check_document(Path(handle.name))
        out = {"accepted": True, "premises": report["premises"], "readings": {
            k: v for k, v in (report.get("readings") or {}).items() if k in ("separations", "findings", "content_bearing")}}
    except Exception as exc:  # VEError, or CheckerUnavailable when Lean and Python give different first diagnostics
        out = {"accepted": False, "error_class": type(exc).__name__, "rejection": getattr(exc, "message", str(exc))}
    Path(handle.name).unlink()
    return out


def main():
    (RUN / "scratch").mkdir(exist_ok=True)
    result = {}
    main_meta, rest = split(RUN / "translation.ve.md")
    with_r1 = copy.deepcopy(main_meta)
    with_r1["environment"]["profiles"] = sorted({*with_r1["environment"]["profiles"], "readings@1"})
    from ve.document import _environment
    env1 = _environment(with_r1["environment"])
    # the environment now names readings@1, so every meaning and model identity is recomputed (composition S1 3)
    with_r1["reading_sets"] = [pilot._reidentified(env1, item) for item in with_r1["reading_sets"]]
    result["a_main_with_readings@1"] = {
        "profiles": with_r1["environment"]["profiles"],
        "note": "expected by composition S1 1.1: every candidate norm has content null, so no set is content-bearing and the "
                "document validates as today (the stored placeholder models are re-identified by the new environment, so the "
                "document is rewritten here). Observed: refused when the norm-defaults@0 block is built (ve/norm_defaults.py "
                "FilledBaseEnvironment drops norms@0 and keeps readings@1), with a message that is false of the document (norms@0 is listed)",
        **verdict(with_r1, rest)}

    # (b) one set with a strict norm candidate as content, in the norm-defaults@0 environment
    m = copy.deepcopy(with_r1)
    env = _environment(m["environment"])
    rs = next(s for s in m["reading_sets"] if s["id"] == "force-u0036-s05")
    rs.pop("models", None)
    strict = pilot.candidate(env, rs["id"], "strict", build.nd_block(nd.ND_RULES["u0036.s05"]), "the strict reading")
    default = next(r for r in rs["readings"] if r["id"] == "default")
    strict["admission"]["distinguishing_models"] = {"default": "pending"}
    default["admission"]["distinguishing_models"] = {"strict": "pending"}
    rs["readings"] = [strict, default]
    result["b_main_with_one_strict_norm_candidate"] = verdict(m, rest)

    # (c) the S1 document with norm-defaults@0 added
    s1_meta, s1_rest = split(RUN / "readings/s1.ve.md")
    c = copy.deepcopy(s1_meta)
    c["environment"]["profiles"] = sorted({*c["environment"]["profiles"], "norm-defaults@0"})
    result["c_s1_document_with_norm_defaults@0"] = verdict(c, s1_rest)
    result["s1_document_profiles"] = s1_meta["environment"]["profiles"]
    (RUN / "probes").mkdir(exist_ok=True)
    (RUN / "probes/s1-probe.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
