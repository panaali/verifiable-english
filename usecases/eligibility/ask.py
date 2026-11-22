"""Ask the Winter Fuel Payment checker about one applicant (release B demo, checklist item 5).

One profile in, the plain-English answer out: a four-line summary (entitled, the payment, whether
HMRC takes it back, the amount kept), then the printout of explain.py (each answer with the
clauses of SI 2025/969 it uses, quoted, the assumptions it rests on, and the Lean check).

The profile is a small JSON file in the cases.json form, or flags, or both (flags override the
file's applicant fields):

    uv run python usecases/eligibility/ask.py usecases/eligibility/demo/b15.json
    uv run python usecases/eligibility/ask.py --birth 1955-03-14 --scot-ni-from 2026-09-20 --ew-from 2026-09-22

A profile file holds {"applicant": {...}, "housemate": {...} or null}; person fields it leaves out
take the cases.json defaults (resident in England or Wales since 1990, state pension only,
income GBP 20,000, paid without a claim). An unknown field name, a date not written YYYY-MM-DD or
an amount not written as GBP digits is refused before anything runs. The file's "key" (a
hand-derived answer, as in cases.json) is never read.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import explain as X  # noqa: E402
import translation as T  # noqa: E402

# The person fields the translation accepts (translation.check_fields).
PERSON_FIELDS = T.PERSON_FIELDS | set(T.UNREAD_FIELDS)
HOUSEMATE_FIELDS = PERSON_FIELDS | T.HOUSEMATE_FIELDS
PROFILE_FIELDS = {"applicant", "housemate", "id", "summary", "key"}
DATE_FIELDS = {"birth", "ew_from", "ew_last_day", "scot_ni_from"}
NESTED_DATES = {"care": {"from", "until"}, "hospital": {"admitted", "discharged"},
                "custody": {"from", "release"}, "claim": {"claimed_on"},
                "shared_home": {"from", "until"}, "partnership": {"from", "until"}}
MONEY = re.compile(r"^[0-9]+(\.[0-9]{2})?$")
SUMMARY = (("Q1", "Entitled"), ("Q2", "Payment"), ("Q3", "Taken back by HMRC"), ("Q4", "Kept"))


class ProfileError(ValueError):
    """The profile cannot be read: an unknown field, a bad date or a bad amount."""


def _check_date(where, value):
    if value is None:
        return
    try:
        if not isinstance(value, str) or datetime.date.fromisoformat(value).isoformat() != value:
            raise ValueError
    except ValueError:
        raise ProfileError(f"{where}: {value!r} is not a date written YYYY-MM-DD") from None


def _check_person(role, person, allowed):
    if person is None:
        return
    if not isinstance(person, dict):
        raise ProfileError(f"{role}: expected an object of person fields")
    unknown = sorted(set(person) - allowed)
    if unknown:
        raise ProfileError(f"{role}: unknown field(s) {', '.join(unknown)}; known: {', '.join(sorted(allowed))}")
    if "birth" not in person:
        raise ProfileError(f"{role}: a birth date ('birth') is required")
    for name in DATE_FIELDS & set(person):
        _check_date(f"{role}.{name}", person[name])
    for name, keys in NESTED_DATES.items():
        part = person.get(name)
        if part is None:
            continue
        if not isinstance(part, dict):
            raise ProfileError(f"{role}.{name}: expected an object")
        for key in keys & set(part):
            _check_date(f"{role}.{name}.{key}", part[key])
    if "income" in person and not (isinstance(person["income"], str) and MONEY.match(person["income"])):
        raise ProfileError(f"{role}.income: {person['income']!r} is not an amount in GBP written like \"20000.00\"")
    if "benefits" in person and not (isinstance(person["benefits"], list)
                                     and all(isinstance(b, str) for b in person["benefits"])):
        raise ProfileError(f"{role}.benefits: expected a list of benefit names")
    try:  # the translation's own field checks (records, benefit names, periods), on the person with defaults
        T.check_fields(role, T._person(person, T.load_cases()["defaults"]))
    except ValueError as err:
        raise ProfileError(f"{err}; benefit names: {', '.join(T.BENEFITS)}") from None


def check_profile(profile):
    """Refuse a profile with an unknown field, a bad date or a bad amount. Returns the profile."""
    if not isinstance(profile, dict):
        raise ProfileError("a profile is a JSON object with an 'applicant'")
    unknown = sorted(set(profile) - PROFILE_FIELDS)
    if unknown:
        raise ProfileError(f"unknown profile field(s) {', '.join(unknown)}; known: applicant, housemate")
    if "applicant" not in profile:
        raise ProfileError("a profile needs an 'applicant'")
    _check_person("applicant", profile["applicant"], PERSON_FIELDS)
    _check_person("housemate", profile.get("housemate"), HOUSEMATE_FIELDS)
    return profile


def build_profile(path=None, *, birth=None, ew_from=None, ew_last_day=None, scot_ni_from=None,
                  benefits=None, income=None):
    """The profile from a JSON file (optional) with the given applicant fields set over it.
    The file's `key`, if any, is dropped here."""
    profile = {"applicant": {}, "housemate": None}
    if path is not None:
        try:
            profile = json.loads(Path(path).read_text(encoding="utf-8"))
        except json.JSONDecodeError as err:
            raise ProfileError(f"{path}: not valid JSON ({err})") from None
        if not isinstance(profile, dict):
            raise ProfileError(f"{path}: a profile is a JSON object with an 'applicant'")
    profile = {k: v for k, v in profile.items() if k != "key"}
    applicant = dict(profile.get("applicant") or {})
    for name, value in (("birth", birth), ("ew_from", ew_from), ("ew_last_day", ew_last_day),
                        ("scot_ni_from", scot_ni_from), ("benefits", benefits), ("income", income)):
        if value is not None:
            applicant[name] = value
    profile["applicant"] = applicant
    profile.setdefault("housemate", None)
    return check_profile(profile)


