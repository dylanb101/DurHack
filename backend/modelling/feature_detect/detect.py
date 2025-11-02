
import os
import json
from ultralytics import YOLO
from PIL import Image

model = YOLO('jigsaw/corner_detection5/weights/best.pt')

all_pieces = []

for img_path in os.scandir('dataset/images/train/'):
    results = model(img_path.path, conf=0.50, verbose=False)

    corner_count = 0

    img = Image.open(img_path.path)
    width, height = img.size

    piece_data = {
        'file_name': img_path.path.split('/')[-1],
        'features': [],
        'corners': [],
        'piece_centre': (width / 2, height / 2)
    }

    for r in results:
        height, width = r.orig_shape

        for box in r.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().tolist()
            conf = float(box.conf[0])
            class_name = model.names[int(box.cls[0])]

            centre = (
                (x1 + x2) / 2,
                (y1 + y2) / 2
            )

            if class_name == 'Corner':
                corner_count += 1
                piece_data['corners'].append(centre)
            else:
                # Swap class names
                if class_name == 'OUT':
                    class_name = 'IN'
                else:
                    class_name = 'OUT'

                piece_data['features'].append(
                    {
                        'type': class_name,
                        'pt1': (x1, y1),
                        'pt2': (x2, y2),
                        'centre': centre
                    }
                )

        assert corner_count == 4, 'Corner count is not 4'

        # print(json.dumps(piece_data))
        # input()

        all_pieces.append(piece_data)

with open('pieces_output.json', 'w') as f: json.dump(all_pieces, f)
