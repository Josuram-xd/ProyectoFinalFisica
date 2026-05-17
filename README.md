#  Simulación de Cargas Eléctricas

**Universidad Cooperativa de Colombia · M.Sc. Alejandro Molina**

Aplicación web interactiva para simular la minimización de energía potencial de un sistema de *N* cargas eléctricas puntuales dentro de un dominio cuadrado configurable, con visualizaciones en tiempo real.

---

## Instalación y ejecución

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar la app
python app.py
```

Luego abre tu navegador en: **http://127.0.0.1:5000**

---

## Funcionalidades

| Funcionalidad | Estado |
|---|:---:|
| N cargas con posiciones aleatorias (5–100) | ✅ |
| Cargas `qᵢ = ±1` (solo +, solo −, mixtas) | ✅ |
| Algoritmo de minimización de energía (Monte Carlo) | ✅ |
| Dominio `[−L, L] × [−L, L]` configurable | ✅ |
| Scatter plot inicial vs final (rojo / azul) | ✅ |
| Gráfica de convergencia `U(t)` | ✅ |
| Mapa de calor del potencial eléctrico `V(x, y)` | ✅ |
| Campo eléctrico vectorial (quiver) inicial y final | ✅ |
| Animación de la evolución con velocidad automática | ✅ |
| Tabla de posiciones finales | ✅ |
| Análisis físico automático | ✅ |

---

## Parámetros ajustables

| Parámetro | Descripción |
|---|---|
| **N** | Número de cargas |
| **Tipo** | Solo `+1` / solo `−1` / mixtas |
| **L** | Tamaño del dominio |
| **δ** | Desplazamiento máximo por iteración |
| **Instantes** | Número de frames en la animación (5–60) |
| **Resolución** | Resolución de la grilla para campo y potencial |

---

## Fórmulas implementadas

**Energía potencial total**

```math
U = k \sum_{i \lt j} \frac{q_i \, q_j}{\left|\vec{r}_i - \vec{r}_j\right|}
```

**Campo eléctrico**

```math
\vec{E}(\vec{r}) = k \sum_{i} \frac{q_i \left(\vec{r} - \vec{r}_i\right)}{\left|\vec{r} - \vec{r}_i\right|^3}
```

**Potencial eléctrico**

```math
V(\vec{r}) = k \sum_{i} \frac{q_i}{\left|\vec{r} - \vec{r}_i\right|}
```
