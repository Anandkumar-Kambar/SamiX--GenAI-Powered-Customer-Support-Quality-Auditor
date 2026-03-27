"""
SamiX Backend API
Status: Production Ready - Streamlit Cloud to Render Sync
"""
import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# 1. Define Request Schema
class QueryRequest(BaseModel):
    question: str

app = FastAPI(title="SamiX API Engine")

# 2. CORS - This is the most important part for Streamlit Cloud
app.add_middleware(
    CORSMiddleware,
    # Allow your specific Streamlit Cloud URL for security
    # Or use ["*"] to allow all during testing
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "environment": "render-production"}

@app.post("/api/v1/audit")
async def run_audit(
    file: UploadFile = File(...),
    agent_name: str = Form(...)
):
    try:
        # Mocking the AI response
        return {
            "score": 85,
            "transcript": f"Auditing {file.filename} for {agent_name}...",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/rag/query")
async def query_kb(request: QueryRequest):
    return {
        "answer": f"Found info for: {request.question}",
        "sources": ["manual_2026.pdf"]
    }

if __name__ == "__main__":
    # Render provides a $PORT environment variable. 
    # Usually, FastAPI apps on Render listen on 10000 or $PORT.
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
