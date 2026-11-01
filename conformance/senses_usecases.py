"""Pack coverage of the use cases (senses plan 7.2, B8): each English sentence re-read with the pack in place of
its declarations.

Every sentence is read twice by Lean, once per side, and never decided here: by `english.read` under the use case's
environment and overlay (the base), and by `senses.read` under the same environment without the predicates the pack
covers, with the pack. The script only counts: a sentence reads the same when both sides give one reading whose
formulas are equal up to renaming each covered predicate to one sense id (consistently over the use case); it needs a
line when the senses reading is open and a candidate of each open unit is that formula (Lean's resolving lines are
kept); it is switched when it reads the same with a non-default occurrence in Lean's sense map; anything else no
longer reads, with Lean's code and text. A sentence the base does not read is counted apart, with the base's code.
Sentences are read one at a time, never as a whole document (L70). Declaration lines (7.2): before, the environment
and overlay lines the covered predicates take; after, the pack lines they need (their sense lines and the sort lines
those senses name). The preamble lines the sentences need are counted apart.

Usage: `uv run python conformance/senses_usecases.py --write` (writes docs/senses/sn-b8/coverage.json) or `--check`.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve.backends import english_lean, senses as route  # noqa: E402
from ve.english import EnglishVocabulary  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.errors import CheckerUnavailable, VEError  # noqa: E402
from ve.parser import parse  # noqa: E402
from ve.printer import render  # noqa: E402

EVIDENCE = ROOT / "docs/senses/sn-b8/coverage.json"
PREDICATES = ("unary", "binary", "atom")


def _json(path: str):
    return json.loads((ROOT / path).read_text())


def _lines(path: str, label: str = "") -> list[str]:
    return [re.sub(label, "", line).strip() for line in (ROOT / path).read_text().splitlines() if line.strip()]


def _rendered(env_raw: dict, path: str) -> list[str]:
    """The English of each strict statement of a file, by Python's renderer (the base then reads it)."""
    env = Environment(env_raw)
    return [render(parse(env, line + "\n"), env, "ve_english", "per_statement").strip() for line in _lines(path)]


def _agent_policy() -> dict:
    raw = _json("usecases/agent-policy/environment.lean.json")
    raw["vocabulary"]["constants"].update(_json("usecases/agent-policy/log.vocabulary.json")["constants"])
    return raw


def _tagged(path: str) -> list[str]:
    """The sentences of an assist argument, one at a time, without the `[given]`-style tags of its paragraphs (a
    claimed sentence read alone has no premise, which the base reports)."""
    return [sentence for part in (ROOT / path).read_text().split("\n\n") if part.strip()
            for sentence in re.split(r"(?<=\.)\s+", re.sub(r"^\[[a-z]+\]\s*", "", part.strip()))]


def _same(*names: str) -> dict:
    return {name: name for name in names}


# Each use case: its pack, environment, overlay, the predicates the pack covers, each with the pack word that takes
# its place (docs/senses/sn-b8/SOURCES.md), and its English sentences.
USECASES = {
    "agent-policy": dict(pack="policies@1", env=_agent_policy, overlay=None,
                         covered={**_same("reads", "writes", "deletes", "contacts", "messages", "discloses"),
                                  "resides_in": "resides",
                                  **_same("confidential", "tracked", "allowlisted", "principal", "confirmed",
                                          "readonly", "privileged", "affordable", "reported")},
                         sentences=lambda: (_lines("usecases/agent-policy/policy.ve", r"^Rule \d+\. ")
                                            + _lines("usecases/agent-policy/log-schema.ve")
                                            + _lines("usecases/agent-policy/log.ve"))),
    "cedar-attributes": dict(pack="policies@1", env=lambda: _json("usecases/cedar-attributes/environment.json"),
                             overlay=None, covered={},
                             sentences=lambda: _rendered(_json("usecases/cedar-attributes/environment.json"),
                                                         "usecases/cedar-attributes/claim.ve")),
    "fluent": dict(pack="software-services@1", env=lambda: _json("examples/fluent/environment.json"), overlay=None,
                   covered=_same("deployed", "reviewed", "owns"),
                   sentences=lambda: _rendered(_json("examples/fluent/environment.json"), "examples/fluent/examples.ve")),
    "assist": dict(pack="software-services@1", env=lambda: _json("examples/assist/environment.json"),
                   overlay="examples/assist/environment.english.json", covered=_same("deployed", "reviewed", "safe"),
                   sentences=lambda: _tagged("examples/assist/argument.txt")),
}


