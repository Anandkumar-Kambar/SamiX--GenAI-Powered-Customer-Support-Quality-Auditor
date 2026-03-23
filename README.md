# SamiX ~ samiksha
## GenAI-Powered Customer Support Quality Auditor
> *The All-Seeing Eye of Quality* · ಸಮೀಕ್ಷೆ

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Built_with-Streamlit-FF4B4B.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🚀 Quick Start (< 5 minutes)

### Option 1: Automatic Setup (Easiest)
```bash
python quickstart.py  # Does everything for you!
```

### Option 2: Manual Setup

**Prerequisites:**
- Python 3.11+ ([download](https://www.python.org/downloads/))
- Git ([download](https://git-scm.com/download/win))
- FFmpeg ([download](https://ffmpeg.org/download.html)) - Add to PATH!

**Windows:**
```bat
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python generate_hash.py
streamlit run app.py
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python generate_hash.py
streamlit run app.py
```

**Open:** http://localhost:8501

**Default Login:** admin@samix.ai / admin

---

## 📋 Next Steps

### 1. Get API Keys
- **Groq API:** https://console.groq.com/keys
- **Deepgram STT:** https://console.deepgram.com/console/keys (optional)

### 2. Configure
Edit `.env` with your API keys:
```env
GROQ_API_KEY=gsk_your_key_here
DEEPGRAM_API_KEY=your_key_here
```

### 3. Validate Setup
```bash
python validate.py
```

### 4. Run
```bash
streamlit run app.py
```

---

## ☁️ Deploy to Cloud (Free!)

### Streamlit Cloud (Recommended)
1. Push code to GitHub (secrets auto-excluded)
2. Go to https://share.streamlit.io
3. Click "New app" → Select your repo
4. Add secrets via "Advanced settings"
5. Live in ~2 minutes! 🎉

### Docker
```bash
docker-compose up --build
```

### Heroku
```bash
git push heroku main
```

See `DEPLOYMENT.md` for all options (AWS, Google Cloud, etc.)

---

## 📁 Project Structure

```
samix/
├── app.py                      ← Entry point
├── config.py                   ← Configuration management
├── validate.py                 ← Pre-flight checks
├── quickstart.py               ← Auto-setup script
├── generate_hash.py            ← Password hashing
│
├── .env                        ← Environment variables (⚠ not in git)
├── .streamlit/
│   ├── config.toml            ← Streamlit settings
│   └── secrets.toml           ← Secrets (⚠ not in git)
├── .gitignore                 ← Excludes sensitive files
│
├── src/
│   ├── auth/
│   │   └── authenticator.py   ← Auth manager
│   ├── pipeline/
│   │   ├── groq_client.py     ← LLM inference
│   │   ├── stt_processor.py   ← Speech-to-text
│   │   └── alert_engine.py    ← Alerts system
│   ├── ui/
│   │   ├── login_page.py      ← Login UI
│   │   ├── agent_panel.py     ← Agent dashboard
│   │   ├── admin_panel.py     ← Admin dashboard
│   │   ├── components.py      ← UI components
│   │   └── styles.py          ← CSS/styling
│   └── utils/
│       ├── kb_manager.py      ← Knowledge base + RAG
│       ├── history_manager.py ← Audit records
│       ├── cost_tracker.py    ← API cost tracking
│       ├── audio_processor.py ← Audio utilities
│       └── report_generator.py ← Report generation
│
├── data/
│   ├── auth/users.yaml        ← User database
│   ├── kb/                    ← Knowledge base files
│   ├── history/               ← Audit records (JSON)
│   └── uploads/               ← Uploaded audio/transcripts
│
├── Dockerfile                 ← Docker config
├── docker-compose.yml         ← Docker Compose
├── requirements.txt           ← Python dependencies
├── DEPLOYMENT.md              ← Deployment guide
├── PRODUCTION_GUIDE.md        ← Production setup
├── TROUBLESHOOTING.md         ← Troubleshooting
└── QUICKSTART.md              ← Quick reference
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `QUICKSTART.md` | Quick reference & common tasks |
| `DEPLOYMENT.md` | Deploy to Streamlit Cloud, Heroku, AWS, GCP |
| `PRODUCTION_GUIDE.md` | Production setup & security |
| `TROUBLESHOOTING.md` | Common issues & fixes |
| `DEPLOYMENT_AWS.md` | Detailed AWS deployment (if available) |

---

## ✨ Features

- **Multi-Engine AI Analysis**: Groq Llama-3 with dual-pass quality auditing
- **Speech-to-Text Pipeline**: Deepgram (cloud) + Whisper (local fallback)
- **Vector RAG**: Milvus Lite with HuggingFace embeddings
- **Premium UI**: Dark theme with responsive design
- **Secure Auth**: Bcrypt password hashing + session management
- **Cost Tracking**: Real-time API usage & billing
- **Scalable**: Docker, Heroku, Streamlit Cloud, AWS support

---

## 🔧 Configuration

### Environment Variables (.env)
├── .gitignore
├── .streamlit/
│   ├── config.toml               ← Deep Slate dark theme
│   └── secrets.toml              ← NEVER commit · listed in .gitignore
├── src/
│   ├── auth/
│   │   └── authenticator.py      ← streamlit-authenticator wrapper
│   ├── pipeline/
│   │   ├── groq_client.py        ← dual-call LLM (mock fallback)
│   │   ├── stt_processor.py      ← Deepgram + Whisper + chat parser
│   │   └── alert_engine.py       ← st.toast + SMTP email
│   ├── ui/
│   │   ├── styles.py             ← CSS injection (Deep Slate theme)
│   │   ├── components.py         ← gauges, charts, transcript, cost card
│   │   ├── login_page.py         ← professional login screen
│   │   ├── agent_panel.py        ← client workspace
│   │   └── admin_panel.py        ← admin dashboard
│   └── utils/
│       ├── history_manager.py    ← JSON persistence · filename consistency
│       ├── audio_processor.py    ← pydub + TTS summary
│       ├── cost_tracker.py       ← token × price → profit/loss
│       └── kb_manager.py         ← Milvus Lite RAG KB
└── data/
    ├── history/                  ← audit JSON files
    ├── kb/                       ← indexed KB documents
    └── uploads/                  ← raw uploaded files
```

---

## Features

| Feature | Implementation |
|---|---|
| Secure login | streamlit-authenticator · bcrypt hash in secrets.toml |
| Speaker separation | Deepgram diarize=true · Twilio dual-stream for live |
| Filename consistency | uploaded name = stored name = history name = report name |
| Audio player + summary | pydub WAV 16kHz · gTTS / pyttsx3 synthesis |
| Dual scoring | Agent QA 0–100 · Customer sentiment 0–10 per turn |
| ECharts gauges | Empathy · Professionalism · Compliance |
| Dual score chart | Plotly · red-zone markers · hover breakdown |
| Where it went wrong | Exact turn · verbatim quote · wrong fact · correct fact · specific correction |
| RAG KB | Milvus Lite · LangChain · all-MiniLM-L6-v2 · PDF/TXT upload |
| Generalised KB | ITIL · ISO 9001 · GDPR · de-escalation · 50 empathy phrases |
| Alert system | st.toast (screen pop) · SMTP email |
| Cost evaluation | Token count × price · profit/loss per audit |
| Download report | TXT · JSON · CSV · email |
| Admin: model perf | Groq latency · scoring accuracy · STT stats · RAG stats |
| Admin: users | Usage · growth · churn · email action |
| Admin: billing | Revenue vs cost · send invoice emails · margin |
| Admin: RAG KB | Upload · index · delete files · collection tags |
| Admin: system health | Service uptime · latency chart · queue stats |

---

## API keys (all free tiers sufficient for development)

| Service | Free tier | Link |
|---|---|---|
| Groq | ~14,400 requests/day | https://console.groq.com |
| Deepgram | $200 credit | https://console.deepgram.com |
| Streamlit Cloud | Unlimited public apps | https://share.streamlit.io |

Whisper, Milvus Lite, pydub, gTTS — all free, no account needed.

---

## Troubleshooting

**`pydub` audio error** — Install FFmpeg and add to PATH.

**`streamlit-authenticator` import error** — Run `pip install streamlit-authenticator==0.3.2`

**`sentence-transformers` slow first run** — It downloads the MiniLM model (~90 MB) once.

**Groq mock data showing** — Check your Groq API key in secrets.toml starts with `gsk_` (not `gsk_REPLACE`).

**Login not working** — Re-run `python generate_hash.py`, copy the new hash exactly into secrets.toml.
