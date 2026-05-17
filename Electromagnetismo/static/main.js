// ── SLIDER BINDINGS ──────────────────────────────────────

const sliders = [
  { id: "input-N",     val: "val-N",     fmt: v => v },
  { id: "input-L",     val: "val-L",     fmt: v => v },
  { id: "input-delta", val: "val-delta", fmt: v => parseFloat(v).toFixed(2) },
  { id: "input-snap",  val: "val-snap",  fmt: v => v },
];

sliders.forEach(({ id, val, fmt }) => {
  const el   = document.getElementById(id);
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

// ── PROGRESS ─────────────────────────────────────────────

let _realProgress  = 0;   // % real del servidor
let _shownProgress = 0;   // % mostrado en pantalla (siempre avanza)
let _progressTimer = null;

function startProgressAnimation() {
  _realProgress  = 0;
  _shownProgress = 0;
  _progressTimer && clearInterval(_progressTimer);

  // Cada 120ms avanza el display: se acerca al real pero nunca lo supera,
  // y si está lejos del real avanza más rápido.
  _progressTimer = setInterval(() => {
    // Techo: nunca mostrar más del real (excepto pequeño buffer visual de +2)
    const ceiling = Math.min(_realProgress + 2, 99);
    if (_shownProgress < ceiling) {
      // Velocidad proporcional a la distancia al techo
      const gap   = ceiling - _shownProgress;
      const step  = Math.max(0.3, gap * 0.08);
      _shownProgress = Math.min(_shownProgress + step, ceiling);
      _applyProgress(_shownProgress);
    }
  }, 120);
}

function updateRealProgress(pct, label) {
  _realProgress = pct;
  if (label) document.getElementById("progress-text").textContent = label;
  document.getElementById("progress-pct").textContent = Math.round(_shownProgress) + "%";
}

function finishProgress() {
  _realProgress  = 100;
  _shownProgress = 100;
  _applyProgress(100);
  document.getElementById("progress-pct").textContent = "100%";
  _progressTimer && clearInterval(_progressTimer);
}

function _applyProgress(pct) {
  document.getElementById("progress-fill").style.width = pct + "%";
  document.getElementById("progress-pct").textContent  = Math.round(pct) + "%";
}

// ── SIMULATION ───────────────────────────────────────────

let currentJobId = null;
let pollInterval = null;

function getParams() {
  return {
    N:           parseInt(document.getElementById("input-N").value),
    L:           parseFloat(document.getElementById("input-L").value),
    delta:       parseFloat(document.getElementById("input-delta").value),
    n_snapshots: parseInt(document.getElementById("input-snap").value),
    mode:        document.querySelector('input[name="mode"]:checked')?.value || "both",
  };
}

async function runSimulation() {
  const btn = document.getElementById("btn-run");
  btn.disabled  = true;
  btn.innerHTML = 'Simulando...';

  document.getElementById("progress-wrapper").style.display = "block";
  document.getElementById("results-section").style.display  = "none";
  document.getElementById("stats-banner").style.display     = "none";

  startProgressAnimation();
  updateRealProgress(0, "Iniciando simulación...");

  try {
    const res        = await fetch("/api/simulate", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(getParams()),
    });
    const { job_id } = await res.json();
    currentJobId     = job_id;
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
      const res  = await fetch(`/api/job/${jobId}`);
      const data = await res.json();

      if (data.status === "running" || data.status === "queued") {
        updateRealProgress(data.progress, progressLabel(data.progress));

      } else if (data.status === "done") {
        clearInterval(pollInterval);
        finishProgress();
        document.getElementById("progress-text").textContent = "¡Completado!";
        setTimeout(() => showResults(data.result), 400);

      } else if (data.status === "error") {
        clearInterval(pollInterval);
        _progressTimer && clearInterval(_progressTimer);
        alert("Error en simulación:\n" + data.error);
        resetBtn();
      }
    } catch (e) {
      // Silencioso — sigue intentando
    }
  }, 600);
}

function progressLabel(pct) {
  if (pct < 10) return "Inicializando cargas...";
  if (pct < 40) return "Ejecutando minimización de energía...";
  if (pct < 55) return "Calculando campo eléctrico y potencial...";
  if (pct < 75) return "Generando visualizaciones...";
  if (pct < 98) return "Generando frames de animación...";
  return "Finalizando...";
}

