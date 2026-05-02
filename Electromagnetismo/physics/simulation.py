import numpy as np
from scipy.constants import epsilon_0
from .energy import kinetic_energy, potential_energy

def simulate_motion(mass, initial_velocity, initial_height, time_steps, gravity=9.81):

    dt = 0.1  # Intervalo de tiempo en segundos
    positions = []
    velocities = []
    kinetic_energies = []
    potential_energies = []

    velocity = initial_velocity
    height = initial_height

    for step in range(time_steps):
        # Actualizar posición y velocidad
        height -= velocity * dt
        velocity -= gravity * dt

        # Calcular energías
        ke = kinetic_energy(mass, velocity)
        pe = potential_energy(mass, height, gravity)

        # Guardar datos
        positions.append(height)
        velocities.append(velocity)
        kinetic_energies.append(ke)
        potential_energies.append(pe)

    return {
        "positions": np.array(positions),
        "velocities": np.array(velocities),
        "kinetic_energies": np.array(kinetic_energies),
        "potential_energies": np.array(potential_energies)
    }


