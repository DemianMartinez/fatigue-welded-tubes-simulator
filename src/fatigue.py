# Fatigue simulator for butt-welded tubular joints
# ES: Simulador de fatiga para uniones tubulares soldadas a tope

# Stress cycle parameters
# ES: Parámetros del ciclo de esfuerzo


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


# --- Quick test ---
# ES: --- Prueba rápida ---
sigma_a = alternating_stress(120, 12)
sigma_m = mean_stress(120, 12)
print(f"Alternating stress: {sigma_a} MPa")
print(f"Mean stress: {sigma_m} MPa")