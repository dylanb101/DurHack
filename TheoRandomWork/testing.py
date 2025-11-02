import os
import cv2
import matplotlib.pyplot as plt
from image_processing import detect_puzzle_corners
import numpy as np
import math

def process_and_display_images(directory_path, cols=2, rows=2):
    # Number of images per page
    images_per_page = cols * rows

    # Collect all image files
    image_files = sorted([
        f for f in os.listdir(directory_path)
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ])

    # Preprocess all images once
    processed_images = []
    titles = []

    for image_file in image_files:
        image_path = os.path.join(directory_path, image_file)
        corners = detect_puzzle_corners(image_path)

        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        if corners is not None:
            colors = [(255, 0, 255), (0, 255, 255), (0, 255, 0), (255, 128, 0)]
            labels = ['TL', 'TR', 'BR', 'BL']
            for corner, color, label in zip(corners, colors, labels):
                x, y = map(int, corner)
                cv2.circle(img, (x, y), 8, color, -1)
                cv2.putText(img, label, (x + 10, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            titles.append(image_file)
        else:
            titles.append(f"{image_file}\n(no corners)")
            print(f"❌ Failed to detect corners in {image_file}")

        processed_images.append(img)

    total_images = len(processed_images)
    total_pages = math.ceil(total_images / images_per_page)
    current_page = 0

    while True:
        start_idx = current_page * images_per_page
        end_idx = min(start_idx + images_per_page, total_images)
        batch_images = processed_images[start_idx:end_idx]
        batch_titles = titles[start_idx:end_idx]

        # Display the current page
        fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 4 * rows))
        axes = axes.flatten()

        for i, ax in enumerate(axes):
            if i < len(batch_images):
                ax.imshow(batch_images[i])
                ax.set_title(batch_titles[i], fontsize=9)
                ax.axis('off')
            else:
                ax.axis('off')

        plt.tight_layout()
        plt.show(block=False)
        print(f"\nShowing page {current_page + 1}/{total_pages} "
              f"({start_idx + 1}–{end_idx} of {total_images})")
        print("Press [n] for next, [p] for previous, [q] to quit.")
        key = input("👉 Your choice: ").strip().lower()

        plt.close()

        if key == 'n':
            if current_page < total_pages - 1:
                current_page += 1
            else:
                print("✅ End of images.")
                break
        elif key == 'p':
            if current_page > 0:
                current_page -= 1
            else:
                print("🚫 Already at the first page.")
        elif key == 'q':
            print("👋 Exiting viewer.")
            break
        else:
            print("⚠️ Invalid input. Use 'n', 'p', or 'q'.")

# ✅ Path to your images folder
directory_path = 'images'

# Show 10 images at a time (5×2 grid)
process_and_display_images(directory_path, cols=2, rows=2)
