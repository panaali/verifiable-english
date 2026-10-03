"""S2a's deterministic choice encoding and compatible-choice search.

These are elaboration inputs, not verdicts.  A verdict needs the S2 Lean replay
and its checked evidence; callers must not infer ALL from this module alone.
The order here is the source order of ``Document.sets`` and candidate order.
"""

from __future__ import annotations

from copy import deepcopy

from .errors import VEError
from .readings_s1 import Content, decode_content

MAX_CHOICES = 64
READING_SORT = "ve__reading"
HERE = "ve__here"


def bits_of(count: int) -> int:
    """The least number of bits representing every index below ``count``."""
    if count < 1:
        raise ValueError("a reading set needs at least one candidate")
    return (count - 1).bit_length()


def bit_name(position: int, bit: int) -> str:
    return f"ve__bit__{position}__{bit}"


def _fold(tag: str, empty: str, formulas: list) -> list:
    if not formulas:
        return [empty]
    result = formulas[-1]
    for formula in reversed(formulas[:-1]):
        result = [tag, formula, result]
    return result


def conj(formulas: list) -> list:
    return _fold("and", "top", formulas)


def disj(formulas: list) -> list:
    return _fold("or", "bottom", formulas)


def pattern(position: int, count: int, index: int) -> list:
    """The choice atom, least significant bit first, in Lean's tree shape."""
    if position < 1 or index < 0 or index >= 1 << bits_of(count):
        raise ValueError("invalid choice pattern")
    return conj([(["unary", bit_name(position, bit), ["const", HERE]] if index & (1 << bit)
                  else ["not", ["unary", bit_name(position, bit), ["const", HERE]]])
                 for bit in range(bits_of(count))])


def choice_atom(sets, set_id: str, index: int) -> list:
    for position, reading_set in enumerate(sets, 1):
        if reading_set.id == set_id:
            return (pattern(position, len(reading_set.candidates), index)
                    if 0 <= index < len(reading_set.candidates) else ["bottom"])
    return ["bottom"]


def choice_vocabulary(sets) -> dict:
    """The one added sort and constant, and bit predicates in source order."""
    if not sets:
        return {"sorts": [], "constants": {}, "predicates": {}}
    return {"sorts": [READING_SORT], "constants": {HERE: READING_SORT},
            "predicates": {bit_name(position, bit): [READING_SORT]
                           for position, reading_set in enumerate(sets, 1)
                           for bit in range(bits_of(len(reading_set.candidates)))}}


def sup_ready(sets, couplings=(), narrowings=(), *, doc=None) -> bool:
    """The shape conjuncts of S2 1.8, including the active-version checks.

    The decoder has further checks, notably a shared coupling label value.
    This predicate deliberately mirrors only ``supReady`` in the spec.
    """
    ids = [reading_set.id for reading_set in sets]
    if doc is not None:
        units = [item[1] if item[0] != "set" else item[2].unit for item in doc.items]
        if len(units) != len(set(units)):
            return False
        frame = doc.senv.frame_data["vocabulary"]
        if HERE in frame.get("constants", {}) or any(
                bit in frame.get("predicates", {}) for bit in choice_vocabulary(sets)["predicates"]):
            return False
    if len(ids) != len(set(ids)) or any(
            not reading_set.candidates or any(a.content is None for a in reading_set.candidates)
            for reading_set in sets):
        return False
    by_version = {(reading_set.id, reading_set.version): reading_set for reading_set in sets}
    if len({item["id"] for item in couplings}) != len(couplings):
        return False
    for coupling in couplings:
        refs = [(ref["set"], ref["version"]) for ref in coupling["sets"]]
        if (len(refs) < 2 or len({set_id for set_id, _ in refs}) != len(refs)
                or any(ref not in by_version for ref in refs)):
            return False
        if any(coupling["axis"] not in candidate.labels
               for ref in refs for candidate in by_version[ref].candidates):
            return False
    if len({item["id"] for item in narrowings}) != len(narrowings):
        return False
    for narrowing in narrowings:
        reading_set = by_version.get((narrowing["set"], narrowing["version"]))
        if reading_set is not None:
            candidate_ids = {a.id for a in reading_set.candidates}
            if not narrowing["keeps"] or not set(narrowing["keeps"]) <= candidate_ids:
                return False
    return True


