"""Single-process HTTPS server; secrets never cross the semantic worker boundary."""
import asyncio
import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import signal
import sqlite3
import subprocess
import sys
import time
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from ve.errors import VEError
from .examples import EXAMPLES, BY_ID
from .drafts import DraftStore, StaleDraft
from .models import ASSIST_MODELS, DEFAULT_ASSIST_MODEL
from .rules import check_rules, RULES_TEXT

STATIC = Path(__file__).parent / "static"
MAX_BODY = 32768


@dataclass
class Settings:
    token: str
    state: Path
    secure: bool = True
    assist: bool = False
    model: str = DEFAULT_ASSIST_MODEL
    minute_cap: int = 3
    daily_cap: int = 30
    claude_cli_version: str | None = None
    account_config_dir: Path | None = None

    def __post_init__(self):
        if len(self.token) < 32:
            raise ValueError("Access token must contain at least 32 characters; generate a random token.")
        self.state = self.state.resolve()
        self.state.mkdir(parents=True, exist_ok=True, mode=0o700)
        if self.minute_cap < 1 or self.daily_cap < 1:
            raise ValueError("Call caps must be positive.")
        if self.model not in ASSIST_MODELS:
            raise ValueError("Choose an assistant model from: " + ", ".join(ASSIST_MODELS))
        if self.assist:
            (self.state / "claude-empty").mkdir(mode=0o700, exist_ok=True)
            if self.claude_cli_version is None:
                try:
                    self.claude_cli_version = subprocess.check_output(
                        ["claude", "--version"], text=True, timeout=10).strip()
                except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                    raise ValueError("Could not detect claude --version; use --claude-cli-version.") from exc
            if not self.claude_cli_version:
                raise ValueError("Claude CLI version cannot be empty.")
            self.account_config_dir = Path(self.account_config_dir or os.getenv(
                "VE_CLAUDE_ACCOUNT_CONFIG_DIR", "~/.agent-accounts/claude-danielsaeedi37")).expanduser().resolve()


