"""Strict experimental speech-acts@0 semantic core.

This module deliberately has no admission dispatch.  A checked Lean speech route
is required before speech-act documents can become trusted P0 evidence.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from itertools import product
import re

from .ast import (And, Const, Eq, Not, Or, Top, Var, _Checker, _Decoder,
                  _to_data, formula_from_data)
from .errors import ResourceLimit, VEError
from .norms import Norm, NormDocument, _instantiate
from .wire import digest

_TOKEN = re.compile(r"[A-Za-z0-9_.-]{1,64}\Z", re.ASCII)
_PHRASE = re.compile(r"the [A-Za-z][A-Za-z'-]*(?: [A-Za-z][A-Za-z'-]*)*\Z", re.ASCII)
_ALLOWED = {"relational-fol@0", "norms@0", "speech-acts@0"}
# The proof-task act of 1.4, in a phrase W1's frozen act linter accepts.
PROOF_TASK_ACT = "{0} submit a proof of {1}"


def validate_scope(raw, sorts, constants, predicates):
    """Validate the identity-bound task legend without changing old environments.

    Every reference is first a name (a string), with the block's structure and
    phrase checks, and only then resolved, in the order of Lean's `parseScope`,
    `checkPhrases` and `checkSpeech`: a mistyped sort or constant is a block
    error, never an `UnknownSymbol` or a crash.
    """
    block = VEError("InvalidInput: speech_acts block")
    if type(raw) is not dict or "task" not in raw or set(raw) - {"task", "addressee", "definites"}:
        raise block
    if type(raw["task"]) is not str or not _TOKEN.fullmatch(raw["task"]):
        raise block
    result = {"task": raw["task"]}
    addressee = raw.get("addressee")
    if "addressee" in raw and (type(addressee) is not dict or set(addressee) != {"sort", "constant"}
                               or any(type(v) is not str for v in addressee.values())):
        raise block
    definites = raw.get("definites", {})
    if type(definites) is not dict or any(type(c) is not str for c in definites.values()):
        raise block
    normalized = {}
    reserved = {"is", "are", "must", "may", "not", "you", "which", "one", "task"}
    for phrase, constant in definites.items():
        if type(phrase) is not str or len(phrase.encode()) > 80 or not _PHRASE.fullmatch(phrase):
            raise block
        key = " ".join(phrase.split())
        if (key in normalized or key[4:].lower() in reserved or
                key in constants or key[4:] in predicates):
            raise block
        normalized[key] = constant
    if addressee is not None:
        sort, constant = addressee["sort"], addressee["constant"]
        if sort not in sorts:
            raise VEError(f"UnknownSymbol: sort {sort}")
        if constant not in constants or constants[constant].sort != sort:
            raise VEError(f"UnknownSymbol: {constant}")
        result["addressee"] = dict(addressee)
    if len(definites) > 64:
        raise ResourceLimit("definites")
    for constant in normalized.values():
        if constant not in constants:
            raise VEError(f"UnknownSymbol: {constant}")
    if normalized:  # canonical as Lean's `encodeScope`: an empty map is absent
        result["definites"] = normalized
    return result


# The bare kind each tagged content belongs to (W2's kinds, and `binding`).
_CANDIDATE_KINDS = {"ast": "asserted", "norm": "norm", "command": "instruction", "question": "question",
                    "binding": "binding"}


def _wraps(kind, bare):
    """The kind is `bare` itself or a quoted kind (attributed or hedged) wrapping it (3.2), as Lean's `wraps`."""
    while type(kind) is list and len(kind) in (3, 4) and kind[0] in ("attributed", "hedged"):
        kind = kind[-1]
    return kind == bare


def content_kind_ok(kind, tag):
    """A tagged content under a kind that may carry it: `binding` exactly, else the tag's kind or a quoted one."""
    return kind == "binding" if tag == "binding" else tag in _CANDIDATE_KINDS and _wraps(kind, _CANDIDATE_KINDS[tag])


def _all(formulas):
    result = Top()
    for formula in formulas:
        result = And(result, formula)
    return result


def _any(formulas):
    from .ast import Bottom
    result = Bottom()
    for formula in formulas:
        result = Or(result, formula)
    return result


