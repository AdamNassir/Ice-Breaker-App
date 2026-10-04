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
  function create(q, className, onError) {
    const start = Number.isInteger(q.media_start) ? q.media_start : 0;
    const end = Number.isInteger(q.media_end) ? q.media_end : null;
    const id = q.kind === 'video' && q.media_url ? youtubeId(q.media_url) : null;
    if (id) {
      const player = document.createElement('iframe');
      const params = new URLSearchParams({start:String(start),autoplay:'0',rel:'0',hl:'en',cc_lang_pref:'en',playsinline:'1'});
      if (end !== null) params.set('end',String(end));
      player.src = `https://www.youtube-nocookie.com/embed/${id}?${params}`;
      player.className = className + ' youtube-player';
      player.title = q.alt || 'Question video clip';
      player.setAttribute('allow','fullscreen; encrypted-media; picture-in-picture');
      player.allowFullscreen = true;
      // YouTube requires an origin referrer to identify an embedded client.
      player.referrerPolicy = 'strict-origin-when-cross-origin';
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
      if (end !== null && player.currentTime >= end) { player.pause(); if (player.currentTime > end) player.currentTime = end; }
    });
    player.addEventListener('error', () => onError('This clip could not play. Check the link, connection and file format.'));
    return player;
  }
  window.IcebreakerMedia = {create,youtubeId};
})();
