import numpy as np
import matplotlib
matplotlib.use('Agg')  # Usar un backend que no requiera una interfaz gráfica
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
from scipy.constants import epsilon_0

K = 1 / (4 * np.pi * epsilon_0)

PALETTE = {
    "bg":         "#9c9fa5",
    "surface":    "#414447",
    "border":     "#21262d",
    "accent":     "#1ea4d4",
    "accent2":    "#00cfb4",
    "positive":   "#e05252",
    "negative":   "#4a9eff",
    "text":       "#021d38",
    "muted":      "#203144",
}

def _apply_dark_style(fig, ax):
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.set_facecolor(PALETTE["surface"])
    ax.tick_params(colors=PALETTE["muted"], labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(PALETTE["border"])
    ax.xaxis.label.set_color(PALETTE["muted"])
    ax.yaxis.label.set_color(PALETTE["muted"])
    ax.title.set_color(PALETTE["text"])

def plot_positions(positions, charges, L=20, title="Posiciones de Cargas", ax=None, fig=None):
    """
    Scatter plot de las posiciones de las cargas.
    Rojo = positiva  ;  Azul = negativa
    """
    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(5, 5), dpi=110)
    _apply_dark_style(fig, ax)
    pos_mask = charges > 0
    neg_mask = charges < 0

    if pos_mask.any():
        ax.scatter(
            positions[pos_mask, 0], positions[pos_mask, 1],
            c=PALETTE["positive"], s=60, zorder=5,
            edgecolors="white", linewidths=0.4, label="Positiva (+)", alpha=0.92
        )
    if neg_mask.any():
        ax.scatter(
            positions[neg_mask, 0], positions[neg_mask, 1],
            c=PALETTE["negative"], s=60, zorder=5,
            edgecolors="white", linewidths=0.4, label="Negativa (−)", alpha=0.92
        )

    ax.set_xlim(-L, L)
    ax.set_ylim(-L, L)
    ax.set_xlabel("x", fontsize=9)
    ax.set_ylabel("y", fontsize=9)
    ax.set_title(title, fontsize=10, pad=8)
    ax.set_aspect("equal")
    ax.axhline(0, color=PALETTE["border"], lw=0.6)
    ax.axvline(0, color=PALETTE["border"], lw=0.6)

    legend = ax.legend(
        fontsize=7, framealpha=0.15, edgecolor=PALETTE["border"],
        labelcolor=PALETTE["text"], loc="upper right"
    )
    legend.get_frame().set_facecolor(PALETTE["surface"])

    if standalone:
        fig.tight_layout()
    return fig, ax

def plot_electric_field(positions, charges, L=20, resolution=25, ax=None, fig=None):
    """
    Campo eléctrico como quiver plot normalizado por magnitud.
    """
    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(5, 5), dpi=110)

    _apply_dark_style(fig, ax)

    x = np.linspace(-L, L, resolution)
    y = np.linspace(-L, L, resolution)
    gx, gy = np.meshgrid(x, y)

    Ex = np.zeros_like(gx)
    Ey = np.zeros_like(gy)

    for (px, py), q in zip(positions, charges):
        dx = gx - px
        dy = gy - py
        r = np.sqrt(dx**2 + dy**2)
        r = np.where(r < 0.5, 0.5, r)
        Ex += K * q * dx / r**3
        Ey += K * q * dy / r**3

    magnitude = np.sqrt(Ex**2 + Ey**2)
    magnitude = np.where(magnitude == 0, 1, magnitude)
    Ex_n = Ex / magnitude
    Ey_n = Ey / magnitude

    log_mag = np.log1p(magnitude / magnitude.max() * 100)

    ax.quiver(
        gx, gy, Ex_n, Ey_n,
        log_mag,
        cmap="plasma",
        scale=30, width=0.003,
        pivot="mid", alpha=0.85
    )

    pos_mask = charges > 0
    neg_mask = charges < 0
    if pos_mask.any():
        ax.scatter(positions[pos_mask, 0], positions[pos_mask, 1],
                c=PALETTE["positive"], s=55, zorder=6, edgecolors="white", linewidths=0.4)
    if neg_mask.any():
        ax.scatter(positions[neg_mask, 0], positions[neg_mask, 1],
                c=PALETTE["negative"], s=55, zorder=6, edgecolors="white", linewidths=0.4)

    ax.set_xlim(-L, L)
    ax.set_ylim(-L, L)
    ax.set_xlabel("x", fontsize=9)
    ax.set_ylabel("y", fontsize=9)
    ax.set_title("Campo Eléctrico", fontsize=10, pad=8)
    ax.set_aspect("equal")

    if standalone:
        fig.tight_layout()
    return fig, ax

