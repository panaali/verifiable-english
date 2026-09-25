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
import sys
import time
from dataclasses import dataclass
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from .examples import EXAMPLES, BY_ID

STATIC = Path(__file__).parent / "static"
MAX_BODY = 32768


@dataclass
class Settings:
    token: str
    state: Path
    secure: bool = True
    assist: bool = False
    model: str = "haiku"
    minute_cap: int = 3
    daily_cap: int = 30

    def __post_init__(self):
        if len(self.token) < 32:
            raise ValueError("Access token must contain at least 32 characters; generate a random token.")
        self.state = self.state.resolve()
        self.state.mkdir(parents=True, exist_ok=True, mode=0o700)
        if self.minute_cap < 1 or self.daily_cap < 1:
            raise ValueError("Call caps must be positive.")


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
               "config": {"state": str(settings.state), "model": settings.model}}
    # Access token stays in the web process. CLI uses its own configured account.
    env = {k: v for k, v in os.environ.items() if k not in ("VE_WEB_TOKEN", "VE_WEB_TOKEN_FILE")}
    process = await asyncio.create_subprocess_exec(sys.executable, "-m", "ve_webapp.worker",
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL,
        env=env, start_new_session=True)
    try:
        raw, _ = await asyncio.wait_for(process.communicate(json.dumps(payload).encode()),
                                       timeout=50 if action == "propose" else 8)
        if process.returncode or len(raw) > 2_000_000:
            raise HTTPException(503, "Operation could not complete.")
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
    busy = asyncio.Lock()

    def session(request):
        sid = request.cookies.get("ve_session", "")
        value = sessions.get(sid)
        if not value or value["expires"] < time.time():
            sessions.pop(sid, None)
            raise HTTPException(401, "Please sign in.")
        return value

    def csrf(request, expected=None):
        origin = request.headers.get("origin")
        if origin and origin != f"{request.url.scheme}://{request.url.netloc}":
            raise HTTPException(403, "Cross-origin request rejected.")
        if request.headers.get("sec-fetch-site") == "cross-site":
            raise HTTPException(403, "Cross-site request rejected.")
        supplied = request.headers.get("x-ve-csrf", "")
        if not hmac.compare_digest(supplied, expected or "login"):
            raise HTTPException(403, "Missing or invalid CSRF header.")
        if request.headers.get("content-type", "").split(";")[0] != "application/json":
            raise HTTPException(415, "Use application/json.")

    async def data(request):
        try:
            body = await request.json()
        except (ValueError, UnicodeError):
            raise HTTPException(400, "Invalid JSON.")
        if not isinstance(body, dict):
            raise HTTPException(400, "Expected an object.")
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
            raise HTTPException(401, "Access token not recognised.")
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

    @app.post("/api/{action}")
    async def operate(action: str, request: Request):
        csrf(request, session(request)["csrf"])
        if action not in ("validate", "check", "propose"):
            raise HTTPException(404)
        body = await data(request)
        if set(body) - {"example", "text", "premises", "environment", "world"}:
            raise HTTPException(400, "Unknown request field.")
        if not isinstance(body.get("example"), str) or body["example"] not in BY_ID:
            raise HTTPException(400, "Choose a known example vocabulary.")
        for field in ("text", "premises"):
            if field in body and (not isinstance(body[field], str) or len(body[field]) > 6000):
                raise HTTPException(400, f"{field} must be text of at most 6000 characters.")
        if action == "propose" and not body.get("text", "").strip():
            raise HTTPException(400, "Enter a sentence.")
        if busy.locked():
            raise HTTPException(429, "Another operation is running. Try again shortly.")
        async with busy:
            if action == "propose":
                if not settings.assist:
                    raise HTTPException(503, "Live assistance is disabled by the server administrator.")
                quota.reserve()
            result = await runner(action, body, settings)
        return JSONResponse(result, 422 if "error" in result else 200)

    return app
