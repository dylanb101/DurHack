import numpy as np

# Read and clean the file
with open("points.txt", "r") as f:
    text = f.read()

# Remove brackets and split by commas or newlines
cleaned = text.replace('[', '').replace(']', '').replace('\n', '').split(',')

# Convert to float pairs
numbers = [float(x) for x in cleaned if x.strip() != '']
points = np.array(list(zip(numbers[0::2], numbers[1::2])))

# Save to CSV
np.savetxt("points.csv", points, delimiter=",", header="x,y", comments='')
print(f"Saved {len(points)} points to points.csv")
