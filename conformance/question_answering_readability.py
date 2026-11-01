"""Q2.6: the zero-training reading and writing evaluation of `ve ask`, sealed and not run, and its wording counts.

    uv run python conformance/question_answering_readability.py capture   # evidence/render/, evidence/wording.json
    uv run python conformance/question_answering_readability.py build     # readability/ and its MANIFEST.sha256
    uv run python conformance/question_answering_readability.py check     # readability/ is the build's and verifies

No model is called (plan Q2.6; the run is q2-6b). `capture` saves what a human gets of each fixture document (`ve
document render`) and reads back, through Lean's English reader (`ve.backends.english_lean.read`, the request
`read_question` builds, with the document's lexicon), every clause of every situation line of the saved answers;
the frames that cut a line into its slot are Lean's (`VE.Question.answerFrames`, printed by Lean). `build` reads only
saved files: the answers of `tests/fixtures/ask/`, the saved renders and `evidence/expected.json`'s order. Each
reading context is the document as `ve` shows it, the question, VE's answer lines exactly as `ve ask` prints them
and the fixed question; its key is the saved Lean lead. Each writing task gives the intended meaning in plain English,
the document and at most five example questions of another family's document; its gold is the saved
`english.question` reading. The protocol and the bars are in readability/README.md (hand-written, sealed with the rest).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/ask"
OUT = ROOT / "docs/question-answering/q2-6"
EVIDENCE = OUT / "evidence"
SEALED = OUT / "readability"
SITUATION_FRAMES = ("S1", "S2", "S2p", "S3")
FALLBACK = 'classified as "'
# `VE.Words.situationText` joins a situation's clauses with this; `VE.Ask.readingSuffix` starts a line's readings so.
CLAUSE_JOIN, READING_SUFFIX = "; ", ", reading sentence "

# The reading question's options: (label, text); the last is never shuffled. The key is the label of Lean's lead.
OPTIONS = [("YES", "Yes: the text guarantees it."),
           ("RULES-OUT", "No: the text rules it out."),
           ("ALLOWS-FAIL", "It is not guaranteed: the text allows a situation where it fails."),
           ("BY-READING", "It depends on how a sentence of the text is read."),
           ("OPEN", "The text does not settle it, or VE could not decide.")]
LABEL = {"yes": "YES", "no": "RULES-OUT", "notNecessarily": "ALLOWS-FAIL", "by_reading": "BY-READING",
         "notSettled": "OPEN", "unknown": "OPEN"}
CRITICAL = [("ALLOWS-FAIL", "RULES-OUT"), ("RULES-OUT", "ALLOWS-FAIL")]
NO_LEAD = "No."  # D4 and open question 1: the brief's lead, shown in place of "Not necessarily."

# The writing tasks: one per distinct reading of a fixture question (G1 and G2 read the same), the intended meaning
# in plain English (hand-written), and the example questions, saved fixture questions of another family's document.
TASKS = [("G1", ["G1", "G2"], "whether, according to the text, each and every member of the group is eligible"),
         ("G3", ["G3"], "whether, according to the text, all members are verified"),
         ("G4", ["G4"], "whether it is true, according to the text, that not a single member is eligible"),
         ("G10", ["G10"], "whether, according to the text, Ann is eligible"),
         ("U2", ["U2"], "whether the text requires that each person be given equal access to higher education, "
                        "based on merit"),
         ("U3", ["U3"], "whether the text requires that each person be kept from exclusion from education"),
         ("U5", ["U5"], "whether the text allows each person to form and to join trade unions to protect their "
                        "interests"),
         ("U6", ["U6"], "whether the text requires that each person receive elementary education"),
         ("U7", ["U7"], "whether the text requires that each kind of education be made generally available"),
         ("A1", ["A1"], 'whether the text allows the action "a27" to be performed'),
         ("A2", ["A2"], 'whether the text allows the action "a25" to be performed'),
         ("A3", ["A3"], 'whether the text allows the action "a26" to be performed'),
         ("A4", ["A4"], 'whether the text requires that the action "a13" be reported to the user'),
         ("A5", ["A5"], 'whether the text allows the action "a10" to be performed'),
         ("A7", ["A7"], "whether the text allows every action to be performed"),
         ("A8", ["A8"], "whether the text requires that every action be reported to the user")]
EXAMPLES = {"G": ["A4", "A7", "A8", "U5", "U6"], "U": ["G1", "G4", "G10", "A1", "A4"],
            "A": ["G1", "G4", "G10", "U5", "U6"]}

READING = """Read the text below and answer the question that follows it.

