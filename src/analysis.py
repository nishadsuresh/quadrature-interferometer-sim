"""
Analysis pipeline: raw quadrature (I, Q) detector signals -> recovered
mirror displacement.

Steps:
1. Remove DC bias (estimate I0 as the mean of each channel).
2. Remove the 60Hz mains component via a least-squares sinusoid fit at
   exactly 60Hz and subtract it -- narrowband, so it does NOT touch the
   real slow displacement signal the way a generic polynomial detrend would.
3. Recover phase via atan2(Q_ac, I_ac), unwrapped to remove 2*pi jumps.
4. Convert phase to displacement: x = phase * lambda / (4*pi).
"""

from __future__ import annotations

import numpy as np

from optics import HENE_WAVELENGTH_M


def remove_mains(signal: np.ndarray, t: np.ndarray, mains_freq_hz: float = 60.0) -> np.ndarray:
    """Least-squares fit and subtract a sinusoid at exactly mains_freq_hz.
    Narrowband by construction -- unlike a polynomial detrend, this cannot
    accidentally remove real slow-displacement content at other frequencies."""
    cos_term = np.cos(2 * np.pi * mains_freq_hz * t)
    sin_term = np.sin(2 * np.pi * mains_freq_hz * t)
    design = np.column_stack([cos_term, sin_term, np.ones_like(t)])  # + DC term in the same fit
    coeffs, *_ = np.linalg.lstsq(design, signal, rcond=None)
    fitted = design @ coeffs
    # only remove the mains-frequency component, keep the fitted DC offset in
    # (DC is handled separately in recover_displacement via the channel mean)
    mains_only = coeffs[0] * cos_term + coeffs[1] * sin_term
    return signal - mains_only


def recover_displacement(
    I: np.ndarray,
    Q: np.ndarray,
    t: np.ndarray,
    wavelength_m: float = HENE_WAVELENGTH_M,
    remove_mains_flag: bool = True,
    mains_freq_hz: float = 60.0,
) -> np.ndarray:
    """Returns recovered displacement x(t) in meters."""
    I_proc = remove_mains(I, t, mains_freq_hz) if remove_mains_flag else I.copy()
    Q_proc = remove_mains(Q, t, mains_freq_hz) if remove_mains_flag else Q.copy()

    I_ac = I_proc - np.mean(I_proc)
    Q_ac = Q_proc - np.mean(Q_proc)

    phase = np.unwrap(np.arctan2(Q_ac, I_ac))
    displacement = phase * wavelength_m / (4 * np.pi)
    return displacement


def detect_vibration_freq(x_recovered: np.ndarray, t: np.ndarray) -> tuple[float, float]:
    """Removes the slow linear trend (ramp) from recovered displacement, then
    FFTs the residual to find the dominant vibration frequency. Uses
    parabolic interpolation around the FFT peak for sub-bin frequency
    accuracy (plain argmax is only accurate to the bin width).

    Returns (frequency_hz, magnitude_at_peak)."""
    # remove linear trend (the ramp) -- least-squares line fit, subtract
    design = np.column_stack([t, np.ones_like(t)])
    coeffs, *_ = np.linalg.lstsq(design, x_recovered, rcond=None)
    residual = x_recovered - design @ coeffs

    fs = 1 / (t[1] - t[0])
    windowed = residual * np.hanning(len(residual))
    spectrum = np.abs(np.fft.rfft(windowed))
    freqs = np.fft.rfftfreq(len(windowed), d=1 / fs)

    peak_bin = int(np.argmax(spectrum))
    if peak_bin == 0 or peak_bin == len(spectrum) - 1:
        return float(freqs[peak_bin]), float(spectrum[peak_bin])

    y0, y1, y2 = spectrum[peak_bin - 1], spectrum[peak_bin], spectrum[peak_bin + 1]
    denom = y0 - 2 * y1 + y2
    delta = 0.5 * (y0 - y2) / denom if denom != 0 else 0.0
    bin_width = freqs[1] - freqs[0]
    freq = freqs[peak_bin] + delta * bin_width
    return float(freq), float(spectrum[peak_bin])
