"""Python adapter for the ve.discourse@1 document profile.

The frozen environment and document routes receive only the base profile list.
Every reference surface in a unit's source is a slot to account for: a unit
whose content or reading set is admitted must record each one, and its content
and readings must be the elaboration (docs/spec/discourse.md 3.4).
A recorded pronoun, demonstrative or ordinal pair is resolved here: its
accessible candidates are read from the source (registrations in scope, no
competing quantifier of the candidate's sort, the coordinations an ordinal
refers back to), each candidate is expanded into explicit English, and the
expansions with one typed parse are the competitors; the recorded target must
be the unique one and the expansion must reproduce the unit's content. Other
reference forms are recorded but not elaborated in Python: a unit with content
that uses one is `UnsupportedProfile`, never admitted unchecked. The Lean route
(`ve_discourse_route`) is the trusted checker; it reads the same bytes.
"""
from __future__ import annotations

import hashlib
from itertools import product
import re

from .admission import token
from .ast import formula_to_data
from .errors import VEError
from .readings import active_reading_sets
from .wire import digest

PROFILE = "ve.discourse@1"
_FORM_KINDS = {
    "pronoun": {"entity", "unit"}, "demonstrative": {"entity", "unit"},
    "possessive": {"entity"}, "definite": {"entity"},
    "ordinal_pair": {"entity"}, "plural": {"entity"},
    "such": {"predicate"}, "definition_ref": {"predicate"},
    "document_name": {"document"}, "citation": {"claim"},
    "section_ref": {"anchor"}, "navigation": {"anchor", "unit"},
}
_LOCATION = {"section_ref", "navigation"}
_ELABORATED = {"pronoun", "demonstrative", "ordinal_pair"}
_LIMITS = {"anchors": 1024, "mentions": 4096, "names": 1024,
           "documents": 64, "groups": 256, "constraints": 1024}
_BLOCK_KEYS = {"version", "definitions_version", "document_sort", "anchors", "names", "content_names",
               "mentions", "documents", "imports", "groups", "constraints"}
_LEAN_ONLY = {"validity": "validity claims", "self_truth": "self-truth labels", "choices": "recorded reading choices"}
_REFERENCE_WORDS = ("it", "she", "he", "her", "him", "his", "its", "their", "they", "them",
                    "former", "latter", "such")
_PRONOUNS = ("it", "she", "he", "her", "him")
_QUANTIFIERS = ("every", "a", "an", "some")
_CITE_WORDS = ("clause", "section", "article", "lemma")
_MAX_NESTING = 4
_JOIN_LIMIT = 32  # identifiers are at most 64 bytes, so a split name has at most 32 segments


def base_environment(meta):
    """Check the outer declaration, then produce the exact frozen input pair."""
    data = meta["environment"]
    if meta["format"] == "ve-document@1":
        # Unchanged @1 path: only the profile gate of 1.1 is added.
        if type(data) is dict and type(data.get("profiles")) is list and PROFILE in data["profiles"]:
            raise VEError("UnsupportedProfile: ve.discourse@1 requires ve-document@2")
        return data
    if type(data) is not dict or type(data.get("profiles")) is not list:
        raise VEError("invalid environment profiles")
    profiles = data["profiles"]
    if profiles != sorted(set(profiles)) or PROFILE not in profiles or "relational-fol@0" not in profiles:
        raise VEError("UnsupportedProfile: ve.discourse@1 requires a sorted profile list with relational-fol@0")
    if "discourse" not in meta:
        raise VEError("InvalidInput: missing discourse block")
    return {**data, "profiles": [p for p in profiles if p != PROFILE]}


def _array(block, key):
    value = block.get(key, [])
    if type(value) is not list:
        raise VEError(f"InvalidInput: discourse.{key}")
    if len(value) > _LIMITS.get(key, 1_000_000):
        raise VEError(f"ResourceLimit: {key}")
    return value


def _span(value, end):
    return (type(value) is list and len(value) == 2 and
            all(type(x) is int for x in value) and 0 <= value[0] < value[1] <= end)


def _no_null(value):
    if value is None:
        raise VEError("InvalidInput: null in discourse block")
    if type(value) is dict:
        for item in value.values():
            _no_null(item)
    elif type(value) is list:
        for item in value:
            _no_null(item)


def _table(items, key, category):
    result = {}
    for item in items:
        if type(item) is not dict or not token(item.get(key)):
            raise VEError(f"InvalidInput: {category}")
        value = item[key]
        if value in result:
            raise VEError(f"DuplicateDeclaration: {category} {value}")
        result[value] = item
    return result


def _inside(outer, inner):
    return outer[0] <= inner[0] and inner[1] <= outer[1]


def _anchors(block, source):
    anchors = _table(_array(block, "anchors"), "id", "anchor")
    if not anchors:
        raise VEError("InvalidInput: discourse needs a document anchor")
    roots = []
    for aid, anchor in anchors.items():
        if anchor.get("kind") not in {"document", "section", "clause", "item", "article"}:
            raise VEError(f"InvalidInput: anchor {aid}")
        if not _span(anchor.get("span"), len(source)):
            raise VEError(f"InvalidInput: anchor span {aid}")
        parent = anchor.get("parent")
        if parent is None:
            roots.append(aid)
        elif parent not in anchors:
            raise VEError(f"DanglingAnchor: {parent}")
        elif not _inside(anchors[parent]["span"], anchor["span"]):
            raise VEError(f"InvalidInput: anchor span {aid}")
    if len(roots) != 1 or anchors[roots[0]]["kind"] != "document" or anchors[roots[0]]["span"] != [0, len(source)]:
        raise VEError("InvalidInput: anchors need one document root spanning the source")
    for anchor in anchors.values():
        visited = set()
        cursor = anchor
        while "parent" in cursor:
            if cursor["id"] in visited:
                raise VEError("DependencyCycle: anchors")
            visited.add(cursor["id"])
            cursor = anchors[cursor["parent"]]
    siblings = {}
    for anchor in anchors.values():
        parent = anchor.get("parent")
        key = (parent, anchor.get("label"))
        if key in siblings:
            raise VEError(f"DuplicateAnchor: {anchor.get('label')}")
        siblings[key] = anchor
    for anchor in anchors.values():
        peers = [a for a in anchors.values() if a.get("parent") == anchor.get("parent") and a is not anchor]
        if any(max(anchor["span"][0], p["span"][0]) < min(anchor["span"][1], p["span"][1]) for p in peers):
            raise VEError(f"InvalidInput: overlapping anchors {anchor['id']}")
    return anchors


