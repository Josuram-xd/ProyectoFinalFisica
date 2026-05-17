import numpy as np
from scipy.constants import epsilon_0

K = 1 / (4 * np.pi * epsilon_0)


def electric_field(position, charges, gridX, gridY):
    """Campo eléctrico vectorial en una grilla 2D."""
    CampoElectricoX = np.zeros_like(gridX, dtype=np.float64)
    CampoElectricoY = np.zeros_like(gridY, dtype=np.float64)
    # Para cada carga sumar su contribucion al campo electrico, se usa zip para iterar sobre posiciones y cargas simultaneamente
    for posicion, carga_q in zip(position, charges):
        # Se calculan las distancias x, y desde la carga a cada punto de la grilla
        distanciaX = gridX - posicion[0] # 0 porque es la coordenada x de la carga
        distanciaY = gridY - posicion[1] # 1 porque es la coordenada y de la carga
        r  = np.sqrt(distanciaX**2 + distanciaY**2) # distancia desde la carga al punto de la grilla
        r  = np.where(r < 1e-9, 1e-9, r)
        #Se calcula el campo eletrico en cada carga usando la formual E = Ke*q (r_vector / r^3) y se suma a los campos totales
        CampoElectricoX += K * carga_q * distanciaX / r**3
        CampoElectricoY += K * carga_q * distanciaY / r**3
    return CampoElectricoX, CampoElectricoY


def electric_field_magnitude(CampoElectricoX, CampoElectricoY):
    return np.sqrt(CampoElectricoX**2 + CampoElectricoY**2)


def electric_potential(position, charges, gridX, gridY):
    #Se calcula el trabajo necesario para mover una carga desde el infinito hasta las cordenadas de la malla
    potencialElectrico = np.zeros_like(gridX, dtype=np.float64) #el tipo de dato es float64 para evitar problemas de precision
    # el bucle itera sobre cada carga y posicion y calcula su contribucion al potencial electrico usando la formula V = Ke*q/r y se suma al potencial total
    for posicion, carga_q in zip(position, charges):
        distanciaX = gridX - posicion[0]
        distanciaY = gridY - posicion[1]
        # Calcular la distancia r usando la definicion r - r'
        r  = np.sqrt(distanciaX**2 + distanciaY**2)
        r  = np.where(r < 1e-9, 1e-9, r)
        potencialElectrico += K * carga_q / r
    return potencialElectrico


def total_electrostatic_energy(positions, charges):
    energia_total = 0.0
    N = len(charges) # cantidad de cargas
    for i in range(N):
        for j in range(N):
            if i !=j:
                distanciaX = positions[i][0] - positions[j][0]
                distanciaY = positions[i][1] - positions[j][1]
                r = np.sqrt(distanciaX**2 + distanciaY**2)
                if r < 1e-9: #evitar division por cero
                    continue
                energia_total += K * charges[i] * charges[j] / r # energia de interaccion entre las cargas i y j
    return float(energia_total)

def partial_energy(i, positions, charges):
    energia_parcial = 0.0
    N = len(charges)
    for j in range(N):
        if i == j:
            continue
        distanciaX = positions[i][0] - positions[j][0]
        distanciaY = positions[i][1] - positions[j][1]
        r = np.sqrt(distanciaX**2 + distanciaY**2)
        if r < 1e-9: #evitar division por cero
            continue
        energia_parcial += K * charges[i] * charges[j] / r # energia de interaccion entre la carga i y la carga j
    return float(energia_parcial)


def make_grid(lower_bound, upper_bound, resolution=100):
    assert abs(lower_bound) == abs(upper_bound), "Los límites deben ser simétricos."
    x = np.linspace(lower_bound, upper_bound, resolution)
    y = np.linspace(lower_bound, upper_bound, resolution)
    return np.meshgrid(x, y)