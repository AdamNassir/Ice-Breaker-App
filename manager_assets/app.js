(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  let rounds = [], selected = -1, revision = '', token = '', source = '';
  let dirty = false, busy = false, mediaBusy = false, loaded = false;
  let media = {image: [], audio: []};
  const textFields = {title:'title', context:'context', alt:'alt', explanation:'explanation',
    source:'source', source_url:'source-url', technical_note:'technical-note',
    discussion:'discussion', technical_source_url:'technical-url'};
  const toolbar = ['add-question','empty-add','empty-deck','starter-deck','import-deck','export-deck'];

  function node(tag, className, text) {
    const value = document.createElement(tag);
    if (className) value.className = className;
    if (text !== undefined) value.textContent = text;
    return value;
  }
  function tell(message, error = false) {
    $('status').textContent = message; $('status').classList.toggle('error', error); $('status').hidden = false;
  }
  function updateControls() {
    $('save-state').textContent = busy ? 'Working…' : !loaded ? 'Deck not loaded' : dirty ? 'Unsaved changes' : 'Saved deck loaded';
    $('save-state').classList.toggle('dirty', dirty);
    $('save-deck').disabled = busy || mediaBusy || !loaded || !rounds.length;
    $('question-count').textContent = rounds.length;
    $('deck-info').textContent = loaded ? `${rounds.length} question${rounds.length === 1 ? '' : 's'} · ${source}` : '';
    toolbar.forEach(id => $(id).disabled = busy || !loaded);
    $('reload-deck').disabled = busy;
    $('move-up').disabled = busy || selected <= 0;
    $('move-down').disabled = busy || selected < 0 || selected >= rounds.length - 1;
    $('duplicate-question').disabled = busy || selected < 0;
    $('delete-question').disabled = busy || selected < 0;
    $('question-form').querySelectorAll('input,select,textarea,button').forEach(el => el.disabled = busy);
    $('media-file').disabled = busy || mediaBusy;
    document.querySelectorAll('.question-item').forEach(el => el.disabled = busy);
  }
  function markDirty() { dirty = true; updateControls(); }
  function readEditor() {
    if (selected < 0 || !rounds[selected]) return;
    const q = rounds[selected];
    Object.entries(textFields).forEach(([key,id]) => q[key] = $(id).value);
    q.kind = $('kind').value; q.answer = $('answer').value;
    q.body = q.kind === 'audio' ? $('audio-body').value : q.kind === 'image' ? '' : $('body').value;
    if ($('seconds').value !== '') q.seconds = Number($('seconds').value); else delete q.seconds;
    if ($('difficulty').value !== '') q.difficulty = Number($('difficulty').value); else delete q.difficulty;
    q.media = ['image','audio'].includes(q.kind) ? $('media-path').value : '';
    q.image_fit = $('image-fit').value; q.image_position = $('image-position').value || 'center';
  }
  function chooseMedia() {
    const q = rounds[selected], picker = $('media-choice'); picker.replaceChildren(new Option('Choose a file', ''));
    if (!q || !['image','audio'].includes(q.kind)) return;
    const choices = media[q.kind] || [];
    if (q.media && !choices.some(row => row.path === q.media)) picker.append(new Option(q.media.split('/').pop(), q.media));
    choices.forEach(row => picker.append(new Option(row.name, row.path)));
    picker.value = q.media || '';
  }
  function showFields() {
    if (selected < 0) return;
    const kind = $('kind').value, hasMedia = ['image','audio'].includes(kind);
    $('text-fields').hidden = hasMedia; $('media-fields').hidden = !hasMedia;
    $('image-options').hidden = kind !== 'image'; $('audio-description').hidden = kind !== 'audio';
    $('body').classList.toggle('code-editor', kind === 'code' || kind === 'commit');
    $('media-file').accept = kind === 'image' ? 'image/*,.avif,.bmp' : 'audio/*,.m4a,.opus,.webm';
    $('format-help').textContent = kind === 'image' ? 'JPG, PNG, WebP, GIF, AVIF or BMP · up to 25 MB. Convert HEIC or SVG to PNG/JPG first.' : 'MP3, WAV, OGG/Opus, FLAC, M4A, AAC or WebM · up to 25 MB. Playback depends on the browser; MP3/WAV are convenient choices.';
  }
  function renderList() {
    const list = $('question-list'); list.replaceChildren();
    if (!rounds.length) list.append(node('p','small','Your deck is empty. Add a question to begin.'));
    rounds.forEach((q,index) => {
      const button = node('button','question-item'); button.type = 'button'; button.setAttribute('aria-pressed', index === selected ? 'true' : 'false');
      const copy = node('span','question-copy');
      copy.append(node('strong','', q.title || 'Untitled question'), node('small','', `${q.kind || 'Choose format'} · ${q.answer || 'Choose origin'} · ${q.seconds ? q.seconds + 's' : 'Room timer'}`));
      button.append(node('span','question-number',String(index+1).padStart(2,'0')),copy);
      button.addEventListener('click', () => { readEditor(); selected = index; renderList(); loadEditor(); });
      list.append(button);
    });
    updateControls();
  }
  function loadEditor() {
    const q = rounds[selected];
    $('question-form').hidden = !q; $('empty-editor').hidden = Boolean(q); $('preview-card').hidden = !q;
    if (!q) { updateControls(); return; }
    $('editor-heading').textContent = `Question ${selected+1}`;
    Object.entries(textFields).forEach(([key,id]) => $(id).value = q[key] || '');
    $('kind').value = q.kind || 'text'; $('answer').value = q.answer || '';
    $('seconds').value = q.seconds ?? ''; $('difficulty').value = q.difficulty ?? '';
    $('body').value = q.body || ''; $('audio-body').value = q.body || '';
    $('media-path').value = q.media || ''; $('image-fit').value = q.image_fit || 'contain';
    $('image-position').value = q.image_position || 'center';
    $('media-file').value = ''; showFields(); chooseMedia(); renderPreview(); updateControls();
  }
  function renderPreview() {
    const q = rounds[selected]; if (!q) return;
    const box = $('preview'); box.replaceChildren();
    box.append(node('span','preview-type', `${q.kind}${q.difficulty ? ' · Level '+q.difficulty+'/5' : ''}`), node('h3','', q.title || 'Untitled question'));
    if (q.context) box.append(node('p','preview-context',q.context));
    if (q.kind === 'image' && q.media) {
      const img = node('img'); img.src = q.media; img.alt = q.alt || 'Question image'; img.style.objectFit = q.image_fit || 'contain'; img.style.objectPosition = q.image_position || 'center';
      img.addEventListener('error',()=>{if(box.contains(img))box.append(node('p','field-help','This image cannot be previewed. Check the file or upload a PNG/JPG copy.'));});
      box.append(img);
    } else if (q.kind === 'audio' && q.media) {
      if (q.body) box.append(node('p','preview-context',q.body));
      const audio = node('audio'); audio.src = q.media; audio.controls = true; audio.preload = 'metadata'; audio.setAttribute('aria-label',q.alt || 'Question recording');
      audio.addEventListener('error',()=>{if(box.contains(audio))box.append(node('p','field-help','This recording cannot be previewed in this browser. Try an MP3 or WAV copy.'));}); box.append(audio);
    } else if (q.kind === 'image' || q.kind === 'audio') box.append(node('p','preview-context','Upload a file or choose an existing one.'));
    else box.append(node(q.kind === 'text' ? 'p' : 'pre',q.kind === 'text' ? 'preview-text' : '',q.body || 'Your question content appears here.'));
    const reveal = $('preview-reveal'); reveal.replaceChildren(); reveal.hidden = !$('preview-answer').checked;
    reveal.append(node('h3','',`Answer: ${q.answer || 'choose AI or HUMAN'}`));
    for (const [key,label] of [['explanation','Explanation'],['technical_note','Technical detail'],['discussion','Discuss'],['source','Origin']]) {
      if (q[key]) reveal.append(node('strong','',label),node('p','',q[key]));
    }
    for (const [key,label] of [['source_url','View source'],['technical_source_url','Technical reference']]) {
      if (q[key] && /^https:\/\//.test(q[key])) {const p=node('p'),a=node('a','',label);a.href=q[key];a.target='_blank';a.rel='noopener noreferrer';p.append(a);reveal.append(p);}
    }
  }
  async function api(path, method = 'GET', body, raw = false) {
    const headers = {};
    if (method !== 'GET') headers['X-Manager-Token'] = token;
    if (body !== undefined) headers['Content-Type'] = raw ? 'application/octet-stream' : 'application/json';
    const controller = new AbortController(), timeout = setTimeout(()=>controller.abort(),30000);
    try {
      const response = await fetch(path,{method,headers,body:body===undefined?undefined:raw?body:JSON.stringify(body),signal:controller.signal,cache:'no-store'});
      const data = await response.json().catch(()=>({}));
      if (!response.ok) {
        const error = new Error(typeof data.detail === 'string' ? data.detail : 'Check the question fields and try again.');error.status=response.status;throw error;
      }
      return data;
    } catch(error) {
      if (error.name === 'AbortError') throw new Error('The local manager timed out. Keep it running and try again.');
      throw error;
    } finally {clearTimeout(timeout);}
  }
  async function loadDeck() {
    if (dirty && !confirm('Discard your unsaved draft and reload the saved deck?')) return;
    busy = true; updateControls();
    try {
      const [data,files] = await Promise.all([api('/api/deck'),api('/api/media')]);
      rounds=data.rounds;revision=data.revision;token=data.manager_token;source=data.source;media=files;
      selected=rounds.length?0:-1;dirty=false;loaded=true;renderList();loadEditor();
      if(data.warning)tell(`The saved question file needs repair: ${data.warning} Import a backup or build a new deck, then save.`,true);
      else $('status').hidden=true;
    } catch(error) {tell(`Cannot load the manager: ${error.message} Keep the terminal running, then choose Reload saved.`,true);}
    finally {busy=false;updateControls();}
  }
  function addQuestion() {
    readEditor();rounds.push({title:'',kind:'text',answer:'',body:'',image_fit:'contain',image_position:'center'});
    selected=rounds.length-1;markDirty();renderList();loadEditor();$('title').focus();
  }
  $('add-question').addEventListener('click',addQuestion);$('empty-add').addEventListener('click',addQuestion);
  $('question-form').addEventListener('submit',event=>event.preventDefault());
  $('question-form').addEventListener('input',event=>{
    if(['media-file','media-choice'].includes(event.target.id))return;
    readEditor();markDirty();renderList();renderPreview();
  });
  $('kind').addEventListener('change',()=>{
    readEditor();const q=rounds[selected];
    if(q.media && !q.media.startsWith(q.kind==='image'?'/static/images/':'/static/audio/'))q.media='';
    $('media-path').value=q.media||'';showFields();chooseMedia();markDirty();renderList();renderPreview();
  });
  $('media-choice').addEventListener('change',()=>{
    $('media-path').value=$('media-choice').value;readEditor();markDirty();renderPreview();
  });
  $('media-file').addEventListener('change',async()=>{
    const file=$('media-file').files[0],q=rounds[selected];if(!file||!q)return;
    const kind=q.kind, extension='.'+file.name.split('.').pop().toLowerCase();
    if(file.size>25*1024*1024){tell('This file exceeds 25 MB. Choose a smaller copy.',true);$('media-file').value='';return;}
    mediaBusy=true;updateControls();tell('Copying the selected file into the app…');
    try {
      const result=await api(`/api/media?kind=${encodeURIComponent(kind)}&extension=${encodeURIComponent(extension)}`,'POST',file,true);
      media[kind].push({path:result.media,name:result.media.split('/').pop()});
      if(rounds.includes(q)&&q.kind===kind){q.media=result.media;markDirty();if(rounds[selected]===q){$('media-path').value=q.media;chooseMedia();renderPreview();}tell('File added to the question. Save the deck to use it in the game.');}
      else tell('File copied. It is available under existing files.');
    } catch(error){tell(error.message,true);}finally{mediaBusy=false;$('media-file').value='';updateControls();}
  });
  $('save-deck').addEventListener('click',async()=>{
    if(busy||mediaBusy)return;readEditor();busy=true;updateControls();
    try {
      const data=await api('/api/deck','PUT',{revision,rounds});
      rounds=data.rounds;revision=data.revision;source=data.source;dirty=false;
      selected=Math.min(selected,rounds.length-1);renderList();loadEditor();tell(data.message);
    }catch(error){tell(error.message,true);const match=/^Question (\d+)/.exec(error.message);if(match&&rounds[Number(match[1])-1]){selected=Number(match[1])-1;renderList();loadEditor();}}
    finally{busy=false;updateControls();}
  });
  function move(direction) {readEditor();const next=selected+direction;if(next<0||next>=rounds.length)return;[rounds[selected],rounds[next]]=[rounds[next],rounds[selected]];selected=next;markDirty();renderList();loadEditor();}
  $('move-up').addEventListener('click',()=>move(-1));$('move-down').addEventListener('click',()=>move(1));
  $('duplicate-question').addEventListener('click',()=>{readEditor();rounds.splice(selected+1,0,{...rounds[selected]});selected++;markDirty();renderList();loadEditor();});
  $('delete-question').addEventListener('click',()=>{if(selected<0||!confirm('Remove this question from the draft? Its media file will be kept.'))return;rounds.splice(selected,1);selected=Math.min(selected,rounds.length-1);markDirty();renderList();loadEditor();});
  function replaceDraft(values) {rounds=values;selected=rounds.length?0:-1;markDirty();renderList();loadEditor();}
  $('empty-deck').addEventListener('click',()=>{if(confirm('Replace the current draft with an empty deck? The saved deck stays intact until you save.'))replaceDraft([]);});
  $('starter-deck').addEventListener('click',async()=>{if(!confirm('Replace the draft with the bundled starter deck? You can edit it before saving.'))return;busy=true;updateControls();try{replaceDraft((await api('/api/starter')).rounds);}catch(error){tell(error.message,true);}finally{busy=false;updateControls();}});
  $('reload-deck').addEventListener('click',loadDeck);
  $('preview-answer').addEventListener('change',renderPreview);
  $('import-text').addEventListener('click',()=>$('text-file').click());
  $('text-file').addEventListener('change',async()=>{
    const file=$('text-file').files[0],q=rounds[selected];if(!file||!q)return;
    try {
      if(file.size>200000)throw new Error('Choose a smaller text file (up to 50,000 characters).');
      const text=new TextDecoder('utf-8',{fatal:true}).decode(await file.arrayBuffer());
      if(text.includes('\u0000')||text.length>50000)throw new Error('Use plain UTF-8 text of up to 50,000 characters.');
      if(rounds.includes(q)&&['text','code','commit'].includes(q.kind)){q.body=text;if(rounds[selected]===q){$('body').value=text;renderPreview();}markDirty();tell('Text imported into the draft. Save the deck when ready.');}
    }catch(error){tell(error.message,true);}finally{$('text-file').value='';}
  });
  $('import-deck').addEventListener('click',()=>$('deck-file').click());
  $('deck-file').addEventListener('change',async()=>{
    const file=$('deck-file').files[0];if(!file)return;
    try {
      if(file.size>2*1024*1024)throw new Error('The deck file exceeds 2 MB.');
      const value=JSON.parse(await file.text()),values=Array.isArray(value)?value:value.rounds;
      if(!Array.isArray(values)||values.some(q=>!q||typeof q!=='object'||Array.isArray(q)))throw new Error('Choose a deck JSON file containing a rounds list.');
      if(values.length>200)throw new Error('A deck can contain up to 200 questions.');
      if(!dirty||confirm('Replace your unsaved draft with the imported deck?')){replaceDraft(values);tell('Draft imported. Media files must also be present in this app folder. Save the deck when ready.');}
    }catch(error){tell(`Cannot import: ${error.message}`,true);}finally{$('deck-file').value='';}
  });
  $('export-deck').addEventListener('click',()=>{
    readEditor();const url=URL.createObjectURL(new Blob([JSON.stringify({schema_version:1,rounds},null,2)+'\n'],{type:'application/json'}));
    const link=node('a');link.href=url;link.download='questions-draft.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  window.addEventListener('beforeunload',event=>{if(dirty){event.preventDefault();event.returnValue='';}});
  loadDeck();
})();
