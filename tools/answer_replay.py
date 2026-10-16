"""Replay recorded `ve_service` cases against one build, and compare two builds' answers.

Part of the answer-level cutoff (tools/answer_cutoff.py), an R1 experiment: tools/gate.py, the merge
train and the nightlies never use it.

* `replay RECORDING --service PATH --output ANSWERS` sends every case the recording holds
  (`answer_cutoff.py record`) to the build at PATH: the case text the client sent, a case that names
  its environment by handle with that environment in its place (`inline`, the client's resend form),
  so that no answer depends on which handles a process holds, which varies from run to run. Cases go
  in batches of one mode (`batches`, the same for every build); a case's answer is its bound entry
  but its positions in the batch (`unplaced`), kept as the SHA-256 of its compact JSON with Lean's
  key order, so `1` and `1.0`, or `true` and `1`, differ. A batch the service refuses or fails as a whole is
  asked again one case per request, where a refusal, or the class of what was raised, is the
  answer. The client's schema and binding checks run on every response.
* `diff BASE HEAD --output DIFF` lists the cases whose answers differ, or that either side lacks.
  `tools/select_tests.py --cutoff answers=DIFF` selects by it.

A batch is exact for each case's answer: given the request's budget and decoding, result i is
`runMode` of case i (`VE.Service.runRequest_ok`, `boundResults_eq`). What a replay cannot show, the
recorded batches' budgets, one case failing a whole request and the service's request loop,
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

# 2: cases are replayed in batches, and a case's answer is its bound entry but its position.
# 3: and but the position an error result carries (`case_index`).
# 4: every case goes inline (`inline`), so no answer depends on the handles a process holds.
VERSION = 4
BATCH_CASES = 64
BATCH_BYTES = 1 << 20
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


def handle_of(text: str) -> str | None:
    """The environment handle a recorded case text names, if any: read as the service reads it, so a key
    written with escapes names one too."""
    try:
        case = lean_service._decode_json(text)
    except ValueError:
        return None
    handle = case.get(lean_service.HANDLE_KEY) if type(case) is dict else None
    return handle if isinstance(handle, str) else None


def inline(text: str, environments: dict[str, str]) -> str:
    """The case text with the environment it names by handle in place of the handle: what the client
    sends when the service lacks the handle (`_Sent.inline`), which it answers as the handle (VE.Service.Handles)."""
    handle = handle_of(text)
    if handle is None:
        return text
    case = json.loads(text, parse_int=lean_service._json_integer)
    del case[lean_service.HANDLE_KEY]
    case["environment"] = json.loads(environments[handle], parse_int=lean_service._json_integer)
    return lean_service._dumps(case)


def send(service: lean_service.LeanService, mode: str, texts: list[str]) -> dict:
    """The service's response to the inline case texts `texts` in one request."""
    return service.exchange(mode, "[" + ",".join(texts) + "]", len(texts), timeout=REPLAY_TIMEOUT, texts=texts)[1]


def unplaced(entry: dict) -> dict:
    """A bound entry without the positions its request gave it: `index` and an error result's `case_index`
    (VE.Service.Protocol). The client's binding check, which runs on every replayed response, checks them."""
    result = entry.get("result")
    if isinstance(result, dict) and "case_index" in result:
        entry = {**entry, "result": {key: value for key, value in result.items() if key != "case_index"}}
    return {key: value for key, value in entry.items() if key != "index"}


