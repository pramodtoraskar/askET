#!/usr/bin/env python3
"""
Launcher script for Ask ET Web Interface
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_streamlit_app(app_type="basic"):
    """Run the Streamlit web application"""
    
    if app_type == "basic":
        app_file = "src/web_app.py"
        port = 8501
    elif app_type == "advanced":
        app_file = "src/web_app_advanced.py"
        port = 8502
    elif app_type == "minimal":
        app_file = "src/web_app_minimal.py"
        port = 8503
    else:
        print(f"Unknown app type: {app_type}")
        return
    
    if not Path(app_file).exists():
        print(f"Error: {app_file} not found!")
        return
    
    print(f"Starting Ask ET {app_type.title()} Web Interface...")
    print(f"App file: {app_file}")
    print(f"Port: {port}")
    print(f"URL: http://localhost:{port}")
    if app_type == "minimal":
        print("Design: Red Hat Emerging Technologies inspired minimal interface")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        # Run streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            app_file, 
            "--server.port", str(port),
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\nShutting down web interface...")
    except Exception as e:
        print(f"Error running web interface: {e}")

def install_dependencies():
    """Install web dependencies"""
    print("Installing web dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements_web.txt"
        ], check=True)
        print("Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False
    return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Ask ET Web Interface Launcher")
    parser.add_argument(
        "--app", 
        choices=["basic", "advanced", "minimal"], 
        default="basic",
        help="Choose web app type (default: basic)"
    )
    parser.add_argument(
        "--install", 
        action="store_true",
        help="Install web dependencies before running"
    )
    parser.add_argument(
        "--port", 
        type=int,
        help="Custom port number (default: 8501 for basic, 8502 for advanced, 8503 for minimal)"
    )
    
    args = parser.parse_args()
    
    # Install dependencies if requested
    if args.install:
        if not install_dependencies():
            return
    
    # Run the app
    run_streamlit_app(args.app)

if __name__ == "__main__":
    main() 