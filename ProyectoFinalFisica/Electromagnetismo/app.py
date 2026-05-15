"""
app.py — Flask web application for electric charge simulation.
Run with: python app.py
"""

import os
import io
import base64
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template, request, jsonify

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

from physics.simulation import simulate
from visualization.plots import (
    plot_positions,
    plot_electric_field,
    plot_heatmap,
    plot_energy_history,
    plot_error_analysis,
    PALETTE,
)

app = Flask(__name__)
jobs = {}

# Número de workers para generación paralela de frames
_FRAME_WORKERS = min(4, (os.cpu_count() or 2))


def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return f"data:image/png;base64,{data}"


def compute_error_metrics(energy_history):
    energy = np.array(energy_history)
    if len(energy) < 2:
        return {}
    delta_U = np.abs(np.diff(energy))
    tail    = max(1, len(delta_U) // 10)
    return {
        "delta_U_max":         float(delta_U.max()),
        "delta_U_min":         float(delta_U.min()),
        "delta_U_mean":        float(delta_U.mean()),
        "delta_U_final":       float(delta_U[-1]),
        "convergence_level":   float(np.mean(delta_U[-tail:])),
        "reduccion_total_pct": float((1 - energy[-1] / energy[0]) * 100) if energy[0] != 0 else 0.0,
        "n_pasos":             len(energy) - 1,
    }


def _render_frame(args):
    """Renderiza un frame de animación. Ejecutado en paralelo."""
    snap, energy_so_far, L = args

    fig = plt.figure(figsize=(11, 4), dpi=75)
    fig.patch.set_facecolor(PALETTE["bg"])
    gs  = gridspec.GridSpec(1, 3, figure=fig, wspace=0.38,
                            left=0.06, right=0.97, top=0.86, bottom=0.13)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])
    ax3 = fig.add_subplot(gs[2])

    plot_positions(snap["positions"], snap["charges"], L=L,
                   title=f"t={snap['step']}", ax=ax1, fig=fig)
    # Resolución reducida en animación (60 en vez de 200) — gran ahorro
    plot_heatmap(snap["positions"], snap["charges"], L=L, resolution=60,
                 ax=ax2, fig=fig)
    plot_energy_history(list(energy_so_far), ax=ax3, fig=fig)

    return fig_to_base64(fig)


