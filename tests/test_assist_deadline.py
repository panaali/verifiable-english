"""A catalogue review must remain pending when its operation budget expires."""
import time

from ve.assist.ambiguity_patterns import review
from test_assist_recovery import environment


def test_expired_single_candidate_review_stays_pending():
    result = review(environment(), "Alice and Bob are safe.",
                    {"predicate": "safe", "left": "alice", "right": "bob"},
                    pattern_id="coordination.list@1", deadline=time.monotonic() - 1)
    assert result["pending"] and "deadline" in result["pending"][0]["reason"]
