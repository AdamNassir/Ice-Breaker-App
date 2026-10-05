const {JSDOM,VirtualConsole}=require('jsdom');
const fs=require('node:fs'),assert=require('node:assert/strict');
const fixture=JSON.parse(fs.readFileSync(process.env.QA_FIXTURE));
const wait=()=>new Promise(r=>setImmediate(r));
async function until(fn){for(let i=0;i<100;i++){if(fn())return;await wait();}throw Error('Condition timed out');}
(async()=>{
 const errors=[],vc=new VirtualConsole();vc.on('jsdomError',e=>errors.push(e.message));
 const dom=new JSDOM(fs.readFileSync(process.env.QA_PROJECT+'/static/presenter.html','utf8'),{url:'https://game.example.test/presenter?room='+fixture.room.code,runScripts:'outside-only',pretendToBeVisual:true,virtualConsole:vc});
 const w=dom.window,d=w.document,button=d.getElementById('control-button');let poll,current=fixture.rows[0].host,stamp=Date.now()/1000,requests=[],release;
 w.AbortController=global.AbortController;w.setInterval=(fn,ms)=>{if(ms===1500)poll=fn;return 1;};
 w.HTMLCanvasElement.prototype.getContext=()=>({fillRect(){},fillStyle:''});
 w.sessionStorage.setItem('icebreaker:host:'+fixture.room.code,JSON.stringify(fixture.room));
 const response=()=>({ok:true,json:async()=>({...current,server_time:++stamp,deadline:current.phase==='live'?stamp+10:current.deadline})});
 w.fetch=async(path,options)=>{
  if(path.endsWith('/qr'))return {ok:true,json:async()=>fixture.qr};
  if(path.endsWith('/control')){
   const body=JSON.parse(options.body);requests.push(body);
   assert.equal(body.revision,current.revision);
   if(body.action==='start'){assert.equal(current.phase,'lobby');current=fixture.rows[1].host;}
   else {
    assert.equal(current.phase,'revealed');
    current=current.round_index===9?fixture.rows.at(-1).host:fixture.rows.find(r=>r.phase==='live'&&r.host.round_index===current.round_index+1).host;
    await new Promise(resolve=>{release=resolve;});
   }
  }
  return response();
 };
 w.eval(fs.readFileSync(process.env.QA_PROJECT+'/static/media.js','utf8'));w.eval(fs.readFileSync(process.env.QA_PROJECT+'/static/app.js','utf8'));
 const enter=(target=d.body,extra={})=>{const event=new w.KeyboardEvent('keydown',{key:'Enter',bubbles:true,cancelable:true,...extra});target.dispatchEvent(event);return event;};
 await until(()=>button.textContent==='Start round 1'&&!button.disabled&&d.getElementById('room-meta').textContent.includes('1 player'));
 enter();assert.equal(requests.length,0);button.click();await until(()=>button.textContent==='Round in progress');
 enter();assert.equal(requests.length,1);
 for(let i=0;i<10;i++){
  current=fixture.rows.find(r=>r.phase==='revealed'&&r.host.round_index===i).host;
  await poll();assert.equal(button.textContent,i===9?'Show final results':'Next round');
  const count=requests.length;
  enter(d.body,{repeat:true});enter(d.body,{ctrlKey:true});enter(d.body,{isComposing:true});
  enter(d.getElementById('game-title'));enter(d.getElementById('copy-link'));
  const editable=d.createElement('div');editable.setAttribute('contenteditable','true');d.body.append(editable);enter(editable);editable.remove();
  assert.equal(requests.length,count);
  if(i===2)button.click();else assert(enter(i===1?button:d.body).defaultPrevented);
  assert.equal(requests.length,count+1);assert.equal(requests.at(-1).action,'next');
  enter();enter(d.body,{repeat:true});button.click();assert.equal(requests.length,count+1);
  release();await until(()=>i===9?d.body.classList.contains('results-mode'):button.textContent==='Round in progress'&&d.getElementById('round-label').textContent.includes(String(i+2)));
  if(i<9){assert(button.disabled);assert.equal(d.getElementById('clock').textContent,'10');assert(!d.getElementById('stage').hidden);assert(d.getElementById('qr-lobby').hidden);}
 }
 enter();assert.equal(requests.length,11);assert(button.hidden);assert.deepEqual(errors,[]);
 const player=fs.readFileSync(process.env.QA_PROJECT+'/static/index.html','utf8'),presenter=fs.readFileSync(process.env.QA_PROJECT+'/static/presenter.html','utf8');
 for(const text of ['Posts. Text. Images.',"Who made what you're looking at?",'Streak bonuses','2 choices'])assert(!player.includes(text));
 for(const html of [player,presenter])assert(!html.includes('AI means generated. HUMAN includes'));
 assert(!presenter.includes('You set the pace.'));assert(!presenter.includes('They make the call.'));
 w.close();console.log('PASS Enter/click advances and immediately starts all next rounds; fresh timer, repeated/pending key guards, form/editable guards, manual first start, final results and removed intro copy.');
})().catch(e=>{console.error(e);process.exit(1);});
