/* Shared playback for the game and local editor. No media requests go through Supabase. */
(() => {
  'use strict';
  function youtubeId(value) {
    try {
      const url = new URL(value); let id = '';
      if (url.protocol !== 'https:' || url.username || url.password) return null;
      if (url.hostname === 'youtu.be') id = url.pathname.replace(/^\/+|\/+$/g, '');
      else if (['youtube.com','www.youtube.com','m.youtube.com','www.youtube-nocookie.com'].includes(url.hostname)) {
        if (url.pathname === '/watch') id = url.searchParams.get('v') || '';
        else if (/^\/(embed|shorts)\//.test(url.pathname)) id = url.pathname.split('/')[2];
      }
      return /^[\w-]{11}$/.test(id) ? id : null;
    } catch { return null; }
  }
  let youtubeApiPromise;
  function youtubeAPI() {
    if (window.YT?.Player) return Promise.resolve(window.YT);
    if (!youtubeApiPromise) youtubeApiPromise = new Promise((resolve, reject) => {
      const previous = window.onYouTubeIframeAPIReady;
      window.onYouTubeIframeAPIReady = () => {
        if (typeof previous === 'function') previous();
        resolve(window.YT);
      };
      const script = document.createElement('script');
      script.src = 'https://www.youtube.com/iframe_api';
      script.onerror = () => reject(new Error('YouTube playback control could not load.'));
      document.head.append(script);
    });
    return youtubeApiPromise;
  }

  function create(q, className, onError, options = {}) {
    let completed = false;
    const finished = () => {
      if (completed) return;
      completed = true;
      if (typeof options.onEnded === 'function') options.onEnded();
    };
    const start = Number.isInteger(q.media_start) ? q.media_start : 0;
    const end = Number.isInteger(q.media_end) ? q.media_end : null;
    const id = q.kind === 'video' && q.media_url ? youtubeId(q.media_url) : null;
    if (id) {
      const player = document.createElement('iframe');
      const params = new URLSearchParams({start:String(start),autoplay:'0',rel:'0',hl:'en',cc_lang_pref:'en',playsinline:'1'});
      if (options.onEnded) { params.set('enablejsapi', '1'); params.set('origin', location.origin); }
      if (end !== null) params.set('end',String(end));
      player.src = `https://www.youtube-nocookie.com/embed/${id}?${params}`;
      player.className = className + ' youtube-player';
      player.title = q.alt || 'Question video clip';
      player.setAttribute('allow','autoplay; fullscreen; encrypted-media; picture-in-picture');
      player.allowFullscreen = true;
      // YouTube requires an origin referrer to identify an embedded client.
      player.referrerPolicy = 'strict-origin-when-cross-origin';
      if (options.onEnded) {
        // Official YouTube IFrame API reports playback completion including
        // configured clip endpoints. No timer starts until the host receives it.
        youtubeAPI().then(YT => {
          if (!player.isConnected) return;
          const youtubePlayer = new YT.Player(player, { events: {
            onReady: event => { if (options.autoPlay) event.target.playVideo(); },
            onStateChange: event => { if (event.data === YT.PlayerState.ENDED) finished(); },
            onError: () => onError('YouTube cannot play this clip. Use the presenter fallback if needed.')
          }});
          player._icebreakerCleanup = () => { /* Keep embed visible until the phase changes. */ };
        }).catch(() => onError('YouTube playback events are unavailable. The presenter can start voting manually after the clip.'));
      }
      return player;
    }
    const player = document.createElement(q.kind === 'video' ? 'video' : 'audio');
    player.className = className; player.controls = true; player.preload = 'metadata';
    if (q.kind === 'video') player.setAttribute('playsinline','');
    player.setAttribute('aria-label',q.alt || 'Question recording');
    const source = q.media_url || q.media || '';
    // Imported drafts may not have passed server validation yet.
    if (source.startsWith('/static/') || /^https:\/\//i.test(source)) player.src = source;
    player.addEventListener('loadedmetadata', () => {
      if (start >= player.duration && start > 0) { onError('The clip starts beyond the end of this recording.'); return; }
      if (start > 0) player.currentTime = start;
    });
    player.addEventListener('play', () => {
      if (player.currentTime < start || (end !== null && player.currentTime >= end - .05)) player.currentTime = start;
    });
    player.addEventListener('timeupdate', () => {
      if (end !== null && player.currentTime >= end) {
        player.pause(); if (player.currentTime > end) player.currentTime = end;
        finished();
      }
    });
    player.addEventListener('ended', finished);
    if (options.autoPlay) {
      player.addEventListener('canplay', () => {
        if (!completed && player.paused) player.play().catch(() => {
          // Browsers can block unmuted autoplay. The presenter can press Play.
        });
      }, {once:true});
    }
    player.addEventListener('error', () => onError('This clip could not play. Check the link, connection and file format.'));
    return player;
  }
  window.IcebreakerMedia = {create,youtubeId};
})();
