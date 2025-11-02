import os
import cv2
import numpy as np
import json

GREY_THRES = 50
AREA_MIN = 10_000
AREA_MAX = 10_000_000

COMPONENT_PADDING = 30

TOT_IMGS = 0
output_contours_data = []

def decompose_photo(img_name):
    global TOT_IMGS


    img = cv2.imread(img_name)
    _, img = cv2.threshold(
        img,
        GREY_THRES,
        255,
        cv2.THRESH_BINARY
    )
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(img, connectivity=8)

    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area > AREA_MIN and area < AREA_MAX:
            x = stats[i, cv2.CC_STAT_LEFT]
            y = stats[i, cv2.CC_STAT_TOP]
            w = stats[i, cv2.CC_STAT_WIDTH]
            h = stats[i, cv2.CC_STAT_HEIGHT]

            component_mask = (labels[y:y+h, x:x+w] == i).astype(np.uint8) * 255

            component_mask = cv2.copyMakeBorder(
                component_mask,
                COMPONENT_PADDING,
                COMPONENT_PADDING,
                COMPONENT_PADDING,
                COMPONENT_PADDING,
                cv2.BORDER_CONSTANT,
                value=0
            )

            # Export the puzzle piece
            f_name = f'output_{TOT_IMGS:02d}.png'
            cv2.imwrite(f'output/{f_name}', component_mask)

            contours, _ = cv2.findContours(component_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            assert len(contours) == 1

            output_contours_data.append({
                'file_name': f_name,
                'contours': contours[0].squeeze().tolist()
            })

            outline = np.zeros_like(component_mask)
            cv2.drawContours(outline, contours, -1, 255, 1)
            cv2.imwrite(f'output_contours/output_{TOT_IMGS:02d}.png', outline)

            TOT_IMGS += 1

            # disp = cv2.resize(outline, (800, 600))
            # cv2.imshow(f'component_{i}.png', disp)

# img = cv2.resize(img, (800, 600))
# cv2.imshow("Image Window", img)

if __name__ == '__main__':
    for fname in os.listdir('./input_scans/'):
        decompose_photo('input_scans/' + fname)

    print(len(output_contours_data))
    with open('contour_data.json', 'w') as f: json.dump(output_contours_data, f)

# cv2.waitKey(0)
# cv2.destroyAllWindows()
