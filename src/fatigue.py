import math


# Fatigue simulator for butt-welded tubular joints
# ES: Simulador de fatiga para uniones tubulares soldadas a tope

# Material properties: ASTM A500 Gr. B (design assumptions)
# ES: Propiedades del material: ASTM A500 Gr. B (supuestos de diseño)
S_UT = 400.0      # Ultimate tensile strength, MPa / ES: Resistencia última, MPa
S_Y = 290.0       # Yield strength, MPa / ES: Límite de fluencia, MPa
S_E = 94.75       # Corrected endurance limit, MPa / ES: Límite de fatiga corregido, MPa
K_F = 1.2           # Fatigue stress-concentration factor (reinforced butt weld) / ES: Factor de concentración de esfuerzo por fatiga (soldadura a tope reforzada)
F_FRACTION = 0.9  # Fatigue strength fraction at 10^3 cycles / ES: Fracción f a 10^3 ciclos


def alternating_stress(sigma_max, sigma_min):
    """Return the alternating stress amplitude in MPa.
    ES: Devuelve la amplitud del esfuerzo alternante en MPa.
    """
    return (sigma_max - sigma_min) / 2


def mean_stress(sigma_max, sigma_min):
    """Return the mean stress in MPa.
    ES: Devuelve el esfuerzo medio en MPa.
    """
    return (sigma_max + sigma_min) / 2


def moment_of_inertia(outer_diameter, wall_thickness):
    """Return the second moment of area of a hollow circular section in mm^4.
    ES: Devuelve el momento de inercia de una sección circular hueca en mm^4.
    """
    inner_diameter = outer_diameter - 2 * wall_thickness
    return math.pi * (outer_diameter**4 - inner_diameter**4) / 64


def max_bending_moment(force_kn, span):
    """Return the maximum bending moment in N*mm for a simply supported
    beam with a central point load.
    ES: Devuelve el momento flexionante máximo en N*mm para una viga
    simplemente apoyada con carga puntual al centro.
    """
    force_n = force_kn * 1000  # kN to N / ES: de kN a N
    return force_n * span / 4


def bending_stress(force_kn, span, outer_diameter, wall_thickness):
    """Return the bending stress at the outer fiber in MPa.
    ES: Devuelve el esfuerzo por flexión en la fibra externa en MPa.
    """
    moment = max_bending_moment(force_kn, span)
    inertia = moment_of_inertia(outer_diameter, wall_thickness)
    c = outer_diameter / 2
    return moment * c / inertia


def goodman_equivalent_stress(sigma_a, sigma_m, s_ut):
    """Return the Goodman equivalent stress in MPa.
    ES: Devuelve el esfuerzo equivalente de Goodman en MPa.
    """
    if sigma_m <= 0:
        return sigma_a
    else:
        return sigma_a / (1 - (sigma_m / s_ut))


def basquin_constants(s_ut, s_e, f):
    """Return Basquin constants a (MPa) and b for the S-N curve.
    ES: Devuelve las constantes de Basquin a (MPa) y b de la curva S-N.
    """
    a = (f * s_ut)**2 / s_e
    b = -math.log10(f * s_ut / s_e) / 3
    return a, b


def fatigue_life(sigma_rev, s_e, a, b):
    """Return cycles to failure. Returns infinity if below the endurance limit.
    ES: Devuelve los ciclos hasta la falla. Devuelve infinito si está por
    debajo del límite de fatiga.
    """
    if sigma_rev <= s_e:
        return math.inf
    return (sigma_rev / a)**(1 / b)


def life_for_force(force_max_kn, span, outer_diameter, wall_thickness):
    """Return cycles to failure for a load cycle with R = 0.1.
    Returns 0.0 if the static yield limit is exceeded.
    ES: Devuelve los ciclos hasta la falla para un ciclo de carga con R = 0.1.
    Devuelve 0.0 si se rebasa el límite de fluencia estática.
    """
    force_min_kn = force_max_kn / 10
    sigma_max = bending_stress(force_max_kn, span, outer_diameter, wall_thickness)

    # Static yield check: immediate failure (0 cycles)
    # ES: Verificación de fluencia estática: falla instantánea (0 ciclos)
    if sigma_max >= S_Y:
        return 0.0

    sigma_min = bending_stress(force_min_kn, span, outer_diameter, wall_thickness)

    # Apply K_F to operating stresses, not to S_E
    # ES: K_F aplicado a los esfuerzos operativos, no a S_E
    sigma_a = alternating_stress(sigma_max, sigma_min) * K_F
    sigma_m = mean_stress(sigma_max, sigma_min) * K_F

    sigma_rev = goodman_equivalent_stress(sigma_a, sigma_m, S_UT)

    # Encapsulation: Constants are calculated locally
    # ES: Encapsulamiento: Las constantes se calculan localmente
    a, b = basquin_constants(S_UT, S_E, F_FRACTION)

    return fatigue_life(sigma_rev, S_E, a, b)


def miner_damage(spectrum, span, outer_diameter, wall_thickness):
    """Return the cumulative damage D for a load spectrum.
    ES: Devuelve el daño acumulado D para un espectro de cargas.
    """
    total_damage = 0.0
    for force_max_kn, cycles in spectrum:
        life = life_for_force(force_max_kn, span, outer_diameter, wall_thickness)

        # Intentional early exit: static yield breaks the structure completely
        # ES: Salida temprana intencional: la fluencia estática rompe la estructura por completo
        if life == 0.0:
            return math.inf

        total_damage += cycles / life

    return total_damage


