import os
import json
import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, List

async def fetch_website_data(url: str) -> Dict[str, Any]:
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    result = {
        "url": url,
        "title": "",
        "meta_description": "",
        "headings": [],
        "links": [],
        "images": [],
        "page_sample_text": "",
        "contact_email": "",
        "contact_phone": "",
        "contact_name": "",
        "status_code": 200,
        "errors": []
    }

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }) as client:
            resp = await client.get(url)
            result["status_code"] = resp.status_code
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Extract contact email using regex
            import re
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resp.text)
            if emails:
                # filter out common false positives
                valid_emails = [e for e in emails if not e.endswith('.png') and not e.endswith('.jpg') and not e.endswith('.svg')]
                if valid_emails:
                    result["contact_email"] = valid_emails[0]
                    
            # Extract phone numbers
            phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', resp.text)
            if phones:
                result["contact_phone"] = phones[0]

            if soup.title and soup.title.string:
                result["title"] = soup.title.string.strip()
            
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc and meta_desc.get("content"):
                result["meta_description"] = meta_desc["content"].strip()
                
            for h in soup.find_all(["h1", "h2", "h3"])[:15]:
                text = h.get_text(strip=True)
                if text:
                    result["headings"].append({"tag": h.name, "text": text})
                    
            for img in soup.find_all("img")[:15]:
                src = img.get("src", "")
                alt = img.get("alt", "")
                if src:
                    result["images"].append({"src": src, "alt": alt})

            # Extract body text
            for s in soup(["script", "style", "nav", "footer"]):
                s.decompose()
            body_text = soup.get_text(separator=" ", strip=True)
            result["page_sample_text"] = body_text[:2000]

    except Exception as e:
        result["errors"].append(str(e))
        result["page_sample_text"] = f"Failed to fetch content directly: {str(e)}"

    return result
