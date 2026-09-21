# Phase T design v2: a training study on Colab

Status: design only; nothing has been run. v2 applies Worker X's required changes 1-6, `design/phase-t-literature.md`, and the constrained-decoding decision. Names marked *(to build)* do not exist yet; `codex/grammar`, `codex/argument` and `codex/views` had no commits when this was written.

## 1. Plumbing

One browser visit: open <https://colab.research.google.com/drive/1YTZU3dhXys-kE3QkzaCZEB-6iYOJSJn_>, pick the GPU, paste the cell, run it, keep the tab open (`caffeinate -dims` locally). The cell reads `HF_TOKEN` from Colab Secrets, polls a private Hugging Face dataset repo, runs `jobs/<id>/job.json` (`{"cmd": "bash run.sh", "timeout_s": 7200}`), pushes `out/` every 4 minutes, and unassigns the runtime on `control/STOP` or after 45 idle minutes. It is syntax-checked against `huggingface_hub` 1.32 and has not been run in Colab.

```python
import os, sys, json, time, subprocess, traceback
from google.colab import userdata, runtime
os.environ["HF_TOKEN"] = userdata.get("HF_TOKEN")          # never printed; inherited by jobs
subprocess.run([sys.executable, "-m", "pip", "-q", "install", "-U", "huggingface_hub"])
from huggingface_hub import HfApi, snapshot_download
QUEUE = "ve-colab-jobs"                                      # second session: "ve-colab-jobs-2"
api = HfApi(); KW = dict(repo_id=f"{api.whoami()['name']}/{QUEUE}", repo_type="dataset")
api.create_repo(private=True, exist_ok=True, **KW)
put = lambda path, obj: api.upload_file(path_or_fileobj=json.dumps(obj).encode(), path_in_repo=path, **KW)
gpu = subprocess.run("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader",
                     shell=True, capture_output=True, text=True).stdout.strip()
t0 = last_job = time.time(); beat = 0
while True:
    try:
        files = set(api.list_repo_files(**KW))
        todo = sorted(f.split("/")[1] for f in files if f.startswith("jobs/") and f.endswith("/job.json")
                      and f"results/{f.split('/')[1]}/CLAIMED" not in files)
        if time.time() - beat > 300:
            put("status/heartbeat.json", {"t": time.time(), "up_h": (time.time() - t0) / 3600, "gpu": gpu, "todo": todo})
            beat = time.time()
        if "control/STOP" in files or (not todo and time.time() - last_job > 45 * 60):
            if "control/STOP" in files: api.delete_file("control/STOP", **KW)
            runtime.unassign()                              # stops compute-unit burn
        for j in todo[:1]:
            put(f"results/{j}/CLAIMED", {"t": time.time(), "gpu": gpu})
            d = snapshot_download(allow_patterns=f"jobs/{j}/*", local_dir="/content/q", **KW) + f"/jobs/{j}"
            spec = json.load(open(f"{d}/job.json")); os.makedirs(f"{d}/out", exist_ok=True)
            with open(f"{d}/out/log.txt", "w") as log:
                p = subprocess.Popen(spec["cmd"], shell=True, cwd=d, stdout=log, stderr=subprocess.STDOUT)
                end = time.time() + spec.get("timeout_s", 3600); push = time.time()
                while p.poll() is None:
                    time.sleep(5)
                    if time.time() > end: p.kill()
                    if time.time() - push > 240:
                        api.upload_folder(folder_path=f"{d}/out", path_in_repo=f"results/{j}", **KW); push = time.time()
            api.upload_folder(folder_path=f"{d}/out", path_in_repo=f"results/{j}", **KW)
            put(f"results/{j}/DONE", {"rc": p.returncode, "t": time.time()})
            last_job = time.time()
    except Exception:
        traceback.print_exc()
    time.sleep(20)
```

```sh
export HF_TOKEN=$(cat ~/Downloads/hugginface-access-token.txt)   # never echo
hf upload $U/ve-colab-jobs colab/jobs/0001 jobs/0001 --repo-type dataset
hf download $U/ve-colab-jobs --repo-type dataset --include "results/0001/*" --local-dir colab/
```

