from typing import List, Tuple
import numpy as np
import cv2

class Edge:
    def __init__(
        self,
        type_: str,
        curve: np.ndarray,
        name: str,
        contour_map: List[Tuple[float, float]],
        direction: str,
    ):
        self.type = type_
        self.curve = curve
        self.name = name
        self.contour_map = contour_map
        self.direction = direction

    def normalize(self) -> np.ndarray:
        if len(self.curve) == 0:
            return np.array([])

        # Resample to 100 points for consistency
        num_points = 100
        t = np.linspace(0, 1, len(self.curve))
        t_new = np.linspace(0, 1, num_points)
        x = np.interp(t_new, t, self.curve[:, 0])
        y = np.interp(t_new, t, self.curve[:, 1])
        normalized_curve = np.vstack((x, y)).T

        # Center around (0, 0)
        centroid = np.mean(normalized_curve, axis=0)
        normalized_curve -= centroid

        return normalized_curve

    def is_compatible_with(self, other: "Edge") -> bool:
        if (self.type == "OUT" and other.type == "IN"
            or self.type == "IN" and other.type == "OUT"):
            return True
        else:
            return False

class PuzzlePiece:
     def __init__(
        self,
        center: Tuple[float, float],
        corners: List[Tuple[float, float]],
        contour: List[Tuple[float, float]],
        image_path: str,
        edges: List[Edge],
    ):
        self.center = center
        self.corners = corners
        self.image_path = image_path
        self.edges = edges
        
        # Load image and find contour
        img = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            if contours:
                # Get largest contour
                largest_contour = max(contours, key=cv2.contourArea)
                # Convert to list of tuples
                self.contour = [(float(pt[0][0]), float(pt[0][1])) for pt in largest_contour]
            else:
                self.contour = contour  # fallback to provided contour
        else:
            self.contour = contour  # fallback to provided contour


