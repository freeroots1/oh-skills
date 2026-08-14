from PIL import Image

img = Image.open('/tmp/code.bmp')
pixels = list(img.getdata())
w, h = img.size

colors = {
    (138, 75, 0): '1',
    (162, 0, 99): '2',
    (162, 88, 0): '3',
    (199, 37, 0): '4',
    (238,238,238): '.'
}

print('By color:')
for y in range(h):
    row = ''
    for x in range(w):
        pixel = pixels[y*w + x]
        if isinstance(pixel, tuple):
            row += colors.get(pixel, '?')
        else:
            row += colors.get((pixel, pixel, pixel), '?')
    print(row)

print()
print('Character 1 (brown - color code 1):')
for y in range(h):
    row = ''
    for x in range(w):
        pixel = pixels[y*w + x]
        p = pixel if isinstance(pixel, tuple) else (pixel, pixel, pixel)
        if p == (138, 75, 0):
            row += '#'
        else:
            row += ' '
    print(f'  {row}')

print()
print('Character 2 (magenta - color code 2):')
for y in range(h):
    row = ''
    for x in range(w):
        pixel = pixels[y*w + x]
        p = pixel if isinstance(pixel, tuple) else (pixel, pixel, pixel)
        if p == (162, 0, 99):
            row += '#'
        else:
            row += ' '
    print(f'  {row}')

print()
print('Character 3 (brown2 - color code 3):')
for y in range(h):
    row = ''
    for x in range(w):
        pixel = pixels[y*w + x]
        p = pixel if isinstance(pixel, tuple) else (pixel, pixel, pixel)
        if p == (162, 88, 0):
            row += '#'
        else:
            row += ' '
    print(f'  {row}')

print()
print('Character 4 (red - color code 4):')
for y in range(h):
    row = ''
    for x in range(w):
        pixel = pixels[y*w + x]
        p = pixel if isinstance(pixel, tuple) else (pixel, pixel, pixel)
        if p == (199, 37, 0):
            row += '#'
        else:
            row += ' '
    print(f'  {row}')