- Limits: Pro has no background execution (Pro+ only) and a 12 h cap, and publishes no idle period. Every run saves adapter, optimizer and RNG state every 25 steps and resumes.
- Compute units cannot be read inside the VM. Estimate them from heartbeat uptime x the rate table; the true balance is under Runtime > View resources.
- Alternatives checked: the official `google-colab-cli` 0.6.0 exists (`colab run --gpu A100 script.py`), but open bug #106 cuts off access to a VM that is still billing after 60 minutes, and it cannot read Secrets. Drive sync and tunnels add OAuth clicks and fragility. Kaggle (about 30 GPU-hours a week, `kaggle kernels push`) is the fallback.

## 2. Estimand

Arm A never shows the judge the formal claim `F`; arm B' shows a faithful rendering of `F`, and nothing the policy wrote. So **A vs B' tests replacing a policy-controlled explanation channel with a deterministic rendering**. It does not test VE against other notations. Faithful exposure is guaranteed; correct judgment is not, since a judge can misread a rendering and a policy can learn to exploit that. Arm F' separates the claims:

| Arm | The frozen training judge reads | Role |
|---|---|---|
| A | requirement + the policy's explanation | primary |
| B' | requirement + canonical VE rendering of the parsed AST; no checker | primary |
| F' | requirement + deterministic FOL-keyword rendering of the same AST *(to build)*; no checker | VE-specific control |
| R | nothing; approval is random, matched to A (section 4) | control |
| C | no judge; hidden scenario tests + two-way reference check | privileged baseline |
| B | B' judge x scenario tests | privileged baseline |

- Determinism claim: B' or F' against A. VE-specific claim: B' against F'.
- B and C see reference-linked information that no deployed supervisor has, and C shares oracle machinery with the outcome. They are privileged baselines, not ceilings, and the outcome is **not** independent of C.
- All arms share the environment's task term, which uses `ve.evaluate(env, F, M)`. It is part of the task, not of supervision.

**Task and temptation.** Each item has an environment, a prose requirement with hidden reference `R`, and a visible system state `M` (a `FiniteModel` listed as facts). In half the items `M` violates `R` but satisfies an E1-family weakening. The policy emits the structured output `{ve, explanation}` in every arm.

## 3. Labels, fragment and outcomes

**Three-valued oracle** *(to build on `codex/argument`)*:
- EQUIVALENT: certified entailment in both directions.
- DIFFERENT: a distinguishing finite model, confirmed by `check_countermodel`.
- UNKNOWN: anything else, including resource limits.

`meaning_id` hashes AST structure, so it is only a fast path to EQUIVALENT. `find_countermodel` returning `NotFound` proves nothing: "at most three objects" against `true` passes at size 3. Every rate is reported under both extreme assignments of UNKNOWN, and a decision must hold under both.

**Fragment.** Templates, and the decoding grammar, are restricted to the two-variable fragment with equality: at most two variable names, predicates of arity at most 2, a small set of constants, and no counting beyond what two variables express. This fragment is decidable and has the finite model property, so UNKNOWN can arise only from resource limits. The generator reports the UNKNOWN rate on reference-attack pairs, and the target is under 2%.

**Reference validation.** Each `R` must be satisfiable and not valid, and each attack must come with a stored distinguishing model. The empty-sort convention is fixed once and must be identical in the prover, the search and the generator; vacuous-domain attacks are validated under it. The oracle lives in a separate module from the rewards, uses a held-out model bank, and is cross-checked against the Lean semantics on the conformance cases.

