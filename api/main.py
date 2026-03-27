"""
SamiX Backend API
Endpoint Sync & CORS Enabled
"""
from fastapi import FastAPI, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn

app = FastAPI(title="SamiX API Engine", version="1.0.0")

# CRITICAL: Allow your Streamlit UI to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your specific Streamlit URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "services": {"groq": True, "deepgram": True}}

# Match the path used in src/api_client.py
@app.post("/api/v1/audit")
async def run_audit(
    file: UploadFile = File(...),
    agent_name: str = Form(...)
):
    """
    Main Audit Engine.
    In a full implementation, this calls Deepgram for audio 
    and Groq for scoring.
    """
    # Mock response for testing the connection
    return {
        "score": 85,
        "sentiment": "Positive",
        "duration": 124,
        "transcript": f"This is a simulated transcript for agent {agent_name}.",
        "status": "success"
    }

@app.post("/api/v1/rag/query")
async def query_kb(question: str):
    return {"answer": "Policy check: Standard greeting is required.", "sources": ["manual_v1.pdf"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
