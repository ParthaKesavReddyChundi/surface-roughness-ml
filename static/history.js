/* =====================================================
   history.js — Session Prediction History + Sparkline
   Exposes: window.SurfaceHistory.addEntry / clearHistory
   ===================================================== */

window.SurfaceHistory = (function () {
  const STORAGE_KEY = "surfacesense_history";
  const MAX_ENTRIES = 20;
  let chart = null;

  /* ── Storage helpers ─────────────────────────────── */
  function load() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]"); }
    catch { return []; }
  }
  function save(entries) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
  }

  /* ── Quality helpers ─────────────────────────────── */
  function qColor(level) {
    return { 1: "#22d3a0", 2: "#f59e0b", 3: "#f43f5e" }[level] || "#6366f1";
  }

  /* ── Public: addEntry ────────────────────────────── */
  function addEntry(inputs, result) {
    const entries = load();
    entries.push({
      id:             entries.length + 1,
      timestamp:      new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
      print_speed:    inputs.print_speed,
      layer_height:   inputs.layer_height,
      nozzle_temp:    inputs.nozzle_temp,
      vibration_freq: inputs.vibration_freq,
      predicted_ra:   result.predicted_ra,
      quality_label:  result.quality_label,
      quality_level:  result.quality_level,
    });
    if (entries.length > MAX_ENTRIES) entries.shift();
    save(entries);
    render(entries);
    showCard();
  }

  /* ── Public: clearHistory ────────────────────────── */
  function clearHistory() {
    localStorage.removeItem(STORAGE_KEY);
    if (chart) { chart.destroy(); chart = null; }
    const card = document.getElementById("history-card");
    gsap.to(card, {
      opacity: 0, y: 20, duration: 0.35,
      onComplete: () => { card.hidden = true; card.style.opacity = ""; }
    });
  }

  /* ── Card reveal ─────────────────────────────────── */
  function showCard() {
    // In the new layout the card is always in its section.
    // Just ensure the content block is visible (app.js handles #history-content toggle).
    const content = document.getElementById("history-content");
    const empty   = document.getElementById("history-empty");
    if (content && empty) {
      empty.hidden   = true;
      content.hidden = false;
      content.style.opacity = "1";
    }
    // Legacy: also show the card itself if it has hidden attr
    const card = document.getElementById("history-card");
    if (card && card.hidden) {
      card.hidden = false;
      card.style.opacity = "1";
      gsap.from(card, { opacity: 0, y: 30, duration: 0.5, ease: "power2.out" });
    }
  }


  /* ── Render table ────────────────────────────────── */
  function renderTable(entries) {
    const tbody = document.getElementById("history-tbody");
    if (!tbody) return;
    tbody.innerHTML = [...entries].reverse().map(e => `
      <tr>
        <td>${e.id}</td>
        <td>${e.timestamp}</td>
        <td>${e.print_speed}</td>
        <td>${e.layer_height}</td>
        <td>${e.nozzle_temp}</td>
        <td>${e.vibration_freq}</td>
        <td class="ra-cell" style="color:${qColor(e.quality_level)};font-family:var(--mono);font-weight:700">${e.predicted_ra.toFixed(4)}</td>
        <td><span class="q-pill q${e.quality_level}">${e.quality_label}</span></td>
      </tr>`).join("");
  }

  /* ── Render chart ────────────────────────────────── */
  function renderChart(entries) {
    const canvas = document.getElementById("history-chart");
    if (!canvas || typeof Chart === "undefined") return;

    const labels = entries.map(e => `#${e.id}`);
    const values = entries.map(e => e.predicted_ra);
    const colors = entries.map(e => qColor(e.quality_level));

    if (chart) {
      chart.data.labels = labels;
      chart.data.datasets[0].data = values;
      chart.data.datasets[0].pointBackgroundColor = colors;
      chart.data.datasets[0].pointBorderColor     = colors;
      chart.update("active");
      return;
    }

    Chart.defaults.color = "#64748b";
    chart = new Chart(canvas, {
      type: "line",
      data: {
        labels,
        datasets: [{
          label:                "Ra (µm)",
          data:                 values,
          borderColor:          "#6366f1",
          backgroundColor:      "rgba(99,102,241,0.07)",
          pointBackgroundColor: colors,
          pointBorderColor:     colors,
          pointRadius:          6,
          pointHoverRadius:     9,
          borderWidth:          2,
          tension:              0.4,
          fill:                 true,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#1a2235",
            titleColor:      "#e2e8f0",
            bodyColor:       "#94a3b8",
            callbacks: { label: ctx => ` Ra = ${ctx.parsed.y.toFixed(4)} µm` }
          }
        },
        scales: {
          x: { ticks: { font: { family: "Inter", size: 11 } }, grid: { color: "rgba(255,255,255,0.04)" } },
          y: {
            ticks: { font: { family: "Space Mono", size: 10 }, callback: v => v.toFixed(2) },
            grid:  { color: "rgba(255,255,255,0.04)" },
            title: { display: true, text: "Ra (µm)", font: { size: 11 } }
          }
        }
      }
    });
  }

  /* ── Render (table + chart) ──────────────────────── */
  function render(entries) {
    renderTable(entries);
    renderChart(entries);
  }

  /* ── Auto-load on page start ─────────────────────── */
  function init() {
    const entries = load();
    if (entries.length) { showCard(); render(entries); }
    const btn = document.getElementById("clear-history-btn");
    if (btn) btn.addEventListener("click", clearHistory);
  }

  return { addEntry, clearHistory, init };
})();
