/* Multiple phone DOMs exercise the real local game API, not canned team responses. */
const {JSDOM,VirtualConsole}=require('jsdom');
const assert=require('node:assert/strict'),fs=require('node:fs');
const base=process.env.QA_GAME_BASE,project=process.env.QA_PROJECT;
const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function until(fn){for(let i=0;i<200;i++){if(fn())return;await wait(15);}throw Error('Team UI condition timed out');}
async function request(path,body,token){
 const response=await fetch(base+path,{method:body===undefined?'GET':'POST',headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{})},body:body===undefined?undefined:JSON.stringify(body)});
 const result=await response.json();assert(response.ok,JSON.stringify(result));return result;
}

(async()=>{
 const room=await request('/api/rooms',{seconds:10});
 const pages=[],errors=[];
 const html=await (await fetch(base+'/?room='+room.code)).text();
 async function phone(nickname,saved){
  const vc=new VirtualConsole();vc.on('jsdomError',e=>errors.push(e.message));
  const page=new JSDOM(html,{url:base+'/?room='+room.code,runScripts:'outside-only',pretendToBeVisual:true,virtualConsole:vc});
  pages.push(page);const w=page.window,d=w.document;
  let poll;
  w.AbortController=global.AbortController;w.fetch=(path,options)=>fetch(new URL(path,base),options);
  w.setInterval=(fn,ms)=>{if(ms===1500)poll=fn;return 1;};
  if(saved)w.localStorage.setItem('icebreaker:player:'+room.code,JSON.stringify(saved));
  const css=d.createElement('style');css.textContent=fs.readFileSync(project+'/static/style.css','utf8');d.head.append(css);
  for(const script of ['newsarticle.js','media.js','imagezoom.js','workflow.js','app.js'])w.eval(fs.readFileSync(project+'/static/'+script,'utf8'));
  if(!saved){
   assert.equal(d.getElementById('room-code').value,room.code,'QR pre-fills room code');
   d.getElementById('nickname').value=nickname;
   d.getElementById('join-form').dispatchEvent(new w.Event('submit',{bubbles:true,cancelable:true}));
  }
  await until(()=>!d.getElementById('team-lobby').hidden&&d.getElementById('team-player').textContent.includes(nickname));
  return {w,d,poll:()=>poll(),session:JSON.parse(w.localStorage.getItem('icebreaker:player:'+room.code)),
          mode:kind=>d.querySelector(`[data-team-mode="${kind}"]`).click()};
 }
 try{
  const ada=await phone('Ada'),linus=await phone('Linus');
  ada.mode('create');
  const name=ada.d.getElementById('team-name');name.value='Draft name';
  await ada.poll();assert.equal(name.value,'Draft name','poll must preserve typing/focus');
  assert.equal(ada.w.getComputedStyle(ada.d.querySelector('.stage')).display,'none');
  linus.mode('join');assert(linus.d.querySelector('.teams-empty'));
  name.value='Les Décodeurs';
  ada.d.getElementById('team-create-form').dispatchEvent(new ada.w.Event('submit',{bubbles:true,cancelable:true}));
  await until(()=>ada.d.getElementById('team-heading').textContent==='Your team');
  assert.equal(ada.d.querySelector('.team-card-title').textContent,'Les Décodeurs | Ada');
  assert.deepEqual([...ada.d.querySelectorAll('.team-members li')].map(n=>n.textContent),['Ada']);
  await linus.poll();
  assert.equal(linus.d.querySelector('.team-card-title').textContent,'Les Décodeurs | Ada');
  assert.deepEqual([...linus.d.querySelectorAll('.team-members li')].map(n=>n.textContent),['Ada']);
  linus.d.querySelector('[data-join-team]').click();
  await until(()=>linus.d.getElementById('team-heading').textContent==='Your team');
  await ada.poll();
  assert.deepEqual([...ada.d.querySelectorAll('.team-members li')].map(n=>n.textContent),['Ada','Linus']);
  const restored=await phone('Linus',linus.session);
  assert.equal(restored.d.querySelector('.team-card-title').textContent,'Les Décodeurs | Ada');
  assert(restored.d.querySelector('.team-selected'));
  assert(restored.d.getElementById('team-choices').hidden);
  const card=restored.d.querySelector('.team-card');await restored.poll();assert.equal(restored.d.querySelector('.team-card'),card,'unchanged polls do not recreate roster');

  const other=await phone('Grace');other.mode('create');
  const hostile='<img src=x onerror=alert(1)>';
  other.d.getElementById('team-name').value=hostile;
  other.d.getElementById('team-create-form').dispatchEvent(new other.w.Event('submit',{bubbles:true,cancelable:true}));
  await until(()=>other.d.getElementById('team-heading').textContent==='Your team');
  await ada.poll();assert.equal(ada.d.querySelectorAll('.team-card').length,2);
  assert(!ada.d.querySelector('#team-list img,#team-list [onerror]'));
  assert([...ada.d.querySelectorAll('.team-card-title')].some(n=>n.textContent===hostile+' | Grace'));

  const before=await request(`/api/rooms/${room.code}/state`,undefined,room.token);
  assert.equal(before.teams.length,2);assert.equal(before.teams[0].members.length,2);
  await request(`/api/rooms/${room.code}/control`,{action:'start',revision:before.revision},room.token);
  for(const page of [ada,linus,restored,other]){
   await page.poll();assert(page.d.getElementById('team-lobby').hidden);
   assert(!page.d.body.classList.contains('player-team-lobby'));
   assert(!page.d.getElementById('vote-controls').hidden);
   assert(page.d.querySelector('.question-title'));
   assert(!page.d.getElementById('my-team-label').hidden);
  }
  assert.equal(linus.d.getElementById('my-team-label').textContent,'Les Décodeurs | Ada');
  const late=await fetch(base+`/api/rooms/${room.code}/teams`,{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+linus.session.token},body:JSON.stringify({name:'Too late'})});
  assert.equal(late.status,409);
  const answer=linus.d.querySelector('[data-answer="AI"]');answer.click();
  await until(()=>linus.d.getElementById('vote-status').textContent.includes('locked in'));
  assert.deepEqual(errors,[]);
  console.log('PASS teams: actual API and multiple phone DOMs; QR join, create/join choices, live creator/member directory, typing/poll preservation, refresh, safe text, lock on start and normal individual voting.');
 }finally{for(const page of pages)page.window.close();}
})().catch(error=>{console.error(error);process.exit(1);});
