import numpy as np
from scipy.constants import epsilon_0

K = 1 / (4 * np.pi * epsilon_0)

def electric_field(
    position: np.ndarray,
    charges: np.ndarray,
    gridX: np.ndarray,
    gridY: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Calcula el campo eléctrico en una grilla debido a un conjunto de cargas."""

    E_x = np.zeros_like(gridX, dtype=np.float64)
    E_y = np.zeros_like(gridY, dtype=np.float64)

    for positions, q in zip(position, charges):
        dX = gridX - positions[0]
        dY = gridY - positions[1]
        distance = np.sqrt(dX**2 + dY**2)
        distance = np.where(distance < 1e-9, 1e-9, distance)
        distance_cubed = distance**3
        E_x += K * q * dX / distance_cubed
        E_y += K * q * dY / distance_cubed

    return E_x, E_y


def electric_field_magnitude(E_x: np.ndarray, E_y: np.ndarray) -> np.ndarray:
    return np.sqrt(E_x**2 + E_y**2)


def electric_potential(
    position: np.ndarray,
    charges: np.ndarray,
    gridX: np.ndarray,
    gridY: np.ndarray,
) -> np.ndarray:
    """Potencial eléctrico V(x,y) = k * sum(q_i / r_i)."""
    V = np.zeros_like(gridX, dtype=np.float64)
    for pos, q in zip(position, charges):
        dx = gridX - pos[0]
        dy = gridY - pos[1]
        r = np.sqrt(dx**2 + dy**2)
        r = np.where(r < 1e-9, 1e-9, r)
        V += K * q / r
    return V


def total_electrostatic_energy(
    positions: np.ndarray, charges: np.ndarray
) -> float:
    """
    Energía electrostática total:
        U = k * sum_{i<j} (q_i * q_j / |r_i - r_j|)
    """
    N = len(charges)
    U = 0.0
    for i in range(N):
        for j in range(i + 1, N):
            dx = positions[i, 0] - positions[j, 0]
            dy = positions[i, 1] - positions[j, 1]
            r = np.sqrt(dx**2 + dy**2)
            if r < 1e-9:
                continue
            U += K * charges[i] * charges[j] / r
    return U


def make_grid(
    lower_bound: float, upper_bound: float, resolution: int = 100
) -> tuple[np.ndarray, np.ndarray]:
    """Crea una malla uniforme 2D."""
    assert abs(lower_bound) == abs(upper_bound), (
        "Los límites deben ser simétricos."
    )
    x = np.linspace(lower_bound, upper_bound, resolution)
    y = np.linspace(lower_bound, upper_bound, resolution)
    return np.meshgrid(x, y)