class Quota:
    """Reserve before spawning; failures count, restarts and new sessions do not reset spend."""
    def __init__(self, settings):
        self.settings = settings
        self.path = settings.state / "quota.sqlite3"
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS calls (at REAL NOT NULL)")
        self.path.chmod(0o600)

    def reserve(self):
        now = time.time()
        with sqlite3.connect(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            minute = db.execute("SELECT count(*) FROM calls WHERE at > ?", (now - 60,)).fetchone()[0]
            daily = db.execute("SELECT count(*) FROM calls WHERE at >= ?", (int(now // 86400) * 86400,)).fetchone()[0]
            if minute >= self.settings.minute_cap or daily >= self.settings.daily_cap:
                raise HTTPException(429, "Assistant call allowance reached. Try later; the daily cap resets at UTC midnight.")
            db.execute("INSERT INTO calls VALUES (?)", (now,))
            db.execute("DELETE FROM calls WHERE at < ?", (now - 172800,))


async def worker(action, data, settings):
    payload = {"action": action, "data": data,
               "config": {"state": str(settings.state), "model": settings.model,
                          "cli_version": settings.claude_cli_version,
                          "account_config_dir": str(settings.account_config_dir) if settings.account_config_dir else None}}
    # Access token stays in the web process. CLI uses its own configured account.
    env = {k: v for k, v in os.environ.items() if k not in ("VE_WEB_TOKEN", "VE_WEB_TOKEN_FILE")}
    process = await asyncio.create_subprocess_exec(sys.executable, "-m", "ve_webapp.worker",
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL,
        env=env, start_new_session=True)
    try:
        raw, _ = await asyncio.wait_for(process.communicate(json.dumps(payload).encode()),
                                       timeout=50 if action == "propose" else 8)
        if process.returncode or len(raw) > 2_000_000:
            raise HTTPException(503, "The operation is not complete.")
        return json.loads(raw)
    except asyncio.TimeoutError:
        raise HTTPException(504, "Time budget exhausted. Simplify the statement and try again.")
    finally:
        # Also terminate descendants if a CLI exits leaving a subprocess behind.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        await process.wait()


class Boundary:
    """Bound streamed bodies too, not only Content-Length; add headers to all responses."""
    def __init__(self, app, secure):
        self.app, self.secure = app, secure

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        async def secured(message):
            if message["type"] == "http.response.start":
                message["headers"] += [(b"cache-control", b"no-store"), (b"x-content-type-options", b"nosniff"),
                    (b"referrer-policy", b"no-referrer"), (b"x-frame-options", b"DENY"),
                    (b"content-security-policy", b"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")]
                if self.secure:
                    message["headers"].append((b"strict-transport-security", b"max-age=31536000"))
            await send(message)
        body = bytearray()
        try:
            async with asyncio.timeout(10):
                while True:
                    message = await receive()
                    if message["type"] == "http.disconnect":
                        return
                    body.extend(message.get("body", b""))
                    if len(body) > MAX_BODY:
                        return await JSONResponse({"detail": "Request exceeds 32 KiB."}, 413)(scope, receive, secured)
                    if not message.get("more_body"):
                        break
        except TimeoutError:
            return await JSONResponse({"detail": "Request timed out."}, 408)(scope, receive, secured)
        consumed = False
        async def bounded():
            nonlocal consumed
            if not consumed:
                consumed = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()
        await self.app(scope, bounded, secured)


def create_app(settings, runner=worker):
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(Boundary, secure=settings.secure)
    sessions, attempts = {}, []
    quota = Quota(settings)
    drafts = DraftStore(settings.state, settings.token)
    busy = asyncio.Lock()

    def session(request):
        sid = request.cookies.get("ve_session", "")
        value = sessions.get(sid)
        if not value or value["expires"] < time.time():
            sessions.pop(sid, None)
            raise HTTPException(401, "The session is not valid.")
        return value

    def csrf(request, expected=None):
        origin = request.headers.get("origin")
        if origin and origin != f"{request.url.scheme}://{request.url.netloc}":
            raise HTTPException(403, "The origin is foreign. The request is rejected.")
        if request.headers.get("sec-fetch-site") == "cross-site":
            raise HTTPException(403, "The site is foreign. The request is rejected.")
        supplied = request.headers.get("x-ve-csrf", "")
        if not hmac.compare_digest(supplied.encode(), (expected or "login").encode()):
            raise HTTPException(403, "The CSRF header is not valid.")
        if request.headers.get("content-type", "").split(";")[0] != "application/json":
            raise HTTPException(415, "The request needs the JSON.")

    async def data(request):
        try:
            body = await request.json()
        except (ValueError, UnicodeError, RecursionError):
            raise HTTPException(400, "The JSON is not valid.")
        if not isinstance(body, dict):
            raise HTTPException(400, "The request needs the object.")
        return body

    @app.get("/")
    async def index():
        return FileResponse(STATIC / "index.html")

    @app.get("/assets/{name}")
    async def asset(name: str):
        if name not in ("app.js", "style.css"):
            raise HTTPException(404)
        return FileResponse(STATIC / name)

    @app.post("/api/login")
    async def login(request: Request):
        csrf(request)
        now = time.time()
        attempts[:] = [t for t in attempts if t > now - 60]
        if len(attempts) >= 15:
            raise HTTPException(429, "Too many login attempts. Wait a minute.")
        attempts.append(now)
        body = await data(request)
        token = body.get("token")
        if not isinstance(token, str) or not hmac.compare_digest(hashlib.sha256(token.encode()).digest(), hashlib.sha256(settings.token.encode()).digest()):
            raise HTTPException(401, "The token is not known.")
        for key in list(sessions):
            if sessions[key]["expires"] < now:
                del sessions[key]
        if len(sessions) >= 100:
            raise HTTPException(429, "Session limit reached.")
        sid, secret = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        sessions.pop(request.cookies.get("ve_session"), None)
        sessions[sid] = {"csrf": secret, "expires": now + 8 * 3600}
        response = JSONResponse({"csrf": secret, "assist": settings.assist, "model": settings.model})
        response.set_cookie("ve_session", sid, secure=settings.secure, httponly=True, samesite="strict", max_age=8*3600)
        return response

    @app.get("/api/session")
    async def current(request: Request):
        return {"csrf": session(request)["csrf"], "assist": settings.assist, "model": settings.model}

    @app.post("/api/logout")
    async def logout(request: Request):
        csrf(request, session(request)["csrf"])
        sessions.pop(request.cookies.get("ve_session"), None)
        response = JSONResponse({"ok": True})
        response.delete_cookie("ve_session", secure=settings.secure, httponly=True, samesite="strict")
        return response

    @app.get("/api/examples")
    async def examples(request: Request):
        session(request)
        return EXAMPLES

    @app.get('/api/drafts')
    async def list_drafts(request: Request):
        session(request)
        return drafts.list()

    @app.post('/api/drafts')
    async def create_draft(request: Request):
        csrf(request, session(request)['csrf'])
        body = await data(request)
        if set(body) - {'example'}:
            raise HTTPException(400, 'The field is not known.')
        try:
            return drafts.create(body.get('example', 'policy'))
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc

    @app.post('/api/drafts/import')
    async def import_draft(request: Request):
        csrf(request, session(request)['csrf'])
        body = await data(request)
        try:
            return drafts.import_copy(body)
        except (ValueError, VEError) as exc:
            raise HTTPException(400, str(exc)) from exc

    @app.get('/api/drafts/{draft_id}')
    async def get_draft(draft_id: str, request: Request):
        session(request)
        try:
            return drafts.get(draft_id)
        except ValueError as exc:
            raise HTTPException(404, str(exc)) from exc

    @app.get('/api/drafts/{draft_id}/export')
    async def export_draft(draft_id: str, request: Request):
        session(request)
        try:
            return drafts.export(draft_id)
        except ValueError as exc:
            raise HTTPException(404, str(exc)) from exc

    @app.post('/api/drafts/{draft_id}/commands')
    async def change_draft(draft_id: str, request: Request):
        csrf(request, session(request)['csrf'])
        body = await data(request)
        if set(body) != {'revision', 'request_id', 'action', 'args'}:
            raise HTTPException(400, 'The request needs the revision. The request needs the request ID. The request needs the action. The request needs the arguments.')
        if type(body['action']) is not str:
            raise HTTPException(400, 'The action is not valid.')
        if body['action'] in {'proposer_reserve', 'proposer_finish'}:
            raise HTTPException(400, 'Use the document assistant control.')
        try:
            return drafts.change(draft_id, body['revision'], body['request_id'], body['action'], body['args'])
        except StaleDraft as exc:
            raise HTTPException(409, str(exc)) from exc
        except (ValueError, VEError, SyntaxError) as exc:
            raise HTTPException(400, str(exc)) from exc

    @app.post('/api/drafts/{draft_id}/assist')
    async def assist_draft(draft_id: str, request: Request):
        csrf(request, session(request)['csrf'])
        body = await data(request)
        if set(body) != {'revision', 'request_id'} or type(body['request_id']) is not str:
            raise HTTPException(400, 'The request needs the revision. The request needs the request ID.')
        try:
            current = drafts.get(draft_id)
            if body['revision'] != current['revision']:
                raise StaleDraft('This document changed in another tab. Reload its latest revision.')
            reserved = drafts.change(draft_id, current['revision'], body['request_id'] + 'reserve',
                                     'proposer_reserve', {})
            if reserved['units'][0]['state'] == 'unresolved':
                return reserved
            if not reserved['history'] or reserved['history'][-1]['action'] != 'proposer_reserved':
                return reserved
        except StaleDraft as exc:
            raise HTTPException(409, str(exc)) from exc
        except (ValueError, VEError) as exc:
            raise HTTPException(400, str(exc)) from exc
        outcome = {'kind': 'failed', 'error': 'Unavailable'}
        if settings.assist:
            try:
                quota.reserve()
                async with busy:
                    result = await runner('propose', {'example': reserved['example'],
                                                      'text': reserved['units'][0]['source']}, settings)
                candidates = result.get('candidates', [])
                if candidates:
                    natural = candidates[0].get('natural', {}).get('sentences', [])
                    if natural and natural[0].get('form') == 'natural':
                        outcome = {'kind': 'suggestion', 'text': natural[0]['text'].rstrip('.') + '.'}
            except HTTPException as exc:
                outcome = {'kind': 'failed', 'error': 'CallAllowanceReached' if exc.status_code == 429 else 'Unavailable'}
            except Exception:
                outcome = {'kind': 'failed', 'error': 'Unavailable'}
        try:
            return drafts.change(draft_id, reserved['revision'], body['request_id'] + 'finish',
                                 'proposer_finish', {'outcome': outcome})
        except StaleDraft:
            return {'status': 'stale', 'reason': 'Assistant request superseded by a newer document revision.'}
        except (ValueError, VEError) as exc:
            raise HTTPException(400, str(exc)) from exc

    @app.get('/api/rules')
    async def rules_example(request: Request):
        session(request)
        return {'text': RULES_TEXT, 'result': check_rules(RULES_TEXT)}

    @app.post('/api/rules')
    async def rules_check(request: Request):
        csrf(request, session(request)['csrf'])
        body = await data(request)
        if set(body) != {'text'} or type(body['text']) is not str or len(body['text']) > 6000:
            raise HTTPException(400, 'Enter rules in English, up to 6000 characters.')
        try:
            return check_rules(body['text'])
        except (ValueError, VEError, SyntaxError) as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.post("/api/{action}")
    async def operate(action: str, request: Request):
        csrf(request, session(request)["csrf"])
        if action not in ("validate", "check", "propose"):
            raise HTTPException(404)
        body = await data(request)
        if set(body) - {"example", "text", "premises", "environment", "world"}:
            raise HTTPException(400, "The field is not known.")
        if not isinstance(body.get("example"), str) or body["example"] not in BY_ID:
            raise HTTPException(400, "The vocabulary is not known.")
        for field in ("text", "premises"):
            if field in body and (not isinstance(body[field], str) or len(body[field]) > 6000):
                raise HTTPException(400, f"{field} must be text of at most 6000 characters.")
        if action == "propose" and not body.get("text", "").strip():
            raise HTTPException(400, "The request needs the sentence.")
        if busy.locked():
            raise HTTPException(429, "Another operation is running. Try again shortly.")
        async with busy:
            if action == "propose":
                if not settings.assist:
                    raise HTTPException(503, "The assistant is disabled.")
                quota.reserve()
            result = await runner(action, body, settings)
        return JSONResponse(result, 422 if "error" in result else 200)

    return app
