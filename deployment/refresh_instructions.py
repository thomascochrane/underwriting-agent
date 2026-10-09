"""Update recognized base instructions while preserving owner customization."""
import hashlib
import os
from pathlib import Path
import shutil

home=Path(os.environ.get('HERMES_HOME','/opt/data'))
target=home/'SOUL.md'; source=Path('/deployment/SOUL.md')
known={
    'd823d12e790e329043a7ddb8f8258108fbba498291f392998385ec37169cf79d',
    '9a5efb19de3a15ba9a866e6c8c8db475fd893f9b669ddd568737d88a9d4e74dd',
}
current=target.read_bytes()
digest=hashlib.sha256(current).hexdigest()
if current==source.read_bytes():
    print('Instructions already current.')
elif digest not in known:
    raise SystemExit('Existing instructions were customized; preserve and reconcile them explicitly.')
else:
    backup=home/('SOUL.before-update-'+digest[:12]+'.md')
    if backup.exists() and backup.read_bytes()!=current:
        raise SystemExit('Instruction backup conflict; nothing overwritten.')
    if not backup.exists(): shutil.copyfile(target,backup)
    shutil.copyfile(source,target)
    print('Current base guidance installed; previous instructions retained.')
