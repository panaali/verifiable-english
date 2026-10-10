"""RD-5 step 1: migrate the UDHR translation of run 20261006T1800Z to readings with their own vocabulary.

    uv run --frozen python usecases/udhr-pilot/run-20261010T1400Z/migrate.py [--commit bd6c7ab2] [--out DIR]

Reads the run at `bd6c7ab2` with `git show` (docs/spec/readings-defaults-PLAN.md, RD-5 step 1) and writes, into
`--out` (default: this directory), the migrated main document `translation.ve.md` and `unmigrated.json`:

- `readings@1` joins the main profiles, and `norm-defaults@0` with it: Lean checks a document whose readings carry
  their own vocabulary as a product of its sentences only under `norm-defaults@0` on the norms chain (RD-4b,
  `test_a_component_outside_the_completion_is_refused`). The main frame's one regulated predicate states its
  default (`allow`), so the profile changes nothing it says;
- every reading with a companion gets the companion unit's `content` and `kind`, and `companion.environment` and
  `companion.open_terms` from the companion's front matter (E4). Its recorded `meaning_id` is kept: Lean computes
  the identity over the companion's own environment and refuses a reading whose recorded id differs;
- each asserted reading without a companion gets one copied from the main frame: the main environment restricted to
  the symbols the assertion mentions, with the profiles, language and revision of the set's norm companions. Its
  `meaning_id` is proposed with the W1 identity over the copied environment (Python's, as for the companions) and
  checked by Lean the same way;
- no renaming (E1). Every set is offered to Lean by itself (`situations.py`): a set Lean's split refuses (two
  readings declaring a name differently, a merged frame the frozen decoders refuse) or whose pairs Lean does not all
  find separated stays as it was, on W2, and is listed with Lean's text. A set whose readings declare an open term
  differently stops the migration (E4), naming the set and Lean's text;
- W2's `models` are dropped from migrated sets, S1's `situations` and `distinguishing_models` are added. A set left
  on W2 keeps its models and readings; the identities W2 computes over the environment (model ids, a formula's
  meaning id) are recomputed for the new profiles (`tools/readings_s1_pilot.py` `_reidentified`).

Nothing here decides a reading's meaning, a separation or an admission: Lean does, and this script records its
answers.
"""
from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

RUN = "usecases/udhr-pilot/run-20261006T1800Z"
COMMIT = "bd6c7ab2"
ADDED_PROFILES = ("norm-defaults@0", "readings@1")
OPEN_TERM_DIFFERENCE = "declare open term"


def git_show(commit, path):
    return subprocess.run(["git", "show", f"{commit}:{path}"], cwd=ROOT, check=True, capture_output=True).stdout


def git_ls(commit, path):
    out = subprocess.run(["git", "ls-tree", "--name-only", f"{commit}:{path}"], cwd=ROOT, check=True,
                         capture_output=True).stdout.decode()
    return out.split()


def split_document(raw):
    """(front matter, source bytes) of a `ve-document@1` file."""
    _, front, source = raw.split(b"---\n", 2)
    return json.loads(front), source


def join_document(meta, source):
    return b"---\n" + json.dumps(meta, ensure_ascii=False).encode() + b"\n---\n" + source


def read_run(commit=COMMIT):
    """The run's main front matter and source, and each companion by (unit, candidate): its front matter."""
    meta, source = split_document(git_show(commit, f"{RUN}/translation.ve.md"))
    companions = {}
    for name in git_ls(commit, f"{RUN}/readings"):
        if name.endswith(".ve.md"):
            unit, candidate = name.split(".")[:2]
            companions[(unit, candidate)] = (name, split_document(git_show(commit, f"{RUN}/readings/{name}"))[0])
    return meta, source, companions


def companion_reading(reading, file_name, companion):
    """A reading carrying its companion inline: the companion unit's content and kind, its environment and open
    terms. A companion with other than one unit with content is refused by name (the migration stops)."""
    held = [u for u in companion["units"] if u.get("content") is not None]
    if len(held) != 1:
        raise SystemExit(f"migrate: {file_name} holds {len(held)} units with content, not one")
    [unit] = held
    return {"id": reading["id"], "kind": unit["kind"], "content": unit["content"], "meaning_id": reading["meaning_id"],
            "admission": {**reading["admission"], "distinguishing_models": {}},
            "companion": {"environment": companion["environment"], "open_terms": companion.get("open_terms", [])}}


def mentioned(formula, out=None):
    """The predicates, constants and quantified sorts a formula's JSON mentions, in order of first mention."""
    out = out if out is not None else {"predicates": [], "constants": [], "sorts": []}

    def add(kind, name):
        if name not in out[kind]:
            out[kind].append(name)
    if type(formula) is list and formula:
        head = formula[0]
        if head in ("forall", "exists") and len(formula) == 3 and type(formula[1]) is str:
            add("sorts", formula[1])
            mentioned(formula[2], out)
        elif head in ("unary", "binary", "atom", "predicate") and len(formula) >= 2 and type(formula[1]) is str:
            add("predicates", formula[1])
            for term in formula[2:]:
                mentioned(term, out)
        elif head == "const" and len(formula) == 2 and type(formula[1]) is str:
            add("constants", formula[1])
        else:
            for part in formula[1:]:
                mentioned(part, out)
    return out


