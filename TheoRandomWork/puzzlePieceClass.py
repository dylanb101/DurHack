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

        #Centre around (0, 0)
        centroid = np.mean(normalized_curve, axis=0)
        normalized_curve -= centroid

        return normalized_curve

    def is_compatible_with(self, other: "Edge") -> bool:
        if (self.type == "OUT" and other.type == "IN"
            or self.type == "IN" and other.type == "OUT"):
            return True
        else:
            return False

from typing import List, Tuple
import numpy as np
import cv2

class PuzzlePiece:
    def __init__(
        self,
        centre: Tuple[float, float],
        corners: List[Tuple[float, float]],
        contour: List[Tuple[float, float]],
        image_path: str,
        edges: List[Edge],
        edge_types: List[str] = None,
    ):
        self.centre = centre
        self.corners = corners
        self.image_path = image_path
        self.contour = contour
        self.edge_types = edge_types if edge_types else ["FLAT"] * len(corners)
        self.edges = self._create_edges()

    def _create_edges(self) -> List[Edge]:
        """Create four edges from the four corners."""
        edges = []
        num_corners = len(self.corners)
        
        for i in range(num_corners):
            corner1 = self.corners[i]
            corner2 = self.corners[(i + 1) % num_corners]
            
            # Use find_edge method to get the contour segment
            edge_curve = self.find_edge(corner1, corner2)
            
            # Create an Edge object with the correct type
            edge = Edge(
                type_=self.edge_types[i],
                curve=edge_curve,
                name=f"edge_{i}",
                contour_map=[corner1, corner2],
                direction="horizontal" if i % 2 == 0 else "vertical"
            )
            edges.append(edge)
        
        return edges

    def find_edge(self, corner1: Tuple[float, float], corner2: Tuple[float, float]) -> np.ndarray:
        """Find the contour segment between two corners."""
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