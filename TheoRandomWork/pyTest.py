import cv2
import math
import numpy as np
import matplotlib.pyplot as plt

#Array of points around the jigsaw piece.
points_array = []

def rdp(points):
    epsilon = 0.025 
    # Base case
    if len(points) < 3:
        return points

    # Find the point with the maximum distance from any point

    first, last = points[0], points[-1]
    max_dist = -1
    index = -1
    for i in range(1, len(points)-1):
        dist = perpendicular_distance(points[i], first, last)
        if dist > max_dist:
            max_dist = dist
            index = i

    #If max distance > epsilon, recursively simplify
    if max_dist > epsilon:
        # Recursively simplify left and right segments
        left = rdp(points[:index+1])
        right = rdp(points[index:])

        # Combine results, avoid duplicating the middle point
        return left[:-1] + right
    else:
        # No point is far enough, keep only endpoints
        return [first, last]


# Find perpendicular distance. poimt, start and end are all arrays in form [x_n,y_n]
def perpendicular_distance(p, v1, v2):
    p = np.array(p, dtype = float)
    v1 = np.array(v1, dtype = float)
    v2 = np.array(v2, dtype = float)

    v1_to_v2 = v2 - v1
    point_vec = p - v1

    # Dot product zero method to find closest t
    v1_v2_dist = np.dot(v1_to_v2, v1_to_v2)
    if v1_v2_dist == 0:  # In case segment is a single point
        return np.linalg.norm(point_vec)

    # This ensures that it is only comparing the closest to the segment, rather than the whole line made by the vector
    t = np.dot(point_vec, v1_to_v2) / v1_v2_dist
    t = max(0, min(1, t))  # clamp to segment

    closest_point = v1 + t * v1_to_v2
    distance = np.linalg.norm(p - closest_point)
    return distance    


points = np.loadtxt("jigsaw_piece.csv", delimiter=",", skiprows=1)
simplified = np.array(rdp(points))  # convert list to array

np.savetxt("simplified.csv", simplified, delimiter=",", header="x,y", comments='')

plt.figure(figsize=(5,5))
plt.plot(points[:,0], points[:,1], '-o', label='Original')
plt.plot(simplified[:,0], simplified[:,1], '-ro', label='Simplified')
plt.gca().set_aspect('equal')
plt.legend()
plt.show()
