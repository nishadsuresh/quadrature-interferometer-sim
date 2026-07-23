# Quadrature Interferometer Simulator

**Nishad Suresh**

## Abstract

This project simulates a Michelson interferometer with realistic detector noise and implements the analysis pipeline required to recover nanometer-scale mirror displacement and vibration from the resulting fringe signals. A naive single-photodiode approach was tested during design and found to fail (54% displacement error, with a fundamental direction ambiguity since cos(phi) cannot distinguish +phi from -phi). This motivated a switch to quadrature (I/Q) homodyne detection, using two detectors 90 degrees apart, which resolves the ambiguity via atan2(Q, I) and gives an unambiguous, monotonic phase estimate. The resulting pipeline recovers displacement to 0.0395% RMS error and vibration frequency to 0.0019% error, and remains under 1% error across a detector-noise sweep from 0% to 6%.

**Status:** all 5 phases complete.

## 1. Motivation

This is the one project in this portfolio tied to ongoing optics research rather than an abstract simulation exercise. The central engineering decision -- moving from single-detector to quadrature (I/Q) homodyne detection -- is the primary instrumentation content of the project, not an implementation detail, and is treated as such throughout this document.

## 2. Physics

For a Michelson interferometer with one mirror displaced by `x(t)`, the round-trip path length changes by `2x(t)`, giving phase `phi(t) = 4*pi*x(t)/lambda`. The two quadrature detectors measure:

```
I(t) = I0 * (1 + V*cos(phi(t)))
Q(t) = I0 * (1 + V*sin(phi(t)))
```

## 3. Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python tests/test_phase1.py   # fringe spacing check
python src/validate.py        # displacement recovery
python tests/test_phase3.py   # vibration detection
python tests/test_phase4.py   # noise sweep
python src/dashboard.py       # full visualization
```

## 4. Methodology and Results

| # | Phase | Acceptance test | Result |
|---|---|---|---|
| 1 | Physics simulation: quadrature I/Q with tunable noise | Fringe spacing matches λ/2 analytically | ✅ 0.000000% error (31 fringes) |
| 2 | Analysis: bias/mains removal, atan2 unwrap, displacement recovery | <1% RMS error on injected displacement | ✅ 0.0395% error |
| 3 | Vibration detection via FFT | Vibration frequency within 1% | ✅ 0.0019% error |
| 4 | Noise sweep | <1% error across tested noise range | ✅ max 0.1234% across 0-6% noise |
| 5 | Validation report + dashboard | A written report a reader can check | ✅ `report/validation_report.md` |

### 4.1 Full dashboard

![dashboard](results/dashboard.png)

Fringes, displacement recovery, and vibration spectrum, generated from a single validated simulation run.

### 4.2 Noise robustness

![noise sweep](results/noise_sweep_plot.png)

Full validation writeup with all equations and numbers is available at `report/validation_report.md`.

## 5. A Methodology Issue Found During Review

The original DC-bias estimator, a whole-record mean, only worked correctly because every test case up to that point included a large phase ramp. Pure steady-state vibration sensing with no ramp, one of this project's two stated goals, silently produced 58%+ recovery error under that estimator. This was corrected by geometrically fitting a circle to the (I, Q) trajectory instead (see `report/validation_report.md` for the full account, including a first fix attempt using low-pass filtering that did not actually resolve the issue). Every result reported in Section 4 reflects the corrected code.

A later independent review caught two smaller loose ends left over from that fix: `analysis.py`'s module docstring still described the old low-pass-filter approach rather than the circle fit that had replaced it, and `dashboard.py` re-simulated the interferometer a second time using its own hand-copied parameters instead of reusing `validate.py`'s single source of truth, a real risk of the two silently drifting apart. Both were corrected; `dashboard.py` now pulls I/Q directly from a single `run_validation()` call.

## 6. Limitations

**Simulation only.** Every number reported above is computed on simulated detector data, not a real optical bench. This is framed throughout as validation of the analysis pipeline, not as a claim of having built a physical interferometer.

**No comparison to real bench data yet.** This is the natural next step, planned in collaboration with an optics research mentor, to strengthen the empirical tie beyond simulation. Noted as future work in the validation report.

**Simplified noise model.** Shot noise is modeled as intensity-independent Gaussian noise for tunability, rather than true signal-dependent Poisson shot noise. This is a reasonable approximation at the noise levels tested, but a real bench's noise floor may behave somewhat differently.

## 7. Summary

This project implements and validates the complete quadrature-detection analysis pipeline required by a real Michelson interferometer, recovering nanometer-scale displacement to 0.0395% error and vibration frequency to 0.0019% error, and remaining robust to detector noise up to 6%.

## References

Sources used to design, validate, and cross-check this project's methodology:

[1] C. Lehmann et al., "Nonlinearity correction for homodyne quadrature interferometers," arXiv:2511.04386, Nov. 2025 (Max Planck Institute for Gravitational Physics). https://arxiv.org/abs/2511.04386 -- direction-dependent ellipse-fit correction technique motivating this project's Phase 2 upgrade path.

[2] G. Cooper et al., "A compact, large-range interferometer for precision measurement and inertial sensing," Class. Quantum Grav. 35, 095007 (2018). arXiv:1710.05943. https://arxiv.org/abs/1710.05943

[3] O. Smetana et al., "Compact Michelson interferometers with subpicometer sensitivity," arXiv:2202.10274. https://arxiv.org/abs/2202.10274

[4] S. M. Kranzhoff et al., "A vertical inertial sensor with interferometric readout," Class. Quantum Grav. 40, 015007 (2023). https://doi.org/10.1088/1361-6382/aca580

[5] R. Halir and J. Flusser, "Numerically stable direct least squares fitting of ellipses," WSCG'98 Conference Proceedings, 1998. -- the general ellipse-fitting family relevant to `fit_circle_center` and the planned Phase 2 ellipse correction.

[6] I. Kasa, "A circle fitting procedure and its error analysis," IEEE Trans. Instrumentation and Measurement, vol. 25, no. 1, 1976, pp. 8-14. https://doi.org/10.1109/TIM.1976.6312298 -- the algebraic circle-fit method `src/analysis.py` implements for DC-bias recovery.

[7] P. Hariharan, Basics of Interferometry, 2nd ed., Academic Press, 2007. -- general reference for Michelson interferometer theory and fringe formation underlying `src/physics.py`.
