#!/usr/bin/env python3
"""
Startup Script - Payment Orchestrator Web Interface
Starts both FastAPI backend and Streamlit frontend
"""

import subprocess
import sys
import time
import signal
import os

def print_banner():
    """Print startup banner"""
    print("=" * 80)
    print("  PAYMENT PROCESSING ORCHESTRATOR - WEB INTERFACE")
    print("  Standard Bank / ZenLabs - October 2025")
    print("=" * 80)
    print()

def check_dependencies():
    """Check if required packages are installed"""
    required = [
        "fastapi",
        "uvicorn",
        "streamlit",
        "plotly",
        "pandas",
        "requests"
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ Missing required packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print()
        print("Install missing packages with:")
        print("   pip install -r requirements_web.txt --break-system-packages")
        print()
        return False
    
    return True

def start_api_server():
    """Start FastAPI server"""
    print("🚀 Starting FastAPI backend server...")
    print("   URL: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    print()
    
    # Use 'start' command on Windows to open in new window
    if sys.platform == "win32":
        subprocess.Popen(
            f'start "API Server" cmd /k python api_server.py',
            shell=True,
            cwd=os.getcwd()
        )
    else:
        subprocess.Popen(["python", "api_server.py"])
    
    # Wait for API to be ready
    print("⏳ Waiting for API server to be ready...")
    time.sleep(5)
    
    # Check if API is running
    import requests
    for attempt in range(10):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ API server is ready!")
                print()
                return True
        except:
            if attempt < 9:
                time.sleep(1)
            else:
                print("⚠️ Could not verify API health, but continuing...")
                return True
    return True

def start_streamlit_ui():
    """Start Streamlit UI"""
    print("🎨 Starting Streamlit UI...")
    print("   URL: http://localhost:8501")
    print()
    
    # Use 'start' command on Windows to open in new window
    if sys.platform == "win32":
        subprocess.Popen(
            f'start "Streamlit UI" cmd /k python -m streamlit run streamlit_ui.py --server.port=8501 --server.headless=true',
            shell=True,
            cwd=os.getcwd()
        )
    else:
        subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "streamlit_ui.py", 
             "--server.port=8501", "--server.headless=true"]
        )
    
    time.sleep(5)
    print("✅ Streamlit UI is ready!")
    print()
    
    return True

def main():
    """Main startup function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start servers
    try:
        start_api_server()
        start_streamlit_ui()
        
        print("=" * 80)
        print("  ✅ PAYMENT ORCHESTRATOR WEB INTERFACE IS RUNNING")
        print("=" * 80)
        print()
        print("Access the application:")
        print("  🎨 Streamlit UI:  http://localhost:8501")
        print("  🔌 FastAPI:       http://localhost:8000")
        print("  📚 API Docs:      http://localhost:8000/docs")
        print()
        print("Press Ctrl+C to stop all servers (close the server windows)")
        print("=" * 80)
        print()
        
        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n")
            print("🛑 Shutting down servers...")
            print("   Please close the API Server and Streamlit UI windows")
            print("✅ All servers stopped")
            
    except Exception as e:
        print(f"❌ Error starting servers: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