=== TEXT ===
{document}
=== A QUESTION SOMEONE ASKED VE ABOUT THE TEXT ===
{question}

=== VE'S ANSWER ===
{answer}

=== QUESTION ===
What does VE's answer tell you?
{options}

Answer with the letter of one option and a one-sentence reason, in exactly this form:
ANSWER: <letter>
REASON: <one sentence>
"""
WRITING = """You are writing in Verifiable English (VE), a controlled form of English that a checker reads. Write one \
yes-or-no question to VE about the text below that asks what you want to ask.

=== TEXT ===
{document}
=== WHAT YOU WANT TO ASK ===
You want to ask {intention}.

=== EXAMPLE VE QUESTIONS (about another text) ===
{examples}

Answer with your question and a one-sentence reason, in exactly this form:
QUESTION: <your VE question>
REASON: <one sentence>
"""
RETRY = """VE's response to your question:
{ve_message}

Write the question again (attempt {attempt} of 3). You may change it or keep it.
Answer with your question and a one-sentence reason, in exactly this form:
QUESTION: <your VE question>
REASON: <one sentence>
"""


def _json(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


def fixture_ids() -> list[str]:
    """The fixtures in the spec's order (evidence/expected.json)."""
    return [row["id"] for row in json.loads((EVIDENCE / "expected.json").read_text())["fixtures"]]


def answered() -> list[dict]:
    """The saved answer of every fixture that has one (A1d is a refusal), in the spec's order."""
    entries = [json.loads((FIXTURES / f"{ident}.json").read_text()) for ident in fixture_ids()]
    return [entry for entry in entries if "result" in entry]


def render_path(document: str) -> Path:
    return EVIDENCE / "render" / (Path(document).name.removesuffix(".ve.md") + ".txt")


# ---------------------------------------------------------------------------------------------------------------
# capture: Lean and `ve` calls, saved once

FRAMES_LEAN = """import VE.Question.Frames
open VE.Question
def pieceJson : Piece → Lean.Json
  | .lit s => Lean.Json.arr #[Lean.Json.str "lit", Lean.Json.str s]
  | .slot => Lean.Json.arr #[Lean.Json.str "slot"] | .num => Lean.Json.arr #[Lean.Json.str "num"]
  | .citation => Lean.Json.arr #[Lean.Json.str "citation"] | .answerLead => Lean.Json.arr #[Lean.Json.str "answerLead"]
#eval IO.println (Lean.Json.mkObj (answerFrames.map fun (f, ps) => (f, Lean.Json.arr (ps.map pieceJson).toArray))).compress
"""


def lean_frames() -> dict:
    """Lean's answer frames, printed by Lean (`VE.Question.answerFrames`)."""
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp) / "frames.lean"
        source.write_text(FRAMES_LEAN)
        done = subprocess.run(["lake", "env", "lean", str(source)], cwd=ROOT / "lean", capture_output=True,
                              text=True, check=True)
    return json.loads(done.stdout)


def slot(frames: dict, line: dict) -> str:
    """A situation line's one slot, cut by its frame's fixed text (`frame: [lit, slot, lit]`)."""
    pieces = frames[line["frame"]]
    if [p[0] for p in pieces] != ["lit", "slot", "lit"]:
        raise ValueError(f"frame {line['frame']} is not one slot between two fixed texts")
    head, tail, text = pieces[0][1], pieces[2][1], line["text"]
    if not (text.startswith(head) and text.endswith(tail)) or len(text) < len(head) + len(tail):
        raise ValueError(f"line is not of its frame {line['frame']}: {text!r}")
    return text[len(head):len(text) - len(tail)]