def same_up_to_renaming(base, senses, covered, renaming: dict, inverse: dict) -> bool:
    """Equal formulas, except that each covered predicate of the base is one sense id on the senses side, the same
    id for it everywhere (`renaming`, kept over the use case) and an id no other predicate takes (`inverse`)."""
    if type(base) is not type(senses):
        return False
    if isinstance(base, list):
        if len(base) != len(senses):
            return False
        if base and base[0] in PREDICATES and len(base) > 1 and base[0] == senses[0]:
            name, symbol = base[1], senses[1]
            if name in covered:
                if renaming.setdefault(name, symbol) != symbol or inverse.setdefault(symbol, name) != name \
                        or symbol == name:
                    return False
            elif symbol != name:
                return False
            return all(same_up_to_renaming(b, s, covered, renaming, inverse) for b, s in zip(base[2:], senses[2:]))
        return all(same_up_to_renaming(b, s, covered, renaming, inverse) for b, s in zip(base, senses))
    return base == senses


def reduced(env_raw: dict, overlay: dict | None, covered) -> tuple[Environment, dict | None]:
    """The environment and overlay without the covered predicates: the pack takes their place."""
    raw = json.loads(json.dumps(env_raw))
    for name in covered:
        raw["vocabulary"]["predicates"].pop(name)
    env = Environment(raw)
    if overlay is None:
        return env, None
    trimmed = {**overlay, "environment_id": env.environment_id,
               "predicates": {k: v for k, v in overlay.get("predicates", {}).items() if k not in covered}}
    return env, trimmed


def classify(env: Environment, overlay, senses_env: Environment, senses_overlay, pack: bytes, sentence: str,
             covered, renaming: dict, inverse: dict) -> dict:
    """One sentence, read once on each side."""
    row = {"sentence": sentence}
    try:
        base = english_lean.read(env, sentence, EnglishVocabulary(env, vocabulary=overlay),
                                 {} if overlay is None else {"vocabulary": overlay}).response
        if base["status"] != "one":
            return {**row, "class": "base_unread", "code": base.get("code"), "text": base.get("text")}
        reading = route.read(senses_env, sentence, [pack], overlay=senses_overlay)["reading"]
    except (VEError, CheckerUnavailable) as exc:
        return {**row, "class": "unavailable", "text": str(exc)}
    formulas = base["ast"]
    units = reading.get("units", [])
    if reading["status"] in ("one", "open") and len(units) == len(formulas):
        lines, ok = [], True
        for formula, unit in zip(formulas, units):
            if unit["candidates"]:
                match = next((c for c in unit["candidates"] if same_up_to_renaming(
                    formula, c["formula"], covered, dict(renaming), dict(inverse))), None)
                ok = ok and match is not None and same_up_to_renaming(formula, match["formula"], covered, renaming,
                                                                         inverse)
                lines += [match["lines"]] if match else []
            else:
                ok = ok and same_up_to_renaming(formula, unit["formula"], covered, renaming, inverse)
        if ok and lines:
            return {**row, "class": "needs_line", "lines": lines}
        if ok:
            switched = any(not entry["is_default"] for entry in reading["sense_map"])
            return {**row, "class": "switched" if switched else "same"}
    return {**row, "class": "no_longer_reads", "status": reading["status"], "code": reading.get("code"),
            "text": reading.get("text"), "details": reading.get("details") or reading.get("failure")}


def declaration_lines(env_raw: dict, overlay: dict | None, covered) -> int:
    """The environment and overlay lines the covered predicates take (one per declared field)."""
    predicates = env_raw["vocabulary"]["predicates"]
    entries = (overlay or {}).get("predicates", {})
    return sum(1 + len(predicates[name]) + len(entries.get(name, {})) for name in covered)


