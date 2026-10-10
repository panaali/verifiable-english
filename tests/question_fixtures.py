"""The Q1 acceptance fixtures of docs/spec/question-answering.md section 7, as one table.

Each row is (fixture, frame, question, answer): the fixture's id in the spec (`G22c` is G22's control question, `A6r`,
`A6c` and `A6d` are A6 on the other three A documents, since Q1 depends only on the vocabulary), the vocabulary it is
read in (a document of `usecases/question-answering`, or a base-8 environment of the English reader's spec), the
question, and `english.question`'s result without its identities, a witness list written as its length.

The table is checked three ways (tests/test_question_reading.py): against the spec's own rows; against Lean, by the
`#guard`s that `tools/question_fixtures.py` generates from it into `lean/VE/Question/Fixtures.lean`, which `lake
build` evaluates; and against the running `ve_service`, through the relay and through `ve ask`. G21 (work budget 0)
and G24 (speech acts' auxiliaries) are not reachable through the mode and are `#guard`s of
`lean/VE/Question/Examples.lean` only.
"""
from __future__ import annotations

import copy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = {"G": "usecases/question-answering/group.ve.md",
             "U": "usecases/question-answering/udhr-part07.ve.md",
             "A": "usecases/question-answering/agent-policy/a-unspecified.ve.md",
             "Ar": "usecases/question-answering/agent-policy/a-rules.ve.md",
             "Ac": "usecases/question-answering/agent-policy/a-conflict.ve.md",
             "Ad": "usecases/question-answering/agent-policy/a-deny.ve.md"}

# Base 8.1's F (lean/VE/EnglishGrammar/ReadExamples.lean `envJson false sortsF predsF constsF`) and FD.
SORTS_F = [("person", None), ("service", None)]
PREDS_F = [("deployed", ["service"], "{0} is deployed", None),
           ("reviewed", ["service"], "{0} is reviewed", "{0} is not reviewed"),
           ("owns", ["person", "service"], "{0} owns {1}", "{0} does not own {1}")]
CONSTS_F = [("alice", "person"), ("legacy", "service")]
# Base 8.3's LFv3: `owns` on its fallback wording with the declared negative, which fails V5 and V6.
LFV3 = {"wordings": [["deployed", "{0} is deployed"], ["owns", "{0} has the recorded relation \"owns\" to {1}"],
                     ["reviewed", "{0} is reviewed"]],
        "negatives": [["owns", "{0} does not own {1}"], ["reviewed", "{0} is not reviewed"]]}


def env_json(sorts, preds, consts) -> dict:
    vocabulary = {
        "sorts": {s: {"description": "A sort.", **({"verbalisation": {"singular": n, "plural": n + "s"}} if n else {})}
                  for s, n in sorts},
        "predicates": {p: {"arguments": args, "description": "A predicate.", "verbalisation": w,
                           **({"negative_verbalisation": neg} if neg else {})} for p, args, w, neg in preds},
        "constants": {c: {"sort": s, "description": "A constant."} for c, s in consts}}
    return {"language": "ve.core@0", "profile": "relational-fol@0", "spec_revision": "ve-v0-draft-2026-09-20",
            "vocabulary": vocabulary}


def environment(frame: str):
    """The environment a frame's questions are read in: a document's, as `ve ask` builds it, or a base-8 one."""
    from ve import Environment, ask
    if frame in DOCUMENTS:
        return ask.environment((ROOT / DOCUMENTS[frame]).read_bytes())
    if frame == "FD":
        return Environment(env_json(SORTS_F + [("dservice", "deployed service")], PREDS_F, CONSTS_F))
    if frame == "F-LFv3":
        return Environment(env_json(SORTS_F, PREDS_F, CONSTS_F))
    raise KeyError(frame)


def request(frame: str, question: str) -> dict:
    """The `english.question` case of a fixture: the relay's request; F-LFv3 with base 8.3's lexicon."""
    from ve.backends import english_lean
    from ve.english import EnglishVocabulary
    env = environment(frame)
    case = english_lean.request(env, question, EnglishVocabulary(env, _defer_overlay_refusals=True), {})
    case.update(id="english.question", question=question)
    if frame == "F-LFv3":
        case["lexicon"] = {**copy.deepcopy(case["lexicon"]), **copy.deepcopy(LFV3)}
    return case


