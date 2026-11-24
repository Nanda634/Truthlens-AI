"""
Splicing indicator analysis - spec section 13.
Lightweight heuristic combining edge-density irregularity and local color/
illumination variance across quadrants. This is NOT a trained splicing
classifier - it surfaces a supporting signal only.
"""
import cv2
import numpy as np


def splicing_analysis(path: str) -> dict:
    try:
        img = cv2.imread(path)
        if img is None:
            return {"available": False, "splicing_probability": None, "regions": [], "error": "Could not read image."}

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 80, 160)

        h, w = gray.shape
        mid_y, mid_x = h // 2, w // 2
        quadrants = {
            "top_left": (slice(0, mid_y), slice(0, mid_x)),
            "top_right": (slice(0, mid_y), slice(mid_x, w)),
            "bottom_left": (slice(mid_y, h), slice(0, mid_x)),
            "bottom_right": (slice(mid_y, h), slice(mid_x, w)),
        }

        edge_densities = []
        color_means = []
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        for name, (ys, xs) in quadrants.items():
            edge_densities.append(edges[ys, xs].mean())
            color_means.append(lab[ys, xs].reshape(-1, 3).mean(axis=0))

        edge_std = float(np.std(edge_densities))
        color_variation = float(np.mean(np.std(np.array(color_means), axis=0)))

        splicing_prob = min(1.0, (edge_std / 25.0) * 0.5 + (color_variation / 20.0) * 0.5)

        return {
            "available": True,
            "splicing_probability": round(splicing_prob, 3),
            "edge_density_std": round(edge_std, 3),
            "color_variation": round(color_variation, 3),
            "regions": [],
            "note": "Heuristic signal based on edge/illumination irregularity, not a trained splicing classifier.",
        }
    except Exception as e:
        return {"available": False, "splicing_probability": None, "regions": [], "error": str(e)}
