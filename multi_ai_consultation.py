# multi_ai_consultation.py
import json
import time
import random
import subprocess
from datetime import datetime
from typing import List, Dict, Any
import os
import sys

# Import specialized prompts
try:
    from specialized_legal_prompts import PromptManager
    SPECIALIZED_PROMPTS_AVAILABLE = True
except ImportError:
    SPECIALIZED_PROMPTS_AVAILABLE = False
    print("⚠️ Specialized prompts not available")

# Try to import ollama, fallback to CLI if not available
try:
    import ollama
    # Test if Ollama is actually working
    try:
        ollama.list()
        OLLAMA_AVAILABLE = True
        OLLAMA_METHOD = "python"
        print("✅ Ollama Python client connected successfully!")
    except Exception as e:
        # Check if CLI works
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                # CLI exists but subprocess integration is problematic
                OLLAMA_AVAILABLE = False  # Force mock for now
                OLLAMA_METHOD = "mock"
                print("⚠️ Ollama CLI detected but subprocess integration has issues.")
                print("Using improved mock responses that demonstrate the system.")
            else:
                OLLAMA_AVAILABLE = False
                OLLAMA_METHOD = "none"
                print("⚠️ Ollama not responding. Using mock responses.")
        except:
            OLLAMA_AVAILABLE = False
            OLLAMA_METHOD = "none"
            print("⚠️ Ollama not found. Using mock responses for development.")
except ImportError:
    # Check if CLI works without Python client
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            OLLAMA_AVAILABLE = True
            OLLAMA_METHOD = "cli"
            print("✅ Ollama CLI available (no Python client), using CLI method!")
        else:
            OLLAMA_AVAILABLE = False
            OLLAMA_METHOD = "none"
            print("⚠️ Ollama not found. Using mock responses.")
    except:
        OLLAMA_AVAILABLE = False
        OLLAMA_METHOD = "none"
        print("⚠️ Ollama not found. Using mock responses for development.")

def generate_with_ollama_cli(model, prompt):
    """Fallback to use Ollama CLI directly if Python client fails"""
    try:
        # Shorten and clean the prompt for CLI
        lines = prompt.split('\n')
        # Extract just the essential parts
        user_query = ""
        ai_name = "AI"
        
        for line in lines:
            if "USER QUERY:" in line:
                user_query = line.split("USER QUERY:")[-1].strip()
            if "Legal-AI:" in line and not user_query:
                ai_name = "Legal-AI"
            elif "Tech-AI:" in line and not user_query:
                ai_name = "Tech-AI"
            elif "Business-AI:" in line and not user_query:
                ai_name = "Business-AI"
        
        # Create a much shorter prompt
        if "Legal-AI" in prompt:
            short_prompt = f"You are Legal-AI, a conservative legal expert. User asks: {user_query}. Respond as Legal-AI briefly."
        elif "Tech-AI" in prompt:
            short_prompt = f"You are Tech-AI, a pragmatic technical expert. User asks: {user_query}. Respond as Tech-AI briefly."
        elif "Business-AI" in prompt:
            short_prompt = f"You are Business-AI, a strategic business expert. User asks: {user_query}. Respond as Business-AI briefly."
        else:
            short_prompt = f"User asks: {user_query}. Respond briefly."
        
        # Use subprocess to call ollama directly with encoding fix
        result = subprocess.run(
            ['ollama', 'run', model, short_prompt],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=30
        )
        if result.returncode == 0:
            return {"response": result.stdout.strip()}
        else:
            return {"response": f"Error: {result.stderr}"}
    except Exception as e:
        return {"response": f"CLI Error: {e}"}

