"""
Web Server Launcher for Filum.ai Pain Point to Solution Agent
===========================================================

This script launches the FastAPI web server for the Pain Point Agent.

Usage:
    python web/server.py [--host HOST] [--port PORT] [--reload]

Example:
    python web/server.py --host 0.0.0.0 --port 8000 --reload
    python web/server.py  # Default: localhost:8000
"""

import sys
import argparse
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Kiểm tra các dependencies cần thiết"""
    required_packages = [
        'fastapi', 'uvicorn', 'jinja2', 'python-multipart'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print(f"Please install them using:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_knowledge_base():
    """Kiểm tra knowledge base file"""
    kb_path = project_root / "data" / "knowledge_base.json"
    if not kb_path.exists():
        print(f"❌ Knowledge base not found: {kb_path}")
        print("Please ensure knowledge_base.json exists in the data/ directory")
        return False
    
    print(f"✅ Knowledge base found: {kb_path}")
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Launch Filum.ai Pain Point Agent Web Server"
    )
    parser.add_argument(
        '--host', 
        default='127.0.0.1',
        help='Host to bind the server (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port', 
        type=int, 
        default=8000,
        help='Port to bind the server (default: 8000)'
    )
    parser.add_argument(
        '--reload', 
        action='store_true',
        help='Enable auto-reload for development'
    )
    parser.add_argument(
        '--log-level',
        choices=['critical', 'error', 'warning', 'info', 'debug', 'trace'],
        default='info',
        help='Log level (default: info)'
    )
    
    args = parser.parse_args()
    
    print("🚀 Starting Filum.ai Pain Point to Solution Agent Web Server...")
    print(f"📁 Project root: {project_root}")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check knowledge base
    if not check_knowledge_base():
        sys.exit(1)
    
    try:
        import uvicorn
        
        print(f"🌐 Server will start at: http://{args.host}:{args.port}")
        print(f"📚 API Documentation: http://{args.host}:{args.port}/docs")
        print(f"🔄 Auto-reload: {'Enabled' if args.reload else 'Disabled'}")
        print("-" * 60)
        
        # Import and run the FastAPI app
        from web.app import app
        
        uvicorn.run(
            "web.app:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
            access_log=True
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
