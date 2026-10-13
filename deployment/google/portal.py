"""Dedicated Agents OAuth endpoint, following Zamisla's hosted OAuth pattern.

Only publish through the authenticated Cloudflare tunnel; the socket is loopback
on the host. Application credentials and authorized-user tokens never enter Git.
"""
from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import secrets
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

PREFIX = "/google/agents"
ORIGIN = "https://zamisla.com"
CALLBACK = ORIGIN + PREFIX + "/callback"
ACCOUNT = "agents@zivoe.com"
SCOPES = (
    "openid", "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
)
TOKEN_URI = "https://oauth2.googleapis.com/token"


class ConnectionError(ValueError):
    pass


def private_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.with_name(path.name + "." + secrets.token_hex(8) + ".tmp")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(data, stream)
    os.replace(temporary, path)


def request_json(url, form=None, bearer=None):
    headers = {"Accept": "application/json"}
    data = None
    if form is not None:
        data = urllib.parse.urlencode(form).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if bearer:
        headers["Authorization"] = "Bearer " + bearer
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers), timeout=25) as response:
            result = json.loads(response.read(1024 * 1024))
        if not isinstance(result, dict):
            raise ValueError()
        return result
    except (OSError, ValueError, urllib.error.URLError):
        # Never reflect Google's response or request URLs: they may contain codes.
        raise ConnectionError("Google could not complete the request. Please start again.") from None


class Portal:
    def __init__(self, root, operator, transport=request_json, now=time.time):
        self.root = Path(root)
        self.operator = operator.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+", self.operator):
            raise ValueError("GOOGLE_ACCESS_EMAIL must name the connection administrator")
        self.transport = transport
        self.now = now
        self.lock = threading.Lock()

    def require_operator(self, headers):
        value = headers.get("Cf-Access-Authenticated-User-Email", "").strip().lower()
        if not hmac.compare_digest(value, self.operator):
            raise ConnectionError("This connection is restricted to its administrator.")

    def client(self):
        try:
            web = json.loads((self.root / "google_client_secret.json").read_text())["web"]
            if not web.get("client_id") or not web.get("client_secret") or CALLBACK not in web.get("redirect_uris", []):
                raise ValueError()
            # Endpoints are constants, never taken from an uploaded credential file.
            return web
        except (OSError, ValueError, KeyError, TypeError):
            raise ConnectionError("The Agents Web OAuth client has not been installed with the correct callback yet.") from None

    def status(self):
        try:
            self.client()
            configured = True
        except ConnectionError:
            configured = False
        return {"client_configured": configured, "token_present": (self.root / "google_token.json").is_file(), "account": ACCOUNT}

    def start(self):
        client = self.client()
        state = secrets.token_urlsafe(32)
        verifier = secrets.token_urlsafe(64)
        digest = hashlib.sha256(state.encode()).hexdigest()
        directory = self.root / ".pending"
        with self.lock:
            directory.mkdir(mode=0o700, parents=True, exist_ok=True)
            for stale in directory.glob("*.json"):
                if self.now() - stale.stat().st_mtime > 1200:
                    stale.unlink(missing_ok=True)
            private_json(directory / (digest + ".json"), {
                "expires": self.now() + 600, "verifier": verifier,
                "client_id": client["client_id"], "operator": self.operator,
            })
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        return "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
            "client_id": client["client_id"], "redirect_uri": CALLBACK,
            "response_type": "code", "scope": " ".join(SCOPES),
            "state": state, "code_challenge": challenge, "code_challenge_method": "S256",
            "access_type": "offline", "prompt": "consent select_account", "login_hint": ACCOUNT,
        })

    def finish(self, state, code):
        if not re.fullmatch(r"[A-Za-z0-9_-]{43}", state) or not code or len(code) > 8192:
            raise ConnectionError("Invalid authorization response. Please start again.")
        pending_path = self.root / ".pending" / (hashlib.sha256(state.encode()).hexdigest() + ".json")
        with self.lock:
            try:
                pending = json.loads(pending_path.read_text())
                pending_path.unlink()  # Consume once, before any network request.
            except (OSError, ValueError):
                raise ConnectionError("This sign-in expired or was already used. Please start again.") from None
        client = self.client()
        if pending["expires"] < self.now() or pending["operator"] != self.operator or pending["client_id"] != client["client_id"]:
            raise ConnectionError("This sign-in expired or its configuration changed. Please start again.")
        token = self.transport(TOKEN_URI, form={
            "grant_type": "authorization_code", "code": code,
            "client_id": client["client_id"], "client_secret": client["client_secret"],
            "redirect_uri": CALLBACK, "code_verifier": pending["verifier"],
        })
        if not isinstance(token.get("access_token"), str) or not token["access_token"]:
            raise ConnectionError("Google did not return an access token.")
        identity = self.transport("https://openidconnect.googleapis.com/v1/userinfo", bearer=token["access_token"])
        if identity.get("email_verified") is not True or str(identity.get("email", "")).lower() != ACCOUNT:
            raise ConnectionError("Please sign in with agents@zivoe.com. The existing connection was not changed.")
        granted = set(str(token.get("scope", "")).split())
        if not set(SCOPES).issubset(granted):
            raise ConnectionError("Not all requested permissions were granted. The existing connection was not changed.")
        # Require a fresh offline grant; never merge tokens from different clients.
        if not isinstance(token.get("refresh_token"), str) or not token["refresh_token"]:
            raise ConnectionError("Google did not grant offline access. Please reconnect and approve access.")
        expiry = datetime.now(timezone.utc) + timedelta(seconds=int(token.get("expires_in", 3600)))
        private_json(self.root / "google_token.json", {
            "type": "authorized_user", "token": token["access_token"],
            "refresh_token": token["refresh_token"], "token_uri": TOKEN_URI,
            "client_id": client["client_id"], "client_secret": client["client_secret"],
            "scopes": sorted(granted), "expiry": expiry.isoformat().replace("+00:00", "Z"),
            "account": ACCOUNT, "universe_domain": "googleapis.com",
        })


