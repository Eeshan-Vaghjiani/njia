"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (c) => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"}[c]));
  const list = (value) => Array.isArray(value) ? value : [];
  const pct = (value) => typeof value === "number" && Number.isFinite(value) && value >= 0 && value <= 100 ? `${value}%` : "Not available";
  const state = {meta:null, tab:"upload", advisor:null, market:null, briefTarget:null, briefText:null, marketTarget:null, skills:new Set(), confirmed:[], completed:new Set(), reviewed:false, busy:false, controller:null, request:0, retry:null, synthetic:false, followup:null, answers:[]};
  const SAMPLE = "SYNTHETIC SAMPLE — fictional candidate\nNairobi, Kenya | Junior data analyst\n\nPROFILE\nEarly-career operations assistant moving into data analysis, with a diploma in business information technology.\n\nEXPERIENCE\nOperations Assistant, fictional Nairobi retail cooperative, 2024–2025\nUsed Excel pivot tables to summarise weekly sales across three branches.\nChecked stock records against sales spreadsheets and flagged duplicate entries for the supervisor.\nPrepared a monthly sales summary and explained changes to the operations team.\n\nPROJECT\nBuilt a Power BI dashboard using a synthetic retail dataset to compare sales by product and branch.\nUsed SQL SELECT, JOIN and GROUP BY queries to answer sales questions in a personal practice project.\nDocumented the data-cleaning steps and checked totals against the source spreadsheet.\n\nNEXT STEP\nSeeking a junior Data Analyst role in Kenya. I want to learn Python; I have not used it in a project yet.";
  const target = () => ({country:$("country").value, role:$("role").value});
  const sameTarget = (a, b) => a && b && a.country === b.country && a.role === b.role;
  const label = (id) => state.meta?.skills?.find((s) => s.id === id)?.label || id;
  const skillDirty = () => [...state.skills].sort().join("\0") !== [...state.confirmed].sort().join("\0");
  const briefStale = () => !!state.advisor && (!sameTarget(target(), state.briefTarget) || state.briefText !== $("cv-text").value || (state.tab === "upload" && !!$("cv-file").files[0]));
  const snapshot = () => ({target: state.briefTarget || state.marketTarget || target(), currentTarget: target(), marketTarget: state.marketTarget, skills: [...state.confirmed], reviewed: state.reviewed, advisor: state.advisor, market: state.market, synthetic: state.synthetic, meta: state.meta, stale: briefStale()});
  // Feature modules (jobs.js, interview.js) render from these events and never mutate coach state.
  const emit = (name) => document.dispatchEvent(new CustomEvent(`njia:${name}`, {detail: snapshot()}));
  window.NjiaCoach = Object.freeze({snapshot, label});
  function status(message, busy = false) { $("status").textContent = message; $("status").hidden = !message; $("status").dataset.busy = String(busy); }
  function clearError() { $("error-panel").hidden = true; state.retry = null; }
  function showError(error, retry, fallback = false) {
    $("error-message").textContent = error.message || "Njia could not connect. Check your connection and try again. Your input is still here.";
    $("error-panel").hidden = false; $("retry").hidden = !retry; $("market-fallback").hidden = !fallback; state.retry = retry;
  }
  async function api(path, body, signal) {
    const options = {signal};
    if (body !== undefined) { options.method = "POST"; options.body = body instanceof FormData ? body : JSON.stringify(body); if (!(body instanceof FormData)) options.headers = {"Content-Type":"application/json"}; }
    let response;
    try { response = await fetch(path, options); } catch (error) { if (error.name === "AbortError") throw error; throw new Error("Could not reach Njia. Check your connection, then retry. Your CV input has been kept on this page."); }
    let data;
    try { data = await response.json(); } catch { throw new Error("The server returned an unreadable response. Retry, or paste a shorter CV summary."); }
    if (!response.ok) {
      const messages = {404:"Career advice is not available on this server yet. Retry after deployment, or use market evidence only.", 413:"This file is too large. Choose a file up to 4,000,000 bytes (4 MB).", 422:"Check your CV (10–15,000 characters), target role and consent, then retry.", 429:"Njia is busy. Wait a moment, then try again.", 503:"Career advice is temporarily unavailable. Retry shortly, or use market evidence only."};
      throw new Error(typeof data.detail === "string" ? data.detail : messages[response.status] || "The request could not be completed. Retry shortly; your input is still here.");
    }
    return data;
  }
  function setBusy(value) {
    state.busy = value; document.body.classList.toggle("is-busy", value);
    $("input-fields").disabled = value;
    ["build-brief", "reset", "confirm-skills", "add-skill", "skill-select", "retry", "retry-meta", "market-fallback", "download-report"].forEach((id) => { $(id).disabled = value; });
    $("skill-chips").querySelectorAll("button").forEach((b) => { b.disabled = value; });
    $("followup-panel").querySelectorAll("fieldset, button").forEach((el) => { el.disabled = value; });
    $("cancel-request").hidden = !value; $("coach-form").setAttribute("aria-busy", String(value));
    $("build-brief").firstElementChild.textContent = value ? "Working on your next move…" : state.advisor ? "Rebuild my career brief" : "Build my career brief";
  }
  async function run(task, retry, fallback = false) {
    if (state.busy) return;
    clearError(); const request = ++state.request; const controller = new AbortController(); state.controller = controller; setBusy(true);
    let timedOut = false;
    const timer = setTimeout(() => { timedOut = true; controller.abort(); }, 90000);
    try { await task(controller.signal); }
    catch (error) {
      if (request !== state.request) return;
      status("");
      if (error.name === "AbortError" && !timedOut) status("Request cancelled. Your input is still here. A request already received by the server may finish processing.");
      else showError(timedOut ? new Error("This request took too long. Retry, or use market evidence only. Your input is still here.") : error, retry, fallback);
    } finally { clearTimeout(timer); if (request === state.request) { setBusy(false); state.controller = null; } }
  }
  function switchTab(tab, focus = false) {
    state.tab = tab;
    ["upload", "paste"].forEach((name) => { $(name + "-tab").setAttribute("aria-selected", String(name === tab)); $(name + "-tab").tabIndex = name === tab ? 0 : -1; $(name + "-panel").hidden = name !== tab; });
    if (focus) $(tab + "-tab").focus();
    updateStaleness();
  }
  function updateCount() { $("character-count").textContent = `${$("cv-text").value.length.toLocaleString()} / 15,000`; }
  function requireConsent() {
    if (!$("consent").checked) { $("consent").focus(); throw new Error("Please review your CV and tick the consent checkbox before uploading or requesting AI advice."); }
  }
  function validateText(text) { if (text.trim().length < 10 || text.length > 15000) throw new Error("Add 10–15,000 characters of CV text. Include a project or work example, or try the synthetic sample."); }
  async function upload(signal) {
    requireConsent(); const file = $("cv-file").files[0];
    if (!file) { $("cv-file").focus(); throw new Error("Choose a PDF, DOCX or TXT file, paste your CV, or try the sample."); }
    if (!/\.(pdf|docx|txt)$/i.test(file.name)) throw new Error("Choose a PDF, DOCX or TXT file. For other formats, paste the text instead.");
    if (!file.size || file.size > 4000000) throw new Error(file.size ? "Choose a file up to 4,000,000 bytes (4 MB), or paste its text." : "This file is empty. Choose a CV containing text.");
    status("Reading your uploaded CV on the server…", true);
    const body = new FormData(); body.append("file", file); body.append("consent", "true");
    const data = await api("/api/upload", body, signal); signal.throwIfAborted();
    if (typeof data.text !== "string" || !data.text.trim()) throw new Error("No readable text was found. Scanned PDFs may need OCR; try a DOCX or paste your text.");
    $("cv-text").value = data.text; $("cv-file").value = ""; $("text-label").textContent = "Your extracted CV — review or edit"; state.synthetic = false; $("sample-note").hidden = true; updateCount(); switchTab("paste");
    validateText(data.text); return data.text;
  }
  function buildBrief() {
    run(async (signal) => {
      clearFollowup(); requireConsent(); const selected = target();
      const text = state.tab === "upload" ? await upload(signal) : $("cv-text").value;
      signal.throwIfAborted(); requireConsent(); validateText(text);
      status("Reading your CV to ask a few quick questions…", true);
      let questions = null;
      try {
        // Follow-up questions are optional: any failure goes straight to the brief.
        const questionSignal = typeof AbortSignal.any === "function" && typeof AbortSignal.timeout === "function" ? AbortSignal.any([signal, AbortSignal.timeout(25000)]) : signal;
        questions = await api("/api/questions", {...selected, text, consent:true}, questionSignal);
      } catch (error) { if (signal.aborted) throw error; questions = null; }
      signal.throwIfAborted();
      const valid = list(questions?.questions).filter((q) => q && typeof q.id === "string" && /^q[1-9]$/.test(q.id) && typeof q.question === "string" && ["skill", "detail"].includes(q.type) && (q.type === "detail" || list(q.options).length)).slice(0, 5);
      if (valid.length) { showFollowup({...questions, questions:valid}, selected, text); return; }
      await advise(signal, selected, text, []);
    }, buildBrief, true);
  }
  async function advise(signal, selected, text, answers) {
    status(answers.length ? "Building your career brief with your answers. Waiting for the server…" : "Preparing your career advice and historical market evidence. Waiting for the server…", true);
    const body = {...selected, text, consent:true}; if (answers.length) body.answers = answers;
    const data = await api("/api/advise", body, signal); signal.throwIfAborted();
    if (!data.advisor || typeof data.advisor.summary !== "string" || !data.market || !Array.isArray(data.market.skills)) throw new Error("The career brief was incomplete. Please retry; your CV text is ready in the editor.");
    clearFollowup(); state.answers = answers;
    state.advisor = data.advisor; state.market = data.market; state.briefTarget = selected; state.marketTarget = selected; state.briefText = text;
    state.skills = new Set(list(data.advisor.suggested_skills)); state.confirmed = [...state.skills]; state.reviewed = false; state.completed.clear();
    $("include-excerpts").checked = false; $("export-status").textContent = ""; $("copy-fallback").hidden = true;
    render(); status(data.advisor.mode === "curated" ? "Your curated brief is ready. AI was unavailable; the mode and limitations are shown in your report." : "Your career brief is ready. Review the advice and confirm your detected skills."); revealResults(); emit("brief");
  }
  function showFollowup(data, selected, text) {
    state.followup = {target:selected, text, questions:data.questions};
    $("followup-mode").innerHTML = data.mode === "groq" ? `<span class="badge">AI questions · ${esc(data.model || "model not supplied")}</span>` : '<span class="badge">Curated questions · AI unavailable</span>';
    $("followup-mode").title = data.note || "";
    const total = data.questions.length;
    $("followup-questions").innerHTML = data.questions.map((q, index) => {
      const name = `followup-${q.id}`;
      const head = `<legend><span class="followup-count">${index + 1} of ${total}</span>${esc(q.question)}</legend>${q.why ? `<p id="${name}-why" class="hint followup-why">${esc(q.why)}</p>` : ""}`;
      if (q.type === "skill") return `<fieldset class="followup-question" data-type="skill">${head}<div class="followup-options">${list(q.options).map((option) => `<label class="followup-option"><input type="radio" name="${name}" value="${esc(option)}"${q.why ? ` aria-describedby="${name}-why"` : ""}><span>${esc(option)}</span></label>`).join("")}</div></fieldset>`;
      return `<fieldset class="followup-question" data-type="detail">${head}<label class="sr-only" for="${name}">Your answer (optional)</label><textarea id="${name}" name="${name}" rows="3" maxlength="400" placeholder="Optional. Only if true, e.g. who used it or what changed."${q.why ? ` aria-describedby="${name}-why"` : ""}></textarea></fieldset>`;
    }).join("");
    $("followup-panel").hidden = false;
    status(`${total} quick question${total === 1 ? "" : "s"} before your brief. Answer what’s true, or skip.`);
    $("followup-title").focus({preventScroll:true}); $("followup-panel").scrollIntoView({behavior:"auto", block:"start"});
  }
  function clearFollowup() {
    state.followup = null; $("followup-panel").hidden = true; $("followup-questions").innerHTML = ""; $("followup-mode").textContent = "";
  }
  function followupStale(pending) {
    return !sameTarget(target(), pending.target) || $("cv-text").value !== pending.text || !$("consent").checked || (state.tab === "upload" && !!$("cv-file").files[0]);
  }
  function invalidateFollowup() {
    if (!state.followup) return;
    clearFollowup(); status("Your CV, target or consent changed, so the follow-up questions were cleared. Build your brief again when ready.");
  }
  function followupAnswers(pending) {
    return pending.questions.flatMap((q) => {
      const field = q.type === "skill" ? $("followup-panel").querySelector(`input[name="followup-${q.id}"]:checked`) : $(`followup-${q.id}`);
      const answer = field ? field.value.trim().slice(0, 400) : "";
      return answer ? [{id:q.id, type:q.type, skill:typeof q.skill === "string" ? q.skill.slice(0, 100) : null, question:q.question.slice(0, 300), answer}] : [];
    }).slice(0, 6);
  }
  function continueBrief(skip = false) {
    const pending = state.followup;
    if (!pending || state.busy) return;
    if (followupStale(pending)) { invalidateFollowup(); return; }
    const answers = skip ? [] : followupAnswers(pending);
    const send = () => run(async (signal) => {
      if (state.followup !== pending || followupStale(pending)) throw new Error("Those follow-up questions are out of date. Build your brief again.");
      requireConsent(); await advise(signal, pending.target, pending.text, answers);
    }, send, true);
    send();
  }
  function previewUpload() {
    run(async (signal) => {
      clearFollowup(); await upload(signal); $("consent").checked = false;
      status("Preview ready. Edit or remove personal details below, then tick consent again and build your brief. No AI advice request has been sent."); $("cv-text").focus();
    }, previewUpload);
  }
  function revealResults() { $("results").hidden = false; $("workspace").classList.add("has-results"); $("reset").hidden = false; $("brief-title").focus({preventScroll:true}); $("results").scrollIntoView({behavior:"auto", block:"start"}); }
  function sourceText() { return `${state.meta?.source || "Source metadata unavailable"} · ${state.meta?.year ?? "year unavailable"} · ${state.market?.scope || "scope unavailable"} · ${typeof state.market?.sample_size === "number" ? state.market.sample_size.toLocaleString() : "Unknown number of"} historical postings`; }
  function sourceLink() {
    try { const url = new URL(state.meta?.source_url); return ["https:", "http:"].includes(url.protocol) ? url.href : null; } catch { return null; }
  }
  function priorities() {
    const market = state.market; if (!market) return [];
    // Ranking and percentages come exclusively from the deterministic market response.
    const gaps = list(market.gaps); const candidates = [...gaps, ...list(market.skills).filter((s) => !gaps.some((g) => g.id === s.id))].slice(0, 3);
    return candidates.map((skill) => {
      const advice = sameTarget(state.briefTarget, state.marketTarget) ? list(state.advisor?.gaps).find((g) => g.skill === skill.id) : null;
      const owned = skill.owned === true || state.confirmed.includes(skill.id);
      return {...skill, reason:advice?.reason || (owned ? "Already in your skill list. Make the evidence easy to find in your CV." : "Appears in this historical role sample but is not in your skill list. Missing CV evidence does not mean missing ability."), first_step:advice?.first_step || (owned ? `Choose one real ${skill.label || label(skill.id)} example. Write down the task, your approach and how you checked the result.` : `Check whether you already use ${skill.label || label(skill.id)}. If so, add evidence; otherwise, complete a small introductory exercise and save the output.`)};
    });
  }
  function renderMarket() {
    const m = state.market; if (!m) return;
    const link = sourceLink();
    $("market-source").innerHTML = `<strong>HISTORICAL MARKET EVIDENCE</strong><br>${esc(sourceText())}${link ? ` · <a href="${esc(link)}" target="_blank" rel="noopener noreferrer">View source ↗</a>` : ""}${m.fallback ? `<p class="notice">Only ${esc(m.local_postings ?? "a limited number of")} local postings for this role. Figures use the ${esc(m.scope)}; they are not Kenya-only estimates.</p>` : ""}`;
    $("coverage").innerHTML = `<strong>${esc(pct(m.coverage))}</strong><p><b>Demand-weighted skill coverage</b><br><span class="muted">${state.reviewed ? "Based on your confirmed skills" : "Based on unreviewed skill suggestions"}. Not proficiency or hiring odds.</span></p>`;
    const cards = priorities();
    $("priority-cards").innerHTML = cards.length ? cards.map((s, index) => `<article class="priority-card"><div class="priority-top"><span>0${index + 1}</span><span class="demand">${esc(pct(s.demand_pct))}<br><small>of sample postings</small></span></div><h4>${esc(s.label || label(s.id))}</h4><p>${esc(s.reason)}</p><p class="first-step"><b>Your first move</b><br>${esc(s.first_step)}</p></article>`).join("") : '<p class="empty-note">No ranked skills were returned for this role. Try a different target role.</p>';
    $("market-method").textContent = m.method || "No calculation method was returned by the server.";
    $("jobs").innerHTML = list(m.jobs).length ? list(m.jobs).map((job) => `<article class="job-card"><h4>${esc(job.title)}</h4><p class="muted">${esc(job.country)} · ${esc(state.meta?.year ?? "Year unavailable")} · historical example</p><div class="chips">${list(job.skills).map((s) => `<span class="chip">${esc(s)}</span>`).join("")}</div></article>`).join("") : '<p class="empty-note">No matching examples yet. Confirm skills mentioned in this dataset to find related historical postings.</p>';
    updateStaleness();
  }
  function renderSkills() {
    $("skill-chips").innerHTML = state.skills.size ? [...state.skills].map((id) => `<span class="chip">${esc(label(id))}<button type="button" data-remove-skill="${esc(id)}" aria-label="Remove ${esc(label(id))}" ${state.busy ? "disabled" : ""}>×</button></span>`).join("") : '<p class="muted">No skills selected. Add only skills you can support.</p>';
    $("skill-status").textContent = skillDirty() ? "Unconfirmed edits. Confirm to recalculate market evidence." : state.reviewed ? "Skills confirmed. The AI brief retains its original CV-based assessment." : "Suggested skills are waiting for your review.";
    updateStaleness();
  }
  function answersNote(a) {
    const used = a?.answers_used;
    if (!used || typeof used !== "object") return "";
    const how = {"Used it at work":"work", "Used it in a project or course":"project"};
    const answerFor = (id) => list(state.answers).find((item) => item.type === "skill" && item.skill === id)?.answer;
    const parts = [...list(used.added).map((id) => `+ ${label(id)}${how[answerFor(id)] ? ` (${how[answerFor(id)]})` : ""}`), ...list(used.removed).map((id) => `− ${label(id)} (not yet)`)];
    const details = Number.isInteger(used.details) && used.details > 0 ? used.details : 0;
    if (details) parts.push(`${details} detail${details === 1 ? "" : "s"} used`);
    return parts.length ? `Your answers shaped this brief: ${parts.join(", ")}.` : "Your answers were noted. They did not change your detected skills.";
  }
  function render() {
    const a = state.advisor;
    $("brief-title").textContent = a ? "Your next move, made clearer." : "Start with the market evidence.";
    $("brief-context").textContent = `${(state.briefTarget || state.marketTarget).role} · ${(state.briefTarget || state.marketTarget).country}${state.synthetic ? " · synthetic sample" : ""}`;
    $("ai-provenance").innerHTML = a ? `<span class="badge mode">${a.mode === "curated" ? "Curated fallback · no AI assessment" : `AI mode: ${esc(a.mode || "not supplied")}`}</span><span class="badge">Model: ${esc(a.model || (a.mode === "curated" ? "none (curated)" : "not supplied"))}</span>` : '<span class="badge mode">Market evidence only · no AI brief</span><span class="badge">Model: none</span>';
    const note = answersNote(a); $("answers-used").textContent = note; $("answers-used").hidden = !note;
    $("advisor-summary").textContent = a?.summary || "AI advice could not be generated. You can still choose your skills and use historical market demand to focus your next step. Confirm your skills below to make this view useful.";
    $("strengths").innerHTML = list(a?.strengths).map((s) => `<details><summary>Evidence for ${esc(label(s.skill))}</summary><blockquote>${esc(s.evidence)}</blockquote></details>`).join("");
    $("cv-improvements").innerHTML = list(a?.cv_improvements).length ? a.cv_improvements.map((item) => `<article class="rewrite-card"><div class="rewrite-pair"><div class="rewrite-side"><p class="eyebrow">BEFORE</p><p>${esc(item.before)}</p></div><div class="rewrite-side after"><p class="eyebrow">SUGGESTED REWRITE</p><p>${esc(item.after)}</p></div></div><p class="rewrite-reason">${esc(item.reason)}</p></article>`).join("") : '<p class="empty-note">No grounded rewrite was returned. Choose a real CV bullet and clarify the task, tool and outcome. Add a metric only if you can verify it.</p>';
    $("seven-day-plan").innerHTML = list(a?.seven_day_plan).map((day, index) => `<li class="${state.completed.has(index) ? "completed" : ""}"><label><input type="checkbox" data-day="${index}" ${state.completed.has(index) ? "checked" : ""} aria-label="Mark day ${esc(day.day)} complete"><span class="day-number">Day ${esc(day.day)}</span><span><span class="day-action">${esc(day.action)}</span><span class="deliverable"><b>Keep:</b> ${esc(day.deliverable)}</span></span></label></li>`).join("");
    if (!list(a?.seven_day_plan).length) $("seven-day-plan").innerHTML = '<li class="muted">No daily plan was returned. Rebuild your brief for personalised actions.</li>';
    $("copy-checklist").disabled = !list(a?.seven_day_plan).length;
    $("whatsapp-checklist").hidden = !list(a?.seven_day_plan).length;
    $("interview-question").textContent = a?.interview?.question || "Rebuild your career brief to get a question tailored to your CV and target role.";
    $("interview-rubric").textContent = a?.interview?.what_good_looks_like || "No interview guidance was returned.";
    $("interview-guidance").open = false;
    $("limitations").innerHTML = [...list(a?.limitations), "Historical sample, not a representative labour-market survey or a live vacancy feed.", "Skill suggestions are self-reported evidence, not verified ability. Review AI advice for accuracy."].map((text) => `<li>${esc(text)}</li>`).join("");
    $("skills-title").textContent = !a ? "Review your skills" : a.mode === "curated" ? "Review detected skills (keyword fallback)" : "Review AI-detected skills";
    renderMarket(); renderSkills();
  }
  function updateStaleness() {
    if (!state.market) return;
    const notes = [];
    if (briefStale()) notes.push(`AI brief is stale: it still reflects ${state.briefTarget.role} / ${state.briefTarget.country} and the previous CV text. Rebuild to update the advice, rewrites, plan and interview.`);
    else if (state.reviewed && state.advisor) notes.push("Market evidence uses your confirmed skills. The AI brief remains based on the original CV; confirming skills does not rewrite AI advice.");
    if (!sameTarget(target(), state.marketTarget)) notes.push(`Market evidence still reflects ${state.marketTarget.role} / ${state.marketTarget.country}. Confirm skills to recalculate for your current target.`);
    $("stale-note").textContent = notes.join(" "); $("stale-note").hidden = !notes.length;
    $("market-state").textContent = `Market target: ${state.marketTarget.role} / ${state.marketTarget.country}. ${skillDirty() ? "Skill edits are not yet included in these figures." : state.reviewed ? "Human-confirmed skills. AI coaching is separate." : "Review the detected skills below to confirm this starting point."}`;
  }
  function confirmSkills() {
    run(async (signal) => {
      if (!state.meta) throw new Error("Reconnect to load the skill vocabulary before confirming skills.");
      const selected = target(); const skills = [...state.skills]; status("Recalculating market evidence from your confirmed skills…", true);
      const market = await api("/api/analyze", {...selected, skills}, signal); signal.throwIfAborted();
      if (!Array.isArray(market.skills)) throw new Error("Market evidence was incomplete. Please retry.");
      state.market = market; state.marketTarget = selected; state.confirmed = skills; state.reviewed = true; renderMarket(); renderSkills(); status("Market evidence updated. Your AI brief has not been regenerated."); emit("skills");
    }, confirmSkills);
  }
  function marketFallback() {
    run(async (signal) => {
      const selected = target(); status("Loading historical market evidence only. No CV text is sent in this request…", true);
      const skills = [...state.skills]; const market = await api("/api/analyze", {...selected, skills}, signal); signal.throwIfAborted();
      if (!Array.isArray(market.skills)) throw new Error("Market evidence was incomplete. Please retry.");
      state.market = market; state.marketTarget = selected; state.confirmed = skills; state.reviewed = false; render(); revealResults(); status("Market evidence is ready. Review your skills to personalise the calculation; rebuild for AI advice."); emit("brief");
    }, marketFallback);
  }
  function checklist() {
    const selected = state.briefTarget || target();
    return `Njia — action checklist\n${selected.role} / ${selected.country}${briefStale() ? "\nSTALE: based on the previous CV or target. Rebuild for current advice." : ""}\n\n` + list(state.advisor?.seven_day_plan).map((d, i) => `[${state.completed.has(i) ? "x" : " "}] Day ${d.day}: ${d.action}\n    Deliverable: ${d.deliverable}`).join("\n\n");
  }
  async function copyText(text, message) {
    try { await navigator.clipboard.writeText(text); $("export-status").textContent = message; status(message); }
    catch { $("copy-fallback").hidden = false; $("copy-text").value = text; $("copy-text").focus(); $("copy-text").select(); $("export-status").textContent = "Automatic copying is unavailable. Select and copy the text below."; }
  }
  function whatsappText() {
    const selected = state.briefTarget || target();
    const days = list(state.advisor?.seven_day_plan).map((d, i) => `${state.completed.has(i) ? "✅" : "⬜"} Day ${d.day}: ${String(d.action).slice(0, 180)}`);
    return `Njia — my 7-day plan (${selected.role} / ${selected.country})${briefStale() ? "\n(Based on my previous CV or target.)" : ""}\n\n${days.join("\n")}\n\n${new URL("/", location.origin).href}`;
  }
  function downloadReport() {
    if (!state.market) return;
    const a = state.advisor, m = state.market, include = $("include-excerpts").checked;
    const paragraph = (text) => `<p>${esc(text)}</p>`;
    const targetLabel = (t) => `${t.role} / ${t.country}`;
    let html = `<header><p>NJIA / CAREER BRIEF</p><h1>Your next move, made clearer.</h1>${paragraph(`Created ${new Date().toLocaleDateString("en-KE")} · ${targetLabel(state.briefTarget || state.marketTarget)}`)}</header>`;
    html += paragraph(`Mode: ${a?.mode || "market only"} · Model: ${a?.model || "none"}`);
    if (answersNote(a)) html += paragraph(`${answersNote(a)} Follow-up answers are self-reported.`);
    if (briefStale()) html += '<p class="notice">STALE AI BRIEF: the current CV or target has changed. This report preserves the original advice.</p>';
    if (!sameTarget(target(), state.marketTarget)) html += paragraph("Market figures reflect the market target below, not the newly selected target.");
    if (skillDirty()) html += paragraph("Unconfirmed skill edits are excluded from these market figures.");
    html += paragraph("Personalised career advice may reveal CV details. Review this report before sharing. Raw CV text is not attached.");
    html += `<h2>The short version</h2>${paragraph(a?.summary || "Market evidence only. No AI advice was generated.")}`;
    if (include && list(a?.strengths).length) html += `<h2>CV evidence</h2>${a.strengths.map((s) => `<h3>${esc(label(s.skill))}</h3>${paragraph(s.evidence)}`).join("")}`;
    html += `<h2>Historical market evidence</h2>${paragraph(targetLabel(state.marketTarget))}${paragraph(sourceText())}${paragraph(state.meta?.source_url || "Source URL unavailable")}${paragraph(`Coverage: ${pct(m.coverage)} — ${m.method || "Method unavailable"}`)}${paragraph(`Skills used (${state.reviewed ? "human-confirmed" : "unreviewed suggestions"}): ${state.confirmed.map(label).join(", ") || "none"}`)}`;
    if (m.fallback) html += paragraph(`Regional fallback: ${m.local_postings ?? "Unknown"} local postings; using ${m.scope}. These are not Kenya-only estimates.`);
    html += `<h2>Your priorities</h2>${priorities().map((s) => `<h3>${esc(s.label || label(s.id))} · ${esc(pct(s.demand_pct))} of sample postings</h3>${paragraph(s.reason)}${paragraph(`First move: ${s.first_step}`)}`).join("")}`;
    if (include) html += `<h2>CV rewrites — verify before using</h2>${list(a?.cv_improvements).map((s) => `<article><h3>Before</h3>${paragraph(s.before)}<h3>Suggested rewrite</h3>${paragraph(s.after)}${paragraph(s.reason)}</article>`).join("") || paragraph("No grounded rewrites were returned.")}`;
    else html += paragraph("CV evidence quotes and before/after rewrites were excluded by your download preference. Other personalised advice may still refer to your experience.");
    html += `<h2>Seven-day action checklist</h2><pre>${esc(checklist())}</pre><h2>Interview practice</h2>${paragraph(a?.interview?.question || "No question returned.")}${paragraph(a?.interview?.what_good_looks_like || "")}`;
    html += `<h2>Method & limitations</h2>${paragraph("Skill confirmation recalculates market evidence only; it does not regenerate the AI brief.")}<ul>${[...list(a?.limitations), "Historical job examples are not live vacancies. Coverage is not a hiring probability or verified proficiency score.", "This sample is not a representative labour-market survey."].map((s) => `<li>${esc(s)}</li>`).join("")}</ul>`;
    const documentText = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'"><title>Njia — career brief</title><style>body{max-width:800px;margin:40px auto;padding:0 24px;color:#142638;background:#fffefb;font:17px/1.65 Arial,sans-serif}h1,h2,h3{font-family:Georgia,serif;line-height:1.25}h1{font-size:42px}h2{margin-top:34px;border-top:1px solid #ddd;padding-top:20px}p,li{white-space:pre-wrap;overflow-wrap:anywhere}pre{white-space:pre-wrap;font:inherit}header{border-bottom:3px solid #b7441e}article,.notice{padding:18px;background:#f3eee5;margin:14px 0}@media print{body{margin:0;max-width:none}article{break-inside:avoid}}</style></head><body>${html}</body></html>`;
    const url = URL.createObjectURL(new Blob([documentText], {type:"text/html;charset=utf-8"})); const link = document.createElement("a"); link.href = url; link.download = "njia-career-brief.html"; document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 60000);
    $("export-status").textContent = `Report download requested. ${include ? "CV excerpts and rewrites are included." : "CV excerpts and rewrites are excluded."} Review before sharing.`;
  }
  async function loadMeta() {
    $("retry-meta").disabled = true;
    try {
      const meta = await api("/api/meta", undefined, AbortSignal.timeout(20000));
      if (!Array.isArray(meta.roles) || !meta.roles.length || !Array.isArray(meta.skills) || !Array.isArray(meta.countries) || !meta.countries.length) throw new Error("Incomplete metadata");
      state.meta = meta;
      // Avoid changing user input underneath an active request or an existing brief.
      if (!state.busy) {
        const selected = target();
        $("country").innerHTML = meta.countries.map((c) => `<option>${esc(c.name)}</option>`).join(""); $("country").value = meta.countries.some((c) => c.name === selected.country) ? selected.country : meta.countries[0].name;
        $("role").innerHTML = meta.roles.map((r) => `<option>${esc(r)}</option>`).join(""); $("role").value = meta.roles.includes(selected.role) ? selected.role : meta.roles[0];
      }
      $("skill-select").innerHTML = '<option value="">Add a skill…</option>' + meta.skills.map((s) => `<option value="${esc(s.id)}">${esc(s.label)}</option>`).join("");
      $("service-note").textContent = `Historical ${meta.year ?? "year unavailable"} tech/data evidence. AI mode and model are shown with each brief.`; $("retry-meta").hidden = !state.busy; $("retry-meta").textContent = "Refresh roles";
      if (state.market) { renderMarket(); renderSkills(); }
    } catch { $("service-note").textContent = "Role and skill metadata could not load. Reconnect to restore all choices. You can still try the default Kenya / Data Analyst brief."; $("retry-meta").hidden = false; $("retry-meta").textContent = "Reconnect"; }
    finally { $("retry-meta").disabled = false; }
  }
  $("coach-form").addEventListener("submit", (event) => { event.preventDefault(); if (state.followup && !$("followup-panel").hidden) continueBrief(false); else buildBrief(); });
  $("followup-submit").addEventListener("click", () => continueBrief(false));
  $("followup-skip").addEventListener("click", () => continueBrief(true));
  ["upload", "paste"].forEach((tab) => {
    $(tab + "-tab").addEventListener("click", () => switchTab(tab));
    $(tab + "-tab").addEventListener("keydown", (event) => { if (["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) { event.preventDefault(); switchTab(event.key === "Home" ? "upload" : event.key === "End" ? "paste" : tab === "upload" ? "paste" : "upload", true); } });
  });
  $("sample").addEventListener("click", () => {
    $("cv-file").value = ""; $("cv-text").value = SAMPLE; $("consent").checked = false; state.synthetic = true; $("sample-note").hidden = false; $("text-label").textContent = "Your experience, in your words"; clearFollowup();
    if ([...$("country").options].some((o) => o.value === "Kenya")) $("country").value = "Kenya";
    if ([...$("role").options].some((o) => o.value === "Data Analyst")) $("role").value = "Data Analyst";
    updateCount(); switchTab("paste"); clearError(); status("Fictional sample loaded. Review it and tick consent to build an example brief."); $("cv-text").focus();
  });
  $("cv-file").addEventListener("change", () => { $("file-name").textContent = $("cv-file").files[0]?.name || "PDF, DOCX or TXT · up to 4 MB"; $("consent").checked = false; invalidateFollowup(); clearError(); updateStaleness(); });
  $("cv-text").addEventListener("input", () => { updateCount(); invalidateFollowup(); clearError(); updateStaleness(); });
  ["country", "role"].forEach((id) => $(id).addEventListener("change", () => { invalidateFollowup(); updateStaleness(); }));
  $("consent").addEventListener("change", () => { invalidateFollowup(); if (!$("consent").checked && state.busy) state.controller?.abort(); });
  $("preview-upload").addEventListener("click", previewUpload);
  $("cancel-request").addEventListener("click", () => state.controller?.abort());
  $("retry").addEventListener("click", () => state.retry?.());
  $("retry-meta").addEventListener("click", loadMeta);
  $("market-fallback").addEventListener("click", marketFallback);
  $("confirm-skills").addEventListener("click", confirmSkills);
  $("add-skill").addEventListener("click", () => { const id = $("skill-select").value; if (!id) { $("skill-select").focus(); return; } if (state.skills.size >= 100 && !state.skills.has(id)) { $("skill-status").textContent = "You can confirm up to 100 skills. Remove one before adding another."; return; } state.skills.add(id); $("skill-select").value = ""; renderSkills(); $("skill-select").focus(); });
  $("skill-chips").addEventListener("click", (event) => { const button = event.target.closest("[data-remove-skill]"); if (!button || state.busy) return; state.skills.delete(button.dataset.removeSkill); renderSkills(); $("skill-select").focus(); });
  $("seven-day-plan").addEventListener("change", (event) => { if (!event.target.matches("[data-day]")) return; const day = Number(event.target.dataset.day); event.target.checked ? state.completed.add(day) : state.completed.delete(day); event.target.closest("li").classList.toggle("completed", event.target.checked); });
  $("copy-checklist").addEventListener("click", () => copyText(checklist(), "Action checklist copied. It contains personalised advice; review before sharing."));
  $("whatsapp-checklist").addEventListener("click", (event) => {
    if (!list(state.advisor?.seven_day_plan).length) { event.preventDefault(); return; }
    event.currentTarget.href = `https://wa.me/?text=${encodeURIComponent(whatsappText())}`;
  });
  $("download-report").addEventListener("click", downloadReport);
  $("share-app").addEventListener("click", async () => {
    const share = {title:"Njia — a clearer next move", text:"A practical career coach for your next move. Try Njia.", url:new URL("/", location.origin).href};
    if (navigator.share) { try { await navigator.share(share); $("export-status").textContent = "Njia app link shared. No CV or career brief was included."; } catch (error) { if (error.name !== "AbortError") await copyText(share.url, "Public Njia link copied. No CV or brief is included."); } }
    else await copyText(share.url, "Public Njia link copied. No CV or brief is included.");
  });
  $("edit-input").addEventListener("click", () => { $("input-section").scrollIntoView({behavior:"auto"}); (state.tab === "paste" ? $("cv-text") : $("cv-file")).focus({preventScroll:true}); });
  $("reset").addEventListener("click", () => {
    state.advisor = null; state.market = null; state.briefTarget = null; state.marketTarget = null; state.briefText = null; state.skills.clear(); state.confirmed = []; state.completed.clear(); state.reviewed = false; state.synthetic = false; state.answers = [];
    clearFollowup(); $("answers-used").hidden = true;
    $("coach-form").reset(); $("cv-text").value = ""; $("copy-text").value = ""; $("copy-fallback").hidden = true; $("sample-note").hidden = true; $("file-name").textContent = "PDF, DOCX or TXT · up to 4 MB";
    if ([...$("country").options].some((o) => o.value === "Kenya")) $("country").value = "Kenya";
    if ([...$("role").options].some((o) => o.value === "Data Analyst")) $("role").value = "Data Analyst";
    $("text-label").textContent = "Your experience, in your words"; $("include-excerpts").checked = false; $("results").hidden = true; $("workspace").classList.remove("has-results"); $("reset").hidden = true;
    // Remove previous personal output from the DOM as well as application state.
    ["advisor-summary", "strengths", "cv-improvements", "seven-day-plan", "interview-question", "interview-rubric", "skill-chips", "priority-cards", "jobs", "limitations", "export-status", "answers-used"].forEach((id) => { $(id).textContent = ""; });
    clearError(); status(""); updateCount(); switchTab("upload"); setBusy(false); $("input-section").scrollIntoView({behavior:"auto"}); $("cv-file").focus({preventScroll:true});
    emit("reset");
  });
  loadMeta();
})();
