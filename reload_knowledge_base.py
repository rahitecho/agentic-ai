import os
from dotenv import load_dotenv
from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.vectordb.pgvector.pgvector2 import PgVector2

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

db_url = "postgresql+psycopg://techovarya:F00tball@localhost:5432/agentic-ai"

def force_reload_knowledge_base():
    print("Creating knowledge base...")
    knowledge_base = PDFUrlKnowledgeBase(
        urls=["https://phi-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
        vector_db=PgVector2(collection="recipes", db_url=db_url)
    )
    
    print("Loading PDF and creating embeddings...")
    try:
        # Force recreate the knowledge base
        knowledge_base.load(recreate=True)
        print("✅ Knowledge base loaded successfully!")
        
        # Test search
        print("\nTesting search...")
        results = knowledge_base.search("Thai recipes", limit=3)
        print(f"Found {len(results)} results")
        
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Content: {result.content[:150]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    force_reload_knowledge_base()