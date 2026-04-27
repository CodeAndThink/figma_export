import json
import os

def draw_screen_ascii(screen_file, width=60):
    if not os.path.exists(screen_file):
        print(f"[ERROR] Khong tim thay file: {screen_file}")
        return

    with open(screen_file, "r", encoding="utf-8") as f:
        screen_data = json.load(f)

    # Lay bounding box cua frame chinh
    main_box = screen_data.get("absoluteBoundingBox", {})
    if not main_box:
        print("[ERROR] Khong tim thay absoluteBoundingBox cho frame.")
        return

    main_x = main_box["x"]
    main_y = main_box["y"]
    main_w = main_box["width"]
    main_h = main_box["height"]

    # Ty le de ve trong terminal (ky tu thuong cao gap doi rong)
    scale_x = width / main_w
    # Ky tu terminal co ty le khoang 2:1 (cao:rong), nen chia 2 cho height
    char_aspect_ratio = 2.0 
    height = int((main_h / main_w) * width / char_aspect_ratio)
    scale_y = height / main_h

    # Tao canvas bang mang 2 chieu
    canvas = [[" " for _ in range(width + 1)] for _ in range(height + 1)]

    def draw_rect(x, y, w, h, label=""):
        # Chuyen doi sang toa do canvas
        start_col = int((x - main_x) * scale_x)
        start_row = int((y - main_y) * scale_y)
        end_col = int((x + w - main_x) * scale_x)
        end_row = int((y + h - main_y) * scale_y)

        # Gioi han trong canvas
        start_col = max(0, min(width, start_col))
        end_col = max(0, min(width, end_col))
        start_row = max(0, min(height, start_row))
        end_row = max(0, min(height, end_row))

        if start_col == end_col or start_row == end_row:
            return

        # Ve cac canh
        for c in range(start_col, end_col + 1):
            canvas[start_row][c] = "-"
            canvas[end_row][c] = "-"
        for r in range(start_row, end_row + 1):
            canvas[r][start_col] = "|"
            canvas[r][end_col] = "|"
        
        # Ve cac goc
        canvas[start_row][start_col] = "+"
        canvas[start_row][end_col] = "+"
        canvas[end_row][start_col] = "+"
        canvas[end_row][end_col] = "+"

        # Ve nhan (label)
        if label:
            label_text = label[:max(0, end_col - start_col - 1)]
            for i, char in enumerate(label_text):
                if start_row + 1 <= end_row:
                    canvas[start_row + 1][start_col + 1 + i] = char

    def traverse(node):
        if node.get("id") != screen_data.get("id"): # Bo qua frame chinh vi se ve sau
            bbox = node.get("absoluteBoundingBox")
            if bbox and node.get("visible", True) is not False:
                # Chi ve cac component co kich thuoc dang ke
                if bbox["width"] > 5 and bbox["height"] > 5:
                    draw_rect(bbox["x"], bbox["y"], bbox["width"], bbox["height"], node.get("name", ""))
        
        for child in node.get("children", []):
            traverse(child)

    # Ve frame chinh truoc
    draw_rect(main_x, main_y, main_w, main_h, screen_data.get("name", "SCREEN"))
    
    # Ve cac con
    traverse(screen_data)

    # In canvas
    print(f"\n--- ASCII PREVIEW: {screen_data.get('name')} ---")
    for row in canvas:
        print("".join(row))
    print("-" * (width + 2))

if __name__ == "__main__":
    import sys
    file_to_preview = "screens/Welcome Screen.json"
    if len(sys.argv) > 1:
        file_to_preview = sys.argv[1]
    
    draw_screen_ascii(file_to_preview)
