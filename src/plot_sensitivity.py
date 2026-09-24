import math
import matplotlib.pyplot as plt
from fatigue import (
    life_for_force,
    bending_stress,
    alternating_stress,
    mean_stress,
    goodman_equivalent_stress,
    S_E,
    S_UT,
    K_F
)


def find_critical_boundary(param_type, base_force, base_span, od, base_t, low, high):
    """Numerically find the parameter value where sigma_rev equals S_E.
    The caller must supply a bracket [low, high] where sigma_rev is monotonic
    and Goodman stays valid (sigma_m < S_UT).
    ES: Encuentra numéricamente el valor del parámetro donde sigma_rev iguala a S_E.
    Quien llama debe dar un intervalo [low, high] donde sigma_rev sea monótona
    y Goodman siga siendo válido (sigma_m < S_UT).
    """

    # --- Precondition Check / Verificación de precondición ---
    def exceeds_goodman_domain(test_val):
        f = test_val if param_type == 'load' else base_force
        s = test_val if param_type == 'span' else base_span
        t = test_val if param_type == 'thickness' else base_t
        s_max = bending_stress(f, s, od, t)
        s_min = bending_stress(f / 10.0, s, od, t)
        return mean_stress(s_max, s_min) * K_F >= S_UT

    if exceeds_goodman_domain(low) or exceeds_goodman_domain(high):
        raise ValueError(
            f"Bracket [{low}, {high}] for '{param_type}' exceeds the Goodman "
            f"domain (sigma_m >= S_UT)."
        )

    for _ in range(100):
        mid = (low + high) / 2.0

        # Override the target parameter for this iteration
        # ES: Sobrescribir el parámetro objetivo para esta iteración
        f = mid if param_type == 'load' else base_force
        s = mid if param_type == 'span' else base_span
        t = mid if param_type == 'thickness' else base_t

        s_max = bending_stress(f, s, od, t)
        s_min = bending_stress(f / 10.0, s, od, t)
        s_a = alternating_stress(s_max, s_min) * K_F
        s_m = mean_stress(s_max, s_min) * K_F
        s_rev = goodman_equivalent_stress(s_a, s_m, S_UT)

        if abs(s_rev - S_E) < 1e-4:
            return mid

        # Bisection logic: load and span increase stress; thickness decreases it
        # ES: Lógica de bisección: carga y claro aumentan el esfuerzo; el espesor lo disminuye
        if param_type in ['load', 'span']:
            if s_rev > S_E:
                high = mid
            else:
                low = mid
        else:
            if s_rev > S_E:
                low = mid
            else:
                high = mid

    return (low + high) / 2.0


def plot_sensitivity_curve(x_data, y_data, xlabel, title, filename, critical_val=None, unit="", x_limits=None):
    """Draw and save a sensitivity plot with a logarithmic life scale.
    ES: Dibuja y guarda una gráfica de sensibilidad con escala logarítmica para la vida.
    """
    plt.figure(figsize=(8, 6))

    plt.plot(x_data, y_data, "bo-", label="Fatigue life")

    if critical_val is not None:
        plt.axvline(
            x=critical_val, color="r", linestyle="--",
            label=f"Endurance threshold: {critical_val:.2f} {unit}"
        )

    plt.xlabel(xlabel)
    plt.ylabel("Life (cycles to failure)")
    plt.title(title)

    plt.yscale("log")

    if x_limits is not None:
        plt.xlim(x_limits[0], x_limits[1])

    plt.grid(True, which="both", linestyle=":")
    plt.legend()
    plt.tight_layout()

    plt.savefig(filename, dpi=150)
    print(f"Sensitivity plot saved successfully to {filename}")
    plt.close()


if __name__ == "__main__":
    test_od = 114.3
    span_mm = 1200.0
    thickness_mm = 6.35
    force_kn = 25.0

    # Calculate reproducible critical values dynamically with physical brackets
    # ES: Calcular valores críticos reproducibles de forma dinámica con intervalos físicos
    crit_load = find_critical_boundary(
        'load', force_kn, span_mm, test_od, thickness_mm, low=0.1, high=54.0
    )
    crit_thick = find_critical_boundary(
        'thickness', force_kn, span_mm, test_od, thickness_mm, low=2.0, high=50.0
    )
    crit_span = find_critical_boundary(
        'span', force_kn, span_mm, test_od, thickness_mm, low=100.0, high=5000.0
    )

    print("\n--- Critical Boundaries ---")
    print(f"Critical load: {crit_load:.2f} kN")
    print(f"Critical thickness: {crit_thick:.4f} mm")
    print(f"Critical span: {crit_span:.2f} mm\n")

    # ---------------------------------------------------------
    # 1. Load Sensitivity Sweep
    # ---------------------------------------------------------
    loads = [20, 22, 24, 25, 26, 28, 30, 35, 40, 45, 50]
    x_load, y_load = [], []

    for current_load in loads:
        life = life_for_force(current_load, span_mm, test_od, thickness_mm)
        if life != 0.0 and life != math.inf:
            x_load.append(current_load)
            y_load.append(life)

    plot_sensitivity_curve(
        x_load, y_load,
        "Maximum Force, F (kN)",
        "Sensitivity Analysis - Load Variation",
        "data/sensitivity_load.png",
        critical_val=crit_load,
        unit="kN",
        x_limits=(18, 52)
    )

    # ---------------------------------------------------------
    # 2. Thickness Sensitivity Sweep
    # ---------------------------------------------------------
    thicknesses = [4, 5, 6, 6.35, 7]
    x_thick, y_thick = [], []

    for current_t in thicknesses:
        life = life_for_force(force_kn, span_mm, test_od, current_t)
        if life != 0.0 and life != math.inf:
            x_thick.append(current_t)
            y_thick.append(life)

    plot_sensitivity_curve(
        x_thick, y_thick,
        "Wall Thickness, t (mm)",
        "Sensitivity Analysis - Thickness Variation",
        "data/sensitivity_thickness.png",
        critical_val=crit_thick,
        unit="mm",
        x_limits=(3.8, 7.2)
    )

    # ---------------------------------------------------------
    # 3. Span Sensitivity Sweep
    # ---------------------------------------------------------
    spans = [1100, 1200, 1300, 1400, 1600]
    x_span, y_span = [], []

    for current_span in spans:
        life = life_for_force(force_kn, current_span, test_od, thickness_mm)
        if life != 0.0 and life != math.inf:
            x_span.append(current_span)
            y_span.append(life)

    plot_sensitivity_curve(
        x_span, y_span,
        "Span Length, L (mm)",
        "Sensitivity Analysis - Span Variation",
        "data/sensitivity_span.png",
        critical_val=crit_span,
        unit="mm",
        x_limits=(1050, 1650)
    )
