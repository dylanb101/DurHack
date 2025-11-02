import numpy as np
from scipy.spatial.distance import directed_hausdorff
from scipy.interpolate import interp1d
from concurrent.futures import ProcessPoolExecutor
import json

# === Configuration ===
DISTANCE_THRESHOLD = 0.15  # Maximum distance for a valid match
NUM_SAMPLE_POINTS = 100    # Resample edges to this many points for comparison
PARALLEL_WORKERS = None    # None = use all CPU cores

# === Edge Type Compatibility ===
COMPATIBLE_EDGES = {
    ('tab', 'blank'),
    ('blank', 'tab'),
    ('flat', 'flat')
}

def is_compatible(edge_type1, edge_type2):
    """Check if two edge types can connect."""
    return (edge_type1, edge_type2) in COMPATIBLE_EDGES


# === Edge Extraction ===
def find_closest_contour_index(point, contour):
    """Find index of contour point closest to given point."""
    distances = np.sqrt(((contour - point)**2).sum(axis=1))
    return np.argmin(distances)


def extract_edge_curves(contour, corners):
    """
    Extract 4 edge curves from contour using corner coordinates.
    Returns edges in order: [top, right, bottom, left]
    """
    contour = np.array(contour)
    corners = np.array(corners)
    
    # Find nearest contour indices for each corner
    corner_indices = [find_closest_contour_index(corner, contour) for corner in corners]
    
    # Extract edges between consecutive corners
    edges = []
    for i in range(4):
        start_idx = corner_indices[i]
        end_idx = corner_indices[(i + 1) % 4]
        
        if end_idx > start_idx:
            edge = contour[start_idx:end_idx + 1]
        else:  # Handle wraparound
            edge = np.vstack([contour[start_idx:], contour[:end_idx + 1]])
        
        edges.append(edge)
    
    return edges


# === Edge Normalization ===
def resample_edge(edge, num_points=NUM_SAMPLE_POINTS):
    """
    Resample edge to fixed number of points using interpolation.
    This normalizes edges of different lengths for comparison.
    """
    if len(edge) < 2:
        raise ValueError("Edge must have at least 2 points")
    
    # Compute cumulative arc length
    distances = np.sqrt(((np.diff(edge, axis=0))**2).sum(axis=1))
    cumulative_dist = np.concatenate([[0], np.cumsum(distances)])
    
    # Create interpolation functions for x and y
    interp_x = interp1d(cumulative_dist, edge[:, 0], kind='linear')
    interp_y = interp1d(cumulative_dist, edge[:, 1], kind='linear')
    
    # Sample at evenly spaced points along the curve
    sample_distances = np.linspace(0, cumulative_dist[-1], num_points)
    resampled = np.column_stack([interp_x(sample_distances), interp_y(sample_distances)])
    
    return resampled


def normalize_edge_for_matching(edge):
    """
    Normalize edge: resample, center, and scale.
    """
    # Resample to fixed number of points
    edge = resample_edge(edge)
    
    # Center the edge
    centroid = edge.mean(axis=0)
    centered = edge - centroid
    
    # Scale by max distance from center
    max_dist = np.sqrt((centered**2).sum(axis=1)).max()
    if max_dist > 1e-6:
        normalized = centered / max_dist
    else:
        normalized = centered
    
    return normalized


# === Edge Matching ===
def flip_edge_horizontal(edge):
    """Flip edge horizontally (for matching tab with blank)."""
    flipped = edge.copy()
    flipped[:, 0] = -flipped[:, 0]
    return flipped


def reverse_edge_direction(edge):
    """Reverse the direction of an edge."""
    return edge[::-1]


def compute_edge_distance(edge1, edge2):
    """
    Compute distance between two edges using Hausdorff distance.
    Returns the symmetric Hausdorff distance.
    """
    d1 = directed_hausdorff(edge1, edge2)[0]
    d2 = directed_hausdorff(edge2, edge1)[0]
    return max(d1, d2)


def match_edges(edge1, edge2, type1, type2):
    """
    Match two edges and return distance score.
    Handles flipping and reversing as needed.
    """
    # Normalize both edges
    norm_edge1 = normalize_edge_for_matching(edge1)
    norm_edge2 = normalize_edge_for_matching(edge2)
    
    # For tab-blank matching, flip one edge (they should be inverse)
    if (type1 == 'tab' and type2 == 'blank') or (type1 == 'blank' and type2 == 'tab'):
        norm_edge2 = flip_edge_horizontal(norm_edge2)
    
    # Try both orientations (forward and reversed)
    dist_forward = compute_edge_distance(norm_edge1, norm_edge2)
    dist_reversed = compute_edge_distance(norm_edge1, reverse_edge_direction(norm_edge2))
    
    return min(dist_forward, dist_reversed)


# === Piece Processing ===
def preprocess_piece(piece):
    """
    Preprocess a piece: extract and normalize edge curves.
    Returns piece with added 'edge_curves' field.
    """
    contour = np.array(piece['contour'])
    corners = piece['corners']
    
    # Extract 4 edges
    edge_curves = extract_edge_curves(contour, corners)
    
    piece['edge_curves'] = edge_curves
    return piece


