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


def plot_goodman_diagram(sigma_m, sigma_a, sf, force_kn, title, filename, x_limits=None, y_limits=None):
    """Draw and save a Goodman diagram.
    ES: Dibuja y guarda un diagrama de Goodman.
    """
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
    plt.plot(sigma_m, sigma_a, "ro", label=f"Operating point ({force_kn} kN)\nSF = {sf:.3f}")

    # Formatting and labels
    # ES: Formato y etiquetas
    plt.xlabel(r"Mean stress, $\sigma_m$ (MPa)")
    plt.ylabel(r"Alternating stress, $\sigma_a$ (MPa)")
    plt.title(title)

    # Handle axis limits
    # ES: Manejo de límites de los ejes
    if x_limits is not None:
        plt.xlim(x_limits[0], x_limits[1])
    else:
        plt.xlim(left=0)

    if y_limits is not None:
        plt.ylim(y_limits[0], y_limits[1])
    else:
        plt.ylim(bottom=0)

    plt.grid(True, linestyle=":")
    plt.legend(loc="upper right")
    plt.tight_layout()

    # Save and close figure to prevent memory accumulation
    # ES: Guardar y cerrar figura para prevenir acumulación en memoria
    plt.savefig(filename, dpi=150)
    print(f"Diagram saved successfully to {filename}")
    plt.close()


if __name__ == "__main__":
    # Test bench parameters (nominal case)
    # ES: Parámetros del banco de pruebas (caso nominal)
    span = 1200.0
    outer_diameter = 114.3
    wall_thickness = 6.35
    force_max = 25.0
    force_min = force_max / 10.0

    # Calculate stresses once
    # ES: Calcular esfuerzos una sola vez
    sigma_max = bending_stress(force_max, span, outer_diameter, wall_thickness)
    sigma_min = bending_stress(force_min, span, outer_diameter, wall_thickness)

    sigma_a = alternating_stress(sigma_max, sigma_min) * K_F
    sigma_m = mean_stress(sigma_max, sigma_min) * K_F
    sf_bench = goodman_safety_factor(sigma_a, sigma_m, S_E, S_UT)

    # 1. General diagram
    # ES: 1. Diagrama general
    plot_goodman_diagram(
        sigma_m, sigma_a, sf_bench, force_max,
        "Goodman Diagram - ASTM A500 Gr. B",
        "data/goodman_diagram.png"
    )

    # 2. Detailed diagram near operating point
    # ES: 2. Diagrama de detalle cerca del punto de operación
    plot_goodman_diagram(
        sigma_m, sigma_a, sf_bench, force_max,
        "Goodman Diagram - Detail near the operating point",
        "data/goodman_detail.png",
        x_limits=(85, 95), y_limits=(72, 75)
    )
