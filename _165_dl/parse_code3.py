from PIL import Image
import numpy as np

img = Image.open('/tmp/code.bmp')
pixels = np.array(img)
print('Array shape:', pixels.shape)

# Print as text, marking each pixel color
for y in range(pixels.shape[0]):
    row = ''
    for x in range(pixels.shape[1]):
        r, g, b = pixels[y, x]
        if r > 240 and g > 240 and b > 240:
            row += ' '  # white bg
        elif r < 10 and g < 10 and b < 10:
            row += '#'  # black text
        elif r > 200 and g > 200 and b < 50:
            row += 'Y'  # yellow
        elif r < 50 and g > 150 and b > 200:
            row += 'B'  # blue
        else:
            row += '?'
    print(row)

# Find column-by-column where there are non-white pixels
print()
print('Column analysis (non-white pixel count per column):')
for x in range(pixels.shape[1]):
    count = 0
    for y in range(pixels.shape[0]):
        r, g, b = pixels[y, x]
        if not (r > 240 and g > 240 and b > 240):
            count += 1
    if count > 0:
        print(f'  col {x:2d}: {count} non-white pixels')