def plot_heatmap(positions, charges, L=20, resolution=200, ax=None, fig=None):
    """
    Mapa de calor del potencial eléctrico V(x,y).
    Caliente = potencial positivo, Frío = potencial negativo.
    """
    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(5, 5), dpi=110)

    _apply_dark_style(fig, ax)

    x = np.linspace(-L, L, resolution)
    y = np.linspace(-L, L, resolution)
    gx, gy = np.meshgrid(x, y)

    V = np.zeros_like(gx)
    for (px, py), q in zip(positions, charges):
        dx = gx - px
        dy = gy - py
        r = np.sqrt(dx**2 + dy**2)
        r = np.where(r < 0.3, 0.3, r)
        V += K * q / r

    V_clipped = np.clip(V, np.percentile(V, 2), np.percentile(V, 98))

    colors_list = [
        (0.18, 0.38, 0.80),
        (0.12, 0.12, 0.20),
        (0.75, 0.22, 0.22),
    ]
    cmap_custom = LinearSegmentedColormap.from_list("electro", colors_list, N=512)

    img = ax.imshow(
        V_clipped, extent=[-L, L, -L, L],
        origin="lower", cmap=cmap_custom, aspect="equal",
        interpolation="bilinear"
    )

    cbar = plt.colorbar(img, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(colors=PALETTE["muted"], labelsize=7)
    cbar.set_label("V (V)", color=PALETTE["muted"], fontsize=8)
    cbar.ax.yaxis.set_tick_params(color=PALETTE["muted"])

    pos_mask = charges > 0
    neg_mask = charges < 0
    if pos_mask.any():
        ax.scatter(positions[pos_mask, 0], positions[pos_mask, 1],
                c=PALETTE["positive"], s=50, zorder=6,
                edgecolors="white", linewidths=0.5, label="(+)")
    if neg_mask.any():
        ax.scatter(positions[neg_mask, 0], positions[neg_mask, 1],
                c=PALETTE["negative"], s=50, zorder=6,
                edgecolors="white", linewidths=0.5, label="(−)")

    ax.set_xlabel("x", fontsize=9)
    ax.set_ylabel("y", fontsize=9)
    ax.set_title("Potencial Eléctrico V(x,y)", fontsize=10, pad=8)

    legend = ax.legend(fontsize=7, framealpha=0.2, edgecolor=PALETTE["border"],
                    labelcolor=PALETTE["text"])
    legend.get_frame().set_facecolor(PALETTE["surface"])

    if standalone:
        fig.tight_layout()
    return fig, ax

def plot_energy_history(energy_history, ax=None, fig=None):
    """
    Gráfica de U(t) en función de iteraciones aceptadas.
    """
    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(figsize=(7, 3.5), dpi=110)

    _apply_dark_style(fig, ax)

    steps = np.arange(len(energy_history))
    ax.plot(steps, energy_history, color=PALETTE["accent"], lw=1.4, alpha=0.9, zorder=3)
    ax.fill_between(steps, energy_history,
                    alpha=0.12, color=PALETTE["accent"], zorder=2)

    ax.set_xlabel("Iteraciones aceptadas (t)", fontsize=9)
    ax.set_ylabel("U (J)", fontsize=9)
    ax.set_title("Evolución de la Energía Electrostática U(t)", fontsize=10, pad=8)
    ax.grid(True, color=PALETTE["border"], lw=0.5, alpha=0.6)

    if len(energy_history) > 0:
        ax.annotate(
            f"U_final = {energy_history[-1]:.3e} J",
            xy=(steps[-1], energy_history[-1]),
            xytext=(-80, 16),
            textcoords="offset points",
            fontsize=8,
            color=PALETTE["accent2"],
            arrowprops=dict(arrowstyle="->", color=PALETTE["accent2"], lw=0.8),
        )

    if standalone:
        fig.tight_layout()
    return fig, ax

def save_figure(fig, path):
    fig.savefig(path, dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)