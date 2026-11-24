"""
Noise / high-frequency residual consistency analysis - spec section 11.
Compares local noise variance across image blocks; large deviations between
regions can indicate localized editing (splicing / smoothing / regeneration).
"""
import cv2
import numpy as np


def noise_consistency_analysis(path: str, block_size: int = 32) -> dict:
    try:
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return {"available": False, "score": None, "error": "Could not read image."}

        # High-pass residual via Laplacian - approximates sensor/compression noise.
        residual = cv2.Laplacian(img, cv2.CV_64F)

        h, w = residual.shape
        block_vars = []
        for y in range(0, h - block_size, block_size):
            for x in range(0, w - block_size, block_size):
                block = residual[y:y + block_size, x:x + block_size]
                block_vars.append(block.var())

        if len(block_vars) < 4:
            return {"available": False, "score": None, "error": "Image too small for block analysis."}

        block_vars = np.array(block_vars)
        median_var = float(np.median(block_vars))
        std_var = float(np.std(block_vars))
        cv = std_var / median_var if median_var > 1e-6 else 0.0

        outlier_count = int(np.sum(np.abs(block_vars - median_var) > 2.5 * std_var)) if std_var > 0 else 0
        outlier_pct = round(outlier_count / len(block_vars) * 100, 2)

        score = min(1.0, (min(cv, 3.0) / 3.0) * 0.5 + (outlier_pct / 20.0) * 0.5)

        return {
            "available": True,
            "median_block_variance": round(median_var, 4),
            "coefficient_of_variation": round(cv, 4),
            "outlier_block_percentage": outlier_pct,
            "score": round(score, 3),
        }
    except Exception as e:
        return {"available": False, "score": None, "error": str(e)}
