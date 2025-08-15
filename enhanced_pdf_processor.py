# enhanced_pdf_processor.py
"""
Enhanced PDF processing system for legal documents.
Supports OCR, text extraction, and intelligent chunking for RAG integration.
"""

import os
import sys
import json
import io
from typing import List, Dict, Any, Tuple
import re
from pathlib import Path

# Try importing PDF libraries with fallbacks
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

class LegalDocumentProcessor:
    """Process legal PDF documents for knowledge base integration"""
    
    def __init__(self, output_dir: str = "processed_legal_docs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Legal document patterns for better text extraction
        self.legal_patterns = {
            'section_headers': re.compile(r'^(SECTION|CHAPTER|ARTICLE|PART)\s+\d+', re.IGNORECASE | re.MULTILINE),
            'subsections': re.compile(r'^\([a-z0-9]+\)', re.MULTILINE),
            'citations': re.compile(r'\d+\s+U\.S\.C\.?\s+§?\s*\d+|\d+\s+CFR\s+\d+|\d+\s+Fed\.\s*Reg\.\s+\d+'),
            'dates': re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\w+\s+\d{1,2},\s+\d{4}\b'),
            'case_names': re.compile(r'\b[A-Z][a-z]+\s+v\.\s+[A-Z][a-z]+\b'),
        }
        
        print(f"📄 Legal Document Processor initialized")
        print(f"   PyPDF2: {'✅' if PYPDF2_AVAILABLE else '❌'}")
        print(f"   PyMuPDF: {'✅' if PYMUPDF_AVAILABLE else '❌'}")
        print(f"   OCR: {'✅' if OCR_AVAILABLE else '❌'}")
    
    def extract_text_pypdf2(self, pdf_path: str) -> str:
        """Extract text using PyPDF2"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"❌ PyPDF2 extraction failed: {e}")
        return text
    
    def extract_text_pymupdf(self, pdf_path: str) -> str:
        """Extract text using PyMuPDF (fitz)"""
        text = ""
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
        except Exception as e:
            print(f"❌ PyMuPDF extraction failed: {e}")
        return text
    
    def extract_text_ocr(self, pdf_path: str) -> str:
        """Extract text using OCR as fallback"""
        if not OCR_AVAILABLE:
            return ""
        
        text = ""
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap()
                img_data = pix.tobytes("ppm")
                
                # Convert to PIL Image
                img = Image.open(io.BytesIO(img_data))
                
                # Perform OCR
                page_text = pytesseract.image_to_string(img)
                text += page_text + "\n"
            
            doc.close()
        except Exception as e:
            print(f"❌ OCR extraction failed: {e}")
        
        return text
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using best available method"""
        print(f"📖 Extracting text from {os.path.basename(pdf_path)}...")
        
        text = ""
        
        # Try PyMuPDF first (usually better)
        if PYMUPDF_AVAILABLE and not text.strip():
            text = self.extract_text_pymupdf(pdf_path)
            if text.strip():
                print("   ✅ Extracted using PyMuPDF")
        
        # Try PyPDF2 as fallback
        if PYPDF2_AVAILABLE and not text.strip():
            text = self.extract_text_pypdf2(pdf_path)
            if text.strip():
                print("   ✅ Extracted using PyPDF2")
        
        # Try OCR as last resort
        if OCR_AVAILABLE and not text.strip():
            print("   🔍 Attempting OCR extraction...")
            text = self.extract_text_ocr(pdf_path)
            if text.strip():
                print("   ✅ Extracted using OCR")
        
        if not text.strip():
            print("   ❌ No text could be extracted")
        
        return text
    
    def clean_legal_text(self, text: str) -> str:
        """Clean and normalize legal document text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR errors in legal documents
        text = re.sub(r'\bl\b', 'I', text)  # Common OCR error
        text = re.sub(r'\bO\b', '0', text)  # Zero vs O confusion
        
        # Normalize quotes
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r"[''']", "'", text)
        
        # Fix section numbering
        text = re.sub(r'§\s*(\d+)', r'Section \1', text)
        
        return text.strip()
    
    def identify_document_type(self, text: str, filename: str) -> str:
        """Identify the type of legal document"""
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        # Check filename first
        if any(term in filename_lower for term in ['constitution', 'const']):
            return 'Constitution'
        elif any(term in filename_lower for term in ['criminal', 'penal']):
            return 'Criminal Law'
        elif any(term in filename_lower for term in ['civil', 'civilian']):
            return 'Civil Law'
        elif any(term in filename_lower for term in ['contract', 'agreement']):
            return 'Contract Law'
        elif any(term in filename_lower for term in ['employment', 'labor']):
            return 'Employment Law'
        elif any(term in filename_lower for term in ['copyright', 'intellectual']):
            return 'Intellectual Property'
        elif any(term in filename_lower for term in ['arbitration']):
            return 'Arbitration Law'
        
        # Check content
        if any(term in text_lower for term in ['constitution', 'constitutional']):
            return 'Constitution'
        elif any(term in text_lower for term in ['criminal code', 'penal code']):
            return 'Criminal Law'
        elif any(term in text_lower for term in ['civil code', 'civil law']):
            return 'Civil Law'
        
        return 'General Legal Document'
    
    def intelligent_chunking(self, text: str, doc_type: str, chunk_size: int = 800) -> List[Dict[str, Any]]:
        """Intelligently chunk legal documents based on structure"""
        chunks = []
        
        # Split by legal sections first
        sections = self.legal_patterns['section_headers'].split(text)
        
        if len(sections) > 1:
            # Document has clear sections
            for i, section in enumerate(sections):
                if not section.strip():
                    continue
                
                # Add section header back
                if i > 0:
                    section_match = self.legal_patterns['section_headers'].search(text)
                    if section_match:
                        section = section_match.group() + " " + section
                
                # Further split if section is too long
                if len(section) > chunk_size:
                    sub_chunks = self.split_by_paragraphs(section, chunk_size)
                    for j, sub_chunk in enumerate(sub_chunks):
                        chunks.append({
                            'content': sub_chunk,
                            'chunk_type': 'section_part',
                            'section_number': i,
                            'sub_chunk': j,
                            'document_type': doc_type
                        })
                else:
                    chunks.append({
                        'content': section,
                        'chunk_type': 'section',
                        'section_number': i,
                        'document_type': doc_type
                    })
        else:
            # No clear sections, split by paragraphs
            paragraph_chunks = self.split_by_paragraphs(text, chunk_size)
            for i, chunk in enumerate(paragraph_chunks):
                chunks.append({
                    'content': chunk,
                    'chunk_type': 'paragraph',
                    'chunk_number': i,
                    'document_type': doc_type
                })
        
        return chunks
    
    def split_by_paragraphs(self, text: str, chunk_size: int) -> List[str]:
        """Split text by paragraphs, respecting chunk size"""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # If adding this paragraph would exceed chunk size
            if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add remaining text
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def extract_metadata(self, text: str, filename: str) -> Dict[str, Any]:
        """Extract metadata from legal document"""
        metadata = {
            'filename': filename,
            'document_type': self.identify_document_type(text, filename),
            'length': len(text),
            'word_count': len(text.split()),
            'has_citations': bool(self.legal_patterns['citations'].search(text)),
            'has_case_names': bool(self.legal_patterns['case_names'].search(text)),
            'extraction_date': str(datetime.now())
        }
        
        # Extract key entities
        citations = self.legal_patterns['citations'].findall(text)
        case_names = self.legal_patterns['case_names'].findall(text)
        dates = self.legal_patterns['dates'].findall(text)
        
        metadata.update({
            'citations_found': len(citations),
            'cases_found': len(case_names),
            'dates_found': len(dates),
            'sample_citations': citations[:5],  # First 5 citations
            'sample_cases': case_names[:5],     # First 5 case names
        })
        
        return metadata
    
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Process a single PDF document"""
        filename = os.path.basename(pdf_path)
        print(f"\n📄 Processing: {filename}")
        
        # Extract text
        raw_text = self.extract_text_from_pdf(pdf_path)
        
        if not raw_text.strip():
            return {
                'success': False,
                'error': 'No text could be extracted from PDF',
                'filename': filename
            }
        
        # Clean text
        cleaned_text = self.clean_legal_text(raw_text)
        
        # Extract metadata
        metadata = self.extract_metadata(cleaned_text, filename)
        
        # Intelligent chunking
        chunks = self.intelligent_chunking(cleaned_text, metadata['document_type'])
        
        # Save processed document
        output_data = {
            'metadata': metadata,
            'full_text': cleaned_text,
            'chunks': chunks,
            'processing_info': {
                'original_length': len(raw_text),
                'cleaned_length': len(cleaned_text),
                'num_chunks': len(chunks),
                'avg_chunk_size': sum(len(chunk['content']) for chunk in chunks) / len(chunks) if chunks else 0
            }
        }
        
        # Save to file
        output_filename = self.output_dir / f"{Path(filename).stem}_processed.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Processed into {len(chunks)} chunks")
        print(f"   💾 Saved to: {output_filename}")
        
        return {
            'success': True,
            'filename': filename,
            'chunks': chunks,
            'metadata': metadata,
            'output_file': str(output_filename)
        }
    
    def process_legal_directory(self, directory: str = "legal_docs") -> List[Dict[str, Any]]:
        """Process all PDFs in the legal documents directory"""
        if not os.path.exists(directory):
            print(f"❌ Directory {directory} not found")
            return []
        
        pdf_files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            print(f"📂 No PDF files found in {directory}")
            return []
        
        print(f"📂 Found {len(pdf_files)} PDF files to process")
        
        results = []
        for pdf_file in pdf_files:
            pdf_path = os.path.join(directory, pdf_file)
            result = self.process_pdf(pdf_path)
            results.append(result)
        
        # Summary
        successful = [r for r in results if r.get('success', False)]
        failed = [r for r in results if not r.get('success', False)]
        
        print(f"\n📊 PROCESSING SUMMARY:")
        print(f"   ✅ Successfully processed: {len(successful)}")
        print(f"   ❌ Failed to process: {len(failed)}")
        
        if failed:
            print(f"\n❌ Failed files:")
            for result in failed:
                print(f"   - {result['filename']}: {result.get('error', 'Unknown error')}")
        
        return results

# Add datetime import at the top
from datetime import datetime

def install_requirements():
    """Helper function to install required packages"""
    packages = [
        'PyPDF2',
        'PyMuPDF',  # fitz
        'Pillow',   # PIL
        'pytesseract'
    ]
    
    print("📦 Required packages for full PDF processing:")
    for package in packages:
        print(f"   pip install {package}")
    
    print("\n🔧 For OCR support, also install tesseract:")
    print("   Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
    print("   Ubuntu: sudo apt install tesseract-ocr")
    print("   macOS: brew install tesseract")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        install_requirements()
    else:
        processor = LegalDocumentProcessor()
        results = processor.process_legal_directory()
        
        if results:
            print(f"\n🎯 Ready to integrate {len([r for r in results if r.get('success')])} documents into RAG system!")