def latest_reading_sets(sets):
    """1.2 and 1.5 over W2's reading sets: per source unit, the latest version decides.

    An `open` latest version keeps the unit pending (dormant, no premise); an
    `authored` one is the author's signed singleton choice.  Earlier versions
    are history and change nothing, as W2's `active_reading_sets`.  Only a
    signed version is a choice: an authored version without the author's
    signature token, or an open one carrying one, is rejected as by W2's
    `validate_reading_sets`, never taken as the unit's meaning.
    """
    from .admission import token
    latest = {}
    for item in sets:
        if (type(item) is not dict or type(item.get("unit")) is not str
                or type(item.get("version")) is not int or item.get("status") not in ("open", "authored")):
            raise VEError("InvalidInput: reading sets on the speech-acts route need their unit, version and status")
        if item["version"] < 1:
            raise VEError("invalid or duplicate reading set version")
        if item["status"] == "authored" and (type(item.get("readings")) is not list or len(item["readings"]) != 1
                                             or type(item["readings"][0]) is not dict
                                             or not {"kind", "content"} <= set(item["readings"][0])
                                             or not token(item.get("signature"))):
            raise VEError("authored reading needs one signed choice")
        if item["status"] == "open" and "signature" in item:
            raise VEError("open reading set cannot have an author signature")
        unit = item["unit"]
        if unit in latest and latest[unit]["version"] == item["version"]:
            raise VEError("invalid or duplicate reading set version")
        if unit not in latest or item["version"] > latest[unit]["version"]:
            latest[unit] = item
    return latest


def _reading_choice(unit, reading_set):
    """The unit as its latest reading set leaves it: a signed choice supplies kind and content.

    The meaning is `specified`, except that a chosen reading question means its
    derived open term (3.2, 4.6), as Lean's `chosenUnit`.
    """
    if reading_set["status"] != "authored":
        return {k: v for k, v in unit.items() if k != "source"}
    choice = reading_set["readings"][0]
    content = choice["content"]
    if type(content) is list:  # W2's formula-only assertion candidate
        content = {"ast": content}
    result = {k: v for k, v in unit.items() if k not in ("content", "source")}
    question = content.get("question") if type(content) is dict else None
    meaning = ({"open": [f"intended-reading.{unit.get('id')}"]}
               if type(question) is dict and question.get("mode") == "reading" else "specified")
    result.update({"kind": choice["kind"], "meaning": meaning})
    if content is not None:
        result["content"] = content
    return result


def _binding_entry(env, uid, binding):
    """The legend entry one binding (a unit's or a candidate's) supplies, checked as the block's entry.

    Returns its key ("you", "task" or the phrase) and value.  The phrase
    passes the block's own checks (`validate_scope`) and the constant is
    declared, whether or not the entry is merged.
    """
    if (type(binding) is not dict or set(binding) not in ({"you"}, {"task"}, {"phrase", "constant"})
            or any(type(v) is not str for v in binding.values())
            or "phrase" in binding and (len(binding["phrase"].encode()) > 80
                                        or not _PHRASE.fullmatch(binding["phrase"]))):
        raise VEError(f"InvalidInput: invalid binding fields for {uid}")
    key = binding.get("phrase", next(iter(binding)))
    actual = binding.get("constant", binding.get(key))
    if key == "task":
        if not _TOKEN.fullmatch(actual):
            raise VEError("InvalidInput: speech_acts block")
    elif "phrase" in binding:
        validate_scope({"task": "t", "definites": {key: actual}}, env.sorts, env.constants, env.predicates)
    elif actual not in env.constants:
        raise VEError(f"UnknownSymbol: {actual}")
    return key, actual


def _merge_bindings(env, scope, bindings):
    """1.1 and 1.5: the scope with the bindings of units that are not pending merged in.

    `bindings` lists `(unit, binding, pending)` in document order.  A binding
    unit whose reading set is open supplies no entry and declares nothing (its
    candidates may bind otherwise); it keeps the single-unit checks, as a
    dormant command does.  The one merge of `SpeechDocument` and `effective_scope`.
    """
    scope = copy.deepcopy(scope)
    seen = set()
    for uid, binding, pending in bindings:
        key, actual = _binding_entry(env, uid, binding)
        if pending:
            continue
        if key in seen:
            raise VEError(f"DuplicateDeclaration: binding {key}")
        seen.add(key)
        expected = (scope["task"] if key == "task" else
                    scope.get("addressee", {}).get("constant") if key == "you" else
                    scope.get("definites", {}).get(key))
        if expected is not None and actual != expected:
            raise VEError(f"BindingConflict: {key}")
        if key == "task":
            scope["task"] = actual
        elif key == "you":
            scope["addressee"] = {"sort": env.constants[actual].sort, "constant": actual}
        else:
            scope.setdefault("definites", {})[key] = actual
    return scope


@dataclass(frozen=True, slots=True)
class Command:
    unit: str
    force: str
    act: str
    args: tuple[str, ...]
    guard: object
    active: bool = True


@dataclass(frozen=True, slots=True)
class Question:
    unit: str
    mode: str
    body: object | None = None
    sort: str | None = None
    domain: tuple[str, ...] = ()
    query: str | None = None
    reading_set: tuple[str, int] | None = None


