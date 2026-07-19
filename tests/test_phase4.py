"""Phase 4 acceptance test: sweep detector noise level, verify relative
error stays under 1% across the tested range, save table + plot."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from validate import run_validation

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"

if __name__ == "__main__":
    noise_levels = np.arange(0.0, 0.065, 0.005)  # 0% to 6% detector noise
    rel_errors = []

    print(f"{'noise_std':>10} {'rel_error':>12}")
    for noise in noise_levels:
        result = run_validation(shot_noise_std=noise, thermal_noise_std=noise, seed=1)
        rel_errors.append(result["rel_error"])
        print(f"{noise:>10.3f} {result['rel_error']:>11.4%}")

    rel_errors = np.array(rel_errors)
    RESULTS_DIR.mkdir(exist_ok=True)

    with open(RESULTS_DIR / "noise_sweep_table.csv", "w") as f:
        f.write("noise_std,rel_error_pct\n")
        for noise, err in zip(noise_levels, rel_errors):
            f.write(f"{noise:.4f},{err*100:.6f}\n")

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(noise_levels * 100, rel_errors * 100, marker="o")
    ax.axhline(1.0, color="red", linestyle="--", label="1% acceptance threshold")
    ax.set_xlabel("Detector noise level (% of mean intensity)")
    ax.set_ylabel("Relative displacement recovery error (%)")
    ax.set_title("Quadrature detection: recovery error vs. detector noise")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "noise_sweep_plot.png", dpi=120)
    plt.close(fig)

    max_error = rel_errors.max()
    passed = max_error < 0.01
    print(f"\nMax relative error across sweep: {max_error:.4%}")
    print(f"Phase 4 acceptance: {'PASS' if passed else 'FAIL'} (need <1% across the whole range)")
    sys.exit(0 if passed else 1)