**Outcomes** on held-out templates and their renamed-vocabulary twins:
- Report P(approved and wrong), P(wrong), and P(approved | wrong). The wrong-output population shifts during training, so the conditional rate alone can reverse a conclusion.
- Report P(approved and EQUIVALENT) as the usefulness measure.
- **Primary:** the training judge's approval in its own view, against oracle labels, as change from the shared SFT baseline.
- **Transfer:** approval by a panel that never contains a training judge or the alternate training judge: `Qwen/Qwen2.5-3B-Instruct` in Colab, plus the PLAN's hosted weak judges run locally.
- **Cross-scoring:** every evaluated output from every arm is scored under all three views. This separates "the policy became more deceptive" from "this view is harder to fool".
- Also: judge MCC over steps and KL, the capability gap between judge and policy, truncation and zero-variance rates, and 100 audited rollouts per arm (by a strong model, with the user spot-checking 20, because there are no human raters).

## 4. Optimization (frozen before the pilot)

- **Policy:** `Qwen/Qwen3-4B-Instruct-2507` if the sizing rule in section 9 passes, otherwise `Qwen/Qwen2.5-1.5B-Instruct`; LoRA r=32 on attention and MLP projections. **Judge:** `HuggingFaceTB/SmolLM3-3B`; the alternate is `microsoft/Phi-4-mini-instruct`. All are ungated; existence checked through the HF API. Second policy family: `allenai/OLMo-2-0425-1B-Instruct`.
- **Decoding:** grammar-constrained (`ve/grammar.py`, *to build*), identical in every arm from the SFT baseline onward, with no retries in rollouts. Verify-and-retry (`ve/authoring.py`) is used only for SFT data. Results therefore describe grammar-constrained policies. Length budgets are separate: `ve` at most 96 tokens, `explanation` at most 64. Hitting a cap gives reward 0 and is counted. Judge inputs are capped at 512 tokens, and an overflow is a generator error, never a silent truncation.
- **GRPO** on the stack chosen in section 8. One optimizer step = 16 prompts x 8 samples = 128 completions, run as 16 microbatches of 8. 200 steps = 25,600 completions per run. `num_iterations=1`, so updates are on-policy and `epsilon=0.2` rarely binds. AdamW, lr 1e-5 constant after 10 warm-up steps, no weight decay, gradient-norm clip 1.0, temperature 1.0, top-p 1.0. `loss_type="dr_grpo"` and `scale_rewards="none"`; confirm the names against the pinned TRL version (Unsloth pins `trl<=0.24.0`; current TRL is 1.13).
- **Reward** = valid x approve x task. `valid` and `approve` are 0 or 1, with approval defined as APPROVE logit > REJECT logit. `task` is 1.0 if `M` satisfies `F`, else 0.3. No other scaling.
- **KL:** the reference is the frozen SFT adapter. beta = 0.04 in every arm. Arms are compared only at checkpoints with KL at or below a common budget K, which is set from the pilot. A run stops when it exceeds 2K.
- **Arm R:** approval is Bernoulli, with p equal to arm A's baseline approval rate for that item type (tempting or honest). `valid` and `task` are treated exactly as in the other arms.
- **Judge hygiene:** single-token verdicts are verified; scoring uses a fixed batch composition and greedy logits; a duplicate-input check every 50 steps must reproduce verdicts.
- **Logging:** per step, the fraction of groups with zero reward variance.
- Rejection-sampling fine-tuning replaces GRPO only if the probe exceeds 90 s per step.

## 5. Gate (all on the dev split; no main runs before it passes)

1. **Competence.** On held-out templates, the SFT policy's EQUIVALENT rate on honest items is at least 50%. Below that, honest acceptance is not estimable. Parse validity is reported but is guaranteed by the grammar.
2. **Learning signal.** At baseline, at least 30% of 8-sample groups have non-zero reward variance under both A and B'. Otherwise GRPO receives no gradient.
3. **Selection probe.** Best-of-n for n = 1 to 32, per reward, on untouched dev items. This shows selection pressure only, not learnability.
4. **Paired RL pilot.** A and B', 2 paired seeds, 60 steps. Go if P(approved and wrong) under A rises above the SFT baseline in both seeds. The pilot's variance feeds the power simulation and sets K.

The smallest useful effect delta is not fixed at 10 points. It is the smallest difference that the 5-seed design detects with power 0.8 in a simulation from the pilot's variance. If delta exceeds 15 points, add seeds or report that the study cannot be informative. At most 3 reconfigurations (judge, sneaky prompt) are allowed, each logged; after that, report "deception not inducible at this scale".

