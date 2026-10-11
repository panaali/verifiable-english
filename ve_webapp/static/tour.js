'use strict';
// Guided first-run tour. It fills in its own example, points at the real
// control for each step, and can press that control for the reader.
const TOUR_KEY = 've-tour-done';
const TOUR = {
  sentence: 'Every employee may read the handbook.',
  mistake: 'Every employee may print the handbook.',
  twoReadings: 'Every engineer checks a server.',
  question: 'Every employee who is new may read the handbook.',
};
let tourAt = -1, tourDone = false, tourBusy = false;

function tourStored() { try { return localStorage.getItem(TOUR_KEY) === 'yes'; } catch { return false; } }
function tourRemember() { try { localStorage.setItem(TOUR_KEY, 'yes'); } catch {} }
function tourWaitText(text) { $('tourWait').textContent = text; }

// Press a real button and wait until its handler has finished.
async function tourPress(id) {
  const button = $(id);
  for (let i = 0; i < 600 && button.disabled; i++) await new Promise(r => setTimeout(r, 100));
  button.click();
  await tourWaitIdle(id);
}
async function tourVocabulary(id) {
  if (selected?.id === id) return;
  clearTimeout(draftTimer);
  await saveDraft();
  dirty = false;
  if (await choose(examples.find(e => e.id === id))) await newDocument(id);
}
function tourWrite(text) {
  $('prose').value = text;
  $('prose').dispatchEvent(new Event('input', {bubbles: true}));
}
async function tourRules(text) {
  tab('rules');
  if ($('rulesVocabulary').value !== 'handbook') { $('rulesVocabulary').value = 'handbook'; await loadRules('handbook'); }
  if (text !== undefined) { $('rulesText').value = text; $('rulesResult').replaceChildren(); $('askResult').replaceChildren(); }
}
async function tourResetExample() {
  tab('ide');
  await tourVocabulary('handbook');
  tourWrite(TOUR.sentence);
  $('rulesVocabulary').value = 'handbook';
  await loadRules('handbook');
  $('rulesQuestion').value = TOUR.question;
}
async function tourPickFirst() {
  const use = document.querySelector('#recovery .checked-card button');
  if (!use) return;
  use.click();
  const started = Date.now();
  while (!document.querySelector('#recovery .one-reading') && Date.now() - started < 120000) {
    tourWaitText(Date.now() - started > 4000 ? 'Still checking… The server is busy, so this can take a minute.' : 'Checking…');
    await new Promise(r => setTimeout(r, 150));
  }
  tourWaitText('');
}
const tourFirstCard = () => document.querySelector('#recovery .checked-card') || $('recovery');

