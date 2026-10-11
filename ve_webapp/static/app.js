'use strict';
const $ = id => document.getElementById(id);
let csrf = '', examples = [], selected, assist = false, revision = 0, validationTimer, lessonRevision = 0, dirty = false;
let activeDraft = null, draftTimer, draftQueue = Promise.resolve();
const el = (tag, text, className) => { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (className) n.className = className; return n; };
function notify(text) { $('notice').textContent = text; setTimeout(() => { $('notice').textContent = ''; }, 5000); }
async function api(path, body, login = false) {
  const response = await fetch('/api/' + path, {method: body === undefined ? 'GET' : 'POST', headers: body === undefined ? {} : {'Content-Type':'application/json','X-VE-CSRF':login ? 'login' : csrf}, body:body === undefined ? undefined : JSON.stringify(body)});
  const data = await response.json();
  if (!response.ok) {
    if (response.status === 401 && !login) signedOut();
    const err = data.error;
    throw new Error(err ? `${err.code || 'Invalid request'}: ${err.message}${err.span ? ` (line ${err.span.line}, column ${err.span.column})` : ''}` : data.detail || 'The request is rejected.');
  }
  return data;
}
async function task(button, fn) { button.disabled = true; try { await fn(); } catch (e) { notify(e.message); } finally { button.disabled = false; } }
function signedOut() { csrf = ''; dirty=false; $('workspace').hidden = true; $('login').hidden = false; $('logout').hidden = true; $('token').value = ''; }
async function signedIn(data) {
  csrf = data.csrf; assist = data.assist;
  examples = await api('examples');
  $('workspace').hidden = false; $('login').hidden = true; $('logout').hidden = false;
  $('assistStatus').textContent = assist ? `${data.model} · one paid call per request` : 'The assistant is disabled. The checker is available.';
  $('propose').disabled = !assist;
  $('gallery').replaceChildren(); $('exampleSelect').replaceChildren();
  for (const item of examples) {
    const button = el('button'); button.append(el('small',item.category),el('strong',item.title));
    button.onclick = () => choose(item); button.dataset.example = item.id; $('gallery').append(button);
    const option = el('option',item.title); option.value = item.id; $('exampleSelect').append(option);
  }
  await choose(examples[0]);
  const saved = await api('drafts');
  activeDraft = saved[0] || await api('drafts',{example:selected.id});
  selected = examples.find(e=>e.id===activeDraft.example) || selected;
  if(selected.id!==examples[0].id)await choose(selected);
  $('exampleSelect').value=selected.id;
  renderDraft(activeDraft,true);
  await loadRules($('rulesVocabulary').value);
  try { renderAsimov(await api('asimov')); } catch(e) { notify(e.message); }
  tab('ide');
  if(typeof tourAfterSignIn==='function')tourAfterSignIn();
}
function tab(name) {
  for(const id of ['learn','ide','rules','asimov']){
    $(id).hidden = name !== id; $(id+'Nav').classList.toggle('active',name === id);
    $(id+'Nav').setAttribute('aria-current',name === id ? 'page' : 'false');
  }
}
const verdictNames={required:'Required',permitted:'Permitted',forbidden:'Forbidden','ruled out':'Ruled out','no clear action':'No clear action'};
function verdictBadge(verdict){ return el('span',verdictNames[verdict] || 'Unknown','badge asimov-badge asimov-'+verdict.replaceAll(' ','-')); }
let asimovGroups={},asimovScenarios=[];const asimovCards=new Map();
// Cards sit in the section and under the law VE returned; a re-run places its card again.
function layoutAsimov() {
  for(const [group,target] of [['approves','asimovApproves'],['rejects','asimovRejects'],['limits','asimovLimits']]){
    $(target).replaceChildren();
    for(const law of Object.keys(asimovGroups)){
      const cards=asimovScenarios.filter(s=>s.group===group&&s.law===law);
      if(!cards.length)continue;
      if(group!=='limits')$(target).append(el('h3',asimovGroups[law],'asimov-law'));
      $(target).append(...cards.map(s=>asimovCards.get(s.id)));
    }
  }
}
function scenarioCard(s, live=false) {
  const card=el('article',undefined,'asimov-card');
  card.append(el('small',asimovGroups[s.law],'eyebrow'),el('h3',s.title),el('p',s.situation));
  const focus=s.options.find(o=>o.id===s.focus);
  const line=el('div',undefined,'asimov-verdict');line.append(el('strong',focus.label),verdictBadge(s.verdict));
  card.append(line,el('p',s.why,'asimov-why'));
  if(s.limit)card.append(el('p',s.limit,'note asimov-limit'));
  const list=el('ul',undefined,'asimov-options');
  for(const robot of s.robots){
    if(s.robots.length>1){list.append(el('li',robot.label,'asimov-robot'));if(robot.diagnosis)list.append(el('li',robot.diagnosis,'note'));}
    for(const o of s.options.filter(o=>o.robot===robot.id)){
      const item=el('li'),head=el('div',undefined,'asimov-option');head.append(el('span',o.label),verdictBadge(o.verdict));
      item.append(head,el('small',o.why));
      if(o.consequences.length)item.append(el('small','If chosen: '+o.consequences.join(' '),'asimov-outcome'));
      list.append(item);
    }
  }
  card.append(list);
  if(s.facts.length){
    const edit=el('details',undefined,'asimov-edit');edit.append(el('summary','Change the facts'));
    const boxes=s.facts.map(f=>{const label=el('label',undefined,'inline'),input=el('input');input.type='checkbox';input.checked=f.value;input.dataset.fact=f.id;label.append(input,el('span',f.label));edit.append(label);return input;});
    const again=el('button','Ask VE again');
    again.onclick=()=>task(again,async()=>{
      const next=await api('asimov',{scenario:s.id,facts:Object.fromEntries(boxes.map(b=>[b.dataset.fact,b.checked]))});
      const fresh=scenarioCard(next,true);fresh.querySelector('.asimov-edit').open=true;
      asimovScenarios=asimovScenarios.map(x=>x.id===next.id?next:x);asimovCards.set(next.id,fresh);
      layoutAsimov();fresh.querySelector('.asimov-edit button').focus();
    });
    edit.append(again);card.append(edit);
  }
  card.append(el('small',live?'VE decided this again just now, with your facts.':'VE decided this when the page was built.','note asimov-source'));
  return card;
}
function renderAsimov(page) {
  asimovGroups=page.groups;
  $('asimovQuotes').replaceChildren(...page.quotes.map(q=>{const box=el('figure',undefined,'asimov-quote');box.append(el('figcaption',q.law,'eyebrow'),el('blockquote',q.text),el('small',q.source));return box;}));
  $('asimovDocument').textContent=page.document.verdict==='CONFLICT-FREE'?'Conflict-free':'Conflict check unresolved';
  $('asimovRules').replaceChildren(...page.rules.map(rule=>{
    const item=el('li'),head=el('div',undefined,'asimov-rule-head');
    head.append(el('strong',`Rule ${rule.number}`),el('span',rule.law,'badge model'),el('span',rule.status==='checked'?'Checked':'Not checked','badge'));
    if(rule.precedence)head.append(el('small',rule.precedence));
    item.append(head,el('p',rule.text));return item;
  }));
  asimovScenarios=page.scenarios;asimovCards.clear();
  for(const s of asimovScenarios)asimovCards.set(s.id,scenarioCard(s));
  layoutAsimov();
  $('asimovLimitNote').textContent=page.limits.note;$('asimovFactsNote').textContent=page.limits.facts;
  $('asimovOpen').replaceChildren(...page.limits.open.map(text=>el('li',text)));
}
function view(title, text, prose = false) { const box=el('div',undefined,'view'); box.append(el('h3',title),el(prose?'p':'pre',text)); return box; }
function naturalView(natural) {
  const box=el('div',undefined,'view natural-view');box.append(el('h3','Natural English'));
  for(const sentence of natural.sentences){
    const line=el('p',sentence.form==='explicit form'
      ? 'The reading is not available. The view shows the logic.'
      : sentence.text+'.','reader-sentence');
    if(sentence.form==='explicit form')line.append(el('span','explicit form','badge explicit-badge'));
    box.append(line);
  }
  return box;
}
function readingTabs(data) {
  const group=el('div',undefined,'reading-group'),tabs=el('div',undefined,'reading-tabs');
  const panels=[['Natural English',naturalView(data.natural)],['Strict VE',view('Strict VE',data.views.ve_strict)],['Fluent',view('Fluent',data.views.ve_fluent)],['Logic',view('Logic',data.views.fol_symbols)]];
  for(const [index,[title,panel]] of panels.entries()){
    const button=el('button',title);button.type='button';button.setAttribute('aria-pressed',String(index===0));
    button.classList.toggle('active',index===0);panel.hidden=index!==0;
    button.onclick=()=>{for(const [i,[,p]] of panels.entries()){p.hidden=i!==index;tabs.children[i].classList.toggle('active',i===index);tabs.children[i].setAttribute('aria-pressed',String(i===index));}};
    tabs.append(button);
  }
  group.append(tabs,...panels.map(([,panel])=>panel));return group;
}
async function choose(item) {
  if(dirty && !confirm("Your latest words are still saving. Change example now?")) { $('exampleSelect').value=selected.id; return false; }
  dirty=false; selected = item; revision++; const version=++lessonRevision;$('runLesson').disabled=true;
  $('exampleSelect').value = item.id;
  document.querySelectorAll('[data-example]').forEach(b=>{b.classList.toggle('selected',b.dataset.example===item.id);b.setAttribute('aria-pressed',String(b.dataset.example===item.id));});
  $('lessonCategory').textContent=item.category; $('lessonTitle').textContent=item.title; $('lessonNote').textContent=item.note;
  $('lessonResult').replaceChildren(); $('lessonViews').replaceChildren(view('Source English',item.english,true));
  $('claim').value=item.claim; $('premises').value=item.premises; $('prose').value=''; $('environment').value=JSON.stringify(item.environment,null,2); $('world').value=JSON.stringify(item.world,null,2); $('useWorld').checked=true;
  $('candidates').replaceChildren(); $('checkResult').replaceChildren(el('div','The result is pending.','empty')); $('validation').replaceChildren();
  $('provenance').textContent='The example is untrusted. The reading needs approval.';
  try {
    const d=await api('validate',{example:item.id,text:item.premises+'\n'+item.claim});
    if(version!==lessonRevision)return;
    $('lessonViews').append(readingTabs(d));
  } catch(e) { notify(e.message); }
  await validate();
  if(version===lessonRevision)$('runLesson').disabled=false;
  return true;
}
function payload(includeWorld=false) {
  let environment, world;
  try { environment=JSON.parse($('environment').value); if(includeWorld && $('useWorld').checked) world=JSON.parse($('world').value); }
  catch { throw new Error('Vocabulary or world JSON is invalid. Open “Vocabulary & small world” to fix it.'); }
  return {example:selected.id,text:$('claim').value,premises:$('premises').value,environment,...(world?{world}: {})};
}
function detail(parent,title,value) { const d=el('details');d.append(el('summary',title),el('pre',typeof value==='string'?value:JSON.stringify(value,null,2),'result-detail'));parent.append(d); }
function worldView(parent, world, summary) {
  const wrap=el('div'); wrap.append(el('h3','A possible world'));
  for(const sentence of summary || [])wrap.append(el('p',sentence,'note'));
  detail(wrap,'Exact world & name mapping',world);parent.append(wrap);
}
function verdict(target, data) {
  target.replaceChildren();
  const titles={certified:'The consequence is certified.',countermodel:'The counterexample is present.',unknown:'The result is unresolved.'};
  const box=el('div',undefined,'verdict '+data.status);
  box.append(el('h3',titles[data.status]),el('p',data.status==='certified'?'The proof is replayed. The conclusion follows the assumptions.':data.detail));target.append(box);
  if(data.evaluation) target.append(el('p',(data.evaluation.value===null?'The result is unresolved.':
    data.evaluation.value?'The conclusion is satisfied.':'The conclusion is refuted.')+
    ' The world is checked. The proof is separate.','note'));
  if(data.countermodel) worldView(target,data.countermodel,data.countermodel_summary);
  if(data.certificate) detail(target,'Inspect proof certificate & replay',{replay:data.replay,certificate:data.certificate});
  target.append(el('p',data.assurance,'note'));detail(target,'Exact meaning identity',data.meaning_id);
}
async function validate() {
  const v=revision;
  try { const data=await api('validate',payload()); if(v!==revision)return; $('validation').replaceChildren(el('p','The reading is checked. The proof is not checked.','badge'),readingTabs(data)); }
  catch(e) { if(v===revision)$('validation').replaceChildren(el('p',e.message,'error')); }
}
async function check() {
  const v=revision; $('checkResult').replaceChildren(el('p','The checker checks the proof.','note'));
  try { const data=await api('check',payload(true));if(v===revision)verdict($('checkResult'),data); }
  catch(e) {if(v===revision)$('checkResult').replaceChildren(el('p',e.message,'error'));}
}
$('loginForm').onsubmit=e=>{e.preventDefault();task(e.submitter,async()=>{try{await signedIn(await api('login',{token:$('token').value},true));$('token').value='';}catch(err){$('loginError').textContent=err.message;}});};
$('logout').onclick=()=>task($('logout'),async()=>{await api('logout',{});signedOut();});
$('learnNav').onclick=()=>tab('learn');$('ideNav').onclick=()=>tab('ide');$('rulesNav').onclick=()=>tab('rules');$('asimovNav').onclick=()=>tab('asimov');$('openExample').onclick=async()=>{tab('ide');await newDocument(selected.id);};
$('exampleSelect').onchange=async()=>{const item=examples.find(e=>e.id===$('exampleSelect').value);try{await saveDraft();if(await choose(item))await newDocument(item.id);}catch(e){notify(e.message);$('exampleSelect').value=selected.id;}};
$('runLesson').onclick=()=>task($('runLesson'),async()=>{const v=lessonRevision;const d=await api('check',{example:selected.id});if(v===lessonRevision)verdict($('lessonResult'),d);});
$('validate').onclick=()=>task($('validate'),validate);$('check').onclick=()=>task($('check'),check);
for(const id of ['claim','premises','environment','world','useWorld']) $(id).addEventListener('input',()=>{
  dirty=true;revision++;$('checkResult').replaceChildren(el('div','The result is not current. The checker needs the document.','empty'));$('validation').replaceChildren();
  if(id==='environment')$('candidates').replaceChildren();
  if(id==='claim'){$('provenance').textContent='The document is current. The paraphrase needs approval.';clearTimeout(validationTimer);validationTimer=setTimeout(validate,650);}
});
$('prose').addEventListener('input',()=>{dirty=true;$('candidates').replaceChildren();});
window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue='';}});
$('propose').onclick=()=>task($('propose'),async()=>{
  const v=revision, source=$('prose').value;const body=payload();body.text=source;delete body.premises;
  $('candidates').replaceChildren(el('p','The assistant is working. The candidate is untrusted.','note'));
  try {
    const response=await api('propose',body);if(v!==revision || source!==$('prose').value)return;
    const data=response; $('candidates').replaceChildren();
    if(!data.candidates.length)$('candidates').append(el('p','The candidate is not available. The sentence needs the vocabulary.','note'));
    for(const c of data.candidates){
      const box=el('article',undefined,'candidate');box.append(el('span','MODEL PROPOSAL · UNTRUSTED','badge model'));
      if(c.natural)box.append(naturalView(c.natural));
      else box.append(el('p','The reading is not available.','note'));
      const advanced=el('details');advanced.append(el('summary','Strict VE and model gloss'),el('code',c.text));
      if(c.reading)advanced.append(el('p',c.reading,'note'));
      box.append(advanced);
      const accept=el('button','Accept this reading');accept.onclick=()=>{dirty=true;revision++;$('claim').value=c.text;$('provenance').textContent='Model proposal accepted by you for this draft. Fidelity is your responsibility; checking is separate.';$('checkResult').replaceChildren(el('div','The reading is approved. The consequence needs checking.','empty'));validate();$('strictEditor').open=true;$('claim').focus();};box.append(accept);$('candidates').append(box);
    }
    for(const comparison of data.comparisons){
      const box=el('div',undefined,'view');box.append(el('h3','Alternative readings'));
      box.append(el('p',comparison.relation.replaceAll('_',' '),'note'));
      for(const model of comparison.distinguishing_models || [])for(const sentence of model.reader_summary || [])box.append(el('p',sentence,'note'));
      detail(box,'Exact comparison and checked worlds',comparison);$('candidates').append(box);
    }
    $('candidates').append(el('p','Readings considered so far, not an exhaustive list. Acceptance applies to this local draft; it is not an audited assist-session sign-off.','note'));
  }catch(e){$('candidates').replaceChildren(el('p',e.message,'error'));}
});
$('export').onclick=()=>task($('export'),async()=>{await saveDraft();const data=await api(`drafts/${activeDraft.id}/export`);const a=el('a');const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));a.href=url;a.download='ve-document.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
$('importFile').onchange=async e=>{const file=e.target.files[0];if(!file)return;try{if(file.size>32000)throw new Error('This import exceeds the 32 KiB limit.');const data=JSON.parse(await file.text());renderDraft(await api('drafts/import',data),true);tab('ide');}catch(err){notify(err.message);}finally{e.target.value='';}};
document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key==='Enter'&&!$('ide').hidden&&!$('workspace').hidden){e.preventDefault();if(!$('check').disabled)task($('check'),check);}});
let theme;try{theme=localStorage.getItem('ve-theme');}catch{}document.documentElement.dataset.theme=theme||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');
$('theme').onclick=()=>{const t=document.documentElement.dataset.theme==='dark'?'light':'dark';document.documentElement.dataset.theme=t;try{localStorage.setItem('ve-theme',t);}catch{}};
api('session').then(signedIn).catch(()=>signedOut());

