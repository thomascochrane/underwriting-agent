"""Durable single-host engine queue. Private files never belong in Git."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import time
import uuid

ROOT = Path(os.environ.get('UNDERWRITER_JOBS', '/jobs'))
TERMINAL = ('succeeded', 'completed_with_warnings', 'validation_failed', 'failed', 'interrupted', 'cancelled')

class Connection(sqlite3.Connection):
    def __exit__(self, *args):
        try:
            return super().__exit__(*args)
        finally:
            self.close()

def connect():
    ROOT.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(ROOT / 'jobs.sqlite3', timeout=30, factory=Connection)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('PRAGMA busy_timeout=30000')
    db.executescript('''
      CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY, request_key TEXT UNIQUE NOT NULL,
        request_hash TEXT NOT NULL, request TEXT NOT NULL,
        state TEXT NOT NULL, stage TEXT NOT NULL, created REAL NOT NULL,
        updated REAL NOT NULL, cancel INTEGER NOT NULL DEFAULT 0,
        result TEXT NOT NULL DEFAULT '{}');
      CREATE TABLE IF NOT EXISTS deliveries (
        id INTEGER PRIMARY KEY, job_id TEXT NOT NULL, kind TEXT NOT NULL,
        payload TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'pending',
        attempts INTEGER NOT NULL DEFAULT 0, next_at REAL NOT NULL DEFAULT 0,
        receipt TEXT, error TEXT, UNIQUE(job_id, kind));
      CREATE TABLE IF NOT EXISTS health (
        service TEXT PRIMARY KEY, updated REAL NOT NULL, details TEXT NOT NULL);
    ''')
    return db

def encode(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False)

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def job_dir(job_id):
    if not re.fullmatch(r'[a-f0-9]{32}', job_id):
        raise ValueError('Invalid job ID')
    return ROOT / job_id

def allowed_source(path):
    raw = Path(path).absolute()
    if any(p.is_symlink() for p in [raw, *raw.parents]):
        raise ValueError('Symlink inputs are not supported')
    resolved = raw.resolve(strict=True)
    roots = [Path(p).resolve() for p in os.environ.get(
        'UNDERWRITER_INPUT_ROOTS', '/workspace:/opt/data/cache:/jobs').split(os.pathsep)]
    if not any(resolved.is_relative_to(p) for p in roots):
        raise ValueError('Input must be inside the deal workspace or attachment cache')
    return resolved

def snapshot_file(source, target, max_bytes=200 * 1024 * 1024):
    source = allowed_source(source)
    if not source.is_file() or source.stat().st_size > max_bytes:
        raise ValueError('Input is missing, not a regular file, or too large')
    before = digest(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copyfile(source, target)
    after = digest(target)
    if after != before or digest(source) != before:
        raise ValueError('Input changed during snapshot; submit again after it is stable')
    return {'sha256': after, 'bytes': target.stat().st_size, 'original': str(source)}

def reserve(key, request):
    request_hash = hashlib.sha256(encode(request).encode()).hexdigest()
    now = time.time()
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        old = db.execute('SELECT * FROM jobs WHERE request_key=?', (key,)).fetchone()
        if old:
            if old['request_hash'] != request_hash:
                raise ValueError('Request key already used with different inputs/options')
            return old['id'], False
        job_id = uuid.uuid4().hex
        db.execute('INSERT INTO jobs(id,request_key,request_hash,request,state,stage,created,updated) '
                   'VALUES(?,?,?,?,?,?,?,?)',
                   (job_id, key, request_hash, encode(request), 'staging', 'snapshotting', now, now))
    return job_id, True

def update(job_id, state, stage, result=None):
    with connect() as db:
        if result is None:
            db.execute('UPDATE jobs SET state=?,stage=?,updated=? WHERE id=?',
                       (state, stage, time.time(), job_id))
        else:
            db.execute('UPDATE jobs SET state=?,stage=?,result=?,updated=? WHERE id=?',
                       (state, stage, encode(result), time.time(), job_id))

def status(job_id):
    with connect() as db:
        row = db.execute('SELECT * FROM jobs WHERE id=?', (job_id,)).fetchone()
        if not row:
            raise ValueError('Unknown job')
        value = dict(row)
        value['request'] = json.loads(value['request'])
        value['result'] = json.loads(value['result'])
        value['deliveries'] = [dict(x) for x in db.execute(
            'SELECT id,kind,state,attempts,receipt,error FROM deliveries WHERE job_id=?', (job_id,))]
        return value

def heartbeat(service, details):
    with connect() as db:
        db.execute('INSERT INTO health VALUES(?,?,?) ON CONFLICT(service) DO UPDATE SET '
                   'updated=excluded.updated,details=excluded.details', (service,time.time(),encode(details)))

def finish(job_id, state, result, summary, artifact=None):
    """Commit computation result and delivery intent together; no in-memory callback."""
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        row = db.execute('SELECT request FROM jobs WHERE id=?', (job_id,)).fetchone()
        request = json.loads(row['request'])
        db.execute('UPDATE jobs SET state=?,stage=?,result=?,updated=? WHERE id=?',
                   (state, 'done', encode(result), time.time(), job_id))
        if request.get('chat_id'):
            db.execute('INSERT OR IGNORE INTO deliveries(job_id,kind,payload) VALUES(?,?,?)',
                       (job_id,'summary',encode({'chat_id': request['chat_id'], 'text': summary})))
            if artifact:
                db.execute('INSERT OR IGNORE INTO deliveries(job_id,kind,payload) VALUES(?,?,?)',
                           (job_id,'artifact',encode({'chat_id': request['chat_id'], 'path': str(artifact),
                            'sha256': digest(artifact), 'caption': 'Underwriting job ' + job_id})))

def recover_worker():
    with connect() as db:
        rows = db.execute("SELECT id FROM jobs WHERE state='running' OR "
                          "(state='staging' AND updated < ?)", (time.time()-600,)).fetchall()
    for row in rows:
        finish(row['id'], 'interrupted', {'reason': 'Worker restarted or submission was interrupted. '
               'Retained files may be partial; submit an explicit new attempt.'},
               'Job ' + row['id'] + ' was interrupted. Outputs were retained; it was not automatically rerun.')

def claim():
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        row = db.execute("SELECT * FROM jobs WHERE state='queued' ORDER BY created LIMIT 1").fetchone()
        if not row:
            return None
        db.execute("UPDATE jobs SET state='running',stage='preflight',updated=? WHERE id=?",
                   (time.time(),row['id']))
        return dict(row)
