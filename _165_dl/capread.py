import struct, sys, subprocess

def read_captcha(filepath):
    with open(filepath, "rb") as f:
        data = f.read()
    # BMP header: 40x10, 24-bit
    w, h = 40, 10
    pixels = []
    for y in range(h-1, -1, -1):
        row = []
        for x in range(w):
            off = 54 + (y*w + x) * 3
            b, g, r = data[off], data[off+1], data[off+2]
            # 非白色/浅灰=前景色
            is_fg = (r < 200 or g < 200 or b < 200)
            row.append(1 if is_fg else 0)
        pixels.append(row)
    
    # 找数字区域(连续有前景像素的列)
    cols_with_fg = []
    for x in range(w):
        if any(pixels[y][x] for y in range(h)):
            cols_with_fg.append(x)
    
    if not cols_with_fg:
        return None
    
    # 分组列
    groups = []
    current = [cols_with_fg[0]]
    for i in range(1, len(cols_with_fg)):
        if cols_with_fg[i] - cols_with_fg[i-1] <= 1:
            current.append(cols_with_fg[i])
        else:
            groups.append(current)
            current = [cols_with_fg[i]]
    groups.append(current)
    
    # 每个组识别数字
    result = ""
    for g in groups:
        if len(g) < 3:
            continue
        x_start, x_end = g[0], g[-1]
        # 简单特征: 统计前景像素
        fg_count = sum(1 for y in range(h) for x in range(x_start, x_end+1) if pixels[y][x])
        # 7段数码管启发式
        top = sum(pixels[0][x] for x in range(x_start, x_end+1))
        mid = sum(pixels[h//2][x] for x in range(x_start, x_end+1))
        bot = sum(pixels[h-1][x] for x in range(x_start, x_end+1))
        left_top = sum(pixels[y][x_start] for y in range(0, h//2))
        left_bot = sum(pixels[y][x_start] for y in range(h//2, h))
        right_top = sum(pixels[y][x_end] for y in range(0, h//2))
        right_bot = sum(pixels[y][x_end] for y in range(h//2, h))
        
        # 简单识别
        # 实际可能需要更复杂的逻辑
        if fg_count < 5:
            continue
        
        # 所有段都有 -> 可能是8
        all_segs = top>0 and mid>0 and bot>0 and left_top>0 and left_bot>0 and right_top>0 and right_bot>0
        # 缺中段 -> 0
        no_mid = top>0 and mid==0 and bot>0 and left_top>0 and left_bot>0 and right_top>0 and right_bot>0
        # 缺左上和右下 -> 2
        no_lt_rb = top>0 and mid>0 and bot>0 and left_top==0 and left_bot>0 and right_top>0 and right_bot==0
        
        if all_segs:
            result += "8"
        elif no_mid:
            result += "0"
        else:
            result += "?"
    
    return result if result else None

# Test
code = read_captcha("/tmp/bj_t1.bmp")
print(f"Detected: {code}")
