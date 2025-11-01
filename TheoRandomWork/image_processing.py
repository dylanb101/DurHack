import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path

# Parameters
MAX_SIZE = 800
CORNER_RADIUS = 6
BLUR_KERNEL = 15
EPSILON_FRACTION = 0.005

# Folder containing jigsaw piece images
IMAGE_FOLDER = "images"  # Change this to your folder path

def find_four_extreme_corners(corners):
    """
    Find the 4 extreme corners by looking at combinations of min/max x and y.
    """
    if len(corners) < 4:
        print("Warning: Less than 4 corners detected!")
        return corners
    
    x_coords = corners[:, 0]
    y_coords = corners[:, 1]
    
    # Top-left: minimum x+y (closest to origin)
    top_left_idx = np.argmin(x_coords + y_coords)
    top_left = corners[top_left_idx]
    
    # Top-right: maximum x-y
    top_right_idx = np.argmax(x_coords - y_coords)
    top_right = corners[top_right_idx]
    
    # Bottom-left: minimum x-y
    bottom_left_idx = np.argmin(x_coords - y_coords)
    bottom_left = corners[bottom_left_idx]
    
    # Bottom-right: maximum x+y (farthest from origin)
    bottom_right_idx = np.argmax(x_coords + y_coords)
    bottom_right = corners[bottom_right_idx]
    
    return np.array([top_left, top_right, bottom_left, bottom_right])

def process_puzzle_piece(img_path):
    """
    Process a single puzzle piece image and return the result image with corners.
    Returns: (result_image, four_corners, success, error_message)
    """
    # Load image
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None, None, False, "Could not load image"
    
    # Resize for display
    h, w = img.shape
    scale = MAX_SIZE / max(w, h)
    new_w, new_h = int(w * scale), int(h * scale)
    img_resized = cv2.resize(img, (new_w, new_h))
    
    try:
        # Blur to remove pattern
        blurred = cv2.GaussianBlur(img_resized, (BLUR_KERNEL, BLUR_KERNEL), 0)
        
        # Threshold
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations
        kernel = np.ones((5, 5), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=3)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            return None, None, False, "No contours found"
        
        # Get largest contour
        main_contour = max(contours, key=cv2.contourArea)
        perimeter = cv2.arcLength(main_contour, True)
        
        # Douglas-Peucker
        epsilon = EPSILON_FRACTION * perimeter
        approx_contour = cv2.approxPolyDP(main_contour, epsilon, True)
        approx_corners = approx_contour.reshape(-1, 2)
        
        if len(approx_corners) < 4:
            return None, None, False, f"Only {len(approx_corners)} corners found"
        
        # Get 4 extreme corners
        four_corners = find_four_extreme_corners(approx_corners)
        
        # Create result image
        img_result = cv2.cvtColor(img_resized, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(img_result, [approx_contour], -1, (0, 255, 0), 2)
        
        # Draw corners with labels
        corner_labels = ['TL', 'TR', 'BL', 'BR']
        corner_colors = [(255, 0, 255), (0, 255, 255), (255, 128, 0), (128, 255, 0)]
        
        for point, label, color in zip(four_corners, corner_labels, corner_colors):
            cv2.circle(img_result, tuple(point), CORNER_RADIUS + 4, color, -1)
            cv2.circle(img_result, tuple(point), CORNER_RADIUS + 6, (255, 255, 255), 2)
            cv2.putText(img_result, label, tuple(point + 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Convert BGR to RGB for matplotlib
        img_result = cv2.cvtColor(img_result, cv2.COLOR_BGR2RGB)
        
        return img_result, four_corners, True, None
        
    except Exception as e:
        return None, None, False, str(e)

# Get all image files from folder
image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
image_files = []

if os.path.exists(IMAGE_FOLDER):
    for file in os.listdir(IMAGE_FOLDER):
        if Path(file).suffix.lower() in image_extensions:
            image_files.append(os.path.join(IMAGE_FOLDER, file))
else:
    print(f"Folder '{IMAGE_FOLDER}' not found. Looking for images in current directory...")
    for file in os.listdir('.'):
        if Path(file).suffix.lower() in image_extensions:
            image_files.append(file)

if len(image_files) == 0:
    print("No image files found!")
    print(f"Please place images in '{IMAGE_FOLDER}' folder or current directory")
else:
    print(f"Found {len(image_files)} images")
    
    # Process all images
    results = []
    for img_path in image_files:
        print(f"Processing: {os.path.basename(img_path)}...", end=' ')
        result_img, corners, success, error = process_puzzle_piece(img_path)
        
        if success:
            print("✓")
            results.append((os.path.basename(img_path), result_img, corners))
        else:
            print(f"✗ ({error})")
    
    if len(results) == 0:
        print("No images were successfully processed!")
    else:
        # Display results
        num_results = len(results)
        cols = min(3, num_results)  # Max 3 columns
        rows = (num_results + cols - 1) // cols  # Ceiling division
        
        fig, axes = plt.subplots(rows, cols, figsize=(6*cols, 6*rows))
        
        # Handle single image case
        if num_results == 1:
            axes = np.array([axes])
        
        # Flatten axes for easy iteration
        axes_flat = axes.flatten() if num_results > 1 else axes
        
        for idx, (filename, result_img, corners) in enumerate(results):
            ax = axes_flat[idx]
            ax.imshow(result_img)
            ax.set_title(f'{filename}\n4 corners detected', fontsize=10, fontweight='bold')
            ax.axis('off')
        
        # Hide unused subplots
        for idx in range(num_results, len(axes_flat)):
            axes_flat[idx].axis('off')
        
        plt.tight_layout()
        plt.show()
        
        # Print corner coordinates
        print("\n" + "="*70)
        print("CORNER DETECTION RESULTS")
        print("="*70)
        for filename, _, corners in results:
            print(f"\n{filename}:")
            print(f"  Top-Left:     ({corners[0][0]}, {corners[0][1]})")
            print(f"  Top-Right:    ({corners[1][0]}, {corners[1][1]})")
            print(f"  Bottom-Left:  ({corners[2][0]}, {corners[2][1]})")
            print(f"  Bottom-Right: ({corners[3][0]}, {corners[3][1]})")
        print("="*70)