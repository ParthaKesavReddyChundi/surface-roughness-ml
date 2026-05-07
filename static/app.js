/* ===================================================
   app.js — SurfaceSense Orchestrator
   No canvas. Sidebar nav. All module wiring.
   =================================================== */

/* ── 1. SIDEBAR NAVIGATION ──────────────────────────── */
const sidebar        = document.getElementById("sidebar");
const overlay        = document.getElementById("sidebar-overlay");
const sidebarToggle  = document.getElementById("sidebar-toggle");
const navItems       = document.querySelectorAll(".nav-item");
const sections       = document.querySelectorAll(".section");
const topbarTitle    = document.getElementById("topbar-title");

const SECTION_TITLES = {
  overview: "Overview", predict: "Predict Ra", explain: "Explainable AI",
  model: "Model Insights", optimizer: "Optimizer", history: "Session History", guide: "Parameter Guide"
};

function showSection(name) {
  sections.forEach(s => s.classList.remove("active"));
  navItems.forEach(n => n.classList.remove("active"));
  const sec = document.getElementById(`section-${name}`);
  if (sec) {
    sec.classList.add("active");
    gsap.from(sec.children, { opacity: 0, y: 22, stagger: .07, duration: .4, ease: "power2.out",
      onStart: () => sec.querySelectorAll(".card").forEach(c => c.style.opacity = "1") });
  }
  document.querySelector(`.nav-item[data-section="${name}"]`)?.classList.add("active");
  topbarTitle.textContent = SECTION_TITLES[name] || name;
  // Close sidebar on mobile
  if (window.innerWidth <= 768) { sidebar.classList.remove("open"); overlay.classList.remove("visible"); }
}

navItems.forEach(btn => btn.addEventListener("click", () => showSection(btn.dataset.section)));

// Feature cards + action links → navigate
document.addEventListener("click", e => {
  const goto = e.target.closest("[data-goto]")?.dataset.goto;
  if (goto) showSection(goto);
});

sidebarToggle.addEventListener("click", () => {
  sidebar.classList.toggle("open");
  overlay.classList.toggle("visible");
});
overlay.addEventListener("click", () => { sidebar.classList.remove("open"); overlay.classList.remove("visible"); });


/* ── 2. ENTRANCE ANIMATION ──────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  gsap.from(".section-hero", { opacity: 0, y: 30, duration: .7, ease: "power3.out", delay: .1 });
  gsap.from(".stats-row .stat-card", { opacity: 0, y: 20, stagger: .08, duration: .5, ease: "power2.out", delay: .35 });
  gsap.from(".feature-card", { opacity: 0, y: 24, stagger: .06, duration: .5, ease: "power2.out", delay: .5 });

  loadModelInfo();
  updateOverviewStats();
  SurfaceHistory.init();
});


/* ── 3. BUTTON SHIMMER ──────────────────────────────── */
const btn = document.getElementById("predict-btn");
btn.addEventListener("mousemove", e => {
  const r = btn.getBoundingClientRect();
  btn.style.background = `radial-gradient(circle at ${((e.clientX-r.left)/r.width*100).toFixed(1)}% ${((e.clientY-r.top)/r.height*100).toFixed(1)}%, #818cf8, #6366f1 55%)`;
}, { passive: true });
btn.addEventListener("mouseleave", () => { btn.style.background = ""; });


/* ── 4. FORM SUBMIT ─────────────────────────────────── */
const form        = document.getElementById("predict-form");
const resultIdle  = document.getElementById("result-idle");
const resultData  = document.getElementById("result-data");
const resultError = document.getElementById("result-error");

