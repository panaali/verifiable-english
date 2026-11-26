"""The ONE bridge script of the GitLab relocation translation (statute corpus batch 5). Evidence branch, not for merge. It
gives only the first anniversary of a start date (ISOLATION.md D8: "the same day and month one year later"); the language has
day steps and no year step. A 29 February start date has no anniversary the text fixes: refused (D8). Never an amount, a sum or
a comparison with a limit of the text. The encoder enters the result as a stated fact marked "bridge" (encode.py); the unit
(33) is ledgered "bridged".
"""
from __future__ import annotations

import datetime as dt


def anniversary(start: str) -> str:
    d = dt.date.fromisoformat(start)
    if (d.month, d.day) == (2, 29):
        raise ValueError("start date 29 February: the text fixes no anniversary (refused, D8)")
    return d.replace(year=d.year + 1).isoformat()
