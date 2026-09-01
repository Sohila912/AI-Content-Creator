const state = {
  scriptType: "Explainer",
  tone: "Professional",
  script: "",
  generating: false,
  accentIndex: 0
};

const accents = ["#9b7cff", "#ff62b0", "#5ee7f7", "#7ee787", "#ffb86b"];

function $(id){ return document.getElementById(id); }

function showToast(message){
  const toast = $("toast");
  if(!toast) return;
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2200);
}

async function loadConfig(){
  try{
    const res = await fetch("/config");
    const cfg = await res.json();
    document.querySelectorAll("[data-brand]").forEach(el => el.textContent = cfg.brand_name || "Content Studio");
    document.title = `${cfg.brand_name || "Content Studio"} • Studio`;
  }catch(_){}
}

function setupChips(containerId, key){
  const container = $(containerId);
  if(!container) return;
  container.querySelectorAll(".chip").forEach(btn => {
    btn.addEventListener("click", () => {
      container.querySelectorAll(".chip").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      state[key] = btn.dataset.value;
    });
  });
}

function setupTheme(){
  const btn = $("themeBtn");
  if(!btn) return;
  btn.addEventListener("click", () => {
    state.accentIndex = (state.accentIndex + 1) % accents.length;
    document.documentElement.style.setProperty("--accent", accents[state.accentIndex]);
    showToast("Accent updated");
  });
}

function setupScriptPage(){
  if(!$("generateBtn")) return;

  setupChips("scriptType", "scriptType");
  setupChips("tone", "tone");
  setupTheme();

  $("topic").addEventListener("input", e => $("charCount").textContent = e.target.value.length);

  $("resetBtn").addEventListener("click", () => {
    $("topic").value = "";
    $("audience").value = "General audience";
    $("cta").value = "End with a natural call to action.";
    $("duration").value = "2–3 minutes";
    $("platform").value = "YouTube";
    $("language").value = "English";
    document.querySelectorAll(".chip-row").forEach(row => {
      const first = row.querySelector(".chip");
      row.querySelectorAll(".chip").forEach(b => b.classList.remove("active"));
      first.classList.add("active");
    });
    state.scriptType = "Explainer";
    state.tone = "Professional";
    $("charCount").textContent = "0";
    showToast("Brief reset");
  });

  $("generateBtn").addEventListener("click", generateStream);
  $("copyBtn").addEventListener("click", copyScript);
  $("downloadBtn").addEventListener("click", downloadScript);
}

function getBrief(){
  return {
    topic: $("topic").value.trim(),
    script_type: state.scriptType,
    tone: state.tone,
    duration: $("duration").value,
    platform: $("platform").value,
    audience: $("audience").value.trim() || "General audience",
    language: $("language").value,
    cta: $("cta").value.trim() || "End with a natural call to action.",
    style: state.tone === "Cinematic" ? "Cinematic, visual and atmospheric" : "Clear, engaging and conversational"
  };
}

async function generateStream(){
  if(state.generating) return;
  const brief = getBrief();

  if(!brief.topic){
    showToast("Add a topic or concept first");
    $("topic").focus();
    return;
  }

  state.generating = true;
  state.script = "";
  const btn = $("generateBtn");
  btn.disabled = true;
  $("generateLabel").textContent = "Generating live…";
  $("outputStatus").textContent = "Writing in real time";
  $("wordCount").textContent = "0 words";
  $("scriptOutput").innerHTML = '<div class="stream-cursor"></div>';

  try{
    const response = await fetch("/generate-script-stream", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify(brief)
    });

    if(!response.ok){
      const err = await response.json().catch(() => ({}));
      throw new Error(err.error || "Generation failed");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while(true){
      const {value, done} = await reader.read();
      if(done) break;

      buffer += decoder.decode(value, {stream:true});
      const events = buffer.split("\n\n");
      buffer = events.pop();

      for(const raw of events){
        const line = raw.split("\n").find(x => x.startsWith("data: "));
        if(!line) continue;

        const payload = JSON.parse(line.slice(6));
        if(payload.type === "chunk"){
          state.script += payload.text;
          renderScript();
        }else if(payload.type === "done"){
          $("outputStatus").textContent = "Complete · saved locally";
          $("wordCount").textContent = `${payload.word_count || state.script.split(/\s+/).filter(Boolean).length} words`;
        }else if(payload.type === "error"){
          throw new Error(payload.error);
        }
      }
    }

    $("outputStatus").textContent = "Complete";
    localStorage.setItem("lastScript", state.script);
  }catch(err){
    $("outputStatus").textContent = "Generation error";
    $("scriptOutput").textContent = `Something went wrong:\n\n${err.message}`;
    showToast(err.message);
  }finally{
    state.generating = false;
    btn.disabled = false;
    $("generateLabel").textContent = "Generate live script";
  }
}

