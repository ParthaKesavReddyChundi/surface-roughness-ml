/* =====================================================
   optimizer.js — Optimization Advisor
   Calls POST /optimize and renders tip cards.
   Exposes: window.SurfaceOptimizer.fetchAndRender
   ===================================================== */

window.SurfaceOptimizer = (function () {

  /* ── Public: fetchAndRender ──────────────────────── */
  async function fetchAndRender(inputs, baseRa) {
    const card = document.getElementById("optimizer-card");
    const body = document.getElementById("tips-body");

    // show loading skeleton
    card.hidden = false;
    card.style.opacity = "1";   // override CSS default of 0
    body.innerHTML = `<div class="tips-loading"><span class="tips-spinner"></span> Calculating improvements…</div>`;
    gsap.from(card, { opacity: 0, y: 30, duration: 0.5, ease: "power2.out" });

    try {
      const res  = await fetch("/optimize", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(inputs),
      });
      const data = await res.json();

      if (!data.success || !data.tips || data.tips.length === 0) {
        body.innerHTML = `<p class="tips-empty">✅ Parameters are already well-optimised for this configuration.</p>`;
        return;
      }

      renderTips(body, data.tips, baseRa);

    } catch (err) {
      body.innerHTML = `<p class="tips-empty" style="color:var(--red)">Could not load tips: ${err.message}</p>`;
    }
  }

  /* ── Render tip rows ─────────────────────────────── */
  function renderTips(container, tips, baseRa) {
    const arrowIcon = d => d === "increase" ? "↑" : "↓";
    const arrowClass = d => d === "increase" ? "tip-up" : "tip-down";

    container.innerHTML = tips.map((tip, i) => `
      <div class="tip-row" style="animation-delay:${i * 0.08}s">
        <div class="tip-rank">${i + 1}</div>
        <div class="tip-main">
          <span class="tip-param">${tip.param}</span>
          <span class="tip-arrow ${arrowClass(tip.direction)}">${arrowIcon(tip.direction)}</span>
          <span class="tip-action">
            ${tip.direction} by ${tip.pct}%
            <span class="tip-vals">${tip.current_val} → <strong>${tip.new_val}</strong> ${tip.unit}</span>
          </span>
        </div>
        <div class="tip-delta">
          <span class="tip-new-ra">${tip.new_ra.toFixed(4)} µm</span>
          <span class="tip-improvement">−${tip.improvement.toFixed(4)} µm</span>
        </div>
      </div>
    `).join("");

    // stagger animate each row
    gsap.from(".tip-row", {
      opacity: 0, x: -20, stagger: 0.1, duration: 0.45, ease: "power2.out"
    });
  }

  return { fetchAndRender };
})();
