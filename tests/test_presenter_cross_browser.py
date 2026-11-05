"""Chromium browser-context regression for Mercato presenter handoff.

No external navigation: this sandbox blocks browser URLs, so render the real
presenter HTML and execute the shipped JS with simulated URL fragments and API
responses. Two isolated browser contexts represent different computers.
"""
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'static/presenter.html').read_text()
HTML = re.sub(r'<script\b[^>]*src=[^>]*></script>', '', HTML)
HTML = re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*>', '', HTML)
SCRIPT = (ROOT / 'static/app.js').read_text()
SCRIPT = SCRIPT.replace('new URLSearchParams(location.search)', 'new URLSearchParams(window.__queryString)', 1)
SCRIPT = SCRIPT.replace("new URLSearchParams(location.hash.replace(/^#/, ''))", 'new URLSearchParams(window.__hashString)', 1)
assert 'window.__queryString' in SCRIPT and 'window.__hashString' in SCRIPT
CODE = 'ABC234'
TOKEN = 'secretPresenterTokenForAnotherBrowser_X1-Y2-Z3'


def open_presenter(browser, query, fragment):
    context = browser.new_context()
    page = context.new_page()
    page.set_content(HTML, wait_until='domcontentloaded')
    page.evaluate('''({query,fragment,token}) => {
      window.__queryString = query;
      window.__hashString = fragment;
      window.__url = '';
      window.__copied = '';
      const items = new Map();
      const local = {
        getItem: k => items.get(k) || null,
        setItem: (k,v) => items.set(k,v),
        removeItem: k => items.delete(k)
      };
      Object.defineProperty(window, 'sessionStorage', {configurable:true,value:local});
      window.history.replaceState = (_, _title, url) => {window.__url=url;};
      window.setInterval = () => 1;
      Object.defineProperty(navigator, 'clipboard', {configurable:true,
        value:{writeText:async value => {window.__copied=value;}}});
      window.fetch = async (path, opts={}) => {
        const ok=opts.headers?.Authorization === 'Bearer '+token;
        return ok ? {ok:true,json:async()=>({
          code:'ABC234', title:'Seminar Game', phase:'lobby', round_index:0,
          round_number:1, round_count:6, revision:0,server_time:1000,
          deadline:null, duration:25,player_count:1,answered_count:0,
          leaderboard:[],question:null,reveal:null,teams:[],teams_enabled:true,
          teams_open:true,ranking_type:'teams',me:null
        })} : {ok:false,status:401,json:async()=>({detail:'Game token required'})};
      };
    }''', {'query':query,'fragment':fragment,'token':TOKEN})
    page.evaluate(SCRIPT)
    return context,page


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True,
                               args=['--no-sandbox','--disable-dev-shm-usage'])
    try:
        ctx1,a=open_presenter(browser, '?room='+CODE+'&seminar=1', 'host_token='+TOKEN)
        a.wait_for_function("document.querySelector('#game')?.hidden === false")
        first_url = a.evaluate('window.__url')
        assert first_url == '/presenter?room=ABC234&seminar=1#host_token='+TOKEN,first_url
        assert a.locator('#entry').is_hidden()
        assert a.locator('#room-title').inner_text()=='Seminar Game'
        a.locator('#copy-presenter-link').click()
        a.wait_for_function('window.__copied.includes("#host_token=")')
        assert a.evaluate('window.__copied').endswith('#host_token='+TOKEN)
        # Independent tab/browser: empty session storage, only the full URL.
        ctx2,b=open_presenter(browser,'?'+first_url.split('?',1)[1].split('#')[0],first_url.split('#',1)[1])
        b.wait_for_function("document.querySelector('#game')?.hidden === false")
        assert b.locator('#entry').is_hidden()
        assert b.locator('#control-button').inner_text()=='Start round 1'
        assert b.evaluate('window.__url')==first_url
        # A copied address with no token must not grant access to presenter.
        ctx3,c=open_presenter(browser,'?room='+CODE+'&seminar=1','')
        c.wait_for_function("document.querySelector('#seminar-link-help')?.hidden === false")
        assert c.locator('#create-form').is_hidden()
        assert c.locator('#game').is_hidden()
        assert c.evaluate('window.__url')==''
        print('PASS: 2 isolated Chromium contexts enter existing room with full private link; address URL retains token; missing token shows help not password')
        for context in (ctx1,ctx2,ctx3): context.close()
    finally: browser.close()