def _joint(block, active):
    sets = {(s["id"], s["version"]): s for s in active if s["status"] == "open"}
    constraints = _array(block, "constraints")
    decoded = []
    for row in constraints:
        if type(row) is not dict or row.get("kind") not in {"requires", "excludes"}:
            raise VEError("InvalidInput: discourse constraint")
        pair = []
        for key in ("a", "b"):
            ref = row.get(key)
            if type(ref) is not list or len(ref) != 3 or type(ref[1]) is not int:
                raise VEError("InvalidInput: discourse constraint reading")
            rs = sets.get((ref[0], ref[1]))
            if rs is None:
                raise VEError(f"InvalidInput: inactive reading set {ref[0]}@{ref[1]}")
            ids = [r["id"] for r in rs["readings"]]
            if ref[2] not in ids:
                raise VEError(f"InvalidInput: reading {ref[2]} not in {ref[0]}@{ref[1]}")
            pair.append((ref[0], ref[1], ids.index(ref[2])))
        decoded.append((row["kind"], *pair))
    count = 1
    ordered = list(sets.values())
    for rs in ordered:
        count *= len(rs["readings"])
        if count > 64:
            return {"status": "UNKNOWN", "budget": 64, "constraints": len(decoded)}
    choices = []
    for indices in product(*(range(len(rs["readings"])) for rs in ordered)):
        choice = {(rs["id"], rs["version"]): index for rs, index in zip(ordered, indices)}
        if all((choice[a[:2]] != a[2] or choice[b[:2]] == b[2]) if kind == "requires"
               else (choice[a[:2]] != a[2] or choice[b[:2]] != b[2])
               for kind, a, b in decoded):
            choices.append({f"{rs['id']}@{rs['version']}": index for rs, index in zip(ordered, indices)})
    if not choices:
        raise VEError("InvalidCompatibility: " + ", ".join(sorted(s["id"] for s in ordered)))
    return {"status": "complete", "choices": choices, "count": len(choices),
            "constraints": len(decoded)}


def joint_assertion(env, active, joint):
    """The disjunction of compatible conjunctions, for the frozen premise gate."""
    from .ast import And, Or, Top, formula_from_data

    if joint["status"] != "complete":
        return None
    open_sets = [rs for rs in active if rs["status"] == "open"]
    if any(any(r["kind"] != "asserted" or r["content"] is None
               for r in rs["readings"]) for rs in open_sets):
        return None
    alternatives = []
    for choice in joint["choices"]:
        conjuncts = [formula_from_data(env, rs["readings"][choice[f"{rs['id']}@{rs['version']}"]]["content"])
                     for rs in open_sets]
        value = Top()
        for formula in reversed(conjuncts):
            value = And(formula, value)
        alternatives.append(value)
    value = alternatives[-1]
    for formula in reversed(alternatives[:-1]):
        value = Or(formula, value)
    return value


def check_joint_extensions(meta, report, joint):
    """Require each lemma and the final report to fit one complete joint choice (the Lean
    `gateOk` over `gateChoices`): each compatible choice also fixes every active authored set at
    its one signed reading, so a label naming an authored set extends exactly when W2 accepts it;
    a `v:all` label needs the set at version v."""
    from .admission import parse_label

    if joint["status"] != "complete":
        return
    authored = {f"{rs['id']}@{rs['version']}": 0
                for rs in active_reading_sets(meta.get("reading_sets", [])) if rs["status"] == "authored"}
    gate = [{**choice, **authored} for choice in joint["choices"]]

    def extends(leaves):
        labels = [parse_label(leaf.get("label")) for leaf in leaves]
        choices = [(label.args[0], label.args[1], label.args[2])
                   for label in labels if label is not None and label.kind == "readings"]
        return any(all(f"{name}@{version}" in choice and index in (None, choice[f"{name}@{version}"])
                       for name, version, index in choices) for choice in gate)

    for lemma in meta.get("lemmas", []):
        if not extends(lemma["leaves"]):
            raise VEError(f"InvalidCompatibility: citation {lemma['name']}")
    if not extends(report["assumptions"]):
        raise VEError(f"InvalidCompatibility: report {report['root']['name']}")


# Reading the source ---------------------------------------------------------

def _words(env):
    """The sort and unary-predicate words a reference surface may use: their symbol names
    (the Lean route's reading of the same bytes) and the English nouns of the sorts."""
    from .english import EnglishVocabulary
    try:
        nouns = EnglishVocabulary(env).sorts
    except VEError:
        nouns = {}
    sorts = {}
    for name in env.sorts:
        sorts[name.lower()] = name
        noun = nouns.get(name)
        if type(noun) is str and re.fullmatch(r"[A-Za-z]+", noun):
            sorts[noun.lower()] = name
    unary = {name.lower() for name, decl in env.predicates.items() if len(decl.arguments) == 1}
    return sorts, unary


def _word_pattern(words):
    return "|".join(re.escape(w) for w in sorted(words, key=len, reverse=True)) or r"(?!)"


_FOLD = {"\u0130": "i", "\u0131": "i", "\u017f": "s", "\u212a": "k"}
_PUNCT = ',;:!?()"'


def _fold(c):
    """The case fold of a character onto a lowercase ASCII letter or digit, or None (the Lean
    `foldChar`): ASCII letters and digits, and the four characters `re.I` equates with ASCII
    letters (İ and ı read i, ſ reads s, the Kelvin sign reads k)."""
    if c.isascii() and c.isalnum():
        return c.lower()
    return _FOLD.get(c)


def _fold_text(text):
    """A text with every character that has a fold folded (the Lean `foldWord`)."""
    return "".join(_fold(c) or c for c in text)


def _segments(text):
    """The segments of a text: its maximal runs of characters with a fold, folded, with their
    character offsets (the Lean `segments`)."""
    out, start = [], None
    for i, c in enumerate(text + " "):
        if i < len(text) and _fold(c) is not None:
            start = i if start is None else start
        elif start is not None:
            out.append((start, i, "".join(_fold(x) for x in text[start:i])))
            start = None
    return out


