"""D gate analysis (PREREG-DRAFT.md). Stdlib only; no model calls.

    python3 experiments/D-gate/analyze.py high [low]

Reads runs/<arm>/answers.jsonl and every runs/<arm>/ledger-<UTC date>.jsonl, reconciles all scheduled
samples (43 items x K=3) against the ledger identities, and refuses to analyse incomplete, duplicate or
unreconcilable data (exit 2). An arm stopped under a stop rule (runs/<arm>/STOP.json) gets no verdict.

Sample status (frozen):
  YES / NO        the final nonempty line of the reply is exactly `ANSWER: YES` or `ANSWER: NO`
  UNPARSED        a complete reply whose final nonempty line is not an answer line      } INVALID
  TRUNCATED       the reply stopped without a final turn (e.g. the output-token limit)  }
  ENDPOINT_ERROR  the call started but failed for an endpoint or infrastructure reason (incl. timeout)
INVALID samples are model outcomes: they count as errors in the primary error rate, never in a
directional numerator (false approval / false rejection), and a sensitivity analysis excludes them.
ENDPOINT_ERROR samples are excluded (available-case item means). An item with no model outcome is
listed and counts as error 0 in every gate statistic (missingness can never create a pass).

Primary (effort=high only): mean item error over the non-edge items (tag `edge`: D26, D42), clustered
by artefact. Gate: PASS needs the point estimate >= 0.15 AND (robustness, preregistered) >= 0.15 with the
planted edits excluded, errors on >= 5 artefacts, and >= 0.15 in every leave-one-artefact-out analysis.
A PASS whose 95% cluster-bootstrap lower bound is < 0.15 is a WEAK PASS. A t-interval over artefact
means is reported. The low-effort arm is descriptive: a pass at low effort alone does not count.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE = 0.15
K = 3
MIN_ERROR_ARTEFACTS = 5
ENDPOINT_ERROR_FRACTION = 0.10
BOOT_N, BOOT_SEED = 10000, 0

VALID = ("YES", "NO")
INVALID = ("UNPARSED", "TRUNCATED")
MODEL_OUTCOMES = VALID + INVALID
STATUSES = MODEL_OUTCOMES + ("ENDPOINT_ERROR",)
TRUNCATION_ERROR = "Truncated or non-final response"
FINAL_LEDGER = ("ok", "error", "infrastructure_error")
LEDGER_NAME = re.compile(r"^ledger-(\d{4}-\d{2}-\d{2})\.jsonl$")
ANSWER_LINE = re.compile(r"ANSWER:[ \t]*(YES|NO)")


class DataError(Exception):
    """The run data cannot be analysed (incomplete, duplicated or not reconcilable with the ledger)."""


# ------------------------------------------------------------------------------------------------
# Parsing and classification (shared with run_raw.py)
# ------------------------------------------------------------------------------------------------

def parse(text):
    """The answer on the final nonempty line, else UNPARSED. Earlier answer lines never count."""
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    if not lines:
        return "UNPARSED"
    m = ANSWER_LINE.fullmatch(lines[-1])
    return m.group(1) if m else "UNPARSED"


def classify_ledger_final(row):
    """Status of a sample from its final ledger row (claude_cli statuses ok/error/infrastructure_error)."""
    if row["status"] == "ok":
        return parse(row.get("text"))
    if row["status"] == "error" and str(row.get("error", "")).startswith(TRUNCATION_ERROR):
        return "TRUNCATED"
    return "ENDPOINT_ERROR"


def max_endpoint_errors(n_scheduled):
    """Stop rule: the run stops once endpoint errors exceed 10% of the scheduled samples."""
    return math.floor(ENDPOINT_ERROR_FRACTION * n_scheduled)


def sha256_text(s):
    return hashlib.sha256(s.encode()).hexdigest()


def schedule(prompt_ids, k=K):
    return [(i, s) for i in prompt_ids for s in range(k)]


# ------------------------------------------------------------------------------------------------
# Reconciliation
# ------------------------------------------------------------------------------------------------

def read_jsonl(path):
    rows = []
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except ValueError as exc:
                raise DataError(f"{path}:{n}: not JSON") from exc
    return rows


def load_arm(arm_dir):
    arm_dir = Path(arm_dir)
    answers = read_jsonl(arm_dir / "answers.jsonl") if (arm_dir / "answers.jsonl").exists() else []
    ledgers = {}
    for p in sorted(arm_dir.glob("ledger*.jsonl")):
        if not LEDGER_NAME.match(p.name):
            raise DataError(f"unexpected ledger file {p.name}")
        ledgers[p.name] = read_jsonl(p)
    stop = json.loads((arm_dir / "STOP.json").read_text()) if (arm_dir / "STOP.json").exists() else None
    return answers, ledgers, stop


def ledger_index(ledgers, prompts, frozen, arm, problems):
    """Per (item, sample): the started rows and final rows across every daily segment, after
    checking each row's identity against the frozen inputs."""
    fc = frozen["arms"][arm]
    idx = defaultdict(lambda: {"started": [], "final": []})
    for name, rows in ledgers.items():
        day = LEDGER_NAME.match(name).group(1)
        for r in rows:
            where = f"{name}: {r.get('item_id')}#{r.get('sample_index')} {r.get('status')}"
            ident = (r.get("item_id"), r.get("sample_index"))
            if ident[0] not in prompts or ident[1] not in range(frozen["k"]):
                problems.append(f"{where}: not a scheduled sample")
                continue
            if r.get("account_label") != frozen["account_label"]:
                problems.append(f"{where}: account {r.get('account_label')!r} is not the frozen account")
            if sha256_text(r.get("system") or "") != frozen["system_sha256"]:
                problems.append(f"{where}: system prompt differs from the frozen SYSTEM")
            if sha256_text(r.get("prompt") or "") != prompts[ident[0]]:
                problems.append(f"{where}: prompt differs from prompts.jsonl")
            c = r.get("controls") or {}
            for k, v in fc.items():
                if c.get(k) != v:
                    problems.append(f"{where}: control {k}={c.get(k)!r}, frozen {v!r}")
            if c.get("binary_sha256") != frozen["claude_binary_sha256"]:
                problems.append(f"{where}: claude binary differs from the frozen one")
            if c.get("context_date") != day:
                problems.append(f"{where}: context_date {c.get('context_date')} is not the segment date {day}")
            if r.get("status") == "started":
                if str(r.get("timestamp", ""))[:10] != day:
                    problems.append(f"{where}: started on {str(r.get('timestamp'))[:10]}, outside its segment")
                idx[ident]["started"].append(dict(r, _segment=name))
            elif r.get("status") in FINAL_LEDGER:
                if r["status"] == "ok" and r.get("served_model") != frozen["model"]:
                    problems.append(f"{where}: served model {r.get('served_model')!r}")
                idx[ident]["final"].append(dict(r, _segment=name))
            elif r.get("status") == "retry_scheduled":
                problems.append(f"{where}: infrastructure retries are not allowed in this study")
            else:
                problems.append(f"{where}: unknown ledger status")
    return idx


