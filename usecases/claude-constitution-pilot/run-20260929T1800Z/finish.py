#!/usr/bin/env python3
"""Run VE on the built documents, write the ledger, rendering and metrics.

Run after build.py, from anywhere:  uv run python usecases/claude-constitution-pilot/run-20260929T1800Z/finish.py
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUN))
import spec  # noqa: E402

SOURCE_PATH = ROOT / "usecases/claude-constitution-pilot/source/claude-constitution.md"
SOURCE = SOURCE_PATH.read_bytes()
DOCS = {"main": RUN / "translation.ve.md", "strict": RUN / "readings/all-strict.ve.md",
        "default": RUN / "readings/all-default.ve.md"}
COVERED = {"CHECKED", "LABELLED", "OPEN", "READINGS"}
AUDIT_PASSED_LABELLED = ["u0023", "u0032.heading", "u0069.heading", "u0095.heading", "u0103", "u0108", "u0126",
                         "u0143.heading", "u0162.heading", "u0174.heading", "u0219.heading", "u0254.heading",
                         "u0268.heading", "u0277", "u0282", "u0286.heading", "u0294", "u0298"]


def ve(*args):
    proc = subprocess.run([sys.executable, "-m", "ve", *args], cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"ve {' '.join(args)} failed:\n{proc.stderr[-2000:]}")
    return proc.stdout


def front_matter(path):
    data = path.read_bytes()
    end = data.index(b"\n---\n", 4)
    return json.loads(data[4:end])


def excerpt(text):
    text = text.replace("\n", " ")
    return text[:160]


# ------------------------------------------------------------------ ledger
def new_ledger(prev, main_meta, english):
    by_old = {u["old"]: u for u in spec.UNITS}
    units_by_id = {u["id"]: u for u in main_meta["units"]}
    out, replaced = [], {}
    for entry in prev:
        item = by_old.get(entry["id"])
        if item is None:
            note_extra = {
                "u0164.s02": "List lead-in of the hard-constraint bullets u0165.s01 to s07: it supplies their subject and "
                             "the force “should never”, which their reading sets carry. It stays UNFORMALISED on its own "
                             "(no rule of its own; the bullets' rules are its content).",
                "u0166.s01": "Cited by the narrowing of the hard-constraint force readings (absolute restrictions). "
                             "Unchanged: still UNFORMALISED.",
                "u0166.s04": "Cited by the narrowing of the hard-constraint force readings (cannot be unlocked by any "
                             "operator or user). Unchanged: still UNFORMALISED.",
            }.get(entry["id"])
            if note_extra:
                entry = {**entry, "citation_note": note_extra}
            out.append(entry)
            continue
        a, b = entry["span"]
        pieces = item.get("pieces") or [(SOURCE[a:b].decode("utf-8"), "norm", None, None)]
        cursor = a
        for index, (s, kind, feature, note) in enumerate(pieces, 1):
            width = len(s.encode("utf-8"))
            uid = entry["id"] if "pieces" not in item else f"{entry['id']}.p{index}"
            base = {"id": uid, "span": [cursor, cursor + width], "source_excerpt": excerpt(s),
                    "parent_unit": entry["parent_unit"], "old_unit": entry["id"]}
            cursor += width
            if kind != "norm":
                out.append({**base, "status": "UNFORMALISED", "missing_feature": feature, "other_blockers": [],
                            "note": note})
                continue
            forced = item["kind"] == "norm-force"
            doc_unit = units_by_id[uid]
            record = {**base, "status": "READINGS" if forced else "OPEN", "kind": "norm",
                      "rule": item["rule"], "predicate": item["predicate"], "sign": "negative" if not item["sign"] else "positive",
                      "open_terms": item["open_terms"],
                      "previous_status": entry["status"], "previous_missing_feature": entry.get("missing_feature"),
                      "note": item["readings_note"]}
            if forced:
                record["reading_set"] = f"force-{uid.replace('.', '-')}"
                record["readings"] = [
                    {"id": "strict", "elaborated_in": "readings/all-strict.ve.md",
                     "english": english["strict"][item["rule"]]["text"],
                     "english_round_trip": english["strict"][item["rule"]]["round_trip"],
                     "meaning": "a strict rule" + (" (hard: true, no exception decision, no instruction switch)"
                                                   if item.get("hard_if_narrowed") else "")},
                    {"id": "default", "elaborated_in": "readings/all-default.ve.md",
                     "english": english["default"][item["rule"]]["text"],
                     "english_round_trip": english["default"][item["rule"]]["round_trip"],
                     "meaning": "a defeasible rule with an open exception decided by nobody the source names "
                                f"(decision {'soft__excepted__' + item['rule'].replace('-', '_')})"}]
                record["document_status"] = "OPEN (pending reading set: candidate norms cannot carry content)"
                if item.get("cites"):
                    record["narrowing"] = {"id": f"narrow-{uid.replace('.', '-')}", "keeps": ["strict"],
                                           "by": "translator", "reason_spans": item["cites"],
                                           "effect": "recorded only; both readings stay in the set"}
            else:
                record["document_status"] = "OPEN (active default rule)"
                record["readings"] = [{"id": "default", "note": "one reading: “generally” marks a defeasible duty",
                                       "english": english["default"][item["rule"]]["text"],
                                       "english_round_trip": english["default"][item["rule"]]["round_trip"]}]
            out.append(record)
        assert cursor == b, entry["id"]
    return out


# ------------------------------------------------------------------ metrics
def counts(ledger):
    units = Counter(e["status"] for e in ledger)
    nbytes = Counter()
    for e in ledger:
        nbytes[e["status"]] += e["span"][1] - e["span"][0]
    return units, nbytes


def aggregate(ledger):
    groups = defaultdict(list)
    for e in ledger:
        groups[e["parent_unit"]].append(e)
    units, nbytes = Counter(), Counter()
    for members in groups.values():
        statuses = {m["status"] for m in members}
        units["MIXED" if len(statuses) > 1 else next(iter(statuses))] += 1
        for m in members:
            nbytes[m["status"]] += m["span"][1] - m["span"][0]
    return len(groups), dict(units), dict(nbytes)


def full(counter):
    return {k: counter.get(k, 0) for k in ("CHECKED", "LABELLED", "OPEN", "READINGS", "UNFORMALISED")}


def tally(ledger):
    return dict(Counter(e["missing_feature"] for e in ledger if e["status"] == "UNFORMALISED"))


# ------------------------------------------------------------------ rendering
LABEL = re.compile(r"^(Checked reading|Open rule reading): (Rule (\S+) .*)$")


def relabel(text, docmeta):
    """The generic renderer prints “Checked reading” for OPEN content-bearing rules; say what the ledger says."""
    open_terms = {}
    for unit in docmeta["units"]:
        c = unit.get("content")
        if c and "norm" in c and type(unit["meaning"]) is dict:
            open_terms[c["norm"]["name"]] = [t for t in unit["meaning"]["open"] if not t.startswith("soft__")]
    lines = []
    for line in text.split("\n"):
        m = LABEL.match(line)
        if m and m.group(3) in open_terms:
            terms = ", ".join(open_terms[m.group(3)]) or "none beyond the exception"
            line = f"Open reading (open terms: {terms}; deciders unresolved): {m.group(2)}"
        lines.append(line)
    return "\n".join(lines)


def paraphrases(text):
    out = {}
    for line in text.split("\n"):
        m = LABEL.match(line) or re.match(r"^(Open reading \(.*?\)): (Rule (\S+) .*)$", line)
        if m:
            out[m.group(3)] = m.group(2) if m.re is LABEL else m.group(2)
    return out


def english_forms(path):
    """The soft-norm English export of every rule alone, and whether it parses back to the same rule."""
    from ve.norm_english import _render_soft_english, parse_english, render_english
    from ve.softnorms import SoftEnvironment, SoftNormDocument
    meta = front_matter(path)
    env = SoftEnvironment(meta["environment"])
    out = {}
    for unit in meta["units"]:
        content = unit.get("content")
        if not content or "norm" not in content:
            continue
        doc = SoftNormDocument(env, [content])
        text, manifest = _render_soft_english(doc)
        # The soft export pairs printed lines with rules one to one, so a rule whose guard prints as a list loses
        # its list lines; complete the display from the W1 rendering of the same rule.
        w1_lines = render_english(doc.core, _w1=True)[0].split("\n")
        truncated = len(text.split("\n")) < len(w1_lines)
        display = text if not truncated else text.split("\n")[0] + "\n" + "\n".join(w1_lines[1:])
        try:
            back = parse_english(env, text, manifest)
            ok = back.document_hash == doc.document_hash
            error = None if ok else "hash differs"
        except Exception as exc:  # the English export exists but does not parse back
            ok, error = False, f"{type(exc).__name__}: {exc}"
        out[content["norm"]["name"]] = {"text": " ".join(part.strip() for part in display.split("\n")).removeprefix("Rule 1. "),
                                        "export_truncated": truncated, "round_trip": ok, "error": error}
    return out


def expand_main(main_text, strict_text, default_text, main_meta, english):
    strict = paraphrases(strict_text)
    default = paraphrases(default_text)
    order = sorted((u["span"][0], u["id"]) for u in main_meta["units"] if u["id"] in
                   {rs["unit"] for rs in main_meta.get("reading_sets", [])})
    unit_to_rule = {}
    for item in spec.UNITS:
        if item["kind"] != "norm-force":
            continue
        for u in main_meta["units"]:
            if u["id"] == item["old"] or u["id"].startswith(item["old"] + ".p"):
                if any(rs["unit"] == u["id"] for rs in main_meta["reading_sets"]):
                    unit_to_rule[u["id"]] = item
    rules = [unit_to_rule[uid] for _, uid in order]
    narrowed = {n["set"]: n for n in main_meta.get("narrowings", [])}
    lines, out, index = main_text.split("\n"), [], 0
    i = 0
    while i < len(lines):
        if (lines[i] == "Recorded meaning: The passage is recorded as a rule."
                and lines[i + 1:i + 2] == ["This sentence could mean:"]):
            item = rules[index]
            uid = order[index][1]
            index += 1
            name = item["rule"]
            out.append("Open reading set (force word ambiguous; both readings kept, elaborated in the companion documents):")
            for label, table, sentences in (("strict", strict, english["strict"]), ("default", default, english["default"])):
                shown = sentences[name]
                trip = "parses back to the same rule" if shown["round_trip"] else f"does not parse back ({shown['error']})"
                out.append(f"Reading {label} — English: {shown['text']} [{trip}]")
                out.append(f"  checker: {table[name]}")
            narrow = narrowed.get(f"force-{uid.replace('.', '-')}")
            if narrow:
                out.append(f"Translator's narrowing (recorded, set unchanged): keeps strict, citing {', '.join(narrow['reason_spans'])}.")
            i += 4
            continue
        out.append(lines[i])
        i += 1
    assert index == len(rules), (index, len(rules))
    return "\n".join(out)


def probe_profiles():
    """Add one more profile to the strict companion's environment and record what `ve document check` says.

    Shows which merged features can share an environment with the norms this run introduces."""
    import tempfile
    base = DOCS["strict"].read_bytes()
    end = base.index(b"\n---\n", 4)
    meta, tail = json.loads(base[4:end]), base[end + 5:]
    result = {}
    for extra in ("closure@0", "order@0", "time@0", "reports@0", "alternatives@0", "speech-acts@0", "definitions@0", "data@0"):
        m = json.loads(json.dumps(meta))
        m["environment"]["profiles"] = sorted(set(m["environment"]["profiles"]) | {extra})
        with tempfile.NamedTemporaryFile("wb", suffix=".ve.md", delete=False) as handle:
            handle.write(b"---\n" + json.dumps(m, ensure_ascii=False, separators=(",", ":")).encode() + b"\n---\n" + tail)
        proc = subprocess.run([sys.executable, "-m", "ve", "document", "check", handle.name], cwd=ROOT,
                              capture_output=True, text=True)
        Path(handle.name).unlink()
        result[extra] = ("accepted at document-check level" if proc.returncode == 0
                         else (proc.stderr.strip().splitlines() or ["rejected"])[-1].split(": ", 1)[-1])
    return result


def main():
    # ---- VE runs
    results = {}
    for key, path in DOCS.items():
        rel = str(path.relative_to(ROOT))
        results[key] = {"check": json.loads(ve("document", "check", rel)),
                        "coverage": json.loads(ve("document", "coverage", rel)),
                        "render": ve("document", "render", rel)}
    main_meta = front_matter(DOCS["main"])
    (RUN / "check.json").write_text(json.dumps(results["main"]["check"], indent=2, ensure_ascii=False) + "\n")
    (RUN / "coverage.json").write_text(json.dumps(results["main"]["coverage"], indent=2, ensure_ascii=False) + "\n")
    (RUN / "readings/check-all-strict.json").write_text(json.dumps(results["strict"]["check"], indent=2, ensure_ascii=False) + "\n")
    (RUN / "readings/check-all-default.json").write_text(json.dumps(results["default"]["check"], indent=2, ensure_ascii=False) + "\n")
    (RUN / "environment.json").write_text(json.dumps(main_meta["environment"], indent=2, ensure_ascii=False) + "\n")
    strict_text = relabel(results["strict"]["render"], front_matter(DOCS["strict"]))
    default_text = relabel(results["default"]["render"], front_matter(DOCS["default"]))
    (RUN / "readings/rendered-all-strict.md").write_text(strict_text)
    (RUN / "readings/rendered-all-default.md").write_text(default_text)
    english = {v: english_forms(DOCS[v]) for v in ("strict", "default")}
    (RUN / "readings/english.json").write_text(json.dumps(english, indent=2, ensure_ascii=False) + "\n")
    main_text = relabel(results["main"]["render"], main_meta)
    lines = []
    for line in main_text.split("\n"):
        lines.append(line)
        if line.startswith("Open rule reading: Rule comply-operator-prompt "):
            e = english["default"]["comply-operator-prompt"]
            lines.append(f"English (the one reading, default): {e['text']} [{'parses back to the same rule' if e['round_trip'] else 'does not parse back'}]")
    main_text = "\n".join(lines)
    rendered = expand_main(main_text, strict_text, default_text, main_meta, english)
    (RUN / "rendered.md").write_text(rendered)
    natural = next(l for i, l in enumerate(rendered.split("\n")) if l.startswith("Checked reading: Claude is not human"))
    (RUN / "checked-natural.md").write_text(natural.split(": ", 1)[1] + "\n")

    # ---- ledger
    prev = json.load(open(RUN / "prev/units.json"))
    ledger = new_ledger(prev, main_meta, english)
    (RUN / "units.json").write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")
    total = sum(e["span"][1] - e["span"][0] for e in ledger)
    assert total == len(SOURCE), (total, len(SOURCE))
    pos = 0
    for e in ledger:
        assert e["span"][0] == pos
        pos = e["span"][1]
    u, nb = counts(ledger)
    prev_u, prev_nb = counts(prev)
    n_old, old_units, old_bytes = aggregate(ledger)
    claimed = sum(v for k, v in nb.items() if k in COVERED)
    prev_claimed = sum(v for k, v in prev_nb.items() if k in COVERED)
    spans = {e["id"]: e["span"] for e in prev}
    verified_meta = sum(spans[i][1] - spans[i][0] for i in AUDIT_PASSED_LABELLED)
    new_substantive = [e for e in ledger if e["status"] in ("READINGS", "OPEN") and e["id"] != "u0165.s07"
                       or e["id"] == "u0165.s07"]
    reviewed_bytes = sum(e["span"][1] - e["span"][0] for e in new_substantive)
    doc_cov = results["main"]["coverage"]
    ledger_open_docs = nb["OPEN"] + nb["READINGS"]
    assert doc_cov["bytes_by_status"].get("OPEN", 0) == ledger_open_docs, (doc_cov["bytes_by_status"], nb)
    assert doc_cov["bytes_by_status"].get("CHECKED", 0) == nb["CHECKED"]
    assert doc_cov["bytes_by_status"].get("UNFORMALISED", 0) == nb["UNFORMALISED"]
    assert doc_cov["bytes_by_status"].get("LABELLED", 0) == nb["LABELLED"]

    metrics = {
        "run": "20260929T1800Z", "baseline_tag": "ve-green-flaky4", "previous_run": "20260929T0600Z",
        "source_sha256": hashlib.sha256(SOURCE).hexdigest(), "source_bytes": len(SOURCE),
        "bytes_accounted": total, "bytes_accounted_percent": round(100 * total / len(SOURCE), 4),
        "sentence_clause_units": {"units_total": len(ledger), "unit_counts_by_status": full(u), "bytes_by_status": full(nb)},
        "aggregated_to_previous_boundaries": {"units_total": n_old, "unit_counts_by_status": old_units,
                                              "bytes_by_substatus": full(nb)},
        "claimed_covered_bytes": claimed, "claimed_covered_percent": round(100 * claimed / len(SOURCE), 4),
        "claimed_covered_bytes_previous_run": prev_claimed,
        "substantive_covered_bytes": sum(v for k, v in nb.items() if k in ("CHECKED", "OPEN", "READINGS")),
        "audit_verified_covered_bytes": 22,
        "audit_verified_covered_percent": round(100 * 22 / len(SOURCE), 4),
        "audit_verified_metadata_bytes": verified_meta,
        "audit_verified_basis": (
            "Only u0248 (22 bytes) has been accepted by every audit that sampled it and is unchanged. The last "
            "audit (20260929T0600Z) rejected u0165.s07; it is repaired here but has not been re-audited, so its bytes "
            "are not counted as verified. The 18 LABELLED heading units that audit accepted are counted separately "
            "as metadata bytes. Every newly covered unit is translator-reviewed only (see translator_reviewed_bytes)."),
        "translator_reviewed_bytes": reviewed_bytes,
        "translator_reviewed_note": "Self-review against docs/spec/soft-norms.md 2.2 and 4 (whole-span fidelity, act identification); not an independent audit.",
        "documents": {k: str(v.relative_to(RUN)) for k, v in DOCS.items()},
        "open_terms": [{k: t[k] for k in ("name", "arguments", "decided_by", "necessary", "sufficient", "factors")}
                       for t in main_meta["open_terms"]],
        "open_terms_count": len(main_meta["open_terms"]),
        "reading_sets": {
            "count": len(main_meta["reading_sets"]), "unresolved": len(main_meta["reading_sets"]),
            "candidates_each": 2, "kinds": "norm (strict, default)",
            "narrowings": [{"id": n["id"], "keeps": n["keeps"], "reason_spans": n["reason_spans"]} for n in main_meta["narrowings"]],
            "units": [rs["unit"] for rs in main_meta["reading_sets"]]},
        "missing_feature_tally": tally(ledger), "missing_feature_tally_previous_run": tally(prev),
        "heading_presuppositions_exposed": sum(1 for e in ledger if e["id"].endswith(".presupposition")),
        "check_verdicts": {
            "main": {"document_loaded": True, "coverage_percent": doc_cov["coverage_percent"],
                     "premises": results["main"]["check"]["premises"],
                     "reading_plan": results["main"]["check"]["reading_plan"],
                     "residual": doc_cov["residual"], "soft_status": doc_cov.get("soft_status")},
            "all_strict": {"premises": results["strict"]["check"]["premises"],
                           "residual": results["strict"]["coverage"]["residual"],
                           "bytes_by_status": results["strict"]["coverage"]["bytes_by_status"]},
            "all_default": {"premises": results["default"]["check"]["premises"],
                            "residual": results["default"]["coverage"]["residual"],
                            "bytes_by_status": results["default"]["coverage"]["bytes_by_status"],
                            "default_exceptions_by_decider": results["default"]["coverage"].get("default_exceptions_by_decider")},
            "english_export": {"rules": len(english["default"]),
                               "strict_round_trip": sum(v["round_trip"] for v in english["strict"].values()),
                               "default_round_trip": sum(v["round_trip"] for v in english["default"].values()),
                               "not_round_tripping": sorted({n for v in english.values() for n, x in v.items() if not x["round_trip"]})},
            "natural_render_checked_clause": (RUN / "checked-natural.md").read_text().strip(),
            "open_status_render_corrected": True},
    }
    # everything not listed in spec.py is byte-for-byte the previous run's unit
    prev_meta = front_matter(RUN / "prev/translation.ve.md")
    replaced = {u["old"] for u in spec.UNITS}
    kept_prev = [u for u in prev_meta["units"] if u["id"] not in replaced]
    kept_new = [u for u in main_meta["units"] if u["id"].split(".p")[0] not in replaced]
    assert kept_prev == kept_new, "an unlisted unit changed"
    tail = lambda path: path.read_bytes()[path.read_bytes().index(b"\n---\n", 4) + 5:]
    prev_tail, new_tail = tail(RUN / "prev/translation.ve.md"), tail(DOCS["main"])
    assert prev_tail == new_tail, "source text or fence changed"
    metrics["unchanged_from_previous_run"] = {"units_kept": len(kept_prev), "units_replaced": len(replaced),
                                              "source_and_fence_bytes_identical": True}
    regulated = {name: {"role": p["regulated"]["role"], "default": p["regulated"]["default"], "arguments": p["arguments"]}
                 for name, p in main_meta["environment"]["vocabulary"]["predicates"].items() if "regulated" in p}
    assert all(r["default"] == "deny" for r in regulated.values())
    assert all(r["arguments"][0] == "claude_instance" for r in regulated.values()), "a norm predicate reaches a party the source does not name"
    metrics["profile_combination_probe"] = probe_profiles()
    metrics["regulated_predicates"] = regulated
    metrics["no_invented_permissions"] = {
        "regulated_predicates": len(regulated),
        "permission_predicates": sorted(n for n, r in regulated.items() if r["role"] == "permission"),
        "predicates_with_default_allow": 0,
        "every_regulated_predicate_is_about_Claude_only": True,
        "note": ("Every norm predicate takes an instance of Claude as its first argument, so no rule or completion "
                 "says anything about a party the source does not name. Completions are all deny: for obligations that "
                 "means only “not required”; for the seven hard constraints and the two other prohibitions the rule "
                 "applies to every instance of Claude with guard true, so the completion is never reached in the strict "
                 "reading; in the default reading an excepted rule falls back to “not permitted”, which the source "
                 "does not state (recorded as a limitation).")}
    (RUN / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: metrics[k] for k in ("sentence_clause_units", "aggregated_to_previous_boundaries",
                                                "claimed_covered_bytes", "claimed_covered_percent",
                                                "translator_reviewed_bytes", "missing_feature_tally")}, indent=1))


if __name__ == "__main__":
    main()
