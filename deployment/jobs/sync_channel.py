"""Publish only this agent's Telegram credentials to the delivery service."""
import json
import os
from pathlib import Path
import re
from dotenv import dotenv_values

def sync():
    destination=Path('/job-channel')
    if not destination.is_dir():
        print('Job delivery overlay is not mounted; nothing exported.')
        return
    env=dotenv_values(Path(os.environ.get('HERMES_HOME','/opt/data'))/'.env')
    token=env.get('TELEGRAM_BOT_TOKEN','') or ''
    users=[x.strip() for x in (env.get('TELEGRAM_ALLOWED_USERS','') or '').split(',') if x.strip().isdigit()]
    configured=bool(re.fullmatch(r'[0-9]+:[A-Za-z0-9_-]+',token) and users)
    value={'token':token,'allowed_users':users} if configured else {}
    path=destination/'telegram.json'
    temp=destination/'telegram.json.tmp'
    fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
    with os.fdopen(fd,'w') as f:
        json.dump(value,f)
    os.chmod(temp,0o600)
    # Official image maintenance commands may run as root before dropping privileges.
    if os.geteuid()==0:
        os.chown(temp,10000,10000)
    temp.replace(path)
    print('Job Telegram delivery configured.' if configured else 'Job Telegram delivery awaits credentials.')

if __name__=='__main__':
    sync()