def ledger_status(entry):
    """(status, key, segment, error) implied by a sample's ledger rows (exactly one start)."""
    start = entry["started"][0]
    finals = [f for f in entry["final"] if f.get("key") == start.get("key")]
    if not finals:
        return "ENDPOINT_ERROR", start.get("key"), start["_segment"], "interrupted: started, no outcome logged"
    f = finals[-1]
    return classify_ledger_final(f), f.get("key"), f["_segment"], f.get("error")


def reconcile(answers, ledgers, prompts, frozen, arm, allow_incomplete=False):
    """Check the answers against the schedule and the ledger. Returns (records, orphans):
    records[(id, s)] = the answers row; orphans = scheduled samples the ledger shows as started but
    with no answers row (only with allow_incomplete, for the runner's resume). Raises DataError."""
    problems = []
    sched = schedule(list(prompts), frozen["k"])
    sset = set(sched)
    records = {}
    for r in answers:
        ident = (r.get("id"), r.get("sample"))
        if ident not in sset:
            problems.append(f"answers: {ident} is not a scheduled sample")
        elif ident in records:
            problems.append(f"answers: duplicate row for {ident}")
        elif r.get("status") not in STATUSES:
            problems.append(f"answers: {ident} has unknown status {r.get('status')!r}")
        elif r.get("arm") != arm:
            problems.append(f"answers: {ident} belongs to arm {r.get('arm')!r}")
        else:
            records[ident] = r
    idx = ledger_index(ledgers, prompts, frozen, arm, problems)
    orphans = []
    for ident in sched:
        entry = idx.get(ident)
        rec = records.get(ident)
        n_start = len(entry["started"]) if entry else 0
        if n_start > 1:
            problems.append(f"{ident}: started {n_start} times in the ledger (replay)")
            continue
        if entry and not entry["started"] and entry["final"]:
            problems.append(f"{ident}: ledger outcome without a start")
            continue
        if rec is None:
            if n_start == 1:
                if allow_incomplete:
                    orphans.append(ident)
                else:
                    problems.append(f"{ident}: started in the ledger but no answers row")
            continue
        if n_start == 0:
            problems.append(f"{ident}: answers row without a ledger start")
            continue
        status, key, segment, _ = ledger_status(entry)
        if rec["status"] != status:
            problems.append(f"{ident}: answers status {rec['status']} but the ledger implies {status}")
        if rec.get("key") != key or rec.get("ledger") != segment:
            problems.append(f"{ident}: answers row does not name its ledger call")
        if rec["status"] in VALID and rec.get("answer") != rec["status"]:
            problems.append(f"{ident}: answer field disagrees with status")
    missing = [i for i in sched if i not in records and i not in orphans]
    if missing and not allow_incomplete:
        problems.append(f"incomplete: {len(missing)} of {len(sched)} scheduled samples have no record "
                        f"(first: {missing[:3]})")
    if problems:
        raise DataError("; ".join(problems[:20]) + (f" (+{len(problems) - 20} more)" if len(problems) > 20 else ""))
    return records, orphans