@dataclass(frozen=True, slots=True)
class Query:
    id: str
    premises: tuple[str, ...]
    target: object


class SpeechDocument:
    """Validated typed projection of a speech document for experimental checks.

    Units use the W2 unit shape.  No question or command body is admitted as an
    assertion; the only generated premises are W1's active policy layers.
    """

    def __init__(self, env, units, queries=(), *, reading_sets=()):
        if "speech-acts@0" not in env.profiles or "norms@0" not in env.profiles:
            raise VEError("UnsupportedProfile: speech-acts@0 requires norms@0")
        for profile in env.profiles:
            if profile not in _ALLOWED:
                raise VEError(f"UnsupportedProfile: speech-acts@0 with {profile}")
        if any(p.defined is not None for p in env.predicates.values()):
            raise VEError("UnsupportedProfile: speech-acts@0 with definitions")
        if any(p.functional is not None or p.total is not None for p in env.predicates.values()):
            raise VEError("UnsupportedProfile: speech-acts@0 with functional")
        from .admission import _check_kind
        self.env = env
        self.scope = env.to_dict()["speech_acts"]
        self.units = tuple(units)
        self.query_records = tuple(queries)
        self.reading_sets = tuple(reading_sets)
        latest = latest_reading_sets(self.reading_sets)
        self.pending_units = frozenset(u for u, r in latest.items() if r["status"] == "open")
        # 4.1(4): what a reading question may name, an existing set id at one of its versions.
        self._set_versions = frozenset((r["id"], r["version"]) for r in self.reading_sets
                                       if type(r.get("id")) is str)
        # Units that ask about a query without being live questions or commands: quoted
        # questions and reading candidates, each a consumer at its unit (1.4).
        self._dormant_asks = []
        # Reading-question candidates, for the source wrapper's open-term check (4.6).
        self.candidate_questions = []
        self.queries = {}
        self.commands = []
        self.questions = []
        self.bindings = []
        self.asserted = []
        self.norms = []
        self.meaning_ids = {}
        self.warnings = []
        ids = set()
        self._effective = []
        for raw in self.units:
            if type(raw) is not dict or not {"id", "kind", "meaning", "support"} <= set(raw):
                raise VEError("InvalidInput: speech unit")
            uid = raw["id"]
            if type(uid) is not str or not _TOKEN.fullmatch(uid) or uid in ids:
                raise VEError("InvalidInput: speech unit id")
            ids.add(uid)
            if uid in latest:
                raw = _reading_choice(raw, latest[uid])
            self._effective.append(raw)
            pending = uid in self.pending_units
            content = raw.get("content")
            kind = raw["kind"]
            if kind != "binding":  # W2's kinds, as Lean's `decodeKind`
                _check_kind(kind)
            if type(raw["meaning"]) is dict and "unformalised" in raw["meaning"] and content is not None:
                raise VEError("unformalised unit cannot assert content")
            if type(content) is dict and "binding" in content:
                if kind != "binding":
                    raise VEError("InvalidInput: binding content requires binding kind")
                self.bindings.append((uid, content["binding"], pending))
            elif kind == "binding":  # as Lean's decoder: a binding unit carries its binding
                raise VEError(f"InvalidInput: invalid binding fields for {uid}")
            elif type(content) is dict and "command" in content:
                if not content_kind_ok(kind, "command"):
                    raise VEError("InvalidInput: command content requires instruction kind")
                self.commands.append(self._command(uid, content["command"], kind == "instruction"
                                                   and raw["meaning"] == "specified" and not pending))
            elif type(content) is dict and "question" in content:
                if not content_kind_ok(kind, "question"):
                    raise VEError("InvalidInput: question content requires question kind")
                if kind == "question":
                    self.questions.append(self._question(uid, content["question"], raw))
                else:
                    # A quoted question is asked by nobody: dormant, with every single-unit
                    # check of a reading candidate, and a consumer of the query it names.
                    question = self._question(uid, content["question"],
                                              {"meaning": {"open": [f"intended-reading.{uid}"]}})
                    if question.query is not None:
                        self._dormant_asks.append((uid, question.query))
            elif type(content) is dict and "norm" in content:
                if not content_kind_ok(kind, "norm"):
                    raise VEError("InvalidInput: norm content requires norm kind")
                # 1.5 and W2: an author norm unit is active unless its reading is pending.
                if kind == "norm" and not pending:
                    self.norms.append(NormDocument._decode(content))
                else:  # dormant norms keep every single-rule check, as Lean's decoder
                    from .norm_admission import _check_quoted
                    _check_quoted(env, content)
            elif content is not None:
                # A formula, W2's `{"ast": ...}` or the P0 route's bare AST, under any
                # kind as in Lean's decoder; W2's fixed asserted premises are the
                # `asserted` ones outside a pending reading set, or the author's
                # signed singleton choice (1.5).
                if type(content) is dict and set(content) == {"ast"}:
                    content = content["ast"]
                elif type(content) is not list:
                    raise VEError("InvalidInput: asserted content" if kind == "asserted"
                                  else "InvalidInput: misplaced speech content")
                formula = formula_from_data(env, content)
                if kind == "asserted" and not pending:
                    self.asserted.append((uid, formula))
            elif kind == "asserted" and not any(r["unit"] == uid for r in self.reading_sets):
                raise VEError("asserted unit needs content or a reading set")
        if any(item["unit"] not in ids for item in self.reading_sets):
            raise VEError("invalid reading set unit or status")
        self.scope = _merge_bindings(env, self.scope, self.bindings)
        # 1.1 and 3.5: a binding that supplies a scope entry supplies it to the
        # environment, so every identity (meaning ids, certificates) binds the
        # effective scope; without one the environment is unchanged.
        if self.scope != env.to_dict()["speech_acts"]:
            from .environment import Environment
            self.env = Environment({**env.to_dict(), "speech_acts": self.scope})
        for uid, binding, _ in self.bindings:
            self.meaning_ids[uid] = self._id({"binding": binding})
        self._check_candidates()
        if len(self.questions) > 256:
            raise ResourceLimit("questions")
        self._queries(queries)
        self._check_wordings()
        # 3.5: a proof task and a follows question bind their query's identity in
        # place of the bare query id, in the object shape Lean's `commandAst` and
        # `questionAst` digest.
        for command in self.commands:
            data = self.command_data(command)
            if (qid := self.query_of(command)) is not None:
                data["query"] = self.query_identity(qid)
            self.meaning_ids[command.unit] = self._id({"command": data})
        for question in self.questions:
            data = self.question_data(question)
            if question.query is not None:
                data["query"] = self.query_identity(question.query)
            self.meaning_ids[question.unit] = self._id({"question": data})
        self.policy = NormDocument(self.env, [*self.norms, *(self.demand(c) for c in self.commands if c.active)])
        for rule in self.norms:
            if any(edge.startswith("cmd-") for edge in rule.over):
                raise VEError(f"UnknownRule: rule {next(edge for edge in rule.over if edge.startswith('cmd-'))}")

    def _id(self, value):
        return digest(f"ve-meaning-{self.env.identity_version}\n",
                      {"environment_id": self.env.environment_id, "ast": value})

    def _check_candidates(self):
        """Every elaborated reading candidate decodes as content of its kind.

        Coverage class R claims each candidate is admitted as a command,
        question, norm, binding or assertion (6); a malformed candidate is
        rejected, never counted, and only a `null` candidate is unelaborated.
        Each is checked as the unit would be were it chosen: its kind agrees
        with its content, a binding passes the single-binding checks, and a
        candidate that asks about a query (a follows question, a proof task)
        is one of the query's consumers, regenerated at its unit (1.4).
        """
        from .admission import _check_kind
        from .norm_admission import _check_quoted
        for item in self.reading_sets:
            uid = item["unit"]
            readings = item.get("readings")
            if type(readings) is not list or not 1 <= len(readings) <= 64:
                raise VEError("reading sets hold 1 to 64 readings")
            for reading in readings:
                if type(reading) is not dict or not {"kind", "content"} <= set(reading):
                    raise VEError("invalid reading")
                content, kind = reading["content"], reading["kind"]
                if kind != "binding":
                    _check_kind(kind)
                if content is None:
                    continue
                if type(content) is list:
                    content = {"ast": content}
                if type(content) is not dict or len(content) != 1:
                    raise VEError("invalid speech reading content")
                tag, value = next(iter(content.items()))
                if not content_kind_ok(kind, tag):
                    raise VEError("invalid speech reading content")
                if tag == "ast":
                    formula_from_data(self.env, value)
                elif tag == "command":
                    if (qid := self.query_of(self._command(uid, value, False))) is not None:
                        self._dormant_asks.append((uid, qid))
                elif tag == "question":
                    # Chosen, a reading question means its derived open term (`_reading_choice`).
                    question = self._question(uid, value, {"meaning": {"open": [f"intended-reading.{uid}"]}})
                    if question.query is not None:
                        self._dormant_asks.append((uid, question.query))
                    if question.mode == "reading":
                        self.candidate_questions.append((item, question))
                elif tag == "norm":
                    _check_quoted(self.env, content)
                else:
                    _binding_entry(self.env, uid, value)

    def _command(self, uid, raw, active):
        if (type(raw) is not dict or not {"force", "act", "args"} <= set(raw)
                or set(raw) - {"force", "act", "args", "guard"}):
            raise VEError(f"InvalidInput: invalid command fields for {uid}")
        force, predicate, args = raw["force"], raw["act"], raw["args"]
        if force not in ("require", "forbid"):
            raise VEError("InvalidInput: force")
        # Every reference is a name (Lean's `decodeCommand`), then resolved and typed.
        if type(predicate) is not str or type(args) is not list or any(type(a) is not str for a in args):
            raise VEError(f"InvalidInput: invalid command fields for {uid}")
        if predicate not in self.env.predicates:
            raise VEError(f"UnknownSymbol: regulated predicate {predicate}")
        decl = self.env.predicates[predicate]
        reg = decl.regulated
        if reg is None or reg.role != ("obligation" if force == "require" else "permission"):
            act = reg.act if reg and reg.act else predicate
            raise VEError(f"Missing{'Obligation' if force == 'require' else 'Permission'}Role: {act}")
        for arg in args:
            if arg not in self.env.constants:
                raise VEError(f"UnknownSymbol: {arg}")
        if [self.env.constants[a].sort for a in args] != list(decl.arguments[1:]):
            raise VEError(f"TypeMismatch: command args for {uid}")
        guard = formula_from_data(self.env, raw.get("guard", ["top"]))
        return Command(uid, force, predicate, tuple(raw["args"]), guard, active)

    def _question(self, uid, raw, unit):
        if type(raw) is not dict or "mode" not in raw:
            raise VEError(f"InvalidInput: invalid question fields for {uid}")
        mode = raw["mode"]
        if mode == "polar" and set(raw) == {"mode", "body"}:
            return Question(uid, mode, formula_from_data(self.env, raw["body"]))
        if mode in ("which_all", "which_one") and set(raw) == {"mode", "sort", "domain", "body"}:
            sort, domain = raw["sort"], raw["domain"]
            # Names first, then resolved and typed, in Lean's `checkSpeech` order.
            if type(sort) is not str or type(domain) is not list or any(type(n) is not str for n in domain):
                raise VEError(f"InvalidInput: invalid question fields for {uid}")
            if sort not in self.env.sorts:
                raise VEError(f"UnknownSymbol: sort {sort}")
            if len(domain) > 16:
                raise ResourceLimit("alternatives")
            if len(domain) < 2:
                raise VEError(f"InvalidInput: invalid question fields for {uid}")
            for name in domain:
                if name not in self.env.constants:
                    raise VEError(f"UnknownAlternative: {uid}, {name}")
                if self.env.constants[name].sort != sort:
                    raise VEError(f"AlternativeSort: {uid}")
            if (twice := next((n for n in domain if domain.count(n) > 1), None)) is not None:
                raise VEError(f"DuplicateAlternative: {uid}, {twice}")
            body = _Decoder().decode(raw["body"])
            _Checker(self.env).formula(body, (sort,))
            return Question(uid, mode, body, sort, tuple(domain))
        if mode == "follows" and set(raw) == {"mode", "query"} and type(raw["query"]) is str:
            return Question(uid, mode, query=raw["query"])
        if mode == "reading" and set(raw) == {"mode", "set", "version"}:
            # 4.1(4): it names an existing set id at an existing version.
            if (type(raw["version"]) is not int or raw["version"] < 1 or type(raw["set"]) is not str
                    or (raw["set"], raw["version"]) not in self._set_versions):
                raise VEError(f"InvalidInput: invalid question fields for {uid}")
            if unit["meaning"] != {"open": [f"intended-reading.{uid}"]}:
                raise VEError(f"InvalidInput: invalid question fields for {uid}")
            if len(uid.encode()) > 47:
                raise ResourceLimit("open-term name")
            return Question(uid, mode, reading_set=(raw["set"], raw["version"]))
        raise VEError(f"InvalidInput: invalid question fields for {uid}")

    def _queries(self, records):
        asserted = dict(self.asserted)
        for raw in records:
            # The record's own references are names (Lean's `decodeQuery`); they are
            # resolved against the regeneration below.
            if (type(raw) is not dict or set(raw) != {"id", "premises", "target"} or type(raw["id"]) is not str
                    or type(raw["premises"]) is not list or any(type(p) is not str for p in raw["premises"])
                    or type(raw["target"]) is not dict or set(raw["target"]) != {"ast"}):
                raise VEError("InvalidInput: query")
            target = formula_from_data(self.env, raw["target"]["ast"])
            qid = raw["id"]
            if qid in self.queries:
                raise VEError("InvalidInput: duplicate query")
            self.queries[qid] = Query(qid, tuple(raw["premises"]), target)
        # 1.4: the record is regenerated at every unit that asks, in document
        # order, as Lean's decoder does; a later consumer with more earlier
        # assertions makes a reused record stale.
        # A reading candidate that asks is a consumer at its unit, as it would be if chosen.
        asks = {}
        for uid, qid in [*((q.unit, q.query) for q in self.questions if q.query is not None),
                         *((c.unit, qid) for c in self.commands if (qid := self.query_of(c)) is not None),
                         *self._dormant_asks]:
            asks.setdefault(uid, []).append(qid)
        consumers = {}
        before = []
        for raw in self.units:
            uid = raw["id"]
            for qid in asks.get(uid, ()):
                if qid not in self.queries or list(self.queries[qid].premises) != before:
                    raise VEError(f"QueryMismatch: {uid}")
                consumers.setdefault(qid, uid)
            if uid in asserted:
                before.append(uid)
        for qid, query in self.queries.items():
            if qid not in consumers:
                raise VEError(f"QueryMismatch: {qid}")
            if query.target in (asserted[u] for u in query.premises):
                self.warnings.append(f"TrivialQuery: {consumers[qid]}")

    def query_of(self, command):
        """The constant in the act's first slot of sort `query` (Lean's `queryOf`)."""
        sorts = self.env.predicates[command.act].arguments[1:]
        return next((arg for arg, sort in zip(command.args, sorts) if sort == "query"), None)

    def query_identity(self, qid):
        """A query as bound into a meaning: its id, premise meaning ids and target meaning id."""
        query = self.queries[qid]
        asserted = dict(self.asserted)
        return {"id": qid, "premises": [self._id(_to_data(asserted[u])) for u in query.premises],
                "target": self._id(_to_data(query.target))}

    def _check_wordings(self):
        """Every wording reads as its unit's content (2.1); the gloss lint is only a warning per unit."""
        from .speech_english import parse_speech, _sentence
        by_id = {u["id"]: u for u in self._effective}
        for command in self.commands:
            source = by_id[command.unit].get("source")
            query = self.query_of(command)
            lint = []
            if source is not None and parse_speech(self.env, source, self.scope, query=query,
                                                   warnings=lint)[0] != self.command_data(command):
                raise VEError(f"InvalidInput: invalid command fields for {command.unit}")
            if source is not None and query is not None and source.startswith("Prove that "):
                wording = source[len("Prove that "):-len(" using these premises.")] + "."
                if _sentence(self.env, wording) != self.queries[query].target:
                    raise VEError(f"QueryMismatch: {command.unit}")
            self.warnings.extend(f"{w} in {command.unit}" for w in dict.fromkeys(lint))
        for question in self.questions:
            source = by_id[question.unit].get("source")
            lint = []
            if source is not None and parse_speech(self.env, source, self.scope, query=question.query,
                                                   reading_set=question.reading_set,
                                                   warnings=lint)[0] != self.question_data(question):
                raise VEError(f"ModeMismatch: {question.unit}")
            if source is not None and question.query is not None:
                wording = source[len("Does it follow from these premises that "):-1] + "."
                if _sentence(self.env, wording) != self.queries[question.query].target:
                    raise VEError(f"QueryMismatch: {question.unit}")
            self.warnings.extend(f"{w} in {question.unit}" for w in dict.fromkeys(lint))

    def command_data(self, c):
        return {"force": c.force, "act": c.act, "args": list(c.args), "guard": _to_data(c.guard)}

    def question_data(self, q):
        return ({"mode": "polar", "body": _to_data(q.body)} if q.mode == "polar" else
                {"mode": q.mode, "sort": q.sort, "domain": list(q.domain), "body": _to_data(q.body)}
                if q.mode in ("which_all", "which_one") else
                {"mode": "follows", "query": q.query} if q.mode == "follows" else
                {"mode": "reading", "set": q.reading_set[0], "version": q.reading_set[1]})

    def demand(self, command):
        if "addressee" not in self.scope:
            raise VEError("UnboundSlot: you")
        decl = self.env.predicates[command.act]
        you = self.scope["addressee"]
        if you["sort"] != decl.arguments[0]:
            raise VEError("TypeMismatch: addressee")
        constants = [you["constant"], *command.args]
        equalities = [Eq(Var(len(constants) - 1 - i), Const(a)) for i, a in enumerate(constants)]
        eq = equalities[-1]
        for equality in reversed(equalities[:-1]):
            eq = And(equality, eq)
        return Norm(f"cmd-{command.unit}", command.act, command.force == "require",
                    And(eq, command.guard))

    def premises(self):
        from .background import background
        return (tuple(p.formula for p in background(self.env)) +
                tuple(f for _, f in self.policy.premises()) +
                tuple(f for _, f in self.asserted))

    def query_premises(self, qid):
        from .background import background
        query = self.queries[qid]
        asserted = dict(self.asserted)
        return (tuple(p.formula for p in background(self.env)) +
                tuple(f for _, f in self.policy.premises()) +
                tuple(asserted[u] for u in query.premises))

    def _caller_premises(self, qid=None):
        """The checker inserts Background itself; supply only the layer and claims."""
        asserted = dict(self.asserted)
        chosen = self.queries[qid].premises if qid is not None else tuple(asserted)
        return (tuple(f for _, f in self.policy.premises()) +
                tuple(asserted[u] for u in chosen))

    def check_answer_certificate(self, question, token, certificate, *, conditional=False,
                                 max_steps=10_000):
        """Replay the exact answer target; never infer a negative from proof failure."""
        from .entailment import check_entailment_certificate
        if question.mode not in ("polar", "which_one", "which_all"):
            raise VEError("InvalidInput: question has no formula answer")
        h = self.presupposition(question)
        f = self.correct(question, token)
        premises = self._caller_premises()
        target = f if conditional else And(h, f)
        if conditional:
            premises += (h,)
        replay = check_entailment_certificate(self.env, premises, target, certificate,
                                              max_steps=max_steps)
        if not replay.valid:
            raise VEError(f"AnswerMismatch: {question.unit}")
        return {"status": "supported given presupposition" if conditional else "supported",
                "answer": token, "evidence": "certificate",
                "assumptions": [f"speech:presupposition:{question.unit}"] if conditional else [],
                **self._premise_status(premises, max_steps)}

    def check_presupposition_failure_certificate(self, question, certificate, *, max_steps=10_000):
        """Replay a certificate for ¬H(q) over premises(D): no token is a correct answer (5.3)."""
        from .entailment import check_entailment_certificate
        if question.mode not in ("polar", "which_one", "which_all"):
            raise VEError("InvalidInput: question has no formula answer")
        premises = self._caller_premises()
        replay = check_entailment_certificate(self.env, premises, Not(self.presupposition(question)), certificate,
                                              max_steps=max_steps)
        if not replay.valid:
            raise VEError(f"AnswerMismatch: {question.unit}")
        return {"status": "PRESUPPOSITION-FAILED", "evidence": "certificate",
                **self._premise_status(premises, max_steps)}

    def check_consequence_certificate(self, qid, certificate, *, max_steps=10_000):
        """Replay a consequence or proof-task submission against its pinned query."""
        from .entailment import check_entailment_certificate
        if qid not in self.queries:
            raise VEError(f"QueryMismatch: {qid}")
        replay = check_entailment_certificate(self.env, self._caller_premises(qid),
                                              self.queries[qid].target, certificate,
                                              max_steps=max_steps)
        if not replay.valid:
            raise VEError(f"QueryMismatch: {qid}")
        return {"status": "follows", "evidence": "certificate", "query": qid,
                **self._premise_status(self._caller_premises(qid), max_steps)}

    def _premise_status(self, premises, max_steps):
        """5.3: P0's three-way status of the exact list a certificate was checked over.

        Opposite answers are both certified only over inconsistent premises, so
        every certificate line says which: a checked model (not vacuous), a
        replayed inconsistency certificate (vacuous), or UNKNOWN in the budget.
        """
        from .vacuity import premise_status
        status = premise_status(self.env, list(premises), max_proof_steps=max_steps)
        return {"premises": status,
                "vacuous": {"INCONSISTENT": "yes", "model": "no"}.get(status["status"], "unknown")}

    def complete_model(self, base_wire, *, max_evaluations=1_000_000):
        """Regenerate regulated tables from a supplied base structure.

        The caller supplies only base predicate tables.  A table for a
        regulated predicate is rejected by FiniteModel's exact field check.
        """
        from .evaluate import _Evaluator, _Exhausted
        from .model import FiniteModel
        base_env = self.policy.base_environment()
        base = FiniteModel.from_dict(base_env, base_wire) if type(base_wire) is dict else base_wire
        if base.environment_id != base_env.environment_id:
            raise VEError("InvalidModel: base environment mismatch")
        wire = base.to_dict()
        evaluator = _Evaluator(base_env, base, max_evaluations, trace=False)
        try:
            for predicate in self.policy.order:
                decl = self.env.predicates[predicate]
                formula = self.policy.outcome(predicate, base=True)
                table = []
                for row in product(*(base.domains[s] for s in decl.arguments)):
                    bindings = tuple(reversed(tuple(zip(decl.arguments, row))))
                    if evaluator.formula(formula, bindings)[0]:
                        table.append(list(row))
                wire["relations"][predicate] = table
        except _Exhausted as exc:
            raise ResourceLimit("model evaluation budget") from exc
        return FiniteModel.from_dict(self.env, wire)

    def evaluate_answer_model(self, question, token, base_wire, *, max_evaluations=1_000_000):
        """Evaluate H and F in one checked premise model, with model-only scope."""
        from .evaluate import _Evaluator, _Exhausted
        model = self.complete_model(base_wire, max_evaluations=max_evaluations)
        evaluator = _Evaluator(self.env, model, max_evaluations, trace=False)
        try:
            if any(not evaluator.formula(formula)[0] for formula in self.premises()):
                raise VEError("InvalidModel: model does not satisfy pinned premises")
            if not evaluator.formula(self.presupposition(question))[0]:
                return {"status": "PRESUPPOSITION-FAILED", "evidence": "model",
                        "model_id": model.model_id, "scope": "this model only"}
            if not evaluator.formula(self.correct(question, token))[0]:
                raise VEError(f"AnswerMismatch: {question.unit}")
        except _Exhausted as exc:
            raise ResourceLimit("model evaluation budget") from exc
        return {"status": "evaluated", "answer": token, "evidence": "model",
                "model_id": model.model_id, "scope": "this model only"}

    def presupposition(self, question):
        if question.mode != "which_one":
            return Top()
        claims = [self._instance(question, name) for name in question.domain]
        pairs = (Not(And(claims[i], claims[j])) for i in range(len(claims))
                 for j in range(i + 1, len(claims)))
        return And(_any(claims), _all(pairs))

    def _instance(self, question, name):
        return _instantiate(question.body, (Const(name),))

    def correct(self, question, token):
        if question.mode == "polar":
            if token not in ("yes", "no"):
                raise VEError(f"AnswerOutsideDomain: {question.unit}, {token}")
            return question.body if token == "yes" else Not(question.body)
        if question.mode == "which_one":
            if token not in question.domain:
                raise VEError(f"AnswerOutsideDomain: {question.unit}, {token}")
            return self._instance(question, token)
        if question.mode == "which_all":
            if type(token) is not tuple or len(set(token)) != len(token) or any(x not in question.domain for x in token):
                raise VEError(f"AnswerOutsideDomain: {question.unit}, {token}")
            if tuple(x for x in question.domain if x in token) != token:
                raise VEError(f"AnswerOutsideDomain: {question.unit}, {token}")
            # 1.3's two conjunctions, as Lean's `allAnswer`, so a certificate's
            # conclusion identity is the same in every checker.
            return And(_all(self._instance(question, a) for a in token),
                       _all(Not(self._instance(question, a)) for a in question.domain if a not in token))
        raise VEError(f"InvalidInput: mode {question.mode} has no answer formula")


