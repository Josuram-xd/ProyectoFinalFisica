# import streamlit as st
# import streamlit.components.v1 as components
# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.colors as mcolors
# from matplotlib.patches import FancyArrowPatch
# import io
# import imageio
# import tempfile
# import os
# import time 
# import json

# # ─────────────────────────────────────────────
# # PAGE CONFIG
# # ─────────────────────────────────────────────
# st.set_page_config(
#     page_title="Simulación de Cargas Eléctricas",
#     page_icon="⚡",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

# # ─────────────────────────────────────────────
# # CUSTOM CSS
# # ─────────────────────────────────────────────
# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

# html, body, [class*="css"] {
#     font-family: 'Syne', sans-serif;
# }
# h1, h2, h3 {
#     font-family: 'Syne', sans-serif;
#     font-weight: 800;
#     letter-spacing: -0.03em;
# }
# code, .stCode {
#     font-family: 'Space Mono', monospace !important;
# }

# /* Sidebar */
# [data-testid="stSidebar"] {
#     background: linear-gradient(180deg, #0a0a1a 0%, #0d1b2a 100%);
#     border-right: 1px solid #1e3a5f;
# }
# [data-testid="stSidebar"] * {
#     color: #e0eaff !important;
# }
# [data-testid="stSidebar"] .stSlider > label,
# [data-testid="stSidebar"] .stSelectbox > label,
# [data-testid="stSidebar"] .stNumberInput > label {
#     color: #7eb8f7 !important;
#     font-size: 0.75rem;
#     text-transform: uppercase;
#     letter-spacing: 0.1em;
# }

# /* Main */
# .main {
#     background: #05050f;
#     color: #e0eaff;
# }
# .stApp {
#     background: #05050f;
# }

# /* Metric cards */
# .metric-card {
#     background: linear-gradient(135deg, #0d1b2a, #1a2744);
#     border: 1px solid #1e3a5f;
#     border-radius: 12px;
#     padding: 1rem 1.25rem;
#     text-align: center;
# }
# .metric-label {
#     font-size: 0.7rem;
#     text-transform: uppercase;
#     letter-spacing: 0.12em;
#     color: #5b8db8;
#     margin-bottom: 0.3rem;
# }
# .metric-value {
#     font-family: 'Space Mono', monospace;
#     font-size: 1.4rem;
#     color: #7eb8f7;
#     font-weight: 700;
# }

# /* Section headers */
# .section-header {
#     font-family: 'Syne', sans-serif;
#     font-size: 0.7rem;
#     text-transform: uppercase;
#     letter-spacing: 0.15em;
#     color: #5b8db8;
#     border-bottom: 1px solid #1e3a5f;
#     padding-bottom: 0.4rem;
#     margin-bottom: 1rem;
# }

# /* Buttons */
# .stButton > button {
#     background: linear-gradient(135deg, #1a3a6b, #0f2447);
#     color: #7eb8f7;
#     border: 1px solid #2a5fa8;
#     border-radius: 8px;
#     font-family: 'Space Mono', monospace;
#     font-size: 0.8rem;
#     text-transform: uppercase;
#     letter-spacing: 0.08em;
#     padding: 0.5rem 1.5rem;
#     transition: all 0.2s;
# }
# .stButton > button:hover {
#     background: linear-gradient(135deg, #2a5fa8, #1a3a6b);
#     border-color: #7eb8f7;
#     color: #ffffff;
# }

# /* Title area */
# .title-area {
#     padding: 1.5rem 0 1rem;
#     border-bottom: 1px solid #1e3a5f;
#     margin-bottom: 1.5rem;
# }
# .title-area h1 {
#     color: #e0eaff;
#     font-size: 2rem;
#     margin: 0;
# }
# .title-area p {
#     color: #5b8db8;
#     font-family: 'Space Mono', monospace;
#     font-size: 0.75rem;
#     margin: 0.3rem 0 0;
# }
# </style>
# """, unsafe_allow_html=True)

# # ─────────────────────────────────────────────
# # PHYSICS FUNCTIONS
# # ─────────────────────────────────────────────
# def compute_energy(positions, charges, k=1.0):
#     N = len(charges)
#     U = 0.0
#     for i in range(N):
#         for j in range(i + 1, N):
#             r = np.linalg.norm(positions[i] - positions[j])
#             if r > 1e-10:
#                 U += k * charges[i] * charges[j] / r
#     return U

# def compute_energy_fast(positions, charges, k=1.0):
#     """Vectorized energy computation"""
#     diff = positions[:, np.newaxis, :] - positions[np.newaxis, :, :]
#     dist = np.sqrt((diff**2).sum(axis=2))
#     np.fill_diagonal(dist, np.inf)
#     qi_qj = charges[:, np.newaxis] * charges[np.newaxis, :]
#     U = 0.5 * k * np.sum(qi_qj / dist)
#     return U

# def compute_electric_field(x_grid, y_grid, positions, charges, k=1.0):
#     Ex = np.zeros_like(x_grid)
#     Ey = np.zeros_like(y_grid)
#     for i, (pos, q) in enumerate(zip(positions, charges)):
#         dx = x_grid - pos[0]
#         dy = y_grid - pos[1]
#         r3 = (dx**2 + dy**2)**1.5
#         r3 = np.where(r3 < 1e-6, 1e-6, r3)
#         Ex += k * q * dx / r3
#         Ey += k * q * dy / r3
#     return Ex, Ey

# def compute_electric_potential(x_grid, y_grid, positions, charges, k=1.0):
#     V = np.zeros_like(x_grid)
#     for i, (pos, q) in enumerate(zip(positions, charges)):
#         dx = x_grid - pos[0]
#         dy = y_grid - pos[1]
#         r = np.sqrt(dx**2 + dy**2)
#         r = np.where(r < 0.1, 0.1, r)
#         V += k * q / r
#     return V

