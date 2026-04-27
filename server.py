import os
import sys
import io
import json
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from funcs.figma_export import fetch_figma_data, extract_file_key
from funcs.split_screens import split_figma_screens

app = FastAPI()

# --- API ROUTES (Đặt lên trên cùng) ---

@app.post("/api/export")
async def run_export(request: Request):
    body = await request.json()
    token = body.get("token")
    file_link = body.get("file_link")
    file_key = extract_file_key(file_link)

    def generate():
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()
        try:
            yield f"[*] Đang tải dữ liệu cho File Key: {file_key}\n"
            fetch_figma_data(token=token, file_key=file_key)
            yield mystdout.getvalue()
            mystdout.truncate(0)
            mystdout.seek(0)

            yield "\n[2/3] Đang tách màn hình...\n"
            split_figma_screens(token=token, file_key=file_key)
            yield mystdout.getvalue()
            mystdout.truncate(0)
            mystdout.seek(0)

            yield "\n=== HOAN THANH TAT CA CAC BUOC ===\n"
        except Exception as e:
            yield f"\n[ERROR] Co loi xay ra: {str(e)}\n"
        finally:
            sys.stdout = old_stdout

    return StreamingResponse(generate(), media_type="text/plain")

@app.get("/api/screens")
async def list_screens():
    screen_dir = "screens"
    if not os.path.exists(screen_dir):
        return []
    folders = [f for f in os.listdir(screen_dir) if os.path.isdir(os.path.join(screen_dir, f))]
    return folders

@app.get("/api/data/{folder}")
async def get_json_data(folder: str):
    from urllib.parse import unquote
    folder_name = unquote(folder)
    path = os.path.join("screens", folder_name, "data.json")
    
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    raise HTTPException(status_code=404, detail=f"File not found: {path}")

@app.get("/api/preview/{folder}")
async def get_preview(folder: str):
    from urllib.parse import unquote
    folder_name = unquote(folder)
    path = os.path.join("screens", folder_name, "preview.png")
    if os.path.exists(path):
        return FileResponse(path)
    raise HTTPException(status_code=404, detail="Preview not found")

# --- STATIC FILES ---

@app.get("/")
async def read_index():
    return FileResponse("web/index.html")

@app.get("/style.css")
async def read_css():
    return FileResponse("web/style.css")

@app.get("/script.js")
async def read_js():
    return FileResponse("web/script.js")

# Mount thư mục web (nếu cần dùng các file khác bên trong)
if os.path.exists("web"):
    app.mount("/web", StaticFiles(directory="web"), name="web")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
