"""
Copy-move forgery detection - spec section 12.
Uses ORB feature matching + spatial-offset clustering: genuine duplicated
regions produce many keypoint matches sharing a consistent translation vector
that isn't simply the identity match.
"""
import cv2
import numpy as np


def copy_move_detection(path: str, min_matches: int = 8) -> dict:
    try:
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return {"available": False, "score": None, "error": "Could not read image.", "regions": []}

        orb = cv2.ORB_create(nfeatures=2000)
        keypoints, descriptors = orb.detectAndCompute(img, None)

        if descriptors is None or len(keypoints) < 20:
            return {"available": True, "score": 0.0, "matches_found": 0, "regions": [],
                    "note": "Insufficient keypoints for reliable copy-move analysis."}

        bf = cv2.BFMatcher(cv2.NORM_HAMMING)
        matches = bf.knnMatch(descriptors, descriptors, k=3)

        offsets = []
        regions = []
        h, w = img.shape
        min_dist = 0.02 * max(h, w)  # ignore near-identical (self) matches

        for m_list in matches:
            for m in m_list[1:]:  # skip index 0 (match to itself)
                pt1 = np.array(keypoints[m.queryIdx].pt)
                pt2 = np.array(keypoints[m.trainIdx].pt)
                dist = np.linalg.norm(pt1 - pt2)
                if dist > min_dist and m.distance < 40:
                    offset = tuple(np.round(pt1 - pt2, -1))  # bucket offsets
                    offsets.append((offset, pt1, pt2))

        if not offsets:
            return {"available": True, "score": 0.0, "matches_found": 0, "regions": [],
                    "note": "No consistent duplicated regions detected."}

        # cluster by offset bucket
        from collections import Counter
        offset_counts = Counter(o[0] for o in offsets)
        best_offset, count = offset_counts.most_common(1)[0]

        matched_points = [pt1 for (off, pt1, pt2) in offsets if off == best_offset]
        score = min(1.0, count / 40.0)

        if count >= min_matches and matched_points:
            xs = [p[0] for p in matched_points]
            ys = [p[1] for p in matched_points]
            regions.append({
                "x": float(min(xs)), "y": float(min(ys)),
                "width": float(max(xs) - min(xs) + 10),
                "height": float(max(ys) - min(ys) + 10),
                "confidence": round(score, 3),
            })

        return {
            "available": True,
            "score": round(score, 3),
            "matches_found": int(count),
            "regions": regions,
        }
    except Exception as e:
        return {"available": False, "score": None, "error": str(e), "regions": []}
