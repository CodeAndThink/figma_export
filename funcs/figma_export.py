import json
import os
import requests
import time
import random

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

def request_with_retry(method, url, headers=None, params=None, json_data=None, stream=False, max_retries=5):
    """Thực hiện request với cơ chế retry và exponential backoff."""
    retry_codes = [429, 500, 502, 503, 504]
    
    for i in range(max_retries):
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params, stream=stream, timeout=60)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=json_data, stream=stream, timeout=60)
            
            if response.status_code == 200:
                return response
            
            if response.status_code in retry_codes:
                wait_time = (2 ** i) + random.random()
                print(f"[RETRY] Loi {response.status_code}. Dang thu lai sau {wait_time:.2f}s (Lan {i+1}/{max_retries})...")
                time.sleep(wait_time)
                continue
            
            # Neu loi khac thi tra ve luon
            return response
            
        except Exception as e:
            wait_time = (2 ** i) + random.random()
            print(f"[RETRY] Loi ket noi: {e}. Dang thu lai sau {wait_time:.2f}s (Lan {i+1}/{max_retries})...")
            time.sleep(wait_time)
            
    return None

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
    
    response = request_with_retry("GET", url, headers=headers, stream=True)

    if response and response.status_code == 200:
        # Lưu kết quả ra file JSON bên trong folder screens (Sử dụng stream để tiết kiệm RAM)
        output_dir = "screens"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        output_file = os.path.join(output_dir, "figma_data.json")
        
        print(f"[*] Dang luu vao file: {output_file}...")
        with open(output_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
            
        print(f"[SUCCESS] Thanh cong! Du lieu da duoc luu.")
        
        # In ra một số thông tin (Chỉ đọc lại nếu cần, hoặc bỏ qua nếu file quá lớn)
        # print(f"[INFO] Ten file Figma: ...")
        
    else:
        status = response.status_code if response else "Unknown"
        print(f"[ERROR] Loi khi tai du lieu: {status}")
        if response:
            print(response.text[:500])

def fetch_node_images(node_ids, format="png", scale=1, token=None, file_key=None):
    """
    Lay link anh render tu Figma cho danh sach cac node ID.
    """
    global FIGMA_TOKEN, FIGMA_FILE_KEY
    t = token or FIGMA_TOKEN
    fk = file_key or FIGMA_FILE_KEY

    if not node_ids or not t or not fk:
        return {}

    # Batching: Chia nho danh sach ID (toi da 100 IDs moi request)
    batch_size = 100
    all_images = {}
    
    headers = {
        "X-Figma-Token": t
    }

    for i in range(0, len(node_ids), batch_size):
        batch = node_ids[i:i + batch_size]
        ids_param = ",".join(batch)
        url = f"https://api.figma.com/v1/images/{fk}?ids={ids_param}&format={format}&scale={scale}"
        
        print(f"[*] Dang lay link anh cho batch {i//batch_size + 1} ({len(batch)} nodes)...")
        response = request_with_retry("GET", url, headers=headers)

        if response and response.status_code == 200:
            batch_images = response.json().get("images", {})
            all_images.update(batch_images)
        else:
            status = response.status_code if response else "Unknown"
            print(f"  [!] Loi khi lay link anh batch {i//batch_size + 1}: {status}")

    return all_images

if __name__ == "__main__":
    token, file_key = get_cli_config()
    fetch_figma_data(token, file_key)