def position(sets, set_id: str, index: int) -> int:
    """The 1-based candidate position across all open sets."""
    before = 0
    for reading_set in sets:
        if reading_set.id == set_id:
            if 0 <= index < len(reading_set.candidates):
                return before + index + 1
            break
        before += len(reading_set.candidates)
    raise ValueError("candidate outside active reading sets")


def qualify(number: int, name: str) -> str:
    return f"rd-{number}-{name}"


def copies(doc, name: str) -> list[str]:
    """All qualified copies of an interface rule, or the fixed rule name."""
    for reading_set in doc.sets:
        if ("rule", name) in doc.interface_of(reading_set):
            return [qualify(position(doc.sets, reading_set.id, index), name)
                    for index in range(len(reading_set.candidates))]
    return [name]


def first_nonuniform(doc):
    """The first fixed child and interface rule with unlike candidate parents."""
    for _, fixed in doc.fixed_units():
        if fixed.kind != "norm":
            continue
        for name in fixed.body.get("over", []):
            for reading_set in doc.sets:
                if ("rule", name) not in doc.interface_of(reading_set):
                    continue
                parents = [frozenset(a.content.body.get("over", [])) for a in reading_set.candidates
                           if a.content is not None and a.content.kind == "norm"
                           and a.content.body.get("name") == name]
                if len(parents) != len(reading_set.candidates) or len(set(parents)) != 1:
                    return reading_set.id, name
    return None


def uniform_precedence(doc) -> bool:
    """S2 1.8's protection against an unchosen copy yielding to a fixed child."""
    return first_nonuniform(doc) is None


def choice_contents(doc, choice):
    """Every fixed unit and chosen candidate at its source position, own names."""
    if list(choice) != [reading_set.id for reading_set in doc.sets] or any(
            type(choice[R.id]) is not int or not 0 <= choice[R.id] < len(R.candidates)
            for R in doc.sets):
        raise VEError("InvalidInput: incomplete reading choice")
    return doc.build(lambda _: True, lambda R: R.candidates[choice[R.id]])


def superposed_contents(doc):
    """S2a's gated assertions and norms in S1's source order.

    This is a raw content transformation. A caller must extend the frame with
    ``choice_vocabulary`` and run the lower chain's well-formedness check before
    treating the result as superposable.
    """
    if any(a.content is None for R in doc.sets for a in R.candidates):
        raise VEError("InvalidInput: pending reading cannot be superposed")
    out = []
    for item in doc.items:
        if item[0] == "bar":
            raise VEError("UnsupportedProfile: rights superposition is S2b")
        if item[0] == "fixed":
            content = item[2]
            if content.kind != "norm":
                out.append(content)
                continue
            raw = deepcopy(content.raw)
            raw["norm"]["over"] = [copy for name in content.body.get("over", [])
                                    for copy in copies(doc, name)]
            if "cites" in raw:
                cites = {}
                for key, value in raw["cites"].items():
                    if key.startswith("over:"):
                        for name in copies(doc, key[5:]):
                            cites["over:" + name] = value
                    else:
                        cites[key] = value
                raw["cites"] = cites
            out.append(decode_content(raw))
            continue
        reading_set = item[2]
        number = next(i for i, R in enumerate(doc.sets, 1) if R.id == reading_set.id)
        for index, candidate in enumerate(reading_set.candidates):
            content = candidate.content
            atom = pattern(number, len(reading_set.candidates), index)
            if content.kind == "assertion":
                out.append(decode_content(["implies", atom, deepcopy(content.body)]))
            elif content.kind == "norm":
                raw = deepcopy(content.raw)
                rule = raw["norm"]
                rule["name"] = qualify(position(doc.sets, reading_set.id, index), rule["name"])
                rule["guard"] = ["and", rule.get("guard", ["top"]), atom]
                exception = rule.get("exception")
                if isinstance(exception, dict) and isinstance(exception.get("sufficient"), list):
                    exception["sufficient"] = [["and", formula, atom]
                                               for formula in exception["sufficient"]]
                out.append(decode_content(raw))
            else:
                raise VEError("UnsupportedProfile: rights superposition is S2b")
    return out