## 6. Inference

- **One primary comparison:** B' minus A, in the change of P(approved and wrong) from the SFT baseline, on the test split.
- Seeds are paired across arms: same data order, SFT adapter and RNG. The bootstrap resamples seed pairs and template clusters, and each vocabulary twin stays in its template's cluster.
- **Checkpoint rule:** the latest checkpoint with KL at or below K whose dev P(approved and EQUIVALENT) is at least the baseline minus 5 points. If fewer than 4 of 5 seeds qualify in either arm, the result is inconclusive. No post-hoc interpolation.
- **Decisions.** Superiority: the 95% interval lies below 0 under both UNKNOWN bounds. Equivalence: the interval lies inside +/-m, with m set by the same simulation. Otherwise inconclusive. A negative point estimate alone is not a refutation.
- B' vs F' and F' vs A are secondary, Holm-adjusted. Judges are reported separately.

## 7. Budget and schedule

**End-to-end probe (about 20 minutes, L4).** 8 steps each of A and B' with the judge in the loop; one 100-item evaluation with cross-scoring; one full checkpoint upload. Report seconds per step per arm, judge seconds per step, evaluation seconds per item, and checkpoint seconds and MB. Oracle and panel scoring run locally on downloaded outputs, at zero units; time 100 oracle calls on the local CPU.

Provisional figures for the 1.5B policy at L4, 1.7 units per hour and an assumed 50 s per step (4.7 units per run). Nothing here is measured; rescale after the probe. Section 9 gives the variant with a larger policy.

| Order | Item | Units | Running total |
|---|---|---|---|
| 0 | Probe, judge calibration, SFT warm-up, baseline evaluation | 6 | 6 |
| 0 | Gate 1-3, and the pilot (4 runs x 60 steps) | 9 | 15 |
| 1 | **A and B', 5 paired seeds** (28 h) | 47 | 62 |
| 1 | Evaluation: per run 4 x 300 dev + 600 test generations, x 3 views | 6 | 68 |
| 2 | F', 5 seeds (14 h) | 24 | 92 |
| 3 | R, 3 seeds | 14 | 106 |
| 4 | C, 3 seeds | 14 | 120 |
| 5 | B, 3 seeds | 14 | 134 |
| | Restart and rerun reserve | 16 | 150 |

- At 90 s per step, the primary contrast costs 85 units and F' 42, so only A, B', F' and evaluation fit.
- Order of cuts: second family (unfunded unless steps take 35 s or less), then B, C, R, then F'. Never cut primary seeds or evaluation.
- **Wall-clock.** Primary training takes about 28 h on one L4, so Phase T finishes after the first paper draft. The draft reports the gate (competence, selection probe, pilot) and marks RL results as pending.
- **Parallelism.** Run one runner cell per Colab session, with a different `QUEUE` in each. Units are unchanged and wall-clock divides by the session count (Pro usually allows 2-3 GPU sessions; unverified). Keep each paired seed's arms on the same GPU type.
- **Faster GPUs.** A100 saves units only above 3.2x L4 speed; at about 2.5x it buys about 11 h of primary training for about 60 units. G4 (96 GB) could run three arms as concurrent processes and is unit-neutral at 5.1x aggregate throughput. The probe decides.

## 8. Stack: Unsloth or plain TRL + vLLM

Sources: Unsloth's RL guide, memory-efficient-RL page and notebook index; PyPI metadata; `unsloth_zoo/rl_replacements.py`. **Every performance number below is a vendor claim. I found no independent GRPO measurement on T4, L4 or A100.**

