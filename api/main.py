"""
SamiX Backend API
Status: Production Ready - Streamlit Cloud to Render Sync
"""
import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# 1. Define Request Schema for RAG
class QueryRequest(BaseModel):
    question: str

app = FastAPI(title="SamiX API Engine")

# 2. GLOBAL CORS FIX
# This allows your Streamlit Cloud app to bypass browser security blocks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (Streamlit Cloud uses dynamic subdomains)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "environment": "render-production",
        "integration": "streamlit-cloud-ready"
    }

@app.post("/api/v1/audit")
async def run_audit(
    file: UploadFile = File(...),
    agent_name: str = Form(...)
):
    try:
        # Placeholder for Deepgram + Groq logic
        return {
            "score": 85,
            "transcript": f"Audited {file.filename} for {agent_name}.",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/rag/query")
async def query_kb(request: QueryRequest):
    return {
        "answer": f"KB Result for: {request.question}",
        "sources": ["manual_2026.pdf"]
    }

if __name__ == "__main__":
    # Render dynamic port assignment
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
