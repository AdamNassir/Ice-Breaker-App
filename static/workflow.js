/* Shared post-bonus explanation. Presentation narrative, not an agent runner. */
(() => {
  'use strict';
  const steps = [
    ['One complete instruction file',
      'I gave the agent a single brief covering the app, restrictions, code structure and expected behaviour.'],
    ['The agent built and checked the app',
      'I configured the agent to test what it produces. It cycled through build, test, fix and test again before returning an output.'],
    ['I reviewed the code and tested it',
      'I went into the code, ran the app and tested the experience myself on the presenter screen and on phones.'],
    ['I set up the question manager',
      'I added instructions for AI-generated content and supplied sources for real content, then assembled and checked the questions.'],
    ['UpdateGuide.md became the update loop',
      'With the local watcher running, I saved a request in UpdateGuide.md. The agent changed the code and tested it. Independent checks fed failures back for another attempt; once they passed, the watcher replaced my request with a report.'],
    ['I verified the report and tested again',
      'I checked the modified files and behaviour. Any further change went back into UpdateGuide.md, and the cycle repeated.']
  ];
  function node(tag, className, text) {
    const item = document.createElement(tag); item.className = className;
    if (text) item.textContent = text;
    return item;
  }
  function create() {
    const panel = node('section', 'build-workflow');
    panel.setAttribute('aria-label', 'From instructions to app');
    panel.append(node('h3', 'workflow-heading', 'From instructions to app'));
    panel.append(node('p', 'workflow-caption', 'An illustrative reconstruction of the development workflow.'));
    const list = node('ol', 'workflow-steps');
    for (const [title, body] of steps) {
      const step = node('li', 'workflow-step');
      step.append(node('h4', '', title), node('p', '', body)); list.append(step);
    }
    panel.append(list, node('p', 'workflow-loop', 'Instructions → build → agent checks → human review → update → repeat'));
    panel.append(node('p', 'workflow-note', 'The local watcher must be running to react to saved requests. The deployed game stays separate from the agent.'));
    return panel;
  }
  window.IcebreakerWorkflow = {create};
})();
