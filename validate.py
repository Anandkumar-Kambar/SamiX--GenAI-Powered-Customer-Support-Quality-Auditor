"""
SamiX Pre-Flight Validation Script

Validates that the environment is properly configured before running the application.
Run this script to diagnose configuration issues.

Usage:
    python validate.py
"""
import sys
import os
from pathlib import Path
from importlib import import_module

def check_python_version():
    """Verify Python version is 3.11 or higher."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python {version.major}.{version.minor} detected")
        print(f"   Required: Python 3.11+")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_directories():
    """Verify all required directories exist."""
    required_dirs = [
        "data",
        "data/auth",
        "data/kb",
        "data/history",
        "data/uploads",
        "src",
        "src/auth",
        "src/pipeline",
        "src/ui",
        "src/utils",
        ".streamlit",
    ]
    
    ok = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✓ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ (missing)")
            ok = False
    
    return ok

def check_files():
    """Verify all critical files exist."""
    required_files = [
        "app.py",
        "config.py",
        "requirements.txt",
        ".env",
        ".streamlit/secrets.toml",
        "src/auth/authenticator.py",
        "src/pipeline/groq_client.py",
        "src/pipeline/stt_processor.py",
        "src/ui/login_page.py",
        "src/utils/kb_manager.py",
    ]
    
    ok = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            print(f"❌ {file_path} (missing)")
            ok = False
    
    return ok

def check_dependencies():
    """Verify all required packages are installed."""
    required_packages = [
        "streamlit",
        "groq",
        "streamlit_authenticator",
        "langchain",
        "pymilvus",
        "bcrypt",
        "pydub",
        "dotenv",
        "yaml",
    ]
    
    print("\nChecking dependencies...")
    missing = []
    
    for package in required_packages:
        try:
            import_module(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"❌ {package} (not installed)")
            missing.append(package)
    
    if missing:
        print(f"\n⚠ Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    return True

def check_environment_variables():
    """Check for required API keys."""
    print("\nChecking environment variables...")
    
    # Try loading from config
    try:
        from config import Config
        
        groq_key = Config.get_groq_api_key()
        if groq_key == "NOT_CONFIGURED" or "your_" in groq_key.lower():
            print("❌ GROQ_API_KEY not configured")
            return False
        else:
            print(f"✓ GROQ_API_KEY configured (starts with: {groq_key[:8]}...)")
        
        deepgram_key = Config.get_deepgram_api_key()
        if "your_" in deepgram_key.lower():
            print("ℹ DEEPGRAM_API_KEY not configured (will use local Whisper)")
        else:
            print(f"✓ DEEPGRAM_API_KEY configured (starts with: {deepgram_key[:8]}...)")
        
        return True
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False

def check_file_permissions():
    """Verify write permissions for required directories."""
    print("\nChecking file permissions...")
    
    writable_dirs = [
        "data",
        "logs",
        ".streamlit",
    ]
    
    ok = True
    for dir_path in writable_dirs:
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        
        test_file = path / ".write_test"
        try:
            test_file.touch()
            test_file.unlink()
            print(f"✓ {dir_path}/ is writable")
        except Exception as e:
            print(f"❌ {dir_path}/ is not writable: {e}")
            ok = False
    
    return ok

def main():
    """Run all validation checks."""
    print("\n" + "="*70)
    print("SamiX Pre-Flight Validation")
    print("="*70 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Directories", check_directories),
        ("Required Files", check_files),
        ("Dependencies", check_dependencies),
        ("Environment Variables", check_environment_variables),
        ("File Permissions", check_file_permissions),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        print("-" * 70)
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Error during validation: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("Validation Summary")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status:10} {check_name}")
    
    print(f"\nResult: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✓ All checks passed! Ready to run:")
        print("  streamlit run app.py")
        return 0
    else:
        print("\n⚠ Some checks failed. Review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
