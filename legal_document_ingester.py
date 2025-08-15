# legal_document_ingester.py
import os
import requests

class LegalDocumentDownloader:
    def __init__(self):
        self.legal_sources = {
            # Free legal resources
            "us_constitution.txt": "https://www.archives.gov/founding-docs/constitution-transcript",
            "copyright_basics.txt": "https://www.copyright.gov/circs/circ01.pdf",
            # Add more free legal resources
        }
    
    def download_legal_docs(self):
        """Download free legal documents"""
        for filename, url in self.legal_sources.items():
            if not os.path.exists(filename):
                print(f"📥 Downloading {filename}...")
                # Implement download logic here
                
    def ingest_local_files(self, folder_path="legal_docs"):
        """Ingest legal documents from local folder"""
        documents = []
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"📁 Created folder: {folder_path}")
            print("Add your legal documents (.txt, .pdf) to this folder")
            return documents
        
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            
            if filename.endswith('.txt'):
                with open(filepath, 'r') as f:
                    content = f.read()
                    documents.append({
                        'title': filename,
                        'content': content,
                        'source': filepath
                    })
                    print(f"✅ Loaded: {filename}")
        
        return documents