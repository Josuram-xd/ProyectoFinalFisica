import numpy as np
from scipy.constants import epsilon_0

K = 1 / (4 * np.pi * epsilon_0)


def electric_field(position, charges, gridX, gridY):
    """Campo eléctrico vectorial en una grilla 2D."""
    E_x = np.zeros_like(gridX, dtype=np.float64)
    E_y = np.zeros_like(gridY, dtype=np.float64)
    for pos, q in zip(position, charges):
        dX = gridX - pos[0]
        dY = gridY - pos[1]
        r  = np.sqrt(dX**2 + dY**2)
        r  = np.where(r < 1e-9, 1e-9, r)
        E_x += K * q * dX / r**3
        E_y += K * q * dY / r**3
    return E_x, E_y


def electric_field_magnitude(E_x, E_y):
    return np.sqrt(E_x**2 + E_y**2)


def electric_potential(position, charges, gridX, gridY):
    """Potencial eléctrico V(x,y) = k * Σ(q_i / r_i)."""
    V = np.zeros_like(gridX, dtype=np.float64)
    for pos, q in zip(position, charges):
        dx = gridX - pos[0]
        dy = gridY - pos[1]
        r  = np.sqrt(dx**2 + dy**2)
        r  = np.where(r < 1e-9, 1e-9, r)
        V += K * q / r
    return V


def total_electrostatic_energy(positions, charges):
    """
    Energía electrostática total vectorizada con NumPy.
    U = k * Σ_{i<j} (q_i * q_j / |r_i - r_j|)

    Complexity: O(N²) pero en C via NumPy, ~50x más rápido que el doble for Python.
    """
    # Diferencias vectorizadas: diff[i,j] = positions[i] - positions[j]
    diff = positions[:, np.newaxis, :] - positions[np.newaxis, :, :]  # (N, N, 2)
    dist = np.sqrt((diff ** 2).sum(axis=2))                           # (N, N)

    # Máscara triangular superior (i < j) para no duplicar pares
    mask = np.triu(np.ones_like(dist, dtype=bool), k=1)

    # Evitar división por cero en diagonal (ya excluida por mask, pero por seguridad)
    dist_safe = np.where(mask, dist, 1.0)

    # Producto de cargas q_i * q_j
    q_prod = charges[:, np.newaxis] * charges[np.newaxis, :]          # (N, N)

    U = K * np.sum(q_prod[mask] / dist_safe[mask])
    return float(U)


def partial_energy(i, positions, charges):
    """
    Energía de interacción de la carga i con todas las demás.
    Usado para el cálculo incremental en la simulación:
        ΔU = partial_energy(i, new) - partial_energy(i, old)

    Vectorizado: O(N) en NumPy en lugar de O(N²) completo.
    """
    diff = positions[i] - positions          # (N, 2)
    dist = np.sqrt((diff ** 2).sum(axis=1))  # (N,)
    dist[i] = np.inf                         # excluir auto-interacción
    dist = np.where(dist < 1e-9, 1e-9, dist)
    return float(K * np.sum(charges[i] * charges / dist))


def make_grid(lower_bound, upper_bound, resolution=100):
    assert abs(lower_bound) == abs(upper_bound), "Los límites deben ser simétricos."
    x = np.linspace(lower_bound, upper_bound, resolution)
    y = np.linspace(lower_bound, upper_bound, resolution)
    return np.meshgrid(x, y)