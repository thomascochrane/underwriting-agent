"""Run Hermes' Google CLI using the explicitly mounted Agents identity."""
import os
from pathlib import Path
import sys

ROOT = Path("/google-agents")
SCRIPT = Path("/opt/hermes/skills/productivity/google-workspace/scripts/google_api.py")
if not (ROOT / "google_token.json").is_file():
    raise SystemExit("Agents Google connection is not authorized. Open https://zamisla.com/google/agents/ to connect agents@zivoe.com.")
os.environ["HERMES_HOME"] = str(ROOT)
os.execv(sys.executable, [sys.executable, str(SCRIPT), *sys.argv[1:]])