def _label_end(text, end):
    """The end of a citation label: the first token the discourse lexer reads after offset `end`,
    when it is a word (the Lean `labelEnd`: spaces separate, `,;:!?()"` and a `.` not between two
    ASCII letters or digits are punctuation)."""
    i = end
    while i < len(text) and text[i].isspace():
        i += 1
    j = i
    while j < len(text):
        c = text[j]
        if c.isspace() or c in _PUNCT:
            break
        if c == "." and not (j > i and text[j - 1].isascii() and text[j - 1].isalnum()
                             and j + 1 < len(text) and text[j + 1].isascii() and text[j + 1].isalnum()):
            break
        j += 1
    return j if j > i else None


def _segment_lengths(words, j, sorts, unary, displays):
    """The lengths, in segments, of the reference surfaces starting at segment `j` that end on a
    segment (the Lean `segmentLengths`): a reference word; `this|that` before a sort name's
    segments; `the` before `former|latter` or segments whose `_`-join is a unary predicate; a
    document display's segments."""
    after = words[j + 1:]
    lengths = []
    if words[j] in _REFERENCE_WORDS:
        lengths.append(1)
    if words[j] in ("this", "that"):
        for sort in sorts:
            phrase = [w for _, _, w in _segments(sort)]
            if phrase and after[:len(phrase)] == phrase:
                lengths.append(len(phrase) + 1)
    if words[j] == "the":
        if after[:1] and after[0] in ("former", "latter"):
            lengths.append(2)
        lengths.extend(k + 2 for k in range(min(len(after), _JOIN_LIMIT)) if "_".join(after[:k + 1]) in unary)
    for display in displays:
        phrase = [w for _, _, w in _segments(display)]
        if phrase and words[j:j + len(phrase)] == phrase:
            lengths.append(len(phrase))
    return lengths


def reference_surfaces(doc, text, displays=()):
    """The reference surfaces of one unit's text as (start, end) character offsets, in order
    (docs/spec/discourse.md 4.1(6); the Lean `textSurfaces`). The text is read as its segments; at
    each segment the surfaces starting there are a reference word, `this|that` before a sort name,
    `the` before `former|latter` or a unary predicate, a document display, and after `by` a
    citation word through its label. Scanning left to right, the longest surface starting at a
    segment is taken and the scan resumes after it, so a longer surface is never split into its
    shorter parts. A sort is read by its name and by its declared singular noun."""
    env = doc["environment"]
    sorts = sorted(env.sorts) + [d.verbalisation.singular for d in env.sorts.values() if d.verbalisation]
    unary = {name for name, decl in env.predicates.items() if len(decl.arguments) == 1}
    segments = _segments(text)
    words = [w for _, _, w in segments]
    found, j = [], 0
    while j < len(segments):
        ends = [segments[j + n - 1][1] for n in _segment_lengths(words, j, sorts, unary, displays)]
        if words[j] in _CITE_WORDS and j and words[j - 1] == "by":
            label = _label_end(text, segments[j][1])
            ends.append(segments[j][1] if label is None else label)
        if not ends:
            j += 1
            continue
        end = max(ends)
        found.append((segments[j][0], end))
        j += 1
        while j < len(segments) and segments[j][0] < end:
            j += 1
    return found


def _innermost(anchors, span):
    containing = [a for a in anchors.values() if _inside(a["span"], span)]
    return min(containing, key=lambda a: a["span"][1] - a["span"][0]) if containing else None


def _scope_texts(doc, unit, position):
    """The texts accessibility reads (4.2): each earlier unit of the unit's innermost anchor,
    then the unit's own text before the mention."""
    anchor = _innermost(doc["discourse_anchors"], unit["span"])
    if anchor is None:
        return []
    texts = [u["source"] for u in doc["units"]
             if u["span"][1] <= unit["span"][0] and _inside(anchor["span"], u["span"])]
    texts.append(doc["source"][unit["span"][0]:position].decode("utf-8", "replace"))
    return texts


def _competing_quantifier(doc, unit, position, sort):
    """A quantified mention of `sort` in an earlier sentence of the innermost anchor or earlier in
    the unit's own sentence: `every|a|an|some [modifier] <sort word>` (the Lean `binderAt`)."""
    sorts, _ = _words(doc["environment"])
    nouns = [w for w, s in sorts.items() if s == sort]
    pattern = re.compile(r"\b(?:" + "|".join(_QUANTIFIERS) + r")\s+(?:[\w-]+\s+)?(?:" + _word_pattern(nouns) + r")\b",
                         re.I)
    return any(pattern.search(text) for text in _scope_texts(doc, unit, position))


def _spellings(registration):
    return [registration["display"], *registration.get("aliases", [])]


def _coordinations(doc, unit, position, names):
    """The coordinations `c1 and c2` of registered spellings in the texts accessibility reads,
    in their order: the antecedents of `the former`/`the latter` (the Lean `earlierPairs`)."""
    texts = _scope_texts(doc, unit, position)
    pairs = []
    for first in names:
        for second in names:
            if any(re.search(r"(?<![\w-])" + re.escape(a) + r"\s+and\s+" + re.escape(b) + r"(?![\w-])", text, re.I)
                   for text in texts for a in _spellings(first) for b in _spellings(second)):
                pairs.append((first["constant"], second["constant"]))
    return pairs


# Resolution ----------------------------------------------------------------

def _surface_fits(doc, mention):
    """A recorded pronoun, demonstrative or ordinal pair covers exactly its surface: a pronoun,
    `this|that <sort word>`, `the former|latter` (otherwise it is no slot: MentionNotSlot)."""
    surface = _fold_text(doc["source"][mention["span"][0]:mention["span"][1]].decode("utf-8", "replace").strip())
    sorts, _ = _words(doc["environment"])
    form = mention["form"]
    if form == "pronoun":
        return surface in _PRONOUNS
    if form == "demonstrative":
        return re.fullmatch(r"(?:this|that)\s+(?:" + _word_pattern(sorts) + ")", surface) is not None
    return surface in {"the former", "the latter"}


