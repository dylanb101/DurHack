import cv2
import math
import numpy as np
import matplotlib.pyplot as plt

# --- RDP Implementation ---

def rdp(points, epsilon=50):
    """Recursive Ramer–Douglas–Peucker simplification."""
    if len(points) < 3:
        return points

    first, last = points[0], points[-1]
    max_dist = -1
    index = -1

    for i in range(1, len(points) - 1):
        dist = perpendicular_distance(points[i], first, last)
        if dist > max_dist:
            max_dist = dist
            index = i

    if max_dist > epsilon:
        left = rdp(points[:index + 1], epsilon)
        right = rdp(points[index:], epsilon)
        return left[:-1] + right
    else:
        return [first, last]


def perpendicular_distance(p, v1, v2):
    """Compute the perpendicular distance from point p to line segment v1–v2."""
    p = np.array(p, dtype=float)
    v1 = np.array(v1, dtype=float)
    v2 = np.array(v2, dtype=float)

    v1_to_v2 = v2 - v1
    point_vec = p - v1

    v1_v2_dist = np.dot(v1_to_v2, v1_to_v2)
    if v1_v2_dist == 0:
        return np.linalg.norm(point_vec)

    t = np.dot(point_vec, v1_to_v2) / v1_v2_dist
    t = max(0, min(1, t))  # clamp to segment
    closest_point = v1 + t * v1_to_v2
    distance = np.linalg.norm(p - closest_point)
    return distance


# --- Load points ---

points = np.loadtxt("points.csv", delimiter=",", skiprows=1)

# --- Plot all raw points before simplification ---

plt.figure(figsize=(8, 8))
plt.plot(points[:, 0], points[:, 1], 'o-', markersize=2, linewidth=0.8, label='Original Points')
plt.title("Raw Points Before Simplification")
plt.xlabel("X")
plt.ylabel("Y")
plt.axis('equal')
plt.grid(True)
plt.legend()
plt.show()

# --- Apply RDP simplification ---

simplified = np.array(rdp(points.tolist(), epsilon=50))

# --- Save simplified points ---

np.savetxt("simplified.csv", simplified, delimiter=",", header="x,y", comments='')

# --- Plot both together ---

plt.figure(figsize=(8, 8))
plt.plot(points[:, 0], points[:, 1], '-o', markersize=2, linewidth=0.8, label='Original')
plt.plot(simplified[:, 0], simplified[:, 1], '-ro', markersize=4, linewidth=1.2, label='Simplified')
plt.gca().set_aspect('equal')
plt.title("RDP Simplification Comparison")
plt.xlabel("X")
plt.ylabel("Y")
plt.legend()
plt.grid(True)
plt.show()
