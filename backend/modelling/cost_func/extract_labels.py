"""
Converts raw MakeSense.ai labels data into usable Numpy array
"""

import json

def convert(f_name_in, f_name_out):
	with open(f_name_in) as f: data = json.load(f)
	data = data[list(data.keys())[0]]['regions']

	output = []

	for region in data.values():
		region = region['shape_attributes']
		x_pts = region['all_points_x']
		y_pts = region['all_points_y']
		pts = list(zip(x_pts, y_pts))
		output.append(pts)

	with open(f_name_out, 'w') as f: json.dump(output, f)

if __name__ == '__main__':
	convert('./data/labels1_raw.json', './data/labels.json')