def _accessible(doc, unit, mention, names, anchors):
    """The accessible targets of a recorded pronoun, demonstrative or ordinal pair, each with the
    constant its expansion names."""
    form = mention["form"]
    env = doc["environment"]
    if form == "ordinal_pair":
        surface = doc["source"][mention["span"][0]:mention["span"][1]].decode("utf-8").lower().split()
        index = {"former": 0, "latter": 1}.get(surface[-1] if surface else "")
        if index is None:
            return []
        scoped = [n for n in names if _inside(anchors[n["scope"]]["span"], unit["span"])]
        return [({"kind": "entity", "name": pair[index], "pair": list(pair)}, pair[index])
                for pair in _coordinations(doc, unit, mention["span"][0], scoped)]
    result = []
    for registration in names:
        constant = registration["constant"]
        if not _inside(anchors[registration["scope"]]["span"], unit["span"]):
            continue
        if _competing_quantifier(doc, unit, mention["span"][0], env.constants[constant].sort):
            continue
        result.append(({"kind": "entity", "name": constant}, constant))
    return result


def _expanded(doc, unit, choices):
    """The unit's text with each mention replaced by an explicit name: its one typed parse."""
    from .english import parse_english
    start, end = unit["span"]
    raw, cursor = b"", start
    for mention, display in sorted(choices, key=lambda x: x[0]["span"][0]):
        raw += doc["source"][cursor:mention["span"][0]] + display.encode("utf-8")
        cursor = mention["span"][1]
    raw += doc["source"][cursor:end]
    try:
        expanded = raw.decode("utf-8")
        parsed = parse_english(doc["environment"], expanded)
        if len(parsed.formulas) != 1:
            return None
        return expanded, formula_to_data(doc["environment"], parsed.formulas[0])
    except (VEError, UnicodeError):
        return None


def _target_key(target):
    return tuple((k, tuple(v) if type(v) is list else v) for k in ("kind", "name", "pair") if (v := target.get(k)) is not None)


def _same_target(recorded, candidate):
    return all(recorded.get(k) == candidate.get(k) for k in ("kind", "name", "pair"))


def _resolve_unit(doc, unit, rows, names, anchors, readings=()):
    """Resolve a unit's recorded pronouns, demonstratives and ordinal pairs together: every
    accessible assignment is a competitor, a typed expansion is the only filter (4.3). The
    unit's recorded meaning, its content and every reading of its active set, must be the
    expansion's formula."""
    displays = {n["constant"]: n["display"] for n in names}
    candidates = [_accessible(doc, unit, m, names, anchors) for m in rows]
    typed = []
    for combo in product(*candidates):
        expansion = _expanded(doc, unit, [(m, displays[c]) for m, (_, c) in zip(rows, combo)])
        if expansion is not None:
            typed.append((combo, expansion))
    recorded = [m["target"] for m in rows]
    accessible = [next((t for t, _ in cands if _same_target(r, t)), None) for r, cands in zip(recorded, candidates)]
    if all(a is not None for a in accessible):
        combo = [(m, displays[a["name"]]) for m, a in zip(rows, accessible)]
        own = _expanded(doc, unit, combo)
        if own is None:
            m = rows[0]
            raise VEError(f"IllTypedTarget: {m['id']}: {m['target'].get('name')}")
    if not typed:
        raise VEError(f"UnresolvedReference: {rows[0]['id']}")
    if len(typed) > 1:
        # competitors differ when their targets do (the pair of an ordinal included), not only
        # when the constants they name do: two coordinations are two candidates (4.2)
        for i, m in enumerate(rows):
            targets = {_target_key(combo[i][0]) for combo, _ in typed}
            if len(targets) > 1:
                names_at = sorted({combo[i][1] for combo, _ in typed})
                raise VEError(f"AmbiguousReference: {m['id']}: {', '.join(names_at)}")
    for m, a in zip(rows, accessible):
        if a is None:
            raise VEError(f"InaccessibleTarget: {m['id']}: {m['target'].get('name')}")
    expanded, formula = typed[0][1]
    recorded = [unit["content"]] if unit["content"] is not None else []
    if any(meaning != formula for meaning in [*recorded, *readings]):
        raise VEError(f"ManifestMismatch: bound.{unit['id']}")
    return expanded


# Groups -------------------------------------------------------------------

def _conjuncts(formula):
    if type(formula) is list and len(formula) == 3 and formula[0] == "and":
        return _conjuncts(formula[1]) + _conjuncts(formula[2])
    return [formula]


def _contains_var(formula, index=0):
    if formula == ["var", index]:
        return True
    if type(formula) is list:
        if len(formula) == 3 and formula[0] in {"exists", "forall"}:
            return _contains_var(formula[2], index + 1)
        return any(_contains_var(item, index) for item in formula[1:])
    return False


def _same_witness(content):
    """One outermost existential whose body is a conjunction in which every conjunct mentions
    the bound variable (4.6, the Lean `sharedWitness`)."""
    return (type(content) is list and len(content) == 3 and content[0] == "exists"
            and type(content[2]) is list and len(content[2]) == 3 and content[2][0] == "and"
            and all(_contains_var(c) for c in _conjuncts(content[2])))


def _parse_one(doc, text):
    from .english import parse_english
    try:
        parsed = parse_english(doc["environment"], text)
    except VEError:
        return None
    if len(parsed.formulas) != 1:
        return None
    return formula_to_data(doc["environment"], parsed.formulas[0])


def group_reading(doc, spans):
    """The owning set's reading regenerated per group from the spans' English (4.6): the first
    span `a|an|some [ADJ] NOUN is P.` gives the witness and its body; each later span
    `PRONOUN is Q.` predicates Q of the same witness (the pronoun read as the first span's noun
    phrase); the reading is one existential over the conjunction of the bodies."""
    units = {u["id"]: u for u in doc["units"]}
    first = re.match(r"(?i)(?:a|an|some)\s+(\S+)\s+(is\s.*)", units[spans[0]]["source"].strip(), re.S)
    if first is None:
        return None
    # `a`, `an` and `some` introduce the same existential witness (the Lean grammar's `some`)
    subject = "Some " + first[1]
    opening = _parse_one(doc, subject + " " + first[2])
    if opening is None or opening[0] != "exists":
        return None
    sort, bodies = opening[1], [opening[2]]
    for uid in spans[1:]:
        later = re.match(r"(?i)(" + "|".join(_PRONOUNS) + r")\s+(is\s.*)", units[uid]["source"].strip(), re.S)
        if later is None:
            return None
        rewritten = _parse_one(doc, subject + " " + later[2])
        if rewritten is None or rewritten[0] != "exists" or rewritten[1] != sort:
            return None
        bodies.append(rewritten[2])
    body = bodies[-1]
    for earlier in reversed(bodies[:-1]):
        body = ["and", earlier, body]
    return ["exists", sort, body]


