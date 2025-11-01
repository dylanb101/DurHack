import numpy as np
import matplotlib.pyplot as plt

def arc_knob(center, radius, start_angle, end_angle, num_points=20):
    """Generate points along an arc."""
    angles = np.linspace(start_angle, end_angle, num_points)
    x = center[0] + radius * np.cos(angles)
    y = center[1] + radius * np.sin(angles)
    return np.column_stack((x, y))

def jigsaw_piece_centered_knobs(num_points_per_side=20, knob_radius=0.2):
    points = []

    # Bottom edge
    x0, x1 = 0, 1
    y = 0
    mid_x = (x0 + x1) / 2

    # Line to start of knob
    points.extend([[x, y] for x in np.linspace(x0, mid_x - knob_radius, num_points_per_side)])

    # Knob: semicircle upward
    knob = arc_knob(center=[mid_x, y], radius=knob_radius, start_angle=np.pi, end_angle=0, num_points=20)
    points.extend(knob)

    # Line after knob
    points.extend([[x, y] for x in np.linspace(mid_x + knob_radius, x1, num_points_per_side)])

    # Right edge
    y0, y1 = 0, 1
    x = 1
    mid_y = (y0 + y1) / 2
    points.extend([[x, y] for y in np.linspace(y0, mid_y - knob_radius, num_points_per_side)])

    # Hole: semicircle leftward (concave)
    hole = arc_knob(center=[x, mid_y], radius=knob_radius, start_angle=-np.pi/2, end_angle=np.pi/2, num_points=20)
    points.extend(hole)

    # Line after hole
    points.extend([[x, y] for y in np.linspace(mid_y + knob_radius, y1, num_points_per_side)])

    # Top edge
    x0, x1 = 1, 0
    y = 1
    mid_x = (x0 + x1) / 2
    points.extend([[x, y] for x in np.linspace(x0, mid_x + knob_radius, num_points_per_side)])
    # Knob down
    knob = arc_knob(center=[mid_x, y], radius=knob_radius, start_angle=0, end_angle=np.pi, num_points=20)
    points.extend(knob)
    points.extend([[x, y] for x in np.linspace(mid_x - knob_radius, x1, num_points_per_side)])

    # Left edge
    y0, y1 = 1, 0
    x = 0
    mid_y = (y0 + y1) / 2
    points.extend([[x, y] for y in np.linspace(y0, mid_y + knob_radius, num_points_per_side)])
    # Hole right
    hole = arc_knob(center=[x, mid_y], radius=knob_radius, start_angle=np.pi/2, end_angle=-np.pi/2, num_points=20)
    points.extend(hole)
    points.extend([[x, y] for y in np.linspace(mid_y - knob_radius, y1, num_points_per_side)])

    return np.array(points)

# Generate and plot
points = jigsaw_piece_centered_knobs(num_points_per_side=20, knob_radius=0.15)

plt.figure(figsize=(5,5))
plt.plot(points[:,0], points[:,1], '-o')
plt.gca().set_aspect('equal')
plt.title("Jigsaw Piece with Centered Knobs and Holes")
plt.show()

np.savetxt("jigsaw_piece.csv", points, delimiter=",", header="x,y", comments='')
