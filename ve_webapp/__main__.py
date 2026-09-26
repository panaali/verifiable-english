"""uv run python -m ve_webapp --cert ... --key ..."""
import argparse
import os
from pathlib import Path
import uvicorn
from .server import Settings, create_app


def main():
    p = argparse.ArgumentParser(description="VE writing desk (HTTPS by default)")
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=8443)
    p.add_argument("--cert", default=os.getenv("VE_WEB_CERT"))
    p.add_argument("--key", default=os.getenv("VE_WEB_KEY"))
    p.add_argument("--http", action="store_true", help="Allow plain HTTP on 127.0.0.1 only")
    p.add_argument("--token-file", default=os.getenv("VE_WEB_TOKEN_FILE"))
    p.add_argument("--state-dir", type=Path, default=Path(".webapp-private"))
    p.add_argument("--assist", action="store_true", help="Enable subscription-spending Claude assistance")
    p.add_argument("--model", choices=("haiku", "sonnet", "opus"), default="haiku")
    p.add_argument("--claude-cli-version", help="Expected output of claude --version (detected at startup by default)")
    p.add_argument("--minute-cap", type=int, default=3)
    p.add_argument("--daily-cap", type=int, default=30)
    args = p.parse_args()
    if not 1024 <= args.port <= 65535:
        p.error("Use an unprivileged port from 1024 to 65535.")
    if args.http:
        if args.host != "127.0.0.1" or args.cert or args.key:
            p.error("Plain HTTP requires --host 127.0.0.1 and no TLS arguments.")
    elif not args.cert or not args.key:
        p.error("HTTPS requires --cert and --key (or VE_WEB_CERT / VE_WEB_KEY).")
    token = Path(args.token_file).read_text().strip() if args.token_file else os.getenv("VE_WEB_TOKEN", "")
    os.umask(0o077)
    try:
        settings = Settings(token, args.state_dir, not args.http, args.assist, args.model,
                            args.minute_cap, args.daily_cap, args.claude_cli_version)
    except ValueError as exc:
        p.error(str(exc))
    uvicorn.run(create_app(settings), host=args.host, port=args.port, ssl_certfile=args.cert,
                ssl_keyfile=args.key, access_log=False, proxy_headers=False, limit_concurrency=32,
                timeout_keep_alive=5)


if __name__ == "__main__":
    main()
