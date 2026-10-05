/* No frontend framework or build step. All scores/deadlines come from FastAPI. */
(() => {
  'use strict';
  const host = document.body.dataset.role === 'presenter';
  const $ = id => document.getElementById(id);
  const storage = host ? sessionStorage : localStorage;
  const key = code => `icebreaker:${host ? 'host' : 'player'}:${code}`;
  let session = null, state = null, polling = false, votePending = false, controlPending = false;
  let stageKey = '', boardKey = '', clockEnd = 0, noticeTimeout = null, qrAttempt = 0;
  const query = new URLSearchParams(location.search);
  let lastHost = '', playerLink = '';
  const celebratedRooms = new Set();
  try { if (host) lastHost = sessionStorage.getItem('icebreaker:last-host') || ''; } catch {}
  const initialCode = (query.get('room') || lastHost).toUpperCase();

  function notify(message, persistent = false) {
    clearTimeout(noticeTimeout);
    $('notice').textContent = message;
    $('notice').hidden = false;
    if (!persistent) noticeTimeout = setTimeout(() => { $('notice').hidden = true; }, 6000);
  }

  async function api(path, body, authenticated = true) {
    const headers = { 'Content-Type': 'application/json' };
    if (authenticated && session) headers.Authorization = `Bearer ${session.token}`;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 12000);
    try {
      const response = await fetch(path, {
        method: body === undefined ? 'GET' : 'POST', headers,
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: controller.signal, cache: 'no-store'
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const message = typeof data.detail === 'string' ? data.detail : 'Check the form and try again.';
        const error = new Error(message); error.status = response.status; throw error;
      }
      return data;
    } catch (error) {
      if (error.name === 'AbortError') throw new Error('Connection timed out. Check your network and retry.');
      throw error;
    } finally { clearTimeout(timeout); }
  }

  function saveSession(value) {
    session = value;
    try {
      storage.setItem(key(value.code), JSON.stringify(value));
      if (host) sessionStorage.setItem('icebreaker:last-host', value.code);
    } catch { notify('Browser storage is unavailable. Keep this tab open during the game.'); }
    history.replaceState(null, '', `${host ? '/presenter' : '/'}?room=${value.code}`);
    $('entry').hidden = true; $('game').hidden = false; $('leave').hidden = false;
    if (host) {
      $('share-code').textContent = value.code;
      playerLink = value.join_url || `${location.origin}/?room=${value.code}`;
      loadQR(value);
    }
  }

  async function loadQR(value) {
    const qr = $('join-qr'), status = $('qr-status'), retry = $('retry-qr');
    const attempt = ++qrAttempt;
    qr.hidden = true; retry.hidden = true;
    status.hidden = false; status.textContent = 'Creating QR code…';
    try {
      const result = await api(`/api/rooms/${value.code}/qr`);
      if (session !== value || attempt !== qrAttempt) return;
      // Draw the server-generated modules directly. No image-load event or
      // data-URL support is needed to finish showing the QR code.
      const matrix = result.qr_matrix;
      if (!Array.isArray(matrix) || matrix.length < 21 || matrix.length > 185 ||
          !matrix.every(row => Array.isArray(row) && row.length === matrix.length &&
            row.every(cell => typeof cell === 'boolean'))) {
        throw new Error('QR response is outdated or invalid. Refresh this page after updating the app.');
      }
      const context = qr.getContext('2d');
      if (!context) throw new Error('This browser cannot draw the QR code.');
      const scale = 10;
      qr.width = qr.height = matrix.length * scale;
      context.fillStyle = '#ffffff'; context.fillRect(0, 0, qr.width, qr.height);
      context.fillStyle = '#000000';
      matrix.forEach((row, y) => row.forEach((dark, x) => {
        if (dark) context.fillRect(x * scale, y * scale, scale, scale);
      }));
      playerLink = result.join_url;
      qr.hidden = false;
      status.textContent = ''; status.hidden = true;
    } catch (error) {
      if (session === value && attempt === qrAttempt) {
        status.textContent = `QR code unavailable: ${error.message} Use the player link or room code.`;
        retry.hidden = false;
      }
    }
  }

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function waiting(title, message, symbol = '◎') {
    const wrap = element('div', 'waiting');
    wrap.append(element('span', 'waiting-icon', symbol), element('h2', '', title), element('p', '', message));
    return wrap;
  }

  function placement(player, me, podium = false) {
    const row = element(podium ? 'article' : 'li', `final-player${podium ? ' podium-player' : ''}${player.id === me ? ' final-me' : ''}`);
    row.dataset.rank = player.rank; row.dataset.playerId = player.id;
    const rank = element('span', 'final-rank', String(player.rank));
    rank.setAttribute('aria-label', `Rank ${player.rank}`);
    if (player.rank <= 3) {
      const medal = element('span', 'final-medal', ['🥇', '🥈', '🥉'][player.rank - 1]);
      medal.setAttribute('aria-hidden', 'true'); rank.prepend(medal);
    }
    row.append(rank, element('strong', 'final-name', player.nickname), element('span', 'final-score', String(player.score)));
    return row;
  }

  function results(s) {
    const wrap = element('section', 'final-standings');
    wrap.setAttribute('aria-label', 'Final placements');
    const ranks = [1, 2, 3].filter(rank => s.leaderboard.some(player => player.rank === rank));
    const podium = element('div', `final-podium podium-count-${ranks.length}`);
    for (const rank of ranks) {
      const place = element('div', `podium-place podium-rank-${rank}`);
      s.leaderboard.filter(player => player.rank === rank).forEach(player => place.append(placement(player, s.me?.id, true)));
      podium.append(place);
    }
    wrap.append(podium);
    const rest = element('ol', 'final-list');
    s.leaderboard.filter(player => player.rank > 3).forEach(player => rest.append(placement(player, s.me?.id)));
    if (rest.children.length) wrap.append(rest);
    if (!host) wrap.append(playerBonus(s.code));
    return wrap;
  }

  function celebrate(podium, code) {
    if (!podium || celebratedRooms.has(code)) return;
    celebratedRooms.add(code);
    if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) return;
    const layer = element('div', 'confetti-layer');
    layer.setAttribute('aria-hidden', 'true');
    const places = [...podium.querySelectorAll('.podium-place')];
    const bounds = podium.getBoundingClientRect();
    places.forEach((place, index) => {
      const box = place.getBoundingClientRect();
      const fallback = places.length === 3 ? [50, 16.7, 83.3][index] : (index + .5) / places.length * 100;
      for (let i = 0; i < 24; i++) {
        const piece = element('i', 'confetti-piece');
        piece.style.left = bounds.width ? `${box.left + box.width / 2 - bounds.left}px` : `${fallback}%`;
        piece.style.top = `${box.top - bounds.top + 12}px`;
        piece.style.background = ['#e52330', '#1f2ade', '#ffffff'][i % 3];
        piece.style.setProperty('--dx', `${(Math.random() - .5) * 420}px`);
        piece.style.setProperty('--rise', `${-160 - Math.random() * 180}px`);
        piece.style.setProperty('--spin', `${360 + Math.random() * 900}deg`);
        piece.style.animationDelay = `${Math.random() * .3}s`;
        layer.append(piece);
      }
    });
    podium.append(layer);
    setTimeout(() => layer.remove(), 4300);
  }

  function imageFrame(q, highlight, zoomView) {
    const frame = element('figure', 'image-frame');
    const img = element('img', 'round-image'); img.src = q.media; img.alt = q.alt || 'Round image';
    if (['contain', 'cover'].includes(q.image_fit)) img.style.objectFit = q.image_fit;
    if (q.image_position) img.style.objectPosition = q.image_position;
    img.addEventListener('error', () => {
      if (!frame.querySelector('.image-error')) frame.append(element('p', 'image-error', 'Image could not load. Tell the presenter before voting.'));
    });
    frame.append(img);
    if (highlight) {
      const ns = 'http://www.w3.org/2000/svg';
      const overlay = document.createElementNS(ns, 'svg');
      overlay.classList.add('image-highlight'); overlay.setAttribute('aria-hidden', 'true');
      overlay.style.display = 'none';
      const circle = document.createElementNS(ns, 'circle');
      circle.setAttribute('fill', 'none'); circle.setAttribute('stroke', '#ff2020');
      circle.setAttribute('stroke-width', '5'); circle.setAttribute('vector-effect', 'non-scaling-stroke');
      overlay.append(circle); frame.append(overlay);
      const position = () => {
        if (!img.naturalWidth || !img.naturalHeight) return;
        overlay.setAttribute('viewBox', `0 0 ${img.naturalWidth} ${img.naturalHeight}`);
        overlay.setAttribute('preserveAspectRatio', q.image_fit === 'cover' ? 'xMidYMid slice' : 'xMidYMid meet');
        circle.setAttribute('cx', String(highlight.x / 100 * img.naturalWidth));
        circle.setAttribute('cy', String(highlight.y / 100 * img.naturalHeight));
        circle.setAttribute('r', String(highlight.radius / 100 * img.naturalWidth));
        overlay.style.display = '';
      };
      img.addEventListener('load', position);
      if (img.complete) position();
    }
    return host ? frame : window.IcebreakerImages.create(frame, zoomView);
  }

  function playerBonus(code) {
    // Phone-only epilogue. No API request, timer, vote or score change.
    const panel = element('section', 'player-bonus');
    panel.setAttribute('aria-label', 'Bonus question');
    panel.append(element('h2', '', 'Was this game made with AI or not ?'));
    const choices = element('div', 'vote-controls');
    const reveal = element('p', 'bonus-reveal', 'AI');
    reveal.setAttribute('aria-live', 'polite');
    const workflow = window.IcebreakerWorkflow.create();
    const savedKey = `icebreaker:bonus:${code}`;
    let answered = false;
    try { answered = storage.getItem(savedKey) === 'answered'; } catch {}
    choices.hidden = answered; reveal.hidden = !answered; workflow.hidden = !answered;
    for (const answer of ['AI', 'HUMAN']) {
      const button = element('button', `answer ${answer.toLowerCase()}`, answer);
      button.type = 'button';
      button.addEventListener('click', () => {
        choices.hidden = true; reveal.hidden = false; workflow.hidden = false;
        try { storage.setItem(savedKey, 'answered'); } catch {}
      });
      choices.append(button);
    }
    panel.append(choices, reveal, workflow);
    return panel;
  }

  function renderStage(s) {
    const signature = JSON.stringify([s.code, s.phase, s.round_index, s.question, s.reveal?.reveal_media, s.reveal?.reveal_alt, s.phase === 'finished' ? s.leaderboard : null]);
    if (signature === stageKey) return;
    stageKey = signature;
    const stage = $('stage');
    const imageKey = s.question?.kind === 'image' ? `${s.code}:${s.round_index}:${s.question.media}` : '';
    const zoomView = imageKey && stage.dataset.imageKey === imageKey ? stage.querySelector('.image-viewer')?.getView() : undefined;
    const newsKey = s.question?.kind === 'text' && s.question.text_style === 'news'
      ? JSON.stringify([s.code, s.round_index, s.question.body]) : '';
    const newsScroll = newsKey && stage.dataset.newsKey === newsKey ? stage.querySelector('.news-site')?.scrollTop : 0;
    stage.dataset.newsKey = newsKey;
    stage.dataset.imageKey = imageKey;
    stage.replaceChildren();
    stage.classList.toggle('text-stage', ['live', 'revealed'].includes(s.phase) && s.question?.kind === 'text');
    if (s.phase === 'lobby') {
      if (!host) stage.append(waiting("You're in.", `Welcome, ${s.me.nickname}. Watch this screen for the first round.`));
    } else if (s.phase === 'ready') {
      stage.append(waiting(`Round ${s.round_number} is next.`, host ?
        'Take a moment, then start the timer when you are ready.' : 'Your presenter will start the next round.'));
    } else if (s.phase === 'finished') {
      stage.append(results(s));
      celebrate(stage.querySelector('.final-podium'), s.code);
    } else {
      const q = s.question;
      const heading = element('div', 'question-heading');
      heading.append(element('h2', 'question-title', q.title));
      if (q.context) heading.append(element('p', 'question-intro', q.context));
      stage.append(heading);
      if (q.kind === 'image') {
        // Same round/image key preserves phone zoom when identities are revealed.
        const revealed = s.phase === 'revealed' && s.reveal?.reveal_media;
        const image = revealed ? {...q, media: s.reveal.reveal_media, alt: s.reveal.reveal_alt || q.alt} : q;
        stage.append(imageFrame(image, s.reveal?.image_highlight, zoomView));
      } else if (q.kind === 'audio' || q.kind === 'video') {
        const isVideo = q.kind === 'video';
        const player = window.IcebreakerMedia.create(q, isVideo ? 'round-video' : 'round-audio', message => {
          if (!stage.querySelector('.image-error')) stage.append(element('p', 'image-error', message));
        });
        stage.append(player);
      } else if (q.kind === 'text') {
        if (q.text_style === 'news') {
          const page = window.IcebreakerNews.create(q);
          stage.append(page);
          page.scrollTop = newsScroll || 0;
          return;
        }
        const prose = element('div', 'text-content');
        q.body.split('\n\n').forEach((part, index) => {
          if (index) prose.append(document.createTextNode('\n\n'));
          prose.append(element('p', 'text-paragraph', part));
        });
        stage.append(prose);
      } else stage.append(element('pre', 'code-block', q.body));
    }
  }

  function renderReveal(s) {
    const panel = $('reveal'); panel.hidden = !s.reveal;
    if (!s.reveal) { panel.replaceChildren(); return; }
    const r = s.reveal;
    const signature = JSON.stringify([s.round_index, r.answer, r.image_reveal, r.source_url, r.reveal_sources]);
    if (panel.dataset.signature === signature) return;
    panel.dataset.signature = signature; panel.replaceChildren();
    panel.append(element('h3', '', r.answer));
    if (s.question?.kind === 'image' && r.answer === 'HUMAN' && r.image_reveal) {
      panel.append(element('p', 'photo-credit', r.image_reveal));
      if (r.source_url?.startsWith('https://')) {
        const link = element('a', 'photo-source', 'View source');
        link.href = r.source_url; link.target = '_blank'; link.rel = 'noopener noreferrer';
        panel.append(link);
      }
    }
    if (s.question?.kind === 'text' && r.answer === 'HUMAN' && r.reveal_sources?.length) {
      const sources = element('div', 'text-sources');
      sources.append(element('p', '', 'Sources'));
      r.reveal_sources.forEach(source => {
        if (!source.url?.startsWith('https://')) return;
        const link = element('a', 'text-source', source.label);
        link.href = source.url; link.target = '_blank'; link.rel = 'noopener noreferrer';
        sources.append(link);
      });
      panel.append(sources);
    }
  }

  function renderBoard(s) {
    if (host) return;
    const signature = JSON.stringify([s.leaderboard, s.me?.id]);
    if (signature === boardKey) return;
    boardKey = signature;
    const board = $('leaderboard'); board.replaceChildren();
    if (!s.leaderboard.length) board.append(element('p', 'empty-board', 'Players will appear here as they join.'));
    s.leaderboard.forEach(p => {
      const row = element('div', `leader-row${s.me?.id === p.id ? ' me' : ''}`);
      const name = element('div', 'nickname', p.nickname + (s.me?.id === p.id ? ' (you)' : ''));
      if (p.streak > 1) name.append(element('span', 'leader-streak', `${p.streak} correct in a row`));
      row.append(element('span', 'rank', String(p.rank).padStart(2, '0')), name, element('span', 'leader-score', p.score)); board.append(row);
    });
  }

  function render(s, roundTrip = 0) {
    if (state && s.server_time < state.server_time) return; // Ignore out-of-order HTTP responses.
    const newSnapshot = s !== state;
    state = s;
    const finished = s.phase === 'finished';
    document.body.classList.toggle('results-mode', finished);
    document.querySelectorAll('.topbar, footer, .game-heading, #round-progress, .round-toolbar, .side-card, .host-controls, #vote-status, #connection').forEach(node => node.hidden = finished);
    if (host) {
      const lobby = s.phase === 'lobby';
      document.body.classList.toggle('presenter-lobby', lobby);
      document.body.classList.toggle('presenter-playing', !lobby && !finished);
      $('qr-lobby').hidden = !lobby;
      $('stage').hidden = lobby;
      document.querySelectorAll('.game-heading, #round-progress, .round-toolbar').forEach(node => node.hidden = lobby || finished);
    }
    if (finished) $('notice').hidden = true;
    // Use monotonic browser time rather than the phone's possibly inaccurate wall clock.
    if (newSnapshot) clockEnd = performance.now() + Math.max(0, (s.deadline - s.server_time) * 1000 - roundTrip / 2);
    $('room-title').textContent = s.title;
    const labels = {lobby:'IN THE LOBBY', ready:'TAKE A BREATHER', live:'MAKE YOUR CALL', revealed:'THE REVEAL', finished:'FINAL RESULTS'};
    $('phase-label').textContent = labels[s.phase];
    $('round-label').textContent = s.phase === 'finished' ? `${s.round_count} rounds complete` : `Round ${s.round_number} / ${s.round_count}`;
    $('room-meta').textContent = `${s.player_count} player${s.player_count === 1 ? '' : 's'} · Room ${s.code}`;
    if (!host) $('board-title').textContent = s.phase === 'finished' ? 'Final standings' : 'Leaderboard';
    const progress = $('round-progress'); progress.replaceChildren();
    for (let i = 0; i < s.round_count; i++) {
      const node = element('span', i < s.round_index || s.phase === 'finished' || (i === s.round_index && s.phase === 'revealed') ? 'done' :
        i === s.round_index && s.phase === 'live' ? 'active' : '');
      progress.append(node);
    }
    $('clock-wrap').hidden = s.phase !== 'live'; $('timer-track').hidden = s.phase !== 'live';
    renderStage(s); renderReveal(s); renderBoard(s);
    if (host) {
      $('answered-count').textContent = s.phase === 'live' || s.phase === 'revealed' ? `${s.answered_count} / ${s.player_count} answered` : '';
      const button = $('control-button');
      button.hidden = s.phase === 'finished';
      button.disabled = controlPending || s.phase === 'live' || !s.player_count;
      button.textContent = s.phase === 'live' ? 'Round in progress' : s.phase === 'revealed' ?
        s.round_number === s.round_count ? 'Show final results' : 'Next round' : `Start round ${s.round_number}`;
      $('control-help').textContent = '';
    } else {
      $('my-score').textContent = s.me.score; $('my-streak').textContent = s.me.streak; $('my-rank').textContent = s.me.rank;
      $('vote-controls').hidden = s.phase !== 'live';
      document.querySelectorAll('[data-answer]').forEach(button => {
        button.classList.toggle('selected', button.dataset.answer === s.me.vote);
        button.disabled = votePending || s.phase !== 'live' || Boolean(s.me.vote) || performance.now() >= clockEnd;
      });
      $('vote-status').textContent = s.phase === 'live' ? (s.me.vote ? `${s.me.vote} locked in. Wait for the reveal.` : 'One answer. Make it count.') :
        '';
    }
    updateClock();
  }

  function updateClock() {
    if (!state || state.phase !== 'live') return;
    const remaining = Math.max(0, (clockEnd - performance.now()) / 1000);
    $('clock').textContent = Math.ceil(remaining);
    $('timer-fill').style.width = `${Math.min(100, remaining / state.duration * 100)}%`;
    if (!remaining && !host) document.querySelectorAll('[data-answer]').forEach(button => button.disabled = true);
  }

  async function poll() {
    if (!session || polling || votePending || controlPending || document.hidden) return;
    polling = true;
    const started = performance.now();
    try {
      const s = await api(`/api/rooms/${session.code}/state`);
      render(s, performance.now() - started); $('connection').textContent = '';
    } catch (error) {
      $('connection').textContent = `${error.message} ${[401,404,410].includes(error.status) ? 'Return to setup to join another room.' : 'Reconnecting…'}`;
      if (!host) document.querySelectorAll('[data-answer]').forEach(button => button.disabled = true);
    } finally { polling = false; }
  }

  if (host) {
    $('retry-qr').addEventListener('click', () => { if (session) loadQR(session); });
    $('seconds').addEventListener('input', () => { $('seconds-output').textContent = `${$('seconds').value} sec`; });
    $('create-form').addEventListener('submit', async event => {
      event.preventDefault(); $('create-button').disabled = true;
      $('notice').hidden = true;
      try {
        const room = await api('/api/rooms', {title:$('game-title').value, seconds:Number($('seconds').value), password:$('password').value}, false);
        $('password').value = ''; saveSession(room); await poll();
      } catch (error) { notify(error.message, error.status === 503); } finally { $('create-button').disabled = false; }
    });
    $('control-button').addEventListener('click', async () => {
      if (!state || !session || controlPending || $('control-button').disabled || $('control-button').hidden) return;
      controlPending = true; $('control-button').disabled = true;
      try {
        const s = await api(`/api/rooms/${session.code}/control`, {action:state.phase === 'revealed' ? 'next' : 'start', revision:state.revision});
        render(s);
      } catch (error) { notify(error.message); await poll(); }
      finally { controlPending = false; if (state) render(state); }
    });
    document.addEventListener('keydown', event => {
      if (event.key !== 'Enter' || event.defaultPrevented || event.isComposing ||
          event.altKey || event.ctrlKey || event.metaKey || event.shiftKey ||
          !state || state.phase !== 'revealed') return;
      const button = $('control-button');
      // Keep form fields and unrelated controls' normal keyboard behavior.
      const target = event.target;
      if (target instanceof Element && (target.isContentEditable ||
          target.closest('input, textarea, select, a, [contenteditable], [role="button"], button') && target !== button)) return;
      event.preventDefault();
      // Suppress held keys and double presses while the next round is starting.
      if (event.repeat || controlPending || button.disabled || button.hidden) return;
      button.click();
    });
    $('copy-link').addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(playerLink); notify('Player link copied.'); }
      catch { notify('Clipboard access is unavailable here. Use the QR code or room code.'); }
    });
  } else {
    $('room-code').value = initialCode;
    $('join-form').addEventListener('submit', async event => {
      event.preventDefault(); $('join-button').disabled = true;
      try {
        const code = $('room-code').value.trim().toUpperCase();
        const room = await api(`/api/rooms/${code}/join`, {nickname:$('nickname').value.trim()}, false);
        saveSession(room); await poll();
      } catch (error) { notify(error.message); } finally { $('join-button').disabled = false; }
    });
    document.querySelectorAll('[data-answer]').forEach(button => button.addEventListener('click', async () => {
      if (votePending || !state || state.phase !== 'live') return;
      votePending = true; document.querySelectorAll('[data-answer]').forEach(b => b.disabled = true);
      try {
        render(await api(`/api/rooms/${session.code}/vote`, {answer:button.dataset.answer, round_index:state.round_index}));
      } catch (error) { notify(error.message); await poll(); }
      finally { votePending = false; if (state) render(state); }
    }));
  }

  $('leave').addEventListener('click', () => {
    session = null; state = null;
    try { if (host) sessionStorage.removeItem('icebreaker:last-host'); } catch {}
    history.replaceState(null, '', host ? '/presenter' : '/');
    $('entry').hidden = false; $('game').hidden = true; $('leave').hidden = true;
    document.body.classList.remove('results-mode', 'presenter-lobby', 'presenter-playing');
    document.querySelectorAll('.topbar, footer, .game-heading, #round-progress, .round-toolbar, .side-card, .host-controls, #vote-status, #connection').forEach(node => node.hidden = false);
    $('connection').textContent = ''; if (!host) $('room-code').value = '';
    stageKey = ''; boardKey = '';
  });
  try {
    const saved = initialCode && storage.getItem(key(initialCode));
    if (saved) saveSession(JSON.parse(saved));
  } catch { notify('Browser storage is unavailable. Keep this tab open during the game.'); }
  document.addEventListener('visibilitychange', () => { if (!document.hidden) poll(); });
  setInterval(poll, 1500); // EDIT polling cadence here (milliseconds).
  setInterval(updateClock, 100);
  poll();
})();
