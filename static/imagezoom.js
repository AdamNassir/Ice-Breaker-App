/* Player image inspection. No requests, dependencies or changes to voting. */
(() => {
  'use strict';
  const MAX_ZOOM = 6; // EDIT maximum magnification here.
  function create(frame, initial) {
    const viewer = document.createElement('div'); viewer.className = 'image-viewer';
    const viewport = document.createElement('div'); viewport.className = 'image-viewport';
    viewport.tabIndex = 0;
    viewport.setAttribute('role', 'group');
    viewport.setAttribute('aria-label', 'Question image. Pinch to zoom, drag to move. Use plus, minus or arrow keys; zero resets.');
    const controls = document.createElement('div'); controls.className = 'image-zoom-controls';
    const output = document.createElement('output'); output.className = 'image-zoom-level';
    output.setAttribute('aria-label', 'Image zoom');
    const pointers = new Map(); let scale = 1, x = 0, y = 0, gesture = null, lastTap = null, lastTouch = -Infinity;
    let pending = initial || null;
    const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
    function paint() {
      const bounds = viewport.getBoundingClientRect();
      x = clamp(x, -bounds.width * (scale - 1) / 2, bounds.width * (scale - 1) / 2);
      y = clamp(y, -bounds.height * (scale - 1) / 2, bounds.height * (scale - 1) / 2);
      frame.style.transform = `translate(${x}px, ${y}px) scale(${scale})`;
      viewport.classList.toggle('is-zoomed', scale > 1);
      output.textContent = `${Math.round(scale * 100)}%`;
      minus.disabled = scale <= 1; plus.disabled = scale >= MAX_ZOOM;
    }
    function zoom(value, anchor = {x:0, y:0}) {
      const next = clamp(value, 1, MAX_ZOOM), ratio = next / scale;
      x = anchor.x - (anchor.x - x) * ratio;
      y = anchor.y - (anchor.y - y) * ratio;
      scale = next; paint();
    }
    function reset() { pending = null; scale = 1; x = y = 0; lastTap = null; rebase(); paint(); }
    function button(text, label, action) {
      const b = document.createElement('button'); b.type = 'button'; b.textContent = text;
      b.className = 'image-zoom-button'; b.setAttribute('aria-label', label);
      b.addEventListener('click', () => { pending = null; action(); rebase(); });
      return b;
    }
    const minus = button('−', 'Zoom out', () => zoom(scale / 1.5));
    const plus = button('+', 'Zoom in', () => zoom(scale * 1.5));
    const resetButton = button('Reset', 'Reset image zoom and position', reset);
    controls.append(minus, output, plus, resetButton);
    viewport.append(frame); viewer.append(viewport, controls);
    frame.querySelector('img').draggable = false;
    function geometry() {
      const points = [...pointers.values()].slice(0, 2), rect = viewport.getBoundingClientRect();
      const middle = points.length === 2 ? {x:(points[0].x + points[1].x)/2, y:(points[0].y + points[1].y)/2} : points[0];
      return {count:points.length, middle:middle && {x:middle.x - rect.left - rect.width/2, y:middle.y - rect.top - rect.height/2},
        distance:points.length === 2 ? Math.hypot(points[1].x - points[0].x, points[1].y - points[0].y) : 0};
    }
    function rebase() { gesture = {...geometry(), scale, x, y}; }
    viewport.addEventListener('pointerdown', event => {
      if (event.pointerType === 'mouse' && event.button !== 0) return;
      if (event.pointerType !== 'mouse') { event.preventDefault(); lastTouch = performance.now(); }
      pending = null;
      const p = {x:event.clientX, y:event.clientY, startX:event.clientX, startY:event.clientY, moved:false, tap:pointers.size === 0, time:performance.now()};
      if (pointers.size) { lastTap = null; for (const point of pointers.values()) point.tap = false; }
      pointers.set(event.pointerId, p);
      viewport.setPointerCapture(event.pointerId); rebase();
      viewport.classList.add('is-dragging');
    });
    viewport.addEventListener('pointermove', event => {
      const p = pointers.get(event.pointerId); if (!p) return;
      p.x = event.clientX; p.y = event.clientY;
      if (Math.hypot(p.x - p.startX, p.y - p.startY) > 8) p.moved = true;
      const now = geometry();
      if (now.count !== gesture.count) { rebase(); return; }
      const next = now.count === 2 && gesture.distance > 0 ? clamp(gesture.scale * now.distance / gesture.distance, 1, MAX_ZOOM) : gesture.scale;
      const ratio = next / gesture.scale;
      x = now.middle.x - (gesture.middle.x - gesture.x) * ratio;
      y = now.middle.y - (gesture.middle.y - gesture.y) * ratio;
      scale = next; paint();
    });
    function end(event) {
      const p = pointers.get(event.pointerId); if (!p) return;
      pointers.delete(event.pointerId);
      if (event.type === 'pointerup' && event.pointerType !== 'mouse' && p.tap && !p.moved && performance.now() - p.time < 300) {
        const now = performance.now();
        if (lastTap && now - lastTap.time < 350 && Math.hypot(p.x-lastTap.x, p.y-lastTap.y) < 30) {
          const rect = viewport.getBoundingClientRect();
          zoom(scale > 1 ? 1 : 2.5, {x:p.x-rect.left-rect.width/2, y:p.y-rect.top-rect.height/2}); lastTap = null;
        } else lastTap = {time:now, x:p.x, y:p.y};
      } else lastTap = null;
      rebase(); if (!pointers.size) viewport.classList.remove('is-dragging');
    }
    for (const type of ['pointerup', 'pointercancel', 'lostpointercapture']) viewport.addEventListener(type, end);
    viewport.addEventListener('dblclick', event => {
      event.preventDefault();
      if (performance.now() - lastTouch < 600) return;
      const rect = viewport.getBoundingClientRect();
      zoom(scale > 1 ? 1 : 2.5, {x:event.clientX-rect.left-rect.width/2, y:event.clientY-rect.top-rect.height/2});
    });
    viewport.addEventListener('keydown', event => {
      if (event.ctrlKey || event.metaKey || event.altKey || event.isComposing) return;
      if (!['+', '=', '-', '0', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) return;
      event.preventDefault(); pending = null;
      if (event.key === '+' || event.key === '=') zoom(scale * 1.5);
      else if (event.key === '-') zoom(scale / 1.5);
      else if (event.key === '0') reset();
      else { x += event.key === 'ArrowLeft' ? 40 : event.key === 'ArrowRight' ? -40 : 0;
        y += event.key === 'ArrowUp' ? 40 : event.key === 'ArrowDown' ? -40 : 0; paint(); }
      rebase();
    });
    function resize() {
      if (pending && viewport.clientWidth && viewport.clientHeight) {
        scale = clamp(pending.scale, 1, MAX_ZOOM); x = pending.x; y = pending.y; pending = null;
      }
      paint(); rebase();
    }
    // Disconnect when the round changes; avoid retaining detached viewers.
    if (window.ResizeObserver) {
      const observer = new ResizeObserver(() => { if (!viewer.isConnected) observer.disconnect(); else resize(); });
      observer.observe(viewport);
      const cleanup = new MutationObserver(() => { if (!viewer.isConnected) { observer.disconnect(); cleanup.disconnect(); } });
      cleanup.observe(document.getElementById('stage'), {childList:true});
    }
    frame.querySelector('img').addEventListener('load', resize);
    viewer.getView = () => pending || {scale, x, y};
    paint(); return viewer;
  }
  window.IcebreakerImages = {create};
})();