# def run_simulation(N, L, delta, n_steps, charge_mode, k=1.0,
#                    custom_positions=None, custom_charges=None):
#     """Run the energy minimization simulation."""
#     if custom_positions is not None and len(custom_positions) > 0:
#         positions = np.array(custom_positions, dtype=float)
#         charges   = np.array(custom_charges,   dtype=float)
#         N = len(charges)
#     else:
#         np.random.seed(42)
#         positions = np.random.uniform(-L, L, (N, 2))
#         if charge_mode == "Solo positivas (+1)":
#             charges = np.ones(N)
#         elif charge_mode == "Solo negativas (-1)":
#             charges = -np.ones(N)
#         else:
#             charges = np.where(np.random.rand(N) > 0.5, 1.0, -1.0)

#     energy = compute_energy_fast(positions, charges, k)

#     history_energy = [energy]
#     history_iter = [0]
#     history_positions = [positions.copy()]

#     accepted = 0
#     for step in range(1, n_steps + 1):
#         idx = np.random.randint(N)
#         displacement = np.random.uniform(-delta, delta, 2)
#         new_pos = positions[idx] + displacement

#         if not (-L <= new_pos[0] <= L and -L <= new_pos[1] <= L):
#             continue

#         new_positions = positions.copy()
#         new_positions[idx] = new_pos
#         new_energy = compute_energy_fast(new_positions, charges, k)

#         if new_energy < energy:
#             positions = new_positions
#             energy = new_energy
#             accepted += 1
#             history_energy.append(energy)
#             history_iter.append(step)
#             # Save every 10th accepted config to avoid memory issues
#             if accepted % max(1, n_steps // 200) == 0:
#                 history_positions.append(positions.copy())

#     history_positions.append(positions.copy())

#     return {
#         "positions": positions,
#         "charges": charges,
#         "energy_history": np.array(history_energy),
#         "iter_history": np.array(history_iter),
#         "position_history": history_positions,
#         "initial_positions": history_positions[0],
#         "accepted": accepted,
#         "final_energy": energy,
#     }

# # ─────────────────────────────────────────────
# # PLOT FUNCTIONS
# # ─────────────────────────────────────────────
# DARK_BG = "#05050f"
# PLOT_BG = "#080818"
# GRID_COLOR = "#1a2744"
# TEXT_COLOR = "#7eb8f7"

# def style_ax(ax, title=""):
#     ax.set_facecolor(PLOT_BG)
#     ax.tick_params(colors=TEXT_COLOR, labelsize=8)
#     for spine in ax.spines.values():
#         spine.set_edgecolor(GRID_COLOR)
#     ax.grid(True, color=GRID_COLOR, linewidth=0.5, alpha=0.7)
#     if title:
#         ax.set_title(title, color=TEXT_COLOR, fontsize=10, fontweight='bold', pad=8)

# def plot_scatter(positions, charges, L, title="Configuración"):
#     fig, ax = plt.subplots(figsize=(5, 5))
#     fig.patch.set_facecolor(DARK_BG)
#     style_ax(ax, title)

#     pos_mask = charges > 0
#     neg_mask = charges < 0

#     if pos_mask.any():
#         ax.scatter(positions[pos_mask, 0], positions[pos_mask, 1],
#                    c='#ff4d6d', s=80, zorder=5, edgecolors='#ff8fa3',
#                    linewidths=0.8, label="Positiva (+1)")
#     if neg_mask.any():
#         ax.scatter(positions[neg_mask, 0], positions[neg_mask, 1],
#                    c='#4d94ff', s=80, zorder=5, edgecolors='#80b3ff',
#                    linewidths=0.8, label="Negativa (-1)")

#     ax.set_xlim(-L, L)
#     ax.set_ylim(-L, L)
#     ax.set_xlabel("x", color=TEXT_COLOR, fontsize=9)
#     ax.set_ylabel("y", color=TEXT_COLOR, fontsize=9)
#     ax.legend(facecolor=PLOT_BG, edgecolor=GRID_COLOR,
#                labelcolor=TEXT_COLOR, fontsize=8)
#     plt.tight_layout()
#     return fig

# def plot_energy_history(energy_history, iter_history):
#     fig, ax = plt.subplots(figsize=(7, 3.5))
#     fig.patch.set_facecolor(DARK_BG)
#     style_ax(ax, "Energía Electrostática U(t)")

#     ax.plot(iter_history, energy_history, color='#7eb8f7',
#             linewidth=1.2, alpha=0.9)
#     ax.fill_between(iter_history, energy_history,
#                     alpha=0.15, color='#4d94ff')
#     ax.set_xlabel("Iteración aceptada", color=TEXT_COLOR, fontsize=9)
#     ax.set_ylabel("U (u.a.)", color=TEXT_COLOR, fontsize=9)
#     plt.tight_layout()
#     return fig

# def plot_electric_field(positions, charges, L, grid_n=20):
#     x = np.linspace(-L, L, grid_n)
#     y = np.linspace(-L, L, grid_n)
#     X, Y = np.meshgrid(x, y)
#     Ex, Ey = compute_electric_field(X, Y, positions, charges)
#     E_mag = np.sqrt(Ex**2 + Ey**2)
#     Ex_n = Ex / (E_mag + 1e-10)
#     Ey_n = Ey / (E_mag + 1e-10)

#     fig, ax = plt.subplots(figsize=(5, 5))
#     fig.patch.set_facecolor(DARK_BG)
#     style_ax(ax, "Campo Eléctrico |E⃗|")

#     heatmap = ax.contourf(X, Y, np.log1p(E_mag), levels=30,
#                            cmap='plasma', alpha=0.85)
#     ax.quiver(X, Y, Ex_n, Ey_n, color='white', alpha=0.5,
#               scale=25, width=0.003)

