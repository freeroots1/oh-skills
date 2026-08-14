from PIL import Image
img = Image.open('/tmp/code.bmp')
print('Size:', img.size)
print('Mode:', img.mode)
pixels = list(img.getdata())
for y in range(10):
    row = ''
    for x in range(40):
        pixel = pixels[y*40 + x]
        if isinstance(pixel, tuple):
            r, g, b = pixel[0], pixel[1], pixel[2]
        else:
            r, g, b = pixel, pixel, pixel
        if r > 200 and g > 200 and b > 200:
            row += ' '
        else:
            row += '#'
    print(row)