# ------------------------------------------------------------------------------------------------
# Statistics
# ------------------------------------------------------------------------------------------------

def item_stats(records, items, gt, k=K):
    out = {}
    for iid in items:
        st = [records[(iid, s)]["status"] for s in range(k) if (iid, s) in records]
        model = [x for x in st if x in MODEL_OUTCOMES]
        valid = [x for x in model if x in VALID]
        ref = gt[iid]
        wrong_valid = sum(x != ref for x in valid)
        other = "NO" if ref == "YES" else "YES"
        out[iid] = dict(
            n_model=len(model), n_valid=len(valid), n_invalid=len(model) - len(valid),
            n_endpoint_error=st.count("ENDPOINT_ERROR"),
            # primary: invalid counts as an error
            error=(wrong_valid + len(model) - len(valid)) / len(model) if model else None,
            error_valid_only=wrong_valid / len(valid) if valid else None,
            # directional: the numerator needs an actual YES/NO opposite to the reference
            wrong_direction=valid.count(other) / len(model) if model else None,
            wrong_direction_valid_only=valid.count(other) / len(valid) if valid else None)
    return out


def mean_over(stats, ids, field, missing_as=0.0):
    """Mean of an item statistic; items without data count as `missing_as`, or are skipped if None."""
    vals = [stats[i][field] for i in ids]
    vals = [v for v in vals if v is not None] if missing_as is None else [missing_as if v is None else v for v in vals]
    return sum(vals) / len(vals) if vals else None


def cluster_boot(values_by_cluster, n=BOOT_N, seed=BOOT_SEED):
    """Percentile 95% CI of the item-weighted mean, resampling clusters (artefacts)."""
    rnd = random.Random(seed)
    cl = sorted(values_by_cluster)
    stats = []
    for _ in range(n):
        xs = [e for c in (rnd.choice(cl) for _ in cl) for e in values_by_cluster[c]]
        stats.append(sum(xs) / len(xs))
    stats.sort()
    return stats[int(0.025 * n)], stats[int(0.975 * n) - 1]