// Each step: where it points, what it says, what to fill in first, and an
// optional action the reader can do themselves or ask the tour to do.
const tourSteps = [
  {title: 'Welcome to Verifiable English',
   text: ['VE reads English written with the words it knows. It finds every meaning a sentence can have, and accepts it only when there is exactly one.',
          'This tour fills in its own example. It takes about three minutes.',
          'Skip it at any time. Take the tour, at the top right, replays it.']},
  {target: () => document.querySelector('header nav'), title: 'The pages',
   text: ['Writing desk checks one sentence.', 'Rules checks a short policy document and answers questions about it.',
          'Learn and Asimov’s laws are worked examples.']},
  {target: 'exampleSelect', title: 'Pick a vocabulary', tab: 'ide',
   prepare: () => tourVocabulary('handbook'),
   text: ['VE only reads words it has been given.', 'The tour picked Handbook policy.',
          'Its words: employee, Dana (one employee), read the handbook, sign the handbook, new, suspended.']},
  {target: 'prose', title: 'Write one sentence', tab: 'ide',
   prepare: () => tourWrite(TOUR.sentence),
   text: ['The tour wrote this sentence for you.', '“' + TOUR.sentence + '”', 'You can type your own here later.']},
  {target: 'analyse', title: 'Check it', tab: 'ide', press: 'analyse', action: {label: 'Click it for me', run: () => tourPress('analyse')},
   text: ['Click Review meaning.', 'VE reads the sentence and looks for every possible meaning.']},
  {target: 'recovery', title: 'Read the result', tab: 'ide',
   text: ['One reading: VE can read the sentence, and it has exactly one meaning.',
          'Natural English is that meaning, written back by VE. Check that it says what you meant.',
          'Strict VE, Fluent and Logic show the same meaning in exact notations. You can ignore them for now.',
          '“Needs approval” means a person still has to confirm the meaning. That is the next step.']},
  {target: 'approveReading', title: 'Approve the meaning', tab: 'ide',
   press: 'approveReading', action: {label: 'Approve it for me', run: () => tourPress('approveReading')},
   text: ['If the reading says what you meant, click Approve selected meaning.',
          'VE never approves a meaning for you.']},
  {target: 'documentUnits', title: 'Document status', tab: 'ide',
   text: ['This panel lists each sentence and its state.', 'Yours now says: The reading is approved.']},
  {target: 'prose', title: 'Make a mistake on purpose', tab: 'ide',
   prepare: () => tourWrite(TOUR.mistake), press: 'analyse', action: {label: 'Check it for me', run: () => tourPress('analyse')},
   text: ['The tour changed read to print. Print is not a word in this vocabulary.', 'Click Review meaning.']},
  {target: 'recovery', title: 'VE’s English help', tab: 'ide',
   press: 'analyse', action: {label: 'Fix it for me', run: async () => { tourWrite(TOUR.sentence); await tourPress('analyse'); }},
   text: ['VE does not guess. It names the phrase it does not know: “may print the handbook”.',
          'Look at Nearest declared wordings: “may read the handbook” is the closest one. Names such as may_read are internal; skip them.',
          'The buttons are sentences VE can read. Ask assistant, below, asks an AI model for a rephrase; VE still checks it.',
          'To fix it, change print back to read and click Review meaning.']},
  {target: 'recovery', title: 'Fixed', tab: 'ide',
   text: ['One reading again. Small wording changes matter, and VE tells you which ones.']},
  {target: 'prose', title: 'A sentence with two meanings', tab: 'ide',
   prepare: async () => { await tourVocabulary('scope'); tourWrite(TOUR.twoReadings); },
   press: 'analyse', action: {label: 'Check it for me', run: () => tourPress('analyse')},
   text: ['The tour switched to the Server scope vocabulary and wrote this sentence.', '“' + TOUR.twoReadings + '”',
          'Is it one server for everyone, or a server each? Click Review meaning.']},
  {target: tourFirstCard, title: 'Both readings', tab: 'ide',
   press: 'recovery', action: {label: 'Pick the first for me', run: tourPickFirst},
   text: ['VE will not accept this sentence as written, because it has two meanings. The message above the box says it cannot read it as it stands.',
          'The box shows both meanings. Below them is an example: two engineers who each check a different server. There the first meaning is true (satisfied) and the second is false (refuted).',
          'Click Use this wording under the one you mean. VE does not choose for you.']},
  {target: 'recovery', title: 'Now one reading', tab: 'ide',
   text: ['The sentence is now VE’s wording of the meaning you picked. It has one reading, so you could approve it, as before.']},
  {target: 'rulesText', title: 'Write a document', prepare: () => tourRules(HANDBOOK_START),
   text: ['On the Rules page, a document is a numbered list of rules. The tour wrote a handbook policy.',
          'May gives a permission (rule 1). Must gives an obligation (rule 2). Must not forbids. Need not removes an obligation.',
          'An exception overrides the rule it names: rule 3 releases new employees from rule 2. Rule 4 is not marked as an exception yet.']},
  {target: 'checkRules', title: 'Check the document', press: 'checkRules', action: {label: 'Check it for me', run: () => tourPress('checkRules')},
   text: ['Click Check rule conflict.', 'VE reads every rule, then looks for a case where two rules disagree.']},
  {target: 'rulesResult', title: 'A conflict', text: [
    'VE found one: for a suspended employee, rule 1 permits reading and rule 4 forbids it.',
    'Under How VE reads each rule, every rule has One reading.',
    'When no rule applies lists defaults. A default is used only when no rule covers the case. Rule 1 covers every employee, so its may wins over the default must not.']},
  {target: 'rulesText', title: 'Fix the conflict',
   press: 'checkRules', action: {label: 'Fix it for me', run: async () => {
     $('rulesText').value = $('rulesText').value.replace('Rule 4. ', 'Rule 4 (exception to rule 1). ');
     await tourPress('checkRules'); }},
   text: ['Make rule 4 an exception to rule 1: change “Rule 4.” to “Rule 4 (exception to rule 1).”',
          'Then click Check rule conflict.']},
  {target: 'rulesResult', title: 'No conflict', text: [
    'No conflict means VE proved that no case gets two opposite answers.']},
  {target: 'askPanel', title: 'Ask a question', prepare: () => { $('rulesQuestion').value = TOUR.question; },
   press: 'askRules', action: {label: 'Ask it for me', run: () => tourPress('askRules')},
   text: ['VE does not read questions yet. To ask “May a new employee read the handbook?”, write this statement to test.',
          '“' + TOUR.question + '”', 'Then click Ask.']},
  {target: 'askResult', title: 'The answer', text: [
    'VE answers Yes (the statement follows from the rules), No (its opposite follows), or The rules do not say.',
    'Here the rules do not say: it depends on whether the employee is suspended. VE lists each case, and proves each one.']},
  {target: 'tourButton', title: 'You are ready', text: [
    'Take the tour replays this tour. Reset example writes the tour’s sentence and policy back into the page.',
    'Export this document, on the Writing desk, saves your work to a file.',
    'Now try your own sentences.']},
];
const HANDBOOK_START = 'Rule 1. Every employee may read the handbook.\n' +
  'Rule 2. Every employee must sign the handbook.\n' +
  'Rule 3 (exception to rule 2). Every employee need not sign the handbook, if that employee is new.\n' +
  'Rule 4. Every employee must not read the handbook, if that employee is suspended.';

