import os
from llama_index.core import Document, SummaryIndex, Settings
from llama_index.core.embeddings import MockEmbedding
from llama_index.llms.groq import Groq

def generate_historical_report(sessions_list: list):
    """
    Ingests Supabase session data into LlamaIndex to generate an aggregate clinical baseline report.
    """
    if not sessions_list:
        return {"summary": "Insufficient historical data to construct a clinical baseline matrix."}

    # 1. Convert DB rows into LlamaIndex Documents
    documents = []
    for session in sessions_list:
        game_type = session.get("game_type", "Unknown Task")
        metrics = session.get("metrics", {})
        text_content = f"Task: {game_type} | Age Group: {metrics.get('age_group')} | Latency: {metrics.get('action_initiation_time_ms')}ms | Total Time: {metrics.get('total_response_time_ms')}ms | Errors: {metrics.get('cursor_reversals')}"
        documents.append(Document(text=text_content))

    # 2. Configure Groq via LlamaIndex & Bypass OpenAI Embeddings
    groq_api_key = os.environ.get("GROQ_API_KEY")
    
    # Set Groq as the main LLM brain
    Settings.llm = Groq(model="llama-3.3-70b-versatile", api_key=groq_api_key)
    
    # Use MockEmbedding to completely bypass OpenAI API key requirement
    Settings.embed_model = MockEmbedding(embed_dim=1)

    try:
        # 3. Build Summary Index (Best for synthesizing a handful of records without embeddings)
        index = SummaryIndex.from_documents(documents)
        query_engine = index.as_query_engine()

        # 4. Strict Clinical Query
        clinical_query = """
        Analyze these historical cognitive telemetry entries for the subject.
        Synthesize the data into a strict, minimalist, 3-sentence clinical summary.
        Focus objectively on indicators of ADHD (impulsivity/error trends), PTSD (response latency/hesitation), and overall Executive Load.
        Do not use any fluff, introductory text, or philosophical framing.
        """
        
        response = query_engine.query(clinical_query)
        return {"summary": str(response).strip()}
        
    except Exception as e:
        print(f"❌ [report_svc.py] LlamaIndex Error: {str(e)}")
        return {"summary": "Failed to synthesize data. Diagnostic engine failure."}