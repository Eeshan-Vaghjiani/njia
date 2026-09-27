"use strict";
/* Interview research and practice. Renders from coach.js events; never mutates coach state. */
(() => {
  const root = document.getElementById("interview-research");
  if (!root) return;
  const $ = (id) => document.getElementById(id);
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (c) => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"}[c]));
  const list = (value) => Array.isArray(value) ? value : [];
  const label = (id) => window.NjiaCoach?.label?.(id) || id;
  const CATEGORY = {technical:"Technical", behavioural:"Behavioural", case:"Case", tool:"Tool"};
  const STAR = [["situation", "Situation"], ["task", "Task"], ["action", "Action"], ["result", "Result"]];
  const state = {detail:null, target:null, questions:null, loading:false, error:"", selected:null, drafts:new Map(), feedback:null, feedbackError:"", submitting:false, qRequest:0, fRequest:0, qController:null, fController:null};

  const safeUrl = (value) => { try { const url = new URL(value); return ["https:", "http:"].includes(url.protocol) ? url.href : null; } catch { return null; } };
  const sameTarget = (a, b) => a && b && a.country === b.country && a.role === b.role;
  const strengthFor = (skill) => skill ? list(state.detail?.advisor?.strengths).find((s) => s && s.skill === skill && typeof s.evidence === "string" && s.evidence.trim()) : null;
  const briefQuestion = () => {
    const interview = state.detail?.advisor?.interview;
    return typeof interview?.question === "string" && interview.question.trim() ? interview : null;
  };

  async function post(path, body, signal) {
    let response;
    try { response = await fetch(path, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body), signal}); }
    catch (error) { if (error.name === "AbortError") throw error; throw new Error("Could not reach Njia. Check your connection, then retry."); }
    let data;
    try { data = await response.json(); } catch { throw new Error("The server returned an unreadable response. Please retry."); }
    if (!response.ok) {
      const messages = {422:"Check your answer (20–3,000 characters) and consent, then retry.", 429:"Njia is busy. Wait a moment, then try again.", 503:"This service is temporarily unavailable. Retry shortly."};
      throw new Error(typeof data.detail === "string" ? data.detail : messages[response.status] || "The request could not be completed. Please retry.");
    }
    return data;
  }

  function withTimeout(controller, ms) {
    let timedOut = false;
    const timer = setTimeout(() => { timedOut = true; controller.abort(); }, ms);
    return {done: () => clearTimeout(timer), timedOut: () => timedOut};
  }

  function evidenceNote(strength) {
    return strength ? `<p class="use-evidence"><b>Use your evidence:</b> “${esc(strength.evidence)}”</p>` : "";
  }

  function questionCard(q, index) {
    const url = safeUrl(q.source_url);
    const skill = q.skill ? `<span class="badge">${esc(label(q.skill))}</span>` : "";
    const source = url ? `<a class="source-link" href="${esc(url)}" target="_blank" rel="noopener noreferrer">Source: ${esc(q.source_title || new URL(url).hostname)} ↗</a>` : `<span class="muted">${state.questions?.mode === "web" ? "Source link unavailable" : "Curated by Njia · not web-sourced"}</span>`;
    return `<article class="web-question${state.selected?.key === `web:${index}` ? " is-selected" : ""}">
      <div class="wq-meta"><span class="badge category">${esc(CATEGORY[q.category] || "Question")}</span>${skill}</div>
      <h4 class="wq-question">${esc(q.question)}</h4>
      <p><b>Why they ask:</b> ${esc(q.why_asked)}</p>
      <p><b>How to prepare:</b> ${esc(q.how_to_prepare)}</p>
      ${evidenceNote(strengthFor(q.skill))}
      <div class="wq-footer"><p class="wq-source">${source}</p><button class="secondary-button practise-button" type="button" data-practise="web:${index}">Practise this</button></div>
    </article>`;
  }

  function renderQuestions() {
    const area = $("web-questions-area"); if (!area) return;
    const button = $("load-web-questions");
    if (button) { button.disabled = state.loading; button.firstElementChild.textContent = state.loading ? "Searching the web…" : `Find real interview questions for ${state.target?.role || "your role"}`; }
    if (state.loading) { area.innerHTML = '<p class="status iq-status" data-busy="true" role="status">Searching the web for questions candidates report for this role. This can take up to a minute…</p>'; return; }
    if (state.error) { area.innerHTML = `<div class="error-panel" role="alert"><p>${esc(state.error)}</p><div class="inline-actions"><button id="retry-web-questions" class="secondary-button" type="button">Try again</button></div></div>`; return; }
    const data = state.questions; if (!data) { area.innerHTML = ""; return; }
    const questions = list(data.questions);
    const web = data.mode === "web";
    const found = typeof data.fetched_at === "string" && !Number.isNaN(Date.parse(data.fetched_at)) ? ` · found ${new Date(data.fetched_at).toLocaleString("en-KE", {dateStyle:"medium", timeStyle:"short"})}` : "";
    area.innerHTML = `<div class="provenance iq-provenance"><span class="badge mode">${web ? `Web search · ${questions.length} sourced questions` : "Curated · not web-sourced"}</span><span class="badge">Model: ${esc(data.model || (web ? "not supplied" : "none (curated)"))}</span></div>
      <p class="hint">${esc(data.note)}${esc(found)}</p>
      ${questions.length ? `<div class="web-question-list">${questions.map(questionCard).join("")}</div>` : '<p class="empty-note">No questions were returned. Try again shortly.</p>'}`;
  }

  function renderBriefCard() {
    const brief = briefQuestion();
    return brief ? `<article class="practice-question brief-question${state.selected?.key === "brief" ? " is-selected" : ""}">
        <div class="wq-meta"><span class="badge mode">From your brief</span></div>
        <h4 class="wq-question">${esc(brief.question)}</h4>
        ${brief.what_good_looks_like ? `<details><summary>What a good answer includes</summary><p>${esc(brief.what_good_looks_like)}</p></details>` : ""}
        <div class="wq-footer"><span class="muted">Written for your CV and target role</span><button class="secondary-button practise-button" type="button" data-practise="brief">Practise this</button></div>
      </article>` : '<p class="empty-note">Build an AI career brief to get a question tailored to your CV, or load real questions below.</p>';
  }

  function renderAll() {
    const role = state.target?.role || "your role";
    root.innerHTML = `<div class="iq-toolbar"><button id="load-web-questions" class="primary-button" type="button"><span>Find real interview questions for ${esc(role)}</span><span aria-hidden="true">↗</span></button><p class="hint">Searches the web using only your target role, country and common skills. No CV text is sent.</p></div>
      <div id="brief-question-area">${renderBriefCard()}</div>
      <div id="web-questions-area"></div>
      <section id="practice-panel" class="practice-panel" tabindex="-1" aria-labelledby="practice-heading" hidden></section>`;
    renderQuestions();
  }

  function selectQuestion(key) {
    let selected = null;
    if (key === "brief") { const brief = briefQuestion(); if (brief) selected = {key, question:brief.question, origin:"From your brief", evidence:null}; }
    else if (key.startsWith("web:")) {
      const q = list(state.questions?.questions)[Number(key.slice(4))];
      if (q) selected = {key, question:q.question, origin: state.questions.mode === "web" ? `From the web · ${q.source_title || "source linked above"}` : "Curated by Njia · not web-sourced", evidence:strengthFor(q.skill)?.evidence || null};
    }
    if (!selected) return;
    saveDraft(); state.fRequest++; state.fController?.abort(); state.fController = null;
    state.selected = selected; state.feedback = null; state.feedbackError = ""; state.submitting = false;
    root.querySelectorAll(".is-selected").forEach((el) => el.classList.remove("is-selected"));
    root.querySelector(`[data-practise="${CSS.escape(key)}"]`)?.closest("article")?.classList.add("is-selected");
    renderPractice();
    const panel = $("practice-panel"); panel.scrollIntoView({behavior:"auto", block:"start"}); $("practice-answer").focus({preventScroll:true});
  }

  function saveDraft() { const box = $("practice-answer"); if (box && state.selected) state.drafts.set(state.selected.key, box.value); }

  function renderPractice() {
    const panel = $("practice-panel"); if (!panel) return;
    const s = state.selected; if (!s) { panel.hidden = true; panel.innerHTML = ""; return; }
    const draft = state.drafts.get(s.key) || "";
    panel.hidden = false;
    panel.innerHTML = `<p class="eyebrow">PRACTISE YOUR ANSWER</p>
      <h4 id="practice-heading" class="practice-heading">${esc(s.question)}</h4>
      <p class="muted">${esc(s.origin)}</p>
      ${s.evidence ? `<p class="use-evidence"><b>Use your evidence:</b> “${esc(s.evidence)}”</p>` : ""}
      <label for="practice-answer">Your answer</label>
      <textarea id="practice-answer" rows="7" maxlength="3000" aria-describedby="practice-help" placeholder="Answer as you would out loud. Try STAR: Situation, Task, Action, Result. Use only real facts.">${esc(draft)}</textarea>
      <div class="text-meta"><span id="practice-help">20–3,000 characters. Remove names and contact details.</span><span id="practice-count">${draft.length.toLocaleString()} / 3,000</span></div>
      <label class="check-label practice-consent" for="practice-consent"><input id="practice-consent" type="checkbox"><span>Send my answer and matching CV evidence, with basic contact redaction, to Groq or its NVIDIA API Catalog backup for feedback</span></label>
      ${s.evidence ? '<p class="hint">Your matching CV evidence quote is sent too, so the outline can use your real facts.</p>' : ""}
      <div class="inline-actions"><button id="practice-submit" class="primary-button" type="button"><span>Get feedback</span><span aria-hidden="true">↗</span></button><button id="practice-cancel" class="text-button" type="button" hidden>Cancel</button></div>
      <div id="practice-error" class="error-panel" role="alert" hidden></div>
      <div id="practice-feedback" aria-live="polite"></div>`;
    renderFeedback();
  }

  function renderFeedback() {
    const box = $("practice-feedback"); if (!box) return;
    const submit = $("practice-submit"), cancel = $("practice-cancel"), error = $("practice-error");
    submit.disabled = state.submitting; submit.firstElementChild.textContent = state.submitting ? "Reviewing your answer…" : state.feedback ? "Get feedback again" : "Get feedback";
    cancel.hidden = !state.submitting;
    error.hidden = !state.feedbackError;
    error.innerHTML = state.feedbackError ? `<p>${esc(state.feedbackError)}</p>${state.feedbackRetry ? '<div class="inline-actions"><button id="practice-retry" class="secondary-button" type="button">Try again</button></div>' : ""}` : "";
    if (state.submitting) { box.innerHTML = '<p class="status iq-status" data-busy="true">Reviewing your answer…</p>'; return; }
    const f = state.feedback; if (!f) { box.innerHTML = ""; return; }
    const score = Number.isInteger(f.score) && f.score >= 1 && f.score <= 5 ? f.score : null;
    const ai = !!f.mode && f.mode !== "checklist";
    const items = (values) => list(values).length ? `<ul>${list(values).map((v) => `<li>${esc(v)}</li>`).join("")}</ul>` : '<p class="muted">None noted.</p>';
    box.innerHTML = `<article class="feedback-card">
      <div class="provenance"><span class="badge mode">${ai ? (f.mode === "nvidia" ? "AI feedback · NVIDIA fallback" : "AI feedback") : "Checklist feedback · no AI"}</span><span class="badge">Model: ${esc(f.model || (ai ? "not supplied" : "none (checklist)"))}</span></div>
      <div class="score-line"><strong class="score-value">${score ? `${score} / 5` : "Score unavailable"}</strong>${score ? `<span class="score-dots" role="img" aria-label="${score} out of 5">${[1, 2, 3, 4, 5].map((n) => `<span class="${n <= score ? "on" : ""}"></span>`).join("")}</span>` : ""}</div>
      <p class="verdict">${esc(f.verdict)}</p>
      <ul class="star-list" aria-label="STAR checklist">${STAR.map(([key, name]) => { const ok = f.star?.[key] === true; return `<li class="${ok ? "yes" : "no"}"><span aria-hidden="true">${ok ? "✓" : "✗"}</span> ${name}<span class="sr-only">${ok ? " present" : " missing"}</span></li>`; }).join("")}</ul>
      <div class="feedback-columns"><div><h5>What worked</h5>${items(f.strengths)}</div><div><h5>Improve next</h5>${items(f.improvements)}</div></div>
      <h5>A stronger answer outline</h5>
      <p class="stronger-answer">${esc(f.stronger_answer)}</p>
      <p class="hint">${esc(f.note)}</p>
      <button id="practice-revise" class="secondary-button" type="button">Revise my answer</button>
    </article>`;
  }

  async function loadQuestions() {
    if (state.loading || !state.target) return;
    const request = ++state.qRequest; const controller = new AbortController(); state.qController = controller;
    const timer = withTimeout(controller, 80000);
    state.loading = true; state.error = ""; renderQuestions();
    try {
      const data = await post("/api/interview/questions", {country:state.target.country, role:state.target.role, skills:list(state.detail?.skills).slice(0, 100)}, controller.signal);
      if (request !== state.qRequest) return;
      if (!data || !Array.isArray(data.questions)) throw new Error("The question list was incomplete. Please retry.");
      state.questions = data;
    } catch (error) {
      if (request !== state.qRequest) return;
      state.error = timer.timedOut() ? "The web search took too long. Try again shortly." : error.name === "AbortError" ? "" : error.message;
    } finally {
      timer.done();
      if (request === state.qRequest) { state.loading = false; state.qController = null; renderQuestions(); }
    }
  }

  async function submitAnswer() {
    const s = state.selected; if (!s || state.submitting) return;
    const answer = $("practice-answer").value; saveDraft();
    if (answer.trim().length < 20) { state.feedbackError = "Write at least 20 characters so there is something to review."; state.feedbackRetry = false; renderFeedback(); $("practice-answer").focus(); return; }
    if (!$("practice-consent").checked) { state.feedbackError = "Tick the consent box to send your answer for feedback."; state.feedbackRetry = false; renderFeedback(); $("practice-consent").focus(); return; }
    const request = ++state.fRequest; const controller = new AbortController(); state.fController = controller;
    const timer = withTimeout(controller, 65000);
    state.submitting = true; state.feedbackError = ""; state.feedbackRetry = true; renderFeedback();
    try {
      const body = {role:state.target?.role, question:s.question.slice(0, 500), answer, consent:true};
      if (s.evidence) body.evidence = s.evidence.slice(0, 700);
      const data = await post("/api/interview/feedback", body, controller.signal);
      if (request !== state.fRequest) return;
      if (!data || typeof data.verdict !== "string") throw new Error("The feedback was incomplete. Please retry.");
      state.feedback = data;
    } catch (error) {
      if (request !== state.fRequest) return;
      state.feedbackError = timer.timedOut() ? "Feedback took too long. Try again; your answer is still here." : error.name === "AbortError" ? "Feedback request cancelled. Your answer is still here." : error.message;
    } finally {
      timer.done();
      if (request === state.fRequest) { state.submitting = false; state.fController = null; renderFeedback(); if (state.feedback && !state.feedbackError) $("practice-feedback").scrollIntoView({behavior:"auto", block:"nearest"}); }
    }
  }

  function clearAll() {
    state.qRequest++; state.fRequest++; state.qController?.abort(); state.fController?.abort();
    Object.assign(state, {detail:null, target:null, questions:null, loading:false, error:"", selected:null, feedback:null, feedbackError:"", submitting:false, qController:null, fController:null});
    state.drafts.clear(); root.innerHTML = "";
  }

  root.addEventListener("click", (event) => {
    const practise = event.target.closest("[data-practise]");
    if (practise) { selectQuestion(practise.dataset.practise); return; }
    const id = event.target.closest("button")?.id;
    if (id === "load-web-questions" || id === "retry-web-questions") loadQuestions();
    else if (id === "practice-submit" || id === "practice-retry") submitAnswer();
    else if (id === "practice-cancel") state.fController?.abort();
    else if (id === "practice-revise") { const box = $("practice-answer"); box.scrollIntoView({behavior:"auto", block:"center"}); box.focus({preventScroll:true}); }
  });
  root.addEventListener("input", (event) => {
    if (event.target.id !== "practice-answer") return;
    $("practice-count").textContent = `${event.target.value.length.toLocaleString()} / 3,000`;
    if (state.selected) state.drafts.set(state.selected.key, event.target.value);
  });

  document.addEventListener("njia:brief", (event) => {
    const detail = event.detail || window.NjiaCoach?.snapshot?.() || null;
    const target = detail?.target && typeof detail.target.role === "string" ? {country:detail.target.country, role:detail.target.role} : null;
    const keep = sameTarget(target, state.target) && state.questions;
    const questions = keep ? state.questions : null;
    clearAll();
    state.detail = detail; state.target = target; state.questions = questions;
    if (target) renderAll();
  });
  document.addEventListener("njia:skills", (event) => {
    if (!state.target) return;
    state.detail = {...(state.detail || {}), skills:list(event.detail?.skills)};
  });
  document.addEventListener("njia:reset", clearAll);
})();