def handler_for(portal):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass  # Callback query strings contain authorization codes.

        def reply(self, status, body, location=None):
            payload = body.encode()
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'")
            if location:
                self.send_header("Location", location)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def page(self, message=""):
            status = portal.status()
            state = "Authorization saved. API access still needs verification." if status["token_present"] else "Not connected yet."
            setup = "" if status["client_configured"] else "The OAuth client is awaiting installation."
            button = '<form method="post" action="' + PREFIX + '/connect"><button>Connect agents@zivoe.com</button></form>' if status["client_configured"] else ""
            self.reply(200, '<!doctype html><html><head><meta name="viewport" content="width=device-width"><title>Zivoe Agents · Google connection</title><style>body{font:18px system-ui;max-width:680px;margin:10vh auto;padding:24px;color:#182e29}button{font:inherit;padding:14px;border:0;border-radius:8px;background:#164f43;color:white}p{line-height:1.6}</style></head><body><h1>Zivoe Agents</h1><h2>Google Workspace connection</h2><p>Shared account: <strong>agents@zivoe.com</strong></p><p>' + html.escape(message or state) + '</p><p>' + setup + '</p><p>Connect Gmail, Drive, Docs, and Sheets. Drive access is limited to files shared with this account. Only applications explicitly given this connection can use it.</p>' + button + '</body></html>')

        def do_GET(self):
            parsed = urllib.parse.urlsplit(self.path)
            if parsed.path == "/healthz":
                self.reply(200, "ok")
                return
            try:
                portal.require_operator(self.headers)
            except ConnectionError as error:
                self.reply(403, html.escape(str(error)))
                return
            try:
                if parsed.path in (PREFIX, PREFIX + "/"):
                    self.page()
                elif parsed.path == PREFIX + "/callback":
                    query = urllib.parse.parse_qs(parsed.query, max_num_fields=20)
                    if "error" in query:
                        self.reply(303, "", PREFIX + "/")
                        return
                    portal.finish(query.get("state", [""])[0], query.get("code", [""])[0])
                    self.reply(303, "", PREFIX + "/")
                else:
                    self.reply(404, "Not found")
            except ConnectionError as error:
                self.reply(400, html.escape(str(error)))
            except Exception:
                self.reply(500, "Connection could not be completed. Please restart sign-in.")

        def do_POST(self):
            try:
                portal.require_operator(self.headers)
                if self.headers.get("Origin") != ORIGIN:
                    raise ConnectionError("Invalid connection request origin.")
                if self.path != PREFIX + "/connect":
                    self.reply(404, "Not found")
                    return
                # The empty form carries no credentials; reject oversized requests.
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 <= length <= 1024:
                    raise ConnectionError("Invalid connection request size.")
                self.rfile.read(length)
                self.reply(303, "", portal.start())
            except ConnectionError as error:
                self.reply(403, html.escape(str(error)))
            except Exception:
                self.reply(500, "Connection could not be started. Please try again.")
    return Handler


if __name__ == "__main__":
    portal = Portal(os.environ.get("GOOGLE_AGENTS_HOME", "/google-agents"), os.environ["GOOGLE_ACCESS_EMAIL"])
    server = ThreadingHTTPServer(("0.0.0.0", 8766), handler_for(portal))
    server.serve_forever()
