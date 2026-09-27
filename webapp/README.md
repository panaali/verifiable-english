# Verifiable English writing desk

A locally served, authenticated web app using the existing `ve` library. No frontend build, fonts, analytics, or CDN requests. The gallery and checker never call a model. Live assistance is opt-in.

## Run on the VM

From `~/code/ve-webapp`:

```bash
# This VM's shared uv cache may be read-only.
export UV_CACHE_DIR=/tmp/ve-webapp-uv
uv sync
mkdir -p .webapp-private
chmod 700 .webapp-private
# Generate once. Do not regenerate the token on every restart.
(umask 077; uv run python -c 'import secrets; print(secrets.token_urlsafe(32))' > .webapp-private/access-token)
(umask 077; openssl req -x509 -newkey rsa:2048 -sha256 -days 30 -nodes \
  -keyout .webapp-private/key.pem -out .webapp-private/cert.pem \
  -subj '/CN=localhost' -addext 'subjectAltName=DNS:localhost,IP:127.0.0.1')
uv run python -m ve_webapp \
  --token-file .webapp-private/access-token \
  --cert .webapp-private/cert.pem --key .webapp-private/key.pem
```

Defaults: **HTTPS on `0.0.0.0:8443`**. Open `https://localhost:8443` locally, or `https://VM_HOST:8443` remotely. Read the token file privately and paste it into the login form. Never put tokens in URLs, command arguments, commits, or logs. `VE_WEB_TOKEN` is an alternative to a token file; `VE_WEB_TOKEN_FILE`, `VE_WEB_CERT`, and `VE_WEB_KEY` are supported too. Tokens must contain at least 32 characters; use the random generator above.

A 30-day development self-signed certificate was generated in the ignored `.webapp-private` directory during implementation. It is for localhost only and causes a browser trust warning. For public access, provide a trusted certificate and matching private key for your hostname using `--cert` / `--key`, and permit inbound TCP 8443 in your VM/cloud firewall. No firewall, DNS, system service, or system settings are changed by this app. It does not terminate HTTPS at a proxy or trust forwarded headers. Run it as an ordinary user in a persistent terminal or your existing service manager. Keep a single server worker; the entry point enforces this topology.

For loopback tests only:

```bash
uv run python -m ve_webapp --http --host 127.0.0.1 --port 8080 \
  --token-file .webapp-private/access-token
```

Non-loopback plain HTTP and privileged ports are rejected. Sessions expire after eight hours and disappear on server restart. Rotate the access-token file and restart to revoke every session. Explicit sign-out revokes the current session.

## Live assistance

Configure the same authenticated Claude CLI/account used by `ve assist`, then append:

```bash
--assist --model haiku --minute-cap 3 --daily-cap 30
```

The existing `ve_experiments.assist_haiku.ClaudeProposer` uses the controlled CLI endpoint, its pinned model/CLI checks, isolated working directory, and credential sanitizer. Account selection uses `VE_ASSIST_CLAUDE_ACCOUNT` or the existing `VE_CLAUDE_ACCOUNT_CONFIG_DIR`. No credentials are provisioned by this app. The repository currently pins Claude CLI `2.1.280 (Claude Code)`. Put that version on `PATH` for live assistance. A missing CLI, incompatible version, or unavailable account returns an availability error; there is no provider fallback. Preflight rejection can happen before any calls-ledger row is written.

Each click proposes **one sentence**, with at most one backend attempt and a 1,024-token output ceiling; automatic repair is disabled. Suggestions never run while typing. Calls are limited to three per rolling minute and 30 per UTC day by default, shared by all sessions using the access token. SQLite reservations persist in the state directory and count failures conservatively, including rejected or timed-out requests. Do not delete or change the state directory to reset allowance. These are call caps, not exact input-token or currency caps. Input is bounded to 6,000 characters per text field and 32 KiB per request. A user can request 1–3 readings in the single response; the UI shows all candidates and checked distinguishing worlds when available.

The private `calls.jsonl` ledger records backend usage and may contain submitted prose and model output. Keep the directory private; do not commit or publish it. The web process's access-token environment variables are removed before spawning the worker. The CLI's own subscription credentials remain governed by its existing isolation and sanitization path.

## Use