def canonical_content(content):
    """The S2 wire spelling of a transformed assertion or soft rule."""
    if content.kind == "assertion":
        return {"assertion": content.body}
    if content.kind != "norm":
        return {"kind": content.kind}
    rule = content.body
    exception = rule.get("exception")
    return {"norm": {"name": rule["name"], "predicate": rule["predicate"], "sign": rule["sign"],
                     "mode": rule.get("mode", "strict"), "guard": rule.get("guard", ["top"]),
                     "unless": rule.get("unless", []), "over": rule.get("over", []),
                     "rank": rule.get("rank"), "alterable": rule.get("alterable", []),
                     "exception": ({"decided_by": exception.get("decided_by"),
                                    "sufficient": exception.get("sufficient", []),
                                    "necessary": exception.get("necessary", []),
                                    "factors": exception.get("factors", [])}
                                   if exception is not None else None),
                     "hard": rule.get("hard", False)}}


def superposed_units(doc):
    """The source positions and transformed units independently regenerated for Lean comparison."""
    transformed = iter(superposed_contents(doc))
    units = []
    for item in doc.items:
        if item[0] == "fixed":
            units.append({"unit": item[1], "content": canonical_content(next(transformed))})
        elif item[0] == "set":
            reading_set = item[2]
            for index, candidate in enumerate(reading_set.candidates):
                if candidate.content is not None:
                    units.append({"unit": reading_set.unit, "set": reading_set.id,
                                  "version": reading_set.version, "index": index,
                                  "position": position(doc.sets, reading_set.id, index),
                                  "content": canonical_content(next(transformed))})
    return units


def name_map(doc):
    """The candidate rule and decision names in Lean's S2 elaboration order."""
    result = []
    for reading_set in doc.sets:
        candidates = []
        for index, candidate in enumerate(reading_set.candidates):
            names = []
            if candidate.content is not None and candidate.content.kind == "norm":
                rule = candidate.content.body
                name = rule["name"]
                qualified = qualify(position(doc.sets, reading_set.id, index), name)
                names.append([name, qualified])
                if rule.get("mode", "strict") == "default":
                    names.append([f"soft__excepted__{name.replace('-', '_')}",
                                  f"soft__excepted__{qualified.replace('-', '_')}"])
                for party in rule.get("alterable", []):
                    names.append([f"soft__off__{name.replace('-', '_')}__{party}",
                                  f"soft__off__{qualified.replace('-', '_')}__{party}"])
            candidates.append({"index": index, "id": candidate.id,
                               "position": position(doc.sets, reading_set.id, index), "names": names})
        result.append({"set": reading_set.id, "version": reading_set.version, "candidates": candidates})
    return result


def in_force(reading_set, narrowing: dict) -> bool:
    return reading_set.id == narrowing["set"] and reading_set.version == narrowing["version"]


