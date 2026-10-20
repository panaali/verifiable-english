#!/usr/bin/env python3
"""Run 20261018T1800Z: the ledger changes of the plans merged for this run, as functions on the ledger (a list of entries, one per unit).

* QT-0p (quantities): u0042.presupposition CHECKED; u0043.s02 MIXED (p1 LABELLED, p2 CHECKED).
* PS-0p (presupposition): steps 1 to 5 (claims removed or replaced by notes, u0245 offered, u0286 and u0032 reverted), step 4 (`presupposition_triggers` on every unit) and the
  `other_blockers` tag, step 6 (`presupposition-goals.json`).
* JT-0p (judgment terms): the class of every open term and `judgment_terms` on every unit.

Nothing here touches a document; `apply_plans.py` does that. The ledger is the translator's record, so the fields below are the translator's claims; the audit reads them.
"""
from __future__ import annotations

import copy
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

RUN = Path(__file__).resolve().parent
COVERED = {"CHECKED", "LABELLED", "OPEN", "READINGS"}


# ---------------------------------------------------------------------------------------------------------------- QT-0p
QT_NOTE_U0042 = ("QT-0p (quantities plan, DRI QT2; content docs/research/evidence/quantities/qt0p/constitution-u0042-u0043.ve.md on research/quantities-p1). The heading's presupposition is "
                 "that Claude has exactly three types of principals and nothing more: three pairwise different principal types that are Claude's, and every one of Claude's types is among "
                 "them. It names none of them (u0043.s02 does). The closure is over Claude's types (`claude_principal_type`), never over all principal types, which the source does not state.")
QT_NOTE_P1 = ("“At the moment,” is the document's present, with no date: the clause says the list that follows holds now and may change; VE records it as a comment about the text (a time "
              "adverbial with no date, so no time construct is needed).")
QT_NOTE_P2 = ("QT-0p. Anthropic, operators and users are each one of Claude's types of principals, they are pairwise different, and every one of Claude's types is one of them. The three "
              "constants are of the sort `principal_type`; `operators` and `users` are constants, not the sorts `operator` and `user`, and the rendered English parses back to the same "
              "formula (checked by checkpoint-qt0p and this run's round trip). The predicate's planned wording “is one of Claude's types of principals” is refused by the English lint "
              "(LOGICAL_WORD, PHRASE_SYNTAX, SORT_NOUN, SYMBOL_COLLISION, UNARY_MODIFIER), so VE writes it as `is classified as \"claude_principal_type\"`: the checked content is the plan's, "
              "its English carries one quoted name. Reported as a finding.")


def qt0p(ledger, english):
    """u0042.presupposition becomes CHECKED; u0043.s02 is replaced by its two parts."""
    out = []
    for e in ledger:
        if e["id"] == "u0042.presupposition":
            e = copy.deepcopy(e)
            for k in ("missing_feature", "presupposed_claim"):
                e.pop(k, None)
            e.update({"status": "CHECKED", "note": QT_NOTE_U0042, "kind": "asserted", "support": "assumption", "claimed": True,
                      "plan_repair": {"plan": "quantities", "item": "QT-0p"}, "checked_english": english["u0042.presupposition"],
                      "previous_status": "UNFORMALISED", "previous_missing_feature": "counting",
                      "previous_presupposed_claim": "Claude has three types of principals."})
            e["other_blockers"] = [b for b in e.get("other_blockers", []) if b != "counting"]
            out.append(e)
        elif e["id"] == "u0043.s02":
            base = {k: v for k, v in e.items() if k not in ("id", "span", "source_excerpt", "status", "missing_feature", "other_blockers", "note", "status_in_previous_run")}
            a, b = e["span"][0], e["span"][0] + 15
            p1 = {**base, "id": "u0043.s02.p1", "span": [a, b], "source_excerpt": "At the moment, ", "old_unit": "u0043.s02", "status": "LABELLED",
                  "note": QT_NOTE_P1, "kind": "meta", "claimed": True, "plan_repair": {"plan": "quantities", "item": "QT-0p"},
                  "previous_status": "UNFORMALISED", "previous_missing_feature": "counting", "other_blockers": ["other:scope"]}
            p2 = {**base, "id": "u0043.s02.p2", "span": [b, e["span"][1]], "source_excerpt": e["source_excerpt"][len("At the moment, "):], "old_unit": "u0043.s02", "status": "CHECKED",
                  "note": QT_NOTE_P2, "kind": "asserted", "support": "assumption", "claimed": True, "plan_repair": {"plan": "quantities", "item": "QT-0p"},
                  "checked_english": english["u0043.s02.p2"], "previous_status": "UNFORMALISED", "previous_missing_feature": "counting", "other_blockers": ["other:scope"]}
            for p in (p1, p2):
                p["parent_unit"] = e["parent_unit"]
                p["mixed_parent"] = "u0043.s02"
            out += [p1, p2]
        else:
            out.append(e)
    return out


