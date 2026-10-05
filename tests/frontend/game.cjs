const {JSDOM,VirtualConsole}=require('jsdom');
const assert=require('node:assert/strict'),fs=require('node:fs');
const project=process.env.QA_PROJECT,base=process.env.QA_MANAGER_BASE||'http://127.0.0.1:8770',errors=[];
const fixture=JSON.parse(fs.readFileSync(process.env.QA_FIXTURE));
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function until(fn){for(let i=0;i<200;i++){if(fn())return;await sleep(20);}throw Error('DOM condition timed out');}
function dom(file,url){const vc=new VirtualConsole();vc.on('jsdomError',e=>errors.push(e.message));return new JSDOM(fs.readFileSync(project+'/'+file,'utf8'),{url,runScripts:'outside-only',pretendToBeVisual:true,virtualConsole:vc});}
function set(w,id,value,type='input'){const el=w.document.getElementById(id);el.value=value;el.dispatchEvent(new w.Event(type,{bubbles:true}));}
function shared(w){w.eval(fs.readFileSync(project+'/static/media.js','utf8'));w.eval(fs.readFileSync(project+'/static/imagezoom.js','utf8'));w.eval(fs.readFileSync(project+'/static/workflow.js','utf8'));}
(async()=>{
 const editor=dom('manager_assets/index.html',base),w=editor.window,d=w.document,$=id=>d.getElementById(id);
 w.fetch=(path,options)=>fetch(new URL(path,base),options);w.AbortController=global.AbortController;w.confirm=()=>true;
 assert.deepEqual([...d.querySelectorAll('.brand-logos img')].map(n=>n.alt),['LogicLever','TotalEnergies']);shared(w);w.eval(fs.readFileSync(project+'/manager_assets/app.js','utf8'));
 await until(()=>!$('add-image').disabled);assert.equal($('question-count').textContent,'10');assert($('status').hidden);
 d.querySelectorAll('.question-item')[8].click();assert(d.querySelector('#preview img').src.endsWith('/static/images/sample19.png'));
 let player;
 d.querySelectorAll('.question-item')[6].click();assert(d.querySelector('#preview img').src.endsWith('/static/images/sample25.png'));
 d.querySelectorAll('.question-item')[2].click();assert(d.querySelector('#preview img').src.endsWith('/static/images/sample23.png'));assert(!d.querySelector('#preview audio'));
 $('add-video').click();set(w,'title','Linked clip');set(w,'answer','HUMAN');set(w,'media-mode','link','change');set(w,'media-url','https://youtu.be/fn3KWM1kuAw');set(w,'media-start','2');set(w,'media-end','8');
 player=d.querySelector('#preview iframe');assert(player);assert.equal(new URL(player.src).searchParams.get('start'),'2');assert.equal(new URL(player.src).searchParams.get('end'),'8');
 $('save-deck').click();await until(()=>$('status').textContent.startsWith('Deck saved.')&&!$('save-deck').disabled);
 let saved=JSON.parse(fs.readFileSync(project+'/questions.json')).rounds;assert.equal(saved.length,11);assert.equal(saved[5].image_highlight.x,35.5);assert.deepEqual(saved[4].reveal_sources,JSON.parse(fs.readFileSync(process.env.QA_ORIGINAL+'/questions.json')).rounds[4].reveal_sources);assert(saved[1].image_reveal.includes('1987–88'));assert.equal(saved[10].media_start,2);assert.equal(saved[10].media,'');
 // A successful local upload must clear a prior link, and keep the uploaded bytes.
 set(w,'media-mode','local','change');const bytes=fs.readFileSync(project+'/static/audio/sample17.mp3');
 set(w,'kind','audio','change');Object.defineProperty($('media-file'),'files',{configurable:true,value:[new File([bytes],'voice.mp3')]});$('media-file').dispatchEvent(new w.Event('change',{bubbles:true}));
 await until(()=>$('media-path').value.endsWith('.mp3')&&!$('media-file').disabled);assert(fs.readFileSync(project+$('media-path').value).equals(bytes));assert.equal($('media-url').value,'');assert(d.querySelector('#preview audio'));
 $('save-deck').click();await until(()=>$('status').textContent.startsWith('Deck saved.')&&!$('save-deck').disabled);
 saved=JSON.parse(fs.readFileSync(project+'/questions.json')).rounds;assert.equal(saved[10].media_url,'');assert(saved[10].media.endsWith('.mp3'));
 // Shared playback boundaries and hostile YouTube host rejection.
 const M=w.IcebreakerMedia;assert.equal(M.youtubeId('https://youtube.com.evil.test/watch?v=fn3KWM1kuAw'),null);assert.equal(M.youtubeId('https://user:secret@youtube.com/watch?v=fn3KWM1kuAw'),null);
 const audio=M.create({kind:'audio',media:'/static/audio/sample17.mp3',media_start:2,media_end:8},'round-audio',()=>{});Object.defineProperty(audio,'duration',{value:10});let pauses=0;audio.pause=()=>pauses++;
 audio.dispatchEvent(new w.Event('loadedmetadata'));assert.equal(audio.currentTime,2);audio.currentTime=9;audio.dispatchEvent(new w.Event('timeupdate'));assert.equal(audio.currentTime,8);assert.equal(pauses,1);audio.dispatchEvent(new w.Event('play'));assert.equal(audio.currentTime,2);
 editor.window.close();
 console.log('PASS manager: ten image/text rounds, French Macron and manager reply, custom YouTube/audio previews, clip boundaries, save/reload, local upload clears link, unchanged bytes, URL guards.');
 for(const role of ['host','player']){
  const page=dom('static/'+(role==='host'?'presenter.html':'index.html'),'https://game.example.test/'+(role==='host'?'presenter':'')+'?room='+fixture.room.code);
  const pw=page.window,pd=pw.document;const css=pd.createElement('style');css.textContent=fs.readFileSync(project+'/static/style.css','utf8');pd.head.append(css);let poll,current=fixture.rows[0][role],tick=0;
  pw.AbortController=global.AbortController;pw.setInterval=(fn,ms)=>{if(ms===1500)poll=fn;return 1;};pw.HTMLCanvasElement.prototype.getContext=()=>({fillRect(){},fillStyle:''});
  const storage=role==='host'?pw.sessionStorage:pw.localStorage;storage.setItem('icebreaker:'+role+':'+fixture.room.code,JSON.stringify(role==='host'?fixture.room:fixture.player));
  pw.fetch=async path=>({ok:true,json:async()=>{if(path.endsWith('/qr'))return fixture.qr;const stamp=Date.now()/1000+(++tick)*100;return {...current,server_time:stamp,deadline:current.phase==='live'?stamp+10:current.deadline};}});
  assert.deepEqual([...pd.querySelectorAll('.brand-logos img')].map(n=>n.alt),['LogicLever','TotalEnergies']);assert.equal(pw.getComputedStyle(pd.documentElement).getPropertyValue('--blue'),'#1f2ade');assert.equal(pw.getComputedStyle(pd.documentElement).getPropertyValue('--red'),'#e52330');shared(pw);pw.eval(fs.readFileSync(project+'/static/app.js','utf8'));await sleep(10);
  for(const row of fixture.rows){current=row[role];await poll();const q=current.question;
   if(row.phase==='live'){
    assert(!pd.querySelector('#stage audio,#stage video,#stage iframe'),'default deck has no recording rounds');
    if(role==='host'){assert(pd.getElementById('qr-lobby').hidden);assert(!pd.getElementById('stage').hidden);assert(!pd.querySelector('#leaderboard'));assert.equal(pw.getComputedStyle(pd.querySelector('.presenter-grid')).display,'block');}
    assert(pd.getElementById('reveal').hidden);assert(!pd.querySelector('.image-highlight'));assert(!pd.querySelector('.photo-credit'));assert(!pd.querySelector('.text-sources'));assert(!pd.querySelector('.confetti-layer'));assert(!pd.querySelector('.difficulty'));assert(!pd.querySelector('.question-context'));assert.equal(pd.querySelector('#stage .question-title').textContent,q.title);assert.equal(pd.querySelector('#stage .question-intro').textContent,q.context);assert(!pd.querySelector('#stage .kind'));assert.equal(pd.getElementById('clock').textContent,'10');
    if(q.kind==='image')assert(pd.querySelector('#stage img').src.endsWith(q.media));
    else if(q.kind==='text'){assert.equal(pd.querySelector('#stage .text-content').textContent,q.body);assert(pd.getElementById('stage').classList.contains('text-stage'));assert.equal(pw.getComputedStyle(pd.getElementById('stage')).minHeight,'0');}
    else if(q.kind==='video'&&q.media_url.includes('youtube')){const iframe=pd.querySelector('#stage iframe');assert(iframe);assert.equal(new URL(iframe.src).hostname,'www.youtube-nocookie.com');assert.equal(new URL(iframe.src).searchParams.get('end'),'18');assert.equal(new URL(iframe.src).searchParams.get('hl'),'en');}
    else {const e=pd.querySelector('#stage '+q.kind);assert(e.controls);assert.equal(e.src,q.media_url||'https://game.example.test'+q.media);}
    const existing=pd.querySelector('#stage audio,#stage video,#stage iframe');await poll();if(existing)assert.equal(pd.querySelector('#stage audio,#stage video,#stage iframe'),existing,'polling must preserve playback');
   }else if(row.phase==='revealed'){assert.equal(pd.querySelector('.question-title').textContent,q.title);assert.equal(pd.querySelector('.question-intro').textContent,q.context);assert(!pd.getElementById('reveal').hidden);assert.equal(pd.querySelector('#reveal h3').textContent,current.reveal.answer);
    if(current.reveal.image_reveal){
     assert.equal(pd.querySelector('.photo-credit').textContent,current.reveal.image_reveal);
     assert.equal(pd.querySelector('.photo-source').href,current.reveal.source_url);
     assert.equal(pd.querySelector('#reveal').children.length,3);
    } else if(current.reveal.reveal_sources?.length){
     const links=[...pd.querySelectorAll('.text-source')];assert.equal(links.length,4);
     assert.deepEqual(links.map(a=>a.textContent),current.reveal.reveal_sources.map(s=>s.label));
     assert.deepEqual(links.map(a=>a.href),current.reveal.reveal_sources.map(s=>s.url));
     for(const a of links){assert.equal(a.target,'_blank');assert(a.rel.includes('noopener'));}
     assert(!pd.getElementById('reveal').textContent.includes(current.reveal.explanation));
     const panel=pd.querySelector('.text-sources');await poll();assert.equal(pd.querySelector('.text-sources'),panel);
    } else {assert.equal(pd.getElementById('reveal').textContent,current.reveal.answer);assert.equal(pd.getElementById('reveal').children.length,1);assert(!pd.querySelector('.photo-credit'));}
    if(current.reveal.image_highlight){
     const img=pd.querySelector('#stage img');Object.defineProperty(img,'naturalWidth',{value:1536});Object.defineProperty(img,'naturalHeight',{value:1024});img.dispatchEvent(new pw.Event('load'));
     const svg=pd.querySelector('.image-highlight'),circle=svg.querySelector('circle');assert.equal(svg.style.display,'');assert.equal(svg.getAttribute('viewBox'),'0 0 1536 1024');
     assert.equal(circle.getAttribute('stroke'),'#ff2020');assert.equal(Number(circle.getAttribute('cx')),current.reveal.image_highlight.x/100*1536);assert.equal(Number(circle.getAttribute('cy')),current.reveal.image_highlight.y/100*1024);assert.equal(Number(circle.getAttribute('r')),current.reveal.image_highlight.radius/100*1536);
    }else assert(!pd.querySelector('.image-highlight'));
    if(role==='player'){assert(pd.getElementById('vote-controls').hidden);assert.equal(pd.getElementById('vote-status').textContent,'');}else assert.equal(pd.getElementById('control-help').textContent,'');}
   else if(row.phase==='lobby'){if(role==='host'){assert(!pd.getElementById('qr-lobby').hidden);assert(pd.getElementById('stage').hidden);assert(!pd.querySelector('#stage img'));assert(!pd.querySelector('.question-heading'));assert(!pd.querySelector('#leaderboard'));assert.equal(pd.getElementById('control-button').textContent,'Start round 1');}}
   else{assert(pd.querySelector('.confetti-layer'));assert.equal(pd.querySelectorAll('.confetti-piece').length,24);const burst=pd.querySelector('.confetti-layer');await poll();assert.equal(pd.querySelector('.confetti-layer'),burst,'polling preserves one confetti burst');assert(pd.querySelector('.final-standings'));assert.equal(pd.querySelector('.final-name').textContent,'Fun Tester');assert.equal(pd.querySelector('.final-score').textContent,'1750');}
  }
  assert(!pd.querySelector('.scoring-note'));assert(!pd.querySelector('.share-url'));assert(!pd.querySelector('.qr-help'));
  if(role==='host'){
   assert(pd.getElementById('qr-lobby').hidden);assert(!pd.getElementById('join-qr').hidden);assert(pd.getElementById('qr-status').hidden);assert.equal(pd.getElementById('qr-status').textContent,'');
   let copied;Object.defineProperty(pw.navigator,'clipboard',{value:{writeText:async value=>{copied=value;}}});pd.getElementById('copy-link').click();await sleep(10);assert.equal(copied,fixture.qr.join_url);
  }
  current=fixture.placements[role];await poll();assert(pw.document.body.classList.contains('results-mode'));
  const placements=[...pd.querySelectorAll('#stage .final-player')];assert.deepEqual(placements.map(p=>Number(p.dataset.rank)),[1,2,3,4,4,6]);assert.equal(pd.querySelectorAll('.confetti-piece').length,72,'new room celebrates all three podium places');
  assert.deepEqual(placements.map(p=>p.querySelector('.final-name').textContent),['Ada','Linus','Grace','Alan','Margaret','Ken']);
  assert.deepEqual(placements.map(p=>p.querySelector('.final-score').textContent),['1750','1600','1400','1000','1000','750']);
  assert.deepEqual([...pd.querySelectorAll('#stage .final-medal')].map(p=>p.textContent),['🥇','🥈','🥉']);
  assert(!pd.querySelector('.bonus-link'));
  if(role==='host') {assert(!pd.querySelector('.build-workflow'));assert(!pd.querySelector('.player-bonus'));assert(!pd.querySelector('#stage h1,#stage h2,#stage p'));}
  else {
   const panel=pd.querySelector('.player-bonus');assert(panel);
   assert.equal(panel.querySelector('h2').textContent,'Was this game made with AI or not ?');
   assert.deepEqual([...panel.querySelectorAll('button')].map(n=>n.textContent),['AI','HUMAN']);
   assert(panel.querySelector('.bonus-reveal').hidden);assert(panel.querySelector('.build-workflow').hidden);
   const scoreBefore=placements.map(n=>n.querySelector('.final-score').textContent);
   panel.querySelectorAll('button')[1].click();
   assert(panel.querySelector('.vote-controls').hidden);assert(!panel.querySelector('.bonus-reveal').hidden);
   assert.equal(panel.querySelector('.bonus-reveal').textContent,'AI');assert(!panel.querySelector('.build-workflow').hidden);assert.equal(panel.querySelectorAll('.workflow-step').length,6);assert.deepEqual([...panel.querySelectorAll('.workflow-step h4')].map(n=>n.textContent),['One complete instruction file','The agent built and checked the app','I reviewed the code and tested it','I set up the question manager','UpdateGuide.md became the update loop','I verified the report and tested again']);assert(panel.querySelector('.build-workflow').textContent.includes('build, test, fix and test again'));
   assert.deepEqual([...pd.querySelectorAll('.final-score')].map(n=>n.textContent),scoreBefore);
  }
  assert.equal(pd.querySelectorAll('.final-list .final-medal').length,0);assert(!pd.querySelector('#stage .waiting'));
  pd.querySelectorAll('.topbar,footer,.game-heading,#round-progress,.round-toolbar,.side-card,.host-controls,#vote-status,#connection').forEach(node=>assert(node.hidden));
  const gold=placements[0],goldGroup=gold.closest('.podium-place'),silver=placements[1].closest('.podium-place');assert.equal(pw.getComputedStyle(goldGroup).gridColumn,'2');assert.equal(pw.getComputedStyle(silver).gridColumn,'1');
  current={...fixture.placements[role],leaderboard:fixture.placements[role].leaderboard.map((p,i)=>({...p,rank:i<2?1:i+1}))};await poll();assert.equal(pd.querySelectorAll('.podium-rank-1 .final-medal').length,2);assert(!pd.querySelector('.confetti-layer'),'rank updates must not restart confetti');if(role==='player'){assert(pd.querySelector('.player-bonus .vote-controls').hidden);assert(!pd.querySelector('.player-bonus .bonus-reveal').hidden);assert(!pd.querySelector('.build-workflow').hidden);}
  pw.matchMedia=()=>({matches:true});current={...current,code:'REDUCED'};await poll();assert(!pd.querySelector('.confetti-layer'),'reduced motion skips confetti');
  page.window.close();console.log('PASS '+role+': ten-second timer, question titles/short introductions, blue/red branding, AI/HUMAN reveals with configured photo credits, minimal podium, medals, numeric scores and tied ranks; QR/copy link retained.');
 }
 const bonus=dom('static/bonus.html','https://game.example.test/bonus'),bd=bonus.window.document;bonus.window.eval(fs.readFileSync(project+'/static/workflow.js','utf8'));bonus.window.eval(fs.readFileSync(project+'/static/bonus.js','utf8'));assert.equal(bd.querySelector('h1').textContent,'Was this game made with AI or not ?');assert(bd.getElementById('bonus-reveal').hidden);assert(bd.querySelector('.build-workflow').hidden);bd.querySelector('[data-answer=HUMAN]').click();assert(bd.getElementById('bonus-choices').hidden);assert(!bd.getElementById('bonus-reveal').hidden);assert.equal(bd.getElementById('bonus-reveal').textContent,'AI');assert(!bd.querySelector('.build-workflow').hidden);assert.equal(bd.querySelectorAll('.workflow-step').length,6);bonus.window.close();
 assert.deepEqual(errors,[]);
})().catch(e=>{console.error(e);process.exit(1);});
