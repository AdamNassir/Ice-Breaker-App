/* Standalone discussion question: no room, points or stored answers. */
(() => {
  'use strict';
  document.querySelectorAll('[data-answer]').forEach(button => button.addEventListener('click', () => {
    document.getElementById('bonus-choices').hidden = true;
    document.getElementById('bonus-reveal').hidden = false;
  }));
})();