# ---------------------------------------------------------------------------------------------------------------- PS-0p
E_TITLES = ["u0040", "u0075", "u0151", "u0162", "u0174", "u0195", "u0207", "u0212", "u0257", "u0260"]
NOTE_TITLE = "no trigger word: a title (scope SC-3a)"
NOTE_U0055 = "wh-title: its presupposition is that there is a way to treat them; the recorded claim was not it"
NOTE_D = "the text withholds this (u0269.s02): not assumed"
NOTE_RELATIONAL = "relational-noun wording not admitted in VE English (PS-0p phase 1): 'is a … of' wordings are refused"
NOTE_U0286 = ("offered in PS-0p's form (predicate `open_problem` worded “{0} is unsolved”, fence “Some thing is unsolved.”, `∃x open_problem(x)`; it loads, the check is admitted, CHECKED +29 B) "
              "and reverted in this run: with QT-0p's `principal_type` (size 3) in the document, the whole-document premise check is UNKNOWN (the 100,000-evaluation budget is spent before a "
              "model is found and no ground fact names a witness for the existential). The DRI has not accepted UNKNOWN for the constitution's premise check, so the unit stays UNFORMALISED "
              "(evidence/ps0p/premise-variants.json, premise-diag-*.txt)")
NOTE_U0032 = ("class B item, offered and reverted in this run: the wording the lint admits for “constitutes genuine helpfulness” is “{0} is helpful” (it drops “genuine” and “constitutes”), the "
              "claim is an existential (`∃x genuine_helpfulness(x)`), and the existential leaves the whole-document premise check UNKNOWN (as u0286); so the unit stays UNFORMALISED "
              "(evidence/ps0p/premise-variants.json)")
NOTE_U0069 = ("class B item, not offered: the noun “deployment context” has no admitted wording (“{0} is a deployment context” is refused, LOGICAL_WORD and UNARY_MODIFIER, "
              "evidence/ps0p/wording-lint.json); “{0} is deployed” is admitted but says something else")
NOTE_U0083 = ("class B item, not offered: “values other than helpfulness” needs the noun “core value”, which waits for PS-6r (PS-0p step 5)")
NOTE_U0245 = ("class B item, offered to the audit (PS-0p step 5): the heading presupposes that Claude is a novel entity. Predicate `novel_entity` worded “{0} is novel” (the lint admits it; “is a novel "
              "entity” is refused, UNARY_MODIFIER, so the English drops the noun, which the sort `entity` (“thing”) already carries), open term (what counts as novel, and compared with what), "
              "fence “Claude is novel.” (`novel_entity(claude)`). A ground fact, so the premise check stays `model`. Claimed only if the audit accepts it.")

HEADINGS = {
    "u0013": [("possessive", "Claude’s", "Claude has core values.")],
    "u0095": [("possessive", "Anthropic’s", "Anthropic has guidelines.")],
    "u0286": [("factive", "Acknowledging", "There are open problems.")],
    "u0002": [("definite", "the mission of", "Anthropic has exactly one mission.")],
    "u0235": [("possessive", "Claude’s", "Claude has a nature.")],
    "u0069": [("plural", "existing", "There are deployment contexts.")],
    "u0083": [("plural", "other", "There are values other than helpfulness.")],
    "u0245": [("other:predicative-as", "as", "Claude is a novel entity.")],
    "u0032": [("wh-title", "What", "Something constitutes genuine helpfulness.")],
    "u0008": [("possessive", "Our", "The authors have an approach."), ("possessive", "Claude’s", "Claude has a constitution.")],
    "u0238": [("possessive", "our", "The authors have views."), ("possessive", "Claude’s", "Claude has a nature.")],
    "u0219": [("wh-title", "How", "The authors think about corrigibility.")],
    "u0027": [("wh-title", "Why", "Helpfulness is one of Claude’s most important traits."), ("possessive", "Claude’s", "Claude has traits.")],
    "u0042": [("possessive", "Claude’s", "Claude has exactly three types of principals.")],
    "u0130": [("definite", "The", "Actions have costs and benefits.")],
    "u0143": [("definite", "The", "Intentions and context have a role.")],
    "u0254": [("possessive", "Claude’s", "Claude has wellbeing and psychological stability.")],
    "u0268": [("possessive", "Claude’s", "Claude has wellbeing.")],
    "u0055": [("wh-title", "How", "There is a way to treat operators and users.")],
}
HEADING_CARRIER = {"u0042": "assumed", "u0245": "assumed"}   # the heading's own unit has content exactly `pre` (QT-0p; PS-0p class B)