def clauses(frames: dict, line: dict) -> list[str]:
    """The clauses a situation line shows: its slot without the readings it names, split where Lean joins them."""
    body = slot(frames, line)
    if line["readings"]:
        body = body[:body.index(READING_SUFFIX)]
    return body.split(CLAUSE_JOIN)


def capture() -> None:
    from ve.ask import environment
    from ve.backends import english_lean
    from ve.english import EnglishVocabulary
    from ve.errors import VEError
    entries = answered()
    for document in sorted({entry["path"] for entry in entries}):
        shown = subprocess.run([sys.executable, "-m", "ve", "document", "render", document], cwd=ROOT,
                               capture_output=True, text=True, check=True)
        render_path(document).parent.mkdir(parents=True, exist_ok=True)
        render_path(document).write_text(shown.stdout)
    frames = lean_frames()
    readers, outcomes, rows = {}, {}, []
    for entry in entries:
        for index, line in enumerate(entry["result"]["lines"]):
            if line["frame"] not in SITUATION_FRAMES:
                continue
            if entry["path"] not in readers:
                env = environment((ROOT / entry["path"]).read_bytes())
                readers[entry["path"]] = (env, EnglishVocabulary(env, _defer_overlay_refusals=True))
            env, words = readers[entry["path"]]
            read_back = []
            for clause in clauses(frames, line):
                key = (entry["path"], clause)
                if key not in outcomes:  # each distinct clause of a document is read once
                    try:
                        reading = english_lean.read(env, clause + ".", words, {})
                        outcomes[key] = {"status": reading.status, "code": reading.response.get("code")}
                    except VEError as exc:
                        outcomes[key] = {"status": "unavailable", "code": type(exc).__name__}
                read_back.append({"clause": clause, **outcomes[key]})
            rows.append({"fixture": entry["id"], "line": index, "frame": line["frame"], "text": line["text"],
                         "clauses": read_back})
    saved = {"method": "each clause of each S1, S2, S2p and S3 line of the saved answers (tests/fixtures/ask/*.json "
                       "result.lines), with a full stop, read by Lean's English reader (ve.backends.english_lean.read) "
                       "in the document's environment with its lexicon; status `one` is one reading",
             "frames": {name: frames[name] for name in SITUATION_FRAMES}, "situation_lines": rows,
             "fallback": [{"fixture": entry["id"], "lines": [i for i, line in enumerate(entry["result"]["lines"])
                                                            if FALLBACK in line["text"]]} for entry in entries]}
    (EVIDENCE / "wording.json").write_text(_json(saved))


# ---------------------------------------------------------------------------------------------------------------
# build: saved files only

def _order(ident: str) -> list[tuple[str, str]]:
    """The options of `ident`'s items: the first four in an order fixed by a hash of the fixture id, then OPEN."""
    head = sorted(OPTIONS[:-1], key=lambda o: hashlib.sha256(f"{ident}:{o[0]}".encode()).hexdigest())
    return head + OPTIONS[-1:]


def reading_items(entries: list[dict]) -> list[tuple[dict, str]]:
    items = []
    for entry in entries:
        result, order = entry["result"], _order(entry["id"])
        letters = [chr(ord("A") + i) for i in range(len(order))]
        key = LABEL[result["lead"]]
        options = "\n".join(f"{letter}. {text}" for letter, (_, text) in zip(letters, order))
        document = render_path(entry["path"]).read_text()
        lead = [i for i, line in enumerate(result["lines"]) if line["frame"].startswith("A") and line["frame"] != "A0"]
        variants = [("shown", result["text"])]
        if result["lead"] == "notNecessarily":
            [i] = [j for j in lead if result["lines"][j]["frame"] == "A4"]
            variants.append(("no", [NO_LEAD if j == i else t for j, t in enumerate(result["text"])]))
        for variant, text in variants:
            ident = f"R-{entry['id']}" + ("" if variant == "shown" else "-no")
            items.append(({"id": ident, "fixture": entry["id"], "variant": variant, "document": entry["path"],
                           "question": entry["question"], "lead": result["lead"], "lead_lines": lead,
                           "key": letters[[o[0] for o in order].index(key)], "key_label": key,
                           "options": [{"letter": l, "label": o[0], "text": o[1]} for l, o in zip(letters, order)],
                           "context": f"contexts/{ident}.txt"},
                          READING.format(document=document, question=entry["question"], answer="\n".join(text),
                                         options=options)))
    return items


