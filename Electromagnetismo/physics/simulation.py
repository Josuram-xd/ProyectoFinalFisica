import numpy as np
from .energy import total_electrostatic_energy


def initialize_charges(
    N: int = 50,
    L: float = 20,
    mode: str = "both",
    seed: int = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Inicializa posiciones aleatorias y cargas.

    mode:
        "positive"  → todas q_i = +1
        "negative"  → todas q_i = −1
        "both"      → mitad +1, mitad −1 (aleatorio)
    """
    rng = np.random.default_rng(seed)
    positions = rng.uniform(-L, L, size=(N, 2))

    if mode == "positive":
        charges = np.ones(N)
    elif mode == "negative":
        charges = -np.ones(N)
    else:
        charges = rng.choice([-1.0, 1.0], size=N)

    return positions, charges


def simulate(
    N: int = 50,
    L: float = 20,
    delta: float = 0.5,
    max_iterations: int = 10_000,
    n_snapshots: int = 20,
    snapshot_interval: float = None,
    mode: str = "both",
    seed: int = None,
) -> dict:
    """
    Simulación de minimización de energía electrostática.

    Algoritmo:
    1. Seleccionar una carga aleatoria.
    2. Moverla un pequeño desplazamiento δ en dirección aleatoria.
    3. Aceptar solo si la nueva posición está dentro de [−L, L]² 
        y la energía total disminuye.

    Parámetros
    ----------
    N                : número de cargas
    L                : mitad del lado del dominio
    delta            : magnitud máxima del desplazamiento
    max_iterations   : iteraciones totales del algoritmo
    n_snapshots      : cantidad de instantes a capturar
    snapshot_interval: intervalo en iteraciones aceptadas entre snapshots
                    (si None, se distribuyen uniformemente)
    mode             : 'positive', 'negative', 'both'
    seed             : semilla aleatoria

    Retorna
    -------
    dict con:
        positions_final  : ndarray (N,2)
        charges          : ndarray (N,)
        positions_initial: ndarray (N,2)
        energy_history   : lista de U en cada paso aceptado
        snapshots        : lista de dicts {step, positions, charges, energy}
        accepted_steps   : int
    """
    rng = np.random.default_rng(seed)
    positions, charges = initialize_charges(N, L, mode, seed)
    positions_initial = positions.copy()

    U = total_electrostatic_energy(positions, charges)
    energy_history = [U]
    snapshots = []
    accepted_steps = 0

    if snapshot_interval is None:
        snap_steps = set(
            np.round(np.linspace(0, max_iterations - 1, n_snapshots)).astype(int)
        )
    else:
        snap_steps = None

    snapshots.append({
        "step": 0,
        "positions": positions.copy(),
        "charges": charges.copy(),
        "energy": U,
    })

    for iteration in range(max_iterations):
        i = rng.integers(0, N)
        angle = rng.uniform(0, 2 * np.pi)
        dx = delta * np.cos(angle)
        dy = delta * np.sin(angle)

        new_pos = positions[i] + np.array([dx, dy])

        if np.any(np.abs(new_pos) > L):
            continue

        old_pos = positions[i].copy()
        positions[i] = new_pos
        U_new = total_electrostatic_energy(positions, charges)

        if U_new < U:
            U = U_new
            energy_history.append(U)
            accepted_steps += 1

            should_snap = (
                (snap_steps is not None and iteration in snap_steps)
                or (snapshot_interval is not None and accepted_steps % snapshot_interval == 0)
            )

            if should_snap:
                snapshots.append({
                    "step": accepted_steps,
                    "positions": positions.copy(),
                    "charges": charges.copy(),
                    "energy": U,
                })
        else:
            positions[i] = old_pos

    snapshots.append({
        "step": accepted_steps,
        "positions": positions.copy(),
        "charges": charges.copy(),
        "energy": U,
    })

    return {
        "positions_final": positions,
        "charges": charges,
        "positions_initial": positions_initial,
        "energy_history": energy_history,
        "snapshots": snapshots,
        "accepted_steps": accepted_steps,
    }