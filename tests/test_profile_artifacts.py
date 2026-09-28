"""Keep published English measurements in sync with their raw samples."""

import json
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from bench.timing import DEFAULT_REPEATS, DEFAULT_WARMUPS, stats


BENCH = Path(__file__).resolve().parents[1] / "bench"


def _data(phase):
    return json.loads((BENCH / f"PROFILE-ENGLISH-{phase}.json").read_text())


def _one_decimal(value):
    return f"{Decimal(str(value)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP):,.1f}"


def _sampled_paths(data):
    for row in data["documents"].values():
        yield row, "wall_ms", "load", "stats", DEFAULT_REPEATS
    for row in data["sentences"]:
        for name in ("parse", "natural", "combined"):
            yield row, f"{name}_ms", f"{name}_load", f"{name}_stats", DEFAULT_REPEATS
    for row in data["raw_source"].values():
        for sentence in row["sentences"]:
            yield sentence, "wall_ms", "load", "stats", DEFAULT_REPEATS
    for name, row in data["editor"].items():
        if name in ("scope", "reference"):
            yield row, "parse_ms", "parse_load", "parse_stats", DEFAULT_REPEATS
            yield row, "catalogue_ms", "load", "stats", data["sampling"]["editor_catalogue_repeats"]
        else:
            yield row, "wall_ms", "load", "stats", DEFAULT_REPEATS


def test_after_metadata_and_every_sample_agree():
    data = _data("AFTER")
    assert data["sampling"] == {
        "default_repeats": DEFAULT_REPEATS,
        "editor_catalogue_repeats": 20,
        "warmups": DEFAULT_WARMUPS,
    }
    assert "20 samples" in data["method"]
    assert "repeats" not in data  # A single count would misdescribe the catalogues.
    for row, samples_key, load_key, stats_key, repeats in _sampled_paths(data):
        samples = row[samples_key]
        assert len(samples) == len(row[load_key]) == repeats
        assert row[stats_key] == stats(samples)


def test_published_comparison_matches_raw_json():
    before, after = _data("BEFORE"), _data("AFTER")
    report = (BENCH / "PROFILE-ENGLISH-AFTER.md").read_text()
    assert "five sequential warm-process repeats per case, except editor catalogues, which ran 20" in report
    assert not re.search(r"\b[\d,]+ passed\b", report)  # Results change after new commits.
    paths = {
        "BlueDot document check": lambda data: data["documents"]["bluedot"]["stats"],
        "Latest Claude document check": lambda data: data["documents"]["claude"]["stats"],
        "Latest UDHR document check": lambda data: data["documents"]["udhr"]["stats"],
        "Editor scope catalogue": lambda data: data["editor"]["scope"]["stats"],
        "Editor reference catalogue": lambda data: data["editor"]["reference"]["stats"],
        "Editor checked wording": lambda data: data["editor"]["validation"]["stats"],
        "Editor recovery classify": lambda data: data["editor"]["classify"]["stats"],
        "Longest admitted sentence (150 tokens), parse plus natural display":
            lambda data: max(data["sentences"], key=lambda row: row["tokens"])["combined_stats"],
    }
    for label, select in paths.items():
        expected = "| " + label
        lines = [line for line in report.splitlines() if line.startswith(expected + " |")]
        assert len(lines) == 1
        values = re.findall(r"[\d,]+\.\d", lines[0])
        assert values == [
            _one_decimal(select(data)[metric])
            for data in (before, after) for metric in ("p50_ms", "p95_ms")
        ]


def test_profile_report_links_resolve():
    for name in ("PROFILE-ENGLISH-BEFORE.md", "PROFILE-ENGLISH-AFTER.md"):
        report = (BENCH / name).read_text()
        for target in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", report):
            if ":" not in target:
                assert (BENCH / target).is_file(), (name, target)
