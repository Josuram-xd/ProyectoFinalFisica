"""
app.py — Flask web application for electric charge simulation.
Run with: python app.py
"""

import os
import io
import base64
import json
import threading
import uuid
from flask import Flask, render_template, request, jsonify, send_file

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from physics.simulation import simulate
from visualization.plots import (
    plot_positions,
    plot_electric_field,
    plot_heatmap,
    plot_energy_history,
)

app = Flask(__name__)

# In-memory job storage
jobs = {}


def fig_to_base64(fig):
    """Convert matplotlib figure to base64 string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return f"data:image/png;base64,{data}"


def run_simulation_job(job_id, params):
    """Run simulation in background thread."""
    try:
        jobs[job_id]["status"] = "running"
        jobs[job_id]["progress"] = 10

        result = simulate(
            N=params["N"],
            L=params["L"],
            delta=params["delta"],
            max_iterations=params["max_iterations"],
            n_snapshots=params["n_snapshots"],
            snapshot_interval=100,
            mode=params["mode"],
        )

        jobs[job_id]["progress"] = 70

        positions_f = result["positions_final"]
        positions_i = result["positions_initial"]
        charges = result["charges"]
        energy_hist = result["energy_history"]
        snapshots = result["snapshots"]
        L = params["L"]

        # Generate position table data
        positions_table = []
        for i, (pos, q) in enumerate(zip(positions_f, charges)):
            positions_table.append({
                "id": i + 1,
                "sign": "+" if q > 0 else "−",
                "x": round(float(pos[0]), 2),
                "y": round(float(pos[1]), 2),
            })

        jobs[job_id]["progress"] = 80

        # Generate all plots
        fig, _ = plot_positions(positions_i, charges, L=L, title="Configuración Inicial")
        img_initial = fig_to_base64(fig)

        fig, _ = plot_positions(positions_f, charges, L=L, title="Configuración Final")
        img_final = fig_to_base64(fig)

        fig, _ = plot_electric_field(positions_f, charges, L=L)
        img_field = fig_to_base64(fig)

        fig, _ = plot_heatmap(positions_f, charges, L=L)
        img_heatmap = fig_to_base64(fig)

        fig, _ = plot_energy_history(energy_hist)
        img_energy = fig_to_base64(fig)

        fig, _ = plot_electric_field(positions_i, charges, L=L)
        img_field_initial = fig_to_base64(fig)

        fig, _ = plot_heatmap(positions_i, charges, L=L)
        img_potential_initial = fig_to_base64(fig)

        jobs[job_id]["progress"] = 95

        # Generate animation frames as base64 list
        animation_frames = []
        energy_so_far = []
        for snap in snapshots:
            energy_so_far.append(snap["energy"])

            fig2 = plt.figure(figsize=(12, 4.5), dpi=80)
            fig2.patch.set_facecolor("#0d1117")
            import matplotlib.gridspec as gridspec
            gs = gridspec.GridSpec(1, 3, figure=fig2, wspace=0.35,
                                left=0.06, right=0.97, top=0.88, bottom=0.12)
            ax1 = fig2.add_subplot(gs[0])
            ax2 = fig2.add_subplot(gs[1])
            ax3 = fig2.add_subplot(gs[2])

            plot_positions(snap["positions"], snap["charges"], L=L,
                        title=f"t={snap['step']}", ax=ax1, fig=fig2)
            plot_heatmap(snap["positions"], snap["charges"], L=L, resolution=80,
                        ax=ax2, fig=fig2)
            plot_energy_history(list(energy_so_far), ax=ax3, fig=fig2)

            frame_b64 = fig_to_base64(fig2)
            animation_frames.append(frame_b64)

        jobs[job_id]["progress"] = 100
        jobs[job_id]["status"] = "done"
        jobs[job_id]["result"] = {
            "accepted_steps": result["accepted_steps"],
            "energy_initial": float(energy_hist[0]),
            "energy_final": float(energy_hist[-1]),
            "n_positive": int(np.sum(charges > 0)),
            "n_negative": int(np.sum(charges < 0)),
            "img_initial": img_initial,
            "img_final": img_final,
            "img_field": img_field,
            "img_heatmap": img_heatmap,
            "img_energy": img_energy,
            "img_field_initial": img_field_initial,
            "img_potential_initial": img_potential_initial,
            "animation_frames": animation_frames,
            "positions_table": positions_table,
        }

    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/simulate", methods=["POST"])
def api_simulate():
    data = request.json
    params = {
        "N": int(data.get("N", 50)),
        "L": float(data.get("L", 20)),
        "delta": float(data.get("delta", 0.5)),
        "max_iterations": int(data.get("n_snapshots", 20)) * 100,
        "n_snapshots": int(data.get("n_snapshots", 20)),
        "mode": data.get("mode", "both"),
    }

    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "queued", "progress": 0}

    thread = threading.Thread(target=run_simulation_job, args=(job_id, params))
    thread.daemon = True
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/api/job/<job_id>", methods=["GET"])
def api_job_status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    if job["status"] == "done":
        return jsonify({
            "status": "done",
            "progress": 100,
            "result": job["result"],
        })
    elif job["status"] == "error":
        return jsonify({"status": "error", "error": job.get("error", "Unknown error")})
    else:
        return jsonify({"status": job["status"], "progress": job.get("progress", 0)})


if __name__ == "__main__":
    app.run(debug=True, port=5000)