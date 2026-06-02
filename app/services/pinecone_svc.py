import os

_pc = None
_index = None

def get_pinecone_index():
    """Lazily initialize Pinecone only when needed. Returns None if API key is missing."""
    global _pc, _index
    
    if _pc is not None:
        return _index
    
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("⚠️  [pinecone_svc.py] PINECONE_API_KEY not set. Vector retrieval disabled.")
        return None
    
    try:
        from pinecone import Pinecone
        _pc = Pinecone(api_key=api_key)
        _index = _pc.Index("vaani-knowledge")
        print("✅ [pinecone_svc.py] Pinecone initialized successfully")
        return _index
    except Exception as e:
        print(f"❌ [pinecone_svc.py] Failed to initialize Pinecone: {e}")
        return None

def get_clinical_guidelines(query_text: str) -> str:
    """Embeds the query using Pinecone Inference and retrieves psychological guidelines."""
    index = get_pinecone_index()
    
    if index is None:
        return "No additional clinical context found. (Vector DB unavailable)"
    
    try:
        # Generate embedding using Pinecone's free serverless model
        embedding = index.inference.embed(
            model="multilingual-e5-large",
            inputs=[query_text],
            parameters={"input_type": "query"}
        )
        
        # Search the database
        results = index.query(
            vector=embedding[0].values,
            top_k=2,
            include_metadata=True
        )
        
        # Extract text context
        contexts = [match.metadata.get("text", "") for match in results.matches if match.metadata]
        return "\n".join(contexts) if contexts else "No additional clinical context found."
    except Exception as e:
        print(f"Vector DB Warning: {e}")
        return ""