# Decoding the block (3.1) -----------------------------------------------------

_ANCHOR_KINDS = {"document", "section", "clause", "item", "article"}
_TARGET_KINDS = {"entity", "predicate", "unit", "anchor", "rule", "claim", "document"}
_READINGS = {"assertive", "presuppositional", "distributive"}


def _fields(item, required, optional=()):
    """Exactly the required fields and some of the optional ones (the Lean `displayFields`)."""
    if type(item) is not dict or not set(required) <= set(item) or set(item) - set(required) - set(optional):
        raise VEError("InvalidInput: discourse fields")


def _string(value):
    if type(value) is not str:
        raise VEError("InvalidInput: string expected")
    return value


def _strings(value):
    if type(value) is not list:
        raise VEError("InvalidInput: array expected")
    return [_string(v) for v in value]


def _nat(value):
    if type(value) is not int or value < 0:
        raise VEError("InvalidInput: natural number expected")
    return value


def _rows(block, key):
    value = block.get(key, [])
    if type(value) is not list:
        raise VEError(f"InvalidInput: discourse.{key}")
    return value


def _optional(item, decode, *keys):
    for key in keys:
        if key in item:
            decode(item[key])


def decode_block(block, reading_sets=()):
    """The strict decode of a `discourse` block (3.1), the Lean `Wire.decodeManifest`: every table
    has its wire shape, optional fields are absent (never null), and a group's, constraint's or
    recorded choice's reading names a reading of a declared set version (1.5). It reads no unit
    and resolves nothing: it is what a stored document must pass (4.1(10))."""
    from .ast import _Decoder
    if type(block) is not dict:
        raise VEError("InvalidInput: discourse block")
    if not block:
        return
    _no_null(block)
    _fields(block, ("version", "anchors"), (*_BLOCK_KEYS, *_LEAN_ONLY))
    if block["version"] != PROFILE:
        raise VEError("InvalidInput: discourse version")
    _optional(block, _string, "definitions_version", "document_sort")
    if type(block["anchors"]) is not list:
        raise VEError("InvalidInput: discourse.anchors")
    for anchor in block["anchors"]:
        _fields(anchor, ("id", "kind", "label", "span"), ("parent", "edition", "exports"))
        _string(anchor["id"]), _string(anchor["label"])
        if anchor["kind"] not in _ANCHOR_KINDS:
            raise VEError(f"InvalidInput: anchor kind {anchor['kind']}")
        _span_shape(anchor["span"])
        _optional(anchor, _string, "parent", "edition")
        _optional(anchor, _strings, "exports")
    for name in _rows(block, "names"):
        _fields(name, ("constant", "display", "scope"), ("aliases",))
        _string(name["constant"]), _string(name["display"]), _string(name["scope"])
        _optional(name, _strings, "aliases")
    for item in _rows(block, "content_names"):
        _fields(item, ("name", "units", "scope"))
        _string(item["name"]), _strings(item["units"]), _string(item["scope"])
    for mention in _rows(block, "mentions"):
        _fields(mention, ("id", "unit", "span", "form", "target"), ("restriction", "reading", "presupposition_unit"))
        _string(mention["id"]), _string(mention["unit"]), _span_shape(mention["span"])
        if mention["form"] not in _FORM_KINDS:
            raise VEError(f"InvalidInput: form {mention['form']}")
        target = mention["target"]
        _fields(target, ("kind",), ("name", "version", "members", "pair", "units", "content_name"))
        if target["kind"] not in _TARGET_KINDS:
            raise VEError(f"InvalidInput: target kind {target['kind']}")
        _optional(target, _string, "name", "content_name")
        _optional(target, _nat, "version")
        _optional(target, _strings, "members", "units")
        if "pair" in target and len(_strings(target["pair"])) != 2:
            raise VEError("InvalidInput: pair")
        if "reading" in mention and mention["reading"] not in _READINGS:
            raise VEError(f"InvalidInput: reading {mention['reading']}")
        if "restriction" in mention:
            try:
                _Decoder().decode(mention["restriction"])
            except (VEError, SyntaxError) as exc:
                raise VEError(f"InvalidInput: restriction of {mention['id']}") from exc
        _optional(mention, _string, "presupposition_unit")
    for declaration in _rows(block, "documents"):
        _fields(declaration, ("name", "display", "refers", "version"),
                ("author", "supersedes", "scope", "source_id", "document_id"))
        _string(declaration["name"]), _strings(declaration["display"]), _nat(declaration["version"])
        refers = declaration["refers"]
        if refers != "self" and not (type(refers) is dict and len(refers) == 1
                                     and next(iter(refers)) in {"embedded", "import", "part"}
                                     and type(next(iter(refers.values()))) is str):
            raise VEError("InvalidInput: refers")
        _optional(declaration, _string, "author", "scope", "source_id", "document_id")
        _optional(declaration, _strings, "supersedes")
    imports = block.get("imports", {})
    if type(imports) is not dict:
        raise VEError("InvalidInput: discourse.imports")
    for pin in imports.values():
        _fields(pin, ("source_id", "document_id", "bytes"))
        _string(pin["source_id"]), _string(pin["document_id"]), _string(pin["bytes"])
    readings = {(s.get("id"), s.get("version")): [r.get("id") for r in s.get("readings", []) if type(r) is dict]
                for s in reading_sets if type(s) is dict and type(s.get("readings", [])) is list}

    def reading(set_id, version, reading_id):
        if reading_id not in readings.get((set_id, version), []):
            raise VEError(f"InvalidInput: reading {reading_id} not in {set_id}@{version}")

    def triple(value):
        if (type(value) is not list or len(value) != 3 or type(value[0]) is not str
                or type(value[2]) is not str):
            raise VEError("InvalidInput: discourse constraint reading")
        reading(value[0], _nat(value[1]), value[2])

    for group in _rows(block, "groups"):
        _fields(group, ("set", "version", "reading", "spans"))
        reading(_string(group["set"]), _nat(group["version"]), _string(group["reading"]))
        _strings(group["spans"])
    for row in _rows(block, "constraints"):
        _fields(row, ("kind", "a", "b"))
        if row["kind"] not in {"requires", "excludes"}:
            raise VEError(f"InvalidInput: constraint kind {row['kind']}")
        triple(row["a"]), triple(row["b"])
    for binding in _rows(block, "validity"):
        _fields(binding, ("unit", "document", "holds"))
        _string(binding["unit"]), _string(binding["document"])
        if type(binding["holds"]) is not bool:
            raise VEError("InvalidInput: validity holds")
    _strings(block.get("self_truth", []))
    for choice in _rows(block, "choices"):
        triple(choice)


