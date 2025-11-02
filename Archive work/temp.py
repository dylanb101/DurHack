import cv2
import numpy as np

def detect_puzzle_corners(image_path):
    """
    Returns: Array of 4 corner coordinates in clockwise order from top-left
    Returns None if detection fails
    """
    # Config
    max_size = 800
    blur_size = 15
    epsilon_frac = 0.005
    erode_size = 10
    erode_iters = 2
    min_angle = 70
    max_angle = 110
    min_dist = 50
    
    def calc_angle(p1, p2, p3):
        # angle at p2
        v1 = p1 - p2
        v2 = p3 - p2
        cos_ang = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
        cos_ang = np.clip(cos_ang, -1.0, 1.0)
        return np.degrees(np.arccos(cos_ang))
    
    def valid_corner(pts, idx):
        # check if corner is ~90 degrees
        n = len(pts)
        if n < 3:
            return True
        
        prev = (idx - 1) % n
        nxt = (idx + 1) % n
        
        ang = calc_angle(pts[prev], pts[idx], pts[nxt])
        return min_angle <= ang <= max_angle
    
    def filter_corners(contour):
        # keep only corners near 90 deg
        pts = contour.reshape(-1, 2)
        good = []
        
        for i in range(len(pts)):
            if valid_corner(pts, i):
                good.append(pts[i])
        
        return np.array(good) if good else pts
    
    def get_four_corners(pts):
        # find 4 extreme corners
        if len(pts) < 4:
            return None
        
        x = pts[:, 0]
        y = pts[:, 1]
        
        tl = pts[np.argmin(x + y)]
        tr = pts[np.argmax(x - y)]
        bl = pts[np.argmin(x - y)]
        br = pts[np.argmax(x + y)]
        
        corners = np.array([tl, tr, bl, br])
        
        # check they're not too close together
        unique = []
        for c in corners:
            ok = True
            for u in unique:
                if np.linalg.norm(c - u) < min_dist:
                    ok = False
                    break
            if ok:
                unique.append(c)
        
        if len(unique) < 4:
            return None
        
        return corners
    
    # load image
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    
    # resize for processing
    h, w = img.shape
    scale = max_size / max(w, h)
    new_w, new_h = int(w * scale), int(h * scale)
    img_small = cv2.resize(img, (new_w, new_h))
    
    try:
        # blur out the puzzle pattern
        blurred = cv2.GaussianBlur(img_small, (blur_size, blur_size), 0)
        
        # threshold
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # clean up with morphology
        kern = np.ones((5, 5), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kern, iterations=3)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kern, iterations=2)
        
        # erode to get rid of tabs
        erode_kern = np.ones((erode_size, erode_size), np.uint8)
        eroded = cv2.erode(binary, erode_kern, iterations=erode_iters)
        
        # dilate back to original size
        restored = cv2.dilate(eroded, erode_kern, iterations=erode_iters)
        
        # find contours
        contours, _ = cv2.findContours(restored, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # get biggest contour
        main = max(contours, key=cv2.contourArea)
        perim = cv2.arcLength(main, True)
        
        # simplify contour
        eps = epsilon_frac * perim
        approx = cv2.approxPolyDP(main, eps, True)
        
        # filter out tab corners by angle
        good_corners = filter_corners(approx)
        
        if len(good_corners) < 4:
            return None
        
        # pick the 4 main corners
        four = get_four_corners(good_corners)
        
        if four is None:
            return None
        
        # scale back to original size
        four = four / scale
        
        # reorder clockwise from top-left
        clockwise = np.array([
            four[0],  # TL
            four[1],  # TR
            four[3],  # BR
            four[2]   # BL
        ])
        
        return clockwise
        
    except:
        return None