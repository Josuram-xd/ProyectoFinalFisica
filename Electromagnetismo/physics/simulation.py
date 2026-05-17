import numpy as np
from .energy import total_electrostatic_energy


def initialize_charges(
    N: int = 50,
    L: float = 20,
    mode: str = "both",
    seed: int = None, #esta semilla se usa para genear posiciones y cargas aleatorias de manera reproducible 
) -> tuple[np.ndarray, np.ndarray]:

    rng = np.random.default_rng(seed) # se crea un generador de numeros aleatorios con semilla none, lo que garantiza numeros diferentes
    positions = rng.uniform(-L, L, size=(N, 2)) #posiciones aleatorias dentro del cuadrado [-L, L] x [-L, L]

    if mode == "positive":
        charges = np.ones(N)
    elif mode == "negative":
        charges = -np.ones(N)
    else:
        charges = rng.choice([-1, 1], size=N) #cargas aleatorias de +1 o -1 con igual probabilidad

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
    
    #A continuacion se implementara el algoritmo de minimizacion de energia 

    #crear un generador de numero aleatorios
    rng = np.random.default_rng(seed)
    #inicializar posiciones y cargas aleatorias usando la funcion initialize_charges
    positions, charges = initialize_charges(N, L, mode, seed)
    #guardar las posiciones iniciales para compararlas con las finales usando copy
    positions_initial = positions.copy()

    U = total_electrostatic_energy(positions, charges)
    # se crea una lista para almacenar la energia total del sistema en cada paso 
    energy_history = [U]
    # se crea una lista para almacenar posiciones, cargas y energia en cada snapshot
    snapshots = []
    # contador de pasos aceptados para controlar los snapshots basados en intervalos de pasos aceptados
    accepted_steps = 0

    if snapshot_interval is None:
        # Si no se especifica un intervalo de snapshots, se calculan los pasos específicos para tomar snapshots basados en el número total de iteraciones y el número deseado de snapshots
        snap_steps = set(
            np.round(np.linspace(0, max_iterations - 1, n_snapshots)).astype(int)
        )
    else:
        #si existe un intervalo de snapshots se usa el contador de pasos aceptados para determinar cuando tomar un snapshot
        snap_steps = None

    snapshots.append({
        #se inicializan los valores del primer snapshot
        "step": 0,
        "positions": positions.copy(),
        "charges": charges.copy(),
        "energy": U,
    })

    #crea un bucle que itera sobre el numero maximo de iteraciones para intentar mover las cargas y minimizar la energia del sistema
    for iteration in range(max_iterations):
        #selecciona una carga aleatoria y un angulo aleatorio para determinar la direccion del movimiento
        i = rng.integers(0, N)
        angle = rng.uniform(0, 2 * np.pi)
        # se calculan los desplazamientos dx y dy usando el angulo y mutliplicandole a cada componente la distancia delta 
        dx = delta * np.cos(angle)
        dy = delta * np.sin(angle)

        # se crea una nueva posicion para la carga seleccionada sumando el desplazamiento a su posicion actual
        new_pos = positions[i] + np.array([dx, dy])

        # Verificar que la nueva posición esté dentro del dominio [−L, L]²
        if np.any(np.abs(new_pos) > L):
            continue

        #Se guarda la posicion anterior de la carga seleccionada para poder revertir el movimiento si la energia no disminuye
        old_pos = positions[i].copy()
        # se define la nueva posicion y se calcula la nueva energia total del sisteam
        positions[i] = new_pos
        U_new = total_electrostatic_energy(positions, charges)


        # Aceptar el movimiento solo si la energía disminuye
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