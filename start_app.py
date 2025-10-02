"""
Startup script that ensures virtual environment is used
"""
import subprocess
import sys
import os

def start_application():
    print("🎓 AISB Student Management System")
    print("=" * 40)
    
    # Check if we're in virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if in_venv:
        print("✅ Virtual environment detected")
    else:
        print("⚠️  Not in virtual environment")
        print("Please activate virtual environment first:")
        print("   .\\venv\\Scripts\\activate")
        return
    
    # Test imports
    try:
        import streamlit
        import crewai
        import firebase_admin
        print("✅ All required packages available")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return
    
    print("\n🚀 Starting AISB Student Management System...")
    print("The application will open in your browser")
    print("Press Ctrl+C to stop")
    print("-" * 40)
    
    try:
        # Use the simple main file to avoid import issues
        subprocess.run([sys.executable, "-m", "streamlit", "run", "main_simple.py"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("\nTrying alternative method...")
        try:
            subprocess.run(["streamlit", "run", "main_simple.py"])
        except Exception as e2:
            print(f"❌ Alternative method also failed: {e2}")
            print("\nPlease try manually:")
            print("   streamlit run main_simple.py")

if __name__ == "__main__":
    start_application()
