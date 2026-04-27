import os
from funcs.figma_export import fetch_figma_data
from funcs.split_screens import split_figma_screens

def main():
    print("=== FIGMA EXPORT & SPLIT TOOL ===")
    
    # 1. Tai du lieu tu Figma
    print("\n[1/3] Dang tai du lieu tu Figma API...")
    fetch_figma_data()
    
    # 2. Cat du lieu thanh cac screen
    print("\n[2/3] Dang tach du lieu thanh cac file screen...")
    split_figma_screens()
    
    # 3. Preview cac man hinh
    print("\n[3/3] Preview cac man hinh da trich xuat:")
    screen_dir = "screens"
    # Liet ke cac thu muc man hinh
    folders = [f for f in os.listdir(screen_dir) if os.path.isdir(os.path.join(screen_dir, f))]
    
    for i, foldername in enumerate(folders):
        print(f"{i+1}. {foldername}")
    
    print("\n=== HOAN THANH TAT CA CAC BUOC ===")

if __name__ == "__main__":
    main()
