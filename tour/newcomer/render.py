"""Write one stand-in newcomer's transcript (tour/newcomer/run<n>.md) from the session's stream-json record.

usage: python3 tour/newcomer/render.py <run number> <session record .jsonl> <out .md>

The record is the newline-separated JSON a `claude -p --output-format stream-json` session prints. This keeps, in
order, every tool call the session made (its tool and input), each call's output, and the session's final reply,
verbatim except for the scrub below. It drops everything else: session and message ids, account and rate-limit
details, cost and token counts, and the hidden reasoning (the record holds none of its text).

Scrub (scrub()): the newcomer's own folder becomes <newcomer>; any other home folder becomes <home>; e-mail
addresses become <e-mail>; a Claude account name (claude-<name> that is not a model name) becomes <account>; a
run of zero bytes (one output holds some) becomes "[<n> zero bytes]" and any other control character its backslash-x code.
The tour page the session read is not repeated: its sha256 is printed instead (the page is in this repository).
"""
from __future__ import annotations

import hashlib
import json
import re
import sys

NEWCOMER_DIR = re.compile(r"/(?:home|Users)/[^/\s\"'`]+/[^\s\"'`]*?newcomer-\d+")
HOME = re.compile(r"/(?:home|Users)/[^/\s\"'`]+")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
ACCOUNT = re.compile(r"\bclaude-(?!(?:sonnet|opus|haiku|fable)-)[a-z0-9][a-z0-9.]*\b")
ZEROS = re.compile("\x00+")
CONTROL = re.compile("[\x01-\x08\x0b-\x1f\x7f]")
PAGE_READ = re.compile(r"^\s*1\t# A tour of Verifiable English")


def scrub(text: str) -> str:
    text = NEWCOMER_DIR.sub("<newcomer>", text)
    text = HOME.sub("<home>", text)
    text = EMAIL.sub("<e-mail>", text)
    text = ACCOUNT.sub("<account>", text)
    text = ZEROS.sub(lambda m: f"[{len(m.group(0))} zero bytes]", text)
    return CONTROL.sub(lambda m: f"\\x{ord(m.group(0)):02x}", text)


def _result_text(content) -> str:
    if isinstance(content, str):
        return content
    return "".join(part.get("text", "") for part in content or [] if isinstance(part, dict))


def _page_text(read_output: str) -> str:
    """The page as the Read tool showed it, without its line-number prefixes."""
    return "\n".join(re.sub(r"^\s*\d+\t", "", line, count=1) for line in read_output.split("\n"))


def fence(text: str, lang: str = "") -> str:
    ticks = max([3] + [len(m) + 1 for m in re.findall(r"`{3,}", text)])
    return f"{'`' * ticks}{lang}\n{text.rstrip(chr(10))}\n{'`' * ticks}"


def events(path):
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def render(run: int, path) -> str:
    model, steps, outputs, final, seconds = "", [], {}, "", None
    for event in events(path):
        kind = event.get("type")
        if kind == "system" and event.get("subtype") == "init":
            model = event.get("model", "")
        elif kind == "assistant":
            for block in event["message"]["content"]:
                if block.get("type") == "tool_use":
                    steps.append((block["id"], block["name"], block.get("input", {})))
        elif kind == "user" and isinstance(event["message"]["content"], list):
            for block in event["message"]["content"]:
                if block.get("type") == "tool_result":
                    outputs[block["tool_use_id"]] = _result_text(block.get("content"))
        elif kind == "result":
            final = event.get("result", "")
            seconds = round(event.get("duration_ms", 0) / 1000)
    out = [f"# Stand-in newcomer, run {run}", "",
           f"A stand-in, not a person: a fresh {model} session that knew nothing of the project (see README.md in "
           "this folder for how it was run and what was removed from the record). It made "
           f"{len(steps)} tool calls in {seconds} seconds. Every call and its output follow in order, then its "
           "report.", ""]
    for number, (call_id, tool, given) in enumerate(steps, 1):
        output = outputs.get(call_id, "")
        if tool == "Bash":
            out += [f"## Call {number}: Bash", "", fence(scrub(given.get("command", "")), "sh"), ""]
        else:
            shown = {k: v for k, v in given.items()}
            out += [f"## Call {number}: {tool}", "", fence(scrub(json.dumps(shown, indent=1, ensure_ascii=False)),
                                                             "json"), ""]
        if PAGE_READ.match(output):
            digest = hashlib.sha256(_page_text(output).encode("utf-8")).hexdigest()
            lines = output.count("\n") + 1
            out += [f"Output: the tour page, {lines} lines, not repeated here (sha256 of its text without the line "
                    f"numbers: {digest}; README.md in this folder says which version it is).", ""]
        else:
            out += ["Output:", "", fence(scrub(output)), ""]
    out += ["## Report (the session's final reply)", "", scrub(final).rstrip("\n"), ""]
    return "\n".join(out)


def main(argv):
    run, path, dest = int(argv[1]), argv[2], argv[3]
    with open(dest, "w", encoding="utf-8") as handle:
        handle.write(render(run, path))


if __name__ == "__main__":
    main(sys.argv)
