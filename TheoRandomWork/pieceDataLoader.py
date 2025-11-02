from puzzlePieceClass import PuzzlePiece
import json

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
        
        all_edges.append(curr_edge)

    # --------------------------------------
    # import matplotlib.pyplot as plt

    # fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    # axes = axes.flatten()

    # for i, edge in enumerate(all_edges):
    #     # Extract x and y coordinates
    #     x_coords = [point[0] for point in edge]
    #     y_coords = [point[1] for point in edge]
        
    #     # Plot on the corresponding subplot
    #     axes[i].plot(x_coords, y_coords, 'b-', linewidth=2)
    #     axes[i].scatter(x_coords[0], y_coords[0], c='green', s=100, zorder=5, label='Start')
    #     axes[i].scatter(x_coords[-1], y_coords[-1], c='red', s=100, zorder=5, label='End')
    #     axes[i].set_title(f'Edge {i+1}')
    #     axes[i].set_aspect('equal')
    #     axes[i].legend()
    #     axes[i].grid(True, alpha=0.3)

    # plt.tight_layout()
    # plt.show()
    # --------------------------------------

    piece = PuzzlePiece(
        centre=tuple(item1["piece_centre"]),
        corners=corners,
        image_path=item2["file_name"],
        edges=[],
        contour=contour,
    )
    pieces.append(piece)

print(len(pieces))
