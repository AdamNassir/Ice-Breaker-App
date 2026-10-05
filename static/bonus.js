/* Standalone discussion question: no room, points or stored answers. */
(() => {
  'use strict';
  const workflow = window.IcebreakerWorkflow.create();
  workflow.hidden = true;
  document.querySelector('.bonus-page').append(workflow);
  document.querySelectorAll('[data-answer]').forEach(button => button.addEventListener('click', () => {
    document.getElementById('bonus-choices').hidden = true;
    document.getElementById('bonus-reveal').hidden = false;
    workflow.hidden = false;
  }));
})();
