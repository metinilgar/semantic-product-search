"""
ShopSearchAgent - Development runner script
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def check_requirements():
    """Check if requirements are installed"""
    try:
        import fastapi
        import uvicorn
        import qdrant_client
        import google.generativeai
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Run: pip install -r requirements.txt")
        return False


def check_env_file():
    """Check if .env file exists and has required variables"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        print("Copy .env.example to .env and add your GEMINI_API_KEY")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
        if "GEMINI_API_KEY=" not in content or "your_gemini_api_key_here" in content:
            print("❌ GEMINI_API_KEY not set in .env file")
            return False
    
    print("✅ Environment configuration found")
    return True


def check_qdrant():
    """Check if Qdrant is running"""
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(url="http://localhost:6333")
        collections = client.get_collections()
        print("✅ Qdrant is running and accessible")
        return True
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
        print("Start Qdrant with: docker run -p 6333:6333 qdrant/qdrant")
        return False


def run_tests():
    """Run unit tests"""
    print("🧪 Running tests...")
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ All tests passed")
        print(result.stdout)
    else:
        print("❌ Tests failed")
        print(result.stderr)
    
    return result.returncode == 0


def run_server(host="0.0.0.0", port=8000, reload=True):
    """Run the FastAPI server"""
    print(f"🚀 Starting ShopSearchAgent server on {host}:{port}")
    
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "app.main:app",
        "--host", host,
        "--port", str(port)
    ]
    
    if reload:
        cmd.append("--reload")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\\n👋 Server stopped")


def setup_environment():
    """Setup development environment"""
    print("🔧 Setting up development environment...")
    
    # Create .env from example if it doesn't exist
    if not Path(".env").exists() and Path(".env.example").exists():
        import shutil
        shutil.copy(".env.example", ".env")
        print("📝 Created .env file from .env.example")
        print("⚠️  Please edit .env and add your GEMINI_API_KEY")
    
    # Install requirements
    print("📦 Installing requirements...")
    result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    if result.returncode == 0:
        print("✅ Setup complete")
    else:
        print("❌ Setup failed")


def main():
    parser = argparse.ArgumentParser(description="ShopSearchAgent Development Tools")
    parser.add_argument("command", choices=["setup", "check", "test", "run"], 
                       help="Command to execute")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        setup_environment()
    
    elif args.command == "check":
        print("🔍 Checking system requirements...")
        checks = [
            check_requirements(),
            check_env_file(),
            check_qdrant()
        ]
        
        if all(checks):
            print("\\n✅ All checks passed! Ready to run.")
        else:
            print("\\n❌ Some checks failed. Please fix the issues above.")
            sys.exit(1)
    
    elif args.command == "test":
        if not run_tests():
            sys.exit(1)
    
    elif args.command == "run":
        # Quick checks before running
        if not check_requirements() or not check_env_file():
            print("❌ Pre-run checks failed")
            sys.exit(1)
        
        run_server(args.host, args.port, not args.no_reload)


if __name__ == "__main__":
    main()