import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist

def load_and_extract(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    _, bin_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(bin_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    largest = max(contours, key=cv2.contourArea).reshape(-1,2)
    # Center and normalize
    largest = largest - np.mean(largest, axis=0)
    largest = largest / np.sqrt((largest**2).sum(axis=1)).max()
    return largest

def plot_hausdorff(c1, c2, num_connections=100):
    plt.figure(figsize=(8,8))
    plt.plot(c1[:,0], c1[:,1], 'b-', label='Piece 1')
    plt.plot(c2[:,0], c2[:,1], 'r-', label='Piece 2')

    # Compute distances between all points
    dists = cdist(c1, c2)
    # Take num_connections closest pairs
    idx = np.unravel_index(np.argsort(dists, axis=None)[:num_connections], dists.shape)
    
    for i,j in zip(*idx):
        plt.plot([c1[i,0], c2[j,0]], [c1[i,1], c2[j,1]], 'g--', alpha=0.5)

    plt.legend()
    plt.axis('equal')
    plt.show()

# === Example usage ===
piece1 = load_and_extract("images/output_00.png")
piece2 = load_and_extract("images/output_01.png")

plot_hausdorff(piece1, piece2)
