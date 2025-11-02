# from puzzlePieceClass import PuzzlePiece
import json
import matplotlib.pyplot as plt
from matplotlib import image as mpimg
from shapely.geometry import Polygon
import numpy as np
import math

DO_DISPLAY = True

class Piece:
    def __init__(
        self,
        centre,
        corners,
        image_path,
        edges,
        contour,
    ):
        self.centre = centre
        self.corners = corners
        self.image_path = image_path
        self.edges = edges
        self.contour = contour


def is_pt_inside(test_pt, top_left, bottom_right):
    x, y = test_pt
    x1, y1 = top_left
    x2, y2 = bottom_right
    return x1 <= x <= x2 and y1 <= y <= y2

def display(all_edges, f_name):
    fig, axes = plt.subplots(3, 3, figsize=(18, 18))

    coords = (
        (0, 1),
        (1, 2),
        (2, 1),
        (1, 0),
    )

    for i, edge_dict in enumerate(all_edges):
        edge = edge_dict['pts']
        ftype = edge_dict['type']
        x_coords = [point[0] for point in edge]
        y_coords = [point[1] for point in edge]

        x, y = coords[i]

        axes[y, x].plot(x_coords, y_coords, 'b-', linewidth=2)
        axes[y, x].scatter(x_coords[0], y_coords[0], c='green', s=100, zorder=5, label='Start')
        axes[y, x].scatter(x_coords[-1], y_coords[-1], c='red', s=100, zorder=5, label='End')
        axes[y, x].set_title(ftype)
        axes[y, x].set_aspect('equal')
        axes[y, x].legend()
        axes[y, x].grid(True, alpha=0.3)
        axes[y, x].invert_yaxis()

    img = mpimg.imread('images/' + f_name)
    axes[1, 1].imshow(img)
    axes[1, 1].set_title("Your Image")
    axes[1, 1].axis('off')

    for i in range(3):
        for j in range(3):
            if (j, i) not in coords and not (i == 1 and j == 1):
                axes[i, j].axis('off')

    plt.tight_layout()
    plt.show()

with open("pieces_output.json", "r") as f:
    data1 = json.load(f)

with open("contour_data.json", "r") as f:
    data2 = json.load(f)

pieces = []
for item1, item2 in zip(data1, data2):

    corners = item1["corners"]
    contour = item2["contours"]

    idxs = []
    for corner in corners:
        best_point = min(
            contour,
            key=lambda point: (point[0] - corner[0]) ** 2 + (point[1] - corner[1]) ** 2,
        )
        idxs.append(contour.index(best_point))
    idxs.sort()

    assert len(idxs) == 4

    all_edges = []
    for idx_idx in range(0, 4):
        idx = idxs[idx_idx]
        curr_edge = [contour[idx]]

        while True:
            idx = (idx + 1) % len(contour)
            curr_edge.append(contour[idx])
            if idx == idxs[(idx_idx + 1) % 4]:
                break

        ftype = 'flat'
        for feature in item1['features']:
            pt1 = feature['pt1']
            pt2 = feature['pt2']

            for edge_pt in curr_edge:
                if is_pt_inside(edge_pt, pt1, pt2):
                    ftype = feature['type']

        all_edges.append({
            'pts': np.array(curr_edge, dtype=np.float32),
            'type': ftype
        })

    # --------------------------------------
    if DO_DISPLAY:
        display(all_edges, item2['file_name'])
    # --------------------------------------

    piece = Piece(
        centre=tuple(item1["piece_centre"]),
        corners=corners,
        image_path=item2["file_name"],
        edges=all_edges,
        contour=contour,
    )
    pieces.append(piece)

# PoC
def get_area(edg1, edg2, display=False):
    comb = np.concatenate([edg1, edg2, [edg1[0]]])

    if display:
        xs = [pt[0] for pt in comb]
        ys = [pt[1] for pt in comb]

        plt.plot(xs, ys)
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Line Plot from Coordinates')
        plt.grid(True)
        plt.show()

    return Polygon(comb).area

edg1 = pieces[0].edges[1]['pts']
edg2 = pieces[0].edges[3]['pts']

# def translate(x, y, contour):
#     for pt in contour:
#         pt[0] += x
#         pt[1] += y

# def rotate(theta, contour, about):
#     cos_a = np.cos(theta)
#     sin_a = np.sin(theta)

#     rotation_matrix = np.array([
#         [cos_a, -sin_a],
#         [sin_a, cos_a]
#     ])

#     about = np.array(about)

#     translated = contour - about
#     rotated = (rotation_matrix.T @ translated).T
#     result = rotated + about

#     return result

print(get_area(edg1, edg2, True))