#     pos_mask = charges > 0
#     neg_mask = charges < 0
#     if pos_mask.any():
#         ax.scatter(positions[pos_mask, 0], positions[pos_mask, 1],
#                    c='#ff4d6d', s=80, zorder=5, edgecolors='white', linewidths=0.8)
#     if neg_mask.any():
#         ax.scatter(positions[neg_mask, 0], positions[neg_mask, 1],
#                    c='#4d94ff', s=80, zorder=5, edgecolors='white', linewidths=0.8)

#     cbar = plt.colorbar(heatmap, ax=ax)
#     cbar.ax.tick_params(colors=TEXT_COLOR, labelsize=7)
#     cbar.set_label("log(|E|+1)", color=TEXT_COLOR, fontsize=8)
#     ax.set_xlim(-L, L); ax.set_ylim(-L, L)
#     ax.set_xlabel("x", color=TEXT_COLOR, fontsize=9)
#     ax.set_ylabel("y", color=TEXT_COLOR, fontsize=9)
#     plt.tight_layout()
#     return fig

# def plot_potential_heatmap(positions, charges, L, grid_n=60):
#     x = np.linspace(-L, L, grid_n)
#     y = np.linspace(-L, L, grid_n)
#     X, Y = np.meshgrid(x, y)
#     V = compute_electric_potential(X, Y, positions, charges)

#     fig, ax = plt.subplots(figsize=(5, 5))
#     fig.patch.set_facecolor(DARK_BG)
#     style_ax(ax, "Potencial Eléctrico V(x,y)")

#     vmax = np.percentile(np.abs(V), 95)
#     hm = ax.contourf(X, Y, V, levels=40,
#                       cmap='RdBu_r', vmin=-vmax, vmax=vmax, alpha=0.9)

#     pos_mask = charges > 0
#     neg_mask = charges < 0
#     if pos_mask.any():
#         ax.scatter(positions[pos_mask, 0], positions[pos_mask, 1],
#                    c='#ff4d6d', s=80, zorder=5, edgecolors='white', linewidths=0.8)
#     if neg_mask.any():
#         ax.scatter(positions[neg_mask, 0], positions[neg_mask, 1],
#                    c='#4d94ff', s=80, zorder=5, edgecolors='white', linewidths=0.8)

#     cbar = plt.colorbar(hm, ax=ax)
#     cbar.ax.tick_params(colors=TEXT_COLOR, labelsize=7)
#     cbar.set_label("V (u.a.)", color=TEXT_COLOR, fontsize=8)
#     ax.set_xlim(-L, L); ax.set_ylim(-L, L)
#     ax.set_xlabel("x", color=TEXT_COLOR, fontsize=9)
#     ax.set_ylabel("y", color=TEXT_COLOR, fontsize=9)
#     plt.tight_layout()
#     return fig

# def generate_gif(position_history, charges, L, max_frames=60):
#     """Generate animation GIF from position history."""
#     frames_idx = np.linspace(0, len(position_history) - 1,
#                               min(max_frames, len(position_history)), dtype=int)
#     images = []
#     for idx in frames_idx:
#         pos = position_history[idx]
#         fig, ax = plt.subplots(figsize=(4, 4))
#         fig.patch.set_facecolor(DARK_BG)
#         style_ax(ax)
#         pos_mask = charges > 0
#         neg_mask = charges < 0
#         if pos_mask.any():
#             ax.scatter(pos[pos_mask, 0], pos[pos_mask, 1],
#                        c='#ff4d6d', s=60, edgecolors='#ff8fa3', linewidths=0.8)
#         if neg_mask.any():
#             ax.scatter(pos[neg_mask, 0], pos[neg_mask, 1],
#                        c='#4d94ff', s=60, edgecolors='#80b3ff', linewidths=0.8)
#         ax.set_xlim(-L, L); ax.set_ylim(-L, L)
#         ax.set_xlabel("x", color=TEXT_COLOR, fontsize=8)
#         ax.set_ylabel("y", color=TEXT_COLOR, fontsize=8)
#         buf = io.BytesIO()
#         plt.savefig(buf, format='png', dpi=80, facecolor=DARK_BG)
#         buf.seek(0)
#         images.append(imageio.imread(buf))
#         plt.close(fig)

#     gif_buf = io.BytesIO()
#     imageio.mimsave(gif_buf, images, format='GIF', fps=10)
#     gif_buf.seek(0)
#     return gif_buf

# # ─────────────────────────────────────────────
# # INTERACTIVE CANVAS
# # Arquitectura: canvas HTML5 con click/drag completos.
# # Comunicación JS→Python via st.query_params:
# #   - JS escribe  ?charges=<json_b64>  en la URL (mismo origen, sin restricción)
# #   - Streamlit lee st.query_params["charges"] en cada rerun
# #   - Un botón "Aplicar" dentro del iframe dispara window.location.reload()
# #     para forzar el rerun de Streamlit con los nuevos query_params
# # ─────────────────────────────────────────────

# import urllib.parse
# import base64


# def _encode_charges(charges_list: list) -> str:
#     """Serializa la lista de cargas a base64 URL-safe para query_params."""
#     raw = json.dumps(charges_list, separators=(",", ":"))
#     return base64.urlsafe_b64encode(raw.encode()).decode()


# def _decode_charges(b64: str) -> list:
#     """Decodifica el base64 de query_params a lista de cargas."""
#     if isinstance(b64, list):
#         b64 = b64[0]
#     b64 = b64 or ""
#     # Base64 URL-safe enviado desde JS puede omitir el relleno '='.
#     padding = len(b64) % 4
#     if padding:
#         b64 += "=" * (4 - padding)
#     raw = base64.urlsafe_b64decode(b64.encode()).decode()
#     return json.loads(raw)


