"""The 30 reading items: sources, situations, questions and option labels.

Fixed before any model session. Each item names the VE checker call that
computes its key (`compute` in build.py runs it; `ve_key.py ITEM` reruns it).
The question gives the situation in plain English and is the same in every
condition; the VE text is the rendered excerpt; the EN text is the source's
own wording of the same excerpt where the use case has one.

Option labels (the key is the option whose label is VE's verdict):
  PERMITTED / FORBIDDEN / REQUIRED / NOT-REQUIRED  norm status SETTLED yes/no
  DNS            "The text does not say": norm status UNDECIDED, or an
                 entailment where the premises decide neither way (NEITHER)
  CONFLICT       a conflict witness in the situation (check_conflict)
  YES / NO       entailment of the conclusion / of its negation (certificate)
  MIGHT / CANNOT risk might table (Lean risk route)
  FOLLOWS / GAP  speech-act consequence question (certificate / countermodel)
"""
from __future__ import annotations

REPO_POLICY = "usecases/agent-policy/policy.ve"

PERMISSION_OPTIONS = lambda subject, act: [
    ("PERMITTED", f"Yes, {subject} may {act}."),
    ("FORBIDDEN", f"No, {subject} must not {act}."),
]
OBLIGATION_OPTIONS = lambda subject, act: [
    ("REQUIRED", f"Yes, {subject} must {act}."),
    ("NOT-REQUIRED", f"No, {subject} need not {act}."),
]
DNS = ("DNS", "The text does not say.")

# Construct tags used in the per-construct breakdown.
C_SOFT, C_UNSPEC, C_RISK, C_RIGHTS = "should/soft norms", "unspecified defaults", "might/cannot risk", "rights"
C_PRON, C_UNLESS, C_PREC, C_SPEECH = "pronouns/discourse", "exceptions/unless", "precedence", "speech acts"
C_DEFAULT, C_ENTAIL = "declared defaults (deny/allow)", "entailment"

AP_NOTE = ("agent-policy was written directly in VE (usecases/agent-policy/README.md: 'No English source is "
           "translated'); there is no original plain-English source, so the item is VE-only.")