def _span_shape(value):
    if type(value) is not list or len(value) != 2:
        raise VEError("InvalidInput: span")
    _nat(value[0]), _nat(value[1])


# Stored documents (4.1(10)) --------------------------------------------------

def _stored_identities(raw, name):
    from .document import stored_identities
    try:
        return stored_identities(raw)
    except VEError as exc:
        raise VEError(f"InvalidInput: document {name}: {exc}") from exc


def _stored_block(meta, name):
    """A stored `@2` document's whole discourse block decodes, as the importing document's does."""
    if meta["format"] != "ve-document@2":
        return
    try:
        decode_block(meta.get("discourse"), meta.get("reading_sets", []))
    except VEError as exc:
        raise VEError(f"InvalidInput: document {name}: {exc}") from exc


def _stored_children(meta, source, directory):
    """The stored documents a document names: its imports' sibling files and embedded units."""
    block = meta.get("discourse", {}) if type(meta.get("discourse")) is dict else {}
    imports = block.get("imports", {}) if type(block.get("imports", {})) is dict else {}
    children = []
    for pin in imports.values():
        path = directory / pin.get("bytes", "") if type(pin) is dict and type(pin.get("bytes")) is str else None
        if path is not None and path.is_file():
            children.append(path.read_bytes())
    units = {u.get("id"): u for u in meta.get("units", []) if type(u) is dict}
    for declaration in block.get("documents", []) if type(block.get("documents", [])) is list else []:
        refers = declaration.get("refers") if type(declaration) is dict else None
        if type(refers) is dict and "embedded" in refers and refers["embedded"] in units:
            span = units[refers["embedded"]].get("span")
            if _span(span, len(source)):
                children.append(source[span[0]:span[1]])
    return children


def _chain(raws, directory, depth):
    """Source ids of the stored chain to depth `depth` (None: deeper than the budget)."""
    from .document import _split, stored_identities
    ids = []
    for raw in raws:
        if depth == 0:
            return None
        try:
            meta, source, _ = _split(raw)
            source_id = stored_identities(raw)[1]
        except VEError:
            ids.append(hashlib.sha256(raw).hexdigest())
            continue
        rest = _chain(_stored_children(meta, source, directory), directory, depth - 1)
        if rest is None:
            return None
        ids.extend([source_id, *rest])
    return ids


def check_stored_documents(doc, documents, imports, units):
    """Integrity of every imported and embedded document (4.1(10)): stored bytes re-fingerprint
    to their pinned source id, each decodes and its recomputed document id is its pin, the chain
    repeats no source id and nests at most four deep. Whether a stored document is admitted is
    the second-phase outcome of a validity claim, never a condition here."""
    directory = doc["directory"]
    stored = []
    for key, pin in imports.items():
        name = next((n for n, d in documents.items() if d.get("refers") == {"import": key}), key)
        path = directory / pin["bytes"] if type(pin["bytes"]) is str else None
        if path is None or not path.is_file():
            continue
        raw = path.read_bytes()
        try:
            meta, sid, did = _stored_identities(raw, name)
        except VEError:
            if hashlib.sha256(raw).hexdigest() != pin["source_id"]:
                raise VEError(f"StaleTarget: {name}") from None
            raise
        if sid != pin["source_id"]:
            raise VEError(f"StaleTarget: {name}")
        _stored_block(meta, name)
        if did != pin["document_id"]:
            raise VEError(f"StaleTarget: {name}")
        stored.append(raw)
    for name, declaration in documents.items():
        refers = declaration.get("refers")
        if type(refers) is dict and "embedded" in refers:
            start, end = units[refers["embedded"]]["span"]
            raw = doc["source"][start:end]
            meta, sid, did = _stored_identities(raw, name)
            _stored_block(meta, name)
            if declaration.get("document_id", did) != did or declaration.get("source_id", sid) != sid:
                raise VEError(f"StaleTarget: {name}")
            stored.append(raw)
    chain = _chain(stored, directory, _MAX_NESTING)
    if chain is None:
        raise VEError("ResourceLimit: document nesting")
    seen = {doc["source_id"]}
    for source_id in chain:
        if source_id in seen:
            raise VEError(f"ImportCycle: {source_id}")
        seen.add(source_id)


# The validator ---------------------------------------------------------------

def _definition_version(env, name):
    """The W3 definition version of a predicate at `definitions_version`: the base pair declares
    no definition versions (W2 admission defers definitions), so there is none."""
    return None


def _unrecorded(doc, unit, rows, displays):
    """The first reference surface of a unit with meaning that no recorded formula-producing
    mention records with exactly its byte range (containing or overlapping it is not enough): a
    location binding (`navigation`, `section_ref`) is never a slot, so it never accounts for one
    (the Lean `uncoveredSurface`)."""
    start = unit["span"][0]
    recorded = {tuple(m["span"]) for m in rows}
    for a, b in reference_surfaces(doc, unit["source"], displays):
        begin = start + len(unit["source"][:a].encode("utf-8"))
        end = start + len(unit["source"][:b].encode("utf-8"))
        if (begin, end) not in recorded:
            return begin, end
    return None