function renderScript(){
  $("scriptOutput").textContent = state.script;
  $("scriptOutput").scrollTop = $("scriptOutput").scrollHeight;
  $("wordCount").textContent = `${state.script.split(/\s+/).filter(Boolean).length} words`;
}

async function copyScript(){
  if(!state.script){ showToast("Nothing to copy yet"); return; }
  await navigator.clipboard.writeText(state.script);
  showToast("Script copied");
}

function downloadScript(){
  if(!state.script){ showToast("Generate a script first"); return; }
  const blob = new Blob([state.script], {type:"text/plain;charset=utf-8"});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "script.txt";
  a.click();
  URL.revokeObjectURL(url);
  showToast("Script exported");
}

async function searchTopics(){
  const query = $("query").value.trim();
  if(!query){ showToast("Enter a subject to explore"); $("query").focus(); return; }

  const btn = $("searchBtn");
  btn.disabled = true;
  btn.innerHTML = "<span>◌</span> Discovering…";

  try{
    const response = await fetch("/search-topics", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({
        query,
        time_range: $("timeRange").value,
        max_results: Number($("maxResults").value)
      })
    });

    const data = await response.json();
    if(!response.ok || !data.success) throw new Error(data.error || "Search failed");
    renderTopics(data.topics || []);
  }catch(err){
    $("results").innerHTML = `<div class="empty-state"><div><div class="empty-icon">!</div><h3>Couldn't load discoveries</h3><p>${escapeHtml(err.message)}</p></div></div>`;
  }finally{
    btn.disabled = false;
    btn.innerHTML = "<span>✦</span> Discover topics";
  }
}

function renderTopics(topics){
  $("resultCount").textContent = `${topics.length} ${topics.length === 1 ? "idea" : "ideas"}`;
  $("resultsTitle").textContent = topics.length ? "Fresh discoveries" : "No discoveries yet";

  if(!topics.length){
    $("results").innerHTML = '<div class="empty-state"><div><div class="empty-icon">⌁</div><h3>No results found</h3><p>Try a broader or more specific query.</p></div></div>';
    return;
  }

  $("results").innerHTML = topics.map((t, i) => `
    <article class="topic-card">
      <div class="topic-number">${String(i+1).padStart(2,"0")}</div>
      <h3>${escapeHtml(t.title || "Untitled")}</h3>
      <p>${escapeHtml(t.description || "No description available.")}</p>
      <div class="source"><span>${escapeHtml(t.source_domain || "Web source")}</span><span>${t.published_date ? escapeHtml(t.published_date) : "Recent"}</span></div>
      <div class="topic-actions">
        <button class="small-btn use-topic" data-topic="${escapeAttr(t.title || "")}">Use for script →</button>
        ${t.url ? `<a class="small-btn" href="${escapeAttr(t.url)}" target="_blank" rel="noopener">Source ↗</a>` : ""}
      </div>
    </article>
  `).join("");

  document.querySelectorAll(".use-topic").forEach(btn => {
    btn.addEventListener("click", () => {
      sessionStorage.setItem("selectedTopic", btn.dataset.topic);
      window.location.href = "/script";
    });
  });
}

function escapeHtml(value){
  return String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
}
function escapeAttr(value){ return escapeHtml(value); }

function setupIdeasPage(){
  if(!$("searchBtn")) return;
  $("searchBtn").addEventListener("click", searchTopics);
  $("query").addEventListener("keydown", e => { if(e.key === "Enter") searchTopics(); });
}

function hydrateSelectedTopic(){
  const topic = sessionStorage.getItem("selectedTopic");
  if(topic && $("topic")){
    $("topic").value = topic;
    $("charCount").textContent = topic.length;
    sessionStorage.removeItem("selectedTopic");
    showToast("Topic loaded into your brief");
  }
}

loadConfig();
setupIdeasPage();
setupScriptPage();
hydrateSelectedTopic();