def pack_lines(senses_env: Environment, senses_overlay, pack: bytes, covered: dict, renaming: dict) -> dict:
    """The pack lines the covered predicates need (plan 7.2's "after" on a use case): the sense line of each one's
    word and the sort lines those senses' kinds name. Lean ties each word to its sense ids (`senses.project` over
    that word alone); a predicate the sentences read must be renamed to that id. A word that is not one sense line
    Lean reads it to stops the measure: the count would have no line to pick."""
    data = json.loads(pack)
    senses = set()
    for name, word in covered.items():
        entries = [i for i, sense in enumerate(data["senses"]) if sense["word"] == word]
        symbols = set()
        if len(entries) == 1:
            projected = route.project(senses_env, [pack], "", [word], overlay=senses_overlay)["projection"]
            symbols = set(projected["environment"]["vocabulary"]["predicates"]) - set(senses_env.predicates)
        if len(symbols) != 1 or name in renaming and renaming[name] not in symbols:
            raise ValueError(f"the pack sense of {name!r} ({word!r}) is not one line Lean reads it to")
        senses |= set(entries)
    kinds = {kind for i in senses for kind in data["senses"][i]["kinds"]}
    return {"senses": len(senses), "sorts": sum(1 for sort in data["sorts"] if sort["name"] in kinds)}


def negatives_removed(env_raw: dict, overlay: dict | None, covered) -> int:
    """Hand-written negatives of covered predicates whose wording is a simple adjective (`{0} is not w`)."""
    entries = [env_raw["vocabulary"]["predicates"][name] for name in covered]
    entries += [(overlay or {}).get("predicates", {}).get(name, {}) for name in covered]
    return sum(1 for entry in entries if re.fullmatch(r"\{0\} is not [a-z]+", entry.get("negative_verbalisation", "")))


def measure(names=None) -> dict:
    out = {}
    for name, case in USECASES.items():
        if names and name not in names:
            continue
        env_raw = case["env"]()
        overlay = _json(case["overlay"]) if case["overlay"] else None
        pack = (ROOT / "ve/senses/packs" / (case["pack"] + ".json")).read_bytes()
        env = Environment(env_raw)
        senses_env, senses_overlay = reduced(env_raw, overlay, case["covered"])
        renaming, inverse = {}, {}
        rows = [classify(env, overlay, senses_env, senses_overlay, pack, sentence, case["covered"], renaming, inverse)
                for sentence in case["sentences"]()]
        counts = {}
        for row in rows:
            counts[row["class"]] = counts.get(row["class"], 0) + 1
        needed = pack_lines(senses_env, senses_overlay, pack, case["covered"], renaming)
        out[name] = {"pack": case["pack"], "sentences": len(rows), "counts": counts, "renaming": renaming,
                     "declaration_lines": {"before": declaration_lines(env_raw, overlay, case["covered"]),
                                           "after": needed["senses"] + needed["sorts"],
                                           "pack_senses": needed["senses"], "pack_sorts": needed["sorts"]},
                     "preamble_lines": len({line for row in rows for line in row.get("lines", [])}),
                     "negatives_removed": negatives_removed(env_raw, overlay, case["covered"]),
                     "rows": [row for row in rows if row["class"] not in ("same",)]}
    return out


def evidence_text(table: dict) -> str:
    """The table as saved: per use case its summary on one line, then one line per row that does not read the same."""
    out = []
    for name, entry in sorted(table.items()):
        summary = {key: value for key, value in entry.items() if key != "rows"}
        rows = [json.dumps(row, ensure_ascii=False, sort_keys=True) for row in entry["rows"]]
        out.append(f' {json.dumps(name)}: {{"summary": {json.dumps(summary, ensure_ascii=False, sort_keys=True)}, '
                   '"rows": [' + ("\n  " + ",\n  ".join(rows) + "\n " if rows else "") + "]}")
    return "{\n" + ",\n".join(out) + "\n}\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    table = measure()
    text = evidence_text(table)
    if args.write:
        EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
        EVIDENCE.write_text(text)
    if args.check and EVIDENCE.read_text() != text:
        print(f"{EVIDENCE} differs from a fresh measurement", file=sys.stderr)
        return 1
    print(json.dumps({name: {"sentences": t["sentences"], **t["counts"]} for name, t in table.items()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