# def charge_canvas(L, default_N=10, charge_mode="Mixtas (+1 y -1)"):
#     """
#     Canvas interactivo.
#     Comunicacion JS->Python:
#       El iframe NO puede tocar window.parent por cross-origin en produccion.
#       Solucion: el iframe hace window.location.href = '/?charges=...' apuntando
#       a SI MISMO (la URL del iframe), y Streamlit recoge esos query_params
#       en el padre en el siguiente rerun porque components.html renderiza en
#       el mismo servidor.
#       PERO la forma mas simple y confiable: el iframe tiene un <form> con
#       method=GET que navega window.top (toda la ventana) a la URL de Streamlit
#       con los query params. Esto siempre funciona.
#     """
#     # ── Inicializar session_state ─────────────
#     if "charges_on_canvas" not in st.session_state:
#         st.session_state.charges_on_canvas = []
#     if "canvas_add_mode" not in st.session_state:
#         st.session_state.canvas_add_mode = "➕ Positiva"
#     if "simulate_requested" not in st.session_state:
#         st.session_state.simulate_requested = False

#     # ── Leer datos enviados via query_params ─────────────────────────────
#     qp = st.query_params
#     if "charges" in qp:
#         try:
#             incoming = _decode_charges(qp["charges"])
#             if isinstance(incoming, list) and len(incoming) > 0:
#                 incoming = [{"x": float(c["x"]), "y": float(c["y"]),
#                              "charge": float(c["charge"])} for c in incoming]
#                 st.session_state.charges_on_canvas = incoming
#                 st.session_state.result = None
#         except Exception as ex:
#             pass
#         if "simulate" in qp:
#             st.session_state.simulate_requested = True
#         st.query_params.clear()
#         st.rerun()

#     # ── Toolbar ──────────────────────────────
#     col_t1, col_t2, col_t3, col_t4, col_t5 = st.columns([1.5, 1.1, 1.1, 0.9, 0.9])

#     with col_t1:
#         mode_idx = 0 if st.session_state.canvas_add_mode == "➕ Positiva" else 1
#         add_mode = st.radio(
#             "Carga al insertar",
#             ["➕ Positiva", "➖ Negativa"],
#             index=mode_idx,
#             horizontal=False,
#             key="canvas_mode_radio",
#         )
#         if add_mode != st.session_state.canvas_add_mode:
#             st.session_state.canvas_add_mode = add_mode

#     with col_t2:
#         st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
#         if st.button("🎲 Aleatorio", use_container_width=True):
#             np.random.seed(None)
#             new_charges = []
#             for _ in range(default_N):
#                 if charge_mode == "Solo positivas (+1)":
#                     q = 1.0
#                 elif charge_mode == "Solo negativas (-1)":
#                     q = -1.0
#                 else:
#                     q = 1.0 if np.random.rand() > 0.5 else -1.0
#                 new_charges.append({
#                     "x": float(np.random.uniform(-L * 0.85, L * 0.85)),
#                     "y": float(np.random.uniform(-L * 0.85, L * 0.85)),
#                     "charge": q,
#                 })
#             st.session_state.charges_on_canvas = new_charges
#             st.session_state.result = None
#             st.rerun()

#     with col_t3:
#         st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
#         if st.button("✖ Limpiar todo", use_container_width=True):
#             st.session_state.charges_on_canvas = []
#             st.session_state.result = None
#             st.rerun()

#     with col_t4:
#         n_pos = sum(1 for c in st.session_state.charges_on_canvas if c["charge"] > 0)
#         st.markdown(f"""
#         <div class="metric-card" style="padding:0.5rem;">
#             <div class="metric-label">Positivas</div>
#             <div class="metric-value" style="color:#ff4d6d;font-size:1.2rem;">{n_pos}</div>
#         </div>""", unsafe_allow_html=True)

#     with col_t5:
#         n_neg = sum(1 for c in st.session_state.charges_on_canvas if c["charge"] < 0)
#         st.markdown(f"""
#         <div class="metric-card" style="padding:0.5rem;">
#             <div class="metric-label">Negativas</div>
#             <div class="metric-value" style="color:#4d94ff;font-size:1.2rem;">{n_neg}</div>
#         </div>""", unsafe_allow_html=True)

#     st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

#     st.markdown("""
#     <div style="font-family:'Space Mono',monospace;font-size:11px;color:#5b8db8;
#                 text-align:center;padding:2px 0 6px;letter-spacing:0.06em;">
#         Click izq. insertar &nbsp;|&nbsp; Click der. borrar &nbsp;|&nbsp; Arrastrar mover
#     </div>""", unsafe_allow_html=True)

#     # ── Canvas HTML ──────────────────────────
#     charges_json = json.dumps(st.session_state.charges_on_canvas, separators=(",", ":"))
#     q_value      = 1.0 if st.session_state.canvas_add_mode == "➕ Positiva" else -1.0

#     # La clave: el iframe navega window.top (toda la pagina del navegador)
#     # a la URL base de Streamlit + query params.
#     # window.top.location siempre es accesible cuando mismo origen (localhost).
#     # En Streamlit Cloud tambien funciona porque el origen es el mismo dominio.
#     canvas_html = f"""<!DOCTYPE html>
# <html>
# <head><meta charset="utf-8">
# <style>
# * {{ margin:0; padding:0; box-sizing:border-box; }}
# body {{ background:#05050f; overflow:hidden; }}
# #wrap {{ display:flex; flex-direction:column; align-items:center; padding:4px 4px 0; }}
# canvas {{ border:1px solid #1e3a5f; border-radius:8px; display:block; cursor:crosshair; touch-action:none; }}
# #btns {{ display:flex; gap:8px; margin-top:6px; width:100%; max-width:580px; }}
# button {{ flex:1; padding:7px 0; border-radius:6px; border:1px solid; font-family:monospace;
#          font-size:12px; font-weight:700; letter-spacing:0.06em; cursor:pointer; transition:all .15s; }}
# #btn-apply {{ background:#0f2447; border-color:#2a5fa8; color:#7eb8f7; }}
# #btn-apply:hover {{ background:#1a3a6b; color:#fff; }}
# #btn-sim {{ background:#0f3020; border-color:#2a8a50; color:#5de0a0; }}
# #btn-sim:hover {{ background:#1a5030; color:#fff; }}
# #status {{ font-family:monospace; font-size:10px; color:#3a6a9a; text-align:center; margin-top:3px; height:14px; }}
# </style>
# </head>
# <body>
# <div id="wrap">
#   <canvas id="c"></canvas>
#   <div id="btns">
#     <button id="btn-apply">Guardar cambios</button>
#     <button id="btn-sim">Guardar y Simular</button>
#   </div>
#   <div id="status">sin cambios pendientes</div>
# </div>
# <script>
# const L     = {L};
# const Q_ADD = {q_value};
# let charges = {charges_json};
# let dirty   = false;
# let dragIdx = -1, mouseDown = false, movedDuringDrag = false;

