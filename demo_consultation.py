#!/usr/bin/env python3
"""
Demonstration script showing the Multi-AI Consultation System capabilities.
Runs a scripted conversation to showcase AI-to-AI interactions.
"""

import sys
import os
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def simulate_typing(text, delay=0.03):
    """Simulate typing effect for demo"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def demo_consultation():
    """Run a demonstration consultation"""
    
    print("🎯 MULTI-AI CONSULTATION SYSTEM - DEMO MODE")
    print("=" * 60)
    print("This demo shows how the AI experts interact and debate.")
    print("In development mode (without Ollama), responses are pre-scripted.")
    print("=" * 60)
    
    # Simulate user questions and AI responses
    demo_scenarios = [
        {
            "user": "I want to scrape competitor pricing data from their website",
            "responses": [
                ("⚖️ Legal-AI", "I must advise extreme caution here. Website scraping often violates Terms of Service agreements and could expose you to legal action under the Computer Fraud and Abuse Act. We need to review their robots.txt and ToS first."),
                ("💻 Tech-AI", "Technically, this is straightforward with tools like Scrapy or Beautiful Soup. @Legal-AI, while ToS violations are a concern, enforcement is rare for basic price monitoring. The technical implementation is simple."),
                ("⚖️ Legal-AI", "@Tech-AI, you're underestimating the risk. The hiQ vs LinkedIn case established that ToS violations can constitute unauthorized access. I recommend using public APIs or manually collecting publicly available data instead."),
                ("📊 Business-AI", "Both perspectives have merit. @Legal-AI raises valid compliance concerns, but @Tech-AI is right about competitive necessity. What if we start with publicly available pricing pages and explore API partnerships with data providers?")
            ]
        },
        {
            "user": "Should we implement user tracking across our website for better analytics?",
            "responses": [
                ("📊 Business-AI", "User tracking can provide valuable insights for optimization and personalization. The data would help us improve user experience and conversion rates significantly."),
                ("⚖️ Legal-AI", "We need to consider GDPR, CCPA, and other privacy regulations. User consent is mandatory, and we must implement proper data governance. The liability for non-compliance is substantial."),
                ("💻 Tech-AI", "Implementation is straightforward with Google Analytics or custom solutions. @Legal-AI, privacy compliance is just a matter of proper cookie banners and consent management."),
                ("⚖️ Legal-AI", "@Tech-AI, it's not that simple. We need data processing agreements, regular audits, and the ability to delete user data on request. The technical architecture must support privacy by design."),
                ("📊 Business-AI", "Let's implement a phased approach: start with essential analytics only, ensure full compliance, then gradually expand based on clear business needs and user consent.")
            ]
        }
    ]
    
    for i, scenario in enumerate(demo_scenarios, 1):
        print(f"\n🎬 DEMO SCENARIO {i}")
        print("-" * 40)
        
        print(f"\n👤 You: {scenario['user']}")
        
        print(f"\n🔄 Consulting with AI experts...")
        time.sleep(1)
        
        print(f"\n{'='*60}")
        print("AI EXPERT PANEL DISCUSSION:")
        print('='*60)
        
        for speaker, response in scenario['responses']:
            print(f"\n{speaker}: ", end='')
            time.sleep(0.5)
            simulate_typing(response, delay=0.01)
            time.sleep(1)
        
        print(f"\n{'-'*60}")
        
        if i < len(demo_scenarios):
            input("\nPress Enter to continue to next scenario...")

def main():
    """Main demo function"""
    try:
        demo_consultation()
        
        print("\n🎉 DEMO COMPLETE!")
        print("\nThis demonstrates how your AI expert panel:")
        print("✅ Provides multiple professional perspectives")
        print("✅ Engages in natural debate and discussion")  
        print("✅ Challenges each other's assumptions")
        print("✅ Finds balanced solutions to complex problems")
        print("✅ Maintains professional ethics and boundaries")
        
        print("\n🚀 To experience the full system:")
        print("1. Install Ollama: https://ollama.ai/download")
        print("2. Run: ollama pull llama2")
        print("3. Start the system: python multi_ai_consultation.py")
        
        print("\nThe real system will provide:")
        print("📚 Knowledge base integration with your legal documents")
        print("🤖 Dynamic AI responses powered by local language models")
        print("💾 Session logging and conversation management")
        print("🔍 Intelligent PDF processing for legal knowledge")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo ended by user")

if __name__ == "__main__":
    main()
