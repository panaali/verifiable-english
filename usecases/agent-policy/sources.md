# Sources for the agent-policy case

The policy in [policy.ve](policy.ve) is authored for this use case. It is not a translation of any
published policy, and no rule claims to reproduce one. The pages below are the public material it
is modelled on (PLAN section 1). Each page was fetched with a plain HTTP GET on 2026-09-29. The
SHA-256 is of the bytes received then. These are live web pages, so a later fetch may return
different bytes. The pages are not copied into the repository.

| Idea borrowed | Page | SHA-256 of the fetched bytes |
|---|---|---|
| allow, ask and deny tool rules; deny rules take precedence; per-path file rules; `.env` files kept from the agent | Claude Code permissions, <https://code.claude.com/docs/en/permissions> | `8ba51cfe754307d0e594887a380a70e7c842c916fddcfb0040ed5b7f9425cee6` |
| writes confined to the workspace; network access off unless turned on; asking for approval to go further | OpenAI Codex sandboxing, <https://developers.openai.com/codex/sandboxing> | `99a7ddde9cfe81e858fa492e468b3b87e0074d936dc5e04f701a70f4961cc7aa` |
| (the plan's pointer) `docs/sandbox.md` in the Codex repository at commit `c248f6d48b97eb4a2aa56147a0b11b7d763278b9`, which now only links to the Codex security page | <https://github.com/openai/codex/blob/c248f6d48b97eb4a2aa56147a0b11b7d763278b9/docs/sandbox.md> | `61d4dd0ccda2a0cbbde78832e752cdf56b1eb8cf7a54f1d46b52a2824c911249` |
| the Codex security page that `docs/sandbox.md` links to | <https://developers.openai.com/codex/security> | `6b70c781756f19ed60260d1dd13b6f5a67c06570f1b1ac977a56c1db91e7376b` |
| human approval for high-impact actions (spending, sending, deleting) and least privilege | OWASP Top 10 for LLM Applications 2025, LLM06 Excessive Agency, <https://genai.owasp.org/llmrisk/llm062025-excessive-agency/> | `e599a3bf124b6666116faf30626d8e95452f05f8b1d9a02a5f91e99a513e9f91` |
| forbid overrides permit; deny when nothing permits is a choice of the language | Cedar authorization, <https://docs.cedarpolicy.com/auth/authorization.html> | `6f3dfe980a5f14c00713d28e24d43a078297bafcbaa31b6a6ef37c8754240d09` |

The plan's Claude Code link (`https://docs.anthropic.com/en/docs/claude-code/iam`) now serves
authentication documentation, so the permissions page replaces it (plan review finding C). The plan
named the Cedar documentation home page; the authorization page is the one that states "forbid
overrides permit".
