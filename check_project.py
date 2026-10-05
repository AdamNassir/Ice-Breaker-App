"""Local agent gate: API tests, JavaScript syntax and actual game DOM regressions."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def main():
    node = shutil.which('node')
    if not node:
        print('Install Node.js LTS, reopen the terminal, then run npm --prefix tests/frontend ci.')
        return 1
    env = {**os.environ, 'DATABASE_URL': '', 'VERCEL': '', 'PRESENTER_PASSWORD': '',
           'PYTHONUTF8': '1', 'PYTHONIOENCODING': 'utf-8'}
    commands = [[sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v']]
    for folder in ('static', 'manager_assets', 'tests/frontend'):
        commands.extend([node, '--check', str(p)] for p in sorted((ROOT / folder).glob('*.js')))
        commands.extend([node, '--check', str(p)] for p in sorted((ROOT / folder).glob('*.cjs')))
    commands.append([sys.executable, 'tests/run_frontend.py'])
    for command in commands:
        print('Checking: ' + ' '.join(command), flush=True)
        if subprocess.run(command, cwd=ROOT, env=env, check=False).returncode:
            return 1
    print('PASS Python, JavaScript syntax and full game/manager/zoom/keyboard/workflow DOM checks.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