def writing_tasks(entries: list[dict]) -> list[tuple[dict, str]]:
    by_id = {entry["id"]: entry for entry in entries}
    tasks = []
    for ident, fixtures, intention in TASKS:
        entry = by_id[fixtures[0]]
        examples = [by_id[e]["question"] for e in EXAMPLES[ident[0]]]
        tasks.append(({"id": f"W-{ident}", "fixtures": fixtures, "document": entry["path"], "intention": intention,
                       "gold": entry["result"]["ast"], "gold_sentence": entry["result"]["sentence"],
                       "examples": EXAMPLES[ident[0]], "context": f"contexts/W-{ident}.txt"},
                      WRITING.format(document=render_path(entry["path"]).read_text(), intention=intention,
                                     examples="\n".join(f"{i}. {q}" for i, q in enumerate(examples, 1)))))
    return tasks


def files() -> dict[str, str]:
    """Every sealed file the builder writes, by path relative to readability/ (README.md is hand-written)."""
    entries = answered()
    reading, writing = reading_items(entries), writing_tasks(entries)
    out = {item["context"]: text for item, text in reading + writing}
    out["items.json"] = _json({"critical": CRITICAL, "question": "What does VE's answer tell you?",
                               "items": [item for item, _ in reading]})
    out["writing.json"] = _json({"retry": "contexts/retry.txt", "tasks": [task for task, _ in writing]})
    out["contexts/retry.txt"] = RETRY
    return out


def manifest(texts: dict[str, str]) -> str:
    return "".join(f"{hashlib.sha256(texts[p].encode()).hexdigest()}  {p}\n" for p in sorted(texts))


def build(dest: Path, readme: Path = SEALED / "README.md") -> None:
    texts = {**files(), "README.md": readme.read_text()}
    for path, text in texts.items():
        (dest / path).parent.mkdir(parents=True, exist_ok=True)
        (dest / path).write_text(text)
    (dest / "MANIFEST.sha256").write_text(manifest(texts))


def problems(dest: Path = SEALED) -> list[str]:
    """What differs from the build, and every manifest line that does not verify."""
    found = []
    texts = {**files(), "README.md": (dest / "README.md").read_text()}
    on_disk = {str(p.relative_to(dest)) for p in dest.rglob("*") if p.is_file()} - {"MANIFEST.sha256"}
    found += [f"not built: {p}" for p in sorted(on_disk - set(texts))]
    found += [f"differs from the build: {p}" for p in sorted(texts)
              if not (dest / p).is_file() or (dest / p).read_text() != texts[p]]
    for row in (dest / "MANIFEST.sha256").read_text().splitlines():
        digest, path = row.split("  ", 1)
        if not (dest / path).is_file() or hashlib.sha256((dest / path).read_bytes()).hexdigest() != digest:
            found.append(f"manifest does not verify: {path}")
    if (dest / "MANIFEST.sha256").read_text() != manifest(texts):
        found.append("manifest is not the build's")
    return found


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) == 2 else None
    if command == "capture":
        capture()
    elif command == "build":
        build(SEALED)
    elif command == "check":
        if errors := problems():
            raise SystemExit("\n".join(errors))
    else:
        raise SystemExit("usage: question_answering_readability.py capture|build|check")
