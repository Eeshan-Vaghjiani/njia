"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (c) => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"}[c]));
  const list = (value) => Array.isArray(value) ? value : [];
  const label = (id) => window.NjiaCoach?.label?.(id) || id;
  const state = {request:0, controller:null, detail:null, remote:null, remoteError:null, web:null, webStatus:"idle"};

  function safeUrl(value) {
    try { const url = new URL(String(value)); return url.protocol === "https:" || url.protocol === "http:" ? url.href : null; } catch { return null; }
  }
  function posted(iso) {
    if (typeof iso !== "string" || !/^\d{4}-\d{2}-\d{2}/.test(iso)) return "";
    const days = Math.floor((Date.now() - Date.parse(`${iso.slice(0, 10)}T00:00:00Z`)) / 86400000);
    if (!Number.isFinite(days)) return "";
    if (days <= 0) return "Posted today";
    if (days === 1) return "Posted yesterday";
    if (days < 45) return `Posted ${days} days ago`;
    const months = Math.round(days / 30);
    return `Posted ${months} months ago`;
  }
  async function post(body, signal) {
    let response;
    try { response = await fetch("/api/jobs", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body), signal}); }
    catch (error) { if (error.name === "AbortError") throw error; throw new Error("Could not reach Njia to load live jobs. Check your connection and retry."); }
    let data;
    try { data = await response.json(); } catch { throw new Error("Live jobs returned an unreadable response. Please retry."); }
    if (!response.ok || !data || !Array.isArray(data.jobs)) throw new Error(typeof data?.detail === "string" ? data.detail : "Live jobs are unavailable right now. Please retry.");
    return data;
  }

  function meter(job) {
    const found = Number.isInteger(job.detected_count) ? job.detected_count : list(job.matched_skills).length + list(job.missing_skills).length;
    if (typeof job.match_pct !== "number" || !Number.isFinite(job.match_pct)) {
      return '<div class="match-meter unknown"><p><b>Match not calculated</b> <span class="muted">· we could not detect specific skills in this posting. Read it to judge the fit.</span></p></div>';
    }
    const pct = Math.max(0, Math.min(100, Math.round(job.match_pct)));
    const matched = list(job.matched_skills).length;
    const level = pct >= 60 ? "strong" : pct >= 30 ? "partial" : "low";
    return `<div class="match-meter ${level}" role="img" aria-label="Skill match ${pct}%: you have ${matched} of ${found} skills detected in this posting"><div class="match-top"><strong>${pct}%</strong><span>You have ${matched} of ${found} skill${found === 1 ? "" : "s"} we detected</span></div><div class="match-bar" aria-hidden="true"><span style="width:${pct}%"></span></div></div>`;
  }
  function card(job) {
    const url = safeUrl(job.url);
    const via = job.kind === "local" ? (job.source || "web search") : "Himalayas";
    const badges = [`<span class="badge kind ${job.kind === "local" ? "local" : "remote"}">${job.kind === "local" ? "Local" : "Remote"}</span>`,
      ...list(job.seniority).map((s) => `<span class="badge">${esc(s)}</span>`),
      job.employment_type ? `<span class="badge">${esc(job.employment_type)}</span>` : ""].join("");
    const meta = [job.eligibility, posted(job.posted), job.salary].filter(Boolean).map(esc).join(" · ");
    const have = list(job.matched_skills).map((id) => `<span class="chip have">✓ ${esc(label(id))}</span>`).join("");
    const gaps = list(job.missing_skills).slice(0, 6).map((id) => `<span class="chip gap">${esc(label(id))}</span>`).join("");
    return `<article class="live-job" data-kind="${job.kind === "local" ? "local" : "remote"}">
      <div class="live-job-head"><h4>${esc(job.title)}</h4><p class="live-job-company">${esc(job.company || "Company not listed")}${job.location ? ` · ${esc(job.location)}` : ""}</p></div>
      <div class="live-job-badges">${badges}</div>
      ${meta ? `<p class="live-job-meta">${meta}</p>` : ""}
      ${meter(job)}
      ${have ? `<p class="chip-label">In your skills</p><div class="chips">${have}</div>` : ""}
      ${gaps ? `<p class="chip-label">Mentioned in the posting, not in your list</p><div class="chips">${gaps}</div>` : ""}
      <div class="live-job-actions">${url ? `<a class="apply-link" href="${esc(url)}" target="_blank" rel="noopener noreferrer">View &amp; apply ↗</a>` : '<span class="muted">No safe link available</span>'}<span class="via">via ${job.kind === "local" ? esc(via) : '<a href="https://himalayas.app" target="_blank" rel="noopener noreferrer">Himalayas</a>'}</span>${job.kind === "local" ? '<span class="verify">Found via web search · verify on source</span>' : ""}</div>
    </article>`;
  }
  const skeleton = (count) => Array.from({length:count}, () => '<div class="live-job-skeleton" aria-hidden="true"><span></span><span></span><span></span></div>').join("");
  function notes(data) {
    const items = [...new Set([...list(state.remote?.notes), ...list(data?.notes)])];
    return items.length ? `<details class="live-jobs-notes"><summary>How these jobs are chosen</summary><ul>${items.map((n) => `<li>${esc(n)}</li>`).join("")}</ul></details>` : "";
  }

  function render() {
    const root = $("live-jobs");
    if (!root || !state.detail) return;
    const t = state.detail.target || {};
    const role = esc(t.role || "your target role"), country = esc(t.country || "your country");
    let html = "";
    if (state.remoteError || (state.remote && state.remote.status === "unavailable")) {
      html += `<div class="notice live-jobs-error" role="alert"><p>${esc(state.remoteError || state.remote.message || "Remote listings are unavailable right now.")}</p><button type="button" class="secondary-button" data-jobs-retry>Try again</button></div>`;
    } else if (!state.remote) {
      html += `<p class="live-jobs-headline" role="status">Finding remote ${role} jobs open to applicants in ${country}…</p>${skeleton(2)}`;
    } else {
      const jobs = list(state.remote.jobs), total = state.remote.total_available;
      const query = state.remote.query ? `matching “${esc(state.remote.query)}” ` : "";
      html += typeof total === "number" && total > 0
        ? `<p class="live-jobs-headline"><strong>${esc(total.toLocaleString())}</strong> remote jobs ${query}are open to applicants in ${country} right now${jobs.length ? " · your best matches below" : ""}</p>`
        : jobs.length ? `<p class="live-jobs-headline">Remote ${role} jobs open to applicants in ${country} · your best matches below</p>` : "";
      html += jobs.length ? `<div class="live-jobs-list">${jobs.map(card).join("")}</div><p class="live-jobs-credit">Remote listings via <a href="https://himalayas.app" target="_blank" rel="noopener noreferrer">Himalayas</a>, the original source. Apply on the listing page.</p>`
        : `<p class="empty-note">No open remote ${role} listings on Himalayas matched this role for applicants in ${country} right now. Try again later or pick a related role.</p>`;
    }
    html += '<div class="live-jobs-web">';
    if (state.webStatus === "loading") {
      html += `<p class="live-jobs-subhead" role="status">Searching the web for local ${role} postings in ${country}… this can take up to a minute.</p>${skeleton(1)}`;
    } else if (state.webStatus === "error" || state.web?.status === "unavailable") {
      html += `<div class="notice"><p>${esc(state.web?.message || "Local web search did not respond.")} Remote listings above are unaffected.</p><button type="button" class="text-button" data-jobs-retry-web>Retry local search ↻</button></div>`;
    } else if (state.web?.status === "not_configured") {
      html += `<p class="empty-note">${esc(state.web.message || "Local web search is not available on this server.")}</p>`;
    } else if (state.web) {
      const jobs = list(state.web.jobs);
      html += jobs.length ? `<p class="live-jobs-subhead"><strong>Local postings in ${country}</strong> · found via web search, verify on source</p><div class="live-jobs-list">${jobs.map(card).join("")}</div>`
        : `<p class="empty-note">No verifiable local ${role} postings in ${country} were found by web search just now. Check local job boards directly.</p>`;
    }
    html += "</div>";
    html += notes(state.web);
    root.innerHTML = html;
    root.setAttribute("aria-busy", String(!state.remote && !state.remoteError || state.webStatus === "loading"));
  }

  function fetchWeb(body, id, signal) {
    state.webStatus = "loading"; state.web = null;
    post({...body, source:"web"}, signal).then((data) => { if (id !== state.request) return; state.web = data; state.webStatus = "done"; render(); })
      .catch((error) => { if (error.name === "AbortError" || id !== state.request) return; state.webStatus = "error"; render(); });
  }
  function load(detail) {
    const t = detail?.target;
    if (!t?.country || !t?.role) return;
    state.controller?.abort();
    const controller = new AbortController(), id = ++state.request;
    Object.assign(state, {controller, detail, remote:null, remoteError:null, web:null});
    const body = {country:t.country, role:t.role, skills:[...new Set(list(detail.skills))].slice(0, 100)};
    state.body = body;
    post({...body, source:"remote"}, controller.signal).then((data) => { if (id !== state.request) return; state.remote = data; const refresh = $("refresh-jobs"); if (refresh) refresh.hidden = false; render(); })
      .catch((error) => { if (error.name === "AbortError" || id !== state.request) return; state.remoteError = error.message; render(); });
    fetchWeb(body, id, controller.signal);
    render();
  }
  function reset() {
    state.controller?.abort();
    state.request += 1;
    Object.assign(state, {controller:null, detail:null, remote:null, remoteError:null, web:null, webStatus:"idle", body:null});
    const root = $("live-jobs"); if (root) { root.innerHTML = ""; root.removeAttribute("aria-busy"); }
    const refresh = $("refresh-jobs"); if (refresh) refresh.hidden = true;
  }
  const latest = () => window.NjiaCoach?.snapshot?.() || state.detail;

  document.addEventListener("njia:brief", (event) => load(event.detail));
  document.addEventListener("njia:skills", (event) => load(event.detail));
  document.addEventListener("njia:reset", reset);
  document.addEventListener("click", (event) => {
    const target = event.target instanceof Element ? event.target : null;
    if (!target) return;
    if (target.closest("#refresh-jobs") || target.closest("[data-jobs-retry]")) load(latest());
    else if (target.closest("[data-jobs-retry-web]") && state.body && state.controller) { fetchWeb(state.body, state.request, state.controller.signal); render(); }
  });
})();
