import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import json
from shapely.geometry import Polygon
from overlap_ammount import compute_overlap_area  # Your module


def trace_contours(image_path, title="Trace contours"):
    """
    Display image and allow user to trace multiple contours.
    Left-click to add points, right-click to finish one contour.
    Close window when done.
    Returns a list of contours (each contour is a list of points).
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
    """Display image and allow user to click one point."""
    img = mpimg.imread(image_path)
    plt.figure()
    plt.imshow(img)
    plt.title(title + "\nClick the reference point.")
    plt.axis('equal')
    point = plt.ginput(n=1, timeout=0)[0]
    plt.close()
    print(f"{title} - reference point at {point}")
    return point


def translate_contours(contours, src_point, dst_point):
    """Translate all contours so src_point moves to dst_point."""
    dx = dst_point[0] - src_point[0]
    dy = dst_point[1] - src_point[1]
    translated = []
    for contour in contours:
        translated.append([[x + dx, y + dy] for x, y in contour])
    return translated


def contours_to_polygon(contours):
    """
    Convert list of contours to a Shapely Polygon with holes.
    First contour is treated as exterior; others as interiors.
    """
    if not contours:
        return None
    exterior = contours[0]
    interiors = contours[1:] if len(contours) > 1 else []
    return Polygon(shell=exterior, holes=interiors)


def plot_overlaid_contours(contours1, contours2, inter_area=0.0):
    """Plot two sets of contours and highlight overlap area if possible."""
    poly1 = contours_to_polygon(contours1)
    poly2 = contours_to_polygon(contours2)
    inter = poly1.intersection(poly2)

    fig, ax = plt.subplots()
    ax.set_aspect('equal', adjustable='box')

    # Plot contours1
    for c in contours1:
        x, y = zip(*c)
        ax.fill(x, y, alpha=0.3, color='blue', label='Contour 1')

    # Plot contours2
    for c in contours2:
        x, y = zip(*c)
        ax.fill(x, y, alpha=0.3, color='red', label='Contour 2')

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


def main():
    # Input image paths
    image1 = input("Enter first image path: ").strip()
    image2 = input("Enter second image path: ").strip()

    # Trace contours
    contours1 = trace_contours(image1, "Trace first shape (first contour = outer, others = holes)")
    contours2 = trace_contours(image2, "Trace second shape (first contour = outer, others = holes)")

    # Pick reference points
    ref1 = pick_reference_point(image1, "Pick reference point on first shape")
    ref2 = pick_reference_point(image2, "Pick reference point on second shape")

    # Translate second contours to align reference points
    contours2_translated = translate_contours(contours2, ref2, ref1)

    # Compute overlap area
    poly1 = contours_to_polygon(contours1)
    poly2 = contours_to_polygon(contours2_translated)
    inter = poly1.intersection(poly2)
    overlap_area = inter.area if not inter.is_empty else 0.0
    print(f"\nOverlap area: {overlap_area:.6f}")

    # Plot overlaid contours
    plot_overlaid_contours(contours1, contours2_translated, overlap_area)

    # Optionally save traced contours
    save = input("Save traced contours? (y/n): ").strip().lower()
    if save == 'y':
        with open("contours1.json", "w") as f:
            json.dump(contours1, f, indent=2)
        with open("contours2.json", "w") as f:
            json.dump(contours2_translated, f, indent=2)
        print("Contours saved as contours1.json and contours2.json")


if __name__ == "__main__":
    main()
