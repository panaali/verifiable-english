"""Deterministic file shards and fail-closed assembly of full gate records."""
from __future__ import annotations

import datetime
import hashlib
import json
import os
from pathlib import Path

from tools import gate_collection, test_schedule


def _valid_expiry(value: object) -> bool:
    if type(value) is not str:
        return False
    try:
        return datetime.date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _valid_evidence(value: object) -> bool:
    return (type(value) is str and bool(value.strip()) and
            not Path(value).is_absolute() and ".." not in Path(value).parts)


def plan(ids: list[str], estimates: test_schedule.Estimates, count: int,
         *, selected: list[str] | None = None) -> dict:
    if count < 1 or not ids or len(ids) != len(set(ids)):
        raise ValueError("shard plan needs a nonempty, unique collection and positive N")
    selected = ids if selected is None else selected
    if not selected or len(selected) != len(set(selected)) or not set(selected) <= set(ids):
        raise ValueError("invalid selected collection")
    files: dict[str, list[str]] = {}
    for nodeid in selected:
        if not isinstance(nodeid, str) or "::" not in nodeid:
            raise ValueError(f"invalid collected test ID: {nodeid!r}")
        files.setdefault(nodeid.split("::", 1)[0], []).append(nodeid)
    weights = {file: sum(estimates.durations.get(node, estimates.unrecorded) for node in nodes)
               for file, nodes in files.items()}
    loads = [0.0] * count
    assignments = {}
    for file in sorted(files, key=lambda name: (-weights[name], name)):
        shard = min(range(count), key=lambda index: (loads[index], index))
        assignments[file] = shard + 1
        loads[shard] += weights[file]
    body = {"n": count, "collected": gate_collection.encode_ids(ids),
            "selected": gate_collection.encode_ids(selected),
            "assignments": assignments, "weights": weights}
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {**body, "digest": digest, "seconds": [round(value, 1) for value in loads]}


def share(plan_record: dict, number: int) -> list[str]:
    ids = gate_collection.decode_ids(plan_record["selected"])
    if ids is None or type(number) is not int or not 1 <= number <= plan_record["n"]:
        raise ValueError("invalid shard plan or number")
    return [node for node in ids if plan_record["assignments"][node.split("::", 1)[0]] == number]


def validate_plan(value: dict) -> list[str]:
    if not isinstance(value, dict) or type(value.get("n")) is not int or value["n"] < 1:
        raise ValueError("invalid shard plan")
    ids = gate_collection.decode_ids(value.get("collected"))
    selected = gate_collection.decode_ids(value.get("selected"))
    if not ids or not selected or len(ids) != len(set(ids)) or len(selected) != len(set(selected)) \
            or not set(selected) <= set(ids):
        raise ValueError("invalid shard plan collection")
    files = {node.split("::", 1)[0] for node in selected if isinstance(node, str) and "::" in node}
    assignments = value.get("assignments")
    weights = value.get("weights")
    if len(files) != len({node.split("::", 1)[0] for node in selected}) or not isinstance(assignments, dict) \
            or set(assignments) != files or not isinstance(weights, dict) or set(weights) != files \
            or any(type(index) is not int or not 1 <= index <= value["n"] for index in assignments.values()) \
            or any(not test_schedule.seconds_value(weight) for weight in weights.values()):
        raise ValueError("invalid shard plan assignments")
    body = {key: value[key] for key in ("n", "collected", "selected", "assignments", "weights")}
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if value.get("digest") != digest:
        raise ValueError("shard plan digest differs from contents")
    # Recompute the greedy assignment, including tie breaks, from the recorded weights.
    loads = [0.0] * value["n"]
    for file in sorted(files, key=lambda name: (-weights[name], name)):
        index = min(range(value["n"]), key=lambda i: (loads[i], i))
        if assignments[file] != index + 1:
            raise ValueError("shard plan is not greedy longest first")
        loads[index] += weights[file]
    return ids


