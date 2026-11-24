"""The encoder for the Copilot Extension policy translation: a case spec (cases.py, smoke_cases.py) -> the translation's Ctx
and the stated facts. Conventions (encoder judgement where they decide anything, listed in RESULT.md):
C1 CLOSED WORLD over each item's PLAIN facts (translation.ACT_PLAIN, GH_PLAIN, DUTY_PLAIN, DEL_PLAIN): what the case does not
   say an act is or does, it is not / does not; a duty item is exactly the duty the question names.
C2 STATED facts (judgments and outside outcomes: translation.ACT_STATED, GH_STATED, DUTY_STATED) are never closed: each is
   given only where the case states it (true or false); otherwise unknown, and a rule that turns on it stays OPEN.
C3 one item per act, GitHub act, duty or deletion a question asks about (and per earlier act a termination question needs);
   the data an act concerns is described on the act item itself.
C4 days: a stated date enters as a Lean date; nothing is computed here.
spec = {"items": [{"id", "kind", "facts": [plain facts true], "stated": {name: bool}, "day" | "qday" | "ev" | "dd": ISO}],
        "links": [(gh item, act item)]}
"""
from __future__ import annotations

import translation as T

PLAIN = {"act": T.ACT_PLAIN, "gh": T.GH_PLAIN, "duty": T.DUTY_PLAIN, "del": T.DEL_PLAIN, "q": {}}
STATED = {"act": T.ACT_STATED, "gh": T.GH_STATED, "duty": T.DUTY_STATED, "del": {}, "q": {}}


def build(spec):
    items = [(it["id"], it["kind"]) for it in spec["items"]]
    ctx = T.Ctx(items, spec.get("links", ()))
    facts = []

    def add(f):
        facts.append({"id": f"f{len(facts)}", "formula": f})

    for it in spec["items"]:
        x, kind = it["id"], it["kind"]
        true = set(it.get("facts", ()))
        bad = true - set(PLAIN[kind])
        if bad:
            raise ValueError(f"{x}: not a plain fact of a {kind} item: {sorted(bad)}")
        for name in PLAIN[kind]:
            add(T.U(name, x) if name in true else T.Not(T.U(name, x)))
        for name, v in sorted(it.get("stated", {}).items()):
            if name not in STATED[kind]:
                raise ValueError(f"{x}: not a stated fact of a {kind} item: {name}")
            add(T.U(name, x) if v else T.Not(T.U(name, x)))
        for base in ("day", "qday", "ev", "dd"):
            if it.get(base):
                if base not in T.KINDS[kind]:
                    raise ValueError(f"{x}: a {kind} item has no {base}")
                add(T.Eq(T.k(base, x), ["date", it[base]]))
    return ctx, facts