def effective_scope(env, units, reading_sets=()):
    """The scope a document's bindings leave (1.1), for wordings read before the document is built.

    Exactly `SpeechDocument.scope`: the same merge (`_merge_bindings`) over the
    bindings of the effective units (each unit, or its latest signed choice),
    pending bindings supplying nothing.  No partial document is built, so
    nothing else (a query record, a candidate that asks about one) is checked
    out of its context here; the document built afterwards checks everything.
    """
    latest = latest_reading_sets(reading_sets)
    bindings = []
    for raw in units:
        if type(raw) is not dict or type(raw.get("id")) is not str:
            continue
        if raw["id"] in latest:
            raw = _reading_choice(raw, latest[raw["id"]])
        content = raw.get("content")
        if raw.get("kind") == "binding" and type(content) is dict and "binding" in content:
            bindings.append((raw["id"], content["binding"], latest.get(raw["id"], {}).get("status") == "open"))
    return _merge_bindings(env, env.to_dict()["speech_acts"], bindings)


def combine(first: SpeechDocument, second: SpeechDocument):
    if first.scope != second.scope or first.env.environment_id != second.env.environment_id:
        raise VEError(f"ScopeMismatch: {first.scope['task']}, {second.scope['task']}")
    ids = {u["id"] for u in first.units}
    if ids & {u["id"] for u in second.units}:
        raise VEError("DuplicateDeclaration: speech unit")
    # Everything that decides activeness and premises travels with the units:
    # a command pending in either document stays dormant in the combination.
    return SpeechDocument(first.env, (*first.units, *second.units),
                          (*first.query_records, *second.query_records),
                          reading_sets=(*first.reading_sets, *second.reading_sets))
