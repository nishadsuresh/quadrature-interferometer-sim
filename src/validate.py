"""Injects a known displacement waveform (ramp + vibration), runs it through
the full simulate -> recover pipeline, and measures recovery error."""

from __future__ import annotations

import numpy as np

from optics import simulate_interferometer
from analysis import recover_displacement


def make_test_displacement(ramp_velocity_m_s: float, vib_amplitude_m: float, vib_freq_hz: float):
    def displacement_fn(t):
        return ramp_velocity_m_s * t + vib_amplitude_m * np.sin(2 * np.pi * vib_freq_hz * t)
    return displacement_fn


def run_validation(
    ramp_velocity_m_s: float = 2e-6,
    vib_amplitude_m: float = 40e-9,
    vib_freq_hz: float = 55.0,
    duration_s: float = 2.0,
    fs: float = 20_000,
    shot_noise_std: float = 0.01,
    thermal_noise_std: float = 0.01,
    mains_amplitude: float = 0.02,
    drift_amplitude: float = 0.01,
    seed: int = 1,
) -> dict:
    t = np.arange(0, duration_s, 1 / fs)
    displacement_fn = make_test_displacement(ramp_velocity_m_s, vib_amplitude_m, vib_freq_hz)

    I, Q, x_true = simulate_interferometer(
        t, displacement_fn,
        shot_noise_std=shot_noise_std, thermal_noise_std=thermal_noise_std,
        mains_amplitude=mains_amplitude, drift_amplitude=drift_amplitude,
        seed=seed,
    )

    x_recovered = recover_displacement(I, Q, t)

    # recovered phase has an arbitrary additive constant (unwrap doesn't know
    # absolute phase) -- align by removing each series' mean before comparing
    x_true_centered = x_true - np.mean(x_true)
    x_recovered_centered = x_recovered - np.mean(x_recovered)

    error = x_recovered_centered - x_true_centered
    rms_error = np.sqrt(np.mean(error ** 2))
    peak_to_peak = np.ptp(x_true_centered)
    rel_error = rms_error / peak_to_peak

    return {
        "t": t, "x_true": x_true_centered, "x_recovered": x_recovered_centered,
        "rms_error_m": rms_error, "peak_to_peak_m": peak_to_peak, "rel_error": rel_error,
    }


if __name__ == "__main__":
    import sys
    result = run_validation()
    print(f"Peak-to-peak displacement: {result['peak_to_peak_m']*1e9:.2f} nm")
    print(f"RMS recovery error:        {result['rms_error_m']*1e9:.4f} nm")
    print(f"Relative error:            {result['rel_error']:.4%}")
    passed = result["rel_error"] < 0.01
    print(f"\nPhase 2 acceptance: {'PASS' if passed else 'FAIL'} (need <1% RMS error)")
    sys.exit(0 if passed else 1)
