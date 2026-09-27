# W3 definitions rerun

The four mathematical names are identity-bound `defined` declarations. Each theorem uses a vocabulary version containing only the declarations it needs, so no theorem copies a definition axiom into its own hypotheses. Python, Lean and Rust decode the declarations and regenerate the definition Background; the certificates below are replayed by both checkers.

| Theorem | Python certificate | Lean certificate | Copied definition hypotheses |
|---|---|---|---:|
| T5 | yes | yes | 0 |
| T6 | yes | yes | 0 |
| T7a | yes | yes | 0 |
| T7b | yes | yes | 0 |
| T7 | yes | yes | 0 |
| T8 | yes | yes | 0 |

The definitions, as the English surface writes them:

- By definition, for every first point, the first point is greatest exactly when every second point ranks below the first point.
- By definition, for every first point, the first point is minimum exactly when for every second point, if it is not the case that the second point is the same as the first point, then the first point precedes the second point.
- By definition, for every first point, the first point is minimal exactly when every second point does not precede the first point.
- By definition, for every first point, for every second point, the first point matches the second point exactly when both the first point ranks below the second point and the second point ranks below the first point.

T7mono is certified by citing T7a and T7b to obtain T7: **Checked** in Python, **Checked** in one Lean bundle run. Its report retains the `background:definitions` and `open:transitivity` leaves, and reads:

> By T7a and T7b, for every point named P1, for every point named P2, for every point named P3, for every point named P4, if all of the following hold:
>   (a) P1 matches P2;
>   (b) both P3 matches P4 and P1 ranks below P3, then P2 ranks below P4.

**Certified: 18/19** (C2, T1, T2, T3, T4, T5, T6, T7, T7a, T7b, T7mono, T8, T9, T9a, T9b, T9c, T9d, T9e). The checked-in baseline certifies 15 queries in Python and Lean; the closure-induction supplement (`usecases/closure-induction`) certifies T9 and T9e in both; T7mono is added here by citation. C1 remains honestly uncertified: it is false, and refuted by a one-element countermodel.