def summary(data):
    """The four summary lines: one per question, from explain.explanation's data."""
    by_q = {e["question"]: e for e in data["answers"]}
    lines = []
    for question, label in SUMMARY:
        e = by_q[question]
        value = "not applicable (not entitled)" if e["answer"] == "N/A" else e["display"]
        lines.append(f"{label}: {value}")
    return "\n".join(lines) + "\n"


def ask(profile, *, lean=True):
    """The demo printout for one profile dict: the summary, a blank line, then explain's printout."""
    data = X.explanation(check_profile(profile), lean=lean)
    return summary(data) + "\n" + X.render(data)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("profile", nargs="?", help="a JSON file holding one profile (cases.json form)")
    parser.add_argument("--birth", help="the applicant's birth date, YYYY-MM-DD")
    parser.add_argument("--ew-from", help="first day ordinarily resident in England or Wales, YYYY-MM-DD")
    parser.add_argument("--ew-last-day", help="last day ordinarily resident in England or Wales, YYYY-MM-DD")
    parser.add_argument("--scot-ni-from", help="first day ordinarily resident in Scotland or Northern Ireland")
    parser.add_argument("--benefit", action="append", dest="benefits", metavar="NAME",
                        help="a benefit paid to the applicant for the qualifying week (repeat for each; "
                             "e.g. state_pension, pension_credit); replaces the default list")
    parser.add_argument("--income", help="the applicant's total income in GBP, e.g. 20000.00")
    parser.add_argument("--no-lean", action="store_true", help="skip the Lean check of the certificates")
    args = parser.parse_args(argv)
    if args.profile is None and args.birth is None:
        parser.error("give a profile file, or at least --birth")
    try:
        profile = build_profile(args.profile, birth=args.birth, ew_from=args.ew_from, ew_last_day=args.ew_last_day,
                                scot_ni_from=args.scot_ni_from, benefits=args.benefits, income=args.income)
    except (ProfileError, OSError) as err:
        print(f"ask.py: {err}", file=sys.stderr)
        return 2
    sys.stdout.write(ask(profile, lean=not args.no_lean))
    return 0


if __name__ == "__main__":
    sys.exit(main())