function showResults(result) {
  document.getElementById("stat-pos").textContent   = result.n_positive;
  document.getElementById("stat-neg").textContent   = result.n_negative;
  document.getElementById("stat-steps").textContent = result.accepted_steps.toLocaleString("es");
  document.getElementById("stat-ui").textContent    = result.energy_initial.toExponential(3);
  document.getElementById("stat-uf").textContent    = result.energy_final.toExponential(3);
  document.getElementById("stats-banner").style.display = "flex";

  document.getElementById("img-initial").src          = result.img_initial;
  document.getElementById("img-final").src             = result.img_final;
  document.getElementById("img-field").src             = result.img_field;
  document.getElementById("img-heatmap").src           = result.img_heatmap;
  document.getElementById("img-energy").src            = result.img_energy;
  document.getElementById("img-field-initial").src     = result.img_field_initial;
  document.getElementById("img-potential-initial").src = result.img_potential_initial;
  document.getElementById("img-error").src             = result.img_error;

  renderErrorMetrics(result.error_metrics);

  animationFrames = result.animation_frames;
  animFrame       = 0;
  animInterval    = Math.max(120, 6000 / animationFrames.length);
  showAnimFrame(0);
  document.getElementById("anim-tot").textContent = animationFrames.length;

  const fillTable = (tbodyId, rows) => {
    const tbody = document.getElementById(tbodyId);
    tbody.innerHTML = "";
    rows.forEach(row => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${row.id}</td>
        <td class="${row.sign === '+' ? 'charge-plus' : 'charge-minus'}">${row.sign}1</td>
        <td>${row.x}</td>
        <td>${row.y}</td>
      `;
      tbody.appendChild(tr);
    });
  };
  fillTable("charges-tbody", result.positions_table);
  fillTable("charges-tbody-initial", result.positions_table_initial);

  document.getElementById("results-section").style.display      = "flex";
  document.getElementById("results-section").style.flexDirection = "column";

  setTimeout(() => {
    document.getElementById("results-section").scrollIntoView({ behavior: "smooth", block: "start" });
  }, 200);

  resetBtn();
}

function renderErrorMetrics(metrics) {
  const tbody = document.getElementById("error-tbody");
  if (!tbody || !metrics || Object.keys(metrics).length === 0) return;

  const rows = [
    ["Pasos aceptados totales",           metrics.n_pasos],
    ["ΔU máximo",                         metrics.delta_U_max?.toExponential(3) + " J"],
    ["ΔU mínimo",                         metrics.delta_U_min?.toExponential(3) + " J"],
    ["ΔU promedio",                       metrics.delta_U_mean?.toExponential(3) + " J"],
    ["ΔU último paso",                    metrics.delta_U_final?.toExponential(3) + " J"],
    ["Nivel de convergencia (10% final)", metrics.convergence_level?.toExponential(3) + " J"],
    ["Reducción total de energía",        metrics.reduccion_total_pct?.toFixed(2) + " %"],
  ];

  tbody.innerHTML = rows.map(([label, value]) => `
    <tr>
      <td>${label}</td>
      <td style="font-family: var(--font-mono); color: var(--accent);">${value}</td>
    </tr>
  `).join("");
}

function resetBtn() {
  const btn     = document.getElementById("btn-run");
  btn.disabled  = false;
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
let animFrame       = 0;
let animPlaying     = false;
let animTimer       = null;
let animInterval    = 300;

function showAnimFrame(idx) {
  if (!animationFrames.length) return;
  animFrame = Math.max(0, Math.min(idx, animationFrames.length - 1));
  document.getElementById("anim-img").src         = animationFrames[animFrame];
  document.getElementById("anim-cur").textContent = animFrame + 1;
  const pct = animationFrames.length > 1
    ? (animFrame / (animationFrames.length - 1)) * 100
    : 100;
  document.getElementById("anim-progress-fill").style.width = pct + "%";
}

function animPrev() { stopPlay(); showAnimFrame(animFrame - 1); }
function animNext() { stopPlay(); showAnimFrame(animFrame + 1); }

function togglePlay() {
  if (animPlaying) {
    stopPlay();
  } else {
    animPlaying = true;
    document.getElementById("btn-play").textContent = "⏸ Pausa";
    animTimer = setInterval(() => {
      animFrame++;
      if (animFrame >= animationFrames.length) animFrame = 0;
      showAnimFrame(animFrame);
    }, animInterval);
  }
}

function stopPlay() {
  animPlaying = false;
  if (animTimer) clearInterval(animTimer);
  document.getElementById("btn-play").textContent = "⏵ Play";
}