const documentStates={
  draft:'The draft is available.', analysing:'The reading is pending.',
  needs_word:'The reading is unresolved.', needs_repair:'The reading is unresolved.',
  reading_review:'The reading needs approval.', ready:'The reading is ready.',
  approved:'The reading is approved.', unresolved:'The reading is unresolved.',
  exhausted:'The budget is exhausted.', stale:'The result is not current.'
};
function stateSentence(state) { return documentStates[state] || 'The result is unresolved.'; }
function renderDraft(doc, overwrite=false) {
  activeDraft=doc;
  const unit=doc.units[0];
  if(overwrite)$('prose').value=unit?.source || '';
  $('documentMode').disabled=Boolean(unit);
  if(unit)$('documentMode').value=unit.mode;
  $('documentRevision').replaceChildren(el('span','The document is saved.'),el('span',` Revision ${doc.revision}`));
  $('documentStatus').textContent=unit ? stateSentence(unit.state) : 'The draft is empty.';
  $('documentUnits').replaceChildren();
  if(!doc.document_units.length)$('documentUnits').append(el('p','The statement is not available.','note'));
  for(const item of doc.document_units){
    const row=el('div',undefined,'document-unit');
    row.append(el('span',item.source),el('strong',stateSentence(item.status)));
    if(item.reason)row.append(el('p',item.reason,'note'));
    $('documentUnits').append(row);
  }
  $('recovery').replaceChildren();
  $('wordSort').replaceChildren();
  for(const sort of Object.keys(doc.environment.vocabulary.sorts)) {
    const opt=el('option',sort.replaceAll('_',' '));opt.value=sort;$('wordSort').append(opt);
  }
  if(!unit){$('recovery').append(el('p','The document accepts the sentence. The reading needs approval.','note'));return;}
  if(unit.reason)$('recovery').append(el('p',unit.reason,'error'));
  if(unit.word_prompt){
    const p=unit.word_prompt;
    $('recovery').append(el('h3','Word help'),el('p',`Check “${p.term}”. ${p.expected_construction}`,'note'));
    if(p.nearest_registered_wordings.length)$('recovery').append(el('p',`Nearby declared words: ${p.nearest_registered_wordings.join(', ')}. These are suggestions, not replacements.`,'note'));
    if(unit.templates?.length){
      $('recovery').append(el('p','The app shows the example.','note'));
      for(const template of unit.templates){const button=el('button',template);button.onclick=()=>{$('prose').value=template;$('prose').dispatchEvent(new Event('input',{bubbles:true}));};$('recovery').append(button);}
    }
  }
  if(unit.pending.length)for(const pending of unit.pending)$('recovery').append(el('p',pending.reason || 'The reading is unresolved.','note'));
  if(unit.reading_view){
    const box=el('article',undefined,'candidate one-reading');
    box.append(el('h3',unit.reading_view.sentences===1?'One reading':'Readings'),readingTabs(unit.reading_view));
    $('recovery').append(box);
  }
  if(unit.state==='ready')$('recovery').append(el('p','The reading is ready. The reading needs approval.','note'));
  if(unit.state==='approved')$('recovery').append(el('p',`Meaning approved at this revision. ${unit.paraphrase || ''}`,'note'));
  if(unit.state==='unresolved')$('recovery').append(el('p','The statement is unresolved. The statement is visible.','note'));
  if(unit.mode==='translation' && (unit.readings.length>1 || unit.cards?.length))
    $('recovery').append(el('p','Source alternatives stay together. A cited narrowing has not been reviewed here, so this unit cannot be approved as one reading.','note'));
  for(const card of unit.cards || []){
    const box=el('article',undefined,'candidate checked-card');
    box.append(el('h3','Two checked readings'),el('p','This example situation makes one reading true and the other false.','note'));
    for(let i=0;i<card.paraphrases.length;i++){
      const row=el('div',undefined,'card-reading');row.append(el('p',card.paraphrases[i]));
      row.append(el('p',card.values[i]?'The reading is satisfied.':'The reading is refuted.','badge'));
      if(unit.mode==='authoring'){
        const use=el('button','Use this wording');use.onclick=()=>task(use,async()=>{
          await changeDraft('reply',{text:card.paraphrases[i],rejected:card.meaning_ids.filter((_,j)=>j!==i).map(meaning_id=>({meaning_id,reason:'The candidate is rejected.'}))});
          await changeDraft('analyze',{});
        });row.append(use);
      }
      box.append(row);
    }
    for(const line of card.situation_text)box.append(el('p',line,'note'));
    $('recovery').append(box);
  }
  for(const suggestion of unit.suggestions || []){
    const box=el('article',undefined,'candidate');box.append(el('h3','Assistant suggestion · untrusted'),el('p',suggestion));
    const use=el('button','Use this restatement');use.onclick=()=>task(use,async()=>{await changeDraft('reply',{text:suggestion});await changeDraft('analyze',{});});
    box.append(use);$('recovery').append(box);
  }
  $('approveReading').disabled=unit.state!=='ready';
}
async function changeDraft(action,args) {
  const operation=async()=>{
    if(!activeDraft)throw new Error('The document is not available.');
    const before=activeDraft;
    try {
      const next=await api(`drafts/${before.id}/commands`,{revision:before.revision,request_id:crypto.randomUUID(),action,args});
      const sameText=$('prose').value===args.source;
      renderDraft(next,action!=='save' || sameText);
      if(action==='save'&&sameText)dirty=false;
      return next;
    } catch(e) {
      if(e.message.includes('another tab'))renderDraft(await api(`drafts/${before.id}`),true);
      throw e;
    }
  };
  const pending=draftQueue.then(operation);
  draftQueue=pending.catch(()=>{});
  return pending;
}
async function saveDraft() {
  if(!activeDraft || !$('prose').value.trim())return;
  if(activeDraft.units[0]?.source===$('prose').value)return;
  await changeDraft('save',{source:$('prose').value,mode:$('documentMode').value});
}
async function newDocument(example=selected.id) {
  await saveDraft();
  clearTimeout(draftTimer);
  await draftQueue;
  activeDraft=await api('drafts',{example});
  $('documentMode').value='authoring';
  renderDraft(activeDraft,true);
  $('recovery').replaceChildren(el('p','The document accepts the sentence.','note'));
  dirty=false;
}
$('newDocument').onclick=()=>task($('newDocument'),()=>newDocument());
$('prose').addEventListener('input',()=>{
  dirty=true;clearTimeout(draftTimer);
  draftTimer=setTimeout(()=>saveDraft().catch(e=>notify(e.message)),700);
  $('documentStatus').textContent='The document is pending.';
});
$('analyse').onclick=()=>task($('analyse'),async()=>{clearTimeout(draftTimer);$('recovery').replaceChildren(el('p','Checking…','note checking'));await saveDraft();await changeDraft('analyze',{});});
$('approveReading').onclick=()=>task($('approveReading'),async()=>{
  await saveDraft();const unit=activeDraft.units[0];await changeDraft('approve',{wording:unit.source.trim()});
});
$('noneReading').onclick=()=>task($('noneReading'),async()=>{
  const text=prompt('None of these means what you intended. Restate the sentence or give an example.');
  if(!text)return;
  const unit=activeDraft.units[0];const rejected=Object.values(unit.catalogue_results).flatMap(r=>r.candidates || []).map(r=>({meaning_id:r.meaning_id,reason:'The candidate is rejected.'}));
  await changeDraft('reply',{text,rejected});await changeDraft('analyze',{});
});
$('askRepair').onclick=()=>task($('askRepair'),async()=>{
  clearTimeout(draftTimer);await saveDraft();
  await draftQueue;
  const doc=activeDraft;
  const result=await api(`drafts/${doc.id}/assist`,{revision:doc.revision,request_id:crypto.randomUUID().replaceAll('-','')});
  if(result.status==='stale'){renderDraft(await api(`drafts/${doc.id}`),true);notify(result.reason);return;}
  renderDraft(result,false);
});
$('cancelReview').onclick=()=>task($('cancelReview'),()=>changeDraft('cancel',{}));
$('undoReview').onclick=()=>task($('undoReview'),async()=>{
  const target=activeDraft.undo_target;
  if(target==null)throw new Error('The revision is not available.');
  await changeDraft('undo',{target_revision:target});
});
$('unresolvedReading').onclick=()=>task($('unresolvedReading'),async()=>{
  const reason=prompt('The sentence is unresolved.');if(reason)await changeDraft('unresolved',{reason});
});
$('defineWord').onclick=()=>task($('defineWord'),async()=>{
  const word=$('newWord').value.trim().toLowerCase(),kind=$('wordKind').value,sort=$('wordSort').value;
  const args={word,kind,positive_example:$('wordExample').value.trim(),negative_example:$('wordNegative').value.trim(),
    direction:$('wordDirection').value,sorts:kind==='relation'?[sort,sort]:kind==='property'?[sort]:[]};
  if(!confirm('The word needs approval. The reading needs review.'))return;
  await changeDraft('define',args);$('glossaryStatus').textContent='The word is known. The sentence needs approval.';
});
$('confirmGlossary').onclick=()=>task($('confirmGlossary'),async()=>{
  const sentence=$('glossarySentence').value.trim();
  if(!confirm('The synonym needs approval.\n'+sentence))return;
  await changeDraft('glossary',{sentence});$('glossaryStatus').textContent='The synonym is approved. The sentence needs approval.';
});
function rulesResult(result) {
  const box=el('div',undefined,'verdict '+(result.status==='clear'?'certified':'countermodel'));
  box.append(el('h3',result.status==='clear'?'No conflict':result.status==='conflict'?'Conflict found':'Not decided'),el('p',result.explanation));
  const list=el('ol',undefined,'rule-readings');
  for(const text of result.readings || []){const item=el('li');item.append(el('span',text),el('span','One reading','badge'));list.append(item);}
  const parts=[box];
  if(list.children.length)parts.push(el('h3','How VE reads each rule'),list);
  if(result.defaults?.length){parts.push(el('h3','When no rule applies'));for(const text of result.defaults)parts.push(el('p',text,'note'));}
  $('rulesResult').replaceChildren(...parts);
}
async function loadRules(vocabulary) {
  const rules=await api('rules?vocabulary='+encodeURIComponent(vocabulary));
  $('rulesText').value=rules.text;rulesResult(rules.result);$('askResult').replaceChildren();
}
async function checkRules() {
  $('rulesResult').replaceChildren(el('p','Checking…','note checking'));
  try{rulesResult(await api('rules',{text:$('rulesText').value,vocabulary:$('rulesVocabulary').value}));}
  catch(e){$('rulesResult').replaceChildren(el('p',e.message,'error'));}
}
async function askRules() {
  $('askResult').replaceChildren(el('p','Checking…','note checking'));
  try{
    const r=await api('rules/ask',{text:$('rulesText').value,vocabulary:$('rulesVocabulary').value,question:$('rulesQuestion').value});
    const names={yes:'Yes','no':'No','not settled':'The rules do not say'};
    const box=el('div',undefined,'verdict '+(r.answer==='not settled'?'unknown':'certified'));
    box.append(el('h3',names[r.answer]),el('p',r.explanation),el('p','VE read the statement as: '+r.reading+'.','note'));
    const parts=[box];
    if(r.cases.length){const list=el('ul',undefined,'ask-cases');for(const c of r.cases){const item=el('li');item.append(el('strong',c.answer==='yes'?'Yes':'No'),el('span',' · '+c.when+'.'));list.append(item);}parts.push(el('h3','It depends on the case'),list);}
    $('askResult').replaceChildren(...parts);
  }catch(e){$('askResult').replaceChildren(el('p',e.message,'error'));}
}
$('checkRules').onclick=()=>task($('checkRules'),checkRules);
$('askRules').onclick=()=>task($('askRules'),askRules);
$('rulesQuestion').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();if(!$('askRules').disabled)task($('askRules'),askRules);}});
$('rulesVocabulary').onchange=()=>task($('rulesVocabulary'),()=>loadRules($('rulesVocabulary').value));
