from puzzlePieceClass import PuzzlePiece  # Replace with your actual module name
import json

with open("piece_data.json", "r") as f:
    data1 = json.load(f)

with open("piece_data2.json", "r") as f:
    data2 = json.load(f)

pieces = []
for item1, item2 in zip(data1, data2):
    piece = PuzzlePiece(
        center=tuple(item1["center"]),
        corners=[tuple(corner) for corner in item1["corners"]],
        image_path=item2["image_path"],  # or however you want to combine them
        edges=[],
        contours = [],
    )
    pieces.append(piece)

# Test it
print(f"Center: {piece.center}")
print(f"Corners: {piece.corners}")
print(f"Number of contour points: {len(piece.contour)}")
print(f"Image path: {piece.image_path}")