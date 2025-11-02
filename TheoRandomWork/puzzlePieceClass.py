from typing import List, Tuple
import numpy as np


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
        self.contour = contour
        self.image_path = image_path
        self.edges = edges

     def _extract_edge_by_index(self, edge_index: int) -> np.ndarray:
        """
        Private helper to extract the curve of an edge by index.
        """
        if 0 <= edge_index < len(self.edges):
            return self.edges[edge_index].curve
        raise IndexError("Edge index out of range.")

     def _find_nearest_contour_index(
        self, point: np.ndarray, contour: np.ndarray
    ) -> int:
        """
        Private helper to find the index of the nearest contour point to a given point.
        """
        if contour.size == 0:
            raise ValueError("Contour is empty.")
        distances = np.linalg.norm(contour - point, axis=1)
        return int(np.argmin(distances))