class MockOllama:
    """Improved Mock Ollama that responds contextually"""
    def generate(self, model, prompt, options=None):
        # Simulate thinking time
        time.sleep(random.uniform(0.5, 1.5))
        
        # Extract user input from prompt
        user_input = ""
        if "USER QUERY:" in prompt:
            user_input = prompt.split("USER QUERY:")[-1].strip().lower()
        
        # Contextual responses based on user input and AI persona
        if "legal" in model.lower() or "Legal-AI" in prompt:
            if any(word in user_input for word in ["hi", "hello", "hey", "greet"]):
                return {"response": "Hello! I'm Legal-AI, your legal expert. I'm here to help you navigate legal complexities and identify potential risks. What legal matters can I assist you with today?"}
            elif any(word in user_input for word in ["scrape", "scraping", "data"]):
                return {"response": "I must advise caution regarding web scraping. This often violates Terms of Service and could expose you to legal action under the Computer Fraud and Abuse Act. Let's explore compliant alternatives."}
            elif any(word in user_input for word in ["track", "tracking", "analytics"]):
                return {"response": "User tracking raises significant privacy law concerns. We need to consider GDPR, CCPA compliance, and ensure proper consent mechanisms are in place."}
            else:
                return {"response": "From a legal perspective, I need to evaluate the regulatory implications and potential risks involved. Could you provide more details about the specific legal aspects you're concerned about?"}
        
        elif "tech" in model.lower() or "Tech-AI" in prompt:
            if any(word in user_input for word in ["hi", "hello", "hey", "greet"]):
                return {"response": "Hey there! I'm Tech-AI, your technical expert. I focus on practical solutions and efficient implementation. What technical challenge can I help you solve today?"}
            elif any(word in user_input for word in ["scrape", "scraping", "data"]):
                return {"response": "From a technical standpoint, web scraping is straightforward using tools like Scrapy, Beautiful Soup, or Selenium. @Legal-AI might be overthinking the compliance aspects - most basic data collection is fine."}
            elif any(word in user_input for word in ["track", "tracking", "analytics"]):
                return {"response": "User tracking is easy to implement with Google Analytics, custom event tracking, or tools like Mixpanel. @Legal-AI, privacy compliance is just a matter of adding proper cookie banners."}
            else:
                return {"response": "This looks technically feasible. I can outline several implementation approaches using modern frameworks. What's the specific technical requirement you're trying to solve?"}
        
        elif "business" in model.lower() or "Business-AI" in prompt:
            if any(word in user_input for word in ["hi", "hello", "hey", "greet"]):
                return {"response": "Hello! I'm Business-AI, your strategic advisor. I help balance legal requirements with technical possibilities to achieve business objectives. What business challenge shall we tackle?"}
            elif any(word in user_input for word in ["scrape", "scraping", "data"]):
                return {"response": "I see both perspectives here. @Legal-AI raises valid compliance concerns, but @Tech-AI is right about competitive necessity. What if we start with publicly available data and explore API partnerships?"}
            elif any(word in user_input for word in ["track", "tracking", "analytics"]):
                return {"response": "User analytics can provide valuable business insights. Let's find a balanced approach that satisfies @Legal-AI's compliance requirements while meeting @Tech-AI's implementation efficiency."}
            else:
                return {"response": "Let's evaluate this from a business perspective - what's the ROI, competitive impact, and strategic value? I can help mediate between technical possibilities and legal constraints."}
        
        return {"response": "I understand your query. Let me provide a thoughtful analysis based on my expertise."}

