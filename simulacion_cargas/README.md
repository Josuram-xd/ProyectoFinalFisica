# ⚡ Simulación de Cargas Eléctricas
**Universidad Cooperativa de Colombia · M.Sc. Alejandro Molina**

## Instalación y ejecución

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar la app
streamlit run app.py
```

Luego abre tu navegador en: **http://localhost:8501**

## Funcionalidades incluidas

| Funcionalidad | Estado |
|---|---|
| N=50 cargas con posiciones aleatorias | ✅ |
| Cargas qi = ±1 (solo +, solo -, mixtas) | ✅ |
| Algoritmo de minimización de energía | ✅ |
| Dominio [-L, L] × [-L, L] configurable | ✅ |
| Scatter plot inicial vs final (rojo/azul) | ✅ |
| Gráfica U(t) con convergencia | ✅ |
| Mapa de calor del potencial eléctrico V(x,y) | ✅ |
| Campo eléctrico con vectores (quiver) | ✅ |
| Animación GIF de la evolución | ✅ |
| Exportar datos CSV | ✅ |
| Análisis físico automático | ✅ |

## Parámetros ajustables (sidebar)

- **N**: número de cargas (5–100)
- **Tipo de cargas**: solo +1 / solo -1 / mixtas
- **L**: tamaño del dominio
- **δ**: desplazamiento máximo por iteración
- **Iteraciones**: 500 a 50,000
- **Resolución** del campo y potencial

## Fórmulas implementadas

**Energía total:**
U = k Σ_{i<j} q_i q_j / |r_i - r_j|

**Campo eléctrico:**
E⃗(r⃗) = k Σ_i q_i (r⃗ - r⃗_i) / |r⃗ - r⃗_i|³

**Potencial eléctrico:**
V(r⃗) = k Σ_i q_i / |r⃗ - r⃗_i|
