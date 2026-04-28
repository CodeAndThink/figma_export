import os
import webbrowser
import subprocess
import time

def main():
    print("=== FIGMA EXPORT PRO - UI MODE ===")
    
    # 1. Kiểm tra thư viện
    try:
        import fastapi
        import uvicorn
    except ImportError:
        print("[ERROR] Thieu thu vien! Vui long chay lenh sau de cai dat:")
        print("pip install fastapi uvicorn requests")
        return

    # 2. Tu dong mo trinh duyet sau 2 giay (doi server len)
    url = "http://127.0.0.1:8001"
    print(f"[*] Dang khoi dong server tai: {url}")
    
    # Run server trong mot process rieng hoac chay truc tiep neu day la diem ket thuc
    # De don gian va chac chan, chung ta se goi server.py
    try:
        # Mo trinh duyet
        webbrowser.open(url)
        
        # Chay server
        from server import app
        uvicorn.run(app, host="127.0.0.1", port=8001)
    except KeyboardInterrupt:
        print("\n[*] Da dung server.")
    except Exception as e:
        print(f"[ERROR] Khong the khoi chay server: {e}")

if __name__ == "__main__":
    main()
