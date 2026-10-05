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
      'I wrote a requested change and saved the file. The agent read it, changed the code and tested the result, then replaced my request with a report of what it had done.'],
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
    panel.append(node('p', 'workflow-note', 'Saving a file hands off instructions to a running agent workflow; the game itself does not run or watch an agent.'));
    return panel;
  }
  window.IcebreakerWorkflow = {create};
})();
