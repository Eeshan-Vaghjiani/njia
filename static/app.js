"use strict";
const $ = (s) => document.querySelector(s);
const esc = (v) => String(v).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const state = {meta:null, skills:new Set(), analysis:null, plan:null, assessment:null, grade:null, reflection:"", answers:{}, planRequest:0, attempt:0, completed:new Set(), tab:"overview", revision:0, uploadRequest:0, aiConsent:false, hours:5};
const MAX_UPLOAD_BYTES = 4000000;
const SAMPLE = "I am an aspiring data analyst in Nairobi. I use SQL to query sales records and Excel to build pivot tables and monthly reports. I have also created dashboards in Power BI. I want to learn Python and R.";
const label = id => state.meta?.skills.find(s => s.id === id)?.label || id;
function status(message, error=false) { const el=$("#status"); el.textContent=message; el.hidden=!message; el.classList.toggle("error",error); }
async function api(path, body) {
  const response=await fetch(path, body===undefined ? {} : body instanceof FormData ? {method:"POST",body} : {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
  if(!response.ok){let detail;try{detail=(await response.json()).detail;}catch{}throw new Error(typeof detail==="string" ? detail : response.status===413 ? "File too large. Choose a file no larger than 4,000,000 bytes." : "Please check your input and try again.");}
  return response.json();
}
async function busy(button, text, fn) {
  const original=button.innerHTML, revision=state.revision; button.disabled=true; button.textContent=text;
  let request=state.planRequest, attempt=state.attempt;
  try{const pending=fn();request=state.planRequest;attempt=state.attempt;await pending;}catch(error){if(revision===state.revision && request===state.planRequest && attempt===state.attempt && button.isConnected)status(error.message || "Could not reach the server. Please try again.",true);}finally{button.innerHTML=original;button.disabled=false;}
}
function uploadStatus(message, error=false){const el=$("#upload-status");el.textContent=message;el.hidden=!message;el.classList.toggle("error",error);}
function revise(){state.revision++;state.uploadRequest++;uploadStatus("");$("#upload").disabled=!state.meta;$("#upload").textContent="Upload & preview text ↑";$("#upload").removeAttribute("aria-busy");}
function clearFile(){ $("#cv-file").value="";$("#upload-consent").checked=false; }
function remoteAI(){return state.meta?.ai?.is_remote===true || state.meta?.ai?.provider==="groq";}
function aiLabel(){const ai=state.meta?.ai;if(remoteAI())return ai.configured ? "Remote AI coaching available via Groq · optional" : "Remote AI unavailable · curated plans available";return ai?.provider==="ollama" ? "Server-hosted Ollama coaching · availability checked when used" : "Curated plans · no generative model connected";}
function planMode(mode){return mode==="groq" ? "AI coaching · Groq" : mode==="ollama" ? "AI coaching · Ollama" : "Curated plan";}
function payload(){return {country:$("#country").value,role:$("#role").value,skills:[...state.skills]};}
function invalidate(){revise();state.planRequest++;state.attempt++;state.answers={};state.analysis=null;state.plan=null;state.grade=null;state.assessment=null;state.reflection="";state.completed.clear();["overview","plan","practice"].forEach(id=>{$(`#${id}`).innerHTML="";$(`#${id}`).hidden=true;});$("#welcome").hidden=false;status("");}
function renderSkills(){
  $("#skill-count").textContent=state.skills.size;
  $("#skill-chips").innerHTML=state.skills.size ? [...state.skills].sort().map(s=>`<span class="chip">${esc(label(s))}<button data-remove="${esc(s)}" aria-label="Remove ${esc(label(s))}">×</button></span>`).join("") : '<span class="empty-chip">Your confirmed skills will appear here</span>';
}
function switchTab(tab){
  state.tab=tab;document.querySelectorAll(".tab").forEach(b=>{b.classList.toggle("active",b.dataset.tab===tab);b.setAttribute("aria-selected",String(b.dataset.tab===tab));});
  ["overview","plan","practice"].forEach(id=>$(`#${id}`).hidden=!state.analysis || id!==tab);
  if(state.analysis){$("#welcome").hidden=true;if(tab==="plan")renderPlan();if(tab==="practice")renderPractice();}
}
function sample(){ clearFile();$("#cv").value=SAMPLE;$("#country").value="Kenya";$("#role").value="Data Analyst";$("#consent").checked=true;state.skills=new Set();invalidate();renderSkills();$("#extraction-note").textContent="Synthetic sample profile loaded. Find the skills, review them, then find your path.";$("#cv").focus(); }
function chartRow(s){return `<div class="chart-row"><div class="chart-label">${esc(s.label)} ${s.owned?'<span aria-label="In your skills">✓</span>':""}</div><div class="bar-track"><div class="bar ${s.owned?"owned":""}" style="width:${s.demand_pct}%"></div></div><div class="chart-value">${s.demand_pct}%</div></div>`;}
function renderOverview(){
  const a=state.analysis, gap=a.gaps[0];
  $("#overview").innerHTML=`<div class="result-heading"><div><div class="section-kicker">02 / YOUR MARKET, DECODED</div><h2>Your next step looks clearer.</h2><p>${esc(a.role)} · ${esc(a.country)}</p></div><span class="tiny-badge">${a.sample_size.toLocaleString()} postings</span></div>
  ${a.fallback?`<div class="callout fallback-note">Only <strong>${a.local_postings}</strong> local postings for this role. Below our 50-posting threshold, so all figures below use the <strong>10-country Africa/MENA sample</strong>.</div>`:""}
  <div class="score-card"><div class="score-ring" style="--progress:${a.coverage}%"><strong>${a.coverage}%</strong></div><div class="score-copy"><h3>Your demand-weighted skill coverage</h3><p>You have ${a.matched_count} of the top ${a.skills.length} skills in this market’s postings. ${a.matched_count ? "A foundation to build on." : "Let’s start with the most requested skills."}</p><p class="score-foot">Based on confirmed skills, not tested proficiency or hiring odds.</p></div></div>
  <div class="panel-card"><div class="panel-heading"><h3>What employers asked for</h3><div class="legend"><span class="have"><i></i>Your skills</span><span><i></i>Room to grow</span></div></div><p class="hint">Share of ${esc(a.scope)} ${esc(a.role)} postings mentioning each skill · 2023</p>${a.skills.slice(0,7).map(chartRow).join("")}<details class="chart-details"><summary>See all ${a.skills.length} skills & the calculation</summary>${a.skills.slice(7).map(chartRow).join("")}<p class="hint">Coverage = mentions of your confirmed skills among the top 15 ÷ all mentions of those top 15 skills × 100. Each posting is counted at most once per skill. A posting can mention several skills.</p></details>
  <div class="callout">${gap?`<strong>A good place to start: ${esc(gap.label)}.</strong> It appears in ${gap.count} of ${a.sample_size} postings (${gap.demand_pct}%) and isn’t in your confirmed skills yet.`:'<strong>You cover the top skills in this sample.</strong> Deepen your knowledge with practice and a portfolio project.'}</div><div class="section-action"><span class="hint">A focused plan, shaped by this market.</span><button class="primary-button" data-go="plan">Build my learning path <span>→</span></button></div></div>
  <div class="panel-card"><div class="panel-heading"><h3>Your skills in the real world</h3><span class="tiny-badge">Historical examples</span></div><p class="hint">${esc(a.retrieval_method)}</p>${a.jobs.length?a.jobs.map(j=>`<div class="job-card"><h4>${esc(j.title)}</h4><p>${esc(j.country)} · 2023 · skill similarity ${Math.round(j.similarity*100)}% (not hiring odds)</p><div class="chips">${j.skills.map(s=>`<span class="chip ${j.matched.includes(s)?"match":""}">${esc(s)}</span>`).join("")}</div></div>`).join(""):'<p class="muted">Add a skill mentioned in this market to retrieve related historical postings.</p>'}</div>
  <p class="hint">Analyzed on the server in ${a.elapsed_ms} ms · No CV storage · <a href="${esc(state.meta.source_url)}" target="_blank" rel="noreferrer">View dataset source ↗</a></p>`;
}
function renderPlan(){
  if(!state.analysis)return;
  if(!state.plan){$("#plan").innerHTML=`<div class="result-heading"><div><div class="section-kicker">03 / ONE WEEK AT A TIME</div><h2>A little structure. Real progress.</h2><p>Four weeks focused on your highest-demand gaps.</p></div></div><div class="panel-card"><h3>Make space for your next step.</h3><p class="muted">Choose a pace that fits your week. You’ll get practical exercises, learning resources, and something to show for your work.</p>${remoteAI()?`<div class="ai-choice"><label class="check-label"><input id="ai-consent" type="checkbox" ${state.aiConsent?"checked":""} ${state.meta.ai.configured?"":"disabled"} aria-describedby="ai-help"><span>I opt in to sending structured skill and curriculum data to Groq for AI coaching. My CV is never sent to AI.</span></label><p id="ai-help" class="hint">${state.meta.ai.configured?"Leave unchecked to create a curated plan without remote AI.":"Groq is not configured. You can still create a curated plan."}</p></div>`:""}<div class="plan-toolbar"><label for="hours">Hours per week<select id="hours">${[2,3,5,8,10,15,20].map(h=>`<option value="${h}" ${h===state.hours?"selected":""}>${h} hours / week</option>`).join("")}</select></label><button class="primary-button" id="generate-plan">Create my 4-week plan <span>→</span></button></div><p class="hint">${esc(aiLabel())}. Resources may have optional paid content; use the free material. Software licences are noted where relevant.</p></div>`;return;}
  const p=state.plan;
  $("#plan").innerHTML=`<div class="result-heading"><div><div class="section-kicker">03 / ONE WEEK AT A TIME</div><h2>Your four-week learning path.</h2><p>${esc(state.analysis.role)} · ${p.weeks[0].hours} hours per week · <span id="progress">${state.completed.size}</span>/4 complete</p></div><span class="tiny-badge">${planMode(p.mode)}</span></div><p class="hint">${esc(p.note)}</p>${p.weeks.map(w=>`<article class="panel-card week-card ${state.completed.has(w.week)?"completed":""}"><span class="week-number">0${w.week}</span><div class="section-kicker">WEEK ${w.week} · ${w.hours} HOURS</div><h3>${esc(w.title)}</h3><p class="why">${esc(w.why)}</p><ul>${w.tasks.map(t=>`<li>${esc(t)}</li>`).join("")}</ul><div class="deliverable"><strong>Your evidence:</strong> ${esc(w.deliverable)}</div><a class="resource-link" href="${esc(w.resource.url)}" target="_blank" rel="noreferrer">${esc(w.resource.title)} ↗</a><label class="progress-label"><input type="checkbox" data-week="${w.week}" ${state.completed.has(w.week)?"checked":""}> Mark this week complete (this session only)</label></article>`).join("")}<div class="export-row"><button class="secondary-button" data-download>Download my path ↓</button><button class="primary-button" data-go="practice">Try a practice check →</button><button class="text-button" id="new-plan">Change my pace</button></div>`;
}
function renderPractice(){
  if(!state.analysis)return;
  const skills=state.meta.assessment_skills;
  let suggested=state.analysis.gaps.find(s=>skills.includes(s.id))?.id || [...state.skills].find(s=>skills.includes(s)) || "sql";
  if(state.assessment)suggested=state.assessment.skill;
  const head=`<div class="result-heading"><div><div class="section-kicker">04 / PUT IT INTO PRACTICE</div><h2>Build confidence. Collect evidence.</h2><p>A short check of the fundamentals, with room to reflect.</p></div></div><div class="panel-card"><div class="plan-toolbar"><label for="practice-skill">Skill to practice<select id="practice-skill">${skills.map(s=>`<option value="${s}" ${s===suggested?"selected":""}>${esc(label(s))}</option>`).join("")}</select></label><button class="primary-button" id="start-practice">${state.assessment?"Start again":"Start a practice check"} →</button></div><p class="hint">Available for SQL, R, Python, Excel, Power BI, and Docker. Three fixed questions; no certification or AI grading. Starting again clears the previous practice result.</p></div>`;
  let body="";
  if(state.grade){const g=state.grade;body=`<div class="panel-card"><div class="panel-heading"><h3>${esc(g.label)} · ${g.correct}/${g.total} correct</h3><span class="tiny-badge">Practice evidence</span></div><p class="muted">${esc(g.summary)}</p>${g.feedback.map(f=>`<div class="feedback ${f.correct?"":"wrong"}"><strong>${f.correct?"✓":"↗"} ${esc(f.question)}</strong><p>Your answer: ${esc(f.selected)}<br>Answer key: ${esc(f.expected)}<br>${esc(f.explanation)}</p></div>`).join("")}${state.reflection?`<h3>Your reflection</h3><p class="muted">${esc(state.reflection)}</p><p class="hint">Saved only in this page’s memory. Not graded.</p>`:""}<p class="hint">${esc(g.method)}</p><button class="secondary-button" data-download>Download my evidence report ↓</button></div>`;}
  else if(state.assessment){body=`<form id="practice-form" class="panel-card practice-form"><h3>${esc(state.assessment.label)} fundamentals</h3>${state.assessment.questions.map(q=>`<fieldset><legend>${q.id+1}. ${esc(q.prompt)}</legend>${q.options.map((o,i)=>`<label class="radio-option"><input type="radio" name="q${q.id}" value="${i}" required>${esc(o)}</label>`).join("")}</fieldset>`).join("")}<label for="reflection">${esc(state.assessment.reflection)}</label><textarea id="reflection" maxlength="2000" rows="3" placeholder="Optional reflection for you and a mentor. Don’t include personal details.">${esc(state.reflection)}</textarea><p class="hint">Self-review only. This reflection is not sent to the server.</p><button class="primary-button" type="submit">Check my answers →</button></form>`;}
  else{body=`<div class="panel-card"><h3>Your experience is more than a score.</h3><p class="muted">Use the check to spot concepts to revisit, then show what you’ve learned in a small project. Share your report with a mentor for a human perspective.</p><button class="secondary-button" data-download>Download my current skill report ↓</button></div>`;}
  $("#practice").innerHTML=head+body;
  for(const [question, answer] of Object.entries(state.answers)){const input=$(`#practice-form input[name="q${question}"][value="${answer}"]`);if(input)input.checked=true;}
}
function download(){
  const a=state.analysis;if(!a)return;
  let text=`# Njia — Skill Evidence Report\n\nCreated: ${new Date().toISOString()}\nTarget: ${a.role} / ${a.country}\nEvidence scope: ${a.scope}, ${a.sample_size} historical postings (2023)\nLocal sample: ${a.local_postings}; expanded sample: ${a.fallback?'yes':'no'}\n\n## Confirmed skills (self-reported)\n${[...state.skills].map(label).join(", ") || "None yet"}\n\n## Demand-weighted coverage\n${a.coverage}% — ${a.method}\n\n## Skills in the market\n${a.skills.map(s=>`- ${s.label}: ${s.count}/${a.sample_size} postings (${s.demand_pct}%) — ${s.owned?"confirmed":"gap"}`).join("\n")}\n`;
  if(state.plan){text+=`\n## Four-week learning plan\n${state.plan.note}\n`;for(const w of state.plan.weeks)text+=`\n### Week ${w.week}: ${w.title} (${w.hours} hours)\n${w.why}\n${w.tasks.map(t=>`- ${t}`).join("\n")}\nEvidence: ${w.deliverable}\nResource: ${w.resource.title} — ${w.resource.url}\nMarked complete: ${state.completed.has(w.week)?"yes":"no"}\n`;}
  if(state.grade){const g=state.grade;text+=`\n## Practice check: ${g.label}\n${g.correct}/${g.total} correct. ${g.method}\n${g.feedback.map(f=>`- ${f.question}\n  Your answer: ${f.selected}\n  Correct answer: ${f.expected}\n  ${f.explanation}`).join("\n")}\n\nReflection (not graded): ${state.reflection || "Not provided"}\n`;}
  text+=`\n## Methods and limitations\nServer-side lexicon skill extraction, deterministic demand counts, and TF-IDF/cosine job retrieval. ${["ollama","groq"].includes(state.plan?.mode)?`${planMode(state.plan.mode)} used for plan wording. Model: ${state.plan.model || "not specified"}.`:"No generative model used in this report."}\nNo Brev credits used. No CV storage. Files and text are processed in server memory. CV never sent to AI or included in this report. Confirmed skills and optional reflection are included: review before sharing.\nData: ${state.meta.source}, ${state.meta.source_url}; 2023, tech/data only. Prepared source documentation identifies Apache-2.0. This is not a hiring decision, certification, live vacancy feed, or representative labour-market survey.\n`;
  const url=URL.createObjectURL(new Blob([text],{type:"text/markdown;charset=utf-8"}));const link=document.createElement("a");link.href=url;link.download="njia-skill-evidence.md";link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
$("#about-button").onclick=()=>$("#about").showModal();$("#close-about").onclick=()=>$("#about").close();
$("#sample").onclick=sample;$("#welcome-sample").onclick=()=>{if(state.meta)sample();};
$("#clear-text").onclick=()=>{revise();clearFile();status("");$("#cv").value="";$("#consent").checked=false;$("#extraction-note").textContent="Text cleared. Confirmed skills are kept until you remove them or reset the session.";};
$("#country").onchange=invalidate;$("#role").onchange=invalidate;
$("#cv").oninput=()=>{revise();status("");$("#extraction-note").textContent="Text changed. Review it and find skills again to update your confirmed skills.";};
$("#consent").onchange=revise;
$("#upload-consent").onchange=revise;
$("#cv-file").onchange=()=>{revise();$("#upload-consent").checked=false;const file=$("#cv-file").files[0];if(file)uploadStatus(file.size>MAX_UPLOAD_BYTES?"File too large. Choose a file no larger than 4,000,000 bytes.":!/\.(pdf|docx|txt)$/i.test(file.name)?"Choose a PDF, DOCX or TXT file.":`${file.name} selected. Agree to server processing, then upload to preview.`,file.size>MAX_UPLOAD_BYTES || !/\.(pdf|docx|txt)$/i.test(file.name));};
$("#upload").onclick=async()=>{
  const file=$("#cv-file").files[0];
  if(!file){uploadStatus("Choose a PDF, DOCX or TXT file first.",true);return;}
  if(!/\.(pdf|docx|txt)$/i.test(file.name)){uploadStatus("Choose a PDF, DOCX or TXT file.",true);return;}
  if(!file.size || file.size>MAX_UPLOAD_BYTES){uploadStatus(file.size?"File too large. Choose a file no larger than 4,000,000 bytes.":"This file is empty. Choose a CV containing text.",true);return;}
  if(!$("#upload-consent").checked){uploadStatus("Please agree to process this file in server memory first.",true);return;}
  revise();const revision=state.revision, request=state.uploadRequest, button=$("#upload");
  const current=()=>revision===state.revision && request===state.uploadRequest;
  const body=new FormData();body.append("file",file);body.append("consent","true");
  button.disabled=true;button.textContent="Preparing your preview…";button.setAttribute("aria-busy","true");uploadStatus("Uploading and reading your CV in server memory…");
  try{
    const data=await api("/api/upload",body);if(!current())return;
    if(typeof data.text!=="string" || !data.text.trim())throw new Error("No readable text was returned. Try another file or paste your text.");
    if(data.text.length>$("#cv").maxLength)throw new Error("The preview exceeds 15,000 characters. Shorten your CV and upload again, or paste a shorter skills summary.");
    state.skills.clear();invalidate();renderSkills();$("#cv").value=data.text;$("#consent").checked=false;
    $("#extraction-note").textContent="Preview ready. Review and edit the text, agree to skill extraction, then select Find my skills.";
    uploadStatus(`${data.filename || file.name}: preview ready below. ${data.note || ""} Review the text before finding your skills.`);
    $("#cv").focus();
  }catch(error){if(current())uploadStatus(error.message || "Could not upload your CV. Please try again.",true);}
  finally{if(current()){button.disabled=!state.meta;button.textContent="Upload & preview text ↑";button.removeAttribute("aria-busy");}}
};
$("#add-skill").onclick=()=>{const s=$("#skill-select").value;if(s){state.skills.add(s);invalidate();renderSkills();$("#skill-select").value="";}};
$("#extract").onclick=()=>busy($("#extract"),"Finding your skills…",async()=>{
  if(!$("#consent").checked)throw new Error("Please review the text and agree to server processing first, or add skills manually.");
  const text=$("#cv").value;if(text.trim().length<10)throw new Error("Add at least 10 characters about your skills or use the sample profile.");
  const revision=state.revision;const data=await api("/api/extract",{text,consent:true});if(revision!==state.revision)return;
  state.skills=new Set(data.skills);invalidate();renderSkills();$("#extraction-note").textContent=data.note;
  status(data.skills.length?`Found ${data.skills.length} skills. Review them, add anything missing, then find your path.`:"No vocabulary matches found. Add your skills manually; they may be implied or outside this dataset.");
});
$("#analyze").onclick=()=>busy($("#analyze"),"Mapping your market…",async()=>{
  const revision=state.revision;const data=await api("/api/analyze",payload());if(revision!==state.revision)return;
  state.planRequest++;state.attempt++;state.answers={};state.analysis=data;state.plan=null;state.grade=null;state.assessment=null;state.reflection="";state.completed.clear();renderOverview();switchTab("overview");status("");if(innerWidth<761)$(".results-area").scrollIntoView({behavior:"smooth"});
});
document.addEventListener("click",event=>{
  const remove=event.target.closest("[data-remove]");if(remove){state.skills.delete(remove.dataset.remove);invalidate();renderSkills();}
  const tab=event.target.closest("[data-tab],[data-go]");if(tab)switchTab(tab.dataset.tab || tab.dataset.go);
  if(event.target.closest("[data-download]"))download();
  if(event.target.closest("#generate-plan")){const btn=$("#generate-plan");busy(btn,"Building your plan…",async()=>{const revision=state.revision;const request=++state.planRequest;const aiConsent=remoteAI() && state.meta.ai.configured===true && state.aiConsent;const p=await api("/api/plan",{...payload(),hours:Number($("#hours").value),use_ai:remoteAI()?aiConsent:true,ai_consent:aiConsent});if(revision!==state.revision || request!==state.planRequest || !state.analysis)return;state.plan=p;renderPlan();status("");});}
  if(event.target.closest("#new-plan")){state.planRequest++;state.plan=null;state.completed.clear();renderPlan();}
  if(event.target.closest("#start-practice")){busy($("#start-practice"),"Getting your check…",async()=>{const revision=state.revision;const attempt=++state.attempt;const data=await api(`/api/assessment/${encodeURIComponent($("#practice-skill").value)}`);if(revision!==state.revision || attempt!==state.attempt || !state.analysis)return;state.assessment=data;state.grade=null;state.reflection="";state.answers={};renderPractice();status("");});}
});
document.addEventListener("change",event=>{if(event.target.matches('#practice-form input[type="radio"]'))state.answers[event.target.name.slice(1)]=Number(event.target.value);if(event.target.matches("[data-week]")){const n=Number(event.target.dataset.week);event.target.checked?state.completed.add(n):state.completed.delete(n);$("#progress").textContent=state.completed.size;event.target.closest(".week-card").classList.toggle("completed",event.target.checked);}});
document.addEventListener("input",event=>{if(event.target.id==="reflection")state.reflection=event.target.value;});
document.addEventListener("change",event=>{if(event.target.id==="ai-consent" || event.target.id==="hours"){const id=event.target.id;if(id==="ai-consent")state.aiConsent=event.target.checked;else state.hours=Number(event.target.value);state.planRequest++;status("");renderPlan();$(`#${id}`)?.focus();}});
document.addEventListener("submit",event=>{if(event.target.id!=="practice-form")return;event.preventDefault();const form=event.target;busy(form.querySelector('button[type="submit"]'),"Checking…",async()=>{const revision=state.revision;const attempt=state.attempt;const skill=state.assessment.skill;const answers=state.assessment.questions.map(q=>Number(new FormData(form).get(`q${q.id}`)));const data=await api("/api/assessment/grade",{skill,answers});if(revision!==state.revision || attempt!==state.attempt || state.assessment?.skill!==skill)return;state.grade=data;renderPractice();status("");});});
$("#reset").onclick=()=>{state.skills.clear();state.aiConsent=false;state.hours=5;invalidate();clearFile();renderSkills();$("#cv").value="";$("#consent").checked=false;$("#extraction-note").textContent="Session cleared. You can choose skills manually or use an example.";switchTab("overview");};
(async()=>{try{state.meta=await api("/api/meta");$("#country").innerHTML=state.meta.countries.map(c=>`<option ${c.name==="Kenya"?"selected":""}>${esc(c.name)}</option>`).join("");$("#role").innerHTML=state.meta.roles.map(r=>`<option ${r==="Data Analyst"?"selected":""}>${esc(r)}</option>`).join("");$("#skill-select").innerHTML='<option value="">Add a skill…</option>'+state.meta.skills.map(s=>`<option value="${esc(s.id)}">${esc(s.label)}</option>`).join("");$("#posting-count").textContent=state.meta.postings.toLocaleString();$("#mode-note").textContent=aiLabel()+". Demand analysis and job retrieval run on the server. CV never sent to AI.";["country","role","skill-select","sample","extract","add-skill","analyze","upload"].forEach(id=>$(`#${id}`).disabled=false);}catch(error){status("Could not load Njia. Please refresh the page and try again.",true);$("#mode-note").textContent="Server unavailable. Please refresh to reconnect.";}})();
