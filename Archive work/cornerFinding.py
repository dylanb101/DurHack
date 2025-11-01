import numpy as np
import matplotlib.pyplot as plt

def angle_between(v1, v2):

    v1_u = v1 / np.linalg.norm(v1)
    v2_u = v2 / np.linalg.norm(v2)
    dot = np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)  # clamp for numerical stability
    angle_rad = np.arccos(dot)
    print(angle_rad)
    return np.degrees(angle_rad)

def find_corners(points, angle_threshold=30, window=5):
    corners = []
    n = len(points)
    for i in range(n):
        p_prev = points[(i - window) % n]
        p_curr = points[i]
        p_next = points[(i + window) % n]

        v1 = p_curr - p_prev
        v2 = p_next - p_curr

        if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
            continue

        angle = angle_between(v1, v2)
        if angle < (180 - angle_threshold):
            corners.append(p_curr)
    return np.array(corners)



# --- Main Script ---

# Load simplified points

simplified_points = np.loadtxt("jigsaw_piece.csv", delimiter=",", skiprows=1)

# Detect corners

corners = find_corners(simplified_points, angle_threshold=30)

# Plot

plt.figure(figsize=(6,6))
plt.plot(simplified_points[:,0], simplified_points[:,1], '-o', color='lightgray', label='Simplified Shape')
if len(corners) > 0:
    plt.scatter(corners[:,0], corners[:,1], color='red', s=80, label='Detected Corners')

plt.gca().set_aspect('equal')
plt.title("Detected Corners on Simplified Jigsaw Piece")
plt.legend()
plt.show()

# Optional: save corners to CSV

np.savetxt("detected_corners.csv", corners, delimiter=",", header="x,y", comments='')
