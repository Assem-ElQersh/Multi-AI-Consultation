#!/usr/bin/env python3
"""
Convenient launcher for the Multi-AI Consultation System.
This script provides an easy way to start the system with pre-checks.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_system_ready():
    """Quick system readiness check"""
    print("🔍 Checking system readiness...")
    
    issues = []
    
    # Check if main files exist
    required_files = [
        'multi_ai_consultation.py',
        'specialized_legal_prompts.py', 
        'legal_rag_system.py'
    ]
    
    for file in required_files:
        if not Path(file).exists():
            issues.append(f"Missing file: {file}")
    
    # Check Ollama availability
    try:
        import ollama
        # Try to connect
        ollama.generate(model='llama2', prompt='test')
        print("   ✅ Ollama connection working")
    except ImportError:
        issues.append("Ollama Python client not installed")
    except Exception as e:
        issues.append(f"Ollama connection failed: {e}")
    
    # Check for legal documents
    legal_dir = Path("legal_docs")
    if legal_dir.exists():
        pdf_count = len(list(legal_dir.glob("*.pdf")))
        if pdf_count > 0:
            print(f"   ✅ Found {pdf_count} legal documents")
        else:
            print("   ⚠️ No legal PDFs found (Legal-AI will use basic knowledge)")
    else:
        print("   ⚠️ No legal_docs directory (Legal-AI will use basic knowledge)")
    
    if issues:
        print("\n❌ System not ready:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nRun: python setup_multi_ai.py")
        return False
    
    print("   ✅ All systems ready!")
    return True

def main():
    """Main launcher function"""
    print("🎯 MULTI-AI CONSULTATION SYSTEM LAUNCHER")
    print("=" * 50)
    
    if not check_system_ready():
        sys.exit(1)
    
    print("\n🚀 Starting Multi-AI Consultation System...\n")
    
    try:
        from multi_ai_consultation import main as run_consultation
        run_consultation()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting system: {e}")
        print("Try running: python multi_ai_consultation.py")

if __name__ == "__main__":
    main()
