#!/usr/bin/env python3
"""
Payment Orchestrator Startup Manager
Helps start API server and Streamlit UI with proper checks
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                          ║")
    print("║   🚀 PAYMENT ORCHESTRATOR - STARTUP MANAGER                              ║")
    print("║   AI-Powered Payment Routing System                                     ║")
    print("║                                                                          ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝")
    print()

def check_port_available(port):
    """Check if a port is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result != 0  # True if port is available

def check_api_health():
    """Check if API server is running and healthy"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def kill_process_on_port(port):
    """Kill process running on given port"""
    try:
        if sys.platform == "win32":
            subprocess.run(f'netstat -ano | findstr :{port}', shell=True, capture_output=True)
        else:
            result = subprocess.run(f'lsof -ti:{port}', shell=True, capture_output=True, text=True)
            if result.stdout:
                pid = result.stdout.strip()
                subprocess.run(f'kill -9 {pid}', shell=True)
                print(f"✓ Killed process on port {port}")
                return True
    except Exception as e:
        print(f"⚠️  Could not kill process on port {port}: {e}")
    return False

def start_api_server():
    """Start the API server"""
    print("═══════════════════════════════════════════════════════════════════════════")
    print("Starting API Server...")
    print("═══════════════════════════════════════════════════════════════════════════")
    print()
    
    # Check if port is available
    if not check_port_available(8000):
        print("⚠️  Port 8000 is already in use!")
        choice = input("Kill existing process and restart? (y/n): ")
        if choice.lower() == 'y':
            kill_process_on_port(8000)
            time.sleep(2)
        else:
            print("❌ Cannot start API server (port 8000 in use)")
            return None
    
    # Check if api_server.py exists
    if not os.path.exists("api_server.py"):
        print("❌ Error: api_server.py not found in current directory")
        print("   Please cd to /mnt/user-data/outputs first")
        return None
    
    # Start API server
    print("Starting API server on http://localhost:8000")
    print("API docs will be at: http://localhost:8000/docs")
    print()
    
    try:
        # Start in background
        if sys.platform == "win32":
            process = subprocess.Popen(
                ["python", "api_server.py"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            process = subprocess.Popen(
                ["python", "api_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setpgrp
            )
        
        # Wait for API to be ready
        print("Waiting for API server to start", end="")
        for i in range(30):  # 30 seconds timeout
            time.sleep(1)
            print(".", end="", flush=True)
            if check_api_health():
                print("\n✅ API Server started successfully!")
                print("   Available at: http://localhost:8000")
                return process
        
        print("\n⚠️  API server started but health check failed")
        print("   Check the terminal for errors")
        return process
        
    except Exception as e:
        print(f"\n❌ Failed to start API server: {e}")
        return None

def start_streamlit():
    """Start Streamlit UI"""
    print()
    print("═══════════════════════════════════════════════════════════════════════════")
    print("Starting Streamlit UI...")
    print("═══════════════════════════════════════════════════════════════════════════")
    print()
    
    # Check if API is running
    if not check_api_health():
        print("❌ Error: API server must be running first!")
        print("   Please start the API server in another terminal:")
        print("   python api_server.py")
        return None
    
    # Check if port is available
    if not check_port_available(8501):
        print("⚠️  Port 8501 is already in use!")
        choice = input("Kill existing Streamlit and restart? (y/n): ")
        if choice.lower() == 'y':
            kill_process_on_port(8501)
            time.sleep(2)
        else:
            print("❌ Cannot start Streamlit (port 8501 in use)")
            return None
    
    # Check if streamlit_ui.py exists
    if not os.path.exists("streamlit_ui.py"):
        print("❌ Error: streamlit_ui.py not found in current directory")
        print("   Please cd to /mnt/user-data/outputs first")
        return None
    
    # Start Streamlit
    print("Starting Streamlit UI on http://localhost:8501")
    print()
    
    try:
        if sys.platform == "win32":
            process = subprocess.Popen(
                ["streamlit", "run", "streamlit_ui.py"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            process = subprocess.Popen(
                ["streamlit", "run", "streamlit_ui.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        # Wait a bit for Streamlit to start
        time.sleep(3)
        
        print("✅ Streamlit UI started successfully!")
        print("   Open your browser to: http://localhost:8501")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start Streamlit: {e}")
        return None

def main():
    """Main startup function"""
    print_banner()
    
    # Change to outputs directory if not already there
    if not os.path.exists("api_server.py"):
        outputs_dir = Path("/mnt/user-data/outputs")
        if outputs_dir.exists():
            os.chdir(outputs_dir)
            print(f"Changed directory to: {outputs_dir}")
        else:
            print("❌ Error: Could not find /mnt/user-data/outputs directory")
            sys.exit(1)
    
    print("What would you like to start?")
    print()
    print("  1) API Server only")
    print("  2) Streamlit UI only (API must be running already)")
    print("  3) Both (API server first, then Streamlit)")
    print("  4) Check status")
    print()
    
    try:
        choice = input("Enter your choice (1-4): ").strip()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(0)
    
    if choice == "1":
        api_process = start_api_server()
        if api_process:
            print()
            print("API Server is running!")
            print("Press Ctrl+C to stop (will terminate this script)")
            try:
                api_process.wait()
            except KeyboardInterrupt:
                print("\n\nStopping API server...")
                api_process.terminate()
                
    elif choice == "2":
        streamlit_process = start_streamlit()
        if streamlit_process:
            print()
            print("Streamlit UI is running!")
            print("Press Ctrl+C to stop (will terminate this script)")
            try:
                streamlit_process.wait()
            except KeyboardInterrupt:
                print("\n\nStopping Streamlit...")
                streamlit_process.terminate()
                
    elif choice == "3":
        # Start API first
        api_process = start_api_server()
        if not api_process:
            print("\n❌ Cannot continue without API server")
            sys.exit(1)
        
        # Wait a moment
        time.sleep(2)
        
        # Start Streamlit
        streamlit_process = start_streamlit()
        
        if api_process and streamlit_process:
            print()
            print("═══════════════════════════════════════════════════════════════════════════")
            print("✅ BOTH SERVERS ARE RUNNING!")
            print("═══════════════════════════════════════════════════════════════════════════")
            print()
            print("  API Server: http://localhost:8000")
            print("  Streamlit UI: http://localhost:8501")
            print()
            print("Open your browser to: http://localhost:8501")
            print()
            print("Press Ctrl+C to stop both servers...")
            print()
            
            try:
                # Keep running until interrupted
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\nStopping servers...")
                streamlit_process.terminate()
                api_process.terminate()
                print("✓ Servers stopped")
                
    elif choice == "4":
        print()
        print("═══════════════════════════════════════════════════════════════════════════")
        print("Checking System Status...")
        print("═══════════════════════════════════════════════════════════════════════════")
        print()
        
        # Check API
        api_running = check_api_health()
        if api_running:
            print("✅ API Server: RUNNING on http://localhost:8000")
        else:
            print("❌ API Server: NOT RUNNING")
        
        # Check Streamlit
        streamlit_running = not check_port_available(8501)
        if streamlit_running:
            print("✅ Streamlit UI: RUNNING on http://localhost:8501")
        else:
            print("❌ Streamlit UI: NOT RUNNING")
        
        print()
        if api_running and streamlit_running:
            print("✅ System is fully operational!")
        elif api_running:
            print("⚠️  API is running but Streamlit is not")
            print("   Start Streamlit: streamlit run streamlit_ui.py")
        elif streamlit_running:
            print("⚠️  Streamlit is running but API is not")
            print("   Start API: python api_server.py")
        else:
            print("❌ System is not running")
            print("   Start both: python start_manager.py (choose option 3)")
            
    else:
        print("❌ Invalid choice")
        sys.exit(1)

if __name__ == "__main__":
    main()