def copied_environment(main_env, formula, like):
    """The main environment restricted to the symbols `formula` mentions (each predicate's and constant's sorts
    included), with `like`'s profiles, language and revision; and the declarations copied, as `kind name` lines."""
    vocabulary = main_env["vocabulary"]
    names = mentioned(formula)
    sorts = list(names["sorts"])
    for p in names["predicates"]:
        sorts += [s for s in vocabulary["predicates"][p]["arguments"] if s not in sorts]
    for c in names["constants"]:
        if vocabulary["constants"][c]["sort"] not in sorts:
            sorts.append(vocabulary["constants"][c]["sort"])
    env = {"language": like["language"], "profiles": like["profiles"], "spec_revision": like["spec_revision"],
           "vocabulary": {"constants": {c: vocabulary["constants"][c] for c in sorted(names["constants"])},
                          "predicates": {p: vocabulary["predicates"][p] for p in sorted(names["predicates"])},
                          "sorts": {s: vocabulary["sorts"][s] for s in sorted(sorts)}}}
    copied = [f"sort {s}" for s in sorted(sorts)] + [f"predicate {p}" for p in sorted(names["predicates"])] + \
        [f"constant {c}" for c in sorted(names["constants"])]
    return env, copied


def asserted_meaning_id(env, formula):
    """The W1 identity of `formula` over its copied environment (proposed; Lean checks it, 5 row 13)."""
    from ve.ast import formula_from_data
    from ve.environment import Environment
    from ve.identity import meaning_id
    environment = Environment(env)
    return meaning_id(environment, formula_from_data(environment, formula))


def candidate_sets(meta, companions):
    """Every reading set with its readings carrying companions (the migration's candidates), and the copied
    declarations of the asserted readings, by set."""
    out, copied = [], {}
    for item in meta["reading_sets"]:
        like = next((c["environment"] for (u, _), (_, c) in sorted(companions.items()) if u == item["unit"]), None)
        readings = []
        for r in item["readings"]:
            key = (item["unit"], r["id"])
            if key in companions:
                readings.append(companion_reading(r, *companions[key]))
            elif r.get("content") is not None and like is not None:
                env, lines = copied_environment(meta["environment"], r["content"], like)
                copied[f"{item['id']}:{r['id']}"] = lines
                readings.append({"id": r["id"], "kind": r["kind"], "content": r["content"],
                                 "meaning_id": asserted_meaning_id(env, r["content"]),
                                 "admission": {**r["admission"], "distinguishing_models": {}},
                                 "companion": {"environment": env, "open_terms": []}})
            else:
                raise SystemExit(f"migrate: {item['id']}:{r['id']} has neither a companion nor content")
        out.append({k: v for k, v in item.items() if k not in ("models", "readings")} | {"readings": readings})
    return out, copied


def main_environment(meta):
    env = copy.deepcopy(meta["environment"])
    env["profiles"] = sorted({*env["profiles"], *ADDED_PROFILES})
    return env


def migrate(commit=COMMIT, out=HERE, executable=None):
    """Write the migrated document and `unmigrated.json` into `out`; return the record written."""
    import situations
    meta, source, companions = read_run(commit)
    env = main_environment(meta)
    candidates, copied = candidate_sets(meta, companions)
    result = situations.separate(env, meta["units"], candidates, executable=executable)
    stops = [(s, text) for s, text in result["refused"].items() if OPEN_TERM_DIFFERENCE in text]
    if stops:
        raise SystemExit(f"migrate: stopped (E4): set {stops[0][0]}: {stops[0][1]}")
    from tools.readings_s1_pilot import _reidentified
    from ve.document import _environment
    originals = {item["id"]: item for item in meta["reading_sets"]}
    # A set left on W2 keeps its readings and models; only their identities, which are over the environment's
    # identity (now with the added profiles), are recomputed, as the S1 pilot rerun does (W2's own identities).
    environment = _environment(env)
    sets = [result["migrated"].get(item["id"]) or _reidentified(environment, item) for item in meta["reading_sets"]]
    migrated_meta = {**meta, "environment": env, "reading_sets": sets}
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "translation.ve.md").write_bytes(join_document(migrated_meta, source))
    record = {
        "source": f"{RUN} at {commit} (git show)",
        "profiles_added": list(ADDED_PROFILES),
        "sets": len(meta["reading_sets"]),
        "migrated": [s for s in originals if s in result["migrated"]],
        "not_migrated": [{"set": s, "reason": text} for s, text in result["refused"].items()] +
                        [{"set": s, "reason": "unseparated pairs", "pairs": pairs}
                         for s, pairs in result["unseparated"].items()],
        "copied_declarations": copied,
        "situations": {s: len(item.get("situations", {})) for s, item in result["migrated"].items()},
    }
    (out / "unmigrated.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--commit", default=COMMIT)
    parser.add_argument("--out", default=str(HERE))
    args = parser.parse_args(argv)
    record = migrate(args.commit, Path(args.out))
    print(json.dumps({k: (len(v) if type(v) in (list, dict) else v) for k, v in record.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
