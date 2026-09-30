#!/usr/bin/env python3
"""Run VE on the built documents, write the ledger, rendering and metrics.

Run after build.py, from anywhere:  uv run python usecases/claude-constitution-pilot/run-20260930T1800Z/finish.py
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
# Units accepted as faithful by the audits of this lineage that are unchanged in this run.
# 20260929T0600Z audit (19/20): 18 LABELLED units and the CHECKED unit u0248.
# 20260929T1800Z audit (18/20): 14 LABELLED heading markers, 3 READINGS units and 1 OPEN unit.
# 20260930T0600Z audit (18/20): 5 LABELLED units, 8 LABELLED heading markers, 4 READINGS units and 1 OPEN unit;
# it rejected u0165.s05 and u0165.s06 (repaired in this run, not re-audited).
AUDIT_PASSED_LABELLED = ["u0023", "u0032.heading", "u0069.heading", "u0095.heading", "u0103", "u0108", "u0126",
                         "u0143.heading", "u0162.heading", "u0174.heading", "u0219.heading", "u0254.heading",
                         "u0268.heading", "u0277", "u0282", "u0286.heading", "u0294", "u0298",
                         "u0002.heading", "u0008.heading", "u0013.heading", "u0040.heading", "u0042.heading",
                         "u0075.heading", "u0083.heading", "u0151.heading", "u0195.heading", "u0257.heading",
                         "u0265", "u0027.heading", "u0130.heading", "u0207.heading", "u0260.heading"]
AUDIT_PASSED_SUBSTANTIVE = ["u0248", "u0052.s01", "u0168.s01", "u0263.s04.p2", "u0073.s05",
                            "u0036.s05", "u0165.s01", "u0165.s04"]
AUDIT_REJECTED_1800Z = ["u0156.s03", "u0165.s03"]
AUDIT_REJECTED_0600Z = ["u0165.s05", "u0165.s06"]
# Units with the same defect as the two rejected ones (a prohibition whose default reading fell back to "not
# permitted"), repaired together with them.
REPAIRED = ["u0165.s01", "u0165.s02", "u0165.s03", "u0165.s04", "u0165.s05", "u0165.s06", "u0165.s07",
            "u0156.s03", "u0125.s04.p2"]
# Of those, the 20260930T0600Z audit accepted u0165.s01 and u0165.s04 (unchanged here) and rejected u0165.s05, s06.
REPAIRED_NOT_REAUDITED = [i for i in REPAIRED if i not in ("u0165.s01", "u0165.s04")]


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
REPAIR_TEXT = {
    "u0156.s03": "Rejected by the 20260929T1800Z audit (the defeasible reading fell back to \u201cnot permitted\u201d, which the "
                 "source does not say). Rewritten as a duty to avoid the act, so an excepted case reads \u201cnot required\u201d.",
    "u0165.s03": "Rejected by the 20260929T1800Z audit (the defeasible reading fell back to \u201cnot permitted\u201d; the act "
                 "phrase and both English readings dropped \u201cif deployed\u201d; the damage clause was attached to "
                 "cyberweapons by the act phrase). Rewritten as a duty to avoid the act, guarded by the open case atom "
                 "carrying the source\u2019s words, so nothing is dropped or attached.",
}
REPAIR_TEXT["u0165.s05"] = ("Rejected by the 20260930T0600Z audit (the act phrase said \u201cassisting an attempt on humanity\u201d, "
                            "so \u201cengage\u201d survived only in the guard). The act phrase is now the neutral pointer "
                            "\u201cthe participation in\u201d; the source\u2019s words (\u201cengaging or assisting in an "
                            "attempt to kill or disempower \u2026\u201d) stay in the case atom. Not re-audited.")
REPAIR_TEXT["u0165.s06"] = ("Rejected by the 20260930T0600Z audit (same defect as u0165.s05). The act phrase is now the neutral "
                            "pointer \u201cthe involvement in\u201d; the source\u2019s words (\u201cengaging or assisting any "
                            "individual or group with an attempt to seize \u2026\u201d) stay in the case atom. Not re-audited.")
SAME_DEFECT_TEXT = ("Same defect as the two units the 20260929T1800Z audit rejected (a prohibition written as a permission "
                    "whose default reading fell back to \u201cnot permitted\u201d), found by this run\u2019s own review of "
                    "the class; rewritten the same way. Not audited.")


def new_ledger(prev, main_meta, english, prev1800, separation):
    by_old = {u["old"]: u for u in spec.UNITS}
    prev1800 = {e["id"]: e for e in prev1800}
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
                      "status_in_previous_run": prev1800[uid]["status"] if uid in prev1800 else None,
                      "note": item["readings_note"]}
            record["case_atoms"] = {a: atom_words(main_meta["environment"], a) for a in guard_atoms(item)}
            if uid in REPAIRED:
                record["audit_repair"] = REPAIR_TEXT.get(uid, SAME_DEFECT_TEXT)
                if uid in ("u0165.s01", "u0165.s04"):
                    record["audit_repair"] = SAME_DEFECT_TEXT.replace("Not audited.", "Accepted as faithful by the 20260930T0600Z audit; unchanged since.")
            if uid in separation:
                record["separating_situation"] = separation[uid]
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
    for record in out:
        if record["id"].endswith(".heading") and "open_terms" in record:
            del record["open_terms"]  # the tag belongs to the title, not to the bare marker (1800Z audit, minor issue)
    return out



# ------------------------------------------------------------------ separating situations
def separating_situations(env_dict):
    """For every reading set, a one-element situation in which the strict and the default reading of the rule give
    different outcomes, computed with VE's own soft elaboration and evaluator.

    VE itself cannot check this: a candidate norm carries no content (finding F2), so the model recorded inside the
    reading set is only a placeholder. This is the check the reading set should carry. The situation makes every
    guard atom true and every carve-out atom false; in the default reading the rule\u2019s named exception is true."""
    from ve.evaluate import _Evaluator
    from ve.model import FiniteModel
    from ve.softnorms import SoftEnvironment, SoftNormDocument
    import build
    env = SoftEnvironment(env_dict)

    def positive_atoms(f, out):
        if isinstance(f, list):
            if f and f[0] in ("unary", "binary"):
                out.add(f[1])
            for part in f[1:]:
                positive_atoms(part, out)

    def outcome(item, mode, excepted):
        doc = SoftNormDocument(env, [build.norm_block(item, mode)])
        tree = doc.elaborated
        base = tree.base_environment()
        guard = set()
        positive_atoms(item["guard"], guard)
        data = {"complete": True, "domains": {sort: [sort + "0"] for sort in base.sorts},
                "constants": {c: env_dict["vocabulary"]["constants"][c]["sort"] + "0"
                              for c in env_dict["vocabulary"]["constants"]},
                "relations": {p: ([[sort + "0" for sort in d.arguments]]
                                  if p in guard or (excepted and p.startswith("soft__excepted__")) else [])
                              for p, d in base.predicates.items()}}
        model = FiniteModel.from_dict(base, data)
        evaluator = _Evaluator(base, model, 1_000_000, trace=False)
        for label, premise in doc.extended_env.soft_premises:
            assert evaluator.formula(premise, ())[0], label
        decl = tree.env.predicates[item["predicate"]]
        bindings = tuple(zip(reversed(decl.arguments), reversed([sort + "0" for sort in decl.arguments])))
        value, _ = evaluator.formula(tree.outcome(item["predicate"], base=True), bindings)
        return bool(value), model.model_id

    out = {}
    for item in spec.UNITS:
        if item["kind"] != "norm-force":
            continue
        uid = item["old"] if "pieces" not in item else f"{item['old']}.p2"
        strict_value, strict_model = outcome(item, "strict", False)
        default_value, default_model = outcome(item, "default", True)
        assert strict_value and not default_value, (uid, strict_value, default_value)
        out[uid] = {"situation": "one situation of each sort; every guard atom of the rule true, every carve-out false",
                    "strict_reading_outcome": "required" if strict_value else "not required",
                    "default_reading_outcome_when_exception_applies": "required" if default_value else "not required",
                    "strict_model_id": strict_model, "default_model_id": default_model,
                    "note": "computed by finish.py with VE\u2019s evaluator; not admitted by the document check"}
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
LABEL = re.compile(r"^(Checked reading|Open rule reading|Open reading): (Rule (\S+) .*)$")


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



def guard_atoms(item):
    """The base atoms named by a rule\u2019s guard and carve-outs, in order of first appearance."""
    found = []

    def walk(f):
        if isinstance(f, list):
            if f and f[0] in ("unary", "binary") and f[1] not in found:
                found.append(f[1])
            for part in f[1:]:
                walk(part)
    walk(item["guard"])
    for u in item["unless"]:
        walk(u)
    return found


def atom_words(env_meta, name):
    """The verbalisation the environment declares for a base atom, with slots named."""
    text = env_meta["vocabulary"]["predicates"][name]["verbalisation"]
    return text.replace("{0}", "the situation").replace("{1}", "the situation")


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
            atoms = guard_atoms(item)
            if atoms:
                out.append("Classifications named above, in the words the environment declares for them (the renderer prints only "
                           "the name; each is an open term whose test the source does not give):")
                for atom in atoms:
                    out.append(f"  \u201c{atom}\u201d: {atom_words(main_meta['environment'], atom)}.")
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
    for extra in ("closure@0", "order@0", "time@0", "reports@0", "alternatives@0", "speech-acts@0", "definitions@0", "data@0", "rights@0", "risk@0", "ve.discourse@1"):
        m = json.loads(json.dumps(meta))
        m["environment"]["profiles"] = sorted(set(m["environment"]["profiles"]) | {extra})
        if extra == "rights@0":  # needs the rights block (docs/spec/rights.md 3.1); minimal one, no right declared
            m["environment"]["vocabulary"]["rights"] = {"holders": ["user"], "bearers": ["claude_instance"], "protected": [], "alters": {}}
        if extra == "ve.discourse@1":  # needs ve-document@2 and a manifest (docs/spec/discourse.md 1.1); minimal one: the root anchor
            m["format"] = "ve-document@2"
            m["discourse"] = {"version": "ve.discourse@1", "anchors": [{"id": "doc", "kind": "document", "label": "Claude's constitution", "span": [0, len(SOURCE)]}]}
        with tempfile.NamedTemporaryFile("wb", suffix=".ve.md", delete=False) as handle:
            handle.write(b"---\n" + json.dumps(m, ensure_ascii=False, separators=(",", ":")).encode() + b"\n---\n" + tail)
        proc = subprocess.run([sys.executable, "-m", "ve", "document", "check", handle.name], cwd=ROOT,
                              capture_output=True, text=True)
        if extra == "ve.discourse@1":  # the admission is Lean's; the check above may print Python's own diagnostic instead
            from ve.discourse import lean_admission
            row = lean_admission(Path(handle.name).read_bytes(), Path(handle.name).parent)
            result["ve.discourse@1: the Lean route's own verdict"] = row.get("error") if row.get("status") == "error" else row.get("status")
        Path(handle.name).unlink()
        result[extra] = ("accepted at document-check level" if proc.returncode == 0
                         else (proc.stderr.strip().splitlines() or ["rejected"])[-1].split(": ", 1)[-1])
    # The same manifest on the norms-only base translation (norms@0, no soft-norms@0): does the discourse route take any norm?
    base = (RUN / "prev/translation.ve.md").read_bytes()
    end = base.index(b"\n---\n", 4)
    meta, tail = json.loads(base[4:end]), base[end + 5:]
    meta["environment"]["profiles"] = sorted(set(meta["environment"]["profiles"]) | {"ve.discourse@1"})
    meta["format"] = "ve-document@2"
    meta["discourse"] = {"version": "ve.discourse@1", "anchors": [{"id": "doc", "kind": "document", "label": "Claude's constitution", "span": [0, len(SOURCE)]}]}
    with tempfile.NamedTemporaryFile("wb", suffix=".ve.md", delete=False) as handle:
        handle.write(b"---\n" + json.dumps(meta, ensure_ascii=False, separators=(",", ":")).encode() + b"\n---\n" + tail)
    proc = subprocess.run([sys.executable, "-m", "ve", "document", "check", handle.name], cwd=ROOT, capture_output=True, text=True)
    Path(handle.name).unlink()
    result["ve.discourse@1 on the norms@0-only translation"] = ("accepted at document-check level" if proc.returncode == 0
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
    prev1800 = json.load(open(RUN / "prev0600Z/units.json"))  # the previous run's ledger (20260930T0600Z)
    separation = separating_situations(main_meta["environment"])
    (RUN / "readings/separating-situations.json").write_text(json.dumps(separation, indent=2, ensure_ascii=False) + "\n")
    ledger = new_ledger(prev, main_meta, english, prev1800, separation)
    (RUN / "units.json").write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")
    total = sum(e["span"][1] - e["span"][0] for e in ledger)
    assert total == len(SOURCE), (total, len(SOURCE))
    pos = 0
    for e in ledger:
        assert e["span"][0] == pos
        pos = e["span"][1]
    u, nb = counts(ledger)
    prev_u, prev_nb = counts(prev1800)
    n_old, old_units, old_bytes = aggregate(ledger)
    claimed = sum(v for k, v in nb.items() if k in COVERED)
    prev_claimed = sum(v for k, v in prev_nb.items() if k in COVERED)
    spans = {e["id"]: e["span"] for e in ledger}
    width = lambda ids: sum(spans[i][1] - spans[i][0] for i in ids)
    status = {e["id"]: e["status"] for e in ledger}
    assert all(status[i] in COVERED for i in AUDIT_PASSED_LABELLED + AUDIT_PASSED_SUBSTANTIVE)
    for i in AUDIT_PASSED_LABELLED + AUDIT_PASSED_SUBSTANTIVE:  # only units unchanged since the audit count
        assert prev1800[[e["id"] for e in prev1800].index(i)]["span"] == spans[i], i
    verified_meta = width(sorted(set(AUDIT_PASSED_LABELLED)))
    verified_substantive = width(AUDIT_PASSED_SUBSTANTIVE)
    repaired_bytes = width(REPAIRED_NOT_REAUDITED)
    reviewed_bytes = repaired_bytes
    doc_cov = results["main"]["coverage"]
    ledger_open_docs = nb["OPEN"] + nb["READINGS"]
    assert doc_cov["bytes_by_status"].get("OPEN", 0) == ledger_open_docs, (doc_cov["bytes_by_status"], nb)
    assert doc_cov["bytes_by_status"].get("CHECKED", 0) == nb["CHECKED"]
    assert doc_cov["bytes_by_status"].get("UNFORMALISED", 0) == nb["UNFORMALISED"]
    assert doc_cov["bytes_by_status"].get("LABELLED", 0) == nb["LABELLED"]

    metrics = {
        "run": "20260930T1800Z", "baseline_tag": "ve-green-risk", "previous_run": "20260930T0600Z",
        "source_sha256": hashlib.sha256(SOURCE).hexdigest(), "source_bytes": len(SOURCE),
        "bytes_accounted": total, "bytes_accounted_percent": round(100 * total / len(SOURCE), 4),
        "sentence_clause_units": {"units_total": len(ledger), "unit_counts_by_status": full(u), "bytes_by_status": full(nb)},
        "aggregated_to_previous_boundaries": {"units_total": n_old, "unit_counts_by_status": old_units,
                                              "bytes_by_substatus": full(nb)},
        "claimed_covered_bytes": claimed, "claimed_covered_percent": round(100 * claimed / len(SOURCE), 4),
        "claimed_covered_bytes_previous_run": prev_claimed,
        "substantive_covered_bytes": sum(v for k, v in nb.items() if k in ("CHECKED", "OPEN", "READINGS")),
        "audit_verified_covered_bytes": verified_substantive,
        "audit_verified_covered_percent": round(100 * verified_substantive / len(SOURCE), 4),
        "audit_verified_covered_units": AUDIT_PASSED_SUBSTANTIVE,
        "audit_verified_metadata_bytes": verified_meta,
        "audit_verified_metadata_percent": round(100 * verified_meta / len(SOURCE), 4),
        "audit_verified_basis": (
            "Audit-verified means accepted as faithful by an independent audit of this lineage AND unchanged (same span, "
            "same status, same translation content) in this run. Substantive: u0248 (CHECKED; 20260929T0600Z audit); from the "
            "20260929T1800Z audit u0052.s01, u0168.s01, u0263.s04.p2 (READINGS) and u0073.s05 (OPEN); from the 20260930T0600Z "
            "audit u0036.s05, u0165.s01 and u0165.s04 (READINGS), which this run did not touch. Metadata: the LABELLED "
            "units and heading markers those audits accepted. The four units rejected by the two latest audits "
            "(u0156.s03, u0165.s03 by 20260929T1800Z; u0165.s05, u0165.s06 by 20260930T0600Z) and the three other "
            "units with the same defect (u0165.s02, u0165.s07, u0125.s04.p2) are repaired but not re-audited, so they "
            "are counted as claimed, not as verified. Every other covered unit is unaudited."),
        "audit_rejected_units_and_repair_status": {
            "rejected_by_20260929T1800Z_audit": AUDIT_REJECTED_1800Z,
            "rejected_by_20260930T0600Z_audit": AUDIT_REJECTED_0600Z,
            "repaired_same_defect_class": REPAIRED,
            "of_which_accepted_by_20260930T0600Z_audit_unchanged": ["u0165.s01", "u0165.s04"],
            "repaired_not_reaudited": REPAIRED_NOT_REAUDITED,
            "bytes_repaired_not_reaudited": repaired_bytes,
            "status_now": {i: status[i] for i in REPAIRED},
            "counted_as_audit_verified": False},
        "claimed_but_not_audit_verified_bytes": claimed - verified_substantive - verified_meta,
        "translator_reviewed_bytes": reviewed_bytes,
        "translator_reviewed_note": "The seven repaired units not yet re-audited were re-read against their source words by the translator (SELF-REVIEW.md); not an independent audit.",
        "documents": {k: str(v.relative_to(RUN)) for k, v in DOCS.items()},
        "open_terms": [{k: t[k] for k in ("name", "arguments", "decided_by", "necessary", "sufficient", "factors")}
                       for t in main_meta["open_terms"]],
        "open_terms_count": len(main_meta["open_terms"]),
        "reading_sets": {
            "count": len(main_meta["reading_sets"]), "unresolved": len(main_meta["reading_sets"]),
            "candidates_each": 2, "kinds": "norm (strict, default)",
            "narrowings": [{"id": n["id"], "keeps": n["keeps"], "reason_spans": n["reason_spans"]} for n in main_meta["narrowings"]],
            "units": [rs["unit"] for rs in main_meta["reading_sets"]]},
        "missing_feature_tally": tally(ledger), "missing_feature_tally_previous_run": tally(prev1800),
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
    # everything not listed in spec.py is byte-for-byte the base translation's unit (as in every run of this lineage)
    prev_meta = front_matter(RUN / "prev/translation.ve.md")
    replaced = {u["old"] for u in spec.UNITS}
    kept_prev = [u for u in prev_meta["units"] if u["id"] not in replaced]
    kept_new = [u for u in main_meta["units"] if u["id"].split(".p")[0] not in replaced]
    assert kept_prev == kept_new, "an unlisted unit changed"
    tail = lambda path: path.read_bytes()[path.read_bytes().index(b"\n---\n", 4) + 5:]
    prev_tail, new_tail = tail(RUN / "prev/translation.ve.md"), tail(DOCS["main"])
    assert prev_tail == new_tail, "source text or fence changed"
    # ... and compared with the previous run's ledger (20260930T0600Z): which entries differ at all
    strip = lambda e: {k: v for k, v in e.items() if k not in ("audit_repair", "separating_situation", "status_in_previous_run",
                                                              "case_atoms")}
    old_by_id = {e["id"]: e for e in prev1800}
    changed = sorted(e["id"] for e in ledger if e["id"] not in old_by_id or strip(e) != strip(old_by_id[e["id"]]))
    assert set(changed) <= set(AUDIT_REJECTED_0600Z), changed
    assert len(old_by_id) == len(ledger)
    metrics["unchanged_from_previous_run"] = {
        "units_kept_from_base_translation": len(kept_prev), "units_replaced_by_spec": len(replaced),
        "source_and_fence_bytes_identical": True,
        "ledger_entries_identical_to_20260930T0600Z": len(ledger) - len(changed),
        "ledger_entries_changed": changed,
        "changed_reason": {"repaired after the 20260930T0600Z audit (act phrase made a neutral pointer)": [i for i in changed if i in AUDIT_REJECTED_0600Z]}}
    regulated = {name: {"role": p["regulated"]["role"], "default": p["regulated"]["default"], "arguments": p["arguments"]}
                 for name, p in main_meta["environment"]["vocabulary"]["predicates"].items() if "regulated" in p}
    assert all(r["default"] == "deny" for r in regulated.values())
    assert all(r["arguments"][0] == "claude_instance" for r in regulated.values()), "a norm predicate reaches a party the source does not name"
    assert all(r["role"] == "obligation" for r in regulated.values()), "a permission predicate would say what is allowed"
    metrics["profile_combination_probe"] = probe_profiles()
    metrics["regulated_predicates"] = regulated
    metrics["no_invented_permissions"] = {
        "regulated_predicates": len(regulated),
        "permission_predicates": sorted(n for n, r in regulated.items() if r["role"] == "permission"),
        "predicates_with_default_allow": 0,
        "every_regulated_predicate_is_about_Claude_only": True,
        "every_regulated_predicate_is_an_obligation": True,
        "note": ("Every norm predicate is a duty of an instance of Claude (first argument), so no rule or completion says "
                 "anything about a party the source does not name, and no predicate says what is permitted. The "
                 "completion of every predicate is deny, which for a duty means only \u201cnot required\u201d. The nine "
                 "prohibitions are written as duties to avoid the act, so a case the defeasible reading lifts (its exception "
                 "applies) reads \u201cnot required to avoid\u201d, the meaning of a lifted duty, and not \u201cnot permitted\u201d, "
                 "which the source does not say. Limitation that remains: the language has no third outcome \u201cunspecified\u201d, "
                 "so \u201cnot required\u201d is still a completion that the source never states.")}
    metrics["risk_probe"] = json.loads((RUN / "probes/risk-probe.json").read_text())
    metrics["discourse_probe"] = json.loads((RUN / "probes/discourse-probe.json").read_text())
    metrics["rights_reading_probe"] = json.loads((RUN / "probes/rights-reading-probe.json").read_text())
    metrics["separating_situations"] = {"reading_sets": len(separation), "all_separate_strict_from_default": True,
                                        "file": "readings/separating-situations.json",
                                        "note": "The model stored inside each reading set is a placeholder (a candidate norm carries no "
                                                "content, so VE cannot check that it separates the readings); the separation is shown "
                                                "here by computation."}
    (RUN / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: metrics[k] for k in ("sentence_clause_units", "aggregated_to_previous_boundaries",
                                                "claimed_covered_bytes", "claimed_covered_percent",
                                                "translator_reviewed_bytes", "missing_feature_tally")}, indent=1))


if __name__ == "__main__":
    main()
