/* ===================================================
   app.js  —  SurfaceSense GSAP UI Logic
   =================================================== */

/* ── 1.  Particle canvas background ────────────────── */
(function initCanvas() {
  const canvas = document.getElementById("bg-canvas");
  const ctx    = canvas.getContext("2d");
  let W, H, particles;

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function mkParticle() {
    return {
      x:  Math.random() * W,
      y:  Math.random() * H,
      r:  Math.random() * 1.4 + 0.3,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      a:  Math.random()
    };
  }

  function init() {
    resize();
    particles = Array.from({ length: 110 }, mkParticle);
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach(p => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(99,102,241,${p.a * 0.55})`;
      ctx.fill();
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > W) p.vx *= -1;
      if (p.y < 0 || p.y > H) p.vy *= -1;
    });

    // draw faint connecting lines
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 90) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(99,102,241,${0.12 * (1 - dist / 90)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(draw);
  }

  window.addEventListener("resize", resize);
  init();
  draw();
})();


/* ── 2.  Entrance animations ────────────────────────── */
gsap.registerPlugin(ScrollTrigger);

const tl = gsap.timeline({ defaults: { ease: "power3.out" } });

tl.to("#site-header",  { opacity: 1, y: 0, duration: .7, delay: .1 })
  .from("#site-header", { y: -20 }, "<")

  .to("#eyebrow",   { opacity: 1, y: 0, duration: .6 }, "-=.3")
  .from("#eyebrow", { y: 20 }, "<")

  .to("#hero-title", { opacity: 1, y: 0, duration: .7 }, "-=.35")
  .from("#hero-title", { y: 30 }, "<")

  .to("#hero-sub",  { opacity: 1, y: 0, duration: .6 }, "-=.4")
  .from("#hero-sub", { y: 20 }, "<")

  .to("#input-card",  { opacity: 1, y: 0, duration: .7 }, "-=.3")
  .from("#input-card",  { y: 40 }, "<")

  .to("#result-card", { opacity: 1, y: 0, duration: .7 }, "-=.5")
  .from("#result-card", { y: 40 }, "<");

// stagger fields
gsap.from(".field", {
  opacity: 0, y: 20, stagger: 0.08, duration: 0.5, ease: "power2.out", delay: 1.0
});


/* ── 3.  Hover shimmer on button ────────────────────── */
const btn = document.getElementById("predict-btn");
btn.addEventListener("mousemove", (e) => {
  const rect = btn.getBoundingClientRect();
  const x = ((e.clientX - rect.left) / rect.width  * 100).toFixed(1);
  const y = ((e.clientY - rect.top)  / rect.height * 100).toFixed(1);
  btn.style.background =
    `radial-gradient(circle at ${x}% ${y}%, #818cf8, #6366f1 55%)`;
});
btn.addEventListener("mouseleave", () => {
  btn.style.background = "";
});


/* ── 4.  Form submit → Predict ──────────────────────── */
const form        = document.getElementById("predict-form");
const resultIdle  = document.getElementById("result-idle");
const resultData  = document.getElementById("result-data");
const resultError = document.getElementById("result-error");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const body = {
    print_speed:    parseFloat(document.getElementById("print_speed").value),
    layer_height:   parseFloat(document.getElementById("layer_height").value),
    nozzle_temp:    parseFloat(document.getElementById("nozzle_temp").value),
    vibration_freq: parseFloat(document.getElementById("vibration_freq").value),
  };

  // validate
  if (Object.values(body).some(isNaN)) {
    shakeForm();
    return;
  }

  // loading state
  btn.classList.add("loading");
  btn.disabled = true;
  hideAll();

  try {
    const res  = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const data = await res.json();

    if (!data.success) throw new Error(data.error || "Prediction failed");

    showResult(data);
  } catch (err) {
    showError(err.message);
  } finally {
    btn.classList.remove("loading");
    btn.disabled = false;
  }
});


/* ── 5.  Show / hide helpers ────────────────────────── */
function hideAll() {
  resultIdle.hidden  = true;
  resultData.hidden  = true;
  resultError.hidden = true;
}

function showError(msg) {
  resultError.hidden = false;
  document.getElementById("error-msg").textContent = msg;
  gsap.from("#result-error", { opacity: 0, y: 10, duration: .4 });
}

function showResult(data) {
  resultData.hidden = false;
  const { predicted_ra, quality_label, quality_level } = data;

  // animated Ra counter
  const raEl = document.getElementById("ra-value");
  gsap.to({ val: 0 }, {
    val: predicted_ra,
    duration: 1.4,
    ease: "power2.out",
    onUpdate: function () {
      raEl.textContent = this.targets()[0].val.toFixed(4);
    }
  });

  // quality badge
  const badge = document.getElementById("quality-badge");
  const icons = { 1: "✅", 2: "⚠️", 3: "❌" };
  badge.className = ["", "smooth", "acceptable", "rough"][quality_level];
  document.getElementById("quality-icon").textContent = icons[quality_level];
  document.getElementById("quality-text").textContent = quality_label;

  // gauge — Ra range approx 2–7 µm  → map to 0–100%
  const RA_MIN = 1.8, RA_MAX = 7.5;
  const pct   = Math.min(100, Math.max(0, ((predicted_ra - RA_MIN) / (RA_MAX - RA_MIN)) * 100));
  const gaugeFill   = document.getElementById("gauge-fill");
  const gaugeNeedle = document.getElementById("gauge-needle");

  const gradMap = {
    1: "linear-gradient(90deg, #22d3a0, #6ee7b7)",
    2: "linear-gradient(90deg, #f59e0b, #fcd34d)",
    3: "linear-gradient(90deg, #f43f5e, #fb7185)"
  };
  gaugeFill.style.background = gradMap[quality_level];

  gsap.fromTo(gaugeFill,
    { width: "0%" },
    { width: pct + "%", duration: 1.3, ease: "power2.out" }
  );
  gsap.to(gaugeNeedle, { left: pct + "%", duration: 1.3, ease: "power2.out" });

  // interpretation text
  const msgs = {
    1: `Ra = ${predicted_ra.toFixed(4)} µm — excellent surface finish. Your print is smooth and likely print-ready.`,
    2: `Ra = ${predicted_ra.toFixed(4)} µm — acceptable quality. Minor post-processing may improve the finish.`,
    3: `Ra = ${predicted_ra.toFixed(4)} µm — rough surface detected. Consider reducing layer height or print speed.`
  };
  document.getElementById("interpretation").textContent = msgs[quality_level];

  // card reveal
  gsap.from("#result-data > *", {
    opacity: 0, y: 18, stagger: 0.1, duration: 0.5, ease: "power2.out"
  });
}


/* ── 6.  Input shake on invalid ─────────────────────── */
function shakeForm() {
  gsap.to("#input-card", {
    x: [-8, 8, -6, 6, -3, 3, 0],
    duration: 0.45,
    ease: "none"
  });
}


/* ── 7.  Input focus micro-animation ─────────────────── */
document.querySelectorAll(".field input").forEach(input => {
  input.addEventListener("focus", () => {
    gsap.to(input, { scale: 1.01, duration: .15, ease: "power1.out" });
  });
  input.addEventListener("blur", () => {
    gsap.to(input, { scale: 1, duration: .15 });
  });
});
