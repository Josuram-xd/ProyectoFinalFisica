import numpy as np
from .energy import partial_energy, total_electrostatic_energy


def initialize_charges(N=50, L=20, mode="both", seed=None):
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
    N=50,
    L=20,
    delta=0.5,
    max_iterations=10_000,
    n_snapshots=20,
    snapshot_interval=100,
    mode="both",
    seed=None,
):
    """
    Minimización de energía electrostática — versión optimizada.

    Optimización clave: en lugar de recalcular U total (O(N²)) en cada iteración,
    solo recalcula la energía parcial de la carga movida (O(N)).
    Esto da una aceleración de ~N veces en el loop principal.
    """
    rng = np.random.default_rng(seed)
    positions, charges = initialize_charges(N, L, mode, seed)
    positions_initial  = positions.copy()

    # Energía total inicial (una sola vez)
    U              = total_electrostatic_energy(positions, charges)
    energy_history = [U]
    snapshots      = []
    accepted_steps = 0

    # Snapshot inicial
    snapshots.append({
        "step":      0,
        "positions": positions.copy(),
        "charges":   charges.copy(),
        "energy":    U,
    })

    # Pre-generar todos los números aleatorios de una vez (mucho más rápido)
    indices = rng.integers(0, N, size=max_iterations)
    angles  = rng.uniform(0, 2 * np.pi, size=max_iterations)
    cos_a   = np.cos(angles)
    sin_a   = np.sin(angles)

    for iteration in range(max_iterations):
        i       = indices[iteration]
        new_pos = positions[i] + delta * np.array([cos_a[iteration], sin_a[iteration]])

        # Rechazar si sale del dominio
        if np.any(np.abs(new_pos) > L):
            continue

        # Cálculo incremental: solo la energía parcial de la carga i
        U_i_old = partial_energy(i, positions, charges)

        old_pos      = positions[i].copy()
        positions[i] = new_pos

        U_i_new = partial_energy(i, positions, charges)
        delta_U = U_i_new - U_i_old

        if delta_U < 0:
            # Aceptar: actualizar energía total con el delta
            U += delta_U
            energy_history.append(U)
            accepted_steps += 1

            if accepted_steps % snapshot_interval == 0:
                snapshots.append({
                    "step":      accepted_steps,
                    "positions": positions.copy(),
                    "charges":   charges.copy(),
                    "energy":    U,
                })
        else:
            positions[i] = old_pos

    # Snapshot final
    snapshots.append({
        "step":      accepted_steps,
        "positions": positions.copy(),
        "charges":   charges.copy(),
        "energy":    U,
    })

    # Reducir a n_snapshots uniformemente distribuidos
    if len(snapshots) > n_snapshots:
        idx       = np.round(np.linspace(0, len(snapshots) - 1, n_snapshots)).astype(int)
        snapshots = [snapshots[k] for k in idx]

    return {
        "positions_final":   positions,
        "charges":           charges,
        "positions_initial": positions_initial,
        "energy_history":    energy_history,
        "snapshots":         snapshots,
        "accepted_steps":    accepted_steps,
    }