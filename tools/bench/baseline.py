"""Compare CPU-time measurements with stored baselines (tools/bench/baselines.json)."""
from __future__ import annotations


def allowed(baseline: float, stored: dict) -> float:
    """The most CPU seconds a measurement with this baseline may take."""
    return baseline * (1 + stored["tolerance"]) + stored["slack_seconds"]


def over(measurements: dict[str, float], stored: dict) -> list[str]:
    """One line per measurement that has no baseline or exceeds what its baseline allows."""
    lines = []
    for key, seconds in measurements.items():
        baseline = stored["baselines"].get(key)
        if baseline is None:
            lines.append(f"{key}: no baseline (run with --update-baselines and commit it)")
        elif seconds > allowed(baseline, stored):
            lines.append(f"{key}: {seconds} CPU s, baseline {baseline}, allowed {allowed(baseline, stored):.3f}")
    return lines


def updated(stored: dict, measurements: dict[str, float]) -> dict:
    return {**stored, "baselines": dict(sorted({**stored["baselines"], **measurements}.items()))}
