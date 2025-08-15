# setup_multi_ai.py
"""
Setup script for the Multi-AI Consultation System.
Installs dependencies and guides through Ollama setup.
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_pip_packages():
    """Install required Python packages"""
    packages = [
        'ollama',
        'sentence-transformers',
        'scikit-learn',
        'numpy',
        'PyPDF2',
        'PyMuPDF',
        'Pillow',
        'pytesseract'
    ]
    
    print("\n📦 Installing Python packages...")
    
    for package in packages:
        print(f"   Installing {package}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package], 
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
            print(f"   ✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"   ⚠️ {package} installation failed (optional for some features)")

def check_ollama_installation():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Ollama not found")
    return False

def install_ollama_instructions():
    """Provide Ollama installation instructions"""
    system = platform.system().lower()
    
    print("\n🤖 OLLAMA INSTALLATION REQUIRED")
    print("Ollama provides the local AI models for the consultation system.")
    print("\nInstallation instructions:")
    
    if system == "windows":
        print("1. Download Ollama for Windows from: https://ollama.ai/download")
        print("2. Run the installer")
        print("3. Restart your terminal/command prompt")
    elif system == "darwin":  # macOS
        print("1. Install using Homebrew: brew install ollama")
        print("   OR download from: https://ollama.ai/download")
    elif system == "linux":
        print("1. Run: curl -fsSL https://ollama.ai/install.sh | sh")
        print("   OR download from: https://ollama.ai/download")
    
    print("\n🔄 After installing Ollama, restart this setup script.")

def setup_ollama_models():
    """Download required Ollama models"""
    if not check_ollama_installation():
        install_ollama_instructions()
        return False
    
    models = [
        'llama2',           # Main model for AI responses
        'llama2:13b',       # Larger model for complex legal analysis (optional)
        'codellama',        # For technical AI responses (optional)
    ]
    
    print("\n🔄 Setting up AI models...")
    print("This may take a while as models are large (several GB each)")
    
    # Check which models are already available
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        installed_models = result.stdout
    except:
        installed_models = ""
    
    for model in models:
        if model in installed_models:
            print(f"   ✅ {model} already installed")
            continue
        
        print(f"   📥 Downloading {model}...")
        if model == 'llama2':
            # This is required
            try:
                subprocess.check_call(['ollama', 'pull', model])
                print(f"   ✅ {model} installed successfully")
            except subprocess.CalledProcessError:
                print(f"   ❌ Failed to install {model}")
                return False
        else:
            # These are optional
            try:
                print(f"      (Optional model - you can skip with Ctrl+C)")
                subprocess.check_call(['ollama', 'pull', model])
                print(f"   ✅ {model} installed successfully")
            except (subprocess.CalledProcessError, KeyboardInterrupt):
                print(f"   ⏭️ Skipped {model} (optional)")
    
    return True

def setup_legal_documents():
    """Set up legal documents directory"""
    legal_dir = Path("legal_docs")
    
    if not legal_dir.exists():
        legal_dir.mkdir()
        print("📁 Created legal_docs directory")
        print("   Add your PDF legal documents to this folder")
    else:
        pdf_count = len(list(legal_dir.glob("*.pdf")))
        print(f"📁 Legal docs directory exists with {pdf_count} PDF files")
    
    return True

def test_system():
    """Test if the system works"""
    print("\n🧪 Testing system components...")
    
    # Test imports
    try:
        import ollama
        print("   ✅ Ollama Python client")
    except ImportError:
        print("   ❌ Ollama Python client not available")
        return False
    
    try:
        from sentence_transformers import SentenceTransformer
        print("   ✅ Sentence transformers")
    except ImportError:
        print("   ❌ Sentence transformers not available")
        return False
    
    # Test Ollama connection
    try:
        response = ollama.generate(model='llama2', prompt='Test')
        print("   ✅ Ollama connection working")
    except Exception as e:
        print(f"   ❌ Ollama connection failed: {e}")
        return False
    
    print("   ✅ All systems operational!")
    return True

def create_launch_script():
    """Create a convenient launch script"""
    script_content = """#!/usr/bin/env python3
# Launch script for Multi-AI Consultation System

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_ai_consultation import main

if __name__ == "__main__":
    main()
"""
    
    with open("launch_consultation.py", "w") as f:
        f.write(script_content)
    
    print("🚀 Created launch_consultation.py - use this to start the system")

def main():
    """Main setup function"""
    print("🎯 MULTI-AI CONSULTATION SYSTEM SETUP")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install packages
    install_pip_packages()
    
    # Setup Ollama
    if not setup_ollama_models():
        print("\n⚠️ Setup incomplete. Please install Ollama and run setup again.")
        return
    
    # Setup legal documents
    setup_legal_documents()
    
    # Test system
    if test_system():
        print("\n🎉 SETUP COMPLETE!")
        print("\nYour Multi-AI Consultation System is ready!")
        print("\nTo start:")
        print("   python multi_ai_consultation.py")
        print("   OR")
        print("   python launch_consultation.py")
        
        create_launch_script()
        
        print("\n💡 Tips:")
        print("   - Add PDF legal documents to the 'legal_docs' folder")
        print("   - The Legal-AI will have access to actual legal knowledge")
        print("   - AIs will debate and provide multiple perspectives")
        print("   - Type 'quit' to end a consultation session")
        
    else:
        print("\n❌ Setup encountered issues. Check error messages above.")

if __name__ == "__main__":
    main()
