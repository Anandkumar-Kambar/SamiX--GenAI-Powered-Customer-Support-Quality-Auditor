# SamiX ~ samiksha
## GenAI-Powered Customer Support Quality Auditor
> *ARCHITECTURE* 

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Built_with-Streamlit-FF4B4B.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---
# SamiX Architecture 

This document explains how the SamiX system works under the hood, the core components, and the advantages of its modern decoupled design.

## 🏗 The Decoupled System Architecture

SamiX operates using a **Client/Server separation** to maximize performance and reliability:

1. **Frontend (Streamlit Client)**: A lightweight, responsive, lightning-fast UI. It handles authentication, data visualization (Plotly charts), audio recording, and session history management.
2. **Backend (FastAPI Server)**: A heavy-duty API that handles the intensive AI workloads (audio conversion, Speech-to-Text inference, LLM generation, and Vector DB retrieval).

### How the Pipeline Works (The `POST /audit` flow)
When a user uploads an audio file via the Streamlit UI, the following sequence occurs:
1. **Request**: Streamlit sends the audio file to the FastAPI backend via an asynchronous `httpx` HTTP POST request.
2. **Audio Processing**: The backend uses `pydub` to normalize the audio into a standard WAV format.
3. **STT Transcription**: The backend calls `Deepgram Nova-3` for ultra-fast diarized transcription (with a local `Whisper` fallback).
4. **Contextual Summarization**: The transcript is sent to `Groq (Llama-3.3-70B)` to extract the primary customer queries.
5. **RAG Retrieval**: The summarized queries are fed into the Knowledge Base (Milvus) to retrieve specific company policies (Classic RAG stage).
6. **Informed Scoring**: A massive prompt containing the transcript **and** the retrieved policies is sent to Groq. The LLM acts as an expert QA auditor, explicitly grounding its scores and "wrong turn" corrections against the retrieved policies.
7. **Response**: The structured JSON payload is returned to Streamlit, which parses it, saves it to SQLite, and renders the Dashboard.

---

## 🧠 Classic RAG Implementation

SamiX utilizes a textbook "Classic RAG" architecture to eliminate LLM hallucinations:

- **Stage 1: Indexing**: Policy documents (PDF/TXT) are split into 800-character chunks with a 100-character overlap, embedded using `BAAI/bge-small-en-v1.5`, and stored entirely offline in `Milvus Lite`. A backup is kept for pure keyword search.
- **Stage 2: Retrieval (Hybrid + Reranking)**: 
  - Standard semantic similarity matching (dense vector) against Milvus.
  - Keyword matching (sparse BM25) against the backup text.
  - Features are merged using Reciprocal Rank Fusion (RRF).
  - The final top 10 candidates are fed through a **Cross-Encoder Reranker (`ms-marco-MiniLM-L-6-v2`)** to ensure only the most precise, contextually relevant chunks are sent to the LLM.
- **Stage 3: Generation**: The highly curated RAG context is injected as a specific `<POLICY_CONTEXT>` block inside the Groq system prompt.

---

## 🌟 Advantages of this Architecture

1. **Zero UI Timeouts**: Because LLM inference and deep STT models take time (sometimes 10–20 seconds), performing them inside the Streamlit main thread previously caused the UI to lag or disconnect. By offloading this to FastAPI, Streamlit remains wildly responsive.
2. **Scalability**: You can deploy the Streamlit UI on a cheap Edge server (like Streamlit Community Cloud) and deploy the API on a dedicated machine where you can independently scale GPU/CPU power.
3. **Platform Agnostic API**: Because the heavy lifting is exposed via a REST API (`/audit`), you can easily hook SamiX into *other* systems. Want a Slack bot that automatically audits calls? Just hit the API. Want to integrate into a CRM? Just hit the API.
4. **Resiliency**: The system features graceful fallbacks at almost every layer (Deepgram → Whisper; Milvus Vector → BM25 Keyword matcher; API Backend → Local UI processing).
