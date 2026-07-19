"""Phase 1 acceptance test: for a known linear displacement ramp (no noise),
fringe spacing in I(t) must match lambda/2 analytically."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import numpy as np
from scipy.signal import find_peaks

from optics import simulate_interferometer, HENE_WAVELENGTH_M

if __name__ == "__main__":
    # ramp fast enough to get many fringes, slow enough to resolve them well
    velocity_m_per_s = 5e-6  # 5 um/s
    duration_s = 2.0
    fs = 100_000  # sample rate high enough to resolve fringes cleanly
    t = np.arange(0, duration_s, 1 / fs)

    displacement_fn = lambda t: velocity_m_per_s * t

    I, Q, x_true = simulate_interferometer(t, displacement_fn, contrast=0.9, seed=1)
    # no noise for this test -- checking the clean physics, not noise robustness (later phases)

    peaks, _ = find_peaks(I)
    peak_displacements = x_true[peaks]
    fringe_spacings = np.diff(peak_displacements)

    expected_spacing = HENE_WAVELENGTH_M / 2
    mean_spacing = np.mean(fringe_spacings)
    rel_error = abs(mean_spacing - expected_spacing) / expected_spacing

    print(f"Expected fringe spacing (lambda/2): {expected_spacing*1e9:.4f} nm")
    print(f"Measured mean fringe spacing:       {mean_spacing*1e9:.4f} nm  ({len(peaks)} fringes)")
    print(f"Relative error: {rel_error:.6%}")

    passed = rel_error < 0.001  # well within numerical/discretization tolerance
    print(f"\nPhase 1 acceptance: {'PASS' if passed else 'FAIL'} (need <0.1% error vs analytic lambda/2)")
    sys.exit(0 if passed else 1)
