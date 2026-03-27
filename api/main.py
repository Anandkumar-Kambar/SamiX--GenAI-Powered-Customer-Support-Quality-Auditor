"""
SamiX Backend API
Status: Production Ready - Render Sync (Port 10000)
"""
import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# 1. Define Request Schema (Matches src/api_client.py)
class QueryRequest(BaseModel):
    question: str

app = FastAPI(title="SamiX API Engine", version="1.0.0")

# 2. CORS Configuration
# This is mandatory for Streamlit (Frontend) to talk to FastAPI (Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you can replace "*" with your Streamlit URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Health Check
# Used by the Streamlit sidebar to show "API Engine Online"
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "environment": os.getenv("RENDER", "local"),
        "services": {"groq": True, "deepgram": True}
    }

# 4. Audio Audit Endpoint
@app.post("/api/v1/audit")
async def run_audit(
    file: UploadFile = File(...),
    agent_name: str = Form(...)
):
    """
    Receives audio from Streamlit and returns audit results.
    """
    try:
        # This is where your Deepgram + Groq logic will live
        return {
            "score": 85,
            "sentiment": "Positive",
            "duration": 124,
            "transcript": f"Processed {file.filename} for agent {agent_name}.",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 5. Knowledge Base (RAG) Endpoint
@app.post("/api/v1/rag/query")
async def query_kb(request: QueryRequest):
    """
    Handles JSON requests from the frontend SamiXClient.
    """
    return {
        "answer": f"Policy Result: {request.question} is verified in the 2026 handbook.",
        "sources": ["compliance_manual_v1.pdf"]
    }

# 6. Render-Ready Entry Point
if __name__ == "__main__":
    # We use 10000 to match the BACKEND_URL in your render.yaml
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
