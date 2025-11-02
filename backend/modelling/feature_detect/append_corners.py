
with open('LABELS_COMBINED.csv') as f:
    for line in f:
        _, x, y, f_name, w, h = line.strip().split(',')
        x = float(x)
        y = float(y)
        w = float(w)
        h = float(h)

        f_name = f_name.replace('.png', '.txt')

        with open(f'dataset/labels/train/{f_name}', 'a') as fa:
            fa.write(f'\n2 {x/w} {y/h} 0.06 0.06')