def merge_records(records: list[dict]) -> dict:
    """Assemble only complete, matching shard runs. Refusals are full failed records."""
    from tools import gate  # keep the unsharded gate's record helpers authoritative

    if records and all(isinstance(row, dict) and isinstance(row.get("shard"), dict) for row in records):
        records = sorted(records, key=lambda row: (type(row["shard"].get("k")) is not int,
                                                str(row["shard"].get("k"))))
    first = records[0] if records and isinstance(records[0], dict) else {}
    merged = {key: first.get(key) for key in ("schema_version", "commit_sha", "tree_sha", "dirty", "runner",
                                             "toolchains", "environment", "trust", "durations_source", "collection")}
    merged.update(mode="full", status="failed", stages=list(gate.REQUIRED_STAGES), counts={}, skips=[], failures=[])

    def refuse(reason: str) -> dict:
        merged["failures"] = [{"stage": "shards", "reason": reason}]
        merged["stages"] = []
        return merged

    try:
        if not records or not isinstance(first.get("shard"), dict):
            return refuse("no shard records")
        metadata = first["shard"]
        shard_plan = metadata["plan"]
        ids = validate_plan(shard_plan)
        n = shard_plan["n"]
        # A missing identity must not agree with the same missing value in
        # every shard. These are the source and runner identities of the run.
        if type(first.get("schema_version")) is not int or first["schema_version"] != 1 or \
                any(type(first.get(key)) is not str or len(first[key]) != 40 or
                    any(char not in "0123456789abcdef" for char in first[key])
                    for key in ("commit_sha", "tree_sha")) or \
                not isinstance(first.get("runner"), dict) or \
                any(type(first["runner"].get(key)) is not str or not first["runner"][key].strip()
                    for key in ("system", "machine")) or \
                not isinstance(first.get("toolchains"), dict) or not first["toolchains"] or \
                not isinstance(first.get("environment"), dict):
            return refuse("missing or malformed shard identity")
        if len(records) != n:
            return refuse(f"missing shard record: expected {n}, got {len(records)}")
        by_number = {}
        for record in records:
            if not isinstance(record, dict) or not isinstance(record.get("shard"), dict):
                return refuse("invalid shard record")
            row = record["shard"]
            number = row.get("k")
            if type(number) is not int or not 1 <= number <= n or number in by_number:
                return refuse(f"missing or duplicate shard number: {number!r}")
            if record.get("schema_version") != first.get("schema_version") or record.get("mode") != "shard":
                return refuse(f"shard {number}: schema or mode differs")
            if type(row.get("n")) is not int or row["n"] != n or \
                    row.get("digest") != shard_plan["digest"] or row.get("plan") != shard_plan:
                return refuse(f"shard {number}: N or plan digest differs")
            if any(record.get(key) != first.get(key) for key in ("commit_sha", "tree_sha")):
                return refuse(f"shard {number}: commit or tree differs")
            if not isinstance(record.get("environment"), dict):
                return refuse(f"shard {number}: environment missing")
            runner = record.get("runner", {})
            common_runner = first.get("runner", {})
            if not isinstance(runner, dict) or not isinstance(common_runner, dict) or \
                    any(runner.get(key) != common_runner.get(key) for key in ("system", "machine")):
                return refuse(f"shard {number}: runner platform differs")
            if not isinstance(record.get("toolchains"), dict) or \
                    {key: value for key, value in record["toolchains"].items() if key != "paths"} != \
                    {key: value for key, value in first["toolchains"].items() if key != "paths"}:
                return refuse(f"shard {number}: toolchains differ")
            if record.get("dirty") is not False:
                return refuse(f"shard {number}: dirty source")
            if record.get("status") not in ("shard-passed", "failed"):
                return refuse(f"shard {number}: invalid status {record.get('status')!r}")
            if record.get("stages") != (["toolchains", "lean_build", "lean_audit", "rust_build",
                                          "cargo_test", "pytest"] if number == 1 else
                                         ["toolchains", "lean_build", "pytest"]):
                return refuse(f"shard {number}: incomplete stages")
            if row.get("collected") != shard_plan["collected"]:
                return refuse(f"shard {number}: collection differs")
            if not isinstance(record.get("collection"), dict) or \
                    gate_collection.decode_ids(record["collection"].get("collected_zlib")) != ids:
                return refuse(f"shard {number}: full collection differs")
            ran = row.get("ran")
            if not isinstance(ran, list) or not ran or ran != share(shard_plan, number):
                return refuse(f"shard {number}: ran IDs differ from plan or no suite ran")
            counts = record.get("counts", {})
            if not isinstance(counts, dict) or any(type(counts.get(key)) is not int or counts[key] < 0
                                                    for key in ("collected", "selected", "passed", "skipped",
                                                                "failed", "deselected")) or \
                    counts["collected"] != len(ran) or \
                    counts["selected"] != len(ran) or \
                    sum(counts[key] for key in ("passed", "skipped", "failed")) != len(ran) or \
                    counts["deselected"] != (len(ids) - len(gate_collection.decode_ids(shard_plan["selected"]))
                                             if number == 1 else 0):
                return refuse(f"shard {number}: incomplete test events")
            if number == 1 and (type(counts.get("rust_passed")) is not int or
                                counts["rust_passed"] <= 0 or type(counts.get("rust_ignored")) is not int or
                                counts["rust_ignored"] != 0):
                return refuse("shard 1: incomplete native Rust test events")
            skips = record.get("skips")
            if not isinstance(skips, list) or len(skips) != counts["skipped"] + counts["deselected"] or \
                    any(not isinstance(skip, dict) or type(skip.get("nodeid")) is not str or
                        skip["nodeid"] not in ids or type(skip.get("allowed")) is not bool or
                        type(skip.get("deselected", False)) is not bool
                        for skip in skips) or len({skip["nodeid"] for skip in skips}) != len(skips) or \
                    {skip["nodeid"] for skip in skips if not skip.get("deselected")} - set(ran) or \
                    sum(skip.get("deselected", False) for skip in skips) != counts["deselected"] or \
                    (record.get("status") == "shard-passed" and any(skip["allowed"] is not True for skip in skips)):
                return refuse(f"shard {number}: incomplete skip events")
            failures = record.get("failures")
            if not isinstance(failures, list) or any(not isinstance(failure, dict) or
                                                    type(failure.get("stage")) is not str or
                                                    type(failure.get("reason")) is not str for failure in failures) or \
                    len([failure for failure in failures if failure["stage"] == "pytest"]) != counts["failed"]:
                return refuse(f"shard {number}: incomplete failure events")
            if record.get("status") == "shard-passed" and record.get("failures"):
                return refuse(f"shard {number}: passing status with failures")
            if record.get("status") == "failed" and not record.get("failures"):
                return refuse(f"shard {number}: failed status without a reason")
            quarantine = record.get("quarantine")
            if not isinstance(quarantine, dict) or not isinstance(first.get("quarantine"), dict) or \
                    type(quarantine.get("enabled")) is not bool or \
                    not isinstance(quarantine.get("active"), list) or \
                    not isinstance(quarantine.get("expired"), list) or \
                    not isinstance(quarantine.get("retried"), dict) or \
                    any(type(node) is not str for node in quarantine["active"] + quarantine["expired"]) or \
                    len(quarantine["active"]) != len(set(quarantine["active"])) or \
                    (not quarantine["enabled"] and
                     (quarantine["active"] or quarantine["expired"] or quarantine["retried"] or
                      "day" in quarantine)) or \
                    (quarantine["enabled"] and type(quarantine.get("day")) is not str) or \
                    any(quarantine.get(key) != first["quarantine"].get(key)
                   for key in ("enabled", "day", "active", "expired")):
                return refuse(f"shard {number}: quarantine policy differs")
            retries = quarantine["retried"]
            if any(type(node) is not str or node not in ran or not isinstance(retry, dict) or
                   node not in quarantine["active"] or
                   retry.get("suite") != "failed" or retry.get("alone") not in
                   ("passed", "failed", "skipped", "no result") or
                   type(retry.get("owner")) is not str or not retry["owner"].strip() or
                   not _valid_expiry(retry.get("expires")) or
                   not _valid_evidence(retry.get("evidence")) or
                   (record["status"] == "shard-passed" and retry["alone"] != "passed")
                   for node, retry in retries.items()):
                return refuse(f"shard {number}: contradictory quarantine retry")
            by_number[number] = record
        if set(by_number) != set(range(1, n + 1)):
            return refuse("missing shard record")
        if gate_collection.decode_ids(first.get("collection", {}).get("collected_zlib")) != ids:
            return refuse("shard 1 full collection differs from plan")
        if any(by_number[i]["shard"]["collected"] != shard_plan["collected"] for i in by_number):
            return refuse("collections differ")
        merged["counts"] = dict(first["counts"])
        for key in ("passed", "skipped", "failed", "selected"):
            merged["counts"][key] = sum(by_number[i]["counts"].get(key, 0) for i in range(1, n + 1))
        merged["counts"]["collected"] = len(ids)
        merged["counts"]["deselected"] = first["counts"].get("deselected", 0)
        skips = [skip for i in range(1, n + 1) for skip in by_number[i]["skips"]]
        order = {node: index for index, node in enumerate(ids)}
        merged["skips"] = sorted(skips, key=lambda skip: (bool(skip.get("deselected")),
                                                          order.get(skip.get("nodeid"), len(ids))))
        merged["failures"] = [failure for i in range(1, n + 1) for failure in by_number[i]["failures"]]
        seconds = {}
        for i in range(1, n + 1):
            part = by_number[i].get("pytest_seconds")
            if not isinstance(part, dict) or set(part) != set(by_number[i]["shard"]["ran"]) or \
                    any(not test_schedule.seconds_value(value) for value in part.values()):
                return refuse(f"shard {i}: incomplete durations")
            seconds.update(part)
        merged["durations"] = test_schedule.record_field(seconds)
        merged["quarantine"] = dict(first.get("quarantine", {}))
        merged["quarantine"]["retried"] = {node: row for i in range(1, n + 1)
                                            for node, row in by_number[i].get("quarantine", {}).get("retried", {}).items()}
        merged["shards"] = {"n": n, "plan_digest": shard_plan["digest"],
                            "runs": [{"k": i, "runner": by_number[i]["runner"],
                                      "seconds": by_number[i]["shard"].get("seconds")}
                                     for i in range(1, n + 1)]}
        merged["status"] = "passed" if not merged["failures"] and all(
            by_number[i]["status"] == "shard-passed" for i in range(1, n + 1)) else "failed"
        return merged
    except (KeyError, TypeError, ValueError) as exc:
        return refuse(f"malformed shard record: {exc}")