def ps0p_notes(ledger):
    """Steps 1 to 3 and 5, on the ledger text. Returns the ids of the units changed."""
    changed = []
    by = {e["id"]: e for e in ledger}

    def edit(uid, plan_item, **fields):
        e = by[uid]
        for k, v in fields.items():
            if v is None:
                e.pop(k, None)
            else:
                e[k] = v
        e["plan_repair"] = {"plan": "presupposition", "item": plan_item}
        changed.append(uid)

    for t in E_TITLES:
        uid = f"{t}.presupposition"
        assert by[uid]["status"] == "UNFORMALISED" and "presupposed_claim" in by[uid]
        edit(uid, "PS-0p step 1", presupposed_claim=None, previous_presupposed_claim=by[uid]["presupposed_claim"], note=NOTE_TITLE)
    uid = "u0055.presupposition"
    edit(uid, "PS-0p step 1", presupposed_claim=None, previous_presupposed_claim=by[uid]["presupposed_claim"], note=NOTE_U0055, listed_for_audit=True)
    for t in ("u0254", "u0268"):
        uid = f"{t}.presupposition"
        edit(uid, "PS-0p step 2", presupposed_claim=None, previous_presupposed_claim=by[uid]["presupposed_claim"], note=NOTE_D, withheld_by="u0269.s02")
    for t in ("u0013", "u0095", "u0002", "u0235"):
        edit(f"{t}.presupposition", "PS-0p step 3", note=NOTE_RELATIONAL)
    edit("u0286.presupposition", "PS-0p step 3", note=NOTE_U0286, offered_and_reverted=True, trigger="factive", trigger_words="Acknowledging")
    edit("u0032.presupposition", "PS-0p step 5", note=NOTE_U0032, offered_and_reverted=True)
    edit("u0069.presupposition", "PS-0p step 5", note=NOTE_U0069)
    edit("u0083.presupposition", "PS-0p step 5", note=NOTE_U0083)
    # u0245: the claim is the unit's content now
    e = by["u0245.presupposition"]
    assert e["status"] == "UNFORMALISED"
    prev_claim, prev_mf = e["presupposed_claim"], e["missing_feature"]
    for k in ("presupposed_claim", "missing_feature", "other_blockers"):
        e.pop(k, None)
    e.update({"status": "OPEN", "kind": "asserted", "support": "assumption", "claimed": True, "note": NOTE_U0245, "open_terms": ["novel_entity"],
              "carrier": "assumed", "trigger": "predicative as", "trigger_words": "as", "previous_status": "UNFORMALISED", "previous_missing_feature": prev_mf,
              "previous_presupposed_claim": prev_claim, "offered_to_audit": True, "plan_repair": {"plan": "presupposition", "item": "PS-0p step 5"}})
    changed.append("u0245.presupposition")
    return changed


# ---- step 4: presupposition_triggers
FALSE_FULL_WORDS = {"remainder", "remainders", "discoveries", "discovery", "discoverer"}
STOP = {"is", "are", "was", "were", "to", "that", "which", "and", "or", "in", "on", "of", "for", "with", "as", "by", "can", "should", "will", "would", "may", "must", "might", "could",
        "has", "have", "had", "but", "if", "when", "than", "from", "at", "about", "into", "be", "being", "been", "do", "does", "did", "not", "so", "it", "their", "its", "we", "who", "whose"}
