import matplotlib.pyplot as plt

from fatigue import (basquin_constants, bending_stress, alternating_stress,
                     mean_stress, goodman_equivalent_stress, fatigue_life,
                     S_UT, S_E, F_FRACTION)

# Build the S-N curve between 10^3 and 10^6 cycles
# ES: Construir la curva S-N entre 10^3 y 10^6 ciclos
a, b = basquin_constants(S_UT, S_E, F_FRACTION)

cycles = []
stress = []
exponent = 3.0
while exponent <= 6.0:
    n = 10**exponent
    cycles.append(n)
    stress.append(a * n**b)
    exponent = exponent + 0.05


# Operating point for the test bench
# ES: Punto de operación del banco de pruebas
force_max = 45
sigma_max = bending_stress(force_max, 1200, 114.3, 6.35)
sigma_min = bending_stress(force_max / 10, 1200, 114.3, 6.35)
sigma_a = alternating_stress(sigma_max, sigma_min)
sigma_m = mean_stress(sigma_max, sigma_min)
sigma_rev = goodman_equivalent_stress(sigma_a, sigma_m, S_UT)
life = fatigue_life(sigma_rev, S_E, a, b)

# Plot
# ES: Graficar
plt.figure(figsize=(8, 5))
plt.plot(cycles, stress, label="S-N curve (base material)")
plt.axhline(S_E, linestyle="--", label=f"Endurance limit Se = {S_E} MPa")
plt.xscale("log")
plt.yscale("log")
plt.xlabel("Cycles to failure, N")
plt.ylabel("Equivalent alternating stress, MPa")
plt.title("S-N curve - ASTM A500 Gr. B")
plt.grid(True, which="both", linestyle=":")
plt.plot(life, sigma_rev, "ro", label=f"Operating point ({force_max} kN)")
plt.legend()
plt.tight_layout()
plt.savefig("data/sn_curve.png", dpi=150)
plt.show()