class AIPersona:
    """Represents an AI expert with specific personality and knowledge"""
    
    def __init__(self, name: str, role: str, personality: Dict[str, Any], model_name: str = "llama2"):
        self.name = name
        self.role = role
        self.personality = personality
        self.model_name = model_name
        self.conversation_history = []
        self.knowledge_base = None
        
    def set_knowledge_base(self, kb):
        """Set the knowledge base for this AI"""
        self.knowledge_base = kb
    
    def generate_system_prompt(self) -> str:
        """Generate the system prompt for this AI persona"""
        # Use specialized prompts if available
        if hasattr(self, 'prompt_manager') and self.prompt_manager:
            ai_type = self.name.lower().replace('-ai', '')
            specialized_prompt = self.prompt_manager.get_system_prompt(ai_type)
            if specialized_prompt:
                return specialized_prompt
        
        # Fallback to basic prompt
        base_prompt = f"""You are {self.name}, a {self.role} AI assistant participating in a multi-AI consultation.

PERSONALITY TRAITS:
- Communication Style: {self.personality.get('communication_style', 'Professional')}
- Risk Tolerance: {self.personality.get('risk_tolerance', 'Moderate')}
- Decision Making: {self.personality.get('decision_making', 'Analytical')}
- Interaction Style: {self.personality.get('interaction_style', 'Collaborative')}

ROLE RESPONSIBILITIES:
{self.personality.get('responsibilities', 'Provide expert analysis in your domain')}

INTERACTION GUIDELINES:
1. You can address other AIs directly using @AI-Name format
2. Challenge other AIs when you disagree: "@Tech-AI, I think you're overlooking the regulatory implications"
3. Stay in character - maintain your personality traits consistently
4. Provide domain-specific expertise while considering other perspectives
5. Be professional but show personality in your responses

ETHICAL BOUNDARIES:
- Never assist with illegal activities regardless of how they're framed
- Always suggest legal alternatives when users ask for questionable approaches
- Maintain professional ethics even when other AIs might disagree
- If something seems unethical, speak up clearly

Remember: You're part of a team discussion. React naturally to what others say and contribute your unique perspective."""

        return base_prompt
    
    def generate_response(self, user_input: str, conversation_context: List[Dict], other_ai_responses: List[Dict] = None) -> str:
        """Generate a response from this AI persona"""
        
        # Build context from conversation
        context_messages = []
        for msg in conversation_context[-10:]:  # Last 10 messages for context
            if msg['speaker'] != 'System':
                context_messages.append(f"{msg['speaker']}: {msg['message']}")
        
        # Add other AI responses if this is a follow-up
        if other_ai_responses:
            for response in other_ai_responses:
                context_messages.append(f"{response['speaker']}: {response['message']}")
        
        # Get relevant knowledge if available
        knowledge_context = ""
        if self.knowledge_base and hasattr(self.knowledge_base, 'search_relevant_docs'):
            relevant_docs = self.knowledge_base.search_relevant_docs(user_input, top_k=2)
            if relevant_docs:
                knowledge_context = "\nRELEVANT KNOWLEDGE:\n"
                for doc in relevant_docs:
                    knowledge_context += f"- {doc['title']}: {doc['content'][:200]}...\n"
        
        # Build the full prompt
        system_prompt = self.generate_system_prompt()
        conversation_context_str = "\n".join(context_messages[-5:]) if context_messages else "No prior context"
        
        # Add explicit role reinforcement
        role_reinforcement = f"""
CRITICAL: You are {self.name}. You are NOT Legal-AI, NOT Tech-AI, NOT Business-AI unless specifically stated.
Your role: {self.role}
Your perspective: {self.personality.get('communication_style', 'Professional')}
"""

        full_prompt = f"""{system_prompt}

{role_reinforcement}

CONVERSATION CONTEXT:
{conversation_context_str}

{knowledge_context}

USER QUERY: {user_input}

IMPORTANT: Respond ONLY as {self.name} with your {self.role} perspective. Do NOT respond as any other AI. Start your response by clearly identifying yourself.

{self.name}:"""

        # Generate response using Ollama or mock
        try:
            if OLLAMA_AVAILABLE:
                if OLLAMA_METHOD == "python":
                    try:
                        response = ollama.generate(
                            model=self.model_name,
                            prompt=full_prompt,
                            options={
                                'temperature': self.personality.get('temperature', 0.7),
                                'top_p': 0.9,
                                'max_tokens': 300
                            }
                        )
                        return response['response'].strip()
                    except Exception as e:
                        print(f"⚠️ Python client failed, trying CLI: {e}")
                        response = generate_with_ollama_cli(self.model_name, full_prompt)
                        return response['response'].strip()
                elif OLLAMA_METHOD == "cli":
                    response = generate_with_ollama_cli(self.model_name, full_prompt)
                    return response['response'].strip()
            else:
                mock_ollama = MockOllama()
                response = mock_ollama.generate(self.model_name, full_prompt)
                return response['response'].strip()
                
        except Exception as e:
            return f"Error generating response: {e}"

