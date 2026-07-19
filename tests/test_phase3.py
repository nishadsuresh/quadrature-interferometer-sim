"""Phase 3 acceptance test: recovered vibration frequency within 1% of injected."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from validate import run_validation
from analysis import detect_vibration_freq

if __name__ == "__main__":
    INJECTED_VIB_FREQ_HZ = 55.0
    result = run_validation(vib_freq_hz=INJECTED_VIB_FREQ_HZ)

    measured_freq, magnitude = detect_vibration_freq(result["x_recovered"], result["t"])
    rel_error = abs(measured_freq - INJECTED_VIB_FREQ_HZ) / INJECTED_VIB_FREQ_HZ

    print(f"Injected vibration frequency: {INJECTED_VIB_FREQ_HZ} Hz")
    print(f"Measured vibration frequency: {measured_freq:.4f} Hz")
    print(f"Relative error: {rel_error:.4%}")

    passed = rel_error < 0.01
    print(f"\nPhase 3 acceptance: {'PASS' if passed else 'FAIL'} (need <1% frequency error)")
    sys.exit(0 if passed else 1)
