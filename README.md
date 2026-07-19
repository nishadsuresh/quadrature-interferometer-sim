# quadrature-interferometer-sim

Simulates a Michelson interferometer with realistic detector noise, then recovers nanometer-scale mirror displacement and vibration from the fringe signals — the exact analysis pipeline a real optics bench needs.

**Status: Phase 1 of 5** (physics simulation).

## Why this exists, and the key design decision

This is the one project in the portfolio tied to real ongoing optics research, not an anonymous simulator. During planning, a naive single-photodiode approach was tested and **failed**: 54% displacement error, plus a fundamental direction ambiguity (`cos(phi)` can't distinguish `+phi` from `-phi`). Switching to **quadrature (I/Q) homodyne detection** — two detectors 90° apart — resolves this: `atan2(Q, I)` gives an unambiguous, monotonic phase estimate. That upgrade is the real instrumentation-engineering content here, not a detail.

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
python tests/test_phase1.py
```

## Phases

| # | Phase | Acceptance test | Result |
|---|---|---|---|
| 1 | Physics sim: quadrature I/Q with tunable noise | Fringe spacing matches λ/2 analytically | ✅ 0.000000% error (31 fringes measured) |
| 2 | Analysis: bias/mains removal, atan2 unwrap, displacement recovery | <1% RMS error on injected displacement | — |
| 3 | Vibration detection via FFT | Vibration frequency within 1% | — |
| 4 | Noise sweep | <1% error across tested noise range | — |
| 5 | Validation report | A written report a reader can check | — |

## One-line summary

I built and validated the full quadrature-detection analysis pipeline a real Michelson interferometer needs, recovering nanometer displacement to under 1% error, tied to my optics research.
