/* Media-specific deterministic regression checks. No network or browser required. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=__dirname+'/../static';
let ended=0,playing=0,created=[];
class FakeElement {
  constructor(type){this.type=type;this.attributes={};this.handlers={};this.style={};this.paused=true;this.isConnected=true;}
  setAttribute(k,v){this.attributes[k]=v;}
  addEventListener(k,v){this.handlers[k]=v;}
  dispatch(k){this.handlers[k]?.({type:k});}
  play(){this.paused=false;this.dispatch('play');return Promise.resolve();}
}
const window={
  YT:{PlayerState:{PLAYING:1,ENDED:0},Player: class{
    constructor(iframe,settings){this.iframe=iframe;this.settings=settings;created.push(this);}
    playVideo(){playing++;}
    end(){this.settings.events.onStateChange({data:0});}
    ready(){this.settings.events.onReady({target:this});}
  }}
};
const document={createElement:type=>new FakeElement(type)};
vm.runInNewContext(fs.readFileSync(root+'/media.js','utf8'),{window,document,URL,URLSearchParams,location:{origin:'https://example.net'},console});
const q={kind:'video',media_url:'https://www.youtube.com/watch?v=6wjoRWgu2Z4',media_start:3,media_end:9};
const el=window.IcebreakerMedia.create(q,'round-video',e=>{throw Error(e)},{hideControls:true,autoPlay:true,onEnded:()=>ended++});
assert.equal(el.type,'iframe');
assert(el.src.startsWith('https://www.youtube-nocookie.com/embed/6wjoRWgu2Z4?'));
const u=new URL(el.src),params=u.searchParams;
for (const [key,value] of Object.entries({controls:'0',autoplay:'1',enablejsapi:'1',start:'3',end:'9',playsinline:'1',fs:'0',iv_load_policy:'3'}))
  assert.equal(params.get(key),value,key);
assert.equal(params.get('origin'),'https://example.net');
assert.equal(created.length,0);
Promise.resolve().then(()=>{
  assert.equal(created.length,1);
  created[0].ready();assert.equal(playing,1);
  created[0].end();created[0].end();assert.equal(ended,1);
  const preview=window.IcebreakerMedia.create(q,'round-video',e=>{throw Error(e)});
  assert.equal(new URL(preview.src).searchParams.get('controls'),'1');
  assert.equal(new URL(preview.src).searchParams.get('autoplay'),'0');
  const local=window.IcebreakerMedia.create({kind:'video',media:'/static/videos/test.mp4'},'round-video',()=>{}, {hideControls:true,autoPlay:true,onEnded:()=>ended++});
  assert.equal(local.controls,false);assert.equal(typeof local._icebreakerPlay,'function');
  local._icebreakerPlay();local.dispatch('ended');assert.equal(ended,2);
  console.log('PASS YouTube minimal controls + autoplay + one-time completion; HTML5 video clean-controls + manual fallback');
}).catch(e=>{console.error(e);process.exit(1)});