form.addEventListener("submit", async e => {
  e.preventDefault();
  const body = {
    print_speed:    parseFloat(document.getElementById("print_speed").value),
    layer_height:   parseFloat(document.getElementById("layer_height").value),
    nozzle_temp:    parseFloat(document.getElementById("nozzle_temp").value),
    vibration_freq: parseFloat(document.getElementById("vibration_freq").value),
  };
  if (Object.values(body).some(isNaN)) { shakeForm(); return; }

  btn.classList.add("loading"); btn.disabled = true;
  resultIdle.hidden = true; resultData.hidden = true; resultError.hidden = true;

  try {
    const res  = await fetch("/predict", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body) });
    const data = await res.json();
    if (!data.success) throw new Error(data.error || "Prediction failed");

    showResult(data);
    SurfaceHistory.addEntry(body, data);
    updateOverviewStats();
    SurfaceOptimizer.fetchAndRender(body, data.predicted_ra);
    SurfaceExplain.run(body);

    // Light up nav dots
    document.getElementById("explain-dot").hidden   = false;
    document.getElementById("optimizer-dot").hidden = false;

    // Update topbar pill
    const pill = document.getElementById("last-ra-pill");
    pill.hidden = false;
    pill.textContent = `Last: ${data.predicted_ra.toFixed(4)} µm`;

  } catch (err) {
    resultError.hidden = false; resultError.style.opacity = "1";
    document.getElementById("error-msg").textContent = err.message;
  } finally {
    btn.classList.remove("loading"); btn.disabled = false;
  }
});


/* ── 5. SHOW RESULT ─────────────────────────────────── */
function showResult(data) {
  resultData.hidden = false; resultData.style.opacity = "1";
  const { predicted_ra, quality_label, quality_level, confidence } = data;

  gsap.to({ val: 0 }, { val: predicted_ra, duration: 1.1, ease: "power2.out",
    onUpdate: function () { document.getElementById("ra-value").textContent = this.targets()[0].val.toFixed(4); } });

  const badge = document.getElementById("quality-badge");
  badge.className = ["","smooth","acceptable","rough"][quality_level];
  document.getElementById("quality-icon").textContent = { 1:"✅", 2:"⚠️", 3:"❌" }[quality_level];
  document.getElementById("quality-text").textContent = quality_label;

  const pct = Math.min(100, Math.max(0, ((predicted_ra - 1.8) / (7.5 - 1.8)) * 100));
  document.getElementById("gauge-fill").style.background = { 1:"linear-gradient(90deg,#22d3a0,#6ee7b7)", 2:"linear-gradient(90deg,#f59e0b,#fcd34d)", 3:"linear-gradient(90deg,#f43f5e,#fb7185)" }[quality_level];
  gsap.fromTo("#gauge-fill", { width:"0%" }, { width:pct+"%", duration:1.1, ease:"power2.out" });
  gsap.to("#gauge-needle", { left:pct+"%", duration:1.1, ease:"power2.out" });

  if (confidence) {
    const cb = document.getElementById("confidence-band");
    cb.hidden = false; cb.style.opacity = "1";
    document.getElementById("conf-range").textContent = `${confidence.lower.toFixed(4)} – ${confidence.upper.toFixed(4)} µm`;
    document.getElementById("conf-model").textContent = `${confidence.model_name} · ±${confidence.rmse.toFixed(4)} µm RMSE` + (confidence.r2 ? ` · R² = ${confidence.r2.toFixed(4)}` : "");
  }

  document.getElementById("interpretation").textContent = {
    1: `Ra = ${predicted_ra.toFixed(4)} µm — excellent surface finish. Print is smooth.`,
    2: `Ra = ${predicted_ra.toFixed(4)} µm — acceptable quality. Minor post-processing may help.`,
    3: `Ra = ${predicted_ra.toFixed(4)} µm — rough surface. Reduce layer height or print speed.`
  }[quality_level];

  gsap.from("#result-data > *", { opacity:0, y:14, stagger:.08, duration:.4, ease:"power2.out" });
}


/* ── 6. SHAKE ───────────────────────────────────────── */
function shakeForm() {
  gsap.to("#input-card", { x:[-8,8,-6,6,-3,3,0], duration:.4, ease:"none" });
}


/* ── 7. INPUT FOCUS ─────────────────────────────────── */
document.querySelectorAll(".field input").forEach(inp => {
  inp.addEventListener("focus", () => gsap.to(inp, { scale:1.01, duration:.12 }), { passive:true });
  inp.addEventListener("blur",  () => gsap.to(inp, { scale:1, duration:.12 }),    { passive:true });
});