def compatible(sets, choice: dict[str, int], couplings=(), narrowings=()) -> bool:
    """Exactly one valid index per active set, with all active restrictions."""
    if list(choice) != [reading_set.id for reading_set in sets]:
        return False
    by_id = {reading_set.id: reading_set for reading_set in sets}
    if any(type(choice[reading_set.id]) is not int or
           not 0 <= choice[reading_set.id] < len(reading_set.candidates)
           for reading_set in sets):
        return False
    for coupling in couplings:
        labels = [by_id[ref["set"]].candidates[choice[ref["set"]]].labels.get(coupling["axis"])
                  for ref in coupling["sets"]]
        if any(label is None or label != labels[0] for label in labels):
            return False
    for narrowing in narrowings:
        reading_set = by_id.get(narrowing["set"])
        if reading_set is not None and in_force(reading_set, narrowing):
            if reading_set.candidates[choice[reading_set.id]].id not in narrowing["keeps"]:
                return False
    return True


def choices(sets, couplings=(), narrowings=(), *, limit=MAX_CHOICES):
    """Return at most ``limit + 1`` compatible choices and an over-budget flag.

    The extra choice distinguishes exactly 64 from more than 64.  A stale
    narrowing is ignored, as required by S2 1.2.
    """
    if limit < 0:
        raise ValueError("negative choice limit")
    result: list[dict[str, int]] = []
    selected: dict[str, int] = {}

    def visit(position: int):
        if len(result) > limit:
            return
        if position == len(sets):
            if compatible(sets, selected, couplings, narrowings):
                result.append(dict(selected))
            return
        reading_set = sets[position]
        for index in range(len(reading_set.candidates)):
            selected[reading_set.id] = index
            visit(position + 1)
            if len(result) > limit:
                break
        selected.pop(reading_set.id, None)

    visit(0)
    return result, len(result) > limit


def one_premises(sets):
    """Exclude unused bit patterns, omitting labels with no formula."""
    labelled = []
    for position, reading_set in enumerate(sets, 1):
        count = len(reading_set.candidates)
        unused = [["not", pattern(position, count, index)]
                  for index in range(count, 1 << bits_of(count))]
        if unused:
            labelled.append((f"readings:{reading_set.id}@{reading_set.version}:one", conj(unused)))
    return labelled


def coupling_premises(sets, couplings):
    by_id = {reading_set.id: reading_set for reading_set in sets}
    labelled = []
    for coupling in couplings:
        forbidden = []
        refs = coupling["sets"]
        for left_ref, right_ref in zip(refs, refs[1:]):
            left, right = by_id[left_ref["set"]], by_id[right_ref["set"]]
            for i, a in enumerate(left.candidates):
                for j, b in enumerate(right.candidates):
                    if a.labels[coupling["axis"]] != b.labels[coupling["axis"]]:
                        forbidden.append(["not", ["and", choice_atom(sets, left.id, i),
                                                  choice_atom(sets, right.id, j)]])
        if forbidden:
            labelled.append((f"coupling:{coupling['id']}", conj(forbidden)))
    return labelled


def narrowing_premises(sets, narrowings):
    labelled = []
    for narrowing in narrowings:
        for reading_set in sets:
            if in_force(reading_set, narrowing):
                dropped = [["not", choice_atom(sets, reading_set.id, i)]
                           for i, a in enumerate(reading_set.candidates) if a.id not in narrowing["keeps"]]
                if dropped:
                    labelled.append((f"narrowing:{narrowing['id']}", conj(dropped)))
                break
    return labelled


def choice_core(sets, couplings=(), narrowings=()):
    """Labelled closed formulas over the bits; quiescence is added separately."""
    return (one_premises(sets) + coupling_premises(sets, couplings) +
            narrowing_premises(sets, narrowings))


def _decision_atom(name, sorts):
    if len(sorts) == 1:
        return ["unary", name, ["var", 0]]
    if len(sorts) == 2:
        return ["binary", name, ["var", 1], ["var", 0]]
    return ["bottom"]


def _quiet_formula(sets, name, sorts, owners):
    atoms = [conj([choice_atom(sets, sets[m].id, i) for m, i in owner]) for owner in owners]
    formula = ["implies", _decision_atom(name, sorts), disj(atoms)]
    for sort in reversed(sorts):
        formula = ["forall", sort, formula]
    return formula


