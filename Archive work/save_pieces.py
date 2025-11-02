import os
import json
import pickle
from typing import List, Dict, Any, Tuple

import numpy as np

from puzzlePieceClass import PuzzlePiece, Edge

def build_piece_from_entry(entry: Dict[str, Any]) -> PuzzlePiece:
    """
    Build a PuzzlePiece from one JSON entry:
    - corners copied verbatim (as tuples)
    - contour set equal to corners
    - center is centroid of corners (or (0,0) if missing)
    - image_path set to images/<file_name> (tries several keys and shapes)
    - edges ignored (empty list)
    """
    corners_raw = entry.get("corners", [])
    corners: List[Tuple[float, float]] = [tuple(map(float, c)) for c in corners_raw]

    contour: List[Tuple[float, float]] = corners.copy()

    if corners:
        arr = np.array(corners, dtype=float)
        center = (float(arr[:, 0].mean()), float(arr[:, 1].mean()))
    else:
        center = (0.0, 0.0)

    def extract_filename(obj: Dict[str, Any]) -> str:
        # common direct keys
        for key in ("file_name", "filename", "image", "file", "name"):
            v = obj.get(key)
            if isinstance(v, str) and v:
                return os.path.basename(v)
            if isinstance(v, dict):
                # nested dict like {"image": {"file_name": "foo.png"}}
                for sub in ("file_name", "filename", "name", "path"):
                    sv = v.get(sub)
                    if isinstance(sv, str) and sv:
                        return os.path.basename(sv)
        # a list of images e.g. "images": [{"file_name": "..."}] or ["img.png"]
        imgs = obj.get("images") or obj.get("image_list")
        if isinstance(imgs, list) and imgs:
            first = imgs[0]
            if isinstance(first, str):
                return os.path.basename(first)
            if isinstance(first, dict):
                for sub in ("file_name", "filename", "name", "path"):
                    sv = first.get(sub)
                    if isinstance(sv, str) and sv:
                        return os.path.basename(sv)
        return ""

    file_name = extract_filename(entry)
    image_path = os.path.join("images", file_name) if file_name else ""

    edges: List[Edge] = []  # ignore edges for now

    return PuzzlePiece(center=center, corners=corners, contour=contour, image_path=image_path, edges=edges)


def load_input_json(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def make_pieces_from_input(input_path: str, n: int = 100) -> List[PuzzlePiece]:
    raw = load_input_json(input_path)
    pieces: List[PuzzlePiece] = [build_piece_from_entry(item) for item in raw]

    def make_dummy(i: int) -> PuzzlePiece:
        contour = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        corners = contour.copy()
        center = (0.5, 0.5)
        return PuzzlePiece(center=center, corners=corners, contour=contour, image_path=f"images/img_dummy_{i}.png", edges=[])

    if len(pieces) < n:
        for i in range(len(pieces), n):
            pieces.append(make_dummy(i))

    return pieces[:n]


def pieces_to_json_serializable(pieces: List[PuzzlePiece]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for p in pieces:
        out.append({
            "center": [float(p.center[0]), float(p.center[1])],
            "corners": [[float(x), float(y)] for x, y in p.corners],
            "contour": [[float(x), float(y)] for x, y in p.contour],
            "image_path": p.image_path,
            "edges": []  # intentionally empty (edges ignored)
        })
    return out


def save_pickle(path: str, pieces: List[PuzzlePiece]) -> None:
    with open(path, "wb") as f:
        pickle.dump(pieces, f)


def save_json(path: str, pieces: List[PuzzlePiece]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(pieces_to_json_serializable(pieces), f, indent=2)


if __name__ == "__main__":
    input_path = r"c:\Users\TheSi\Desktop\code\DurHack\TheoRandomWork\pieces_output.json"
    out_pickle = r"c:\Users\TheSi\Desktop\code\DurHack\pieces_100.pkl"
    out_json = r"c:\Users\TheSi\Desktop\code\DurHack\pieces_100.json"

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input JSON not found: {input_path}")

    pieces = make_pieces_from_input(input_path, n=100)
    save_pickle(out_pickle, pieces)
    save_json(out_json, pieces)
    print(f"Saved {len(pieces)} pieces to:\n  {out_pickle}\n  {out_json}")
    