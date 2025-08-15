# legal_rag_system.py
import ollama
import os
import json
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class LegalKnowledgeBase:
    def __init__(self):
        self.documents = []
        self.embeddings = []
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Free embedding model
        
    def add_legal_document(self, title, content):
        """Add legal document to knowledge base"""
        # Split into chunks for better retrieval
        chunks = self.split_into_chunks(content, chunk_size=500)
        
        for i, chunk in enumerate(chunks):
            doc = {
                "title": title,
                "chunk_id": i,
                "content": chunk,
                "embedding": self.model.encode(chunk)
            }
            self.documents.append(doc)
            self.embeddings.append(doc["embedding"])
        
        print(f"✅ Added {len(chunks)} chunks from '{title}'")
    
    def split_into_chunks(self, text, chunk_size=500):
        """Split text into manageable chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def search_relevant_docs(self, query, top_k=3):
        """Find most relevant documents for a query"""
        if not self.documents:
            return []
        
        query_embedding = self.model.encode(query)
        similarities = cosine_similarity([query_embedding], self.embeddings)[0]
        
        # Get top-k most similar documents
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        relevant_docs = []
        for idx in top_indices:
            doc = self.documents[idx]
            doc_copy = doc.copy()
            doc_copy["similarity"] = similarities[idx]
            relevant_docs.append(doc_copy)
        
        return relevant_docs
    
    def load_legal_documents(self):
        """Load legal documents from files"""
        legal_files = [
            "contract_law.txt",
            "employment_law.txt", 
            "copyright_law.txt",
            "criminal_law.txt"
        ]
        
        for filename in legal_files:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    content = f.read()
                    self.add_legal_document(filename.replace('.txt', ''), content)

class LegalRAGAssistant:
    def __init__(self):
        self.knowledge_base = LegalKnowledgeBase()
        self.setup_knowledge_base()
    
    def setup_knowledge_base(self):
        """Setup legal knowledge base"""
        print("🔄 Setting up legal knowledge base...")
        
        # Check if we have legal documents, if not create sample ones
        self.create_sample_legal_docs()
        self.knowledge_base.load_legal_documents()
        
        print("✅ Knowledge base ready!")
    
    def create_sample_legal_docs(self):
        """Create sample legal documents if they don't exist"""
        sample_docs = {
            "contract_law.txt": """
            CONTRACT LAW BASICS
            
            Essential Elements of a Contract:
            1. Offer: A clear proposal to enter into an agreement
            2. Acceptance: Unqualified agreement to the terms of the offer
            3. Consideration: Something of value exchanged between parties
            4. Mutual assent: Both parties must understand and agree to the terms
            5. Capacity: Parties must be legally able to enter contracts
            6. Legality: The contract purpose must be legal
            
            Types of Contracts:
            - Express contracts: Terms explicitly stated
            - Implied contracts: Terms inferred from conduct
            - Unilateral contracts: One party makes a promise in exchange for performance
            - Bilateral contracts: Both parties exchange promises
            
            Contract Remedies:
            - Damages: Monetary compensation for breach
            - Specific performance: Court order to fulfill contract terms
            - Rescission: Cancellation of the contract
            - Restitution: Return of benefits received
            
            Statute of Frauds:
            Certain contracts must be in writing:
            - Contracts for sale of land
            - Contracts that cannot be performed within one year
            - Contracts for sale of goods over $500
            - Marriage contracts
            - Contracts to pay another's debt
            """,
            
            "employment_law.txt": """
            EMPLOYMENT LAW OVERVIEW
            
            At-Will Employment:
            - Either party can terminate employment at any time
            - Exceptions: discrimination, retaliation, public policy violations
            - Some states have additional protections
            
            Discrimination Laws:
            Protected classes under federal law:
            - Race, color, religion, sex, national origin (Title VII)
            - Age 40+ (ADEA)
            - Disability (ADA)
            - Genetic information (GINA)
            
            Wage and Hour Laws:
            - Federal minimum wage requirements
            - Overtime pay for hours over 40/week
            - Exempt vs. non-exempt employees
            - Meal and rest break requirements (state-specific)
            
            Workplace Safety:
            - OSHA requires safe working conditions
            - Employees have right to report safety violations
            - Protection from retaliation for safety complaints
            
            Family and Medical Leave:
            - FMLA provides unpaid leave for qualifying events
            - Job protection during leave
            - Continuation of health benefits
            """,
            
            "copyright_law.txt": """
            COPYRIGHT LAW FUNDAMENTALS
            
            What Copyright Protects:
            - Original works of authorship
            - Literary, dramatic, musical, artistic works
            - Computer software and databases
            - Architectural works
            
            Copyright Duration:
            - Works created after 1978: Life + 70 years
            - Corporate works: 95 years from publication or 120 years from creation
            - Works published before 1978: Different rules apply
            
            Fair Use Doctrine:
            Four factors for fair use analysis:
            1. Purpose and character of use (commercial vs. educational)
            2. Nature of copyrighted work
            3. Amount used relative to whole work
            4. Effect on market value of original work
            
            Copyright Infringement:
            - Unauthorized copying, distribution, or display
            - Substantial similarity to original work
            - Access to original work
            
            Digital Millennium Copyright Act (DMCA):
            - Safe harbor provisions for online platforms
            - Notice and takedown procedures
            - Protection against false claims
            """
        }
        
        for filename, content in sample_docs.items():
            if not os.path.exists(filename):
                with open(filename, 'w') as f:
                    f.write(content)
                print(f"📄 Created sample file: {filename}")
    
    def get_legal_advice(self, question):
        """Get legal advice using RAG"""
        # Search for relevant documents
        relevant_docs = self.knowledge_base.search_relevant_docs(question, top_k=3)
        
        if not relevant_docs:
            context = "No relevant legal documents found."
        else:
            # Combine relevant documents into context
            context_parts = []
            for doc in relevant_docs:
                context_parts.append(f"From {doc['title']}:\n{doc['content']}\n")
            context = "\n---\n".join(context_parts)
        
        # Create prompt with context
        prompt = f"""You are a legal AI assistant. Use the following legal information to answer the user's question accurately.

LEGAL CONTEXT:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
- Base your answer on the legal information provided
- If the context doesn't contain relevant information, say so
- Always remind the user this is not legal advice
- Be specific and cite the relevant legal principles

ANSWER:"""

        # Send to Ollama
        try:
            response = ollama.generate(
                model='llama2',
                prompt=prompt,
                options={'temperature': 0.3}
            )
            return response['response']
        except Exception as e:
            return f"Error: {e}"
    
    def chat(self):
        print("⚖️ LEGAL RAG ASSISTANT")
        print("Powered by local knowledge base + Ollama")
        print(f"📚 Loaded {len(self.knowledge_base.documents)} legal document chunks")
        print("-" * 50)
        
        while True:
            question = input("\n👤 You: ")
            
            if question.lower() in ['quit', 'exit']:
                print("Legal consultation ended.")
                break
            
            print("\n🔍 Searching legal knowledge base...")
            answer = self.get_legal_advice(question)
            print(f"\n⚖️ Legal-AI: {answer}")

if __name__ == "__main__":
    assistant = LegalRAGAssistant()
    assistant.chat()