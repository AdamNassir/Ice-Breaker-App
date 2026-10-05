"""Generate real API states, then exercise local manager and game DOMs without cloud accounts."""
import json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
node = shutil.which('node')
if not node:
    raise SystemExit('Install Node.js LTS before running frontend checks.')
if subprocess.run([node, '-e', "require('jsdom')"], cwd=ROOT/'tests/frontend', capture_output=True).returncode:
    raise SystemExit('Install local DOM dependencies: npm --prefix tests/frontend ci')
checks_dir = ROOT / '.agent' / 'checks'
checks_dir.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(dir=checks_dir) as tmp:
 project=Path(tmp)/'project'
 shutil.copytree(ROOT,project,ignore=shutil.ignore_patterns('.agent','node_modules','.git','.venv','__pycache__','*.sqlite3*','.env','.env.local','.question-manager-backups','.vercel'))
 with socket.socket() as sock:
  sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
 base_url=f'http://127.0.0.1:{port}'
 fixture_file=Path(tmp)/'fixture.json'
 os.environ.update(DATABASE_URL='',PRESENTER_PASSWORD='',VERCEL='',SQLITE_PATH=str(Path(tmp)/'initial.sqlite3'),QA_MANAGER_BASE=base_url,QA_PROJECT=str(project),QA_ORIGINAL=str(ROOT),QA_FIXTURE=str(fixture_file),PYTHONUTF8='1')
 sys.path.insert(0,str(ROOT))
 from fastapi.testclient import TestClient
 import main
 from question_content import load_rounds
 from store import Store
 root=ROOT
 main.store=Store();main.store.path=Path(tmp)/'game.sqlite3'
 with TestClient(main.app) as c:
  room=c.post('/api/rooms',json={'seconds':10}).json();assert 'code' in room,room
  code=room['code'];host={'Authorization':'Bearer '+room['token']}
  player=c.post(f'/api/rooms/{code}/join',json={'nickname':'Fun Tester'}).json();ph={'Authorization':'Bearer '+player['token']}
  def states(phase):return {'phase':phase,'host':c.get(f'/api/rooms/{code}/state',headers=host).json(),'player':c.get(f'/api/rooms/{code}/state',headers=ph).json()}
  def control(action):
   revision=c.get(f'/api/rooms/{code}/state',headers=host).json()['revision']
   r=c.post(f'/api/rooms/{code}/control',headers=host,json={'action':action,'revision':revision});assert r.status_code==200,r.text
  rows=[states("lobby")]
  for i,q in enumerate(load_rounds(root)):
   if i==0:control('start')
   rows.append(states('live'));assert rows[-1]['host']['duration']==10
   assert rows[-1]['host']['phase']=='live' and rows[-1]['host']['round_index']==i
   for r in (rows[-1]['host'],rows[-1]['player']):
    assert not set(r['question']).intersection({'answer','source','source_url','explanation','discussion','image_reveal','image_highlight','reveal_sources','reveal_media','reveal_alt'})
   vote=c.post(f'/api/rooms/{code}/vote',headers=ph,json={'answer':q['answer'],'round_index':i});assert vote.status_code==200
   deadline=rows[-1]['host']['deadline']
   with patch.object(main.time,'time',return_value=deadline+1):rows.append(states('revealed'))
   control('next')
  rows.append(states('finished'));assert rows[-1]['player']['me']['score']==1550
  for path in ['/static/news/housing.jpg','/static/news/ai.jpg','/static/news/football.jpg','/static/branding/publication.svg','/static/newsarticle.js','/static/newsarticle.css','/static/images/sample26.jpg','/static/images/sample27.png','/static/images/profile-source.png','/static/branding/logiclever-full.jpg','/static/media.js','/static/images/sample13.jpg','/static/images/sample15.jpg','/static/images/sample16.jpg','/static/audio/sample17.mp3','/static/images/sample18.png','/static/images/sample18-reveal.png','/static/images/linkedin-profile-source.png','/static/images/sample19.png','/static/images/sample20.jpg','/static/images/sample23.png','/static/images/sample24.jpg','/static/images/sample25.png','/static/branding/logiclever.png','/static/branding/totalenergies.png','/bonus','/static/bonus.js']:assert c.get(path).status_code==200,path
  for private in ['/questions.json','/Content.py','/ContentSources.md','/api/deck']:assert c.get(private).status_code==404,private
  qr=c.get(f'/api/rooms/{code}/qr',headers=host).json()
  trophy_room=c.post('/api/rooms',json={'seconds':10}).json();trophy_code=trophy_room['code'];trophy_host={'Authorization':'Bearer '+trophy_room['token']}
  entrants=[]
  for name,score in [('Ada',1750),('Linus',1600),('Grace',1400),('Alan',1000),('Margaret',1000),('Ken',750)]:
   entrant=c.post(f'/api/rooms/{trophy_code}/join',json={'nickname':name}).json();entrants.append((entrant,score))
  with main.store.room(trophy_code) as saved:
   saved['phase']='finished';saved['index']=len(load_rounds(root))-1
   for entrant,score in entrants:saved['players'][entrant['player_id']]['score']=score
  placements={'host':c.get(f'/api/rooms/{trophy_code}/state',headers=trophy_host).json(),
              'player':c.get(f'/api/rooms/{trophy_code}/state',headers={'Authorization':'Bearer '+entrants[0][0]['token']}).json()}
  assert [p['rank'] for p in placements['host']['leaderboard']]==[1,2,3,4,4,6]
  (fixture_file).write_text(json.dumps(dict(room=room,player=player,rows=rows,qr=qr,placements=placements)))
 log=(Path(tmp)/'manager.log').open('w',encoding='utf-8')
 server=subprocess.Popen([sys.executable,'question_manager.py','--no-browser','--port',str(port)],cwd=project,env=os.environ,stdout=log,stderr=log)
 try:
  for i in range(150):
   if server.poll() is not None:raise RuntimeError('Local manager stopped before checks. Read its startup output.')
   try:urllib.request.urlopen(base_url+'/api/deck',timeout=1);break
   except OSError:time.sleep(.1)
  else:raise RuntimeError('Local manager did not start.')
  for filename in ('resources.cjs','game.cjs','zoom.cjs','keyboard.cjs','workflow.cjs'):
   subprocess.run([node,str(ROOT/'tests/frontend'/filename)],cwd=ROOT,env=os.environ,check=True)
 finally:
  server.terminate()
  try:server.wait(timeout=5)
  except subprocess.TimeoutExpired:server.kill();server.wait()
  log.close()
print('PASS frontend states generated from the actual API; isolated manager and game checks.')