# const canvas = document.getElementById('c');
# const ctx    = canvas.getContext('2d');
# const status = document.getElementById('status');

# function resize() {{
#   const W = Math.min(window.innerWidth - 12, 580);
#   canvas.width = W; canvas.height = W; draw();
# }}
# function toCanvas(wx, wy) {{
#   const s = canvas.width / (2*L);
#   return [(wx+L)*s, (L-wy)*s];
# }}
# function toWorld(cx, cy) {{
#   const s = canvas.width / (2*L);
#   return [cx/s - L, L - cy/s];
# }}
# function getCanvasXY(e) {{
#   const rect = canvas.getBoundingClientRect();
#   const sx = canvas.width/rect.width, sy = canvas.height/rect.height;
#   const cx = e.touches ? e.touches[0].clientX : e.clientX;
#   const cy = e.touches ? e.touches[0].clientY : e.clientY;
#   return [(cx-rect.left)*sx, (cy-rect.top)*sy];
# }}
# function nearest(wx, wy) {{
#   let minD=Infinity, minI=-1;
#   charges.forEach((c,i) => {{ const d=Math.hypot(c.x-wx,c.y-wy); if(d<minD){{minD=d;minI=i;}} }});
#   return {{idx:minI, dist:minD}};
# }}

# function draw() {{
#   const W = canvas.width;
#   ctx.clearRect(0,0,W,W);
#   ctx.fillStyle='#080818'; ctx.fillRect(0,0,W,W);
#   ctx.strokeStyle='#1a2744'; ctx.lineWidth=0.5;
#   const step=W/10;
#   for(let i=0;i<=10;i++) {{
#     ctx.beginPath(); ctx.moveTo(i*step,0); ctx.lineTo(i*step,W); ctx.stroke();
#     ctx.beginPath(); ctx.moveTo(0,i*step); ctx.lineTo(W,i*step); ctx.stroke();
#   }}
#   ctx.strokeStyle='#2a4a6b'; ctx.lineWidth=1.5;
#   let [ax0,ay0]=toCanvas(0,-L),[ax1,ay1]=toCanvas(0,L);
#   let [bx0,by0]=toCanvas(-L,0),[bx1,by1]=toCanvas(L,0);
#   ctx.beginPath(); ctx.moveTo(ax0,ay0); ctx.lineTo(ax1,ay1); ctx.stroke();
#   ctx.beginPath(); ctx.moveTo(bx0,by0); ctx.lineTo(bx1,by1); ctx.stroke();
#   ctx.fillStyle='#5b8db8'; ctx.font='10px monospace';
#   ctx.fillText('x',W-12,W/2-5); ctx.fillText('y',W/2+4,12);
#   ctx.font='8px monospace';
#   ctx.fillText(`-${{L}}`,2,W-2); ctx.fillText(`${{L}}`,W-16,10);

#   const R = Math.max(9, W*0.021);
#   charges.forEach((c,i) => {{
#     const [px,py]=toCanvas(c.x,c.y);
#     const isPos=c.charge>0;
#     const fill=isPos?'#ff4d6d':'#4d94ff';
#     const ring=isPos?'#ff8fa3':'#80b3ff';
#     const isDrag=(i===dragIdx);
#     const glowR=isDrag?R*3.5:R*2.5;
#     const grdA=isDrag?(isPos?'rgba(255,77,109,0.55)':'rgba(77,148,255,0.55)')
#                      :(isPos?'rgba(255,77,109,0.28)':'rgba(77,148,255,0.28)');
#     const grd=ctx.createRadialGradient(px,py,R*0.2,px,py,glowR);
#     grd.addColorStop(0,grdA); grd.addColorStop(1,'rgba(0,0,0,0)');
#     ctx.beginPath(); ctx.arc(px,py,glowR,0,Math.PI*2); ctx.fillStyle=grd; ctx.fill();
#     if(isDrag){{ ctx.shadowColor=isPos?'#ff4d6d':'#4d94ff'; ctx.shadowBlur=18; }}
#     ctx.beginPath(); ctx.arc(px,py,R,0,Math.PI*2);
#     ctx.fillStyle=fill; ctx.fill();
#     ctx.strokeStyle=isDrag?'white':ring; ctx.lineWidth=isDrag?2.5:1.8; ctx.stroke();
#     ctx.shadowBlur=0;
#     ctx.fillStyle='white';
#     ctx.font=`bold ${{Math.round(R*1.15)}}px monospace`;
#     ctx.textAlign='center'; ctx.textBaseline='middle';
#     ctx.fillText(isPos?'+':'−',px,py+1);
#   }});
#   ctx.textAlign='left'; ctx.textBaseline='alphabetic';
#   const nPos=charges.filter(c=>c.charge>0).length;
#   const nNeg=charges.filter(c=>c.charge<0).length;
#   ctx.fillStyle='rgba(8,8,24,0.78)'; ctx.fillRect(4,4,170,20);
#   ctx.fillStyle=dirty?'#e0c060':'#5b8db8'; ctx.font='9px monospace';
#   ctx.fillText(`${{charges.length}} cargas  (+${{nPos}} / -${{nNeg}})${{dirty?' *':''}}`,8,18);
# }}

# function markDirty() {{
#   dirty=true;
#   status.textContent='* cambios sin guardar';
#   status.style.color='#c0a020';
# }}

