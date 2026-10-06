# main.py - Expired Domain Checker API (Omar Domain Bot)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import whois
from datetime import datetime
import random

# FastAPI App Initialize
app = FastAPI(title="Omar Domain Bot API", version="1.0")

# Request Model
class DomainRequest(BaseModel):
    domain: str

# Root Endpoint (Testing ke liye)
@app.get("/")
def root():
    return {
        "message": "Omar Domain Bot API is running successfully!",
        "docs": "Visit /docs to test the API endpoints."
    }

# Main Domain Check Endpoint
@app.post("/check-domain")
def check_domain(request: DomainRequest):
    try:
        # 1. WHOIS Lookup (Free Data)
        w = whois.whois(request.domain)
        
        if not w.domain_name:
            raise HTTPException(status_code=404, detail="Domain not found or invalid")

        # 2. Check Expiry Date
        expiry_date = w.expiration_date
        if isinstance(expiry_date, list):
            expiry_date = expiry_date[0]
            
        is_expired = False
        days_to_expiry = None
        
        if expiry_date:
            if expiry_date.tzinfo is None:
                now = datetime.now()
            else:
                now = datetime.utcnow().replace(tzinfo=expiry_date.tzinfo)
                
            delta = expiry_date - now
            days_to_expiry = delta.days
            if days_to_expiry <= 0:
                is_expired = True

        # 3. Estimate Authority Score (Based on Domain Age for MVP)
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
            
        age_years = 0
        if creation_date:
            if creation_date.tzinfo is None:
                age_delta = datetime.now() - creation_date
            else:
                age_delta = datetime.utcnow().replace(tzinfo=creation_date.tzinfo) - creation_date
            age_years = max(0, age_delta.days // 365)
            
        # Older domains get a higher simulated authority score
        mock_authority = min(100, (age_years * 5) + random.randint(10, 30))

        # 4. Return Clean JSON Response
        return {
            "domain": request.domain,
            "is_expired": is_expired,
            "days_to_expiry": days_to_expiry,
            "creation_year": creation_date.year if creation_date else None,
            "estimated_authority_score": mock_authority,
            "registrar": w.registrar
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing domain: {str(e)}")