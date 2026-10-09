"""Apply the known base-prompt update, preserving any owner customization."""
import hashlib
import os
from pathlib import Path
import shutil

home=Path(os.environ.get('HERMES_HOME','/opt/data'))
target=home/'SOUL.md'; source=Path('/deployment/SOUL.md')
old='d823d12e790e329043a7ddb8f8258108fbba498291f392998385ec37169cf79d'
if target.read_bytes()==source.read_bytes():
    print('Instructions already current.')
elif hashlib.sha256(target.read_bytes()).hexdigest()!=old:
    raise SystemExit('Existing instructions were customized; preserve them and reconcile the engine-job guidance explicitly.')
else:
    backup=home/'SOUL.before-engine-jobs.md'
    if not backup.exists(): shutil.copyfile(target,backup)
    shutil.copyfile(source,target)
    print('Engine-job guidance installed; previous instructions retained.')
