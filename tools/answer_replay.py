"""Replay recorded `ve_service` cases against one build, and compare two builds' answers.

Part of the answer-level cutoff (tools/answer_cutoff.py), an R1 experiment: tools/gate.py, the merge
train and the nightlies never use it.

* `replay RECORDING --service PATH --output ANSWERS` sends every case the recording holds
  (`answer_cutoff.py record`) to the build at PATH, one case per request, as recorded: the case
  text the client sent and, for a case that names its environment by handle, that environment
  registered with it. Each answer is the whole response but its nonce, kept as the SHA-256 of its
  compact JSON with Lean's key order, so `1` and `1.0`, or `true` and `1`, differ; a request that
  raises keeps its exception's class. The client's schema and binding checks run on every answer.
* `diff BASE HEAD --output DIFF` lists the cases whose answers differ, or that either side lacks.
  `tools/select_tests.py --cutoff answers=DIFF` selects by it.

One case per request is exact for each case's answer: given the request's budget and decoding,
result i is `runMode` of case i (`VE.Service.runRequest_ok`, `boundResults_eq`). What a single case
cannot show, a batch's budget, one case failing a whole request and the service's request loop,
lives in lean/VE/Service/Protocol.lean, lean/Serve.lean and lean/VE/Json.lean; the cutoff selects
every service user when one of those changes.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import queue
import sys
import threading

from layer_policy import ROOT

sys.path.insert(0, str(ROOT))
from ve.backends import lean_service  # noqa: E402

VERSION = 1
# Wall-clock seconds per replayed request: an explicit timeout replaces the mode's CPU deadline, so
# a loaded machine never turns an answer into CheckerUnavailable; a hung build still ends.
REPLAY_TIMEOUT = 600.0
UNREPLAYABLE = "unreplayable"


def digest_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_jsonl(path: Path):
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            yield json.loads(line)


def load_cases(recording: Path) -> tuple[dict[str, tuple[str, str]], dict[str, str]]:
    """The recording's cases (key -> (mode, text)) and environments (digest -> text)."""
    cases = {row["k"]: (row["m"], row["c"]) for row in read_jsonl(recording / "cases.jsonl.gz")}
    environments = {row["d"]: row["t"] for row in read_jsonl(recording / "environments.jsonl.gz")}
    return cases, environments


def answer_digest(response: object) -> str:
    return hashlib.sha256(json.dumps(response, ensure_ascii=False, separators=(",", ":"))
                          .encode()).hexdigest()[:32]


def ask(service: lean_service.LeanService, mode: str, text: str, environments: dict[str, str]) -> str:
    """The digest of `service`'s answer to the one case `text`, sent as the client sent it."""
    try:
        case = lean_service._decode_json(text)
    except ValueError:
        case = None
    handle = case.get(lean_service.HANDLE_KEY) if type(case) is dict else None
    try:
        if isinstance(handle, str):
            if handle not in environments:
                return f"{UNREPLAYABLE}: the recording lacks the case's environment"
            sent = lean_service._Sent(None, text, handle, environments[handle])
            decoded = {handle: json.loads(environments[handle], parse_int=lean_service._json_integer)}
            _, response = service.exchange(mode, f"[{text}]", 1, timeout=REPLAY_TIMEOUT, texts=[text],
                                           environments={handle: environments[handle]},
                                           expanded=[sent.expanded(decoded)])
        else:
            _, response = service.exchange(mode, f"[{text}]", 1, timeout=REPLAY_TIMEOUT, texts=[text])
    except Exception as exc:  # noqa: BLE001  the class is the answer, compared like any other
        return f"raised: {type(exc).__name__}"
    response = dict(response)
    response.pop("id", None)
    return answer_digest(response)


def replay(recording: Path, executable: Path, jobs: int = 4, *, progress=print) -> dict:
    cases, environments = load_cases(recording)
    if not cases:
        raise ValueError(f"{recording} holds no case to replay")
    build = lean_service.executable_sha256(Path(executable))
    pending: queue.Queue = queue.Queue()
    for key in sorted(cases):
        pending.put(key)
    answers: dict[str, str] = {}
    lock = threading.Lock()

    def work():
        with lean_service.LeanService(executable, expected_sha256=build,
                                      startup_timeout=REPLAY_TIMEOUT) as service:
            while True:
                try:
                    key = pending.get_nowait()
                except queue.Empty:
                    return
                mode, text = cases[key]
                answer = ask(service, mode, text, environments)
                with lock:
                    answers[key] = answer
                    if len(answers) % 20000 == 0:
                        progress(f"replayed {len(answers)} of {len(cases)} cases")

    threads = [threading.Thread(target=work, daemon=True) for _ in range(max(1, jobs))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    if len(answers) != len(cases):
        raise RuntimeError(f"replayed {len(answers)} of {len(cases)} cases")
    return {"version": VERSION, "service": build, "recording": digest_file(recording / "requests.json.gz"),
            "answers": dict(sorted(answers.items()))}


def diff(base: dict, head: dict) -> dict:
    """The cases whose answers differ between two replays of one recording, or that one side lacks."""
    for side in (base, head):
        if side.get("version") != VERSION or not isinstance(side.get("answers"), dict) or not side["answers"]:
            raise ValueError("not an answer replay, or an empty one")
    if base["recording"] != head["recording"]:
        raise ValueError("the two replays are of different recordings")
    keys = base["answers"].keys() | head["answers"].keys()
    # A case either side could not replay is never the same answer.
    changed = sorted(key for key in keys if base["answers"].get(key) != head["answers"].get(key)
                     or base["answers"][key].startswith(UNREPLAYABLE))
    return {"version": VERSION, "recording": base["recording"], "base": base["service"], "head": head["service"],
            "cases": len(keys), "changed": changed}


def write_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    opener = gzip.open if path.name.endswith(".gz") else open
    with opener(path, "wt", encoding="utf-8") as handle:
        json.dump(data, handle, separators=(",", ":"))


def read_json(path: Path) -> dict:
    opener = gzip.open if Path(path).name.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("replay", help="replay a recording against one ve_service build")
    one.add_argument("recording", type=Path)
    one.add_argument("--service", type=Path, default=lean_service.DEFAULT_EXECUTABLE)
    one.add_argument("--jobs", type=int, default=4, help="service processes")
    one.add_argument("--output", type=Path, required=True)
    two = sub.add_parser("diff", help="the cases whose answers two replays disagree on")
    two.add_argument("base", type=Path)
    two.add_argument("head", type=Path)
    two.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "replay":
        data = replay(args.recording, args.service, args.jobs)
        write_json(data, args.output)
        print(f"replayed {len(data['answers'])} cases against {data['service'][:16]}: {args.output}")
        return 0
    data = diff(read_json(args.base), read_json(args.head))
    write_json(data, args.output)
    print(f"{len(data['changed'])} of {data['cases']} answers changed: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