/* ── 8. MODEL INFO ──────────────────────────────────── */
async function loadModelInfo() {
  try {
    const data = await fetch("/model_info").then(r => r.json());
    if (!data.success) return;
    document.getElementById("sf-model-name").textContent = data.model_name || "ML";
    document.getElementById("stat-model-val").textContent = data.model_name || "—";
    if (data.r2 != null) {
      const r2El = document.getElementById("stat-r2-val");
      r2El.textContent = data.r2.toFixed(4);
      r2El.style.color = data.r2 >= 0.9 ? "var(--green)" : "var(--amber)";
    }

    const metricsEl = document.getElementById("model-metrics");
    if (metricsEl) {
      const r2c   = data.r2   != null ? `<span class="metric-value ${data.r2>=0.9?'good':'warn'}">${data.r2.toFixed(4)}</span>` : `<span class="metric-value">—</span>`;
      const rmsec = data.rmse != null ? `<span class="metric-value">${data.rmse.toFixed(4)}</span>` : `<span class="metric-value">—</span>`;
      metricsEl.innerHTML = `
        <div class="metric-row"><span class="metric-label">Best Model</span><span class="metric-value">${data.model_name}</span></div>
        <div class="metric-row"><span class="metric-label">R² Score</span>${r2c}</div>
        <div class="metric-row"><span class="metric-label">RMSE (µm)</span>${rmsec}</div>
        <div class="metric-row"><span class="metric-label">Features</span><span class="metric-value">${(data.features||[]).length}</span></div>
        <div class="metric-row"><span class="metric-label">Model Class</span><span class="metric-value" style="font-size:.8rem">${data.model_class}</span></div>`;
    }

    if (data.importances) renderImportanceChart(data.importances);
  } catch {}
}

function renderImportanceChart(imp) {
  const canvas = document.getElementById("importance-chart");
  if (!canvas || typeof Chart === "undefined") return;
  const LABELS = { "Print Speed(mm/min)":"Print Speed","Layer Height(mm)":"Layer Height","Nozzle Temperature(°C)":"Nozzle Temp","Vibration Frequency(Hz)":"Vibration Freq" };
  const entries = Object.entries(imp).map(([k,v]) => ({ label:LABELS[k]||k, value:v })).sort((a,b) => b.value-a.value);
  new Chart(canvas, {
    type:"bar",
    data:{ labels:entries.map(e=>e.label), datasets:[{ data:entries.map(e=>e.value), backgroundColor:["rgba(99,102,241,.7)","rgba(34,211,160,.7)","rgba(245,158,11,.7)","rgba(244,63,94,.7)"], borderRadius:5 }] },
    options:{ indexAxis:"y", responsive:true, maintainAspectRatio:false, plugins:{ legend:{ display:false } }, scales:{ x:{ grid:{ color:"rgba(255,255,255,.04)" }, ticks:{ color:"#64748b", font:{ size:10 } } }, y:{ grid:{ display:false }, ticks:{ color:"#e2e8f0", font:{ family:"Inter", size:11 } } } } }
  });
}


/* ── 9. OVERVIEW STATS ──────────────────────────────── */
function updateOverviewStats() {
  try {
    const history = JSON.parse(localStorage.getItem("surfacesense_history") || "[]");
    document.querySelector("#stat-predictions .stat-val").textContent = history.length;
    if (history.length) {
      const best = Math.min(...history.map(e => e.predicted_ra)).toFixed(4);
      document.querySelector("#stat-best-ra .stat-val").textContent = best;
    }
  } catch {}
}


/* ── 10. HISTORY MODULE: show content vs empty ───────── */
// Patch history.js to toggle #history-empty / #history-content
const _origAdd = SurfaceHistory.addEntry.bind(SurfaceHistory);
SurfaceHistory.addEntry = function(inputs, result) {
  _origAdd(inputs, result);
  document.getElementById("history-empty").hidden   = true;
  document.getElementById("history-content").hidden = false;
  document.getElementById("history-content").style.opacity = "1";
};