def superposed_document(doc):
    """`sup D` as Python's soft elaborator reads it (1.4): the frame extended by the choice vocabulary, the
    transformed contents in source order, and the soft document of their rules, every gated assertion typed over
    its complete vocabulary. Raises the chain's diagnostic when `sup D` is not well-formed."""
    from .ast import formula_from_data
    from .softnorms import SoftEnvironment, SoftNormDocument

    vocabulary = choice_vocabulary(doc.sets)
    frame = deepcopy(doc.senv.soft_frame().to_dict())
    for sort in vocabulary["sorts"]:
        frame["vocabulary"]["sorts"][sort] = {"description": sort}
    for name, sort in vocabulary["constants"].items():
        frame["vocabulary"]["constants"][name] = {"sort": sort, "description": name}
    for name, sorts in vocabulary["predicates"].items():
        frame["vocabulary"]["predicates"][name] = {"arguments": sorts, "description": name}
    contents = superposed_contents(doc)
    soft = SoftNormDocument(SoftEnvironment(frame, generated=True),
                            [content.raw for content in contents if content.kind == "norm"])
    for content in contents:
        if content.kind == "assertion":
            formula_from_data(soft.extended_env, content.body, _generated=True)
    return frame, contents, soft


def superposed_elaboration(doc, couplings=(), narrowings=()):
    """Regenerate the S2a labelled slot and sizes, including decision-table quiescence.

    Decision names and colliding pairs come from Python's soft elaborator on
    the transformed document; their ownership comes from the source positions.
    """
    vocabulary = choice_vocabulary(doc.sets)
    frame, _, soft = superposed_document(doc)
    origin = {}
    for m, reading_set in enumerate(doc.sets):
        for i, candidate in enumerate(reading_set.candidates):
            if candidate.content is not None and candidate.content.kind == "norm":
                origin[qualify(position(doc.sets, reading_set.id, i),
                               candidate.content.body["name"])] = (m, i)
    keys = []
    for rule in soft.rules:
        if rule.mode == "default":
            name = f"soft__excepted__{rule.core.name.replace('-', '_')}"
            keys.append((name, soft.decisions[name], [([origin[rule.core.name]]
                                                      if rule.core.name in origin else [])]))
    for rule in soft.rules:
        for party in rule.alterable:
            name = f"soft__off__{rule.core.name.replace('-', '_')}__{party}"
            keys.append((name, soft.decisions[name], [([origin[rule.core.name]]
                                                      if rule.core.name in origin else [])]))
    if soft.env.soft["outranking"]["mode"] == "holistic":
        triples = {}
        for left, right in soft.collisions:
            pair = soft._rank_pair(left, right)
            if pair is None:
                continue
            low, high = pair
            name = soft._outweighs_name(low, high, soft._act(left),
                                        soft.env.predicates[left.core.predicate].arguments)
            triples.setdefault(name, [])
            owner = list(dict.fromkeys(origin[n] for n in (left.core.name, right.core.name) if n in origin))
            if len(owner) == 2 and owner[0][0] == owner[1][0]:
                continue
            if owner not in triples[name]:
                triples[name].append(owner)
        keys.extend((name, soft.decisions[name], owners) for name, owners in triples.items())
    labelled = one_premises(doc.sets)
    for m, reading_set in enumerate(doc.sets):
        for i, _ in enumerate(reading_set.candidates):
            mine = [_quiet_formula(doc.sets, name, sorts, owners)
                    for name, sorts, owners in keys if owners == [[(m, i)]]]
            if mine:
                labelled.append((f"readings:{reading_set.id}@{reading_set.version}:{i}:quiet", conj(mine)))
    for name, sorts, owners in keys:
        if [] in owners or (len(owners) == 1 and len(owners[0]) == 1):
            continue
        if [] not in owners:
            _, _, low, high, act = name.split("__", 4)
            labelled.append((f"readings:quiet:outweighs:{act}:{low}:{high}",
                             _quiet_formula(doc.sets, name, sorts, owners)))
    labelled += coupling_premises(doc.sets, couplings) + narrowing_premises(doc.sets, narrowings)

    def nodes(tree):
        return 1 + sum(nodes(item) for item in tree if type(item) is list)

    sizes = {"sorts": len(frame["vocabulary"]["sorts"]),
             "predicates": (len(doc.senv.frame_data["vocabulary"]["predicates"]) +
                            len(vocabulary["predicates"]) + len(soft.decisions)),
             "nodes": sum(nodes(rule["norm"]["guard"]) +
                          sum(nodes(unless) for unless in rule["norm"]["unless"])
                          for rule in (r.to_dict() for r in soft.elaborated.rules)),
             "limits": {"sorts": 32, "predicates": 256, "nodes": 10000}}
    return labelled, sizes