ROLE_OWNER = re.compile(r"^(the (user|operator|principal)(’s|'s)|its|their)\s+(.*)$", re.I)
CHANGE = [(re.compile(r"^(stop|stops|stopped|stopping|ceas\w*)$", re.I), "was going on before the point the sentence speaks of."),
          (re.compile(r"^(continu\w*)$", re.I), "was already going on."),
          (re.compile(r"^(resum\w*)$", re.I), "was going on earlier and had stopped."),
          (re.compile(r"^(remain\w*|still)$", re.I), "already holds."),
          (re.compile(r"^no longer$", re.I), "held earlier."),
          (re.compile(r"^(again|return\w* to)$", re.I), "happened or held earlier.")]


MODIFIERS = {"core", "more", "specific", "other", "own", "good", "most", "default", "holistic", "official", "usage", "system", "commercial", "production", "ethical", "harm-avoidance",
             "first-person", "visible", "three", "consumer-facing", "hard", "broad", "general", "important", "overall", "particular", "different", "best", "likely", "reasoning"}


def following_noun_phrase(source, end):
    """The noun phrase after a possessive, by a small rule: the next word, and the next again while the word is a modifier (`Claude’s core values` -> `core values`,
    `Anthropic’s usage policies` -> `usage policies`). A template, not a parse: the translator's `pre` is not checked by VE."""
    rest = source[end:end + 120].decode("utf-8", "ignore")
    words = []
    for w in re.findall(r"[\w’'-]+|[^\s\w]", rest):
        if not re.match(r"[\w’'-]+$", w) or w.lower() in STOP:
            break
        words.append(w)
        if w.lower() not in MODIFIERS or len(words) == 4:
            break
    return " ".join(words)


def pre_of(trigger, source):
    """The translator's `pre` for one census trigger (English), by the trigger's group; a template, not a checked sentence."""
    g, words = trigger["group"], trigger["words"]
    lo = words.lower()
    if g == "G1":
        noun = "operator" if "operator" in lo else "user"
        plural = lo.endswith("s")
        return ("There are %ss." % noun) if plural else ("There is %s %s." % ("an" if noun == "operator" else "a", noun))
    if g == "G2":
        m = ROLE_OWNER.match(words)
        if not m:
            return f"What “{words}” names exists."
        owner, noun = m.group(1), m.group(4)
        if owner.lower().startswith("the "):
            owner = "The " + owner[4:]
            owner = re.sub(r"(’s|'s)$", "", owner)
        else:
            owner = f"What “{owner}” stands for"
        return f"{owner} has {noun}."
    if g in ("G4", "G6"):
        who = re.sub(r"(’s|'s)$", "", words.split(" ")[0] if g == "G6" else words)
        if g == "G6":
            return f"{who} has {' '.join(words.split(' ')[1:])}."
        noun = following_noun_phrase(source, trigger["span"][1])
        who = re.sub(r"(’s|'s)$", "", words)
        who = who[0].upper() + who[1:]
        return f"{who} has {noun}." if noun else f"{who} has what the text names after “{words}”."
    if g == "G3":
        for rx, phrase in CHANGE:
            if rx.match(lo):
                return f"The state or activity this sentence speaks of {phrase}"
        raise AssertionError(words)
    if g == "G5":
        return f"What follows “{words}” (its complement) is true."
    raise AssertionError(g)


def clean_census(census_units, source):
    """The census (research/presupposition-p1, regular expressions over the pinned text) without its named lexical false positives (O4, O6, O8, O9 of phase 1 section 2.1):
    `remainder` for `remain`, `discoveries` for `discover`, `returned to the orchestrator` for `return to`. Returns {unit id: [entries with absolute spans]} and the dropped list."""
    dropped, out = [], {}
    text = source.decode("utf-8")
    for u in census_units:
        keep = []
        for t in u["presupposition_triggers"]:
            a, b = t["span"]
            s = source[a:b].decode("utf-8")
            assert s == t["words"], (u["id"], s, t["words"])
            tail = re.match(r"\w*", source[b:b + 30].decode("utf-8", "ignore")).group(0)
            full = (s + tail).lower()
            if t["group"] in ("G3", "G5") and full in FALSE_FULL_WORDS or (t["group"] == "G3" and re.match(r"\s+the orchestrator", source[b:b + 30].decode("utf-8", "ignore"))
                                                                      and s.lower().startswith("return")):
                dropped.append({"unit": u["id"], "words": s, "full_word": full})
                continue
            keep.append(t)
        out[u["id"]] = keep
    return out, dropped


