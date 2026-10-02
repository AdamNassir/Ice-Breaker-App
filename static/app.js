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
  let lastHost = '';
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
      const link = value.join_url || `${location.origin}/?room=${value.code}`;
      $('join-url').textContent = link; $('join-url').href = link;
      loadQR(value);
    }
  }

  async function loadQR(value) {
    const qr = $('join-qr'), status = $('qr-status'), retry = $('retry-qr');
    const attempt = ++qrAttempt;
    qr.hidden = true; retry.hidden = true;
    status.textContent = 'Creating QR code…';
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
      $('join-url').textContent = result.join_url; $('join-url').href = result.join_url;
      qr.hidden = false;
      status.textContent = 'Scan with your phone camera.';
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

  function renderStage(s) {
    const signature = JSON.stringify([s.phase, s.round_index, s.question]);
    if (signature === stageKey) return;
    stageKey = signature;
    const stage = $('stage'); stage.replaceChildren();
    if (s.phase === 'lobby') {
      stage.append(waiting(host ? 'The room is open.' : "You're in.", host ?
        'Share the player link or room code. Start the first round when everyone is ready.' :
        `Welcome, ${s.me.nickname}. Watch this screen for the first round.`));
    } else if (s.phase === 'ready') {
      stage.append(waiting(`Round ${s.round_number} is next.`, host ?
        'Take a moment, then start the timer when you are ready.' : 'Your presenter will start the next round.'));
    } else if (s.phase === 'finished') {
      const winners = s.leaderboard.filter(p => p.rank === 1);
      const title = winners.length > 1 ? 'A shared first place!' : `${winners[0]?.nickname || 'Everyone'} takes first place!`;
      const wrap = waiting('The verdict is in.', title, '★');
      if (!host) {
        wrap.append(element('div', 'results-score', `${s.me.score} points`),
          element('p', '', `Rank ${s.me.rank} · ${s.me.correct} correct out of ${s.me.history.length} rounds played`));
      }
      wrap.append(element('p', 'final-note', 'What fooled you? Discuss the clues you trusted. Provenance is stronger evidence than appearance.'));
      stage.append(wrap);
    } else {
      const q = s.question;
      const heading = element('div', 'content-meta');
      heading.append(element('span', 'kind', q.kind === 'text' ? 'Written content' : q.kind));
      if (Number.isInteger(q.difficulty) && q.difficulty >= 1 && q.difficulty <= 5) {
        const levels = ['Warm-up', 'Inspection', 'Subtle behavior', 'Concurrency', 'Expert'];
        heading.append(element('span', 'difficulty', `Level ${q.difficulty}/5 · ${levels[q.difficulty - 1]}`));
      }
      stage.append(heading, element('h2', '', q.title));
      if (q.context) stage.append(element('p', 'question-context', q.context));
      if (q.kind === 'image') {
        const img = element('img', 'round-image'); img.src = q.media; img.alt = q.alt || 'Round image';
        if (['contain', 'cover'].includes(q.image_fit)) img.style.objectFit = q.image_fit;
        if (q.image_position) img.style.objectPosition = q.image_position;
        img.addEventListener('error', () => {
          if (!stage.querySelector('.image-error')) stage.append(element('p', 'image-error', 'Image could not load. Tell the presenter before voting.'));
        });
        stage.append(img);
      } else if (q.kind === 'audio' || q.kind === 'video') {
        const isVideo = q.kind === 'video';
        stage.append(element('p', 'small', q.body || (isVideo ? 'Watch, then choose AI or Human.' : 'Listen, then choose AI or Human.')));
        const player = element(q.kind, isVideo ? 'round-video' : 'round-audio');
        player.src = q.media; player.controls = true; player.preload = 'metadata';
        if (isVideo) player.setAttribute('playsinline', '');
        player.setAttribute('aria-label', q.alt || (isVideo ? 'Round video' : 'Round audio'));
        player.addEventListener('error', () => stage.append(element('p', 'image-error', `${isVideo ? 'Video' : 'Audio'} could not play. Tell the presenter and check the file format.`)));
        stage.append(player);
      } else stage.append(element(q.kind === 'text' ? 'p' : 'pre', q.kind === 'text' ? 'text-content' : 'code-block', q.body));
    }
  }

  function renderReveal(s) {
    const panel = $('reveal'); panel.hidden = !s.reveal;
    if (!s.reveal) { panel.replaceChildren(); return; }
    const r = s.reveal;
    const signature = JSON.stringify([r, s.me?.history]);
    if (panel.dataset.signature === signature) return;
    panel.dataset.signature = signature; panel.replaceChildren();
    panel.append(element('h3', '', `The answer is ${r.answer}.`), element('p', '', r.explanation));
    if (r.technical_note) {
      panel.append(element('h4', 'reveal-subtitle', 'Technical detail'), element('p', '', r.technical_note));
    }
    if (r.discussion) panel.append(element('p', 'discussion-prompt', `Discuss: ${r.discussion}`));
    if (s.me) {
      const last = s.me.history.find(row => row.round === s.round_number);
      const message = last ? (last.correct ? `Correct! +${last.points} points · ${s.me.streak} in a row` :
        last.answer ? 'A convincing disguise. Your streak starts fresh next round.' : 'No answer this round. Try the next one.') : 'You joined after this round ended.';
      panel.append(element('p', 'result-note', message));
    }
    panel.append(element('p', 'vote-counts', `The room voted: AI ${r.distribution.AI} · HUMAN ${r.distribution.HUMAN}`));
    const source = element('p', 'source', r.source);
    if (r.source_url && /^https:\/\//.test(r.source_url)) {
      const link = element('a', '', ' View source'); link.href = r.source_url; link.target = '_blank'; link.rel = 'noopener noreferrer'; source.append(link);
    }
    if (r.technical_source_url && /^https:\/\//.test(r.technical_source_url)) {
      const link = element('a', '', ' Technical reference');
      link.href = r.technical_source_url; link.target = '_blank'; link.rel = 'noopener noreferrer'; source.append(link);
    }
    panel.append(source);
  }

  function renderBoard(s) {
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
    // Use monotonic browser time rather than the phone's possibly inaccurate wall clock.
    if (newSnapshot) clockEnd = performance.now() + Math.max(0, (s.deadline - s.server_time) * 1000 - roundTrip / 2);
    $('room-title').textContent = s.title;
    const labels = {lobby:'IN THE LOBBY', ready:'TAKE A BREATHER', live:'MAKE YOUR CALL', revealed:'THE REVEAL', finished:'FINAL RESULTS'};
    $('phase-label').textContent = labels[s.phase];
    $('round-label').textContent = s.phase === 'finished' ? `${s.round_count} rounds complete` : `Round ${s.round_number} / ${s.round_count}`;
    $('room-meta').textContent = `${s.player_count} player${s.player_count === 1 ? '' : 's'} · Room ${s.code}`;
    $('board-title').textContent = s.phase === 'finished' ? 'Final standings' : 'Leaderboard';
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
      $('control-help').textContent = s.phase === 'live' ? 'Answers reveal when the timer reaches zero.' : s.phase === 'revealed' ?
        'Discuss the reveal, then continue when ready.' : s.phase === 'finished' ? 'Create a new room for another game.' : 'The timer starts when you do.';
    } else {
      $('my-score').textContent = s.me.score; $('my-streak').textContent = s.me.streak; $('my-rank').textContent = s.me.rank;
      $('vote-controls').hidden = !['live','revealed'].includes(s.phase);
      document.querySelectorAll('[data-answer]').forEach(button => {
        button.classList.toggle('selected', button.dataset.answer === s.me.vote);
        button.disabled = votePending || s.phase !== 'live' || Boolean(s.me.vote) || performance.now() >= clockEnd;
      });
      $('vote-status').textContent = s.phase === 'live' ? (s.me.vote ? `${s.me.vote} locked in. Wait for the reveal.` : 'One answer. Make it count.') :
        s.phase === 'revealed' ? 'Your presenter will choose when to continue.' : '';
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
      try {
        const room = await api('/api/rooms', {title:$('game-title').value, seconds:Number($('seconds').value), password:$('password').value}, false);
        $('password').value = ''; saveSession(room); await poll();
      } catch (error) { notify(error.message); } finally { $('create-button').disabled = false; }
    });
    $('control-button').addEventListener('click', async () => {
      if (!state || controlPending) return;
      controlPending = true; $('control-button').disabled = true;
      try {
        const s = await api(`/api/rooms/${session.code}/control`, {action:state.phase === 'revealed' ? 'next' : 'start', revision:state.revision});
        render(s);
      } catch (error) { notify(error.message); await poll(); }
      finally { controlPending = false; if (state) render(state); }
    });
    $('copy-link').addEventListener('click', async () => {
      try { await navigator.clipboard.writeText($('join-url').href); notify('Player link copied.'); }
      catch { notify('Copy the player link shown above. Clipboard access is unavailable here.'); }
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
