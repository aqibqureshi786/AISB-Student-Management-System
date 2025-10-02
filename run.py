"""
Simple startup script for AISB Student Management System
"""
import subprocess
import sys
import os

def check_requirements():
    """Check if required packages are installed"""
    try:
        import streamlit
        import pandas
        print("✅ Basic requirements found")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("⚠️  .env file not found")
        print("Please copy env_example.txt to .env and update with your values")
        print("The system will run in development mode with mock data")
    else:
        print("✅ .env file found")

def main():
    print("🎓 AISB Student Management System")
    print("=" * 40)
    
    if not check_requirements():
        return
    
    check_env_file()
    
    print("\n🚀 Starting the application...")
    print("The application will open in your default web browser")
    print("Press Ctrl+C to stop the application")
    print("-" * 40)
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "main.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped")

if __name__ == "__main__":
    main()
