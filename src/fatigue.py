# Fatigue simulator for butt-welded tubular joints
# ES: Simulador de fatiga para uniones tubulares soldadas a tope

# Stress cycle parameters
# ES: Parámetros del ciclo de esfuerzo

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


# --- Quick test ---
# ES: --- Prueba rápida ---
sigma_a = alternating_stress(120, 12)
sigma_m = mean_stress(120, 12)
sigma_max = bending_stress(25, 1200, 114.3, 6.35)
sigma_min = bending_stress(2.5, 1200, 114.3, 6.35)
print(f"Alternating stress: {sigma_a} MPa")
print(f"Mean stress: {sigma_m} MPa")
print(f"Max bending stress: {sigma_max:.2f} MPa")
print(f"Min bending stress: {sigma_min:.2f} MPa")
