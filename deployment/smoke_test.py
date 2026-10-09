"""Offline deployment smoke tests; never use the real credential volume."""
import contextlib
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import runtime


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self.env = patch.multiple(runtime, HOME=self.home, MARKER=self.home / ".initialized")
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def initialize(self):
        with contextlib.redirect_stdout(io.StringIO()):
            runtime.initialize()

    def test_fresh_setup_and_repeat_preserve_user_changes(self):
        # Upstream seeds an empty gateway block and a different model provider.
        (self.home / "config.yaml").write_text(
            "gateway: null\nmodel:\n  provider: auto\n  base_url: https://example.invalid\n",
            encoding="utf-8",
        )
        self.initialize()
        cfg = runtime.yaml.safe_load((self.home / "config.yaml").read_text())
        self.assertEqual(cfg["model"]["provider"], "openai-codex")
        self.assertNotIn("base_url", cfg["model"])
        self.assertEqual(cfg["terminal"]["cwd"], "/workspace")
        env = runtime.dotenv_values(self.home / ".env")
        self.assertEqual(env["API_SERVER_ENABLED"], "false")
        self.assertEqual(env["TELEGRAM_ALLOW_ALL_USERS"], "false")
        # Emulate later user config and saved credentials, then initialize again.
        (self.home / "config.yaml").write_text("model: {provider: user-choice}\n")
        (self.home / "auth.json").write_text('{"test": "preserve-me"}')
        (self.home / "SOUL.md").write_text("User customization")
        before = {p.name: p.read_bytes() for p in self.home.iterdir() if p.is_file()}
        self.initialize()
        after = {p.name: p.read_bytes() for p in self.home.iterdir() if p.is_file()}
        self.assertEqual(before, after)

    def test_readiness_fails_closed_then_accepts_explicit_users(self):
        self.initialize()
        with patch.object(runtime, "codex_logged_in", return_value=False):
            state = runtime.readiness()
            self.assertFalse(state["chatgpt_logged_in"])
            self.assertFalse(state["telegram_token_present"])
            self.assertFalse(state["telegram_users_configured"])
        runtime.set_key(str(self.home / ".env"), "TELEGRAM_BOT_TOKEN", "123456:offline_test_token")
        runtime.set_key(str(self.home / ".env"), "TELEGRAM_ALLOWED_USERS", "*")
        with patch.object(runtime, "codex_logged_in", return_value=True):
            self.assertFalse(runtime.readiness()["telegram_users_configured"])
            runtime.set_key(str(self.home / ".env"), "TELEGRAM_ALLOWED_USERS", "123,456")
            state = runtime.readiness()
            self.assertTrue(all(state.values()), state)

    def test_invalid_telegram_input_writes_nothing(self):
        self.initialize()
        before = (self.home / ".env").read_bytes()
        with patch.object(runtime.getpass, "getpass", return_value="invalid"):
            with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
                runtime.configure_telegram()
        self.assertEqual((self.home / ".env").read_bytes(), before)

    def test_gateway_refuses_missing_credentials(self):
        self.initialize()
        with patch.object(runtime, "codex_logged_in", return_value=False), \
             patch("sys.argv", ["runtime.py", "gateway"]), \
             patch.object(runtime.os, "execvp") as launch, \
             contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as failure:
                runtime.main()
        self.assertEqual(failure.exception.code, 78)
        launch.assert_not_called()


if __name__ == "__main__":
    unittest.main()