def ask(service: lean_service.LeanService, mode: str, texts: list[str]) -> list[str]:
    """The answer to each case of `texts`: its bound entry but its positions, from one request; when the
    request is refused or fails as a whole, each case is asked alone, and a refusal (the response but its
    nonce) or the class of what was raised is that case's answer."""
    try:
        response = send(service, mode, texts)
    except lean_service.ResourceLimit:
        if len(texts) == 1:  # the client's own line limit: the service never saw the case
            return [f"{UNREPLAYABLE}: the case does not fit one request line inline"]
        response = None
    except Exception as exc:  # noqa: BLE001  the class is the answer, compared like any other
        if len(texts) == 1:
            return [f"raised: {type(exc).__name__}"]
        response = None
    if response is not None and response.get("status") != "error":
        return [answer_digest(unplaced(entry)) for entry in response["results"]]
    if len(texts) == 1:
        return [answer_digest({key: value for key, value in response.items() if key != "id"})]
    return [ask(service, mode, [text])[0] for text in texts]


def batches(cases: dict[str, tuple[str, str]], environments: dict[str, str]) -> list[tuple[str, list[str]]]:
    """The requests a replay sends: per mode, in key order, at most BATCH_CASES cases and about
    BATCH_BYTES of inline case text; the same for every build replayed."""
    by_mode: dict[str, list[str]] = {}
    for key in sorted(cases):
        by_mode.setdefault(cases[key][0], []).append(key)
    found: list[tuple[str, list[str]]] = []
    for mode, ordered in sorted(by_mode.items()):
        keys, size = [], 0
        for key in ordered:
            text = cases[key][1]
            extra = len(text) + len(environments.get(handle_of(text) or "", ""))
            if keys and (len(keys) >= BATCH_CASES or size + extra > BATCH_BYTES):
                found.append((mode, keys))
                keys, size = [], 0
            keys.append(key)
            size += extra
        found.append((mode, keys))
    return found


def replay(recording: Path, executable: Path, jobs: int = 4, *, progress=print,
           modes: set[str] | None = None) -> dict:
    """Every case's answer from the build at `executable`; with `modes`, only those modes' cases
    (`partial` then names them, and `diff` refuses such a replay)."""
    cases, environments = load_cases(recording)
    if modes is not None:
        cases = {key: case for key, case in cases.items() if case[0] in modes}
    if not cases:
        raise ValueError(f"{recording} holds no case to replay")
    build = lean_service.executable_sha256(Path(executable))
    answers: dict[str, str] = {}
    pending: queue.Queue = queue.Queue()
    for mode, keys in batches(cases, environments):
        lost = [key for key in keys
                if (handle := handle_of(cases[key][1])) is not None and handle not in environments]
        answers.update((key, f"{UNREPLAYABLE}: the recording lacks the case's environment") for key in lost)
        if len(lost) < len(keys):
            pending.put((mode, [key for key in keys if key not in lost]))
    lock = threading.Lock()

    def work():
        with lean_service.LeanService(executable, expected_sha256=build, startup_timeout=REPLAY_TIMEOUT,
                                      handles=False) as service:
            while True:
                try:
                    mode, keys = pending.get_nowait()
                except queue.Empty:
                    return
                found = ask(service, mode, [inline(cases[key][1], environments) for key in keys])
                with lock:
                    before = len(answers) // 50000
                    answers.update(zip(keys, found, strict=True))
                    if len(answers) // 50000 > before:
                        progress(f"replayed {len(answers)} of {len(cases)} cases")

    threads = [threading.Thread(target=work, daemon=True) for _ in range(max(1, jobs))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    if len(answers) != len(cases):
        raise RuntimeError(f"replayed {len(answers)} of {len(cases)} cases")
    return {"version": VERSION, "service": build, "recording": digest_file(recording / "requests.json.gz"),
            **({"partial": sorted(modes)} if modes is not None else {}), "answers": dict(sorted(answers.items()))}


def diff(base: dict, head: dict) -> dict:
    """The cases whose answers differ between two replays of one recording, or that one side lacks."""
    for side in (base, head):
        if side.get("version") != VERSION or not isinstance(side.get("answers"), dict) or not side["answers"]:
            raise ValueError("not an answer replay, or an empty one")
        if "partial" in side:
            raise ValueError(f"a replay of the modes {side['partial']} only")
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