- **Writing desk:** opens on a blank, server-saved English document. Review meaning to see diagnostics and only ambiguity cards with a checked separating situation. Choose an explicit rewrite, then approve its meaning. Cancel, undo, unresolved, and assistant outage remain visible in the revision history. Reloads and a server restart preserve acknowledged revisions. A second tab with a stale revision must reload before writing.
- **Words:** declare a new kind, property, or relation explicitly, or confirm synonyms with a W3 glossary sentence. A vocabulary revision invalidates earlier approval. The example vocabulary is only a starting point.
- **Rules:** edit the W1 example using must, must not, may, exception, and precedence sentences. The result is a checked conflict situation or a conflict-free proof, stated in English.
- **Learn:** curated, scoped examples; audited natural English opens first, with per-sentence **explicit form** badges where the library cannot certify a symbol-free reading. Strict VE, fluent, and logic views have separate tabs. Evaluate a tiny world and replay a certificate or display a checked countermodel in plain English.
- Expand **Vocabulary & small world** to edit the library's environment/world JSON. The selected example is the starting vocabulary, not an unrestricted natural-language vocabulary. Each strict statement ends in a period and separate statements use separate lines. The app supplies a trailing newline for the parser.
- Light/dark theme, keyboard focus, responsive layout, four-step tour, and JSON document export/import. An export is unsigned and cannot prove authorship; import replays Z3's ledger before accepting it. The browser saves English edits after a short pause and warns if an edit is still unacknowledged.

“Certified” means the **experimental Python certificate checker** replayed an exact deduction. The app does not run Lean. “Countermodel” means the library independently checked a finite world where the assumptions hold and the conclusion fails. “Unknown” is never a success. Proofs from inconsistent assumptions can be vacuously valid; this workspace does not perform a separate consistency audit. A finite-world evaluation is neither an entailment proof nor empirical evidence. Predicate descriptions, legal interpretation, source fidelity, and the truth of premises remain human responsibilities.

Meaning approval uses the revisioned Z3 recovery ledger and is stored server-side per access token. It binds the source, chosen meaning, checked situation, and vocabulary versions. A proof does not approve an author's intent. The advanced strict editor remains a separate consequence checker.

## Security and limits

HttpOnly, SameSite=Strict cookies; Secure cookies on HTTPS; per-session CSRF headers plus same-origin checks; JSON-only writes; restrictive CSP; no CORS; no access logs; static asset allowlist; bounded request bodies (including streamed bodies); body and computation deadlines; fixed worker command with JSON stdin, never shell interpolation; no client-controlled file paths. Login attempts are limited globally to 15/minute and at most 100 active sessions. HTTPS sets HSTS for the hostname.

Draft writes use SQLite transactions, content hashes, idempotent request IDs, and compare-and-swap revisions. Z3 replays the recovery ledger on every read. Drafts have a 100-document and 300-revision limit per token; each source is at most 6,000 characters. The shared token provides one access role, not individual accounts.

## Verification

```bash
# Existing conformance tests require the local Lean executable when lake is installed.
(cd lean && lake build)
UV_CACHE_DIR=/tmp/ve-webapp-uv uv run pytest -q
# Optional headless browser test (installs test-only tooling, no project dependency):
PLAYWRIGHT_BROWSERS_PATH=/tmp/ve-webapp-browsers UV_CACHE_DIR=/tmp/ve-webapp-uv \
  uv run --with playwright python -m playwright install chromium
PLAYWRIGHT_BROWSERS_PATH=/tmp/ve-webapp-browsers UV_CACHE_DIR=/tmp/ve-webapp-uv \
  uv run --with playwright python webapp/smoke.py
```

API tests mock the model, exercise the real VE library and subprocess path, verify authentication/CSRF, cookie flags, call allowances, input limits, and examples. The browser smoke test starts its own loopback server with a temporary token and no live model capability.

Implementation verification (2026-09-25): full `uv run pytest -q` completed with **1,657 passed, 3 skipped, 1 live test deselected** after building Lean and Rust locally. The optional skips were llguidance, xgrammar, and an uncached pinned tokenizer. Headless browser smoke, HTTPS startup, and wheel asset inclusion passed. One final live-assist smoke request was rejected at preflight: this VM has Claude CLI 2.1.283 while the controlled endpoint requires 2.1.280. The calls ledger remained empty; no live inference was made. No system CLI installation was changed.
