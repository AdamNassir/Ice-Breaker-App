"""Real subprocess/file-watcher tests using a deterministic fake CLI, not model calls."""
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import agent_watch as agent

FAKE_CLI = r'''
import json,os,sys,time
from pathlib import Path
root=Path.cwd();prompt=sys.stdin.read();mode=sys.argv[1]
count_file=root/'calls.txt';count=int(count_file.read_text())+1 if count_file.exists() else 1;count_file.write_text(str(count))
(root/'seen.txt').write_text(prompt,encoding='utf-8')
if mode=='exit':raise SystemExit(7)
if mode=='timeout':time.sleep(60)
if mode=='new':(root/'UpdateGuide.md').write_text('# Pending update\nNewer human request.\n')
if mode=='gate':(root/'check_project.py').write_text('print("weakened")')
value='GOOD' if mode not in {'repair','fail'} or mode=='repair' and 'AssertionError: expected GOOD' in prompt else 'BAD'
(root/'app.txt').write_text(value)
output=Path(sys.argv[sys.argv.index('--output-last-message')+1])
result={'status':'blocked' if mode=='blocked' else 'completed','summary':'A simulated implementation.','changes':['Updated app.txt.'],'validation':['Simulated CLI validation; independent checks follow.'],'limitations':[]}
output.write_text(json.dumps([] if mode=='invalid' else result))
print(json.dumps({'type':'turn.completed'}))
'''


class AgentWatcherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.request = b'# Pending update\nChange the local app.\n'
        (self.root/'UpdateGuide.md').write_bytes(self.request)
        (self.root/'app.txt').write_text('BEFORE')
        (self.root/'fake_cli.py').write_text(FAKE_CLI)
        (self.root/'check_project.py').write_text('print("original gate")')
        (self.root/'check.py').write_text("from pathlib import Path\nassert Path('app.txt').read_text() == 'GOOD', 'expected GOOD'\n")
        self.settings = {**agent.DEFAULTS, 'max_attempts': 2,
                         'checks': [[sys.executable, 'check.py']], 'agent_timeout_seconds': 10}

    def tearDown(self):
        self.temp.cleanup()

    def watcher(self, mode='good'):
        return agent.Watcher(self.root, self.settings, [sys.executable, str(self.root/'fake_cli.py'), mode])

    def run_request(self, mode='good'):
        watcher = self.watcher(mode)
        with redirect_stdout(io.StringIO()):
            result = watcher.process(self.request)
        state = watcher.previous()
        run = self.root/state['run_directory']
        return result, state, run

    def test_completed_reports_drafts_and_empty_files_do_not_trigger(self):
        for data in (b'', b' \n', b'# Completed update - old\nInstructions\n',
                     b'# Draft update\nStill editing\n', b'# Agent report - failed\n',
                     b'# Update request template\nDescribe a change\n'):
            self.assertFalse(agent.is_request(data))
        self.assertTrue(agent.is_request(self.request))
        self.assertTrue(agent.is_request(b'Remove the unnecessary button.'))
        self.assertTrue(agent.is_request(b'\xef\xbb\xbf# Pending update\nA Unicode request.'))

    def test_success_writes_report_and_archives_request_without_credentials(self):
        (self.root/'.env').write_text('DATABASE_URL=private-value')
        (self.root/'.env.local').write_text('private')
        (self.root/'node_modules').mkdir();(self.root/'node_modules'/'runtime.txt').write_text('large dependency')
        ok, state, run = self.run_request()
        self.assertTrue(ok);self.assertEqual(state['status'], 'completed')
        self.assertEqual((run/'request.md').read_bytes(), self.request)
        report = (self.root/'UpdateGuide.md').read_text()
        self.assertTrue(report.startswith('# Completed update'))
        self.assertIn('PASS:', report);self.assertIn('`app.txt`', report)
        with zipfile.ZipFile(run/'before.zip') as archive:
            self.assertEqual(archive.read('app.txt'), b'BEFORE')
            self.assertNotIn('.env', archive.namelist());self.assertNotIn('.env.local', archive.namelist())
            self.assertFalse(any(name.startswith('node_modules/') for name in archive.namelist()))
        prompt = (run/'prompt-1.txt').read_text()
        self.assertIn('Do NOT edit UpdateGuide.md', prompt)
        self.assertIn(str(sys.executable), prompt)

    def test_failed_checks_feed_back_and_second_attempt_repairs(self):
        ok, state, run = self.run_request('repair')
        self.assertTrue(ok);self.assertEqual(state['status'], 'completed')
        self.assertEqual((self.root/'calls.txt').read_text(), '2')
        self.assertIn('AssertionError: expected GOOD', (run/'prompt-2.txt').read_text())
        self.assertEqual(json.loads((run/'checks-1.json').read_text())[0]['exit_code'], 1)
        self.assertEqual(json.loads((run/'checks-2.json').read_text())[0]['exit_code'], 0)

    def test_retry_limit_preserves_request_and_blocks_duplicate_and_restart(self):
        ok, state, run = self.run_request('fail')
        self.assertFalse(ok);self.assertEqual(state['status'], 'needs_attention')
        self.assertEqual((self.root/'calls.txt').read_text(), '2')
        self.assertEqual((self.root/'UpdateGuide.md').read_bytes(), self.request)
        self.assertIn('FAIL:', (run/'report.md').read_text())
        watcher = self.watcher()
        self.assertFalse(watcher.eligible(self.request))
        self.assertTrue(watcher.eligible(self.request, retry=True))
        self.assertTrue(watcher.eligible(self.request+b'A different request.'))

    def test_blocked_agent_does_not_publish_a_verified_report(self):
        ok, state, run = self.run_request('blocked')
        self.assertFalse(ok)
        self.assertEqual((self.root/'UpdateGuide.md').read_bytes(), self.request)
        self.assertFalse(list(run.glob('check-*.log')))
        self.assertIn('No independent checks completed', (run/'report.md').read_text())

    def test_cli_failure_and_malformed_output_preserve_request(self):
        for mode in ('exit', 'invalid'):
            with self.subTest(mode=mode):
                ok, state, run = self.run_request(mode)
                self.assertFalse(ok);self.assertEqual(state['status'], 'needs_attention')
                self.assertEqual((self.root/'UpdateGuide.md').read_bytes(), self.request)
                self.assertIn('needs attention', (run/'report.md').read_text())

    def test_newer_editor_save_is_not_overwritten(self):
        ok, state, run = self.run_request('new')
        self.assertTrue(ok);self.assertEqual(state['status'], 'completed_with_new_request')
        current = (self.root/'UpdateGuide.md').read_bytes()
        self.assertIn(b'Newer human request.', current)
        self.assertTrue(self.watcher().eligible(current))
        self.assertEqual((run/'request.md').read_bytes(), self.request)
        self.assertTrue((run/'report.md').read_text().startswith('# Completed update'))

    def test_agent_cannot_weaken_protected_check_gate(self):
        ok, state, run = self.run_request('gate')
        self.assertFalse(ok);self.assertEqual((self.root/'UpdateGuide.md').read_bytes(), self.request)
        self.assertIn('Restore the protected gate files', (run/'prompt-2.txt').read_text())

    def test_timeout_stops_cli_and_keeps_pending_request(self):
        self.settings['agent_timeout_seconds'] = 1
        started = time.monotonic()
        ok, state, run = self.run_request('timeout')
        self.assertFalse(ok);self.assertLess(time.monotonic()-started, 8)
        self.assertIn('TIMEOUT', (run/'agent-1.log').read_text())
        self.assertEqual((self.root/'UpdateGuide.md').read_bytes(), self.request)

    def test_exclusive_watcher_lock_and_automatic_release(self):
        with agent.single_watcher(self.root):
            with self.assertRaisesRegex(ValueError, 'already running'):
                with agent.single_watcher(self.root): pass
        with agent.single_watcher(self.root): pass

    def test_windows_npm_shim_uses_node_without_a_shell(self):
        shim=self.root/'codex.cmd';shim.write_text('npm shim')
        entry=self.root/'node_modules/@openai/codex/bin/codex.js';entry.parent.mkdir(parents=True);entry.write_text('stub')
        with patch.object(agent.shutil, 'which', side_effect=lambda name: str(shim) if name=='codex' else 'node.exe'):
            self.assertEqual(agent.resolve_command(['codex']), ['node.exe',str(entry)])
        entry.unlink()
        with patch.object(agent.shutil, 'which', side_effect=lambda name: str(shim) if name=='codex' else 'node.exe'):
            with self.assertRaisesRegex(ValueError, 'npm shim'):agent.resolve_command(['codex'])

    def test_configuration_rejects_unbounded_or_shell_string_settings(self):
        for value in ({'max_attempts':100}, {'checks':['python check.py']}, {'checks':[]},
                      {'poll_seconds':True}, {'max_attempts':1.5}, {'unknown':1}):
            (self.root/'agent_config.json').write_text(json.dumps(value))
            with self.assertRaises(ValueError):agent.load_settings(self.root)

    def test_live_watcher_debounces_saves_and_does_not_run_its_own_report(self):
        (self.root/'agent_watch.py').write_bytes(Path(agent.__file__).read_bytes())
        settings={**self.settings,'codex_command':[sys.executable,str(self.root/'fake_cli.py'),'good'],
                  'poll_seconds':.05,'debounce_seconds':.3}
        (self.root/'agent_config.json').write_text(json.dumps(settings))
        (self.root/'UpdateGuide.md').write_text('# Completed update\nOld report.\n')
        with (self.root/'watcher.log').open('w') as log:
            process=subprocess.Popen([sys.executable,'agent_watch.py'],cwd=self.root,stdout=log,stderr=log)
            try:
                self.until(lambda:(self.root/'.agent/watcher.lock').exists(),process)
                (self.root/'UpdateGuide.md').write_text('# Pending update\nPartial save.\n')
                time.sleep(.06)
                final=b'# Pending update\nThe final saved request.\n';(self.root/'UpdateGuide.md').write_bytes(final)
                self.until(lambda:(self.root/'.agent/state.json').exists() and json.loads((self.root/'.agent/state.json').read_text()).get('status')=='completed',process)
                time.sleep(.5)
                self.assertEqual((self.root/'calls.txt').read_text(),'1')
                state=json.loads((self.root/'.agent/state.json').read_text());run=self.root/state['run_directory']
                self.assertEqual((run/'request.md').read_bytes(),final)
                duplicate=subprocess.run([sys.executable,'agent_watch.py','--once'],cwd=self.root,capture_output=True,timeout=5)
                self.assertEqual(duplicate.returncode,2)
                self.assertIn(b'already running',duplicate.stderr)
            finally:
                process.terminate();process.wait(timeout=5)

    def until(self, condition, process):
        end=time.monotonic()+8
        while time.monotonic()<end:
            if condition():return
            if process.poll() is not None:self.fail('Watcher exited early: '+(self.root/'watcher.log').read_text())
            time.sleep(.03)
        self.fail('Watcher condition timed out: '+(self.root/'watcher.log').read_text())


if __name__ == '__main__':
    unittest.main()
