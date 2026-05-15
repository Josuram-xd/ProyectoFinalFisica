# ⚡ Simulación de Cargas Eléctricas
**Universidad Cooperativa de Colombia · M.Sc. Alejandro Molina**

## Instalación y ejecución

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar la app
python app.py
```

Luego abre tu navegador en: **http://127.0.0.1:5000**

## Funcionalidades incluidas

| Funcionalidad | Estado |
|---|---|
| N=50 cargas con posiciones aleatorias | ✅ |
| Cargas qi = ±1 (solo +, solo -, mixtas) | ✅ |
| Algoritmo de minimización de energía | ✅ |
| Dominio [-L, L] × [-L, L] configurable | ✅ |
| Scatter plot inicial vs final (rojo/azul) | ✅ |
| Gráfica U(t) con convergencia | ✅ |
| Mapa de calor del potencial eléctrico V(x,y) inicial y final | ✅ |
| Campo eléctrico con vectores (quiver) inicial y final | ✅ |
| Animación de la evolución con velocidad automática | ✅ |
| Tabla de posiciones finales | ✅ |
| Análisis físico automático | ✅ |

## Parámetros ajustables

- **N**: número de cargas (5–100)
- **Tipo de cargas**: solo +1 / solo -1 / mixtas
- **L**: tamaño del dominio
- **δ**: desplazamiento máximo por iteración
- **Instantes (video)**: número de frames en la animación (5-60)
- **Resolución** del campo y potencial

## Fórmulas implementadas

**Energía total:**
U = k Σ_{i<j} q_i q_j / |r_i - r_j|

**Campo eléctrico:**
E⃗(r⃗) = k Σ_i q_i (r⃗ - r⃗_i) / |r⃗ - r⃗_i|³

**Potencial eléctrico:**
V(r⃗) = k Σ_i q_i / |r⃗ - r⃗_i|
