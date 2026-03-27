# 🛡️ SamiX: GenAI-Powered Quality Auditor

**SamiX** is a professional Customer Support Quality Assurance (QA) platform. It uses Generative AI to automate the auditing of support interactions, transforming raw audio recordings into actionable quality scores, transcripts, and sentiment analysis.

---

## 🚀 Key Features

* **AI-Powered Audits:** Automated scoring based on custom rubrics using **Groq (Llama 3)**.
* **Speech-to-Text:** High-accuracy transcription powered by **Deepgram**.
* **Decoupled Architecture:** Separate Streamlit Frontend and FastAPI Backend for high performance.
* **Role-Based Access:** Dedicated views for **Admins** (Analytics) and **Agents** (Audit Workspace).
* **Self-Healing Database:** Automatic SQLite table initialization and admin seeding on first launch.

---

## 🏗️ Technical Stack

* **Frontend:** [Streamlit](https://streamlit.io/)
* **Backend:** [FastAPI](https://fastapi.tiangolo.com/)
* **Database:** SQLite with [SQLAlchemy ORM](https://www.sqlalchemy.org/)
* **LLM Inference:** Groq Cloud (Llama-3-70b)
* **Audio Intelligence:** Deepgram Nova-2

---

## 🚦 Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
