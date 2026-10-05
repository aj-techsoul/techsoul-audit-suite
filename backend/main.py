import os
import uuid
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

from services.crawler_service import fetch_website_data
from services.gemini_service import generate_audit_report
from services.pdf_service import build_pdf_report
from services.db_service import get_settings, update_settings, init_db

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="AI Website Audit & PDF Generator API")

@app.get("/api/health")
def health_check():
    """Used by Electron to know when the backend is ready."""
    return {"status": "ok"}

# Initialize database
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
NEXT_ASSETS = os.path.join(STATIC_DIR, "_next")
if os.path.exists(NEXT_ASSETS):
    app.mount("/_next", StaticFiles(directory=NEXT_ASSETS), name="next_assets")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

PROMPT_FILE = os.path.join(os.path.dirname(__file__), "..", "AI-prompt.txt")
DEFAULT_PROMPT = ""
if os.path.exists(PROMPT_FILE):
    with open(PROMPT_FILE, "r") as f:
        DEFAULT_PROMPT = f.read()

class AuditRequest(BaseModel):
    url: str
    client_name: Optional[str] = "Client Website"
    api_key: Optional[str] = None
    tone: Optional[str] = "Aggressive & Direct"
    custom_prompt: Optional[str] = None

class CompanySettingsModel(BaseModel):
    user_name: Optional[str] = "AJ"
    company_name: Optional[str] = "TECHSOUL (GrowEagles TechSoul Pvt. Ltd.)"
    website_url: Optional[str] = "https://techsoul.in"
    email: Optional[str] = "mail@techsoul.in"
    phone: Optional[str] = "+919862542983"
    designation: Optional[str] = "Founder / Lead Consultant"
    linkedin: Optional[str] = "https://linkedin.com/company/techsoul"
    gemini_api_key: Optional[str] = "AIzaSyDQpTdBtRWq4fADA__3evxddax67M1LtyQ"
    passcode: Optional[str] = "123456"

class PasscodeVerificationRequest(BaseModel):
    passcode: str

@app.get("/api/settings")
def get_company_settings():
    return get_settings()

@app.post("/api/settings")
def update_company_settings(settings: CompanySettingsModel):
    return update_settings(settings.dict())

@app.post("/api/verify-passcode")
def verify_passcode(req: PasscodeVerificationRequest):
    settings = get_settings()
    stored_code = str(settings.get("passcode", "123456")).strip()
    user_code = str(req.passcode).strip()
    if not stored_code or stored_code == user_code:
        return {"success": True, "message": "Access granted"}
    return {"success": False, "message": "Invalid passcode"}

@app.get("/")
def read_root():
    static_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(static_file):
        return FileResponse(static_file)
    return {"status": "online", "message": "Website Audit API is operational"}

@app.post("/api/audit")
async def create_audit(req: AuditRequest):
    try:
        # Fetch DB Settings
        db_settings = get_settings()

        # Step 1: Crawl website
        crawled_data = await fetch_website_data(req.url)
        
        # Step 2: Gemini Prompt
        prompt = req.custom_prompt if req.custom_prompt else DEFAULT_PROMPT
        api_key = req.api_key if req.api_key and req.api_key.startswith("AIzaSy") else (db_settings.get("gemini_api_key") if db_settings.get("gemini_api_key", "").startswith("AIzaSy") else None)
        if not api_key:
            from services.gemini_service import GEMINI_API_KEY
            api_key = GEMINI_API_KEY
        
        audit_json = generate_audit_report(
            url=req.url,
            client_name=req.client_name,
            crawled_data=crawled_data,
            prompt_template=prompt,
            api_key=api_key,
            tone=req.tone or "Aggressive & Direct"
        )

        report_id = str(uuid.uuid4())[:8]
        pdf_filename = f"Audit_Report_{report_id}.pdf"
        pdf_path = os.path.join(REPORTS_DIR, pdf_filename)

        # Step 3: Build PDF with company settings
        build_pdf_report(audit_json, pdf_path, company_info=db_settings)

        return {
            "report_id": report_id,
            "url": req.url,
            "client_name": req.client_name,
            "download_url": f"/api/reports/{pdf_filename}",
            "pdf_url": f"/api/reports/{pdf_filename}",
            "audit_data": audit_json,
            "company_settings": db_settings
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/{filename}")
def download_report(filename: str):
    file_path = os.path.join(REPORTS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    return FileResponse(file_path, media_type="application/pdf", filename=filename)

if __name__ == "__main__":
    import argparse, uvicorn
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", type=str, default="127.0.0.1")
    args = parser.parse_args()
    uvicorn.run("main:app", host=args.host, port=args.port, reload=False)
