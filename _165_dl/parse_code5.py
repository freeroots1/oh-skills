from PIL import Image

img = Image.open('/tmp/code.bmp')
pixels = list(img.getdata())
w, h = img.size

# Show unique colors
unique_colors = set()
for pixel in pixels:
    if isinstance(pixel, tuple):
        unique_colors.add(pixel)
    else:
        unique_colors.add((pixel, pixel, pixel))

print('Unique colors:')
for c in sorted(unique_colors):
    print(f'  RGB({c[0]:3d},{c[1]:3d},{c[2]:3d})')

# Map each color to a character
color_map = {}
for c in sorted(unique_colors):
    r, g, b = c
    if r > 230 and g > 230 and b > 230:
        color_map[c] = ' '  # near white - background
    elif r < 30 and g < 30 and b < 30:
        color_map[c] = '@'  # near black
    elif r > 200 and g < 100 and b < 100:
        color_map[c] = 'R'  # red-ish
    elif r > 200 and g > 200 and b < 80:
        color_map[c] = 'Y'  # yellow
    elif r < 100 and g > 150 and b > 150:
        color_map[c] = 'C'  # cyan/blue
    else:
        color_map[c] = '?'

print()
print('Color-mapped grid:')
for y in range(h):
    row = ''
    for x in range(w):
        pixel = pixels[y*w + x]
        if isinstance(pixel, tuple):
            row += color_map.get(pixel, '?')
        else:
            row += color_map.get((pixel, pixel, pixel), '?')
    print(row)
