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
    throw new Error(err ? `${err.code || 'Invalid input'}: ${err.message}${err.span ? ` (line ${err.span.line}, column ${err.span.column})` : ''}` : data.detail || 'Request failed.');
  }
  return data;
}
async function task(button, fn) { button.disabled = true; try { await fn(); } catch (e) { notify(e.message); } finally { button.disabled = false; } }
function signedOut() { csrf = ''; dirty=false; $('workspace').hidden = true; $('login').hidden = false; $('logout').hidden = true; $('token').value = ''; }
async function signedIn(data) {
  csrf = data.csrf; assist = data.assist;
  examples = await api('examples');
  $('workspace').hidden = false; $('login').hidden = true; $('logout').hidden = false;
  $('assistStatus').textContent = assist ? `${data.model} · one paid call per request` : 'Live assistance disabled · local checking available';
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
  const rules=await api('rules');$('rulesText').value=rules.text;$('rulesResult').replaceChildren(el('p',rules.result.explanation));
  tab('ide');
}
function tab(name) {
  $('learn').hidden = name !== 'learn'; $('ide').hidden = name !== 'ide'; $('rules').hidden = name !== 'rules';
  $('learnNav').classList.toggle('active',name === 'learn'); $('ideNav').classList.toggle('active',name === 'ide');
  $('rulesNav').classList.toggle('active',name === 'rules');
  $('learnNav').setAttribute('aria-current',name === 'learn' ? 'page' : 'false');
  $('ideNav').setAttribute('aria-current',name === 'ide' ? 'page' : 'false');
  $('rulesNav').setAttribute('aria-current',name === 'rules' ? 'page' : 'false');
}
function view(title, text, prose = false) { const box=el('div',undefined,'view'); box.append(el('h3',title),el(prose?'p':'pre',text)); return box; }
function naturalView(natural) {
  const box=el('div',undefined,'view natural-view');box.append(el('h3','Natural English'));
  for(const sentence of natural.sentences){
    const line=el('p',sentence.text+'.','reader-sentence');
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
  $('candidates').replaceChildren(); $('checkResult').replaceChildren(el('div','Your verdict will appear here.','empty')); $('validation').replaceChildren();
  $('provenance').textContent='Example supplied by the app. Review its meaning before using it.';
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
  const titles={certified:'✓ Certified consequence',countermodel:'↗ A countermodel exists',unknown:'? Unknown within budget'};
  const box=el('div',undefined,'verdict '+data.status);
  box.append(el('h3',titles[data.status]),el('p',data.status==='certified'?'The Python checker replayed a proof of this exact conclusion from these assumptions.':data.detail));target.append(box);
  if(data.evaluation) target.append(el('p',`Small-world evaluation: ${data.evaluation.value===null?'unknown':data.evaluation.value?'true':'false'}. This is one world, not a proof of entailment.`,'note'));
  if(data.countermodel) worldView(target,data.countermodel,data.countermodel_summary);
  if(data.certificate) detail(target,'Inspect proof certificate & replay',{replay:data.replay,certificate:data.certificate});
  target.append(el('p',data.assurance,'note'));detail(target,'Exact meaning identity',data.meaning_id);
}
async function validate() {
  const v=revision;
  try { const data=await api('validate',payload()); if(v!==revision)return; $('validation').replaceChildren(el('p','✓ Parsed and type-checked · no proof checked yet','badge'),readingTabs(data)); }
  catch(e) { if(v===revision)$('validation').replaceChildren(el('p',e.message,'error')); }
}
async function check() {
  const v=revision; $('checkResult').replaceChildren(el('p','Checking proof and countermodel budgets…','note'));
  try { const data=await api('check',payload(true));if(v===revision)verdict($('checkResult'),data); }
  catch(e) {if(v===revision)$('checkResult').replaceChildren(el('p',e.message,'error'));}
}
$('loginForm').onsubmit=e=>{e.preventDefault();task(e.submitter,async()=>{try{await signedIn(await api('login',{token:$('token').value},true));$('token').value='';}catch(err){$('loginError').textContent=err.message;}});};
$('logout').onclick=()=>task($('logout'),async()=>{await api('logout',{});signedOut();});
$('learnNav').onclick=()=>tab('learn');$('ideNav').onclick=()=>tab('ide');$('rulesNav').onclick=()=>tab('rules');$('openExample').onclick=async()=>{tab('ide');await newDocument(selected.id);};
$('exampleSelect').onchange=async()=>{const item=examples.find(e=>e.id===$('exampleSelect').value);try{await saveDraft();if(await choose(item))await newDocument(item.id);}catch(e){notify(e.message);$('exampleSelect').value=selected.id;}};
$('runLesson').onclick=()=>task($('runLesson'),async()=>{const v=lessonRevision;const d=await api('check',{example:selected.id});if(v===lessonRevision)verdict($('lessonResult'),d);});
$('validate').onclick=()=>task($('validate'),validate);$('check').onclick=()=>task($('check'),check);
for(const id of ['claim','premises','environment','world','useWorld']) $(id).addEventListener('input',()=>{
  dirty=true;revision++;$('checkResult').replaceChildren(el('div','Inputs changed. Check again for a current verdict.','empty'));$('validation').replaceChildren();
  if(id==='environment')$('candidates').replaceChildren();
  if(id==='claim'){$('provenance').textContent='Edited by you · review the updated paraphrase.';clearTimeout(validationTimer);validationTimer=setTimeout(validate,650);}
});
$('prose').addEventListener('input',()=>{dirty=true;$('candidates').replaceChildren();});
window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue='';}});
$('propose').onclick=()=>task($('propose'),async()=>{
  const v=revision, source=$('prose').value;const body=payload();body.text=source;delete body.premises;
  $('candidates').replaceChildren(el('p','Asking the assistant for readings… Nothing is accepted automatically.','note'));
  try {
    const response=await api('propose',body);if(v!==revision || source!==$('prose').value)return;
    const data=response; $('candidates').replaceChildren();
    if(!data.candidates.length)$('candidates').append(el('p','No valid candidates returned. Try a simpler sentence using the declared vocabulary.','note'));
    for(const c of data.candidates){
      const box=el('article',undefined,'candidate');box.append(el('span','MODEL PROPOSAL · UNTRUSTED','badge model'));
      if(c.natural)box.append(naturalView(c.natural));
      else box.append(el('p','A checked natural reading is unavailable.','note'));
      const advanced=el('details');advanced.append(el('summary','Strict VE and model gloss'),el('code',c.text));
      if(c.reading)advanced.append(el('p',c.reading,'note'));
      box.append(advanced);
      const accept=el('button','Accept this reading');accept.onclick=()=>{dirty=true;revision++;$('claim').value=c.text;$('provenance').textContent='Model proposal accepted by you for this draft. Fidelity is your responsibility; checking is separate.';$('checkResult').replaceChildren(el('div','New reading accepted. Check its consequences.','empty'));validate();$('strictEditor').open=true;$('claim').focus();};box.append(accept);$('candidates').append(box);
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
const steps=[['One reading, several views','Pick an example in Learn. Natural English gives the checked reading. Strict VE, fluent, and logic views are available in separate tabs.'],['Keep assumptions visible','Open the writing desk. The conclusion is separate from the assumptions. Remove the policy rule and check again: the checker can show a world where the conclusion fails.'],['The assistant drafts. You decide.','Write one English sentence and request readings. This spends one model call when enabled. Compare the paraphrase and alternatives before accepting or editing.'],['Read the verdict precisely','Certified means a Python-replayed proof from your assumptions. Countermodel means a checked exception to that inference. Unknown means the budget did not decide. None certifies real-world evidence. Export to keep your draft.']];let tourIndex=0;
function showTour(){ $('tourCount').textContent=`QUICK TOUR / ${tourIndex+1} OF ${steps.length}`;$('tourTitle').textContent=steps[tourIndex][0];$('tourText').textContent=steps[tourIndex][1];$('tourNext').textContent=tourIndex===steps.length-1?'Start exploring ✓':'Next →'; }
$('tourButton').onclick=()=>{tourIndex=0;showTour();$('tour').showModal();};$('tourClose').onclick=()=>$('tour').close();$('tourNext').onclick=()=>{if(++tourIndex===steps.length)$('tour').close();else showTour();};
api('session').then(signedIn).catch(()=>signedOut());

function renderDraft(doc, overwrite=false) {
  activeDraft=doc;
  const unit=doc.units[0];
  if(overwrite)$('prose').value=unit?.source || '';
  $('documentRevision').textContent=`Saved revision ${doc.revision}`;
  $('documentStatus').textContent=unit ? unit.state.replaceAll('_',' ') : 'blank draft';
  $('recovery').replaceChildren();
  $('wordSort').replaceChildren();
  for(const sort of Object.keys(doc.environment.vocabulary.sorts)) {
    const opt=el('option',sort.replaceAll('_',' '));opt.value=sort;$('wordSort').append(opt);
  }
  if(!unit){$('recovery').append(el('p','Start with any English sentence. Nothing is approved until you review its meaning.','note'));return;}
  if(unit.reason)$('recovery').append(el('p',unit.reason,'error'));
  if(unit.word_prompt){
    const p=unit.word_prompt;
    $('recovery').append(el('h3','A word or construction needs your help'),el('p',`Check “${p.term}”. ${p.expected_construction}`,'note'));
    if(p.nearest_registered_wordings.length)$('recovery').append(el('p',`Nearby declared words: ${p.nearest_registered_wordings.join(', ')}. These are suggestions, not replacements.`,'note'));
  }
  if(unit.pending.length)for(const pending of unit.pending)$('recovery').append(el('p',pending.reason || 'A reading is still unresolved.','note'));
  if(unit.state==='ready')$('recovery').append(el('p','One checked reading is ready. Confirm that it says what you intend.','note'));
  if(unit.state==='approved')$('recovery').append(el('p',`Meaning approved at this revision. ${unit.paraphrase || ''}`,'note'));
  if(unit.state==='unresolved')$('recovery').append(el('p','This unit remains visible and can be resumed by reviewing it again.','note'));
  for(const card of unit.cards || []){
    const box=el('article',undefined,'candidate checked-card');
    box.append(el('h3','Two checked readings'),el('p','This example situation makes one reading true and the other false.','note'));
    for(let i=0;i<card.paraphrases.length;i++){
      const row=el('div',undefined,'card-reading');row.append(el('p',card.paraphrases[i]));
      row.append(el('p',card.values[i]?'True in this situation':'False in this situation','badge'));
      const use=el('button','Use this wording');use.onclick=()=>task(use,async()=>{
        await changeDraft('reply',{text:card.paraphrases[i],rejected:card.meaning_ids.filter((_,j)=>j!==i).map(meaning_id=>({meaning_id,reason:'Author chose the other checked reading.'}))});
        await changeDraft('analyze',{});
      });row.append(use);box.append(row);
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
    if(!activeDraft)throw new Error('Open a document first.');
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
  await changeDraft('save',{source:$('prose').value});
}
async function newDocument(example=selected.id) {
  await saveDraft();
  clearTimeout(draftTimer);
  await draftQueue;
  activeDraft=await api('drafts',{example});
  renderDraft(activeDraft,true);
  $('recovery').replaceChildren(el('p','Start with any English sentence.','note'));
  dirty=false;
}
$('newDocument').onclick=()=>task($('newDocument'),()=>newDocument());
$('prose').addEventListener('input',()=>{
  dirty=true;clearTimeout(draftTimer);
  draftTimer=setTimeout(()=>saveDraft().catch(e=>notify(e.message)),700);
  $('documentStatus').textContent='saving';
});
$('analyse').onclick=()=>task($('analyse'),async()=>{clearTimeout(draftTimer);await saveDraft();await changeDraft('analyze',{});});
$('approveReading').onclick=()=>task($('approveReading'),async()=>{
  await saveDraft();const unit=activeDraft.units[0];await changeDraft('approve',{wording:unit.source.trim()});
});
$('noneReading').onclick=()=>task($('noneReading'),async()=>{
  const text=prompt('None of these means what you intended. Restate the sentence or give an example.');
  if(!text)return;
  const unit=activeDraft.units[0];const rejected=Object.values(unit.catalogue_results).flatMap(r=>r.candidates || []).map(r=>({meaning_id:r.meaning_id,reason:'None matches the author’s intent.'}));
  await changeDraft('reply',{text,rejected});await changeDraft('analyze',{});
});
$('askRepair').onclick=()=>task($('askRepair'),async()=>{
  clearTimeout(draftTimer);await saveDraft();
  const doc=activeDraft;
  const result=await api(`drafts/${doc.id}/assist`,{revision:doc.revision,request_id:crypto.randomUUID().replaceAll('-','')});
  if(result.status==='stale'){renderDraft(await api(`drafts/${doc.id}`),true);notify(result.reason);return;}
  renderDraft(result,false);
});
$('cancelReview').onclick=()=>task($('cancelReview'),()=>changeDraft('cancel',{}));
$('undoReview').onclick=()=>task($('undoReview'),async()=>{
  const events=activeDraft.history;
  const target=events.length>1?events[events.length-2].revision:events[0]?.revision;
  if(target===undefined)throw new Error('There is no earlier revision.');
  await changeDraft('undo',{target_revision:target});
});
$('unresolvedReading').onclick=()=>task($('unresolvedReading'),async()=>{
  const reason=prompt('Why is this sentence still unresolved?');if(reason)await changeDraft('unresolved',{reason});
});
$('defineWord').onclick=()=>task($('defineWord'),async()=>{
  const word=$('newWord').value.trim().toLowerCase(),kind=$('wordKind').value,sort=$('wordSort').value;
  const args={word,kind,description:$('wordExample').value.trim(),sorts:kind==='relation'?[sort,sort]:kind==='property'?[sort]:[]};
  if(!confirm(`Add “${word}” as ${kind} with this meaning? Existing approvals will need review.`))return;
  await changeDraft('define',args);$('glossaryStatus').textContent=`“${word}” was declared. Review the sentence again.`;
});
$('confirmGlossary').onclick=()=>task($('confirmGlossary'),async()=>{
  const sentence=$('glossarySentence').value.trim();
  if(!confirm(`Confirm this synonym statement for this document?\n${sentence}`))return;
  await changeDraft('glossary',{sentence});$('glossaryStatus').textContent='Synonyms confirmed. Review the sentence again.';
});
$('checkRules').onclick=()=>task($('checkRules'),async()=>{
  const result=await api('rules',{text:$('rulesText').value});
  $('rulesResult').replaceChildren(el('h2',result.status==='clear'?'No conflict found':result.status==='conflict'?'Conflict found':'Unknown within budget'),el('p',result.explanation));
});
