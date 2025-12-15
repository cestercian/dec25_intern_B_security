import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from fastapi.middleware.cors import CORSMiddleware
from gmail_service import GmailService
import uvicorn

app = FastAPI()

# Configure CORS (allow frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FetchEmailsRequest(BaseModel):
    access_token: str

    @field_validator('access_token')
    @classmethod
    def access_token_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Access token cannot be empty')
        return v

@app.get("/")
def read_root():
    return {"message": "Hello from dashboard-backend!"}

logger = logging.getLogger(__name__)

@app.post("/api/v1/emails/fetch")
def fetch_emails(request: FetchEmailsRequest):
    # Validation handled by Pydantic
    
    try:
        gmail = GmailService(request.access_token)
        emails = gmail.fetch_recent_emails()
        
        return {"status": "success", "count": len(emails), "emails": emails}
    except Exception as e:
        logger.error(f"Error fetching emails: {e}", exc_info=True)
        raise HTTPException(status_code=502, detail="Failed to fetch emails from Gmail") from e

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
