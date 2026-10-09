"""Independent Telegram outbox. An uncertain send is never blindly repeated."""
from __future__ import annotations
import argparse
import fcntl
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request
import uuid
import store

CHANNEL=Path(os.environ.get('UNDERWRITER_CHANNEL','/job-channel/telegram.json'))
MAX_FILE=49*1024*1024

class DeliveryError(Exception):
    def __init__(self,state,reason,delay=0):
        self.state=state; self.reason=reason; self.delay=delay

def credentials():
    return json.loads(CHANNEL.read_text()) if CHANNEL.exists() else {}

def send(token,kind,payload):
    """Return Telegram's receipt; do not log token-bearing URLs or exception strings."""
    if kind=='summary':
        method='sendMessage'
        body=json.dumps({'chat_id':payload['chat_id'],'text':payload['text'][:4000]}).encode()
        content_type='application/json'
    else:
        path=Path(payload['path'])
        if not path.resolve().is_relative_to(store.ROOT.resolve()) or path.is_symlink():
            raise DeliveryError('failed','Invalid artifact path')
        if not path.is_file() or store.digest(path)!=payload['sha256']:
            raise DeliveryError('failed','Artifact is missing or changed')
        if path.stat().st_size>MAX_FILE:
            raise DeliveryError('failed','Artifact exceeds the current Telegram upload limit; files remain on server')
        boundary='underwriter'+uuid.uuid4().hex
        parts=[]
        for name in ('chat_id','caption'):
            parts.append(('--'+boundary+'\r\nContent-Disposition: form-data; name="'+name+'"\r\n\r\n'+payload[name]+'\r\n').encode())
        parts.append(('--'+boundary+'\r\nContent-Disposition: form-data; name="document"; filename="results.zip"\r\nContent-Type: application/zip\r\n\r\n').encode())
        parts.extend([path.read_bytes(),('\r\n--'+boundary+'--\r\n').encode()])
        body=b''.join(parts); method='sendDocument'; content_type='multipart/form-data; boundary='+boundary
    req=urllib.request.Request('https://api.telegram.org/bot'+token+'/'+method,
                               data=body,headers={'Content-Type':content_type})
    try:
        with urllib.request.urlopen(req,timeout=120) as response:
            data=json.load(response)
    except urllib.error.HTTPError as exc:
        try:
            data=json.loads(exc.read())
        except Exception:
            data={}
        finally:
            exc.close()
        code=exc.code
        if code==429:
            raise DeliveryError('retry','Telegram rate limit',max(5,min(3600,int(data.get('parameters',{}).get('retry_after',60)))))
        if code in (400,401,403,404,413):
            raise DeliveryError('failed','Telegram rejected delivery (HTTP '+str(code)+')')
        raise DeliveryError('uncertain','Telegram server error; acceptance is unknown')
    except Exception:
        raise DeliveryError('uncertain','No reliable Telegram receipt; verify chat before retrying')
    if not data.get('ok'):
        if data.get('error_code')==429:
            raise DeliveryError('retry','Telegram rate limit',60)
        raise DeliveryError('failed','Telegram rejected delivery')
    result=data.get('result',{})
    if not result.get('message_id') or str(result.get('chat',{}).get('id'))!=payload['chat_id']:
        raise DeliveryError('uncertain','Missing or inconsistent Telegram receipt')
    return {'message_id':result['message_id'],'chat_id':str(result['chat']['id']),'confirmed_at':time.time()}

def recover():
    with store.connect() as db:
        db.execute("UPDATE deliveries SET state='uncertain',error='Notifier restarted during send; verify chat before retrying' WHERE state='sending'")

def tick(transport=send):
    cfg=credentials()
    store.heartbeat('notifier',{'configured':bool(cfg.get('token') and cfg.get('allowed_users'))})
    if not cfg.get('token'):
        return False
    with store.connect() as db:
        db.execute('BEGIN IMMEDIATE')
        row=db.execute("SELECT * FROM deliveries WHERE state IN ('pending','retry') AND next_at<=? ORDER BY id LIMIT 1",(time.time(),)).fetchone()
        if not row:
            return False
        row=dict(row); payload=json.loads(row['payload'])
        # Restrict independently from the requesting agent: private conversations only.
        if not payload['chat_id'].isdigit() or payload['chat_id'] not in cfg.get('allowed_users',[]):
            db.execute("UPDATE deliveries SET state='failed',error='Destination is not an allowed private chat' WHERE id=?",(row['id'],))
            return True
        if row['kind']=='artifact':
            parent=db.execute("SELECT state FROM deliveries WHERE job_id=? AND kind='summary'",(row['job_id'],)).fetchone()
            if parent and parent['state']!='sent':
                db.execute('UPDATE deliveries SET next_at=? WHERE id=?',(time.time()+30,row['id']))
                return True
        db.execute("UPDATE deliveries SET state='sending',attempts=attempts+1 WHERE id=?",(row['id'],))
    try:
        receipt=transport(cfg['token'],row['kind'],payload)
        with store.connect() as db:
            db.execute("UPDATE deliveries SET state='sent',receipt=?,error=NULL WHERE id=?",(store.encode(receipt),row['id']))
    except DeliveryError as exc:
        state=exc.state
        if state=='retry' and row['attempts']>=5:
            state='failed'
        with store.connect() as db:
            db.execute('UPDATE deliveries SET state=?,error=?,next_at=? WHERE id=?',
                       (state,exc.reason,time.time()+max(exc.delay,2**min(row['attempts'],8)),row['id']))
    except Exception:
        with store.connect() as db:
            db.execute("UPDATE deliveries SET state='uncertain',error='Unexpected failure during send; verify chat' WHERE id=?",(row['id'],))
    return True

def retry(delivery_id,acknowledge):
    with store.connect() as db:
        row=db.execute('SELECT * FROM deliveries WHERE id=?',(delivery_id,)).fetchone()
        if not row or row['state'] not in ('failed','uncertain'):
            raise ValueError('Only failed or uncertain deliveries can be retried')
        if row['state']=='uncertain' and not acknowledge:
            raise ValueError('Check Telegram first, then explicitly acknowledge duplicate risk')
        db.execute("UPDATE deliveries SET state='pending',next_at=0,attempts=0,error=NULL WHERE id=?",(delivery_id,))

def main():
    p=argparse.ArgumentParser(); p.add_argument('--retry',type=int); p.add_argument('--acknowledge-duplicate-risk',action='store_true')
    args=p.parse_args()
    if args.retry:
        retry(args.retry,args.acknowledge_duplicate_risk); print('Delivery queued; analysis was not rerun.'); return
    store.connect().close()
    with (store.ROOT/'notifier.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        recover()
        while True:
            tick(); time.sleep(2)

if __name__=='__main__':
    main()
