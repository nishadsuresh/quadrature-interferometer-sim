"""
Michelson interferometer physics simulation with quadrature (I/Q) homodyne
detection.

DESIGN DECISION (from empirical testing during planning, see ee-projects.md):
a naive single-photodiode approach fails with 54% displacement error and a
direction ambiguity (cos(phi) can't distinguish +phi from -phi). Quadrature
detection -- two detectors 90 degrees apart -- resolves this: atan2(Q,I)
gives an unambiguous, monotonic phase estimate.

Physics: for a Michelson interferometer with one mirror displaced by x(t),
the round-trip path length change is 2x(t), so the phase is
    phi(t) = 4*pi*x(t) / lambda
The two quadrature detector intensities are
    I(t) = I0 * (1 + V*cos(phi(t)))
    Q(t) = I0 * (1 + V*sin(phi(t)))
where V is fringe visibility/contrast (0..1) and I0 is mean intensity.
"""

from __future__ import annotations

import numpy as np

HENE_WAVELENGTH_M = 632.8e-9  # HeNe laser, meters


def simulate_interferometer(
    t: np.ndarray,
    displacement_fn,
    wavelength_m: float = HENE_WAVELENGTH_M,
    mean_intensity: float = 1.0,
    contrast: float = 0.9,
    shot_noise_std: float = 0.0,
    thermal_noise_std: float = 0.0,
    mains_amplitude: float = 0.0,
    mains_freq_hz: float = 60.0,
    drift_amplitude: float = 0.0,
    drift_freq_hz: float = 0.1,
    seed: int | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate quadrature (I, Q) detector signals for a given displacement
    waveform, with optional realistic noise sources.

    Parameters
    ----------
    t : time array (seconds)
    displacement_fn : callable, x(t) in meters -- the "true" mirror displacement
    shot_noise_std : shot-like noise (modeled as intensity-independent additive
        Gaussian here for simplicity -- true shot noise scales with sqrt(signal),
        but at the intensities/contrasts used this is a reasonable approximation
        and keeps the noise model's parameters independently tunable)
    thermal_noise_std : detector thermal (Gaussian) noise
    mains_amplitude, mains_freq_hz : 60Hz electrical pickup
    drift_amplitude, drift_freq_hz : slow low-frequency drift (thermal/mechanical)

    Returns
    -------
    (I, Q, x_true) -- the two detector signals and the ground-truth displacement
    (returned for validation; a real system would not have x_true).
    """
    rng = np.random.default_rng(seed)

    x_true = displacement_fn(t)
    phi = 4 * np.pi * x_true / wavelength_m

    I = mean_intensity * (1 + contrast * np.cos(phi))
    Q = mean_intensity * (1 + contrast * np.sin(phi))

    mains = mains_amplitude * np.sin(2 * np.pi * mains_freq_hz * t)
    drift = drift_amplitude * np.sin(2 * np.pi * drift_freq_hz * t)

    I = I + mains + drift + rng.normal(0, shot_noise_std, size=t.shape) + rng.normal(0, thermal_noise_std, size=t.shape)
    Q = Q + mains + drift + rng.normal(0, shot_noise_std, size=t.shape) + rng.normal(0, thermal_noise_std, size=t.shape)

    return I, Q, x_true
