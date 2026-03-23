@echo off
REM ============================================================================
REM SamiX Setup Script for Windows
REM ============================================================================
REM This script automates the initial setup of the SamiX application
REM including venv creation, dependency installation, and configuration.

echo.
echo ============================================================================
echo SamiX - Setup Wizard
echo ============================================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    echo And make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/5] Checking Python version...
python --version
echo.

REM Check FFmpeg installation
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo WARNING: FFmpeg not found in PATH
    echo pydub requires FFmpeg for audio processing
    echo Download from: https://ffmpeg.org/download.html
    echo Add ffmpeg/bin to your PATH
    echo.
)

REM Create virtual environment
echo [2/5] Creating Python virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo.

REM Upgrade pip
echo [4/5] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip, continuing anyway...
)
echo.

REM Install dependencies
echo [5/5] Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)
echo.

echo ============================================================================
echo Setup Complete!
echo ============================================================================
echo.
echo Next steps:
echo 1. Edit .env with your API keys (GROQ_API_KEY, DEEPGRAM_API_KEY)
echo 2. Edit .streamlit\secrets.toml with your credentials
echo 3. Run: streamlit run app.py
echo 4. Open http://localhost:8501 in your browser
echo.
echo Default credentials:
echo   Email: admin@samix.ai
echo   Password: admin
echo.
echo IMPORTANT: Change default credentials before deploying!
echo.
pause
