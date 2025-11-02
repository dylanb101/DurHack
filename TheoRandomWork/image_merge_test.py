import cv2
import numpy as np
import matplotlib.pyplot as plt

def load_piece(path):
    """Load image and ensure alpha channel. Black pixels → alpha 0."""
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(f"Image not found: {path}")

    # If grayscale, convert to BGR
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # If no alpha channel, add one
    if img.shape[2] == 3:
        alpha = np.ones(img.shape[:2], dtype=np.uint8) * 255
        img = np.dstack([img, alpha])

    # Make black pixels transparent
    black_mask = np.all(img[:, :, :3] == 0, axis=2)
    img[black_mask, 3] = 0
    return img


def estimate_offset(pieceA, pieceB, max_features=500, top_matches=50):
    """
    Estimate translation offset of pieceB relative to pieceA using ORB features.
    Returns (dx, dy) integer offset.
    """
    grayA = cv2.cvtColor(pieceA[:, :, :3], cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(pieceB[:, :, :3], cv2.COLOR_BGR2GRAY)

    # Detect ORB keypoints and descriptors
    orb = cv2.ORB_create(max_features)
    kpA, desA = orb.detectAndCompute(grayA, None)
    kpB, desB = orb.detectAndCompute(grayB, None)

    # If descriptors are None (no features), fallback
    if desA is None or desB is None:
        return 0, 0

    # Match descriptors
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(desA, desB)
    if not matches:
        return 0, 0

    # Take top matches
    matches = sorted(matches, key=lambda x: x.distance)[:top_matches]

    # Compute median translation
    offsets = []
    for m in matches:
        ptA = np.array(kpA[m.queryIdx].pt)
        ptB = np.array(kpB[m.trainIdx].pt)
        offsets.append(ptA - ptB)
    offsets = np.array(offsets)
    dx, dy = np.median(offsets, axis=0)
    return int(dx), int(dy)


def merge_pieces(pieceA, pieceB):
    """
    Merge two pieces using feature-based alignment and alpha blending.
    """
    hA, wA = pieceA.shape[:2]
    hB, wB = pieceB.shape[:2]

    # Estimate translation
    dx, dy = estimate_offset(pieceA, pieceB)

    # Compute canvas size
    x_min = min(0, dx)
    y_min = min(0, dy)
    x_max = max(wA, dx + wB)
    y_max = max(hA, dy + hB)
    canvas_w = x_max - x_min
    canvas_h = y_max - y_min

    canvas = np.zeros((canvas_h, canvas_w, 4), dtype=np.float32)

    # Place pieceA
    offsetA_x = -x_min
    offsetA_y = -y_min
    canvas[offsetA_y:offsetA_y+hA, offsetA_x:offsetA_x+wA] = pieceA.astype(np.float32)

    # Place pieceB
    offsetB_x = offsetA_x + dx
    offsetB_y = offsetA_y + dy

    alphaA = canvas[offsetB_y:offsetB_y+hB, offsetB_x:offsetB_x+wB, 3] / 255.0
    alphaB = pieceB[:, :, 3] / 255.0
    combined_alpha = alphaB + alphaA * (1 - alphaB)
    combined_alpha = np.clip(combined_alpha, 1e-6, 1.0)  # avoid divide by zero

    for c in range(3):
        canvas[offsetB_y:offsetB_y+hB, offsetB_x:offsetB_x+wB, c] = (
            pieceB[:, :, c] * alphaB + canvas[offsetB_y:offsetB_y+hB, offsetB_x:offsetB_x+wB, c] * alphaA * (1 - alphaB)
        ) / combined_alpha

    canvas[offsetB_y:offsetB_y+hB, offsetB_x:offsetB_x+wB, 3] = combined_alpha * 255

    return canvas.astype(np.uint8)


def main():
    pieceA = load_piece("images/output_4.png")
    pieceB = load_piece("images/output_26.png")

    merged = merge_pieces(pieceA, pieceB)

    # Convert BGRA → RGBA for matplotlib
    merged_rgb = cv2.cvtColor(merged, cv2.COLOR_BGRA2RGBA)
    plt.figure(figsize=(20, 20))
    plt.imshow(merged_rgb)
    plt.axis("off")
    plt.title("Merged Puzzle Pieces (Feature-based)")
    plt.show()


if __name__ == "__main__":
    main()
