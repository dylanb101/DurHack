import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import json
from shapely.geometry import Polygon
import math


def trace_contours(image_path, title="Trace contours"):
    """
    Interactive tool to trace contours on an image.
    Left-click to add points, right-click to finish contour, close window when done.
    """
    img = mpimg.imread(image_path)
    plt.figure()
    plt.imshow(img)
    plt.title(f"{title}\nLeft-click to add points, right-click to finish contour, close window when done.")
    plt.axis('equal')

    all_contours = []
    while True:
        points = plt.ginput(n=-1, timeout=0, show_clicks=True)
        if not points:
            break
        all_contours.append(points)
        print(f"{title} - contour with {len(points)} points recorded.")
    
    plt.close()
    print(f"{title} - total {len(all_contours)} contours recorded.")
    return all_contours


def pick_reference_point(image_path, title="Pick reference point"):
    """
    Interactive tool to pick a reference point on an image.
    """
    img = mpimg.imread(image_path)
    plt.figure()
    plt.imshow(img)
    plt.title(title + "\nClick the reference point.")
    plt.axis('equal')
    point = plt.ginput(n=1, timeout=0)[0]
    plt.close()
    print(f"{title} - reference point at {point}")
    return point


def translate_and_rotate(contours, ref_point, dx=0, dy=0, angle_deg=0):
    """
    Transform contours by translation and rotation around a reference point.
    """
    angle = math.radians(angle_deg)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    transformed = []
    for contour in contours:
        new_contour = []
        for x, y in contour:
            # Translate to origin
            x0, y0 = x - ref_point[0], y - ref_point[1]
            # Rotate
            xr = x0 * cos_a - y0 * sin_a
            yr = x0 * sin_a + y0 * cos_a
            # Translate back and apply offset
            new_contour.append([xr + ref_point[0] + dx, yr + ref_point[1] + dy])
        transformed.append(new_contour)
    
    return transformed


def contours_to_polygon_with_holes(contours):
    """
    Convert a list of contours to a Polygon with holes.
    First contour is the exterior, subsequent contours are holes if contained.
    """
    if not contours:
        return None

    exterior = contours[0]
    interiors = []

    exterior_poly = Polygon(exterior)
    for contour in contours[1:]:
        test_poly = Polygon(contour)
        if exterior_poly.contains(test_poly):
            interiors.append(contour)

    return Polygon(shell=exterior, holes=interiors)


def compute_overlap_area(contours1, contours2):
    """
    Compute the area of intersection between two sets of contours.
    """
    poly1 = contours_to_polygon_with_holes(contours1)
    poly2 = contours_to_polygon_with_holes(contours2)
    inter = poly1.intersection(poly2)
    return inter.area if not inter.is_empty else 0.0


def compute_fit_score(contours1, contours2, edge1_indices=None, edge2_indices=None, 
                      gap_penalty=5.0, extra_penalty=1.0, overlap_penalty=3.0):
    """
    Compute a fit score that rewards edge alignment and penalizes gaps and overlaps.
    Higher score is better.
    
    If edge indices are provided, computes the gap between those specific edges.
    Otherwise, uses the symmetric difference as a proxy for poor fit.
    
    Args:
        contours1, contours2: The contour sets
        edge1_indices, edge2_indices: Tuples of (contour_idx, start_point_idx, end_point_idx) 
                                       to specify which edge segments should align
        gap_penalty: Weight for penalizing gaps between the specified edges
        extra_penalty: Weight for penalizing extra non-overlapping material
        overlap_penalty: Weight for penalizing overlap (jigsaw pieces shouldn't overlap)
    """
    poly1 = contours_to_polygon_with_holes(contours1)
    poly2 = contours_to_polygon_with_holes(contours2)
    
    area1 = poly1.area
    area2 = poly2.area
    inter = poly1.intersection(poly2)
    overlap_area = inter.area if not inter.is_empty else 0.0
    
    # Extra material (symmetric difference)
    extra_material = area1 + area2 - 2 * overlap_area
    
    # If edges are specified, compute gap between them
    gap_penalty_value = 0
    if edge1_indices is not None and edge2_indices is not None:
        edge1_points = extract_edge_points(contours1, edge1_indices)
        edge2_points = extract_edge_points(contours2, edge2_indices)
        gap_penalty_value = compute_edge_gap(edge1_points, edge2_points)
    
    # Score: penalize gaps, overlaps, and extra material
    # Note: We want minimal overlap for jigsaw pieces
    score = -gap_penalty * gap_penalty_value - overlap_penalty * overlap_area - extra_penalty * extra_material
    
    return score, overlap_area


def extract_edge_points(contours, edge_spec):
    """
    Extract points along a specified edge.
    edge_spec: (contour_idx, start_point_idx, end_point_idx)
    """
    if edge_spec is None:
        return []
    
    contour_idx, start_idx, end_idx = edge_spec
    contour = contours[contour_idx]
    
    if start_idx <= end_idx:
        return contour[start_idx:end_idx+1]
    else:
        # Wrap around
        return contour[start_idx:] + contour[:end_idx+1]


def compute_edge_gap(edge1_points, edge2_points):
    """
    Compute a measure of the gap between two edges.
    Uses average minimum distance between points on the edges.
    """
    if not edge1_points or not edge2_points:
        return 0.0
    
    total_dist = 0.0
    
    # For each point on edge1, find closest point on edge2
    for p1 in edge1_points:
        min_dist = float('inf')
        for p2 in edge2_points:
            dist = math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
            min_dist = min(min_dist, dist)
        total_dist += min_dist
    
    # Average distance
    return total_dist / len(edge1_points)


