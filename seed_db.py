import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("vaani-knowledge")

guidelines = [
    {"id": "g1", "text": "If a child shows frequent hesitations or prolonged pauses while reading or speaking, it may indicate cognitive load associated with dyslexia. Provide a supportive superpower acknowledging their careful thinking."},
    {"id": "g2", "text": "Fragmented speech or repeating the same syllables can be a sign of speech anxiety or early trauma. The admin report should flag this for the parent to monitor in a low-pressure environment."},
    {"id": "g3", "text": "When a child expresses frustration like 'I can't do this' or 'It's too hard', the AI must always counter with extreme positive reinforcement, labeling them as a 'Brave Explorer'."}
]

print("Embedding and uploading data to Pinecone...")
try:
    for item in guidelines:
        # Generate embedding
        embed_res = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[item["text"]],
            parameters={"input_type": "passage"}
        )
        
        # Upsert to index
        index.upsert(
            vectors=[
                {
                    "id": item["id"],
                    "values": embed_res[0].values,
                    "metadata": {"text": item["text"]}
                }
            ]
        )
    print("✅ Data successfully seeded into Pinecone!")
except Exception as e:
    print(f"❌ Error seeding database: {e}")
