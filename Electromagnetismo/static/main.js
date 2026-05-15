// ── SLIDER BINDINGS ──────────────────────────────────────

const sliders = [
  { id: "input-N",     val: "val-N",     fmt: v => v },
  { id: "input-L",     val: "val-L",     fmt: v => v },
  { id: "input-delta", val: "val-delta", fmt: v => parseFloat(v).toFixed(2) },
  { id: "input-snap",  val: "val-snap",  fmt: v => v },
];

sliders.forEach(({ id, val, fmt }) => {
  const el = document.getElementById(id);
  const disp = document.getElementById(val);
  if (!el || !disp) return;
  disp.textContent = fmt(el.value);
  el.addEventListener("input", () => { disp.textContent = fmt(el.value); });
});

// ── RADIO BUTTONS ────────────────────────────────────────

document.querySelectorAll('.radio-option').forEach(opt => {
  opt.addEventListener('click', () => {
    document.querySelectorAll('.radio-option').forEach(o => o.classList.remove('selected'));
    opt.classList.add('selected');
    opt.querySelector('input[type=radio]').checked = true;
  });
});

// ── SIMULATION ───────────────────────────────────────────

let currentJobId = null;
let pollInterval = null;

function getParams() {
  return {
    N:              parseInt(document.getElementById("input-N").value),
    L:              parseFloat(document.getElementById("input-L").value),
    delta:          parseFloat(document.getElementById("input-delta").value),
    n_snapshots:    parseInt(document.getElementById("input-snap").value),
    mode:           document.querySelector('input[name="mode"]:checked')?.value || "both",
  };
}

async function runSimulation() {
  const btn = document.getElementById("btn-run");
  btn.disabled = true;
  btn.innerHTML = 'Simulando...';

  // Show progress, hide results
  document.getElementById("progress-wrapper").style.display = "block";
  document.getElementById("results-section").style.display = "none";
  document.getElementById("stats-banner").style.display = "none";
  setProgress(0, "Iniciando simulación...");

  try {
    const res = await fetch("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(getParams()),
    });
    const { job_id } = await res.json();
    currentJobId = job_id;
    pollJob(job_id);
  } catch (e) {
    alert("Error al iniciar la simulación: " + e.message);
    resetBtn();
  }
}

function pollJob(jobId) {
  if (pollInterval) clearInterval(pollInterval);
  pollInterval = setInterval(async () => {
    try {
      const res = await fetch(`/api/job/${jobId}`);
      const data = await res.json();

      if (data.status === "running") {
        setProgress(data.progress, progressLabel(data.progress));
      } else if (data.status === "done") {
        clearInterval(pollInterval);
        setProgress(100, "¡Completado!");
        setTimeout(() => showResults(data.result), 300);
      } else if (data.status === "error") {
        clearInterval(pollInterval);
        alert("Error en simulación: " + data.error);
        resetBtn();
      }
    } catch (e) {
      // Keep polling silently
    }
  }, 800);
}

function progressLabel(pct) {
  if (pct < 20)  return "Inicializando cargas...";
  if (pct < 50)  return "Ejecutando minimización de energía...";
  if (pct < 75)  return "Calculando campo eléctrico...";
  if (pct < 95)  return "Generando visualizaciones...";
  return "Ensamblando animación...";
}

function setProgress(pct, label) {
  document.getElementById("progress-fill").style.width = pct + "%";
  document.getElementById("progress-text").textContent = label;
  document.getElementById("progress-pct").textContent = pct + "%";
}

function showResults(result) {
  // Stats banner
  document.getElementById("stat-pos").textContent   = result.n_positive;
  document.getElementById("stat-neg").textContent   = result.n_negative;
  document.getElementById("stat-steps").textContent = result.accepted_steps.toLocaleString("es");
  document.getElementById("stat-ui").textContent    = result.energy_initial.toExponential(3);
  document.getElementById("stat-uf").textContent    = result.energy_final.toExponential(3);
  document.getElementById("stats-banner").style.display = "flex";

  // Images
  document.getElementById("img-initial").src = result.img_initial;
  document.getElementById("img-final").src   = result.img_final;
  document.getElementById("img-field").src   = result.img_field;
  document.getElementById("img-heatmap").src = result.img_heatmap;
  document.getElementById("img-energy").src  = result.img_energy;
  document.getElementById("img-field-initial").src = result.img_field_initial;
  document.getElementById("img-potential-initial").src = result.img_potential_initial;

  // Animation
  animationFrames = result.animation_frames;
  animFrame = 0;
  animInterval = Math.max(100, 5000 / animationFrames.length); // Auto-adjust for 5s total animation
  showAnimFrame(0);
  document.getElementById("anim-tot").textContent = animationFrames.length;

  // Table
  const tbody = document.getElementById("charges-tbody");
  tbody.innerHTML = "";
  result.positions_table.forEach(row => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.id}</td>
      <td class="${row.sign === '+' ? 'charge-plus' : 'charge-minus'}">${row.sign}1</td>
      <td>${row.x}</td>
      <td>${row.y}</td>
    `;
    tbody.appendChild(tr);
  });

  // Show results section
  document.getElementById("results-section").style.display = "flex";
  document.getElementById("results-section").style.flexDirection = "column";

  // Scroll to results
  setTimeout(() => {
    document.getElementById("results-section").scrollIntoView({ behavior: "smooth", block: "start" });
  }, 200);

  resetBtn();
}

function resetBtn() {
  const btn = document.getElementById("btn-run");
  btn.disabled = false;
  btn.innerHTML = '<span class="btn-icon">▶</span> Generar Simulación';
}

// ── TABS ─────────────────────────────────────────────────

function switchTab(name, el) {
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
  el.classList.add("active");
  document.getElementById("tab-" + name).classList.add("active");
}

// ── ANIMATION ────────────────────────────────────────────

let animationFrames = [];
let animFrame = 0;
let animPlaying = false;
let animTimer = null;
let animInterval = 300;

function showAnimFrame(idx) {
  if (!animationFrames.length) return;
  animFrame = Math.max(0, Math.min(idx, animationFrames.length - 1));
  document.getElementById("anim-img").src = animationFrames[animFrame];
  document.getElementById("anim-cur").textContent = animFrame + 1;
  const pct = animationFrames.length > 1
    ? (animFrame / (animationFrames.length - 1)) * 100
    : 100;
  document.getElementById("anim-progress-fill").style.width = pct + "%";
}

function animPrev() {
  stopPlay();
  showAnimFrame(animFrame - 1);
}

function animNext() {
  stopPlay();
  showAnimFrame(animFrame + 1);
}

function togglePlay() {
  if (animPlaying) {
    stopPlay();
  } else {
    animPlaying = true;
    document.getElementById("btn-play").textContent = "⏸ Pausa";
    animTimer = setInterval(() => {
      animFrame++;
      if (animFrame >= animationFrames.length) { animFrame = 0; }
      showAnimFrame(animFrame);
    }, animInterval);
  }
}

function stopPlay() {
  animPlaying = false;
  if (animTimer) clearInterval(animTimer);
  document.getElementById("btn-play").textContent = "⏵ Play";
}