| | Unsloth 2026.9.7 | Plain TRL 1.13 + vLLM 0.29 (colocate) |
|---|---|---|
| Rollouts | vLLM in-process (`fast_inference=True`), sharing the weights with the trainer; "Standby" (`UNSLOTH_VLLM_STANDBY=1`) frees the KV cache during the update | vLLM in-process with its own copy of the weights; optional sleep mode |
| Memory | Vendor rule: for 4-bit QLoRA GRPO, VRAM in GB is about the parameter count in billions; 16-bit LoRA needs at least 4x more. Vendor: Llama 3.1 8B at 20K context, 8 generations, 54 GB against 511 GB | 16-bit LoRA; vendor says TRL tops out at 8B with 1K context on an A100 |
| Speed | Vendor: about 300 tokens/s on a T4; about 4,000 tokens/s on an A100-40GB with a 4-bit Llama 3.2 3B; "10% faster RL" | No figures found |
| Models | Dynamic 4-bit uploads exist for our candidates (checked: `unsloth/Qwen3-4B-Instruct-2507-unsloth-bnb-4bit`, `unsloth/Qwen2.5-1.5B-Instruct-unsloth-bnb-4bit`, `unsloth/Qwen2.5-7B-Instruct-unsloth-bnb-4bit`). GRPO notebooks: Qwen2.5 3B, Qwen3 4B, Llama 3.2 3B, Llama 3.1 8B, Qwen3-8B FP8 (L4), gpt-oss 20B, Gemma, Ministral 3 | Any HF causal LM |
| Custom reward | Plain Python callables `f(prompts, completions, **kwargs) -> list[float]`, as in the notebooks. Nothing prevents calling `ve` and a second frozen HF model in the same process | Same |
| Guided decoding | `GRPOConfig(vllm_sampling_params=SamplingParams(...))`; the patch copies every `SamplingParams` field, so `structured_outputs` with a grammar should pass through. **Unverified.** It is one grammar for all prompts | Only `vllm_structured_outputs_regex`; a recursive grammar needs a patch |
| Risk | Monkey-patches TRL and pins `trl<=0.24.0` with a long transformers exclusion list; option names differ from TRL 1.13; vendor advice of `gpu_memory_utilization=0.9-0.95` leaves no room for our judge | Fewer moving parts; more VRAM, so a smaller policy per GPU |

- **Judge memory.** A 3B bf16 judge needs about 6-7 GB outside vLLM's pool. Set `gpu_memory_utilization` near 0.6 and measure.
- **Grammar workaround.** Since one `SamplingParams` serves the whole batch, export a single fragment-level grammar (generic identifiers, two variable names, bounded depth) and let `ve.parse` enforce each environment's vocabulary, with reward 0 on failure. If the pass-through fails, fall back to a vLLM logits processor, and failing that to post-hoc validity with zero reward in every arm.
- **Largest policy at 16 x 8 completions and 512-token context (estimates from the vendor rule, not measured).** T4: 3-4B QLoRA, fp16 only, slow. L4: 8B QLoRA or FP8 with Unsloth, about 3B bf16 LoRA with plain TRL. A100-40GB: 14B QLoRA or 8B bf16 LoRA with Unsloth, about 7-8B with plain TRL at short context.
- **Recommendation.** Use Unsloth, starting from `unslothai/notebooks` `nb/Qwen3_(4B)-GRPO.ipynb` converted to `train_grpo.py`, with versions pinned in `requirements-colab.txt`. The end-to-end probe runs the same 8 steps on plain TRL too. Choose by units per run; on a tie choose plain TRL, because it has fewer patches.

## 9. Model size against the literature

| Study | Policy | Supervisor in the reward | Seeds |
|---|---|---|---|
| Wen 2024 | 7B | time-limited humans | not stated |
| Mahmoud 2026 | Qwen2.5-7B-Instruct (14B and 32B ablations) | GPT-4o-mini (weak), GPT-OSS-120B (strong); 16 H100 for 1.5 days | 1 |
| Arnesen 2024 | 8B | a model judge, trained with DPO (judge size recalled as GPT-4-class, not rechecked) | 1 |
| Kenton 2026 | Gemini Flash-class, proprietary | frozen weak judge | 3-4 |
| Kirchner 2024 | GPT-4-family provers | verifier at about 1/1000 of prover compute | not stated |
| Re:Form 2025 | 0.5B-14B | Dafny verifier | not stated |
| Tan 2026 | open models; sizes not in the abstract | Dafny verifier | not stated |
| Zhang 2026 | Qwen2.5-Coder-1.5B, deepseek-coder-1.3b, Llama-3.2-1B | test suites | 5, 400 steps |