# // ── Enviar datos a Streamlit ─────────────────────────────────────────
# // Navegamos window.top (la ventana completa del navegador, no el iframe)
# // a la URL base de Streamlit con los query params.
# // Esto siempre funciona: mismo origen en local y en Streamlit Cloud.
# function pushCharges(andSimulate) {{
#   const rounded = charges.map(c => ({{
#     x: Math.round(c.x*10000)/10000,
#     y: Math.round(c.y*10000)/10000,
#     charge: c.charge
#   }}));
#   const raw = JSON.stringify(rounded);
#   const b64 = btoa(unescape(encodeURIComponent(raw)))
#                 .replace(/[+]/g,'-').replace(/[/]/g,'_').replace(/=/g,'');
#   const param = andSimulate ? 'charges='+b64+'&simulate=1' : 'charges='+b64;

#   // Obtener la URL raiz de Streamlit (quitar todo lo que sea path del iframe)
#   // En Streamlit, la app corre en / o en un subpath configurado.
#   // window.top.location.href es la URL del navegador principal.
#   let base;
#   try {{
#     base = window.top.location.href.split('?')[0];
#   }} catch(e) {{
#     // Si hay restriccion cross-origin (raro en Streamlit)
#     base = '/';
#   }}
#   window.top.location.href = base + '?' + param;

#   status.textContent = andSimulate ? 'Simulando...' : 'Guardado, recargando...';
#   status.style.color = '#5de0a0';
#   dirty = false;
# }}

# document.getElementById('btn-apply').addEventListener('click', () => pushCharges(false));
# document.getElementById('btn-sim').addEventListener('click',   () => pushCharges(true));

# // ── Mouse events ─────────────────────────────
# canvas.addEventListener('contextmenu', e => e.preventDefault());

# canvas.addEventListener('mousedown', e => {{
#   e.preventDefault(); mouseDown=true; movedDuringDrag=false;
#   const [cx,cy]=getCanvasXY(e);
#   const [wx,wy]=toWorld(cx,cy);
#   if(e.button===2) {{
#     if(!charges.length) return;
#     const {{idx,dist}}=nearest(wx,wy);
#     if(idx>=0 && dist<L*0.15) {{ charges.splice(idx,1); draw(); markDirty(); }}
#     return;
#   }}
#   if(e.button===0) {{
#     const {{idx,dist}}=nearest(wx,wy);
#     if(idx>=0 && dist<L*0.07) {{ dragIdx=idx; canvas.style.cursor='grabbing'; }}
#   }}
# }});

# canvas.addEventListener('mousemove', e => {{
#   if(!mouseDown||dragIdx<0) {{
#     const [cx,cy]=getCanvasXY(e);
#     const [wx,wy]=toWorld(cx,cy);
#     const {{idx,dist}}=nearest(wx,wy);
#     canvas.style.cursor=(idx>=0&&dist<L*0.07)?'grab':'crosshair';
#     return;
#   }}
#   e.preventDefault(); movedDuringDrag=true;
#   const [cx,cy]=getCanvasXY(e);
#   let [wx,wy]=toWorld(cx,cy);
#   wx=Math.max(-L,Math.min(L,wx)); wy=Math.max(-L,Math.min(L,wy));
#   charges[dragIdx].x=wx; charges[dragIdx].y=wy; draw();
# }});

# canvas.addEventListener('mouseup', e => {{
#   e.preventDefault();
#   if(e.button===0) {{
#     if(dragIdx>=0) {{
#       dragIdx=-1; canvas.style.cursor='crosshair';
#       if(movedDuringDrag) markDirty();
#     }} else if(!movedDuringDrag) {{
#       const [cx,cy]=getCanvasXY(e);
#       const [wx,wy]=toWorld(cx,cy);
#       if(wx<-L||wx>L||wy<-L||wy>L) {{ mouseDown=false; return; }}
#       if(!charges.some(c=>Math.hypot(c.x-wx,c.y-wy)<L*0.06)) {{
#         charges.push({{x:wx,y:wy,charge:Q_ADD}}); draw(); markDirty();
#       }}
#     }}
#   }}
#   mouseDown=false; movedDuringDrag=false;
# }});

# canvas.addEventListener('mouseleave', e => {{
#   if(dragIdx>=0) {{
#     dragIdx=-1; canvas.style.cursor='crosshair';
#     if(movedDuringDrag) markDirty();
#     movedDuringDrag=false; mouseDown=false;
#   }}
# }});

# window.addEventListener('resize', resize);
# resize();
# </script>
# </body>
# </html>"""

#     components.html(canvas_html, height=660, scrolling=False)

#     # ── Controles Python bajo el canvas ──────────────────────────────────
#     col_sim1, col_sim2 = st.columns([2, 1])
#     with col_sim1:
#         with st.expander("📍 O introduce coordenadas manualmente"):
#             col_x, col_y, col_btn = st.columns([1, 1, 1.2])
#             with col_x:
#                 x_manual = st.number_input("x", value=0.0, step=0.1,
#                                            min_value=float(-L), max_value=float(L), key="x_input_canvas")
#             with col_y:
#                 y_manual = st.number_input("y", value=0.0, step=0.1,
#                                            min_value=float(-L), max_value=float(L), key="y_input_canvas")
#             with col_btn:
#                 st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
#                 if st.button("➕ Insertar", use_container_width=True, key="btn_insert_canvas"):
#                     charges_list = st.session_state.charges_on_canvas
#                     threshold = L * 0.06
#                     too_close = any(
#                         ((c["x"] - x_manual)**2 + (c["y"] - y_manual)**2)**0.5 < threshold
#                         for c in charges_list
#                     )
#                     if not too_close:
#                         q = 1.0 if st.session_state.canvas_add_mode == "➕ Positiva" else -1.0
#                         charges_list.append({"x": x_manual, "y": y_manual, "charge": q})
#                         st.session_state.charges_on_canvas = charges_list
#                         st.session_state.result = None
#                         st.rerun()