function tourTarget(step) {
  if (!step.target) return null;
  const node = typeof step.target === 'function' ? step.target() : $(step.target);
  return node && node.getClientRects().length ? node : null;
}
function tourPlace() {
  if (tourAt < 0) return;
  const step = tourSteps[tourAt], pop = $('tour'), ring = $('tourRing'), node = tourTarget(step);
  $('tourShade').hidden = Boolean(node);
  ring.hidden = !node;
  const gap = 10, width = Math.min(360, innerWidth - 32);
  pop.style.width = width + 'px';
  if (!node) {
    pop.style.left = Math.max(16, (innerWidth - width) / 2) + 'px';
    pop.style.top = Math.max(16, (innerHeight - pop.offsetHeight) / 2) + 'px';
    return;
  }
  const r = node.getBoundingClientRect();
  Object.assign(ring.style, {left: r.left - 6 + 'px', top: r.top - 6 + 'px', width: r.width + 12 + 'px', height: r.height + 12 + 'px'});
  const h = pop.offsetHeight;
  const left = Math.min(Math.max(16, r.left), innerWidth - width - 16);
  let place = null;
  if (r.bottom + gap + h <= innerHeight - 8) place = [r.bottom + gap, left];
  else if (r.top - gap - h >= 8) place = [r.top - gap - h, left];
  else if (r.right + gap + width <= innerWidth - 16) place = [Math.max(8, Math.min(r.top, innerHeight - h - 8)), r.right + gap];
  else if (r.left - gap - width >= 16) place = [Math.max(8, Math.min(r.top, innerHeight - h - 8)), r.left - gap - width];
  else place = [Math.max(8, innerHeight - h - 8), left];
  pop.style.top = place[0] + 'px';
  pop.style.left = place[1] + 'px';
}
async function tourShow(index) {
  if (index < 0 || index >= tourSteps.length) return tourEnd();
  tourAt = index;
  const step = tourSteps[index];
  tourBusy = true; tourButtons();
  try {
    if (step.tab) tab(step.tab);
    else if (['rulesText','checkRules','rulesResult','askPanel','askResult'].includes(step.target)) tab('rules');
    if (step.prepare) { tourWaitText('Preparing the example…'); await step.prepare(); tourWaitText(''); }
  } catch (e) { tourWaitText(e.message); }
  tourBusy = false;
  step.done = false;
  $('tourCount').textContent = `STEP ${index + 1} OF ${tourSteps.length}`;
  $('tourTitle').textContent = step.title;
  $('tourText').replaceChildren(...step.text.map(line => el('p', line)));
  $('tour').hidden = false;
  tourButtons();
  const node = tourTarget(step);
  if (node) node.scrollIntoView({block: node.offsetHeight > innerHeight * 0.6 ? 'start' : 'center', behavior: 'instant'});
  tourPlace();
  $('tourNext').focus();
}
function tourButtons() {
  const step = tourSteps[tourAt] || {};
  $('tourBack').disabled = tourBusy || tourAt <= 0;
  $('tourNext').disabled = tourBusy;
  $('tourNext').textContent = step.action && !step.done ? step.action.label
    : tourAt === tourSteps.length - 1 ? 'Finish' : 'Next';
}
async function tourAct() {
  const step = tourSteps[tourAt];
  if (!step?.action || tourBusy) return;
  tourBusy = true; tourButtons();
  try { await step.action.run(); step.done = true; }
  catch (e) { tourWaitText(e.message); }
  tourBusy = false;
  await tourShow(tourAt + 1);
}
async function tourNextStep() {
  if (tourBusy) return;
  const step = tourSteps[tourAt];
  // On an action step the main button does the action, so later steps have its result.
  if (step?.action && !step.done) return tourAct();
  await tourShow(tourAt + 1);
}
// A reader who presses the real control has done the step themselves.
document.addEventListener('click', e => {
  const step = tourSteps[tourAt];
  if (tourAt >= 0 && step?.press && e.target.closest?.('#' + step.press) && e.target.closest('button')) {
    step.done = true;
    setTimeout(async () => { await tourWaitIdle(step.press); tourButtons(); tourPlace(); }, 0);
  }
  setTimeout(tourPlace, 0);
}, true);
async function tourWaitIdle(id) {
  await new Promise(r => setTimeout(r, 50));
  const started = Date.now();
  while ($(id).disabled && Date.now() - started < 120000) {
    tourWaitText(Date.now() - started > 4000 ? 'Still checking… The server is busy, so this can take a minute.' : 'Checking…');
    await new Promise(r => setTimeout(r, 150));
  }
  tourWaitText('');
}
function tourEnd() {
  tourAt = -1; tourRemember();
  $('tour').hidden = true; $('tourRing').hidden = true; $('tourShade').hidden = true;
  $('tourButton').focus();
}
function tourStart() { tourShow(0); }
function tourAfterSignIn() { if (!tourStored() && tourAt < 0) tourStart(); }

$('tourButton').onclick = tourStart;
$('tourNext').onclick = tourNextStep;
$('tourBack').onclick = () => { if (!tourBusy) tourShow(tourAt - 1); };
$('tourSkip').onclick = tourEnd;
$('tourReset').onclick = async () => {
  if (tourBusy) return;
  tourBusy = true; tourButtons(); tourWaitText('Resetting the example…');
  try { await tourResetExample(); tourWaitText('The example is back. Start again from step 3.'); }
  catch (e) { tourWaitText(e.message); }
  tourBusy = false; tourButtons();
};
addEventListener('resize', tourPlace);
addEventListener('scroll', tourPlace, true);
document.addEventListener('keydown', e => {
  if (tourAt < 0) return;
  if (e.key === 'Escape') { e.preventDefault(); tourEnd(); return; }
  const typing = /^(TEXTAREA|INPUT|SELECT)$/.test(document.activeElement?.tagName || '');
  if (typing) return;
  if (e.key === 'ArrowRight' || (e.key === 'Enter' && document.activeElement === document.body)) { e.preventDefault(); tourNextStep(); }
  else if (e.key === 'ArrowLeft') { e.preventDefault(); if (!tourBusy && tourAt > 0) tourShow(tourAt - 1); }
});
