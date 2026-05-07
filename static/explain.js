/* =====================================================
   explain.js — Explainable AI (XAI) Panel
   Calls POST /explain and renders a contribution chart.
   Exposes: window.SurfaceExplain.run(inputs)
   ===================================================== */

window.SurfaceExplain = (function () {
  let chart = null;

  /* ── Public: run ─────────────────────────────────── */
  async function run(inputs) {
    const panel   = document.getElementById("xai-content");
    const skeleton = document.getElementById("xai-loading");
    skeleton.hidden = false;
    panel.hidden    = true;

    try {
      const res  = await fetch("/explain", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(inputs),
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error);
      render(data);
    } catch (err) {
      skeleton.innerHTML = `<p style="color:var(--red);text-align:center">XAI error: ${err.message}</p>`;
    }
  }

  /* ── Render ──────────────────────────────────────── */
  function render(data) {
    const panel    = document.getElementById("xai-content");
    const skeleton = document.getElementById("xai-loading");
    skeleton.hidden = true;
    panel.hidden    = false;
    panel.style.opacity = "1";

    const { features, predicted_ra, method } = data;

    // Update method badge
    document.getElementById("xai-method").textContent = method;
    document.getElementById("xai-ra-echo").textContent = predicted_ra.toFixed(4) + " µm";

    // Build feature rows
    const rowsEl = document.getElementById("xai-rows");
    rowsEl.innerHTML = features.map((f, i) => {
      const isPos = f.contribution >= 0;
      const color = isPos ? "var(--red)" : "var(--green)";
      const bgColor = isPos ? "rgba(244,63,94,.15)" : "rgba(34,211,160,.15)";
      const arrow = isPos ? "▲" : "▼";
      const barW  = Math.min(Math.abs(f.pct), 100);
      return `
        <div class="xai-row" style="animation-delay:${i * 0.09}s">
          <div class="xai-feat-name">
            <span class="xai-rank">${i + 1}</span>
            <div>
              <strong>${f.name}</strong>
              <span class="xai-val">${f.value} ${f.unit}</span>
            </div>
          </div>
          <div class="xai-bar-wrap">
            <div class="xai-bar" style="width:${barW}%;background:${color};box-shadow:0 0 8px ${color}40"></div>
          </div>
          <div class="xai-contrib" style="color:${color}">
            <span class="xai-arrow">${arrow}</span>
            <span>${f.direction}</span>
            <span class="xai-pct">${Math.abs(f.pct)}%</span>
          </div>
        </div>`;
    }).join("");

    // Chart: horizontal bar
    renderChart(features);

    gsap.from(".xai-row", { opacity: 0, x: -24, stagger: 0.09, duration: 0.4, ease: "power2.out" });
  }

  /* ── Chart.js horizontal bar ─────────────────────── */
  function renderChart(features) {
    const canvas = document.getElementById("xai-chart");
    if (!canvas || typeof Chart === "undefined") return;

    const labels = features.map(f => f.name);
    const values = features.map(f => f.contribution);
    const colors = values.map(v => v >= 0 ? "rgba(244,63,94,0.75)" : "rgba(34,211,160,0.75)");
    const borders = values.map(v => v >= 0 ? "#f43f5e" : "#22d3a0");

    if (chart) { chart.destroy(); chart = null; }

    chart = new Chart(canvas, {
      type: "bar",
      data: {
        labels,
        datasets: [{
          label: "Contribution to Ra (µm)",
          data: values,
          backgroundColor: colors,
          borderColor: borders,
          borderWidth: 1.5,
          borderRadius: 6,
        }]
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#1a2235",
            callbacks: {
              label: ctx => ` ${ctx.parsed.x > 0 ? "+" : ""}${ctx.parsed.x.toFixed(4)} µm`
            }
          }
        },
        scales: {
          x: {
            grid: { color: "rgba(255,255,255,0.05)" },
            ticks: { color: "#64748b", font: { family: "Space Mono", size: 10 },
                     callback: v => (v > 0 ? "+" : "") + v.toFixed(3) },
            title: { display: true, text: "Ra Contribution (µm)", color: "#64748b" }
          },
          y: { grid: { display: false }, ticks: { color: "#e2e8f0", font: { family: "Inter", size: 12 } } }
        }
      }
    });
  }

  return { run };
})();