# === Main Matching Logic ===
def find_matches_for_pair(args):
    """
    Worker function to find matches between two pieces.
    Tests all compatible edge combinations.
    """
    piece1, piece2 = args
    matches = []
    
    edge_names = ['top', 'right', 'bottom', 'left']
    
    # Test all edge combinations
    for i, edge1_name in enumerate(edge_names):
        edge1_type = piece1['edges'][i]
        edge1_curve = piece1['edge_curves'][i]
        
        for j, edge2_name in enumerate(edge_names):
            edge2_type = piece2['edges'][j]
            edge2_curve = piece2['edge_curves'][j]
            
            # Skip if edge types are incompatible
            if not is_compatible(edge1_type, edge2_type):
                continue
            
            # Skip if either edge is too short
            if len(edge1_curve) < 2 or len(edge2_curve) < 2:
                continue
            
            try:
                # Compute match distance
                distance = match_edges(edge1_curve, edge2_curve, edge1_type, edge2_type)
                
                # If distance is below threshold, it's a match
                if distance < DISTANCE_THRESHOLD:
                    confidence = 1.0 - (distance / DISTANCE_THRESHOLD)
                    matches.append({
                        'piece1_id': piece1['id'],
                        'piece2_id': piece2['id'],
                        'piece1_edge': edge1_name,
                        'piece2_edge': edge2_name,
                        'distance': float(distance),
                        'confidence': float(confidence)
                    })
            except Exception as e:
                # Skip this edge pair if there's an error
                print(f"Warning: Error matching {piece1['id']}.{edge1_name} with {piece2['id']}.{edge2_name}: {e}")
                continue
    
    return matches


def find_all_matches(pieces, parallel=True):
    """
    Find all matching edges between all pieces.
    
    Args:
        pieces: List of piece dictionaries
        parallel: Use parallel processing
    
    Returns:
        List of match dictionaries sorted by confidence
    """
    print(f"Preprocessing {len(pieces)} pieces...")
    
    # Preprocess all pieces to extract edge curves
    for i, piece in enumerate(pieces):
        try:
            pieces[i] = preprocess_piece(piece)
        except Exception as e:
            print(f"Error preprocessing piece {piece.get('id', i)}: {e}")
            continue
    
    print(f"Finding matches between {len(pieces)} pieces...")
    
    # Generate all unique pairs
    pairs = []
    for i in range(len(pieces)):
        for j in range(i + 1, len(pieces)):
            pairs.append((pieces[i], pieces[j]))
    
    print(f"Testing {len(pairs)} piece pairs...")
    
    all_matches = []
    
    if parallel and len(pairs) > 10:
        # Parallel processing for large datasets
        with ProcessPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
            results = list(executor.map(find_matches_for_pair, pairs))
        
        # Flatten results
        for matches in results:
            all_matches.extend(matches)
    else:
        # Sequential processing for small datasets
        for i, pair in enumerate(pairs):
            matches = find_matches_for_pair(pair)
            all_matches.extend(matches)
            
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(pairs)} pairs...")
    
    # Sort by confidence (highest first)
    all_matches.sort(key=lambda x: x['confidence'], reverse=True)
    
    return all_matches


# === Output Functions ===
def save_matches_to_file(matches, filename='puzzle_matches.json'):
    """Save matches to JSON file."""
    with open(filename, 'w') as f:
        json.dump(matches, f, indent=2)
    print(f"Saved {len(matches)} matches to {filename}")


def print_match_summary(matches, top_n=10):
    """Print summary of top matches."""
    print(f"\n{'='*70}")
    print(f"Found {len(matches)} potential matches")
    print(f"{'='*70}\n")
    
    if matches:
        print(f"Top {min(top_n, len(matches))} matches:\n")
        for i, match in enumerate(matches[:top_n], 1):
            print(f"{i}. {match['piece1_id']}.{match['piece1_edge']} ↔ "
                  f"{match['piece2_id']}.{match['piece2_edge']}")
            print(f"   Confidence: {match['confidence']:.2%} | Distance: {match['distance']:.4f}\n")


# === Example Usage ===
if __name__ == "__main__":
    # Example: Create sample pieces (replace with your actual data)
    sample_pieces = [
        {
            'id': 'piece_01',
            'corners': [(0, 0), (100, 0), (100, 100), (0, 100)],
            'center': (50, 50),
            'edges': ['flat', 'tab', 'blank', 'flat'],
            'contour': [(0, 0), (25, 0), (50, -10), (75, 0), (100, 0),
                       (100, 25), (110, 50), (100, 75), (100, 100),
                       (75, 100), (50, 100), (25, 100), (0, 100),
                       (0, 75), (0, 50), (0, 25)]
        },
        {
            'id': 'piece_02',
            'corners': [(100, 0), (200, 0), (200, 100), (100, 100)],
            'center': (150, 50),
            'edges': ['flat', 'flat', 'tab', 'blank'],
            'contour': [(100, 0), (150, 0), (200, 0), (200, 25), (200, 50),
                       (200, 75), (200, 100), (175, 100), (150, 110), (125, 100),
                       (100, 100), (100, 75), (90, 50), (100, 25)]
        }
    ]
    
    # Find matches
    matches = find_all_matches(sample_pieces, parallel=False)
    
    # Display results
    print_match_summary(matches)
    
    # Save to file
    save_matches_to_file(matches)
    
    print("\nTo use with your data:")
    print("1. Load your pieces into the same dictionary format")
    print("2. Call: matches = find_all_matches(your_pieces)")
    print("3. Adjust DISTANCE_THRESHOLD if needed (lower = stricter)")