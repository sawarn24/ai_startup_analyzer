import chromadb
from chromadb.config import Settings
import uuid
import os
import requests

# Import from your config
try:
    from config import settings
    GEMINI_API_KEY = settings.GEMINI_API_KEY
    HF_TOKEN = settings.HF_TOKEN
    UPLOAD_FOLDER = settings.UPLOAD_FOLDER
    DATA_FOLDER = settings.DATA_FOLDER
except ImportError:
    # Fallback if running outside of api_backend structure
    from dotenv import load_dotenv
    load_dotenv()
    
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    HF_TOKEN = os.getenv('HF_TOKEN')
    UPLOAD_FOLDER = "uploads"
    DATA_FOLDER = "data"

API_URL = "https://router.huggingface.co/hf-inference/models/BAAI/bge-small-en-v1.5"

CHROMA_DB_PATH = "./data/chroma_db"

class RAGSystem:
    """RAG system using ChromaDB and HuggingFace embeddings"""
    
    def __init__(self):
        self.client = chromadb.Client(Settings(
            persist_directory=CHROMA_DB_PATH,
            anonymized_telemetry=False
        ))
        
        # Store HF token and API URL
        self.hf_token = HF_TOKEN
        self.api_url = API_URL
        self.headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        }
        
        try:
            self.collection = self.client.get_collection("startup_documents")
        except:
            self.collection = self.client.create_collection(
                name="startup_documents",
                metadata={"description": "Startup analysis documents"}
            )
    
    def get_embeddings(self, texts):
        """
        Get embeddings from HuggingFace API
        
        Args:
            texts: list of strings or single string
            
        Returns:
            list of embeddings
        """
        # Convert single string to list
        if isinstance(texts, str):
            texts = [texts]
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": texts},
                timeout=60
            )
            response.raise_for_status()
            embeddings = response.json()
            
            # If single text, return single embedding
            if len(texts) == 1:
                return embeddings[0]
            
            return embeddings
            
        except Exception as e:
            print(f"❌ Error getting embeddings: {e}")
            raise
    
    def add_documents(self, extracted_data, startup_id):
        """
        Add all documents to vector database
        
        Args:
            extracted_data: dict from DocumentProcessor
            startup_id: unique identifier for this startup
        """
        all_chunks = []
        metadatas = []
        ids = []
        
        # Add pitch deck chunks
        if extracted_data['pitch_deck']['chunks']:
            for i, chunk in enumerate(extracted_data['pitch_deck']['chunks']):
                all_chunks.append(chunk)
                metadatas.append({
                    "startup_id": startup_id,
                    "doc_type": "pitch_deck",
                    "chunk_index": i,
                    "filename": extracted_data['pitch_deck']['filename']
                })
                ids.append(f"{startup_id}_pitch_{i}")
        
        # Add transcript chunks
        for doc_idx, transcript in enumerate(extracted_data['transcripts']):
            for i, chunk in enumerate(transcript['chunks']):
                all_chunks.append(chunk)
                metadatas.append({
                    "startup_id": startup_id,
                    "doc_type": "transcript",
                    "doc_index": doc_idx,
                    "chunk_index": i,
                    "filename": transcript['filename']
                })
                ids.append(f"{startup_id}_transcript_{doc_idx}_{i}")
        
        # Add email chunks
        for doc_idx, email in enumerate(extracted_data['emails']):
            for i, chunk in enumerate(email['chunks']):
                all_chunks.append(chunk)
                metadatas.append({
                    "startup_id": startup_id,
                    "doc_type": "email",
                    "doc_index": doc_idx,
                    "chunk_index": i,
                    "filename": email['filename']
                })
                ids.append(f"{startup_id}_email_{doc_idx}_{i}")
        
        # Add update chunks
        for doc_idx, update in enumerate(extracted_data['updates']):
            for i, chunk in enumerate(update['chunks']):
                all_chunks.append(chunk)
                metadatas.append({
                    "startup_id": startup_id,
                    "doc_type": "update",
                    "doc_index": doc_idx,
                    "chunk_index": i,
                    "filename": update['filename']
                })
                ids.append(f"{startup_id}_update_{doc_idx}_{i}")
        
        # Create embeddings and add to ChromaDB
        if all_chunks:
            # Get embeddings for all chunks
            embeddings = self.get_embeddings(all_chunks)
            
            # Add to ChromaDB
            self.collection.add(
                documents=all_chunks,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"✅ Added {len(all_chunks)} chunks to RAG system")
            return len(all_chunks)
        
        return 0
    
    def query(self, question, startup_id, n_results=5):
        """
        Query the RAG system with a question
        
        Args:
            question: the question to ask
            startup_id: filter by this startup
            n_results: number of results to return
            
        Returns:
            context string with retrieved documents
        """
        try:
            # Get embedding for the question
            query_embedding = self.get_embeddings(question)
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where={"startup_id": startup_id}
            )
            
            if results['documents'] and results['documents'][0]:
                # Join retrieved documents with separator
                context = "\n\n---\n\n".join(results['documents'][0])
                return context
            
            return ""
            
        except Exception as e:
            print(f"❌ Error querying RAG: {e}")
            return ""
    
    def query_by_doc_type(self, question, startup_id, doc_type, n_results=3):
        """
        Query specific document type
        
        Args:
            question: the question to ask
            startup_id: filter by this startup
            doc_type: type of document (pitch_deck, transcript, email, update)
            n_results: number of results to return
            
        Returns:
            context string with retrieved documents
        """
        try:
            # Get embedding for the question
            query_embedding = self.get_embeddings(question)
            
            # Query ChromaDB with document type filter
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where={
                    "$and": [
                        {"startup_id": startup_id},
                        {"doc_type": doc_type}
                    ]
                }
            )
            
            if results['documents'] and results['documents'][0]:
                # Join retrieved documents with separator
                context = "\n\n---\n\n".join(results['documents'][0])
                return context
            
            return ""
            
        except Exception as e:
            print(f"❌ Error querying by doc type: {e}")
            return ""