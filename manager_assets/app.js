(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const isGlobal = document.body.dataset.deckMode === 'global';
  const newsNames = ['publication','logo_url','edition','navigation','section','breadcrumb','headline','chapo','author','published','topic','sidebar_title','sidebar_caption','advertisement','hero_image','hero_alt'];
  const defaultRelated = [
    {section:'VIE ÉTUDIANTE',title:'Aides au logement : ce qui change en octobre',image:'housing',alt:'Étudiants près du campus'},
    {section:'SPORTS',title:'France-Belgique : les Bleus préparent leur prochain match',image:'football',alt:'Football'},
    {section:'HIGH-TECH',title:'OpenAI se sépare de trois chercheurs en sécurité',image:'ai',alt:'Logo'}
  ];
  function newsFromEditor() {
    const value={};for(const name of newsNames)value[name]=$('news-'+name).value.trim();
    value.related=[...document.querySelectorAll('[data-news-card="0"][data-card-field="title"], [data-news-card="1"][data-card-field="title"], [data-news-card="2"][data-card-field="title"]')].map((_,i)=>{
      const row={};for(const name of ['section','title','image','alt'])row[name]=document.querySelector(`[data-news-card="${i}"][data-card-field="${name}"]`).value.trim();return row;
    }).filter(row=>row.title);
    return value;
  }
  function fillNews(value={}) {
    for(const name of newsNames)$('news-'+name).value=value[name]||'';
    for(let i=0;i<3;i++)for(const name of ['section','title','image','alt']) {
      document.querySelector(`[data-news-card="${i}"][data-card-field="${name}"]`).value=value.related?.[i]?.[name]||'';
    }
  }

  let rounds = [], selected = -1, revision = '', token = '', source = '';
  let dirty = false, busy = false, mediaBusy = false, loaded = false;
  let media = {image: [], audio: [], video: []};
  const mediaFolders = {image:'images', audio:'audio', video:'videos'};
  const formats = {
    image:{accept:'.jpg,.jpeg,.png,.webp,.gif,.avif,.bmp', extensions:['jpg','jpeg','png','webp','gif','avif','bmp'], help:'JPG, PNG, WebP, GIF, AVIF or BMP · up to 25 MB. Convert HEIC or SVG to PNG/JPG first.'},
    audio:{accept:'.mp3,.wav,.ogg,.opus,.flac,.m4a,.aac,.webm', extensions:['mp3','wav','ogg','opus','flac','m4a','aac','webm'], help:'MP3, WAV, OGG/Opus, FLAC, M4A, AAC or WebM · up to 25 MB. Playback depends on the browser; MP3/WAV are convenient choices.'},
    video:{accept:'.mp4,.webm,.ogv,.mov,.m4v', extensions:['mp4','webm','ogv','mov','m4v'], help:'MP4, WebM, OGV, MOV or M4V · up to 25 MB. For presenter playback, use MP4 with H.264 video and AAC audio. Video never appears on participant phones. Convert AVI/MKV or incompatible MOV files first.'}
  };
  const textFields = {title:'title', context:'context', alt:'alt', explanation:'explanation',
    explanation_image:'explanation-image', explanation_image_alt:'explanation-image-alt',
    source:'source', source_url:'source-url', image_reveal:'image-reveal', technical_note:'technical-note',
    discussion:'discussion', technical_source_url:'technical-url', reveal_media:'reveal-media', reveal_alt:'reveal-alt'};
  const toolbar = ['add-question','add-image','add-audio','add-video','empty-add','empty-deck','starter-deck','import-deck','import-bundle','export-deck'];

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
    $('explanation-image-file').disabled = busy || mediaBusy;
    $('explanation-image-choice').disabled = busy || mediaBusy;
    $('explanation-image-clear').disabled = busy || mediaBusy;
    document.querySelectorAll('.question-item').forEach(el => el.disabled = busy);
  }
  function markDirty() { dirty = true; updateControls(); }
  function readEditor() {
    if (selected < 0 || !rounds[selected]) return;
    const q = rounds[selected];
    Object.entries(textFields).forEach(([key,id]) => q[key] = $(id).value);
    q.kind = $('kind').value; q.answer = $('answer').value;
    q.text_style = q.kind === 'text' ? $('text-style').value : 'plain';
    q.news = q.text_style === 'news' ? newsFromEditor() : (q.news || null);
    q.body = ['audio','video'].includes(q.kind) ? $('audio-body').value : q.kind === 'image' ? '' : $('body').value;
    q.timer_mode = $('timer-mode').value;
    if (q.timer_mode === 'local') q.seconds = $('seconds').value === '' ? null : Number($('seconds').value); else delete q.seconds;
    if ($('difficulty').value !== '') q.difficulty = Number($('difficulty').value); else delete q.difficulty;
    q.media = formats[q.kind] ? $('media-path').value : '';
    const linked = ['audio','video'].includes(q.kind) && $('media-mode').value === 'link';
    q.media_url = linked ? $('media-url').value.trim() : '';
    if (linked) q.media = '';
    for(const [key,id] of [['media_start','media-start'],['media_end','media-end']]) {
      if (['audio','video'].includes(q.kind) && $(id).value !== '') q[key] = Number($(id).value); else delete q[key];
    }
    q.image_fit = $('image-fit').value; q.image_position = $('image-position').value || 'center';
    if (q.kind !== 'image') { q.reveal_media = ''; q.reveal_alt = ''; }
  }
  function chooseMedia() {
    const q = rounds[selected], picker = $('media-choice'); picker.replaceChildren(new Option('Choose a file', ''));
    if (!q || !formats[q.kind]) return;
    const choices = media[q.kind] || [];
    if (q.media && !choices.some(row => row.path === q.media)) picker.append(new Option(q.media.split('/').pop(), q.media));
    choices.forEach(row => picker.append(new Option(row.name, row.path)));
    picker.value = q.media || '';
  }
  function chooseExplanationImage() {
    const q=rounds[selected], picker=$('explanation-image-choice');
    picker.replaceChildren(new Option('Choose a saved image (optional)', ''));
    if (!q) return;
    const choices=media.image || [];
    if (q.explanation_image && !choices.some(item=>item.path===q.explanation_image)) {
      picker.append(new Option(q.explanation_image.split('/').pop(),q.explanation_image));
    }
    choices.forEach(item=>picker.append(new Option(item.name,item.path)));
    picker.value=q.explanation_image || '';
  }
  function showFields() {
    if (selected < 0) return;
    const kind = $('kind').value, hasMedia = Boolean(formats[kind]);
    $('local-timer-fields').hidden = $('timer-mode').value !== 'local';
    $('seconds').required = $('timer-mode').value === 'local';
    $('text-fields').hidden = hasMedia; $('media-fields').hidden = !hasMedia;
    $('text-style-field').hidden = kind !== 'text';
    $('news-editor').hidden = kind !== 'text' || $('text-style').value !== 'news';
    $('image-options').hidden = kind !== 'image'; $('audio-description').hidden = !['audio','video'].includes(kind);
    const canLink = ['audio','video'].includes(kind), linked = canLink && $('media-mode').value === 'link';
    $('media-source-fields').hidden = !canLink; $('clip-fields').hidden = !canLink;
    $('local-media-fields').hidden = linked; $('media-link-fields').hidden = !linked;
    $('body').classList.toggle('code-editor', kind === 'code' || kind === 'commit');
    $('media-file').accept = formats[kind]?.accept || '';
    $('format-help').textContent = formats[kind]?.help || '';
  }
  function renderList() {
    const list = $('question-list'); list.replaceChildren();
    if (!rounds.length) list.append(node('p','small','Your deck is empty. Add a question to begin.'));
    rounds.forEach((q,index) => {
      const button = node('button','question-item'); button.type = 'button'; button.setAttribute('aria-pressed', index === selected ? 'true' : 'false');
      const copy = node('span','question-copy');
      copy.append(node('strong','', q.title || 'Untitled question'), node('small','', `${q.kind || 'Choose format'} · ${q.answer || 'Choose origin'} · ${q.timer_mode==='local' ? q.seconds + 's custom' : 'Presenter timer'}`));
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
    $('timer-mode').value = q.timer_mode === 'local' ? 'local' : 'global';
    $('seconds').value = q.seconds ?? ''; $('difficulty').value = q.difficulty ?? '';
    $('body').value = q.body || ''; $('audio-body').value = q.body || '';
    $('text-style').value = q.text_style || 'plain';
    fillNews(q.news||{});
    $('media-path').value = q.media || ''; $('image-fit').value = q.image_fit || 'contain';
    $('media-url').value = q.media_url || ''; $('media-mode').value = q.media_url ? 'link' : 'local';
    $('media-start').value = q.media_start ?? ''; $('media-end').value = q.media_end ?? '';
    $('image-position').value = q.image_position || 'center';
    $('media-file').value = ''; $('explanation-image-file').value = ''; showFields(); chooseMedia(); chooseExplanationImage(); renderPreview(); updateControls();
  }
  function renderPreview() {
    const q = rounds[selected]; if (!q) return;
    const box = $('preview'); box.replaceChildren();
    box.append(node('span','preview-type', `${q.kind}${q.difficulty ? ' · Level '+q.difficulty+'/5' : ''}`), node('h3','', q.title || 'Untitled question'));
    if (q.context) box.append(node('p','preview-context',q.context));
    if (q.kind === 'image' && q.media) {
      const revealed = $('preview-answer').checked && q.reveal_media;
      const img = node('img'); img.src = revealed ? q.reveal_media : q.media; img.alt = revealed ? q.reveal_alt || q.alt || 'Revealed image' : q.alt || 'Question image'; img.style.objectFit = q.image_fit || 'contain'; img.style.objectPosition = q.image_position || 'center';
      img.addEventListener('error',()=>{if(box.contains(img))box.append(node('p','field-help','This image cannot be previewed. Check the file or upload a PNG/JPG copy.'));});
      box.append(img);
    } else if (['audio','video'].includes(q.kind) && (q.media || q.media_url)) {
      if (q.body) box.append(node('p','preview-context',q.body));
      const player = window.IcebreakerMedia.create(q, q.kind === 'video' ? 'round-video' : 'round-audio', message => {
        if(box.contains(player) && !box.querySelector('.media-error'))box.append(node('p','field-help media-error',message));
      }); box.append(player);
    } else if (formats[q.kind]) box.append(node('p','preview-context','Upload a file or choose an existing one.'));
    else if (q.kind === 'text' && q.text_style === 'news') box.append(window.IcebreakerNews.create(q));
    else box.append(node(q.kind === 'text' ? 'p' : 'pre',q.kind === 'text' ? 'preview-text' : '',q.body || 'Your question content appears here.'));
    const reveal = $('preview-reveal'); reveal.replaceChildren(); reveal.hidden = !$('preview-answer').checked;
    reveal.append(node('h3','',`Answer: ${q.answer || 'choose AI or HUMAN'}`));
    for (const [key,label] of [['image_reveal','Photo reveal'],['explanation','Explanation'],['technical_note','Technical detail'],['discussion','Discuss'],['source','Origin']]) {
      if (q[key]) reveal.append(node('strong','',label),node('p','',q[key]));
    }
    if (q.explanation_image) {
      const img=node('img','explanation-preview-image');
      img.src=q.explanation_image;
      img.alt=q.explanation_image_alt || 'Explanation illustration';
      img.style.objectFit='contain';
      reveal.append(img);
    }
    for (const [key,label] of [['source_url','View source'],['technical_source_url','Technical reference']]) {
      if (q[key] && /^https:\/\//.test(q[key])) {const p=node('p'),a=node('a','',label);a.href=q[key];a.target='_blank';a.rel='noopener noreferrer';p.append(a);reveal.append(p);}
    }
  }
  async function api(path, method = 'GET', body, raw = false) {
    const headers = {};
    if (!isGlobal && method !== 'GET') headers['X-Manager-Token'] = token;
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
      if (error.name === 'AbortError') throw new Error('The question manager timed out. Try again.');
      throw error;
    } finally {clearTimeout(timeout);}
  }
  async function loadDeck() {
    if (dirty && !confirm('Discard your unsaved draft and reload the saved deck?')) return;
    busy = true; updateControls();
    try {
      const [data,files] = await Promise.all([api('/api/deck'),api('/api/media')]);
      rounds=data.rounds;revision=data.revision;if(!isGlobal)token=data.manager_token;source=data.source;media=files;
      selected=rounds.length?0:-1;dirty=false;loaded=true;renderList();loadEditor();
      if(data.warning)tell(`Deck needs repair: ${data.warning} Edit the affected question, or import a backup, then save.`,true);
      else $('status').hidden=true;
    } catch(error) {tell(`Cannot load the manager: ${error.message} Keep the terminal running, then choose Reload saved.`,true);}
    finally {busy=false;updateControls();}
  }
  function addQuestion(kind = 'text') {
    readEditor();rounds.push({title:'',kind,answer:'',body:'',image_fit:'contain',image_position:'center'});
    selected=rounds.length-1;markDirty();renderList();loadEditor();$('title').focus();
  }
  $('add-question').addEventListener('click',()=>addQuestion());$('empty-add').addEventListener('click',()=>addQuestion());
  for(const kind of Object.keys(formats))$('add-'+kind).addEventListener('click',()=>addQuestion(kind));
  $('question-form').addEventListener('submit',event=>event.preventDefault());
  $('question-form').addEventListener('input',event=>{
    if(['media-file','media-choice','explanation-image-file','explanation-image-choice'].includes(event.target.id))return;
    readEditor();markDirty();renderList();renderPreview();
  });
  $('kind').addEventListener('change',()=>{
    readEditor();const q=rounds[selected];
    if(q.media && !q.media.startsWith(`/static/${mediaFolders[q.kind]}/`) && !/^https:\/\/[a-z0-9-]+\.public\.blob\.vercel-storage\.com\/icebreaker\//.test(q.media))q.media='';
    $('media-path').value=q.media||'';showFields();chooseMedia();markDirty();renderList();renderPreview();
  });
  $('timer-mode').addEventListener('change',()=>{
    if($('timer-mode').value === 'local' && !$('seconds').value) $('seconds').value = '30';
    readEditor(); showFields(); markDirty(); renderList();
  });
  $('explanation-image-choice').addEventListener('change',()=>{
    $('explanation-image').value=$('explanation-image-choice').value;
    readEditor();markDirty();renderPreview();
  });
  $('explanation-image-clear').addEventListener('click',()=>{
    $('explanation-image').value='';$('explanation-image-alt').value='';
    readEditor();chooseExplanationImage();markDirty();renderPreview();
  });
  $('explanation-image-file').addEventListener('change',async()=>{
    const file=$('explanation-image-file').files[0],q=rounds[selected];
    if(!file||!q)return;
    const suffix=file.name.split('.').pop().toLowerCase(),extension='.'+suffix;
    if(!formats.image.extensions.includes(suffix)){
      tell('Choose a JPG, PNG, WebP, GIF, AVIF or BMP explanation image.',true);
      $('explanation-image-file').value='';return;
    }
    const limit=(isGlobal?4:25)*1024*1024;
    if(file.size>limit){tell('Explanation image exceeds '+(isGlobal?4:25)+' MB.',true);$('explanation-image-file').value='';return;}
    mediaBusy=true;updateControls();tell('Uploading explanation image…');
    try {
      const result=await api('/api/media?kind=image&extension='+encodeURIComponent(extension),'POST',file,true);
      if (!media.image.some(item=>item.path===result.media)) media.image.push({path:result.media,name:result.media.split('/').pop()});
      if(rounds.includes(q)){
        q.explanation_image=result.media;
        if(rounds[selected]===q){$('explanation-image').value=result.media;chooseExplanationImage();renderPreview();}
        markDirty();tell('Explanation image uploaded. Save the deck to use it after reveal.');
      }
    }catch(error){tell(error.message,true)}
    finally{mediaBusy=false;$('explanation-image-file').value='';updateControls()}
  });
  $('text-style').addEventListener('change',()=>{readEditor();showFields();markDirty();renderPreview();});
  $('media-mode').addEventListener('change',()=>{readEditor();showFields();markDirty();renderPreview();});
  $('media-choice').addEventListener('change',()=>{
    $('media-path').value=$('media-choice').value;readEditor();markDirty();renderPreview();
  });
  $('media-file').addEventListener('change',async()=>{
    const file=$('media-file').files[0],q=rounds[selected];if(!file||!q)return;
    const kind=q.kind, suffix=file.name.split('.').pop().toLowerCase(), extension='.'+suffix;
    if(!formats[kind]||!formats[kind].extensions.includes(suffix)){tell(`Choose a supported ${kind} file. ${formats[kind]?.help || 'Select Image, Audio or Video first.'}`,true);$('media-file').value='';return;}
    if(file.size>(isGlobal?4:25)*1024*1024){tell(`This file exceeds ${isGlobal?4:25} MB. Choose a smaller copy.`,true);$('media-file').value='';return;}
    mediaBusy=true;updateControls();tell('Copying the selected file into the app…');
    try {
      const result=await api(`/api/media?kind=${encodeURIComponent(kind)}&extension=${encodeURIComponent(extension)}`,'POST',file,true);
      media[kind].push({path:result.media,name:result.media.split('/').pop()});
      if(rounds.includes(q)&&q.kind===kind){q.media=result.media;q.media_url='';markDirty();if(rounds[selected]===q){$('media-path').value=q.media;$('media-url').value='';$('media-mode').value='local';showFields();chooseMedia();renderPreview();}tell('File added to the question. Save the deck to use it in the game.');}
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
  $('starter-deck').addEventListener('click',async()=>{if(!confirm('Replace the draft with the bundled starter deck? You can edit it before saving.'))return;busy=true;updateControls();try{const data=await api('/api/starter');replaceDraft(data.rounds);if(data.warning)tell(`Starter needs repair: ${data.warning}`,true);}catch(error){tell(error.message,true);}finally{busy=false;updateControls();}});
  $('reload-deck').addEventListener('click',loadDeck);
  $('preview-answer').addEventListener('change',renderPreview);

  $('bitcoin-template').addEventListener('click',async()=>{
    if(!confirm('Replace this question with a copy of the bundled Bitcoin news article?'))return;
    try{
      const starter=await api('/api/starter');
      const bitcoin=starter.rounds.find(q=>q.kind==='text' && /bitcoin/i.test(q.body||''));
      if(!bitcoin)throw new Error('Bitcoin template is missing from the bundled starter.');
      const draft=JSON.parse(JSON.stringify(bitcoin)); draft.text_style='news';
      draft.news={publication:'Le Parisien',edition:'Paris & Île-de-France',section:'Économie',
        breadcrumb:'Accueil / Économie / Votre argent',author:'Sébastien Lernould',
        published:'Le 5 octobre 2026 à 08h12',topic:'Bitcoin',related:defaultRelated};
      rounds[selected]=draft;markDirty();renderList();loadEditor();tell('Bitcoin article copied. All visible text and branding can now be edited.');
    }catch(error){tell(error.message,true);}
  });

  $('news-logo-file').addEventListener('change',async()=>{
    const file=$('news-logo-file').files[0],q=rounds[selected];if(!file||!q)return;
    const ext='.'+file.name.split('.').pop().toLowerCase();
    if(!formats.image.extensions.includes(ext.slice(1))){tell('Choose a supported image format.',true);return;}
    if(file.size>(isGlobal?4:25)*1024*1024){tell(`Maximum file size: ${isGlobal?4:25} MB.`,true);return;}
    mediaBusy=true;updateControls();
    try{
      const result=await api('/api/media?kind=image&extension='+encodeURIComponent(ext),'POST',file,true);
      if(rounds.includes(q)){q.news=q.news||{};q.news.logo_url=result.media;
        if(rounds[selected]===q){$('news-logo_url').value=result.media;renderPreview();}
        markDirty();tell('Publication logo uploaded. Save the deck to publish.');}
    }catch(error){tell(error.message,true)}finally{mediaBusy=false;$('news-logo-file').value='';updateControls()}
  });
  $('news-image-file').addEventListener('change',async()=>{
    const file=$('news-image-file').files[0], q=rounds[selected];if(!file||!q)return;
    const ext='.'+file.name.split('.').pop().toLowerCase();
    if(!formats.image.extensions.includes(ext.slice(1))){tell('Choose a JPG, PNG, WebP or other supported image.',true);return;}
    if(file.size>(isGlobal?4:25)*1024*1024){tell(`Maximum file size here: ${isGlobal?4:25} MB.`,true);return;}
    mediaBusy=true;updateControls();
    try{
      const result=await api('/api/media?kind=image&extension='+encodeURIComponent(ext),'POST',file,true);
      if(rounds.includes(q)) {q.news=q.news||{};q.news.hero_image=result.media;
        if(rounds[selected]===q){$('news-hero_image').value=result.media;renderPreview();}
        markDirty();tell('Article photo uploaded. Save your deck to publish the new article.');}
    }catch(error){tell(error.message,true)}finally{mediaBusy=false;$('news-image-file').value='';updateControls()}
  });

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
  // One-click ZIP import for the Vercel global deck. The server checks every
  // entry and performs a single revision-checked database save after uploads.
  // No ZIP library is needed in the browser (and no 4MB+ Vercel request).
  if(isGlobal){
    $('import-bundle').addEventListener('click',()=>$('bundle-file').click());
    $('bundle-file').addEventListener('change',async()=>{
      const file=$('bundle-file').files[0];if(!file)return;
      try{
        if(!loaded)throw new Error('Reload the saved deck first.');
        if(dirty)throw new Error('Export or save your unsaved draft first.');
        if(!file.name.toLowerCase().endsWith('.zip'))throw new Error('Choose a .zip bundle.');
        if(file.size>4*1024*1024)throw new Error('The ZIP exceeds the 4 MB Vercel request limit.');
        if(!confirm('Import questions and media from this ZIP into the SHARED deck?\nOK = continue; Cancel = no changes.'))return;
        const replace=confirm('Replace the current question deck?\nOK = REPLACE it; Cancel = APPEND the imported questions.');
        const permission=confirm('If the ZIP references photos hosted by publishers, confirm you have the necessary permissions to use them in your seminar.\nOK = confirm and continue; Cancel = stop.');
        if(!permission)return;
        busy=true;updateControls();tell('Importing ZIP, checking sources and uploading media…');
        const params=new URLSearchParams({revision,mode:replace?'replace':'append',acknowledge_media_rights:'true'});
        const response=await fetch('/api/deck/import-bundle?'+params.toString(),{method:'POST',headers:{'Content-Type':'application/zip'},body:file,cache:'no-store'});
        const data=await response.json().catch(()=>({}));
        if(!response.ok)throw new Error(data.detail||'ZIP upload failed.');
        rounds=data.rounds;revision=data.revision;source=data.source;
        selected=rounds.length?0:-1;dirty=false;loaded=true;renderList();loadEditor();
        tell(`Imported ${data.imported_count} questions and ${data.uploaded_images} images into the shared deck.`);
      }catch(error){tell(error.message,true)}finally{busy=false;$('bundle-file').value='';updateControls()}
    });
  }else $('import-bundle').hidden=true;
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
  // Pull other-editor saves into an open page; never overwrite unsaved drafts.
  setInterval(async()=>{
    if(!loaded || dirty || busy || mediaBusy || document.hidden)return;
    try{const snapshot=await api('/api/deck');if(snapshot.revision!==revision)await loadDeck();}
    catch(_error){/* The explicit reload button will display the error. */}
  },30000);
})();
