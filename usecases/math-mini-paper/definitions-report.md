# W3 definitions rerun

The four properties are identity-bound `defined` declarations. Each theorem uses a vocabulary version containing only the declarations it needs, so no theorem copies a definition axiom into its own hypotheses.

| Theorem | Python certificate | Copied definition hypotheses |
|---|---|---:|
| T5 | yes | 0 |
| T6 | yes | 0 |
| T7a | yes | 0 |
| T7b | yes | 0 |
| T7 | yes | 0 |
| T8 | yes | 0 |

T7mono is certified by citing T7a and T7b to obtain T7: **Checked**. Its report retains the `background:definitions` and `open:transitivity` leaves.

The checked-in baseline rerun remains 15/19; this citation adds T7mono to the Python-certified results, yielding 16/19. T9 and T9e still exhaust the current closure checker. C1 remains uncertified. Lean and Rust explicitly reject `defined` entries; these Python certificates therefore have no cross-language acceptance claim.
