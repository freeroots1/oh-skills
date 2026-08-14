import struct

samples = []
for i in range(1, 6):
    fname = f"/tmp/sample{i}_1398777.bmp"
    try:
        with open(fname, "rb") as f:
            data = f.read()
        pixels = data[54:]
        row_size = ((40 * 24 + 31) // 32) * 4  # = 124
        chars = []
        for y in range(10):
            row_start = (9 - y) * row_size
            row_chars = ""
            for x in range(40):
                idx = row_start + x * 3
                b, g, r = pixels[idx], pixels[idx+1], pixels[idx+2]
                if (r, g, b) != (0xee, 0xee, 0xee):
                    row_chars += "#"
                else:
                    row_chars += "."
            chars.append(row_chars)
        print(f"=== Sample {i} ===")
        for row in chars:
            print(row)
        samples.append(chars)
    except Exception as e:
        print(f"Error reading sample {i}: {e}")
