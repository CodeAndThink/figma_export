import json
import os
import requests

# ==========================================
# CẤU HÌNH THÔNG TIN FIGMA (Helper functions)
# ==========================================

def extract_file_key(input_file):
    """Trích xuất File Key từ link Figma hoặc trả về chính nó nếu là Key."""
    input_file = input_file.strip()
    if "figma.com" in input_file:
        parts = input_file.split("/")
        if "file" in parts:
            key = parts[parts.index("file") + 1]
        elif "design" in parts:
            key = parts[parts.index("design") + 1]
        else:
            key = input_file
    else:
        key = input_file
    return key.split("?")[0]

def get_cli_config():
    """Lấy cấu hình từ terminal cho CLI mode."""
    token = input("Nhập Figma Personal Access Token: ").strip()
    file_input = input("Nhập Figma File Link hoặc File Key: ").strip()
    file_key = extract_file_key(file_input)
    return token, file_key

# Biến toàn cục mặc định (có thể được ghi đè)
FIGMA_TOKEN = ""
FIGMA_FILE_KEY = ""

# ==========================================

def fetch_figma_data(token=None, file_key=None):
    global FIGMA_TOKEN, FIGMA_FILE_KEY
    
    # Sử dụng tham số nếu được truyền vào, nếu không dùng global
    t = token or FIGMA_TOKEN
    fk = file_key or FIGMA_FILE_KEY
    
    if not t or not fk:
        print("[ERROR] Thieu FIGMA_TOKEN hoac FIGMA_FILE_KEY")
        return
        
    url = f"https://api.figma.com/v1/files/{fk}"
    
    headers = {
        "X-Figma-Token": t
    }

    print(f"[*] Dang tai du lieu tu Figma (File Key: {fk})...")
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        
        # Lưu kết quả ra file JSON bên trong folder screens
        output_dir = "screens"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        output_file = os.path.join(output_dir, "figma_data.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"[SUCCESS] Thanh cong! Du lieu da duoc luu vao file: {output_file}")
        
        # In ra một số thông tin cơ bản
        document_name = data.get("name", "Unknown")
        print(f"[INFO] Ten file Figma: {document_name}")
        
    else:
        print(f"[ERROR] Loi khi tai du lieu: {response.status_code}")
        print(response.text)

def fetch_node_images(node_ids, format="png", scale=1, token=None, file_key=None):
    """
    Lay link anh render tu Figma cho danh sach cac node ID.
    """
    global FIGMA_TOKEN, FIGMA_FILE_KEY
    t = token or FIGMA_TOKEN
    fk = file_key or FIGMA_FILE_KEY

    if not node_ids or not t or not fk:
        return {}

    ids_param = ",".join(node_ids)
    url = f"https://api.figma.com/v1/images/{fk}?ids={ids_param}&format={format}&scale={scale}"
    
    headers = {
        "X-Figma-Token": t
    }

    print(f"[*] Dang lay link anh cho {len(node_ids)} nodes...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get("images", {})
    else:
        print(f"[ERROR] Loi khi lay link anh: {response.status_code}")
        return {}

if __name__ == "__main__":
    token, file_key = get_cli_config()
    fetch_figma_data(token, file_key)
