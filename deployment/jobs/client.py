"""Hermes terminal interface: submit quickly, inspect status, cancel explicitly."""
from __future__ import annotations
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import time
import store

def channel():
    p = Path(os.environ.get('UNDERWRITER_CHANNEL', '/job-channel/telegram.json'))
    return json.loads(p.read_text()) if p.exists() else {}

def destination(explicit, offline):
    if offline:
        return None
    platform = os.environ.get('HERMES_SESSION_PLATFORM')
    chat = os.environ.get('HERMES_SESSION_CHAT_ID')
    if platform:
        if platform != 'telegram' or not chat or not re.fullmatch(r'[0-9]+', chat):
            raise ValueError('This prototype delivers only to the originating private Telegram chat')
        if explicit and explicit != chat:
            raise ValueError('Cannot override the originating chat')
    else:
        chat = explicit
    cfg = channel()
    if not chat or chat not in cfg.get('allowed_users', []):
        raise ValueError('Private chat is not configured for delivery; use --offline for an explicit local test')
    return chat

def submit(args):
    if not re.fullmatch(r'[a-z][a-z0-9_]*',args.asset_class):
        raise ValueError('Invalid asset class identifier')
    tape = store.allowed_source(args.tape)
    if tape.suffix.lower() not in ('.xlsx','.xlsm','.xls'):
        raise ValueError('Extract the ZIP first and select an Excel tape')
    if args.as_of:
        datetime.date.fromisoformat(args.as_of)
    for value in (args.originator, args.deal):
        if value and not re.fullmatch(r'[a-z0-9][a-z0-9_-]*',value):
            raise ValueError('Invalid originator or deal name')
    if args.deal_config and not args.deal:
        raise ValueError('--deal-config requires --deal')
    if args.config and args.deal_config:
        raise ValueError('Use --config or --deal-config, not both')
    configs = {}
    if args.config:
        base = store.allowed_source(args.config)
        if not base.is_dir():
            raise ValueError('Config must be a directory')
        for p in base.rglob('*'):
            if p.is_symlink():
                raise ValueError('Symlink config rejected')
            if p.is_file():
                if p.suffix.lower() not in ('.yaml','.yml'):
                    continue
                store.allowed_source(p)
                configs[p.relative_to(base).as_posix()] = str(p)
        if 'global.yaml' not in configs:
            raise ValueError('Full configuration requires global.yaml')
    elif args.deal_config:
        configs['deals/'+args.deal+'.yaml'] = str(store.allowed_source(args.deal_config))
    if len(configs) > 500:
        raise ValueError('Too many config files')
    request = {'schema_version':1, 'asset_class':args.asset_class, 'tape': str(tape), 'tape_sha256':store.digest(tape),
               'config_hashes':{k:store.digest(v) for k,v in configs.items()},
               'custom_config':bool(args.config), 'deal':args.deal,
               'originator':args.originator, 'as_of':args.as_of, 'sheet':args.sheet,
               'profile':args.profile, 'no_ai':args.no_ai, 'inspect_only':getattr(args,'inspect_only',False),
               'chat_id':destination(args.chat_id,args.offline), 'parent_job':args.parent_job}
    if args.parent_job:
        parent=store.status(args.parent_job)
        if parent['state'] not in store.TERMINAL:
            raise ValueError('Previous attempt is still active')
    job_id, created = store.reserve(args.request_key,request)
    if not created:
        return store.status(job_id)
    target = store.job_dir(job_id)
    try:
        manifest={'request':request,'tape':store.snapshot_file(tape,target/'input'/('tape'+tape.suffix.lower())),
                  'config':{}}
        for relative, source in configs.items():
            manifest['config'][relative] = store.snapshot_file(source,target/'submitted-config'/relative,5*1024*1024)
        if manifest['tape']['sha256'] != request['tape_sha256'] or any(
            v['sha256'] != request['config_hashes'][k] for k,v in manifest['config'].items()):
            raise ValueError('Inputs changed between hashing and snapshot')
        (target/'input-manifest.json').write_text(store.encode(manifest),encoding='utf-8')
        store.update(job_id,'queued','queued')
    except Exception as exc:
        store.update(job_id,'failed','submission_failed',{'reason':str(exc)})
        raise
    return store.status(job_id)

def main():
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest='command',required=True)
    s=sub.add_parser('submit')
    s.add_argument('tape')
    s.add_argument('--asset-class',required=True,help='Installed engine plug-in, currently mca')
    s.add_argument('--request-key',required=True,help='Stable per-request key; reuse after an uncertain submission')
    for name in ('config','deal-config','deal','originator','as-of','sheet','chat-id','parent-job'):
        s.add_argument('--'+name)
    s.add_argument('--profile',choices=['internal','external'],default='internal')
    s.add_argument('--no-ai',action='store_true',help='Explicitly limited deterministic test')
    s.add_argument('--offline',action='store_true',help='Save outputs without Telegram delivery')
    s.add_argument('--inspect-only',action='store_true',help='Inspect tape layout without analysis or AI')
    for command in ('status','cancel'):
        sub.add_parser(command).add_argument('job_id')
    sub.add_parser('list')
    sub.add_parser('health')
    args=p.parse_args()
    if args.command=='submit':
        result=submit(args)
    elif args.command=='status':
        result=store.status(args.job_id)
    elif args.command=='cancel':
        state=store.status(args.job_id)
        if state['state'] not in store.TERMINAL:
            with store.connect() as db:
                db.execute('UPDATE jobs SET cancel=1 WHERE id=?',(args.job_id,))
        result=store.status(args.job_id)
    elif args.command=='health':
        with store.connect() as db:
            result=[dict(r) for r in db.execute('SELECT * FROM health')]
        for r in result:
            r['age_seconds']=round(time.time()-r['updated'])
            r['details']=json.loads(r['details'])
    else:
        with store.connect() as db:
            result=[dict(r) for r in db.execute('SELECT id,state,stage,created,updated FROM jobs ORDER BY created DESC LIMIT 20')]
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    try:
        main()
    except (ValueError,OSError) as exc:
        raise SystemExit(str(exc))
