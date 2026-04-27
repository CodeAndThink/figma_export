import json
import os
import requests

# ==========================================
# CẤU HÌNH THÔNG TIN FIGMA
# ==========================================

# 1. Điền Personal Access Token của bạn vào đây
# Cách lấy: Mở Figma -> Settings -> Personal Access Tokens -> Generate new token
FIGMA_TOKEN = "figd_FbhsFIOi967HZmlALPEhmyGg7wlG8zwIAZSMl_u7"

# 2. Điền File Key của bạn vào đây
# Cách lấy: Từ link figma có dạng https://www.figma.com/file/ABCDEFG12345/Tên-File
# Thì File Key chính là: ABCDEFG12345
FIGMA_FILE_KEY = "B2E8zlky5H6OoIpZjNay6U"

# ==========================================

def fetch_figma_data():
    url = f"https://api.figma.com/v1/files/{FIGMA_FILE_KEY}"
    
    headers = {
        "X-Figma-Token": FIGMA_TOKEN
    }

    print(f"[*] Dang tai du lieu tu Figma (File Key: {FIGMA_FILE_KEY})...")
    
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

def fetch_node_images(node_ids, format="png", scale=1):
    """
    Lay link anh render tu Figma cho danh sach cac node ID.
    """
    if not node_ids:
        return {}

    ids_param = ",".join(node_ids)
    url = f"https://api.figma.com/v1/images/{FIGMA_FILE_KEY}?ids={ids_param}&format={format}&scale={scale}"
    
    headers = {
        "X-Figma-Token": FIGMA_TOKEN
    }

    print(f"[*] Dang lay link anh cho {len(node_ids)} nodes...")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get("images", {})
    else:
        print(f"[ERROR] Loi khi lay link anh: {response.status_code}")
        return {}

if __name__ == "__main__":
    fetch_figma_data()
