"""Offline recovery/delivery tests. No model, Telegram, or live data."""
import argparse
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import client
import notifier
import store
import worker

class JobsTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.jobs=self.root/'jobs'; self.inputs=self.root/'inputs'; self.inputs.mkdir()
        self.tape=self.inputs/'tape.xlsx'; self.tape.write_bytes(b'synthetic test bytes')
        self.channel=self.root/'channel.json'
        self.channel.write_text(json.dumps({'token':'offline-test','allowed_users':['123']}))
        self.patch=patch.multiple(store,ROOT=self.jobs); self.patch.start()
        self.env=patch.dict(os.environ,{'UNDERWRITER_INPUT_ROOTS':str(self.inputs),
            'UNDERWRITER_CHANNEL':str(self.channel),'HERMES_SESSION_PLATFORM':'telegram','HERMES_SESSION_CHAT_ID':'123'})
        self.env.start()
        self.npatch=patch.object(notifier,'CHANNEL',self.channel); self.npatch.start()
        self.classes=patch.object(worker,'asset_classes',return_value=['mca']); self.classes.start()
        self.args=argparse.Namespace(tape=str(self.tape),request_key='test1',config=None,deal_config=None,
            deal=None,originator=None,as_of=None,sheet=None,profile='internal',no_ai=True,
            chat_id=None,offline=False,parent_job=None,asset_class='mca')
    def tearDown(self):
        self.classes.stop(); self.npatch.stop(); self.env.stop(); self.patch.stop(); self.tmp.cleanup()
    def submit(self):
        return client.submit(self.args)['id']
    def complete(self):
        job=self.submit()
        store.finish(job,'succeeded',{},'offline summary')
        return job
    def test_submit_snapshot_and_duplicate(self):
        job=self.submit()
        self.assertEqual(self.submit(),job)
        self.assertEqual(store.status(job)['state'],'queued')
        self.assertEqual((store.job_dir(job)/'input/tape.xlsx').read_bytes(),self.tape.read_bytes())
    def test_same_key_changed_input_rejected(self):
        self.submit(); self.tape.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'different inputs'):
            self.submit()
    def test_outside_workspace_rejected(self):
        p=self.root/'secret.xlsx'; p.write_bytes(b'secret'); self.args.tape=str(p)
        with self.assertRaises(ValueError): self.submit()
    def test_symlink_rejected(self):
        link=self.inputs/'link.xlsx'; link.symlink_to(self.tape); self.args.tape=str(link)
        with self.assertRaises(ValueError): self.submit()
    def test_cannot_override_origin_chat(self):
        self.args.chat_id='456'
        with self.assertRaises(ValueError): self.submit()
    def test_groups_not_implicitly_enabled(self):
        with patch.dict(os.environ,{'HERMES_SESSION_CHAT_ID':'-100123'}):
            with self.assertRaises(ValueError): self.submit()
    def test_missing_credentials_requires_explicit_offline(self):
        self.channel.unlink()
        with self.assertRaises(ValueError): self.submit()
        self.args.offline=True
        self.assertIsNone(client.submit(self.args)['request']['chat_id'])
    def test_restart_marks_running_interrupted_not_queued(self):
        job=self.submit(); store.claim(); store.recover_worker()
        self.assertEqual(store.status(job)['state'],'interrupted')
        self.assertIsNone(store.claim())
        self.assertEqual(len(store.status(job)['deliveries']),1)
    def test_fresh_staging_is_not_reaped(self):
        job,_=store.reserve('staging',{})
        store.recover_worker(); self.assertEqual(store.status(job)['state'],'staging')
    def test_claim_is_exclusive(self):
        job=self.submit(); self.assertEqual(store.claim()['id'],job); self.assertIsNone(store.claim())
    def test_uninstalled_class_never_uses_mca(self):
        self.args.asset_class='consumer'; job=self.submit()
        with patch.object(worker,'execute') as exe:
            worker.run_job(store.claim()); exe.assert_not_called()
        self.assertEqual(store.status(job)['result']['reason'],'asset_class_not_installed')
    def test_installed_class_is_forwarded_to_engine(self):
        config=self.root/'base-config'; config.mkdir(); (config/'global.yaml').write_text('{}')
        self.args.asset_class='consumer'; job=self.submit()
        commands=[]
        def fake(command,*_):
            commands.append(command)
            if 'run' in command:
                out=store.job_dir(job)/'output'; out.mkdir()
                (out/'run_report.json').write_text(json.dumps({'verdict':'PASS','ai_review':{}}))
            return 0
        with patch.object(worker,'asset_classes',return_value=['mca','consumer']),patch.object(worker,'CONFIG',config),patch.object(worker,'execute',side_effect=fake):
            worker.run_job(store.claim())
        self.assertTrue(commands)
        self.assertTrue(all(cmd[cmd.index('--class')+1]=='consumer' for cmd in commands))
        self.assertEqual(store.status(job)['result']['asset_class'],'consumer')
    def test_cancel_before_engine_run(self):
        job=self.submit()
        with store.connect() as db: db.execute('UPDATE jobs SET cancel=1 WHERE id=?',(job,))
        with patch.object(worker,'execute') as exe:
            worker.run_job(store.claim()); exe.assert_not_called()
        self.assertEqual(store.status(job)['state'],'cancelled')
    def test_input_tampering_fails_before_engine(self):
        job=self.submit(); (store.job_dir(job)/'input/tape.xlsx').write_bytes(b'tamper')
        with patch.object(worker,'execute') as exe:
            worker.run_job(store.claim()); exe.assert_not_called()
        self.assertEqual(store.status(job)['state'],'failed')
    def test_delivery_receipt_is_persisted_no_repeat(self):
        job=self.complete()
        transport=lambda *_:{'message_id':10,'chat_id':'123'}
        self.assertTrue(notifier.tick(transport)); self.assertFalse(notifier.tick(transport))
        self.assertEqual(store.status(job)['deliveries'][0]['state'],'sent')
    def test_revoked_destination_does_not_send(self):
        job=self.complete(); self.channel.write_text(json.dumps({'token':'test','allowed_users':['999']}))
        with patch.object(notifier,'send') as send:
            notifier.tick(send); send.assert_not_called()
        self.assertEqual(store.status(job)['deliveries'][0]['state'],'failed')
    def test_delivery_missing_token_waits_without_claiming(self):
        job=self.complete(); self.channel.unlink(); self.assertFalse(notifier.tick())
        self.assertEqual(store.status(job)['deliveries'][0]['state'],'pending')
    def test_uncertain_send_requires_explicit_retry(self):
        job=self.complete()
        def timeout(*_): raise notifier.DeliveryError('uncertain','timeout')
        notifier.tick(timeout); d=store.status(job)['deliveries'][0]
        self.assertEqual(d['state'],'uncertain'); self.assertFalse(notifier.tick(timeout))
        with self.assertRaises(ValueError): notifier.retry(d['id'],False)
        notifier.retry(d['id'],True)
        self.assertEqual(store.status(job)['state'],'succeeded')
    def test_notifier_restart_does_not_duplicate_inflight_send(self):
        job=self.complete()
        with store.connect() as db: db.execute("UPDATE deliveries SET state='sending'")
        notifier.recover()
        self.assertEqual(store.status(job)['deliveries'][0]['state'],'uncertain')
        self.assertFalse(notifier.tick())
    def test_rate_limit_retry_is_scheduled(self):
        job=self.complete()
        def limited(*_): raise notifier.DeliveryError('retry','rate limit',60)
        notifier.tick(limited)
        self.assertEqual(store.status(job)['deliveries'][0]['state'],'retry')
        self.assertFalse(notifier.tick(limited))
    def test_http_rate_limit_is_definite_rejection(self):
        error=notifier.urllib.error.HTTPError('https://example.invalid/secret',429,'limit',{},
                                            io.BytesIO(b'{"parameters":{"retry_after":20}}'))
        with patch.object(notifier.urllib.request,'urlopen',side_effect=error):
            with self.assertRaises(notifier.DeliveryError) as exc:
                notifier.send('secret','summary',{'chat_id':'123','text':'test'})
        self.assertEqual(exc.exception.state,'retry'); self.assertEqual(exc.exception.delay,20)
    def test_http_timeout_does_not_leak_token_or_assume_rejection(self):
        with patch.object(notifier.urllib.request,'urlopen',side_effect=notifier.urllib.error.URLError('secret')):
            with self.assertRaises(notifier.DeliveryError) as exc:
                notifier.send('secret','summary',{'chat_id':'123','text':'test'})
        self.assertEqual(exc.exception.state,'uncertain'); self.assertNotIn('secret',exc.exception.reason)
    def test_provider_receipt_must_match_destination(self):
        response=io.BytesIO(b'{"ok":true,"result":{"message_id":42,"chat":{"id":999}}}')
        with patch.object(notifier.urllib.request,'urlopen',return_value=response):
            with self.assertRaises(notifier.DeliveryError) as exc:
                notifier.send('secret','summary',{'chat_id':'123','text':'test'})
        self.assertEqual(exc.exception.state,'uncertain')
    def test_finish_is_idempotent(self):
        job=self.complete(); store.finish(job,'succeeded',{},'same')
        self.assertEqual(len(store.status(job)['deliveries']),1)
    def test_changed_artifact_never_sent(self):
        job=self.submit(); artifact=store.job_dir(job)/'results.zip'; artifact.write_bytes(b'old')
        payload={'path':str(artifact),'sha256':store.digest(artifact),'chat_id':'123','caption':'test'}
        artifact.write_bytes(b'new')
        with self.assertRaises(notifier.DeliveryError) as exc:
            notifier.send('dummy','artifact',payload)
        self.assertEqual(exc.exception.state,'failed')
    def test_timeout_terminates_process(self):
        job=self.submit(); store.claim()
        with self.assertRaises(TimeoutError):
            worker.execute([sys.executable,'-c','import time; time.sleep(30)'],job,store.job_dir(job)/'test.log',0.05)
    def test_success_and_validation_failure_keep_distinct_states(self):
        config=self.root/'base-config'; config.mkdir(); (config/'global.yaml').write_text('{}')
        for verdict,exit_code,wanted in [('PASS',0,'succeeded'),('FAIL',1,'validation_failed')]:
            self.args.request_key=verdict; job=self.submit()
            def fake(command,*_):
                if 'run' in command:
                    out=store.job_dir(job)/'output'; out.mkdir()
                    (out/'run_report.json').write_text(json.dumps({'verdict':verdict,'ai_review':{'status':'disabled'}}))
                    (out/'workbook.xlsx').write_bytes(b'synthetic')
                    return exit_code
                return 0
            with patch.object(worker,'CONFIG',config),patch.object(worker,'execute',side_effect=fake):
                worker.run_job(store.claim())
            self.assertEqual(store.status(job)['state'],wanted)
            self.assertTrue((store.job_dir(job)/'results.zip').is_file())
    def test_engine_pass_with_missing_analytics_is_not_clean_success(self):
        config=self.root/'base-config'; config.mkdir(); (config/'global.yaml').write_text('{}')
        job=self.submit()
        def fake(command,*_):
            if 'run' in command:
                out=store.job_dir(job)/'output'; out.mkdir()
                (out/'run_report.json').write_text(json.dumps({'verdict':'PASS','ai_review':{'ran':False,'skipped':'--no-ai'},
                    'notes':['extension example could not run: test failure']}))
            return 0
        with patch.object(worker,'CONFIG',config),patch.object(worker,'execute',side_effect=fake):
            worker.run_job(store.claim())
        result=store.status(job)
        self.assertEqual(result['state'],'completed_with_warnings')
        self.assertTrue(result['result']['analytics_notices'])
    def test_engine_ai_status_contract(self):
        self.assertEqual(worker.review_status({'ai_review':{'ran':True}},False),'completed')
        self.assertEqual(worker.review_status({'ai_review':{'ran':False,'skipped':'review call failed: test'}},False),'failed')
        self.assertEqual(worker.review_status({'ai_review':{'ran':False,'skipped':'cohort-level tape'}},False),'skipped')

if __name__=='__main__': unittest.main()
