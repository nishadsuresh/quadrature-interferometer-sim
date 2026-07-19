"""Regression test for a bug caught in code review: the original DC estimator
(whole-record mean) only worked because every other test includes a large
ramp sweeping through many fringes. Pure steady-state vibration sensing (no
ramp) is one of this project's two stated goals -- verify it actually works
now that DC estimation uses a low-pass filter instead of a whole-record mean."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import numpy as np

from optics import simulate_interferometer
from analysis import recover_displacement

if __name__ == "__main__":
    # pure vibration, NO ramp -- this is exactly the case that previously
    # gave 58%+ error (and 16000%+ at smaller amplitudes)
    vib_amplitude_m = 40e-9
    vib_freq_hz = 55.0
    duration_s = 2.0
    fs = 20_000
    t = np.arange(0, duration_s, 1 / fs)

    displacement_fn = lambda t: vib_amplitude_m * np.sin(2 * np.pi * vib_freq_hz * t)

    I, Q, x_true = simulate_interferometer(t, displacement_fn, seed=1)  # no noise -- isolate DC-estimation correctness
    x_recovered = recover_displacement(I, Q, t)

    x_true_c = x_true - np.mean(x_true)
    x_recovered_c = x_recovered - np.mean(x_recovered)
    rel_error = np.sqrt(np.mean((x_recovered_c - x_true_c) ** 2)) / np.ptp(x_true_c)

    print(f"Pure vibration, no ramp: true amplitude={vib_amplitude_m*1e9}nm, "
          f"recovered p2p={np.ptp(x_recovered_c)*1e9:.2f}nm (true p2p={np.ptp(x_true_c)*1e9:.2f}nm)")
    print(f"Relative error: {rel_error:.4%}")

    passed = rel_error < 0.01
    print(f"\n{'PASS' if passed else 'FAIL'}: no-ramp vibration recovery {'now works' if passed else 'still broken'} (need <1% error)")
    sys.exit(0 if passed else 1)