#     with col_sim2:
#         if len(st.session_state.charges_on_canvas) >= 2:
#             if st.button("⚡ Simular ahora", use_container_width=True, type="primary"):
#                 st.session_state.simulate_requested = True
#                 st.rerun()

#     # ── Retornar datos ────────────────────────────────────────────────────
#     if len(st.session_state.charges_on_canvas) >= 2:
#         return {
#             "positions": [[c["x"], c["y"]] for c in st.session_state.charges_on_canvas],
#             "charges":   [c["charge"] for c in st.session_state.charges_on_canvas],
#         }
#     return None



# # ─────────────────────────────────────────────
# # SESSION STATE
# # ─────────────────────────────────────────────
# if "result" not in st.session_state:
#     st.session_state.result = None
# if "gif_bytes" not in st.session_state:
#     st.session_state.gif_bytes = None
# if "canvas_data" not in st.session_state:
#     st.session_state.canvas_data = None
# if "charges_on_canvas" not in st.session_state:
#     st.session_state.charges_on_canvas = []

# # ─────────────────────────────────────────────
# # SIDEBAR
# # ─────────────────────────────────────────────
# with st.sidebar:
#     st.markdown("## ⚡ Parámetros")
#     st.markdown('<div class="section-header">Sistema de cargas</div>', unsafe_allow_html=True)

#     N = st.slider("N — Número de cargas (aleatorio)", 5, 100, 10,
#                   help="Solo aplica si usas 🎲 Aleatorio en el canvas")
#     charge_mode = st.selectbox("Tipo de cargas (aleatorio)", [
#         "Solo positivas (+1)",
#         "Solo negativas (-1)",
#         "Mixtas (+1 y -1)"
#     ], help="Solo aplica si usas 🎲 Aleatorio en el canvas")
#     L = st.slider("L — Tamaño del dominio [-L, L]", 1.0, 20.0, 5.0, 0.5)

#     st.markdown('<div class="section-header">Algoritmo</div>', unsafe_allow_html=True)
#     delta = st.slider("δ — Desplazamiento máximo", 0.01, 2.0, 0.1, 0.01)
#     n_steps = st.select_slider("Iteraciones", [500, 1000, 5000, 10000, 50000], value=5000)

#     st.markdown('<div class="section-header">Visualización</div>', unsafe_allow_html=True)
#     field_grid = st.slider("Resolución campo eléctrico", 10, 40, 20)
#     potential_grid = st.slider("Resolución potencial", 30, 100, 60)

#     st.markdown("---")
#     gen_gif_btn = st.button("🎬  Generar Video/GIF", use_container_width=True,
#                              disabled=st.session_state.result is None)

# # ─────────────────────────────────────────────
# # TITLE
# # ─────────────────────────────────────────────
# st.markdown("""
# <div class="title-area">
#     <h1>⚡ Simulación de Cargas Eléctricas</h1>
#     <p>Universidad Cooperativa de Colombia · M.Sc. Alejandro Molina · Minimización de Energía Electrostática</p>
# </div>
# """, unsafe_allow_html=True)

# # ─────────────────────────────────────────────
# # CANVAS + AUTO-SIMULATE
# # ─────────────────────────────────────────────
# st.markdown('<div class="section-header">🖱️ Haz click en el canvas para añadir cargas · La simulación corre automáticamente</div>',
#             unsafe_allow_html=True)

# canvas_result = charge_canvas(L, default_N=N, charge_mode=charge_mode)

# # Simular cuando:
# #   1) Se pidio explicitamente (boton Guardar y Simular o Simular ahora), O
# #   2) Hay cargas suficientes y aun no hay resultado
# should_simulate = (
#     st.session_state.get("simulate_requested", False) or
#     (canvas_result is not None and st.session_state.result is None)
# )

# if should_simulate and canvas_result is not None and isinstance(canvas_result, dict):
#     positions_raw = canvas_result.get("positions", [])
#     charges_raw   = canvas_result.get("charges",   [])
#     if len(positions_raw) >= 2:
#         st.session_state.simulate_requested = False
#         st.session_state.canvas_data = canvas_result
#         st.session_state.gif_bytes = None
#         with st.spinner("Simulando..."):
#             t0 = time.time()
#             result_sim = run_simulation(
#                 N, L, delta, n_steps, charge_mode,
#                 custom_positions=positions_raw,
#                 custom_charges=charges_raw
#             )
#             result_sim["elapsed"] = time.time() - t0
#             st.session_state.result = result_sim
#     else:
#         st.session_state.simulate_requested = False

# if gen_gif_btn and st.session_state.result:
#     with st.spinner("Generando GIF de animación..."):
#         res = st.session_state.result
#         gif_bytes = generate_gif(res["position_history"], res["charges"], L)
#         st.session_state.gif_bytes = gif_bytes.getvalue() if hasattr(gif_bytes, 'getvalue') else gif_bytes

# # ─────────────────────────────────────────────
# # RESULTS
# # ─────────────────────────────────────────────
# result = st.session_state.result

# if result is None:
#     st.markdown("""
#     <div style='text-align:center; padding: 3rem 2rem; color: #2a4a6b;
#                 border: 1px dashed #1e3a5f; border-radius: 12px; margin-top:1rem;'>
#         <div style='font-size:2rem;'>👆</div>
#         <div style='font-size:0.9rem; font-family:Space Mono,monospace; margin-top:0.5rem;'>
#             Agrega al menos 2 cargas en el canvas — la simulación corre automáticamente
#         </div>
#     </div>
#     """, unsafe_allow_html=True)
# else:
#     N_actual = len(result["charges"])