class MultiAIConsultation:
    """Main consultation system managing multiple AI personas"""
    
    def __init__(self):
        self.ais = {}
        self.conversation_history = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.prompt_manager = PromptManager() if SPECIALIZED_PROMPTS_AVAILABLE else None
        self.setup_ai_personas()
        
    def setup_ai_personas(self):
        """Initialize the AI personas"""
        
        # Legal AI - Conservative, risk-focused, RAG-enabled
        legal_ai = AIPersona(
            name="Legal-AI",
            role="Legal Expert",
            personality={
                'communication_style': 'Cautious and precise',
                'risk_tolerance': 'Very Low',
                'decision_making': 'Risk-averse and compliance-focused',
                'interaction_style': 'Thorough and methodical',
                'responsibilities': """Provide legal analysis, identify risks, ensure compliance.
- Analyze legal implications of proposed actions
- Identify potential regulatory violations
- Suggest compliant alternatives
- Reference actual legal precedents and statutes when possible""",
                'temperature': 0.3
            }
        )
        
        # Tech AI - Solution-oriented, impatient with constraints
        tech_ai = AIPersona(
            name="Tech-AI", 
            role="Technical Expert",
            personality={
                'communication_style': 'Direct and solution-focused',
                'risk_tolerance': 'Moderate to High',
                'decision_making': 'Pragmatic and implementation-focused',
                'interaction_style': 'Sometimes impatient with overly cautious approaches',
                'responsibilities': """Provide technical solutions and implementation guidance.
- Analyze technical feasibility
- Suggest implementation approaches
- Evaluate performance and scalability
- Challenge overly restrictive constraints when technically unnecessary""",
                'temperature': 0.7
            }
        )
        
        # Business AI - Results-driven, mediates between legal and tech
        business_ai = AIPersona(
            name="Business-AI",
            role="Business Strategy Expert", 
            personality={
                'communication_style': 'Strategic and balanced',
                'risk_tolerance': 'Moderate',
                'decision_making': 'ROI and outcome-focused',
                'interaction_style': 'Diplomatic mediator',
                'responsibilities': """Provide business analysis and strategic guidance.
- Evaluate business impact and ROI
- Balance risk vs. opportunity
- Mediate between technical ambition and legal caution
- Focus on practical, achievable outcomes""",
                'temperature': 0.6
            }
        )
        
        self.ais = {
            'legal': legal_ai,
            'tech': tech_ai,
            'business': business_ai
        }
        
        # Pass prompt manager to AIs
        if self.prompt_manager:
            for ai in self.ais.values():
                ai.prompt_manager = self.prompt_manager
    
    def integrate_legal_rag(self, legal_rag_system):
        """Integrate the existing legal RAG system"""
        if 'legal' in self.ais:
            self.ais['legal'].set_knowledge_base(legal_rag_system.knowledge_base)
            print("✅ Legal RAG system integrated with Legal-AI")
    
    def add_message(self, speaker: str, message: str, timestamp: datetime = None):
        """Add a message to conversation history"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.conversation_history.append({
            'timestamp': timestamp,
            'speaker': speaker,
            'message': message
        })
    
    def check_ethical_boundaries(self, user_input: str) -> bool:
        """Check if the request violates ethical boundaries"""
        # Simple keyword-based ethical checks
        unethical_keywords = [
            'hack', 'illegal', 'steal', 'fraud', 'piracy', 'bypass security',
            'malware', 'virus', 'ddos', 'phishing', 'identity theft',
            'money laundering', 'tax evasion', 'insider trading'
        ]
        
        user_lower = user_input.lower()
        for keyword in unethical_keywords:
            if keyword in user_lower:
                return False
        return True
    
    def generate_ai_responses(self, user_input: str) -> List[Dict[str, str]]:
        """Generate responses from all AI personas"""
        responses = []
        
        # First round - initial responses
        for ai_key, ai in self.ais.items():
            print(f"🤔 {ai.name} is thinking...")
            response = ai.generate_response(user_input, self.conversation_history)
            responses.append({
                'speaker': ai.name,
                'message': response,
                'ai_key': ai_key
            })
            
            # Add to conversation history
            self.add_message(ai.name, response)
        
        # Second round - reactions and debates (sometimes)
        if random.random() < 0.6:  # 60% chance of follow-up interactions
            print("\n💬 AIs are discussing among themselves...")
            time.sleep(1)
            
            # Randomly select 1-2 AIs to provide follow-up responses
            follow_up_ais = random.sample(list(self.ais.items()), random.randint(1, 2))
            
            for ai_key, ai in follow_up_ais:
                follow_up_response = ai.generate_response(
                    user_input, 
                    self.conversation_history,
                    responses  # Include other AI responses for context
                )
                
                responses.append({
                    'speaker': ai.name + " (follow-up)",
                    'message': follow_up_response,
                    'ai_key': ai_key
                })
                
                # Add to conversation history
                self.add_message(ai.name, follow_up_response)
        
        return responses
    
    def handle_unethical_request(self, user_input: str) -> List[Dict[str, str]]:
        """Handle requests that violate ethical boundaries"""
        responses = []
        
        legal_response = "I cannot and will not provide assistance with illegal activities. Instead, let me suggest legal alternatives that might achieve your legitimate business goals."
        
        tech_response = "From a technical standpoint, I understand you might be looking for solutions, but I can't help with anything that violates terms of service or laws. Happy to discuss legitimate technical approaches instead."
        
        business_response = "As a business advisor, I must point out that illegal activities expose your organization to significant legal and reputational risks. Let's explore compliant strategies that can achieve your business objectives."
        
        responses.extend([
            {'speaker': 'Legal-AI', 'message': legal_response, 'ai_key': 'legal'},
            {'speaker': 'Tech-AI', 'message': tech_response, 'ai_key': 'tech'},
            {'speaker': 'Business-AI', 'message': business_response, 'ai_key': 'business'}
        ])
        
        # Add to conversation history
        for response in responses:
            self.add_message(response['speaker'], response['message'])
        
        return responses
    
    def save_conversation(self):
        """Save conversation to file"""
        filename = f"consultation_session_{self.session_id}.json"
        
        conversation_data = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'conversation_history': self.conversation_history
        }
        
        with open(filename, 'w') as f:
            json.dump(conversation_data, f, indent=2, default=str)
        
        print(f"💾 Conversation saved to {filename}")
    
    def display_ai_response(self, response: Dict[str, str]):
        """Display an AI response with appropriate formatting"""
        speaker = response['speaker']
        message = response['message']
        
        # Choose emoji based on AI type
        emoji_map = {
            'Legal-AI': '⚖️',
            'Tech-AI': '💻', 
            'Business-AI': '📊'
        }
        
        # Get base name for emoji (remove follow-up suffix)
        base_name = speaker.split(' (')[0]
        emoji = emoji_map.get(base_name, '🤖')
        
        print(f"\n{emoji} {speaker}: {message}")
    
    def run_consultation(self):
        """Main consultation loop"""
        print("🎯 MULTI-AI CONSULTATION SYSTEM")
        print("=" * 60)
        print("Your AI Expert Panel:")
        print("⚖️ Legal-AI    - Conservative, risk-focused, knows actual law")
        print("💻 Tech-AI     - Solution-oriented, implementation-focused")  
        print("📊 Business-AI - Results-driven, mediates between perspectives")
        print("\n💡 The AIs will discuss your questions and may debate among themselves!")
        print("Type 'quit' to end the session")
        print("=" * 60)
        
        # Add system message
        self.add_message("System", "Multi-AI consultation session started")
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n🔚 Ending consultation session...")
                    self.save_conversation()
                    break
                
                if not user_input:
                    continue
                
                # Add user message to history
                self.add_message("You", user_input)
                
                # Check ethical boundaries
                if not self.check_ethical_boundaries(user_input):
                    print("\n🚫 ETHICAL BOUNDARY VIOLATION DETECTED")
                    responses = self.handle_unethical_request(user_input)
                else:
                    print("\n🔄 Consulting with AI experts...")
                    responses = self.generate_ai_responses(user_input)
                
                # Display responses
                print("\n" + "="*60)
                print("AI EXPERT PANEL DISCUSSION:")
                print("="*60)
                
                for response in responses:
                    self.display_ai_response(response)
                
                print("\n" + "-"*60)
                
            except KeyboardInterrupt:
                print("\n\n🔚 Session interrupted by user")
                self.save_conversation()
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                continue

def main():
    """Main entry point"""
    print("🚀 Initializing Multi-AI Consultation System...")
    
    # Initialize the consultation system
    consultation = MultiAIConsultation()
    
    # Try to integrate legal RAG system
    try:
        from legal_rag_system import LegalRAGAssistant
        legal_rag = LegalRAGAssistant()
        consultation.integrate_legal_rag(legal_rag)
    except Exception as e:
        print(f"⚠️ Could not load legal RAG system: {e}")
        print("Legal-AI will work without specialized legal knowledge base")
    
    # Check Ollama availability
    if not OLLAMA_AVAILABLE:
        print("\n⚠️ DEVELOPMENT MODE")
        print("Ollama not found. Install it with: 'curl -fsSL https://ollama.ai/install.sh | sh'")
        print("For now, using mock responses to demonstrate the system")
        print("Install 'llama2' model with: 'ollama pull llama2'")
    
    print("\n✅ System ready!")
    
    # Start the consultation
    consultation.run_consultation()

if __name__ == "__main__":
    main()
