import cv2

THRES = 50
MAX_SIZE = 800  # max width or height for display

# Load image in grayscale
img = cv2.imread("img.jpg", cv2.IMREAD_GRAYSCALE)
if img is None:
    raise FileNotFoundError("Could not load image. Check the path.")

# Apply binary threshold
_, img_thresh = cv2.threshold(img, THRES, 255, cv2.THRESH_BINARY)

# Get original dimensions
h, w = img_thresh.shape

# Compute scale to maintain aspect ratio
if w > h:
    scale = MAX_SIZE / w
else:
    scale = MAX_SIZE / h

new_w, new_h = int(w * scale), int(h * scale)

# Resize while keeping aspect ratio
img_resized = cv2.resize(img_thresh, (new_w, new_h))

# Show result
cv2.imshow("Thresholded Image", img_resized)
cv2.waitKey(0)
cv2.destroyAllWindows()
