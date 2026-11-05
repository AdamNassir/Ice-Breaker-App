"""Actual Chromium DOM smoke test without navigating to blocked external URLs.

Run: python tests/check_final_ranking_browser.py
"""
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'static/app.js').read_text()
# Browser preview uses about:blank, so force room code only in this test harness.
APP = re.sub(r'const initialCode = \(query\.get\(.room.\) \|\| lastHost\)\.toUpperCase\(\);',
             "const initialCode = 'ABCDEF';", APP, count=1)
assert "const initialCode = 'ABCDEF';" in APP


def snapshot(count, rank_type='teams'):
    rows = [
        {'id':'t1','nickname':'Les Décodeurs','score':1750,'rank':1,'streak':2,'correct':6},
        {'id':'t2','nickname':'Les Visionnaires','score':1600,'rank':2,'streak':1,'correct':5},
        {'id':'t3','nickname':'Les Explorateurs','score':1300,'rank':3,'streak':2,'correct':4},
        {'id':'t4','nickname':'Équipe Alpha','score':900,'rank':4,'streak':0,'correct':2},
        {'id':'t5','nickname':'Équipe Beta','score':900,'rank':4,'streak':0,'correct':2},
    ]
    if rank_type == 'players':
        rows[0]['nickname']='Ada'; rows[1]['nickname']='Grace'
    return {
       'code':'ABCDEF', 'title':'AI or HUMAN?', 'phase':'finished', 'round_count':count,
       'round_index':count-1, 'round_number':count, 'revision':51, 'server_time':1000,
       'deadline':None, 'duration':25,'player_count':9, 'answered_count':9,
       'leaderboard':rows, 'ranking_type':rank_type, 'completed_rounds':count,
       'question':None, 'reveal':None,'me':{'id':'p1', 'nickname':'Ada','team_id':'t1','score':1750,'streak':2,'rank':1,'history':[]},
       'teams':[{'id':r['id'],'name':r['nickname'],'creator':{'id':'p1','nickname':'Ada'},'members':[] } for r in rows] if rank_type=='teams' else [],
       'teams_enabled':True,'teams_open':False,'team_results':{},'pool_deadline':None
    }


def html_text(role):
    html=(ROOT/'static'/('presenter.html' if role=='presenter' else 'index.html')).read_text()
    html=re.sub(r'<script\b[^>]*src=[^>]*></script>','',html)
    html=re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*>','',html)
    return html


def run(page, role, count):
    s=snapshot(count)
    page.set_viewport_size({'width':320 if role=='player' else 1280,'height':900})
    page.set_content(html_text(role),wait_until='domcontentloaded')
    page.add_style_tag(content=(ROOT/'static/style.css').read_text())
    storage_key='icebreaker:'+('host' if role=='presenter' else 'player')+':ABCDEF'
    init='''(args) => {
       const storage = new Map([[args.key, JSON.stringify({code:'ABCDEF',token:'test-token'})]]);
       const session = {getItem:k=>storage.get(k)||null, setItem:(k,v)=>storage.set(k,v), removeItem:k=>storage.delete(k)};
       Object.defineProperty(window,'localStorage',{configurable:true,value:session});
       Object.defineProperty(window,'sessionStorage',{configurable:true,value:session});
       window.history.replaceState=()=>{};
       window.fetch=async path=>({ok:true,json:async()=>path.endsWith('/qr')?{qr_matrix:Array.from({length:21},()=>Array(21).fill(false)),join_url:'https://example.org/?room=ABCDEF'}:window.__rankingSnapshot});
       window.__rankingSnapshot=args.snapshot;
       window.setInterval=()=>1;
       window.IcebreakerWorkflow={create:()=>{let x=document.createElement('div');x.className='build-workflow';return x;}};
       window.matchMedia=()=>({matches:true});
    }'''
    page.evaluate(init, {'key':storage_key,'snapshot':s})
    if role=='presenter':
        page.evaluate('''() => {HTMLCanvasElement.prototype.getContext=()=>({fillRect(){},set fillStyle(x){}});}''')
    page.evaluate(APP)
    page.wait_for_selector('.final-standings .final-heading',timeout=10000)
    assert page.locator('.final-heading').inner_text()=='Final team ranking'
    assert page.locator('.final-summary').inner_text()==f'{count} round'+('' if count==1 else 's')+' completed · 5 teams ranked · Points'
    assert page.locator('#stage .final-player').count()==5
    assert [int(v) for v in page.locator('#stage .final-player').evaluate_all('(items)=>items.map(n=>n.dataset.rank)')]==[1,2,3,4,4]
    assert page.locator('#stage .final-medal').count()==3
    assert page.locator('.results-mode').count()==1
    assert page.locator('#control-button').is_hidden() if role=='presenter' else page.locator('#vote-controls').is_hidden()
    if role=='player':
        assert page.locator('.final-me').count()==1
        assert page.locator('.player-bonus').count()==0
        assert 'Was this game made with AI or not ?' not in page.locator('#stage').inner_text()
        assert page.locator('.build-workflow').count()==0
    else:
        assert page.locator('.player-bonus').count()==0
    widths=page.evaluate('''() => ({scroll:document.documentElement.scrollWidth, client:document.documentElement.clientWidth})''')
    assert widths['scroll']<=widths['client']+1, (role,count,widths)
    if count==6:
        page.screenshot(path=str(ROOT.parent / f'final_team_ranking_{role}.png'),full_page=True)
    page.evaluate('''() => {window.__rankingSnapshot.server_time++;}''')
    # verify a refreshed finished snapshot preserves all team placements
    assert page.locator('#stage .final-player').count()==5
    page.set_content('<div>clear</div>')


with sync_playwright() as playwright:
    browser=playwright.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    try:
        page=browser.new_page()
        for role in ['presenter','player']:
            for count in [1,6,200]:
                run(page, role,count)
                print('PASS', role, count,'rounds',flush=True)
        page.close()
    finally:
        browser.close()
