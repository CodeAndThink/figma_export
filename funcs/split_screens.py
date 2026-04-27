import json
import os
import re
import requests
from funcs.figma_export import fetch_node_images

def sanitize_filename(name):
    # Thay thế các ký tự không hợp lệ bằng dấu gạch dưới
    return re.sub(r'[\\/*?:"<>|]', "_", name).strip()

def split_figma_screens(input_file="screens/figma_data.json", output_dir="screens"):
    if not os.path.exists(input_file):
        print(f"[ERROR] Khong tim thay file: {input_file}")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"[*] Da tao thu muc: {output_dir}")

    print(f"[*] Dang doc du lieu tu {input_file}...")
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    document = data.get("document", {})
    pages = document.get("children", [])

    count = 0
    screen_info = [] # Luu (node_id, screen_folder) de tai anh sau

    for page in pages:
        page_name = page.get("name", "Unknown Page")
        nodes = page.get("children", [])
        
        print(f"[*] Dang xu ly page: {page_name} ({len(nodes)} nodes)")
        
        for node in nodes:
            if node.get("type") == "FRAME":
                node_id = node.get("id")
                screen_name = node.get("name", f"Unnamed_Screen_{node_id}")
                safe_name = sanitize_filename(screen_name)
                
                # Tao thu muc rieng cho tung man hinh
                screen_folder = os.path.join(output_dir, safe_name)
                if not os.path.exists(screen_folder):
                    os.makedirs(screen_folder)
                
                filepath = os.path.join(screen_folder, "data.json")

                with open(filepath, "w", encoding="utf-8") as out_f:
                    json.dump(node, out_f, ensure_ascii=False, indent=4)
                
                print(f"  [+] Da luu JSON: {safe_name}/data.json")
                screen_info.append((node_id, screen_folder))
                count += 1

    # Tai anh cho tat ca cac screen
    if screen_info:
        print(f"\n[*] Dang tai anh preview cho {len(screen_info)} man hinh...")
        node_ids = [info[0] for info in screen_info]
        image_urls = fetch_node_images(node_ids)
        
        for node_id, folder in screen_info:
            img_url = image_urls.get(node_id)
            if img_url:
                try:
                    img_data = requests.get(img_url).content
                    img_path = os.path.join(folder, "preview.png")
                    with open(img_path, "wb") as img_f:
                        img_f.write(img_data)
                    print(f"  [+] Da tai anh: {os.path.basename(folder)}/preview.png")
                except Exception as e:
                    print(f"  [!] Loi khi tai anh {node_id}: {e}")

    print(f"\n[SUCCESS] Hoan thanh! Da trich xuat {count} screens vao thu muc '{output_dir}'.")

if __name__ == "__main__":
    split_figma_screens()
