import math
import matplotlib.pyplot as plt
from fatigue import damage_history


def plot_cumulative_damage(spectrum, span, outer_diameter, wall_thickness, filename):
    """Draw and save the Palmgren-Miner cumulative damage history.
    ES: Dibuja y guarda el historial de daño acumulado de Palmgren-Miner.
    """
    cycles, damage = damage_history(spectrum, span, outer_diameter, wall_thickness)

    # Check for static failure (Option 3 implementation)
    # ES: Verificar falla estática (implementación de Opción 3)
    static_failure = False
    if damage[-1] == math.inf:
        static_failure = True
        # Remove the infinite point for clean plotting
        # ES: Remover el punto infinito para una graficación limpia
        cycles.pop()
        damage.pop()

    plt.figure(figsize=(8, 6))

    # Plot the damage trajectory (markers and line)
    # ES: Graficar la trayectoria del daño (marcadores y línea)
    plt.plot(cycles, damage, "bo-", label="Damage trajectory")

    # Plot the D = 1 threshold
    # ES: Graficar el umbral D = 1
    plt.axhline(1.0, color="r", linestyle="--", label="Failure Threshold (D = 1)")

    # If static yield occurred, mark the exact cycle where it broke
    # ES: Si ocurrió fluencia estática, marcar el ciclo exacto donde se rompió
    if static_failure:
        plt.axvline(x=cycles[-1], color="k", linestyle=":", label="Static Yield Collapse")
        title_text = "Cumulative Damage History\n(WARNING: Aborted due to static yield)"
    else:
        title_text = "Cumulative Damage History - Palmgren-Miner"

    # Formatting and labels
    # ES: Formato y etiquetas
    plt.xlabel("Accumulated cycles, N")
    plt.ylabel("Cumulative damage, D")
    plt.title(title_text)

    plt.xlim(left=0)
    plt.ylim(bottom=0)
    plt.grid(True, linestyle=":")
    plt.legend(loc="upper left")
    plt.tight_layout()

    plt.savefig(filename, dpi=150)
    print(f"Plot saved successfully to {filename}")
    plt.close()


if __name__ == "__main__":
    # Test bench parameters (nominal case)
    # ES: Parámetros del banco de pruebas (caso nominal)
    test_span = 1200.0
    test_od = 114.3
    test_t = 6.35

    # Spectrum defined here, not in fatigue.py
    # ES: Espectro definido aquí, no en fatigue.py
    nominal_spectrum = [(20, 500000), (25, 300000), (35, 50000)]

    plot_cumulative_damage(
        nominal_spectrum,
        test_span,
        test_od,
        test_t,
        "data/damage_accumulation.png"
    )
