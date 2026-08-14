from PIL import Image
import sys

# Known digit patterns (10 rows each, trimmed to content)
PATTERNS = {}

# 0 - full rectangle
PATTERNS[0] = [
    " #### ",
    "#    #",
    "#    #",
    "#    #",
    "#    #",
    "#    #",
    "#    #",
    "#    #",
    "#    #",
    " #### "
]

# 1 - vertical line, serif at top and bottom  
PATTERNS[1] = [
    "  #  ",
    " ##  ",
    "  #  ",
    "  #  ",
    "  #  ",
    "  #  ",
    "  #  ",
    "  #  ",
    "  #  ",
    "#####"
]

# 2 - top bar, right, diagonal, bottom bar
PATTERNS[2] = [
    " #### ",
    "#    #",
    "     #",
    "     #",
    "    # ",
    "   #  ",
    "  #   ",
    " #    ",
    "#     ",
    "######"
]

# 3 - top bar, upper right, middle bar, lower right, bottom bar
PATTERNS[3] = [
    " #### ",
    "#    #",
    "     #",
    "     #",
    "  ### ",
    "     #",
    "     #",
    "     #",
    "#    #",
    " #### "
]

# 4 - vertical line, cross, vertical
PATTERNS[4] = [
    "    # ",
    "   ## ",
    "  # # ",
    "  # # ",
    " #  # ",
    "#   # ",
    "######",
    "    # ",
    "    # ",
    "   ###"
]

# 5 - top bar, left, middle bar, right, bottom bar
PATTERNS[5] = [
    "######",
    "#     ",
    "#     ",
    "#     ",
    "##### ",
    "     #",
    "     #",
    "     #",
    "#    #",
    " #### "
]

# 6 - 
PATTERNS[6] = [
    " #### ",
    "#    #",
    "#     ",
    "#     ",
    "####  ",
    "#    #",
    "#    #",
    "#    #",
    "#    #",
    " #### "
]

# 7 - top bar, diagonal
PATTERNS[7] = [
    "######",
    "#    #",
    "    # ",
    "    # ",
    "   #  ",
    "   #  ",
    "  #   ",
    "  #   ",
    " #    ",
    " #    "
]

# 8 - two circles
PATTERNS[8] = [
    " #### ",
    "#    #",
    "#    #",
    "#    #",
    " #### ",
    "#    #",
    "#    #",
    "#    #",
    "#    #",
    " #### "
]

# 9 - 
PATTERNS[9] = [
    " #### ",
    "#    #",
    "#    #",
    "#    #",
    " #### ",
    "     #",
    "     #",
    "     #",
    "#    #",
    " #### "
]

def compare_pattern(ch_lines, pattern_idx):
    """Compare extracted character lines against a known pattern"""
    pattern = PATTERNS[pattern_idx]
    
    # Normalize - trim empty columns and rows
    def trim(lines):
        # Find first and last non-empty row
        first_row = 0
        last_row = len(lines) - 1
        while first_row < len(lines) and all(c ==   for c in lines[first_row]):
            first_row += 1
        while last_row >= 0 and all(c ==   for c in lines[last_row]):
            last_row -= 1
        
        # Find first and last non-empty column
        if first_row <= last_row:
            first_col = len(lines[0])
            last_col = 0
            for r in range(first_row, last_row+1):
                for c, ch in enumerate(lines[r]):
                    if ch !=  :
                        first_col = min(first_col, c)
                        last_col = max(last_col, c)
        else:
            return 999
        
        trimmed = [row[first_col:last_col+1] for row in lines[first_row:last_row+1]]
        return trimmed
    
    t_ch = trim(ch_lines)
    t_pat = trim(pattern)
    
    if not t_ch or not t_pat:
        return 999
    
    # Compare by resizing to same dimensions
    # Simple approach: compare character by character after normalization
    ch_h, ch_w = len(t_ch), len(t_ch[0])
    pat_h, pat_w = len(t_pat), len(t_pat[0])
    
    if abs(ch_h - pat_h) > 2 or abs(ch_w - pat_w) > 2:
        return 999
    
    # Simple pixel match
    matches = 0
    total = 0
    for r in range(min(ch_h, pat_h)):
        for c in range(min(ch_w, pat_w)):
            total += 1
            ch_pixel = (t_ch[r][c] if c < len(t_ch[r]) else  ) 
            pat_pixel = (t_pat[r][c] if c < len(t_pat[r]) else  )
            if ch_pixel == pat_pixel:
                matches += 1
    
    # Score as percentage
    if total == 0:
        return 999
    return (1 - matches / total) * 100

def recognize_digit(lines):
    """Recognize a single digit from 10 lines of text"""
    best_score = 999
    best_digit = -1
    for d in range(10):
        score = compare_pattern(lines, d)
        if score < best_score:
            best_score = score
            best_digit = d
    return best_digit, best_score

def solve_captcha(img_path):
    """Solve captcha image file"""
    img = Image.open(img_path)
    px = list(img.getdata())
    bg = (238,238,238)
    w, h = 40, 10
    
    # Find non-background colors
    colors = {}
    for p in px:
        if isinstance(p, tuple) and p != bg and p not in colors:
            colors[p] = len(colors)
    
    result = []
    for c in sorted(colors.keys()):
        min_x, max_x = w, 0
        min_y, max_y = h, 0
        for y in range(h):
            for x in range(w):
                p = px[y*w+x]
                v = p if isinstance(p, tuple) else (p,p,p)
                if v == c:
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
        
        # Extract character as lines
        lines = []
        for y2 in range(min_y, max_y+1):
            line = ""
            for x2 in range(min_x, max_x+1):
                p = px[y2*w+x2]
                v = p if isinstance(p, tuple) else (p,p,p)
                line += "#" if v == c else " "
            lines.append(line)
        
        digit, score = recognize_digit(lines)
        result.append((min_x, digit, score))
    
    # Sort by x position
    result.sort(key=lambda x: x[0])
    code = "".join(str(d[1]) for d in result)
    
    # Debug
    for r in result:
        print(f"  x={r[0]}: digit={r[1]} score={r[2]:.1f}", file=sys.stderr)
    
    return code

if __name__ == "__main__":
    code = solve_captcha(sys.argv[1])
    print(f"CODE:{code}")
