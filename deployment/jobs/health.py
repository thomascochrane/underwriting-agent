"""Read-only Docker heartbeat check; no network/provider calls."""
import os
from pathlib import Path
import sqlite3
import sys
import time

path=Path(os.environ.get('UNDERWRITER_JOBS','/jobs'))/'jobs.sqlite3'
try:
    db=sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True,timeout=5)
    row=db.execute('SELECT updated FROM health WHERE service=?',(sys.argv[1],)).fetchone()
    db.close()
    raise SystemExit(0 if row and time.time()-row[0]<180 else 1)
except sqlite3.Error:
    raise SystemExit(1)
