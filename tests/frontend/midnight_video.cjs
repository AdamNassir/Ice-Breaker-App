/* Midnight preference and real host video-end transition without a cloud browser. */
const {JSDOM}=require('jsdom');
const fs=require('node:fs');
const assert=require('node:assert/strict');
const root=process.env.QA_PROJECT || process.cwd();
const fixture=JSON.parse(fs.readFileSync(process.env.QA_FIXTURE));
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function until(fn){for(let i=0;i<100;i++){if(fn())return;await pause(10);}throw Error('Timed out waiting for video state');}
(async()=>{
  const game=JSDOM.fragment('<button class="theme-toggle">Midnight mode</button>');
  const themePage=new JSDOM('<!doctype html><html><body><button class="theme-toggle">Midnight mode</button></body></html>',{url:'https://example.com/',runScripts:'outside-only'});
  const t=themePage.window;
  t.eval(fs.readFileSync(root+'/static/theme.js','utf8'));
  t.document.dispatchEvent(new t.Event('DOMContentLoaded'));
  assert.equal(t.document.documentElement.dataset.theme,'light');
  t.document.querySelector('button').click();
  assert.equal(t.document.documentElement.dataset.theme,'midnight');
  assert.equal(t.document.querySelector('button').getAttribute('aria-pressed'),'true');
  assert.equal(t.localStorage.getItem('icebreaker:theme'),'midnight');
  t.document.querySelector('button').click();
  assert.equal(t.document.documentElement.dataset.theme,'light');
  themePage.window.close();

  const base='https://example.com';
  const question={title:'Video test',kind:'video',media:'/static/videos/test.mp4',context:'Optional context'};
  const source=fs.readFileSync(root+'/static/presenter.html','utf8');
  const page=new JSDOM(source,{url:base+'/presenter?room='+fixture.room.code,runScripts:'outside-only',pretendToBeVisual:true});
  const w=page.window,d=w.document;
  w.AbortController=global.AbortController;
  w.HTMLCanvasElement.prototype.getContext=()=>({fillRect(){},fillStyle:''});
  w.setInterval=()=>0;
  w.sessionStorage.setItem('icebreaker:host:'+fixture.room.code,JSON.stringify(fixture.room));
  const starting={...fixture.rows[1].host,phase:'watching',deadline:null,revision:3,question,
                  reveal:null,server_time:Date.now()/1000,round_index:0,round_number:1,round_count:1};
  let snapshot=starting,completionCalls=0;
  w.fetch=async (url,options={})=>{
    if(url.endsWith('/qr'))return {ok:true,json:async()=>fixture.qr};
    if(url.endsWith('/state'))return {ok:true,json:async()=>({...snapshot,server_time:Date.now()/1000})};
    if(url.endsWith('/control')){
      const command=JSON.parse(options.body);
      assert.equal(command.action,'begin_voting');
      assert.equal(snapshot.phase,'watching');
      assert.equal(command.revision,3);
      completionCalls++;
      snapshot={...snapshot,phase:'live',deadline:Date.now()/1000+10,revision:4,server_time:Date.now()/1000};
      return {ok:true,json:async()=>snapshot};
    }
    throw Error('Unexpected URL '+url);
  };
  w.eval(fs.readFileSync(root+'/static/media.js','utf8'));
  w.eval(fs.readFileSync(root+'/static/app.js','utf8'));
  await until(()=>d.querySelector('#stage video'));
  assert.equal(d.getElementById('control-button').textContent,'Video cannot finish? Start voting');
  assert.equal(d.getElementById('clock-wrap').hidden,true);
  d.querySelector('#stage video').dispatchEvent(new w.Event('ended'));
  await until(()=>completionCalls===1);
  await until(()=>d.getElementById('control-button').textContent==='Round in progress');
  assert.equal(d.getElementById('clock-wrap').hidden,false);
  d.querySelector('#stage video').dispatchEvent(new w.Event('ended'));
  assert.equal(completionCalls,1);
  page.window.close();
  console.log('PASS midnight mode persistence; video ends before presenter-authorized 10-second voting countdown.');
})().catch(e=>{console.error(e);process.exit(1);});
