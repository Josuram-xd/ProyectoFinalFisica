import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from .plots import (
    plot_positions,
    plot_electric_field,
    plot_heatmap,
    plot_energy_history,
    save_figure,
    PALETTE,
)


def generate_frame(
    frame_index: int,
    positions: np.ndarray,
    charges: np.ndarray,
    energy_history: list,
    L: float = 20,
    output_dir: str = "frames",
) -> str:
    """
    Genera un frame compuesto con:
    - Scatter plot de posiciones
    - Mapa de calor del potencial
    - Evolución de la energía hasta este instante

    Retorna la ruta al archivo .png guardado.
    """
    os.makedirs(output_dir, exist_ok=True)

    fig = plt.figure(figsize=(12, 4.5), dpi=110)
    fig.patch.set_facecolor(PALETTE["bg"])

    gs = gridspec.GridSpec(1, 3, figure=fig, wspace=0.35, left=0.06, right=0.97,
                        top=0.88, bottom=0.12)

    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])
    ax3 = fig.add_subplot(gs[2])

    plot_positions(positions, charges, L=L,
                title=f"Posiciones — t={frame_index}",
                ax=ax1, fig=fig)

    plot_heatmap(positions, charges, L=L, resolution=120,
                ax=ax2, fig=fig)
    ax2.set_title(f"Potencial V(x,y) — t={frame_index}", fontsize=10, pad=8)

    plot_energy_history(energy_history, ax=ax3, fig=fig)

    fig.text(
        0.5, 0.97,
        f"Simulación de Cargas Eléctricas  ·  Instante {frame_index}",
        ha="center", va="top",
        fontsize=11, color=PALETTE["text"], fontweight="semibold"
    )

    path = os.path.join(output_dir, f"frame_{frame_index:05d}.png")
    save_figure(fig, path)
    return path


def generate_all_frames(
    snapshots: list[dict],
    L: float = 20,
    output_dir: str = "frames",
) -> list[str]:
    """
    Genera todos los frames a partir de una lista de snapshots.
    Cada snapshot es un dict con:
        {
        "step": int,
        "positions": np.ndarray shape (N,2),
        "charges": np.ndarray shape (N,),
        "energy": float
        }

    Retorna lista ordenada de rutas a los .png generados.
    """
    frame_paths = []
    energy_history = []

    for snap in snapshots:
        energy_history.append(snap["energy"])
        path = generate_frame(
            frame_index=snap["step"],
            positions=snap["positions"],
            charges=snap["charges"],
            energy_history=list(energy_history),
            L=L,
            output_dir=output_dir,
        )
        frame_paths.append(path)
        print(f"  Frame {snap['step']:05d} guardado → {path}")

    return frame_paths


def build_video(
    frame_paths: list[str],
    output_path: str = "simulacion.mp4",
    fps: int = 10,
) -> str:
    """
    Ensambla un video MP4 a partir de los frames generados.
    Requiere ffmpeg instalado en el sistema.

    Retorna la ruta al video generado.
    """
    import subprocess, shutil

    if not shutil.which("ffmpeg"):
        raise RuntimeError(
            "ffmpeg no encontrado. Instálalo con: sudo apt install ffmpeg"
        )

    if not frame_paths:
        raise ValueError("No se proporcionaron frames para el video.")

    first_frame_dir = os.path.dirname(frame_paths[0])
    pattern = os.path.join(first_frame_dir, "frame_%05d.png")

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", pattern,
        "-vcodec", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "20",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg error:\n{result.stderr}")

    print(f"Video guardado en: {output_path}")
    return output_path


def build_gif(
    frame_paths: list[str],
    output_path: str = "simulacion.gif",
    fps: int = 5,
    max_frames: int = 60,
) -> str:
    """
    Alternativa ligera: genera un GIF animado con Pillow.
    Ideal cuando no hay ffmpeg disponible.
    """
    from PIL import Image

    if not frame_paths:
        raise ValueError("No se proporcionaron frames para el GIF.")

    step = max(1, len(frame_paths) // max_frames)
    selected = frame_paths[::step]

    images = [Image.open(p).convert("RGB") for p in selected]
    duration_ms = int(1000 / fps)

    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        optimize=True,
        duration=duration_ms,
        loop=0,
    )

    print(f"GIF guardado en: {output_path}  ({len(selected)} frames)")
    return output_path