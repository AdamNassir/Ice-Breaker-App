const {JSDOM,VirtualConsole}=require('jsdom');
const fs=require('node:fs'),assert=require('node:assert/strict');
const fixture=JSON.parse(fs.readFileSync(process.env.QA_FIXTURE));
const wait=()=>new Promise(r=>setImmediate(r));
(async()=>{
 const errors=[],vc=new VirtualConsole();vc.on('jsdomError',e=>errors.push(e.message));
 function dom(file,url){return new JSDOM(fs.readFileSync(process.env.QA_PROJECT+'/static/'+file,'utf8'),{url,runScripts:'outside-only',pretendToBeVisual:true,virtualConsole:vc});}
 function load(w,files){for(const file of files)w.eval(fs.readFileSync(process.env.QA_PROJECT+'/static/'+file,'utf8'));}
 for(const answer of ['AI','HUMAN']){
  const browser=dom('bonus.html','https://game.test/bonus'),w=browser.window,d=w.document;let requests=0;w.fetch=()=>{requests++;throw Error('No requests allowed');};
  load(w,['workflow.js','bonus.js']);assert(d.querySelector('.build-workflow').hidden);
  d.querySelector(`[data-answer="${answer}"]`).click();assert(!d.querySelector('.build-workflow').hidden);assert.equal(d.getElementById('bonus-reveal').textContent,'AI');assert.equal(d.querySelectorAll('.workflow-step').length,6);assert.equal(requests,0);w.close();
 }
 for(const initial of [false,true]){
  const final=fixture.rows.at(-1).player,browser=dom('index.html','https://game.test/?room='+final.code),w=browser.window,d=w.document;let poll,calls=0,stamp=Date.now()/1000;
  w.AbortController=global.AbortController;w.setInterval=(fn,ms)=>{if(ms===1500)poll=fn;return 1;};
  w.localStorage.setItem('icebreaker:player:'+final.code,JSON.stringify(fixture.player));
  if(initial)w.localStorage.setItem('icebreaker:bonus:'+final.code,'answered');
  w.fetch=async(path,options)=>{assert(!options.body);calls++;return {ok:true,json:async()=>({...final,server_time:++stamp})};};
  load(w,['newsarticle.js','media.js','imagezoom.js','workflow.js','app.js']);await wait();await wait();
  const workflow=d.querySelector('.build-workflow');assert(workflow);assert.equal(workflow.hidden,!initial);
  const scores=[...d.querySelectorAll('.final-score')].map(n=>n.textContent),before=calls;
  if(!initial)d.querySelector('.player-bonus .vote-controls button').click();
  assert.equal(calls,before);assert(!workflow.hidden);assert(d.querySelector('.player-bonus .vote-controls').hidden);
  await poll();assert.equal(d.querySelector('.build-workflow'),workflow);assert(!workflow.hidden);assert.deepEqual([...d.querySelectorAll('.final-score')].map(n=>n.textContent),scores);
  const text=workflow.textContent;for(const term of ['agent','instruction file','question manager','UpdateGuide.md','tested again','illustrative'])assert(text.includes(term));
  assert.equal(w.localStorage.getItem('icebreaker:bonus:'+final.code),'answered');w.close();
 }
 assert.deepEqual(errors,[]);console.log('PASS both standalone bonus answers, AI player answer, persisted reveal after page restore, hidden-before-answer workflow, exact six steps, unchanged scores/no vote API and poll stability.');
})().catch(e=>{console.error(e);process.exit(1);});
