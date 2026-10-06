"""Local saved-request agent. Uses authenticated Codex CLI; never imported by FastAPI."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid
import zipfile

ROOT = Path(__file__).resolve().parent
IGNORED_DIRS = {'.agent', '.git', '.venv', 'venv', 'node_modules', '__pycache__',
                '.pytest_cache', '.vercel', '.question-manager-backups'}
PROTECTED = ('agent_watch.py', 'agent_config.json', 'check_project.py')
DEFAULTS = {
    'codex_command': ['codex'], 'model': '', 'poll_seconds': 0.5,
    'debounce_seconds': 1.5, 'max_attempts': 3,
    'agent_timeout_seconds': 900, 'check_timeout_seconds': 180,
    'checks': [['{python}', 'check_project.py']],
}
RESULT_SCHEMA = {
    'type': 'object', 'additionalProperties': False,
    'properties': {
        'status': {'type': 'string', 'enum': ['completed', 'blocked']},
        'summary': {'type': 'string'},
        'changes': {'type': 'array', 'items': {'type': 'string'}},
        'validation': {'type': 'array', 'items': {'type': 'string'}},
        'limitations': {'type': 'array', 'items': {'type': 'string'}},
    },
    'required': ['status', 'summary', 'changes', 'validation', 'limitations'],
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.write-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as file:
            file.write(data); file.flush(); os.fsync(file.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def save_json(path, value):
    atomic_write(path, (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))


def load_settings(root):
    path = root / 'agent_config.json'
    value = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    if not isinstance(value, dict) or set(value) - set(DEFAULTS):
        raise ValueError('agent_config.json has unknown settings or is not an object.')
    settings = {**DEFAULTS, **value}
    for key in ('codex_command', 'checks'):
        items = settings[key]
        if not isinstance(items, list) or not items:
            raise ValueError(f'{key} must be a nonempty list.')
        commands = items if key == 'checks' else [items]
        if any(not isinstance(cmd, list) or not cmd or
               any(not isinstance(arg, str) or not arg or '\x00' in arg for arg in cmd)
               for cmd in commands):
            raise ValueError(f'{key} must contain argument lists; shell commands are not accepted.')
    if not isinstance(settings['model'], str):
        raise ValueError('model must be a string; leave it empty to use your Codex default.')
    bounds = {'poll_seconds': (0.05, 10), 'debounce_seconds': (0.05, 30),
              'max_attempts': (1, 5), 'agent_timeout_seconds': (1, 3600),
              'check_timeout_seconds': (1, 1800)}
    for key, (low, high) in bounds.items():
        number = settings[key]
        if isinstance(number, bool) or not isinstance(number, (int, float)) or not low <= number <= high:
            raise ValueError(f'{key} must be between {low} and {high}.')
    if not isinstance(settings['max_attempts'], int):
        raise ValueError('max_attempts must be an integer.')
    return settings


def resolve_command(command):
    """Avoid shell=True, including Windows npm .cmd shims."""
    program = shutil.which(command[0])
    if not program:
        raise ValueError(f'Cannot find {command[0]}. Install Codex CLI and reopen the terminal.')
    if Path(program).suffix.lower() in {'.cmd', '.bat'}:
        entry = Path(program).parent / 'node_modules' / '@openai' / 'codex' / 'bin' / 'codex.js'
        node = shutil.which('node')
        if not entry.is_file() or not node:
            raise ValueError('Cannot resolve the Windows Codex npm shim. Reinstall @openai/codex or use codex.exe in codex_command.')
        return [node, str(entry), *command[1:]]
    return [program, *command[1:]]


def is_request(data):
    text = data.decode('utf-8-sig').strip()
    if not text:
        return False
    first = text.splitlines()[0].lstrip('# ').casefold()
    return not first.startswith(('completed update', 'agent report', 'draft update', 'update request template'))


def read_request(root):
    path = root / 'UpdateGuide.md'
    if path.is_symlink():
        raise ValueError('UpdateGuide.md must be a local file, not a symlink.')
    try:
        with path.open('rb') as file:
            data = file.read(128 * 1024 + 1)
    except FileNotFoundError:
        return b''
    if len(data) > 128 * 1024:
        raise ValueError('Keep UpdateGuide.md below 128 KB.')
    return data


def source_files(root):
    for folder, directories, names in os.walk(root, followlinks=False):
        directories[:] = sorted(d for d in directories if d not in IGNORED_DIRS and not (Path(folder) / d).is_symlink())
        for name in sorted(names):
            path = Path(folder) / name
            if path.is_symlink() or (name.startswith('.env') and name != '.env.example'):
                continue
            if name.endswith(('.pyc', '.log', '.tmp', '.zip')) or '.sqlite3' in name:
                continue
            yield path


def manifest(root):
    return {p.relative_to(root).as_posix(): digest(p.read_bytes()) for p in source_files(root)}


@contextmanager
def single_watcher(root):
    folder = root / '.agent'; folder.mkdir(exist_ok=True)
    with (folder / 'watcher.lock').open('a+b') as lock:
        lock.seek(0); lock.write(b'0'); lock.flush(); lock.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise ValueError('Another watcher is already running for this folder.') from error
        try:
            yield
        finally:
            if os.name == 'nt':
                lock.seek(0); msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)


def stop_process(process):
    if process.poll() is not None:
        return
    if os.name == 'nt':
        subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    else:
        try: os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError: pass
    try: process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if os.name != 'nt':
            try: os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError: pass
        process.kill(); process.wait()


def execute(command, root, log, timeout, prompt=None):
    env = {**os.environ, 'PYTHONUTF8': '1', 'PYTHONIOENCODING': 'utf-8',
           'DATABASE_URL': '', 'PRESENTER_PASSWORD': '', 'VERCEL': ''}
    options = {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == 'nt' else {'start_new_session': True}
    with log.open('wb') as output:
        process = subprocess.Popen(command, cwd=root, env=env, stdin=subprocess.PIPE if prompt is not None else subprocess.DEVNULL,
                                   stdout=output, stderr=output, **options)
        try:
            process.communicate(input=prompt.encode('utf-8') if prompt is not None else None, timeout=timeout)
        except subprocess.TimeoutExpired:
            stop_process(process); output.write(b'\nTIMEOUT: process stopped.\n'); return 124
        except BaseException:
            stop_process(process); raise
        return process.returncode


class Watcher:
    def __init__(self, root, settings, command=None):
        self.root = root
        self.settings = settings
        self.command = command or resolve_command(settings['codex_command'])
        self.state_path = root / '.agent' / 'state.json'

    def previous(self):
        if not self.state_path.exists():
            return {}
        return json.loads(self.state_path.read_text(encoding='utf-8'))

    def eligible(self, data, retry=False):
        return is_request(data) and (retry or self.previous().get('request_hash') != digest(data))

    def prompt(self, data, run, attempt, feedback):
        return f'''You are the local coding agent for this ice-breaker project.
Read AGENTS.md, CreationInstructions.md and Verification.md, then implement the saved request below.
The request snapshot is also in {run.relative_to(self.root).as_posix()}/request.md.
Attempt {attempt} of {self.settings['max_attempts']}.

Work only in this repository. Preserve other questions/media and JSON/fallback equivalence.
Use this Python executable for tests: {sys.executable}
Implement, run meaningful relevant checks, fix failures and test again.
Do not weaken/delete tests or alter agent_watch.py, agent_config.json or check_project.py.
Do NOT edit UpdateGuide.md: the watcher owns its final report and protects concurrent editor saves.
Do not read/print .env or credentials. Do not push, publish, deploy or send messages.
Do not install dependencies automatically; if required tools are missing, report blocked.
Use installed local tools and the CLI sandbox; never bypass its permissions.
The watcher runs independent checks after your turn; your status alone does not establish success.
Return structured JSON matching the supplied schema. Mark blocked for unresolved requirements.
Clearly distinguish actual tests from anything you could not verify.

SAVED REQUEST:
{data.decode('utf-8-sig')}

PREVIOUS CHECK FEEDBACK:
{feedback or 'Initial implementation pass.'}
'''

    def process(self, data):
        run = self.root / '.agent' / 'runs' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8])
        run.mkdir(parents=True)
        atomic_write(run / 'request.md', data)
        before = manifest(self.root)
        save_json(run / 'before.json', before)
        with zipfile.ZipFile(run / 'before.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
            for name in before: archive.write(self.root / name, name)
        save_json(run / 'schema.json', RESULT_SCHEMA)
        state = {'request_hash': digest(data), 'status': 'running', 'run_directory': run.relative_to(self.root).as_posix()}
        save_json(self.state_path, state)
        result = {'status': 'blocked', 'summary': 'The agent did not complete this request.', 'changes': [], 'validation': [], 'limitations': []}
        feedback = ''; checks = []; passed = False; changed_gate = []
        try:
            for attempt in range(1, self.settings['max_attempts'] + 1):
                print(f'Agent attempt {attempt}: {run.name}', flush=True)
                answer = run / f'answer-{attempt}.json'
                prompt = self.prompt(data, run, attempt, feedback)
                atomic_write(run / f'prompt-{attempt}.txt', prompt.encode('utf-8'))
                command = [*self.command, '--no-daemon', '--ask-for-approval', 'never', 'exec', '--sandbox', 'workspace-write',
                           '--skip-git-repo-check', '--json', '--color', 'never',
                           '--output-schema', str(run / 'schema.json'), '--output-last-message', str(answer)]
                if self.settings['model']: command.extend(['--model', self.settings['model']])
                command.append('-')
                code = execute(command, self.root, run / f'agent-{attempt}.log', self.settings['agent_timeout_seconds'], prompt)
                if code:
                    raise ValueError(f'Codex exited with code {code}. See agent-{attempt}.log; login, quota, sandbox or timeout may need attention.')
                parsed = json.loads(answer.read_text(encoding='utf-8'))
                if not isinstance(parsed, dict) or set(parsed) != set(RESULT_SCHEMA['required']) or parsed.get('status') not in {'completed', 'blocked'}:
                    raise ValueError('Codex did not return the required structured result.')
                if not isinstance(parsed['summary'], str) or any(not isinstance(parsed[k], list) or any(not isinstance(x, str) for x in parsed[k]) for k in ('changes', 'validation', 'limitations')):
                    raise ValueError('Codex returned invalid report fields.')
                result = parsed
                if result['status'] == 'blocked': break
                checks = []
                print('Running independent project checks.', flush=True)
                for index, args in enumerate(self.settings['checks'], 1):
                    args = [arg.replace('{python}', sys.executable) for arg in args]
                    log = run / f'check-{attempt}-{index}.log'
                    code = execute(args, self.root, log, self.settings['check_timeout_seconds'])
                    checks.append({'command': args, 'exit_code': code, 'log': log.name})
                after = manifest(self.root)
                changed_gate = [name for name in PROTECTED if before.get(name) != after.get(name)]
                passed = all(c['exit_code'] == 0 for c in checks) and not changed_gate
                save_json(run / f'checks-{attempt}.json', checks)
                if passed: break
                feedback = '\n\n'.join(f"{c['command']} -> exit {c['exit_code']}\n" + (run / c['log']).read_text(encoding='utf-8', errors='replace')[-12000:] for c in checks if c['exit_code'])
                if changed_gate: feedback += '\nRestore the protected gate files: ' + ', '.join(changed_gate)
                print('Checks failed. Returning their output to the agent.', flush=True)
        except KeyboardInterrupt:
            state['status'] = 'interrupted'; save_json(self.state_path, state)
            print('Stopped. Request and checkpoint preserved.', flush=True)
            raise
        except (OSError, ValueError, KeyError) as error:
            result['limitations'].append(str(error)); passed = False
        if not passed and changed_gate:
            result['limitations'].append('Protected validation files were changed: ' + ', '.join(changed_gate) + '. Restore them before retrying.')
        after = manifest(self.root)
        changes = {
            'modified': sorted(n for n in before.keys() & after.keys() if before[n] != after[n]),
            'added': sorted(after.keys() - before.keys()), 'removed': sorted(before.keys() - after.keys()),
        }
        if passed and 'UpdateGuide.md' not in changes['modified']: changes['modified'].append('UpdateGuide.md'); changes['modified'].sort()
        report = self.report(result, changes, checks, passed, run)
        atomic_write(run / 'report.md', report.encode('utf-8'))
        if passed and read_request(self.root) == data:
            atomic_write(self.root / 'UpdateGuide.md', report.encode('utf-8'))
            state['status'] = 'completed'
            print('Completed. Review UpdateGuide.md and test the app.', flush=True)
        else:
            state['status'] = 'completed_with_new_request' if passed else 'needs_attention'
            print(f"{state['status']}: UpdateGuide.md preserved. Read {state['run_directory']}/report.md", flush=True)
        state['report'] = (run / 'report.md').relative_to(self.root).as_posix()
        save_json(self.state_path, state)
        return passed

    def report(self, result, changes, checks, passed, run):
        heading = '# Completed update — local agent' if passed else '# Agent report — needs attention'
        lines = [heading, '', result['summary'], '', '## Changes', '']
        lines.extend('- ' + item for item in result['changes'])
        for kind, names in changes.items():
            lines.extend(['', '## ' + kind.capitalize() + ' files', ''])
            lines.extend('- `' + name + '`' for name in names)
            if not names: lines.append('None.')
        lines.extend(['', '## Independent checks', ''])
        for check in checks: lines.append('- ' + ('PASS' if check['exit_code'] == 0 else 'FAIL') + ': `' + ' '.join(check['command']) + '` (exit ' + str(check['exit_code']) + ', ' + check['log'] + ').')
        if not checks: lines.append('No independent checks completed; this is not a verified result.')
        lines.extend(['', '## Agent-reported validation', ''])
        lines.extend('- ' + item for item in result['validation'])
        lines.extend(['', '## Limitations and next steps', ''])
        lines.extend('- ' + item for item in result['limitations'])
        if not passed: lines.append('- The request remains pending. Review logs, correct the issue, then use --once --retry. Code changes may be partial; the checkpoint is preserved.')
        lines.extend(['- Review the actual changed files and rehearse the app before deployment. Nothing was pushed or deployed by the watcher.',
                      '- Request, source checkpoint, logs and this report: `' + run.relative_to(self.root).as_posix() + '/`.', ''])
        return '\n'.join(lines)


def doctor(root, command):
    for args, label in [(['--version'], 'Codex CLI'), (['login', 'status'], 'Codex login')]:
        result = subprocess.run([*command, *args], cwd=root, capture_output=True, timeout=20)
        if result.returncode: raise ValueError(f'{label} is not ready. Install Codex or run codex login first.')
        print(label + ': ready')
    global_help = subprocess.run([*command, '--help'], cwd=root, capture_output=True, timeout=20)
    if global_help.returncode or b'--no-daemon' not in global_help.stdout + global_help.stderr:
        raise ValueError('Update Codex CLI: the foreground --no-daemon option is required.')
    result = subprocess.run([*command, 'exec', '--help'], cwd=root, capture_output=True, timeout=20)
    help_text = (result.stdout + result.stderr).decode('utf-8', errors='replace')
    if result.returncode or any(flag not in help_text for flag in ('--output-schema', '--output-last-message', '--sandbox', '--skip-git-repo-check')):
        raise ValueError('Update Codex CLI: required automation options are missing.')
    node = shutil.which('node')
    if not node: raise ValueError('Install Node.js LTS and reopen the terminal.')
    result = subprocess.run([node, '-e', "require('jsdom')"], cwd=root / 'tests/frontend', capture_output=True)
    if result.returncode: raise ValueError('Run npm --prefix tests/frontend ci before starting the agent.')
    result = subprocess.run([sys.executable, '-c', 'import fastapi,httpx,uvicorn,pydantic,qrcode,psycopg'], capture_output=True)
    if result.returncode: raise ValueError('Use the project venv and install requirements-dev.txt.')
    print('CLI options, Python packages and local DOM checks: ready')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--once', action='store_true', help='Process one pending request, then exit.')
    parser.add_argument('--retry', action='store_true', help='Explicitly retry the same preserved request once.')
    parser.add_argument('--doctor', action='store_true', help='Check installation/login without a model call.')
    parser.add_argument('--status', action='store_true', help='Show the last local run state.')
    args = parser.parse_args()
    try:
        if args.status:
            path = ROOT / '.agent/state.json'
            print(path.read_text(encoding='utf-8') if path.exists() else 'No local agent run yet.'); return 0
        settings = load_settings(ROOT)
        command = resolve_command(settings['codex_command'])
        if args.doctor: doctor(ROOT, command); return 0
        with single_watcher(ROOT):
            watcher = Watcher(ROOT, settings, command)
            candidate = None; since = time.monotonic(); retry = args.retry
            print('Watching UpdateGuide.md. Save a request; completed reports and drafts are ignored. Ctrl+C stops.', flush=True)
            while True:
                data = read_request(ROOT)
                if data != candidate: candidate = data; since = time.monotonic()
                if time.monotonic() - since >= settings['debounce_seconds']:
                    if watcher.eligible(data, retry):
                        ok = watcher.process(data); retry = False
                        if args.once: return 0 if ok else 1
                        candidate = None
                    elif args.once:
                        print('No new pending request.'); return 0
                time.sleep(settings['poll_seconds'])
    except KeyboardInterrupt:
        print('Watcher stopped.'); return 130
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print('Agent setup: ' + str(error), file=sys.stderr); return 2


if __name__ == '__main__':
    raise SystemExit(main())
