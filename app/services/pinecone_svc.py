import os
from pinecone import Pinecone

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("vaani-knowledge")

def get_clinical_guidelines(query_text: str) -> str:
    """Embeds the query using Pinecone Inference and retrieves psychological guidelines."""
    try:
        # Generate embedding using Pinecone's free serverless model
        embedding = pc.inference.embed(
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