def run_simulation_job(job_id, params):
    try:
        jobs[job_id]["status"]   = "running"
        jobs[job_id]["progress"] = 5

        # ── 1. Simulación ────────────────────────────────────────────
        result = simulate(
            N=params["N"],
            L=params["L"],
            delta=params["delta"],
            max_iterations=params["max_iterations"],
            n_snapshots=params["n_snapshots"],
            snapshot_interval=max(1, params["max_iterations"] // (params["n_snapshots"] * 10)),
            mode=params["mode"],
        )
        jobs[job_id]["progress"] = 40

        positions_f = result["positions_final"]
        positions_i = result["positions_initial"]
        charges     = result["charges"]
        energy_hist = result["energy_history"]
        snapshots   = result["snapshots"]
        L           = params["L"]

        # ── 2. Tabla de posiciones ────────────────────────────────────
        positions_table = [
            {
                "id":   i + 1,
                "sign": "+" if q > 0 else "−",
                "x":    round(float(pos[0]), 2),
                "y":    round(float(pos[1]), 2),
            }
            for i, (pos, q) in enumerate(zip(positions_f, charges))
        ]

        # ── 3. Gráficas estáticas en paralelo ────────────────────────
        jobs[job_id]["progress"] = 50

        def mk(fn, *a, **kw):
            fig, _ = fn(*a, **kw)
            return fig_to_base64(fig)

        with ThreadPoolExecutor(max_workers=_FRAME_WORKERS) as ex:
            f_init    = ex.submit(mk, plot_positions,     positions_i, charges, L, "Configuración Inicial")
            f_final   = ex.submit(mk, plot_positions,     positions_f, charges, L, "Configuración Final")
            f_field   = ex.submit(mk, plot_electric_field, positions_f, charges, L)
            f_heat    = ex.submit(mk, plot_heatmap,       positions_f, charges, L)
            f_energy  = ex.submit(mk, plot_energy_history, energy_hist)
            f_fi      = ex.submit(mk, plot_electric_field, positions_i, charges, L)
            f_pi      = ex.submit(mk, plot_heatmap,       positions_i, charges, L)
            f_err     = ex.submit(mk, plot_error_analysis, energy_hist)

            img_initial          = f_init.result()
            img_final            = f_final.result()
            img_field            = f_field.result()
            img_heatmap          = f_heat.result()
            img_energy           = f_energy.result()
            img_field_initial    = f_fi.result()
            img_potential_initial= f_pi.result()
            img_error            = f_err.result()

        jobs[job_id]["progress"] = 75

        error_metrics = compute_error_metrics(energy_hist)

        # ── 4. Frames de animación en paralelo ───────────────────────
        energy_accumulator = []
        frame_args = []
        for snap in snapshots:
            energy_accumulator.append(snap["energy"])
            frame_args.append((snap, list(energy_accumulator), L))

        animation_frames = []
        with ThreadPoolExecutor(max_workers=_FRAME_WORKERS) as ex:
            futures = [ex.submit(_render_frame, arg) for arg in frame_args]
            total   = len(futures)
            for k, fut in enumerate(futures):
                animation_frames.append(fut.result())
                # Progreso granular durante frames: 75% → 98%
                jobs[job_id]["progress"] = 75 + int((k + 1) / total * 23)

        # ── 5. Done ──────────────────────────────────────────────────
        jobs[job_id]["progress"] = 100
        jobs[job_id]["status"]   = "done"
        jobs[job_id]["result"]   = {
            "accepted_steps":        result["accepted_steps"],
            "energy_initial":        float(energy_hist[0]),
            "energy_final":          float(energy_hist[-1]),
            "n_positive":            int(np.sum(charges > 0)),
            "n_negative":            int(np.sum(charges < 0)),
            "img_initial":           img_initial,
            "img_final":             img_final,
            "img_field":             img_field,
            "img_heatmap":           img_heatmap,
            "img_energy":            img_energy,
            "img_field_initial":     img_field_initial,
            "img_potential_initial": img_potential_initial,
            "img_error":             img_error,
            "error_metrics":         error_metrics,
            "animation_frames":      animation_frames,
            "positions_table":       positions_table,
        }

    except Exception as e:
        import traceback
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"]  = f"{e}\n{traceback.format_exc()}"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/simulate", methods=["POST"])
def api_simulate():
    data   = request.json
    n_snap = int(data.get("n_snapshots", 20))
    params = {
        "N":              int(data.get("N", 50)),
        "L":              float(data.get("L", 20)),
        "delta":          float(data.get("delta", 0.5)),
        "max_iterations": n_snap * 500,   # escala automática con los instantes
        "n_snapshots":    n_snap,
        "mode":           data.get("mode", "both"),
    }

    job_id       = str(uuid.uuid4())
    jobs[job_id] = {"status": "queued", "progress": 0}

    t = threading.Thread(target=run_simulation_job, args=(job_id, params))
    t.daemon = True
    t.start()

    return jsonify({"job_id": job_id})


@app.route("/api/job/<job_id>", methods=["GET"])
def api_job_status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    if job["status"] == "done":
        return jsonify({"status": "done", "progress": 100, "result": job["result"]})
    elif job["status"] == "error":
        return jsonify({"status": "error", "error": job.get("error", "Unknown error")})
    else:
        return jsonify({"status": job["status"], "progress": job.get("progress", 0)})


if __name__ == "__main__":
    app.run(debug=False, port=5000, threaded=True)