#     # ── Metrics ──────────────────────────────
#     c1, c2, c3, c4, c5 = st.columns(5)
#     metrics = [
#         ("Cargas", str(N_actual)),
#         ("Aceptadas", f"{result['accepted']:,}"),
#         ("U inicial", f"{result['energy_history'][0]:.2f}"),
#         ("U final", f"{result['final_energy']:.2f}"),
#         ("CPU", f"{result['elapsed']:.2f}s"),
#     ]
#     for col, (label, val) in zip([c1, c2, c3, c4, c5], metrics):
#         with col:
#             st.markdown(f"""
#             <div class="metric-card">
#                 <div class="metric-label">{label}</div>
#                 <div class="metric-value">{val}</div>
#             </div>""", unsafe_allow_html=True)

#     st.markdown("<br>", unsafe_allow_html=True)

#     # ── Scatter: Initial vs Final ─────────────
#     st.markdown('<div class="section-header">📍 Configuración Espacial</div>', unsafe_allow_html=True)
#     col_a, col_b = st.columns(2)
#     with col_a:
#         fig_init = plot_scatter(result["initial_positions"], result["charges"], L,
#                                 title="Configuración Inicial (tu dibujo)")
#         st.pyplot(fig_init, use_container_width=True)
#         plt.close(fig_init)
#     with col_b:
#         fig_final = plot_scatter(result["positions"], result["charges"], L,
#                                  title="Configuración Final (minimizada)")
#         st.pyplot(fig_final, use_container_width=True)
#         plt.close(fig_final)

#     # ── Energy history ────────────────────────
#     st.markdown('<div class="section-header">📉 Evolución de la Energía U(t)</div>', unsafe_allow_html=True)
#     fig_energy = plot_energy_history(result["energy_history"], result["iter_history"])
#     st.pyplot(fig_energy, use_container_width=True)
#     plt.close(fig_energy)

#     delta_U = result["energy_history"][-1] - result["energy_history"][0]
#     if abs(result["energy_history"][0]) > 1e-10:
#         reduction_pct = abs(delta_U / result["energy_history"][0]) * 100
#     else:
#         reduction_pct = 0.0
#     st.caption(f"📊 Reducción total de energía: {delta_U:.4f} u.a. ({reduction_pct:.1f}%)")

#     # ── Electric field + Potential ────────────
#     st.markdown('<div class="section-header">🔬 Campo Eléctrico y Potencial (Configuración Final)</div>',
#                 unsafe_allow_html=True)
#     col_c, col_d = st.columns(2)
#     with col_c:
#         with st.spinner("Calculando campo eléctrico..."):
#             fig_field = plot_electric_field(result["positions"], result["charges"],
#                                             L, grid_n=field_grid)
#             st.pyplot(fig_field, use_container_width=True)
#             plt.close(fig_field)
#     with col_d:
#         with st.spinner("Calculando potencial eléctrico..."):
#             fig_pot = plot_potential_heatmap(result["positions"], result["charges"],
#                                              L, grid_n=potential_grid)
#             st.pyplot(fig_pot, use_container_width=True)
#             plt.close(fig_pot)

#     # ── GIF / Video ───────────────────────────
#     st.markdown('<div class="section-header">🎬 Animación de la Evolución</div>', unsafe_allow_html=True)
#     if st.session_state.gif_bytes:
#         st.image(st.session_state.gif_bytes, caption="Evolución del sistema de cargas")
#         st.download_button("⬇ Descargar GIF", st.session_state.gif_bytes,
#                            file_name="simulacion_cargas.gif", mime="image/gif")
#     else:
#         st.info("Presiona **🎬 Generar Video/GIF** en el panel lateral para crear la animación.")

#     # ── Physical Analysis ─────────────────────
#     st.markdown('<div class="section-header">🧪 Análisis Físico</div>', unsafe_allow_html=True)

#     n_pos = int((result["charges"] > 0).sum())
#     n_neg = int((result["charges"] < 0).sum())
#     U_i   = result["energy_history"][0]
#     U_f   = result["final_energy"]
#     mixed = n_pos > 0 and n_neg > 0

#     analysis_text = f"""
# **Sistema:** {N_actual} cargas | {n_pos} positivas, {n_neg} negativas | Dominio [-{L}, {L}] × [-{L}, {L}]

# **Energía inicial:** {U_i:.4f} u.a. → **Energía final:** {U_f:.4f} u.a. (reducción del {reduction_pct:.1f}%)

# **Interpretación física:**
# - **Repulsión (mismo signo):** Las cargas del mismo signo se alejan entre sí para minimizar la energía positiva.
# {"- **Atracción (signos opuestos):** Las cargas opuestas se acercan para maximizar la energía negativa (término negativo en U), reduciendo la energía total." if mixed else ""}
# - **Convergencia:** La gráfica U(t) muestra tendencia decreciente → el algoritmo encuentra mínimos locales.
# - **Campo eléctrico:** Las flechas apuntan alejándose de cargas positivas (+) y hacia cargas negativas (−).
# - **Potencial:** Regiones rojas = alto potencial (cargas +), regiones azules = bajo potencial (cargas −).
# - **Zonas de alta intensidad:** El campo es más intenso cerca de las cargas, donde r → 0 y E ∝ 1/r².
#     """
#     st.markdown(analysis_text)

#     # ── Raw Data ──────────────────────────────
#     with st.expander(" Ver datos numéricos de la simulación"):
#         import pandas as pd
#         df_pos = pd.DataFrame({
#             "x": result["positions"][:, 0],
#             "y": result["positions"][:, 1],
#             "carga": result["charges"]
#         })
#         st.dataframe(df_pos, use_container_width=True)
#         csv = df_pos.to_csv(index=False).encode()
#         st.download_button("⬇ Descargar posiciones finales (CSV)", csv,
#                            "posiciones_finales.csv", "text/csv")

#         df_energy = pd.DataFrame({
#             "iteracion": result["iter_history"],
#             "energia": result["energy_history"]
#         })
#         csv_e = df_energy.to_csv(index=False).encode()
#         st.download_button("⬇ Descargar historia de energía (CSV)", csv_e,
#                            "energia_historia.csv", "text/csv")