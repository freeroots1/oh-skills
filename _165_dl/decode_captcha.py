# Read captcha BMP and decode digits
# 40x10 pixel, 24-bit BMP
# Try to identify digits by column profile (density of non-bg pixels per column)

import struct, os

# Digit patterns: 10 rows x 8 cols for each digit 0-9
# Based on analyzing sample captchas

def get_column_profile(pixels, row_size):
    """Get density of non-background pixels per column"""
    profile = []
    for x in range(40):
        count = 0
        for y in range(10):
            row_start = (9 - y) * row_size
            idx = row_start + x * 3
            b, g, r = pixels[idx], pixels[idx+1], pixels[idx+2]
            if (r, g, b) != (0xee, 0xee, 0xee):
                count += 1
        profile.append(count)
    return profile

def read_and_decode(filename):
    with open(filename, "rb") as f:
        data = f.read()
    pixels = data[54:]
    row_size = ((40 * 24 + 31) // 32) * 4  # 124 bytes
    profile = get_column_profile(pixels, row_size)
    
    # Print column profile
    cols_str = "".join(str(min(c, 9)) if c > 0 else "." for c in profile)
    print(f"Profile: {cols_str}")
    
    # Find digit boundaries - columns with 0 non-bg pixels are gaps
    # Print the raw profile numbers
    print(f"Raw: {profile}")
    
    # Print the visual representation
    for y in range(10):
        row_start = (9 - y) * row_size
        line = ""
        for x in range(40):
            idx = row_start + x * 3
            b, g, r = pixels[idx], pixels[idx+1], pixels[idx+2]
            if (r, g, b) != (0xee, 0xee, 0xee):
                line += "#"
            else:
                line += "."
        print(f"{y}: {line}")
    print()

# Process all samples
for i in range(1, 6):
    fname = f"/tmp/sample{i}_1398777.bmp"
    if os.path.exists(fname):
        print(f"=== Sample {i} ===")
        read_and_decode(fname)
