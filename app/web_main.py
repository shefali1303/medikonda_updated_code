from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import init_db, list_records, load_record, save_record
from .defaults import DEFAULT_DATA, TEMPLATE_PRESETS
from .paths import app_root, user_path
from .pdf_generator import generate_document_pdf

ROOT = app_root()
OUTPUT_DIR = user_path("output", "placeholder").parent
LOGO_DIR = user_path("logos", "placeholder").parent

app = FastAPI(title="Medikonda PDF Generator Web App")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")
app.mount("/assets", StaticFiles(directory=str(ROOT / "assets")), name="assets")
app.mount("/generated", StaticFiles(directory=str(OUTPUT_DIR)), name="generated")
templates = Jinja2Templates(directory=str(ROOT / "templates"))


@app.on_event("startup")
def _startup() -> None:
    init_db()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOGO_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/bootstrap")
def bootstrap() -> Dict[str, Any]:
    return {
        "default_data": copy.deepcopy(DEFAULT_DATA),
        "template_presets": copy.deepcopy(TEMPLATE_PRESETS),
        "records": list_records(),
    }


@app.get("/api/records")
def records() -> Dict[str, Any]:
    return {"records": list_records()}


@app.get("/api/records/{record_id}")
def record(record_id: int) -> Dict[str, Any]:
    data = load_record(record_id)
    if not data:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"record": data}


def _safe_filename(name: str) -> str:
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", name.strip())
    return name[:120] or "file"


@app.post("/api/upload-logo")
async def upload_logo(file: UploadFile = File(...)) -> Dict[str, Any]:
    ext = Path(file.filename or "logo.png").suffix.lower()
    if ext not in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
        raise HTTPException(status_code=400, detail="Please upload PNG, JPG, WEBP, or BMP logo file.")
    path = LOGO_DIR / _safe_filename(file.filename or "logo.png")
    content = await file.read()
    path.write_bytes(content)
    return {"logo_path": str(path), "logo_url": f"/generated/../logos/{path.name}"}


@app.post("/api/save")
async def save(payload: Dict[str, Any]) -> Dict[str, Any]:
    record_id = save_record(payload)
    data = load_record(record_id)
    return {"ok": True, "record_id": record_id, "record": data, "records": list_records()}


@app.post("/api/generate")
async def generate(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        pdf_path = generate_document_pdf(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"ok": True, "file_name": pdf_path.name, "download_url": f"/download/{pdf_path.name}", "open_url": f"/generated/{pdf_path.name}"}


@app.get("/download/{file_name}")
def download(file_name: str) -> FileResponse:
    safe = _safe_filename(file_name)
    path = OUTPUT_DIR / safe
    if not path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(path, media_type="application/pdf", filename=path.name)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}
