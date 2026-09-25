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

The existing `ve_experiments.assist_haiku.ClaudeProposer` uses the controlled CLI endpoint, its pinned model/CLI checks, isolated working directory, and credential sanitizer. Account selection uses `VE_ASSIST_CLAUDE_ACCOUNT` or the existing `VE_CLAUDE_ACCOUNT_CONFIG_DIR`. No credentials are provisioned by this app. A missing CLI, incompatible version, or unavailable account returns an availability error; there is no provider fallback.

Each click proposes **one sentence**, with at most one backend attempt and a 1,024-token output ceiling; automatic repair is disabled. Suggestions never run while typing. Calls are limited to three per rolling minute and 30 per UTC day by default, shared by all sessions using the access token. SQLite reservations persist in the state directory and count failures conservatively, including rejected or timed-out requests. Do not delete or change the state directory to reset allowance. These are call caps, not exact input-token or currency caps. Input is bounded to 6,000 characters per text field and 32 KiB per request. A user can request 1–3 readings in the single response; the UI shows all candidates and checked distinguishing worlds when available.

The private `calls.jsonl` ledger records backend usage and may contain submitted prose and model output. Keep the directory private; do not commit or publish it. The web process's access-token environment variables are removed before spawning the worker. The CLI's own subscription credentials remain governed by its existing isolation and sanitization path.

## Use

- **Learn:** four curated, scoped examples; English, strict VE, fluent, and logic views; evaluate a tiny world and replay a certificate or display a checked countermodel.
- **Writing desk:** request sentence-level model readings; review a deterministic paraphrase and alternatives; accept/edit explicitly; live strict parsing with line/column diagnostics; separate assumptions from the conclusion; Ctrl/⌘+Enter checks the consequence.
- Expand **Vocabulary & small world** to edit the library's environment/world JSON. The selected example is the starting vocabulary, not an unrestricted natural-language vocabulary. Each strict statement ends in a period and separate statements use separate lines. The app supplies a trailing newline for the parser.
- Light/dark theme, keyboard focus, responsive layout, four-step tour, and JSON draft export. Drafts live only in the current tab; switching examples replaces the draft and reloading loses it (the UI warns about unsaved edits). Export first to keep work. Only the theme is saved in local storage.

“Certified” means the **experimental Python certificate checker** replayed an exact deduction. The app does not run Lean. “Countermodel” means the library independently checked a finite world where the assumptions hold and the conclusion fails. “Unknown” is never a success. Proofs from inconsistent assumptions can be vacuously valid; this workspace does not perform a separate consistency audit. A finite-world evaluation is neither an entailment proof nor empirical evidence. Predicate descriptions, legal interpretation, source fidelity, and the truth of premises remain human responsibilities.

Candidate acceptance is a local drafting action, not a persistent audited `AssistSession` approval ledger. The app uses assist's proposal/paraphrase/comparison machinery; it does not expose the full CLI graph workflow, freeze-target protocol, or session verification. Backend usage is ledgered. Exported provenance is explanatory metadata, not a signed certificate of authorship.

## Security and limits

HttpOnly, SameSite=Strict cookies; Secure cookies on HTTPS; per-session CSRF headers plus same-origin checks; JSON-only writes; restrictive CSP; no CORS; no access logs; static asset allowlist; bounded request bodies (including streamed bodies); body and computation deadlines; fixed worker command with JSON stdin, never shell interpolation; no client-controlled file paths. Login attempts are limited globally to 15/minute and at most 100 active sessions. HTTPS sets HSTS for the hostname.

One operation runs at a time; excess work receives 429. Semantic work is killed after eight seconds; assist after 50 seconds (CLI deadline 40 seconds), including its process group. Library search budgets also apply. An internet service can still need upstream volumetric abuse protection. The shared token provides one access role, not individual accounts.

## Verification

```bash
UV_CACHE_DIR=/tmp/ve-webapp-uv uv run pytest -q
# Optional headless browser test (installs test-only tooling, no project dependency):
PLAYWRIGHT_BROWSERS_PATH=/tmp/ve-webapp-browsers UV_CACHE_DIR=/tmp/ve-webapp-uv \
  uv run --with playwright python -m playwright install chromium
PLAYWRIGHT_BROWSERS_PATH=/tmp/ve-webapp-browsers UV_CACHE_DIR=/tmp/ve-webapp-uv \
  uv run --with playwright python webapp/smoke.py
```

API tests mock the model, exercise the real VE library and subprocess path, verify authentication/CSRF, cookie flags, call allowances, input limits, and examples. The browser smoke test starts its own loopback server with a temporary token and no live model capability.