def answer_of(result: dict) -> dict:
    """A result as the table writes it: without identities, the witnesses as their number."""
    return {k: (len(v) if k == "witnesses" else v) for k, v in result.items() if k != "identities"}


# G20: 71 candidates, 646 bytes.
LONG = "Is every member" + " eligible" * 70 + "?"

FIXTURES = [
    ('G1', 'G', 'Is every member eligible?',
     {"ast": ["forall", "member", ["unary", "eligible", ["var", 0]]], "form": "fronted", "sentence": "every member is eligible.", "spans": [[0, 25]], "status": "one", "text": "You asked whether every member is eligible."}),
    ('G2', 'G', 'Is it the case that every member is eligible?',
     {"ast": ["forall", "member", ["unary", "eligible", ["var", 0]]], "form": "caseThat", "sentence": "every member is eligible.", "spans": [[0, 45]], "status": "one", "text": "You asked whether every member is eligible."}),
    ('G3', 'G', 'Is every member verified?',
     {"ast": ["forall", "member", ["unary", "verified", ["var", 0]]], "form": "fronted", "sentence": "every member is verified.", "spans": [[0, 25]], "status": "one", "text": "You asked whether every member is verified."}),
    ('G4', 'G', 'Is it the case that no member is eligible?',
     {"ast": ["not", ["exists", "member", ["unary", "eligible", ["var", 0]]]], "form": "caseThat", "sentence": "no member is eligible.", "spans": [[0, 42]], "status": "one", "text": "You asked whether no member is eligible."}),
    ('G5', 'G', 'Is a member eligible?',
     {"class": "SyntaxError", "code": "IndefiniteQuestion", "rephrasings": ["Is every member eligible?", "Is some member eligible?"], "span": [0, 21], "status": "indefinite", "text": "VE cannot tell whether \"a\" here means every or some. Ask one of these instead:"}),
    ('G6', 'G', 'Is every member eligible',
     {"class": "SyntaxError", "code": "NotOneQuestion", "span": [0, 24], "status": "notQuestion", "text": "Write one question that ends with a question mark."}),
    ('G7', 'G', 'Does every member vote?',
     {"class": "SyntaxError", "code": "QuestionForm", "span": [0, 23], "status": "none", "text": "VE answers questions that begin with \"Is\", \"Must\" or \"May\", or with \"Is it the case that\" followed by a sentence."}),
    ('G8', 'G', 'Who is eligible?',
     {"class": "SyntaxError", "code": "QuestionForm", "span": [0, 16], "status": "none", "text": "VE answers yes-or-no questions. It does not answer who, what or which questions yet."}),
    ('G9', 'G', 'Must Ann be eligible?',
     {"class": "SyntaxError", "code": "NoDerivation", "span": [0, 20], "status": "none", "text": "The question has no reading with the current vocabulary. Closest sentence tried: \"Ann must be eligible.\". Unknown English phrase 'must be eligible'. Nearest declared wordings: 'is eligible'; 'member'; 'is verified'."}),
    ('G10', 'G', 'Is Ann eligible?',
     {"ast": ["unary", "eligible", ["const", "ann"]], "form": "fronted", "sentence": "Ann is eligible.", "spans": [[0, 16]], "status": "one", "text": "You asked whether Ann is eligible."}),
    ('G11', 'G', 'Is every member who registered is eligible?',
     {"class": "SyntaxError", "code": "QuestionWordMoved", "rephrasings": ["Is every member who is registered eligible?"], "span": [0, 43], "status": "moved", "text": "VE could read this question only by putting \"is\" back inside a smaller part of the sentence, such as a part that begins with \"who\", \"that\", \"which\", \"if\", \"both\" or \"either\". English moves a word to the front only from the main sentence. Ask this instead:"}),
    ('G11c', 'G', 'Is every member who is registered eligible?',
     {"ast": ["forall", "member", ["implies", ["unary", "registered", ["var", 0]], ["unary", "eligible", ["var", 0]]]], "form": "fronted", "sentence": "every member who is registered is eligible.", "spans": [[0, 43]], "status": "one", "text": "You asked whether every member who is registered is eligible."}),
    ('G12', 'G', 'Is every member eligible and?',
     {"class": "SyntaxError", "code": "NoDerivation", "span": [24, 28], "status": "none", "text": "The question has no reading with the current vocabulary. Closest sentence tried: \"every member is eligible and.\". Expected '.' here. Use the English paraphrase as a writing example."}),
    ('G13', 'G', 'Is it the case that therefore Ann is eligible?',
     {"class": "SyntaxError", "code": "QuestionWithMarker", "span": [0, 46], "status": "rejected", "text": "A question cannot contain \"therefore\", \"so\", \"hence\" or \"it follows that\"."}),
    ('G14', 'G', 'Is it eligible?',
     {"class": "SyntaxError", "code": "PronounUnresolved", "span": [0, 15], "status": "rejected", "text": "The question uses \"it\", and it is not settled what \"it\" refers to. Repeat the name."}),
    ('G15', 'G', 'Is every member eligible ?',
     {"class": "SyntaxError", "code": "BadSpacing", "span": [25, 26], "status": "rejected", "text": "The spacing at position 25 is not allowed: write no space before the question mark."}),
    ('G16', 'G', 'Is every member eligible? Is Ann eligible?',
     {"class": "SyntaxError", "code": "NotOneQuestion", "span": [0, 42], "status": "notQuestion", "text": "Write one question that ends with a question mark."}),
    ('G17', 'G', 'Is it the case that every member is happy?',
     {"class": "SyntaxError", "code": "NoDerivation", "span": [32, 41], "status": "none", "text": "The question has no reading with the current vocabulary. Closest sentence tried: \"every member is happy.\". Unknown English phrase 'is happy'. Nearest declared wordings: 'ann'; 'bo'; 'member'."}),
    ('G18', 'G', 'Is Ann eligible. Bo eligible?',
     {"class": "SyntaxError", "code": "NotOneQuestion", "span": [0, 29], "status": "notQuestion", "text": "Write one question that ends with a question mark."}),
    ('G19', 'G', 'Is every member eligible!?',
     {"class": "SyntaxError", "code": "BadCharacter", "span": [24, 25], "status": "rejected", "text": "The character at position 24 cannot appear outside a quoted name."}),
    ('G20', 'G', LONG,
     {"class": "ResourceLimit", "code": "QuestionTooLong", "span": [0, 646], "status": "budget", "text": "The question is longer than VE reads. Ask a shorter question."}),
    ('G22', 'FD', 'Is every deployed service reviewed?',
     {"class": "AmbiguousDerivation", "code": "Ambiguous", "span": [0, 35], "status": "many", "text": "The sentence \"every deployed service is reviewed.\" can be read in more than one way. Two of the ways are shown.", "witnesses": 2}),
    ('G22c', 'FD', 'Is every service reviewed?',
     {"ast": ["forall", "service", ["unary", "reviewed", ["var", 0]]], "form": "fronted", "sentence": "every service is reviewed.", "spans": [[0, 26]], "status": "one", "text": "You asked whether every service is reviewed."}),
    ('G23', 'F-LFv3', 'Is legacy deployed?',
     {"class": "CheckerUnavailable", "code": "InvalidGrammar", "failure": ["V6", "negative", "owns"], "fault": "lexicon", "status": "invalidGrammar", "text": "The vocabulary selection was not accepted (invalidGrammar lexicon: V6 negative owns). No text was read."}),
    ('G25', 'G', 'Is every and?',
     {"class": "SyntaxError", "code": "NoDerivation", "span": [0, 9], "status": "none", "text": "The question has no reading with the current vocabulary. Closest sentence tried: \"every is and.\". Unknown English phrase 'is'. Nearest declared wordings: 'bo'; 'ann'; 'member'."}),
    ('G26', 'G', 'Is "é" and?',
     {"class": "SyntaxError", "code": "NoDerivation", "span": [3, 6], "status": "none", "text": "The question has no reading with the current vocabulary. Closest sentence tried: \"\"é\" is and.\". Unknown English phrase '\"é\"'. Nearest declared wordings: 'bo'; 'ann'; 'member'."}),
    ('G27', 'G', 'Is a member who registered is eligible?',
     {"advice": {"id": "question-indefinite", "text": "Write \"every\" or \"some\" in place of \"a\"."}, "class": "SyntaxError", "code": "NoDerivation", "span": [3, 4], "status": "none", "text": "The question has no reading with the current vocabulary. Closest sentence tried: \"a is member who registered is eligible.\". Unknown English phrase 'a'. Nearest declared wordings: 'bo'; 'ann'; 'member'."}),
    ('G28', 'G', 'Is every member that registered is eligible?',
     {"class": "SyntaxError", "code": "QuestionWordMoved", "rephrasings": ["Is every member that is registered eligible?"], "span": [0, 44], "status": "moved", "text": "VE could read this question only by putting \"is\" back inside a smaller part of the sentence, such as a part that begins with \"who\", \"that\", \"which\", \"if\", \"both\" or \"either\". English moves a word to the front only from the main sentence. Ask this instead:"}),
    ('G29', 'G', 'Is there a member who is eligible?',
     {"ast": ["exists", "member", ["unary", "eligible", ["var", 0]]], "form": "fronted", "sentence": "there is a member who is eligible.", "spans": [[0, 34]], "status": "one", "text": "You asked whether there is a member who is eligible."}),
    ('G30', 'G', 'Is if ann verified, then bo is eligible?',
     {"class": "SyntaxError", "code": "QuestionWordMoved", "rephrasings": ["Is it the case that if ann is verified, then bo is eligible?"], "span": [0, 40], "status": "moved", "text": "VE could read this question only by putting \"is\" back inside a smaller part of the sentence, such as a part that begins with \"who\", \"that\", \"which\", \"if\", \"both\" or \"either\". English moves a word to the front only from the main sentence. Ask this instead:"}),
    ('G30c', 'G', 'Is it the case that if ann is verified, then bo is eligible?',
     {"ast": ["implies", ["unary", "verified", ["const", "ann"]], ["unary", "eligible", ["const", "bo"]]], "form": "caseThat", "sentence": "if ann is verified, then bo is eligible.", "spans": [[0, 60]], "status": "one", "text": "You asked whether if ann is verified, then bo is eligible."}),
    ('G31', 'G', 'Is if every member verified, then every member is eligible?',
     {"class": "SyntaxError", "code": "QuestionWordMoved", "rephrasings": ["Is it the case that if every member is verified, then every member is eligible?"], "span": [0, 59], "status": "moved", "text": "VE could read this question only by putting \"is\" back inside a smaller part of the sentence, such as a part that begins with \"who\", \"that\", \"which\", \"if\", \"both\" or \"either\". English moves a word to the front only from the main sentence. Ask this instead:"}),
    ('G32', 'G', 'Is both ann eligible and bo is verified?',
     {"class": "SyntaxError", "code": "QuestionWordMoved", "rephrasings": ["Is it the case that both ann is eligible and bo is verified?"], "span": [0, 40], "status": "moved", "text": "VE could read this question only by putting \"is\" back inside a smaller part of the sentence, such as a part that begins with \"who\", \"that\", \"which\", \"if\", \"both\" or \"either\". English moves a word to the front only from the main sentence. Ask this instead:"}),
    ('G33', 'G', 'Is either ann eligible or bo is verified, or both?',
     {"class": "SyntaxError", "code": "QuestionWordMoved", "rephrasings": ["Is it the case that either ann is eligible or bo is verified, or both?"], "span": [0, 50], "status": "moved", "text": "VE could read this question only by putting \"is\" back inside a smaller part of the sentence, such as a part that begins with \"who\", \"that\", \"which\", \"if\", \"both\" or \"either\". English moves a word to the front only from the main sentence. Ask this instead:"}),
    ('G34', 'G', 'Is for every member, ann eligible?',
     {"class": "SyntaxError", "code": "QuestionWordMoved", "rephrasings": ["Is it the case that for every member, ann is eligible?"], "span": [0, 34], "status": "moved", "text": "VE could read this question only by putting \"is\" back inside a smaller part of the sentence, such as a part that begins with \"who\", \"that\", \"which\", \"if\", \"both\" or \"either\". English moves a word to the front only from the main sentence. Ask this instead:"}),
    ('A1', 'A', 'May "a27" be performed?',
     {"ast": ["unary", "permitted", ["const", "a27"]], "form": "fronted", "sentence": "\"a27\" may be performed.", "spans": [[0, 23]], "status": "one", "text": "You asked whether \"a27\" may be performed."}),
    ('A1d', 'Ad', 'May "a27" be performed?',
     {"ast": ["unary", "permitted", ["const", "a27"]], "form": "fronted", "sentence": "\"a27\" may be performed.", "spans": [[0, 23]], "status": "one", "text": "You asked whether \"a27\" may be performed."}),
    ('A2', 'A', 'May "a25" be performed?',
     {"ast": ["unary", "permitted", ["const", "a25"]], "form": "fronted", "sentence": "\"a25\" may be performed.", "spans": [[0, 23]], "status": "one", "text": "You asked whether \"a25\" may be performed."}),
    ('A3', 'A', 'May "a26" be performed?',
     {"ast": ["unary", "permitted", ["const", "a26"]], "form": "fronted", "sentence": "\"a26\" may be performed.", "spans": [[0, 23]], "status": "one", "text": "You asked whether \"a26\" may be performed."}),
    ('A4', 'A', 'Must "a13" be reported to the user?',
     {"ast": ["unary", "report_required", ["const", "a13"]], "form": "fronted", "sentence": "\"a13\" must be reported to the user.", "spans": [[0, 35]], "status": "one", "text": "You asked whether \"a13\" must be reported to the user."}),
    ('A5', 'Ac', 'May "a10" be performed?',
     {"ast": ["unary", "permitted", ["const", "a10"]], "form": "fronted", "sentence": "\"a10\" may be performed.", "spans": [[0, 23]], "status": "one", "text": "You asked whether \"a10\" may be performed."}),
    ('A6', 'A', 'May an action be performed?',
     {"class": "SyntaxError", "code": "IndefiniteQuestion", "rephrasings": ["May every action be performed?", "May some action be performed?"], "span": [0, 27], "status": "indefinite", "text": "VE cannot tell whether \"an\" here means every or some. Ask one of these instead:"}),
    ('A6r', 'Ar', 'May an action be performed?',
     {"class": "SyntaxError", "code": "IndefiniteQuestion", "rephrasings": ["May every action be performed?", "May some action be performed?"], "span": [0, 27], "status": "indefinite", "text": "VE cannot tell whether \"an\" here means every or some. Ask one of these instead:"}),
    ('A6c', 'Ac', 'May an action be performed?',
     {"class": "SyntaxError", "code": "IndefiniteQuestion", "rephrasings": ["May every action be performed?", "May some action be performed?"], "span": [0, 27], "status": "indefinite", "text": "VE cannot tell whether \"an\" here means every or some. Ask one of these instead:"}),
    ('A6d', 'Ad', 'May an action be performed?',
     {"class": "SyntaxError", "code": "IndefiniteQuestion", "rephrasings": ["May every action be performed?", "May some action be performed?"], "span": [0, 27], "status": "indefinite", "text": "VE cannot tell whether \"an\" here means every or some. Ask one of these instead:"}),
    ('A7', 'Ar', 'May every action be performed?',
     {"ast": ["forall", "action", ["unary", "permitted", ["var", 0]]], "form": "fronted", "sentence": "every action may be performed.", "spans": [[0, 30]], "status": "one", "text": "You asked whether every action may be performed."}),
    ('A8', 'A', 'Must every action be reported to the user?',
     {"ast": ["forall", "action", ["unary", "report_required", ["var", 0]]], "form": "fronted", "sentence": "every action must be reported to the user.", "spans": [[0, 42]], "status": "one", "text": "You asked whether every action must be reported to the user."}),
    ('A9', 'A', 'Must an agent not send email unless the user confirms?',
     {"advice": {"id": "question-indefinite", "text": "Write \"every\" or \"some\" in place of \"an\"."}, "class": "SyntaxError", "code": "NoDerivation", "span": [0, 13], "status": "none", "text": "The question has no reading with the current vocabulary. Closest sentence tried: \"an must agent not send email unless the user confirms.\". Unknown English phrase 'an must agent'. Nearest declared wordings: '\"spawn_agent\"'; 'messages {1}'; '\"f_env\"'."}),
    ('U1', 'U', 'Must every qualified person be given access to higher education?',
     {"class": "SyntaxError", "code": "NoDerivation", "span": [0, 63], "status": "none", "text": "The question has no reading with the current vocabulary. Closest sentence tried: \"every must qualified person be given access to higher education.\". Unknown English phrase 'must qualified person be given access to higher education'. Nearest declared wordings: 'must be spared exclusion from education'; 'must receive elementary education'; 'is classified as \"has_the_right_to_education\"'."}),
    ('U2', 'U', 'Must every person be given equal access to higher education on the basis of merit?',
     {"ast": ["forall", "person", ["unary", "equal_access_to_higher_education_required", ["var", 0]]], "form": "fronted", "sentence": "every person must be given equal access to higher education on the basis of merit.", "spans": [[0, 82]], "status": "one", "text": "You asked whether every person must be given equal access to higher education on the basis of merit."}),
    ('U3', 'U', 'Must every person be spared exclusion from education?',
     {"ast": ["forall", "person", ["unary", "education_spared_required", ["var", 0]]], "form": "fronted", "sentence": "every person must be spared exclusion from education.", "spans": [[0, 53]], "status": "one", "text": "You asked whether every person must be spared exclusion from education."}),
    ('U4', 'U', 'Is it the case that every person has the right to education?',
     {"class": "SyntaxError", "code": "NoDerivation", "span": [32, 59], "status": "none", "text": "The question has no reading with the current vocabulary. Closest sentence tried: \"every person has the right to education.\". Unknown English phrase 'has the right to education'. Nearest declared wordings: 'is classified as \"has_the_right_to_education\"'; 'course of education'; 'is classified as \"asylum_right_covers_case\"'."}),
    ('U5', 'U', 'May every person form as well as join trade unions to protect their interests?',
     {"ast": ["forall", "person", ["unary", "person_may_form_and_join_trade_unions", ["var", 0]]], "form": "fronted", "sentence": "every person may form as well as join trade unions to protect their interests.", "spans": [[0, 78]], "status": "one", "text": "You asked whether every person may form as well as join trade unions to protect their interests."}),
    ('U6', 'U', 'Must every person receive elementary education?',
     {"ast": ["forall", "person", ["unary", "elementary_education_received_required", ["var", 0]]], "form": "fronted", "sentence": "every person must receive elementary education.", "spans": [[0, 47]], "status": "one", "text": "You asked whether every person must receive elementary education."}),
    ('U7', 'U', 'Must every education kind be made generally available?',
     {"ast": ["forall", "education_kind", ["unary", "education_generally_available_required", ["var", 0]]], "form": "fronted", "sentence": "every education kind must be made generally available.", "spans": [[0, 54]], "status": "one", "text": "You asked whether every education kind must be made generally available."}),
    ('U8', 'U', 'May a university charge fees?',
     {"advice": {"id": "question-indefinite", "text": "Write \"every\" or \"some\" in place of \"a\"."}, "class": "SyntaxError", "code": "NoDerivation", "span": [4, 5], "status": "none", "text": "The question has no reading with the current vocabulary. Closest sentence tried: \"a may university charge fees.\". Expected 'therefore', 'so', 'hence', 'it follows that', 'it is not the case that ', 'both ', 'either ', 'if ', 'all of the following hold: first clause: ', 'both of the following hold: first clause: ', 'at least one of the following holds: first clause: ', 'if the following holds: first clause: ', 'all of the following hold: ', 'both of the following hold: ', 'at least one of the following holds: ', 'if the following holds: ', 'for every ', 'every ', 'there is ', 'it', 'that ', 'the first ', 'the second ', 'the third ', 'the fourth ', 'the fifth ', 'the sixth ', 'the seventh ', 'the eighth ', 'this holds in all cases', 'this is impossible', 'some ', 'no ' or 'starting from ' here. Use the English paraphrase as a writing example."}),
    ('U9', 'U', 'Does every person have the right to education?',
     {"class": "SyntaxError", "code": "QuestionForm", "span": [0, 46], "status": "none", "text": "VE answers questions that begin with \"Is\", \"Must\" or \"May\", or with \"Is it the case that\" followed by a sentence."}),
]
