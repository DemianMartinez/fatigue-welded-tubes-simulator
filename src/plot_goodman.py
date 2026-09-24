import matplotlib.pyplot as plt
from fatigue import (
    bending_stress,
    alternating_stress,
    mean_stress,
    goodman_safety_factor,
    S_UT,
    S_Y,
    S_E,
    K_F
)

# 1. Define test bench parameters (nominal case)
# ES: 1. Definir parámetros del banco de pruebas (caso nominal)
span = 1200.0
outer_diameter = 114.3
wall_thickness = 6.35
force_max = 25.0
force_min = force_max / 10.0

# 2. Calculate stresses
# ES: 2. Calcular esfuerzos
sigma_max = bending_stress(force_max, span, outer_diameter, wall_thickness)
sigma_min = bending_stress(force_min, span, outer_diameter, wall_thickness)

# Apply fatigue stress-concentration factor (K_F)
# ES: Aplicar factor de concentración de esfuerzo por fatiga (K_F)
sigma_a = alternating_stress(sigma_max, sigma_min) * K_F
sigma_m = mean_stress(sigma_max, sigma_min) * K_F

sf_bench = goodman_safety_factor(sigma_a, sigma_m, S_E, S_UT)

# 3. Create the plot
# ES: 3. Crear la gráfica
plt.figure(figsize=(8, 6))

# Goodman line: from (0, S_E) to (S_UT, 0)
# ES: Recta de Goodman: de (0, S_E) a (S_UT, 0)
plt.plot([0, S_UT], [S_E, 0], "b-", label="Goodman line")

# Langer (yield) line: from (0, S_Y) to (S_Y, 0)
# ES: Recta de Langer (fluencia): de (0, S_Y) a (S_Y, 0)
plt.plot([0, S_Y], [S_Y, 0], "g--", label="Langer line (Yield)")

# Load line for R = 0.1: from (0, 0) to operating point
# ES: Línea de carga para R = 0.1: de (0, 0) al punto de operación
plt.plot([0, sigma_m], [0, sigma_a], "k-.", label="Load line (R = 0.1)")

# Operating point
# ES: Punto de operación
plt.plot(sigma_m, sigma_a, "ro", label=f"Operating point ({force_max} kN)\nSF = {sf_bench:.3f}")

# 4. Formatting and labels
# ES: 4. Formato y etiquetas
plt.xlabel(r"Mean stress, $\sigma_m$ (MPa)")
plt.ylabel(r"Alternating stress, $\sigma_a$ (MPa)")
plt.title("Goodman Diagram - ASTM A500 Gr. B")

# Force axes to start at zero for proper geometrical visualization
# ES: Forzar los ejes a iniciar en cero para una correcta visualización geométrica
plt.xlim(left=0)
plt.ylim(bottom=0)

plt.grid(True, linestyle=":")
plt.legend()
plt.tight_layout()

# 5. Save and show
# ES: 5. Guardar y mostrar
plt.savefig("data/goodman_diagram.png", dpi=150)
print("Goodman diagram saved successfully to data/goodman_diagram.png")
plt.show()
