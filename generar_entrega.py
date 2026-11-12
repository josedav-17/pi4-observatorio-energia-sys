import numpy as np

# Definición de tensores básicos
x = np.array([0.8, 0.6, 0.3])
w = np.array([0.5, -0.2, 0.7])
b = 0.1

# Producto individual de cada entrada por su peso
productos = w * x
print(f"Productos individuales (w*x): {productos}")

# Suma ponderada vectorial (z = w^T * x + b)
z = np.dot(w, x) + b
print(f"Suma ponderada (z): {z:.2f}")

# Función de activación ReLU (a = max(0, z))
a = np.maximum(0, z)
print(f"Activación (a): {a:.2f}")