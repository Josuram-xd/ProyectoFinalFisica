import numpy as np
from scipy.constants import epsilon_0


def electric_field (position: np.ndarray, charges: np.ndarray, gridX: np.ndarray, gridY: np.ndarray) -> np.ndarray:

    """Calcula el campo eléctrico en un punto de interes, debido a un conjunto de cargas."""

    #Definir matrices para almacenar los componentes del campo eléctrico
    E_x = np.zeros_like(gridX, dtype=np.float64)
    E_y = np.zeros_like(gridY, dtype=np.float64)
    K = 1 / (4 * np.pi * epsilon_0)

    for positions, q in zip(position, charges):

        # Calcular las distancias en x, y entre el punto de interes y la carga
        dX = gridX -positions[0]  
        dy = gridY- positions[1] 

        #Calcular la magnitud de la distancia
        distance = np.sqrt(dX**2 + dy**2) 

        # Evitar división por cero al establecer una distancia mínima
        distance = np.where(distance < 1e-9, 1e-9, distance)

        distance_cubed = distance**3

        E_x += K * q * dX / distance_cubed
        E_y += K * q * dy / distance_cubed

        return E_x, E_y

def electric_field_magnitude(E_x: np.ndarray, E_y:np.ndarray) -> np.ndarray:
    return np.sqrt(E_x**2 + E_y**2)

def make_grid(lower_bound:float, upper_bound:float, resolution:int = 100) -> tuple[np.ndarray, np.ndarray]:
    #Asegurar que la magnitud del lado inferior del dominio sea igual a la del lado superior para mantener una cuadrícula uniforme
    assert abs(lower_bound) == abs(upper_bound), "Los límites deben ser simétricos para mantener una cuadrícula uniforme."
    x = np.linspace(lower_bound, upper_bound, resolution)
    y = np.linspace(lower_bound, upper_bound, resolution)
    return np.meshgrid(x, y)    


