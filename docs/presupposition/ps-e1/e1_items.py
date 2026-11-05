"""PS-E1 frozen items: built from scenarios.json with the option wording of spec 2.5 and audited against the plan."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "docs/research/presupposition-E1"
ITEMS = DATA / "items.jsonl"
QUESTION = "What does the sentence say about this situation?"
FALSE, TRUE = "The sentence is false in this situation.", "The sentence is true in this situation."
SILENT, RULE_SILENT = "The sentence says nothing about this situation.", "This rule decides nothing in this situation."
CANNOT = "I cannot tell."
CELLS = {"top": "TOP", "negated": "NEG", "antecedent": "ANT", "consequent": "CON", "rule_act": "ACT", "rule_guard": "GRD"}
RULE_CELLS, E_CELLS = {"rule_act", "rule_guard"}, {"negated", "antecedent"}
CARRIER = {"a": "asserted", "b": "conditioned", "c": "assumed", "d": "none", "e": "in_place"}
FILTERS = {"if": 3, "and": 3, "or": 2, "every": 2, "rule_guard": 2}


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def took_for_granted(pre):
    return f"The sentence takes for granted that {pre}, so this situation goes against the text."


def options(cell, pre):
    """The options the plan allows in a cell (plan PS-E1, spec 2.5)."""
    rows = {} if cell == "rule_act" else {"a": FALSE}
    rows |= {"b": RULE_SILENT if cell in RULE_CELLS else SILENT, "c": took_for_granted(pre), "d": CANNOT}
    return rows | ({"e": TRUE} if cell in E_CELLS else {})


def prompt(item):
    """The user message of a trial; the ids, the family and the key never reach the reader."""
    head = f'Section heading: "{item["heading"]}"\n' if item["heading"] else ""
    opts = "\n".join(f"({k}) {v}" for k, v in item["options"].items())
    return f'{head}Sentence: "{item["sentence"]}"\nSituation: {item["situation"]}\nQuestion: {item["question"]}\n{opts}\n'


def model(rels):
    pairs = ", ".join(f'("{p}", {json.dumps(t)})' for p, t in rels.items())
    return f'model [("entity", ["w", "c", "x", "y"]), ("agent", ["ag"])] [{pairs}] [("w", "w"), ("c", "c")]'


def target(sc, cell):
    binders = 1 if cell in RULE_CELLS else 0
    if sc["row"] == "generic":
        body = sc["body_act"] if cell == "rule_act" else sc["body"]
        reading = f'generic (wa "{sc["pre_atom"]}") (wa "{body}")'
    else:
        pred = sc["P_act"] if cell == "rule_act" else sc.get("P_guard", sc["P"]) if cell == "rule_guard" else sc["P"]
        n = f"{binders} " if sc["row"] == "definite" else ""
        reading = f'{sc["row"]} {n}"entity" (dr "{sc["D"]}" "c") (va "{pred}")'
    frame = {"top": ".hole", "negated": ".notF .hole", "antecedent": f'.impL .hole (wa "{sc["R"]}")',
             "consequent": f'.impR (wa "{sc["L"]}") .hole', "rule_act": '.allF "agent" (.impR .top .hole)',
             "rule_guard": f'.allF "agent" (.impL .hole (wa "{sc["A"]}"))'}[cell]
    rels = {sc["L"]: [["w"]]} if cell == "consequent" else {}
    situation = f'{sc["L_text"]} {sc["situation"]}' if cell == "consequent" else sc["situation"]
    opts = options(cell, sc["pre"])
    return {"id": f'T-{sc["code"]}-{CELLS[cell]}-{sc["s"]}', "family": "target", "class": sc["class"], "row": sc["row"],
            "cell": cell, "heading": sc.get("heading"), "sentence": sc[cell], "situation": situation,
            "question": QUESTION, "pre": sc["pre"], "options": opts, "key": {k: CARRIER[k] for k in opts},
            "lean": {"reading": reading, "frame": frame, "model": model(rels)}}


def other(sc):
    opts = options(sc["cell"], sc["pre"])
    key = {k: CARRIER[k] for k in opts}
    if sc["family"] == "proviso":
        key["c"] = "unconditional"
    item = {"id": sc["id"], "family": sc["family"], "class": None, "row": sc["row"], "cell": sc["cell"], "heading": None,
            "sentence": sc["sentence"], "situation": sc["situation"], "question": QUESTION, "pre": sc["pre"],
            "options": opts, "key": key,
            "lean": {"reading": sc["reading"], "frame": sc["frame"], "model": model(sc["rels"])}}
    if sc["family"] == "control":
        item |= {"expected": sc["expected"], "filter": sc["filter"]}
    return item


def build():
    data = json.loads((DATA / "scenarios.json").read_text())
    return [target(sc, cell) for sc in data["targets"] for cell in CELLS] + [other(sc) for sc in data["others"]]


def dumps(items):
    return "".join(json.dumps(i, ensure_ascii=False, sort_keys=True) + "\n" for i in items)


def load(path=ITEMS):
    return [json.loads(line) for line in Path(path).read_text().splitlines()]


def audit(items, cfg, table):
    """The pre-call audit: every item against the plan's cell rules and its stub row. Raises on the first fault."""
    def need(ok, why):
        if not ok:
            raise ValueError(why)
    rows = {r["id"]: r for r in table}
    need(len({i["id"] for i in items}) == len(items) == 108, "108 distinct items")
    need(set(rows) == {i["id"] for i in items}, "one stub row per item")
    need(len({(i["sentence"], i["situation"]) for i in items}) == 108, "distinct stimuli")
    fam = {f: [i for i in items if i["family"] == f] for f in ("target", "control", "suspension", "proviso")}
    need([len(fam[f]) for f in fam] == [84, 12, 6, 6], "84 + 12 + 6 + 6 items")
    need(sorted(set(cfg["mapping"].values())) == ["definite", "generic", "plural"] and len(cfg["mapping"]) == 7,
         "seven classes on three rows")
    for cls in cfg["mapping"]:
        for cell in CELLS:
            need(sum(i["class"] == cls and i["cell"] == cell for i in fam["target"]) == 2, f"{cls}/{cell}: two items")
    for row in ("definite", "plural", "generic"):
        need(sum(i["row"] == row for i in fam["suspension"]) == 2, f"suspension: two {row} items")
        need(sum(i["row"] == row for i in fam["proviso"]) == 2, f"proviso: two {row} items")
        need(sum(i["row"] == row for i in fam["control"]) == 4, f"controls: four {row} items")
    need({f: sum(i["filter"] == f for i in fam["control"]) for f in FILTERS} == FILTERS, "the filters of R 4.1")
    for i in items:
        s, r, where = i["sentence"], rows[i["id"]], i["id"]
        need(i["question"] == QUESTION, f"{where}: question")
        need(i["options"] == options(i["cell"], i["pre"]), f"{where}: options of the cell")
        need(i["pre"] in i["options"]["c"] and list(i["options"]) == sorted(i["options"]), f"{where}: option (c), order")
        need(("a" in i["options"]) == (i["cell"] != "rule_act"), f"{where}: (a) dropped only at a rule act")
        need(("e" in i["options"]) == (i["cell"] in E_CELLS), f"{where}: (e) only in negated and antecedent cells")
        need(r["cell"] == i["cell"], f"{where}: stub cell")
        if i["family"] == "target":
            need(i["row"] == cfg["mapping"][i["class"]], f"{where}: class row")
            need(i["key"] == {k: CARRIER[k] for k in i["options"]}, f"{where}: key")
            need(r["goal"] is False, f"{where}: the goal fails in the situation")
            need(bool(i["heading"]) == (i["class"] == "heading_noun_phrase"), f"{where}: heading")
            if i["heading"]:
                need(i["heading"] in s, f"{where}: the sentence reuses the heading")
            word = {"negated": " not ", "antecedent": "If ", "consequent": "If ", "rule_act": " must ", "rule_guard": " must "}
            need(word.get(i["cell"], "") in s, f"{where}: sentence shape")
            need(i["cell"] not in ("top", "negated") or "If " not in s, f"{where}: no conditional")
            need(i["cell"] != "top" or " not " not in s, f"{where}: no negation")
            need(i["cell"] != "rule_guard" or s.startswith("If "), f"{where}: guard")
            need(i["cell"] != "rule_act" or not s.startswith("If "), f"{where}: silent guard")
        if i["cell"] in E_CELLS:
            need(r["shallow"] is True, f"{where}: a negated or antecedent item has a shallow frame (R-D4)")
        if i["family"] == "control":
            need(r["goal"] is True, f"{where}: the goal holds in a control's situation")
            need(i["expected"] == ("b" if r["base"] else "a"), f"{where}: key is the proved carrier's value")
        if i["family"] == "suspension":
            need(r["goal"] is False and " uncertain whether " in s, f"{where}: suspension")
        if i["family"] == "proviso":
            need(r["goal"] is True and r["close"] is False and i["key"]["c"] == "unconditional", f"{where}: proviso")


if __name__ == "__main__":
    ITEMS.write_text(dumps(build()))
    print(f"{len(build())} items written to {ITEMS}")