def validate_discourse(doc):
    block = doc["meta"]["discourse"]
    if type(block) is not dict:
        raise VEError("InvalidInput: discourse block")
    _no_null(block)
    for key, feature in _LEAN_ONLY.items():
        if block.get(key):
            raise VEError(f"UnsupportedProfile: ve.discourse@1 {feature} are not implemented in Python")
    if block and block.get("version") != PROFILE:
        raise VEError("InvalidInput: discourse version")
    if set(block) - _BLOCK_KEYS - set(_LEAN_ONLY):
        raise VEError("InvalidInput: discourse field")
    if block.get("definitions_version", doc["environment"].environment_id) != doc["environment"].environment_id:
        raise VEError(f"StaleTarget: definitions@{block['definitions_version']}")
    env, units = doc["environment"], {u["id"]: u for u in doc["units"]}
    active = active_reading_sets(doc["meta"].get("reading_sets", []))
    grouped = set()
    anchors = _anchors(block, doc["source"]) if block else {}
    doc["discourse_anchors"] = anchors
    names = _array(block, "names")
    for name in names:
        if type(name) is not dict or name.get("constant") not in env.constants or name.get("scope") not in anchors:
            raise VEError("InvalidInput: discourse name")
        if type(name.get("display")) is not str or type(name.get("aliases", [])) is not list:
            raise VEError("InvalidInput: discourse name display")
    constants = [name["constant"] for name in names]
    for i, constant in enumerate(constants):
        if constant in constants[:i]:
            raise VEError(f"DuplicateDeclaration: name {constant}")
    for i, name in enumerate(names):
        for other in names[i + 1:]:
            if set([name["display"], *name.get("aliases", [])]) & set([other["display"], *other.get("aliases", [])]):
                if max(anchors[name["scope"]]["span"][0], anchors[other["scope"]]["span"][0]) < min(anchors[name["scope"]]["span"][1], anchors[other["scope"]]["span"][1]):
                    raise VEError(f"DuplicateDeclaration: name {name['display']}")
    content_names = _array(block, "content_names")
    for item in content_names:
        if type(item) is not dict or item.get("scope") not in anchors or type(item.get("units")) is not list or any(u not in units for u in item["units"]):
            raise VEError("InvalidInput: content_name")
        if type(item.get("name")) is not str or not item["name"]:
            raise VEError("InvalidInput: content_name")
    for i, item in enumerate(content_names):
        for other in content_names[i + 1:]:
            if item["name"] == other["name"] and max(
                    anchors[item["scope"]]["span"][0], anchors[other["scope"]]["span"][0]) < min(
                    anchors[item["scope"]]["span"][1], anchors[other["scope"]]["span"][1]):
                raise VEError(f"DuplicateDeclaration: content_name {item['name']}")
    document_sort = block.get("document_sort")
    documents = _table(_array(block, "documents"), "name", "document")
    if documents:
        if document_sort not in env.sorts or {n for n, c in env.constants.items() if c.sort == document_sort} != set(documents):
            raise VEError(f"InvalidInput: document sort {document_sort} has other constants")
    imports = block.get("imports", {})
    if type(imports) is not dict or len(imports) > 64:
        raise VEError("ResourceLimit: imports")
    for key, pin in imports.items():
        if type(pin) is not dict or set(pin) != {"source_id", "document_id", "bytes"}:
            raise VEError(f"InvalidInput: import {key}")
    for name, declaration in documents.items():
        refers = declaration.get("refers")
        if refers == "self":
            if "source_id" in declaration or "document_id" in declaration:
                raise VEError(f"InvalidInput: self document pin {name}")
        elif type(refers) is dict and len(refers) == 1:
            ref_kind, ref_id = next(iter(refers.items()))
            if ref_kind == "part":
                if ref_id not in anchors:
                    raise VEError(f"DanglingAnchor: {ref_id}")
            elif ref_kind == "embedded":
                if ref_id not in units or units[ref_id]["kind"] != "meta":
                    raise VEError(f"UnknownDocument: {name}")
            elif ref_kind == "import":
                pin = imports.get(ref_id)
                if pin is None:
                    raise VEError(f"UnknownDocument: {name}")
                if (declaration.get("source_id"), declaration.get("document_id")) != (
                        pin["source_id"], pin["document_id"]):
                    raise VEError(f"ManifestMismatch: documents.{name}")
            else:
                raise VEError(f"InvalidInput: document refers {name}")
        else:
            raise VEError(f"InvalidInput: document refers {name}")
    check_stored_documents(doc, documents, imports, units)
    displays = [d for declaration in documents.values() for d in declaration.get("display", [])
                if type(d) is str]
    mentions = _table(_array(block, "mentions"), "id", "mention")
    by_unit = {}
    for mid, m in mentions.items():
        uid = m.get("unit")
        if uid not in units or not _span(m.get("span"), len(doc["source"])) or not _inside(units[uid]["span"], m["span"]):
            raise VEError(f"InvalidInput: mention {mid} span")
        form, target = m.get("form"), m.get("target")
        if form not in _FORM_KINDS or type(target) is not dict:
            raise VEError(f"InvalidInput: mention {mid}")
        kind = target.get("kind")
        if kind not in _FORM_KINDS[form]:
            raise VEError(f"TargetKindMismatch: {mid}: {form}, {kind}")
        if "reading" in m and m["reading"] not in {"assertive", "presuppositional", "distributive"}:
            raise VEError(f"InvalidInput: reading {m['reading']}")
        by_unit.setdefault(uid, []).append(m)
    for uid, rows in by_unit.items():
        rows.sort(key=lambda m: (m["span"][0], -m["span"][1]))
        for i, a in enumerate(rows):
            for b in rows[i + 1:]:
                if a["span"][1] <= b["span"][0]:
                    break
                if not _inside(a["span"], b["span"]):
                    raise VEError(f"InvalidInput: mentions {a['id']}, {b['id']} overlap")
    statuses = {}
    for mid, m in mentions.items():
        target = m["target"]
        kind, form = target["kind"], m["form"]
        if "version" in target:
            # a pin is checked, never carried: only a definition_ref to a predicate has one, and it
            # must be the regenerated definition version (none is declared: the Lean `pinOk`)
            if form != "definition_ref" or kind != "predicate" or type(target.get("name")) is not str:
                raise VEError(f"InvalidInput: mention {mid} target")
            if _definition_version(env, target["name"]) != target["version"]:
                raise VEError(f"StaleTarget: {mid}: {target['name']}@{target['version']}")
        if kind == "entity":
            if form == "plural":
                members = target.get("members")
                if type(members) is not list or len(members) < 2 or len(set(members)) != len(members):
                    raise VEError("InvalidInput: plural members")
            elif form == "ordinal_pair":
                pair = target.get("pair")
                if type(pair) is not list or len(pair) != 2 or target.get("name") not in pair:
                    raise VEError("InvalidInput: ordinal pair")
        elif kind == "anchor":
            if target.get("name") not in anchors:
                raise VEError(f"DanglingAnchor: {target.get('name')}")
        elif kind == "predicate":
            if target.get("name") not in env.predicates:
                raise VEError(f"UnresolvedReference: {mid}")
        elif kind == "unit":
            if type(target.get("units")) is not list or any(u not in units for u in target["units"]):
                raise VEError(f"UnresolvedReference: {mid}")
            if "content_name" in target and not any(c["name"] == target["content_name"] and c["units"] == target["units"] for c in content_names):
                raise VEError(f"ManifestMismatch: mentions.{mid}.content_name")
        elif kind == "document" and target.get("name") not in documents:
            raise VEError(f"UnknownDocument: {target.get('name')}")
        elif kind == "rule":
            rules = {u["content"]["norm"]["name"] for u in doc["units"]
                     if u["kind"] == "norm" and type(u["content"]) is dict and "norm" in u["content"]}
            if target.get("name") not in rules:
                raise VEError(f"UnknownRule: {target.get('name')}")
        elif kind == "claim":
            lemmas = doc["meta"].get("lemmas", [])
            if target.get("name") not in {l.get("meaning_id") for l in lemmas if type(l) is dict}:
                raise VEError("Citation is absent, cyclic, or not earlier in the bundle")
        statuses[mid] = "navigation" if form in _LOCATION else "recorded"
    groups = _array(block, "groups")
    for group in groups:
        if type(group) is dict and type(group.get("spans")) is list:
            grouped.update(group["spans"])
    # a unit's meaning is its content or the readings of its active set (W2); either way its
    # reference surfaces are slots, so a reading set is never a way around them. Every unit is
    # checked, in document order, before any unit is resolved (the Lean `coverageOk`).
    def has_meaning(unit):
        return unit["content"] is not None or any(s["unit"] == unit["id"] for s in active)
    for unit in doc["units"]:
        if has_meaning(unit) and unit["id"] not in grouped:
            producing = [m for m in by_unit.get(unit["id"], []) if m["form"] not in _LOCATION]
            gap = _unrecorded(doc, unit, producing, displays)
            if gap is not None:
                raise VEError(f"UnrecordedSlot: {unit['id']}: [{gap[0]}, {gap[1]})")
    presentations = {}
    for unit in doc["units"]:
        rows = by_unit.get(unit["id"], [])
        producing = [m for m in rows if m["form"] not in _LOCATION]
        readings = [r["content"] for s in active if s["unit"] == unit["id"] for r in s["readings"]]
        meaning = has_meaning(unit)
        if not producing or unit["id"] in grouped:
            continue
        unsupported = sorted({m["form"] for m in producing} - _ELABORATED)
        if unsupported:
            if meaning:
                raise VEError(f"UnsupportedProfile: ve.discourse@1 {', '.join(unsupported)} elaboration "
                              f"is not implemented in Python ({unit['id']})")
            continue
        for m in producing:
            if not _surface_fits(doc, m):
                raise VEError(f"MentionNotSlot: {m['id']}")
        entity = [m for m in producing if m["target"]["kind"] == "entity"]
        if len(entity) != len(producing):
            if meaning:
                raise VEError(f"UnsupportedProfile: ve.discourse@1 unit reference elaboration "
                              f"is not implemented in Python ({unit['id']})")
            continue
        presentation = _resolve_unit(doc, unit, sorted(producing, key=lambda m: m["span"][0]), names, anchors,
                                     readings)
        for m in producing:
            statuses[m["id"]] = "resolved"
        if meaning:
            presentations[unit["id"]] = presentation
    references = [{"mention": mid, "unit": m["unit"], "form": m["form"], "target": m["target"],
                   "status": statuses[mid]} for mid, m in mentions.items()]
    for group in groups:
        if type(group) is not dict or type(group.get("spans")) is not list or not group["spans"] or len(group["spans"]) > 16:
            raise VEError("InvalidInput: group")
        rs = next((s for s in active if (s["id"], s["version"]) == (group.get("set"), group.get("version"))), None)
        if rs is None or group.get("reading") not in [r["id"] for r in rs["readings"]] or rs["unit"] != group["spans"][0]:
            raise VEError("InvalidInput: group reading")
        if rs["status"] == "authored":
            raise VEError("UnsupportedProfile: authored discourse group elaboration is not implemented")
        name = f"{rs['id']}@{rs['version']}:{group['reading']}"
        for uid in group["spans"]:
            if uid not in units or units[uid]["content"] is not None or any(s["unit"] == uid and s is not rs for s in active):
                raise VEError(f"IndependentFragment: {uid}")
            if any(m["form"] not in _LOCATION for m in by_unit.get(uid, [])):
                raise VEError(f"IndependentFragment: {uid}")
        reading = next(r for r in rs["readings"] if r["id"] == group["reading"])
        if not _same_witness(reading.get("content")):
            raise VEError(f"WitnessSplit: {name}")
        regenerated = group_reading(doc, group["spans"])
        if regenerated is None:
            raise VEError(f"InvalidInput: group {name} spans are outside the supported fragment")
        if regenerated != reading["content"]:
            raise VEError(f"ManifestMismatch: groups.{name}")
        for uid in group["spans"]:
            units[uid]["status"] = units[rs["unit"]]["status"]
    joint = _joint(block, active)
    # the block's own wire shape, exactly as a stored document's is decoded (Lean decodeManifest)
    decode_block(block, active)
    return {"references": references, "groups": groups, "joint": joint,
            "presentations": presentations}


def report_discourse(doc, result):
    info = doc["discourse"]
    result["references"] = info["references"]
    result["groups"] = info["groups"]
    result["reviewed_presentations"] = info.get("presentations", {})
    result["joint_choices"] = {k: v for k, v in info["joint"].items() if k != "choices"}
    inner_id = result.get("admission", {}).get("report_id") or digest(
        "ve-document-inner@1\n", {"document_id": doc["document_id"],
                                   "premises": result["premises"]})
    result["report_id"] = digest(
        "ve-discourse-report@1\n",
        {"profiles": doc["meta"]["environment"]["profiles"],
         "environment_id": doc["environment"].environment_id,
         "document_id": doc["document_id"],
         "report_id": inner_id,
         "references": result["references"], "validity": []})
