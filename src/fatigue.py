# Fatigue simulator for butt-welded tubular joints
# ES: Simulador de fatiga para uniones tubulares soldadas a tope

# Stress cycle parameters
# ES: Parámetros del ciclo de esfuerzo

# Material properties: ASTM A500 Gr. B (design assumptions)
# ES: Propiedades del material: ASTM A500 Gr. B (supuestos de diseño)
S_UT = 400.0      # Ultimate tensile strength, MPa / ES: Resistencia última, MPa
S_Y = 290.0       # Yield strength, MPa / ES: Límite de fluencia, MPa
S_E = 105.67      # Corrected endurance limit, MPa / ES: Límite de fatiga corregido, MPa
F_FRACTION = 0.9  # Fatigue strength fraction at 10^3 cycles / ES: Fracción f a 10^3 ciclos

import math


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


# --- Quick test ---
# ES: --- Prueba rápida ---
a, b = basquin_constants(S_UT, S_E, F_FRACTION)

for force_max in [25, 45]:
    force_min = force_max / 10
    sigma_max = bending_stress(force_max, 1200, 114.3, 6.35)
    sigma_min = bending_stress(force_min, 1200, 114.3, 6.35)
    sigma_a = alternating_stress(sigma_max, sigma_min)
    sigma_m = mean_stress(sigma_max, sigma_min)
    sigma_rev = goodman_equivalent_stress(sigma_a, sigma_m, S_UT)
    life = fatigue_life(sigma_rev, S_E, a, b)

    print(f"F_max = {force_max} kN")
    print(f"  sigma_max = {sigma_max:.2f} MPa, sigma_rev = {sigma_rev:.2f} MPa")
    print(f"  Life: {life:.3e} cycles")
