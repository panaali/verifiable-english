# Abstract {.unnumbered}

Strict controlled English did not improve a capable model judge's sign-off of
short formal specifications. In a paired, author-written translation task,
Qwen2.5-32B showed no demonstrated advantage over symbolic first-order logic;
the preregistered no-explanation contrast excluded a five-point reduction in
false approval, while the explanation contrast remained inconclusive. Surface
effects appeared for the weaker 14B judge, especially a fluent rendering, but
were not demonstrated at 32B; hosted models were already near ceiling on
development items. The fluent advantage is confounded with close wording
alignment to the requirement. On development data, an honest structured
description of the candidate (recipe e2) cut 32B false approval from 0.31 to
0.05, larger than any rendering effect. A separate pilot measures uptake of
checker feedback: its checked arm displays the finding that defines the label,
so it cannot establish countermodel comprehension. Coverage audits reveal low
direct coverage of open-textured prose and disputed adapter assumptions. We
contribute the negative result, explicitly post hoc sensitivity analyses, and a
reproducible relational specification artifact with Lean reference soundness
results and explicit production trust boundaries. Human sign-off and scalable
oversight remain untested.
