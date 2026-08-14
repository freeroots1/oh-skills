from PIL import Image
import subprocess, os

def get_code_and_ocr():
    # Fetch a fresh code
    subprocess.run(['curl', '-s', 'http://bjhzsv.com/main/inc/code.asp', 
                   '--cookie-jar', '/tmp/code_c.jar', '--output', '/tmp/code7.bmp'], 
                   capture_output=True)
    
    img = Image.open('/tmp/code7.bmp')
    pixels = list(img.getdata())
    w, h = img.size
    
    # Get unique non-bg colors
    bg = (238,238,238)
    colors = {}
    for pixel in pixels:
        if isinstance(pixel, tuple):
            if pixel != bg and pixel not in colors:
                colors[pixel] = len(colors) + 1
        else:
            p = (pixel, pixel, pixel)
            if p != bg and p not in colors:
                colors[p] = len(colors) + 1
    
    # Extract each character by color
    chars = {}
    for pixel_val, idx in colors.items():
        min_x, max_x = w, 0
        min_y, max_y = h, 0
        for y in range(h):
            for x in range(w):
                p = pixels[y*w + x]
                if isinstance(p, tuple):
                    v = p
                else:
                    v = (p, p, p)
                if v == pixel_val:
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
        
        # Extract just this character
        char_w = max_x - min_x + 1
        char_h = max_y - min_y + 1
        char_img = Image.new('L', (char_w, char_h), 255)
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                p = pixels[y*w + x]
                if isinstance(p, tuple):
                    v = p
                else:
                    v = (p, p, p)
                if v == pixel_val:
                    char_img.putpixel((x - min_x, y - min_y), 0)
        
        # Save and OCR
        fname = f'/tmp/char_{idx}_{min_x}.png'
        char_img.save(fname)
        result = subprocess.run(['tesseract', fname, 'stdout', '--psm', '10', 
                                '-c', 'tessedit_char_whitelist=0123456789'], 
                               capture_output=True, text=True, timeout=10)
        ocr = result.stdout.strip()
        
        # Also print as text
        print(f'Character {idx} at x={min_x}-{max_x} OCR=[{ocr}]:')
        for cy in range(char_h):
            row = ''
            for cx in range(char_w):
                if char_img.getpixel((cx, cy)) == 0:
                    row += '#'
                else:
                    row += ' '
            print(f'  |{row}|')
        print()
        
        chars[min_x] = (idx, ocr)
    
    # Sort by x position
    sorted_chars = ''.join(chars[x][1] for x in sorted(chars.keys()))
    print(f'Combined OCR: {sorted_chars}')
    return sorted_chars

get_code_and_ocr()