def plot_overlaid_contours(contours1, contours2, inter_area=0.0):
    """
    Visualize two sets of contours and their overlap.
    """
    poly1 = contours_to_polygon_with_holes(contours1)
    poly2 = contours_to_polygon_with_holes(contours2)
    inter = poly1.intersection(poly2)

    fig, ax = plt.subplots()
    ax.set_aspect('equal', adjustable='box')

    # Plot first shape
    for c in contours1:
        x, y = zip(*c)
        ax.fill(x, y, alpha=0.3, color='blue', label='Shape 1')

    # Plot second shape
    for c in contours2:
        x, y = zip(*c)
        ax.fill(x, y, alpha=0.3, color='red', label='Shape 2')

    # Plot intersection
    if not inter.is_empty:
        polys = [inter] if isinstance(inter, Polygon) else inter.geoms
        for g in polys:
            xi, yi = g.exterior.xy
            ax.fill(xi, yi, alpha=0.5, color='green', label='Overlap')
            for interior in g.interiors:
                xi, yi = interior.xy
                ax.fill(xi, yi, alpha=0.5, color='green')

    ax.legend()
    plt.title(f"Overlap area: {inter_area:.6f}")
    plt.show()


def optimize_alignment(contours1, contours2, ref2, max_shift=20, shift_step=1, 
                       max_angle=15, angle_step=1, edge1_spec=None, edge2_spec=None,
                       gap_penalty=5.0, extra_penalty=1.0, overlap_penalty=3.0):
    """
    Find the optimal translation and rotation to maximize fit score.
    Rotation happens around ref2 (the reference point on piece 2).
    
    Args:
        ref2: Reference point to rotate around
        edge1_spec, edge2_spec: Tuples of (contour_idx, start_point_idx, end_point_idx)
                                to specify which edges should be aligned
        gap_penalty: Weight for penalizing gaps between edges (default 5.0)
        extra_penalty: Weight for penalizing extra material (default 1.0)
        overlap_penalty: Weight for penalizing overlap (default 3.0)
    """
    best_score = float('-inf')
    best_overlap = 0
    best_transform = contours2

    for angle in range(-max_angle, max_angle + 1, angle_step):
        # First rotate around ref2
        rotated = translate_and_rotate(contours2, ref2, dx=0, dy=0, angle_deg=angle)
        
        # Then try translations
        for dx in range(-max_shift, max_shift + 1, shift_step):
            for dy in range(-max_shift, max_shift + 1, shift_step):
                # Apply translation to the already-rotated contours
                translated = translate_and_rotate(rotated, ref2, dx=dx, dy=dy, angle_deg=0)
                
                score, overlap = compute_fit_score(contours1, translated, 
                                                   edge1_spec, edge2_spec,
                                                   gap_penalty, extra_penalty, overlap_penalty)
                if score > best_score:
                    best_score = score
                    best_overlap = overlap
                    best_transform = translated

    return best_transform, best_overlap


def main():
    """
    Main workflow: trace contours, align shapes, and compute overlap.
    """
    image1 = "test_images/piece1.png"
    image2 = "test_images/piece2.png"

    # Trace contours on both images
    contours1 = trace_contours(image1, "Trace first shape (first contour = outer, others = holes)")
    contours2 = trace_contours(image2, "Trace second shape (first contour = outer, others = holes)")

    # Pick reference points
    ref1 = pick_reference_point(image1, "Pick reference point on first shape")
    ref2 = pick_reference_point(image2, "Pick reference point on second shape")

    # Initial translation to roughly align reference points
    contours2_translated = translate_and_rotate(
        contours2, ref2, 
        dx=ref1[0] - ref2[0], 
        dy=ref1[1] - ref2[1], 
        angle_deg=0
    )

    # Optimize alignment
    # To use edge-specific gap penalty, specify which edge segments should align:
    # edge_spec format: (contour_index, start_point_index, end_point_index)
    # Example: edge1_spec = (0, 5, 15) means use points 5-15 from first contour of shape 1
    # Leave as None to use only area-based penalties
    
    edge1_spec = None  # Set to (0, start_idx, end_idx) to specify edge on piece 1
    edge2_spec = None  # Set to (0, start_idx, end_idx) to specify edge on piece 2
    
    best_contours, best_overlap = optimize_alignment(
        contours1, contours2_translated, ref1,
        edge1_spec=edge1_spec, edge2_spec=edge2_spec,
        gap_penalty=5.0,      # Increase to more heavily penalize gaps between edges
        extra_penalty=1.0,    # Increase to more heavily penalize extra material
        overlap_penalty=3.0   # Increase to more heavily penalize overlapping pieces
    )
    print(f"\nBest overlap area: {best_overlap:.6f}")

    # Visualize results
    plot_overlaid_contours(contours1, best_contours, best_overlap)

    # Save contours
    with open("contours1.json", "w") as f:
        json.dump(contours1, f, indent=2)
    with open("contours2.json", "w") as f:
        json.dump(best_contours, f, indent=2)
    print("Contours saved as contours1.json and contours2.json")


if __name__ == "__main__":
    main()