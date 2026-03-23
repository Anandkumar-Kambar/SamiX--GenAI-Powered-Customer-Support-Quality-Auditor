"""
SamiX Enterprise Design System

Professional dark theme design system inspired by modern SaaS leaders (AirCover, Linear, Stripe).
Features dark mode with enterprise-grade aesthetics, glassmorphism, and sophisticated interactions.
"""

CSS = """
<style>
/* Modern Font Stack - Inter for that premium B2B feel */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  /* Shopeers Premium Palette - Modern B2B */
  --bg-base:     #F8FAFC;       /* Very light slate background */
  --bg-surface:  #FFFFFF;       /* Clean white surface */
  --bg-hover:    #F1F5F9;       /* Light slate on hover */
  --bg-overlay:  rgba(255,255,255,0.95);
  --bg-elevated: #FFFFFF;       /* Elevated cards */
  
  /* Primary Brand - Shopeers Blue */
  --accent:      #152EAE;       /* Deep Professional Shopeers Blue */
  --accent-dark: #0D1C6A;       /* Darker tone for depth */
  --accent-light: #2563EB;      /* Vibrant blue for highlights */
  --accent-glow: rgba(21, 46, 174, 0.15);
  --accent-subtle: rgba(21, 46, 174, 0.05);
  
  /* Gradients */
  --grad-primary: linear-gradient(135deg, #152EAE 0%, #2563EB 100%);
  --grad-surface: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
  
  /* Supporting Colors */
  --success:     #10B981;       /* Emerald Green */
  --success-bg:  #F0FDF4;
  --warning:     #F59E0B;       /* Amber */
  --warning-bg:  #FFFBEB;
  --danger:      #EF4444;       /* Red */
  --danger-bg:   #FEF2F2;
  --info:        #3B82F6;       /* Blue */
  
  /* Text Colors - High Contrast for Light Mode */
  --text-primary:    #0F172A;   /* Deep slate/black */
  --text-secondary:  #475569;   /* Slate gray */
  --text-tertiary:   #64748B;   /* Medium slate */
  --text-muted:      #94A3B8;   /* Light slate */
  
  /* Borders & Dividers */
  --border:          #E2E8F0;
  --border-accent:   #152EAE;
  --divider:         #F1F5F9;
  
  /* Effects */
  --radius:          14px;      /* Softer rounded corners */
  --radius-lg:       18px;
  --radius-sm:       10px;
  --blur:            12px;
  --shadow-sm:       0 1px 3px rgba(0,0,0,0.05);
  --shadow:          0 4px 12px rgba(0,0,0,0.03);
  --shadow-md:       0 10px 25px -5px rgba(0,0,0,0.05), 0 8px 10px -6px rgba(0,0,0,0.05);
  --shadow-lg:       0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
  
  /* Typography */
  --font-sans:       'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono:       'JetBrains Mono', 'Courier New', monospace;
}

/* App-Wide Styling */
.stApp, html, body {
  background: var(--bg-base) !important;
  color: var(--text-primary) !important;
  font-family: var(--font-sans) !important;
  font-size: 14px !important;
  line-height: 1.6 !important;
}

/* Sidebar Styling - Shopeers Dark Sidebar */
section[data-testid="stSidebar"] {
  background: #0F172A !important; /* Deep navy sidebar */
  border-right: 1px solid rgba(255,255,255,0.05) !important;
}
section[data-testid="stSidebar"] * {
  color: rgba(255,255,255,0.7) !important;
}
section[data-testid="stSidebar"] .stMarkdownContainer p {
  color: rgba(255,255,255,0.9) !important;
}

/* Sidebar Active State */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:hover {
  background: rgba(255,255,255,0.05) !important;
  border-radius: var(--radius-sm);
}

/* Main content area */
.stMainBlockContainer {
  padding-top: 2rem !important;
  max-width: 1200px !important;
}

/* Modern Tabs */
.stTabs [data-baseweb="tab-list"] {
  gap: 8px !important;
  border-bottom: 1px solid var(--border) !important;
  padding: 0 0 12px 0 !important;
  background: transparent !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--text-tertiary) !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  padding: 10px 20px !important;
  border-radius: var(--radius-sm) !important;
  border: 1px solid transparent !important;
  transition: all 0.2s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
  color: var(--text-primary) !important;
  background: var(--bg-hover) !important;
}
.stTabs [aria-selected="true"] {
  color: var(--accent) !important;
  background: white !important;
  border: 1px solid var(--border) !important;
  box-shadow: var(--shadow-sm) !important;
}

/* Metric Cards - Shopeers Analytics Style */
div[data-testid="metric-container"] {
  background: var(--bg-surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 24px !important;
  box-shadow: var(--shadow) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
div[data-testid="metric-container"]:hover {
  box-shadow: var(--shadow-md) !important;
  transform: translateY(-4px) !important;
  border-color: var(--accent-light) !important;
}
div[data-testid="metric-container"] label {
  color: var(--text-tertiary) !important;
  font-family: var(--font-sans) !important;
  font-weight: 600 !important;
  font-size: 12px !important;
  letter-spacing: 0.1px !important;
  margin-bottom: 8px !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
  color: var(--text-primary) !important;
  font-family: var(--font-sans) !important;
  font-weight: 800 !important;
  font-size: 34px !important;
  letter-spacing: -1px !important;
}

/* Premium Buttons */
.stButton > button {
  background: var(--accent) !important;
  color: #FFFFFF !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  font-family: var(--font-sans) !important;
  font-size: 14px !important;
  font-weight: 600 !important;
  padding: 12px 24px !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
  box-shadow: 0 4px 6px -1px rgba(21, 46, 174, 0.1), 0 2px 4px -1px rgba(21, 46, 174, 0.06) !important;
}
.stButton > button:hover {
  filter: brightness(1.1) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 10px 15px -3px rgba(21, 46, 174, 0.2) !important;
}

/* Secondary Button Fallback (Simplified) */
.stButton > button[kind="secondary"] {
  background: white !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border) !important;
}

/* Input Fields */
input, textarea, select {
  background: #FFFFFF !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text-primary) !important;
  font-family: var(--font-sans) !important;
  padding: 12px 16px !important;
  transition: all 0.2s ease !important;
  font-size: 14px !important;
}
input:focus, textarea:focus, select:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 4px var(--accent-glow) !important;
}

/* Glass Cards & Surfaces */
.glass-card {
  background: #FFFFFF !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 24px !important;
  box-shadow: var(--shadow) !important;
  margin-bottom: 1.5rem !important;
}

/* Section Headers */
.section-header {
  font-size: 24px;
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 1.5rem;
  letter-spacing: -0.5px;
}

/* Badges */
.mono-badge {
  background: var(--bg-hover) !important;
  color: var(--accent) !important;
  border: 1px solid var(--border) !important;
  padding: 4px 10px !important;
  border-radius: 6px !important;
  font-family: var(--font-mono) !important;
  font-size: 11px !important;
  font-weight: 600 !important;
  display: inline-block !important;
}

/* Status Flags */
.verdict-good {
  color: #059669 !important;
  background: #ECFDF5 !important;
  padding: 4px 12px !important;
  border-radius: 20px !important;
  font-weight: 700 !important;
  font-size: 12px !important;
  display: inline-block !important;
}
.verdict-fail {
  color: #DC2626 !important;
  background: #FEF2F2 !important;
  padding: 4px 12px !important;
  border-radius: 20px !important;
  font-weight: 700 !important;
  font-size: 12px !important;
  display: inline-block !important;
}

/* Transcript Bubbles */
.transcript-agent {
  background: #F8FAFC !important;
  border-left: 4px solid var(--accent) !important;
  padding: 16px !important;
  border-radius: 0 12px 12px 0 !important;
  margin-bottom: 12px !important;
}
.transcript-customer {
  background: white !important;
  border-left: 4px solid #94A3B8 !important;
  padding: 16px !important;
  border-radius: 0 12px 12px 0 !important;
  margin-bottom: 12px !important;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: var(--bg-base);
}
::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 20px;
}
::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}

</style>
"""


def inject_css() -> None:
    """
    Bootstrap function.
    Injects the custom CSS engine into the Streamlit session.
    Must be called early in the page render cycle.
    """
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)
