import os
from dotenv import load_dotenv
from pinecone import Pinecone

# Load API keys from .env
load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")
if not api_key:
    raise ValueError("PINECONE_API_KEY is missing in .env file.")

# Initialize Pinecone
print("Connecting to Pinecone...")
pc = Pinecone(api_key=api_key)
index = pc.Index("vaani-knowledge")

# Baseline Clinical Insights for RAG
clinical_data = [
    {
        "id": "baseline_1", 
        "text": "High reaction times (>1200ms) paired with frequent cursor reversals often indicate cognitive hesitation or underlying ADHD traits.", 
        "metadata": {"source": "baseline_v1", "category": "adhd_traits"}
    },
    {
        "id": "baseline_2", 
        "text": "Rapid, accurate spatial rotation task completion suggests strong visual-spatial intelligence, a common 'superpower' in neurodivergent profiles like Dyslexia.", 
        "metadata": {"source": "baseline_v1", "category": "dyslexia_strengths"}
    },
    {
        "id": "baseline_3", 
        "text": "Action initiation times under 300ms without task accuracy reflect high impulsivity, whereas times over 1500ms reflect potential executive dysfunction.", 
        "metadata": {"source": "baseline_v1", "category": "executive_function"}
    },
    {
        "id": "baseline_4", 
        "text": "Hyper-focus is detected when reaction times remain consistently low and accurate without fatigue across a prolonged, repetitive session.", 
        "metadata": {"source": "baseline_v1", "category": "hyperfocus"}
    },
    {
        "id": "baseline_5", 
        "text": "Lightning-fast reflexes coupled with poor pattern recognition suggest an overactive limbic system overriding prefrontal cortex planning.", 
        "metadata": {"source": "baseline_v1", "category": "cognitive_behavior"}
    }
]

print("Generating embeddings using multilingual-e5-large...")
try:
    # Generate embeddings via Pinecone Inference API
    embeddings = pc.inference.embed(
        model="multilingual-e5-large",
        inputs=[item["text"] for item in clinical_data],
        parameters={"input_type": "passage"}
    )
    
    # Prepare data format for Upsert (id, vector values, metadata)
    vectors = []
    for i, item in enumerate(clinical_data):
        vectors.append({
            "id": item["id"],
            "values": embeddings[i].values,
            "metadata": {"text": item["text"], **item["metadata"]}
        })
    
    print("Pushing data to vaani-knowledge index...")
    index.upsert(vectors=vectors)
    print("✅ RAG Knowledge Base successfully updated!")

except Exception as e:
    print(f"❌ Error uploading to Pinecone: {e}")