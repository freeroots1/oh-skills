from PIL import Image

img = Image.open('/tmp/code.bmp')
pixels = list(img.getdata())
w, h = img.size

# Print column analysis
print('Column analysis:')
for x in range(w):
    count = 0
    colors = set()
    for y in range(h):
        pixel = pixels[y*w + x]
        if isinstance(pixel, tuple):
            r, g, b = pixel
        else:
            r, g, b = pixel, pixel, pixel
        if not (r > 240 and g > 240 and b > 240):
            count += 1
    if count > 0:
        print(f'  col {x:2d}: {count} px')

# Print the image chars per column segment
# Let me try to figure out each character
# Print with more detail
print()
print('Full pixel grid (B=black, Y=yellow, .=white):')
for y in range(h):
    row = ''
    for x in range(w):
        pixel = pixels[y*w + x]
        if isinstance(pixel, tuple):
            r, g, b = pixel
        else:
            r, g, b = pixel, pixel, pixel
        if r > 240 and g > 240 and b > 240:
            row += '.'
        elif r < 20 and g < 20 and b < 20:
            row += 'B'
        elif r > 200 and g > 200 and b < 50:
            row += 'Y'
        elif r < 80 and g > 150 and b > 200:
            row += 'C'
        else:
            row += '?'
    print(row)
