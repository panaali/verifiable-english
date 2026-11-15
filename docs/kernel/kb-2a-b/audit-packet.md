# kb-2a-b: audit packet for DESIGN kb-2a section 3 item 3 (the uc-audit of the acceptance document)

Document: `tests/data/kb2a/rsp-mixed.ve.md` (built by `docs/kernel/kb-2a-b/build_rsp_mixed.py` from the pinned RSP 3.4 text
and the D1 translation). Answer: `tests/data/kb2a/rsp-mixed.answer.json` (Lean's, `ve document check --json`). The audit
itself is scheduled by the DRI after merge; a unit judged unfaithful is listed with the finding, not re-labelled.

Choices of the reading set rs1-t1 (RS1 on t1-plan): choice 0: rs1-t1 reading 0 (cond); choice 1: rs1-t1 reading 1 (uncond); choice 2: rs1-t1 reading 2 (ov).

## intro-aspire

- Status: **UNFORMALISED**
- Unit bytes: “We aspire to advance the latter through a mixture of example-setting, addressing unsolved technical problems, advocacy through industry groups, and policy advocacy.”
- Full source sentence: “We aspire to advance the latter through a mixture of example-setting, addressing unsolved technical problems, advocacy through industry groups, and policy advocacy.”
- Kind `unformalised`, meaning `{"unformalised": "aim_without_force"}`, support `none`
- Core statements: none (no content)

## t1-plan

- Status: **OPEN**
- Unit bytes: “We will maintain or improve on our ASL-3 protections , which include classiﬁer guards at least as robust as our initial Constitutional Classiﬁers; access controls for trusted users with exemptions to classiﬁer guards; red-teaming, bug bounties, and threat intelligence for continually assessing the threat of jailbreaks; and a number of noteworthy security controls.”
- Full source sentence: “We will maintain or improve on our ASL-3 protections , which include classiﬁer guards at least as robust as our initial Constitutional Classiﬁers; access controls for trusted users with exemptions to classiﬁer guards; red-teaming, bug bounties, and threat intelligence for continually assessing the threat of jailbreaks; and a number of noteworthy security controls.”
- Kind `norm`, meaning `{"open": ["crossed"]}`, support `testimony`
- Core statements per choice:
  - choice 0: judgments@0: judgment term `crossed`; norms@0 (reading rs1-t1:0): rule `{"norm": {"guard": ["and", ["unary", "listed", ["var", 0]], ["binary", "crossed", ["var", 1], ["var", 0]]], "name": "rs1-t1", "over": [], "predicate": "plans_in_place", "sign": true, "unless": []}}`
  - choice 1: judgments@0: judgment term `crossed`; norms@0 (reading rs1-t1:1): rule `{"norm": {"guard": ["unary", "listed", ["var", 0]], "name": "rs1-t1", "over": [], "predicate": "plans_in_place", "sign": true, "unless": []}}`
  - choice 2: judgments@0: judgment term `crossed`

## t4-name

- Status: **CHECKED**
- Unit bytes: “Automated R&D in key domains.”
- Full source sentence: “Automated R&D in key domains.”
- Kind `asserted`, meaning `"specified"`, support `testimony`
- Core statements per choice:
  - choice 0: facts: premise `["unary", "listed", ["const", "automated_rd"]]`
  - choice 1: facts: premise `["unary", "listed", ["const", "automated_rd"]]`
  - choice 2: facts: premise `["unary", "listed", ["const", "automated_rd"]]`

## s35-aim

- Status: **CHECKED**
- Unit bytes: “We will aim to minimize redactions to the public version of the report or to the version of the report shared with all regular-clearance Anthropic employees.”
- Full source sentence: “We will aim to minimize redactions to the public version of the report or to the version of the report shared with all regular-clearance Anthropic employees.”
- Kind `norm`, meaning `"specified"`, support `testimony`
- Core statements per choice:
  - choice 0: soft-norms@0: rule `{"norm": {"exception": {"decided_by": "unstated", "factors": [], "necessary": [], "sufficient": []}, "guard": ["top"], "mode": "default", "name": "f13-minimize-default", "over": [], "predicate": "redactions_minimized", "sign": true, "unless": []}}`
  - choice 1: soft-norms@0: rule `{"norm": {"exception": {"decided_by": "unstated", "factors": [], "necessary": [], "sufficient": []}, "guard": ["top"], "mode": "default", "name": "f13-minimize-default", "over": [], "predicate": "redactions_minimized", "sign": true, "unless": []}}`
  - choice 2: soft-norms@0: rule `{"norm": {"exception": {"decided_by": "unstated", "factors": [], "necessary": [], "sufficient": []}, "guard": ["top"], "mode": "default", "name": "f13-minimize-default", "over": [], "predicate": "redactions_minimized", "sign": true, "unless": []}}`

## s35-disclose

- Status: **CHECKED**
- Unit bytes: “We will disclose the existence of each redaction made in the public version of the report”
- Full source sentence: “We will disclose the existence of each redaction made in the public version of the report and aim to give a brief justiﬁcation for such redactions, though in many cases this will necessarily be very high-level.”
- Kind `norm`, meaning `"specified"`, support `testimony`
- Core statements per choice:
  - choice 0: soft-norms@0: rule `{"norm": {"guard": ["top"], "name": "f13-disclose", "over": [], "predicate": "redactions_disclosed", "sign": true, "unless": []}}`
  - choice 1: soft-norms@0: rule `{"norm": {"guard": ["top"], "name": "f13-disclose", "over": [], "predicate": "redactions_disclosed", "sign": true, "unless": []}}`
  - choice 2: soft-norms@0: rule `{"norm": {"guard": ["top"], "name": "f13-disclose", "over": [], "predicate": "redactions_disclosed", "sign": true, "unless": []}}`

## s36-full-review

- Status: **OPEN**
- Unit bytes: “At a minimum, we will complete a full external review process (described below) with at least one external reviewer anytime a Risk Report covers highly capable models and is signiﬁcantly redacted, deﬁned as follows:”
- Full source sentence: “At a minimum, we will complete a full external review process (described below) with at least one external reviewer anytime a Risk Report covers highly capable models and is signiﬁcantly redacted, deﬁned as follows:”
- Kind `norm`, meaning `{"open": ["highly_capable", "significantly_redacted"]}`, support `testimony`
- Core statements per choice:
  - choice 0: judgments@0: judgment term `highly_capable`; judgments@0: judgment term `significantly_redacted`; soft-norms@0: rule `{"norm": {"guard": ["and", ["unary", "highly_capable", ["var", 0]], ["unary", "significantly_redacted", ["var", 0]]], "name": "f14-full-review", "over": [], "predicate": "full_review", "sign": true, "unless": []}}`
  - choice 1: judgments@0: judgment term `highly_capable`; judgments@0: judgment term `significantly_redacted`; soft-norms@0: rule `{"norm": {"guard": ["and", ["unary", "highly_capable", ["var", 0]], ["unary", "significantly_redacted", ["var", 0]]], "name": "f14-full-review", "over": [], "predicate": "full_review", "sign": true, "unless": []}}`
  - choice 2: judgments@0: judgment term `highly_capable`; judgments@0: judgment term `significantly_redacted`; soft-norms@0: rule `{"norm": {"guard": ["and", ["unary", "highly_capable", ["var", 0]], ["unary", "significantly_redacted", ["var", 0]]], "name": "f14-full-review", "over": [], "predicate": "full_review", "sign": true, "unless": []}}`

## The headers

Each `<unit>-source` unit is a Markdown heading quoting the full source sentence; status **LABELLED** (meta, no content).