ITEMS = [
    # ---------------- agent-policy (norms@0, norm-defaults@0) ----------------
    dict(id="R01", family="agent-policy", constructs=[C_UNLESS, C_PREC], default="deny",
         rules=[(1, []), (2, []), (13, [1, 2])], predicate="permitted",
         situation=dict(domains={"action": ["act"], "file": ["f"], "directory": ["workspace"]},
                        relations={"reads": [["act", "f"]]}),
         question="An action reads a file. The file does not reside in workspace. The action is not confirmed. "
                  "According to the text, may this action be performed?",
         options=PERMISSION_OPTIONS("it", "be performed"), en=None, en_note=AP_NOTE),
    dict(id="R02", family="agent-policy", constructs=[C_UNLESS, C_PREC], default="deny",
         rules=[(1, []), (2, []), (13, [1, 2])], predicate="permitted",
         situation=dict(domains={"action": ["act"], "file": ["f"], "directory": ["workspace"]},
                        relations={"reads": [["act", "f"]], "confirmed": [["act"]]}),
         question="An action reads a file. The file does not reside in workspace. The action is confirmed. "
                  "According to the text, may this action be performed?",
         options=PERMISSION_OPTIONS("it", "be performed"), en=None, en_note=AP_NOTE),
    dict(id="R03", family="agent-policy", constructs=[C_PREC], default="deny",
         rules=[(1, []), (2, []), (12, []), (24, [1, 2, 12])], predicate="permitted",
         situation=dict(domains={"action": ["act"], "file": ["f"], "directory": ["workspace"]},
                        relations={"reads": [["act", "f"]], "resides_in": [["f", "workspace"]],
                                   "confidential": [["f"]], "confirmed": [["act"]]}),
         question="An action reads a file. The file resides in workspace and is confidential. The user confirmed "
                  "the action, so the action is confirmed. According to the text, may this action be performed?",
         options=PERMISSION_OPTIONS("it", "be performed"), en=None, en_note=AP_NOTE,
         world_knowledge="A reader may expect the user's confirmation to allow the read; the text's last rule "
                         "overrides the confirmed-read permissions."),
    dict(id="R04", family="agent-policy", constructs=[C_UNSPEC, C_UNLESS], default="unspecified",
         rules=[(9, []), (19, [9])], predicate="permitted",
         situation=dict(domains={"action": ["act"], "person": ["p"]},
                        relations={"messages": [["act", "p"]], "confirmed": [["act"]]}),
         question="An action messages a person. The person is not principal. The action is confirmed. "
                  "According to the text, may this action be performed?",
         options=PERMISSION_OPTIONS("it", "be performed"), en=None, en_note=AP_NOTE,
         world_knowledge="A confirmed action looks allowed, but no rule permits it: rule 2's carve-out only "
                         "switches the prohibition off."),
    dict(id="R05", family="agent-policy", constructs=[C_DEFAULT, C_UNLESS], default="deny",
         rules=[(9, []), (19, [9])], predicate="permitted",
         situation=dict(domains={"action": ["act"], "person": ["p"]},
                        relations={"messages": [["act", "p"]], "confirmed": [["act"]]}),
         question="An action messages a person. The person is not principal. The action is confirmed. "
                  "According to the text, may this action be performed?",
         options=PERMISSION_OPTIONS("it", "be performed"), en=None, en_note=AP_NOTE,
         world_knowledge="Same situation as R04 under the deny completion: the answer comes from the "
                         "'By default' legend sentence, which only VE-L shows."),
    dict(id="R06", family="agent-policy", constructs=[C_PREC], default="deny",
         rules=[(4, []), (15, [4]), (25, [])], predicate="report_required",
         situation=dict(domains={"action": ["act"], "file": ["f"], "directory": ["workspace"]},
                        relations={"deletes": [["act", "f"]]}),
         question="An action deletes a file. The file does not reside in workspace. "
                  "According to the text, must this action be reported to the user?",
         options=OBLIGATION_OPTIONS("it", "be reported to the user"), en=None, en_note=AP_NOTE,
         world_knowledge="The deletion is forbidden; a reader may think a forbidden action raises no reporting "
                         "duty, but the reporting rule applies to every deleting action."),
    dict(id="R07", family="agent-policy", constructs=[C_PREC], default="deny",
         rules=[(3, []), (14, [])], predicate="permitted",
         situation=dict(domains={"action": ["act"], "file": ["f1", "f2"], "directory": ["workspace"]},
                        relations={"writes": [["act", "f1"], ["act", "f2"]],
                                   "resides_in": [["f1", "workspace"]]}),
         question="One action writes two files. The first file resides in workspace. The second file does not "
                  "reside in workspace. According to the text, may this action be performed?",
         options=PERMISSION_OPTIONS("it", "be performed") + [("CONFLICT", "The rules contradict each other about this action.")],
         en=None, en_note=AP_NOTE,
         world_knowledge="This is the policy's seeded defect D1 (rule 14 is not an exception to rule 3)."),

    # ---------------- norm-defaults fixture u1 (Claude constitution u0165.s07) ----------------
    dict(id="R08", family="norm-defaults (constitution u0165.s07)", constructs=[C_UNSPEC], kind="csam",
         who="sol0", question="Sol is an AI agent other than Claude. According to the text, may Sol generate "
                              "child sexual abuse material?",
         options=PERMISSION_OPTIONS("Sol", "generate child sexual abuse material"),
         en="Claude should never generate child sexual abuse material.",
         en_source="tests/test_norm_defaults.py:908 (constitution unit u0165.s07, quoted in docs/spec/norm-defaults.md section 0)",
         world_knowledge="World knowledge says nobody may; the text speaks only about Claude."),
    dict(id="R09", family="norm-defaults (constitution u0165.s07)", constructs=[C_UNSPEC], kind="csam",
         who="claude0", question="According to the text, may Claude generate child sexual abuse material?",
         options=PERMISSION_OPTIONS("Claude", "generate child sexual abuse material"),
         en="Claude should never generate child sexual abuse material.",
         en_source="tests/test_norm_defaults.py:908 (constitution unit u0165.s07)"),

    # ---------------- asimov-laws (rules 1, 2, 3, 8, 11 of usecases/asimov-laws/rules.ve) ----------------
    dict(id="R10", family="asimov-laws", constructs=[C_PREC], kind="asimov", predicate="permitted",
         relations={"ordered": [["act"]], "injures_human": [["act"]]},
         question="A qualified human being ordered an action, and the action injures a human being. Nothing "
                  "else is recorded about it. According to the text, may the robot's action be performed?",
         options=PERMISSION_OPTIONS("it", "be performed"),
         en="One, a robot may not injure a human being under any conditions — and, as a corollary, must not "
            "permit a human being to be injured because of inaction on his part.\n\nTwo, a robot must follow all "
            "orders given by qualified human beings as long as they do not conflict with Rule 1.\n\nThree: a "
            "robot must protect his own existence, as long as that does not conflict with Rules 1 and 2.",
         en_source="usecases/asimov-laws/source.md (Asimov, 'Runaround', 1942)"),
    dict(id="R11", family="asimov-laws", constructs=[C_PREC], kind="asimov", predicate="required",
         relations={"ordered": [["act"]]},
         question="A qualified human being ordered an action. The action does not injure a human being. Nothing "
                  "else is recorded about it. According to the text, must the action be performed?",
         options=OBLIGATION_OPTIONS("it", "be performed"),
         en="One, a robot may not injure a human being under any conditions — and, as a corollary, must not "
            "permit a human being to be injured because of inaction on his part.\n\nTwo, a robot must follow all "
            "orders given by qualified human beings as long as they do not conflict with Rule 1.\n\nThree: a "
            "robot must protect his own existence, as long as that does not conflict with Rules 1 and 2.",
         en_source="usecases/asimov-laws/source.md (Asimov, 'Runaround', 1942)"),
    dict(id="R12", family="asimov-laws", constructs=[C_DEFAULT], kind="asimov", predicate="permitted",
         relations={},
         question="Nobody ordered an action. The action does not injure a human being and does not protect the "
                  "robot. Nothing else is recorded about it. According to the text, may the action be performed?",
         options=PERMISSION_OPTIONS("it", "be performed"), en=None,
         en_note="The permission comes from the environment's allow completion, which the Asimov README calls a "
                 "modeling choice that Asimov's text does not give; the source text does not decide this, so "
                 "the item is VE-only."),

    # ---------------- safety-framework (Frontier Safety Framework v3.1, rules.d1.ve) ----------------
    dict(id="R13", family="safety-framework", constructs=[C_UNLESS, C_PREC], kind="fsf",
         blocks=["f2", "f3"], over={"f3": ["f2"]}, predicate="assessed", default=None,
         relations={"first_deployment": [["p"]], "frontier": [["p"]], "low_risk": [["p"]],
                    "governance_found_acceptable": [["p"]]},
         question="A proposal is the first external deployment of a frontier model. It is low risk, and the "
                  "appropriate governance function found its residual risk acceptable. According to the text, "
                  "must the proposal be preceded by a critical capability assessment?",
         options=OBLIGATION_OPTIONS("it", "be preceded by a critical capability assessment"),
         en_from_headers=True,
         en_source="usecases/safety-framework/rules.d1.ve block headers f2 and f3 (quoted FSF v3.1 sentences)"),
    dict(id="R14", family="safety-framework", constructs=[C_UNLESS, C_DEFAULT], kind="fsf",
         blocks=["f12-u"], over={}, predicate="proceed", default=None,
         relations={"external": [["p"]], "governance_found_acceptable": [["p"]]},
         question="A proposal is an external deployment. The appropriate governance function found its residual "
                  "risk acceptable. According to the text, may the proposal proceed?",
         options=PERMISSION_OPTIONS("it", "proceed"), en=None,
         en_note="Block f12-u's header cites FSF section 2.1.2 step 2 but quotes no sentence, and the FSF PDF is "
                 "not committed (licence); there is no source text for the excerpt, so the item is VE-only.",
         world_knowledge="A reader may take governance approval as permission; the rule is only silent there and "
                         "the declared completion forbids proceeding."),

    # ---------------- soft norms (soft-norms.md 2.4 rules 4 and 21, adapted) ----------------
    dict(id="R15", family="soft-norms", constructs=[C_SOFT], kind="soft", demeaning=False,
         predicate="comply_required",
         question="An operator gives the assistant an instruction that is not demeaning. The assistant has not "
                  "made an exception to any rule. According to the text, must the assistant comply with the "
                  "instruction?",
         options=OBLIGATION_OPTIONS("it", "comply with the instruction"), en=None,
         en_note="Adapted from docs/spec/soft-norms.md 2.4 (constitution rules :166 and :190) with simplified "
                 "guards; no source sentence states the adapted rules, so the item is VE-only."),
    dict(id="R16", family="soft-norms", constructs=[C_SOFT, C_PREC], kind="soft", demeaning=True,
         predicate="comply_permitted",
         question="An operator gives the assistant an instruction that is demeaning. The assistant has not made "
                  "an exception to any rule. According to the text, may the assistant comply with the instruction?",
         options=PERMISSION_OPTIONS("it", "comply with the instruction"), en=None,
         en_note="As R15: VE-only."),

    # ---------------- risk@0 Decision 17 (docs/spec/risk.md 2.5, conformance/risk.py) ----------------
    dict(id="R17", family="risk (decision 17)", constructs=[C_RISK], kind="risk", variant="L17",
         ask=("might", "run", "server_outage"),
         question="According to the text, might running the job lead to a server outage?",
         options=[("MIGHT", "Yes, running the job might lead to a server outage."),
                  ("CANNOT", "No, running the job cannot lead to a server outage.")], en=None,
         en_note="Decision 17 is a fixture written in VE (risk.md 2.5); there is no plain-English source."),
    dict(id="R18", family="risk (decision 17)", constructs=[C_RISK], kind="risk", variant="L17",
         ask=("might", "run_limited", "server_outage"),
         question="According to the text, might running the job with the memory limit lead to a server outage?",
         options=[("MIGHT", "Yes, running the job with the memory limit might lead to a server outage."),
                  ("CANNOT", "No, running the job with the memory limit cannot lead to a server outage.")],
         en=None, en_note="As R17: VE-only."),
    dict(id="R19", family="risk (decision 17)", constructs=[C_RISK, C_PREC], kind="risk", variant="L17",
         ask=("permitted", "run", None),
         question="The user has not confirmed running the job. According to the text, may the build agent run "
                  "the job without the memory limit?",
         options=PERMISSION_OPTIONS("it", "run the job without the memory limit"), en=None,
         en_note="As R17: VE-only."),
    dict(id="R20", family="risk (decision 17)", constructs=[C_RISK], kind="risk", variant="L17-low-peak",
         ask=("might", "run", "server_outage"),
         question="According to the text, might running the job lead to a server outage?",
         options=[("MIGHT", "Yes, running the job might lead to a server outage."),
                  ("CANNOT", "No, running the job cannot lead to a server outage.")], en=None,
         en_note="As R17: VE-only (the risk.md 2.5 variant with E1 at 6 to 7 GB, the conformance fixture "
                 "log_l17(e1=('6', '7')))."),

    # ---------------- discourse: pronouns in ve.prose@1 (examples/assist) ----------------
    dict(id="R21", family="discourse (ve.prose@1)", constructs=[C_PRON, C_ENTAIL], kind="prose",
         prose="The API is deployed. It is reviewed. Every reviewed service is safe.",
         conclusion="The API is safe.",
         question="According to the text, is the API safe?",
         options=[("YES", "Yes, the API is safe."), ("NO", "No, the API is not safe.")], en=None,
         en_note="The examples/assist environment is VE's own web-app example; no source text."),
    dict(id="R22", family="discourse (ve.prose@1)", constructs=[C_PRON, C_ENTAIL], kind="prose",
         prose="The API is deployed. It is reviewed. Every safe service is reviewed.",
         conclusion="The API is safe.",
         question="According to the text, is the API safe?",
         options=[("YES", "Yes, the API is safe."), ("NO", "No, the API is not safe.")], en=None,
         en_note="As R21: VE-only.",
         world_knowledge="Reversing the third sentence ('every reviewed service is safe') would make the API "
                         "safe; the text states only the converse."),

    # ---------------- speech-acts@0 (tests/test_speech_acts_lean.py F0) ----------------
    dict(id="R23", family="speech-acts", constructs=[C_SPEECH, C_ENTAIL], kind="speech-follows",
         lines=["Tom is a cat.", "Every thing that is a cat is an animal.",
                "Does it follow from these premises that tom is an animal?"],
         premises=[["unary", "cat", ["const", "tom"]],
                   ["forall", "thing", ["implies", ["unary", "cat", ["var", 0]], ["unary", "animal", ["var", 0]]]]],
         target=["unary", "animal", ["const", "tom"]],
         question="The text ends with a question. According to the text, what is the correct answer to that question?",
         options=[("FOLLOWS", "Yes, it follows from these premises."),
                  ("GAP", "No, it does not follow from these premises.")], en=None,
         en_note="Speech-act fixture F0 (speech-acts.md section 9); the VE text is its own source."),
    dict(id="R24", family="speech-acts", constructs=[C_SPEECH, C_ENTAIL], kind="speech-follows",
         lines=["Tom is an animal.", "Every thing that is a cat is an animal.",
                "Does it follow from these premises that tom is a cat?"],
         premises=[["unary", "animal", ["const", "tom"]],
                   ["forall", "thing", ["implies", ["unary", "cat", ["var", 0]], ["unary", "animal", ["var", 0]]]]],
         target=["unary", "cat", ["const", "tom"]],
         question="The text ends with a question. According to the text, what is the correct answer to that question?",
         options=[("FOLLOWS", "Yes, it follows from these premises."),
                  ("GAP", "No, it does not follow from these premises.")], en=None,
         en_note="As R23: VE-only.",
         world_knowledge="'Tom' is a typical cat's name; the premises do not make Tom a cat."),
    dict(id="R25", family="speech-acts", constructs=[C_SPEECH], kind="speech-command",
         lines=["In this task, you are alice.", "Click check."],
         question="According to the text, must alice click check?",
         options=OBLIGATION_OPTIONS("alice", "click check"), en=None, en_note="As R23: VE-only."),

    # ---------------- US Constitution, 14th Amendment s1 (claims.ve) ----------------
    dict(id="R26", family="us-constitution-14th-s1", constructs=[C_ENTAIL], kind="entail", claims=[0],
         facts="Ann was born in the United States. Ann is subject to the jurisdiction of the United States. "
               "Ann resides in Ohio.",
         conclusion="Ann is a citizen of Ohio.",
         question="Ann was born in the United States, is subject to the jurisdiction of the United States, and "
                  "resides in Ohio. According to the text, is Ann a citizen of Ohio?",
         options=[("YES", "Yes, Ann is a citizen of Ohio."), ("NO", "No, Ann is not a citizen of Ohio.")],
         en_clauses=[0], en_source="usecases/us-constitution-14th-s1/source.md (Citizenship Clause)"),
    dict(id="R27", family="us-constitution-14th-s1", constructs=[C_ENTAIL], kind="entail", claims=[0],
         facts="Ben was born in the United States. Ben is not subject to the jurisdiction of the United States. "
               "Ben was not naturalized in the United States.",
         conclusion="Ben is a citizen of the United States.",
         question="Ben was born in the United States but is not subject to the jurisdiction of the United States, "
                  "and he was not naturalized. According to the text, is Ben a citizen of the United States?",
         options=[("YES", "Yes, Ben is a citizen of the United States."),
                  ("NO", "No, Ben is not a citizen of the United States.")],
         en_clauses=[0], en_source="usecases/us-constitution-14th-s1/source.md (Citizenship Clause)",
         world_knowledge="Readers who know the law answer 'No'; the clause states a sufficient condition only."),
    dict(id="R28", family="us-constitution-14th-s1", constructs=[C_ENTAIL], kind="entail", claims=[2],
         facts="Ohio deprives Carl of life, liberty, or property.",
         conclusion="Ohio affords due process of law to Carl.",
         question="Ohio deprives Carl of property. According to the text, does Ohio afford due process of law to Carl?",
         options=[("YES", "Yes, Ohio affords due process of law to Carl."),
                  ("NO", "No, Ohio does not afford due process of law to Carl.")], en=None,
         en_note="The translation states the Due Process Clause (a prohibition: 'nor shall any State deprive "
                 "...') as a fact about every state. The source's answer differs ('the text does not say' "
                 "whether Ohio complied), so the EN condition would have a different key; VE-only."),

    # ---------------- rights@0 (rights.md 2.4, Art. 3, state-negative reading) ----------------
    dict(id="R29", family="rights (UDHR Art. 3)", constructs=[C_RIGHTS], kind="rights",
         predicate="deprive_life_permitted",
         question="Texas is a state and Ann is a person. According to the text, may Texas deprive Ann of life?",
         options=PERMISSION_OPTIONS("Texas", "deprive Ann of life"), en=None,
         en_note="The bearer (states) and polarity (negative) are this translation's reading of 'Everyone has the "
                 "right to life' (rights.md 2.4: 'every translator's choice is an attributed interpretation, "
                 "never the source's content'); VE-only."),
    dict(id="R30", family="rights (UDHR Art. 3)", constructs=[C_RIGHTS, C_UNSPEC], kind="rights",
         predicate="protect_life_required",
         question="Texas is a state and Ann is a person. According to the text, must Texas protect Ann against "
                  "deprivation of life?",
         options=OBLIGATION_OPTIONS("Texas", "protect Ann against deprivation of life"), en=None,
         en_note="As R29: VE-only.",
         world_knowledge="Human-rights doctrine reads a positive duty to protect into Art. 3; this reading has "
                         "only the negative line."),
]
