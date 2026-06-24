from __future__ import annotations

import base64
import copy
import json
import re
from pathlib import Path
from typing import Any, Dict

import requests
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


# --------------------------------------------------------------------
# GOOGLE DRIVE UPLOAD SETTINGS
# --------------------------------------------------------------------
# Paste your deployed Apps Script Web App URL here.
# Example:
# APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbykXWiyu2aabiRctUhDDBq1S1T_Bu8pNZuTkw6QYf23fYJ0gK0-xwo5wx9xNYdKuImj/exec"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbykXWiyu2aabiRctUhDDBq1S1T_Bu8pNZuTkw6QYf23fYJ0gK0-xwo5wx9xNYdKuImj/exec"
# This must match the SECRET_KEY inside your Apps Script.
APPS_SCRIPT_SECRET = "medikonda-drive-upload-2026"

# Keep this True if you want every generated PDF to upload to Google Drive.
UPLOAD_TO_GOOGLE_DRIVE = True
# --------------------------------------------------------------------


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


def upload_pdf_to_google_drive(pdf_path: Path) -> Dict[str, Any]:
    """
    Uploads the generated PDF to Google Drive through Apps Script.

    Important:
    If upload fails, /api/generate will still return local PDF download links.
    Drive upload is extra, not required for local PDF generation.
    """
    if not UPLOAD_TO_GOOGLE_DRIVE:
        return {
            "ok": False,
            "skipped": True,
            "error": "Google Drive upload is disabled.",
        }

    if not APPS_SCRIPT_URL or APPS_SCRIPT_URL == "PASTE_YOUR_APPS_SCRIPT_WEB_APP_URL_HERE":
        return {
            "ok": False,
            "skipped": True,
            "error": "Apps Script URL is not configured.",
        }

    with pdf_path.open("rb") as file:
      file_base64 = base64.b64encode(file.read()).decode("utf-8")

    payload = {
        "secret": APPS_SCRIPT_SECRET,
        "fileName": pdf_path.name,
        "fileBase64": file_base64,
    }

    response = requests.post(
        APPS_SCRIPT_URL,
        json=payload,
        timeout=90,
    )

    response.raise_for_status()
    result = response.json()

    if not result.get("ok"):
        raise RuntimeError(result.get("error", "Google Drive upload failed."))

    return result


@app.post("/api/upload-logo")
async def upload_logo(file: UploadFile = File(...)) -> Dict[str, Any]:
    ext = Path(file.filename or "logo.png").suffix.lower()
    if ext not in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
        raise HTTPException(status_code=400, detail="Please upload PNG, JPG, WEBP, or BMP logo file.")

    path = LOGO_DIR / _safe_filename(file.filename or "logo.png")
    content = await file.read()
    path.write_bytes(content)

    return {
        "logo_path": str(path),
        "logo_url": f"/generated/../logos/{path.name}",
    }


@app.post("/api/save")
async def save(payload: Dict[str, Any]) -> Dict[str, Any]:
    record_id = save_record(payload)
    data = load_record(record_id)

    return {
        "ok": True,
        "record_id": record_id,
        "record": data,
        "records": list_records(),
    }


@app.post("/api/generate")
async def generate(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        pdf_path = generate_document_pdf(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    drive_url = None
    drive_file_id = None
    drive_error = None

    try:
        drive_result = upload_pdf_to_google_drive(pdf_path)

        if drive_result and drive_result.get("ok"):
            drive_url = drive_result.get("fileUrl")
            drive_file_id = drive_result.get("fileId")
        elif drive_result and drive_result.get("error"):
            drive_error = drive_result.get("error")

    except Exception as exc:
        # Important:
        # Do not fail PDF generation if Google Drive upload fails.
        # User should still get Download and Open Preview links.
        drive_error = str(exc)

    return {
        "ok": True,
        "file_name": pdf_path.name,
        "download_url": f"/download/{pdf_path.name}",
        "open_url": f"/generated/{pdf_path.name}",
        "drive_url": drive_url,
        "drive_file_id": drive_file_id,
        "drive_error": drive_error,
    }


@app.get("/download/{file_name}")
def download(file_name: str) -> FileResponse:
    safe = _safe_filename(file_name)
    path = OUTPUT_DIR / safe

    if not path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=path.name,
    )


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}