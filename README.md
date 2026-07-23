# quadrature-interferometer-sim

Simulates a Michelson interferometer with realistic detector noise, then recovers nanometer-scale mirror displacement and vibration from the fringe signals — the exact analysis pipeline a real optics bench needs.

**Status: all 5 phases complete.**

## Why this exists, and the key design decision

This is the one project in my portfolio tied to real ongoing optics research, not an anonymous simulator. While planning it, I tested a naive single-photodiode approach and it **failed**: 54% displacement error, plus a fundamental direction ambiguity (`cos(phi)` can't distinguish `+phi` from `-phi`). Switching to **quadrature (I/Q) homodyne detection** — two detectors 90° apart — resolves this: `atan2(Q, I)` gives an unambiguous, monotonic phase estimate. That upgrade is the real instrumentation-engineering content here, not a detail.

## Physics

For a Michelson interferometer with one mirror displaced by `x(t)`, the round-trip path length changes by `2x(t)`, giving phase `phi(t) = 4*pi*x(t)/lambda`. The two quadrature detectors measure:
```
I(t) = I0 * (1 + V*cos(phi(t)))
Q(t) = I0 * (1 + V*sin(phi(t)))
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python tests/test_phase1.py   # fringe spacing check
python src/validate.py        # displacement recovery
python tests/test_phase3.py   # vibration detection
python tests/test_phase4.py   # noise sweep
python src/dashboard.py       # full visualization
```

## Phases

| # | Phase | Acceptance test | Result |
|---|---|---|---|
| 1 | Physics sim: quadrature I/Q with tunable noise | Fringe spacing matches λ/2 analytically | ✅ 0.000000% error (31 fringes) |
| 2 | Analysis: bias/mains removal, atan2 unwrap, displacement recovery | <1% RMS error on injected displacement | ✅ **0.0395%** error |
| 3 | Vibration detection via FFT | Vibration frequency within 1% | ✅ **0.0019%** error |
| 4 | Noise sweep | <1% error across tested noise range | ✅ max **0.1234%** across 0-6% noise |
| 5 | Validation report + dashboard | A written report a reader can check | ✅ [`report/validation_report.md`](report/validation_report.md) |

## Results

### Full dashboard (fringes, displacement recovery, vibration spectrum)
![dashboard](results/dashboard.png)

### Noise robustness
![noise sweep](results/noise_sweep_plot.png)

Full validation writeup with all equations and numbers: [`report/validation_report.md`](report/validation_report.md).

## A bug I caught while reviewing the code

My original DC-bias estimator (whole-record mean) only worked because every test above includes a large ramp. Pure steady-state vibration sensing with no ramp — one of this project's two stated goals — gave 58%+ recovery error, silently. I fixed it by geometrically fitting a circle to the (I,Q) trajectory instead (see `report/validation_report.md` for the full story, including a first fix attempt that didn't actually work). Every result above is from the corrected code.

A later quality pass caught a couple of smaller loose ends from that fix: `analysis.py`'s module docstring still described the old low-pass-filter approach instead of the circle fit that actually replaced it, and `dashboard.py` re-simulated the interferometer a second time with its own hand-copied parameters instead of reusing `validate.py`'s single source of truth — a real risk of the two silently drifting apart. Both fixed; `dashboard.py` now pulls I/Q straight from one `run_validation()` call.

## Honest limitations

- **Simulation only** — every number above is on simulated detector data, not a real optical bench. Framed throughout as "I validated the analysis pipeline," not "I built an interferometer."
- **No comparison to real bench data yet** — the natural next step (with my optics research mentor) to strengthen the research tie beyond simulation. Noted as future work in the validation report.
- **Noise model is a simplified approximation** — shot noise is modeled as intensity-independent Gaussian for tunability, rather than true signal-dependent Poisson shot noise. Reasonable at the noise levels tested, but a real bench's noise floor may behave somewhat differently.

## One-line summary

I built and validated the full quadrature-detection analysis pipeline a real Michelson interferometer needs — recovering nanometer displacement to 0.044% error and vibration frequency to 0.002% error, robust to detector noise up to 6%, tied to my optics research.


## References

Sources used to design, validate, and cross-check this project's methodology:

[1] C. Lehmann et al., "Nonlinearity correction for homodyne quadrature interferometers," arXiv:2511.04386, Nov. 2025 (Max Planck Institute for Gravitational Physics). https://arxiv.org/abs/2511.04386 -- direction-dependent ellipse-fit correction technique motivating this project's Phase 2 upgrade path.

[2] G. Cooper et al., "A compact, large-range interferometer for precision measurement and inertial sensing," Class. Quantum Grav. 35, 095007 (2018). arXiv:1710.05943. https://arxiv.org/abs/1710.05943

[3] O. Smetana et al., "Compact Michelson interferometers with subpicometer sensitivity," arXiv:2202.10274. https://arxiv.org/abs/2202.10274

[4] S. M. Kranzhoff et al., "A vertical inertial sensor with interferometric readout," Class. Quantum Grav. 40, 015007 (2023). https://doi.org/10.1088/1361-6382/aca580

[5] R. Halir and J. Flusser, "Numerically stable direct least squares fitting of ellipses," WSCG'98 Conference Proceedings, 1998. -- the general ellipse-fitting family relevant to `fit_circle_center` and the planned Phase 2 ellipse correction.

[6] I. Kasa, "A circle fitting procedure and its error analysis," IEEE Trans. Instrumentation and Measurement, vol. 25, no. 1, 1976, pp. 8-14. https://doi.org/10.1109/TIM.1976.6312298 -- the algebraic circle-fit method `src/analysis.py` implements for DC-bias recovery.

[7] P. Hariharan, Basics of Interferometry, 2nd ed., Academic Press, 2007. -- general reference for Michelson interferometer theory and fringe formation underlying `src/physics.py`.
