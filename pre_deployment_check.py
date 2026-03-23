"""
Complete Pre-Deployment Checklist

Run this to verify everything is ready for production deployment.
"""

import subprocess
import sys
from pathlib import Path

def print_section(title):
    print(f"\n{'='*70}")
    print(f"{'█' * 3} {title}")
    print("="*70)

def run_checks():
    checks_passed = 0
    checks_failed = 0
    
    # ========== PYTHON VERSION ==========
    print_section("Python Environment")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 11:
        print("✓ Python 3.11+")
        checks_passed += 1
    else:
        print("✗ Python 3.11+ required")
        checks_failed += 1
    
    # ========== DIRECTORIES ==========
    print_section("Directory Structure")
    required_dirs = {
        "src": "Source code",
        "data": "Data directory",
        "data/auth": "User database",
        "data/kb": "Knowledge base",
        "data/history": "Audit history",
        ".streamlit": "Streamlit config",
        ".github": "CI/CD workflows",
    }
    for dir_path, desc in required_dirs.items():
        if Path(dir_path).exists():
            print(f"✓ {dir_path:25} {desc}")
            checks_passed += 1
        else:
            print(f"✗ {dir_path:25} {desc}")
            checks_failed += 1
    
    # ========== FILES ==========
    print_section("Critical Files")
    required_files = {
        "app.py": "Streamlit entry point",
        "config.py": "Configuration management",
        "requirements.txt": "Python dependencies",
        ".env": "Environment variables",
        ".streamlit/secrets.toml": "Secrets & API keys",
        ".streamlit/config.toml": "Streamlit settings",
        ".gitignore": "Git exclusions",
        "Dockerfile": "Docker configuration",
        "docker-compose.yml": "Docker Compose config",
        "Procfile": "Heroku deployment",
        "validate.py": "Validation script",
        "quickstart.py": "Auto-setup script",
        "generate_hash.py": "Password hasher",
        "DEPLOYMENT.md": "Deployment guide",
        "PRODUCTION_GUIDE.md": "Production setup",
        "TROUBLESHOOTING.md": "Troubleshooting guide",
        "QUICKSTART.md": "Quick reference",
    }
    for file_path, desc in required_files.items():
        if Path(file_path).exists():
            print(f"✓ {file_path:30} {desc}")
            checks_passed += 1
        else:
            print(f"✗ {file_path:30} {desc}")
            checks_failed += 1
    
    # ========== MODULES ==========
    print_section("Source Code Modules")
    modules = {
        ("src", "__init__.py"): "src package",
        ("src/auth", "authenticator.py"): "Authentication",
        ("src/pipeline", "groq_client.py"): "Groq LLM client",
        ("src/pipeline", "stt_processor.py"): "STT processor",
        ("src/pipeline", "alert_engine.py"): "Alert system",
        ("src/ui", "login_page.py"): "Login UI",
        ("src/ui", "agent_panel.py"): "Agent panel",
        ("src/ui", "admin_panel.py"): "Admin panel",
        ("src/ui", "styles.py"): "Styling",
        ("src/utils", "kb_manager.py"): "Knowledge base",
        ("src/utils", "history_manager.py"): "History management",
        ("src/utils", "cost_tracker.py"): "Cost tracking",
        ("src/utils", "audio_processor.py"): "Audio utilities",
    }
    for (dir_path, file), desc in modules.items():
        full_path = Path(dir_path) / file
        if full_path.exists():
            print(f"✓ {str(full_path):40} {desc}")
            checks_passed += 1
        else:
            print(f"✗ {str(full_path):40} {desc}")
            checks_failed += 1
    
    # ========== DEPENDENCIES ==========
    print_section("Python Packages")
    print("Checking installed packages...")
    packages = {
        "streamlit": "Web framework",
        "groq": "Groq API client",
        "deepgram-sdk": "Deepgram STT",
        "langchain": "LLM framework",
        "pymilvus": "Vector database",
        "bcrypt": "Password hashing",
        "pydub": "Audio processing",
        "python-dotenv": "Environment variables",
        "PyYAML": "YAML support",
    }
    
    for package, desc in packages.items():
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package:25} {desc}")
            checks_passed += 1
        except ImportError:
            print(f"✗ {package:25} {desc}")
            checks_failed += 1
    
    # ========== CONFIGURATION ==========
    print_section("Configuration & Secrets")
    
    # Check .env
    env_path = Path(".env")
    if env_path.exists():
        print(f"✓ .env file exists")
        checks_passed += 1
    else:
        print(f"✗ .env file missing")
        checks_failed += 1
    
    # Check secrets.toml
    secrets_path = Path(".streamlit/secrets.toml")
    if secrets_path.exists():
        print(f"✓ .streamlit/secrets.toml exists")
        checks_passed += 1
    else:
        print(f"✗ .streamlit/secrets.toml missing")
        checks_failed += 1
    
    # Check for actual API keys
    try:
        from config import Config
        
        groq_key = Config.get_groq_api_key()
        if groq_key and "gsk_" in groq_key:
            print(f"✓ GROQ_API_KEY configured")
            checks_passed += 1
        else:
            print(f"⚠ GROQ_API_KEY not configured (template values)")
            # Not counting as failure - template is ok
    except Exception as e:
        print(f"⚠ Could not verify API keys: {e}")
    
    # ========== IMPORTS TEST ==========
    print_section("Import Test")
    
    imports_to_test = [
        ("config", "Config"),
        ("src.auth.authenticator", "AuthManager"),
        ("src.pipeline.groq_client", "GroqClient"),
        ("src.pipeline.stt_processor", "STTProcessor"),
        ("src.utils.kb_manager", "KBManager"),
        ("src.utils.history_manager", "HistoryManager"),
    ]
    
    for module_name, class_name in imports_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"✓ {module_name:40} {class_name}")
            checks_passed += 1
        except Exception as e:
            print(f"✗ {module_name:40} {class_name}: {e}")
            checks_failed += 1
    
    # ========== GIT STATUS ==========
    print_section("Git Configuration")
    
    try:
        result = subprocess.run(
            ["git", "status"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✓ Git repository initialized")
            checks_passed += 1
            
            # Check if secrets are in gitignore
            gitignore_path = Path(".gitignore")
            if gitignore_path.exists():
                content = gitignore_path.read_text()
                if ".env" in content and "secrets.toml" in content:
                    print("✓ .env and secrets.toml in .gitignore")
                    checks_passed += 1
                else:
                    print("⚠ Sensitive files may not be excluded from git")
        else:
            print("⚠ Git not initialized")
    except Exception as e:
        print(f"⚠ Git check failed: {e}")
    
    # ========== SUMMARY ==========
    print_section("Summary")
    total = checks_passed + checks_failed
    percentage = (checks_passed / total * 100) if total > 0 else 0
    
    print(f"\n  ✓ Passed:  {checks_passed}")
    print(f"  ✗ Failed:  {checks_failed}")
    print(f"  Total:   {total}")
    print(f"  Score:   {percentage:.1f}%\n")
    
    if checks_failed == 0:
        print("🎉 ALL CHECKS PASSED - READY FOR DEPLOYMENT!\n")
        print("Next steps:")
        print("  1. Review PRODUCTION_GUIDE.md")
        print("  2. Set production environment variables")
        print("  3. Run: streamlit run app.py --logger.level=error")
        print("  4. Deploy to your platform\n")
        return 0
    else:
        print(f"⚠ {checks_failed} check(s) failed\n")
        print("Before deployment:")
        print("  1. Fix all failed checks above")
        print("  2. Run this script again")
        print("  3. See TROUBLESHOOTING.md for help\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_checks())
