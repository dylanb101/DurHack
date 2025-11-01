import cv2
import numpy as np

img = cv2.imread('C:/Users/TheSi/Desktop/code/DurHack/TheoRandomWork/puzzle_piece.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5,5), 0)
_, thresh = cv2.threshold(blur, 240, 255, cv2.THRESH_BINARY_INV)

kernel = np.ones((5,5), np.uint8)
mask = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

cv2.imshow('Polarized', mask)
cv2.waitKey(0)
cv2.destroyAllWindows()
