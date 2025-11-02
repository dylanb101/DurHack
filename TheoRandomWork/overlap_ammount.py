"""
overlap_area.py
-----------------------
Provides a function to compute the overlap area of two contours.
Contours are lists of [x, y] coordinates.
"""

from shapely.geometry import Polygon, MultiPolygon

def make_valid_polygon(points):
    """Ensure polygon closes and fix invalid geometry."""
    # Ensure closed shape
    if points[0] != points[-1]:
        points = points + [points[0]]

    # Remove duplicate consecutive points
    unique_pts = []
    for p in points:
        if not unique_pts or (abs(p[0] - unique_pts[-1][0]) > 1e-9 or abs(p[1] - unique_pts[-1][1]) > 1e-9):
            unique_pts.append(p)
    points = unique_pts

    poly = Polygon(points)
    if not poly.is_valid:
        poly = poly.buffer(0)

    if isinstance(poly, MultiPolygon):
        # Keep the largest polygon if buffer() returns multiple
        poly = max(poly.geoms, key=lambda g: g.area)
    return poly

def compute_overlap_area(contour1, contour2):
    """
    Compute overlap area between two contours.
    
    Parameters
    ----------
    contour1, contour2 : list of [x, y]
        Lists of points representing the polygons.
    
    Returns
    -------
    float
        Total overlap area.
    """
    poly1 = make_valid_polygon(contour1)
    poly2 = make_valid_polygon(contour2)

    inter = poly1.intersection(poly2)

    if inter.is_empty:
        return 0.0
    elif isinstance(inter, Polygon):
        return inter.area
    elif isinstance(inter, MultiPolygon):
        return sum(p.area for p in inter.geoms)
    else:
        return 0.0
