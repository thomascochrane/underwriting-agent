"""One engine process at a time; SQLite jobs survive conversation/container restarts."""
from __future__ import annotations
import fcntl
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time
import zipfile
import store

ENGINE=os.environ.get('UNDERWRITER_CLI','/opt/engine-venv/bin/underwrite')
CONFIG=Path(os.environ.get('UNDERWRITER_BASE_CONFIG','/opt/engine-config'))
REVISION=os.environ.get('UNDERWRITER_REVISION','unknown')
STOP=False

class EngineAuthError(Exception):
    pass

class UnsupportedAssetClassError(Exception):
    pass

def asset_classes():
    from underwriter.cli import installed_classes
    return installed_classes()

def review_status(report, no_ai):
    if no_ai:
        return 'disabled'
    review=report.get('ai_review') or {}
    if review.get('ran') is True:
        return 'completed'
    skipped=review.get('skipped')
    if skipped:
        return 'failed' if any(x in str(skipped).lower() for x in ('failed','no ai backend')) else 'skipped'
    return 'unknown'

def stopping(*_):
    global STOP
    STOP=True

def terminate(process):
    if process.poll() is None:
        os.killpg(process.pid,signal.SIGTERM)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid,signal.SIGKILL)
            process.wait()

def execute(command,job_id,log,timeout):
    start=time.monotonic()
    with log.open('ab') as f:
        proc=subprocess.Popen(command,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
        try:
            while proc.poll() is None:
                state=store.status(job_id)
                if STOP:
                    terminate(proc)
                    raise InterruptedError('Worker stopped; outputs may be partial')
                if state['cancel']:
                    terminate(proc)
                    raise KeyboardInterrupt('Job cancelled')
                if time.monotonic()-start>timeout:
                    terminate(proc)
                    raise TimeoutError('Engine stage exceeded its execution limit')
                store.heartbeat('worker',{'active_job':job_id,'stage':state['stage'],'engine_revision':REVISION,
                                          'asset_classes':asset_classes(),'request_schema_version':1})
                time.sleep(1)
            return proc.returncode
        finally:
            terminate(proc)

def verify_snapshot(root,manifest):
    entries=[(next((root/'input').glob('tape.*')),manifest['tape'])]
    entries += [(root/'submitted-config'/k,v) for k,v in manifest['config'].items()]
    for p,meta in entries:
        if p.is_symlink() or not p.resolve().is_relative_to(root.resolve()) or store.digest(p)!=meta['sha256']:
            raise ValueError('Snapshot integrity check failed')

def run_job(row):
    job_id=row['id']; root=store.job_dir(job_id); request=json.loads(row['request'])
    try:
        if store.status(job_id)['cancel']:
            raise KeyboardInterrupt('Job cancelled before start')
        if request.get('schema_version')!=1:
            raise ValueError('Unsupported job request schema')
        asset=request['asset_class']
        if asset not in asset_classes():
            raise UnsupportedAssetClassError(asset)
        manifest=json.loads((root/'input-manifest.json').read_text())
        verify_snapshot(root,manifest)
        tape=next((root/'input').glob('tape.*'))
        if request.get('inspect_only'):
            store.update(job_id,'running','inspecting_tape')
            command=[ENGINE,'--class',asset,'inspect',str(tape)]
            if request.get('sheet'): command += ['--sheet',request['sheet']]
            if execute(command,job_id,root/'inspection.txt',180):
                raise ValueError('Tape inspection failed; inspect inspection.txt')
            bundle=root/'results.zip'
            with zipfile.ZipFile(bundle,'x',zipfile.ZIP_DEFLATED) as z:
                z.write(root/'inspection.txt','inspection.txt')
                z.write(root/'input-manifest.json','input-manifest.json')
            store.finish(job_id,'succeeded',{'inspection':str(root/'inspection.txt'),'engine_revision':REVISION},
                         'Job '+job_id+' completed tape inspection only. No underwriting analysis was run.',bundle)
            return
        # Separate configs per job prevent AI drafts and methodology changes leaking between runs.
        cfg=root/'config'
        if request['custom_config']:
            shutil.copytree(root/'submitted-config',cfg)
        else:
            shutil.copytree(CONFIG,cfg)
            if (root/'submitted-config').exists():
                shutil.copytree(root/'submitted-config',cfg,dirs_exist_ok=True)
        before={str(p.relative_to(cfg)):store.digest(p) for p in cfg.rglob('*.yaml')}
        store.update(job_id,'running','validating_configuration')
        code=execute([ENGINE,'--class',asset,'validate-config','--config',str(cfg)],job_id,root/'engine.log',180)
        if code:
            raise ValueError('Configuration validation failed; inspect the retained engine.log')
        if not request['no_ai']:
            store.update(job_id,'running','checking_engine_login')
            if execute(['codex','login','status'],job_id,root/'engine.log',30):
                raise EngineAuthError('Complete the engine Codex sign-in before AI-assisted jobs')
        command=[ENGINE,'--class',asset,'run',str(tape),'--config',str(cfg),'--out',str(root/'output'),
                 '--profile',request['profile']]
        for opt in ('originator','as_of','sheet','deal'):
            if request.get(opt):
                command += ['--'+opt.replace('_','-'),request[opt]]
        command += ['--no-ai'] if request['no_ai'] else ['--ai-backend','codex']
        provenance={'engine_revision':REVISION,'command':command,'request':request,
                    'config_before':before,'started_at':time.time()}
        (root/'run-provenance.json').write_text(store.encode(provenance))
        store.update(job_id,'running','engine_running')
        code=execute(command,job_id,root/'engine.log',int(os.environ.get('UNDERWRITER_JOB_TIMEOUT','3600')))
        store.update(job_id,'running','packaging_results')
        reports=list((root/'output').rglob('run_report.json'))
        report=json.loads(reports[0].read_text()) if len(reports)==1 else None
        verdict=report.get('verdict') if report else None
        if code==0 and verdict=='PASS':
            state='succeeded'
        elif code==1 and verdict=='FAIL':
            state='validation_failed'
        else:
            raise ValueError('Engine failed or did not produce a consistent run report; inspect engine.log')
        ai=report.get('ai_review') or {}
        ai_status=review_status(report,request['no_ai'])
        analytics_notices=[str(n) for n in report.get('notes',[]) if 'extension ' in str(n) and 'could not run' in str(n)]
        warnings=report.get('warnings') or []
        if state=='succeeded' and (analytics_notices or warnings or ai_status in ('failed','unknown')):
            state='completed_with_warnings'
        result={'asset_class':asset,'exit_code':code,'verdict':verdict,'ai_review':ai,'engine_revision':REVISION,
                'ai_review_status':ai_status,'analytics_notices':analytics_notices,'warnings':warnings,
                'fail_reasons':report.get('fail_reasons',[]),'output_dir':str(root/'output'),'no_ai':request['no_ai']}
        summary=('Underwriting job '+job_id+' finished.\nEngine validation: '+str(verdict)+
                 '. This is not credit approval.\n'+
                 ('AI mapping/review was disabled for this limited test.' if request['no_ai'] else
                  'AI review status: '+ai_status+'. See run_report.json for details.')+
                 '\nThe package contains engine outputs and configuration provenance. Broader document review is separate.')
        if analytics_notices:
            summary+='\nSome analytics did not run; the workbook is incomplete. See run_report.json.'
        if warnings:
            summary+='\nThe engine reported '+str(len(warnings))+' warning(s); inspect them before using the results.'
        provenance.update({'finished_at':time.time(),'result':result,
                           'config_after':{str(p.relative_to(cfg)):store.digest(p) for p in cfg.rglob('*.yaml')}})
        (root/'run-provenance.json').write_text(store.encode(provenance))
        (root/'summary.txt').write_text(summary)
        bundle=root/'results.zip'
        paths=[*sorted((root/'output').rglob('*')),*sorted(cfg.rglob('*.yaml')),
               root/'run-provenance.json',root/'input-manifest.json',root/'summary.txt']
        with zipfile.ZipFile(bundle,'x',zipfile.ZIP_DEFLATED) as z:
            for p in paths:
                if p.is_file() and not p.is_symlink():
                    z.write(p,p.relative_to(root).as_posix())
        result['artifact']=str(bundle)
        result['artifact_sha256']=store.digest(bundle)
        if bundle.stat().st_size>49*1024*1024:
            summary+='\nThe result package exceeds the current Telegram upload limit and remains on the server.'
        store.finish(job_id,state,result,summary,bundle)
    except KeyboardInterrupt:
        store.finish(job_id,'cancelled',{'reason':'Cancellation requested'},'Job '+job_id+' was cancelled. Partial files were retained.')
    except InterruptedError:
        store.finish(job_id,'interrupted',{'reason':'Worker stopped; partial files retained'},
                     'Job '+job_id+' was interrupted. It was not automatically rerun.')
    except EngineAuthError:
        store.finish(job_id,'failed',{'reason':'engine_login_required'},
                     'Job '+job_id+' needs the engine Codex sign-in. The Hermes login is separate; no analysis ran.')
    except UnsupportedAssetClassError:
        store.finish(job_id,'failed',{'reason':'asset_class_not_installed','asset_class':request['asset_class'],
                     'available_asset_classes':asset_classes()},
                     'Job '+job_id+' requested an asset class that is not installed. No other methodology was substituted.')
    except Exception as exc:
        # Do not forward raw provider errors/URLs to Telegram. Full diagnostics stay in the job directory.
        (root/'failure.txt').write_text(type(exc).__name__+': '+str(exc))
        store.finish(job_id,'failed',{'reason':type(exc).__name__,'diagnostics':str(root/'failure.txt')},
                     'Job '+job_id+' failed. Diagnostics and partial outputs were retained; ask for its status.')

def main():
    store.connect().close()
    with (store.ROOT/'worker.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        signal.signal(signal.SIGTERM,stopping); signal.signal(signal.SIGINT,stopping)
        store.recover_worker()
        while not STOP:
            row=store.claim()
            if row:
                run_job(row)
            else:
                store.heartbeat('worker',{'active_job':None,'engine_revision':REVISION,
                                          'asset_classes':asset_classes(),'request_schema_version':1})
                time.sleep(2)

if __name__=='__main__':
    main()