def choice_slot(doc, couplings=(), narrowings=()):
    """The full S2a labelled slot independently regenerated in Python."""
    return superposed_elaboration(doc, couplings, narrowings)[0]


def unsatisfiable_ids(sets, couplings=(), narrowings=()):
    """The ids of `ReadingsUnsatisfiable: <ids>` (7): the couplings and the narrowings in force, sorted."""
    active = {(reading_set.id, reading_set.version) for reading_set in sets}
    return ", ".join(sorted([item["id"] for item in couplings] +
                            [item["id"] for item in narrowings
                             if (item["set"], item["version"]) in active]))


# DRI ruling 5 (2026-10-03): the superposed route runs the chain's check on every compatible choice's document, up to
# this many choices (Lean's `maxChoiceChecks`); past them the superposed verdict kinds refuse with CHECK_BUDGET_TEXT.
MAX_CHOICE_CHECKS = 1024
CHECK_BUDGET_TEXT = f"ResourceLimit: more than {MAX_CHOICE_CHECKS} readings to check"


def choice_text(sets, choice) -> str:
    """A choice as section 7 writes it: `<set>@<v>:<i>` in source order."""
    return ", ".join(f"{R.id}@{R.version}:{choice[R.id]}" for R in sets)


def choice_chain_text(doc, choice):
    """The chain's diagnostic of a compatible choice's document with the choice, or None (Lean's
    `choiceChainText`)."""
    from .readings_s1 import Side
    text = Side(doc.senv, choice_contents(doc, choice), doc.unit_ids).chain_text()
    return None if text is None else f"{text} under {choice_text(doc.sets, choice)}"


def route_refusal(doc, route, couplings=(), narrowings=()):
    """4.1 steps 3 and 5 on the superposed and enumerated routes (Lean's `routeRefusal`): `ReadingsUnsatisfiable`
    when no choice is compatible, else the chain's diagnostic under the first compatible choice whose document the
    chain refuses, among every choice up to the route's budget (MAX_CHOICE_CHECKS superposed, 64 enumerated)."""
    sets = doc.sets
    if route not in ("superposed", "enumerated"):
        return None
    found, _ = choices(sets, couplings, narrowings, limit=0)
    if not found:
        return "ReadingsUnsatisfiable: " + unsatisfiable_ids(sets, couplings, narrowings)
    budget = MAX_CHOICE_CHECKS if route == "superposed" else MAX_CHOICES
    checked, over = choices(sets, couplings, narrowings, limit=budget)
    if over:
        return None
    for choice in checked:
        text = choice_chain_text(doc, choice)
        if text is not None:
            return text
    return None


def choices_checked(sets, route, couplings=(), narrowings=()):
    """The `choices_checked` field of `readings-elaborate`: how many compatible choices' documents were checked."""
    budget = MAX_CHOICE_CHECKS if route == "superposed" else MAX_CHOICES
    found, over = choices(sets, couplings, narrowings, limit=budget)
    return f"over {budget}" if over else len(found)
