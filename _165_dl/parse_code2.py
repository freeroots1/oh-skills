from PIL import Image
import subprocess, sys

img = Image.open('/tmp/code.bmp')
# Convert to grayscale and resize for tesseract
img_gray = img.convert('L')
# Increase size 4x for better OCR
img_big = img_gray.resize((160, 40), Image.LANCZOS)
# Save as PNG
img_big.save('/tmp/code_big.png')

# Try tesseract with different options
result = subprocess.run(['tesseract', '/tmp/code_big.png', 'stdout', '--psm', '8', '-c', 'tessedit_char_whitelist=0123456789'], 
                       capture_output=True, text=True, timeout=10)
print('PSM8:', repr(result.stdout.strip()))

result2 = subprocess.run(['tesseract', '/tmp/code_big.png', 'stdout', '--psm', '7', '-c', 'tessedit_char_whitelist=0123456789'], 
                        capture_output=True, text=True, timeout=10)
print('PSM7:', repr(result2.stdout.strip()))

# Try without whitelist
result3 = subprocess.run(['tesseract', '/tmp/code_big.png', 'stdout', '--psm', '8'], 
                        capture_output=True, text=True, timeout=10)
print('PSM8 nowhite:', repr(result3.stdout.strip()))
