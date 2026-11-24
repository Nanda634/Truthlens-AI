"""FFT/DCT-based frequency-domain analysis - spec section 15."""
import cv2
import numpy as np


def frequency_analysis(path: str) -> dict:
    try:
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return {"available": False, "score": None, "error": "Could not read image."}

        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)
        magnitude = np.log(np.abs(fshift) + 1)

        h, w = magnitude.shape
        cy, cx = h // 2, w // 2
        radius = min(cy, cx)

        # Ratio of high-frequency to low-frequency energy. GAN/diffusion output
        # often shows unusual high-frequency periodicity or suppression versus
        # natural camera sensor spectra.
        y, x = np.ogrid[:h, :w]
        dist = np.sqrt((y - cy) ** 2 + (x - cx) ** 2)
        low_mask = dist <= radius * 0.15
        high_mask = dist >= radius * 0.6

        low_energy = float(magnitude[low_mask].mean()) if low_mask.any() else 0.0
        high_energy = float(magnitude[high_mask].mean()) if high_mask.any() else 0.0
        ratio = high_energy / low_energy if low_energy > 1e-6 else 0.0

        # Periodicity check: look for unusually sharp peaks off-center (upsampling artifacts)
        norm_mag = (magnitude - magnitude.min()) / (magnitude.ptp() + 1e-6)
        peak_ratio = float(np.mean(norm_mag > 0.85))

        score = min(1.0, abs(ratio - 0.45) * 0.8 + peak_ratio * 3.0)
        score = max(0.0, min(1.0, score))

        return {
            "available": True,
            "high_low_freq_ratio": round(ratio, 4),
            "peak_energy_fraction": round(peak_ratio, 5),
            "score": round(score, 3),
        }
    except Exception as e:
        return {"available": False, "score": None, "error": str(e)}
