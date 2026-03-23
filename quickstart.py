"""
SamiX Quick Start Script

Automatically sets up and runs the SamiX application.
Use this if you want minimal configuration.

Usage:
    python quickstart.py
"""
import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    print("\n" + "="*70)
    print("SamiX Quick Start")
    print("="*70 + "\n")

def check_requirements():
    """Check for required commands."""
    requirements = {
        "Python 3.11+": "python --version",
        "pip": "pip --version",
        "FFmpeg": "ffmpeg -version",
    }
    
    print("Checking system requirements...\n")
    
    missing = []
    for name, cmd in requirements.items():
        try:
            result = subprocess.run(cmd.split(), capture_output=True)
            if result.returncode == 0:
                print(f"✓ {name}")
            else:
                missing.append(name)
        except:
            if name != "FFmpeg":  # FFmpeg is optional
                missing.append(name)
            else:
                print(f"ℹ {name} (optional)")
    
    if missing:
        print(f"\n❌ Missing: {', '.join(missing)}")
        return False
    
    print("\n✓ All requirements met\n")
    return True

def install_dependencies():
    """Install Python dependencies."""
    print("Installing dependencies...\n")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"],
            check=True
        )
        print("✓ Dependencies installed\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}\n")
        return False

def generate_password(password: str = "admin"):
    """Generate bcrypt hash for default password."""
    print(f"Generating password hash for '{password}'...\n")
    
    try:
        import bcrypt
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        return hashed
    except ImportError:
        print("❌ bcrypt not installed\n")
        return None

def setup_secrets():
    """Create or update .streamlit/secrets.toml with defaults."""
    secrets_dir = Path(".streamlit")
    secrets_file = secrets_dir / "secrets.toml"
    
    secrets_dir.mkdir(exist_ok=True)
    
    if secrets_file.exists():
        print(f"✓ {secrets_file} already exists (not overwriting)\n")
        return
    
    hashed_pw = generate_password()
    if not hashed_pw:
        return
    
    content = f"""# SamiX Secrets (Auto-generated)
# IMPORTANT: Change default credentials!

[auth]
hashed_password = "{hashed_pw}"
cookie_key = "change-this-in-production"
admin_name = "Administrator"
admin_email = "admin@samix.ai"

[groq]
api_key = "gsk_replace_with_your_key"

[deepgram]
api_key = "replace_with_your_key"
"""
    
    secrets_file.write_text(content)
    print(f"✓ Created {secrets_file}\n")
    print("⚠ Update the API keys before deploying!\n")

def run_validation():
    """Run pre-flight validation."""
    print("Running pre-flight checks...\n")
    
    try:
        subprocess.run([sys.executable, "validate.py"], check=True)
        return True
    except subprocess.CalledProcessError:
        print("\n⚠ Some validation checks failed. Continuing anyway...\n")
        return False

def launch_app():
    """Launch the Streamlit app."""
    print("="*70)
    print("Launching SamiX...")
    print("="*70)
    print("\nOpening http://localhost:8501 in your browser...")
    print("Default credentials: admin@samix.ai / admin\n")
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n\nApplication stopped.")
    except Exception as e:
        print(f"\n❌ Error launching app: {e}")
        print("Try running manually: streamlit run app.py")

def main():
    print_banner()
    
    if not check_requirements():
        return 1
    
    if not install_dependencies():
        return 1
    
    setup_secrets()
    
    # run_validation()  # Optional: skip for faster startup
    
    launch_app()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
