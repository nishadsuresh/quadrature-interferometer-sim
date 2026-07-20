"""Dashboard: a single comprehensive figure showing raw quadrature fringes,
recovered vs. true displacement, and the vibration spectrum -- the full
story of one validation run in one image."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from validate import run_validation
from analysis import detect_vibration_freq

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


def render_dashboard(out_path: Path = RESULTS_DIR / "dashboard.png"):
    # shorter window for a readable fringe plot; I/Q/t/x_true/x_recovered all
    # come from this single run_validation call now (rather than a second,
    # separately-parameterized simulate_interferometer call) so there's no
    # risk of the two calls' parameters silently drifting apart.
    result = run_validation(duration_s=0.5, fs=20_000)
    t, I, Q = result["t"], result["I"], result["Q"]
    x_true, x_recovered = result["x_true"], result["x_recovered"]

    freq, _, freqs, spectrum = detect_vibration_freq(x_recovered, t, return_spectrum=True)

    fig, axes = plt.subplots(3, 1, figsize=(9, 10))

    ax = axes[0]
    ax.plot(t[:2000], I[:2000], label="I (0deg)", alpha=0.8)
    ax.plot(t[:2000], Q[:2000], label="Q (90deg)", alpha=0.8)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Detector intensity (a.u.)")
    ax.set_title("Raw quadrature fringe signals (first 100ms)")
    ax.legend()
    ax.grid(alpha=0.3)

    ax = axes[1]
    ax.plot(t * 1000, x_true * 1e9, label="true displacement", linewidth=2)
    ax.plot(t * 1000, x_recovered * 1e9, label="recovered displacement", linestyle="--")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Displacement (nm)")
    ax.set_title(f"Recovered vs. true displacement (rel. error: {result['rel_error']:.4%})")
    ax.legend()
    ax.grid(alpha=0.3)

    ax = axes[2]
    ax.plot(freqs, spectrum)
    ax.axvline(55.0, color="red", linestyle="--", alpha=0.6, label=f"injected 55Hz (measured {freq:.2f}Hz)")
    ax.set_xlim(0, 200)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude")
    ax.set_title("Vibration spectrum (ramp trend removed)")
    ax.legend()
    ax.grid(alpha=0.3)

    fig.tight_layout()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    print(f"Saved dashboard to {out_path}")


if __name__ == "__main__":
    render_dashboard()