def _betacf(a, b, x):
    """Continued fraction for the regularized incomplete beta (Lentz)."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        for aa in (m * (b - m) * x / ((qam + m2) * (a + m2)),
                   -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))):
            d = 1 + aa * d
            d = 1 / (d if abs(d) > tiny else tiny)
            c = 1 + aa / c
            c = c if abs(c) > tiny else tiny
            h *= d * c
        if abs(d * c - 1) < 1e-14:
            break
    return h


def _betai(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def t_cdf(t, df):
    p = 0.5 * _betai(df / 2, 0.5, df / (df + t * t))
    return 1 - p if t > 0 else p


def t_quantile(q, df):
    lo, hi = -100.0, 100.0
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if t_cdf(mid, df) < q else (lo, mid)
    return (lo + hi) / 2


def t_interval(means):
    """Mean of the artefact means and its 95% Student-t interval."""
    n = len(means)
    m = sum(means) / n
    if n < 2:
        return m, [None, None]
    sd = math.sqrt(sum((x - m) ** 2 for x in means) / (n - 1))
    h = t_quantile(0.975, n - 1) * sd / math.sqrt(n)
    return m, [m - h, m + h]


def r4(x):
    return None if x is None else round(x, 4)


def summary(stats, ids, field="error"):
    ids = list(ids)
    if not ids:
        return None
    return dict(items=len(ids), mean=r4(mean_over(stats, ids, field, None)),
                items_without_data=sorted(i for i in ids if stats[i][field] is None))


def analyse_arm(records, items, gt, arm, n_scheduled, k=K):
    stats = item_stats(records, items, gt, k)
    counts = defaultdict(int)
    for r in records.values():
        counts[r["status"]] += 1
    primary_ids = [i for i in items if "edge" not in items[i]["tags"]]
    edge_ids = [i for i in items if "edge" in items[i]["tags"]]
    cluster = {i: items[i]["cluster"] for i in items}
    no_outcome = sorted(i for i in items if stats[i]["n_model"] == 0)

    def est(ids, field="error"):
        return mean_over(stats, ids, field, 0.0)

    by_cluster = defaultdict(list)
    for i in primary_ids:
        by_cluster[cluster[i]].append(stats[i]["error"] or 0.0)
    point = est(primary_ids)
    lo, hi = cluster_boot(by_cluster)
    art_means = [sum(v) / len(v) for _, v in sorted(by_cluster.items())]
    t_mean, t_ci = t_interval(art_means)
    no_edits = [i for i in primary_ids if items[i]["variant"] != "planted-edit"]
    err_artefacts = sorted(c for c, v in by_cluster.items() if any(x > 0 for x in v))
    loao = {c: est([i for i in primary_ids if cluster[i] != c]) for c in sorted(by_cluster)}
    loao_min_c = min(loao, key=loao.get)
    total_err = sum(sum(v) for v in by_cluster.values())
    top_share = max(sum(v) for v in by_cluster.values()) / total_err if total_err else None
    valid_only = mean_over(stats, primary_ids, "error_valid_only", 0.0)
    robust = dict(
        planted_edits_excluded=dict(items=len(no_edits), error=r4(est(no_edits)), holds=est(no_edits) >= GATE),
        artefacts_with_errors=dict(n=len(err_artefacts), artefacts=err_artefacts,
                                   holds=len(err_artefacts) >= MIN_ERROR_ARTEFACTS),
        leave_one_artefact_out=dict(min=r4(loao[loao_min_c]), min_when_dropping=loao_min_c,
                                    holds=loao[loao_min_c] >= GATE,
                                    all={c: r4(v) for c, v in loao.items()}))

    def direction(dirn, ref):
        ids = [i for i in primary_ids if items[i]["direction"] == dirn and gt[i] == ref]
        return dict(items=len(ids), rate=r4(mean_over(stats, ids, "wrong_direction", None)),
                    rate_invalid_excluded=r4(mean_over(stats, ids, "wrong_direction_valid_only", None)),
                    items_without_data=sorted(i for i in ids if stats[i]["n_model"] == 0))

    def item_row(i):
        return dict(reference=gt[i], direction=items[i]["direction"],
                    **{k_: r4(v) if isinstance(v, float) else v for k_, v in stats[i].items()})

    out = dict(
        arm=arm, scheduled_samples=n_scheduled, sample_status=dict(sorted(counts.items())),
        invalid_samples=counts["UNPARSED"] + counts["TRUNCATED"],
        endpoint_errors=dict(n=counts["ENDPOINT_ERROR"], stop_threshold=max_endpoint_errors(n_scheduled)),
        items_without_model_outcome=no_outcome,
        primary=dict(
            definition="mean item error over the non-edge items; INVALID counts as error; an item without "
                       "a model outcome counts as 0; clustered by artefact",
            items=len(primary_ids), artefacts=len(by_cluster), error=r4(point),
            ci95_cluster_bootstrap=[r4(lo), r4(hi)],
            artefact_mean_t_interval=dict(mean_of_artefact_means=r4(t_mean), ci95=[r4(x) for x in t_ci]),
            error_mass_share_of_top_artefact=r4(top_share),
            invalid_excluded_sensitivity=r4(valid_only)),
        robustness=robust,
        key_secondary_false_approval_restriction_NO=direction("restriction", "NO"),
        direction_split=dict(
            restriction_NO_false_approval=direction("restriction", "NO"),
            guarantee_NO_wrong_yes=direction("guarantee", "NO"),
            restriction_YES_wrong_no=direction("restriction", "YES"),
            guarantee_YES_wrong_no=direction("guarantee", "YES")),
        original=summary(stats, [i for i in primary_ids if items[i]["variant"] == "original"]),
        planted_edit=summary(stats, [i for i in primary_ids if items[i]["variant"] == "planted-edit"]),
        cedar=summary(stats, [i for i in primary_ids if items[i]["family"] == "cedar"]),
        k8s=summary(stats, [i for i in primary_ids if items[i]["family"] == "k8s"]),
        by_ve_coverage={c: summary(stats, [i for i in primary_ids if items[i]["ve_coverage"]["category"] == c])
                        for c in sorted({items[i]["ve_coverage"]["category"] for i in primary_ids})},
        edge_items_reported_separately={i: item_row(i) for i in edge_ids},
        all_items_including_edge=r4(est(list(items))),
        per_item={i: item_row(i) for i in items})
    if arm == "high":
        out["gate"] = verdict(point, lo, robust, valid_only)
    else:
        out["gate"] = "not applicable: secondary configuration (descriptive); a pass at low effort alone does not count"
    return out


def verdict(point, lo, robust, valid_only):
    failed = [k for k, v in robust.items() if not v["holds"]]
    if point < GATE:
        v = "FAIL (closes this sample only)"
    elif failed:
        v = "FAIL: the point estimate reaches the gate but the preregistered robustness fails (" + ", ".join(failed) + ")"
    elif lo < GATE:
        v = "WEAK PASS (cluster-bootstrap lower bound < 0.15: replicate on new artefacts first)"
    else:
        v = "PASS"
    if v.startswith(("PASS", "WEAK")) and valid_only < GATE:
        v += "; note: below the gate when INVALID samples are excluded"
    return v


# ------------------------------------------------------------------------------------------------

def load_inputs():
    items = {i["id"]: i for i in json.loads((HERE / "items.json").read_text())}
    gt = {r["id"]: r["answer"] for r in json.loads((HERE / "ground_truth.json").read_text())["items"]}
    prompts = {r["id"]: r["sha256"] for r in map(json.loads, (HERE / "prompts.jsonl").read_text().splitlines())}
    return items, gt, prompts


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    frozen_path = HERE / "FREEZE.json"
    if not frozen_path.exists():
        sys.exit("FREEZE.json missing: nothing frozen, nothing to analyse")
    frozen = json.loads(frozen_path.read_text())
    for name in ("items.json", "ground_truth.json", "prompts.jsonl", "analyze.py"):
        if hashlib.sha256((HERE / name).read_bytes()).hexdigest() != frozen["files"][f"experiments/D-gate/{name}"]:
            sys.exit(f"{name} changed since the freeze")
    items, gt, prompts = load_inputs()
    assert set(items) == set(gt) == set(prompts) and all(gt[i] in ("YES", "NO") for i in gt)
    report = {}
    for arm in argv or ["high"]:
        answers, ledgers, stop = load_arm(HERE / "runs" / arm)
        if stop is not None:
            report[arm] = dict(gate="NO VERDICT: the run stopped under a stop rule", stop=stop)
            continue
        try:
            records, _ = reconcile(answers, ledgers, prompts, frozen, arm)
        except DataError as exc:
            print(json.dumps({arm: f"REFUSED: {exc}"}, indent=1))
            sys.exit(2)
        n = len(schedule(list(prompts), frozen["k"]))
        errs = sum(r["status"] == "ENDPOINT_ERROR" for r in records.values())
        if errs > max_endpoint_errors(n):
            report[arm] = dict(gate="NO VERDICT: endpoint errors exceed the stop threshold", endpoint_errors=errs)
            continue
        report[arm] = analyse_arm(records, items, gt, arm, n, frozen["k"])
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
