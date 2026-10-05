import sqlite3
import os
from typing import Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "app_data.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT DEFAULT 'AJ',
            company_name TEXT DEFAULT 'TECHSOUL (GrowEagles TechSoul Pvt. Ltd.)',
            website_url TEXT DEFAULT 'https://techsoul.in',
            email TEXT DEFAULT 'mail@techsoul.in',
            phone TEXT DEFAULT '+919862542983',
            designation TEXT DEFAULT 'Founder / Lead Consultant',
            linkedin TEXT DEFAULT 'https://linkedin.com/company/techsoul',
            gemini_api_key TEXT DEFAULT 'AIzaSyDQpTdBtRWq4fADA__3evxddax67M1LtyQ',
            passcode TEXT DEFAULT '123456'
        )
    """)
    # Migration: add passcode column if missing in existing table
    cursor.execute("PRAGMA table_info(company_settings)")
    cols = [column[1] for column in cursor.fetchall()]
    if 'passcode' not in cols:
        cursor.execute("ALTER TABLE company_settings ADD COLUMN passcode TEXT DEFAULT '123456'")

    cursor.execute("SELECT COUNT(*) FROM company_settings")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO company_settings (
                user_name, company_name, website_url, email, phone, designation, linkedin, gemini_api_key, passcode
            ) VALUES (
                'AJ',
                'TECHSOUL (GrowEagles TechSoul Pvt. Ltd.)',
                'https://techsoul.in',
                'mail@techsoul.in',
                '+919862542983',
                'Founder / Lead Consultant',
                'https://linkedin.com/company/techsoul',
                'AIzaSyDQpTdBtRWq4fADA__3evxddax67M1LtyQ',
                '123456'
            )
        """)
    conn.commit()
    conn.close()

def get_settings() -> Dict[str, Any]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM company_settings ORDER BY id ASC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {}

def update_settings(settings_data: Dict[str, Any]) -> Dict[str, Any]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE company_settings SET
            user_name = ?,
            company_name = ?,
            website_url = ?,
            email = ?,
            phone = ?,
            designation = ?,
            linkedin = ?,
            gemini_api_key = ?,
            passcode = ?
        WHERE id = 1
    """, (
        settings_data.get("user_name", "AJ"),
        settings_data.get("company_name", "TECHSOUL (GrowEagles TechSoul Pvt. Ltd.)"),
        settings_data.get("website_url", "https://techsoul.in"),
        settings_data.get("email", "mail@techsoul.in"),
        settings_data.get("phone", "+919862542983"),
        settings_data.get("designation", "Founder / Lead Consultant"),
        settings_data.get("linkedin", "https://linkedin.com/company/techsoul"),
        settings_data.get("gemini_api_key", "AQ.Ab8RN6I3lAIvFjD8lhbh6iGCryMlrf9iN7eqxxMxIXUGuqchfQ"),
        settings_data.get("passcode", "123456")
    ))
    conn.commit()
    conn.close()
    return get_settings()