def merge_files(paths: list[Path], output: Path) -> int:
    from tools import gate
    try:
        records = [json.loads(path.read_text()) for path in paths]
    except (OSError, ValueError) as exc:
        records = []
        reason = str(exc)
    else:
        reason = ""
    merged = merge_records(records)
    if reason:
        merged["failures"] = [{"stage": "shards", "reason": f"cannot read shard record: {reason}"}]
        merged["status"] = "failed"
    # As with a normal full gate, a complete local gate can serve later collection and duration readers via its note.
    if merged.get("stages") == list(gate.REQUIRED_STAGES):
        try:
            commit = gate_collection.rev("HEAD")
            tree = gate_collection.rev("HEAD^{tree}")
            if (commit, tree) == (merged.get("commit_sha"), merged.get("tree_sha")):
                ids = gate_collection.decode_ids(merged["collection"]["collected_zlib"])
                merged["collection"]["head_record"] = "written"
                merged["collection"]["head_record"] = gate.record_collection(commit, ids, dict(os.environ),
                                                                                result=merged)
        except (OSError, RuntimeError, KeyError, TypeError):
            pass  # The JSON is the gate result; a note is the same optional shortcut as in the unsharded gate.
    gate.write_result(output, merged)
    return 0 if merged["status"] == "passed" else 1
