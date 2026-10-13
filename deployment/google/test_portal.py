import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer

from portal import ACCOUNT, CALLBACK, ConnectionError, ORIGIN, Portal, SCOPES, handler_for, private_json


class OAuthTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.clock = 1000
        self.email = ACCOUNT
        self.scopes = " ".join(SCOPES)
        self.calls = []
        private_json(self.root / "google_client_secret.json", {"web": {
            "client_id": "test-client", "client_secret": "test-secret",
            "redirect_uris": [CALLBACK]}})
        self.portal = Portal(self.root, "admin@example.com", self.transport, lambda: self.clock)

    def transport(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if "userinfo" in url:
            return {"email": self.email, "email_verified": True}
        return {"access_token": "test-token", "refresh_token": "test-refresh", "scope": self.scopes, "expires_in": 3600}

    def start(self):
        return urllib.parse.parse_qs(urllib.parse.urlsplit(self.portal.start()).query)

    def test_success_persistent_hermes_token_and_pkce(self):
        query = self.start()
        self.assertEqual(query["redirect_uri"], [CALLBACK])
        self.assertEqual(query["login_hint"], [ACCOUNT])
        self.assertEqual(query["code_challenge_method"], ["S256"])
        self.portal.finish(query["state"][0], "code")
        data = json.loads((self.root / "google_token.json").read_text())
        self.assertEqual(data["account"], ACCOUNT)
        self.assertEqual(data["type"], "authorized_user")
        self.assertIn("code_verifier", self.calls[0][1]["form"])

    def test_wrong_account_does_not_replace_existing_token(self):
        path = self.root / "google_token.json"
        path.write_text('{"preserved": true}')
        self.email = "personal@example.com"
        with self.assertRaises(ConnectionError):
            self.portal.finish(self.start()["state"][0], "code")
        self.assertEqual(json.loads(path.read_text()), {"preserved": True})

    def test_partial_scope_grant_not_saved(self):
        self.scopes = "openid"
        with self.assertRaises(ConnectionError):
            self.portal.finish(self.start()["state"][0], "code")
        self.assertFalse((self.root / "google_token.json").exists())

    def test_expired_state_rejected_before_exchange(self):
        state = self.start()["state"][0]
        self.clock += 601
        with self.assertRaises(ConnectionError):
            self.portal.finish(state, "code")
        self.assertFalse(self.calls)

    def test_replay_rejected(self):
        state = self.start()["state"][0]
        self.portal.finish(state, "code")
        with self.assertRaises(ConnectionError):
            self.portal.finish(state, "code")
        self.assertEqual(len(self.calls), 2)

    def test_mismatched_client_rejected(self):
        state = self.start()["state"][0]
        path = self.root / "google_client_secret.json"
        client = json.loads(path.read_text())
        client["web"]["client_id"] = "another-client"
        private_json(path, client)
        with self.assertRaises(ConnectionError):
            self.portal.finish(state, "code")
        self.assertFalse(self.calls)

    def test_operator_identity_required(self):
        for headers in ({}, {"Cf-Access-Authenticated-User-Email": "someone@example.com"}):
            with self.assertRaises(ConnectionError):
                self.portal.require_operator(headers)
        self.portal.require_operator({"Cf-Access-Authenticated-User-Email": "ADMIN@example.com"})

    def test_callback_must_be_registered(self):
        private_json(self.root / "google_client_secret.json", {"web": {"client_id": "a", "client_secret": "b", "redirect_uris": [ORIGIN + "/wrong"]}})
        self.assertFalse(self.portal.status()["client_configured"])

    def test_http_access_and_csrf(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler_for(self.portal))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        base = "http://127.0.0.1:" + str(server.server_port)
        with urllib.request.urlopen(base + "/healthz") as response:
            self.assertEqual(response.status, 200)
        with self.assertRaises(urllib.error.HTTPError) as denied:
            urllib.request.urlopen(base + "/google/agents/")
        self.assertEqual(denied.exception.code, 403)
        headers = {"Cf-Access-Authenticated-User-Email": "admin@example.com"}
        with urllib.request.urlopen(urllib.request.Request(base + "/google/agents/", headers=headers)) as response:
            self.assertIn(b"Connect Google Workspace", response.read())
            self.assertEqual(response.headers["Cache-Control"], "no-store")
        with self.assertRaises(urllib.error.HTTPError) as denied:
            urllib.request.urlopen(urllib.request.Request(base + "/google/agents/connect", data=b"", headers={**headers, "Origin": "https://wrong.example"}))
        self.assertEqual(denied.exception.code, 403)


if __name__ == "__main__":
    unittest.main()
