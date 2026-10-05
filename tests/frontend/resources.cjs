/* Load the shipped HTML, scripts and CSS over HTTP; do not manually inject them. */
const {JSDOM,VirtualConsole}=require('jsdom');
const fs=require('node:fs'),assert=require('node:assert/strict');
const fixture=JSON.parse(fs.readFileSync(process.env.QA_FIXTURE));
const base=process.env.QA_MANAGER_BASE;
async function until(fn){for(let i=0;i<200;i++){if(fn())return;await new Promise(r=>setTimeout(r,20));}throw Error('HTTP-loaded page did not render');}
(async()=>{
 for(const surface of ['player','host','manager']){
  const errors=[],vc=new VirtualConsole();vc.on('jsdomError',e=>errors.push(e.message));
  const role=surface==='host'?'host':'player',state=fixture.rows.find(r=>r.phase==='live'&&r[role].question.text_style==='news')[role];
  const url=surface==='manager'?base+'/':base+'/static/'+(surface==='host'?'presenter.html':'index.html')+'?room='+state.code;
  const page=await JSDOM.fromURL(url,{runScripts:'dangerously',resources:'usable',pretendToBeVisual:true,virtualConsole:vc,beforeParse(w){
   w.AbortController=global.AbortController;
   w.HTMLCanvasElement.prototype.getContext=()=>({fillRect(){},fillStyle:''});
   if(surface==='manager')w.fetch=(path,options)=>fetch(new URL(path,base),options);
   else {
    (role==='host'?w.sessionStorage:w.localStorage).setItem('icebreaker:'+role+':'+state.code,JSON.stringify(role==='host'?fixture.room:fixture.player));
    w.fetch=async path=>({ok:true,json:async()=>path.endsWith('/qr')?fixture.qr:{...state,server_time:Date.now()/1000,deadline:Date.now()/1000+10}});
   }
  }});
  try{
   const w=page.window,d=w.document;
   if(surface==='manager'){
    await until(()=>d.readyState==='complete'&&d.querySelectorAll('.question-item').length>=5&&!d.getElementById('add-image').disabled);
    d.querySelectorAll('.question-item')[4].click();
   }
   await until(()=>d.querySelector('.news-site')&&d.readyState==='complete');
   const site=d.querySelector('.news-site');
   assert.equal(site.lang,'fr');assert(d.querySelector('.news-navigation'));assert(d.querySelector('.news-sidebar'));assert(d.querySelector('.news-footer'));
   assert.equal(w.getComputedStyle(site).overflowY,'auto');assert.equal(w.getComputedStyle(d.querySelector('.news-page-grid')).display,'grid');
   assert.equal(w.getComputedStyle(d.querySelector('.news-masthead')).display,'grid');
   for(const logo of d.querySelectorAll('.logo-logiclever'))assert.equal(w.getComputedStyle(logo).mixBlendMode,'multiply');
   assert(d.querySelector('link[href*="/static/newsarticle.css"]'));
   assert.equal(d.querySelector('.news-publication-logo').alt,'Le Parisien');
   assert.equal(d.querySelectorAll('img.news-thumb').length,6);
   for(const image of d.querySelectorAll('img.news-thumb')) {
    assert.equal(w.getComputedStyle(image).objectFit,'cover');assert.equal(w.getComputedStyle(image).minHeight,'0');
    assert(image.alt.length>0);
    const response=await fetch(new URL(image.getAttribute('src'),base));
    assert.equal(response.status,200);assert(response.headers.get('content-type').startsWith('image/jpeg'));
    const bytes=new Uint8Array(await response.arrayBuffer());assert.equal(bytes[0],255);assert.equal(bytes[1],216);assert(bytes.length>10000);
   }
   assert.equal(d.querySelector('.news-author').textContent,'Sébastien Lernould');
   const sports=w.IcebreakerNews.create({body:'Ballon d’or : une page publiée par erreur\n\nTexte.'});
   assert.equal(sports.querySelector('.news-author').textContent,'Dominique Sévérac');
   assert(!sports.textContent.includes('La rédaction'));
   assert.equal(typeof w.IcebreakerNews.create,'function');assert.deepEqual(errors,[]);
   console.log('PASS HTTP-loaded '+surface+': shipped HTML loads its scripts/CSS; full French article grid, masthead, navigation, sidebar/footer and logo blending.');
  }finally{page.window.close();}
 }
})().catch(error=>{console.error(error);process.exit(1)});