def damage_history(spectrum, span, outer_diameter, wall_thickness):
    """Return cumulative cycles and cumulative damage after each block.
    Damage is set to infinity for the block that causes static yield.
    ES: Devuelve los ciclos acumulados y el daño acumulado tras cada bloque.
    El daño se fija en infinito para el bloque que provoca fluencia estática.
    """
    cumulative_cycles = [0.0]
    cumulative_damage = [0.0]

    current_cycles = 0.0
    current_damage = 0.0

    for force_max_kn, cycles in spectrum:
        life = life_for_force(force_max_kn, span, outer_diameter, wall_thickness)

        # Immediate static failure: append infinity and abort the remaining spectrum
        # ES: Falla estática inmediata: añadir infinito y abortar el espectro restante
        if life == 0.0:
            cumulative_cycles.append(current_cycles)
            cumulative_damage.append(math.inf)
            break

        current_cycles += cycles
        current_damage += cycles / life

        cumulative_cycles.append(current_cycles)
        cumulative_damage.append(current_damage)

    return cumulative_cycles, cumulative_damage


def blocks_until_failure(force_max_kn, block_cycles, span, outer_diameter, wall_thickness):
    """Return the number of complete blocks that can be run before failure (D >= 1).
    Returns an int, or a float (math.inf) if the load is below the endurance limit.
    ES: Devuelve el número de bloques completos que se pueden correr antes de la falla (D >= 1).
    Devuelve un int, o un float (math.inf) si la carga está bajo el límite de fatiga.
    """
    life = life_for_force(force_max_kn, span, outer_diameter, wall_thickness)

    if life == 0.0:
        return 0
    if life == math.inf:
        return math.inf

    return math.ceil(life / block_cycles) - 1


def goodman_safety_factor(sigma_a, sigma_m, s_e, s_ut):
    """Return the Goodman fatigue safety factor.
    Returns math.inf if alternating stress is zero and mean stress is compressive or zero.
    ES: Devuelve el factor de seguridad a fatiga de Goodman.
    Devuelve math.inf si el esfuerzo alternante es cero y el esfuerzo medio es de compresión o cero.
    """
    if sigma_m <= 0.0:
        # Goodman does not credit compressive benefit; evaluate only against S_e
        # ES: Goodman no acredita beneficio por compresión; evaluamos solo contra S_e
        if sigma_a == 0.0:
            return math.inf
        return s_e / sigma_a

    # Normal case: tensile mean stress
    # ES: Caso normal: esfuerzo medio a tracción
    return 1.0 / ((sigma_a / s_e) + (sigma_m / s_ut))


if __name__ == "__main__":

    # --- Test: single load levels ---
    # ES: --- Prueba: niveles de carga individuales ---
    for force_max in [25, 45, 55]:
        life = life_for_force(force_max, 1200, 114.3, 6.35)
        if life == 0.0:
            print(f"F_max = {force_max} kN: static yield failure")
        else:
            print(f"F_max = {force_max} kN -> life: {life:.3e} cycles")

    # --- Test: Miner cumulative damage ---
    # ES: --- Prueba: daño acumulado de Miner ---
    spectrum = [(20, 500000), (25, 300000), (35, 50000)]
    damage_result = miner_damage(spectrum, 1200, 114.3, 6.35)
    print(f"\nTotal cumulative damage: D = {damage_result:.3f}")

    if damage_result >= 1.0:
        print("Structural failure: D >= 1. The part collapses.")
    else:
        print("Safe operation: D < 1. The part survives the spectrum.")

    # --- Test: damage history ---
    # ES: --- Prueba: historial de daño acumulado ---
    history_cycles, history_damage = damage_history(spectrum, 1200, 114.3, 6.35)
    print("\nDamage history:")
    for damage_value in history_damage:
        print(f"  D = {damage_value:.4f}")

    # --- Test: blocks until failure ---
    # ES: --- Prueba: bloques hasta la falla ---
    blocks_35kn = blocks_until_failure(35, 20000, 1200, 114.3, 6.35)
    print(f"Blocks until failure (35 kN, 20k cycles/block): {blocks_35kn}")

    # --- Test: Goodman safety factor at the nominal 25 kN load ---
    # ES: --- Prueba: factor de seguridad de Goodman a la carga nominal de 25 kN ---
    sigma_max_25 = bending_stress(25, 1200, 114.3, 6.35)
    sigma_min_25 = bending_stress(2.5, 1200, 114.3, 6.35)
    sigma_a_25 = alternating_stress(sigma_max_25, sigma_min_25) * K_F
    sigma_m_25 = mean_stress(sigma_max_25, sigma_min_25) * K_F
    sf_bench = goodman_safety_factor(sigma_a_25, sigma_m_25, S_E, S_UT)
    print(f"Safety factor (25 kN): {sf_bench:.3f}")

    # --- Test: reference case, safety factor above 1 ---
    # ES:  --- Prueba: Caso de referencia, factor de seguridad superior a 1 ---
    sf_example = goodman_safety_factor(40.0, 120.0, 100.0, 400.0)
    print(f"Safety factor (Example): {sf_example:.3f}")

    # --- Test: Pure static tensile load ---
    # ES:  --- Prueba: Carga de tracción puramente estática ---
    sf_static = goodman_safety_factor(0.0, 380.0, 94.75, 400.0)
    print(f"Safety factor (Static 380 MPa): {sf_static:.3f}")