def triggers_for_ledger(ledger, census, source, extra_open=None):
    """Step 4: `presupposition_triggers` on every unit. Headings: the curated table HEADINGS (and nothing for a title); other units: the census entries, cleaned. Returns the
    ids of units whose carrier is unresolved (they gain the blocker `other:presupposition`)."""
    kept, dropped = clean_census(census["units"], source)
    census_by = {u["id"]: u for u in census["units"]}
    unresolved = []
    counts = Counter()
    for e in ledger:
        uid, span = e["id"], e["span"]
        entries = []
        if uid.endswith(".presupposition"):
            for cls, words, pre in HEADINGS.get(uid.split(".")[0], []):
                carrier = HEADING_CARRIER.get(uid.split(".")[0], "unresolved")
                ent = {"words": words, "class": cls, "pre": pre, "carrier": carrier}
                if carrier == "assumed":
                    ent["carrier_unit"] = uid
                if uid in ("u0254.presupposition", "u0268.presupposition"):
                    ent["withheld_by"] = "u0269.s02"
                entries.append(ent)
        else:
            # a part of a split unit (u0043.s02.p1/p2) reads the census of the unit it was split from
            src_id = e.get("old_unit", uid) if uid.startswith("u0043.s02.p") else uid
            for t in kept.get(src_id, []):
                a, b = t["span"]
                if not (span[0] <= a and b <= span[1]):
                    continue
                ent = {"words": t["words"], "class": t["class"], "pre": pre_of(t, source), "carrier": "unresolved", "span": t["span"], "group": t["group"]}
                if uid == "u0043.s02.p2" and t["words"] == "Claude’s":
                    ent["carrier"], ent["carrier_unit"] = "assumed", "u0042.presupposition"
                    ent["pre"] = "Claude has three types of principals."
                entries.append(ent)
        e["presupposition_triggers"] = entries
        for ent in entries:
            counts[(ent["class"], ent["carrier"])] += 1
        if any(x["carrier"] == "unresolved" for x in entries):
            unresolved.append(uid)
    return unresolved, dropped, counts


# ---- step 6: presupposition-goals.json
ROLE_WORDS = re.compile(r"\b(the (user|operator|principal)s?)\b|\b(the (user|operator|principal)(’s|'s)|its|their)\s+(system prompt|instructions?|requests?|message|claims?|content|goals?|context|wishes|interests?|failure|right)\b", re.I)
_norm = lambda s_: s_.lower().replace("’", "'")


