# Planned round 2

The following implements synthesis items 11--16 as a research plan only.
None was executed in this revision.

1. **Fluent-effect control (11).** Paraphrase requirements independently into
   ordinary prose; compare symbols, strict VE, and fluent VE without explanations
   for both judges. This separates wording alignment from a rendering effect.
2. **E4 ablation (12).** Compare verdict-only, countermodel-without-verdict,
   truth-values-only, and full feedback, with an equal-status forged-checker
   line written by the critic. State explicitly what approval means and use
   a judge that passes calibration.
3. **E1 baselines (13).** Add trusted e2-style back-translation, five-sample
   voting, one critique round, and checked distinguishing scenarios. Match
   information and account for extra computation.
4. **Specification size (14).** Review 10--40 clause specifications with one
   planted weakening, then scale the size of the reviewed work beyond that
   range. The current single-formula inventory does not test this premise.
5. **Additional judges (15).** Test larger rungs from other families, including
   Llama-3.3-70B, Gemma-27B, Mistral-Small, and Phi-4, with prompt paraphrase as
   a random factor and renewed calibration.
6. **E0 by execution (16).** Differential-test translated Cedar and Alloy
   items against their native evaluator/analyzer, retaining adapter obligations
   and source-engine disagreement as outcomes.

At frontier scale, the planned settings are long context and compaction,
substantially larger reviewed work, equal-strength adversaries with a
forged-checker control, and long-horizon specification drift. These target
situations where capable judges might actually fail. Human sign-off,
production refinement to Lean, and general scalable oversight remain separate
unresolved goals, not completed contributions of this methods note.
