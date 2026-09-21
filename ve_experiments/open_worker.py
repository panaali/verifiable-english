"""Worker process for local open-weight judges. Standalone: imports nothing from this repository, so it
can run under a different interpreter (the one that has `mlx-lm`), e.g. Python 3.12 while the harness
runs 3.14. Started by `ve_experiments.open_backend`; speaks JSON lines on stdin/stdout.

Request : {"id", "model", "system", "prompt", "max_new", "temp", "seed", "verdict", "allowed"}
Reply   : {"id", "text", "input_tokens", "output_tokens", "gen_s", "batch_size", "extra"} or {"id", "error"}

One model is loaded at a time; a request for another model unloads the current one first.
Greedy requests (temp == 0) that arrive together and share (model, max_new, verdict) are generated as one
batch. Sampled requests (temp > 0) run one at a time, each after seeding the generator with its own seed,
so a (prompt, seed) pair is reproducible.

Verdict modes
  free           the model writes its whole reply (reasoning, then the JSON verdict). Default.
  forced         no reasoning: the reply is forced to be {"verdict": "<v>"} where <v> is the allowed verdict
                 with the higher log-probability as continuation of the assistant prefix '{"verdict": "'.
  reason_forced  the model reasons freely (up to max_new tokens); whatever it wrote from its last
                 '{"verdict"' on is cut, the prefix '{"verdict": "' is appended, and the verdict is chosen by
                 log-probability as above. The reply is reasoning + forced JSON.
"""

from __future__ import annotations

import json
import queue
import sys
import threading
import time

VERDICT_PREFIX = '{"verdict": "'
VERDICT_SUFFIX = '"}'


class MLXEngine:
    def __init__(self) -> None:
        self.name = None
        self.model = None
        self.tok = None

    def load(self, name: str) -> None:
        if name == self.name:
            return
        import gc

        import mlx.core as mx
        from mlx_lm import load

        self.model = self.tok = self.name = None
        gc.collect()
        mx.clear_cache()
        self.model, self.tok = load(name)
        self.name = name

    def _chat(self, system: str, prompt: str) -> str:
        msgs = [{"role": "system", "content": system}, {"role": "user", "content": prompt}] if system else None
        try:
            if msgs is None:
                raise ValueError
            return self.tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
        except Exception:  # template without a system role (Gemma): fold the system text into the user turn
            text = f"{system}\n\n{prompt}" if system else prompt
            return self.tok.apply_chat_template([{"role": "user", "content": text}], add_generation_prompt=True, tokenize=False)

    def _encode(self, text: str) -> list[int]:
        return self.tok.encode(text, add_special_tokens=False)

    def generate(self, reqs: list[dict]) -> list[dict]:
        import mlx.core as mx
        from mlx_lm.generate import batch_generate
        from mlx_lm.sample_utils import make_sampler

        chats = [self._chat(r["system"], r["prompt"]) for r in reqs]
        verdict = reqs[0]["verdict"]
        texts = [""] * len(reqs)
        if verdict != "forced":
            ids = [self._encode(c) for c in chats]
            temp = float(reqs[0]["temp"])
            if temp > 0:
                assert len(reqs) == 1
                mx.random.seed(int(reqs[0]["seed"]))
            out = batch_generate(self.model, self.tok, ids, max_tokens=int(reqs[0]["max_new"]), sampler=make_sampler(temp=temp))
            texts = list(out.texts)
        replies = []
        for r, chat, text in zip(reqs, chats, texts):
            extra = {}
            n_out = len(self._encode(text)) if text else 0
            if verdict in ("forced", "reason_forced"):
                cut = text.rfind('{"verdict"')
                reasoning = (text[:cut] if cut >= 0 else text).rstrip()
                head = chat + (reasoning + "\n\n" if reasoning else "") + VERDICT_PREFIX
                scores = {v: self._continuation_logprob(head, v + VERDICT_SUFFIX) for v in r["allowed"]}
                best = max(scores, key=scores.get)
                text = (reasoning + "\n\n" if reasoning else "") + VERDICT_PREFIX + best + VERDICT_SUFFIX
                extra = {"verdict_logprobs": {k: round(v, 4) for k, v in scores.items()}, "free_had_verdict": cut >= 0}
            replies.append({"id": r["id"], "text": text, "input_tokens": len(self._encode(chat)), "output_tokens": n_out, "extra": extra})
        return replies

    def _continuation_logprob(self, head: str, cont: str) -> float:
        """log P(cont | head), tokenizing head+cont as one string so token merges at the seam are honoured."""
        import mlx.core as mx

        full, base = self._encode(head + cont), self._encode(head)
        k = 0
        while k < min(len(full), len(base)) and full[k] == base[k]:
            k += 1
        k = max(k, 1)
        logits = self.model(mx.array([full[:-1]]))[0]
        logp = logits[k - 1 :].astype(mx.float32)
        logp = logp - mx.logsumexp(logp, axis=-1, keepdims=True)
        targets = mx.array(full[k:])
        return float(mx.sum(mx.take_along_axis(logp, targets[:, None], axis=-1)).item())


def batch_key(r: dict):
    return (r["model"], r["max_new"], r["verdict"], tuple(r["allowed"]), float(r["temp"]) > 0)


def serve(engine, lines, write, max_batch: int = 8, window_s: float = 0.25) -> None:
    """Read requests from `lines` (an iterator of JSON lines), answer through `write(dict)`."""
    q: queue.Queue = queue.Queue()

    def reader() -> None:
        for line in lines:
            if line.strip():
                q.put(json.loads(line))
        q.put(None)

    threading.Thread(target=reader, daemon=True).start()
    pending: list[dict] = []
    closed = False
    while True:
        if not pending:
            if closed:
                return
            item = q.get()
            if item is None:
                return
            pending.append(item)
        deadline = time.monotonic() + window_s
        while not closed and len(pending) < max_batch:  # gather what arrives together
            try:
                item = q.get(timeout=max(0.0, deadline - time.monotonic()))
            except queue.Empty:
                break
            if item is None:
                closed = True
            else:
                pending.append(item)
        key = batch_key(pending[0])
        limit = 1 if key[-1] else max_batch  # sampled requests run alone, with their own seed
        batch = [r for r in pending if batch_key(r) == key][:limit]
        pending = [r for r in pending if r not in batch]
        t0 = time.monotonic()
        try:
            engine.load(batch[0]["model"])
            replies = engine.generate(batch)
        except Exception as exc:  # noqa: BLE001 - reported to the caller, which decides about retries
            replies = [{"id": r["id"], "error": f"{type(exc).__name__}: {exc}"[:500]} for r in batch]
        dt = round(time.monotonic() - t0, 3)
        for rep in replies:
            rep.update(gen_s=dt, batch_size=len(batch))
            write(rep)


def main() -> None:
    out_lock = threading.Lock()
    real_stdout = sys.stdout
    sys.stdout = sys.stderr  # libraries that print must not corrupt the protocol

    def write(obj: dict) -> None:
        with out_lock:
            real_stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
            real_stdout.flush()

    max_batch = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    serve(MLXEngine(), sys.stdin, write, max_batch=max_batch)


if __name__ == "__main__":
    main()