def goals(ledger, meta, source):
    """PS-0p step 6. For each formalised rule (a norm unit of the ledger) whose source sentence contains “the user”, “the operator” or a role or pronoun possessive, one row per match and per
    reading of the rule: the unit, the words, where they sit (the rule's act, or packed inside a guard atom's wording or description, or in neither), the rule's name, guard and carve-outs.
    The count: trigger occurrences in the source sentences of formalised rules, and the goals they project (a goal key is (role noun, position, rule predicate, guard, carve-outs); guards are
    de Bruijn formulas, so the key is up to the unit's variable names), “the user” and “the operator” separately, with how many goals share identical applicability (guard and carve-outs)."""
    voc = meta["environment"]["vocabulary"]["predicates"]
    units = {u["id"]: u for u in _flat(meta["units"])}
    sets = {s_["unit"]: s_ for s_ in meta.get("reading_sets", [])}
    rows, scanned = [], []

    def atoms(node, acc):
        if isinstance(node, list):
            if node and node[0] in ("unary", "binary") and isinstance(node[1], str):
                acc.add(node[1])
            for x in node:
                atoms(x, acc)
        return acc
    for e in ledger:
        if e.get("kind") != "norm":
            continue
        uid, pred = e["id"], e["predicate"]
        reg = voc[pred]["regulated"]
        act, sorts = reg["act"], voc[pred]["arguments"]
        text = source[e["span"][0]:e["span"][1]].decode("utf-8")
        found = list(ROLE_WORDS.finditer(text))
        matches = [m.group(0) for m in found]
        # the phrase around a match, to tell which guard atom packs it: the three words before it plus it, and it plus the words after it up to punctuation (at most two)
        around = []
        for m in found:
            before = re.findall(r"[\w’'-]+", text[:m.start()])[-3:]
            after = re.match(r"((?:\s+[\w’'-]+){0,2})", text[m.end():]).group(1)
            around.append([_norm(" ".join([*before, m.group(0)])), _norm(m.group(0) + after)])
        contents = [(r["id"], r["content"]["norm"]) for r in sets[uid]["readings"]] if uid in sets else [(None, units[uid]["content"]["norm"])]
        scanned.append({"unit": uid, "predicate": pred, "act": act, "argument_sorts": sorts, "matches_in_source": matches, "readings": [c[0] for c in contents]})
        for words, phrases in zip(matches, around):
            role = "operator" if "operator" in words.lower() else ("user" if "user" in words.lower() else "other")
            for rid, norm in contents:
                used = sorted(atoms([norm["guard"], norm["unless"], norm.get("over", [])], set()))
                packed = [a for a in used if any(ph in _norm((voc[a].get("verbalisation") or "") + " " + voc[a].get("description", "")) for ph in phrases)]
                if packed:
                    position, where = "guard", "packed inside the wording or description of guard atom " + ", ".join(packed) + " (no formula position: the translation boundary)"
                elif role in sorts and sorts.index(role) > 0 or (role == "user" and "user" in sorts):
                    position, where = "act", f"argument {{{sorts.index(role)}}} of sort {role} of the rule's act “{act}”"
                elif any(w in _norm(act) for w in _norm(words).split()[-1:]):
                    position, where = "act", f"folded into the rule's act “{act}”"
                else:
                    position, where = "source only", "neither the act nor a guard atom carries the words"
                rows.append({"unit": uid, "reading": rid, "words": words, "role": role, "position": position, "where": where, "rule": norm["name"], "predicate": pred,
                             "guard": norm["guard"], "unless": norm["unless"], "over": norm.get("over", [])})
    keys = defaultdict(list)
    for r in rows:
        keys[(r["role"], r["words"].lower(), r["position"], r["predicate"], json.dumps(r["guard"]), json.dumps(r["unless"]))].append(r)
    out = {"what": ("PS-0p step 6 (presupposition-PLAN 2.1 step 7): the formalised rules whose source sentence contains “the user”, “the operator” or a role/pronoun possessive; one row per match and per "
                    "reading; a goal key is (role noun, words, position, rule predicate, guard, carve-outs) up to the unit's variable names (guards are de Bruijn formulas)"),
           "scanned_norm_units": scanned, "occurrences": rows}
    by_role = {}
    for rl in ("user", "operator", "other"):
        occ = [r for r in rows if r["role"] == rl]
        ks = [k for k in keys if k[0] == rl]
        applic = Counter((k[4], k[5]) for k in ks)
        by_role[rl] = {"source_occurrences": len({(r["unit"], r["words"]) for r in occ}), "rows_per_reading": len(occ), "units": sorted({r["unit"] for r in occ}),
                       "in_act": sum(1 for r in occ if r["position"] == "act"), "in_guard_atom": sum(1 for r in occ if r["position"] == "guard"),
                       "distinct_goals": len(ks), "goals_sharing_identical_applicability": sum(v for v in applic.values() if v > 1)}
    all_ks = list(keys)
    applic_all = Counter((k[4], k[5]) for k in all_ks)
    out["counts"] = by_role
    out["all_roles"] = {"distinct_goals": len(all_ks), "goals_sharing_identical_applicability": sum(v for v in applic_all.values() if v > 1),
                        "applicability_groups_with_more_than_one_goal": sum(1 for v in applic_all.values() if v > 1),
                        "reading": "two goals share identical applicability when their rules have the same guard and carve-outs; they are different goals when their rows (words, position) differ, "
                                   "so nothing is coupled (PS-3 reads this count)"}
    out["note"] = ("`source_occurrences` are the matches in the sentences of the 18 formalised rules (phase 1 found 4 in 3 units); `rows_per_reading` multiplies by the readings of a reading set "
                   "(u0156.s03 has four candidates). Occurrences in a guard atom are packed inside an open term the translator named (instruction_*): they have no formula position. "
                   "The 98 unformalised G1 matches of phase 1 are not rules and are not counted here")
    return out


def _flat(units):
    for u in units:
        if u.get("status") == "MIXED":
            yield from u["parts"]
        else:
            yield u