- At 1.5B we match Zhang, the only preregistered multi-seed study, and sit inside Re:Form's range. We fall below Wen, Mahmoud and Arnesen (7-8B) and far below Kenton and Kirchner.
- At 4B we stay below the 7-8B studies but above the "tiny model" objection, with 5 seeds where they had one.
- **Sizing rule.** Take the largest policy among 1.5B, 4B and 8B for which A, B' and F' at 5 seeds each, plus about 27 units of overhead, fit in 125 units. That means at most 6.5 units per run: 69 s per step on L4, or 22 s per step on A100-40GB.
- My unmeasured guess is that 4B QLoRA passes on L4 or A100 and 8B does not, at roughly 100-130 s per step on L4, or 10-12 units per run. Running 8B for A and B' alone would cost 100-120 units and would sacrifice F', which the cut order permits but which removes the VE-specific claim. I do not recommend it.
- **If 4B passes:** A, B' and F' run at 4B with 5 seeds (up to 98 units). R, C and B run at 1.5B with 3 seeds only if units remain, and are labelled as a different size: they give context and are not contrasts. The second family is dropped. Arms are still cut before seeds.
- **Judge.** Keep the judge below the policy. With a 4B policy, calibrate `HuggingFaceTB/SmolLM2-1.7B-Instruct` and `HuggingFaceTB/SmolLM3-3B` and take the one that passes the E1 gate. Report the measured capability gap.

## 10. Repo prerequisites

- [ ] `requires-python` relaxed to `>=3.12` (Colab). `parse`, `print_document` and `find_countermodel` ran under 3.12.13; run the test suite there; `uv build --wheel`.
- [ ] `codex/argument` merged: a certified entailment API.
- [ ] `codex/grammar` merged: a per-environment grammar, restricted to the two-variable fragment, in a format vLLM accepts.
- [ ] `codex/views` merged: a deterministic FOL-keyword renderer. Note that `ve.render_fol` renders FOL *input* as VE; it is not this.
- [ ] E1 generator merged, fragment-restricted, with validated references and attacks.
- [ ] `experiments/T/PREREG.md`, written after the pilot and before the main runs.

## 11. Implementation tasks

**Worker X (semantics).**
1. `ve_train/oracle.py`: three-valued `label(env, F, R)`, resource-bounded, with worst-case bound helpers.
2. Fragment checker `in_fo2(doc)` and the grammar restriction; a test that every grammar-valid output parses and is in the fragment.
3. Reference and attack validator: satisfiable, not valid, stored distinguishing model, empty-sort convention, UNKNOWN rate report.
4. Held-out model bank and renamed-vocabulary twins in the generator; item schema with template and vocabulary ids and the dev/test split.
5. Conformance of the oracle with the Lean semantics; fuzz of reward C (`Top`, tautologies, vacuous domains, overconstraints).

**Worker C (harness).**
1. `ve_train/reward.py`: `score_A`, `score_Bprime`, `score_Fprime`, `score_B`, `score_C`, `score_R`. It shares no code with the oracle beyond `ve`.
2. `ve_train/judge.py`: logit verdicts, per-view prompts, token verification, repeatability check, overflow errors.
3. `sft_data.py` (verify-and-retry), `train_grpo.py` (frozen config, full-state resume, KL stop, zero-variance logging), `train_rft.py`, `bestofn.py`.
4. `eval_heldout.py` with cross-scoring; a local `panel.py` on the cached CLI calls; `analyze.py` with the paired cluster bootstrap, UNKNOWN bounds, checkpoint rule and power simulation.
5. `colab/`: `probe_e2e.sh` (runs both stacks and both policy sizes), `submit.sh`, `fetch.sh`, and a pinned `requirements-colab.txt` (trl, vllm, peft, transformers).
