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
        self.contour = contour


     def find_edge(self, corner1: Tuple[float, float], corner2: Tuple[float, float]) -> np.ndarray:
        # Find contour points closest to each corner
        contour_array = np.array(self.contour)
        
        dist1 = np.linalg.norm(contour_array - corner1, axis=1)
        dist2 = np.linalg.norm(contour_array - corner2, axis=1)
        
        idx1 = np.argmin(dist1)
        idx2 = np.argmin(dist2)
        
        # Extract the contour segment between the two indices
        if idx1 < idx2:
            edge_segment = contour_array[idx1:idx2+1]
        else:
            # Wrap around if needed
            edge_segment = np.vstack([contour_array[idx1:], contour_array[:idx2+1]])
        
        return edge_segment
        

